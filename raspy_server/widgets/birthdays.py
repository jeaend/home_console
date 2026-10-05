import re
import time
from datetime import date, datetime
from xml.etree import ElementTree as ET
from PIL import ImageFont

import requests

try:
    import config
except ImportError:
    config = None

FONT_DIR = "/usr/share/fonts/opentype/urw-base35"
CONTACTS_URL = "https://contacts.icloud.com/"
CACHE_SECONDS = 6 * 3600
COUNT = 3
NS = {"d": "DAV:", "c": "urn:ietf:params:xml:ns:carddav"}
APPLE_NO_YEAR = 1604

_cache = {"at": 0, "people": None}


def load_font(name, size):
    try:
        return ImageFont.truetype(name, size)
    except IOError:
        return ImageFont.load_default()


def dav(method, url, body, depth="0"):
    response = requests.request(
        method, url, data=body, timeout=20,
        auth=(config.ICLOUD_USER, config.ICLOUD_APP_PASSWORD),
        headers={"Depth": depth, "Content-Type": "application/xml"},
    )
    response.raise_for_status()
    return response.url, ET.fromstring(response.content)


def address_books():
    url, xml = dav("PROPFIND", CONTACTS_URL,
                   '<d:propfind xmlns:d="DAV:"><d:prop><d:current-user-principal/></d:prop></d:propfind>')
    principal = requests.compat.urljoin(url, xml.find(".//d:current-user-principal/d:href", NS).text)
    url, xml = dav("PROPFIND", principal,
                   '<d:propfind xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:carddav">'
                   '<d:prop><c:addressbook-home-set/></d:prop></d:propfind>')
    home = requests.compat.urljoin(url, xml.find(".//c:addressbook-home-set/d:href", NS).text)
    url, xml = dav("PROPFIND", home,
                   '<d:propfind xmlns:d="DAV:"><d:prop><d:resourcetype/></d:prop></d:propfind>', depth="1")
    return [requests.compat.urljoin(home, r.find("d:href", NS).text)
            for r in xml.findall("d:response", NS) if r.find(".//c:addressbook", NS) is not None]


def parse_birthday(value):
    digits = re.sub(r"[^0-9]", "", value.split("T")[0])
    if value.startswith("--") and len(digits) == 4:
        return None, int(digits[:2]), int(digits[2:])
    if len(digits) >= 8:
        year, month, day = int(digits[:4]), int(digits[4:6]), int(digits[6:8])
        return (None if year == APPLE_NO_YEAR else year), month, day
    return None


def parse_card(card):
    card = re.sub(r"\r?\n[ \t]", "", card)
    full_name = first_name = birthday = None
    for line in card.splitlines():
        key, _, value = line.partition(":")
        field = key.split(";")[0].split(".")[-1].upper()
        if field == "FN":
            full_name = value.strip().replace("\\,", ",")
        elif field == "N":
            parts = value.split(";")
            first_name = parts[1].strip() if len(parts) > 1 else None
        elif field == "BDAY":
            birthday = parse_birthday(value.strip())
    name = first_name or (full_name.split()[0] if full_name else None)
    if name and birthday:
        year, month, day = birthday
        return {"name": name, "year": year, "month": month, "day": day}
    return None


def fetch_people():
    people = []
    query = ('<c:addressbook-query xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:carddav">'
             '<d:prop><c:address-data/></d:prop></c:addressbook-query>')
    for book in address_books():
        _, xml = dav("REPORT", book, query, depth="1")
        for data in xml.iter("{urn:ietf:params:xml:ns:carddav}address-data"):
            person = parse_card(data.text or "")
            if person:
                people.append(person)
    return people


def get_people():
    if _cache["people"] is None or time.time() - _cache["at"] > CACHE_SECONDS:
        try:
            _cache["people"] = fetch_people()
            _cache["at"] = time.time()
        except Exception as e:
            print(f"Birthdays fetch error: {type(e).__name__}: {e}", flush=True)
    return _cache["people"]


def next_occurrence(person, today):
    for year in (today.year, today.year + 1):
        try:
            when = date(year, person["month"], person["day"])
        except ValueError:
            when = date(year, 3, 1)
        if when >= today:
            return when


def upcoming(people, today):
    rows = []
    for person in people:
        when = next_occurrence(person, today)
        rows.append({"name": person["name"], "date": when, "days": (when - today).days})
    return sorted(rows, key=lambda r: (r["days"], r["name"]))[:COUNT]


def draw(draw, x=0, y=0, max_width=None, max_height=None):
    box_width = max_width or 600
    box_height = max_height or 210
    draw.rounded_rectangle([x, y, x + box_width, y + box_height], radius=10, outline=0, width=2)

    label_font = load_font(f"{FONT_DIR}/NimbusSans-Bold.otf", 24)
    date_font = load_font(f"{FONT_DIR}/NimbusSans-Bold.otf", 26)
    name_font = load_font(f"{FONT_DIR}/NimbusSans-Regular.otf", 26)
    message_font = load_font(f"{FONT_DIR}/NimbusSans-Regular.otf", 28)

    if not getattr(config, "ICLOUD_USER", ""):
        return

    people = get_people()
    if people is None:
        draw.text((x + box_width / 2, y + box_height / 2), "Birthdays offline", fill=0, font=message_font, anchor="mm")
        return

    pad = 28
    line_height = 38
    date_column = 100
    name_width = box_width - 2 * pad - date_column
    row_y = y + pad + line_height / 2
    draw.text((x + pad, row_y), "BIRTHDAYS", fill=0, font=label_font, anchor="lm")

    rows = upcoming(people, datetime.now().date())
    if not rows:
        draw.text((x + pad + date_column, row_y + line_height), "No birthdays saved", fill=0, font=name_font, anchor="lm")
        return

    for row in rows:
        row_y += line_height
        draw.text((x + pad, row_y), row["date"].strftime("%b %d").replace(" 0", " "), fill=0, font=date_font, anchor="lm")
        name = row["name"]
        while draw.textlength(name, font=name_font) > name_width and len(name) > 1:
            name = name[:-2].rstrip() + "…"
        draw.text((x + pad + date_column, row_y), name, fill=0, font=name_font, anchor="lm")
