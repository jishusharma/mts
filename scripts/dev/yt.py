"""YouTube freedom: one command for captions / audio / transcript of any video id, URL, playlist or channel, never stopped
by one banned IP (operator 2026-11-13: "I need workarounds, I need backups, so that I can download what I need when I need").

    python scripts/dev/yt.py get <id|url|playlist|@channel> [...] [--audio] [--transcript] [--langs hi,en] [--limit 10]
    python scripts/dev/yt.py health [--cached]    one line per route: up / down / locked until
    python scripts/dev/yt.py doctor               restart wireproxy, (re)start Tor, refresh mirrors, drop expired locks
    python scripts/dev/yt.py setup                what every machine runs once: install Tor, refresh mirrors, show health
    python scripts/dev/yt.py routes               the route order

Output goes to the shared cache (env YT_CACHE_DIR; default F:/MTS/data_cache/youtube when that drive exists, else
~/.mts/yt_cache): <id>_timed.txt (header + `[HH:MM:SS] text`), <id>_raw.txt (also in raw_transcripts_canonical/), <id>.meta.json,
<id>.m4a|webm for --audio. A cached video costs no request. Every `get` line names the route that worked.

Routes, tried in this order for one video, a lock or failure moves to the next route in the SAME call (never a wait):
  warp          Cloudflare WARP SOCKS (wgcf + wireproxy), through the legacy per-IP guard of fetch_captions_timed.py
  v6            this machine's own IPv6 address (the home IPv4 can be 429-locked while IPv6 is not; measured 2026-11-14)
  tor           local Tor SOCKS (official expert bundle, scripts/dev/yt_tor.py), YouTube only
  invidious     self-refreshing public Invidious mirrors (yt_mirrors.py): the request never reaches YouTube from here
  piped         same for Piped mirrors
  clients:<x>   yt-dlp with other player clients (tv, web_embedded, mweb, android_vr, ios) through exit <x>
  asr           audio through any route + local Whisper (--transcript only, when no captions exist anywhere)
  gha           GitHub Actions one-shot workflow_dispatch run (a different IP; public captions; run artifact, no cron)
  fleet         `mts_signal.py ask` to another machine (asynchronous: files come back through the repo)
The legacy home-IP path is never a route (fail closed). Every address keeps its own pacing and lock (OURS: pause 8-10 s between
requests, a 429 locks the exit 30 min, then 2 h, then 12 h; a sign-in check only skips the plain-client route 15 min).
Only YouTube hosts may go through a proxy exit (yt_only): no trading or other traffic ever.
"""
import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nowin  # noqa: E402
import yt_mirrors as mirrors  # noqa: E402
import yt_tor  # noqa: E402
import fetch_captions_timed as ft  # noqa: E402

ROOT = HERE.parents[1]
YT_HOSTS = ("youtube.com", "youtu.be", "googlevideo.com", "ytimg.com", "youtube-nocookie.com", "ggpht.com")
LOCK_LEVELS_H = (0.5, 2, 12)          # OURS: exit lock after the 1st, 2nd, 3rd+ consecutive 429
SOFT_LOCK_H = 0.25                    # OURS: plain-client route skipped after a sign-in check
PACE_S = {"warp": 10, "v6": 8, "tor": 8, "direct": 5}   # OURS: seconds between two requests through one exit
CLIENTS = ("tv", "web_embedded", "mweb", "android_vr", "ios")
PROBE_URL = "https://www.youtube.com/generate_204"
SLEEP = time.sleep
ROUTE_ORDER = ("warp", "v6", "tor", "invidious", "piped", "clients:warp", "clients:v6", "clients:tor", "asr", "gha", "fleet")


# ---- errors -------------------------------------------------------------------------------------------------

class Locked(Exception):
    """A 429 / bot check: `hard` locks the whole exit, soft only skips the route that hit it."""
    def __init__(self, why, hard=True, scope="all", until=None):
        super().__init__(why)
        self.why, self.hard, self.scope, self.until = why, hard, scope, until   # until: a known end of the block (datetime)   # scope: "all" or one capability ("captions": timedtext only)


class RouteDown(Exception):
    """The route cannot run now (not installed, port closed, mirror down, transient error)."""


class Miss(Exception):
    """The route worked but the video has no captions / is unavailable; `final` = YouTube itself said so."""
    def __init__(self, why, final=False):
        super().__init__(why)
        self.why, self.final = why, final


# ---- proxy allowlist -----------------------------------------------------------------------------------------

def yt_only(url):
    """Refuse any URL whose host is not a YouTube host: nothing else may go through a proxy exit."""
    from urllib.parse import urlparse
    host = (urlparse(url).hostname or "").lower()
    if not any(host == h or host.endswith("." + h) for h in YT_HOSTS):
        raise ValueError(f"refused: {host or url} is not a YouTube host, proxies carry YouTube traffic only")
    return url


# ---- paths and state -----------------------------------------------------------------------------------------

def cache_dir():
    env = os.environ.get("YT_CACHE_DIR")
    if env:
        return Path(env)
    if Path("F:/MTS/data_cache").exists():
        return Path("F:/MTS/data_cache/youtube")
    return Path.home() / ".mts" / "yt_cache"


def state_file():
    return Path(os.environ.get("YT_ROUTES_FILE") or Path.home() / ".mts" / "yt_routes.json")


def _now():
    return datetime.now(timezone.utc)


def _iso(t):
    return t.isoformat(timespec="seconds")


def _t(s):
    try:
        t = datetime.fromisoformat(s or "")
        return t if t.tzinfo else t.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def load_state():
    try:
        d = json.loads(state_file().read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def save_state(d):
    p = state_file()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, indent=1), encoding="utf-8", newline="\n")


def locked_until(key, now=None):
    """datetime a lock on `key` ('exit:tor', 'route:tor', ...) ends, or None."""
    t = _t((load_state().get(key) or {}).get("locked_until"))
    return t if t and t > (now or _now()) else None


def lock(key, hours, why):
    d = load_state()
    row = d.setdefault(key, {})
    row.update(locked_until=_iso(_now() + timedelta(hours=hours)), why=why[:80])
    save_state(d)


def lock_until_at(key, until, why):
    """Lock `key` until a known moment (the legacy guard's own record), never shorter than what is already set."""
    d = load_state()
    row = d.setdefault(key, {})
    cur = _t(row.get("locked_until"))
    row.update(locked_until=_iso(max(until, cur) if cur else until), why=why[:80])
    save_state(d)


def lock_hard(exit_name, why, scope="all"):
    """Escalating exit lock (30 min, 2 h, 12 h on consecutive 429s); returns the hours used. A scope other than "all" locks
    only that capability (Tor: the timedtext endpoint refuses its exits while metadata and audio still work)."""
    d = load_state()
    row = d.setdefault("exit:" + exit_name + ("" if scope == "all" else ":" + scope), {})
    last = _t(row.get("level_t"))
    level = int(row.get("level") or 0)
    level = min(level + 1, len(LOCK_LEVELS_H)) if last else 1
    hours = LOCK_LEVELS_H[level - 1]
    row.update(locked_until=_iso(_now() + timedelta(hours=hours)), why=why[:80], level=level, level_t=_iso(_now()))
    save_state(d)
    return hours


def note_ok(exit_name, scope="all"):
    d = load_state()
    row = d.setdefault("exit:" + exit_name + ("" if scope == "all" else ":" + scope), {})
    row.update(level=0, level_t=_iso(_now()), last_ok=_iso(_now()))
    row.pop("locked_until", None)
    save_state(d)


def pace(exit_name):
    """Sleep so two requests through one exit are PACE_S apart (per exit, across processes via the state file)."""
    gap = PACE_S.get(exit_name, 8)
    d = load_state()
    last = _t((d.get("exit:" + exit_name) or {}).get("last_req"))
    if last:
        wait = gap - (_now() - last).total_seconds()
        if 0 < wait <= gap:
            SLEEP(wait)
    d = load_state()
    d.setdefault("exit:" + exit_name, {})["last_req"] = _iso(_now())
    save_state(d)


# ---- exits ---------------------------------------------------------------------------------------------------

class Exit:
    name = ""
    proxy = None
    source_address = None
    MAX_ROTATIONS = 0

    def rotate(self):
        """Get a different exit address for the next request (True when done). Only Tor has one."""
        return False

    def ydl_opts(self):
        o = {}
        if self.proxy:
            o["proxy"] = self.proxy
        if self.source_address:
            o["source_address"] = self.source_address
        return o

    def available(self):
        """(ok, why): cheap local check, no network."""
        return True, ""

    def probe(self):
        """(ok, detail): one YouTube-only request (generate_204) through this exit."""
        ok, why = self.available()
        if not ok:
            return False, why
        try:
            import yt_dlp
            yt_only(PROBE_URL)
            with yt_dlp.YoutubeDL(dict(quiet=True, no_warnings=True, socket_timeout=20, **self.ydl_opts())) as y:
                st = y.urlopen(PROBE_URL).status
            return st in (200, 204), f"HTTP {st}"
        except ImportError:
            return False, "yt-dlp not installed"
        except Exception as e:
            return False, str(e)[:70]


class WarpExit(Exit):
    name = "warp"

    @property
    def proxy(self):
        return ft.proxy_url() or ("socks5://%s:%d" % ft.PROXY_ADDR)

    def available(self):
        if not (ft.proxy_dir() / "wireproxy.conf").exists() and not os.environ.get("YT_PROXY"):
            return False, "not set up (YT_PROXY.md: wgcf + wireproxy)"
        if not ft._port_open(ft.PROXY_ADDR):
            if not ft.ensure_proxy(wait=25):
                return False, "wireproxy not answering on 127.0.0.1:40000"
        return True, ""


class TorExit(Exit):
    name = "tor"
    proxy = property(lambda self: yt_tor.socks_url())
    MAX_ROTATIONS = 2   # OURS: fresh circuits tried inside one call before the exit is locked

    def rotate(self):
        SLEEP(10)   # Tor allows about one NEWNYM per 10 s
        return yt_tor.newnym()

    def available(self):
        if yt_tor.exe_path() is None:
            return False, "not installed (python scripts/dev/yt.py setup)"
        try:
            if not yt_tor.start(wait=90):
                return False, "tor did not bootstrap"
        except yt_tor.TorError as e:
            return False, str(e)[:60]
        return True, ""


class V6Exit(Exit):
    name = "v6"
    source_address = "::"

    def available(self):
        try:
            infos = socket.getaddrinfo("www.youtube.com", 443, socket.AF_INET6)
            with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
                s.settimeout(8)
                s.connect(infos[0][4])
            return True, ""
        except (OSError, IndexError):
            return False, "no working IPv6 path to youtube.com"


class DirectExit(Exit):
    """This machine's own address: only inside the GitHub Actions runner (env YT_ALLOW_DIRECT=1), never on a station."""
    name = "direct"

    def available(self):
        if os.environ.get("YT_ALLOW_DIRECT") != "1":
            return False, "home address is never a route (YT_ALLOW_DIRECT unset)"
        return True, ""


EXITS = {"warp": WarpExit, "v6": V6Exit, "tor": TorExit, "direct": DirectExit}


# ---- yt-dlp caption / audio / listing helpers ---------------------------------------------------------------------

def classify_error(msg, status=None):
    """Raise the route error a yt-dlp / HTTP failure means."""
    m = msg or ""
    if status == 429 or "429" in m or "Too Many Requests" in m:
        raise Locked("HTTP 429", hard=True)
    if "Sign in to confirm" in m or "not a bot" in m:
        raise Locked("sign-in check", hard=False)
    if re.search(r"Video unavailable|Private video|has been removed|members-only|This video is not available|account associated", m):
        raise Miss("unavailable: " + m[:50], final=True)
    raise RouteDown(m[:80] or "failed")


def tracks_from_info(info):
    """[{"code","auto","orig","url"}] vtt tracks from a yt-dlp info dict (manual, auto original, auto translations)."""
    out = []
    for key, auto in (("subtitles", False), ("automatic_captions", True)):
        for code, fmts in (info.get(key) or {}).items():
            vtt = next((f for f in fmts or [] if f.get("ext") == "vtt" and f.get("url")), None)
            if not vtt:
                continue
            url = vtt["url"]
            translated = auto and "tlang=" in url
            out.append({"code": code.replace("-orig", ""), "auto": auto, "orig": auto and not translated, "url": url,
                        "translated": translated})
    return out


def pick_ytdlp_track(tracks, langs):
    """Manual in a wanted language, auto original in one, any manual, any auto original, then a translation of a wanted
    language (translations are what YouTube throttles hardest, so they come last)."""
    want = [l.strip().lower() for l in langs if l.strip()]

    def same(t, w):
        c = t["code"].lower()
        return c == w or c.split("-")[0] == w.split("-")[0]
    for pred in (lambda t: not t["auto"], lambda t: t["auto"] and not t["translated"]):
        for w in want:
            for t in tracks:
                if pred(t) and same(t, w):
                    return t
    for t in tracks:
        if not t["auto"]:
            return t
    for t in tracks:
        if t["auto"] and not t["translated"]:
            return t
    for w in want:
        for t in tracks:
            if t["translated"] and same(t, w):
                return t
    return None


class _Quiet:
    """yt-dlp logger that prints nothing: a failing client is normal here and the error is classified, not shown."""
    debug = info = warning = error = staticmethod(lambda *a, **k: None)


def ytdlp_opts(ex, client=None, **more):
    o = dict(quiet=True, no_warnings=True, skip_download=True, socket_timeout=40, noprogress=True, logger=_Quiet(), **more)
    o.update(ex.ydl_opts())
    if client:
        o["extractor_args"] = {"youtube": {"player_client": [client]}}
    return o


def ytdlp_captions(ex, vid, langs, client=None):
    """{"cues","info","lang","auto"} through exit `ex` with yt-dlp (one metadata extract + one caption download)."""
    import yt_dlp
    url = yt_only(f"https://www.youtube.com/watch?v={vid}")
    pace(ex.name)
    try:
        with yt_dlp.YoutubeDL(ytdlp_opts(ex, client)) as y:
            info = y.extract_info(url, download=False) or {}
            t = pick_ytdlp_track(tracks_from_info(info), langs)
            if not t:
                raise Miss("no caption track", final=True)
            yt_only(t["url"])
            pace(ex.name)
            try:
                text = y.urlopen(t["url"]).read().decode("utf-8", "replace")
            except Exception as e:
                if getattr(e, "status", None) == 429 or "429" in str(e):
                    raise Locked("timedtext HTTP 429", hard=True, scope="captions")
                raise
    except (Locked, Miss, RouteDown):
        raise
    except yt_dlp.utils.DownloadError as e:
        classify_error(str(e))
    except Exception as e:   # yt-dlp's HTTPError carries .status; socket/proxy failures land here too
        classify_error(str(e), getattr(e, "status", None))
    cues = ft.parse_vtt(text)
    if not cues:
        raise RouteDown("caption file empty or not vtt")
    return {"cues": cues, "info": {"title": info.get("title") or "", "upload_date": info.get("upload_date") or "",
                                   "uploader": info.get("uploader") or "", "duration": info.get("duration")},
            "lang": t["code"], "auto": t["auto"]}


def ytdlp_audio(ex, vid, dest, client=None):
    import yt_dlp
    url = yt_only(f"https://www.youtube.com/watch?v={vid}")
    pace(ex.name)
    opts = ytdlp_opts(ex, client, outtmpl=str(dest) + ".%(ext)s", format="bestaudio[ext=m4a]/bestaudio")
    opts["skip_download"] = False
    try:
        with yt_dlp.YoutubeDL(opts) as y:
            y.extract_info(url, download=True)
    except yt_dlp.utils.DownloadError as e:
        classify_error(str(e))
    except Exception as e:
        classify_error(str(e), getattr(e, "status", None))
    got = sorted(Path(dest).parent.glob(Path(dest).name + ".*"))
    got = [g for g in got if g.suffix not in (".part", ".ytdl")]
    if not got:
        raise RouteDown("audio file missing after download")
    return got[0]


def ytdlp_list(ex, target, limit, client=None):
    import yt_dlp
    kind, val = mirrors.classify(target)
    if kind == "playlist":
        url = "https://www.youtube.com/playlist?list=" + val
    else:
        url = mirrors.channel_url(target).rstrip("/")
        if "/videos" not in url:
            url += "/videos"
    yt_only(url)
    pace(ex.name)
    try:
        with yt_dlp.YoutubeDL(ytdlp_opts(ex, client, extract_flat=True, playlistend=limit)) as y:
            info = y.extract_info(url, download=False) or {}
    except yt_dlp.utils.DownloadError as e:
        classify_error(str(e))
    except Exception as e:
        classify_error(str(e), getattr(e, "status", None))
    rows = [(e["id"], e.get("title") or "", "") for e in info.get("entries") or [] if e and e.get("id")]
    if not rows:
        raise RouteDown("listing empty")
    return rows[:limit]


# ---- routes --------------------------------------------------------------------------------------------------

class Route:
    name = ""
    caps = ()
    batch = False

    def exit_name(self):
        return None

    def available(self):
        return True, ""

    def health(self, probe=True):
        """(state, detail): state 'up' | 'down' | 'locked'."""
        lk = self.lock_until()
        if lk:
            return "locked", "until " + _iso(lk) + " " + (self._why() or "")
        ok, why = self.available()
        return ("up", why) if ok else ("down", why)

    def _keys(self, cap=None):
        keys = ["route:" + self.name]
        if self.exit_name():
            keys.append("exit:" + self.exit_name())
            if cap:
                keys.append("exit:" + self.exit_name() + ":" + cap)
        return keys

    def _why(self, cap=None):
        d = load_state()
        for k in self._keys(cap):
            if (d.get(k) or {}).get("why") and locked_until(k):
                return d[k]["why"]
        return ""

    def lock_until(self, cap=None):
        ends = [e for e in (locked_until(k) for k in self._keys(cap)) if e]
        return max(ends) if ends else None

    def scoped_note(self):
        """' captions locked until ...' for a capability lock on an otherwise usable exit, else ''."""
        if not self.exit_name():
            return ""
        lk = locked_until("exit:" + self.exit_name() + ":captions")
        return f"; captions locked until {_iso(lk)} (audio/listing still usable)" if lk else ""


class ExitRoute(Route):
    """yt-dlp through one exit with its default client (audio also tries android_vr)."""
    caps = ("captions", "audio", "list")
    CAPTION_CLIENTS = (None,)
    AUDIO_CLIENTS = (None, "android_vr")
    LIST_CLIENTS = (None,)

    def __init__(self, ex):
        self.ex = ex
        self.name = ex.name

    def exit_name(self):
        return self.ex.name

    def available(self):
        return self.ex.available()

    def health(self, probe=True):
        lk = self.lock_until()
        if lk:
            return "locked", "until " + _iso(lk) + " " + (self._why() or "")
        ok, why = self.ex.available()
        if not ok:
            return "down", why
        if not probe:
            return "up", ""
        ok, why = self.ex.probe()
        return ("up", why + self.scoped_note()) if ok else ("down", why)

    def _guard_in(self):
        if self.ex.name == "warp":   # the legacy per-IP guard (lockout record, fleet block, daily budget) keeps ruling WARP
            try:
                ft.spend("yt.py")
            except ft.YTBlocked as e:
                raise Locked("legacy guard locked until " + str(e), hard=True, until=_t(str(e)))
            except ft.BudgetExceeded as e:
                raise Locked("legacy guard budget: " + str(e)[:40], hard=True)

    def _guard_out(self, ok, locked):
        if self.ex.name == "warp":
            if locked:
                ft.mark_blocked()
            elif ok:
                ft.mark_clean()

    def _run(self, fn, clients):
        last = None
        rotations = self.ex.MAX_ROTATIONS
        for c in clients:
            while True:
                try:
                    self._guard_in()
                    r = fn(c)
                    self._guard_out(True, False)
                    return r
                except Locked as e:
                    self._guard_out(False, e.hard)
                    if e.hard:
                        if rotations > 0 and self.ex.rotate():   # same call, new exit address (Tor: fresh circuit)
                            rotations -= 1
                            continue
                        raise
                    last = e   # a sign-in check is client-specific: the next client may pass
                except RouteDown as e:
                    last = e
                break
        raise last or RouteDown("no client worked")

    def captions(self, vid, langs):
        return self._run(lambda c: ytdlp_captions(self.ex, vid, langs, c), self.CAPTION_CLIENTS)

    def audio(self, vid, dest):
        return self._run(lambda c: ytdlp_audio(self.ex, vid, dest, c), self.AUDIO_CLIENTS)

    def listing(self, target, limit):
        return self._run(lambda c: ytdlp_list(self.ex, target, limit, c), self.LIST_CLIENTS)


class ClientsRoute(ExitRoute):
    """yt-dlp through exit <x> with the other player clients, one try each (tv, web_embedded, mweb, android_vr, ios)."""
    CAPTION_CLIENTS = AUDIO_CLIENTS = LIST_CLIENTS = CLIENTS

    def __init__(self, ex):
        super().__init__(ex)
        self.name = "clients:" + ex.name

    def health(self, probe=True):
        lk = self.lock_until()
        if lk:
            return "locked", "until " + _iso(lk) + " " + (self._why() or "")
        ok, why = self.ex.available()
        return ("up", "same exit as " + self.ex.name) if ok else ("down", why)


class MirrorRoute(Route):
    caps = ("captions", "audio", "list")
    MAX_HOSTS = 4   # OURS: mirrors tried per video

    def __init__(self, kind):
        self.kind, self.name = kind, kind

    def _hosts(self):
        if mirrors.list_age_h(self.kind) is None or mirrors.list_age_h(self.kind) > mirrors.LIST_TTL_H:
            try:
                mirrors.refresh()
            except Exception:
                pass
        return mirrors.candidates(self.kind)[:self.MAX_HOSTS]

    def available(self):
        hosts = mirrors.candidates(self.kind)
        return (True, f"{len(hosts)} candidate(s)") if hosts else (False, "no live mirror cached (yt.py doctor)")

    def health(self, probe=True):
        if probe:
            try:
                mirrors.refresh(force=False)
            except Exception:
                pass
        n, tot, live = mirrors.health_summary(self.kind)
        if n:
            return "up", f"{n} of {tot} live: {', '.join(h.replace('https://', '') for h in live[:4])}"
        return "down", f"0 of {tot} live"

    def _try(self, fn):
        last = None
        for host in self._hosts():
            try:
                r = fn(host)
                mirrors.mark(self.kind, host, True)
                return r
            except mirrors.MirrorDown as e:
                mirrors.mark(self.kind, host, False, str(e))
                last = e
        raise RouteDown(str(last) if last else "no mirror")

    def captions(self, vid, langs):
        fn = mirrors.inv_captions if self.kind == "invidious" else mirrors.piped_captions
        got_none = []

        def one(host):
            r = fn(host, vid, langs)
            if r is None:
                got_none.append(host)
                raise mirrors.MirrorDown("no captions on this mirror")
            return r
        try:
            return self._try(one)
        except RouteDown:
            if got_none:
                raise Miss("no captions on " + got_none[0])
            raise

    def audio(self, vid, dest):
        fn = mirrors.inv_audio if self.kind == "invidious" else mirrors.piped_audio
        return self._try(lambda host: fn(host, vid, dest))

    def listing(self, target, limit):
        fn = mirrors.inv_list if self.kind == "invidious" else mirrors.piped_list
        return self._try(lambda host: fn(host, target, limit))


class TranscriptApiRoute(Route):
    """youtube-transcript-api on the runner's own address (GitHub Actions only; a station never calls YouTube directly)."""
    caps = ("captions",)

    def __init__(self):
        self.name = "tapi:direct"

    def available(self):
        if os.environ.get("YT_ALLOW_DIRECT") != "1":
            return False, "home address is never a route (YT_ALLOW_DIRECT unset)"
        try:
            import youtube_transcript_api  # noqa: F401
        except ImportError:
            return False, "youtube-transcript-api not installed"
        return True, ""

    def captions(self, vid, langs):
        from youtube_transcript_api import YouTubeTranscriptApi
        try:
            t = YouTubeTranscriptApi().fetch(vid, languages=list(langs))
        except Exception as e:
            msg = str(e)
            if "Too Many Requests" in msg or "429" in msg or "blocking requests from your IP" in msg:
                raise Locked("transcript-api blocked", hard=False)
            if "Subtitles are disabled" in msg or "No transcripts" in msg:
                raise Miss("no transcript")
            raise RouteDown(msg[:70])
        cues = [(int(s.start), " ".join(s.text.split())) for s in t.snippets if s.text.strip()]
        if not cues:
            raise Miss("empty transcript")
        return {"cues": cues, "info": {}, "lang": getattr(t, "language_code", None), "auto": bool(getattr(t, "is_generated", True))}


class AsrRoute(Route):
    caps = ("transcribe",)

    def __init__(self):
        self.name = "asr"

    def python(self):
        return os.environ.get("YT_ASR_PYTHON") or "F:/MTS/tools/asr-venv/Scripts/python.exe"

    def available(self):
        return (True, "") if Path(self.python()).exists() else (False, "no ASR venv (F:/MTS/tools/asr-venv; ROUTING.md local ASR)")

    def transcribe(self, vid, audio, langs, run=subprocess.run):
        """[(start_s, text)] from local faster-whisper; model small for non-English, medium.en for English."""
        lang = (langs[0] if langs else "en").split("-")[0]
        model = "medium.en" if lang == "en" else "small"
        out = Path(audio).with_suffix(".asr.jsonl")
        out.unlink(missing_ok=True)
        cmd = [self.python(), str(HERE / "asr_transcribe.py"), "--audio", str(audio), "--out", str(out), "--model", model,
               "--language", lang, "--no-hotwords"]
        r = run(cmd, capture_output=True, creationflags=nowin.NOWIN, text=True)
        if r.returncode != 0 or not out.exists():
            raise RouteDown("whisper failed: " + (r.stderr or r.stdout or "")[-80:])
        cues = []
        for line in out.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if rec.get("text"):
                cues.append((int(rec.get("start") or 0), " ".join(str(rec["text"]).split())))
        if not cues:
            raise Miss("whisper produced no text")
        return {"cues": cues, "info": {}, "lang": lang, "auto": True, "model": model}


class GhaRoute(Route):
    """Batch route: one workflow_dispatch run of .github/workflows/yt-fetch.yml (GitHub's own IP), results as a run artifact."""
    caps = ("captions",)
    batch = True

    def __init__(self):
        self.name = "gha"

    def available(self):
        if not shutil.which("gh"):
            return False, "gh not installed on this machine"
        return True, ""

    def run_batch(self, vids, langs, run=subprocess.run, sleep=None, timeout_s=1500):
        """{vid: result-dict} for the ids the runner got. Raises RouteDown when the run cannot be started or fails."""
        sleep = sleep or SLEEP
        gh = shutil.which("gh")
        if not gh:
            raise RouteDown("gh not installed")
        t0 = _now() - timedelta(seconds=10)
        r = run([gh, "workflow", "run", "yt-fetch.yml", "--ref", os.environ.get("YT_GHA_REF", "fast-track"),
                 "-f", "ids=" + ",".join(vids), "-f", "langs=" + ",".join(langs)], cwd=str(ROOT), capture_output=True, creationflags=nowin.NOWIN, text=True)
        if r.returncode != 0:
            raise RouteDown("dispatch failed: " + (r.stderr or r.stdout)[-80:])
        rid = None
        for _ in range(12):
            sleep(5)
            out = run([gh, "run", "list", "--workflow", "yt-fetch.yml", "--limit", "5", "--json",
                       "databaseId,createdAt,event"], cwd=str(ROOT), capture_output=True, creationflags=nowin.NOWIN, text=True).stdout
            try:
                rows = [x for x in json.loads(out or "[]") if x.get("event") == "workflow_dispatch"
                        and (_t(x.get("createdAt")) or t0) >= t0]
            except ValueError:
                rows = []
            if rows:
                rid = rows[0]["databaseId"]
                break
        if not rid:
            raise RouteDown("run did not appear")
        end = time.monotonic() + timeout_s
        while time.monotonic() < end:
            out = run([gh, "run", "view", str(rid), "--json", "status,conclusion"], cwd=str(ROOT), capture_output=True, creationflags=nowin.NOWIN,
                      text=True).stdout
            try:
                st = json.loads(out or "{}")
            except ValueError:
                st = {}
            if st.get("status") == "completed":
                if st.get("conclusion") != "success":
                    raise RouteDown(f"run {rid} ended {st.get('conclusion')}")
                break
            sleep(15)
        else:
            raise RouteDown(f"run {rid} still running after {timeout_s} s")
        with tempfile.TemporaryDirectory() as td:
            r = run([gh, "run", "download", str(rid), "-D", td], cwd=str(ROOT), capture_output=True, creationflags=nowin.NOWIN, text=True)
            if r.returncode != 0:
                raise RouteDown("artifact download failed: " + (r.stderr or "")[-60:])
            got = {}
            for p in Path(td).rglob("*.json"):
                try:
                    rec = json.loads(p.read_text(encoding="utf-8"))
                except ValueError:
                    continue
                if isinstance(rec, dict) and rec.get("cues") and p.stem in vids:
                    rec["cues"] = [(int(s), t) for s, t in rec["cues"]]
                    got[p.stem] = rec
        return got


class FleetRoute(Route):
    """Batch route, asynchronous: asks the other machines through mts_signal.py; files come back through the repo."""
    caps = ()
    batch = True

    def __init__(self):
        self.name = "fleet"

    def available(self):
        return (True, "") if (HERE / "mts_signal.py").exists() else (False, "mts_signal.py missing")

    def ask(self, vids, run=subprocess.run):
        shown = ",".join(vids[:6]) + (f" (+{len(vids) - 6} more, see yt_waiting)" if len(vids) > 6 else "")
        text = f"yt-freedom: fetch captions {shown}: python scripts/dev/yt.py get <id> --no-remote; ship cache files via sync.py"
        r = run([sys.executable, str(HERE / "mts_signal.py"), "ask", text[:190], "--to", "all", "--type", "task"],
                capture_output=True, creationflags=nowin.NOWIN, text=True, cwd=str(ROOT))
        m = re.search(r"\bq-[0-9a-f]{6}\b", (r.stdout or "") + (r.stderr or ""))
        if r.returncode != 0 and not m:
            raise RouteDown("ask failed: " + (r.stderr or r.stdout or "")[-60:])
        return m.group(0) if m else "sent"


def build_routes(names=None, runner=False):
    """Routes in ROUTE_ORDER (all of them), or only `names`. runner=True is the GitHub Actions set: the runner's own address
    plus mirrors, nothing that needs a station's proxies."""
    ex = {n: cls() for n, cls in EXITS.items()}
    allr = {"warp": ExitRoute(ex["warp"]), "v6": ExitRoute(ex["v6"]), "tor": ExitRoute(ex["tor"]),
            "invidious": MirrorRoute("invidious"), "piped": MirrorRoute("piped"),
            "clients:warp": ClientsRoute(ex["warp"]), "clients:v6": ClientsRoute(ex["v6"]),
            "clients:tor": ClientsRoute(ex["tor"]), "asr": AsrRoute(), "gha": GhaRoute(), "fleet": FleetRoute(),
            "direct": ExitRoute(ex["direct"]), "clients:direct": ClientsRoute(ex["direct"]), "tapi:direct": TranscriptApiRoute()}
    if runner:
        order = ["direct", "tapi:direct", "invidious", "piped", "clients:direct"]
    else:
        order = list(ROUTE_ORDER)
    if names:
        order = [n for n in order if n in names]
    return [allr[n] for n in order]


# ---- cache / store ----------------------------------------------------------------------------------------------

def cached(vid, cache=None):
    """Path of an existing caption file for vid (cache dir, then the canonical store), or None."""
    cache = cache or cache_dir()
    for p in (cache / f"{vid}_timed.txt", ft.CANON / f"{vid}_timed.txt", cache / f"{vid}_raw.txt", ft.CANON / f"{vid}_raw.txt"):
        if p.exists():
            return p
    return None


def store(vid, res, route, analyst="", channel="", cache=None):
    """Write the cache files (same format as fetch_captions_timed) + meta.json; returns the timed file path."""
    cache = cache or cache_dir()
    cache.mkdir(parents=True, exist_ok=True)
    kind = "auto" if res.get("auto") else "manual"
    ft.store(vid, analyst, cache, channel, res.get("info") or {}, kind, res["cues"], f"yt.py route {route}")
    meta = {"id": vid, "route": route, "lang": res.get("lang"), "kind": kind, "cues": len(res["cues"]),
            "fetched": _iso(_now()), "info": res.get("info") or {}}
    (cache / f"{vid}.meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n")
    return cache / f"{vid}_timed.txt"


def audio_cached(vid, cache=None):
    cache = cache or cache_dir()
    for ext in ("m4a", "webm", "mp3", "opus"):
        p = cache / f"{vid}.{ext}"
        if p.exists():
            return p
    return None


# ---- orchestration ------------------------------------------------------------------------------------------------

def _blocked_reason(route, cap=None):
    lk = route.lock_until(cap)
    return f"locked until {_iso(lk)}" if lk else ""


def run_route(route, fn, cap=None):
    """Run one route call; returns ('ok', value) or (state, reason) after recording locks. Never raises."""
    why = _blocked_reason(route, cap)
    if why:
        return "locked", why
    ok, down = route.available()
    if not ok:
        return "down", down
    try:
        v = fn()
        if route.exit_name():
            note_ok(route.exit_name(), "all" if cap is None else cap)
        return "ok", v
    except Locked as e:
        if e.hard and route.exit_name() and e.until:
            lock_until_at("exit:" + route.exit_name() + ("" if e.scope == "all" else ":" + e.scope), e.until, e.why)
            return "locked", f"{e.why}"
        if e.hard and route.exit_name():
            hours = lock_hard(route.exit_name(), e.why, e.scope)
            return "locked", f"{e.why}, {'exit' if e.scope == 'all' else e.scope} locked {hours} h"
        lock("route:" + route.name, SOFT_LOCK_H, e.why)
        return "locked", f"{e.why}, route skipped {int(SOFT_LOCK_H * 60)} min"
    except Miss as e:
        return ("nocaps-final" if e.final else "nocaps"), e.why
    except RouteDown as e:
        return "down", str(e)
    except Exception as e:   # a plug-in's bug must not stop the others
        return "down", f"{type(e).__name__}: {str(e)[:60]}"


def get_captions(vid, routes, langs):
    """(result|None, route_name|None, tried[], final_nocaps) trying each captions-capable route in order, same call."""
    tried, final = [], False
    for r in routes:
        if "captions" not in r.caps or r.batch:
            continue
        st, val = run_route(r, lambda r=r: r.captions(vid, langs), "captions")
        if st == "ok":
            tried.append(f"{r.name}:ok")
            return val, r.name, tried, False
        tried.append(f"{r.name}:{st}({val})")
        if st == "nocaps-final":
            final = True
            break
    return None, None, tried, final


def get_audio(vid, routes, cache):
    cache.mkdir(parents=True, exist_ok=True)
    dest = cache / vid
    tried = []
    for r in routes:
        if "audio" not in r.caps:
            continue
        st, val = run_route(r, lambda r=r: r.audio(vid, dest), "audio")
        tried.append(f"{r.name}:ok" if st == "ok" else f"{r.name}:{st}({val})")
        if st == "ok":
            return Path(val), r.name, tried
    return None, None, tried


def get_video(vid, routes, langs, want_audio=False, want_transcript=False, remote=True, analyst="", cache=None, log=print):
    """One video. Returns dict(status OK|NOCAPS|FAIL|CACHED, route, tried, files)."""
    cache = cache or cache_dir()
    out = {"id": vid, "status": "FAIL", "route": None, "tried": [], "files": []}
    have = cached(vid, cache)
    if have:
        if have.parent != cache and not (cache / have.name).exists():
            cache.mkdir(parents=True, exist_ok=True)
            shutil.copy2(have, cache / have.name)
        out.update(status="CACHED", route="cache", files=[str(have)])
    else:
        res, name, tried, final = get_captions(vid, routes, langs)
        out["tried"] += tried
        if res:
            p = store(vid, res, name, analyst, cache=cache)
            out.update(status="OK", route=name, files=[str(p)], cues=len(res["cues"]), lang=res.get("lang"))
        elif final:
            out["status"] = "NOCAPS"
    if want_audio or (want_transcript and out["status"] in ("FAIL", "NOCAPS")):
        ap = audio_cached(vid, cache)
        if ap:
            out["audio"] = str(ap)
        else:
            ap, aroute, atried = get_audio(vid, routes, cache)
            out["tried"] += ["audio-" + t for t in atried]
            if ap:
                out["audio"], out["audio_route"] = str(ap), aroute
                out["files"].append(str(ap))
    if want_transcript and out["status"] in ("FAIL", "NOCAPS") and out.get("audio"):
        asr = next((r for r in routes if r.name == "asr"), None)
        if asr:
            st, val = run_route(asr, lambda: asr.transcribe(vid, out["audio"], langs))
            out["tried"].append(f"asr:{st}")
            if st == "ok":
                p = store(vid, val, "asr", analyst, cache=cache)
                out.update(status="OK", route="asr", files=out["files"] + [str(p)], cues=len(val["cues"]), lang=val.get("lang"))
    return out


def finish_remote(outs, routes, langs, remote, analyst, cache, log=print):
    """After the per-video pass: the ids still without captions go to gha (synchronous), then fleet (async ask)."""
    todo = [o for o in outs if o["status"] in ("FAIL",)]
    if not todo or not remote:
        return
    ids = [o["id"] for o in todo]
    for r in routes:
        if not r.batch or not todo:
            continue
        if r.name == "gha":
            st, got = run_route(r, lambda r=r: r.run_batch(ids, langs))
            for o in todo:
                o["tried"].append(f"gha:{st}")
            if st == "ok":
                for o in list(todo):
                    res = got.get(o["id"])
                    if res:
                        p = store(o["id"], res, "gha", analyst, cache=cache)
                        o.update(status="OK", route="gha", files=[str(p)], cues=len(res["cues"]), lang=res.get("lang"))
                todo = [o for o in todo if o["status"] == "FAIL"]
                ids = [o["id"] for o in todo]
        elif r.name == "fleet":
            st, qid = run_route(r, lambda r=r: r.ask(ids))
            for o in todo:
                o["tried"].append(f"fleet:{st}" + (f"({qid})" if st == "ok" else ""))
                if st == "ok":
                    o["status"] = "ASKED"
                    o["route"] = "fleet:" + qid
            try:
                import yt_transcript_sites as sites
                for o in todo:
                    sites.add_waiting(o["id"], "", [t for t in o["tried"]])
            except Exception:
                pass


def expand(target, limit, routes):
    """[video ids] for a video/URL (itself), playlist or channel target, listed by the first route that can."""
    kind, val = mirrors.classify(target)
    if kind == "video":
        return [val], []
    if kind == "unknown":
        return [], [f"unrecognised target {target!r}"]
    tried = []
    for r in routes:
        if "list" not in r.caps:
            continue
        st, rows = run_route(r, lambda r=r: r.listing(target, limit), "list")
        tried.append(f"{r.name}:{st}")
        if st == "ok" and rows:
            return [v for v, _, _ in rows][:limit], tried
    return [], tried


def cmd_get(a, routes=None, log=print):
    routes = routes or build_routes([n.strip() for n in a.route.split(",")] if a.route else None)
    langs = [l for l in a.langs.split(",") if l.strip()]
    cache = cache_dir()
    outs, bad = [], 0
    ids = []
    for tg in a.targets:
        got, tried = expand(tg, a.limit, routes)
        if not got:
            log(f"{tg} LIST_FAILED tried: {', '.join(tried) or '-'}")
            bad += 1
        ids += [i for i in got if i not in ids]
    for n, vid in enumerate(ids):
        o = get_video(vid, routes, langs, a.audio, a.transcript, not a.no_remote, a.analyst, cache, log)
        outs.append(o)
    finish_remote(outs, routes, langs, not a.no_remote, a.analyst, cache, log)
    for o in outs:
        extra = f" lang={o.get('lang')} cues={o.get('cues')}" if o.get("cues") else ""
        aud = f" audio={o['audio']} via {o.get('audio_route', 'cache')}" if o.get("audio") else ""
        log(f"{o['id']} {o['status']} route={o['route'] or '-'}{extra}{aud} tried: {', '.join(o['tried']) or '-'}")
        if o["files"]:
            log(f"  {o['files'][0]}")
        bad += o["status"] not in ("OK", "CACHED")
    ok = sum(o["status"] in ("OK", "CACHED") for o in outs)
    log(f"YT_GET {ok} of {len(ids)} ok" + (f", {bad} not" if bad else ""))
    return 1 if bad else 0


# ---- health / doctor / setup --------------------------------------------------------------------------------------

def health_lines(routes, probe=True):
    lines, up_caps = [], 0
    for r in routes:
        try:
            st, detail = r.health(probe)
        except Exception as e:
            st, detail = "down", f"{type(e).__name__}: {str(e)[:50]}"
        up_caps += st == "up" and "captions" in r.caps
        lines.append(f"{r.name:<14}{st:<8}{detail}")
    return lines, up_caps


def cmd_health(a, routes=None, log=print):
    routes = routes or build_routes()
    lines, up = health_lines(routes, probe=not a.cached)
    for l in lines:
        log(l)
    log(f"YT_HEALTH {up} captions route(s) up")
    return 0 if up else 1


def restart_wireproxy():
    """Kill any wireproxy and start it again through the existing helper; returns True when the port answers."""
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/IM", "wireproxy.exe"], capture_output=True, creationflags=nowin.NOWIN)
    else:
        subprocess.run(["pkill", "-x", "wireproxy"], capture_output=True, creationflags=nowin.NOWIN)
    SLEEP(1)
    return ft.ensure_proxy(wait=40)


def cmd_doctor(a, log=print):
    log("doctor: wireproxy " + ("restarted, port answers" if (ft.proxy_dir() / "wireproxy.conf").exists() and restart_wireproxy()
                                else "not up or not set up (YT_PROXY.md)"))
    try:
        if yt_tor.exe_path() is None:
            yt_tor.install()
        log("doctor: tor " + ("up (bootstrapped)" if yt_tor.start(wait=120) else "NOT up, see ~/.mts/ytproxy/tor/tor.log"))
    except Exception as e:
        log(f"doctor: tor {type(e).__name__}: {str(e)[:70]}")
    try:
        live = mirrors.refresh(force=True)
        log("doctor: mirrors " + ", ".join(f"{k} {len(v)} live" for k, v in live.items()))
    except Exception as e:
        log(f"doctor: mirrors {type(e).__name__}: {str(e)[:70]}")
    d = load_state()
    gone = [k for k, v in d.items() if isinstance(v, dict) and v.get("locked_until") and not locked_until(k)]
    for k in gone:
        d[k].pop("locked_until", None)
        d[k].pop("why", None)
    if gone:
        save_state(d)
    log(f"doctor: cleared {len(gone)} expired lock(s)")
    return cmd_health(argparse.Namespace(cached=False), None, log)


def cmd_setup(a, log=print):
    """What every MTS machine runs once (mts_signal.py broadcast --cmd): Tor, mirrors, health."""
    try:
        yt_tor.install()
        log("setup: tor " + ("up" if yt_tor.start(wait=120) else "installed, did not bootstrap (tor.log)"))
    except Exception as e:
        log(f"setup: tor {type(e).__name__}: {str(e)[:80]}")
    try:
        live = mirrors.refresh(force=True)
        log("setup: mirrors " + ", ".join(f"{k} {len(v)} live" for k, v in live.items()))
    except Exception as e:
        log(f"setup: mirrors {type(e).__name__}: {str(e)[:80]}")
    if not (ft.proxy_dir() / "wireproxy.conf").exists():
        log("setup: WARP not set up here: MyTradingSys/system/YT_PROXY.md 'Set up a host' (optional, the other exits do not need it)")
    return cmd_health(argparse.Namespace(cached=False), None, log)


def main(argv):
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(prog="yt.py", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("get", help="captions / audio / transcript for ids, URLs, playlists, @channels")
    g.add_argument("targets", nargs="+")
    g.add_argument("--audio", action="store_true", help="also download the audio file")
    g.add_argument("--transcript", action="store_true", help="make sure a transcript exists: captions, else audio + local Whisper")
    g.add_argument("--langs", default="en,hi", help="preferred caption languages, first wins (default en,hi)")
    g.add_argument("--limit", type=int, default=10, help="videos taken from a playlist or channel (default 10)")
    g.add_argument("--analyst", default="", help="label written into the file header")
    g.add_argument("--route", default="", help="comma list: only these routes (see `routes`)")
    g.add_argument("--no-remote", action="store_true", help="skip the gha and fleet routes (used by the runner and by fleet asks)")
    h = sub.add_parser("health", help="one line per route")
    h.add_argument("--cached", action="store_true", help="no network probes")
    sub.add_parser("doctor", help="restart wireproxy, (re)start Tor, refresh mirrors")
    sub.add_parser("setup", help="install Tor, refresh mirrors, show health (every machine, once)")
    sub.add_parser("routes", help="print the route order")
    a = ap.parse_args(argv)
    if a.cmd == "get":
        return cmd_get(a)
    if a.cmd == "health":
        return cmd_health(a)
    if a.cmd == "doctor":
        return cmd_doctor(a)
    if a.cmd == "setup":
        return cmd_setup(a)
    print("\n".join(ROUTE_ORDER))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
