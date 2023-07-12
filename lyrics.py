import requests as req

from system_utils import get_current_song_meta_data


current_song_data = None
current_song_lyrics = None


def _update_song():
    global current_song_lyrics, current_song_data
    song_data = get_current_song_meta_data()
    
    if song_data != current_song_data and song_data is not None:
        current_song_data = song_data
        current_song_lyrics = _get_lyrics(song_data["artist"], song_data["title"])


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
        processed_lyrics.append((seconds, lyric[lyric.find("]") + 1:].strip()))
    return processed_lyrics


def find_current_lyric_index(delta=0.1):
    if current_song_lyrics is not None:
        time = current_song_data["position"]
        for i in range(len(current_song_lyrics) - 1):
            if current_song_lyrics[i][0] <= time + delta < current_song_lyrics[i + 1][0]:
                return i
    return -1


def get_timed_lyrics(delta=0):
    _update_song()
    lyric_index = find_current_lyric_index(delta)
    if lyric_index == -1: return "Lyrics not found"
    return current_song_lyrics[lyric_index][1]


def get_timed_lyrics_previous_and_next():
    def _lyric_representation(lyric_index):
        return current_song_lyrics[lyric_index][1] or "-"

    _update_song()
    lyric_index = find_current_lyric_index()
    if lyric_index == -1: return "Lyrics not found"
    previous = _lyric_representation(lyric_index-1) if lyric_index > 0 else "-"
    current = _lyric_representation(lyric_index)
    next = (_lyric_representation(lyric_index+1)
        if lyric_index + 1 < len(current_song_lyrics) - 1 else "-")
    return [previous, current, next]
