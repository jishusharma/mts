"""Station watcher monitor loop (pipeline station watch 2026-10-26).

Runs in the background of the watcher session (NOT a machine scheduler; the
session owns it and stops it on hand-over). Every 5 min it reads
`traffic.py status --json`, appends one compact line to the watch log, and
prints STATE-CHANGE lines when a station flips liveness, a lane stalls, the
Pipeliner lease is about to expire, or the desk pending count moves.
Renews the Pipeliner trunk lease when under 25 min left.

Ship-flow guard (design research/lead/2026-10-28_watcher-ship-flow-guard-design.md): check_flags() also flags a red last
ship (CI-RED-20m), a held gate slot (GATE-HELD-<slot>-<min>m), a STALE claim and an idle lane with ready cards, and sends one
PIPE signal per flag appearance. It proposes only: no revert, release or kill. Thresholds are OURS; STALE uses sync.STALE_HOURS.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "dev"))

LOG = "MyTradingSys/research/pipeliner/STATION_WATCH_2026-10-26.log"
INTERVAL_S = 300
CI_LAG_MIN = 20       # OURS: 4x a healthy CI run
GATE_HELD_MIN = 20    # OURS
IDLE_POLLS = 2        # OURS: one poll can catch a lane between two cards
STALE_HOURS = 24      # SOURCED: sync.py:52 (replaced by the sync constant when importable)
try:
    import sync as _sync
    STALE_HOURS = _sync.STALE_HOURS
except Exception:     # the monitor must still start without sync.py
    _sync = None


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
    m = re.search(r"\(([-+]?\d+) min\)", text)
    return int(m.group(1)) if m else None


def _num(v, field):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ValueError(f"{field} not a number: {v!r}")
    return float(v)


def _base(flag):
    """Flag identity without its changing minutes suffix, so a slot held 21 then 26 min is one appearance."""
    return re.sub(r"-\d+m$", "", flag)


def check_flags(status, extras, prev_flags):
    """Pure. Returns (flags, proposals). A flag starting '~' is an internal pending mark (lane idle for one poll); one
    starting 'MONITOR ERROR' means a reading was malformed (unknown, never all good). A proposal ([who] action (why)) is
    returned only for a flag whose identity was not in prev_flags."""
    prev_flags = set(prev_flags or ())
    flags, cand, errors = [], {}, []

    def add(flag, who, action, why):
        flags.append(flag)
        cand[flag] = {"flag": flag, "who": who, "action": action, "why": why, "text": f"[{who}] {action} ({why})"}

    try:
        lag = extras.get("green_lag_min")
        if lag is not None and _num(lag, "green_lag_min") > CI_LAG_MIN:
            add("CI-RED-20m", "operator", "last ship red: revert it", f"CI_RED rule, trunk ahead of green {lag:.0f} min")
    except (AttributeError, ValueError, TypeError) as e:
        errors.append(f"MONITOR ERROR: extras.green_lag_min: {e}")
    try:
        slots = extras["gate_slots"]
        if not isinstance(slots, list):
            raise ValueError("gate_slots not a list")
        for s in slots:
            age, alive = _num(s["age_min"], "age_min"), s["alive"]
            if alive and age > GATE_HELD_MIN:
                add(f"GATE-HELD-{s['slot']}-{int(age)}m", "this host",
                    f"gate slot {s['slot']} held {int(age)} min by PID {s.get('pid')}", "held, not dead; its owner decides")
    except (KeyError, AttributeError, ValueError, TypeError) as e:
        errors.append(f"MONITOR ERROR: extras.gate_slots: {e!r}")
    try:
        claims = extras["stale_claims"]
        if not isinstance(claims, list):
            raise ValueError("stale_claims not a list")
        for c in claims:
            age_h = _num(c["age_h"], "age_h")
            if age_h > STALE_HOURS:
                add(f"STALE-CLAIM-{c['slug']}", c.get("owner") or "claim owner", f"release or finish {c['slug']}",
                    f"claim {age_h:.0f} h old, limit {STALE_HOURS} h")
    except (KeyError, AttributeError, ValueError, TypeError) as e:
        errors.append(f"MONITOR ERROR: extras.stale_claims: {e!r}")
    try:
        ready = {}
        for c in status.get("queue") or []:
            ready[c.get("lane")] = ready.get(c.get("lane"), 0) + 1
        for lane, n in sorted(ready.items(), key=lambda kv: str(kv[0])):
            l = (status.get("lanes") or {}).get(lane)
            if not isinstance(l, dict) or l.get("state") == "unknown":
                continue
            if l.get("state") in ("idle", "off") or l.get("running") == 0 or l.get("stalled"):
                if f"LANE-IDLE-{lane}" in prev_flags or f"~LANE-IDLE-{lane}" in prev_flags:
                    add(f"LANE-IDLE-{lane}", "Pipeliner", f"route a ready card to lane {lane}", f"{n} ready, lane idle {IDLE_POLLS} polls")
                else:
                    flags.append(f"~LANE-IDLE-{lane}")
    except (AttributeError, TypeError) as e:
        errors.append(f"MONITOR ERROR: status.queue/lanes: {e!r}")
    seen = {_base(f) for f in prev_flags}
    return flags + errors, [p for f, p in cand.items() if _base(f) not in seen]


def read_green_lag():
    """Minutes the oldest CI-gated trunk commit has been ahead of origin/green/fast-track (make_status.get_ci_line logic);
    0 when level or docs-only; raises when unreadable."""
    run("git", "fetch", "--quiet", "origin", "green/fast-track", "fast-track")
    pend = [int(t) for t in run("git", "log", "--first-parent", "--format=%ct",
                                "origin/green/fast-track..origin/fast-track").split() if t.isdigit()]
    if not pend:
        return 0
    import make_status
    if not run("git", "diff", "--name-only", "origin/green/fast-track", "origin/fast-track", "--", *make_status.CI_PATHS):
        return 0   # docs-only: ci.yml never runs
    return (time.time() - min(pend)) / 60


def read_gate_slots():
    base = Path(os.environ.get("MTS_GATE_SLOTS_DIR") or Path(tempfile.gettempdir()) / "mts_gate_slots") / "gate-slots"
    out = []
    for p in sorted(base.glob("slot-*")) if base.exists() else []:
        try:
            pid = int(p.read_text().strip())
            alive = bool(_sync.pid_alive(pid)) if _sync else True
            out.append({"slot": p.name, "age_min": (time.time() - p.stat().st_mtime) / 60, "pid": pid, "alive": alive})
        except (OSError, ValueError):
            continue   # empty or mid-write: not a held slot
    return out


def read_stale_claims():
    if _sync is None:
        raise RuntimeError("sync.py not importable")
    now = time.time()
    return [{"slug": slug, "owner": f"{kv.get('host', '?')}/{kv.get('account', '?')}",
             "age_h": (now - int(kv.get("epoch", now))) / 3600} for slug, kv in _sync.open_claims(Path.cwd())]


def gather_extras():
    ex = {}
    for key, fn in (("green_lag_min", read_green_lag), ("gate_slots", read_gate_slots), ("stale_claims", read_stale_claims)):
        try:
            ex[key] = fn()
        except Exception as e:
            log(f"MONITOR ERROR: {key} unreadable: {e!r}")
            ex[key] = "unreadable"   # malformed on purpose: check_flags reports it, nothing is called green
    return ex


def send_signal(text):
    run("python", "scripts/dev/mts_signal.py", "send", ("PIPE " + text)[:200], "--to", "all")


def main():
    prev = None
    prev_flags = set()
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
        flags, proposals = check_flags(d, gather_extras(), prev_flags)
        lane_flags += [_base(f) if f.startswith("GATE-HELD") else f for f in flags if not f.startswith("~")]
        for p in proposals:
            send_signal(p["text"])
        prev_flags = set(flags)
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


if __name__ == "__main__":
    main()
