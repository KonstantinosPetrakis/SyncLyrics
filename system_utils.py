import subprocess
import os
from PIL import Image


def _get_current_song_meta_data_gnome():
    command = "playerctl metadata --format '{{artist}}`{{title}}`{{position}}'"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    # Didn't use comma because it could be in the song title
    artist, title, position = process.stdout.read().decode("utf-8").split("`")
    return {"artist": artist, "title": title, "position": int(position)/1000000}


def _set_wallpaper_gnome(path):
    path = os.path.abspath(path)
    uri = "picture-uri" + ("-dark" if GNOME_THEME == "dark" else "")
    subprocess.Popen(f"gsettings set org.gnome.desktop.background {uri} file://{path}", shell=True)


def _get_current_wallpaper_gnome():
    uri = "picture-uri" + ("-dark" if GNOME_THEME == "dark" else "")
    process = subprocess.Popen(f"gsettings get org.gnome.desktop.background {uri}", shell=True, stdout=subprocess.PIPE)
    process.wait()
    path = process.stdout.read().decode("utf-8").replace("file://", "").replace("\n", "").replace("'", "")
    return Image.open(path)


def get_current_song_meta_data():
    if DESKTOP == "gnome":
        return _get_current_song_meta_data_gnome()
    raise NotImplementedError("Desktop not supported")


def set_wallpaper(path):
    if DESKTOP == "gnome":
        return _set_wallpaper_gnome(path)
    raise NotImplementedError("Desktop not supported")


def get_current_wallpaper():
    if DESKTOP == "gnome":
        return _get_current_wallpaper_gnome() 
    raise NotImplementedError("Desktop not supported")


# Find out which desktop environment is being used
process = subprocess.Popen("gsettings --version", shell=True, stdout=subprocess.DEVNULL)
process.wait()
if not process.returncode:
    DESKTOP = "gnome"
    process = subprocess.Popen("gsettings get org.gnome.desktop.interface color-scheme", shell=True, stdout=subprocess.PIPE)
    process.wait()
    if process.stdout.read().decode("utf-8").replace("\n", "") == "'prefer-dark'":
        GNOME_THEME = "dark"
    else:
        GNOME_THEME = "light"
