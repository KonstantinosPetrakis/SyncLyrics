import requests as req

from system_utils import get_current_song_meta_data


current_song_data = None
current_song_lyrics = None


def _update_song():
    """
    This function updates the current song data and lyrics (the global variables).
    """

    global current_song_lyrics, current_song_data
    song_data = get_current_song_meta_data()
    
    if song_data != current_song_data and song_data is not None:
        current_song_data = song_data
        current_song_lyrics = _get_lyrics(song_data["artist"], song_data["title"])


def _get_lyrics(artist: str, title: str) -> list[tuple[float, str]]:
    """
    This function returns the lyrics of the given song by using the lrclib.net API.

    Args:
        artist (str): The artist of the song.
        title (str): The title of the song.

    Returns:
        list[tuple[float, str]]: The lyrics of the song.
    """

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


def _find_current_lyric_index(delta: float = 0.1) -> int:
    """
    This function returns the index of the current lyric in the current_song_lyrics list.

    Args:
        delta (float, optional): A delay to take into account when calculating the index. Defaults to 0.1.

    Returns:
        int: The index of the current lyric in the current_song_lyrics list. If a lyric is not found, -1 is returned.
    """

    if current_song_lyrics is not None:
        time = current_song_data["position"]
        for i in range(len(current_song_lyrics) - 1):
            if current_song_lyrics[i][0] <= time + delta < current_song_lyrics[i + 1][0]:
                return i
    return -1


def get_timed_lyrics(delta: int = 0) -> str:
    """
    This function returns the current lyric of the song.

    Args:
        delta (int, optional): The delay to take into account when calculating the lyric. Defaults to 0.

    Returns:
        str: The current lyric of the song. If a lyric is not found, "Lyrics not found" is returned.
    """

    _update_song()
    lyric_index = _find_current_lyric_index(delta)
    if lyric_index == -1: return "Lyrics not found"
    return current_song_lyrics[lyric_index][1]


def get_timed_lyrics_previous_and_next() -> tuple[str, str, str]:
    """
    This function returns the previous, current and next lyrics of the song.

    Returns:
        tuple[str, str, str]: The previous, current and next lyrics of the song. If a lyric is not found, "-" is returned.
    """

    def _lyric_representation(lyric_index: int) -> str:
        """
        This function returns the lyric representation of the given lyric index.

        Args:
            lyric_index (int): The index of the lyric in the current_song_lyrics list.

        Returns:
            str: The lyric representation of the given lyric index.
        """

        return current_song_lyrics[lyric_index][1] or "-"

    _update_song()
    lyric_index = _find_current_lyric_index()
    if lyric_index == -1: return "Lyrics not found"
    previous = _lyric_representation(lyric_index-1) if lyric_index > 0 else "-"
    current = _lyric_representation(lyric_index)
    next = (_lyric_representation(lyric_index+1)
        if lyric_index + 1 < len(current_song_lyrics) - 1 else "-")
    return previous, current, next
