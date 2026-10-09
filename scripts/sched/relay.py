"""Session relay guard: lets one Claude Code session start the next one from the committed handoff (zero operator input).

The ending session ships its work, calls `handoff` (stamps NEXT_SESSION.md with a relay header), ships that, then runs
`gate`; on GO it fires the App scheduled task named on the GO line (mts-relay-a for even depth, mts-relay-b for odd:
a task cannot start itself while its own run is in progress, so the two alternate) via mcp run_scheduled_task, which opens a fresh session whose
prompt is "read NEXT_SESSION.md and run its block". Fail closed: anything unclear = STOP (the operator starts it by hand).

Header (one HTML comment line in NEXT_SESSION.md, travels through git so every machine/account sees the same chain):
  <!-- relay: go depth=3 id=a1b2c3d4 -->        or        <!-- relay: stop reason=<text> depth=3 id=a1b2c3d4 -->
Gate STOPs on: no header / header says stop / depth >= MAX_DEPTH (default 6, per operator reset) / id equals --started-id
(the session never rewrote the handoff = it would replay the same task) / stop flag file / a launch inside LOCK_MIN minutes.
Per-host state (not in git) lives in $MTS_RELAY_HOME (default ~/.claude): mts-relay-stop (flag), mts-relay-lock.json, mts-relay-log.jsonl.

  python scripts/sched/relay.py handoff --file F (--go | --stop "<reason>") [--reset-depth]
  python scripts/sched/relay.py gate --file F --started-id <id|none>      exit 0 GO, 1 STOP
  python scripts/sched/relay.py status --file F | stop "<why>" | resume
Test hooks: MTS_RELAY_HOME, MTS_RELAY_NOW (ISO), MTS_RELAY_MAX_DEPTH.
"""
import argparse
import json
import os
import re
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True
MAX_DEPTH = int(os.environ.get("MTS_RELAY_MAX_DEPTH") or 6)
LOCK_MIN = 20
HDR = re.compile(r"<!-- relay: (go|stop)(?: reason=([^>]*?))? depth=(\d+) id=([0-9a-f]+) -->")
TS = "%Y-%m-%dT%H:%M:%SZ"


def home():
    return Path(os.environ.get("MTS_RELAY_HOME") or Path.home() / ".claude")


def now():
    v = os.environ.get("MTS_RELAY_NOW")
    return datetime.fromisoformat(v.replace("Z", "+00:00")) if v else datetime.now(timezone.utc)


def log(event, **kw):
    home().mkdir(parents=True, exist_ok=True)
    with open(home() / "mts-relay-log.jsonl", "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"utc": now().strftime(TS), "event": event, **kw}, sort_keys=True) + "\n")


def read_header(path):
    """(state, reason, depth, id) or None when the file or header is missing."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return None
    m = HDR.search(text)
    return (m.group(1), (m.group(2) or "").strip(), int(m.group(3)), m.group(4)) if m else None


def cmd_handoff(a):
    p = Path(a.file)
    text = p.read_text(encoding="utf-8")
    old = read_header(p)
    depth = 0 if (a.reset_depth or old is None) else old[2] + (1 if a.go else 0)
    state = "go" if a.go else "stop"
    reason = "" if a.go else " reason=" + re.sub(r"[>\r\n]", " ", a.stop).strip()
    line = "<!-- relay: %s%s depth=%d id=%s -->" % (state, reason, depth, uuid.uuid4().hex[:8])
    text = HDR.sub(line, text, count=1) if HDR.search(text) else line + "\n" + text
    p.write_text(text, encoding="utf-8", newline="\n")
    print(line)
    return 0


def stop(reason):
    log("stop", reason=reason)
    print("RELAY STOP " + reason)
    return 1


def cmd_gate(a):
    flag = home() / "mts-relay-stop"
    if flag.exists():
        return stop("operator stop flag: " + flag.read_text(encoding="utf-8").strip()[:120])
    h = read_header(a.file)
    if h is None:
        return stop("no relay header in handoff file")
    state, reason, depth, hid = h
    if state != "go":
        return stop("handoff says stop: " + (reason or "no reason"))
    if depth >= MAX_DEPTH:
        return stop("chain depth %d reached cap %d; operator resets with handoff --reset-depth" % (depth, MAX_DEPTH))
    if a.started_id != "none" and hid == a.started_id:
        return stop("handoff id unchanged since session start (task not consumed or handoff not rewritten)")
    lock = home() / "mts-relay-lock.json"
    try:
        last = datetime.fromisoformat(json.loads(lock.read_text(encoding="utf-8"))["utc"].replace("Z", "+00:00"))
        if now() - last < timedelta(minutes=LOCK_MIN):
            return stop("a relay launched %d min ago" % ((now() - last).total_seconds() // 60))
    except (OSError, ValueError, KeyError):
        pass
    home().mkdir(parents=True, exist_ok=True)
    lock.write_text(json.dumps({"utc": now().strftime(TS), "id": hid, "depth": depth}), encoding="utf-8", newline="\n")
    log("go", id=hid, depth=depth)
    print("RELAY GO depth=%d id=%s task=mts-relay-%s" % (depth, hid, "ab"[depth % 2]))
    return 0


def cmd_status(a):
    print("header:", read_header(a.file))
    flag = home() / "mts-relay-stop"
    print("stop flag:", flag.read_text(encoding="utf-8").strip() if flag.exists() else "none")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("handoff")
    h.add_argument("--file", required=True)
    g = h.add_mutually_exclusive_group(required=True)
    g.add_argument("--go", action="store_true")
    g.add_argument("--stop")
    h.add_argument("--reset-depth", action="store_true")
    ga = sub.add_parser("gate")
    ga.add_argument("--file", required=True)
    ga.add_argument("--started-id", required=True)
    st = sub.add_parser("status")
    st.add_argument("--file", required=True)
    sp = sub.add_parser("stop")
    sp.add_argument("why")
    sub.add_parser("resume")
    a = ap.parse_args(argv)
    if a.cmd == "handoff":
        return cmd_handoff(a)
    if a.cmd == "gate":
        return cmd_gate(a)
    if a.cmd == "status":
        return cmd_status(a)
    home().mkdir(parents=True, exist_ok=True)
    flag = home() / "mts-relay-stop"
    if a.cmd == "stop":
        flag.write_text(a.why, encoding="utf-8", newline="\n")
        log("operator_stop", reason=a.why)
    else:
        flag.unlink(missing_ok=True)
        log("operator_resume")
    return 0


if __name__ == "__main__":
    sys.exit(main())
