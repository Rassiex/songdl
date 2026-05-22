import os
import sys
import json
from datetime import datetime

from . import __version__
from .search import search_one, search_youtube
from .downloader import download_audio
from .playlist import create_playlist, add_song, remove_song, save_playlist, load_playlist, list_playlists
from .utils import ensure_dir, format_duration, format_size

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".songdl")
PLAYLIST_DIR = os.path.join(CONFIG_DIR, "playlists")
ensure_dir(PLAYLIST_DIR)


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def print_header():
    clear()
    print("=" * 60)
    print("  SongDL v%s - YouTube Audio Downloader" % __version__)
    print("=" * 60)
    print()


def single_download_mode():
    query = input("  Song title: ").strip()
    if not query:
        return
    result = search_one(query)
    if not result:
        print("  No results found.")
        input("  Press Enter to continue...")
        return
    print(f"  Downloading: {result['title']}")
    out = input("  Output directory (Enter for ./downloads): ").strip() or "./downloads"
    out = ensure_dir(out)
    dl = download_audio(result["url"], out)
    if dl["success"]:
        print(f"  Done: {dl['title']}")
    else:
        print(f"  Failed: {dl.get('error', 'Unknown error')}")
    input("  Press Enter to continue...")


def batch_download_mode():
    print("  Paste song titles (one per line). Empty line to finish:")
    songs = []
    while True:
        line = sys.stdin.readline().strip()
        if not line:
            break
        songs.append(line)
    if not songs:
        return
    out = input("  Output directory (Enter for ./downloads): ").strip() or "./downloads"
    out = ensure_dir(out)
    auto = input("  Auto-pick first result? (y/N): ").strip().lower() == "y"
    downloaded = 0
    failed = 0
    for i, song in enumerate(songs, 1):
        print(f"\n  [{i}/{len(songs)}] {song}")
        if auto:
            results = search_youtube(song, max_results=1)
            if not results:
                print("  No results.")
                failed += 1
                continue
            result = results[0]
        else:
            result = search_one(song)
            if not result:
                print("  Skipped.")
                failed += 1
                continue
        dl = download_audio(result["url"], out)
        if dl["success"]:
            print(f"  Done: {dl['title']}")
            downloaded += 1
        else:
            print(f"  Failed: {dl.get('error', 'Unknown error')}")
            failed += 1
    print(f"\n  Done: {downloaded} downloaded, {failed} failed.")
    input("  Press Enter to continue...")


def playlist_mode():
    while True:
        print_header()
        print("  PLAYLIST MANAGER")
        print("  " + "-" * 56)
        print("  [1] Create a new playlist")
        print("  [2] View / edit a playlist")
        print("  [3] Download a playlist")
        print("  [4] Back to main menu")
        print()
        choice = input("  Choose: ").strip()
        if choice == "1":
            create_playlist_mode()
        elif choice == "2":
            view_playlist_mode()
        elif choice == "3":
            download_playlist_mode()
        elif choice == "4":
            break


def create_playlist_mode():
    name = input("  Playlist name: ").strip()
    if not name:
        return
    pl = create_playlist(name)
    print("  Add songs by searching YouTube.")
    while True:
        q = input("  Search for a song (Enter to finish): ").strip()
        if not q:
            break
        results = search_youtube(q, max_results=5)
        if not results:
            print("  No results.")
            continue
        from .utils import format_duration
        for i, r in enumerate(results, 1):
            dur = format_duration(r["duration"])
            print(f"  [{i}] {r['title']} ({dur}) - {r['uploader']}")
        pick = input(f"  Pick 1-{len(results)} or Enter to skip: ").strip()
        if pick:
            try:
                idx = int(pick) - 1
                if 0 <= idx < len(results):
                    add_song(pl, results[idx]["title"], results[idx]["url"])
                    print(f"  Added: {results[idx]['title']}")
            except ValueError:
                pass
    fpath = os.path.join(PLAYLIST_DIR, f"{sanitize_name(name)}.json")
    save_playlist(pl, fpath)
    print(f"  Playlist saved: {fpath}")


def view_playlist_mode():
    plists = list_playlists(PLAYLIST_DIR)
    if not plists:
        print("  No playlists found.")
        input("  Press Enter...")
        return
    print("  Available playlists:")
    for i, p in enumerate(plists, 1):
        pl = load_playlist(os.path.join(PLAYLIST_DIR, p))
        print(f"  [{i}] {pl['name']} ({len(pl['songs'])} songs)")
    pick = input(f"  Pick 1-{len(plists)}: ").strip()
    try:
        idx = int(pick) - 1
        if 0 <= idx < len(plists):
            pl = load_playlist(os.path.join(PLAYLIST_DIR, plists[idx]))
            show_playlist_songs(pl, os.path.join(PLAYLIST_DIR, plists[idx]))
    except (ValueError, IndexError):
        pass


def show_playlist_songs(pl, filepath):
    while True:
        print_header()
        print(f"  Playlist: {pl['name']} ({len(pl['songs'])} songs)")
        print("  " + "-" * 56)
        if not pl["songs"]:
            print("  (empty)")
        else:
            for i, s in enumerate(pl["songs"], 1):
                print(f"  [{i}] {s['title']}")
        print()
        print("  [N] Add new song")
        print("  [D#] Delete song (e.g. D3)")
        print("  [Q] Back")
        cmd = input("  Command: ").strip().lower()
        if cmd == "q":
            break
        elif cmd == "n":
            q = input("  Search: ").strip()
            if q:
                results = search_youtube(q, max_results=5)
                if results:
                    from .utils import format_duration
                    for i, r in enumerate(results, 1):
                        dur = format_duration(r["duration"])
                        print(f"  [{i}] {r['title']} ({dur}) - {r['uploader']}")
                    pick = input(f"  Pick 1-{len(results)}: ").strip()
                    if pick:
                        try:
                            idx2 = int(pick) - 1
                            if 0 <= idx2 < len(results):
                                add_song(pl, results[idx2]["title"], results[idx2]["url"])
                                save_playlist(pl, filepath)
                                print("  Added!")
                        except ValueError:
                            pass
        elif cmd.startswith("d"):
            try:
                sidx = int(cmd[1:]) - 1
                removed = remove_song(pl, sidx)
                if removed:
                    save_playlist(pl, filepath)
                    print(f"  Removed: {removed['title']}")
            except (ValueError, IndexError):
                pass
        input("  Press Enter...")


def download_playlist_mode():
    plists = list_playlists(PLAYLIST_DIR)
    if not plists:
        print("  No playlists found.")
        input("  Press Enter...")
        return
    print("  Select playlist to download:")
    for i, p in enumerate(plists, 1):
        pl = load_playlist(os.path.join(PLAYLIST_DIR, p))
        print(f"  [{i}] {pl['name']} ({len(pl['songs'])} songs)")
    pick = input(f"  Pick 1-{len(plists)}: ").strip()
    try:
        idx = int(pick) - 1
        if 0 <= idx < len(plists):
            pl = load_playlist(os.path.join(PLAYLIST_DIR, plists[idx]))
            out = input(f"  Output directory (Enter for ./downloads/{sanitize_name(pl['name'])}): ").strip()
            out = out or os.path.join("downloads", sanitize_name(pl["name"]))
            out = ensure_dir(out)
            downloaded = 0
            failed = 0
            for i, s in enumerate(pl["songs"], 1):
                print(f"\n  [{i}/{len(pl['songs'])}] {s['title']}")
                dl = download_audio(s["url"], out)
                if dl["success"]:
                    print(f"  Done: {dl['title']}")
                    downloaded += 1
                else:
                    print(f"  Failed: {dl.get('error', 'Unknown error')}")
                    failed += 1
            print(f"\n  Done: {downloaded} downloaded, {failed} failed.")
    except (ValueError, IndexError):
        pass
    input("  Press Enter...")


def sanitize_name(name):
    import re
    return re.sub(r'[<>:"/\\|?*]', "_", name)


def search_browse_mode():
    while True:
        q = input("  Search YouTube (Enter to go back): ").strip()
        if not q:
            break
        results = search_youtube(q, max_results=10)
        if not results:
            print("  No results.")
            input("  Press Enter...")
            continue
        from .utils import format_duration
        while True:
            print(f"\n  Results for '{q}':")
            for i, r in enumerate(results, 1):
                dur = format_duration(r["duration"])
                print(f"  [{i}] {r['title']}")
                print(f"      {r['uploader']} | {dur} | {r['view_count']:,} views")
            print("  [P] Download as playlist")
            print("  [Q] New search")
            cmd = input("  Choose number to download, or command: ").strip().lower()
            if cmd == "q":
                break
            if cmd == "p":
                pl_name = input("  Playlist name: ").strip()
                if pl_name:
                    pl = create_playlist(pl_name)
                    for r in results:
                        add_song(pl, r["title"], r["url"])
                    fpath = os.path.join(PLAYLIST_DIR, f"{sanitize_name(pl_name)}.json")
                    save_playlist(pl, fpath)
                    print(f"  Playlist saved with {len(results)} songs!")
                    dl_now = input("  Download now? (y/N): ").strip().lower() == "y"
                    if dl_now:
                        out = input("  Output directory (Enter for ./downloads): ").strip() or "./downloads"
                        out = ensure_dir(out)
                        for r in results:
                            print(f"\n  Downloading: {r['title']}")
                            dl = download_audio(r["url"], out)
                            if dl["success"]:
                                print(f"  Done")
                input("  Press Enter...")
                break
            try:
                idx = int(cmd) - 1
                if 0 <= idx < len(results):
                    out = input("  Output directory (Enter for ./downloads): ").strip() or "./downloads"
                    out = ensure_dir(out)
                    dl = download_audio(results[idx]["url"], out)
                    if dl["success"]:
                        print(f"  Done: {dl['title']}")
                    else:
                        print(f"  Failed: {dl.get('error', 'Unknown error')}")
                    input("  Press Enter...")
            except ValueError:
                pass


def main():
    import shutil
    has_ffmpeg = shutil.which("ffmpeg") is not None
    if not has_ffmpeg:
        print("  WARNING: ffmpeg not found - downloading native audio (m4a/opus)")
        print("  Get ffmpeg from https://ffmpeg.org for MP3 support")
        print()
    else:
        print("  ffmpeg OK - MP3 conversion enabled")
    print()
    input("  Press Enter to continue...")

    while True:
        print_header()
        print("  [1] Download a single song")
        print("  [2] Batch download (paste list)")
        print("  [3] Browse & search YouTube")
        print("  [4] Playlist manager")
        print("  [Q] Quit")
        print()
        choice = input("  Choose: ").strip().lower()
        if choice == "1":
            single_download_mode()
        elif choice == "2":
            batch_download_mode()
        elif choice == "3":
            search_browse_mode()
        elif choice == "4":
            playlist_mode()
        elif choice == "q":
            print("  Bye!")
            break


if __name__ == "__main__":
    main()
