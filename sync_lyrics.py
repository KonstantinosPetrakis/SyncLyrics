import asyncio
import webbrowser
import threading as th
import logging
import click
import atexit
import signal
from sys import exit
from os import path
from time import time
from typing import NoReturn


from desktop_notifier import DesktopNotifier
from pystray import Icon, Menu, MenuItem
from PIL import Image

from lyrics import get_timed_lyrics
from graphics import render_text_with_background, restore_wallpaper
from state_manager import get_state
from server import app


def handle_exit(*args, **kwargs) -> NoReturn:
    """
    Exit needs to be handled manually because that's required for handling 
    killing signals, otherwise the program will not exit properly.
    See https://stackoverflow.com/a/76254371/11718554
    """

    exit(0)


def run_tray() -> NoReturn:
    """
    Run the tray icon

    Returns:
        NoReturn: This function never returns.
    """

    Icon("SyncLyrics", Image.open(ICON_URL), menu=Menu(
        MenuItem("Open Lyrics", lambda: webbrowser.open(f"http://localhost:{PORT}"), default=True),
        MenuItem("Open Settings", lambda: webbrowser.open(f"http://localhost:{PORT}/settings")),
        MenuItem("Quit", handle_exit)
    )).run()


def run_server() -> NoReturn:
    """
    Run the flask server

    Returns:
        NoReturn: This function never returns.
    """

    # Mute output from flask
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    def secho(*args, **kwargs): pass
    def echo(*args, **kwargs): pass
    click.echo = echo
    click.secho = secho
    app.run(port=PORT, debug=False, use_reloader=False)
    print("Server ended")


async def main() -> NoReturn:
    """
    The main function of the program. It runs the server and the tray icon, and
    it also handles the lyrics rendering.

    Returns:
        NoReturn: This function never returns.
    """

    # We count the average latency for wallpaper method because it's heavy
    # And we want to take the render time into account 
    delta_sum = 0
    delta_count = 0
    methods = [method for method, active in get_state()["representationMethods"].items() if active]
    last_printed_lyric_per_method = {"wallpaper": None, "terminal": None, "notifications": None}

    while True:
        if "wallpaper" in methods:
            avg_latency = (delta_sum / delta_count) if delta_count > 0 else 0.1
            lyric = get_timed_lyrics(avg_latency)
            if lyric is not None and lyric != last_printed_lyric_per_method["wallpaper"]:
                t0 = time()
                render_text_with_background(lyric)
                delta = time() - t0
                delta_sum += delta
                delta_count += 1
                last_printed_lyric_per_method["wallpaper"] = lyric

        if "terminal" in methods:
            lyric = get_timed_lyrics()
            if lyric is not None and lyric != last_printed_lyric_per_method["terminal"]:
                print(lyric)
                last_printed_lyric_per_method["terminal"] = lyric
        
        if "notifications" in methods:
            lyric = get_timed_lyrics()
            if lyric is not None and lyric != last_printed_lyric_per_method["notifications"]:
                await notifier.clear_all()
                await notifier.send(title="SyncLyrics", message=lyric)
                last_printed_lyric_per_method["notifications"] = lyric



ICON_URL = path.abspath("./resources/images/icon.ico")
PORT = 9012

t_tray = th.Thread(target=run_tray, daemon=True).start()
t_server = th.Thread(target=run_server, daemon=True).start()
notifier = DesktopNotifier("SyncLyrics", ICON_URL)

# Restore wallpaper on exit (exit gracefully)
atexit.register(restore_wallpaper)
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

asyncio.run(main())
