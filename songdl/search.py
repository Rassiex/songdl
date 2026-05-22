import yt_dlp


def search_youtube(query, max_results=5):
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "force_generic_extractor": False,
    }
    search_query = f"ytsearch{max_results}:{query}"
    results = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(search_query, download=False)
            if info and "entries" in info:
                for entry in info["entries"]:
                    results.append({
                        "id": entry.get("id"),
                        "title": entry.get("title", "Unknown"),
                        "url": f"https://youtube.com/watch?v={entry.get('id')}",
                        "duration": entry.get("duration"),
                        "uploader": entry.get("uploader", "Unknown"),
                        "view_count": entry.get("view_count", 0),
                    })
        except Exception as e:
            print(f"  Search error: {e}")
    return results


def search_one(query):
    results = search_youtube(query, max_results=5)
    if not results:
        return None
    if len(results) == 1:
        return results[0]
    from .utils import format_duration
    print(f"\n  Search results for '{query}':")
    for i, r in enumerate(results, 1):
        dur = format_duration(r["duration"])
        print(f"  [{i}] {r['title']}")
        print(f"      {r['uploader']} | {dur} | {r['view_count']:,} views")
    while True:
        try:
            choice = input(f"  Choose 1-{len(results)} (Enter for #1): ").strip()
            if not choice:
                return results[0]
            idx = int(choice) - 1
            if 0 <= idx < len(results):
                return results[idx]
        except (ValueError, IndexError):
            pass
        print(f"  Invalid choice. Enter 1-{len(results)}.")
