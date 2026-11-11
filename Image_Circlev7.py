from PIL import Image, ImageDraw, ImageFont
import os

# ==================== SETTINGS ====================
output_dir = r"C:/number_images/number_Circle"
font_path = r"C:/number_images/Kanchenjunga-Bold.ttf"
font_size = 12

# Text color (Black)
text_color = (0, 0, 0)
prefix = "Or"

# Text outline
outline_color = None #(0, 0, 0)      # Set to None to disable
outline_width = 1

# Circle background - 
circle_color = (255, 165, 0)           # Red
circle_outline_color = (255, 255, 255)  # White outline (set to None to disable)
circle_outline_width = 1
circle_size_multiplier = 1.8         # ← Main control: how big the circle is relative to font size
                                     # Try 2.4 - 2.8 range for good results

# General settings
off_x = 1
off_y = 0
regular_numbers = list(range(1, 9))
# =================================================

os.makedirs(output_dir, exist_ok=True)

# Load font
try:
    font = ImageFont.truetype(font_path, font_size)
    print(f"Font loaded: {font_path}")
except IOError as e:
    print(f"Font load failed: {e}")
    font = ImageFont.load_default()

# Calculate FIXED circle diameter based on font size
circle_diameter = int(font_size * circle_size_multiplier)

for item in regular_numbers:
    text = str(item)
    
    # Measure text size (for centering only)
    temp_draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bbox = temp_draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Final image size (square)
    extra_outline = circle_outline_width * 2 if circle_outline_color is not None else 0
    image_size = circle_diameter + extra_outline + 6  # small safety margin
    
    # Create image
    image = Image.new("RGBA", (image_size, image_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    center_x = image_size // 2
    center_y = image_size // 2
    
    # Draw circle background
    circle_bbox = [
        center_x - circle_diameter//2,
        center_y - circle_diameter//2,
        center_x + circle_diameter//2,
        center_y + circle_diameter//2
    ]
    
    # Circle fill
    draw.ellipse(circle_bbox, fill=circle_color)
    
    # Circle outline
    if circle_outline_color is not None:
        draw.ellipse(circle_bbox, 
                    outline=circle_outline_color, 
                    width=circle_outline_width)
    
    # Draw text outline (if enabled)
    if outline_color is not None:
        draw.text(
            (center_x + off_x, center_y + off_y),
            text,
            font=font,
            fill=outline_color + (255,),
            stroke_width=outline_width,
            stroke_fill=outline_color + (255,),
            anchor="mm"
        )
    
    # Draw main text
    draw.text(
        (center_x + off_x, center_y + off_y),
        text,
        font=font,
        fill=text_color + (255,),
        anchor="mm"
    )
    
    # Save
    output_path = os.path.join(output_dir, f"{prefix}{text}.png")
    image.save(output_path, "PNG")
    print(f"Saved: {output_path}  →  {image_size}x{image_size}px")

print(f"\nAll images generated successfully in '{output_dir}'")