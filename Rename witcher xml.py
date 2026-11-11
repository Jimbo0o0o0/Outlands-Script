import xml.etree.ElementTree as ET
import sys

def rename_treasure_icons(xml_file_path, output_file_path=None):
    """
    Renames all Icon="TREASURE" to Icon="Witcher {Name}" in the Witcher XML file.
    """
    if output_file_path is None:
        output_file_path = xml_file_path  # overwrite if not specified

    # Parse the XML
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Find all Marker elements
    count = 0
    for marker in root.findall('.//Marker'):
        name = marker.get('Name')
        icon = marker.get('Icon')
        
        if icon == 'TREASURE' and name:
            new_icon = f"Witcher{name}"
            marker.set('Icon', new_icon)
            count += 1
            print(f"Updated: {name} -> {new_icon}")

    # Write back to file
    tree.write(output_file_path, encoding='UTF-8', xml_declaration=True)
    print(f"\nSuccessfully updated {count} markers in {output_file_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python rename_witcher_icons.py <input_xml> [output_xml]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file
    
    rename_treasure_icons(input_file, output_file)