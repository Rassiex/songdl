import os
import youtube_dl


def download_audio(url, output_dir, format="mp3", quality="192"):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": format,
            "preferredquality": quality,
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", url)
            ext = info.get("ext", format)
            filename = f"{title}.{format}"
            filepath = os.path.join(output_dir, filename)
            return {"success": True, "title": title, "filepath": filepath}
        except Exception as e:
            err = str(e).lower()
            if "ffmpeg" in err or "avconv" in err:
                return download_audio_native(url, output_dir)
            return {"success": False, "title": url, "error": str(e)}


def download_audio_native(url, output_dir):
    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", url)
            ext = info.get("ext", "m4a")
            filepath = os.path.join(output_dir, f"{title}.{ext}")
            return {"success": True, "title": title, "filepath": filepath, "native": True}
        except Exception as e:
            return {"success": False, "title": url, "error": str(e)}
