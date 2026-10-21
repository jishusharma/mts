"""One-way read-only mirror of the desktop's live state, so any work tree (JIS-NUC, laptop) can read it.

  python scripts/dev/live_mirror.py publish [--root DIR]   # JIS-NB live tree only; copies the ALLOWLIST to <root>/v<utc>/, then moves CURRENT
  python scripts/dev/live_mirror.py pull    [--root DIR]   # any work tree; verifies sha256, lands in runtime_data/_mirror/
  python scripts/dev/live_mirror.py brief                  # one screen: how old, flags, last alert, trades; every line says mirror@<utc>
                                                           # (a work tree whose copy is missing or older than WARN_MIN pulls first)
  python scripts/dev/live_mirror.py export-obs             # copy this machine's observation captures into git-tracked research/ (dedup by obs_id)

Design, review (Opus, 2026-10-10) and fail-closed rules: MyTradingSys/system/LIVE_MIRROR.md.
The mirror is data, never authority: no trading, gating or pause code may read runtime_data/_mirror.
runtime_data/_mirror* is git-ignored: the share is the only channel, so a pull never dirties a tree.
"""
import nowin  # B173: no console flash from git/python children under pythonw
nowin.install()
import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LIVE_MARKER = ".mts_live"
LIVE_HOST_FILE = REPO / "MyTradingSys" / "system" / "live_host.txt"  # one line: the live host's name; changed in the cutover (LIVE_HOST_MOVE.md)


def read_live_host():
    try:
        name = LIVE_HOST_FILE.read_text(encoding="utf-8").strip().upper()
    except OSError:
        name = ""
    return name or "JIS-NB"


LIVE_HOST = read_live_host()
DEFAULT_ROOT = "\\\\" + LIVE_HOST + "\\MTS-Mirror"
# the folder behind that share; sessions on the live host may not be on the share ACL but can read the folder
LIVE_ROOT = os.environ.get("MTS_MIRROR_LIVE_ROOT") or (r"F:\MTS\Mirror" if LIVE_HOST == "JIS-NB" else r"C:\MTS\Mirror")
MIRROR_DIR = "runtime_data/_mirror"
KEEP_VERSIONS = 3
WARN_MIN, STALE_MIN = 15, 60
FILE_CAP = 50 * 1024 * 1024
TOTAL_CAP = 400 * 1024 * 1024
VERSION_RE = re.compile(r"^v\d{8}T\d{6}Z$")
LOCK_STALE_S = 600
PULL_TIMEOUT_S = 45  # as sync.py pull_mirror: a hung share must not hang a session
BRIEF_WIDTH = 160

EXEC = "MyTradingSys/execution"
RT = "MyTradingSys/runtime"
# (relative glob, mode). mode: "whole" | ("tail", n_lines) | ("newest", n_files) | ("newest_tail", n_files, n_lines)
ALLOW = [
    ("runtime_data/snapshots/*.json", ("newest", 48)),
    ("runtime_data/last_alert.json", "whole"),
    ("runtime_data/alert_counter.txt", "whole"),
    ("runtime_data/loop_state.json", "whole"),
    ("runtime_data/canary_state.json", "whole"),
    ("runtime_data/naked_pocs/*.json", "whole"),
    ("runtime_data/live_runner.log", ("tail", 3000)),
    ("runtime_data/supervisor_log.txt", ("tail", 1000)),
    ("runtime_data/apparatus_log.txt", ("tail", 500)),
    ("runtime_data/observations/captures/*.jsonl", "whole"),
    (EXEC + "/auto_trades.jsonl", ("tail", 500)),
    (EXEC + "/auto_trader_state.json", "whole"),
    (EXEC + "/daily_loss_monitor_state.json", "whole"),
    (EXEC + "/plans/*.json", ("newest", 20)),
    (EXEC + "/journal/*.jsonl", ("newest_tail", 3, 300)),
    (EXEC + "/pm_heartbeats/*", ("newest", 10)),
    (RT + "/alerts/*.jsonl", ("tail", 300)),
    (RT + "/live_alert_state.json", "whole"),
    (RT + "/consensus_hook_state.json", "whole"),
    (RT + "/state_code.json", "whole"),
    (RT + "/session_state.json", "whole"),
    (RT + "/current_market_state.md", "whole"),
    (RT + "/orderflow_live/*.csv", ("newest_tail", 2, 20000)),
    (RT + "/oi_live/oi_1m.csv", ("tail", 20000)),
    (RT + "/oi_live/oi_5m_30d.csv", ("tail", 9000)),
    ("MyTradingSys/research/htf_context/*.jsonl", ("newest_tail", 2, 2000)),
    ("MyTradingSys/research/htf_context/_summary.json", "whole"),
    ("Dumps/consensus/consensus_*.jsonl", ("newest_tail", 1, 300)),
]
FLAGS = [EXEC + "/HALT", EXEC + "/HALT_DAILY_LOSS", EXEC + "/AUTO_PAUSE"]  # existence only, published in the manifest
DENY_NAMES = [".env*", "*.pem", "*secret*", "*credential*", "*apikey*", "*api_key*", "*.key"]
DENY_DIRS = {".secrets", ".git"}
KEY_LINE = re.compile(r"(api[_-]?key|secret|token|password|passwd)[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9+/_\-]{16,}", re.I)


class MirrorError(Exception):
    pass


def utcnow():
    return dt.datetime.now(dt.timezone.utc)


def stamp(t=None):
    return (t or utcnow()).strftime("v%Y%m%dT%H%M%SZ")


def parse_stamp(s):
    return dt.datetime.strptime(s, "v%Y%m%dT%H%M%SZ").replace(tzinfo=dt.timezone.utc)


def is_live_tree(repo):
    return (Path(repo) / LIVE_MARKER).exists()


def holds_live_marker(repo):
    """True when this host holds the live tree: the tree itself, or the main checkout a work tree hangs off, has .mts_live."""
    repo = Path(repo)
    if is_live_tree(repo):
        return True
    try:
        out = subprocess.run(["git", "-C", str(repo), "rev-parse", "--git-common-dir"], capture_output=True, text=True, timeout=10)
        if out.returncode == 0 and out.stdout.strip():
            common = Path(out.stdout.strip())
            if not common.is_absolute():
                common = repo / common
            return is_live_tree(common.resolve().parent)
    except (OSError, subprocess.SubprocessError):
        pass
    return False


def default_root(repo):
    """MTS_MIRROR_ROOT wins. The live tree, any work tree beside it (host holds .mts_live) and, by name, the live host
    (live_host.txt) use the local folder; other machines go through the share."""
    env = os.environ.get("MTS_MIRROR_ROOT")
    if env:
        return env
    if is_live_tree(repo):
        return LIVE_ROOT
    if Path(LIVE_ROOT).is_dir() and (socket.gethostname().upper() == LIVE_HOST or holds_live_marker(repo)):
        return LIVE_ROOT
    return DEFAULT_ROOT


def denied(rel):
    parts = Path(rel).parts
    if any(p in DENY_DIRS for p in parts):
        return True
    return any(fnmatch.fnmatch(parts[-1].lower(), pat) for pat in DENY_NAMES)


def redact(text):
    """Blank key-shaped values, keep the line. A sha256 or an order id has no key word before it, so it passes."""
    n = 0
    out = []
    for line in text.splitlines(keepends=True):
        if KEY_LINE.search(line):
            n += 1
            out.append("[REDACTED key-shaped line]\n")
        else:
            out.append(line)
    return "".join(out), n


def tail_lines(path, n):
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        size, block, data = f.tell(), 65536, b""
        while size > 0 and data.count(b"\n") <= n:
            step = min(block, size)
            size -= step
            f.seek(size)
            data = f.read(step) + data
    lines = data.splitlines(keepends=True)
    return b"".join(lines[-n:])


def resolve(repo):
    """[(rel, mode, abs_path)] for every file the allowlist selects; a deny hit on a selected file is fatal."""
    repo = Path(repo)
    picked, hits = [], []
    for pattern, mode in ALLOW:
        matches = sorted((p for p in repo.glob(pattern) if p.is_file()), key=lambda p: (p.stat().st_mtime, p.name))
        if isinstance(mode, tuple) and mode[0] in ("newest", "newest_tail"):
            matches = matches[-mode[1]:]
        for p in matches:
            rel = p.relative_to(repo).as_posix()
            if denied(rel):
                hits.append(rel)
            else:
                picked.append((rel, mode, p))
    if hits:
        raise MirrorError("allowlisted path is on the deny list, publish refused: " + ", ".join(hits))
    return picked


def read_selected(rel, mode, path):
    if isinstance(mode, tuple) and mode[0] == "tail":
        data = tail_lines(path, mode[1])
    elif isinstance(mode, tuple) and mode[0] == "newest_tail":
        data = tail_lines(path, mode[2])
    else:
        data = Path(path).read_bytes()
    if len(data) > FILE_CAP:
        raise MirrorError(f"{rel} is {len(data)} bytes after trimming, over the {FILE_CAP} cap")
    redacted = 0
    if rel.endswith((".json", ".jsonl", ".log", ".txt", ".md", ".csv")):
        text, redacted = redact(data.decode("utf-8", "replace"))
        data = text.encode("utf-8")
    return data, redacted


def publish(repo, root, now=None):
    repo = Path(repo)
    if not is_live_tree(repo):
        raise MirrorError("publish runs only in the live tree (the folder holding .mts_live)")
    now = now or utcnow()
    version = stamp(now)
    vdir = Path(root) / version
    if vdir.exists():
        raise MirrorError(f"{vdir} already exists")
    vdir.mkdir(parents=True)
    files, total, redacted = [], 0, 0
    try:
        for rel, mode, path in resolve(repo):
            data, nred = read_selected(rel, mode, path)
            total += len(data)
            if total > TOTAL_CAP:
                raise MirrorError(f"publish over the {TOTAL_CAP} byte cap")
            dest = vdir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            redacted += nred
            files.append({"rel": rel, "size": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                          "mtime": dt.datetime.fromtimestamp(Path(path).stat().st_mtime, dt.timezone.utc).isoformat()})
        head = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
        manifest = {"schema": 1, "host": socket.gethostname(), "utc": now.isoformat(), "version": version, "git_head": head,
                    "redacted_lines": redacted, "flags": {Path(f).name: (repo / f).exists() for f in FLAGS}, "files": files}
        (vdir / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8", newline="\n")
    except Exception:
        shutil.rmtree(vdir, ignore_errors=True)  # a half-written version is never pointed at
        raise
    tmp = Path(root) / "CURRENT.tmp"
    tmp.write_text(version, encoding="utf-8", newline="\n")
    os.replace(tmp, Path(root) / "CURRENT")  # pointer moves last: readers see the old or the new version, never a mix
    prune(root, version)
    return manifest


FAIL_FILE = "PUBLISH_FAIL.json"


def publish_recorded(repo, root, now=None):
    """publish() for the scheduled task: a failure (any exception) is written to <root>/PUBLISH_FAIL.json so readers see
    it (the task runs hidden, nobody sees stderr); a success clears it. The error is re-raised."""
    root = Path(root)
    try:
        m = publish(repo, root, now=now)
    except Exception as e:
        try:
            prev = json.loads((root / FAIL_FILE).read_text(encoding="utf-8"))
            since = prev.get("since")
        except (OSError, ValueError):
            since = None
        t = (now or utcnow()).isoformat()
        try:
            root.mkdir(parents=True, exist_ok=True)
            (root / FAIL_FILE).write_text(json.dumps({"since": since or t, "last": t, "error": f"{type(e).__name__}: {e}"[:300]}),
                                          encoding="utf-8", newline="\n")
        except OSError:
            pass
        raise
    (root / FAIL_FILE).unlink(missing_ok=True)
    return m


def publish_fail_line(root, now=None):
    """Loud line when the publisher's last run failed; None when fine or unreadable."""
    try:
        f = json.loads((Path(root) / FAIL_FILE).read_text(encoding="utf-8"))
        since = dt.datetime.fromisoformat(f["since"])
        mins = ((now or utcnow()) - since).total_seconds() / 60
        return f"PUBLISHER FAILING for {mins:.0f} min (since {since.strftime('%Y-%m-%d %H:%MZ')}): {f['error']}"
    except (OSError, ValueError, KeyError):
        return None


def prune(root, current):
    versions = sorted(p.name for p in Path(root).iterdir() if p.is_dir() and VERSION_RE.match(p.name))
    for old in versions[:-KEEP_VERSIONS]:
        if old != current:
            shutil.rmtree(Path(root) / old, ignore_errors=True)


class Lock:
    def __init__(self, path):
        self.path = Path(path)

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        for _ in range(2):
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                return self
            except FileExistsError:
                if time.time() - self.path.stat().st_mtime > LOCK_STALE_S:
                    self.path.unlink(missing_ok=True)  # stale lock from a crashed pull
                    continue
                raise MirrorError("another pull is running")
        raise MirrorError("could not take the pull lock")

    def __exit__(self, *a):
        self.path.unlink(missing_ok=True)


def pull(repo, root):
    """Read-only on `root`. On any failure the previous mirror stays and MirrorError is raised."""
    repo = Path(repo)
    if is_live_tree(repo):
        raise MirrorError("pull is for work trees; the live tree owns the data")
    root = Path(root)
    try:
        version = (root / "CURRENT").read_text(encoding="utf-8").strip()
    except OSError as e:
        raise MirrorError(f"no CURRENT pointer under {root}: {e}")
    if not VERSION_RE.match(version):
        raise MirrorError(f"CURRENT holds {version!r}, not a version name")
    vdir = root / version
    try:
        manifest = json.loads((vdir / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise MirrorError(f"manifest of {version} unreadable: {e}")
    dest_root = repo / MIRROR_DIR
    cur = dest_root / "manifest.json"
    if cur.exists():
        try:
            if json.loads(cur.read_text(encoding="utf-8")).get("version") == version:
                return "up to date", manifest
        except ValueError:
            pass
    with Lock(repo / "runtime_data" / "_mirror.lock"):
        stage = repo / (MIRROR_DIR + f".tmp{os.getpid()}")
        shutil.rmtree(stage, ignore_errors=True)
        try:
            for f in manifest["files"]:
                rel = f["rel"]
                if denied(rel) or ".." in Path(rel).parts or Path(rel).is_absolute():
                    raise MirrorError(f"manifest names a refused path: {rel}")
                data = (vdir / rel).read_bytes()
                if hashlib.sha256(data).hexdigest() != f["sha256"]:
                    raise MirrorError(f"sha256 mismatch for {rel}; previous mirror kept")
                out = stage / rel
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(data)
            (stage / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8", newline="\n")
            (stage / ".MIRROR_OF").write_text(f"{manifest['host']} {manifest['utc']}\nNOT LIVE. Data only; no code may trade or gate on it.\n",
                                              encoding="utf-8", newline="\n")
        except Exception:
            shutil.rmtree(stage, ignore_errors=True)
            raise
        old = repo / (MIRROR_DIR + ".old")
        shutil.rmtree(old, ignore_errors=True)
        if dest_root.exists():
            os.replace(dest_root, old)
        os.replace(stage, dest_root)
        shutil.rmtree(old, ignore_errors=True)
    return "pulled", manifest


def flatten(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from flatten(v, f"{prefix}{k}.")
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        yield prefix[:-1], obj


BRIEF_KEYS = ("vwap", "regime", "day_type", "state_code", "oi_change_1h", "oi_1h", "cvd", "net_delta", "poc", "vah", "val",
              "range_position", "last_price", "price", "close")


def brief_lines(repo, now=None):
    now = now or utcnow()
    base = Path(repo) / MIRROR_DIR
    mf = base / "manifest.json"
    if not mf.exists():
        return ["NO MIRROR: run `python scripts/dev/live_mirror.py pull` (never read the old git snapshot as live)"]
    m = json.loads(mf.read_text(encoding="utf-8"))
    pub = dt.datetime.fromisoformat(m["utc"])
    tag = f"mirror@{pub.strftime('%Y-%m-%d %H:%MZ')}"
    age = (now - pub).total_seconds() / 60
    snaps = [f for f in m["files"] if f["rel"].startswith("runtime_data/snapshots/")]
    lag = None
    if snaps:  # both times come from the desktop clock, so desktop/NUC clock skew cannot hide it
        newest = max(dt.datetime.fromisoformat(f["mtime"]) for f in snaps)
        lag = (pub - newest).total_seconds() / 60
    status = "OK"
    if age > STALE_MIN or lag is None or lag > STALE_MIN:
        status = "STALE"
    elif age > WARN_MIN or lag > WARN_MIN:
        status = "WARN"
    out = [f"{tag} {status}: published {age:.0f} min ago by {m['host']}, newest snapshot {'none' if lag is None else f'{lag:.0f} min older than the publish'}; git {m['git_head']}"]
    if status != "OK":
        out.append(f"{tag} do NOT present these numbers as live")
    raised = [k for k, v in m["flags"].items() if v]
    out.append(f"{tag} flags raised: {', '.join(raised) if raised else 'none'}; redacted lines: {m['redacted_lines']}")
    if snaps:
        newest_snap = max(snaps, key=lambda f: f["mtime"])
        flat = dict(flatten(json.loads((base / newest_snap["rel"]).read_text(encoding="utf-8"))))
        keys = [k for k in flat if k.split(".")[-1].lower() in BRIEF_KEYS][:24]
        out.append(f"{tag} snapshot {Path(newest_snap['rel']).name}: " + ("; ".join(f"{k}={flat[k]}" for k in keys) or f"{len(flat)} fields, none of the usual keys"))
    la = base / "runtime_data" / "last_alert.json"
    if la.exists():
        flat = dict(flatten(json.loads(la.read_text(encoding="utf-8"))))
        keys = [k for k in flat if k.split(".")[-1].lower() in ("alert_number", "number", "ts", "time", "signal", "verdict", "price", "thesis", "ssot_thesis")][:8]
        out.append(f"{tag} last Tom alert: " + ("; ".join(f"{k}={str(flat[k])[:60]}" for k in keys) or "present, keys unrecognised") + " (thesis text may be stale: B156)")
    trades = base / EXEC / "auto_trades.jsonl"
    if trades.exists():
        rows = [l for l in trades.read_text(encoding="utf-8").splitlines() if l.strip()][-3:]
        out.append(f"{tag} last auto-trader decisions: " + " | ".join(r[:140] for r in rows))
    return out


def clip(line, width=BRIEF_WIDTH):
    return line if len(line) <= width else line[:width - 3] + "..."


def mirror_age_min(repo, now=None):
    """Minutes since the desktop published the copy in this tree; None when there is no readable copy."""
    try:
        m = json.loads((Path(repo) / MIRROR_DIR / "manifest.json").read_text(encoding="utf-8"))
        return ((now or utcnow()) - dt.datetime.fromisoformat(m["utc"])).total_seconds() / 60
    except (OSError, ValueError, KeyError):
        return None


def try_pull(repo, root, timeout=PULL_TIMEOUT_S):
    """One best-effort pull, capped at `timeout` s. Returns the status line to print, or None when nothing changed."""
    res = {}

    def run():
        try:
            res["r"] = pull(repo, root)
        except MirrorError as e:
            res["err"] = str(e)
        except Exception as e:  # an unreachable share raises OSError subclasses of every kind
            res["err"] = f"{type(e).__name__}: {e}"

    t = threading.Thread(target=run, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        return f"mirror: pull skipped (timed out after {timeout}s)"
    if "err" in res:
        return f"mirror: pull skipped ({res['err'][:100]})"
    state, m = res["r"]
    return f"mirror: pulled {m['version']} ({len(m['files'])} files)" if state == "pulled" else None


def brief(repo, root, now=None, pull_timeout=PULL_TIMEOUT_S):
    """The brief a session prints. A work tree whose copy is missing or older than WARN_MIN pulls first, because trees made
    by the App never run `sync.py start`; the live tree owns the data and never pulls. Lines are clipped to one screen."""
    lines = []
    age = mirror_age_min(repo, now)
    if not is_live_tree(repo) and (age is None or age > WARN_MIN):
        note = try_pull(repo, root, pull_timeout)
        if note:
            lines.append(note)
    fail = publish_fail_line(root, now)
    if fail:
        lines.append(fail)
    return [clip(l) for l in lines + brief_lines(repo, now)]


def export_obs(repo):
    src = Path(repo) / "runtime_data" / "observations" / "captures"
    dest = Path(repo) / "MyTradingSys" / "research" / "missed_trades" / "observations" / f"{socket.gethostname()}_captures.jsonl"
    seen = set()
    if dest.exists():
        for line in dest.read_text(encoding="utf-8").splitlines():
            try:
                seen.add(json.loads(line)["obs_id"])
            except (ValueError, KeyError):
                pass
    new = []
    for f in sorted(src.glob("*.jsonl")) if src.exists() else []:
        for line in f.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if rec.get("obs_id") and rec["obs_id"] not in seen:
                seen.add(rec["obs_id"])
                new.append(line)
    if new:
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "a", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(new) + "\n")
    return len(new), dest


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["publish", "pull", "brief", "export-obs"])
    ap.add_argument("--root", default=os.environ.get("MTS_MIRROR_ROOT"))  # unset: default_root(repo)
    ap.add_argument("--repo", default=str(REPO))
    a = ap.parse_args(argv)
    if not a.root:
        a.root = default_root(a.repo)
    try:
        if a.cmd == "publish":
            m = publish_recorded(a.repo, a.root)
            print(f"published {m['version']}: {len(m['files'])} files, flags raised {[k for k, v in m['flags'].items() if v]}")
        elif a.cmd == "pull":
            state, m = pull(a.repo, a.root)
            print(f"{state}: mirror of {m['host']} {m['utc']} ({len(m['files'])} files)")
        elif a.cmd == "brief":
            print("\n".join(brief(a.repo, a.root)))
        else:
            n, dest = export_obs(a.repo)
            print(f"exported {n} new capture(s) to {dest}")
    except MirrorError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        if a.cmd != "publish":
            raise
        print(f"PUBLISH FAILED: {type(e).__name__}: {e}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
