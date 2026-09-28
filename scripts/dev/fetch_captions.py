"""Fetch YouTube captions (never video/audio) into raw_transcripts_canonical/ in the MTS format.

Usage (repo root):
    python scripts/dev/fetch_captions.py --analyst Malkan [--langs en,en-IN,hi] [--wait 0] ID_OR_URL [...]
IDs may start with '-' (pass them after '--' or as full URLs).
Manual English track first, then auto English, then the other langs. Existing files are never
overwritten. HTTP 429 -> exponential backoff (60s, 120s, ... up to 4 tries) per video.
One line per video: OK / EXISTS / NOCAPS / PRIVATE / RATELIMIT / ERROR.
"""
import argparse
import re
import sys
import tempfile
import time
from pathlib import Path

import yt_dlp

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "raw_transcripts_canonical"
ID_RE = re.compile(r"(?:v=|youtu\.be/|^)([A-Za-z0-9_-]{11})(?:[&?#]|$)")


def vid_of(s: str) -> str:
    m = ID_RE.search(s.strip())
    if not m:
        raise ValueError(f"no 11-char video id in {s!r}")
    return m.group(1)


def vtt_to_text(vtt: str) -> str:
    out, last = [], None
    for line in vtt.splitlines():
        line = line.strip()
        if (not line or line == "WEBVTT" or "-->" in line or line.startswith(("Kind:", "Language:", "NOTE"))
                or line.isdigit()):
            continue
        line = re.sub(r"<[^>]+>", "", line).replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")
        line = " ".join(line.split())
        if line and line != last:  # auto-captions repeat each rolling line
            out.append(line)
            last = line
    text = " ".join(out)
    return re.sub(r"\b(\w+(?: \w+){2,8}) \1\b", r"\1", text)  # collapse residual phrase echoes


def pick_track(info, langs):
    subs, autos = info.get("subtitles") or {}, info.get("automatic_captions") or {}
    for pool, kind in ((subs, "manual"), (autos, "auto")):
        for lang in langs:
            for key in (lang, lang + "-orig"):
                if key in pool:
                    return kind, key
    return None, None


def fetch(vid, analyst, langs):
    dest = OUT / f"{vid}_raw.txt"
    if dest.exists():
        return "EXISTS"
    url = f"https://www.youtube.com/watch?v={vid}"
    base = {"skip_download": True, "quiet": True, "no_warnings": True}
    delay = 60
    for attempt in range(4):
        try:
            with yt_dlp.YoutubeDL(base) as y:
                info = y.extract_info(url, download=False)
            kind, lang = pick_track(info, langs)
            if not kind:
                return "NOCAPS"
            with tempfile.TemporaryDirectory() as td:
                opts = dict(base, writesubtitles=kind == "manual", writeautomaticsub=kind == "auto",
                            subtitleslangs=[lang], subtitlesformat="vtt", outtmpl=str(Path(td) / "%(id)s"))
                with yt_dlp.YoutubeDL(opts) as y:
                    y.download([url])
                vtts = list(Path(td).glob("*.vtt"))
                if not vtts:
                    return "NOCAPS"
                text = vtt_to_text(vtts[0].read_text(encoding="utf-8", errors="replace"))
            d = info.get("upload_date") or ""
            pub = f"{d[:4]}-{d[4:6]}-{d[6:]}" if len(d) == 8 else ""
            OUT.mkdir(exist_ok=True)
            dest.write_text(
                f"# Video ID: {vid}\n# Title: {info.get('title', '')}\n# Published: {pub}\n"
                f"# Source: yt_dlp captions ({kind}, {lang}); uploader: {info.get('uploader', '')}\n"
                f"# Analyst: {analyst}\n# Word count: {len(text.split())}\n# ---\n{text}\n",
                encoding="utf-8", newline="\n")
            return f"OK {kind}/{lang} {len(text.split())}w"
        except yt_dlp.utils.DownloadError as e:
            msg = str(e)
            if "429" in msg or "Too Many Requests" in msg:
                time.sleep(delay)
                delay *= 2
                continue
            if "Private" in msg or "members" in msg.lower():
                return "PRIVATE"
            return f"ERROR {msg[:80]}"
    return "RATELIMIT"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--analyst", required=True)
    ap.add_argument("--langs", default="en,en-IN,en-US,hi")
    ap.add_argument("--wait", type=int, default=0, help="seconds to sleep first (rate-limit cooldown)")
    ap.add_argument("videos", nargs="+")
    a = ap.parse_args(argv)
    time.sleep(a.wait)
    bad = 0
    for v in a.videos:
        vid = vid_of(v)
        r = fetch(vid, a.analyst, a.langs.split(","))
        bad += not r.startswith(("OK", "EXISTS"))
        print(f"{vid} {r}", flush=True)
        time.sleep(20)  # be gentle between videos
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
