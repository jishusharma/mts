"""session_state.py - MTS session SSOT helper.
Two files: session_state.json (AI writes) and session_log.json (append-only).
Atomic writes. No partial reads. Schema-versioned.
"""
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

RUNTIME = Path(__file__).resolve().parent
STATE_FILE = RUNTIME / "session_state.json"
LOG_FILE = RUNTIME / "session_log.json"
VERSION = "5.0.0"

DEFAULT_STATE = {
    "version": VERSION,
    "updated_utc": None,
    "session_start_utc": None,
    "asset": "BTCUSDT",
    "mode": "armed",
    "thesis": {"direction": "neutral", "confidence": "low", "text": ""},
    "watch_levels": [],
    "next_trigger": {"condition": "", "expected_setup": "", "action_plan": ""},
    "invalidates": {"condition": ""},
    "notes": "",
}

def _now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def _atomic_write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".sst_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise

def read_state():
    if not STATE_FILE.exists():
        return dict(DEFAULT_STATE)
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("version") != VERSION:
            print(f"[session_state] WARN version {data.get('version')} != {VERSION}", file=sys.stderr)
        return data
    except Exception as e:
        print(f"[session_state] WARN corrupt state: {e}", file=sys.stderr)
        return dict(DEFAULT_STATE)

def write_state(d):
    if not isinstance(d, dict):
        raise TypeError("state must be dict")
    d = dict(d)
    d["version"] = VERSION
    d["updated_utc"] = _now()
    if not d.get("session_start_utc"):
        d["session_start_utc"] = _now()
    # type checks
    for k in ("asset", "mode", "notes"):
        if k in d and not isinstance(d[k], str):
            raise TypeError(f"{k} must be str")
    if "thesis" in d and not isinstance(d["thesis"], dict):
        raise TypeError("thesis must be dict")
    if "watch_levels" in d and not isinstance(d["watch_levels"], list):
        raise TypeError("watch_levels must be list")
    _atomic_write(STATE_FILE, d)
    return d

def read_log():
    if not LOG_FILE.exists():
        return {"version": VERSION, "events": []}
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "events" not in data or not isinstance(data["events"], list):
            data["events"] = []
        return data
    except Exception as e:
        print(f"[session_state] WARN corrupt log: {e}", file=sys.stderr)
        return {"version": VERSION, "events": []}

def append_log(event):
    if not isinstance(event, dict):
        raise TypeError("event must be dict")
    if "ts" not in event:
        event["ts"] = _now()
    if "type" not in event:
        event["type"] = "note"
    data = read_log()
    data["events"].append(event)
    if len(data["events"]) > 2000:
        data["events"] = data["events"][-2000:]
    data["version"] = VERSION
    _atomic_write(LOG_FILE, data)
    return event

def thesis_line(state, now=None):
    """One display line for the alert card: the thesis plus WHEN it was written (B156). Empty text = no line.
    The age is always shown and never used to hide the thesis (any cut-off would be an unsourced constant)."""
    th = (state or {}).get("thesis") or {}
    text = (th.get("text") or "").strip()
    if not text:
        return ""
    head = f"THESIS: {th.get('direction', '?')} ({th.get('confidence', '?')}) - {text}"
    raw = (state or {}).get("updated_utc")
    try:
        written = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        if written.tzinfo is None:
            written = written.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return head + " [written time unknown]"
    now = now or datetime.now(timezone.utc)
    mins = max(0, int((now - written).total_seconds() // 60))
    d, rem = divmod(mins, 1440)
    h, m = divmod(rem, 60)
    age = f"{d}d {h}h" if d else f"{h}h {m}m"
    return f"{head} [written {written.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%MZ')}, {age} old]"

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["init", "show", "log", "thesis-line"])
    args = ap.parse_args()
    if args.cmd == "init":
        s = write_state(DEFAULT_STATE)
        print(json.dumps(s, indent=2))
    elif args.cmd == "show":
        print(json.dumps(read_state(), indent=2))
    elif args.cmd == "log":
        print(json.dumps(read_log(), indent=2))
    elif args.cmd == "thesis-line":
        print(thesis_line(read_state()))
