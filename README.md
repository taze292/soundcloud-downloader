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
    5) Download Album
    6) Download all
    7) Exit

  [up/down] or [1-7] navigate   [Enter] select   [Esc] quit
```

- **Add URL(s)** — paste any number of SoundCloud links (one per line; enter a blank line to finish). Duplicates are skipped.
- **Loaded URLs** — browse the queue with the arrow keys. Press `Enter` on a track to download just that one, or `R` to remove the highlighted entry.
- **Remove URL(s)** — remove several at once using indices like `1,3`, ranges like `2-4`, or `all`.
- **Set download path** — change where files are saved (default `downloads/`, created automatically).
- **Download Album** — downloads a whole SoundCloud set/album (e.g. `.../user/sets/album-name`). Optionally enter a target directory; leave blank to save into `downloads/<album name>/`. Separate from the single-track queue above.
- **Download all** — downloads every loaded URL in order.

You can also pre-load URLs and options from the command line:

```
python download.py <url1> <url2> ... --path "C:/music"
```

And for scripting/non-interactive use:

```
python download.py <url1> <url2> --path "C:/music" --auto
python download.py --album "https://soundcloud.com/user/sets/album" --album-path "C:/music" --album-items "1-3"
```

`--album-items` limits the album download to specific track indices (e.g. `1-3` or `1,4`); without it the whole album is downloaded. If `--album-path` is omitted, files land in `<download path>/<album name>/`.

## Note on quality

SoundCloud streams are served as lossy audio (MP3/AAC/Opus). Converting to WAV cannot add quality beyond what SoundCloud provides, but it gives you a proper uncompressed `.wav`. If WAV conversion can't run (e.g. no ffmpeg), the original best-quality file is kept as-is.