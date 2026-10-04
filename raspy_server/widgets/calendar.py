from PIL import ImageFont

def draw(draw, x=0, y=0, max_width=None, max_height=None):
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except IOError:
        font = ImageFont.load_default()
        title_font = font

    # Draw a bounding box outline for debugging if desired, constrained to max_width
    if max_width:
        draw.rectangle([x, y, x + max_width, y + (max_height or 300)], outline=0, width=1)

    draw.text((x + 10, y + 10), "Calendar / Schedule", fill=0, font=title_font)
    draw.text((x + 10, y + 50), "- 9:00 AM Standup", fill=0, font=font)
    draw.text((x + 10, y + 80), "- 1:00 PM Code Review", fill=0, font=font)