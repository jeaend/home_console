from flask import Flask, send_file
from PIL import Image, ImageDraw

from widgets import header, weather, calendar, email_note, birthdays
from utils.email_fetcher import fetch_latest_email

app = Flask(__name__)

WIDTH = 1072
HEIGHT = 1448

@app.route("/text.png")
def serve_dashboard():
    try:
        fetch_latest_email()
    except Exception as e:
        print(f"Background email fetch error: {e}")

    img = Image.new("L", (WIDTH, HEIGHT), color=255)
    draw = ImageDraw.Draw(img)
    
    # Outer perimeter border
    draw.rectangle([0, 0, WIDTH - 1, HEIGHT - 1], outline=0, width=8)
    
    margin = 32
    content_width = WIDTH - (margin * 2)
    
    current_y = margin
    
    # 1. Header Slot
    header.draw(draw, x=margin, y=current_y, max_width=content_width, max_height=100)
    current_y += 120
    
    # 2. Weather Slot
    weather.draw(draw, x=margin, y=current_y, max_width=content_width, max_height=440)
    current_y += 455

    # 3. Calendar Slot
    calendar.draw(draw, x=margin, y=current_y, max_width=content_width, max_height=250)
    current_y += 265
    
    # 4. Birthdays Slot (left third)
    birthdays_width = (content_width - 30) // 3
    birthdays.draw(draw, x=margin, y=current_y, max_width=birthdays_width, max_height=210)
    current_y += 225

    # 5. Email Note Slot (pinned to the bottom)
    email_note.draw(draw, x=margin, y=current_y, max_width=content_width,
                    max_height=HEIGHT - margin - current_y, align_bottom=True)

    path = "/tmp/dashboard.png"
    img.save(path, "PNG")
    return send_file(path, mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
