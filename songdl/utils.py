import os
import re


def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', "_", name)


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def format_duration(seconds):
    if not seconds:
        return "?:??"
    h, r = divmod(int(seconds), 3600)
    m, s = divmod(r, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def format_size(bytes):
    if not bytes:
        return "Unknown"
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024
    return f"{bytes:.1f} TB"
