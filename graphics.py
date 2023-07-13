import textwrap

from PIL import Image, ImageDraw, ImageFont, ImageColor
from PIL.ImageFont import FreeTypeFont

from system_utils import get_current_wallpaper, set_wallpaper, get_font_path
from state_manager import get_state


def _get_dominant_color(pil_img: Image.Image, palette_size: int = 16) -> tuple:
    """
    This function uses k-means to cluster similar colors and return the
    centroid of the largest cluster.

    Args:
        pil_img (Image.Image): Τηε image to process.
        palette_size (int, optional): How many clusters to make. Defaults to 16.

    Returns:
        tuple: The dominant color.
    """

    # Resize image to speed up processing
    img = pil_img.copy()
    img.thumbnail((100, 100))

    # Reduce colors (uses k-means internally)
    paletted = img.convert('P', palette=Image.ADAPTIVE, colors=palette_size)

    # Find the color that occurs most often
    palette = paletted.getpalette()
    color_counts = sorted(paletted.getcolors(), reverse=True)
    palette_index = color_counts[0][1]
    dominant_color = tuple(palette[palette_index*3:palette_index*3+3])

    return dominant_color


def _find_words_per_line(font: FreeTypeFont, text: str, max_width: int) -> list[str]:
    """
    This function splits the text into lines that fit the given width.

    Args:
        font (FreeTypeFont): The font used to render the text.
        text (str): The text to split.
        max_width (int): The maximum width of each line.

    Returns:
        list[str]: The lines of the text that fit the given width.
    """

    if len(text) == 0: return []
    max_characters_per_line = len(text)
    while font.getsize(text[:max_characters_per_line])[0] > max_width:
        max_characters_per_line -= 1
    return textwrap.wrap(text, max_characters_per_line)


def render_text(text: str, font_size: int = 50, font_family: str = get_font_path("Arial"),
        color: tuple = (0,0,0), stroke_width: int= 0, stroke_color: tuple = (0, 0, 0),
        width: int = 1, height: int = 1) -> Image.Image:
    """
    This function renders the text on an image with the given parameters.

    Args:
        text (str): The text to render.
        font_size (int, optional): The font size to use. Defaults to 50.
        font_family (str, optional): The path of the font family to use. Defaults to get_font_path("Arial").
        color (tuple, optional): The font color o use. Defaults to (0,0,0).
        stroke_width (int, optional): The stroke width of the text. Defaults to 0.
        stroke_color (tuple, optional): The color of the stroke. Defaults to (0, 0, 0).
        width (int, optional): The width of the text-window as a 0-1 range of backgrounds' width. Defaults to 1.
        height (int, optional): The height of the text-window as a 0-1 range of the background's height. Defaults to 1.

    Returns:
        Image.Image: The image with the rendered text.
    """
    
    font = ImageFont.truetype(font_family, font_size, encoding="unic")
    im = Image.new('RGBA', (int(background.size[0] * width),
        int(background.size[1] * height)))
    draw = ImageDraw.Draw(im)

    text_height = font.getsize(text)[1]
    y = 0 # start at top
    for line in _find_words_per_line(font, text, im.size[0]):
        line_width = font.getsize(line)[0]
        x = int((im.size[0] - line_width) * 0.5) # center text
        draw.text((x, y), line, font=font, fill=color, stroke_width=stroke_width, stroke_fill=stroke_color)
        y += text_height

    return im


def render_text_with_background(text: str):
    """
    This function renders the text on the background and saves it as a wallpaper.

    Args:
        text (str): The text to render.
    """

    clean_background = background.copy()
    front = render_text(text, font_size=FONT_SIZE, font_family=FONT_FAMILY, color=FONT_COLOR,
        stroke_width=FONT_STROKE, stroke_color=STROKE_COLOR, width=WIDTH, height=HEIGHT)
    
    x = int((clean_background.size[0] - front.size[0]) * X_OFFSET)
    y = int((clean_background.size[1]) * Y_OFFSET)

    clean_background.paste(front, (x, y), front)
    clean_background.save("./resources/current_wallpaper.png", "JPEG", quality=QUALITY, optimize=True)
    set_wallpaper("./resources/current_wallpaper.png")


def restore_wallpaper(): 
    """
    This function restores the wallpaper to the one that was set before the program started.
    """
    
    set_wallpaper(get_state()['currentWallpaper'])


# Load settings and define global variables - constants
SETTINGS = get_state()["wallpaperSettings"]
FONT_PERCENT = SETTINGS["fontSize"]
FONT_COLOR = SETTINGS["fontColor"]
PICK_COLOR = SETTINGS["pickColorFromWallpaper"]
FONT_COLOR = ImageColor.getrgb(FONT_COLOR) if FONT_COLOR.startswith("#") else FONT_COLOR
FONT_FAMILY = get_font_path(SETTINGS["fontFamily"])
FONT_STROKE_PERCENT = SETTINGS["fontStroke"]
X_OFFSET = SETTINGS["xOffset"] / 100
Y_OFFSET = SETTINGS["yOffset"] / 100
WIDTH = SETTINGS["width"] / 100
HEIGHT = SETTINGS["height"] / 100
QUALITY = SETTINGS["quality"]
SCALING = SETTINGS["scaling"]

background = get_current_wallpaper()
if SCALING != 100:
    background = background.resize((int(background.size[0] * SCALING / 100),
        int(background.size[1] * SCALING / 100)), Image.ANTIALIAS)
if PICK_COLOR: FONT_COLOR = _get_dominant_color(background)
# Use white or black stroke depending on font color luminance
color_luma = 0.2126 * FONT_COLOR[0] + 0.7152 * FONT_COLOR[1] + 0.0722 * FONT_COLOR[2]
STROKE_COLOR = (0, 0, 0) if color_luma > 60 else (150, 150, 150)
FONT_SIZE = int(background.size[0] * FONT_PERCENT / 100)
FONT_STROKE = int(FONT_SIZE * FONT_STROKE_PERCENT / 100)
