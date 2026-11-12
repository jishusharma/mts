"""Path 4 of YT_PROXY.md "Never blocked": captions from a public Invidious instance, so a locked address keeps working.

The request goes to the instance, never to YouTube, from this address: video id (or channel handle) only, no account, no
cookies, no personal data, a generic User-Agent, one request per step with a pause (OURS). The instance's own server talks to
YouTube. Also holds the waiting list (~/.mts/yt_waiting.json, git-ignored, next to the block record): a video no scripted
path could get, for a Claude desktop session to drain through the Browser 2 panel path.

    python scripts/dev/yt_transcript_sites.py ID [ID ...] --analyst NAME   # same cache files as fetch_captions_timed.py
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# OURS: public Invidious instances tried in order (found working 2026-11-12; instances come and go: env YT_SITE_INSTANCES
# overrides with a comma list). Instances behind a bot check (Cloudflare/Vercel challenge) are never worked around.
INSTANCES = ("yt.chocolatemoo53.com",)
USER_AGENT = "Mozilla/5.0 (compatible; transcript-reader)"
PAUSE_S = 4          # OURS: seconds between two requests to a site
TIMEOUT_S = 45
SITE_VIDEOS_PER_RUN = 12   # OURS: cap per run on videos asked of the sites


def instances():
    env = (os.environ.get("YT_SITE_INSTANCES") or "").strip()
    return tuple(h.strip() for h in env.split(",") if h.strip()) if env else INSTANCES


def http_get(url):
    """(status, text) of one GET with a generic User-Agent and nothing else; (0, "") when unreachable. Tests patch this."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, OSError, ValueError):
        return 0, ""


def _json(url):
    status, text = http_get(url)
    if status != 200:
        return None
    try:
        return json.loads(text)
    except ValueError:
        return None


def fetch_video(vid, langs=("en",), sleep=None):
    """{"cues": [(sec, text)], "info": {...}, "host": h} from the first instance that has captions, or None.
    Two requests per instance (captions, then metadata), PAUSE_S apart; a failing instance is skipped, never retried."""
    from fetch_captions_timed import parse_vtt
    sleep = sleep or time.sleep
    for host in instances():
        base = "https://" + host + "/api/v1/"
        for lang in langs:
            status, text = http_get(base + "captions/" + urllib.parse.quote(vid) + "?lang=" + urllib.parse.quote(lang))
            cues = parse_vtt(text) if status == 200 and text.lstrip().startswith("WEBVTT") else []
            if cues:
                break
        if not cues:
            sleep(PAUSE_S)
            continue
        sleep(PAUSE_S)
        meta = _json(base + "videos/" + urllib.parse.quote(vid)) or {}
        pub = meta.get("published")
        date = datetime.fromtimestamp(pub, timezone.utc).strftime("%Y%m%d") if isinstance(pub, (int, float)) else ""
        info = {"title": meta.get("title") or "", "upload_date": date, "uploader": meta.get("author") or "",
                "duration": meta.get("lengthSeconds")}
        return {"cues": cues, "info": info, "host": host}
    return None


def list_channel(handle, n=8, sleep=None):
    """[(video_id, title, YYYY-MM-DD)] newest first for @handle through the first instance that answers; [] on failure."""
    sleep = sleep or time.sleep
    for host in instances():
        base = "https://" + host + "/api/v1/"
        res = _json(base + "resolveurl?url=" + urllib.parse.quote("https://www.youtube.com/" + handle.lstrip("/"), safe=""))
        ucid = (res or {}).get("ucid")
        sleep(PAUSE_S)
        if not ucid:
            continue
        got = _json(base + "channels/" + urllib.parse.quote(ucid) + "/latest") or {}
        out = []
        for v in got.get("videos") or []:
            p = v.get("published")
            d = datetime.fromtimestamp(p, timezone.utc).strftime("%Y-%m-%d") if isinstance(p, (int, float)) else ""
            if v.get("videoId"):
                out.append((v["videoId"], v.get("title") or "", d))
        return out[:n]
    return []


# ---- waiting list -------------------------------------------------------------------------------------------

def waiting_file():
    return Path(os.environ.get("YT_WAITING_FILE") or Path.home() / ".mts" / "yt_waiting.json")


def read_waiting():
    try:
        data = json.loads(waiting_file().read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, ValueError):
        return []


def add_waiting(vid, channel="", paths_tried=(), now=None):
    """Append (or refresh) one entry: id, channel, time, paths tried. One entry per video id."""
    rows = [r for r in read_waiting() if r.get("id") != vid]
    rows.append({"id": vid, "channel": channel, "time": (now or datetime.now(timezone.utc)).isoformat(timespec="seconds"),
                 "paths_tried": list(paths_tried)})
    p = waiting_file()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rows, indent=1), encoding="utf-8", newline="\n")


def drop_waiting(vid):
    rows = read_waiting()
    keep = [r for r in rows if r.get("id") != vid]
    if len(keep) != len(rows):
        waiting_file().write_text(json.dumps(keep, indent=1), encoding="utf-8", newline="\n")


def pending(cache_dir=None):
    """Waiting entries whose transcript is not cached yet (a panel/ASR fetch by hand also clears an entry)."""
    rows = read_waiting()
    if cache_dir is not None:
        rows = [r for r in rows if not (Path(cache_dir) / (str(r.get("id")) + "_timed.txt")).exists()
                and not (Path(cache_dir) / (str(r.get("id")) + "_raw.txt")).exists()]
    return rows


def waiting_report(cache_dir=None):
    rows = pending(cache_dir)
    if not rows:
        return "WAITING: none"
    lines = [f"WAITING: {len(rows)} video(s); drain by the Browser 2 panel path (YT_PROXY.md path 3), then cache_panel_transcript.py"]
    lines += [f"  {r.get('id')}  {r.get('channel') or '-'}  {r.get('time')}  tried: {', '.join(r.get('paths_tried') or []) or '-'}"
              for r in rows]
    return "\n".join(lines)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--analyst", default="")
    ap.add_argument("--langs", default="en")
    ap.add_argument("--waiting", action="store_true")
    ap.add_argument("videos", nargs="*")
    a = ap.parse_args(argv)
    if a.waiting:
        print(waiting_report())
        return 0
    import fetch_captions_timed as f
    f.CANON.mkdir(exist_ok=True)
    bad = 0
    for i, vid in enumerate(a.videos):
        if i:
            time.sleep(PAUSE_S)
        r = f.site_fetch(vid, a.analyst, a.langs.split(","), Path(f.CANON))
        bad += not r.startswith(("OK", "EXISTS"))
        print(vid, r)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
