# SongDL

A YouTube audio downloader with search, interactive browsing, and playlist management.

## Features

- **Search & Download** – Search YouTube from the CLI, pick from results
- **Batch Download** – Paste a list of song titles, download them all
- **Browse Mode** – Search YouTube, preview results, download individually or save as playlist
- **Playlist Manager** – Create, edit, save, and download playlists
- **Auto or Manual** – Auto-pick the first result or choose from multiple matches

## Installation

```bash
pip install -r requirements.txt
```

Or install as a package:

```bash
pip install .
```

Then run:

```bash
python -m songdl
```

## Usage

Run the interactive menu:

```bash
python -m songdl
```

### Single download

```
[1] Download a single song
> Enter song title
> Pick from search results
> Choose output directory
```

### Batch download

```
[2] Batch download (paste list)
> Paste one song per line, empty line to finish
> Choose auto-pick or manual selection
```

### Browse YouTube

```
[3] Browse & search YouTube
> Search anything
> See 10 results with duration, uploader, views
> Download individual songs
> Save results as a playlist
```

### Playlist manager

```
[4] Playlist manager
> Create playlists by searching and adding songs
> View/edit existing playlists (add/remove songs)
> Download entire playlists
```

## Requirements

- Python 3.6+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (active fork of youtube-dl)
- [ffmpeg](https://ffmpeg.org/) (optional – for MP3 conversion; without it, downloads use native m4a/opus)
