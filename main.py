from lyrics import get_timed_lyrics
from graphics import render_text_with_background
from time import time


last_printed_lyric = None
delta_sum = 0
delta_count = 0
while True:
    avg_latency = (delta_sum / delta_count) if delta_count > 0 else 0.1
    lyric = get_timed_lyrics(avg_latency)
    if lyric is not None and lyric != last_printed_lyric:
        t0 = time()
        render_text_with_background(lyric)
        delta_sum += time() - t0
        last_printed_lyric = lyric
        