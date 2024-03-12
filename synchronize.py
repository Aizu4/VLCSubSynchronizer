import math
import more_itertools
import numpy as np

from moviepy.editor import AudioFileClip
from pysubparser import parser

MARGIN_MS = 10000
PRECISSION_MS = 100
SAMPLING_FPS = 16000


def load_audio_wave_array(filename: str):
    audio_clip = AudioFileClip(filename)
    audio_array = audio_clip.to_soundarray(fps=SAMPLING_FPS, nbytes=2)
    return stereo_to_mono(audio_array)


def normalized_rms_chunks(data, chunk_size: int):
    arr = [rms(chunk) for chunk in more_itertools.grouper(data, chunk_size, fillvalue=0.0)]
    return normalize(arr)


def stereo_to_mono(data):
    return np.mean(data, axis=1) if len(data.shape) == 2 else data


def load_subtitles_chunks(filename: str):
    subtitles = parser.parse(filename)
    timing_pairs = [
        (total_ms(line.start) // PRECISSION_MS, total_ms(line.end) // PRECISSION_MS)
        for line in subtitles
    ]

    size = timing_pairs[-1][1] + 1
    arr = [0] * size

    for start, end in timing_pairs:
        arr[start:end] = [1] * (end - start)
    return arr


def offset_subtitles_chunks(chunks, offset: int):
    if offset > 0:
        return [0] * offset + chunks[:-offset]
    elif offset < 0:
        return chunks[-offset:] + [0] * -offset
    return chunks


def total_ms(t) -> int:
    return int(t.hour * 3_600_000 + t.minute * 60_000 + t.second * 1000 + t.microsecond / 1000)


def normalize(data):
    avg = np.mean(data)
    std = np.std(data)
    return np.subtract(data, avg) / std


def rms(data):
    return np.sqrt(np.mean(np.square(data)))


def loss(arr1, arr2) -> float:
    diff = np.subtract(arr1, arr2)
    diff = np.fabs(diff)
    return np.mean(diff)  # noqa


def equalize_lengths(arr1: list, arr2: list) -> (list, list):
    if len(arr1) > len(arr2):
        arr1 = arr1[:len(arr2)]
    elif len(arr1) < len(arr2):
        arr2 = arr2[:len(arr1)]
    return arr1, arr2


def offset_in_ms(video_file: str, subtitle_file: str) -> int:
    base_subtitles_chunks = load_subtitles_chunks(subtitle_file)
    audio_wave_data = load_audio_wave_array(video_file)
    audio_chunks = normalized_rms_chunks(audio_wave_data, SAMPLING_FPS * PRECISSION_MS // 1000)

    margin = MARGIN_MS // PRECISSION_MS
    min_offset, min_loss = 0, math.inf
    for offset in range(-margin, margin + 1):
        subtitles_chunks = offset_subtitles_chunks(base_subtitles_chunks, offset)

        audio_chunks, subtitles_chunks = equalize_lengths(audio_chunks, subtitles_chunks)

        current_loss = loss(audio_chunks, subtitles_chunks)
        if current_loss < min_loss:
            min_loss, min_offset = current_loss, offset

    return min_offset * PRECISSION_MS

