"""Fetch YouTube captions WITH timestamps (never video/audio) for the extraction pipeline.

Usage (repo root):
    python scripts/dev/fetch_captions_timed.py --analyst Krown [--out DIR] [--langs en] ID_OR_URL [...]
    python scripts/dev/fetch_captions_timed.py --analyst Krown --channel @handle --latest N
        [--scan 12] [--include REGEX] [--exclude REGEX] [--cookies FILE]
--channel lists the newest --scan uploads of the channel (flat, one yt-dlp call), drops titles matching
--exclude or (when --include is given) not matching --include, then fetches until N videos are OK/EXISTS
(videos without captions are skipped and do not count). --out defaults to raw_transcripts_canonical/.
The shared store is raw_transcripts_canonical/<video_id>_raw.txt (git-ignored; CBP and MTS both read it,
header carries `# Channel:` and `# Analyst:`). Exit 0 when every wanted video is OK/EXISTS.
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

try:
    import yt_dlp
except ImportError:   # CI pip line lacks it; the fetcher is a desktop tool, tests inject a stub
    yt_dlp = None

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


def list_channel(handle, scan, cookies=None):
    """Newest `scan` uploads of a channel as [(video_id, title)] (flat listing, no per-video calls)."""
    opts = {"quiet": True, "no_warnings": True, "extract_flat": True, "playlistend": scan}
    if cookies:
        opts["cookiefile"] = cookies
    with yt_dlp.YoutubeDL(opts) as y:
        info = y.extract_info(f"https://www.youtube.com/{handle}/videos", download=False)
    return [(e["id"], e.get("title") or "") for e in (info.get("entries") or []) if e and e.get("id")][:scan]


def video_date(vid, cookies=None):
    """Upload date YYYY-MM-DD of one video (metadata only, no captions); "" when unknown."""
    opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    if cookies:
        opts["cookiefile"] = cookies
    try:
        with yt_dlp.YoutubeDL(opts) as y:
            d = y.extract_info(f"https://www.youtube.com/watch?v={vid}", download=False).get("upload_date") or ""
    except yt_dlp.utils.DownloadError:
        return ""
    return f"{d[:4]}-{d[4:6]}-{d[6:]}" if len(d) == 8 else ""


def fetch(vid, analyst, langs, outdir, channel="", cookies=None):
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
                if cookies:
                    opts["cookiefile"] = cookies
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
                    f"# Analyst: {analyst}\n" + (f"# Channel: {channel}\n" if channel else "")
                    + f"# Duration_s:{info.get('duration')}\n# Word count: {words}\n# ---\n")
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


def fetch_channel(a):
    try:
        rows = list_channel(a.channel, a.scan, a.cookies)
    except yt_dlp.utils.DownloadError as e:
        print(f"{a.channel} LIST_FAILED {str(e)[:80]}")
        return 1
    inc, exc = re.compile(a.include) if a.include else None, re.compile(a.exclude) if a.exclude else None
    picked = 0
    for vid, title in rows:
        if picked >= a.latest:
            break
        if (exc and exc.search(title)) or (inc and not inc.search(title)):
            print(f"{vid} SKIP_OFFTOPIC", flush=True)
            continue
        if a.since and (video_date(vid, a.cookies) or "9") < a.since:
            print(f"{vid} OLDER_THAN_{a.since}", flush=True)
            break  # listing is newest-first: everything after is older too
        r = fetch(vid, a.analyst, a.langs.split(","), Path(a.out), a.channel, a.cookies)
        picked += r.startswith(("OK", "EXISTS"))
        print(f"{vid} {r}", flush=True)
        if r == "BOTCHECK":
            return 1
        if not r.startswith("EXISTS"):
            time.sleep(20)
    print(f"{a.channel}: {picked} of {a.latest}")
    return 0 if picked else 1


def main(argv):
    if yt_dlp is None:
        print("yt_dlp not installed: pip install yt-dlp")
        return 2
    ap = argparse.ArgumentParser()
    ap.add_argument("--analyst", required=True)
    ap.add_argument("--out", default=str(CANON))
    ap.add_argument("--channel", help="@handle; fetch its newest --latest on-topic videos")
    ap.add_argument("--latest", type=int, default=3)
    ap.add_argument("--scan", type=int, default=12, help="uploads to look through when listing a channel")
    ap.add_argument("--include", default="", help="regex: keep only titles matching")
    ap.add_argument("--exclude", default="", help="regex: drop titles matching")
    ap.add_argument("--since", default="", help="YYYY-MM-DD: with --channel, stop at the first video older than this")
    ap.add_argument("--cookies", default=None)
    ap.add_argument("--langs", default="en")
    ap.add_argument("videos", nargs="*")
    a = ap.parse_args(argv)
    bad = 0
    if a.channel:
        return fetch_channel(a)
    if not a.videos:
        ap.error("give video ids/URLs or --channel")
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
