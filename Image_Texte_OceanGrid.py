from PIL import Image, ImageDraw, ImageFont
import os

# ==================== SETTINGS ====================
output_dir = r"C:/number_images/number_Texte"
font_path = r"C:/number_images/Kanchenjunga-Bold.ttf"
font_size = 14

# Text color (Blue)
text_color = (0, 255, 255)
prefix = "Ocean"                    # Change if you want a different prefix

outline_color = (0, 0, 0)      # Set to None to disable outline
outline_width = 2
padding = 1                    # Increased slightly for safety +1 par front_size 10
offset_y = -1                  # -1 par front_size 10

# ==================== COMBINATIONS TO GENERATE ====================
numbers = list(range(1, 15))           # 1 to 14
letters = [chr(i) for i in range(ord('A'), ord('L') + 1)]  # A to L

# Generate all combinations: 1A, 1B, ..., 14L
all_combinations = [f"{num}{letter}" for num in numbers for letter in letters]
# =================================================

os.makedirs(output_dir, exist_ok=True)

# Load font
try:
    font = ImageFont.truetype(font_path, font_size)
    print(f"Font loaded: {font_path}")
except IOError as e:
    print(f"Font load failed: {e}")
    font = ImageFont.load_default()

print(f"Generating {len(all_combinations)} images...\n")

for combo in all_combinations:
    text = combo

    # Measure text for sizing
    temp_draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bbox = temp_draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Calculate image size
    extra = outline_width * 2 if outline_color is not None else 0
    image_width = text_width + 2 * padding + extra
    image_height = text_height + 2 * padding + extra

    # Create image
    image = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Center position
    center_x = image_width // 2
    center_y = image_height // 2 + offset_y

    # Draw outline
    if outline_color is not None:
        draw.text(
            (center_x, center_y),
            text,
            font=font,
            fill=outline_color + (255,),
            stroke_width=outline_width,
            stroke_fill=outline_color + (255,),
            anchor="mm"
        )

    # Draw main text
    draw.text(
        (center_x, center_y),
        text,
        font=font,
        fill=text_color + (255,),
        anchor="mm"
    )

    # Save
    output_path = os.path.join(output_dir, f"{prefix}{text}.png")
    image.save(output_path, "PNG")
    print(f"Saved: {output_path}  →  {image_width}x{image_height}px")

print(f"\n✅ All {len(all_combinations)} images generated successfully in '{output_dir}'")