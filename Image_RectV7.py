from PIL import Image, ImageDraw, ImageFont
import os

# ==================== SETTINGS ====================
output_dir = r"C:/number_images/number_Rectangle"
font_path = r"C:/number_images/Kanchenjunga-Bold.ttf"
font_size = 12

# Text color (Yellow)
text_color = (255, 255, 0)
prefix = "Re"

# Text outline
outline_color = (0, 0, 0)      # Set to None to disable
outline_width = 1

# Rectangle background
rect_color = (255, 0, 0)           # Red
rect_outline_color = (255, 255, 255)  # White (set to None to disable)
rect_outline_width = 2

rect_width_digits = 2              # Design width for 1 / 2 / 3 digits
rect_height_multiplier = 1.5       # Height relative to font size
rect_padding_multiplier = 0.75      # ← Simpler padding control (0.7 to 1.2 recommended)

rect_border_radius = 8             # Rounded corners (0 = sharp rectangle)

# General settings
regular_numbers = list(range(1, 29))
# =================================================

os.makedirs(output_dir, exist_ok=True)

# Load font
try:
    font = ImageFont.truetype(font_path, font_size)
    print(f"Font loaded: {font_path}")
except IOError as e:
    print(f"Font load failed: {e}")
    font = ImageFont.load_default()

# Calculate padding (now simplified)
padding = int(font_size * rect_padding_multiplier)

# Calculate fixed width based on desired number of digits
sample_text = "0" * rect_width_digits
temp_draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
bbox = temp_draw.textbbox((0, 0), sample_text, font=font)
sample_width = bbox[2] - bbox[0]

fixed_rect_width = sample_width + 2 * padding
fixed_rect_height = int(font_size * rect_height_multiplier)

for item in regular_numbers:
    text = str(item)
    
    # Final image size
    extra_outline = rect_outline_width * 2 if rect_outline_color is not None else 0
    image_width = fixed_rect_width + extra_outline + 8
    image_height = fixed_rect_height + extra_outline + 8
    
    # Create image
    image = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    center_x = image_width // 2
    center_y = image_height // 2   # offset_y removed
    
    # Rectangle coordinates
    rect_left = center_x - fixed_rect_width // 2
    rect_top = center_y - fixed_rect_height // 2
    rect_right = rect_left + fixed_rect_width
    rect_bottom = rect_top + fixed_rect_height
    
    rect_bbox = [rect_left, rect_top, rect_right, rect_bottom]
    
    # Draw rounded rectangle
    draw.rounded_rectangle(
        rect_bbox, 
        radius=rect_border_radius,
        fill=rect_color,
        outline=rect_outline_color if rect_outline_color is not None else None,
        width=rect_outline_width
    )
    
    # Draw text outline
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

print(f"\nAll images generated successfully in '{output_dir}'")