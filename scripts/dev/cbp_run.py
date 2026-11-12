"""Run CBP once: fetch new analyst videos (last 5 days), extract, quote-check, store. No scheduler, no daemon.

    python scripts/dev/cbp_run.py --due     # only if a UTC window is open and not yet done in it
    python scripts/dev/cbp_run.py --force   # whenever the operator asks
    python scripts/dev/cbp_run.py --force --no-fetch   # YouTube locked: extract cached (browser-panel) transcripts only

Windows (UTC, OURS): EU 04:00-12:00, pre-US 12:00-midnight. Scheduled starts: 05:00 and 20:00 (Sat 05:30, Sun 16:30);
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
import time as _time
from datetime import datetime, time, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "MyTradingSys"))
import cbp  # noqa: E402
import verify_extract_quotes as vq  # noqa: E402
import fetch_captions_timed as fct  # noqa: E402
import yt_transcript_sites as sites  # noqa: E402


default_cbp_home = cbp.default_cbp_home


CBP_HOME = default_cbp_home()
TRANSCRIPTS = Path(os.environ.get("CBP_TRANSCRIPTS", str(CBP_HOME / "raw_transcripts_canonical")))
VERDICT_DAYS = 21  # a thesis analyst who posts every 2 weeks (Jala, Bob) must still have a latest vote
WINDOWS = (("EU", time(4, 0), time(12, 0)), ("PRE_US", time(12, 0), None))  # holds the 05:00, 05:30 and 20:00, 16:30 starts
# Pacing (OURS). Measured 2026-11-12 from the guard record: the lock of 2026-11-12T02:53Z (level 2, 24 h) followed one CBP run that
# sent 65 YouTube requests in one hour (listing + a date call + a caption call per video, ten analysts back to back, no pause
# between analysts). A normal run now stays under half of that.
ANALYST_PAUSE_S = 30      # pause between two analysts' fetches
MAX_VIDEOS_PER_ANALYST = 3   # --max-videos for each analyst's fetch (the fetcher's own default is 5)
HOURLY_REQUEST_CAP = 30   # stop starting analysts once this many YouTube requests went out in the last hour (any exit IP)
MODEL = os.environ.get("CBP_MODEL", "claude-sonnet-5-5")
PROMPT = """You extract what ONE crypto analyst says in ONE video.
Analyst: %(analyst)s. Published: %(published)s. Title: "%(title)s".
Output ONLY a JSON object, nothing else:
{"bias": "BULLISH|BEARISH|NEUTRAL|NO_VIEW", "symbols": ["BTC",...],
 "quotes": ["<=25 words, verbatim from the transcript"],
 "trades": [{"asset":"BTC","direction":"LONG|SHORT","entry":"...","target":"...","invalidation":"...","quote":"verbatim"}],
 "pointers": ["a level or condition the analyst names, short"],
 "bottom_call": "IN|NOT_IN|UNDECIDED|NO_VIEW", "bottom_conf": "HIGH|MED|LOW",
 "bottom_quote": "verbatim, <=30 words (\"\" if NO_VIEW)", "bottom_summary": "one sentence, your words",
 "alts": [{"coin":"SOL","stance":"BUY|HOLD|SELL|AVOID|WATCH","note":"short, your words","quote":"verbatim <=25 words"}],
 "alts_general": "one sentence on his view of altcoins as a group (\"\" if none)", "alts_general_quote": "verbatim or \"\""}
bottom_call is about the BTC cycle low: IN = he says it is in or very likely in; NOT_IN = he expects lower lows;
UNDECIDED = conditions either way, no commitment; NO_VIEW = not addressed. alts = every non-BTC coin he gives a view on
(BUY only if he says he is buying or it is a buy here).
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
    return cfg, [a for a in cfg["analysts"] if a.get("enabled")]  # 2026-10-31: all feeds (Bottom-is-In vote, alts)


def requests_last_hour(now=None):
    """YouTube requests recorded by the guard in the last 60 min, all IPs (no network)."""
    now = now or datetime.now(timezone.utc)
    n = 0
    req = fct.read_block().get("req")
    for stamps in (req.values() if isinstance(req, dict) else []):
        for v in stamps:
            try:
                t = datetime.fromisoformat(v)
            except (TypeError, ValueError):
                continue
            n += (now - (t if t.tzinfo else t.replace(tzinfo=timezone.utc))) < timedelta(hours=1)
    return n


def catch_up(an, cfg, cutoff, why, outdir=None):
    """Path 4 for one analyst the YouTube fetch did not finish: newest uploads listed and fetched through a public
    transcript site (no YouTube request); a video that still fails goes to the waiting list (never silently dropped).
    Returns the ids still waiting."""
    outdir = Path(outdir or TRANSCRIPTS)
    inc = re.compile(cfg["include_regex"]) if an.get("topic_filter") and cfg.get("include_regex") else None
    exc = re.compile(cfg["exclude_regex"]) if cfg.get("exclude_regex") else None
    waiting = []
    for i, (vid, title, d) in enumerate(sites.list_channel(an["channel"], 8)):
        if (d and d < cutoff) or (exc and exc.search(title)) or (inc and not inc.search(title)):
            continue
        if (outdir / (vid + "_timed.txt")).exists():
            continue
        if i:
            _time.sleep(sites.PAUSE_S)
        r = fct.recover(vid, an["short"], ["en"], outdir, an["channel"], [why])
        if r == "WAITING":
            waiting.append(vid)
    return waiting


def fetch_new(cutoff, store, run=subprocess.run, sleep=None, recent=None):
    """yt-dlp captions for each actionable analyst, newest first, stopping at `cutoff` (YYYY-MM-DD).
    Existing transcripts are skipped by fetch_captions_timed, so reruns download nothing new.
    Returns the analysts whose fetch exited nonzero; one of them never stops the others.
    Paced: a pause between analysts and a one-hour request cap; an analyst the cap skips, or whose fetch did not finish
    (exit 1, not the lock's exit 3 which the fetcher handles itself), goes through path 4 and then the waiting list."""
    sleep, recent = sleep or _time.sleep, recent or requests_last_hour
    cfg, ans = analysts()
    cookies = CBP_HOME / "cookies_utube_1.txt"
    incomplete = []
    for n, an in enumerate(ans):
        used = recent()
        if used >= HOURLY_REQUEST_CAP:
            print("cbp: %s not fetched from YouTube: %d requests in the last hour (cap %d); path 4" % (an["short"], used, HOURLY_REQUEST_CAP))
            catch_up(an, cfg, cutoff, "ytdlp:hourly-cap")
            incomplete.append(an["short"])
            continue
        if n:
            sleep(ANALYST_PAUSE_S)
        cmd = [sys.executable, str(HERE / "fetch_captions_timed.py"), "--analyst", an["short"],
               "--channel", an["channel"], "--latest", "6", "--scan", "8", "--since", cutoff,
               "--max-videos", str(MAX_VIDEOS_PER_ANALYST),
               "--out", str(TRANSCRIPTS), "--canonical-out", str(TRANSCRIPTS), "--exclude", cfg["exclude_regex"]]
        if an.get("topic_filter"):
            cmd += ["--include", cfg["include_regex"]]
        if cookies.exists():
            cmd += ["--cookies", str(cookies)]
        result = run(cmd, check=False)
        if result.returncode:  # DEFERRED (per-run --max-videos budget) or DATE_FAILED exits 1: keep going, retry next window
            print("cbp: fetch incomplete for %s (exit %s); window will be retried" % (an["short"], result.returncode))
            incomplete.append(an["short"])
            if result.returncode != fct.EXIT_BLOCKED:
                catch_up(an, cfg, cutoff, "ytdlp:exit%s" % result.returncode)
    return incomplete


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
    try:
        r.check_returncode()
    except subprocess.CalledProcessError as e:  # keep the cause (OAuth expired etc.): check_returncode drops stderr
        raise subprocess.CalledProcessError(e.returncode, e.cmd, r.stdout, r.stderr) from e
    m = re.search(r"\{.*\}", r.stdout or "", re.S)
    if not m:
        raise ValueError("no JSON from extractor: " + (r.stderr or r.stdout or "")[:120])
    return json.loads(m.group(0))


FAR_ENTRY_PCT = 5.0   # OURS (chosen, unchecked): entry further than this from the publish-day spot close is flagged


def _num(text):
    """First number in a trade-level string ('hold above 2,360', '74k'); None when none parses."""
    m = re.search(r"(\d[\d,]*(?:\.\d+)?)\s*([kK])?", str(text or ""))
    if not m:
        return None
    try:
        v = float(m.group(1).replace(",", ""))
    except ValueError:
        return None
    return v * 1000 if m.group(2) else v


def binance_spot(asset, date):
    """Binance public spot 1d close of ASSETUSDT on date (YYYY-MM-DD); None on any failure. No key."""
    try:
        import urllib.request
        t0 = int(datetime.fromisoformat(date).replace(tzinfo=timezone.utc).timestamp() * 1000)
        url = "https://api.binance.com/api/v3/klines?symbol=%sUSDT&interval=1d&startTime=%d&limit=1" % (asset.upper(), t0)
        with urllib.request.urlopen(url, timeout=10) as r:
            return float(json.loads(r.read())[0][4])
    except Exception:
        return None


def _flag_trades(row, spot, blank=True):
    """Mark impossible extractor output on row (in place): wrong-side stop, entry far from spot, bias vs trades.
    blank=True (a new row): the wrong-side stop is blanked. blank=False (--recheck of a stored row): nothing is deleted,
    the trade gets t["flag"] and cbp.is_tradable skips it."""
    flags = []
    for t in row["trades"]:
        entry, stop = _num(t["entry"]), _num(t["invalidation"])
        if entry is not None and stop is not None and (
                (t["direction"] == "LONG" and stop >= entry) or (t["direction"] == "SHORT" and stop <= entry)):
            if blank:
                t["invalidation"] = ""
            else:
                t["flag"] = "stop_wrong_side"
            flags.append("stop_wrong_side")
        if entry is not None and t["asset"].strip():
            px = spot(t["asset"].strip().upper(), row["published"])
            if px and abs(entry - px) / px * 100 > FAR_ENTRY_PCT:
                if not blank:
                    t["flag"] = (t["flag"] + "," if t.get("flag") else "") + "entry_far_from_spot"
                flags.append("entry_far_from_spot")
    dirs = {t["direction"] for t in row["trades"]}
    if (row["bias"] == "BEARISH" and "LONG" in dirs) or (row["bias"] == "BULLISH" and "SHORT" in dirs):
        flags.append("bias_contradicts_trades")
    if flags:
        row["flags"] = list(dict.fromkeys(flags))


def build_row(video, got, body, spot=binance_spot):
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
            return None, "quote not in transcript: " + bad.strip()[:400]
    row = {"analyst": analyst, "video_id": vid, "published": published,
           **({"channel": channel} if channel else {}),
           "bias": got.get("bias") if got.get("bias") in cbp.BIASES else "NO_VIEW",
           "symbols": [str(s).upper() for s in got.get("symbols") or []],
           "quotes": quotes,
           "trades": [{k: str(t.get(k) or "") for k in cbp.TRADE_FIELDS} for t in trades],
           "pointers": [str(p) for p in got.get("pointers") or []],
           "quote_verified": True,
           "expires_at": (datetime.fromisoformat(published) + timedelta(days=cbp.WINDOW_DAYS)).strftime("%Y-%m-%dT00:00:00Z")}
    _flag_trades(row, spot)
    errs = cbp.validate_row(row)
    return (None, "; ".join(errs)) if errs else (row, "")


def recheck(store=None, spot=binance_spot):
    """--recheck: the build_row checks on every STORED row (build_row only runs them on new rows). Bad trades are marked
    (t["flag"], row["flags"]), never deleted; the stored text stays. Returns [(analyst, video_id, flags)] of flagged rows."""
    data = cbp.load(store)
    out = []
    for r in data["rows"]:
        if not isinstance(r, dict) or not isinstance(r.get("trades"), list):
            continue
        for t in r["trades"]:
            t.pop("flag", None)
        r.pop("flags", None)
        _flag_trades(r, spot, blank=False)
        if r.get("flags"):
            out.append((r.get("analyst"), r.get("video_id"), r["flags"]))
    cbp.save(data, store)
    return out


NEW_TTL_MIN = 15   # OURS: a wake-time check reuses the last answer for this long (one cheap listing per analyst per 15 min)


def new_state_path():
    return stamp_path().with_name("newcheck.json")


def quick_new(now, store=None, lister=sites.list_channel, state=None):
    """--quick-new: newest uploads per analyst channel (public transcript-site listing: no YouTube request, no caption call,
    no guard spend) against the store, rejected list, cached transcripts and the waiting list. Returns [(analyst, video_id)] not known,
    published within the row window. Reuses the last answer for NEW_TTL_MIN minutes."""
    cutoff = (now - timedelta(days=cbp.WINDOW_DAYS)).date().isoformat()
    data = cbp.load(store)
    known = {r["video_id"] for r in data["rows"]} | {x[0] for x in data["rejected"]}
    known |= {v[0] for v in local_videos(cutoff)}
    state_path = Path(state) if state else new_state_path()
    try:
        st = json.loads(state_path.read_text(encoding="utf-8"))
        at = datetime.fromisoformat(st["at"])
        if now - at < timedelta(minutes=NEW_TTL_MIN):
            return [(a, v) for a, v in st["new"] if v not in known]
    except (OSError, ValueError, KeyError, TypeError):
        pass
    cfg, ans = analysts()
    exc = re.compile(cfg["exclude_regex"]) if cfg.get("exclude_regex") else None
    inc = re.compile(cfg["include_regex"]) if cfg.get("include_regex") else None
    new = []
    for an in ans:
        for vid, title, d in lister(an["channel"], 3):
            if (d and d < cutoff) or vid in known or (exc and exc.search(title)) or (an.get("topic_filter") and inc and not inc.search(title)):
                continue
            new.append((an["short"], vid))
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps({"at": now.isoformat(), "new": new}), encoding="utf-8", newline="\n")
    return new


def verdicts_path(store=None):
    return Path(store).with_name("verdicts.json") if store else cbp.default_cbp_home() / "cbp_store" / "verdicts.json"


def build_verdict(video, got, body):
    """Bottom call + alt views from the extractor object; each quote is checked, an unverified item is dropped."""
    norm_body = vq.norm(vq.TIMESTAMP.sub(" ", body))
    ok = lambda q: isinstance(q, str) and q.strip() != "" and vq.first_missing(q, norm_body) is None
    s = lambda v: str(v or "")
    alts = [{k: s(a.get(k)) for k in ("coin", "stance", "note", "quote")}
            for a in got.get("alts") or [] if isinstance(a, dict) and ok(a.get("quote"))]
    call = got.get("bottom_call") if got.get("bottom_call") in ("IN", "NOT_IN", "UNDECIDED", "NO_VIEW") else "NO_VIEW"
    gq = s(got.get("alts_general_quote"))
    return {"analyst": video[1], "published": video[2], "title": video[3],
            "bias": got.get("bias") if got.get("bias") in cbp.BIASES else "NO_VIEW",
            "bottom_call": call, "bottom_conf": s(got.get("bottom_conf")),
            "bottom_quote": s(got.get("bottom_quote")) if ok(got.get("bottom_quote")) else "",
            "bottom_summary": s(got.get("bottom_summary")), "alts": alts,
            "alts_general": s(got.get("alts_general")), "alts_general_quote": gq if ok(gq) else ""}


class FetchIncomplete(Exception):
    """Fetch was partial for some analysts; extraction of everything local still ran and was saved."""
    def __init__(self, analysts, result):
        super().__init__("fetch incomplete for: " + ", ".join(analysts))
        self.analysts, self.result = analysts, result


def _cause(vid, e):
    err = (getattr(e, "stderr", None) or "").strip() if not isinstance(e, ValueError) else ""
    return "%s: %s" % (vid, (err or str(e) or type(e).__name__)[:160])


def run_once(now, fetch=fetch_new, extract=llm_extract, store=None):
    """Fetch, extract new videos, write the store and verdicts. Returns (added, total, rejected).
    Rows (window 5 days) feed cbp.query; verdicts (bottom call + alt views, VERDICT_DAYS) feed the dashboard."""
    cutoff = (now - timedelta(days=cbp.WINDOW_DAYS)).date().isoformat()
    vcut = (now - timedelta(days=VERDICT_DAYS)).date().isoformat()
    data = cbp.load(store)
    vpath = verdicts_path(store)
    try:
        verdicts = json.loads(vpath.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        verdicts = {}
    known = {(r["video_id"], r["analyst"]) for r in data["rows"]} | {(x[0], x[1]) for x in data["rejected"]}
    incomplete = fetch(vcut, known)
    added = rejected = 0
    failures = []
    cause = []
    for video in local_videos(vcut):
        need_row = video[2] >= cutoff and (video[0], video[1]) not in known
        if not need_row and video[0] in verdicts:
            continue
        _, body = parse_transcript(video[4])
        try:
            got = extract(video, body)
            row, why = build_row(video, got, body) if need_row else (None, "")
            verdict = build_verdict(video, got, body)
        except (ValueError, TypeError, AttributeError, OSError, subprocess.SubprocessError) as e:
            failures.append(video[0])
            cause.append(_cause(video[0], e))
            continue  # temporary errors must not become permanent rejections
        verdicts[video[0]] = verdict
        if row:
            data["rows"].append(row)
            added += 1
        elif need_row:
            data["rejected"].append([video[0], video[1], why])
            rejected += 1
        known.add((video[0], video[1]))
    data["rows"] = [r for r in data["rows"] if r["published"] >= cutoff]  # nothing older than 5 days is kept
    cbp.save(data, store)
    verdicts = {k: v for k, v in verdicts.items() if v["published"] >= vcut}
    vpath.parent.mkdir(parents=True, exist_ok=True)
    vpath.write_text(json.dumps(verdicts, indent=1, ensure_ascii=False), encoding="utf-8", newline=chr(10))
    if failures:
        raise RuntimeError("extraction incomplete for %d video(s); retry required: %s" % (len(failures), "; ".join(cause[:3])))
    if incomplete:
        raise FetchIncomplete(incomplete, (added, len(data["rows"]), rejected))
    return added, len(data["rows"]), rejected


def rebuild_dashboard(run=subprocess.run):
    """Refresh market data, then rebuild the v5 CBP Analyst Desk board (cbp_v2/cbp_board.html).
    Each step is best effort: a failure here never fails the run, and the build runs on the last data.
    Returns the names of tools that failed (non-zero exit or exception) so the run log says which one."""
    tools = CBP_HOME / "cbp_v2" / "tools"
    failed = []
    for name in ("fetch_board_data.py", "build_board.py"):
        tool = tools / name
        if tool.is_file():
            try:
                res = run([sys.executable, str(tool)], check=False)
                rc = getattr(res, "returncode", 0)
                if isinstance(rc, int) and rc != 0:
                    print("cbp: %s exit %d; board built on stale data" % (name, rc))
                    failed.append(name)
            except Exception as e:  # noqa: BLE001
                print("cbp: " + name + " failed: " + str(e))
                failed.append(name)
    announce_republish()
    return failed


def announce_republish(out=print, ask=None, login=None, reg=None):
    """After a rebuild: print the REPUBLISH line for the CBP Analyst Desk, and when this run is on a login that cannot publish
    (registry publishers), ask the publisher login to do it (operator 2026-11-07: pages follow builds). Best effort; silent when
    no board was built."""
    try:
        board = CBP_HOME / "cbp_v2" / "cbp_board.html"
        if not board.is_file() or board.stat().st_size == 0:
            return
        import artifacts
        import mts_signal
        reg = reg or artifacts.load()
        pg = next(p for p in reg["pages"] if p["slug"] == "cbp_analyst_desk")
        line = "REPUBLISH cbp_analyst_desk %s %s" % (board, pg["urls"][artifacts.owner(pg)])
        out(line)
        letter = login if login is not None else mts_signal.login()
        if not artifacts.is_publisher(reg, letter):
            text = ("CBP board rebuilt; a session on the publisher login (jishusharma1985) republishes it: "
                    "artifacts.py stamp --file <board>, Artifact publish over the url, artifacts.py publish-record --slug cbp_analyst_desk. " + line)
            (ask or mts_signal.new_ask)(text)
    except Exception as e:  # noqa: BLE001
        print("cbp: republish note failed: " + str(e))


def main(argv=None, now=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--due", action="store_true")
    g.add_argument("--force", action="store_true")
    g.add_argument("--recheck", action="store_true", help="apply the build_row checks to every stored row, mark bad trades, rebuild the board")
    g.add_argument("--new-check", action="store_true", help="print CBP NEW <analyst> <video_id> for uploads not in the store (no captions, no YouTube request)")
    ap.add_argument("--quick-new", action="store_true",
                    help="with --due: also run the new-upload check; a new video fetches even when the window is already done (stamp untouched)")
    ap.add_argument("--no-fetch", action="store_true",
                    help="skip the caption fetch; extract only transcripts already cached (browser-panel path, YT_PROXY.md); stamp withheld")
    a = ap.parse_args(argv)
    now = now or datetime.now(timezone.utc)
    window = None
    if a.recheck:
        flagged = recheck()
        for an, vid, fl in flagged:
            print("CBP FLAGGED %s %s %s" % (an, vid, ",".join(fl)))
        rebuild_dashboard()
        print("cbp: recheck, %d row(s) flagged" % len(flagged))
        return 0
    if a.new_check or a.quick_new:
        try:
            new = quick_new(now)
        except (OSError, ValueError, KeyError) as e:
            print("cbp: new-upload check failed (%s)" % type(e).__name__)
            new = []
        for an, vid in new:
            print("CBP NEW %s %s" % (an, vid))
        if a.new_check:
            return 0
    else:
        new = []
    if a.due:
        window = is_due(now, read_stamp())
        if not window and not new:
            print("cbp: not due")
            return 0
    partial = []
    try:
        try:
            added, total, rejected = run_once(now, fetch=lambda c, k: []) if a.no_fetch else run_once(now)
        except FetchIncomplete as e:  # rows and verdicts are saved; only the stamp is withheld
            (added, total, rejected), partial = e.result, e.analysts
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as e:
        print("cbp: FAILED (%s); window not marked complete" % type(e).__name__, file=sys.stderr)
        return 1
    if not partial and not a.no_fetch and (window or not a.due):  # a no-fetch run has not covered the window: the normal run still owes the fetch
        write_stamp(now, window or open_window(now))
    rebuild_dashboard()
    end = now.astimezone(timezone.utc).date().isoformat()  # window = the 5 days up to today
    print("cbp: +%d rows, %d total, window end %s%s" % (added, total, end, ", %d rejected" % rejected if rejected else ""))
    if partial:
        print("cbp: window not marked complete, fetch incomplete for: " + ", ".join(partial))
    waiting = sites.pending(TRANSCRIPTS)
    if waiting:
        print("cbp: %d video(s) on the waiting list (no scripted path got them; Claude desktop path withdrawn: no Chrome until the operator names a device, "
              "YT_PROXY.md path 3): python scripts/dev/fetch_captions_timed.py --waiting" % len(waiting))
    return 0


if __name__ == "__main__":
    sys.exit(main())
