import requests as req
from system_utils import get_current_song_meta_data


current_song = None
current_song_lyrics = None


def _get_lyrics(artist, title):
    artist_title= f"{artist} {title}"
    song_id = req.request("GET", f"https://lrclib.net/api/search?q={artist_title}").json()
    if len(song_id) == 0: return None
    song_id = song_id[0]["id"]
    lyrics = req.request("GET", f"https://lrclib.net/api/get/{song_id}").json()["syncedLyrics"]
    if lyrics is None: return None

    processed_lyrics = []
    for lyric in lyrics.split("\n"):
        time = lyric[1: lyric.find("]") -1]
        m, s = time.split(":")
        seconds = float(m) * 60 + float(s)
        processed_lyrics.append((seconds, lyric[lyric.find("]") + 1:]))
    return processed_lyrics


def get_timed_lyrics(delta=0.1):
    global current_song, current_song_lyrics, song_data
    song_data = get_current_song_meta_data()
    
    if song_data != current_song:
        current_song_lyrics = _get_lyrics(song_data["artist"], song_data["title"])

    if current_song_lyrics is not None:
        time = song_data["position"]
        for i in range(len(current_song_lyrics) - 1):
            if current_song_lyrics[i][0] <= time + delta < current_song_lyrics[i + 1][0]:
                return current_song_lyrics[i][1]
    return "Lyrics not found"

            