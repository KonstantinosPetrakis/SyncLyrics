from os import path
import json 

from benedict import benedict


DEFAULT_STATE = {
    "theme": "dark",
    "currentWallpaper": None,
    "representationMethods": {
        "notifications": True,
        "wallpaper": False,
        "terminal": False
    },
    "wallpaperSettings": {
        "fontSize": 2.5, # in percent of wallpaper width
        "fontColor": "#FFC0CB", # hex color
        "pickColorFromWallpaper": True, # if true, fontColor is ignored
        "fontFamily": "Arial", 
        "fontStroke": 5, # in percent of font size (e.g 5% of 16px ~ 1px)
        "xOffset": 50, # in percent of screen width
        "yOffset": 80, # in percent of screen height
        "width": 100, # in percent of screen width
        "height": 100, # in percent of screen height
        "quality": 100, # in percent
        "scaling": 100, # in percent
    }
}

state = None # memory cache for state to avoid reading from disk


def reset_state(): set_state(DEFAULT_STATE)


def set_state(new_state):
    global state
    with open("state.json", "w") as f: json.dump(new_state, f, indent=4)
    state = None # clear memory cache


def get_state():
    global state
    if state is not None: return state # memory cache
    if not path.exists("state.json"): reset_state()
    with open("state.json", "r") as f: return json.load(f)


def set_attribute_js_notation(state, attribute, value):
    state = benedict(state, keypath_separator=".")
    state[attribute] = value
    return state.dict()


def get_attribute_js_notation(state, attribute):
    state = benedict(state, keypath_separator=".")
    return state[attribute]
