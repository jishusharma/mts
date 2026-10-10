"""Screenshot intake: every image the operator shows a session is saved, classified, read and closed here.

  python scripts/dev/shot.py ingest [--inbox DIR]              # land new images (idempotent, sha256 de-duplicated)
  python scripts/dev/shot.py hook                              # Claude Code hook: ingest this session, print a notice
  python scripts/dev/shot.py list [--status pending|new|classified|read|done]
  python scripts/dev/shot.py classify <id> --kind chart|positions|app|other|noise --why "<what it is / what the operator meant>"
                             [--symbol BTCUSDT --tf 15m --at "2026-10-08 02:47" --tz +05:30 --source "binance footprint"]
  python scripts/dev/shot.py read <id>... --extract <md>       # extract exists, names the ids, has claim rows
  python scripts/dev/shot.py done <id>... --outcome finding:B156 | feature:FEAT-11 | noaction:"<why>" | note:"<text>"
  python scripts/dev/shot.py sets                              # chart shots grouped into multi-timeframe sets
  python scripts/dev/shot.py status [--max-age-hours 24]       # one line; exit 1 when a shot is overdue (the gate)

Why this exists: Claude saves a pasted image in places no session is told about (the session transcript, ~/.claude/uploads,
a Temp folder that is cleaned), and a plain chat keeps it nowhere. This tool lands every image in one store keyed by
sha256, so saving never depends on a session remembering to do it. The store is gitignored (screenshots can show
accounts); the extracts written about them are tracked. Process: MyTradingSys/methodology/screenshot_intake.md.
Store: env MTS_SHOT_DIR, else <main checkout>/runtime_data/screenshots (one store per machine, shared by every worktree).
"""
import argparse
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
import tempfile
import time
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "MyTradingSys" / "observation"))
import capture  # noqa: E402  (time parsing and the timeframe list are shared with the observation channel)

KINDS = ("chart", "positions", "app", "other", "noise")
PRIVATE_KINDS = ("positions",)
STATUSES = ("new", "classified", "read", "done")
CLAIM_CLASSES = ("MATCH", "MISMATCH", "NOT_IN_DATA")
CLAIM_ROW = re.compile(r"^\|\s*[A-Za-z0-9_.-]+\s*\|\s*(MATCH|MISMATCH|NOT_IN_DATA)\s*\|", re.M)
PRIOR_LINE = re.compile(r"^[\s>*-]*Prior(?::\**|\**:)[ \t]*(\S.*?)\s*$", re.M)  # B157: `Prior: <extract>` / `**Prior:** none`
OUTCOME_ID = re.compile(r"^(B\d{3}|T\d{3}|F-BT-\d+|FEAT-\d+)$")
SET_WINDOW_MIN = 10  # chart shots of one symbol within this many minutes are one set (the 2026-10-08 batch spanned 4)
NAG_EVERY_HOURS = 6  # the SessionStart backlog reminder repeats at most this often
MAX_TEXT = 500
EXT_OK = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


class ShotError(ValueError):
    pass


# ---------------------------------------------------------------- locations
def git(*args, cwd=None):
    r = subprocess.run(["git", *args], cwd=cwd or REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def main_root():
    """The primary checkout (the live tree on the desktop): every worktree shares its store."""
    common = git("rev-parse", "--path-format=absolute", "--git-common-dir").strip()
    if not common:  # git older than 2.31
        rel = git("rev-parse", "--git-common-dir").strip()
        common = str((REPO / rel).resolve()) if rel else ""
    p = Path(common) if common else REPO / ".git"
    return p.parent if p.name == ".git" else REPO


def store_dir():
    return Path(os.environ.get("MTS_SHOT_DIR") or main_root() / "runtime_data" / "screenshots")


def claude_home():
    return Path(os.environ.get("MTS_CLAUDE_HOME") or Path.home() / ".claude")


def temp_root():
    return Path(os.environ.get("MTS_SHOT_TEMP") or Path(tempfile.gettempdir()) / "claude")


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
    counts = {c: 0 for c in CLAIM_CLASSES}
    for m in CLAIM_ROW.finditer(text):
        counts[m.group(1)] += 1
    is_chart = any(S[i].get("kind") == "chart" for i in ids)
    if is_chart and not sum(counts.values()):
        raise ShotError("a chart extract needs claim rows: | id | MATCH or MISMATCH or NOT_IN_DATA | chart claim | data check |")
    prior = carried_context(text, path) if is_chart else (None, [])
    ev_extra = {"prior": repo_rel(prior[0])} if prior[0] else {}
    for i in ids:
        append(store, {"event": "read", "id": i, "ts": now_iso(), "extract": repo_rel(path), "claims": counts, **ev_extra})
    return ids, counts, prior


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


def outcome_exists(token):
    """A filed outcome must really be filed: B/T ids are rows of the registry, F-BT / FEAT ids appear in a markdown doc.
    (A bare grep would let a test file or a code comment 'file' the item.)"""
    if os.environ.get("MTS_SHOT_SKIP_REPO_CHECK"):
        return True
    if re.fullmatch(r"[BT]\d{3}", token):
        bugs = REPO / "MyTradingSys" / "research" / "BUGS.md"
        return bugs.is_file() and re.search(rf"^\|\s*{re.escape(token)}\s*\|", bugs.read_text(encoding="utf-8"), re.M) is not None
    return bool(git("grep", "--untracked", "-l", "-F", "-e", token, "--", "*.md").strip())


def done(store, prefixes, outcome):
    S = fold(load_events(store))
    ids = [resolve(S, p) for p in prefixes]
    kind, _, rest = outcome.partition(":")
    rest = rest.strip()
    if kind in ("finding", "feature"):
        if not OUTCOME_ID.match(rest):
            raise ShotError(f"{kind}: needs an item id such as B156, T070, F-BT-23 or FEAT-11")
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
        if kind == "noaction" and (s.get("claims") or {}).get("MISMATCH") and len(rest) < 20:
            raise ShotError(f"{i} has MISMATCH claims: file them (finding:/feature:) or explain in 20+ characters why not")
    for i in ids:
        append(store, {"event": "done", "id": i, "ts": now_iso(), "outcome": outcome})
    return ids


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
    a = sub.add_parser("done"); a.add_argument("ids", nargs="+"); a.add_argument("--outcome", required=True)
    sub.add_parser("sets")
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
                print(f"Carried context from {repo_rel(prior)}: score each HELD / BROKEN / UNTESTED in this extract")
                for line in falsifiers or ["(the prior read has no Invalidation/Falsify lines)"]:
                    print("  " + line)
        elif args.cmd == "done":
            ids = done(store, args.ids, args.outcome)
            print(f"OK {len(ids)} done: {args.outcome}")
        elif args.cmd == "sets":
            for s in make_sets(fold(load_events(store))):
                flag = "  SINGLE-TF: cross-timeframe layers of chart_read_protocol cannot be done" if s["single_tf"] else ""
                print(f"set {s['set']} {s['symbol']} {s['from']}..{s['to']} tfs {','.join(s['tfs'])} [{s['status']}] ids {' '.join(i[:8] for i in s['ids'])}{flag}")
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
