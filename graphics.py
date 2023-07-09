from PIL import Image, ImageDraw, ImageFont
from system_utils import get_current_wallpaper, set_wallpaper


def render_text(text, font_size=50, font_family='./resources/Gelasio-Medium.ttf', color=(0,0,0), x_percent=0.5, y_percent=0.8):
    font = ImageFont.truetype(font_family, font_size, encoding="unic")
    im = Image.new('RGBA', background.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(im)
    text_width, text_height = font.getsize(text)
    x = background.size[0] * x_percent - text_width / 2
    y = background.size[1] * y_percent - text_height / 2
    draw.text((x, y), text, font=font, fill=color)

    return im


def render_text_with_background(text):
    clean_background = background.copy()
    front = render_text(text, font_size=150)
    clean_background.paste(front, (0, 0), front)
    clean_background.save("./resources/current_wallpaper.png", "JPEG", quality=100, optimize=True)
    set_wallpaper("./resources/current_wallpaper.png")

background = get_current_wallpaper()
