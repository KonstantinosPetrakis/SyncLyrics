from os import path

from flask import Flask, render_template, redirect, flash, request

from lyrics import get_timed_lyrics_previous_and_next
from system_utils import get_available_fonts
from state_manager import *


TEMPLATE_DIRECTORY = path.abspath("resources/templates")
STATIC_DIRECTORY = path.abspath("resources")
app = Flask(__name__, template_folder=TEMPLATE_DIRECTORY, static_folder=STATIC_DIRECTORY)
app.secret_key = "secret key"

VARIABLE_STATE_MAP = {
    "theme": "theme",
    "notification-method": "representationMethods.notifications",
    "wallpaper-method": "representationMethods.wallpaper",
    "terminal-method": "representationMethods.terminal",
    "font-size": "wallpaperSettings.fontSize",
    "font-color": "wallpaperSettings.fontColor",
    "wallpaper-font-color": "wallpaperSettings.pickColorFromWallpaper",
    "font-family": "wallpaperSettings.fontFamily",
    "font-stroke": "wallpaperSettings.fontStroke",
    "x-offset": "wallpaperSettings.xOffset",
    "y-offset": "wallpaperSettings.yOffset",
    "width": "wallpaperSettings.width",
    "height": "wallpaperSettings.height",
    "quality": "wallpaperSettings.quality",
    "scaling": "wallpaperSettings.scaling"
}


@app.context_processor
def theme(): return {"theme": get_state()["theme"]}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/settings", methods=['GET', 'POST'])
def settings():
    state = get_state()
    if request.method == "POST":
        for key, state_key in VARIABLE_STATE_MAP.items():
            value = request.form.get(key, False) 
            if value == "on": value = True
            state = set_attribute_js_notation(state, state_key, value)

        set_state(state)
        flash("Settings have been saved!", "success")

    context = {key: get_attribute_js_notation(state, state_key) 
        for key, state_key in VARIABLE_STATE_MAP.items()}
    context["available_fonts"] = get_available_fonts() 
    
    return render_template("settings.html", **context)


@app.route("/lyrics")
def lyrics():
    lyrics = get_timed_lyrics_previous_and_next()
    if type(lyrics) == str: return {"msg": lyrics} # lyrics not found
    return get_timed_lyrics_previous_and_next()


@app.route("/reset-defaults")
def reset_defaults():
    reset_state()
    flash("Settings have been reset!", "success")
    return redirect("/settings")
