from flask import Flask, request, send_file
from PIL import Image, ImageDraw

from widgets import header, weather, calendar, email_note, birthdays, reminders
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
    
    margin = 20
    gap = 12
    content_width = WIDTH - (margin * 2)
    
    current_y = margin
    
    # 1. Header Slot
    battery = request.args.get("battery", type=int)
    header.draw(draw, x=margin, y=current_y, max_width=content_width, max_height=100, battery=battery)
    current_y += 68
    
    # 2. Weather Slot
    weather.draw(draw, x=margin, y=current_y, max_width=content_width, max_height=440)
    current_y += 440 + gap

    # 3. Email Note Slot (pinned to the bottom; everything above fills whatever it leaves)
    reminders_height = 208
    birthdays_height = 80
    column_top = current_y
    min_height = 250 + reminders_height + birthdays_height + 2 * gap
    note_y = column_top + min_height + gap
    note_top = email_note.draw(draw, x=margin, y=note_y, max_width=content_width,
                               max_height=HEIGHT - margin - note_y, align_bottom=True)

    # 4. Birthdays Slot (full width, single line, just above the note)
    birthdays_y = note_top - gap - birthdays_height
    birthdays.draw_strip(draw, x=margin, y=birthdays_y, max_width=content_width, max_height=birthdays_height)
    column_bottom = birthdays_y - gap

    # 5. Calendar Slot (left two thirds, stretches to fill)
    left_width = (content_width - gap) * 2 // 3
    calendar_height = column_bottom - column_top - reminders_height - gap
    calendar.draw(draw, x=margin, y=current_y, max_width=left_width, max_height=calendar_height)
    current_y += calendar_height + gap

    # 6. Reminders Slot (left, under the calendar)
    reminders.draw(draw, x=margin, y=current_y, max_width=left_width, max_height=reminders_height)

    # 7. Groceries Slot (right third, full column height)
    groceries_x = margin + left_width + gap
    reminders.draw_groceries(draw, x=groceries_x, y=column_top, max_width=margin + content_width - groceries_x,
                             max_height=column_bottom - column_top)

    path = "/tmp/dashboard.png"
    img.save(path, "PNG")
    return send_file(path, mimetype="image/png")

@app.route("/reminders", methods=["POST"])
def receive_reminders():
    payload = request.get_json(silent=True) or request.form.to_dict()
    data = reminders.save(payload)
    return {"saved": {name: len(items) for name, items in data["lists"].items()}}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
