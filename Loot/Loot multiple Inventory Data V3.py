import os
from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import defaultdict

# Constants
INPUT_FOLDER_PATH = r"C:\Program Files (x86)\Ultima Online Outlands\ClassicUO\Data\Client\JournalLogs"
OUTPUT_DIRECTORY = os.path.join(r"C:\Users\dcorr\Documents", "Processed")

CLEAN_PHRASES = [
    "(used to increase a player's total skill cap by 1)",
    "(used to increase a player's skill cap for a skill by 1)",
    "[double click to place]",
    "(0 items, 0 stones)",
    "(double-click to activate)",
    "(double-click to research)",
    "(5,000 held per commodity)",
]

RAZOR_ID_PREFIX = "[Razor]: ID:"
WELCOME_PREFIX = "System: Welcome"


def get_all_outland_journal_files(folder_path: str) -> List[str]:
    """Return ALL .txt files in the folder, sorted by modification time (oldest first)."""
    folder = Path(folder_path)
    if not folder.exists():
        print(f"Error: The folder '{folder_path}' does not exist.")
        return []

    text_files = [f for f in folder.iterdir() if f.suffix.lower() == ".txt"]
    if not text_files:
        print(f"No .txt files found in {folder_path}")
        return []

    # Sort oldest → newest so logs are processed in chronological order
    text_files.sort(key=lambda f: f.stat().st_mtime)
    return [str(f) for f in text_files]


def process_items_data(file_path: str) -> Dict[str, Any]:
    """Parse the journal log and extract player name + items (including gold)."""
    data: Dict[str, Any] = {"name": None, "items": []}

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        for line in lines:
            line = line.strip()
            # Clean unwanted phrases from every line
            for phrase in CLEAN_PHRASES:
                line = line.replace(phrase, "")

            # Extract player name
            if WELCOME_PREFIX in line:
                name_part = line.split(WELCOME_PREFIX, 1)[1].strip()
                data["name"] = name_part

            # Extract Razor ID items
            if RAZOR_ID_PREFIX in line:
                item_data = line.split(RAZOR_ID_PREFIX, 1)[1].strip()
                parts = item_data.split()

                if len(parts) >= 1:  # Need at least an ID
                    item_id = parts[0]
                    remaining = parts[1:]

                    if remaining and remaining[-1].isdigit():
                        amount = int(remaining[-1])
                        description = " ".join(remaining[:-1])
                    else:
                        amount = 1
                        description = " ".join(remaining)

                    description = description.rstrip(":").strip()

                    item = {
                        "id": item_id,
                        "description": description,
                        "amount": amount,
                    }
                    data["items"].append(item)

            # Extract gold or doubloons deposit
            elif "You deposit" in line:
                if "doubloons" in line:
                    currency = "doubloons"
                    splitter = " doubloons"
                    item_id = "8888888888"
                elif "gold" in line:
                    currency = "gold"
                    splitter = " gold"
                    item_id = "9999999999"
                else:
                    # Skip other deposit messages (e.g. items)
                    continue

                try:
                    deposit_data = line.split("You deposit ", 1)[1].strip()
                    amount_str = deposit_data.split(splitter)[0].replace(",", "").strip()
                    
                    if amount_str.isdigit():
                        item = {
                            "id": item_id,
                            "description": currency,
                            "amount": int(amount_str),
                        }
                        data["items"].append(item)
                except:
                    pass

        return data

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return {"name": None, "items": []}
    except PermissionError:
        print(f"Error: Permission denied to read '{file_path}'.")
        return {"name": None, "items": []}
    except Exception as e:
        print(f"Error processing file '{file_path}': {e}")
        return {"name": None, "items": []}


def merge_items(data: Dict[str, Any], group_unidentified: bool = False) -> Dict[str, Any]:
    """Merge duplicate items by description. Optionally group all 'unidentified' items together."""
    merged: Dict[str, Dict[str, Any]] = {}
    unidentified_total = 0
    unidentified_ids: set[str] = set()

    for item in data.get("items", []):
        desc = item["description"].strip()

        if group_unidentified and "unidentified" in desc.lower():
            unidentified_total += item["amount"]
            unidentified_ids.add(item["id"])
            continue

        if desc in merged:
            merged[desc]["amount"] += item["amount"]
        else:
            # Copy to avoid mutating original data
            merged[desc] = {
                "id": item["id"],
                "description": desc,
                "amount": item["amount"],
            }

    # Add grouped unidentified items if requested
    if group_unidentified and unidentified_total > 0:
        unid_id = min(unidentified_ids) if unidentified_ids else "UNID"
        merged["Unidentified Items"] = {
            "id": unid_id,
            "description": "Unidentified Items",
            "amount": unidentified_total,
        }

    # Sort alphabetically by description
    sorted_items = sorted(merged.values(), key=lambda x: x["description"].lower())

    return {
        "name": data.get("name"),
        "items": sorted_items,
    }


def save_items_json(
    data: Dict[str, Any], output_dir: str, input_file_name: str
) -> Optional[str]:
    """Save the raw (unmerged) data as JSON with a timestamp."""
    try:
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H")
        output_file = output_dir_path / f"{input_file_name}_Items_{timestamp}.json"

        with open(output_file, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)

        print(f"JSON Data saved to: {output_file}")
        return str(output_file)
    except Exception as e:
        print(f"Error saving JSON data: {e}")
        return None


def save_items_data(
    items: List[Dict[str, Any]],
    merged_items: List[Dict[str, Any]],
    output_dir: str,
    input_file_name: str,
    name: Optional[str],
    time: Dict[str, str],
) -> Optional[str]:
    """Save a well-organized human-readable summary by category."""
    try:
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H")
        output_file = output_dir_path / f"{input_file_name}_Items_{timestamp}.txt"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Processed Data from {input_file_name}\n")
            f.write(f"Name: {name}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"First timestamp: {time['first_time']}\n")
            f.write("====================== Inventory Summary ======================\n\n")
            f.write(f"Found {len(items)} total item types.\n\n")

            # Totals
            gold_amount = sum(item["amount"] for item in merged_items if item.get("id") == "9999999999")
            doubloon_amount = sum(item["amount"] for item in merged_items if item.get("id") == "8888888888")
            total_amount = sum(item["amount"] for item in merged_items) - gold_amount - doubloon_amount

            f.write(f"Total amount of items (excluding gold and doubloons): {total_amount:,}\n\n")

            # Grouped output
            grouped = group_items_by_category(merged_items)
            
            for category, item_list in grouped.items():
                f.write(f"[{category}]\n")
                
                for item in item_list:
                    f.write(f"   {item['description']}: {item['amount']:,}\n")
                f.write("\n")

            f.write(f"Time played: {time['time_played']}\n")
            f.write("===============================================================\n")
            f.write(f"Last timestamp: {time['last_time']}\n")

        print(f"Data saved to: {output_file}")
        return str(output_file)

    except Exception as e:
        print(f"Error saving data to '{output_dir}': {e}")
        return None

def categorize_item(description: str) -> str:
    """Return a category for the item based on its description."""
    desc = description.lower().strip()

    # Weapons & Armor
    if any(x in desc for x in ["[locked down]"]):
        return "Equipment & Weapons"
    
    if any(x in desc for x in ["unidentified"]):
        return "Unidentified Items"
    
    # Maps
    if any(x in desc for x in ["treasure map", "fishing map", "skinning map", "ore map", "lumber map"]):
        return "Maps"
       
    # Resources - Metals & Wood & Leather
    if "ingot" in desc:
        return "Ingots"
    if any(w in desc for w in ["board", "wood board", "dullwood", "goldenwood", "shadowwood", "rosewood", "verewood", "valewood", "bronzewood", "copperwood", "avarwood"]):
        return "Boards"
    if any(w in desc for w in ["dullhide", "shadowhide", "copperhide", "bronzehide", "goldenhide", "rosehide", "verehide", "valehide", "avarhide"]):
        return "Leather"        
    
    # Aspects & Related
    if any(x in desc for x in ["aspect core", "aspect distillation", "phylactery", "chromatic core", "chromatic phylactery", "chromatic distillation"]):
        return "Aspects & Phylacteries"
    
    # Skill Mastery
    if "skill mastery" in desc:
        return "Skill Mastery"
    
    # Runes
    if "rune (" in desc:
        return "Runes"
    
    # Seeds
    if "seed" in desc:
        return "Seeds"
    
    # Collectables
    if "collectable card" in desc:
        return "Collectable Cards"
    if "mastery chain link" in desc:
        return "Mastery Chain Links"
    
    # Gems & Jewels
    if desc in {"amber", "amethyst", "citrine", "diamond", "emerald", "ruby", "sapphire", "star sapphire", "tourmaline"} or "gem" in desc:
        return "Gems"
    
    # Crafting Materials
    if any(x in desc for x in ["arcane essence", "research materials", "plant chemicals", "blank scroll", "an arcane scroll", "mastercrafting diagram"]):
        return "Crafting Materials"
    
    # Dyes & Cosmetics
    if any(x in desc for x in ["dye", "hue ", "rare cloth", "carpet dye", "headwear dye", "mount gear dye"]):
        return "Dyes & Rare Cloth" 
      
    # Gold & Currency
    if any(x in desc for x in ["gold", "doubloons"]):
        return "Gold & Currency"
    
    # Default
    return "Miscellaneous"


def group_items_by_category(items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group items by category and sort them nicely."""
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    for item in items:
        category = categorize_item(item["description"])
        grouped[category].append(item)
    
    # Sort categories and items within each category
    sorted_grouped = {}
    for category in sorted(grouped.keys()):
        sorted_items = sorted(grouped[category], key=lambda x: x["description"].lower())
        sorted_grouped[category] = sorted_items
    
    return sorted_grouped

def display_inventory_data(
    items: List[Dict[str, Any]],
    merged_items: List[Dict[str, Any]],
    name: Optional[str],
    time: Dict[str, str],
) -> None:
    """Print a nicely organized console summary by category."""
    print(f"Name: {name}")
    print(f"First timestamp: {time['first_time']}\n")
    print("====================== Inventory Summary ======================\n")
    print(f"Found {len(items)} total item types.\n")

    # Totals
    gold_amount = sum(item["amount"] for item in merged_items if item.get("id") == "9999999999")
    doubloon_amount = sum(item["amount"] for item in merged_items if item.get("id") == "8888888888")
    total_items = sum(item["amount"] for item in merged_items) - gold_amount - doubloon_amount

    print(f"Total amount of items (excluding gold and doubloons): {total_items:,}\n")

    # Group by category
    grouped = group_items_by_category(merged_items)

    for category, item_list in grouped.items():
        print(f"[{category}]")
        for item in item_list:
            print(f"   {item['description']}: {item['amount']:,}")
        print()  # blank line between categories

    print(f"Time played: {time['time_played']}")
    print("===============================================================")
    print(f"Last timestamp: {time['last_time']}\n")


def extract_time_played(file_path: str) -> Dict[str, str]:
    """Extract first/last timestamps and calculate total play time from the log."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            document = file.read()

        lines = [line.strip() for line in document.strip().split("\n") if line.strip()]
        if not lines:
            return {
                "first_time": "N/A",
                "last_time": "N/A",
                "time_played": "N/A",
            }

        # First timestamp
        first_line = lines[0]
        if not (first_line.startswith("[") and "]" in first_line):
            return {
                "first_time": "Invalid",
                "last_time": "Invalid",
                "time_played": "No valid timestamps",
            }
        first_ts_str = first_line.split("[", 1)[1].split("]", 1)[0]
        first_time = datetime.strptime(first_ts_str, "%m/%d/%Y %H:%M")

        # Last timestamp
        last_line = lines[-1]
        if not (last_line.startswith("[") and "]" in last_line):
            return {
                "first_time": "Invalid",
                "last_time": "Invalid",
                "time_played": "No valid timestamps",
            }
        last_ts_str = last_line.split("[", 1)[1].split("]", 1)[0]
        last_time = datetime.strptime(last_ts_str, "%m/%d/%Y %H:%M")

        time_diff = last_time - first_time
        total_minutes = int(time_diff.total_seconds() / 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60

        return {
            "first_time": first_time.strftime("%m/%d/%Y %H:%M"),
            "last_time": last_time.strftime("%m/%d/%Y %H:%M"),
            "time_played": f"{hours} hours and {minutes} minutes",
        }

    except Exception as e:
        print(f"Error extracting time from '{file_path}': {e}")
        return {
            "first_time": "Error",
            "last_time": "Error",
            "time_played": "Error",
        }


def main() -> None:
    """Main entry point: process ALL journal logs, generate outputs, and delete each file."""
    input_folder = Path(INPUT_FOLDER_PATH)
    if not input_folder.exists():
        print(f"Error: Input folder '{INPUT_FOLDER_PATH}' does not exist. Please check the path.")
        input("\nPress Enter to exit.")
        return

    all_files = get_all_outland_journal_files(str(input_folder))
    if not all_files:
        print("No further processing due to missing files or access issues.")
        input("\nPress Enter to exit.")
        return

    print(f"Found {len(all_files)} journal log file(s) to process.\n")

    processed_count = 0
    for file_path in all_files:
        print(f"\n{'='*70}")
        print(f"Processing file: {file_path}")
        base_name = Path(file_path).stem

        # Parse raw data
        data = process_items_data(file_path)

        if not data.get("items"):
            print(f" No items found in {file_path} possibly empty.")
            # Still delete it so the folder stays clean
            try:
                Path(file_path).unlink(missing_ok=True)
                print(f"   Empty file deleted: {file_path}")
            except Exception as e:
                print(f"   Could not delete file: {e}")
            continue

        # Merge (using the grouped unidentified style you prefer)
        merged_data_simple = merge_items(data, group_unidentified=True)

        name = data.get("name")
        raw_items = data.get("items", [])
        merged_items_simple = merged_data_simple["items"]

        time_info = extract_time_played(file_path)

        # Console summary
        display_inventory_data(raw_items, merged_items_simple, name, time_info)

        # Save outputs
        save_items_json(data, OUTPUT_DIRECTORY, base_name)
        save_items_data(raw_items, merged_items_simple, OUTPUT_DIRECTORY, base_name, name, time_info)

        # === DELETE THE PROCESSED FILE ===
        try:
            Path(file_path).unlink(missing_ok=True)
            print(f"\n Successfully processed and deleted: {file_path}")
        except Exception as e:
            print(f"\n Warning: Could not delete '{file_path}': {e}")

        processed_count += 1

    print(f"\n{'='*70}")
    print(f" Finished! Processed and deleted {processed_count} file(s).")
    print(f"All output files are in: {OUTPUT_DIRECTORY}")
    input("\nPress Enter to exit.")


if __name__ == "__main__":
    main()