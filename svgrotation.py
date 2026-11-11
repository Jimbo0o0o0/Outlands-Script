import xml.etree.ElementTree as ET
import sys
import os

def rotate_svg(input_path, output_path, angle=45):
    """
    Rotate an SVG file by the given angle (in degrees) around its center.
    
    Args:
        input_path (str): Path to input SVG file
        output_path (str): Path for output SVG file
        angle (float): Rotation angle in degrees (default: 45)
    """
    # Parse the SVG file
    tree = ET.parse(input_path)
    root = tree.getroot()
    
    # SVG namespace
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    
    # Get dimensions
    width = float(root.get('width', '100'))
    height = float(root.get('height', '100'))
    
    # Handle viewBox if present
    viewbox = root.get('viewBox')
    if viewbox:
        try:
            _, _, w, h = map(float, viewbox.split())
            width = w
            height = h
        except:
            pass
    
    cx = width / 2
    cy = height / 2
    
    # Create a group element for rotation
    group = ET.Element('g')
    transform = f"translate({cx}, {cy}) rotate({angle}) translate(-{cx}, -{cy})"
    group.set('transform', transform)
    
    # Move all children into the group (except defs, which should stay at root)
    children_to_move = []
    for child in list(root):
        if child.tag != '{http://www.w3.org/2000/svg}defs':
            children_to_move.append(child)
    
    for child in children_to_move:
        root.remove(child)
        group.append(child)
    
    # Add the group to the root
    root.append(group)
    
    # Write the output
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    
    print(f"✅ SVG rotated by {angle}° and saved to: {output_path}")
    print(f"   Center of rotation: ({cx:.1f}, {cy:.1f})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python rotate_svg.py <input.svg> [output.svg] [angle]")
        print("Example: python rotate_svg.py logo.svg logo_rotated.svg 45")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.svg', '_rotated.svg')
    angle = float(sys.argv[3]) if len(sys.argv) > 3 else 45
    
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    
    rotate_svg(input_file, output_file, angle)