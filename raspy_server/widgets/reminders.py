import json
import time
from datetime import datetime
from PIL import ImageFont

FONT_DIR = "/usr/share/fonts/opentype/urw-base35"
CACHE_FILE = "/tmp/reminders.json"


def load_font(name, size):
    try:
        return ImageFont.truetype(name, size)
    except IOError:
        return ImageFont.load_default()


def save(payload):
    lists = {}
    for line in str(payload.get("items") or "").splitlines():
        name, _, title = line.partition(": ")
        if name.strip() and title.strip():
            lists.setdefault(name.strip().lower(), []).append(title.strip())
    data = {"lists": lists, "at": time.time()}
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)
    return data


def load():
    try:
        with open(CACHE_FILE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def draw(draw, x=0, y=0, max_width=None, max_height=None):
    box_width = max_width or 600
    box_height = max_height or 210
    draw.rounded_rectangle([x, y, x + box_width, y + box_height], radius=10, outline=0, width=2)

    label_font = load_font(f"{FONT_DIR}/NimbusSans-Bold.otf", 24)
    item_font = load_font(f"{FONT_DIR}/NimbusSans-Regular.otf", 26)
    message_font = load_font(f"{FONT_DIR}/NimbusSans-Regular.otf", 28)

    data = load()
    if data is None:
        draw.text((x + box_width / 2, y + box_height / 2), "No reminders yet", fill=0, font=message_font, anchor="mm")
        return

    pad = 28
    line_height = 38
    check_size = 20
    text_x = x + pad + check_size + 16
    item_width = x + box_width - pad - text_x
    row_y = y + pad + line_height / 2
    today = datetime.now().strftime("%A")
    list_name = "Weekend" if today in ("Saturday", "Sunday") else today
    draw.text((x + pad, row_y), list_name.upper(), fill=0, font=label_font, anchor="lm")

    items = data.get("lists", {}).get(list_name.lower(), [])
    if not items:
        draw.text((x + pad, row_y + line_height), "All done", fill=0, font=item_font, anchor="lm")
        return

    rows = int((y + box_height - pad - (row_y + line_height / 2)) // line_height)
    shown = items if len(items) <= rows else items[:rows - 1]
    for item in shown:
        row_y += line_height
        draw.rounded_rectangle([x + pad, row_y - check_size / 2, x + pad + check_size, row_y + check_size / 2],
                               radius=4, outline=0, width=2)
        draw.text((text_x, row_y), truncate(draw, item, item_font, item_width), fill=0, font=item_font, anchor="lm")
    if len(shown) < len(items):
        draw.text((text_x, row_y + line_height), f"+{len(items) - len(shown)} more", fill=0, font=item_font, anchor="lm")


def truncate(draw, text, font, max_width):
    while draw.textlength(text, font=font) > max_width and len(text) > 1:
        text = text[:-2].rstrip() + "…"
    return text


def draw_groceries(draw, x=0, y=0, max_width=None, max_height=None):
    box_width = max_width or 600
    box_height = max_height or 210
    draw.rounded_rectangle([x, y, x + box_width, y + box_height], radius=10, outline=0, width=2)

    label_font = load_font(f"{FONT_DIR}/NimbusSans-Bold.otf", 24)
    item_font = load_font(f"{FONT_DIR}/NimbusSans-Regular.otf", 26)

    pad = 28
    line_height = 38
    item_width = box_width - 2 * pad
    row_y = y + pad + line_height / 2
    draw.text((x + pad, row_y), "GROCERIES", fill=0, font=label_font, anchor="lm")

    data = load()
    if data is None:
        draw.text((x + pad, row_y + line_height), "No groceries yet", fill=0, font=item_font, anchor="lm")
        return
    items = next((v for k, v in data.get("lists", {}).items() if k.startswith("grocer")), [])
    if not items:
        draw.text((x + pad, row_y + line_height), "Nothing needed", fill=0, font=item_font, anchor="lm")
        return

    rows = int((y + box_height - pad - (row_y + line_height / 2)) // line_height)
    shown = items if len(items) <= rows else items[:rows - 1]
    for item in shown:
        row_y += line_height
        draw.text((x + pad, row_y), truncate(draw, item, item_font, item_width), fill=0, font=item_font, anchor="lm")
    if len(shown) < len(items):
        draw.text((x + pad, row_y + line_height), f"+{len(items) - len(shown)} more", fill=0, font=item_font, anchor="lm")
