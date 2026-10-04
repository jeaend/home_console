from datetime import datetime
from PIL import ImageFont

def draw(draw, x=0, y=0, max_width=None, max_height=None):
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        updated_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except IOError:
        font = ImageFont.load_default()
        updated_font = font

    # Draw header text neatly within the slot coordinates
    draw.text((x, y), "Kindle Dashboard", fill=0, font=font)

    updated = f"Updated {datetime.now().strftime('%I:%M %p').lstrip('0')}"
    bbox = draw.textbbox((0, 0), updated, font=updated_font)
    updated_x = x + (max_width or 600) - (bbox[2] - bbox[0])
    draw.text((updated_x, y + 4), updated, fill=0, font=updated_font)
