import os
import requests
from datetime import datetime
from PIL import ImageFont

DEJAVU = "/usr/share/fonts/truetype/dejavu"
ICON_FONT = os.path.join(os.path.dirname(__file__), "..", "fonts", "weathericons-regular-webfont.ttf")

URL = (
    "https://api.open-meteo.com/v1/forecast?latitude=43.65&longitude=-79.38"
    "&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m,is_day"
    "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,sunrise,sunset"
    "&hourly=temperature_2m,weather_code,is_day"
    "&timezone=auto"
)

# WMO weather code -> (label, day icon, night icon)
CONDITIONS = {
    0: ("Clear", "", ""),
    1: ("Mainly clear", "", ""),
    2: ("Partly cloudy", "", ""),
    3: ("Overcast", "", ""),
    45: ("Fog", "", ""),
    48: ("Fog", "", ""),
    51: ("Light drizzle", "", ""),
    53: ("Drizzle", "", ""),
    55: ("Heavy drizzle", "", ""),
    56: ("Freezing drizzle", "", ""),
    57: ("Freezing drizzle", "", ""),
    61: ("Light rain", "", ""),
    63: ("Rain", "", ""),
    65: ("Heavy rain", "", ""),
    66: ("Freezing rain", "", ""),
    67: ("Freezing rain", "", ""),
    71: ("Light snow", "", ""),
    73: ("Snow", "", ""),
    75: ("Heavy snow", "", ""),
    77: ("Snow grains", "", ""),
    80: ("Showers", "", ""),
    81: ("Showers", "", ""),
    82: ("Heavy showers", "", ""),
    85: ("Snow showers", "", ""),
    86: ("Snow showers", "", ""),
    95: ("Thunderstorm", "", ""),
    96: ("Thunderstorm", "", ""),
    99: ("Thunderstorm", "", ""),
}

ICON_THERMOMETER = ""
ICON_UMBRELLA = ""
ICON_WIND = ""
ICON_SUNRISE = ""
ICON_SUNSET = ""


def load_font(name, size):
    try:
        return ImageFont.truetype(name, size)
    except IOError:
        return ImageFont.load_default()


def condition(code, is_day=True):
    label, day_icon, night_icon = CONDITIONS.get(code, ("Fair", "", ""))
    return label, day_icon if is_day else night_icon


def format_clock(iso_time):
    return datetime.strptime(iso_time, "%Y-%m-%dT%H:%M").strftime("%I:%M %p").lstrip("0")


def fetch():
    data = requests.get(URL, timeout=3).json()
    cur = data["current"]
    daily = data["daily"]
    hourly = data["hourly"]

    now_hour = datetime.now().strftime("%Y-%m-%dT%H:00")
    start = next((i for i, t in enumerate(hourly["time"]) if t >= now_hour), 0) + 1

    return {
        "temp": cur["temperature_2m"],
        "feels": round(cur["apparent_temperature"]),
        "code": cur["weather_code"],
        "is_day": bool(cur.get("is_day", 1)),
        "wind": round(cur["wind_speed_10m"]),
        "high": round(daily["temperature_2m_max"][0]),
        "low": round(daily["temperature_2m_min"][0]),
        "rain": daily["precipitation_probability_max"][0],
        "sunrise": format_clock(daily["sunrise"][0]),
        "sunset": format_clock(daily["sunset"][0]),
        "hours": [
            {
                "time": datetime.strptime(hourly["time"][i], "%Y-%m-%dT%H:%M").strftime("%I %p").lstrip("0"),
                "temp": round(hourly["temperature_2m"][i]),
                "code": hourly["weather_code"][i],
                "is_day": bool(hourly["is_day"][i]),
            }
            for i in range(start, min(start + 5, len(hourly["time"])))
        ],
    }


def draw(draw, x=0, y=0, max_width=None, max_height=None):
    box_width = max_width or 600
    box_height = max_height or 440
    draw.rectangle([x, y, x + box_width, y + box_height], outline=0, width=2)

    temp_font = load_font(f"{DEJAVU}/DejaVuSans-Bold.ttf", 120)
    condition_font = load_font(f"{DEJAVU}/DejaVuSans-Bold.ttf", 36)
    feels_font = load_font(f"{DEJAVU}/DejaVuSans.ttf", 28)
    stat_label_font = load_font(f"{DEJAVU}/DejaVuSans.ttf", 26)
    stat_value_font = load_font(f"{DEJAVU}/DejaVuSans-Bold.ttf", 26)
    hour_font = load_font(f"{DEJAVU}/DejaVuSans.ttf", 24)
    hour_temp_font = load_font(f"{DEJAVU}/DejaVuSans-Bold.ttf", 30)
    big_icon_font = load_font(ICON_FONT, 150)
    stat_icon_font = load_font(ICON_FONT, 30)
    hour_icon_font = load_font(ICON_FONT, 52)

    try:
        w = fetch()
    except Exception:
        draw.text((x + box_width / 2, y + box_height / 2), "Weather offline",
                  fill=0, font=condition_font, anchor="mm")
        return

    label, icon = condition(w["code"], w["is_day"])
    stats_left = x + box_width - 380
    stats_right = x + box_width - 30

    # --- Current conditions: icon, temperature, label ---
    top_mid = y + 140
    temp_text = f"{w['temp']:.1f}°"
    temp_max_width = stats_left - 30 - (x + 260)
    temp_size = 120
    while temp_size > 60 and draw.textlength(temp_text, font=temp_font) > temp_max_width:
        temp_size -= 4
        temp_font = load_font(f"{DEJAVU}/DejaVuSans-Bold.ttf", temp_size)
    draw.text((x + 130, top_mid), icon, fill=0, font=big_icon_font, anchor="mm")
    draw.text((x + 260, top_mid - 20), temp_text, fill=0, font=temp_font, anchor="ls")
    draw.text((x + 265, top_mid + 30), label, fill=0, font=condition_font, anchor="ls")
    draw.text((x + 265, top_mid + 72), f"Feels like {w['feels']}°", fill=0, font=feels_font, anchor="ls")

    # --- Stats: icon, label left, value right ---
    stats = [
        (ICON_THERMOMETER, "High / Low", f"{w['high']}° / {w['low']}°"),
        (ICON_UMBRELLA, "Rain", f"{w['rain']}%"),
        (ICON_WIND, "Wind", f"{w['wind']} km/h"),
        (ICON_SUNRISE, "Sunrise", w["sunrise"]),
        (ICON_SUNSET, "Sunset", w["sunset"]),
    ]
    row_y = y + 50
    for stat_icon, stat_label, value in stats:
        draw.text((stats_left + 18, row_y), stat_icon, fill=0, font=stat_icon_font, anchor="mm")
        draw.text((stats_left + 48, row_y), stat_label, fill=0, font=stat_label_font, anchor="lm")
        draw.text((stats_right, row_y), value, fill=0, font=stat_value_font, anchor="rm")
        row_y += 46

    divider_y = y + 285
    draw.line([x + 20, divider_y, x + box_width - 20, divider_y], fill=0, width=2)

    # --- Next 5 hours ---
    col_width = (box_width - 40) / max(len(w["hours"]), 1)
    for idx, h in enumerate(w["hours"]):
        col_x = x + 20 + col_width * idx + col_width / 2
        _, h_icon = condition(h["code"], h["is_day"])
        draw.text((col_x, divider_y + 30), h["time"], fill=0, font=hour_font, anchor="mm")
        draw.text((col_x, divider_y + 82), h_icon, fill=0, font=hour_icon_font, anchor="mm")
        draw.text((col_x, divider_y + 132), f"{h['temp']}°", fill=0, font=hour_temp_font, anchor="mm")
