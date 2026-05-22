import re
import yt_dlp


def search_youtube(query, max_results=5, max_duration=None):
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
                    dur = entry.get("duration")
                    if max_duration is not None and dur and dur > max_duration:
                        continue
                    results.append({
                        "id": entry.get("id"),
                        "title": entry.get("title", "Unknown"),
                        "url": f"https://youtube.com/watch?v={entry.get('id')}",
                        "duration": dur,
                        "uploader": entry.get("uploader", "Unknown"),
                        "view_count": entry.get("view_count", 0),
                    })
        except Exception as e:
            print(f"  Search error: {e}")
    return results


def _fuzzy_variations(query):
    words = query.split()
    if len(words) <= 2:
        return []
    # Remove parentheticals like "(official video)"
    cleaned = re.sub(r"\s*[\(\[][^\)\]]*[\)\]]", "", query).strip()
    if cleaned and cleaned != query:
        yield cleaned
    # Try without the last word
    yield " ".join(words[:-1])
    # Try just the first 2 words
    if len(words) > 2:
        yield " ".join(words[:2])
    # Try just first and last word
    if len(words) > 3:
        yield f"{words[0]} {words[-1]}"


def search_with_fallback(query, max_duration=300):
    results = search_youtube(query, max_results=5, max_duration=max_duration)
    if results:
        return results
    for alt in _fuzzy_variations(query):
        results = search_youtube(alt, max_results=5, max_duration=max_duration)
        if results:
            return results
    return []


def search_one(query, max_duration=300):
    results = search_with_fallback(query, max_duration)
    if not results:
        # Last try: no duration filter
        results = search_youtube(query, max_results=5)
        if not results:
            return None
        # Show all results even if over 5 min
        from .utils import format_duration
        print(f"\n  No songs under 5 min found for '{query}'. All results:")
        for i, r in enumerate(results, 1):
            dur = format_duration(r["duration"])
            tag = " (over 5m)" if r["duration"] and r["duration"] > 300 else ""
            print(f"  [{i}] {r['title']} ({dur}){tag}")
            print(f"      {r['uploader']} | {r['view_count']:,} views")
        try:
            pick = input(f"  Pick 1-{len(results)} or Enter to skip: ").strip()
            if pick:
                idx = int(pick) - 1
                if 0 <= idx < len(results):
                    return results[idx]
        except ValueError:
            pass
        return None
    if len(results) == 1:
        return results[0]
    from .utils import format_duration
    print(f"\n  Search results for '{query}':")
    for i, r in enumerate(results, 1):
        dur = format_duration(r["duration"])
        print(f"  [{i}] {r['title']}")
        print(f"      {r['uploader']} | {dur} | {r['view_count']:,} views")
    print("  [R] Refine search")
    while True:
        choice = input(f"  Choose 1-{len(results)} (Enter for #1): ").strip().lower()
        if choice == "r":
            new_q = input("  New search: ").strip()
            if new_q:
                return search_one(new_q, max_duration)
            return None
        if not choice:
            return results[0]
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(results):
                return results[idx]
        except (ValueError, IndexError):
            pass
        print(f"  Invalid. Enter 1-{len(results)} or R.")


def fetch_playlist(url, max_duration=300):
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "force_generic_extractor": False,
    }
    entries = []
    pl_title = "Playlist"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if info:
                pl_title = info.get("title", "Playlist")
            if info and "entries" in info:
                for e in info["entries"]:
                    if e:
                        dur = e.get("duration")
                        if max_duration is not None and dur and dur > max_duration:
                            continue
                        entries.append({
                            "id": e.get("id"),
                            "title": e.get("title", "Unknown"),
                            "url": f"https://youtube.com/watch?v={e.get('id')}",
                            "duration": dur,
                            "uploader": e.get("uploader", info.get("uploader", "")),
                        })
        except Exception as e:
            print(f"  Playlist fetch error: {e}")
    return entries, pl_title
