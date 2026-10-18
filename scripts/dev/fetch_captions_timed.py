"""Fetch YouTube captions WITH timestamps (never video/audio) for the extraction pipeline.

Usage (repo root):
    python scripts/dev/fetch_captions_timed.py --analyst Krown --out DIR [--langs en] ID_OR_URL [...]
Writes DIR/<id>_timed.txt: header lines (# Video ID/Title/Published/Source/Analyst) then one cue per line
as `[HH:MM:SS] text`. Also writes raw_transcripts_canonical/<id>_raw.txt (untimed, same format as
fetch_captions.py) unless it exists. Existing timed files are skipped. One 20 s pause between videos.
"""
import argparse
import re
import sys
import tempfile
import time
from pathlib import Path

import yt_dlp

ROOT = Path(__file__).resolve().parents[2]
CANON = ROOT / "raw_transcripts_canonical"
ID_RE = re.compile(r"(?:v=|youtu\.be/|^)([A-Za-z0-9_-]{11})(?:[&?#]|$)")
TS_RE = re.compile(r"(\d+):(\d+):(\d+)[.,](\d+)\s+-->")


def parse_vtt(vtt):
    cues, start, last = [], None, None
    for line in vtt.splitlines():
        line = line.strip()
        m = TS_RE.match(line)
        if m:
            h, mi, s = int(m[1]), int(m[2]), int(m[3])
            start = h * 3600 + mi * 60 + s
            continue
        if (not line or line == "WEBVTT" or line.startswith(("Kind:", "Language:", "NOTE")) or line.isdigit()
                or start is None):
            continue
        t = re.sub(r"<[^>]+>", "", line).replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")
        t = " ".join(t.split())
        if t and t != last:
            cues.append((start, t))
            last = t
    return cues


def fetch(vid, analyst, langs, outdir):
    dest = outdir / f"{vid}_timed.txt"
    if dest.exists():
        return "EXISTS"
    url = f"https://www.youtube.com/watch?v={vid}"
    delay = 60
    for _ in range(4):
        try:
            with tempfile.TemporaryDirectory() as td:
                opts = {"skip_download": True, "quiet": True, "no_warnings": True, "writesubtitles": True,
                        "writeautomaticsub": True, "subtitleslangs": langs, "subtitlesformat": "vtt",
                        "outtmpl": str(Path(td) / "%(id)s")}
                with yt_dlp.YoutubeDL(opts) as y:
                    info = y.extract_info(url, download=True)
                vtts = list(Path(td).glob("*.vtt"))
                if not vtts:
                    return "NOCAPS"
                kind = "manual" if (info.get("subtitles") or {}) else "auto"
                cues = parse_vtt(vtts[0].read_text(encoding="utf-8", errors="replace"))
            d = info.get("upload_date") or ""
            pub = f"{d[:4]}-{d[4:6]}-{d[6:]}" if len(d) == 8 else ""
            words = sum(len(t.split()) for _, t in cues)
            head = (f"# Video ID: {vid}\n# Title: {info.get('title', '')}\n# Published: {pub}\n"
                    f"# Source: yt_dlp captions ({kind}); uploader: {info.get('uploader', '')}\n"
                    f"# Analyst: {analyst}\n# Duration_s: {info.get('duration')}\n# Word count: {words}\n# ---\n")
            body = "\n".join(f"[{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}] {t}" for s, t in cues)
            outdir.mkdir(parents=True, exist_ok=True)
            dest.write_text(head + body + "\n", encoding="utf-8", newline="\n")
            canon = CANON / f"{vid}_raw.txt"
            if not canon.exists():
                CANON.mkdir(exist_ok=True)
                canon.write_text(head.replace("# Duration_s", "# Duration_s").split("# Duration_s")[0]
                                 + f"# Word count: {words}\n# ---\n" + " ".join(t for _, t in cues) + "\n",
                                 encoding="utf-8", newline="\n")
            return f"OK {kind} {words}w"
        except yt_dlp.utils.DownloadError as e:
            msg = str(e)
            if "429" in msg or "Too Many Requests" in msg or "Sign in to confirm" in msg:
                if "Sign in to confirm" in msg:
                    return "BOTCHECK"
                time.sleep(delay)
                delay *= 2
                continue
            return f"ERROR {msg[:80]}"
    return "RATELIMIT"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--analyst", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--langs", default="en")
    ap.add_argument("videos", nargs="+")
    a = ap.parse_args(argv)
    bad = 0
    for v in a.videos:
        m = ID_RE.search(v.strip())
        if not m:
            print(f"{v} BADID")
            bad += 1
            continue
        r = fetch(m.group(1), a.analyst, a.langs.split(","), Path(a.out))
        bad += not r.startswith(("OK", "EXISTS"))
        print(f"{m.group(1)} {r}", flush=True)
        if r == "BOTCHECK":
            break
        time.sleep(20)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
