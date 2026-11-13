"""YouTube freedom, route (c): self-refreshing list of live public Invidious / Piped mirrors, for captions, audio and listings.

A mirror is a public site whose own server talks to YouTube; the request from this machine goes to the mirror, never to
YouTube (video id / channel handle only, no account, no cookies, generic User-Agent). Instances come and go, so the list is
pulled from the public registries (api.invidious.io, the Piped documentation list), every instance is health-checked with a
real request (a registry flag is not trusted: a bot-check page or HTML instead of JSON counts as down, and a bot check is
never worked around), and the good ones are cached in ~/.mts/yt_mirrors.json (env YT_MIRRORS_FILE).

    python scripts/dev/yt_mirrors.py refresh     # pull both lists and probe every candidate
    python scripts/dev/yt_mirrors.py list        # cached state, no network
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

INVIDIOUS_LIST_URL = "https://api.invidious.io/instances.json?sort_by=type,users"
PIPED_LIST_URL = ("https://raw.githubusercontent.com/TeamPiped/documentation/refs/heads/main/"
                  "content/docs/public-instances/index.md")
# Seeds when a registry is unreachable (found 2026-11-13); the registries replace them.
INVIDIOUS_SEED = ("yt.chocolatemoo53.com", "inv.nadeko.net")
PIPED_SEED = ("https://pipedapi.kavin.rocks", "https://pipedapi.adminforge.de", "https://api.piped.private.coffee")
PROBE_VIDEO = "dQw4w9WgXcQ"
USER_AGENT = "Mozilla/5.0 (compatible; transcript-reader)"
TIMEOUT_S = 25
LIST_TTL_H = 6              # OURS: refresh the lists after this many hours
FAIL_COOLDOWN_MIN = 30      # OURS: a mirror that failed is not tried again for this long
MAX_PROBES = 24             # OURS: candidates probed per refresh
MAX_AUDIO_BYTES = 400 * 1024 * 1024
PAUSE_S = 3                 # OURS: seconds between two requests to one mirror


class MirrorDown(Exception):
    """The mirror answered with something that is not its API (bot check, HTML, 4xx/5xx, unreachable)."""


def _ssl_context():
    import ssl
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def http_get(url, timeout=TIMEOUT_S, binary=False):
    """(status, text-or-bytes) of one GET with a generic User-Agent; (0, empty) when unreachable. Tests patch this."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ssl_context()) as r:
            body = r.read()
            return r.status, (body if binary else body.decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        return e.code, (b"" if binary else "")
    except (urllib.error.URLError, OSError, ValueError):
        return 0, (b"" if binary else "")


def http_download(url, dest, timeout=60, cap=MAX_AUDIO_BYTES):
    """Stream url to dest (a .part file renamed at the end); returns bytes written or 0. Tests patch this."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    part = Path(str(dest) + ".part")
    n = 0
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ssl_context()) as r, open(part, "wb") as fh:
            if r.status != 200:
                return 0
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                n += len(chunk)
                if n > cap:
                    raise OSError("audio larger than cap")
                fh.write(chunk)
    except (urllib.error.URLError, OSError, ValueError):
        part.unlink(missing_ok=True)
        return 0
    if n:
        os.replace(part, dest)
    else:
        part.unlink(missing_ok=True)
    return n


def _json(url):
    """Parsed JSON of a mirror endpoint; raises MirrorDown for anything that is not JSON 200 (a bot check is HTML)."""
    status, text = http_get(url)
    if status != 200:
        raise MirrorDown(f"HTTP {status}" if status else "unreachable")
    try:
        return json.loads(text)
    except ValueError:
        raise MirrorDown("not JSON (bot check or HTML)")


# ---- list parsing -------------------------------------------------------------------------------------------

def parse_invidious_list(obj):
    """Hosts from api.invidious.io/instances.json ([[host, info], ...]): https only (no onion/i2p), not flagged down.
    The registry's `api` flag is not trusted (a host flagged false served the API), so it only orders: api-true first."""
    out = []
    for row in obj if isinstance(obj, list) else []:
        try:
            host, info = row[0], row[1]
        except (IndexError, TypeError):
            continue
        if not isinstance(host, str) or not isinstance(info, dict) or info.get("type") != "https":
            continue
        mon = info.get("monitor") if isinstance(info.get("monitor"), dict) else {}
        if mon.get("down") is True:
            continue
        up = mon.get("uptime")
        out.append((0 if info.get("api") else 1, -(up if isinstance(up, (int, float)) else 0), host.strip().lower()))
    return [h for _, _, h in sorted(out)]


def parse_piped_list(md):
    """API base URLs from the Piped documentation table (`| name | https://api... | region | ...`)."""
    out = []
    for line in (md or "").splitlines():
        cells = [c.strip() for c in line.split("|")]
        for c in cells:
            if re.fullmatch(r"https://[A-Za-z0-9.-]+(?::\d+)?", c) and c not in out:
                out.append(c)
                break
    return out


# ---- cache --------------------------------------------------------------------------------------------------

def mirrors_file():
    return Path(os.environ.get("YT_MIRRORS_FILE") or Path.home() / ".mts" / "yt_mirrors.json")


def _utcnow():
    return datetime.now(timezone.utc)


def load():
    try:
        d = json.loads(mirrors_file().read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def save(d):
    p = mirrors_file()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, indent=1), encoding="utf-8", newline="\n")


def _iso(t):
    return t.isoformat(timespec="seconds")


def _t(s):
    try:
        t = datetime.fromisoformat(s or "")
        return t if t.tzinfo else t.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def mark(kind, host, ok, err=""):
    """Record one outcome for a mirror (kind 'invidious' | 'piped')."""
    d = load()
    row = d.setdefault(kind, {}).setdefault(host, {})
    row["ok_at" if ok else "fail_at"] = _iso(_utcnow())
    if ok:
        row["fails"] = 0
        row.pop("err", None)
    else:
        row["fails"] = int(row.get("fails") or 0) + 1
        row["err"] = err[:80]
    save(d)


def candidates(kind, now=None):
    """Hosts to try, best first: proven (ok_at) newest first, then never-tried, never one inside its failure cooldown."""
    now = now or _utcnow()
    d = load()
    rows = d.get(kind) or {}
    proven, fresh = [], []
    for host in d.get(kind + "_list") or (INVIDIOUS_SEED if kind == "invidious" else PIPED_SEED):
        r = rows.get(host) or {}
        fail, ok = _t(r.get("fail_at")), _t(r.get("ok_at"))
        if fail and (not ok or fail > ok) and now - fail < timedelta(minutes=FAIL_COOLDOWN_MIN):
            continue
        (proven if ok and (not fail or ok >= fail) else fresh).append((ok or now, host))
    return [h for _, h in sorted(proven, reverse=True)] + [h for _, h in fresh]


def list_age_h(kind, now=None):
    t = _t(load().get(kind + "_list_at"))
    return None if not t else ((now or _utcnow()) - t).total_seconds() / 3600


# ---- probing / refresh --------------------------------------------------------------------------------------

def probe_invidious(host):
    """True when the host's captions API answers JSON with a `captions` key for the probe video."""
    try:
        j = _json(f"https://{host}/api/v1/captions/{PROBE_VIDEO}")
    except MirrorDown:
        return False
    return isinstance(j, dict) and "captions" in j


def probe_piped(base):
    try:
        j = _json(f"{base}/streams/{PROBE_VIDEO}")
    except MirrorDown:
        return False
    return isinstance(j, dict) and bool(j.get("title"))


def probe(kind, host):
    return probe_invidious(host) if kind == "invidious" else probe_piped(host)


def refresh(force=False, probe_limit=MAX_PROBES, workers=6):
    """Pull both registries (seeds when unreachable), probe the candidates, cache the result. Returns
    {"invidious": [live hosts], "piped": [live bases]}."""
    d = load()
    for kind, url, parser, seed in (("invidious", INVIDIOUS_LIST_URL, None, INVIDIOUS_SEED),
                                    ("piped", PIPED_LIST_URL, parse_piped_list, PIPED_SEED)):
        age = list_age_h(kind)
        if not force and age is not None and age < LIST_TTL_H and d.get(kind + "_list"):
            continue
        status, text = http_get(url)
        hosts = []
        if status == 200:
            try:
                hosts = parse_invidious_list(json.loads(text)) if parser is None else parser(text)
            except ValueError:
                hosts = []
        merged = list(hosts) + [s for s in seed if s not in hosts]
        d[kind + "_list"] = merged
        d[kind + "_list_at"] = _iso(_utcnow())
    save(d)
    live = {}
    for kind in ("invidious", "piped"):
        hosts = (load().get(kind + "_list") or [])[:probe_limit]
        with ThreadPoolExecutor(max_workers=workers) as ex:
            res = list(ex.map(lambda h: (h, _safe_probe(kind, h)), hosts))
        for host, ok in res:
            mark(kind, host, ok, "" if ok else "probe failed")
        live[kind] = [h for h, ok in res if ok]
    return live


def _safe_probe(kind, host):
    try:
        return probe(kind, host)
    except Exception:   # a probe must never raise out of a thread pool
        return False


def health_summary(kind):
    """(live_count, known_count, [live hosts]) from the cache only (no network)."""
    d = load()
    rows = d.get(kind) or {}
    known = d.get(kind + "_list") or []
    live = [h for h in known if (rows.get(h) or {}).get("ok_at")
            and not ((rows.get(h) or {}).get("fail_at") and _t(rows[h]["fail_at"]) > _t(rows[h]["ok_at"]))]
    return len(live), len(known), live


# ---- fetchers -----------------------------------------------------------------------------------------------

def parse_ttml(text):
    """[(start_s, text)] from a TTML subtitle (Piped serves it)."""
    cues, last = [], None
    for m in re.finditer(r"<p\b[^>]*\bbegin=\"([^\"]+)\"[^>]*>(.*?)</p>", text or "", re.S):
        b, body = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
        try:
            if b.endswith("s"):
                start = float(b[:-1])
            else:
                parts = [float(x) for x in b.split(":")]
                start = sum(p * 60 ** i for i, p in enumerate(reversed(parts)))
        except ValueError:
            continue
        t = " ".join(body.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&").replace("&#39;", "'")
                     .replace("&quot;", '"').split())
        if t and t != last:
            cues.append((int(start), t))
            last = t
    return cues


def _cues_from(text):
    from fetch_captions_timed import parse_vtt
    if (text or "").lstrip().startswith("WEBVTT"):
        return parse_vtt(text)
    return parse_ttml(text) if "<tt" in (text or "")[:400] or "<p " in (text or "") else []


def pick_track(tracks, langs):
    """Choose one caption track from [{"code", "auto", ...}]: the first wanted language (manual before auto), else
    any manual, else the first track. Returns the dict or None."""
    langs = [l.strip().lower() for l in langs if l.strip()]
    for want in langs:
        for auto in (False, True):
            for t in tracks:
                code = str(t.get("code") or "").lower()
                if bool(t.get("auto")) == auto and (code == want or code.split("-")[0] == want.split("-")[0]):
                    return t
    for t in tracks:
        if not t.get("auto"):
            return t
    return tracks[0] if tracks else None


def inv_captions(host, vid, langs, sleep=time.sleep):
    """{"cues","info","lang","auto"} from one Invidious host, None when the video has no captions there; MirrorDown when
    the host is not serving its API."""
    base = f"https://{host}"
    j = _json(f"{base}/api/v1/captions/{urllib.parse.quote(vid)}")
    raw = j.get("captions") if isinstance(j, dict) else None
    if not raw:
        return None
    tracks = [{"code": c.get("languageCode"), "auto": "auto-generated" in str(c.get("label", "")).lower(), "url": c.get("url"),
               "label": c.get("label")} for c in raw if c.get("url")]
    t = pick_track(tracks, langs)
    if not t:
        return None
    sleep(PAUSE_S)
    status, text = http_get(base + t["url"])
    if status != 200:
        raise MirrorDown(f"captions HTTP {status}")
    cues = _cues_from(text)
    if not cues:
        raise MirrorDown("captions not parseable")
    sleep(PAUSE_S)
    try:
        m = _json(f"{base}/api/v1/videos/{urllib.parse.quote(vid)}?fields=title,author,published,lengthSeconds")
    except MirrorDown:
        m = {}
    return {"cues": cues, "info": _info(m.get("title"), m.get("published"), m.get("author"), m.get("lengthSeconds")),
            "lang": t.get("code"), "auto": t["auto"]}


def _info(title, published, author, length):
    date = datetime.fromtimestamp(published, timezone.utc).strftime("%Y%m%d") if isinstance(published, (int, float)) else ""
    return {"title": title or "", "upload_date": date, "uploader": author or "", "duration": length}


def piped_captions(base, vid, langs, sleep=time.sleep):
    j = _json(f"{base}/streams/{urllib.parse.quote(vid)}")
    if not isinstance(j, dict) or j.get("error"):
        raise MirrorDown(str((j or {}).get("message") or "error")[:60])
    subs = [{"code": s.get("code"), "auto": bool(s.get("autoGenerated")), "url": s.get("url")}
            for s in j.get("subtitles") or [] if s.get("url")]
    t = pick_track(subs, langs)
    if not t:
        return None
    sleep(PAUSE_S)
    status, text = http_get(t["url"])
    cues = _cues_from(text) if status == 200 else []
    if not cues:
        raise MirrorDown(f"subtitle HTTP {status}" if status != 200 else "subtitle not parseable")
    return {"cues": cues, "info": _info(j.get("title"), None, j.get("uploader"), j.get("duration")),
            "lang": t.get("code"), "auto": t["auto"]}


def pick_audio(formats):
    """Best small audio format from Invidious adaptiveFormats / Piped audioStreams: itag 140 (m4a 128k), else the lowest
    bitrate audio. Each item needs itag/bitrate and a type or mimeType starting with audio/. Returns the dict or None."""
    aud = [f for f in formats or [] if str(f.get("type") or f.get("mimeType") or "").startswith("audio/")]
    for f in aud:
        if str(f.get("itag")) == "140":
            return f
    def br(f):
        try:
            return int(f.get("bitrate") or 10 ** 9)
        except (TypeError, ValueError):
            return 10 ** 9
    return sorted(aud, key=br)[0] if aud else None


def inv_audio(host, vid, dest):
    """Download audio through an Invidious host's own proxy (/latest_version ... local=true); returns (bytes, ext)."""
    j = _json(f"https://{host}/api/v1/videos/{urllib.parse.quote(vid)}")
    f = pick_audio(j.get("adaptiveFormats") if isinstance(j, dict) else None)
    if not f:
        raise MirrorDown("no audio format")
    typ = str(f.get("type") or "")
    ext = "m4a" if "mp4" in typ else "webm"
    path = Path(str(dest) + "." + ext)
    n = http_download(f"https://{host}/latest_version?id={urllib.parse.quote(vid)}&itag={f.get('itag')}&local=true", path)
    if not n:
        raise MirrorDown("audio download failed")
    return path


def piped_audio(base, vid, dest):
    j = _json(f"{base}/streams/{urllib.parse.quote(vid)}")
    f = pick_audio(j.get("audioStreams") if isinstance(j, dict) else None)
    if not f or not f.get("url"):
        raise MirrorDown("no audio stream")
    ext = "m4a" if "mp4" in str(f.get("mimeType") or f.get("format") or "") else "webm"
    path = Path(str(dest) + "." + ext)
    if not http_download(f["url"], path):
        raise MirrorDown("audio download failed")
    return path


def inv_list(host, target, limit):
    """[(video_id, title, YYYY-MM-DD)] for a playlist id/URL or @handle/channel URL through one Invidious host."""
    base = f"https://{host}/api/v1/"
    kind, val = classify(target)
    pl = ucid = None
    if kind == "playlist":
        pl = val
    elif kind == "channel_id":
        ucid = val
    else:
        res = _json(base + "resolveurl?url=" + urllib.parse.quote(channel_url(target), safe=""))
        ucid, pl = res.get("ucid"), res.get("playlistId")
    if pl:
        j = _json(base + "playlists/" + urllib.parse.quote(pl))
        vids = j.get("videos") or []
    elif ucid:
        try:
            j = _json(base + "channels/" + urllib.parse.quote(ucid) + "/videos?sort_by=newest")
            vids = j.get("videos") or []
        except MirrorDown:
            vids = (_json(base + "channels/" + urllib.parse.quote(ucid) + "/latest") or {}).get("videos") or []
    else:
        raise MirrorDown("could not resolve target")
    out = []
    for v in vids:
        if v.get("videoId"):
            p = v.get("published")
            out.append((v["videoId"], v.get("title") or "", datetime.fromtimestamp(p, timezone.utc).strftime("%Y-%m-%d")
                        if isinstance(p, (int, float)) else ""))
    return out[:limit]


def piped_list(base, target, limit):
    kind, val = classify(target)
    if kind == "playlist":
        j = _json(f"{base}/playlists/{urllib.parse.quote(val)}")
    elif kind == "channel_id":
        j = _json(f"{base}/channel/{urllib.parse.quote(val)}")
    else:
        raise MirrorDown("piped lists playlists and channel ids only")
    out = []
    for v in j.get("relatedStreams") or []:
        m = re.search(r"v=([A-Za-z0-9_-]{11})", str(v.get("url") or ""))
        if m:
            up = v.get("uploaded")
            out.append((m.group(1), v.get("title") or "", datetime.fromtimestamp(up / 1000, timezone.utc).strftime("%Y-%m-%d")
                        if isinstance(up, (int, float)) and up > 0 else ""))
    return out[:limit]


# ---- target classification (shared with yt.py) -------------------------------------------------------------

VID_RE = re.compile(r"(?:v=|youtu\.be/|shorts/|embed/|^)([A-Za-z0-9_-]{11})(?:[&?#/]|$)")


def classify(target):
    """('video'|'playlist'|'channel_id'|'handle', value) for an id, URL, playlist id, channel id or @handle."""
    t = (target or "").strip()
    m = re.search(r"[?&]list=([A-Za-z0-9_-]{10,})", t)
    if m and "v=" not in t:
        return "playlist", m.group(1)
    if re.fullmatch(r"(?:PL|UU|OLAK5uy_|FL|RD)[A-Za-z0-9_-]{10,}", t):
        return "playlist", t
    m = re.search(r"/channel/(UC[A-Za-z0-9_-]{22})", t)
    if m:
        return "channel_id", m.group(1)
    if re.fullmatch(r"UC[A-Za-z0-9_-]{22}", t):
        return "channel_id", t
    m = re.search(r"youtube\.com/(@[A-Za-z0-9_.-]+)", t)
    if m:
        return "handle", m.group(1)
    if t.startswith("@") and re.fullmatch(r"@[A-Za-z0-9_.-]+", t):
        return "handle", t
    if re.search(r"youtube\.com/(?:c|user)/", t):
        return "handle", t
    m = VID_RE.search(t)
    if m:
        return "video", m.group(1)
    return "unknown", t


def channel_url(target):
    k, v = classify(target)
    if k == "handle":
        return v if v.startswith("http") else "https://www.youtube.com/" + v
    if k == "channel_id":
        return "https://www.youtube.com/channel/" + v
    return target


def main(argv):
    cmd = argv[0] if argv else "list"
    if cmd == "refresh":
        live = refresh(force=True)
        for k, v in live.items():
            print(f"{k}: {len(v)} live: {', '.join(v) or '-'}")
        return 0 if any(live.values()) else 1
    for k in ("invidious", "piped"):
        n, tot, hosts = health_summary(k)
        print(f"{k}: {n} of {tot} live (cached): {', '.join(hosts) or '-'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
