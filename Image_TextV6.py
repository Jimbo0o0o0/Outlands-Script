from PIL import Image, ImageDraw, ImageFont
import os

# ==================== SETTINGS ====================
# Output directory
output_dir = r"C:/number_images/number_Texte"

# Number range (inclusive)
min_number = 1
max_number = 60

# Font settings
font_path = r"C:/number_images/Kanchenjunga-Bold.ttf"
font_size = 18

# Text colors (RGB, short name)
text_colors = [
    ((255, 255, 0), "Y"),   # Yellow
    # Add more colors here if needed, e.g. ((255, 0, 0), "R")
]

# Outline settings (set to None to disable)
outline_color = (0, 0, 0)      # Black outline (RGB). Set to None to disable
outline_width = 2              # Thickness of outline (1-4 recommended)

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

        text = str(number)

        # Get accurate text size
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # === Improved Centering ===
        text_x = (image_width - text_width) // 2
        text_y = (image_height - text_height) // 2 - 8  # Small vertical adjustment if needed

        # Draw outline first (if enabled)
        if outline_color is not None:
            draw.text(
                (text_x, text_y),
                text,
                font=font,
                fill=outline_color + (255,),
                stroke_width=outline_width,
                stroke_fill=outline_color + (255,)
            )

        # Draw main text
        draw.text(
            (text_x, text_y),
            text,
            font=font,
            fill=text_color + (255,)
        )

        # Save
        output_path = os.path.join(output_dir, f"{color_name}{number}.png")
        image.save(output_path, "PNG")
        print(f"Saved: {output_path}")

print(f"\nAll images generated successfully in '{output_dir}'")