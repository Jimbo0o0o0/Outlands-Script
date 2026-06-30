from PIL import Image, ImageDraw, ImageFont
import os

# ==================== SETTINGS ====================
# Output directory
output_dir = r"C:/number_images/number_Circle"

# Number range (inclusive)
min_number = 1
max_number = 99

# Font settings
font_path = r"C:/number_images/Kanchenjunga-Bold.ttf"  # Update with correct path
font_size = 14

# Circle background colors (RGB, short name)
# These will be used as the fill color of the circle
circle_backgrounds = [
    ((255, 0, 0), "Re"),   # Red
    ((255, 165, 0), "Or"),  # Orange
    ((128, 0, 128), "Pu"), # Purple
]

# Circle outline settings
circle_outline_color = (255, 255, 255, 255)      # Black border
circle_outline_width = 2

# Text color - now fixed to black
text_color = (0, 0, 0, 255)   # Black text

# Circle size
circle_diameter = 24

# Image size
image_width, image_height = 31, 31
# =================================================

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load font
try:
    font = ImageFont.truetype(font_path, font_size)
    print(f"Font loaded successfully from {font_path}")
except IOError as e:
    print(f"Failed to load font from {font_path}: {e}")
    print("Falling back to default font")
    font = ImageFont.load_default()

# Generate images
for number in range(min_number, max_number + 1):
    for bg_color, color_name in circle_backgrounds:
        # Create new image with transparent background
        image = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw centered circle with background color
        circle_x = (image_width - circle_diameter) // 2
        circle_y = (image_height - circle_diameter) // 2
        
        draw.ellipse(
            [circle_x, circle_y, circle_x + circle_diameter, circle_y + circle_diameter],
            fill=bg_color,
            outline=circle_outline_color,
            width=circle_outline_width
        )

        # Prepare text (now black)
        text = str(number)

        # Get text size
        try:
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        except AttributeError:
            text_width, text_height = draw.textsize(text, font=font)

        # Center text
        text_x = (image_width - text_width) // 2
        text_y = (image_height - text_height) // 2 - 8

        # Draw black text
        draw.text((text_x, text_y), text, font=font, fill=text_color)

        # Save with color name + number
        output_path = os.path.join(output_dir, f"{color_name}{number}.png")
        image.save(output_path, "PNG")
        print(f"Saved: {output_path}")

print(f"\nAll images generated successfully in '{output_dir}'")