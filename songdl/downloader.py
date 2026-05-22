import os
import time
import shutil
import yt_dlp

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

_FFMPEG_LOCATION = shutil.which("ffmpeg")
if not _FFMPEG_LOCATION:
    local_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "ffmpeg", "bin", "ffmpeg.exe")
    if os.path.isfile(local_path):
        _FFMPEG_LOCATION = os.path.dirname(local_path)


def _make_opts(output_dir, **extra):
    opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
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
                title = info.get("title", url)
                return {"success": True, "title": title}
        except Exception as e:
            err = str(e)
            if attempt < retries:
                time.sleep(1)
                continue
            if "ffmpeg" in err.lower() or "avconv" in err.lower():
                return None
            return {"success": False, "title": url, "error": err}
    return {"success": False, "title": url, "error": "Max retries exceeded"}


def download_audio(url, output_dir, format="mp3", quality="192"):
    opts = _make_opts(output_dir, postprocessors=[{
        "key": "FFmpegExtractAudio",
        "preferredcodec": format,
        "preferredquality": quality,
    }])
    result = _try_download(url, output_dir, opts)
    if result is None:
        return download_audio_native(url, output_dir)
    return result


def download_audio_native(url, output_dir):
    opts = _make_opts(output_dir, format="bestaudio[ext=m4a]/bestaudio/best")
    result = _try_download(url, output_dir, opts)
    if result is None:
        result = _try_download(url, output_dir, opts)
    if result and result["success"]:
        result["native"] = True
    return result or {"success": False, "title": url, "error": "Download failed"}
