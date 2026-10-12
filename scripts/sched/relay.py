"""Session relay guard: lets one Claude Code session start the next one from the committed handoff (zero operator input).

The ending session ships its work, calls `handoff` (stamps NEXT_SESSION.md with a relay header), ships that, then runs
`gate`; on GO it fires the App scheduled task named on the GO line (mts-relay-a for even depth, mts-relay-b for odd:
a task cannot start itself while its own run is in progress, so the two alternate) via mcp run_scheduled_task, which opens a fresh session whose
prompt is "read NEXT_SESSION.md and run its block". Fail closed: anything unclear = STOP (the operator starts it by hand).

Header (one HTML comment line in NEXT_SESSION.md, travels through git so every machine/account sees the same chain):
  <!-- relay: go depth=3 id=a1b2c3d4 -->        or        <!-- relay: stop reason=<text> depth=3 id=a1b2c3d4 -->
Gate STOPs on: no header / header says stop / depth >= MAX_DEPTH (default 6, per operator reset) / id equals --started-id
(the session never rewrote the handoff = it would replay the same task) / stop flag file / the SAME handoff id already
launched (double fire). The lock is keyed by handoff id, not by clock: a short session (the policy) that hands over a NEW id
10 minutes after the previous launch must be allowed through (2026-10-10 06:42 chain death: "a relay launched 15 min ago").
Depth counts from the chain base (`kick` records it per host), so a timer-started chain is never killed by an old depth.
Per-host state (not in git) lives in $MTS_RELAY_HOME (default ~/.claude): mts-relay-stop (flag), mts-relay-lock.json, mts-relay-log.jsonl.

  python scripts/sched/relay.py handoff --file F (--go | --stop "<reason>") [--reset-depth]
  python scripts/sched/relay.py lint --file F [--want go|stop]   task-list quality gate (handoff runs it; refuses on FAIL)
  python scripts/sched/relay.py gate --file F --started-id <id|none>      exit 0 GO, 1 STOP
  python scripts/sched/relay.py kick [--file F | --git-ref REF:PATH]   dispatcher: KICK task=... (exit 0) or IDLE <why> (exit 1)
  python scripts/sched/relay.py status --file F | stop "<why>" | resume
Two hosts, any account (2026-10-12): every host runs the same dispatcher. `handoff` appends who wrote it (host, account, session
title) to relay_runs.jsonl beside the handoff, and `kick --peer-quiet-min N` stays IDLE while ANOTHER host wrote the current
handoff under N minutes ago. A host that goes silent (budget out, machine off, `relay.py stop`) is taken over after N minutes;
nothing is keyed to an account, so signing a different account into either App changes nothing here.
`handoff` also keeps the file under MTS_RELAY_MAX_BYTES by moving old `## ` sections to handoff_history/<date>.md.
Test hooks: MTS_RELAY_HOME, MTS_RELAY_NOW (ISO), MTS_RELAY_MAX_DEPTH, MTS_RELAY_MAX_BYTES, MTS_RELAY_HOST, MTS_RELAY_ACCOUNT.
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
ACTIVE_MIN = 45  # kick: a launch younger than this means a session is probably still working
STALE_H = 1  # kick: the same handoff id launched this long ago and never rewritten = the session died or never started, retry
# (2026-10-10: the gate locks BEFORE the App starts the task; an unattended session could not approve run_scheduled_task, the 3 h wait wasted 3 h)
MAX_BYTES = int(os.environ.get("MTS_RELAY_MAX_BYTES") or 12288)  # handoff size cap: every relay session reads the whole file
RUNS_NAME = "relay_runs.jsonl"
RUNS_KEEP = 400
KICK_REF ="origin/fast-track:MyTradingSys/system/NEXT_SESSION.md"
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


def host():
    import platform
    return os.environ.get("MTS_RELAY_HOST") or platform.node() or "?"


def account():
    """Label of the Claude account signed in to this App right now (which account holds the chat). Read from the App's own
    sign-in record, NOT from $MTS_ACCOUNT: that is a fixed per-machine value and is wrong after an account switch
    (2026-10-12: JIS-NUC had MTS_ACCOUNT=sharma while signed in as jishu.awgp). $MTS_RELAY_ACCOUNT overrides (tests)."""
    v = os.environ.get("MTS_RELAY_ACCOUNT")
    if v:
        return v
    try:
        mail = json.loads((Path.home() / ".claude.json").read_text(encoding="utf-8"))["oauthAccount"]["emailAddress"]
        return mail.split("@", 1)[0]
    except (OSError, ValueError, KeyError, TypeError):
        return os.environ.get("MTS_ACCOUNT") or "?"


def parse_runs(text):
    rows = []
    for ln in (text or "").splitlines():
        try:
            d = json.loads(ln)
            d["_t"] = datetime.fromisoformat(d["utc"].replace("Z", "+00:00"))
            rows.append(d)
        except (ValueError, KeyError, TypeError, AttributeError):
            continue
    return rows


def append_run(handoff_path, **row):
    """One line per handoff in relay_runs.jsonl beside the handoff file: it ships in the same commit, so every host and
    account sees which host/account/session wrote which handoff id (the cross-device list of relay chats)."""
    p = Path(handoff_path).parent / RUNS_NAME
    old = p.read_text(encoding="utf-8").splitlines() if p.exists() else []
    old.append(json.dumps({"utc": now().strftime(TS), "host": host(), "account": account(), **row}, sort_keys=True))
    p.write_text("\n".join(old[-RUNS_KEEP:]) + "\n", encoding="utf-8", newline="\n")


def trim_history(path, text):
    """Over the size cap: move every `## ` section after the first fenced block to handoff_history/<date>.md (appended, nothing
    is lost) so the next session does not pay to read old updates. Returns the kept text."""
    lines = text.split("\n")
    fences = [i for i, ln in enumerate(lines) if ln.startswith("```")]
    start = fences[1] + 1 if len(fences) >= 2 else 0
    cut = next((i for i in range(start, len(lines)) if lines[i].startswith("## ")), None)
    if cut is None:
        return text
    hist = Path(path).parent / "handoff_history" / (now().strftime("%Y-%m-%d") + ".md")
    hist.parent.mkdir(parents=True, exist_ok=True)
    with open(hist, "a", encoding="utf-8", newline="\n") as f:
        f.write("<!-- moved from %s at %s -->\n" % (Path(path).name, now().strftime(TS)) + "\n".join(lines[cut:]).rstrip("\n") + "\n\n")
    return "\n".join(lines[:cut]).rstrip("\n") + "\n\nOlder updates: `handoff_history/` beside this file (read only when a task points there).\n"


def read_lock():
    try:
        d = json.loads((home() / "mts-relay-lock.json").read_text(encoding="utf-8"))
        d["_t"] = datetime.fromisoformat(d["utc"].replace("Z", "+00:00"))
        return d
    except (OSError, ValueError, KeyError):
        return None


def chain_base():
    try:
        return int(json.loads((home() / "mts-relay-chain.json").read_text(encoding="utf-8"))["base"])
    except (OSError, ValueError, KeyError):
        return 0


def read_header(path):
    """(state, reason, depth, id) or None when the file or header is missing."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return None
    m = HDR.search(text)
    return (m.group(1), (m.group(2) or "").strip(), int(m.group(3)), m.group(4)) if m else None


def lint_file(path, want, root=None):
    """Task-list quality gate (handoff_lint.py). MTS_RELAY_NOLINT=1 skips it (tests only)."""
    if os.environ.get("MTS_RELAY_NOLINT"):
        return []
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import handoff_lint
    p = Path(path).resolve()
    root = root or (p.parents[2] if len(p.parents) > 2 else Path.cwd())
    return handoff_lint.lint(p.read_text(encoding="utf-8"), root, want)[0]


def cmd_lint(a):
    errs = lint_file(a.file, a.want, a.root)
    for e in errs:
        print("LINT " + e)
    print("LINT OK" if not errs else "LINT FAIL %d" % len(errs))
    return 1 if errs else 0


def cmd_handoff(a):
    p = Path(a.file)
    text = p.read_text(encoding="utf-8")
    errs = lint_file(p, "go" if a.go else "stop")
    if errs:
        for e in errs:
            print("LINT " + e)
        print("HANDOFF REFUSED: fix the task list (RELAY.md 'Task list standard'), then run handoff again")
        return 2
    if len(text.encode("utf-8")) > MAX_BYTES:
        text = trim_history(p, text)
        if len(text.encode("utf-8")) > MAX_BYTES:
            print("HANDOFF REFUSED: %d bytes after moving old updates to handoff_history/, cap %d: shorten the task block "
                  "(drop DONE items, link files instead of pasting progress)" % (len(text.encode("utf-8")), MAX_BYTES))
            return 2
        print("TRIMMED old updates to handoff_history/ (cap %d bytes)" % MAX_BYTES)
    old = read_header(p)
    depth = 0 if (a.reset_depth or old is None) else old[2] + (1 if a.go else 0)
    state = "go" if a.go else "stop"
    reason = "" if a.go else " reason=" + re.sub(r"[>\r\n]", " ", a.stop).strip()
    hid = uuid.uuid4().hex[:8]
    line = "<!-- relay: %s%s depth=%d id=%s -->" % (state, reason, depth, hid)
    text = HDR.sub(line, text, count=1) if HDR.search(text) else line + "\n" + text
    p.write_text(text, encoding="utf-8", newline="\n")
    append_run(p, state=state, depth=depth, id=hid, session=(a.session or "")[:120])
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
    if depth - chain_base() >= MAX_DEPTH:
        return stop("chain depth %d (base %d) reached cap %d; operator resets with handoff --reset-depth or kick" % (depth, chain_base(), MAX_DEPTH))
    if a.started_id != "none" and hid == a.started_id:
        return stop("handoff id unchanged since session start (task not consumed or handoff not rewritten)")
    lock = home() / "mts-relay-lock.json"
    prev = read_lock()
    if prev and prev.get("id") == hid:
        return stop("handoff %s already launched (double fire)" % hid)
    home().mkdir(parents=True, exist_ok=True)
    lock.write_text(json.dumps({"utc": now().strftime(TS), "id": hid, "depth": depth}), encoding="utf-8", newline="\n")
    log("go", id=hid, depth=depth)
    print("RELAY GO depth=%d id=%s task=mts-relay-%s" % (depth, hid, "ab"[depth % 2]))
    return 0


def header_from_git(spec):
    """(state, reason, depth, id) from `REF:PATH` via git show (the dispatcher runs in the live tree, which lags origin)."""
    import subprocess
    ref = spec.split(":", 1)[0]
    subprocess.run(["git", "fetch", "-q", "origin", ref.split("/", 1)[-1]], capture_output=True, timeout=120)
    r = subprocess.run(["git", "show", spec], capture_output=True, text=True, encoding="utf-8", timeout=60)
    m = HDR.search(r.stdout) if r.returncode == 0 else None
    return (m.group(1), (m.group(2) or "").strip(), int(m.group(3)), m.group(4)) if m else None


def handoff_owner(a, hid):
    """(host, time) of whoever wrote handoff `hid`, from relay_runs.jsonl (same place as the handoff: file or git ref).
    No row for this id (written by an older relay.py or by hand): host 'unknown' = treated as a peer, time = the handoff
    file's last commit on the ref (None in --file mode, where there is nothing to date it by)."""
    import subprocess
    if a.file:
        p = Path(a.file).parent / RUNS_NAME
        text = p.read_text(encoding="utf-8") if p.exists() else ""
    else:
        ref, path = a.git_ref.split(":", 1)
        r = subprocess.run(["git", "show", "%s:%s/%s" % (ref, path.rsplit("/", 1)[0], RUNS_NAME)], capture_output=True, text=True, encoding="utf-8", timeout=60)
        text = r.stdout if r.returncode == 0 else ""
    for d in reversed(parse_runs(text)):
        if d.get("id") == hid:
            return d.get("host") or "unknown", d["_t"]
    if a.file:
        return "unknown", None
    ref, path = a.git_ref.split(":", 1)
    r = subprocess.run(["git", "log", "-1", "--format=%ct", ref, "--", path], capture_output=True, text=True, timeout=60)
    try:
        return "unknown", datetime.fromtimestamp(int(r.stdout.strip()), timezone.utc)
    except ValueError:
        return "unknown", None


def lock_info(prev):
    """` lock=<utc> task=<id>`: lets the dispatcher check list_task_runs for a run started after the lock (no run = launch never happened)."""
    return " lock=%s task=mts-relay-%s" % (prev["_t"].strftime(TS), "ab"[int(prev.get("depth", 0)) % 2])


def cmd_kick(a):
    """Dispatcher (a timer, not a session): start the relay when a committed handoff says go and nobody is working on it.

    Never edits the handoff. Idle when: stop flag, no header, header says stop, the same id was launched less than STALE_H
    hours ago (a session is on it), or any launch is younger than ACTIVE_MIN (a chain is moving). Otherwise records the
    launch (lock + a new chain base, so the depth cap measures this chain only) and prints KICK."""
    def idle(why):
        log("idle", reason=why)
        print("IDLE " + why)
        return 1
    flag = home() / "mts-relay-stop"
    if flag.exists():
        return idle("operator stop flag")
    h = read_header(a.file) if a.file else header_from_git(a.git_ref)
    if h is None:
        return idle("no relay header in handoff")
    state, reason, depth, hid = h
    if state != "go":
        return idle("handoff says stop: " + (reason or "no reason"))
    if a.peer_quiet_min:
        who, when = handoff_owner(a, hid)
        if who != host() and when is not None and now() - when < timedelta(minutes=a.peer_quiet_min):
            return idle("peer %s wrote handoff %s %d min ago (< %d): its chain is moving, this host stays out"
                        % (who, hid, (now() - when).total_seconds() // 60, a.peer_quiet_min))
    prev = read_lock()
    if prev:
        age = now() - prev["_t"]
        if age < timedelta(minutes=ACTIVE_MIN):
            return idle("a launch %d min ago, chain is moving%s" % (age.total_seconds() // 60, lock_info(prev)))
        if prev.get("id") == hid and age < timedelta(hours=STALE_H):
            return idle("handoff %s launched %d min ago, session still on it%s" % (hid, age.total_seconds() // 60, lock_info(prev)))
    home().mkdir(parents=True, exist_ok=True)
    (home() / "mts-relay-lock.json").write_text(json.dumps({"utc": now().strftime(TS), "id": hid, "depth": depth}), encoding="utf-8", newline="\n")
    (home() / "mts-relay-chain.json").write_text(json.dumps({"base": depth}), encoding="utf-8", newline="\n")
    log("kick", id=hid, depth=depth)
    print("KICK depth=%d id=%s task=mts-relay-%s" % (depth, hid, "ab"[depth % 2]))
    return 0


def cmd_brief(a):
    """Print only what a relay session needs from NEXT_SESSION.md: the header and the first few open, non-OPUS tasks
    (B172 cut 3: hand the session its task, not the whole queue)."""
    text = Path(a.file).read_text(encoding="utf-8")
    print("header:", read_header(a.file))
    n = 0
    for line in text.splitlines():
        if not re.match(r"^\s+Q\d+\.", line):
            continue
        if re.search(r"(?<![A-Za-z])(DONE|OPUS)(?![A-Za-z])", line):
            continue
        print(line.strip()[:a.width])
        n += 1
        if n >= a.max:
            break
    if n == 0:
        print("no open non-OPUS task line: pick with `python scripts/dev/tasks.py next`")
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
    h.add_argument("--session", help="title of this App session, recorded in relay_runs.jsonl so the chat can be found later")
    li = sub.add_parser("lint")
    li.add_argument("--file", required=True)
    li.add_argument("--want", choices=["go", "stop"], default="go")
    li.add_argument("--root")
    ga = sub.add_parser("gate")
    ga.add_argument("--file", required=True)
    ga.add_argument("--started-id", required=True)
    k = sub.add_parser("kick")
    k.add_argument("--file")
    k.add_argument("--git-ref", default=KICK_REF)
    k.add_argument("--peer-quiet-min", type=int, default=0,
                   help="IDLE while another host wrote the current handoff less than this many minutes ago (0 = off)")
    br = sub.add_parser("brief")
    br.add_argument("--file", required=True)
    br.add_argument("--max", type=int, default=3)
    br.add_argument("--width", type=int, default=400)
    st = sub.add_parser("status")
    st.add_argument("--file", required=True)
    sp = sub.add_parser("stop")
    sp.add_argument("why")
    sub.add_parser("resume")
    a = ap.parse_args(argv)
    if a.cmd == "handoff":
        return cmd_handoff(a)
    if a.cmd == "lint":
        return cmd_lint(a)
    if a.cmd == "gate":
        return cmd_gate(a)
    if a.cmd == "status":
        return cmd_status(a)
    if a.cmd == "brief":
        return cmd_brief(a)
    if a.cmd == "kick":
        return cmd_kick(a)
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
