# SoundCloud Downloader

Downloads a SoundCloud track from a URL in the highest available quality, converting to WAV when possible (falls back to the original format if conversion is unavailable).

Requires [ffmpeg](https://ffmpeg.org/) on your PATH to produce `.wav` files.

## Usage

```
pip install -r requirements.txt
python download.py https://soundcloud.com/artist/track
```

You can also pass multiple URLs at once:

```
python download.py <url1> <url2> ...
```

With no URL argument, the script asks for one interactively.

Downloads are saved to the `downloads/` folder.

## Note on quality

SoundCloud streams are served as lossy audio (MP3/AAC/Opus). Converting to WAV cannot add quality beyond what SoundCloud provides, but it gives you a proper uncompressed `.wav`. If WAV conversion can't run (e.g. no ffmpeg), the original best-quality file is kept as-is.