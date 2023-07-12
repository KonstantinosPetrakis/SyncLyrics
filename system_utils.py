import subprocess
import platform
import os
import re

from PIL import Image
import matplotlib.font_manager as fm

from state_manager import get_state, set_state


def _remove_text_inside_parentheses_and_brackets(text):
    return re.sub(r"\([^)]*\)|\[[^\]]*\]", '', text)


def _get_current_song_meta_data_gnome():
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


def _set_wallpaper_gnome(path):
    uri = "picture-uri" + ("-dark" if GNOME_THEME == "dark" else "")
    subprocess.Popen(f"gsettings set org.gnome.desktop.background {uri} file:{path}", shell=True)


def _get_current_wallpaper_gnome():
    uri = "picture-uri" + ("-dark" if GNOME_THEME == "dark" else "")
    process = subprocess.Popen(f"gsettings get org.gnome.desktop.background {uri}", shell=True, stdout=subprocess.PIPE)
    process.wait()
    path = process.stdout.read().decode("utf-8").replace("file://", "").replace("\n", "").replace("'", "")
    # Store the current wallpaper path in the state
    state = get_state()
    if state["currentWallpaper"] != path:
        state["currentWallpaper"] = path
        set_state(state)
    return Image.open(path)


def get_available_fonts():
    return fm.get_font_names()


def get_font_path(font_name):
    return fm.findfont(font_name)


def get_current_song_meta_data():
    if DESKTOP == "Gnome":
        return _get_current_song_meta_data_gnome()


def set_wallpaper(path):
    path = f"'{os.path.abspath(path)}'"
    if DESKTOP == "Gnome":
        return _set_wallpaper_gnome(path)


def get_current_wallpaper():
    if DESKTOP == "Gnome":
        return _get_current_wallpaper_gnome() 


# Find out which desktop environment is being used
DESKTOP = platform.system()
if DESKTOP == "Linux":
    process = subprocess.Popen("gsettings get org.gnome.desktop.interface color-scheme", shell=True, stdout=subprocess.PIPE)
    process.wait()
    if process.returncode: raise NotImplementedError("Only gnome is supported on Linux")
    DESKTOP = "Gnome"
    if process.stdout.read().decode("utf-8").replace("\n", "") == "'prefer-dark'":
        GNOME_THEME = "dark"
    else:
        GNOME_THEME = "light"
elif DESKTOP == "Windows":
    raise NotImplementedError("Windows not supported")
elif DESKTOP == "Darwin":
    raise NotImplementedError("MacOS not supported")
