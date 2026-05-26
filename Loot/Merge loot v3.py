import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import re
from typing import Dict, List, Optional, Tuple

# Constants
PROCESSED_FOLDER = Path(r"C:\Users\dcorr\Documents\Processed")

# Regex to extract the date portion (YYYY-MM-DD)
DATE_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2})")


def extract_timestamp(file_name: str) -> str:
    """Extract the YYYY-MM-DD date from a filename."""
    match = DATE_PATTERN.search(file_name)
    return match.group(1) if match else ""


def categorize_item(description: str) -> str:
    """Return a category for the item based on its description."""
    desc = description.lower().strip()

    # Weapons & Armor (identified + unidentified)
    if any(x in desc for x in ["[locked down]"]):
            return "Equipment & Weapons"
        
    if any(x in desc for x in ["unidentified"]):
            return "Unidentified Items"
    # Maps
    if any(x in desc for x in ["treasure map", "fishing map", "skinning map", "ore map", "lumber map"]):
        return "Maps"
       
        # Resources - Metals
    if ("ingot" in desc) and any(x in desc for x in ["ingot", "gold", "iron", "copper", "bronze", "shadow iron", "dull copper", "agapite", "avarite", "valorite", "verite"]):
        return "Ingots"
    
    if ("board" in desc) and any(w in desc for w in ["board", "dullwood", "goldenwood", "shadowwood", "rosewood", "verewood", "valewood", "bronzewood", "copperwood", "avarwood", "wood board"]):
        return "Boards"
    
    if any(w in desc for w in ["dullhide", "shadowhide", "copperhide", "bronzehide", "goldenhide", "rosehide", "verehide", "valehide", "avarhide"]):
        return "Leather"        
    
    # Aspects & Related
    if any(x in desc for x in ["aspect core", "aspect distillation", "phylactery", "chromatic core","chromatic phylactery", "chromatic distillation"]):
        return "Aspects & Phylacteries"
    
    # Skill Mastery
    if "skill mastery" in desc or "skill mastery orb" in desc:
        return "Skill Mastery"
    
    # Runes
    if "rune (" in desc:
        return "Runes"
    
    # Seeds
    if "seed" in desc:
        return "Seeds"
    
    # Collectable Cards
    if "collectable card" in desc:
        return "Collectable Cards"

    if "mastery chain link" in desc:
        return "Mastery Chain "
    
    # Gems & Jewels
    if desc in {"amber", "amethyst", "citrine", "diamond", "emerald", "ruby", "sapphire", "star sapphire", "tourmaline"} or "gem" in desc:
        return "Gems"
    
    # Resources - Other
    if any(x in desc for x in ["arcane essence", "research materials", "plant chemicals", "blank scroll", "an arcane scroll", "mastercrafting diagram"]):
        return "Crafting Materials"
    
    # Dyes & Cosmetics
    if any(x in desc for x in ["dye", "hue ", "rare cloth", "carpet dye", "headwear dye", "mount gear dye"]):
        return "Dyes & Rare Cloth" 
      
        # Gold & Currency
    if any(x in desc for x in ["gold", "doubloons"]):
        return "Gold & Currency"
    # Misc / Other
    return "Miscellaneous"


def merge_json_files(
    input_files: List[Path], output_json_file: Path, output_text_file: Path
) -> None:
    """Merge multiple inventory JSON files with categories in TXT output."""
    merged_items: defaultdict[str, int] = defaultdict(int)
    name: Optional[str] = None

    for file_path in input_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if name is None:
                name = data.get("name", "Merged Inventory")

            for item in data.get("items", []):
                description = item.get("description", "").strip()
                if description:
                    amount = int(item.get("amount", 0))
                    merged_items[description] += amount

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    if not merged_items:
        print("No items were found in any of the input files.")
        return

    # Group by category
    categorized: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
    
    for desc, amount in merged_items.items():
        category = categorize_item(desc)
        categorized[category].append((desc, amount))

    # Sort categories and items within categories
    sorted_categories = sorted(categorized.keys())
    for cat in sorted_categories:
        categorized[cat].sort(key=lambda x: x[0])

    # Write merged JSON (unchanged)
    new_items = [
        {"description": desc, "amount": amount}
        for desc, amount in sorted(merged_items.items())
    ]
    merged_data = {"name": name, "items": new_items}

    try:
        with open(output_json_file, "w", encoding="utf-8") as f:
            json.dump(merged_data, f, indent=4, ensure_ascii=False)
        print(f"Merged JSON written to: {output_json_file}")
    except Exception as e:
        print(f"Error writing JSON: {e}")

    # Write categorized text summary
    try:
        with open(output_text_file, "w", encoding="utf-8") as f:
            f.write("=== MERGED INVENTORY SUMMARY ===\n\n")
            total_items = sum(merged_items.values())
            f.write(f"Total unique item types: {len(merged_items)}\n")
            f.write(f"Total item count: {total_items}\n\n")

            for category in sorted_categories:
                items_in_cat = categorized[category]
                cat_total = sum(amount for _, amount in items_in_cat)
                
                f.write(f"[{category}] - {len(items_in_cat)} types, {cat_total} total\n")
                f.write("-" * 60 + "\n")
                
                for desc, amount in items_in_cat:
                    f.write(f"{desc}, Amount: {amount}\n")
                f.write("\n")
                
        print(f"Categorized text summary written to: {output_text_file}")
    except Exception as e:
        print(f"Error writing text file: {e}")


def main() -> None:
    if not PROCESSED_FOLDER.exists():
        print(f"Error: Folder '{PROCESSED_FOLDER}' does not exist.")
        return

    input_files = list(PROCESSED_FOLDER.glob("*_journal_Items_*.json"))
    if not input_files:
        print(f"No JSON files found in {PROCESSED_FOLDER}")
        return

    input_files.sort(key=lambda p: extract_timestamp(p.name))

    start = extract_timestamp(input_files[0].name)
    end = extract_timestamp(input_files[-1].name)

    output_json = PROCESSED_FOLDER / f"merged_inventory_{start}_to_{end}.json"
    output_txt = PROCESSED_FOLDER / f"merged_inventory_{start}_to_{end}.txt"

    print(f"Found {len(input_files)} files. Date range: {start} → {end}")
    merge_json_files(input_files, output_json, output_txt)


if __name__ == "__main__":
    main()