from PIL import Image, ImageDraw, ImageFont
import os

# ==================== SETTINGS ====================
output_dir = r"C:/number_images/number_Texte_Cardinal"
font_path = r"C:/number_images/Kanchenjunga-Bold.ttf"
font_size = 20

# Text color (Blue)
text_color = (255,165,0)
prefix = "O"                    # Change if you want a different prefix

outline_color = None #(255, 255, 255)      # Set to None to disable outline
outline_width = 1

# === NEW: Text Highlight ===
text_highlight = True                    # Enable/disable highlight
text_highlight_color = (255, 255, 255, 255)    # Black with transparency (RGBA)
text_highlight_padding = 1               # Extra space around text
text_highlight_radius = 0                # Rounded corners of highlight

padding = 4                    # Increased slightly for safety +1 par front_size 10
offset_y = -2                  #  About -1 par front_size 10

# ==================== COMBINATIONS TO GENERATE ====================
#["N", "S", "E", "W", "NE", "NW", "SE", "SW"]
all_combinations =  ["Top Center", "Top Left", "Top Right", "Left", "Right", "Bottom Center", "Bottom Left", "Bottom Right"]
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
    
# === Draw Text Highlight ===
    if text_highlight:
        highlight_left = center_x - text_width//2 - text_highlight_padding - 2
        highlight_top = center_y - text_height//2 - text_highlight_padding - 2
        highlight_right = center_x + text_width//2 + text_highlight_padding
        highlight_bottom = center_y + text_height//2 + text_highlight_padding + 4
        
        draw.rounded_rectangle(
            [highlight_left, highlight_top, highlight_right, highlight_bottom],
            radius=text_highlight_radius,
            fill=text_highlight_color
        )
        
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