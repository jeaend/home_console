from PIL import ImageFont

def draw(draw, x=0, y=0, max_width=None, max_height=None):
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    except IOError:
        font = ImageFont.load_default()
        
    # Draw header text neatly within the slot coordinates
    draw.text((x, y), "Kindle Dashboard", fill=0, font=font)