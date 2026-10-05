from datetime import datetime
from PIL import ImageFont

def draw(draw, x=0, y=0, max_width=None, max_height=None, battery=None):
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
    right = x + (max_width or 600)
    draw.text((right, y + 44), updated, fill=0, font=updated_font, anchor="rs")

    if battery is not None and 0 <= battery <= 100:
        level = f"{battery}%"
        level_right = right - draw.textlength(updated, font=updated_font) - 24
        draw.text((level_right, y + 44), level, fill=0, font=updated_font, anchor="rs")

        icon_right = level_right - draw.textlength(level, font=updated_font) - 8
        icon_left = icon_right - 34
        top, bottom = y + 28, y + 44
        draw.rectangle([icon_right, top + 5, icon_right + 3, bottom - 5], fill=0)
        draw.rectangle([icon_left, top, icon_right, bottom], outline=0, width=2)
        fill_width = round((icon_right - icon_left - 6) * battery / 100)
        if fill_width > 0:
            draw.rectangle([icon_left + 3, top + 3, icon_left + 3 + fill_width, bottom - 3], fill=0)
