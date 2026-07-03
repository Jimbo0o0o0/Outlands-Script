from PIL import Image, ImageDraw, ImageFont
import os

# ==================== SETTINGS ====================
output_dir = r"C:/number_images/number_Texte"
font_path = r"C:/number_images/Kanchenjunga-Bold.ttf"
font_size = 14

text_colors = [
    ((255, 255, 0), "Witcher"),
]

outline_color = (0, 0, 0)      # Set to None to disable
outline_width = 2
padding = 1                    # Increased slightly for safety +1 par front_size 10

regular_numbers = list(range(1, 353))
special_cases = ["4a", "22a", "44a", "80a", "81a", "104a", "106a"]
# =================================================

os.makedirs(output_dir, exist_ok=True)

# Load font
try:
    font = ImageFont.truetype(font_path, font_size)
    print(f"Font loaded: {font_path}")
except IOError as e:
    print(f"Font load failed: {e}")
    font = ImageFont.load_default()

all_items = regular_numbers + special_cases

for item in all_items:
    for text_color, color_name in text_colors:
        text = str(item)

        # Measure text for canvas size
        temp_draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate final image size
        extra = outline_width * 2 if outline_color is not None else 0
        image_width = text_width + 2 * padding + extra
        image_height = text_height + 2 * padding + extra

        # Create image
        image = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Center position (middle of the image)
        center_x = image_width // 2
        center_y = image_height // 2 - 1 # -1 par front_size 10

        # Draw outline first
        if outline_color is not None:
            draw.text(
                (center_x, center_y),
                text,
                font=font,
                fill=outline_color + (255,),
                stroke_width=outline_width,
                stroke_fill=outline_color + (255,),
                anchor="mm"          # Magic: Perfect center
            )

        # Draw main text
        draw.text(
            (center_x, center_y),
            text,
            font=font,
            fill=text_color + (255,),
            anchor="mm"              # Perfect auto-centering
        )

        # Save
        output_path = os.path.join(output_dir, f"{color_name}{text}.png")
        image.save(output_path, "PNG")
        print(f"Saved: {output_path}  →  {image_width}x{image_height}px")

print(f"\n All images generated successfully in '{output_dir}'")