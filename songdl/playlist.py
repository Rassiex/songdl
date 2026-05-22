import json
import os
from datetime import datetime


def create_playlist(name, entries=None):
    return {
        "name": name,
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
        "songs": entries or [],
    }


def add_song(playlist, title, url):
    playlist["songs"].append({
        "title": title,
        "url": url,
        "added": datetime.now().isoformat(),
    })
    playlist["updated"] = datetime.now().isoformat()


def remove_song(playlist, index):
    if 0 <= index < len(playlist["songs"]):
        return playlist["songs"].pop(index)


def save_playlist(playlist, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(playlist, f, indent=2, ensure_ascii=False)


def load_playlist(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def list_playlists(directory):
    if not os.path.isdir(directory):
        return []
    return [f for f in os.listdir(directory) if f.endswith(".json")]
