import sys
sys.path.insert(0, r'C:\Users\Gibbo-Tech\songdl')

from songdl.search import search_youtube
from songdl.utils import format_duration, format_size
from songdl.playlist import create_playlist, add_song, save_playlist, load_playlist
import os
import tempfile

print("=== SongDL Test ===")
print()

# Test 1: Search
print("[1] Testing search...")
results = search_youtube("never gonna give you up", max_results=2)
assert len(results) > 0, "Search returned no results"
for r in results:
    dur = format_duration(r["duration"])
    print(f"  Found: {r['title']} ({dur}) - {r['uploader']}")
print("  SEARCH OK")
print()

# Test 2: Short download
print("[2] Testing download...")
url = results[0]["url"]
print(f"  URL: {url}")
with tempfile.TemporaryDirectory() as tmpdir:
    import yt_dlp
    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "outtmpl": os.path.join(tmpdir, "%(title)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            print(f"  Downloaded: {info.get('title')}")
            for f in os.listdir(tmpdir):
                size = format_size(os.path.getsize(os.path.join(tmpdir, f)))
                print(f"  File: {f} ({size})")
            print("  DOWNLOAD OK")
    except Exception as e:
        print(f"  Download error: {e}")
print()

# Test 3: Playlist
print("[3] Testing playlist...")
pl = create_playlist("Test Playlist")
add_song(pl, "Test Song", "https://youtube.com/watch?v=test")
pl_path = os.path.join(tempfile.gettempdir(), "test_playlist.json")
save_playlist(pl, pl_path)
loaded = load_playlist(pl_path)
assert loaded["name"] == "Test Playlist"
assert len(loaded["songs"]) == 1
assert loaded["songs"][0]["title"] == "Test Song"
os.remove(pl_path)
print("  PLAYLIST OK")
print()

print("=== TESTS COMPLETE ===")
