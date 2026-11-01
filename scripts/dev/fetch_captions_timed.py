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
When yt-dlp gets HTTP 429 on the timedtext endpoint (IP-level, still happens with impersonation), the fetch falls back to
the youtube-transcript-api package (pip install youtube-transcript-api) which uses a different endpoint; the title/date
still come from yt-dlp metadata. Header `# Source:` says which path produced the file.
YouTube guard (shared with fetch_captions.py; we throttle, never evade): at most --max-videos (default 5) network
fetches per run, extra ids print DEFERRED; ONE try per video, 20 s between videos. The first 429 / "Sign in to confirm"
(yt-dlp and the transcript-api fallback both refused) writes blocked_until = now + 6 h plus the host name to
~/.mts/yt_block.json (outside the repo; override with env YT_BLOCK_FILE), prints the rest as UNVERIFIED and stops.
While blocked every run (any job) exits 3 with a message and makes no request. `--status` prints blocked/not blocked
and the last run's budget use, with no network call.
"""
import argparse
import json
import os
import socket
import re
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import yt_dlp
except ImportError:   # CI pip line lacks it; the fetcher is a desktop tool, tests inject a stub
    yt_dlp = None

ROOT = Path(__file__).resolve().parents[2]
CBP_HOME = Path(os.environ["CBP_HOME"]) if os.environ.get("CBP_HOME") else None
CANON = CBP_HOME / "raw_transcripts_canonical" if CBP_HOME else ROOT / "raw_transcripts_canonical"
ID_RE = re.compile(r"(?:v=|youtu\.be/|^)([A-Za-z0-9_-]{11})(?:[&?#]|$)")
TS_RE = re.compile(r"(\d+):(\d+):(\d+)[.,](\d+)\s+-->")
BLOCK_HOURS = 6
BLOCK_MARKS = ("429", "Too Many Requests", "Sign in to confirm")
EXIT_BLOCKED = 3


def block_file():
    return Path(os.environ.get("YT_BLOCK_FILE") or Path.home() / ".mts" / "yt_block.json")


def _utcnow():
    return datetime.now(timezone.utc)


def read_block():
    try:
        return json.loads(block_file().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def write_block(**upd):
    rec = read_block()
    rec.update(upd)
    p = block_file()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rec, indent=1), encoding="utf-8", newline="\n")


def blocked_until():
    """datetime the block ends, or None when not blocked (record missing, unreadable or expired)."""
    try:
        t = datetime.fromisoformat(read_block().get("blocked_until") or "")
    except ValueError:
        return None
    return t if t > _utcnow() else None


def mark_blocked():
    until = _utcnow() + timedelta(hours=BLOCK_HOURS)
    write_block(blocked_until=until.isoformat(timespec="seconds"), host=socket.gethostname())
    return until


def guard_status():
    until, rec = blocked_until(), read_block()
    head = (f"BLOCKED until {until.isoformat(timespec='seconds')} (host {rec.get('host', '?')})" if until
            else "NOT BLOCKED")
    return head + f"; last run budget used {rec.get('last_used', 0)} of {rec.get('last_max', '?')}"


def guarded_run(items, fetch_one, max_videos, pause=20):
    """items: [(id, dest_path)]. fetch_one(id)->status. Returns [(id, status)]; ids past the budget are DEFERRED,
    ids after a block are UNVERIFIED, EXISTS files cost no budget."""
    out, used, stopped = [], 0, False
    for vid, dest in items:
        if stopped:
            out.append((vid, "UNVERIFIED"))
        elif dest is not None and Path(dest).exists():
            out.append((vid, "EXISTS"))
        elif used >= max_videos:
            out.append((vid, "DEFERRED"))
        else:
            if used:
                time.sleep(pause)
            used += 1
            r = fetch_one(vid)
            out.append((vid, r))
            if r == "BLOCKED":
                mark_blocked()
                stopped = True
    write_block(last_used=used, last_max=max_videos, last_run=_utcnow().isoformat(timespec="seconds"))
    return out


def guard_gate(a):
    """Exit code to return now (--status or still blocked), else None."""
    if a.status:
        print(guard_status())
        return 0
    until = blocked_until()
    if until:
        print(f"YT_BLOCKED until {until.isoformat(timespec='seconds')}: no request made. {guard_status()}")
        return EXIT_BLOCKED
    return None


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


def transcript_api_cues(vid, langs):
    """([(start_s, text)], "auto"|"manual") from youtube-transcript-api, or None (not installed, no captions, blocked)."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        t = YouTubeTranscriptApi().fetch(vid, languages=list(langs))
        cues = [(int(s.start), " ".join(s.text.split())) for s in t.snippets if s.text.strip()]
    except Exception:   # library errors are many classes; any failure means "no fallback"
        return None
    return (cues, "auto" if t.is_generated else "manual") if cues else None


def meta(vid, cookies=None):
    """Title/date/uploader/duration of one video (metadata only); {} when YouTube refuses."""
    opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    if cookies:
        opts["cookiefile"] = cookies
    try:
        with yt_dlp.YoutubeDL(opts) as y:
            return y.extract_info(f"https://www.youtube.com/watch?v={vid}", download=False) or {}
    except yt_dlp.utils.DownloadError:
        return {}


def store(vid, analyst, outdir, channel, info, kind, cues, source):
    """Write DIR/<id>_timed.txt and the shared raw store file; returns the OK status string."""
    d = info.get("upload_date") or ""
    pub = f"{d[:4]}-{d[4:6]}-{d[6:]}" if len(d) == 8 else ""
    words = sum(len(t.split()) for _, t in cues)
    head = (f"# Video ID: {vid}\n# Title: {info.get('title', '')}\n# Published: {pub}\n"
            f"# Source: {source} ({kind}); uploader: {info.get('uploader', '')}\n"
            f"# Analyst: {analyst}\n" + (f"# Channel: {channel}\n" if channel else "")
            + f"# Duration_s:{info.get('duration')}\n# Word count: {words}\n# ---\n")
    body = "\n".join(f"[{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}] {t}" for s, t in cues)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / f"{vid}_timed.txt").write_text(head + body + "\n", encoding="utf-8", newline="\n")
    canon = CANON / f"{vid}_raw.txt"
    if not canon.exists():
        CANON.mkdir(exist_ok=True)
        canon.write_text(head.split("# Duration_s")[0] + f"# Word count: {words}\n# ---\n"
                         + " ".join(t for _, t in cues) + "\n", encoding="utf-8", newline="\n")
    return f"OK {kind} {words}w"


def fetch(vid, analyst, langs, outdir, channel="", cookies=None):
    dest = outdir / f"{vid}_timed.txt"
    if dest.exists():
        return "EXISTS"
    url = f"https://www.youtube.com/watch?v={vid}"
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
        return store(vid, analyst, outdir, channel, info, kind, cues, "yt_dlp captions")
    except yt_dlp.utils.DownloadError as e:
        msg = str(e)
        if any(m in msg for m in BLOCK_MARKS):
            got = transcript_api_cues(vid, langs)   # other endpoint; not blocked when timedtext 429s
            if got:
                return store(vid, analyst, outdir, channel, meta(vid, cookies), got[1], got[0],
                             "youtube_transcript_api")
            return "BLOCKED"   # ONE try per video; the guard records the block and stops the run
        return f"ERROR {msg[:80]}"


def fetch_channel(a):
    try:
        rows = list_channel(a.channel, a.scan, a.cookies)
    except yt_dlp.utils.DownloadError as e:
        print(f"{a.channel} LIST_FAILED {str(e)[:80]}")
        if any(m in str(e) for m in BLOCK_MARKS):
            mark_blocked()
        return 1
    inc, exc = re.compile(a.include) if a.include else None, re.compile(a.exclude) if a.exclude else None
    picked = 0
    failed = False
    outdir = Path(a.out)
    used, stopped = 0, False
    for vid, title in rows:
        if picked >= a.latest:
            break
        if (exc and exc.search(title)) or (inc and not inc.search(title)):
            print(f"{vid} SKIP_OFFTOPIC", flush=True)
            continue
        if a.since and not stopped:
            published = video_date(vid, a.cookies)
            if not published:
                print(f"{vid} DATE_FAILED", flush=True)
                failed = True
                continue
            if published < a.since:
                print(f"{vid} OLDER_THAN_{a.since}", flush=True)
                continue  # pinned uploads need not be in date order
        if stopped:
            r = "UNVERIFIED"
        elif (outdir / f"{vid}_timed.txt").exists():
            r = "EXISTS"
        elif used >= a.max_videos:
            r = "DEFERRED"
        else:
            if used:
                time.sleep(20)
            used += 1
            r = fetch(vid, a.analyst, a.langs.split(","), outdir, a.channel, a.cookies)
            if r == "BLOCKED":
                mark_blocked()
                stopped = True
        picked += r.startswith(("OK", "EXISTS"))
        failed |= not r.startswith(("OK", "EXISTS"))
        print(f"{vid} {r}", flush=True)
    write_block(last_used=used, last_max=a.max_videos, last_run=_utcnow().isoformat(timespec="seconds"))
    print(f"{a.channel}: {picked} of {a.latest}")
    return 1 if failed else 0


def main(argv):
    global CANON
    ap = argparse.ArgumentParser()
    ap.add_argument("--analyst", required=True)
    ap.add_argument("--out", default=str(CANON))
    ap.add_argument("--canonical-out", type=Path, help="shared raw transcript store (default: MTS canonical store)")
    ap.add_argument("--channel", help="@handle; fetch its newest --latest on-topic videos")
    ap.add_argument("--latest", type=int, default=3)
    ap.add_argument("--scan", type=int, default=12, help="uploads to look through when listing a channel")
    ap.add_argument("--include", default="", help="regex: keep only titles matching")
    ap.add_argument("--exclude", default="", help="regex: drop titles matching")
    ap.add_argument("--since", default="", help="YYYY-MM-DD: with --channel, stop at the first video older than this")
    ap.add_argument("--cookies", default=None)
    ap.add_argument("--langs", default="en")
    ap.add_argument("--max-videos", type=int, default=5, help="network fetches per run; extra ids are DEFERRED")
    ap.add_argument("--status", action="store_true", help="print blocked/not blocked + budget used; no network")
    ap.add_argument("videos", nargs="*")
    a = ap.parse_args(argv)
    gate = guard_gate(a)
    if gate is not None:
        return gate
    if yt_dlp is None:
        print("yt_dlp not installed: pip install yt-dlp")
        return 2
    if a.canonical_out:
        CANON = a.canonical_out
    if a.channel:
        return fetch_channel(a)
    if not a.videos:
        ap.error("give video ids/URLs or --channel")
    ids, bad = [], 0
    for v in a.videos:
        m = ID_RE.search(v.strip())
        if not m:
            print(f"{v} BADID")
            bad += 1
        else:
            ids.append(m.group(1))
    outdir = Path(a.out)
    res = guarded_run([(i, outdir / f"{i}_timed.txt") for i in ids],
                      lambda i: fetch(i, a.analyst, a.langs.split(","), outdir), a.max_videos)
    for vid, r in res:
        bad += not r.startswith(("OK", "EXISTS"))
        print(f"{vid} {r}", flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
