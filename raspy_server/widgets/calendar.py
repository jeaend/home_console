import time
from datetime import date, datetime, timedelta
from PIL import ImageFont

try:
    import requests
    import caldav
    import icalendar
    import recurring_ical_events
except ImportError:
    caldav = None

try:
    import config
except ImportError:
    config = None

FONT_DIR = "/usr/share/fonts/opentype/urw-base35"
EVENING_HOUR = 17
CACHE_SECONDS = 600
ICLOUD_URL = "https://caldav.icloud.com"

_cache = {"at": 0, "events": None}


def load_font(name, size):
    try:
        return ImageFont.truetype(name, size)
    except IOError:
        return ImageFont.load_default()


def to_local(value, tz):
    if isinstance(value, datetime):
        return value.astimezone(tz) if value.tzinfo else value.replace(tzinfo=tz)
    return datetime.combine(value, datetime.min.time(), tz)


def expand(calendar, start, end, tz):
    events = []
    for ev in recurring_ical_events.of(calendar).between(start, end):
        dtstart = ev["DTSTART"].dt
        if ev.get("DTEND"):
            dtend = ev["DTEND"].dt
        elif ev.get("DURATION"):
            dtend = dtstart + ev["DURATION"].dt
        else:
            dtend = dtstart
        events.append({
            "title": str(ev.get("SUMMARY", "")).strip() or "(No title)",
            "start": to_local(dtstart, tz),
            "end": to_local(dtend, tz),
            "all_day": not isinstance(dtstart, datetime),
        })
    return events


def fetch_events(start, end, tz):
    events = []
    for n, url in enumerate(getattr(config, "ICAL_URLS", []), 1):
        try:
            response = requests.get(url.replace("webcal://", "https://"), timeout=10)
            response.raise_for_status()
            events += expand(icalendar.Calendar.from_ical(response.content), start, end, tz)
        except Exception as e:
            status = getattr(getattr(e, "response", None), "status_code", "")
            print(f"Calendar link {n} failed: {type(e).__name__} {status}".rstrip(), flush=True)

    if getattr(config, "ICLOUD_USER", ""):
        client = caldav.DAVClient(url=ICLOUD_URL, username=config.ICLOUD_USER,
                                  password=config.ICLOUD_APP_PASSWORD, timeout=10)
        names = getattr(config, "CALENDAR_NAMES", [])
        for cal in client.principal().calendars():
            if names and cal.name not in names:
                continue
            if "VEVENT" not in cal.get_supported_components():
                continue
            for obj in cal.search(start=start, end=end, event=True):
                events += expand(obj.icalendar_instance, start, end, tz)

    unique = {(e["title"], e["start"]): e for e in events}
    return sorted(unique.values(), key=lambda e: (e["start"].date(), not e["all_day"], e["start"]))


def get_events(start, end, tz):
    if _cache["events"] is None or time.time() - _cache["at"] > CACHE_SECONDS:
        try:
            _cache["events"] = fetch_events(start, end, tz)
            _cache["at"] = time.time()
        except Exception as e:
            print(f"Calendar fetch error: {type(e).__name__}: {e}", flush=True)
    return _cache["events"]


def sections(events, now):
    today = now.date()
    tomorrow = today + timedelta(days=1)
    today_left = [e for e in events if e["start"].date() == today and (e["all_day"] or e["end"] > now)]
    tomorrow_events = [e for e in events if e["start"].date() == tomorrow]

    if not today_left:
        return [("Tomorrow", tomorrow_events)]
    if now.hour >= EVENING_HOUR:
        return [("Today", today_left), ("Tomorrow", tomorrow_events)]
    return [("Today", today_left)]


def format_time(event):
    if event["all_day"]:
        return "All day"
    return event["start"].strftime("%I:%M %p").lstrip("0")


def draw(draw, x=0, y=0, max_width=None, max_height=None):
    box_width = max_width or 600
    box_height = max_height or 250
    draw.rounded_rectangle([x, y, x + box_width, y + box_height], radius=10, outline=0, width=2)

    label_font = load_font(f"{FONT_DIR}/NimbusSans-Bold.otf", 24)
    time_font = load_font(f"{FONT_DIR}/NimbusSans-Bold.otf", 26)
    title_font = load_font(f"{FONT_DIR}/NimbusSans-Regular.otf", 26)
    message_font = load_font(f"{FONT_DIR}/NimbusSans-Regular.otf", 28)

    if caldav is None:
        draw.text((x + box_width / 2, y + box_height / 2), "Calendar unavailable", fill=0, font=message_font, anchor="mm")
        return

    now = datetime.now().astimezone()
    tz = now.tzinfo
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    events = get_events(day_start, day_start + timedelta(days=2), tz)

    if events is None:
        draw.text((x + box_width / 2, y + box_height / 2), "Calendar offline", fill=0, font=message_font, anchor="mm")
        return

    pad = 28
    line_height = 38
    time_column = 150
    title_width = box_width - 2 * pad - time_column
    max_lines = (box_height - 2 * pad) // line_height

    lines = []
    for label, day_events in sections(events, now):
        lines.append(("label", label))
        if not day_events:
            lines.append(("empty", "Nothing planned"))
        for event in day_events:
            lines.append(("event", event))

    if len(lines) > max_lines:
        hidden = sum(1 for kind, _ in lines[max_lines - 1:] if kind == "event")
        lines = lines[:max_lines - 1]
        if lines[-1][0] == "label":
            lines.pop()
        lines.append(("more", f"+{hidden} more"))

    row_y = y + pad + line_height / 2
    for kind, value in lines:
        if kind == "label":
            draw.text((x + pad, row_y), value.upper(), fill=0, font=label_font, anchor="lm")
        elif kind == "event":
            title = value["title"]
            while draw.textlength(title, font=title_font) > title_width and len(title) > 1:
                title = title[:-2].rstrip() + "…"
            draw.text((x + pad, row_y), format_time(value), fill=0, font=time_font, anchor="lm")
            draw.text((x + pad + time_column, row_y), title, fill=0, font=title_font, anchor="lm")
        else:
            draw.text((x + pad + time_column, row_y), value, fill=0, font=title_font, anchor="lm")
        row_y += line_height
