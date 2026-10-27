"""Station watcher monitor loop (pipeline station watch 2026-10-26).

Runs in the background of the watcher session (NOT a machine scheduler; the
session owns it and stops it on hand-over). Every 5 min it reads
`traffic.py status --json`, appends one compact line to the watch log, and
prints STATE-CHANGE lines when a station flips liveness, a lane stalls, the
Pipeliner lease is about to expire, or the desk pending count moves.
Renews the Pipeliner trunk lease when under 25 min left.
"""
import json
import subprocess
import sys
import time

LOG = "MyTradingSys/research/pipeliner/STATION_WATCH_2026-10-26.log"
INTERVAL_S = 300


def run(*args):
    return subprocess.run(args, capture_output=True, text=True).stdout.strip()


def log(line):
    with open(LOG, "a", encoding="utf-8", newline="\n") as f:
        f.write(line + "\n")
    print(line, flush=True)


def lease_minutes_left():
    out = run("python", "scripts/dev/traffic.py", "status", "--json")
    d = json.loads(out)
    text = (d.get("leases") or {}).get("Pipeliner", {}).get("text", "")
    # "(+43 min)" / "(-2 min)" marker; number is group(1)
    import re

    m = re.search(r"\(([-+]?\d+) min\)", text)
    return int(m.group(1)) if m else None


prev = None
while True:
    out = run("python", "scripts/dev/traffic.py", "status", "--json")
    try:
        d = json.loads(out)
    except ValueError:
        log("MONITOR ERROR: traffic.py status --json did not return JSON: " + out[:200])
        time.sleep(INTERVAL_S)
        continue

    machines = d.get("machines", {})
    snap = {}
    for name, m in machines.items():
        snap[name] = m.get("liveness")
    lane_flags = []
    codex = d.get("lanes", {}).get("codex", {})
    if codex.get("stalled"):
        lane_flags.append("CODEX-STALLED")
    pending = d.get("desk", {}).get("pending")
    snap_key = json.dumps({"l": snap, "p": pending, "lf": lane_flags}, sort_keys=True)
    prefix = "STATE-CHANGE" if prev is not None and snap_key != prev["key"] else "watch"
    line = (
        f"{prefix} {d.get('as_of')} "
        + " ".join(f"{k}={v}" for k, v in sorted(snap.items()))
        + (f" desk_pending={pending}" if pending is not None else "")
        + (" " + " ".join(lane_flags) if lane_flags else "")
    )
    log(line)

    left = lease_minutes_left()
    if left is not None and left <= 25:
        run("python", "scripts/dev/lease.py", "renew", "Pipeliner")
        log(f"lease renewed (was {left} min left)")

    prev = {"key": snap_key}
    time.sleep(INTERVAL_S)
