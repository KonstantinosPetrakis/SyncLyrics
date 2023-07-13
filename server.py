from os import path
from typing import Any

from flask import Flask, render_template, redirect, flash, request, Response

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


def guess_value_type(value: Any) -> Any:
    """
    This function guesses the type of the value.

    Args:
        value (Any): The value to guess the type of.

    Returns:
        Any: The value with the guessed type.
    """

    if value == "true": return True
    if value == "false": return False
    if value == "on": return True
    if value.isdigit(): return int(value)
    return value


@app.context_processor
def theme() -> dict: 
    """
    This function is passed to every template context.
    For now, it only returns the current theme.

    Returns:
        dict: A dictionary containing the current theme.
    """

    return {"theme": get_state()["theme"]}


@app.route("/")
def index() -> str:
    """
    This function returns the index page.

    Returns:
        str: The index page.
    """

    return render_template("index.html")


@app.route("/settings", methods=['GET', 'POST'])
def settings() -> str:
    """
    This function returns the settings page.
    It is also responsible for saving the settings using
    the state manager when a POST request is sent.

    Returns:
        str: The settings page.
    """

    state = get_state()
    if request.method == "POST":
        for key, state_key in VARIABLE_STATE_MAP.items():
            value = request.form.get(key, False, type=guess_value_type) 
            state = set_attribute_js_notation(state, state_key, value)

        set_state(state)
        flash("Settings have been saved! Restart your application.", "success")

    context = {key: get_attribute_js_notation(state, state_key) 
        for key, state_key in VARIABLE_STATE_MAP.items()}
    context["available_fonts"] = get_available_fonts() 
    
    return render_template("settings.html", **context)


@app.route("/lyrics")
def lyrics() -> list[str] | dict[str, str]:
    """
    This function returns the previous, current and next lyrics of the playing song as a list.
    If the lyrics are not found, it returns a dictionary with a message.

    Returns:
        list[str] | dict[str, str]: The previous, current and next lyrics of the playing song as a list. 
        If the lyrics are not found, it returns a dictionary with a message.
    """

    lyrics = get_timed_lyrics_previous_and_next()
    if type(lyrics) == str: return {"msg": lyrics} # lyrics not found
    return list(get_timed_lyrics_previous_and_next())


@app.route("/reset-defaults")
def reset_defaults() -> Response:
    """
    This function resets the settings to their default values and redirects to the settings page.

    Returns:
        Response: A redirect response to the settings page.
    """

    reset_state()
    flash("Settings have been reset!", "success")
    return redirect("/settings")
