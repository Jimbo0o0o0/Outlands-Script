from PIL import Image, ImageDraw, ImageFont
import os

# ==================== SETTINGS ====================
# Output directory
output_dir = r"C:/number_images/number_Rectangle"

# Number range (inclusive)
min_number = 1
max_number = 99

# Font settings
font_path = r"C:/number_images/Kanchenjunga-Bold.ttf"  # Update with correct path
font_size = 16

# Text colors (RGB, short name)
text_colors = [
    #((255, 255, 0), "Y"),   # Yellow
    #((0, 255, 255), "B"),   # Blue (Cyan)
    ((255, 0, 0), "Re"),   # Red
    #((85, 255, 85), "G"),   # Green
    ((255, 165, 0), "Or"),  # Orange
    ((128, 0, 128), "Pu"), # Purple
]

# Rectangle settings
rect_width, rect_height = 25, 17
rect_fill_color = (0, 0, 0, 255)   #  Black

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
    for text_color, color_name in text_colors:
        # Create new image with transparent background
        image = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw rectangle centered
        rect_x = (image_width - rect_width) // 2
        rect_y = (image_height - rect_height) // 2
        draw.rectangle(
            [(rect_x, rect_y), (rect_x + rect_width - 1, rect_y + rect_height - 1)],
            fill=rect_fill_color
        )

        # Prepare text
        text = str(number)

        # Get text size
        try:
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        except AttributeError:
            text_width, text_height = draw.textsize(text, font=font)

        # Center text horizontally, shift up a bit
        text_x = (image_width - text_width) // 2
        text_y = (image_height - text_height) // 2 - 9

        # Draw colored text
        draw.text((text_x, text_y), text, font=font, fill=text_color + (255,))

        # Save
        output_path = os.path.join(output_dir, f"{color_name}{number}.png")
        image.save(output_path, "PNG")
        print(f"Saved: {output_path}")

print(f"\nAll images generated successfully in '{output_dir}'")