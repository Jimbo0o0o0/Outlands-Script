import os
from datetime import datetime
import json
# TODO fix 'stacked potion keg:'
def get_newest_outland_journal_file(folder_path):
    try:
        text_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
        if not text_files:
            print(f"No .txt files found in {folder_path}")
            return None
        
        newest_file = max(text_files,key=lambda f: os.path.getmtime(os.path.join(folder_path, f)))
        return os.path.join(folder_path, newest_file)
    except FileNotFoundError:
        print(f"Error: The folder '{folder_path}' does not exist.")
        return None
    except PermissionError:
        print(f"Error: Permission denied to access '{folder_path}'.")
        return None
    except Exception as e:
        print(f"Error accessing folder '{folder_path}': {e}")
        return None

def get_latest_vendors_file(folder_path, filter_tag=None):
    try:
        # List files that contain "processed" and end with .json, optionally filtering by filter_tag
        if filter_tag is None:
            files = [f for f in os.listdir(folder_path) if "processed" in f and f.endswith(".json")]
        else:
            files = [f for f in os.listdir(folder_path) if "processed" in f and filter_tag in f and f.endswith(".json")]
        
        if not files:
            print(f"No .txt files found in {folder_path}")
            return
            # Find the file with the latest modification time
        latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(folder_path, x)))
        return os.path.join(folder_path, latest_file)
    except FileNotFoundError:
        print(f"Error: The folder '{folder_path}' does not exist.")
        return None
    except PermissionError:
        print(f"Error: Permission denied to access '{folder_path}'.")
        return None
    except Exception as e:
        print(f"Error accessing folder '{folder_path}': {e}")
        return None

def process_vendor_data(file_path):
    vendors = []
    current_vendor = None
    in_scan_section = False

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                # Démarrage de la section de scan
                if "[Razor]: …OutlandMall Start" in line:
                    in_scan_section = True
                    continue

                if "[Razor]: …OutlandMall End" in line:
                    in_scan_section = False
                    #break  # Stop processing completely

                # If not in scan section, ignore the line
                    if not in_scan_section:
                        continue

                if in_scan_section:
                    # Détection du début d'un vendeur
                    if "[Razor]: …vendorStart" in line:
                        parts = line.split()
                        # Vérifier qu'on a bien au moins 6 éléments (par exemple : "[Razor]:", "Start", "<timestamp>", "<ID>", "<vendor_id>", "<vendor_name>")
                        if len(parts) < 6:
                            print(f"Error at line {line_num}: Malformed vendor start line: {line}")
                            continue
                        vendor_id = parts[4]
                        vendor_name = " ".join(parts[5:]).strip()
                        current_vendor = {"id": vendor_id, "name": vendor_name, "location": None, "items": []}
                        continue

                    # Fin d'un vendeur
                    if "[Razor]: …vendorEnd" in line and current_vendor:
                        vendors.append(current_vendor)
                        current_vendor = None
                        continue

                    # Extraction de la localisation
                    if "System: Current location is" in line and current_vendor:
                        _, _, location = line.partition("System: Current location is")
                        if not location.strip():
                            print(f"Error at line {line_num}: Malformed location line: {line}")
                            continue
                        current_vendor["location"] = location.strip()
                        continue

                    # Extraction des articles
                    if "[Razor]: …item" in line and current_vendor:
                        if "Not for sale" in line:
                            continue  # Ignore the line if it contains 'Not for sale'
                        # Filtre les tags inutiles
                        line = line.replace("(used to increase a player's total skill cap by 1)", "")
                        line = line.replace("(used to increase a player's skill cap for a skill by 1)", "")
                        line = line.replace("[double click to place]", "")
                        line = line.replace("(0 items, 0 stones)", "")
                        line = line.replace("(double-click to activate)", "")
                        line = line.replace("(double-click to research)", "")
                        # Vérifier si la ligne contient "|| Stack Price:" ou "|| Price:"
                        if " Stack Price:" in line:
                            parts = line.split(" Stack Price:")
                            is_stack = True
                        elif " Price:" in line:
                            parts = line.split(" Price:")
                            is_stack = False
                        else:
                            print(f"Error at line {line_num}: Missing price information in item line: {line}")
                            continue

                        item_id_part = parts[0].strip().split()
                        if len(item_id_part) < 4:
                            print(f"Error at line {line_num}: Malformed item ID in line: {line}")
                            continue
                        item_id = item_id_part[5]  # Ajuster l'indice selon le format réel

                        price_desc = parts[1].strip()

                        if is_stack:
                            # Traitement spécifique pour les lignes contenant "Stack Price:"
                            stack_parts = price_desc.split(" each ", 1)
                            if len(stack_parts) < 2:
                                print(f"Error at line {line_num}: Malformed stack price line: {line}")
                                continue
                            stack_price = stack_parts[0].strip().replace(",", "")
                            desc_amount = stack_parts[1].strip()
                            
                            extra_info = ""
                            if "(" in desc_amount and ")" in desc_amount:
                                start = desc_amount.index("(")
                                end = desc_amount.index(")")
                                extra_info = desc_amount[start:end+1].strip()
                                desc_amount = desc_amount[:start].strip() + desc_amount[end+1:].strip()
                                
                            if "[" in desc_amount and "]" in desc_amount:
                                start = desc_amount.index("[")
                                end = desc_amount.index("]")
                                extra_info = desc_amount[start:end+1].strip()
                                desc_amount = desc_amount[:start].strip() + desc_amount[end+1:].strip()
                                
                            if " : " in desc_amount:
                                description, amount = desc_amount.split(" : ", 1)
                                description = description.strip()
                                amount = amount.strip()
                            else:
                                description = desc_amount
                                amount = "1"  # Valeur par défaut si aucune quantité n'est spécifiée
                                
                            if extra_info:
                                description += f" {extra_info}"
                                    
                            item = {
                                "id": item_id,
                                "stack_price": stack_price,
                                "description": description,
                                "amount": amount
                            }
                        else:
                            # Traitement pour les lignes contenant "Price:"
                            price_parts = price_desc.split(maxsplit=1)
                            if len(price_parts) < 2:
                                print(f"Error at line {line_num}: Missing price/description in line: {line}")
                                continue
                            price = price_parts[0].replace(",", "")
                            desc_amount = price_parts[1].strip()
                            
                            extra_info = ""
                            if "(" in desc_amount and ")" in desc_amount:
                                start = desc_amount.index("(")
                                end = desc_amount.index(")")
                                extra_info = desc_amount[start:end+1].strip()
                                desc_amount = desc_amount[:start].strip() + desc_amount[end+1:].strip()
                                
                            if "[" in desc_amount and "]" in desc_amount:
                                start = desc_amount.index("[")
                                end = desc_amount.index("]")
                                extra_info = desc_amount[start:end+1].strip()
                                desc_amount = desc_amount[:start].strip() + desc_amount[end+1:].strip()
                            
                            if " : " in desc_amount:
                                description, amount = desc_amount.split(" : ", 1)
                                description = description.strip()
                                amount = amount.strip()
                            else:
                                description = desc_amount
                                amount = "1"  # Valeur par défaut si aucune quantité n'est spécifiée
                                
                            if extra_info:
                                description += f" {extra_info}"
                                    
                            item = {
                                "id": item_id,
                                "price": price,
                                "description": description,
                                "amount": amount
                            }
                        current_vendor["items"].append(item)

        return vendors
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return []
    except PermissionError:
        print(f"Error: Permission denied to read '{file_path}'.")
        return []
    except Exception as e:
        print(f"Error processing file '{file_path}': {e}")
        return []

def save_vendor_data(vendors, output_dir, input_file_name):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H")
        output_file = os.path.join(output_dir, f"{input_file_name}_processed_{timestamp}.txt")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Processed Vendor Data from {input_file_name}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for vendor in vendors:
                f.write(f"Vendor: {vendor['name']} (ID: {vendor['id']})\n")
                f.write(f"Location: {vendor['location']}\n")
                f.write("Inventory:\n")
                if vendor['items']:
                    for item in vendor['items']:
                        if "stack_price" in item:
                            f.write(f"  - Item (ID: {item['id']}) {item['description']}, Amount: {item['amount']}, Stack Price: {item['stack_price']}\n")
                        else:
                            f.write(f"  - Item (ID: {item['id']}) {item['description']}, Amount: {item['amount']}, Price: {item['price']}\n")
                else:
                    f.write("  No items listed\n")
                f.write("-" * 50 + "\n")
        
        print(f"Data saved to: {output_file}")
        return output_file
    except PermissionError:
        print(f"Error: Permission denied to write to '{output_dir}'.")
        return None
    except Exception as e:
        print(f"Error saving data to '{output_dir}': {e}")
        return None
    
def save_inventory_data(inventory_summary, total_inventory_value, output_dir, input_file_name):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H")   
        output_file = os.path.join(output_dir, f"{input_file_name}_inventory_summary_{timestamp}.txt")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Processed Vendor Data from {input_file_name}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("====================== Inventory Summary ======================\n\n")
            for description, details in inventory_summary.items():
                prices_str = ', '.join(str(p) for p in details['prices'])
                f.write(f"- Item {description}, Total Amount: {details['amount']}, Prices: [{prices_str}], Average Price: {details['avg_unit_price']:.1f}, Total Value: {details['total_value']}\n")
            
            f.write(f"\nOverall Total Value: {total_inventory_value}\n")
            f.write("\n===============================================================")

        print(f"Data saved to: {output_file}")
        return output_file

    except PermissionError:
        print(f"Error: Permission denied to write to '{output_dir}'.")
        return None
    except Exception as e:
        print(f"Error saving data to '{output_dir}': {e}")
        return None
    
def display_vendor_data(vendors):
    for vendor in vendors:
        print(f"\nVendor: {vendor['name']} (ID: {vendor['id']})")
        print(f"Location: {vendor['location']}")
        print("Inventory:")
        if vendor['items']:
            for item in vendor['items']:
                if "stack_price" in item:
                    print(f"  - Item (ID: {item['id']}) {item['description']}, Amount: {item['amount']}, Stack Price: {item['stack_price']}")
                else:
                    print(f"  - Item (ID: {item['id']}) {item['description']}, Amount: {item['amount']}, Price: {item['price']}")
        else:
            print("  No items listed")
        print("-" * 50)
   
   
def display_inventory_data(inventory_summary, total_inventory_value):
    print("\n====================== Inventory Summary ======================\n")
    for description, details in inventory_summary.items():
        print(f"- Item {description}, Total Amount: {details['amount']}, Prices: {details['prices']}, Average Unit Price: {details['avg_unit_price']:.1f}, Total Value: {details['total_value']}")

    print(f"\nOverall Total Value: {total_inventory_value}")
    print("\n===============================================================")
        
def print_vendor_changes(changes):
    print("\n=== Vendor Comparison Results ===")
    
    # Check if there are any changes to report
    if not (changes["added_vendors"] or changes["removed_vendors"] or changes["item_changes"]):
        print("No changes detected.")
        return
    
    # Added Vendors
    if changes["added_vendors"]:
        print("\nAdded Vendors:")
        for vendor in changes["added_vendors"]:
            print(f"  - {vendor['name']} (ID: {vendor['id']})")
            print(f"    Location: {vendor['location']}")
            if vendor["items"]:
                print("    Items:")
                for item in vendor["items"]:
                    if "stack_price" in item:
                        print(f"      - (ID: {item['id']}) {item['description']}, Amount: {item['amount']}, Stack Price: {item['stack_price']}")
                    else:
                        print(f"      - (ID: {item['id']}) {item['description']}, Amount: {item['amount']}, Price: {item['price']}")
            else:
                print("    Items: None")
    
    # Removed Vendors
    if changes["removed_vendors"]:
        print("\nRemoved Vendors:")
        for vendor in changes["removed_vendors"]:
            print(f"  - {vendor['name']} (ID: {vendor['id']})")
            print(f"    Location: {vendor['location']}")
            if vendor["items"]:
                print("    Items:")
                for item in vendor["items"]:
                    if "stack_price" in item:
                        print(f"      - (ID: {item['id']}) {item['description']}, Amount: {item['amount']}, Stack Price: {item['stack_price']}")
                    else:
                        print(f"      - (ID: {item['id']}) {item['description']}, Amount: {item['amount']}, Price: {item['price']}")
            else:
                print("    Items: None")
    
    # Item Changes
    if changes["item_changes"]:
        print("\nItem Changes:")
        for vendor_id, vendor_changes in changes["item_changes"].items():
            # Find the vendor name from either added or remaining vendors (assuming new_vendors is available)
            # For simplicity, we'll just use the ID here; you could pass new_vendors to look up names
            print(f"\n  Vendor ID: {vendor_id}")
            
            if vendor_changes["added_items"]:
                print("    Added Items:")
                for item in vendor_changes["added_items"]:
                    if "stack_price" in item:
                        print(f"      - (ID: {item['id']}) {item['description']}, Amount: {item['amount']}, Stack Price: {item['stack_price']}")
                    else:
                        print(f"      - (ID: {item['id']}) {item['description']}, Amount: {item['amount']}, Price: {item['price']}")
            
            if vendor_changes["removed_items"]:
                print("    Removed Items:")
                for item in vendor_changes["removed_items"]:
                    if "stack_price" in item:
                        print(f"      - (ID: {item['id']}) {item['description']}, Amount: {item['amount']}, Stack Price: {item['stack_price']}")
                    else:
                        print(f"      - (ID: {item['id']}) {item['description']}, Amount: {item['amount']}, Price: {item['price']}")
            
            if vendor_changes["changed_items"]:
                print("    Changed Items:")    
                for change in vendor_changes["changed_items"]:
                    old_price = change['old'].get('price', change['old'].get('stack_price'))
                    new_price = change['new'].get('price', change['new'].get('stack_price'))
                    print(f"      - Item ID: {change['item_id']}")
                    print(f"        Old: {change['old']['description']}, Amount: {change['old']['amount']}, Price: {old_price}")
                    print(f"        New: {change['new']['description']}, Amount: {change['new']['amount']}, Price: {new_price}")
 
def save_vendor_data_json(vendors, output_dir, input_file_name):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H") 
        output_file = os.path.join(output_dir, f"{input_file_name}_processed_{timestamp}.json")

        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(vendors, json_file, indent=4, ensure_ascii=False)

        print(f"JSON Data saved to: {output_file}")
        return output_file
    except Exception as e:
        print(f"Error saving JSON data: {e}")
        return None
    
def summarize_inventory(vendors):
    inventory_summary = {}
    total_value = 0

    for vendor in vendors:
        for item in vendor["items"]:
            description = item["description"]
            # Determine price based on stack_price or price
            if "stack_price" in item:
                price = int(item["stack_price"].replace(",", ""))
            else:
                price_total = int(item.get("price", "0").replace(",", ""))
                amount_temp = int(item.get("amount", "1").replace(",", ""))
                price = int(price_total / amount_temp) if amount_temp != 0 else price_total

            amount = int(item.get("amount", "1").replace(",", ""))
            item_total_value = price * amount
            total_value += item_total_value

            if description in inventory_summary:
                # Update existing entry
                inventory_summary[description]["amount"] += amount
                inventory_summary[description]["total_value"] += item_total_value
                # Track multiple prices if they differ
                if price not in inventory_summary[description]["prices"]:
                    inventory_summary[description]["prices"].append(price)
            else:
                # Create new entry
                inventory_summary[description] = {
                    "amount": amount,
                    "prices": [price],  # List to store different prices
                    "total_value": item_total_value
                }

    # Optional: Calculate average price per item after processing
    for description in inventory_summary:
        prices = inventory_summary[description]["prices"]
        inventory_summary[description]["avg_unit_price"] = (
            sum(prices) / len(prices) if prices else 0
        )

    return inventory_summary, total_value

def save_inventory_json(inventory_summary, total_value, output_dir, input_file_name):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H")
        output_file = os.path.join(output_dir, f"{input_file_name}_inventory_summary_{timestamp}.json")
        
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump({"inventory": inventory_summary, "total_value": total_value}, json_file, indent=4, ensure_ascii=False)
        
        print(f"Inventory JSON saved to: {output_file}")
        return output_file
    except Exception as e:
        print(f"Error saving inventory JSON: {e}")
        return None
    
def save_vendor_changes(changes, output_dir, input_file_name):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H")
        output_file = os.path.join(output_dir, f"{input_file_name}_changes_{timestamp}.txt")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Old Vendor Data from {input_file_name}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("=== Vendor Comparison Results ===\n")
            
            # Check if there are any changes to report
            if not (changes["added_vendors"] or changes["removed_vendors"] or changes["item_changes"]):
                f.write("No changes detected.\n")
            else:
                # Added Vendors
                if changes["added_vendors"]:
                    f.write("\nAdded Vendors:\n")
                    for vendor in changes["added_vendors"]:
                        f.write(f"  - {vendor['name']} (ID: {vendor['id']})\n")
                        f.write(f"    Location: {vendor['location']}\n")
                        if vendor["items"]:
                            f.write("    Items:\n")
                            for item in vendor["items"]:
                                if "stack_price" in item:
                                    f.write(f"      - (ID: {item['id']}) {item['description']}, Amount: {item['amount']}, Stack Price: {item['stack_price']}\n")
                                else:
                                    f.write(f"      - (ID: {item['id']}) {item['description']}, Amount: {item['amount']}, Price: {item['price']}\n")
                        else:
                            f.write("    Items: None\n")
                
                # Removed Vendors
                if changes["removed_vendors"]:
                    f.write("\nRemoved Vendors:\n")
                    for vendor in changes["removed_vendors"]:
                        f.write(f"  - {vendor['name']} (ID: {vendor['id']})\n")
                        f.write(f"    Location: {vendor['location']}\n")
                        if vendor["items"]:
                            f.write("    Items:\n")
                            for item in vendor["items"]:
                                if "stack_price" in item:
                                    f.write(f"      - (ID: {item['id']}) {item['description']}, Amount: {item['amount']}, Stack Price: {item['stack_price']}\n")
                                else:
                                    f.write(f"      - (ID: {item['id']}) {item['description']}, Amount: {item['amount']}, Price: {item['price']}\n")
                        else:
                            f.write("    Items: None\n")
                
                # Item Changes
                if changes["item_changes"]:
                    f.write("\nItem Changes:\n")
                    for vendor_id, vendor_changes in changes["item_changes"].items():
                        f.write(f"\n  Vendor ID: {vendor_id}\n")
                        
                        if vendor_changes["added_items"]:
                            f.write("    Added Items:\n")
                            for item in vendor_changes["added_items"]:
                                if "stack_price" in item:
                                    f.write(f"      - (ID: {item['id']}) {item['description']}, Amount: {item['amount']}, Stack Price: {item['stack_price']}\n")
                                else:
                                    f.write(f"      - (ID: {item['id']}) {item['description']}, Amount: {item['amount']}, Price: {item['price']}\n")
                        
                        if vendor_changes["removed_items"]:
                            f.write("    Removed Items:\n")
                            for item in vendor_changes["removed_items"]:
                                if "stack_price" in item:
                                    f.write(f"      - (ID: {item['id']}) {item['description']}, Amount: {item['amount']}, Stack Price: {item['stack_price']}\n")
                                else:
                                    f.write(f"      - (ID: {item['id']}) {item['description']}, Amount: {item['amount']}, Price: {item['price']}\n")
                        
                        if vendor_changes["changed_items"]:
                            f.write("    Changed Items:\n")
                            for change in vendor_changes["changed_items"]:
                                old_price = change['old'].get('price', change['old'].get('stack_price'))
                                new_price = change['new'].get('price', change['new'].get('stack_price'))
                                f.write(f"      - Item ID: {change['item_id']}\n")
                                f.write(f"        Old: {change['old']['description']}, Amount: {change['old']['amount']}, Price: {old_price}\n")
                                f.write(f"        New: {change['new']['description']}, Amount: {change['new']['amount']}, Price: {new_price}\n")

        print(f"Changes saved to: {output_file}")
        return output_file
    
    except PermissionError:
        print(f"Error: Permission denied to write to '{output_dir}'.")
        return None
    except Exception as e:
        print(f"Error saving changes to '{output_dir}': {e}")
        return None
   
def save_vendor_changes_json(changes, output_dir, input_file_name):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H") 
        output_file = os.path.join(output_dir, f"{input_file_name}_changes_{timestamp}.json")

        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(changes, json_file, indent=4, ensure_ascii=False)

        print(f"JSON Data saved to: {output_file}")
        return output_file
    except Exception as e:
        print(f"Error saving JSON data: {e}")
        return None
    
def compare_vendors(new_vendors, old_file_path):
    # Load old vendors from the JSON file
    try:
        with open(old_file_path, 'r', encoding='utf-8') as f:
            old_vendors = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find file '{old_file_path}'. Assuming no previous data.")
        old_vendors = []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in '{old_file_path}'. Assuming no previous data.")
        old_vendors = []
    except Exception as e:
        print(f"Error loading '{old_file_path}': {e}")
        old_vendors = []

    # Convert lists to dictionaries for easier lookup by vendor ID
    new_vendors_dict = {v["id"]: v for v in new_vendors}
    old_vendors_dict = {v["id"]: v for v in old_vendors}

    # Results dictionary
    comparison = {
        "added_vendors": [],
        "removed_vendors": [],
        "item_changes": {}  # Vendor ID -> list of item changes
    }

    # Check for added vendors (in new but not old)
    for vendor_id in new_vendors_dict:
        if vendor_id not in old_vendors_dict:
            comparison["added_vendors"].append(new_vendors_dict[vendor_id])

    # Check for removed vendors (in old but not new)
    for vendor_id in old_vendors_dict:
        if vendor_id not in new_vendors_dict:
            comparison["removed_vendors"].append(old_vendors_dict[vendor_id])

    # Compare items for vendors present in both
    for vendor_id in new_vendors_dict:
        if vendor_id in old_vendors_dict:
            new_items = {item["id"]: item for item in new_vendors_dict[vendor_id]["items"]}
            old_items = {item["id"]: item for item in old_vendors_dict[vendor_id]["items"]}

            vendor_changes = {
                "added_items": [],
                "removed_items": [],
                "changed_items": []
            }

            # Check for added items
            for item_id in new_items:
                if item_id not in old_items:
                    vendor_changes["added_items"].append(new_items[item_id])

            # Check for removed items
            for item_id in old_items:
                if item_id not in new_items:
                    vendor_changes["removed_items"].append(old_items[item_id])

            # Check for changed items
            for item_id in new_items:
                if item_id in old_items:
                    new_item = new_items[item_id]
                    old_item = old_items[item_id]
                    if new_item != old_item:  # Compare entire item dict
                        vendor_changes["changed_items"].append({
                            "item_id": item_id,
                            "old": old_item,
                            "new": new_item
                        })

            # Only add to results if there are changes
            if vendor_changes["added_items"] or vendor_changes["removed_items"] or vendor_changes["changed_items"]:
                comparison["item_changes"][vendor_id] = vendor_changes

    return comparison    
      
def main():
    input_folder_path = r"C:\Program Files (x86)\Ultima Online Outlands\ClassicUO\Data\Client\JournalLogs"
    output_directory = os.path.join(r"C:\Users\dcorr\Documents", "Processed")
    
    if not os.path.exists(input_folder_path):
        print(f"Error: Input folder '{input_folder_path}' does not exist. Please check the path.")
        return

    newest_file = get_newest_outland_journal_file(input_folder_path)
    if not newest_file:
        print("No further processing due to missing files or access issues.")
        return

    print(f"Processing file: {newest_file}")
    base_name = os.path.splitext(os.path.basename(newest_file))[0]
    
    vendors = process_vendor_data(newest_file)
    if vendors is None:
        print("Processing failed. Check error messages above.")
        return
    
    # Optional: Comment out the following lines to skip displaying the data
    display_vendor_data(vendors)
    
    # Optional: Filter vendors by a specific tag
    filter_tag=None # "A+"
    
    if filter_tag:
        vendors[:] = [vendor for vendor in vendors if filter_tag in vendor["name"]]
        base_name += f"_{filter_tag}"
     
    inventory_summary, total_inventory_value = summarize_inventory(vendors)
    #if inventory_summary is None:
    #    print("Error: Failed to summarize inventory.")
    #    return 
        
    # Optional: Comment out the following lines to skip displaying the data
    display_inventory_data(inventory_summary, total_inventory_value)
    
    latest_file = get_latest_vendors_file(output_directory, filter_tag)
    #if not latest_file:
    #    print("No previous file to compare with.")
    #    return
    
    changes = compare_vendors(vendors, latest_file)
    # Optional: Comment out the following lines to skip displaying the data
    print_vendor_changes(changes)
           
    saved_file = save_vendor_data(vendors, output_directory, base_name)
    #if not saved_file:
    #    print("Failed to save the data. Check error messages above.")
    #    return
    
    json_file = save_vendor_data_json(vendors, output_directory, base_name)
    #if not json_file:
    #    print("Failed to save the JSON data. Check error messages above.")
    #    return
    
    inventory_json = save_inventory_json(inventory_summary, total_inventory_value, output_directory, base_name)
    #if not inventory_json:
    #    print("Failed to save the inventory summary. Check error messages above.")
    #    return
    
    inventory_data = save_inventory_data(inventory_summary, total_inventory_value, output_directory, base_name)
    #if not inventory_data:
    #    print("Failed to save the inventory summary. Check error messages above.")
    #    return

    changes_file = save_vendor_changes(changes, output_directory, base_name)
    #if not changes_file:
    #    print("Failed to save the changes. Check error messages above.")
    #    return
    
    change_json = save_vendor_changes_json(changes, output_directory, base_name)
    #if not change_json:
    #    print("Failed to save the JSON changes. Check error messages above.")
    #    return
        
if __name__ == "__main__":
    main()
    