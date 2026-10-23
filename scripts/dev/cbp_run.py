"""Run CBP once: fetch new analyst videos (last 5 days), extract, quote-check, store. No scheduler, no daemon.

    python scripts/dev/cbp_run.py --due     # only if a UTC window is open and not yet done in it
    python scripts/dev/cbp_run.py --force   # whenever the operator asks

Windows (UTC, OURS): EU 09:00-11:00, pre-US 12:00-13:30. The coordinator calls --due on each wake;
the stamp file lives outside the repo (CBP_STAMP, default ~/.mts_cbp_stamp.json).
Only the actionable analysts in F:/CryptoScrapper/cbp_v2/analysts.json are fetched; videos already in the store
(or already rejected) are skipped; nothing older than 5 days is fetched. One LLM pass per new video.
Output: one line "cbp: +<added> rows, <total> total, window end <date>[, <n> rejected]".
Rows are read by MyTradingSys/cbp (cbp.query). Data stays in F:/CryptoScrapper (CBP_STORE, CBP_HOME).
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

CBP_HOME = Path(os.environ.get("CBP_HOME", "F:/CryptoScrapper"))
TRANSCRIPTS = CBP_HOME / "transcripts"
WINDOWS = (("EU", time(9, 0), time(11, 0)), ("PRE_US", time(12, 0), time(13, 30)))
MODEL = os.environ.get("CBP_MODEL", "claude-sonnet-5-5")
PROMPT = """You extract what ONE crypto analyst says in ONE video. Output ONLY a JSON object, nothing else:
{"bias": "BULLISH|BEARISH|NEUTRAL|NO_VIEW", "symbols": ["BTC",...],
 "quotes": ["<=25 words, verbatim from the transcript"],
 "trades": [{"asset":"BTC","direction":"LONG|SHORT","entry":"...","target":"...","invalidation":"...","quote":"verbatim"}],
 "pointers": ["a level or condition the analyst names, short"]}
Rules: only what the analyst says, no inference, no filling gaps. A trade needs entry, target and invalidation in
their words (use "" for any not stated). Every quote and trade.quote must be copied verbatim from the transcript
(auto-captions: copy the caption words as they are). bias is the analyst's own stance on BTC.
Transcript of %(analyst)s, %(published)s, "%(title)s":
"""


def stamp_path():
    return Path(os.environ.get("CBP_STAMP") or Path.home() / ".mts_cbp_stamp.json")


def open_window(now):
    """Name of the UTC window that is open at `now`, else None."""
    t = now.astimezone(timezone.utc).time()
    for name, a, b in WINDOWS:
        if a <= t < b:
            return name
    return None


def is_due(now, stamp):
    """Window name when one is open and the stamp has no run in it today, else None."""
    w = open_window(now)
    day = now.astimezone(timezone.utc).date().isoformat()
    return w if w and day + ":" + w not in stamp.get("done", []) else None


def read_stamp():
    try:
        return json.loads(stamp_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def write_stamp(now, window):
    """Keep only the last 4 entries; the stamp is a bookmark, not a log."""
    s = read_stamp()
    day = now.astimezone(timezone.utc).date().isoformat()
    done = (s.get("done", []) + [day + ":" + window])[-4:] if window else s.get("done", [])
    stamp_path().write_text(json.dumps({"done": done, "last_run": now.isoformat()}), encoding="utf-8", newline="\n")


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
               "--out", str(TRANSCRIPTS), "--exclude", cfg["exclude_regex"]]
        if an.get("topic_filter"):
            cmd += ["--include", cfg["include_regex"]]
        if cookies.exists():
            cmd += ["--cookies", str(cookies)]
        run(cmd, check=False)


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
    """[(video_id, analyst, published, title, path)] of transcripts on disk published on/after cutoff."""
    out = []
    for p in sorted(TRANSCRIPTS.glob("*_timed.txt")):
        meta, _ = parse_transcript(p)
        if meta.get("published", "") >= cutoff and meta.get("analyst"):
            out.append((meta["video id"], meta["analyst"], meta["published"], meta.get("title", ""), p))
    return out


def llm_extract(video, body, run=subprocess.run):
    """One `claude -p` pass per video; returns the parsed JSON object or raises ValueError."""
    vid, analyst, published, title, _ = video
    prompt = PROMPT % {"analyst": analyst, "published": published, "title": title.replace('"', "'")}
    r = run(["claude", "-p", "--model", MODEL, "--tools", "", "--no-session-persistence"],
            input=prompt + body, capture_output=True, text=True, encoding="utf-8", timeout=600)
    m = re.search(r"\{.*\}", r.stdout or "", re.S)
    if not m:
        raise ValueError("no JSON from extractor: " + (r.stderr or r.stdout or "")[:120])
    return json.loads(m.group(0))


def build_row(video, got, body):
    """Row from the extractor's object, or (None, reason). Every quote must occur in the transcript, checked with
    verify_extract_quotes (the one checker); one fabricated quote rejects the whole row."""
    vid, analyst, published, _, _ = video
    norm_body = vq.norm(vq.TIMESTAMP.sub(" ", body))
    quotes = [q for q in got.get("quotes") or [] if isinstance(q, str) and q.strip()]
    trades = [t for t in got.get("trades") or [] if isinstance(t, dict)]
    for q in quotes + [str(t.get("quote") or "") for t in trades]:
        bad = vq.first_missing(q, norm_body) if q.strip() else "empty quote"
        if bad is not None:
            return None, "quote not in transcript: " + bad.strip()[:60]
    row = {"analyst": analyst, "video_id": vid, "published": published,
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
    for video in local_videos(cutoff):
        if (video[0], video[1]) in known:
            continue
        _, body = parse_transcript(video[4])
        try:
            row, why = build_row(video, extract(video, body), body)
        except (ValueError, OSError, subprocess.SubprocessError) as e:
            row, why = None, "extract failed: %s" % str(e)[:100]
            if isinstance(e, (OSError, subprocess.SubprocessError)):
                continue  # extractor unavailable: retry next run, do not mark rejected
        if row:
            data["rows"].append(row)
            added += 1
        else:
            data["rejected"].append([video[0], video[1], why])
            rejected += 1
        known.add((video[0], video[1]))
    data["rows"] = [r for r in data["rows"] if r["published"] >= cutoff]  # nothing older than 5 days is kept
    cbp.save(data, store)
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
    added, total, rejected = run_once(now)
    write_stamp(now, window or open_window(now))
    end = now.astimezone(timezone.utc).date().isoformat()  # window = the 5 days up to today
    print("cbp: +%d rows, %d total, window end %s%s" % (added, total, end, ", %d rejected" % rejected if rejected else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
