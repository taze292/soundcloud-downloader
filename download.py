import argparse
import sys

import yt_dlp


OUTDIR = "downloads"


def build_ydl_options():
    return {
        "outtmpl": f"{OUTDIR}/%(title)s [%(id)s].%(ext)s",
        "format": "bestaudio/best",
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "0",
            }
        ],
        "progress_hooks": [lambda d: print(f"  [{d['status']}] {d.get('_percent_str', '').strip() or ''} {d.get('_speed_str', '').strip() or ''}".rstrip())],
    }


def download(url):
    print(f"\nDownloading: {url}")
    with yt_dlp.YoutubeDL(build_ydl_options()) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            status = "OK"
        except yt_dlp.utils.DownloadError as err:
            status = f"FAILED: {err}"
        except yt_dlp.utils.ExtractorError as err:
            status = f"FAILED: {err}"
        print(f"{status}")
        try:
            for entry in (info.get("entries") or [info]):
                if entry:
                    print(f"  -> {entry.get('title')} ({entry.get('id')})")
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(description="Download SoundCloud tracks in highest quality (WAV when possible).")
    parser.add_argument("urls", nargs="*", help="SoundCloud track URL(s)")
    args = parser.parse_args()

    urls = args.urls
    if not urls:
        urls = [input("SoundCloud URL: ").strip()]

    for url in urls:
        if not url:
            continue
        download(url)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(1)