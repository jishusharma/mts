"""Run CBP once: fetch new analyst videos (last 5 days), extract, quote-check, store. No scheduler, no daemon.

    python scripts/dev/cbp_run.py --due     # only if a UTC window is open and not yet done in it
    python scripts/dev/cbp_run.py --force   # whenever the operator asks

Windows (UTC, OURS): EU 09:00-13:00, pre-US 13:00-midnight. Scheduled starts: 09:00 and 13:00;
windows stay open for retries and catch-up. A coordinator may also call --due on each wake;
the stamp file lives outside the repo (CBP_STAMP, default CBP_HOME/cbp_store/stamp.json).
Only the actionable analysts in <CBP_HOME>/cbp_v2/analysts.json are fetched; videos already in the store
(or already rejected) are skipped; nothing older than 5 days is fetched. One LLM pass per new video.
Output: one line "cbp: +<added> rows, <total> total, window end <date>[, <n> rejected]".
Rows are read by MyTradingSys/cbp (cbp.query). Data stays outside the repo (CBP_STORE, CBP_HOME).
CBP_HOME: the CBP_HOME env var when set; else the legacy F:/CryptoScrapper when that folder exists on this
machine; else a folder under this checkout (runtime_data/cbp). No step in this script assumes a fixed
machine or Gemini: the fetcher is yt-dlp (fetch_captions_timed.py) with a youtube-transcript-api fallback;
Gemini (gemini_queue.py) is a separate, optional path for open-ended search/grounding, not a dependency here.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, time, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "MyTradingSys"))
import cbp  # noqa: E402
import verify_extract_quotes as vq  # noqa: E402


default_cbp_home = cbp.default_cbp_home


CBP_HOME = default_cbp_home()
TRANSCRIPTS = Path(os.environ.get("CBP_TRANSCRIPTS", str(CBP_HOME / "raw_transcripts_canonical")))
WINDOWS = (("EU", time(9, 0), time(13, 0)), ("PRE_US", time(13, 0), None))
MODEL = os.environ.get("CBP_MODEL", "claude-sonnet-5-5")
PROMPT = """You extract what ONE crypto analyst says in ONE video.
Analyst: %(analyst)s. Published: %(published)s. Title: "%(title)s".
Output ONLY a JSON object, nothing else:
{"bias": "BULLISH|BEARISH|NEUTRAL|NO_VIEW", "symbols": ["BTC",...],
 "quotes": ["<=25 words, verbatim from the transcript"],
 "trades": [{"asset":"BTC","direction":"LONG|SHORT","entry":"...","target":"...","invalidation":"...","quote":"verbatim"}],
 "pointers": ["a level or condition the analyst names, short"]}
Rules: only what the analyst says, no inference, no filling gaps. A trade needs entry, target and invalidation in
their words (use "" for any not stated). Every quote and trade.quote must be copied verbatim from the transcript
(auto-captions: copy the caption words as they are). bias is the analyst's own stance on BTC.
"""


def stamp_path():
    return Path(os.environ.get("CBP_STAMP", str(cbp.default_cbp_home() / "cbp_store" / "stamp.json")))


def read_stamp():
    try:
        return json.loads(stamp_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def open_window(now):
    """The WINDOWS entry containing `now` (UTC time), or None."""
    t = now.astimezone(timezone.utc).time()
    for name, start, end in WINDOWS:
        if end is None:
            if t >= start:
                return name
        elif start <= t < end:
            return name
    return None


def is_due(now, stamp):
    """Window name if a window is open AND not yet recorded in stamp for today; None otherwise."""
    w = open_window(now)
    if not w:
        return None
    day = now.astimezone(timezone.utc).date().isoformat()
    entry = day + ":" + w
    return None if entry in stamp.get("done", []) else w


def write_stamp(now, window):
    """Keep only the last 4 entries; the stamp is a bookmark, not a log."""
    s = read_stamp()
    day = now.astimezone(timezone.utc).date().isoformat()
    done = (s.get("done", []) + [day + ":" + window])[-4:] if window else s.get("done", [])
    stamp_path().parent.mkdir(parents=True, exist_ok=True)
    tmp = stamp_path().with_suffix(".tmp")
    tmp.write_text(json.dumps({"done": done, "last_run": now.isoformat()}), encoding="utf-8", newline="\n")
    os.replace(tmp, stamp_path())


def analysts():
    cfg = json.loads((CBP_HOME / "cbp_v2" / "analysts.json").read_text(encoding="utf-8"))
    return cfg, [a for a in cfg["analysts"] if a.get("enabled") and a.get("profile") == "actionable"]


def fetch_new(cutoff, store, run=subprocess.run):
    """yt-dlp captions for each actionable analyst, newest first, stopping at `cutoff` (YYYY-MM-DD).
    Existing transcripts are skipped by fetch_captions_timed, so reruns download nothing new."""
    cfg, ans = analysts()
    cookies = CBP_HOME / "cookies_utube_1.txt"
    for an in ans:
        cmd = [sys.executable, str(HERE / "fetch_captions_timed.py"), "--analyst", an["short"],
               "--channel", an["channel"], "--latest", "6", "--scan", "8", "--since", cutoff,
               "--out", str(TRANSCRIPTS), "--canonical-out", str(TRANSCRIPTS), "--exclude", cfg["exclude_regex"]]
        if an.get("topic_filter"):
            cmd += ["--include", cfg["include_regex"]]
        if cookies.exists():
            cmd += ["--cookies", str(cookies)]
        result = run(cmd, check=False)
        result.check_returncode()


def parse_transcript(path):
    """(meta, body) of a fetch_captions_timed file or a CBP inbox file."""
    text = path.read_text(encoding="utf-8", errors="replace")
    head, _, body = text.partition("# ---\n") if "# ---\n" in text else ("", "", text)
    meta = {}
    for line in head.splitlines():
        m = re.match(r"#\s*([A-Za-z ]+?):\s*(.*)", line)
        if m:
            meta[m.group(1).strip().lower()] = m.group(2).strip()
    return meta, body


def local_videos(cutoff):
    """[(video_id, analyst, published, title, path, channel)] of transcripts on disk published on/after cutoff."""
    out = []
    seen = set()
    for p in sorted(TRANSCRIPTS.glob("*_timed.txt")) + sorted(TRANSCRIPTS.glob("*_raw.txt")):
        meta, _ = parse_transcript(p)
        if meta.get("video id") in seen:
            continue
        if meta.get("published", "") >= cutoff and meta.get("analyst") and meta.get("video id"):
            channel = meta.get("channel")
            out.append((meta["video id"], meta["analyst"], meta["published"], meta.get("title", ""), p, channel))
            seen.add(meta["video id"])
    return out


def llm_extract(video, body, run=subprocess.run):
    """One `claude -p` pass per video; returns the parsed JSON object or raises ValueError."""
    vid, analyst, published, title, _ = video[:5]
    prompt = PROMPT % {"analyst": analyst, "published": published, "title": title.replace('"', "'")}
    # --setting-sources "": project hooks need a session's CLAUDE_PROJECT_DIR and block `claude -p` run from a task
    r = run(["claude", "-p", "--model", MODEL, "--tools", "", "--no-session-persistence", "--setting-sources", ""],
            input=prompt + body, capture_output=True, text=True, encoding="utf-8", timeout=600)
    r.check_returncode()
    m = re.search(r"\{.*\}", r.stdout or "", re.S)
    if not m:
        raise ValueError("no JSON from extractor: " + (r.stderr or r.stdout or "")[:120])
    return json.loads(m.group(0))


def build_row(video, got, body):
    """Row from the extractor's object, or (None, reason). Every quote must occur in the transcript, checked with
    verify_extract_quotes (the one checker); one fabricated quote rejects the whole row."""
    vid, analyst, published = video[0], video[1], video[2]
    channel = video[5] if len(video) > 5 else None
    norm_body = vq.norm(vq.TIMESTAMP.sub(" ", body))
    quotes = [q for q in got.get("quotes") or [] if isinstance(q, str) and q.strip()]
    trades = [t for t in got.get("trades") or [] if isinstance(t, dict)]
    for q in quotes + [str(t.get("quote") or "") for t in trades]:
        bad = vq.first_missing(q, norm_body) if q.strip() else "empty quote"
        if bad is not None:
            return None, "quote not in transcript: " + bad.strip()[:60]
    row = {"analyst": analyst, "video_id": vid, "published": published,
           **({"channel": channel} if channel else {}),
           "bias": got.get("bias") if got.get("bias") in cbp.BIASES else "NO_VIEW",
           "symbols": [str(s).upper() for s in got.get("symbols") or []],
           "quotes": quotes,
           "trades": [{k: str(t.get(k) or "") for k in cbp.TRADE_FIELDS} for t in trades],
           "pointers": [str(p) for p in got.get("pointers") or []],
           "quote_verified": True,
           "expires_at": (datetime.fromisoformat(published) + timedelta(days=cbp.WINDOW_DAYS)).strftime("%Y-%m-%dT00:00:00Z")}
    errs = cbp.validate_row(row)
    return (None, "; ".join(errs)) if errs else (row, "")


def run_once(now, fetch=fetch_new, extract=llm_extract, store=None):
    """Fetch, extract new videos, write the store. Returns (added, total, rejected)."""
    cutoff = (now - timedelta(days=cbp.WINDOW_DAYS)).date().isoformat()
    data = cbp.load(store)
    known = {(r["video_id"], r["analyst"]) for r in data["rows"]} | {(x[0], x[1]) for x in data["rejected"]}
    fetch(cutoff, known)
    added = rejected = 0
    failures = []
    for video in local_videos(cutoff):
        if (video[0], video[1]) in known:
            continue
        _, body = parse_transcript(video[4])
        try:
            row, why = build_row(video, extract(video, body), body)
        except (ValueError, TypeError, AttributeError, OSError, subprocess.SubprocessError):
            failures.append(video[0])
            continue  # temporary errors must not become permanent rejections
        if row:
            data["rows"].append(row)
            added += 1
        else:
            data["rejected"].append([video[0], video[1], why])
            rejected += 1
        known.add((video[0], video[1]))
    data["rows"] = [r for r in data["rows"] if r["published"] >= cutoff]  # nothing older than 5 days is kept
    cbp.save(data, store)
    if failures:
        raise RuntimeError("extraction incomplete for %d video(s); retry required" % len(failures))
    return added, len(data["rows"]), rejected


def main(argv=None, now=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--due", action="store_true")
    g.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    now = now or datetime.now(timezone.utc)
    window = None
    if a.due:
        window = is_due(now, read_stamp())
        if not window:
            print("cbp: not due")
            return 0
    try:
        added, total, rejected = run_once(now)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as e:
        print("cbp: FAILED (%s); window not marked complete" % type(e).__name__, file=sys.stderr)
        return 1
    write_stamp(now, window or open_window(now))
    end = now.astimezone(timezone.utc).date().isoformat()  # window = the 5 days up to today
    print("cbp: +%d rows, %d total, window end %s%s" % (added, total, end, ", %d rejected" % rejected if rejected else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
