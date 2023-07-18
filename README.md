# SyncLyrics

## Description
A cross-platform application that let's you sing along to your favorite songs regardless the player by displaying the lyrics of the currently playing song on your desktop wallpaper, notification pane, terminal or in a locally hosted webpage.

For more information check the SyncLyrics' [website](https://konstantinospetrakis.github.io/SyncLyrics/)!

**For linux playerctl is required**

## Run from source
```python
python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
python sync_lyrics.py
```

## Build
```python
python build.py 
```

## Known Issues
* Tray is partially broken (only default button works) on Linux in the compiled versions. (Works fine when running from source)
* Notification library has an issue on windows, I believe it will be fixed soon, see open issue: 
https://github.com/samschott/desktop-notifier/issues/95
