from datetime import datetime
from PIL import ImageFont

def draw(draw, x=0, y=0, max_width=None, max_height=None):
    try:
        font = ImageFont.truetype("/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf", 44)
        updated_font = ImageFont.truetype("/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf", 22)
    except IOError:
        font = ImageFont.load_default()
        updated_font = font

    now = datetime.now()
    day = now.day
    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

    # Draw header text neatly within the slot coordinates
    draw.text((x, y + 44), f"{now.strftime('%A, %B')} {day}{suffix}", fill=0, font=font, anchor="ls")

    updated = f"Updated {now.strftime('%I:%M %p').lstrip('0')}"
    draw.text((x + (max_width or 600), y + 44), updated, fill=0, font=updated_font, anchor="rs")
