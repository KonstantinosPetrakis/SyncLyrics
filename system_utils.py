import subprocess
import platform
import os
import re
import ctypes
from time import time

from PIL import Image
import matplotlib.font_manager as fm

from state_manager import get_state, set_state


def _remove_text_inside_parentheses_and_brackets(text: str) -> str:
    """
    This function removes text inside parentheses and brackets from the given text.

    Args:
        text (str): The text to remove the text inside parentheses and brackets from.

    Returns:
        str: The text with the text inside parentheses and brackets removed.
    """

    return re.sub(r"\([^)]*\)|\[[^\]]*\]", '', text)


def _get_current_song_meta_data_gnome() -> dict[str, str | int] | None:
    """
    This function returns the current song's metadata if a song is playing, otherwise it returns None.
    It only works on Linux.

    Returns:
        dict[str, str | int] | None: The current song's metadata if a song is playing, otherwise None.
    """

    command = "playerctl metadata --format '{{artist}}`{{title}}`{{album}}`{{position}}'"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    output = process.stdout.read().decode("utf-8").split("`")
    if len(output) == 1: return None # No song is playing
    artist, title, album, position = output
    # If app doesn't provide album, is it not be trusted to provide artist
    # Most of the times the artist is included in the title and that's ok
    if album == "": 
        title = _remove_text_inside_parentheses_and_brackets(title)
        artist = "" 

    return {"artist": artist, "title": title, "position": int(position)/1000000}


async def _get_current_song_meta_data_windows() -> dict[str, str | int] | None:
    """
    This function returns the current song's metadata if a song is playing, otherwise it returns None.
    It only works on Windows.

    Returns:
        dict[str, str | int] | None: The current song's metadata if a song is playing, otherwise None.
    """

    PLABACK_PAUSED = 5

    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    if current_session: 
        if current_session.get_playback_info().playback_status == PLABACK_PAUSED:
            return _get_current_song_meta_data_windows.last_returned_data
        
        # Get artist and title
        info = await current_session.try_get_media_properties_async()
        artist, title, album = info.artist, info.title, info.album_title

        # If app doesn't provide album, is it not be trusted to provide artist
        if album == "":
            title = _remove_text_inside_parentheses_and_brackets(title)
            artist = ""

        # Get position
        info = current_session.get_timeline_properties()
        seconds = info.position.total_seconds()
        not_update_time = time() - info.last_updated_time.timestamp()
        position = seconds + not_update_time
        _get_current_song_meta_data_windows.last_returned_position = {
            "artist": artist, "title": title, "position": position
        }
        return _get_current_song_meta_data_windows.last_returned_position
_get_current_song_meta_data_windows.last_returned_data = None


def _set_wallpaper_gnome(path: str):
    """
    This function sets the wallpaper to the image at the given path.
    It only works on Gnome 3 by using gsettings.

    Args:
        path (str): The path to the image to set as the wallpaper.
    """

    path = f"'{path}'"
    uri = "picture-uri" + ("-dark" if GNOME_THEME == "dark" else "")
    subprocess.Popen(f"gsettings set org.gnome.desktop.background {uri} file:{path}", shell=True)


def _set_wallpaper_windows(path: str):
    """
    This function sets the wallpaper to the image at the given path.

    Args:
        path (str): The path to the image to set as the wallpaper.
    """

    # Define constants
    SPI_SETDESKWALLPAPER = 0x0014
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02

    # Call the SystemParametersInfo function
    path = path.replace("\\", "/").replace("'", "")
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)


def _get_current_wallpaper_gnome() -> Image.Image:
    """
    This function returns the current wallpaper as a PIL Image.
    It only works on Gnome 3 by using gsettings.

    Returns:
        Image.Image: The current wallpaper as a PIL Image.
    """

    uri = "picture-uri" + ("-dark" if GNOME_THEME == "dark" else "")
    process = subprocess.Popen(f"gsettings get org.gnome.desktop.background {uri}", shell=True, stdout=subprocess.PIPE)
    process.wait()
    path = process.stdout.read().decode("utf-8").replace("file:", "").replace("\n", "").replace("'", "")
    # Store the current wallpaper path in the state
    state = get_state()
    if state["currentWallpaper"] != path:
        state["currentWallpaper"] = path
        set_state(state)
    return Image.open(path)


def _get_current_wallpaper_windows() -> Image.Image:
    """
    This function returns the current wallpaper as a PIL Image.
    This function only works on Windows.

    Returns:
        Image.Image: The current wallpaper as a PIL Image.
    """

    # Define constants
    SPI_GETDESKWALLPAPER = 0x0073
    MAX_PATH = 260

    # Create a buffer to store the wallpaper path
    wallpaper_buffer = ctypes.create_unicode_buffer(MAX_PATH)

    # Call the SystemParametersInfo function to get the wallpaper path
    ctypes.windll.user32.SystemParametersInfoW(SPI_GETDESKWALLPAPER, MAX_PATH, wallpaper_buffer, 0)

    # Extract the wallpaper path from the buffer
    wallpaper_path = wallpaper_buffer.value.replace("\\", "/").replace("'", "")
    # Store the current wallpaper path in the state
    state = get_state()
    if state["currentWallpaper"] != wallpaper_path:
        state["currentWallpaper"] = wallpaper_path
        set_state(state)

    return Image.open(wallpaper_path)


def get_available_fonts() -> list[str]:
    """
    This function returns a list of all the available fonts.

    Returns:
        list[str]: A list of all the available fonts.
    """

    return fm.get_font_names()


def get_font_path(font_name: str) -> str:
    """
    This function returns the path to the font with the given name.

    Args:
        font_name (str): The name of the font to get the path to.

    Returns:
        str: The path to the font with the given name.
    """

    return fm.findfont(font_name)


async def get_current_song_meta_data() -> dict[str, str | int] | None:
    """
    This function returns the current song's metadata if a song is playing, otherwise it returns None.

    Returns:
        dict[str, str | int] | None: The current song's metadata if a song is playing, otherwise None.
    """

    if DESKTOP == "Gnome":
        return _get_current_song_meta_data_gnome()
    elif DESKTOP == "Windows":
        return await _get_current_song_meta_data_windows()


def set_wallpaper(path: str):
    """
    This function sets the wallpaper to the image at the given path.

    Args:
        path (str): The path to the image to set as the wallpaper.

    """

    path = os.path.abspath(path)
    if DESKTOP == "Gnome": _set_wallpaper_gnome(path)
    elif DESKTOP == "Windows": _set_wallpaper_windows(path)


def get_current_wallpaper() -> Image.Image:
    """
    This function returns the current wallpaper as a PIL Image.

    Returns:
        Image.Image: The current wallpaper as a PIL Image.
    """

    if DESKTOP == "Gnome": return _get_current_wallpaper_gnome() 
    elif DESKTOP == "Windows": return _get_current_wallpaper_windows()


# Find out which desktop environment is being used
DESKTOP = platform.system()
if DESKTOP == "Linux":
    process = subprocess.Popen("gsettings get org.gnome.desktop.interface color-scheme",
        shell=True, stdout=subprocess.PIPE)
    process.wait()
    if process.returncode: raise NotImplementedError("Only gnome is supported on Linux")
    DESKTOP = "Gnome"
    if process.stdout.read().decode("utf-8").replace("\n", "") == "'prefer-dark'":
        GNOME_THEME = "dark"
    else:
        GNOME_THEME = "light"
elif DESKTOP == "Darwin":
    raise NotImplementedError("MacOS not supported")


if DESKTOP == "Windows":
    from winsdk.windows.media.control import \
        GlobalSystemMediaTransportControlsSessionManager as MediaManager
