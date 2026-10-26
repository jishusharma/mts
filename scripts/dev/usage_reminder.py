"""Hook gate: meter usage around Agent/Task/Workflow spawns.

A hook cannot call MCP, so the agent records a get_usage reading first:
  python scripts/dev/usage_reminder.py record --five <pct> --elapsed <pct>
which writes runtime_data/usage_reading.json (gitignored). Modes (hook JSON on stdin):
  pre   exit 2 + one-line reason (blocks the spawn) when the reading is missing or
        older than 10 min, 5h use > elapsed% + 10, or more than 2 spawns are running.
  post  prints the reminder and decrements the running-spawn counter.
Env MTS_USAGE_GATE=off bypasses; MTS_USAGE_DIR overrides the runtime dir (tests).
Any internal error exits 0 (never blocks on bad input).
"""
import json
import os
import sys
import time
from pathlib import Path

TOOLS = {"Agent", "Task", "Workflow"}
MAX_AGE_S = 600
MAX_RUNNING = 2
SLACK = 10.0
EXPIRE_S = 3600
CMD = "python scripts/dev/usage_reminder.py record --five <5h%> --elapsed <elapsed%>"


def rdir():
    d = os.environ.get("MTS_USAGE_DIR")
    return Path(d) if d else Path(__file__).resolve().parents[2] / "runtime_data"


def _load(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def running(now):
    d = _load(rdir() / "agent_spawns.json")
    items = d.get("running", []) if isinstance(d, dict) else []
    return [t for t in items if isinstance(t, (int, float)) and now - t < EXPIRE_S]


def _save_running(items):
    p = rdir() / "agent_spawns.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"running": items}), encoding="utf-8", newline="\n")


def check(now):
    """Return a block reason or None."""
    r = _load(rdir() / "usage_reading.json")
    if not isinstance(r, dict) or not isinstance(r.get("ts"), (int, float)):
        return f"USAGE GATE: no get_usage reading; call get_usage, then run: {CMD}"
    if now - r["ts"] > MAX_AGE_S:
        return f"USAGE GATE: reading is {int((now - r['ts']) // 60)} min old (>10); call get_usage, then run: {CMD}"
    five, el = float(r["five"]), float(r["elapsed"])
    if five > el + SLACK:
        return f"USAGE GATE: 5h use {five:g}% > elapsed {el:g}% + 10; wait or spawn fewer agents (MTS_USAGE_GATE=off to override)"
    n = len(running(now))
    if n > MAX_RUNNING:
        return f"USAGE GATE: {n} agent spawns recorded running (>2); wait for them to finish"
    return None


def record(argv):
    a = dict(zip(argv[::2], argv[1::2]))
    five, el = float(a["--five"]), float(a["--elapsed"])
    p = rdir() / "usage_reading.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"ts": time.time(), "five": five, "elapsed": el}),
                 encoding="utf-8", newline="\n")
    print(f"recorded five={five:g} elapsed={el:g}")
    return 0


def main(argv):
    try:
        mode = argv[1] if len(argv) > 1 else "pre"
        if mode == "record":
            return record(argv[2:])
        data = json.loads(sys.stdin.read() or "{}")
        if data.get("tool_name") not in TOOLS:
            return 0
        now = time.time()
        if mode == "post":
            print("USAGE: call get_usage then usage_log.py after <card>")
            items = running(now)
            if items:
                items.pop(0)
            _save_running(items)
            return 0
        if os.environ.get("MTS_USAGE_GATE", "").lower() == "off":
            print("USAGE: call get_usage then usage_log.py before <card>")
            return 0
        reason = check(now)
        if reason:
            print(reason, file=sys.stderr)
            return 2
        _save_running(running(now) + [now])
        print("USAGE: call get_usage then usage_log.py before <card>")
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
