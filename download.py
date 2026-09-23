import argparse
import os
import re
import sys

import yt_dlp

DEFAULT_PATH = "downloads"

C_CYAN = "\x1b[36m"
C_GREEN = "\x1b[32m"
C_YELLOW = "\x1b[33m"
C_RED = "\x1b[31m"
C_DIM = "\x1b[2m"
C_BOLD = "\x1b[1m"
C_RESET = "\x1b[0m"
C_CLEAR = "\x1b[H\x1b[J"


def enable_vt():
    if os.name == "nt":
        os.system("")


def clear():
    sys.stdout.write(C_CLEAR)
    sys.stdout.flush()


def get_key():
    if os.name == "nt":
        import msvcrt
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):
            ch2 = msvcrt.getwch()
            return {"H": "UP", "P": "DOWN", "M": "RIGHT", "K": "LEFT"}.get(ch2, ch2)
        if ch == "\r":
            return "ENTER"
        if ch == "\x1b":
            return "ESC"
        if ch == "\x03":
            raise KeyboardInterrupt
        return ch
    import termios
    import tty
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    if ch == "\x1b":
        seq = sys.stdin.read(2)
        if seq == "[A":
            return "UP"
        if seq == "[B":
            return "DOWN"
        if seq == "[D":
            return "LEFT"
        if seq == "[C":
            return "RIGHT"
        return "ESC"
    if ch in ("\r", "\n"):
        return "ENTER"
    if ch == "\x03":
        raise KeyboardInterrupt
    return ch


def wait_enter():
    input()


def parse_indexes(text, count):
    result = set()
    for part in text.replace(" ", "").split(","):
        if not part:
            continue
        if part.lower() == "all":
            return set(range(1, count + 1))
        m = re.match(r"^(\d+)(?:-(\d+))?$", part)
        if not m:
            continue
        a = int(m.group(1))
        b = int(m.group(2)) if m.group(2) else a
        if a > b:
            a, b = b, a
        for n in range(a, b + 1):
            if 1 <= n <= count:
                result.add(n)
    return result


class Downloader:
    def __init__(self, urls=None, path=DEFAULT_PATH):
        self.urls = []
        self.path = path
        for u in urls or []:
            self.add_url(u)

    def add_url(self, url):
        url = url.strip()
        if not url:
            return False
        if url in self.urls:
            return False
        self.urls.append(url)
        return True

    def remove_index(self, idx):
        if 1 <= idx <= len(self.urls):
            self.urls.pop(idx - 1)

    def resolve_path(self):
        os.makedirs(self.path, exist_ok=True)

    def download(self, url):
        opts = {
            "outtmpl": f"{self.path}/%(title)s.%(ext)s",
            "format": "bestaudio/best",
            "noplaylist": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "0",
                }
            ],
        }
        print(f"\n  Downloading: {url}")
        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                print(f"  OK: {info.get('title')}")
                return True
            except (yt_dlp.utils.DownloadError,
                    yt_dlp.utils.ExtractorError,
                    yt_dlp.utils.PostProcessingError) as err:
                print(f"  {C_RED}FAILED:{C_RESET} {err}")
                return False

    def download_album(self, url, target_dir=None, items=None):
        if target_dir:
            outtmpl = f"{target_dir}/%(title)s.%(ext)s"
        else:
            outtmpl = f"{self.path}/%(playlist_title)s/%(title)s.%(ext)s"
        opts = {
            "outtmpl": outtmpl,
            "format": "bestaudio/best",
            "noplaylist": False,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "0",
                }
            ],
        }
        if items:
            opts["playlist_items"] = items
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)
        print(f"\n  Downloading album: {url}")
        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                title = info.get("title") or info.get("playlist_title") or "album"
                entries = info.get("entries")
                n = len(entries) if entries else (1 if info.get("title") else 0)
                print(f"  {C_GREEN}OK:{C_RESET} {title} ({n} track(s))")
                return True
            except (yt_dlp.utils.DownloadError,
                    yt_dlp.utils.ExtractorError,
                    yt_dlp.utils.PostProcessingError) as err:
                print(f"  {C_RED}FAILED:{C_RESET} {err}")
                return False


class App:
    def __init__(self, urls=None, path=DEFAULT_PATH):
        self.dl = Downloader(urls=urls, path=path)
        self.items = [
            ("Add URL(s)", self.add_urls),
            ("Loaded URLs", self.view_urls),
            ("Remove URL(s)", self.remove_urls),
            ("Set download path", self.set_path),
            ("Download Album", self.download_album_menu),
            ("Download all", self.download_all),
            ("Exit", self.exit_app),
        ]

    def header_lines(self):
        return [
            f"{C_CYAN}{C_BOLD}  SoundCloud Downloader{C_RESET}",
            "  ----------------------------------------",
            f"  {C_YELLOW}URLs loaded:{C_RESET} {len(self.dl.urls)}    "
            f"{C_YELLOW}Download path:{C_RESET} {self.dl.path}",
        ]

    def render_menu(self, idx):
        lines = self.header_lines()
        lines.append("")
        for i, (label, _) in enumerate(self.items):
            if i == idx:
                lines.append(f"  {C_CYAN}{C_BOLD}> {i + 1}) {label}{C_RESET}")
            else:
                lines.append(f"   {i + 1}) {label}")
        lines.append("")
        lines.append(
            f"{C_DIM}  [up/down] or [1-{len(self.items)}] navigate   [Enter] select   "
            f"[Esc] quit{C_RESET}"
        )
        return "\n".join(lines) + "\n"

    def run_menu(self):
        idx = 0
        while True:
            clear()
            sys.stdout.write(self.render_menu(idx))
            key = get_key()
            if key == "UP":
                idx = (idx - 1) % len(self.items)
            elif key == "DOWN":
                idx = (idx + 1) % len(self.items)
            elif key.isdigit() and 1 <= int(key) <= len(self.items):
                idx = int(key) - 1
            elif key in ("ENTER", "ESC"):
                action = self.items[idx][1]
                if key == "ESC":
                    action = self.exit_app
                clear()
                result = action()
                if result == "EXIT":
                    return

    def add_urls(self):
        print("  Paste one or more SoundCloud URLs (one per line).")
        print("  Enter an empty line when you're done.\n")
        added = 0
        skipped = 0
        while True:
            try:
                line = input("  URL > ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not line:
                break
            for raw in line.split():
                if self.dl.add_url(raw):
                    added += 1
                else:
                    skipped += 1
        if added:
            print(f"\n  {C_GREEN}Loaded {added} URL(s).{C_RESET}")
        if skipped:
            print(f"  {C_DIM}{skipped} skipped (duplicate or blank).{C_RESET}")
        wait_enter()

    def view_urls(self):
        if not self.dl.urls:
            print(f"  {C_YELLOW}No URLs loaded yet.{C_RESET}")
            wait_enter()
            return
        idx = 0
        while True:
            clear()
            lines = self.header_lines()
            lines.append("")
            lines.append(f"{C_BOLD}  Loaded URLs ({len(self.dl.urls)}){C_RESET}\n")
            for i, url in enumerate(self.dl.urls):
                mark = "> " if i == idx else "  "
                highlight = C_CYAN if i == idx else C_RESET
                lines.append(f"  {C_BOLD}{mark}{i + 1:>2}){C_RESET} {highlight}{url}{C_RESET}")
            lines.append("")
            lines.append(
                f"{C_DIM}  [up/down] move   [Enter] download   [R] remove   "
                f"[Esc] back{C_RESET}"
            )
            sys.stdout.write("\n".join(lines) + "\n")
            key = get_key()
            if key == "UP":
                idx = (idx - 1) % len(self.dl.urls)
            elif key == "DOWN":
                idx = (idx + 1) % len(self.dl.urls)
            elif key in ("r", "R"):
                self.dl.remove_index(idx + 1)
                if not self.dl.urls:
                    wait_enter()
                    return
                idx = min(idx, len(self.dl.urls) - 1)
            elif key == "ENTER":
                clear()
                self.dl.download(self.dl.urls[idx])
                wait_enter()
            elif key == "ESC":
                return

    def remove_urls(self):
        if not self.dl.urls:
            print(f"  {C_YELLOW}No URLs loaded yet.{C_RESET}")
            wait_enter()
            return
        print(f"  Loaded URLs ({len(self.dl.urls)}):\n")
        for i, url in enumerate(self.dl.urls):
            print(f"  {i + 1:>2}) {url}")
        print()
        try:
            text = input(
                "  Indices to remove (e.g. '1,3', '2-4', or 'all') > "
            ).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        idxs = sorted(parse_indexes(text, len(self.dl.urls)), reverse=True)
        if not idxs:
            print(f"\n  {C_YELLOW}Nothing removed.{C_RESET}")
        else:
            confirm = input(f"  Remove {len(idxs)} URL(s)? [y/N] > ").strip()
            if confirm.lower() in ("y", "yes"):
                removed = []
                for i in idxs:
                    removed.append(self.dl.urls[i - 1])
                    self.dl.remove_index(i)
                print(f"\n  {C_GREEN}Removed:{C_RESET}")
                for u in removed:
                    print(f"    - {u}")
            else:
                print(f"\n  {C_YELLOW}Cancelled.{C_RESET}")
        wait_enter()

    def set_path(self):
        try:
            new = input(f"  Download path [{self.dl.path}] > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if new:
            self.dl.path = new
            try:
                self.dl.resolve_path()
                print(f"\n  {C_GREEN}Download path set to: {new}{C_RESET}")
            except OSError as err:
                print(f"\n  {C_RED}Could not create path:{C_RESET} {err}")
        else:
            print(f"\n  {C_DIM}Keeping current path.{C_RESET}")
        wait_enter()

    def download_album_menu(self):
        try:
            url = input("  SoundCloud album/set URL > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not url:
            print(f"\n  {C_YELLOW}No URL entered.{C_RESET}")
            wait_enter()
            return
        try:
            tgt = input("  Download directory (blank = downloads/<album name>) > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        self.dl.download_album(url, target_dir=tgt or None)
        wait_enter()

    def download_all(self):
        if not self.dl.urls:
            print(f"  {C_YELLOW}No URLs loaded yet.{C_RESET}")
            wait_enter()
            return
        self.dl.resolve_path()
        total = len(self.dl.urls)
        ok = 0
        for n, url in enumerate(self.dl.urls, start=1):
            print(f"\n  {C_BOLD}[{n}/{total}]{C_RESET}")
            if self.dl.download(url):
                ok += 1
        print(f"\n  {C_GREEN}Done: {ok}/{total} downloaded to {self.dl.path}{C_RESET}")
        wait_enter()

    def exit_app(self):
        return "EXIT"

    def run(self):
        self.run_menu()
        return
        clear()
        print("  Bye.")


def main():
    parser = argparse.ArgumentParser(
        description="Interactive SoundCloud downloader: add, view, remove URLs "
                    "and download them as WAV (highest available quality)."
    )
    parser.add_argument("urls", nargs="*", help="SoundCloud URL(s) to pre-load")
    parser.add_argument(
        "--path", default=DEFAULT_PATH,
        help=f"Download folder (default: '{DEFAULT_PATH}')",
    )
    parser.add_argument(
        "--auto", action="store_true",
        help="Download all given URLs and exit (no interactive menu)",
    )
    parser.add_argument(
        "--album", metavar="URL",
        help="Download a SoundCloud album/set directly (no interactive menu)",
    )
    parser.add_argument(
        "--album-path", metavar="DIR",
        help="Folder for the album download (default: <download path>/<album name>)",
    )
    parser.add_argument(
        "--album-items", metavar="ITEMS",
        help="Restrict album tracks, e.g. '1-3' or '1,4' (default: all)",
    )
    args = parser.parse_args()

    enable_vt()
    if args.album:
        app = App(path=args.path)
        app.dl.download_album(args.album, target_dir=args.album_path,
                              items=args.album_items)
        return
    app = App(urls=args.urls, path=args.path)
    if args.auto:
        app.dl.resolve_path()
        for url in app.dl.urls:
            print(f"\n  {C_BOLD}[{url}]{C_RESET}")
            app.dl.download(url)
        print(f"\n  {C_GREEN}Done. Files in {app.dl.path}{C_RESET}")
        return
    try:
        app.run()
    except KeyboardInterrupt:
        clear()
        print("  Interrupted.")
        sys.exit(130)


if __name__ == "__main__":
    main()