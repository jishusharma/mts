"""Screenshot intake: every image the operator shows a session is saved, classified, read and closed here.

  python scripts/dev/shot.py ingest [--inbox DIR]              # land new images (idempotent, sha256 de-duplicated)
  python scripts/dev/shot.py hook                              # Claude Code hook: ingest this session, print a notice
  python scripts/dev/shot.py list [--status pending|new|classified|read|done]
  python scripts/dev/shot.py classify <id> --kind chart|positions|app|other|noise --why "<what it is / what the operator meant>"
                             [--symbol BTCUSDT --tf 15m --at "2026-10-08 02:47" --tz +05:30 --source "binance footprint"]
  python scripts/dev/shot.py read <id>... --extract <md>       # extract exists, names the ids, has claim rows
  python scripts/dev/shot.py done <id>... --outcome finding:B156 | finding:card:<task id> | feature:FEAT-11 | noaction:"<why>" | note:"<text>"
  python scripts/dev/shot.py sets                              # chart shots grouped into multi-timeframe sets
  python scripts/dev/shot.py bundle <set>                      # RU3: one evidence packet per multi-chart set
  python scripts/dev/shot.py engine <id> [--raw DIR] [--plan]  # B160: engine snapshot at the shot's minute (SnapAt, 1m archive)
                                                               #   -> MyTradingSys/research/screenshots/engine/<id>.json
  python scripts/dev/shot.py status [--max-age-hours 24]       # one line; exit 1 when a shot is overdue (the gate)

Why this exists: Claude saves a pasted image in places no session is told about (the session transcript, ~/.claude/uploads,
a Temp folder that is cleaned), and a plain chat keeps it nowhere. This tool lands every image in one store keyed by
sha256, so saving never depends on a session remembering to do it. The store is gitignored (screenshots can show
accounts); the extracts written about them are tracked. Process: MyTradingSys/methodology/screenshot_intake.md.
Store: env MTS_SHOT_DIR, else <main checkout>/runtime_data/screenshots (one store per machine, shared by every worktree).
"""
import json
import os
import re
import struct
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "MyTradingSys" / "observation"))
import capture  # noqa: E402  (time parsing and the timeframe list are shared with the observation channel)
sys.path.insert(0, str(HERE))
import nowin  # noqa: E402

nowin.install()

KINDS = ("chart", "positions", "app", "other", "noise")
PRIVATE_KINDS = ("positions",)
STATUSES = ("new", "classified", "read", "done")
CLAIM_CLASSES = ("MATCH", "MISMATCH", "NOT_IN_DATA")
PRIOR_LINE = re.compile(r"^[\s>*-]*Prior(?::\**|\**:)[ \t]*(\S.*?)\s*$", re.M)  # B157: `Prior: <extract>` / `**Prior:** none`
OUTCOME_ID = re.compile(r"^(B\d{3}|T\d{3}|F-BT-\d+|FEAT-\d+|card:[a-z0-9][a-z0-9-]*)$")   # card: = a task card (tasks.py)
SET_WINDOW_MIN = 10  # chart shots of one symbol within this many minutes are one set (the 2026-10-08 batch spanned 4)
NAG_EVERY_HOURS = 6  # the SessionStart backlog reminder repeats at most this often
MAX_TEXT = 500
EXT_OK = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
ENGINE_SYMBOLS = ("BTCUSDT",)  # SnapAt.java hard-codes BTCUSDT
SNAPAT = REPO / "MyTradingSys" / "research" / "core_readiness_2026-09-27" / "harness" / "java" / "SnapAt.java"
ENGINE_JARS = ("jackson-databind-2.16.0.jar", "jackson-core-2.16.0.jar", "jackson-annotations-2.16.0.jar", "okhttp-4.12.0.jar",
               "okio-jvm-3.6.0.jar", "kotlin-stdlib-1.8.21.jar", "Java-WebSocket-1.5.6.jar", "slf4j-api-2.0.9.jar")  # README_REPLAY.md


class ShotError(ValueError):
    pass


# ---------------------------------------------------------------- locations
def git(*args, cwd=None):
    r = subprocess.run(["git", *args], cwd=cwd or REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def main_root():
    """The primary checkout (the live tree on the desktop): every worktree shares its store."""
    out = git("rev-parse", "--path-format=absolute", "--git-common-dir").strip().splitlines()
    common = out[-1].strip() if out else ""
    if not common or common.startswith("--"):  # git older than 2.31 echoes the flag as line 1 (2.24)
        common = ""
        rel = git("rev-parse", "--git-common-dir").strip()
        common = str((REPO / rel).resolve()) if rel else ""
    p = Path(common) if common else REPO / ".git"
    return p.parent if p.name == ".git" else REPO


def store_dir():
    return Path(os.environ.get("MTS_SHOT_DIR") or main_root() / "runtime_data" / "screenshots")


def claude_home():
    return Path(os.environ.get("MTS_CLAUDE_HOME") or Path.home() / ".claude")


def temp_root():
    if os.environ.get("MTS_SHOT_TEMP"):
        return Path(os.environ["MTS_SHOT_TEMP"])
    for var in ("TMPDIR", "TEMP", "TMP"):      # the first two steps of tempfile.gettempdir(), without importing tempfile (~25 ms)
        if os.environ.get(var) and os.path.isdir(os.environ[var]):
            return Path(os.path.abspath(os.environ[var])) / "claude"
    import tempfile
    return Path(tempfile.gettempdir()) / "claude"


def slug(path):
    return re.sub(r"[^A-Za-z0-9]", "-", str(path))


def family_slugs():
    """Claude project-folder names for this repo's checkouts (every worktree, plus mts-* siblings of deleted ones)."""
    env = os.environ.get("MTS_SHOT_SLUGS")
    if env:
        return [s for s in env.split(",") if s]
    paths = [main_root()]
    for line in git("worktree", "list", "--porcelain").splitlines():
        if line.startswith("worktree "):
            paths.append(Path(line[9:]))
    return sorted({slug(p) for p in paths})


def project_dirs():
    base = claude_home() / "projects"
    if not base.is_dir():
        return []
    slugs = family_slugs()
    sibling = slug(main_root().parent / "mts-")
    return [d for d in sorted(base.iterdir()) if d.is_dir() and (d.name in slugs or d.name.startswith(sibling))]


# ---------------------------------------------------------------- event store
def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def manifest(store):
    return store / "manifest.jsonl"


def append(store, event):
    store.mkdir(parents=True, exist_ok=True)
    line = (json.dumps(event, sort_keys=True) + "\n").encode("utf-8")
    fd = os.open(manifest(store), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        os.write(fd, line)  # one write: concurrent sessions cannot interleave inside a line
    finally:
        os.close(fd)


def load_events(store):
    p = manifest(store)
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def fold(events):
    """Current state per shot from the append-only event log (latest event of each kind wins)."""
    S = {}
    for e in events:
        i, ev = e.get("id"), e.get("event")
        if ev == "landed":
            S.setdefault(i, {**e, "status": "new"})
            continue
        s = S.get(i)
        if s is None:
            continue
        if ev == "classified":
            s.update({k: e[k] for k in ("kind", "why", "symbol", "tf", "at", "source", "zones_marked") if k in e})
            for k in ("symbol", "tf", "at", "source", "zones_marked"):
                if k not in e:
                    s.pop(k, None)
            s["status"] = "done" if e["kind"] == "noise" else "classified"
            if e["kind"] == "noise":
                s["outcome"] = "noaction:noise"
            s.pop("extract", None)
        elif ev == "read":
            s.update(extract=e["extract"], claims=e["claims"], status="read")
            if "claim_rows" in e:
                s["claim_rows"] = e["claim_rows"]
            else:
                s.pop("claim_rows", None)
            if "prior" in e:
                s["prior"] = e["prior"]
            else:
                s.pop("prior", None)
        elif ev == "done":
            s.update(outcome=e["outcome"], status="done")
    return S


def resolve(S, prefix):
    hits = [i for i in S if i.startswith(prefix.lower())]
    if len(prefix) < 6 or len(hits) != 1:
        raise ShotError(f"{prefix!r} matches {len(hits)} shots (need a unique prefix of 6+ characters); see `shot.py list`")
    return hits[0]


# ---------------------------------------------------------------- landing
def sniff(data):
    """(ext, width, height) from the bytes; None when it is not an image."""
    if data[:8] == b"\x89PNG\r\n\x1a\n" and len(data) >= 24:
        w, h = struct.unpack(">II", data[16:24])
        return "png", w, h
    if data[:3] == b"\xff\xd8\xff":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            m = data[i + 1]
            if m in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return "jpg", w, h
            i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
        return "jpg", None, None
    if data[:4] == b"GIF8":
        return "gif", None, None
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp", None, None
    return None


def land(store, data, route, session, ts_seen, src, text=""):
    """Save one image. Returns the new shot's record, or None when these bytes were already landed or are not an image."""
    kind = sniff(data)
    if kind is None:
        return None
    import hashlib
    sha = hashlib.sha256(data).hexdigest()
    sid = sha[:12]
    if sid in fold(load_events(store)):
        return None
    ext, w, h = kind
    img = store / "img"
    img.mkdir(parents=True, exist_ok=True)
    tmp = img / f".{sid}.tmp"
    tmp.write_bytes(data)
    os.replace(tmp, img / f"{sid}.{ext}")
    ev = {"event": "landed", "id": sid, "sha256": sha, "ext": ext, "bytes": len(data), "w": w, "h": h,
          "route": route, "session": session, "ts_seen": ts_seen, "ts_landed": now_iso(), "src": src,
          "operator_text": re.sub(r"\s+", " ", text or "").strip()[:MAX_TEXT]}
    append(store, ev)
    return ev


def user_text(rec):
    c = (rec.get("message") or {}).get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return " ".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
    return ""


def ingest_transcript(store, path, cursors):
    """Operator pastes: user records whose own content carries image blocks. Tool-result screenshots are not pastes."""
    import base64
    path = Path(path)
    if not path.is_file():
        return []
    key = str(path)
    size = path.stat().st_size
    off = cursors.get(key, 0)
    if off > size:
        off = 0
    if off == size:
        return []
    new = []
    with open(path, "rb") as f:
        f.seek(off)
        buf = f.read()
    end = buf.rfind(b"\n") + 1  # only complete lines; a record still being written is picked up next time
    for raw in buf[:end].splitlines():
        if b'"image"' not in raw:
            continue
        try:
            rec = json.loads(raw)
        except ValueError:
            continue
        if rec.get("type") != "user":
            continue
        c = (rec.get("message") or {}).get("content")
        if not isinstance(c, list):
            continue
        for b in c:
            if isinstance(b, dict) and b.get("type") == "image" and (b.get("source") or {}).get("type") == "base64":
                try:
                    data = base64.b64decode(b["source"]["data"])
                except Exception:
                    continue
                r = land(store, data, "paste", rec.get("sessionId") or path.stem, rec.get("timestamp"),
                         f"transcript:{path.name}", user_text(rec))
                if r:
                    new.append(r)
    cursors[key] = off + end
    return new


def text_mentioning(transcript, name):
    """The operator words of the prompt that referenced an uploaded file by name (project-thread attachments)."""
    try:
        for line in Path(transcript).read_text(encoding="utf-8").splitlines():
            if name in line and '"type":"user"' in line.replace(" ", ""):
                rec = json.loads(line)
                t = re.sub(r"<[^>]+>", " ", user_text(rec))
                t = re.sub(r'@"[^"]*"', " ", t)           # the attachment path the app prepends
                return re.sub(r"\[Local:[^\]]*\]", " ", t)  # the app's working-folder tag
    except (OSError, ValueError):
        pass
    return ""


def ingest_dir(store, d, route, session, transcript=None):
    new = []
    if not d.is_dir():
        return new
    for f in sorted(d.iterdir()):
        if f.suffix.lower() not in EXT_OK or not f.is_file():
            continue
        try:
            data = f.read_bytes()
        except OSError:
            continue
        ts = datetime.fromtimestamp(f.stat().st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if sha_known(store, data):
            continue
        text = text_mentioning(transcript, f.name) if transcript else ""
        r = land(store, data, route, session, ts, str(f), text)
        if r:
            new.append(r)
    return new


def sha_known(store, data):
    import hashlib
    return hashlib.sha256(data).hexdigest()[:12] in fold(load_events(store))


def load_cursors(store):
    try:
        return json.loads((store / "cursors.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_cursors(store, cur):
    store.mkdir(parents=True, exist_ok=True)
    tmp = store / ".cursors.tmp"
    tmp.write_text(json.dumps(cur), encoding="utf-8", newline="\n")
    os.replace(tmp, store / "cursors.json")


def ingest_session(store, session, transcript, project_slug=None):
    cur = load_cursors(store)
    new = []
    if transcript:
        new += ingest_transcript(store, transcript, cur)
    new += ingest_dir(store, claude_home() / "uploads" / session, "upload", session, transcript)
    slugs = [project_slug] if project_slug else family_slugs()
    for sl in slugs:
        new += ingest_dir(store, temp_root() / sl / session / "images", "temp", session)
    save_cursors(store, cur)
    return new


def ingest_all(store, inbox=None):
    cur = load_cursors(store)
    new, sessions = [], {}
    for pd in project_dirs():
        for t in sorted(pd.glob("*.jsonl")):
            sessions[t.stem] = t
            new += ingest_transcript(store, t, cur)
    up = claude_home() / "uploads"
    if up.is_dir():
        for d in sorted(up.iterdir()):
            if d.name in sessions:  # only sessions of this repo; uploads are shared with every other project
                new += ingest_dir(store, d, "upload", d.name, sessions[d.name])
    for sl in family_slugs():
        base = temp_root() / sl
        if base.is_dir():
            for sd in sorted(base.iterdir()):
                new += ingest_dir(store, sd / "images", "temp", sd.name)
    inbox = Path(inbox) if inbox else store / "inbox"
    new += ingest_dir(store, inbox, "inbox", "operator-inbox")
    save_cursors(store, cur)
    return new


# ---------------------------------------------------------------- actions
def classify(store, prefix, kind, why, symbol=None, tf=None, at=None, tz=None, source=None, zones_marked=False):
    S = fold(load_events(store))
    i = resolve(S, prefix)
    if kind not in KINDS:
        raise ShotError(f"kind must be one of {KINDS}")
    if not why or len(why.strip()) < 8:
        raise ShotError("--why is required: one line saying what this is and what the operator meant (8+ characters)")
    ev = {"event": "classified", "id": i, "ts": now_iso(), "kind": kind, "why": why.strip()}
    if kind == "chart":
        missing = [n for n, v in (("--symbol", symbol), ("--tf", tf), ("--at", at), ("--source", source)) if not v]
        if missing:
            raise ShotError("a chart needs " + ", ".join(missing) + " (the time on the chart's right edge, with --tz for a naive time)")
        if tf not in capture.TF_MINUTES:
            raise ShotError(f"--tf must be one of {tuple(capture.TF_MINUTES)}")
        try:
            ev["at"] = capture.iso(capture.parse_time(at, tz))
        except capture.ObsError as e:
            raise ShotError(str(e))
        ev.update(symbol=symbol.upper(), tf=tf, source=source)
        if zones_marked:
            ev["zones_marked"] = True
    append(store, ev)
    return i


def read_extract(store, prefixes, extract):
    S = fold(load_events(store))
    ids = [resolve(S, p) for p in prefixes]
    for i in ids:
        if S[i].get("status") not in ("classified", "read", "done"):
            raise ShotError(f"{i} is still 'new': classify it first")
    path = Path(extract)
    if not path.is_absolute():
        path = Path.cwd() / path
    if not path.is_file():
        raise ShotError(f"extract not found: {extract}")
    text = path.read_text(encoding="utf-8")
    absent = [i for i in ids if i not in text]
    if absent:
        raise ShotError(f"the extract must name each shot id it covers; missing: {', '.join(absent)}")
    rows = parse_claim_rows(text)
    counts = {c: 0 for c in CLAIM_CLASSES}
    for r in rows:
        counts[r["class"]] += 1
    is_chart = any(S[i].get("kind") == "chart" for i in ids)
    if is_chart and not sum(counts.values()):
        raise ShotError("a chart extract needs claim rows: | id | MATCH or MISMATCH or NOT_IN_DATA | chart claim | data check |")
    prior = carried_context(text, path) if is_chart else (None, [])
    ev_extra = {"prior": repo_rel(prior[0])} if prior[0] else {}
    for i in ids:
        append(store, {"event": "read", "id": i, "ts": now_iso(), "extract": repo_rel(path), "claims": counts, "claim_rows": rows, **ev_extra})
    return ids, counts, prior


CLAIM_ID = re.compile(r"[A-Za-z0-9_.-]+")


def parse_claim_rows(text):
    """B159: every `| id | MATCH or MISMATCH or NOT_IN_DATA | chart claim | data check |` row as a dict
    {id, class, claim, evidence}; the manifest keeps the rows, not only their counts. A row whose second cell names a class
    loosely (`Match`, `NOT IN DATA`) or that lacks an id, claim or evidence is refused with its line number: it would
    otherwise drop out of the count unseen."""
    rows = []
    for n, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in (s[1:-1] if s.endswith("|") else s[1:]).split("|")]
        if len(cells) < 2 or re.sub(r"[\s-]+", "_", cells[1]).upper() not in CLAIM_CLASSES:
            continue  # header, separator, outcome table: not a claim row
        cls = cells[1]
        if cls not in CLAIM_CLASSES:
            raise ShotError(f"line {n}: claim class `{cls}` must be exactly one of {', '.join(CLAIM_CLASSES)}")
        evidence = " | ".join(cells[3:]).strip(" |")
        if len(cells) < 4 or not CLAIM_ID.fullmatch(cells[0]) or not cells[2] or not evidence:
            raise ShotError(f"line {n}: a claim row is | id | {cls} | chart claim | data check |, all four filled: {s[:80]}")
        rows.append({"id": cells[0], "class": cls, "claim": cells[2], "evidence": evidence})
    return rows


def repo_rel(path):
    try:
        rel = str(Path(path).resolve().relative_to(REPO))
    except ValueError:
        rel = str(path)
    return rel.replace("\\", "/")


def carried_context(text, path):
    """B157: a chart read must say which read came before it (`Prior: <extract>` or `Prior: none`), so it starts from
    that read's context instead of cold. Returns (prior path or None, the prior read's Invalidation/Falsify lines),
    which the new read scores HELD / BROKEN / UNTESTED against the new chart."""
    m = PRIOR_LINE.search(text)
    if not m:
        raise ShotError("a chart extract needs a `Prior:` line: the previous read's extract path, or `Prior: none` (B157)")
    value = m.group(1).strip().strip("`")
    if value.lower() == "none":
        return None, []
    cand = Path(value)
    tries = [cand] if cand.is_absolute() else [REPO / cand, path.parent / cand, Path.cwd() / cand]
    found = next((t for t in tries if t.is_file()), None)
    if found is None:
        raise ShotError(f"Prior extract not found: {value}")
    if found.resolve() == path.resolve():
        raise ShotError("Prior must name the previous read, not this extract")
    lines = []
    for line in found.read_text(encoding="utf-8").splitlines():
        s = line.strip().lstrip("-*> ").strip()
        if s.lower().startswith(("invalidation", "falsify")):
            lines.append(s)
    return found, lines


def parse_falsifier_spec(line):
    """Parse a falsifier line into a price-level spec or None.
    Supported:
      - range: outside <lo>-<hi> -> ('range', lo, hi)
      - under/below: acceptance under/below <lvl> -> ('under', lvl)
      - above/over: acceptance above/over <lvl> -> ('above', lvl)
    """
    text = re.sub(r"^[\s\-*>]*", "", line).strip()
    text = re.sub(r"^(?:invalidation|falsify)\s*:\s*", "", text, flags=re.I).strip()
    m_range = re.search(r"outside\s+(?:[^\d]+)?(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:-|–|\.\.|to)\s*(\d+(?:,\d+)*(?:\.\d+)?)", text, re.I)
    if m_range:
        lo = float(m_range.group(1).replace(",", ""))
        hi = float(m_range.group(2).replace(",", ""))
        if lo > hi:
            lo, hi = hi, lo
        return ("range", lo, hi)
    m_under = re.search(r"(?:under|below)\s+(?:[^\d~]*~?\s*)?(\d+(?:,\d+)*(?:\.\d+)?)", text, re.I)
    if m_under:
        return ("under", float(m_under.group(1).replace(",", "")))
    m_above = re.search(r"(?:above|over)\s+(?:[^\d~]*~?\s*)?(\d+(?:,\d+)*(?:\.\d+)?)", text, re.I)
    if m_above:
        return ("above", float(m_above.group(1).replace(",", "")))
    return None


def bar_ohlc(b):
    if isinstance(b, dict):
        h = b.get("h", b.get("high"))
        l = b.get("l", b.get("low"))
        c = b.get("c", b.get("close"))
        o = b.get("o", b.get("open", c))
        return float(o), float(h), float(l), float(c)
    elif isinstance(b, (list, tuple)):
        if len(b) >= 5:
            return float(b[1]), float(b[2]), float(b[3]), float(b[4])
        elif len(b) == 4:
            return float(b[0]), float(b[1]), float(b[2]), float(b[3])
    raise ValueError(f"Unrecognized kline format: {b}")


def falsifier_status(line, klines_since):
    """B157 / T092 gap: compute carried falsifier lines (HELD/BROKEN/UNTESTED) from klines.
    Step 2: function falsifier_status(line, klines_since) returns HELD|BROKEN|UNTESTED for price-level lines.
    - BROKEN: level broken by a bar close
    - HELD: level tested/reached by high/low but all closes held
    - UNTESTED: level not yet reached, or non-price line, or no klines
    """
    spec = parse_falsifier_spec(line)
    if spec is None or not klines_since:
        return "UNTESTED"
    kind = spec[0]
    if kind == "range":
        lo, hi = spec[1], spec[2]
        reached = False
        for b in klines_since:
            _, h, l, c = bar_ohlc(b)
            if c < lo or c > hi:
                return "BROKEN"
            if l <= lo or h >= hi:
                reached = True
        return "HELD" if reached else "UNTESTED"
    elif kind == "under":
        lvl = spec[1]
        reached = False
        for b in klines_since:
            _, h, l, c = bar_ohlc(b)
            if c < lvl:
                return "BROKEN"
            if l <= lvl:
                reached = True
        return "HELD" if reached else "UNTESTED"
    elif kind == "above":
        lvl = spec[1]
        reached = False
        for b in klines_since:
            _, h, l, c = bar_ohlc(b)
            if c > lvl:
                return "BROKEN"
            if h >= lvl:
                reached = True
        return "HELD" if reached else "UNTESTED"
    return "UNTESTED"


def load_klines_since(store, ids, prior, klines_path=None):
    """Load klines between prior extract and current read instant for falsifier evaluation."""
    if klines_path:
        kp = Path(klines_path)
        if kp.is_file():
            try:
                data = json.loads(kp.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    return data
            except (OSError, ValueError):
                pass
        return []
    for env_key in ("MTS_KLINES_PATH", "MTS_KLINES_DIR"):
        p = os.environ.get(env_key)
        if p and Path(p).is_file():
            try:
                data = json.loads(Path(p).read_text(encoding="utf-8"))
                if isinstance(data, list):
                    return data
            except (OSError, ValueError):
                pass
    return []


def outcome_exists(token):
    """A filed outcome must really be filed: B/T ids are rows of the registry, card:<id> is a task card file
    (MyTradingSys/system/tasks/<id>.json, the live channel; it shows under its layer in LAYERS.md), F-BT / FEAT ids appear
    in a markdown doc. (A bare grep would let a test file or a code comment 'file' the item.)"""
    if os.environ.get("MTS_SHOT_SKIP_REPO_CHECK"):
        return True
    if token.startswith("card:"):
        return (REPO / "MyTradingSys" / "system" / "tasks" / f"{token[5:]}.json").is_file()
    if re.fullmatch(r"[BT]\d{3}", token):
        bugs = REPO / "MyTradingSys" / "research" / "BUGS.md"
        return bugs.is_file() and re.search(rf"^\|\s*{re.escape(token)}\s*\|", bugs.read_text(encoding="utf-8"), re.M) is not None
    return bool(git("grep", "--untracked", "-l", "-w", "-F", "-e", token, "--", "*.md").strip())   # -w: FEAT-1 is not FEAT-11 (RV07)


def done(store, prefixes, outcome):
    S = fold(load_events(store))
    ids = [resolve(S, p) for p in prefixes]
    kind, _, rest = outcome.partition(":")
    rest = rest.strip()
    if kind in ("finding", "feature"):
        if not OUTCOME_ID.match(rest):
            raise ShotError(f"{kind}: needs an item id such as B156, T070, F-BT-23, FEAT-11 or card:<task card id>")
        if not outcome_exists(rest):
            raise ShotError(f"{rest} is not in the repo yet: file it first, then close the shot")
    elif kind in ("noaction", "note"):
        if len(rest) < 8:
            raise ShotError(f"{kind}: needs a reason of 8+ characters")
    else:
        raise ShotError("--outcome must start with finding:, feature:, noaction: or note:")
    for i in ids:
        s = S[i]
        if s["status"] == "new":
            raise ShotError(f"{i} is still 'new': classify it first")
        if s.get("kind") == "chart" and s["status"] != "read" and s["status"] != "done":
            raise ShotError(f"{i} is a chart that has not been read: write the extract and run `shot.py read` first")
        if (s.get("claims") or {}).get("MISMATCH"):   # a MISMATCH is a B-item or an explained noaction (screenshot_intake.md)
            if kind in ("note", "feature") or (kind == "noaction" and len(rest) < 20):
                raise ShotError(f"{i} has MISMATCH claims: file them (finding:) or explain in 20+ characters (noaction:) why not")
    for i in ids:
        append(store, {"event": "done", "id": i, "ts": now_iso(), "outcome": outcome})
    return ids


# ---------------------------------------------------------------- engine state at the shot (B160)
def raw_root():
    """The 1m kline archive ArchiveHistoricalSource reads (<raw>/klines/SYMBOL-1m-*.csv); refresh_klines.py tops it up daily."""
    return Path(os.environ.get("MTS_KLINE_RAW") or main_root() / "Dumps" / "backtest" / "raw")


def engine_dir():
    return Path(os.environ.get("MTS_SHOT_ENGINE_DIR") or REPO / "MyTradingSys" / "research" / "screenshots" / "engine")


def floor_minute(at):
    t = datetime.fromisoformat(at.replace("Z", "+00:00")).astimezone(timezone.utc)
    return t.replace(second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def archive_covers(raw, symbol, day):
    """True when <raw>/klines holds the monthly (SYMBOL-1m-YYYY-MM.csv) or daily (SYMBOL-1m-YYYY-MM-DD.csv) file for `day`."""
    d = Path(raw) / "klines"
    names = {f"{symbol}-1m-{day[:7]}.csv", f"{symbol}-1m-{day}.csv"}
    return d.is_dir() and any((d / n).is_file() for n in names)


def engine_plan(store, prefix, raw=None):
    """What `shot.py engine` would replay: refuses anything but a classified chart with a time on a symbol SnapAt serves,
    and an archive without the shot's day (a snapshot from a short archive would be silently wrong)."""
    S = fold(load_events(store))
    i = resolve(S, prefix)
    s = S[i]
    if s.get("kind") != "chart":
        raise ShotError(f"{i} is not a classified chart (kind {s.get('kind')!r}): only a chart has an instant to replay")
    if not s.get("at"):
        raise ShotError(f"{i} has no `at`: re-classify it with --at (the time on the chart's right edge)")
    if s.get("symbol") not in ENGINE_SYMBOLS:
        raise ShotError(f"{i} is {s.get('symbol')}: SnapAt replays {', '.join(ENGINE_SYMBOLS)} only")
    as_of = floor_minute(s["at"])
    raw = Path(raw) if raw else raw_root()
    if not archive_covers(raw, s["symbol"], as_of[:10]):
        raise ShotError(f"the 1m archive {raw / 'klines'} has no {s['symbol']} file for {as_of[:10]}: top it up "
                        "(scripts/dev/refresh_klines.py, or fetch_binance_archive.py --start/--end) or pass --raw")
    return {"id": i, "symbol": s["symbol"], "tf": s.get("tf"), "at": s["at"], "as_of": as_of, "raw": str(raw),
            "out": str(engine_dir() / f"{i}.json")}


def write_instants(plan, d):
    p = Path(d) / "instants.txt"
    p.write_text(plan["as_of"] + "\n", encoding="utf-8", newline="\n")
    return p


def engine_jars():
    m2 = Path(os.environ.get("MTS_M2") or Path.home() / ".m2" / "repository")
    jars = []
    for name in ENGINE_JARS:
        hits = sorted(m2.rglob(name)) if m2.is_dir() else []
        if not hits and m2.is_dir() and name.startswith("slf4j-api-"):  # logging API only: any 2.x jar compiles the engine (JIS-NUC has 2.0.6)
            hits = sorted(m2.rglob("slf4j-api-2.*.jar"), reverse=True)
        if not hits:
            raise ShotError(f"{name} not found under {m2}: run `mvn -q -o compile` once in a worktree so Maven fetches it")
        jars.append(str(hits[0]))
    return jars


def run_engine(plan, runner=subprocess.run):
    """Compile src/main + SnapAt into a temp copy (never src/ or target/), run it from an empty cwd, save one record."""
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="mts_snapat_"))
    try:
        src, out, cwd = tmp / "src", tmp / "out", tmp / "cwd"
        for d in (src, out, cwd):
            d.mkdir()
        for f in sorted((REPO / "src" / "main" / "java" / "datafeed").glob("*.java")) + [SNAPAT]:
            shutil.copy2(f, src / f.name)
        cp = os.pathsep.join(engine_jars())
        r = runner(["javac", "-nowarn", "-encoding", "UTF-8", "-d", str(out), "-cp", cp, *sorted(str(f) for f in src.glob("*.java"))],
                   capture_output=True, text=True)
        if r.returncode:
            raise ShotError("javac failed: " + (r.stderr or r.stdout or "")[-800:])
        inst, jsonl = write_instants(plan, tmp), tmp / "snap.jsonl"
        r = runner(["java", "-Xmx3g", "-cp", str(out) + os.pathsep + cp, "datafeed.SnapAt", plan["raw"], str(inst), str(jsonl)],
                   cwd=str(cwd), capture_output=True, text=True)
        if r.returncode:
            raise ShotError("SnapAt failed: " + (r.stderr or r.stdout or "")[-800:])
        lines = [ln for ln in (jsonl.read_text(encoding="utf-8").splitlines() if jsonl.is_file() else []) if ln.strip()]
        snap = json.loads(lines[0]) if len(lines) == 1 else None
        if not isinstance(snap, dict):
            raise ShotError(f"SnapAt returned {len(lines)} line(s) and no snapshot object for {plan['as_of']}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    rec = {"shot": plan["id"], "symbol": plan["symbol"], "tf": plan["tf"], "at": plan["at"], "as_of": plan["as_of"],
           "raw": plan["raw"], "engine": "SnapAt: MarketDataSnapshot(raw archive).fetchHistoricalSnapshot",
           "git_head": git("rev-parse", "HEAD").strip(), "snapshot": snap}
    path = Path(plan["out"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return path


# ---------------------------------------------------------------- views
def age_hours(ts):
    try:
        return (datetime.now(timezone.utc) - datetime.fromisoformat(ts.replace("Z", "+00:00"))).total_seconds() / 3600
    except (TypeError, ValueError):
        return 0.0


def pending(S):
    return [s for s in S.values() if s["status"] != "done"]


def make_sets(S, window_min=SET_WINDOW_MIN):
    charts = sorted((s for s in S.values() if s.get("kind") == "chart" and s.get("at")), key=lambda s: (s["symbol"], s["at"]))
    sets, cur = [], []
    for s in charts:
        if cur and (s["symbol"] != cur[-1]["symbol"] or
                    (datetime.fromisoformat(s["at"].replace("Z", "+00:00")) -
                     datetime.fromisoformat(cur[-1]["at"].replace("Z", "+00:00"))) > timedelta(minutes=window_min)):
            sets.append(cur)
            cur = []
        cur.append(s)
    if cur:
        sets.append(cur)
    out = []
    for grp in sets:
        tfs = sorted({s["tf"] for s in grp}, key=lambda t: capture.TF_MINUTES[t])
        out.append({"set": grp[0]["id"][:6], "symbol": grp[0]["symbol"], "from": grp[0]["at"], "to": grp[-1]["at"],
                    "tfs": tfs, "ids": [s["id"] for s in grp], "single_tf": len(tfs) < 2,
                    "status": min((s["status"] for s in grp), key=STATUSES.index)})
    return out


def find_set(S, prefix):
    sets = make_sets(S)
    p = prefix.strip()
    for s in sets:
        if s["set"] == p or s["set"].startswith(p) or p.startswith(s["set"]):
            return s
        if any(i == p or i.startswith(p) for i in s["ids"]):
            return s
    raise ShotError(f"set '{prefix}' not found (run `shot.py sets` to list sets)")


def find_previous_read(S, before_at=None):
    candidates = []
    for s in S.values():
        if s.get("status") in ("read", "done") and s.get("extract"):
            t = s.get("at") or s.get("ts_seen") or s.get("ts_landed") or ""
            if before_at and t and t >= before_at:
                continue
            candidates.append((t, s))
    if not candidates:
        return None, None, []
    candidates.sort(key=lambda x: x[0], reverse=True)
    prev_shot = candidates[0][1]
    ext = prev_shot.get("extract")
    falsifiers = []
    if ext:
        p = Path(ext)
        tries = [p] if p.is_absolute() else [REPO / p, Path.cwd() / p]
        found = next((t for t in tries if t.is_file()), None)
        if found:
            try:
                for line in found.read_text(encoding="utf-8").splitlines():
                    st = line.strip().lstrip("-*> ").strip()
                    if st.lower().startswith(("invalidation", "falsify")):
                        falsifiers.append(st)
            except OSError:
                pass
    return prev_shot, ext, falsifiers


def find_open_mismatches(S):
    open_mm = []
    for s in sorted(S.values(), key=lambda x: x.get("at") or x.get("ts_seen") or ""):
        if s.get("status") != "done":
            claims = s.get("claims") or {}
            if claims.get("MISMATCH", 0) > 0:
                rows = [r for r in s.get("claim_rows", []) if r.get("class") == "MISMATCH"]
                open_mm.append({
                    "id": s["id"],
                    "extract": s.get("extract"),
                    "mismatch_count": claims["MISMATCH"],
                    "claim_rows": rows
                })
    return open_mm


def get_mirror_info():
    try:
        import live_mirror
        base = Path(REPO) / live_mirror.MIRROR_DIR
        mf = base / "manifest.json"
        if not mf.is_file():
            return {
                "status": "NO_MIRROR", "tag": "none", "age_min": None, "lag_min": None, "flags": [], "stale": True,
                "lines": ["NO MIRROR: run `python scripts/dev/live_mirror.py pull` (never read the old git snapshot as live)"]
            }
        m = json.loads(mf.read_text(encoding="utf-8"))
        pub = datetime.fromisoformat(m["utc"].replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        age = (now - pub).total_seconds() / 60
        snaps = [f for f in m.get("files", []) if f.get("rel", "").startswith("runtime_data/snapshots/")]
        lag = None
        if snaps:
            newest = max(datetime.fromisoformat(f["mtime"].replace("Z", "+00:00")) for f in snaps)
            lag = (pub - newest).total_seconds() / 60
        stale = (age > live_mirror.STALE_MIN) or (lag is not None and lag > live_mirror.STALE_MIN)
        warn = (age > live_mirror.WARN_MIN) or (lag is not None and lag > live_mirror.WARN_MIN)
        status = "STALE" if stale else ("WARN" if warn else "OK")
        tag = f"mirror@{pub.strftime('%Y-%m-%d %H:%MZ')}"
        lines = live_mirror.brief_lines(REPO, now)
        return {
            "status": status, "tag": tag, "age_min": age, "lag_min": lag,
            "flags": [k for k, v in m.get("flags", {}).items() if v],
            "stale": stale, "lines": lines
        }
    except Exception as e:
        return {
            "status": "ERROR", "tag": "none", "age_min": None, "lag_min": None, "flags": [], "stale": True,
            "lines": [f"Mirror error: {e}"]
        }


def bundle(store, set_prefix):
    S = fold(load_events(store))
    st = find_set(S, set_prefix)
    shots = [S[i] for i in st["ids"]]
    edir = engine_dir()
    engine_snaps = {}
    for sid in st["ids"]:
        ef = edir / f"{sid}.json"
        if ef.is_file():
            try:
                engine_snaps[sid] = json.loads(ef.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                engine_snaps[sid] = None
        else:
            engine_snaps[sid] = None
    prev_shot, prev_extract, prev_falsifiers = find_previous_read(S, st.get("from"))
    open_mm = find_open_mismatches(S)
    mirror = get_mirror_info()
    return {
        "set": st,
        "shots": shots,
        "engine_snapshots": engine_snaps,
        "previous_read": {
            "shot_id": prev_shot["id"] if prev_shot else None,
            "extract": prev_extract,
            "falsifiers": prev_falsifiers
        },
        "open_mismatches": open_mm,
        "mirror": mirror,
    }


def format_bundle(packet):
    st = packet["set"]
    mirror = packet["mirror"]
    lines = []
    lines.append("=" * 70)
    lines.append(f"EVIDENCE PACKET: SET {st['set']} ({st['symbol']} {','.join(st['tfs'])})")
    lines.append("=" * 70)
    lines.append(f"Window: {st['from']} .. {st['to']} | Status: {st['status']} | Shots: {len(st['ids'])}")
    lines.append("")
    lines.append("1. CLASSIFICATION & SHOTS:")
    for s in packet["shots"]:
        lines.append(f"  - {s['id'][:12]} [{s.get('tf', '-')}] {s.get('at', '-')} via {s.get('source', '-')} | {s.get('why', '-')}")
    lines.append("")
    lines.append("2. ENGINE SNAPSHOTS (SnapAt):")
    for sid in st["ids"]:
        snap = packet["engine_snapshots"].get(sid)
        if snap and snap.get("snapshot"):
            sp = snap["snapshot"]
            lines.append(f"  Shot {sid[:12]}: as_of={snap.get('as_of')}")
            key_items = [f"{k}={v}" for k, v in sp.items() if isinstance(v, (int, float, str, bool))][:10]
            lines.append("    " + "; ".join(key_items))
        else:
            lines.append(f"  Shot {sid[:12]}: none (run `shot.py engine {sid[:8]}` to generate)")
    lines.append("")
    lines.append("3. PREVIOUS READ CONTEXT:")
    pr = packet["previous_read"]
    if pr["extract"]:
        lines.append(f"  Prior Extract: {pr['extract']} (shot {str(pr['shot_id'])[:12]})")
        if pr["falsifiers"]:
            lines.append("  Carried Falsifiers to test:")
            for f in pr["falsifiers"]:
                lines.append(f"    - {f}")
    else:
        lines.append("  Prior: none")
    lines.append("")
    lines.append("4. OPEN MISMATCHES:")
    if packet["open_mismatches"]:
        for mm in packet["open_mismatches"]:
            lines.append(f"  - Shot {mm['id'][:12]}: {mm['mismatch_count']} open MISMATCH claim(s) in {mm['extract'] or 'unlinked'}")
            for r in mm["claim_rows"]:
                lines.append(f"      [{r.get('id', '-')}] Claim: {r.get('claim', '-')} | Data: {r.get('evidence', '-')}")
    else:
        lines.append("  none")
    lines.append("")
    lines.append("5. LIVE MIRROR STATUS:")
    if mirror["stale"]:
        lines.append(f"  [FLAGGED] MIRROR IS STALE ({mirror['status']}): do NOT present these numbers as live")
        for l in mirror["lines"]:
            lines.append(f"    {l}")
        lines.append("  NOTICE: Stale mirror is flagged and NOT used for live data claims.")
    else:
        lines.append(f"  {mirror['tag']} [{mirror['status']}]: fresh mirror available")
        for l in mirror["lines"]:
            lines.append(f"    {l}")
    lines.append("")
    lines.append("6. EXTRACT STUB:")
    prior_val = pr["extract"] if pr["extract"] else "none"
    mirror_val = mirror["tag"] if not mirror["stale"] else f"{mirror['tag']} (STALE - FLAGGED)"
    lines.append("```markdown")
    lines.append(f"# Extract: SET {st['set']} ({st['symbol']} {','.join(st['tfs'])})")
    lines.append(f"Prior: {prior_val}")
    lines.append(f"Mirror: {mirror_val}")
    lines.append("")
    lines.append("| id | class | chart claim | data check |")
    for s in packet["shots"]:
        lines.append(f"| {s['id']} | MATCH | <chart claim> | <data check> |")
        lines.append(f"| {s['id']} | MISMATCH | <chart claim> | <data check> |")
    lines.append("```")
    return "\n".join(lines)



def status_line(S, max_age_hours=24):
    c = {k: 0 for k in STATUSES}
    for s in S.values():
        c[s["status"]] += 1
    overdue = [s for s in pending(S) if age_hours(s.get("ts_seen") or s.get("ts_landed")) > max_age_hours]
    claims = {k: 0 for k in CLAIM_CLASSES}
    for s in S.values():
        for k, v in (s.get("claims") or {}).items():
            claims[k] += v
    findings = sum(1 for s in S.values() if str(s.get("outcome", "")).startswith(("finding:", "feature:")))
    line = (f"SHOTS landed {len(S)}: new {c['new']}, classified {c['classified']}, read {c['read']}, done {c['done']}"
            f" | overdue(>{max_age_hours}h) {len(overdue)} | claims MATCH {claims['MATCH']} MISMATCH {claims['MISMATCH']}"
            f" NOT_IN_DATA {claims['NOT_IN_DATA']} | filed {findings}")
    return line, overdue


def notice(new, backlog):
    """What a session is told. Short on purpose: it lands in every prompt that follows a paste."""
    lines = []
    if new:
        lines.append(f"[SCREENSHOT INTAKE] {len(new)} image(s) from this session are now SAVED (sha256 store, survives Temp cleanup):")
        for e in new:
            wh = f"{e['w']}x{e['h']}" if e.get("w") else e["ext"]
            lines.append(f"  {e['id']} {wh} via {e['route']}" + (f' | operator: "{e["operator_text"][:140]}"' if e.get("operator_text") else ""))
        lines.append("Before you answer from them: python scripts/dev/shot.py classify <id> --kind chart|positions|app|other|noise --why \"<what it is, what the operator meant>\""
                     " (chart also needs --symbol --tf --at [--tz] --source). Reading, claim classes and outcomes: MyTradingSys/methodology/screenshot_intake.md."
                     " No shot may stay 'new' at session end.")
    elif backlog:
        lines.append(f"[SCREENSHOT INTAKE] {len(backlog)} saved screenshot(s) are not closed yet (oldest {max(age_hours(s.get('ts_seen') or s.get('ts_landed')) for s in backlog) / 24:.1f} d):"
                     f" {', '.join(s['id'][:8] for s in backlog[:6])}. `python scripts/dev/shot.py list --status pending`")
    return "\n".join(lines)


def hook():
    """Claude Code hook (SessionStart / UserPromptSubmit). Never blocks, never raises: a broken hook must not break a prompt."""
    store = store_dir()
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", "replace") if not sys.stdin.isatty() else ""
        payload = json.loads(raw) if raw.strip() else {}
        sid = payload.get("session_id")
        new = ingest_session(store, sid, payload.get("transcript_path"), slug(payload["cwd"]) if payload.get("cwd") else None) if sid else []
        backlog = []
        if payload.get("hook_event_name") == "SessionStart":
            cur = load_cursors(store)
            if age_hours(cur.get("_nag")) >= NAG_EVERY_HOURS if cur.get("_nag") else True:  # an unclosed backlog is true in every session; say it once in a while, not always
                backlog = pending(fold(load_events(store)))
                if backlog:
                    cur["_nag"] = now_iso()
                    save_cursors(store, cur)
        text = notice(new, backlog)
        if text:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")
            print(text)
    except Exception:
        try:
            import traceback    # only on failure
            store.mkdir(parents=True, exist_ok=True)
            with open(store / "hook_errors.log", "a", encoding="utf-8") as f:
                f.write(now_iso() + "\n" + traceback.format_exc() + "\n")
        except Exception:
            pass
    return 0


def fmt(s):
    base = f"{s['id']} {s['status']:<10} {s.get('kind', '-'):<9}"
    if s.get("kind") == "chart":
        base += f" {s['symbol']} {s['tf']:<4} {s['at']}"
    else:
        base += " " * 27
    return base + f" | {s.get('why') or s.get('operator_text', '')[:80]}"


def main(argv=None):
    if (sys.argv[1:] if argv is None else list(argv)) == ["hook"]:
        return hook()       # fast path: building the argparse tree costs ~0.1 s on every prompt
    import argparse
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("ingest"); a.add_argument("--inbox", help="also land images dropped in this folder (default <store>/inbox)")
    sub.add_parser("hook")
    a = sub.add_parser("list"); a.add_argument("--status", choices=STATUSES + ("pending",))
    a = sub.add_parser("show"); a.add_argument("id")
    a = sub.add_parser("classify"); a.add_argument("id"); a.add_argument("--kind", required=True, choices=KINDS)
    a.add_argument("--why", required=True); a.add_argument("--symbol"); a.add_argument("--tf"); a.add_argument("--at")
    a.add_argument("--tz"); a.add_argument("--source"); a.add_argument("--zones-marked", action="store_true")
    a = sub.add_parser("read"); a.add_argument("ids", nargs="+"); a.add_argument("--extract", required=True)
    a.add_argument("--klines", help="klines json file to score carried falsifiers against")
    a = sub.add_parser("done"); a.add_argument("ids", nargs="+"); a.add_argument("--outcome", required=True)
    sub.add_parser("sets")
    a = sub.add_parser("bundle"); a.add_argument("set"); a.add_argument("--json", action="store_true")
    a = sub.add_parser("engine"); a.add_argument("id"); a.add_argument("--raw", help="1m archive root (default <main>/Dumps/backtest/raw)")
    a.add_argument("--plan", action="store_true", help="print the instant and paths, do not compile or run")
    a = sub.add_parser("status"); a.add_argument("--max-age-hours", type=float, default=24)
    args = p.parse_args(argv)
    if args.cmd == "hook":
        return hook()
    store = store_dir()
    try:
        if args.cmd == "ingest":
            new = ingest_all(store, args.inbox)  # cursors make repeat runs cheap
            for e in new:
                size = f"{e['w']}x{e['h']}" if e.get("w") else e["ext"]
                print(f"LANDED {e['id']} {e['route']} {size} {e['ts_seen']} session {str(e['session'])[:8]}")
            print(f"OK {len(new)} new, store {store}")
        elif args.cmd == "list":
            S = fold(load_events(store))
            rows = pending(S) if args.status == "pending" else [s for s in S.values() if not args.status or s["status"] == args.status]
            for s in sorted(rows, key=lambda s: s.get("ts_seen") or ""):
                print(fmt(s))
        elif args.cmd == "show":
            S = fold(load_events(store)); i = resolve(S, args.id)
            print(json.dumps({**S[i], "file": str(store / "img" / f"{i}.{S[i]['ext']}")}, indent=1, sort_keys=True))
        elif args.cmd == "classify":
            i = classify(store, args.id, args.kind, args.why, args.symbol, args.tf, args.at, args.tz, args.source, args.zones_marked)
            print(f"OK {i} classified {args.kind}")
        elif args.cmd == "read":
            ids, counts, (prior, falsifiers) = read_extract(store, args.ids, args.extract)
            print(f"OK {len(ids)} read, claims {counts}")
            if prior:
                klines_since = load_klines_since(store, args.ids, prior, getattr(args, "klines", None))
                print(f"Carried context from {repo_rel(prior)}: score each HELD / BROKEN / UNTESTED in this extract")
                for line in falsifiers or ["(the prior read has no Invalidation/Falsify lines)"]:
                    if falsifiers:
                        st = falsifier_status(line, klines_since)
                        print(f"  [{st}] {line}")
                    else:
                        print("  " + line)
        elif args.cmd == "done":
            ids = done(store, args.ids, args.outcome)
            print(f"OK {len(ids)} done: {args.outcome}")
        elif args.cmd == "sets":
            for s in make_sets(fold(load_events(store))):
                flag = "  SINGLE-TF: cross-timeframe layers of chart_read_protocol cannot be done" if s["single_tf"] else ""
                print(f"set {s['set']} {s['symbol']} {s['from']}..{s['to']} tfs {','.join(s['tfs'])} [{s['status']}] ids {' '.join(i[:8] for i in s['ids'])}{flag}")
        elif args.cmd == "bundle":
            packet = bundle(store, args.set)
            if getattr(args, "json", False):
                print(json.dumps(packet, indent=1, sort_keys=True))
            else:
                print(format_bundle(packet))
        elif args.cmd == "engine":
            plan = engine_plan(store, args.id, args.raw)
            print(f"PLAN {plan['id']} {plan['symbol']} as_of {plan['as_of']} (at {plan['at']}) raw {plan['raw']} -> {repo_rel(plan['out'])}")
            if not args.plan:
                print(f"OK engine snapshot {repo_rel(run_engine(plan))}: cite it in the extract's claim rows")
        elif args.cmd == "status":
            line, overdue = status_line(fold(load_events(store)), args.max_age_hours)
            print(line)
            for s in overdue[:10]:
                print("  OVERDUE " + fmt(s))
            return 1 if overdue else 0
    except ShotError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
