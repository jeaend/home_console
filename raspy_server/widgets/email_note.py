import json
import os
from PIL import ImageFont

def draw(draw, x=0, y=0, max_width=None, max_height=None):
    box_width = max_width or 600
    box_height = max_height or 140
    
    # Outer box border
    draw.rectangle([x, y, x + box_width, y + box_height], outline=0, width=2)

    try:
        subject_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        meta_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except IOError:
        subject_font = ImageFont.load_default()
        meta_font = subject_font

    cache_file = "/tmp/latest_email.json"
    email_item = None
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                email_item = json.load(f)
        except Exception:
            pass

    if not email_item:
        draw.text((x + 25, y + 55), "No new email notes found.", fill=0, font=meta_font)
        return

    subject = email_item.get("subject", "No Subject")

    # Display subject prominently with vertical centering in the box
    draw.text((x + 25, y + 50), f"{subject[:55]}", fill=0, font=subject_font)
