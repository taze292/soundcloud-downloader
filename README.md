# SoundCloud Downloader

Interactive CLI that downloads SoundCloud tracks in the highest available quality, converting to `.wav` when ffmpeg is available (falls back to the original format otherwise).

Requires [ffmpeg](https://ffmpeg.org/) on your PATH to produce `.wav` files.

## Usage

```
pip install -r requirements.txt
python download.py
```

Run with no arguments to open the interactive menu:

```
  SoundCloud Downloader
  ----------------------------------------
  URLs loaded: 0    Download path: downloads

    1) Add URL(s)
    2) Loaded URLs
    3) Remove URL(s)
    4) Set download path
    5) Set output format
    6) Download Album
    7) Download all
    8) Exit

  [up/down] or [1-8] navigate   [Enter] select   [Esc] quit
```

- **Add URL(s)** — paste any number of SoundCloud links (one per line; enter a blank line to finish). Duplicates are skipped.
- **Loaded URLs** — browse the queue with the arrow keys. Press `Enter` on a track to download just that one, or `R` to remove the highlighted entry.
- **Remove URL(s)** — remove several at once using indices like `1,3`, ranges like `2-4`, or `all`.
- **Set download path** — change where files are saved (default `downloads/`, created automatically).
- **Set output format** — `wav` (default), `mp3`, `flac`, `m4a`, `opus`, or `best` (keep SoundCloud's original file). Every format gets embedded tags (title, artist, album, track, genre, date, description); `mp3`/`flac`/`m4a`/`opus`/`best` also embed the album cover art. WAV can't hold pictures, so it gets text tags only.
- **Download Album** — downloads a whole SoundCloud set/album (e.g. `.../user/sets/album-name`). Optionally enter a target directory; leave blank to save into `downloads/<album name>/`. Tracks get the album name and track numbers tagged. Separate from the single-track queue above.
- **Download all** — downloads every loaded URL in order.
- **Exit**

You can also pre-load URLs and options from the command line:

```
python download.py <url1> <url2> ... --path "C:/music" --format flac
```

And for scripting/non-interactive use:

```
python download.py <url1> <url2> --path "C:/music" --format mp3 --auto
python download.py --album "https://soundcloud.com/user/sets/album" --album-path "C:/music" --album-items "1-3" --format flac
```

`--album-items` limits the album download to specific track indices (e.g. `1-3` or `1,4`); without it the whole album is downloaded. If `--album-path` is omitted, files land in `<download path>/<album name>/`.

## Note on quality

SoundCloud streams are served as lossy audio (MP3/AAC/Opus). Converting to WAV or FLAC cannot add quality beyond what SoundCloud provides — WAV just unpacks it to uncompressed PCM, FLAC keeps it lossless from the stream onward. For cover art + tags use `mp3`, `flac`, `m4a`, or `opus`.