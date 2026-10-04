import requests
from datetime import datetime
from PIL import ImageFont

def draw(draw, x=0, y=0, max_width=None, max_height=None):
    temperature = "--"
    feels_like = "--"
    condition_text = "Fetching weather..."
    code = 0
    high_temp = "--"
    low_temp = "--"
    precip_prob = "--"
    wind_speed = "--"
    sunrise_str = "--"
    sunset_str = "--"
    hourly_slots = []
    
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=43.65&longitude=-79.38&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,sunrise,sunset&hourly=temperature_2m,weather_code&timezone=auto"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            
            cur = data.get("current", {})
            temp_c = cur.get("temperature_2m")
            app_c = cur.get("apparent_temperature")
            code = cur.get("weather_code", 0)
            wind = cur.get("wind_speed_10m")
            
            if temp_c is not None:
                temperature = f"{temp_c}°C"
            if app_c is not None:
                feels_like = f"Feels like {app_c}°C"
            if wind is not None:
                wind_speed = f"{wind} km/h"
            
            daily = data.get("daily", {})
            maxs = daily.get("temperature_2m_max", [])
            mins = daily.get("temperature_2m_min", [])
            precips = daily.get("precipitation_probability_max", [])
            sunrises = daily.get("sunrise", [])
            sunsets = daily.get("sunset", [])
            
            if maxs:
                high_temp = f"{round(maxs[0])}°"
            if mins:
                low_temp = f"{round(mins[0])}°"
            if precips:
                precip_prob = f"{precips[0]}%"
            
            if sunrises and len(sunrises[0]) >= 16:
                t_part = sunrises[0].split("T")[1]
                dt_obj = datetime.strptime(t_part, "%H:%M")
                sunrise_str = dt_obj.strftime("%I:%M %p").lstrip("0")
                
            if sunsets and len(sunsets[0]) >= 16:
                t_part = sunsets[0].split("T")[1]
                dt_obj = datetime.strptime(t_part, "%H:%M")
                sunset_str = dt_obj.strftime("%I:%M %p").lstrip("0")
            
            conditions = {
                0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy",
                3: "Overcast", 51: "Drizzle", 61: "Rain", 71: "Snow"
            }
            condition_text = conditions.get(code, "Fair")
            
            hourly = data.get("hourly", {})
            times = hourly.get("time", [])
            temps = hourly.get("temperature_2m", [])
            codes = hourly.get("weather_code", [])
            
            now_str = datetime.now().strftime("%Y-%m-%dT%H:00")
            start_idx = 0
            for idx, t in enumerate(times):
                if t >= now_str:
                    start_idx = idx
                    break
            
            start_idx += 1
            
            for i in range(start_idx, min(start_idx + 5, len(times))):
                dt = datetime.strptime(times[i], "%Y-%m-%dT%H:%M")
                hour_label = dt.strftime("%I %p").lstrip("0")
                h_code = codes[i] if i < len(codes) else 0
                hourly_slots.append({
                    "time": hour_label,
                    "temp": round(temps[i]),
                    "code": h_code
                })
    except Exception:
        condition_text = "Weather offline"

    try:
        big_temp_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 96)
        condition_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
        meta_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
    except IOError:
        big_temp_font = ImageFont.load_default()
        condition_font = big_temp_font
        meta_font = big_temp_font
        small_font = big_temp_font

    box_width = max_width or 600
    box_height = max_height or 440
    if max_width:
        draw.rectangle([x, y, x + box_width, y + box_height], outline=0, width=2)
    
    # Column Widths: Left (40% / 2/5), Middle (20% / 1/5), Right (40% / 2/5)
    w1 = box_width * 0.40
    w2 = box_width * 0.20
    w3 = box_width * 0.40

    col1_center = x + (w1 * 0.5)
    col2_center = x + w1 + (w2 * 0.5)
    col3_center = x + w1 + w2 + (w3 * 0.5)

    def draw_centered(text, font, center_x, y_pos):
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        draw.text((center_x - w // 2, y_pos), text, fill=0, font=font)

    # --- COLUMN 1: TEMP, CONDITION & FEELS LIKE ---
    draw_centered(temperature, big_temp_font, col1_center, y + 55)
    draw_centered(condition_text, condition_font, col1_center, y + 170)
    draw_centered(feels_like, meta_font, col1_center, y + 220)

    # --- COLUMN 2: SYMBOL ONLY ---
    cur_icon_x, cur_icon_y = col2_center, y + 125
    if code in [0, 1]:  # Sun
        draw.ellipse([cur_icon_x - 30, cur_icon_y - 30, cur_icon_x + 30, cur_icon_y + 30], fill=0)
        draw.line([cur_icon_x - 44, cur_icon_y, cur_icon_x - 34, cur_icon_y], fill=0, width=4)
        draw.line([cur_icon_x + 34, cur_icon_y, cur_icon_x + 44, cur_icon_y], fill=0, width=4)
        draw.line([cur_icon_x, cur_icon_y - 44, cur_icon_x, cur_icon_y - 34], fill=0, width=4)
        draw.line([cur_icon_x, cur_icon_y + 34, cur_icon_x, cur_icon_y + 44], fill=0, width=4)
    elif code in [2, 3]:  # Cloud
        draw.rectangle([cur_icon_x - 34, cur_icon_y - 14, cur_icon_x + 34, cur_icon_y + 22], fill=0)
        draw.ellipse([cur_icon_x - 40, cur_icon_y - 24, cur_icon_x + 6, cur_icon_y + 16], fill=0)
        draw.ellipse([cur_icon_x - 12, cur_icon_y - 36, cur_icon_x + 28, cur_icon_y + 8], fill=0)
    else:  # Rain
        draw.rectangle([cur_icon_x - 34, cur_icon_y - 20, cur_icon_x + 34, cur_icon_y + 14], fill=0)
        draw.ellipse([cur_icon_x - 40, cur_icon_y - 28, cur_icon_x + 6, cur_icon_y + 8], fill=0)
        draw.line([cur_icon_x - 20, cur_icon_y + 20, cur_icon_x - 28, cur_icon_y + 38], fill=0, width=4)
        draw.line([cur_icon_x + 6, cur_icon_y + 20, cur_icon_x - 2, cur_icon_y + 38], fill=0, width=4)

    # --- COLUMN 3: METADATA ---
    draw_centered(f"H/L: {high_temp} / {low_temp}", meta_font, col3_center, y + 40)
    draw_centered(f"Rain: {precip_prob}", meta_font, col3_center, y + 79)
    draw_centered(f"Wind: {wind_speed}", meta_font, col3_center, y + 118)
    draw_centered(f"Rise: {sunrise_str}", meta_font, col3_center, y + 157)
    draw_centered(f"Set:  {sunset_str}", meta_font, col3_center, y + 196)

    # Divider line between top section and hourly forecast
    draw.line([x + 20, y + 285, x + box_width - 20, y + 285], fill=0, width=2)

    # --- 5-HOUR TIMELINE SECTION ---
    col_width = (box_width - 40) / max(len(hourly_slots), 1)
    for idx, h in enumerate(hourly_slots):
        col_x = x + 20 + (idx * col_width) + (col_width / 2)
        
        draw_centered(h["time"], small_font, col_x, y + 305)
        
        ic_x, ic_y = col_x, y + 360
        if h["code"] in [0, 1]:
            draw.ellipse([ic_x - 10, ic_y - 10, ic_x + 10, ic_y + 10], fill=0)
        elif h["code"] in [2, 3]:
            draw.rectangle([ic_x - 14, ic_y - 6, ic_x + 14, ic_y + 6], fill=0)
        else:
            draw.rectangle([ic_x - 14, ic_y - 8, ic_x + 14, ic_y + 4], fill=0)
        
        draw_centered(f"{h['temp']}°C", small_font, col_x, y + 390)