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
The record also stores the public IP it was written from (one api.ipify.org request at write time); when a record is
still live the guard makes one more ipify request and ignores a record written from a different IP, so a VPN exit
(scripts/dev/yt_vpn_fetch.py) is not treated as blocked by the home IP's record, while a 429 on the new IP writes a record
for that IP (the home IP's entry is kept in `by_ip`). A record without an IP, or an unreadable current IP, stands.
Fleet guard (2026-11-01; one public IP is shared by several machines, so a per-machine record is not enough):
 - a 429 is also sent as a `ytblock` signal on the mts-signals branch (mts_signal.py channel), keyed by a short hash of the
   public IP (8 hex chars, never the address: the repo is public); every machine reads it before its next request. Remote
   state unreadable and no local record: old behaviour plus a printed warning.
 - rolling 24 h request budget per public IP (YT_DAILY_BUDGET, default 40, OURS): EVERY network call counts (caption fetch,
   metadata, channel listing, transcript-api); over budget = DEFERRED, no request. Other machines' use arrives as `ytuse` signals.
 - escalating lockout on consecutive blocks 6 h, 24 h, 72 h (OURS); a clean fetch resets the count (`ytclean` signal).
 - a yt-dlp 429 ends the video there: the transcript-api fallback (plus its metadata call) is OFF unless --fallback, and then
   each of its calls is counted against the budget.
Never blocked (operator 2026-11-12, YT_PROXY.md path order): a locked address, a 429 or an unfetched id goes on by itself to
path 4, a public Invidious instance (yt_transcript_sites.py: video id only, no account/cookies, generic User-Agent, never a
YouTube request from this address, paced). It writes the same _timed/_raw files, `# Source: public transcript site <host>`. A
video no scripted path could get is appended to ~/.mts/yt_waiting.json (env YT_WAITING_FILE); `--waiting` prints that list
for a Claude desktop session to drain through the Browser 2 panel path. The guard's lockout itself is unchanged.
YouTube-only proxy (operator 2026-11-02, home IP blocked): when env YT_PROXY is set (a socks5:// or http:// URL; "off" =
none) or ~/.mts/ytproxy/wireproxy.conf exists (free Cloudflare WARP via the open-source wgcf + wireproxy, setup in
MyTradingSys/system/YT_PROXY.md), EVERY YouTube call and the ipify check go through socks5://127.0.0.1:40000; nothing
else on the machine changes. wireproxy is started for the run when the port is closed and stopped after. Proxy set but not
reachable = exit 2 with no request (fail closed: never falls back to the home IP). The guard above applies per exit IP.
"""
import argparse
import hashlib
import json
import os
import socket
import subprocess
import re
import sys
import tempfile
import time
import ipaddress
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import yt_dlp
except ImportError:   # CI pip line lacks it; the fetcher is a desktop tool, tests inject a stub
    yt_dlp = None

sys.path.insert(0, str(Path(__file__).resolve().parent))
import yt_transcript_sites as sites  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CBP_HOME = Path(os.environ["CBP_HOME"]) if os.environ.get("CBP_HOME") else None
CANON = CBP_HOME / "raw_transcripts_canonical" if CBP_HOME else ROOT / "raw_transcripts_canonical"
ID_RE = re.compile(r"(?:v=|youtu\.be/|^)([A-Za-z0-9_-]{11})(?:[&?#]|$)")
TS_RE = re.compile(r"(\d+):(\d+):(\d+)[.,](\d+)\s+-->")
BLOCK_HOURS = 6
BLOCK_LEVELS_H = (6, 24, 72)   # OURS: lockout hours on the 1st, 2nd, 3rd+ consecutive block
BUDGET_WINDOW_H = 24
DAILY_BUDGET = 40              # OURS: YouTube requests per public IP per rolling 24 h (env YT_DAILY_BUDGET)
DAILY_BUDGET_PROXY = 150       # OURS: same, on the shared WARP exit (one CBP run ~35 requests, 2 runs a day)
ALLOW_FALLBACK = False         # transcript-api fallback after a 429 is a second network path: off by default
BLOCK_MARKS = ("429", "Too Many Requests", "Sign in to confirm")
EXIT_BLOCKED = 3
NEXT_PATH = "next path: Browser 2 transcript panel, see YT_PROXY.md"   # message only: a block never ends a YouTube task
EXIT_PROXY_DOWN = 2
PROXY_ADDR = ("127.0.0.1", 40000)   # OURS: wireproxy BindAddress in ~/.mts/ytproxy/wireproxy.conf
_proxy_proc = []


class YTBlocked(Exception):
    """A live block (local or fleet) is in force: no request may be made."""


class BudgetExceeded(Exception):
    """The rolling 24 h request budget of this public IP is used up."""


def daily_budget():
    try:
        return int(os.environ.get("YT_DAILY_BUDGET") or (DAILY_BUDGET_PROXY if proxy_url() else DAILY_BUDGET))
    except ValueError:
        return DAILY_BUDGET


def ip_hash(ip):
    """8 hex chars of sha256(ip): pseudonymous key for the public signals branch (the address itself never travels)."""
    return hashlib.sha256(("mts-yt:" + str(ip)).encode("ascii", "replace")).hexdigest()[:8] if ip else ""


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


def proxy_dir():
    return Path(os.environ.get("YT_PROXY_DIR") or Path.home() / ".mts" / "ytproxy")


def proxy_url():
    """The URL all YouTube traffic goes through, or None (direct). Env YT_PROXY wins ("off" = direct); else a
    wireproxy.conf in proxy_dir() means the local WARP SOCKS port."""
    env = (os.environ.get("YT_PROXY") or "").strip()
    if env:
        return None if env.lower() == "off" else env
    if (proxy_dir() / "wireproxy.conf").exists():
        return "socks5://%s:%d" % PROXY_ADDR
    return None


def _port_open(addr, timeout=1.0):
    try:
        with socket.create_connection(addr, timeout=timeout):
            return True
    except OSError:
        return False


def ensure_proxy(wait=20):
    """True when no proxy is configured or its port answers; starts wireproxy from proxy_dir() for this run if needed."""
    url = proxy_url()
    if not url:
        return True
    hostport = url.split("://", 1)[-1].rsplit("@", 1)[-1].rstrip("/")
    host, _, port = hostport.rpartition(":")
    addr = (host or "127.0.0.1", int(port or 1080))
    if _port_open(addr):
        return True
    d = proxy_dir()
    exe = d / ("wireproxy.exe" if os.name == "nt" else "wireproxy")
    if addr != PROXY_ADDR or not exe.exists() or not (d / "wireproxy.conf").exists():
        return False
    flags = 0x08000000 if os.name == "nt" else 0   # CREATE_NO_WINDOW
    with open(d / "wireproxy.log", "ab") as log:   # the child keeps its own handle
        _proxy_proc.append(subprocess.Popen([str(exe), "-c", str(d / "wireproxy.conf")], cwd=str(d), stdout=log,
                                            stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, creationflags=flags))
    end = time.monotonic() + wait
    while time.monotonic() < end:
        if _port_open(addr):
            return True
        if _proxy_proc[-1].poll() is not None:
            break
        time.sleep(0.5)
    return False


def stop_proxy():
    while _proxy_proc:
        pr = _proxy_proc.pop()
        if pr.poll() is None:
            pr.terminate()
            try:
                pr.wait(timeout=10)
            except subprocess.TimeoutExpired:
                pr.kill()


def ydl_opts(opts):
    """yt-dlp options with the YouTube proxy added when one is configured."""
    url = proxy_url()
    if url:
        opts["proxy"] = url
    return opts


def public_ip():
    """Current public IP via one tiny api.ipify.org request (through the YouTube proxy when set, so the guard keys on
    the exit IP), or None when it cannot be read (tests patch this)."""
    try:
        if proxy_url():
            with yt_dlp.YoutubeDL(ydl_opts({"quiet": True})) as y:
                raw = y.urlopen("https://api.ipify.org").read()
        else:
            with urllib.request.urlopen("https://api.ipify.org", timeout=8) as r:
                raw = r.read()
        return str(ipaddress.ip_address(raw.decode("ascii").strip()))
    except Exception:
        return None


def _future(iso):
    try:
        t = datetime.fromisoformat(iso or "")
    except (ValueError, TypeError):
        return None
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    return t if t > _utcnow() else None


def blocked_until(check_ip=True):
    """Local record or fleet signal, whichever ends later (see _local_blocked_until). The fleet is read only when check_ip."""
    local = _local_blocked_until(check_ip)
    if not check_ip:
        return local
    rows = fleet_rows()
    if rows is None:
        if not read_block().get("blocked_until") and not _warned:
            _warned.append("x")
            print("YT_GUARD WARNING: fleet block state unreadable and no local record: using this machine's record only.")
        return local
    if not any(r.get("kind") == "ytblock" and _future(r.get("until")) for r in rows):
        return local
    ip = public_ip()
    remote = fleet_block(rows, ip_hash(ip) if ip else "")
    return max([t for t in (local, remote) if t], default=None)


def _local_blocked_until(check_ip=True):
    """datetime the block ends, or None when not blocked (record missing, unreadable, expired, or written from a
    different public IP than the current one). The ipify request is made only when a live record exists."""
    rec = read_block()
    top = _future(rec.get("blocked_until"))
    by_ip = rec.get("by_ip") if isinstance(rec.get("by_ip"), dict) else {}
    if not (top or any(_future(v) for v in by_ip.values())):
        return None
    if not check_ip or not rec.get("ip"):
        return top   # legacy record (no IP) or offline status view: stands
    cur = public_ip()
    if cur is None or cur == rec["ip"]:
        return top   # cannot tell: fail closed
    return _future(by_ip.get(cur))


_warned = []
_last_rows = []
_unflushed = [0, ""]   # requests made by this process not yet announced, and their ip hash


def _sig():
    if os.environ.get("MTS_SIGNALS", "").lower() == "off" or os.environ.get("YT_FLEET", "").lower() == "off":
        return None
    if os.environ.get("PYTEST_CURRENT_TEST") and os.environ.get("YT_FLEET", "").lower() != "on":
        return None   # a test must never post to the real signals branch (it did once, 2026-11-01)
    try:
        import mts_signal
        return mts_signal
    except Exception:
        return None


def _host():
    s = _sig()
    return s.host() if s else socket.gethostname().lower()


def fleet_rows(fetch=True):
    """yt* signals from the mts-signals branch (the channel mts_signal.py uses), or None when unreadable.
    fetch=False reads the local clone only (no network; used by --status)."""
    s = _sig()
    if s is None:
        return None
    try:
        h = s.ensure() if fetch else (s.home() if (s.home() / ".git").exists() else None)
        if h is None:
            return None
        return [r for r in s.load(h) if str(r.get("kind", "")).startswith("yt")]
    except Exception:
        return None


def fleet_send(kind, text, **extra):
    s = _sig()
    if s is None:
        return False
    try:
        return bool(s.send(text, to="all", kind=kind, extra=dict(extra, host=_host())))
    except Exception:
        return False


def _rt(r):
    try:
        return datetime.strptime(r["t"], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except (KeyError, ValueError):
        return None


def fleet_block(rows, ih):
    """Latest end of a live fleet block for this IP hash (None: none). A newer ytclean for the same IP voids older blocks.
    ih "" (own IP unknown): any live block counts (fail closed)."""
    best, clean_t = None, None
    for r in rows or []:
        if ih and r.get("ih") != ih:
            continue
        t = _rt(r)
        if r.get("kind") == "ytclean" and t and (clean_t is None or t > clean_t):
            clean_t = t
    for r in rows or []:
        if r.get("kind") != "ytblock" or (ih and r.get("ih") != ih):
            continue
        t, u = _rt(r), _future(r.get("until"))
        if u and not (clean_t and t and t <= clean_t) and (best is None or u > best):
            best = u
    return best


def current_level(rows, ih, rec=None):
    """Consecutive-block count now: the newest of the local record and the fleet's ytblock/ytclean rows for this IP."""
    rec = read_block() if rec is None else rec
    ev = []
    lt = None
    try:
        lt = datetime.fromisoformat(rec.get("level_t") or "")
        lt = lt if lt.tzinfo else lt.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        pass
    if lt:
        ev.append((lt, int(rec.get("level") or 0)))
    for r in rows or []:
        if r.get("kind") in ("ytblock", "ytclean") and (not ih or r.get("ih") == ih) and _rt(r):
            ev.append((_rt(r), int(r.get("level") or 0) if r.get("kind") == "ytblock" else 0))
    return max(ev, key=lambda e: e[0])[1] if ev else 0


def _stamps(rec, ih):
    cutoff = _utcnow() - timedelta(hours=BUDGET_WINDOW_H)
    out = []
    req = rec.get("req") if isinstance(rec.get("req"), dict) else {}
    for v in req.get(ih, []):
        try:
            t = datetime.fromisoformat(v)
            t = t if t.tzinfo else t.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue
        if t > cutoff:
            out.append(t.isoformat(timespec="seconds"))
    return out


def budget_used(rows, ih, rec=None):
    """Requests of the last 24 h from this IP: this machine's record plus other machines' ytuse signals."""
    rec = read_block() if rec is None else rec
    cutoff = _utcnow() - timedelta(hours=BUDGET_WINDOW_H)
    used = len(_stamps(rec, ih))
    for r in rows or []:
        t = _rt(r)
        if r.get("kind") == "ytuse" and r.get("ih") == ih and r.get("host") != _host() and t and t > cutoff:
            try:
                used += int(r.get("n") or 0)
            except (TypeError, ValueError):
                pass
    return used


def spend(what="request"):
    """Call immediately before ANY YouTube network request (fetch, metadata, listing, fallback). Raises YTBlocked or
    BudgetExceeded without making the request; otherwise counts it against the rolling 24 h budget."""
    global _last_rows
    until = blocked_until()
    if until:
        raise YTBlocked(until.isoformat(timespec="seconds"))
    ip = public_ip()
    ih = ip_hash(ip) if ip else "unknown"
    rows = fleet_rows()
    _last_rows = rows or []
    if budget_used(rows, ih) >= daily_budget():
        raise BudgetExceeded(f"{what}: {daily_budget()} requests per 24 h used for this IP")
    rec = read_block()
    req = rec.get("req") if isinstance(rec.get("req"), dict) else {}
    req = {k: _stamps(rec, k) for k in req if k != ih and _stamps(rec, k)}
    req[ih] = _stamps(rec, ih) + [_utcnow().isoformat(timespec="seconds")]
    write_block(req=req)
    _unflushed[0] += 1
    _unflushed[1] = ih


def flush_fleet():
    """Announce this process's request count to the other machines (one ytuse signal)."""
    n, ih = _unflushed
    if n:
        _unflushed[0] = 0
        fleet_send("ytuse", f"yt-guard used {n} requests", ih=ih, n=n)


def mark_clean():
    """A clean fetch: the consecutive-block count goes back to 0 (and the fleet is told)."""
    ip = public_ip()
    ih = ip_hash(ip) if ip else ""
    if current_level(_last_rows, ih) > 0:
        write_block(level=0, level_t=_utcnow().isoformat(timespec="seconds"))
        fleet_send("ytclean", "yt-guard clean fetch, lockout level reset", ih=ih)


def mark_blocked():
    ip = public_ip()
    ih = ip_hash(ip)
    rows = fleet_rows()
    level = min(current_level(rows, ih) + 1, len(BLOCK_LEVELS_H))
    until = _utcnow() + timedelta(hours=BLOCK_LEVELS_H[level - 1])
    stamp = until.isoformat(timespec="seconds")
    rec = read_block()
    by_ip = {k: v for k, v in (rec.get("by_ip") or {}).items() if _future(v)} if isinstance(rec.get("by_ip"), dict) else {}
    if rec.get("ip") and _future(rec.get("blocked_until")):
        by_ip.setdefault(rec["ip"], rec["blocked_until"])   # keep the previous IP's block
    if ip:
        by_ip[ip] = stamp
    write_block(blocked_until=stamp, host=socket.gethostname(), ip=ip, ih=ih, by_ip=by_ip, level=level,
                level_t=_utcnow().isoformat(timespec="seconds"))
    fleet_send("ytblock", f"yt-guard 429: IP locked level {level} until {stamp}", ih=ih, until=stamp, level=level)
    return until


def guard_status():
    until, rec = blocked_until(check_ip=False), read_block()   # --status makes no network call
    ih = rec.get("ih") or ip_hash(rec.get("ip"))
    rows = fleet_rows(fetch=False) or []
    fb = fleet_block(rows, ih) if ih else None
    until = max([t for t in (until, fb) if t], default=None)
    head = (f"BLOCKED until {until.isoformat(timespec='seconds')} (host {rec.get('host', '?')}, "
            f"ip {rec.get('ip') or '?'})" if until
            else "NOT BLOCKED")
    lvl = current_level(rows, ih, rec)
    used = budget_used(rows, ih, rec) if ih else 0
    return (head + f"; lockout level {lvl} of {len(BLOCK_LEVELS_H)} ({'/'.join(map(str, BLOCK_LEVELS_H))} h, OURS)"
            + f"; budget used {used} of {daily_budget()} in 24 h (OURS, ip {ih or '?'}); "
            f"last run budget used {rec.get('last_used', 0)} of {rec.get('last_max', '?')}")


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
            elif r == "UNVERIFIED":   # a live block appeared (another machine's 429): stop, no new record
                stopped = True
            elif r.startswith("OK"):
                mark_clean()
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
        print(NEXT_PATH)
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
    spend("channel listing")
    opts = {"quiet": True, "no_warnings": True, "extract_flat": True, "playlistend": scan}
    if cookies:
        opts["cookiefile"] = cookies
    with yt_dlp.YoutubeDL(ydl_opts(opts)) as y:
        info = y.extract_info(f"https://www.youtube.com/{handle}/videos", download=False)
    return [(e["id"], e.get("title") or "") for e in (info.get("entries") or []) if e and e.get("id")][:scan]


def video_date(vid, cookies=None):
    """Upload date YYYY-MM-DD of one video (metadata only, no captions); "" when unknown."""
    spend("metadata")
    opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    if cookies:
        opts["cookiefile"] = cookies
    try:
        with yt_dlp.YoutubeDL(ydl_opts(opts)) as y:
            d = y.extract_info(f"https://www.youtube.com/watch?v={vid}", download=False).get("upload_date") or ""
    except yt_dlp.utils.DownloadError:
        return ""
    return f"{d[:4]}-{d[4:6]}-{d[6:]}" if len(d) == 8 else ""


def transcript_api_cues(vid, langs):
    """([(start_s, text)], "auto"|"manual") from youtube-transcript-api, or None (not installed, no captions, blocked)."""
    spend("transcript-api")
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        if proxy_url():   # never the home IP while a proxy is configured
            from youtube_transcript_api.proxies import GenericProxyConfig
            api = YouTubeTranscriptApi(proxy_config=GenericProxyConfig(http_url=proxy_url(), https_url=proxy_url()))
        t = api.fetch(vid, languages=list(langs))
        cues = [(int(s.start), " ".join(s.text.split())) for s in t.snippets if s.text.strip()]
    except Exception:   # library errors are many classes; any failure means "no fallback"
        return None
    return (cues, "auto" if t.is_generated else "manual") if cues else None


def meta(vid, cookies=None):
    """Title/date/uploader/duration of one video (metadata only); {} when YouTube refuses."""
    spend("metadata")
    opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    if cookies:
        opts["cookiefile"] = cookies
    try:
        with yt_dlp.YoutubeDL(ydl_opts(opts)) as y:
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
        spend("caption fetch")
    except YTBlocked:
        return "UNVERIFIED"
    except BudgetExceeded:
        return "DEFERRED"
    try:
        with tempfile.TemporaryDirectory() as td:
            opts = {"skip_download": True, "quiet": True, "no_warnings": True, "writesubtitles": True,
                    "writeautomaticsub": True, "subtitleslangs": langs, "subtitlesformat": "vtt",
                    "outtmpl": str(Path(td) / "%(id)s")}
            if cookies:
                opts["cookiefile"] = cookies
            with yt_dlp.YoutubeDL(ydl_opts(opts)) as y:
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
            if ALLOW_FALLBACK:   # opt-in second network path; every call below is counted against the budget
                try:
                    got = transcript_api_cues(vid, langs)
                    if got:
                        return store(vid, analyst, outdir, channel, meta(vid, cookies), got[1], got[0],
                                     "youtube_transcript_api")
                except (YTBlocked, BudgetExceeded):
                    pass
            return "BLOCKED"   # ONE try per video; the guard records the block and stops the run
        return f"ERROR {msg[:80]}"


def site_fetch(vid, analyst, langs, outdir, channel=""):
    """Path 4: captions of one video from a public transcript site (no YouTube request from this address)."""
    if (outdir / f"{vid}_timed.txt").exists():
        return "EXISTS"
    got = sites.fetch_video(vid, langs)
    if not got:
        return "NOSITE"
    return store(vid, analyst, outdir, channel, got["info"], "site", got["cues"], "public transcript site " + got["host"])


def recover(vid, analyst, langs, outdir, channel, tried):
    """A video the YouTube path could not give: try path 4, else the waiting list. Returns OK.../WAITING."""
    r = site_fetch(vid, analyst, langs, outdir, channel)
    if r.startswith(("OK", "EXISTS")):
        sites.drop_waiting(vid)
        return r
    sites.add_waiting(vid, channel, list(tried) + ["site:" + r])
    return "WAITING"


def locked_run(a, outdir):
    """Address locked: no YouTube request at all; ids (or the channel's newest uploads, listed by a site) go by path 4."""
    print(NEXT_PATH + " (trying path 4 first)", flush=True)
    langs = a.langs.split(",")
    if a.channel:
        rows = sites.list_channel(a.channel, a.scan)
        if not rows:
            print(f"{a.channel} LIST_FAILED (locked, site listing gave nothing)")
            return EXIT_BLOCKED
        inc, exc = re.compile(a.include) if a.include else None, re.compile(a.exclude) if a.exclude else None
        picks = [vid for vid, title, d in rows if not (exc and exc.search(title)) and not (inc and not inc.search(title))
                 and not (a.since and d and d < a.since)][:a.latest]
    else:
        picks = [m.group(1) for m in (ID_RE.search(v.strip()) for v in a.videos) if m]
    bad = 0
    for i, vid in enumerate(picks[:sites.SITE_VIDEOS_PER_RUN]):
        if i:
            time.sleep(sites.PAUSE_S)
        r = recover(vid, a.analyst, langs, outdir, a.channel or "", ["ytdlp:locked"])
        bad += not r.startswith(("OK", "EXISTS"))
        print(f"{vid} {r}", flush=True)
    if bad:
        print("WAITING videos listed: python scripts/dev/fetch_captions_timed.py --waiting")
    return EXIT_BLOCKED if bad else 0


def fetch_channel(a):
    try:
        rows = list_channel(a.channel, a.scan, a.cookies)
    except YTBlocked as e:
        print(f"{a.channel} UNVERIFIED (blocked until {e}): no request made")
        return 1
    except BudgetExceeded as e:
        print(f"{a.channel} DEFERRED ({e}): no request made")
        return 1
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
            try:
                published = video_date(vid, a.cookies)
            except (YTBlocked, BudgetExceeded):
                print(f"{vid} DEFERRED", flush=True)
                failed = True
                break
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
            elif r == "UNVERIFIED":
                stopped = True
            elif r.startswith("OK"):
                mark_clean()
        if r in ("BLOCKED", "UNVERIFIED"):   # path 4 by itself, never another YouTube request
            time.sleep(sites.PAUSE_S)
            r = recover(vid, a.analyst, a.langs.split(","), outdir, a.channel, ["ytdlp:" + r.lower()])
        picked += r.startswith(("OK", "EXISTS"))
        failed |= not r.startswith(("OK", "EXISTS"))
        print(f"{vid} {r}", flush=True)
    write_block(last_used=used, last_max=a.max_videos, last_run=_utcnow().isoformat(timespec="seconds"))
    print(f"{a.channel}: {picked} of {a.latest}")
    return 1 if failed else 0


def main(argv):
    try:
        return _main(argv)
    finally:
        try:
            flush_fleet()
        finally:
            stop_proxy()


def _main(argv):
    global CANON, ALLOW_FALLBACK
    ap = argparse.ArgumentParser()
    ap.add_argument("--analyst", default="")
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
    ap.add_argument("--status", action="store_true", help="print lockout level/until + 24 h budget used; no network")
    ap.add_argument("--fallback", action="store_true", help="after a yt-dlp 429 also try transcript-api (counted; off by default)")
    ap.add_argument("--waiting", action="store_true", help="print the waiting list (videos no scripted path could get); no network")
    ap.add_argument("videos", nargs="*")
    a = ap.parse_args(argv)
    if a.waiting:
        print(sites.waiting_report(CANON))
        return 0
    if not a.analyst and not a.status:
        ap.error("--analyst is required")
    if not a.status and not ensure_proxy():
        print(f"YT_PROXY DOWN: {proxy_url()} not reachable; no request made (never falls back to the home IP). "
              f"See MyTradingSys/system/YT_PROXY.md")
        return EXIT_PROXY_DOWN
    gate = guard_gate(a)
    if gate == EXIT_BLOCKED and (a.channel or a.videos):
        if a.canonical_out:
            CANON = a.canonical_out
        return locked_run(a, Path(a.out))
    if gate is not None:
        return gate
    ALLOW_FALLBACK = a.fallback
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
    after = []
    for n, (vid, r) in enumerate(res):
        if r in ("BLOCKED", "UNVERIFIED"):   # path 4 by itself; a miss goes to the waiting list
            if n:
                time.sleep(sites.PAUSE_S)
            r = recover(vid, a.analyst, a.langs.split(","), outdir, "", ["ytdlp:" + r.lower()])
        after.append((vid, r))
        bad += not r.startswith(("OK", "EXISTS"))
        print(f"{vid} {r}", flush=True)
    if any(r == "WAITING" for _, r in after):
        print(NEXT_PATH + "; waiting list: python scripts/dev/fetch_captions_timed.py --waiting")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
