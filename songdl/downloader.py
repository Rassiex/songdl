import os
import time
import shutil
import re
import yt_dlp

from .metadata import extract_artist_title, detect_bpm_key

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

_FFMPEG_LOCATION = shutil.which("ffmpeg")
if not _FFMPEG_LOCATION:
    local_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "ffmpeg", "bin", "ffmpeg.exe")
    if os.path.isfile(local_path):
        _FFMPEG_LOCATION = os.path.dirname(local_path)


def _sanitize(name):
    return re.sub(r'[<>:"/\\|?*]', "_", name)


def _make_opts(output_dir, **extra):
    opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_dir, "%(id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "user_agent": UA,
    }
    if _FFMPEG_LOCATION:
        opts["ffmpeg_location"] = _FFMPEG_LOCATION
    opts.update(extra)
    return opts


def _try_download(url, output_dir, opts, retries=2):
    for attempt in range(retries + 1):
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return {"success": True, "info": info}
        except Exception as e:
            err = str(e)
            if attempt < retries:
                time.sleep(1)
                continue
            if "ffmpeg" in err.lower() or "avconv" in err.lower():
                return None
            return {"success": False, "title": url, "error": err}
    return {"success": False, "title": url, "error": "Max retries exceeded"}


def _find_file(output_dir, video_id, ext):
    for f in os.listdir(output_dir):
        if f.startswith(video_id) and f.endswith("." + ext):
            return os.path.join(output_dir, f)
    for f in os.listdir(output_dir):
        if f.startswith(video_id):
            return os.path.join(output_dir, f)
    return None


def download_audio(url, output_dir, format="mp3", quality="192", analyze=True):
    opts = _make_opts(output_dir, postprocessors=[{
        "key": "FFmpegExtractAudio",
        "preferredcodec": format,
        "preferredquality": quality,
    }])
    result = _try_download(url, output_dir, opts)
    if result is None:
        return download_audio_native(url, output_dir)
    if not result["success"]:
        return result

    info = result["info"]
    video_id = info.get("id", "")
    artist, song_title = extract_artist_title(info)

    # Find downloaded file
    filepath = _find_file(output_dir, video_id, format) or _find_file(output_dir, video_id, "m4a")
    if not filepath:
        for f in os.listdir(output_dir):
            filepath = os.path.join(output_dir, f)
            break

    bpm = key = None
    if analyze and filepath and os.path.isfile(filepath):
        print(f"  Analyzing: {artist} - {song_title}")
        bpm, key = detect_bpm_key(filepath)

    # Build new filename
    tag = ""
    if key and bpm:
        tag = f" ({key} - {bpm}BPM)"
    elif key:
        tag = f" ({key})"
    elif bpm:
        tag = f" ({bpm}BPM)"

    new_name = _sanitize(f"{artist} - {song_title}{tag}.{format}")
    new_path = os.path.join(output_dir, new_name)

    if filepath and os.path.isfile(filepath):
        try:
            if os.path.exists(new_path):
                os.remove(new_path)
            os.rename(filepath, new_path)
        except Exception:
            new_path = filepath
            new_name = os.path.basename(filepath)

    return {
        "success": True,
        "title": f"{artist} - {song_title}",
        "artist": artist,
        "song": song_title,
        "filepath": new_path,
        "filename": new_name,
        "bpm": bpm,
        "key": key,
    }


def download_audio_native(url, output_dir, analyze=True):
    opts = _make_opts(output_dir, format="bestaudio[ext=m4a]/bestaudio/best")
    result = _try_download(url, output_dir, opts)
    if result is None:
        result = _try_download(url, output_dir, opts)
    if not result or not result["success"]:
        return result or {"success": False, "title": url, "error": "Download failed"}

    info = result["info"]
    video_id = info.get("id", "")
    artist, song_title = extract_artist_title(info)
    ext = "m4a"

    filepath = _find_file(output_dir, video_id, ext) or _find_file(output_dir, video_id, "webm")
    if not filepath:
        for f in os.listdir(output_dir):
            filepath = os.path.join(output_dir, f)
            break

    bpm = key = None
    if analyze and filepath and os.path.isfile(filepath):
        print(f"  Analyzing: {artist} - {song_title}")
        bpm, key = detect_bpm_key(filepath)

    tag = ""
    if key and bpm:
        tag = f" ({key} - {bpm}BPM)"
    elif key:
        tag = f" ({key})"
    elif bpm:
        tag = f" ({bpm}BPM)"

    new_name = _sanitize(f"{artist} - {song_title}{tag}.{ext}")
    new_path = os.path.join(output_dir, new_name)

    if filepath and os.path.isfile(filepath):
        try:
            if os.path.exists(new_path):
                os.remove(new_path)
            os.rename(filepath, new_path)
        except Exception:
            new_path = filepath
            new_name = os.path.basename(filepath)

    return {
        "success": True,
        "title": f"{artist} - {song_title}",
        "artist": artist,
        "song": song_title,
        "filepath": new_path,
        "filename": new_name,
        "bpm": bpm,
        "key": key,
        "native": True,
    }
