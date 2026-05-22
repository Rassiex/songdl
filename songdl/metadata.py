import os
import re
import numpy as np

_KEYS_MAJOR = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
_KEYS_MINOR = [k + "m" for k in _KEYS_MAJOR]
_ALL_KEYS = _KEYS_MAJOR + _KEYS_MINOR

# Krumhansl-Schmuckler profiles
_MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
_MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])


def extract_artist_title(info):
    title = info.get("title", "")
    uploader = info.get("uploader", "")
    track = info.get("track")
    artist = info.get("artist")

    if artist and track:
        return artist, track

    # "Official Video", "Lyrics", etc patterns to strip
    cleaned = re.sub(
        r"\s*[\(\[].*(?:official|video|lyric|audio|4K|HD|HQ|music\s*video).*?[\)\]]\s*",
        "",
        title,
        flags=re.IGNORECASE,
    )
    cleaned = cleaned.strip()

    # Try "Artist - Title" pattern
    m = re.match(r"^(.+?)\s*[-–—]\s*(.+)$", cleaned)
    if m:
        return m.group(1).strip(), m.group(2).strip()

    # Try "Title by Artist" pattern
    m = re.match(r"^(.+?)\s+by\s+(.+)$", cleaned, re.IGNORECASE)
    if m:
        return m.group(2).strip(), m.group(1).strip()

    # Try "Artist // Title" pattern
    m = re.match(r"^(.+?)\s*//\s*(.+)$", cleaned)
    if m:
        return m.group(1).strip(), m.group(2).strip()

    return uploader, cleaned or title


def camelot_key(key_name):
    mapping = {
        "C": "8B", "C#": "3B?",
        "D": "10B", "D#": "5B?",
        "E": "12B", "F": "7B?",
        "F#": "2B?", "G": "5B",
        "G#": "10B?", "A": "7B",
        "A#": "12B?", "B": "2B",
        "Cm": "5A", "C#m": "12A?",
        "Dm": "7A", "D#m": "2A?",
        "Em": "9A", "Fm": "4A?",
        "F#m": "11A", "Gm": "6A?",
        "G#m": "1A", "Am": "8A",
        "A#m": "3A?", "Bm": "10A",
    }
    return mapping.get(key_name, key_name)


def detect_bpm_key(filepath):
    try:
        import librosa
    except ImportError:
        return None, None

    # Ensure ffmpeg is findable for audioread
    import shutil
    if not shutil.which("ffmpeg"):
        local_ff = os.path.join(os.environ.get("LOCALAPPDATA", ""), "ffmpeg", "bin")
        if os.path.isfile(os.path.join(local_ff, "ffmpeg.exe")):
            os.environ["PATH"] = local_ff + os.pathsep + os.environ.get("PATH", "")

    try:
        y, sr = librosa.load(filepath, sr=22050, duration=60)
    except Exception:
        return None, None

    if len(y) < sr * 5:
        return None, None

    # BPM
    bpm = None
    try:
        tempo_arr = librosa.beat.tempo(y=y, sr=sr)
        if tempo_arr is not None and len(tempo_arr) > 0:
            t = float(tempo_arr[0])
            if 60 < t < 200:
                bpm = int(round(t))
    except Exception:
        pass

    # Key detection (Krumhansl-Schmuckler)
    try:
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)
        scores_major = [
            np.correlate(np.roll(chroma_mean, i), _MAJOR_PROFILE)[0] for i in range(12)
        ]
        scores_minor = [
            np.correlate(np.roll(chroma_mean, i), _MINOR_PROFILE)[0] for i in range(12)
        ]
        if max(scores_minor) > max(scores_major) * 1.05:
            key = _ALL_KEYS[12 + int(np.argmax(scores_minor))]
        else:
            key = _ALL_KEYS[int(np.argmax(scores_major))]
    except Exception:
        key = None

    return bpm, key
