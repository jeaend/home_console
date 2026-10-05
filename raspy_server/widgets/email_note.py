import json
import os
from datetime import datetime
from email.utils import parseaddr
from PIL import ImageFont

NOTE_FONT = "/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf"
CACHE_FILE = "/tmp/latest_email.json"


def load_font(name, size):
    try:
        return ImageFont.truetype(name, size)
    except IOError:
        return ImageFont.load_default()


def wrap(draw, text, font, max_width):
    lines = []
    for paragraph in text.splitlines() or [""]:
        line = ""
        for word in paragraph.split():
            candidate = f"{line} {word}".strip()
            if draw.textlength(candidate, font=font) <= max_width:
                line = candidate
            else:
                if line:
                    lines.append(line)
                line = word
        lines.append(line)
    return lines


def fit_note(draw, text, max_width, max_height):
    for size in range(56, 27, -4):
        font = load_font(NOTE_FONT, size)
        lines = wrap(draw, text, font, max_width)
        line_height = int(size * 1.3)
        if len(lines) * line_height <= max_height:
            return font, lines, line_height
    return font, lines[: max_height // line_height], line_height


def signature(note):
    name = parseaddr(note.get("sender", ""))[0].split(" ")[0]
    parts = [name]
    received = note.get("received")
    if received:
        parts.append(datetime.fromisoformat(received).strftime("%a %I:%M %p").replace(" 0", " "))
    return ", ".join(p for p in parts if p)


def draw(draw, x=0, y=0, max_width=None, max_height=None):
    box_width = max_width or 600
    box_height = max_height or 140
    center_x = x + box_width / 2

    note = None
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                note = json.load(f)
        except Exception:
            pass

    text = (note or {}).get("subject", "").strip()
    signature_font = load_font(NOTE_FONT, 24)

    pad = 28
    sig_space = 34
    if text:
        font, lines, line_height = fit_note(draw, text, box_width - 2 * pad, box_height - 2 * pad - sig_space)
        card_height = min(box_height, len(lines) * line_height + 2 * pad + sig_space)
    else:
        card_height = 120

    draw.rounded_rectangle([x, y, x + box_width, y + card_height], radius=10, outline=0, width=2)

    if not text:
        empty_font = load_font(NOTE_FONT, 40)
        draw.text((center_x, y + card_height / 2), "No notes yet", fill=0, font=empty_font, anchor="mm")
        return

    text_area = card_height - 2 * pad - sig_space
    text_top = y + pad + (text_area - len(lines) * line_height) / 2
    for i, line in enumerate(lines):
        draw.text((center_x, text_top + i * line_height + line_height / 2), line, fill=0, font=font, anchor="mm")

    sig = signature(note)
    if sig:
        draw.text((x + box_width - pad, y + card_height - pad), sig, fill=0, font=signature_font, anchor="rs")
