"""Session relay: lets one Claude Code session start the next one from the committed handoff (zero operator input).

The dispatcher (an App scheduled task on a cron) runs `tick` in ONE call; on KICK that same session IS the relay session (an
unattended session cannot start another one: B164), so there is no launch step. The ending session ships its work, calls `handoff`
(stamps NEXT_SESSION.md with a relay header), ships that, and runs `unlock` so the next tick starts the next handoff at once.

Header (one HTML comment line in NEXT_SESSION.md, travels through git so every machine/account sees the same chain):
  <!-- relay: go depth=3 id=a1b2c3d4 -->        or        <!-- relay: stop reason=<text> depth=3 id=a1b2c3d4 -->
`kick` stays IDLE on: stop flag / no header / header says stop / no task this host can run / a launch younger than ACTIVE_MIN /
the SAME handoff id launched under STALE_H ago (a session is on it) / another host wrote the handoff under --peer-quiet-min ago.
The lock is keyed by handoff id and freed by `unlock`, not by a clock alone.
Per-host state (not in git) lives in $MTS_RELAY_HOME (default ~/.claude): mts-relay-stop (flag), mts-relay-lock.json,
mts-relay-log.jsonl, mts-relay-routed.json, mts-hourly.json.

  python scripts/sched/relay.py tick [--peer-quiet-min N]       dispatcher: fetch, route, kick, hourly gate, ONE `TICK NOOP|KICK` line
  python scripts/sched/relay.py begin [--root R] [--skip CARD]  KICK session start: relay worktree, sync start, claim a card, brief
  python scripts/sched/relay.py brief --file F                  header + first open tasks of the handoff (never read the whole file)
  python scripts/sched/relay.py handoff --file F (--go | --stop "<reason>") [--reset-depth]
  python scripts/sched/relay.py unlock                          free the launch lock (last action of a KICK session, not after --stop)
  python scripts/sched/relay.py lint --file F [--want go|stop]  task-list quality gate + size cap (handoff runs it; refuses on FAIL)
  python scripts/sched/relay.py kick [--file F | --git-ref REF:PATH]   KICK depth=.. id=.. (exit 0) or IDLE <why> (exit 1), then the QUEUE line
  python scripts/sched/relay.py route [--file F | --git-ref REF:PATH]  post open `lane=CODEX` / `lane=DSA` tasks to their lane once
  python scripts/sched/relay.py status --file F [--host H]      header, stop flag and the QUEUE line
  python scripts/sched/relay.py stop "<why>" | resume
Two hosts, any account (2026-10-12): every host runs the same dispatcher. `handoff` appends who wrote it (host, account, session
title) to relay_runs.jsonl beside the handoff, and `kick --peer-quiet-min N` stays IDLE while ANOTHER host wrote the current
handoff under N minutes ago. A host that goes silent (budget out, machine off, `relay.py stop`) is taken over after N minutes;
nothing is keyed to an account, so signing a different account into either App changes nothing here.
`handoff` also keeps the file under MTS_RELAY_MAX_BYTES by moving old `## ` sections to handoff_history/<date>.md.
Test hooks: MTS_RELAY_HOME, MTS_RELAY_NOW (ISO), MTS_RELAY_MAX_BYTES, MTS_RELAY_HOST, MTS_RELAY_ACCOUNT.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "dev"))
try:
    import hosts  # noqa: E402  (scripts/dev/hosts.py: old and new machine names are one host)
except ImportError:   # run from a copy without scripts/dev: plain case-insensitive compare
    class hosts:   # noqa: N801
        @staticmethod
        def same_host(a, b):
            return bool(a) and str(a).lower() == str(b).lower()

sys.dont_write_bytecode = True
ACTIVE_MIN = 45  # kick: a launch younger than this means a session is probably still working
STALE_H = 1  # kick: the same handoff id launched this long ago and never rewritten = the session died or never started, retry
HOURLY_MIN = 55  # tick: minutes between two hourly bundles (refiner status, housekeeping), kept in mts-hourly.json
HOUSEKEEP_H = 24  # tick: hours between two housekeeping asks
MAX_BYTES = int(os.environ.get("MTS_RELAY_MAX_BYTES") or 12288)  # handoff size cap: every relay session reads the whole file
RUNS_NAME = "relay_runs.jsonl"
HOST_ERR = "go with no unblocked open task for host"  # == handoff_lint.HOST_ERR
NONE_ERR = "go with no unblocked open task:"  # == handoff_lint.NONE_ERR
RUNS_KEEP = 400
SUPER_STALE_MIN = 60  # watchdog (OURS): a super-session stop whose heartbeat is older than this (or unreadable) is lifted
SUPER_PREFIX = "super-session"
HEARTBEAT_NAME = "mts-super-heartbeat.json"
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


def read_header(path):
    """(state, reason, depth, id) or None when the file or header is missing."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return None
    m = HDR.search(text)
    return (m.group(1), (m.group(2) or "").strip(), int(m.group(3)), m.group(4)) if m else None


def lint_file(path, want, root=None, host=None, text=None):
    """Task-list quality gate (handoff_lint.py). MTS_RELAY_NOLINT=1 skips it (tests only). `text` lints that content
    instead of reading `path` (kick --git-ref). `host` makes want=go count only tasks that can run on that host."""
    if os.environ.get("MTS_RELAY_NOLINT"):
        return []
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import handoff_lint
    p = Path(path).resolve()
    root = root or (p.parents[2] if len(p.parents) > 2 else Path.cwd())
    return handoff_lint.lint(text if text is not None else p.read_text(encoding="utf-8"), root, want, host)[0]


def cmd_lint(a):
    errs = lint_file(a.file, a.want, a.root, a.host)
    size = len(Path(a.file).read_text(encoding="utf-8").encode("utf-8"))   # same measure as handoff's cap check
    if size > MAX_BYTES:   # not in lint_file: handoff lints first and may still trim old sections to get under the cap
        errs.append("file is %d bytes, cap %d (every relay session reads the whole file): handoff moves old `## ` sections to "
                    "handoff_history/ and refuses when that is not enough; shorten the task block (drop DONE items, link files)" % (size, MAX_BYTES))
    for e in errs:
        print("LINT " + e)
    print("LINT OK" if not errs else "LINT FAIL %d" % len(errs))
    return 1 if errs else 0


def cmd_handoff(a):
    p = Path(a.file)
    text = p.read_text(encoding="utf-8")
    # no host here: a session must be able to hand a go to the OTHER host (stop is refused while any task is open)
    errs = lint_file(p, "go" if a.go else "stop", host=a.host)
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


def cmd_unlock(a):
    """Last action of a KICK session (not after `handoff --stop`): frees the launch lock so the next tick starts the next handoff."""
    lock = home() / "mts-relay-lock.json"
    had = lock.exists()
    lock.unlink(missing_ok=True)
    log("unlock", had_lock=had)
    print("UNLOCKED" if had else "UNLOCKED (no lock)")
    return 0


def header_from_git(spec):
    """(state, reason, depth, id) from `REF:PATH` via git show (the dispatcher runs in the live tree, which lags origin)."""
    import subprocess
    ref = spec.split(":", 1)[0]
    subprocess.run(["git", "fetch", "-q", "origin", ref.split("/", 1)[-1]], capture_output=True, timeout=120)
    r = subprocess.run(["git", "show", spec], capture_output=True, text=True, encoding="utf-8", timeout=60)
    m = HDR.search(r.stdout) if r.returncode == 0 else None
    return (m.group(1), (m.group(2) or "").strip(), int(m.group(3)), m.group(4)) if m else None


def text_from_git(spec):
    """Handoff text from `REF:PATH` (header_from_git has just fetched it); None when git cannot show it."""
    import subprocess
    r = subprocess.run(["git", "show", spec], capture_output=True, text=True, encoding="utf-8", timeout=60)
    return r.stdout if r.returncode == 0 else None


def handoff_owner(a, hid):
    """(host, time) of whoever wrote handoff `hid`, from relay_runs.jsonl (same place as the handoff: file or git ref).
    No row for this id (a session edited the header by hand, e.g. the Q64 tidy run 2026-10-14 23:28): host 'unknown', which kick does
    NOT treat as a peer (it made this host wait 90 min on its own handoff, 2026-10-14); time = the handoff
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


def cmd_kick(a):
    """Dispatcher (a timer, not a session): start the relay when a committed handoff says go and nobody is working on it.

    Never edits the handoff. Idle when: stop flag, no header, header says stop, the same id was launched less than STALE_H
    hours ago (a session is on it), or any launch is younger than ACTIVE_MIN (a chain is moving). Otherwise records the
    launch (the lock `unlock` frees) and prints KICK."""
    qinfo = {}

    def idle(why):
        log("idle", reason=why)
        print("IDLE " + why)
        if qinfo:
            print(queue_line(qinfo["q"]))
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
        if who != "unknown" and not hosts.same_host(who, host()) and when is not None and now() - when < timedelta(minutes=a.peer_quiet_min):
            return idle("peer %s wrote handoff %s %d min ago (< %d): its chain is moving, this host stays out"
                        % (who, hid, (now() - when).total_seconds() // 60, a.peer_quiet_min))
    # host awareness: a go whose open tasks all belong to other hosts is not work for this one (b1de4866, 2026-10-12)
    me = a.host or host()
    text = None if a.file else text_from_git(a.git_ref)
    root = Path(a.root) if a.root else (Path.cwd() if text is not None else None)
    try:   # the QUEUE line is information: it must never stop a kick
        qtext = Path(a.file).read_text(encoding="utf-8") if a.file else text
        qinfo["q"] = queue_info(qtext, me, root or root_of(a, a.file), None if a.file else a.git_ref.split(":", 1)[0])
    except Exception as e:
        log("queue_error", error=str(e)[:200])
    for e in lint_file(a.file or "x", "go", root, me, text):
        if e.startswith(HOST_ERR):
            return idle("no unblocked task for host %s (%s)" % (me, e.split(": ", 1)[-1]))
        if e.startswith(NONE_ERR):  # only DONE/blocked rows: a KICK would pay for an empty session (RV08)
            return idle("no unblocked open task in handoff %s" % hid)
    q = qinfo.get("q")
    if q and not q["runnable"] and not q["looks"] and (q["lane"]["CODEX"] or q["lane"]["DSA"]):   # open work is all on a lane: no Claude session for it
        return idle("no Claude-runnable task: open work is on lane CODEX (%s) / DSA (%s)%s" % (
            ",".join(q["lane"]["CODEX"]) or "-", ",".join(q["lane"]["DSA"]) or "-", "; run `relay.py route` to post it" if q["unposted"] else ""))
    prev = read_lock()
    if prev:
        age = now() - prev["_t"]
        if age < timedelta(minutes=ACTIVE_MIN):
            return idle("a launch %d min ago, chain is moving" % (age.total_seconds() // 60))
        if prev.get("id") == hid and age < timedelta(hours=STALE_H):
            return idle("handoff %s launched %d min ago, session still on it" % (hid, age.total_seconds() // 60))
    home().mkdir(parents=True, exist_ok=True)
    (home() / "mts-relay-lock.json").write_text(json.dumps({"utc": now().strftime(TS), "id": hid, "depth": depth}), encoding="utf-8", newline="\n")
    log("kick", id=hid, depth=depth)
    print("KICK depth=%d id=%s" % (depth, hid))
    if q:
        print(queue_line(q))
    return 0


# ---- queue awareness + lane routing (operator 2026-10-14) -----------------------------------------------------------

DESK_DIR = "MyTradingSys/system/desk_queue"
CARD_DIR = "MyTradingSys/system/tasks"
ROUTED_NAME = "mts-relay-routed.json"   # per host, in home(): {task key: {lane, ref, utc}}; the lane artifact (row/card relay_key) is the shared record
BLOCK_DSA = re.compile(r"desk row|\bDSA\b", re.I)
BLOCK_OP = re.compile(r"operator|\bJIS\b|decision|control room", re.I)
AFTER = re.compile(r"^\(after([^)]*)\)", re.I)


def sched_import(name, root=None):
    """Import a sibling script: scripts/sched next to this file, else (a copy run from %TEMP%) the tree's scripts/sched or scripts/dev."""
    import importlib
    here = Path(__file__).resolve().parent
    for d in (here, here.parent / "dev", Path(root or ".") / "scripts" / "sched", Path(root or ".") / "scripts" / "dev"):
        if (d / (name + ".py")).is_file():
            if str(d) not in sys.path:
                sys.path.insert(0, str(d))
            return importlib.import_module(name)
    raise ImportError(name)


def parse_queue(text):
    hl = sched_import("handoff_lint")
    lines = hl.block_lines(text or "")
    tasks = hl.parse_tasks(lines) if lines else []
    for t in tasks:   # a copy run from a tree whose handoff_lint predates lane= (the dispatcher's live tree lagged origin): read the tag here
        if "lane" not in t:
            m = re.match(r"^(?:lane=(\w+)\s*)", t["first"], re.I)
            t["lane"] = m.group(1).upper() if m else None
            if m:
                t["first"] = t["first"][m.end():]
                t["state"] = "done" if t["first"].startswith("DONE") else "blocked" if t["first"].startswith("(after") else "open"
    return tasks


def task_key(t):
    """Stable id of one task line, so a lane task is posted once: its Qn plus a hash of its text."""
    import hashlib
    return "%s-%s" % (t["id"].lower(), hashlib.sha1("\n".join(t["lines"]).encode("utf-8")).hexdigest()[:8])


def read_routed():
    try:
        return json.loads((home() / ROUTED_NAME).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def lane_rows(root, ref=None):
    """Desk rows and cards that relay `route` posted: [{kind, id, key, lane, status}] from the tree or from a git ref."""
    texts = []
    if ref:
        r = subprocess.run(["git", "-C", str(root), "grep", "-l", '"relay_key"', ref, "--", DESK_DIR, CARD_DIR],
                           capture_output=True, text=True, encoding="utf-8", timeout=60)
        for ln in r.stdout.splitlines():
            n = ln.split(":", 1)[1] if ":" in ln else ""
            s = subprocess.run(["git", "-C", str(root), "show", "%s:%s" % (ref, n)], capture_output=True, text=True, encoding="utf-8", timeout=60)
            texts.append((n, s.stdout))
    else:
        for d in (DESK_DIR, CARD_DIR):
            for p in sorted((Path(root) / d).glob("*.json")) if (Path(root) / d).is_dir() else []:
                s = p.read_text(encoding="utf-8")
                if '"relay_key"' in s:
                    texts.append((d + "/" + p.name, s))
    out = []
    for n, s in texts:
        try:
            d = json.loads(s)
        except ValueError:
            continue
        if d.get("relay_key"):
            desk = n.startswith(DESK_DIR)
            out.append({"kind": "desk" if desk else "card", "id": d["id"], "key": d["relay_key"],
                        "lane": "DSA" if desk else "CODEX", "status": d.get("status") if desk else d.get("state", "")})
    return out


def codex_look(root):
    """Lines under `codex_run.py status` NEEDS A LOOK; 0 on a host that has no lab (the lab runs on JIS-NUC) or when it cannot be read."""
    if os.environ.get("MTS_RELAY_NOCODEX"):
        return 0
    script = Path(root) / "scripts" / "dev" / "codex_run.py"
    if not script.is_file() or not (Path(os.environ.get("CODEX_HOME") or "F:/codex_home") / "lab_runs").is_dir():
        return 0
    try:
        r = subprocess.run([sys.executable, str(script), "status"], capture_output=True, text=True, encoding="utf-8", timeout=30, cwd=str(root))
    except (OSError, subprocess.SubprocessError):
        return 0
    n, on = 0, False
    for ln in r.stdout.splitlines():
        if "NEEDS A LOOK:" in ln:
            on = True
        elif on and ln.strip().startswith("- "):
            n += 1
    return n


def queue_info(text, me, root=None, ref=None):
    """Count the handoff's Qn tasks by why they wait. Uses handoff_lint's parser (one parser). Buckets are exclusive, first match wins:
    done, blocked (operator/JIS | DSA desk row | other), lane CODEX/DSA (open, run by that lane), other host, runnable (a Claude session can take it now)."""
    hl = sched_import("handoff_lint")
    tasks = parse_queue(text)
    q = {"total": len(tasks), "done": [], "runnable": [], "host": {}, "operator": [], "dsa_row": [], "blocked": [],
         "lane": {"CODEX": [], "DSA": []}, "unposted": [], "looks": [], "codex_look": 0, "me": me}
    routed = read_routed()
    for t in tasks:
        if t["state"] == "done":
            q["done"].append(t["id"])
        elif t["state"] == "blocked":
            why = (AFTER.match(t["first"]) or [None, t["first"]])[1]
            q["dsa_row" if BLOCK_DSA.search(why) else "operator" if BLOCK_OP.search(why) else "blocked"].append(t["id"])
        elif t["lane"] in ("CODEX", "DSA"):
            q["lane"][t["lane"]].append(t["id"])
            if task_key(t) not in routed:
                q["unposted"].append(t["id"])
        elif not hl.runs_on(t, me):
            q["host"].setdefault(t["host"], []).append(t["id"])
        else:
            q["runnable"].append(t["id"])
    open_lane = {task_key(t): t["id"] for t in tasks if t["state"] == "open" and t["lane"] in ("CODEX", "DSA")}
    if root is not None and open_lane:
        for r in lane_rows(root, ref):
            if r["key"] in open_lane and r["status"] in ("done", "failed", "dropped"):
                q["looks"].append("%s %s %s" % (open_lane[r["key"]], r["kind"], r["status"]))
    if root is not None:
        q["codex_look"] = codex_look(root)
    return q


def queue_line(q):
    host = ", ".join("host=%s %d" % (h, len(v)) for h, v in sorted(q["host"].items())) or "host=other 0"
    lane = q["lane"]
    return ("QUEUE total=%d runnable=%d%s | waiting: %s, operator/JIS %d, DSA desk row %d, other blocked %d | lane CODEX %d, lane DSA %d%s"
            " | DONE %d | look=%d%s%s | for %s"
            % (q["total"], len(q["runnable"]), " (%s)" % ",".join(q["runnable"]) if q["runnable"] else "", host, len(q["operator"]),
               len(q["dsa_row"]), len(q["blocked"]), len(lane["CODEX"]), len(lane["DSA"]),
               " (%d not posted yet: run route)" % len(q["unposted"]) if q["unposted"] else "", len(q["done"]), len(q["looks"]),
               " [%s]" % "; ".join(q["looks"]) if q["looks"] else "", " codex_look=%d" % q["codex_look"] if q["codex_look"] else "", q["me"]))


def root_of(a, file=None):
    if getattr(a, "root", None):
        return Path(a.root)
    p = Path(file).resolve() if file else None
    return p.parents[2] if p is not None and len(p.parents) > 2 else Path.cwd()


def task_body(t):
    return " ".join(ln.strip() for ln in t["lines"])


def done_when(t):
    m = re.search(r"DONE when:\s*(.*)$", task_body(t))
    return (m.group(1) if m else task_body(t))[:380]


def post_lane(t, key, root, ship):
    """Post one open lane task to its lane: a desk row (DSA) or a raw lane-CODEX task card (CODEX), both carrying relay_key.
    Returns (ref, note). Skips when a row/card with this key already exists (another host posted it)."""
    desk = sched_import("desk", root)
    tasks_mod = sched_import("tasks", root)
    body = task_body(t)
    with desk.writable(str(root), ship) as wt:
        for r in lane_rows(wt):
            if r["key"] == key:
                return r["id"], "exists"
        title = "%s %s" % (t["id"], re.sub(r"\s+", " ", t["first"])[:70])
        if t["lane"] == "DSA":
            rid = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-") + re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40]
            req = {"id": rid, "title": title, "need": body[:1500], "done_when": done_when(t), "target": "DSA", "from": host(),
                   "posted": now().strftime(TS), "status": "pending", "relay_key": key}
            desk.save(wt, req)
            desk.commit_ship(wt, req, "desk task: %s\n\nResult: task %s queued for DSA (relay route %s)\n" % (title, rid, key), ship)
            return rid, "posted"
        cid = "relay-" + key
        card = tasks_mod.blank(cid, title, lane="CODEX")
        card.update(goal=body[:380], done_when=done_when(t), steps=[body[:380]], relay_key=key,
                    scope_in=sorted(set(sched_import("handoff_lint").PATH.findall(body)))[:6],
                    note="posted by relay.py route from %s of NEXT_SESSION.md; refiner: set kind, size, scope, then tasks.py check" % t["id"])
        tasks_mod.save(wt, card)
        rel = "%s/%s.json" % (CARD_DIR, cid)
        desk.sh(wt, "add", "--", rel)
        desk.sh(wt, "commit", "-q", "-m", "task card: %s (lane CODEX)\n\nResult: card %s created by relay route %s\n" % (title, cid, key), "--", rel)
        if ship:
            desk.run_ship(wt)
        return cid, "posted"


def cmd_route(a):
    """T0 step before kick: post every open lane-tagged task (lane=CODEX, lane=DSA) to its lane exactly once. The task stays in the
    handoff (a Claude session closes it when the result is read), but `kick` no longer counts it as Claude work."""
    text = Path(a.file).read_text(encoding="utf-8") if a.file else text_from_git(a.git_ref)
    if text is None:
        print("ROUTE ERROR cannot read the handoff")
        return 2
    root = root_of(a, a.file)
    routed = read_routed()
    todo = [t for t in parse_queue(text) if t["state"] == "open" and t["lane"] in ("CODEX", "DSA") and task_key(t) not in routed]
    if not todo:
        print("ROUTE nothing to post")
        return 0
    out = []
    for t in todo:
        key = task_key(t)
        try:
            ref, note = post_lane(t, key, root, not a.no_ship)
        except (SystemExit, Exception) as e:   # fail closed: not recorded, so the next tick retries
            out.append("%s %s ERROR %s" % (t["id"], t["lane"], str(e)[:160]))
            continue
        routed[key] = {"lane": t["lane"], "ref": ref, "task": t["id"], "utc": now().strftime(TS)}
        log("route", task=t["id"], lane=t["lane"], ref=ref, note=note)
        out.append("%s %s %s %s" % (t["id"], t["lane"], note, ref))
    home().mkdir(parents=True, exist_ok=True)
    (home() / ROUTED_NAME).write_text(json.dumps(routed, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    print("ROUTE " + "; ".join(out))
    return 1 if any(" ERROR " in o for o in out) else 0


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


def _sh(argv, cwd):
    r = subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


def begin_fail(why):
    print("BEGIN FAILED: " + why.strip().splitlines()[-1][:300] if why.strip() else "BEGIN FAILED")
    return 1


CARD_LINE = re.compile(r"^(\S+) \[([A-Z0-9-]+),")   # a `tasks.py next` line: <id> [<lane>, <size>, p<prio>] <title>


def dev_module(name, *roots):
    """scripts/dev/<name>.py beside this file, else under each of `roots` (the begin worktree). The dispatcher runs a copy of this file
    from %TEMP%, where there is no sibling scripts/dev (2026-10-14: BEGIN FAILED after the worktree and `sync.py start` had run)."""
    import importlib
    for d in [Path(__file__).resolve().parents[1] / "dev"] + [Path(r) / "scripts" / "dev" for r in roots]:
        if (d / (name + ".py")).is_file():
            if str(d) not in sys.path:
                sys.path.insert(0, str(d))
            return importlib.import_module(name)
    raise ImportError("no scripts/dev/%s.py beside relay.py or under %s" % (name, ", ".join(str(r) for r in roots) or "-"))


def pick_card(out, skip, claimed, lanes, slug):
    """(card id, held) from `tasks.py next` output: the first card whose lane is exactly one of `lanes` (DSA, DSA-NB, DSA-NUC, JIS-NB
    and CODEX are run or lab lanes, never a builder's), that is not in `skip` and that no open claim holds (`claimed` = claim slugs,
    `slug` = sync.slugify). `held` counts the builder-lane cards passed over because of a claim."""
    held = 0
    for line in out.splitlines():
        m = CARD_LINE.match(line)
        if not m or m.group(2) not in lanes or m.group(1) in skip:
            continue
        if slug(m.group(1)) in claimed:
            held += 1
            continue
        return m.group(1), held
    return None, held


def cmd_begin(a):
    """B172 cut 2: the whole ritual (relay worktree, sync start, first ready card of a builder lane that no claim holds, claim,
    brief) in one call. Builder lanes = tasks.CODE_LANES minus OPUS (the operator names Opus). Fails closed: any sync/claim
    error prints one line, exits 1 and names no task."""
    root = Path(a.root or os.getcwd()).resolve()
    wt = Path(a.worktree).resolve() if a.worktree else root.parent / "mts-relay"
    branch = a.branch or (host().lower() + "/relay")
    rc, out = _sh(["git", "fetch", "-q", "origin", "fast-track"], root)
    if rc:
        return begin_fail("fetch: " + out)
    if wt.exists():
        rc, out = _sh(["git", "merge", "-q", "--ff-only", "origin/fast-track"], wt)
        if rc:
            return begin_fail("relay tree not fast-forwardable (leftover work?): " + out)
    else:
        rc, out = _sh(["git", "worktree", "add", str(wt), "-b", branch, "origin/fast-track"], root)
        if rc:
            rc, out = _sh(["git", "worktree", "add", str(wt), branch], root)
            if rc:
                return begin_fail("worktree add: " + out)
            rc, out = _sh(["git", "merge", "-q", "--ff-only", "origin/fast-track"], wt)
            if rc:
                return begin_fail("relay branch not fast-forwardable: " + out)
    rc, out = _sh([sys.executable, "scripts/dev/sync.py", "start"], wt)
    if rc:
        return begin_fail("sync start: " + out)
    sync_lines = [l for l in out.splitlines() if l.strip()]
    m = re.search(r"^WORKTREE:\s*(.+)$", out, re.M)
    if m:   # sync.py moved us to a clean per-session tree; work only there
        wt = Path(m.group(1).strip())
    try:
        sync, tasks = dev_module("sync", wt, root), dev_module("tasks", wt, root)
    except ImportError as e:
        return begin_fail("scripts/dev: %s" % e)
    lanes = [l for l in tasks.CODE_LANES if l != "OPUS"]
    try:
        claimed = {s for s, _ in sync.read_claims(wt, "origin/" + sync.TRUNK)}   # as of the fetch above; `claim` below stays the lock
    except (OSError, sync.SyncError) as e:
        return begin_fail("claims: %s" % e)
    rc, out = _sh([sys.executable, "scripts/dev/tasks.py", "next", "--n", "10"], wt)
    if rc:
        return begin_fail("no ready card: " + out)
    pick, held = pick_card(out, a.skip, claimed, lanes, sync.slugify)
    if not pick:
        print("worktree: %s" % wt)   # a `look=` wake-up still edits the handoff in this synced tree (relay_session.md step 1)
        return begin_fail("no ready %s card free to take (%d held by an open claim; hand off with --stop)" % ("/".join(lanes), held))
    rc, out = _sh([sys.executable, "scripts/dev/sync.py", "claim", pick], wt)
    if rc:
        return begin_fail("claim %s: %s" % (pick, out))
    rc, brief = _sh([sys.executable, "scripts/dev/tasks.py", "brief", pick], wt)
    if rc:
        return begin_fail("brief %s: %s" % (pick, brief))
    print("worktree: %s" % wt)
    print("sync: " + " | ".join(l[:90] for l in sync_lines[-3:]))
    print("claimed: %s (release: sync.py release %s)" % (pick, pick))
    for line in brief.splitlines()[:22]:
        print(line[:400])
    log("begin", card=pick)
    return 0


# ---- tick: the dispatcher's one call (2026-10-15) ---------------------------------------------------------------------
# The App bills a full session per cron run (~78k tokens first turn) and every extra model call re-reads it, so everything
# deterministic happens here, in T0: fetch, route, kick, the QUEUE line, the hourly gate, refiner status, prompt drift.

HOURLY_NAME = "mts-hourly.json"   # {last_utc, last_housekeep_utc}: the hourly bundle runs once per HOURLY_MIN, whatever the cron jitter
SESSION_REF = "origin/fast-track:scripts/sched/relay_prompts/relay_session.md"
PROMPT_REF = "origin/fast-track:scripts/sched/relay_prompts/mts-dispatcher.SKILL.md"
SKILL_REL = Path("scheduled-tasks") / "mts-dispatcher" / "SKILL.md"   # under home(): the prompt the App actually runs


def captured(fn, ns):
    """(exit code, stdout, child output) of a cmd_* function. Its prints are collected, and so is anything a child process writes to
    fd 1/2 (route runs `sync.py ship` with inherited streams): tick prints ONE line, nothing may land before it. An exception becomes
    (3, 'ERROR ...', ...) so tick always answers."""
    import contextlib
    import io
    import tempfile
    sys.stdout.flush()
    sys.stderr.flush()
    saved = os.dup(1), os.dup(2)
    child = tempfile.TemporaryFile(mode="w+b")
    buf = io.StringIO()
    try:
        os.dup2(child.fileno(), 1)
        os.dup2(child.fileno(), 2)
        try:
            with contextlib.redirect_stdout(buf):
                rc = fn(ns)
        except (SystemExit, Exception) as e:
            rc = 3
            buf.write("ERROR %s: %s" % (type(e).__name__, str(e)[:160]))
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
        os.dup2(saved[0], 1)
        os.dup2(saved[1], 2)
        os.close(saved[0])
        os.close(saved[1])
    child.seek(0)
    out = child.read().decode("utf-8", "replace")
    child.close()
    return rc, buf.getvalue().strip(), out


def last_line(text, width=160):
    lines = [ln for ln in (text or "").strip().splitlines() if ln.strip()]
    return lines[-1].strip()[:width] if lines else ""


def minutes_since(iso):
    try:
        return (now() - datetime.fromisoformat(iso.replace("Z", "+00:00"))).total_seconds() / 60
    except (ValueError, AttributeError, TypeError):
        return None


def read_hourly():
    try:
        return json.loads((home() / HOURLY_NAME).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def refine_status(root, tree=None):
    """`REFINE_OK` | `REFINE_NEEDED` | `ERROR <why>` from the refiner worktree (../mts-refiner): create or fetch+merge it, then run its own
    `tasks.py status`. Shells out inside that worktree: this file may be a %TEMP% copy with no sibling scripts/dev."""
    wt = Path(tree) if tree else Path(root).resolve().parent / "mts-refiner"
    if wt.exists():
        rc, out = _sh(["git", "fetch", "-q", "origin"], wt)
        if rc:
            return "ERROR fetch: " + last_line(out)
        rc, out = _sh(["git", "merge", "-q", "origin/fast-track"], wt)
        if rc:
            _sh(["git", "merge", "--abort"], wt)   # leave the tree as it was; never force
            return "ERROR merge: " + last_line(out)
    else:
        branch = re.sub(r"[^a-z0-9]", "", host().lower()) + "/refiner"
        rc, out = _sh(["git", "worktree", "add", str(wt), "-b", branch, "origin/fast-track"], root)
        if rc:
            rc, out = _sh(["git", "worktree", "add", str(wt), branch], root)   # the branch survived an earlier worktree
            if rc:
                return "ERROR worktree add: " + last_line(out)
    rc, out = _sh([sys.executable, "scripts/dev/tasks.py", "status"], wt)
    m = re.search(r"\bREFINE_(OK|NEEDED)\b", out)
    return "REFINE_" + m.group(1) if m else "ERROR tasks.py status: " + last_line(out)


def prompt_drift(root, prompt_file=None):
    """` drift=SKILL ...` when the installed dispatcher prompt (home()/scheduled-tasks/mts-dispatcher/SKILL.md) differs from origin's
    copy (relay_prompts/mts-dispatcher.SKILL.md); '' when equal, when no prompt is installed on this host, or when origin has none.
    Read-only. CRLF, the trailing newline and the per-host `--peer-quiet-min N` are ignored."""
    import hashlib
    inst = home() / SKILL_REL
    if not inst.is_file():
        return ""
    try:
        inst_text = inst.read_text(encoding="utf-8")
        if prompt_file:
            repo_text = Path(prompt_file).read_text(encoding="utf-8")
        else:
            r = subprocess.run(["git", "-C", str(root), "show", PROMPT_REF], capture_output=True, text=True, encoding="utf-8", timeout=60)
            repo_text = r.stdout if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError, UnicodeError):
        return ""
    if repo_text is None:
        return ""

    def digest(t):
        return hashlib.sha1(re.sub(r"--peer-quiet-min \d+", "--peer-quiet-min N", t.replace("\r\n", "\n")).strip().encode("utf-8")).hexdigest()[:8]
    a, b = digest(inst_text), digest(repo_text)
    return "" if a == b else "drift=SKILL installed=%s origin=%s (install: relay_prompts/INSTALL.md)" % (a, b)


def hourly_bundle(a, root):
    """(refine, housekeep) once per HOURLY_MIN, else None. refine = REFINE_OK | REFINE_NEEDED | SKIPPED | ERROR <why>; housekeep = bool
    (due once per HOUSEKEEP_H). The state is written before the answer, so a slow or failed model step never repeats within the hour."""
    st = read_hourly()
    gate = getattr(a, "gate", False)   # model-free gate (dispatch_gate.py): own clock, never takes the App routine's housekeeping slot
    key = "last_gate_utc" if gate else "last_utc"
    since = minutes_since(st.get(key))
    if since is not None and since < a.hourly_min:
        return None
    st[key] = now().strftime(TS)
    hk_since = minutes_since(st.get("last_housekeep_utc"))
    housekeep = not gate and (hk_since is None or hk_since >= HOUSEKEEP_H * 60)
    if housekeep:
        st["last_housekeep_utc"] = st[key]
    try:
        home().mkdir(parents=True, exist_ok=True)
        (home() / HOURLY_NAME).write_text(json.dumps(st, sort_keys=True), encoding="utf-8", newline="\n")
    except OSError:
        pass
    if (home() / "mts-relay-stop").exists():
        return "SKIPPED", housekeep
    return refine_status(root, a.refiner_tree), housekeep


def _budget_state():
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import budget
        return budget.state(now())
    except Exception as e:   # pacing must never take the tick down
        return "NORMAL", "budget error %s" % type(e).__name__


def cmd_tick(a):
    """The dispatcher's whole idle path in one call: fetch, route, kick, the QUEUE line, prompt drift and (once per hour, only when
    this host is not waiting on a peer and no session was kicked) the refiner status. Prints ONE `TICK NOOP|KICK ...` line (plus an
    `HOURLY ...` line only when the model has work to do). On KICK it appends the exact commands and relay_session.md. Exit 0 always."""
    root = Path(a.root or os.getcwd()).resolve()
    flags = []
    if not a.file:   # a local --file handoff has nothing to fetch
        rc, out = _sh(["git", "fetch", "-q", "origin", "fast-track"], root)
        if rc:
            flags.append("fetch=STALE")
    ns = argparse.Namespace(file=a.file, git_ref=a.git_ref, root=a.root, no_ship=a.no_ship, host=a.host, peer_quiet_min=a.peer_quiet_min)
    route_rc, route_out, route_child = captured(cmd_route, ns)
    route = re.sub(r"^ROUTE ", "", (route_out.splitlines() or ["?"])[0])[:160]
    if route_rc and last_line(route_child, 100):
        route += " [" + last_line(route_child, 100) + "]"   # why a post or ship failed: the child's last line
    bstate, _bwhy = _budget_state()
    if bstate == "THROTTLE":   # SUPER_SESSION.md Pacing: the weekly meter says wait; kick would record a launch nobody makes
        rc, kick_lines, verdict = 0, [], "IDLE budget=THROTTLE"
    else:
        rc, kick_out, _ = captured(cmd_kick, ns)
        kick_lines = kick_out.splitlines()
        verdict = kick_lines[0] if kick_lines else "ERROR kick printed nothing"
    queue = next((ln[len("QUEUE "):] for ln in kick_lines if ln.startswith("QUEUE ")), "")   # absent on the early IDLEs (stop flag, no header)
    is_kick = rc == 0 and verdict.startswith("KICK ")
    drift = prompt_drift(root, a.prompt_file)
    if drift:
        flags.append(drift)
    extra = []
    if not is_kick and not verdict.startswith("IDLE peer "):   # a peer host is moving: skip every extra, like the old step 4 early exit
        bundle = hourly_bundle(a, root)
        if bundle:
            refine, housekeep = bundle
            if refine in ("REFINE_OK", "SKIPPED"):
                flags.append("refine=" + ("OK" if refine == "REFINE_OK" else "SKIPPED"))
            todo = [] if refine in ("REFINE_OK", "SKIPPED") else ["refine=" + refine]
            if housekeep:
                todo.append("housekeep=yes")
            if todo:
                extra.append("HOURLY " + " ".join(todo))
    flags.append("budget=" + bstate)
    head = "TICK " + (verdict if is_kick else "NOOP | " + re.sub(r"^IDLE ", "", verdict))
    print(" | ".join([head, "route=" + route] + flags + (["queue=" + queue] if queue else [])))
    me = Path(__file__).resolve().as_posix()
    if is_kick:
        print('NEXT: python "%s" begin --root "%s"' % (me, root.as_posix()))
        print('UNLOCK: python "%s" unlock' % me)
        text = None
        if a.session_file:
            text = Path(a.session_file).read_text(encoding="utf-8")
        else:
            r = subprocess.run(["git", "-C", str(root), "show", SESSION_REF], capture_output=True, text=True, encoding="utf-8", timeout=60)
            text = r.stdout if r.returncode == 0 else None
            if text is None and (Path(__file__).resolve().parent / "relay_prompts" / "relay_session.md").is_file():
                text = (Path(__file__).resolve().parent / "relay_prompts" / "relay_session.md").read_text(encoding="utf-8")
        print("--- relay_session.md (follow it exactly) ---")
        print(text.strip() if text else "relay_session.md unreadable: run `git show %s`, follow it, and report relay=ERROR" % SESSION_REF)
    for ln in extra:
        print(ln)
    return 0


def cmd_heartbeat(a):
    """The super-session coordinator rewrites ~/.claude/mts-super-heartbeat.json on every wake."""
    home().mkdir(parents=True, exist_ok=True)
    row = {"coordinator": a.coordinator, "host": host(), "utc": now().strftime(TS), "note": a.note}
    (home() / HEARTBEAT_NAME).write_text(json.dumps(row, sort_keys=True), encoding="utf-8", newline="\n")
    print("HEARTBEAT", row["utc"], a.coordinator)
    return 0


def do_resume(event="operator_resume", **kw):
    (home() / "mts-relay-stop").unlink(missing_ok=True)
    log(event, **kw)


def watchdog():
    """Lift a dead coordinator's stop. Only a stop whose reason starts with `super-session` is ever touched (an operator stop never);
    a missing / unreadable / malformed / old heartbeat counts as stale. Returns a one-line verdict."""
    flag = home() / "mts-relay-stop"
    try:
        why = flag.read_text(encoding="utf-8").strip() if flag.exists() else None
    except (OSError, UnicodeError):
        return "WATCHDOG NOOP stop flag unreadable"   # cannot prove it is a super-session stop: leave it
    if why is None:
        return "WATCHDOG NOOP relay not stopped"
    if not why.startswith(SUPER_PREFIX):
        return "WATCHDOG NOOP operator stop"
    who, age = "none", None
    try:
        hb = json.loads((home() / HEARTBEAT_NAME).read_text(encoding="utf-8"))
        who = str(hb["coordinator"])
        age = (now() - datetime.strptime(hb["utc"], TS).replace(tzinfo=timezone.utc)).total_seconds() / 60
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        age = None   # missing or malformed
    if age is not None and age <= SUPER_STALE_MIN:
        return "WATCHDOG NOOP heartbeat fresh %.0fmin (%s)" % (age, who)
    age_s = "unreadable" if age is None else "%.0fmin" % age
    do_resume("watchdog_resume", who=who, why="stale heartbeat", heartbeat_age=age_s, stop=why[:120])
    return "WATCHDOG RESUMED %s heartbeat %s" % (who, age_s)


def cmd_watchdog(a):
    print(watchdog())
    return 0


def cmd_status(a):
    print("header:", read_header(a.file))
    flag = home() / "mts-relay-stop"
    print("stop flag:", flag.read_text(encoding="utf-8").strip() if flag.exists() else "none")
    try:
        print(queue_line(queue_info(Path(a.file).read_text(encoding="utf-8"), a.host or host(), root_of(a, a.file))))
    except Exception as e:   # fail soft: a QUEUE problem must never hide the header/stop-flag lines or take kick down
        print("QUEUE ? (%s: %s)" % (type(e).__name__, str(e)[:120]))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("handoff")
    h.add_argument("--file", required=True)
    g = h.add_mutually_exclusive_group(required=True)
    g.add_argument("--go", action="store_true")
    g.add_argument("--stop")
    h.add_argument("--host", help="lint want=go for this host only (default: none, any host may run it)")
    h.add_argument("--reset-depth", action="store_true")
    h.add_argument("--session", help="title of this App session, recorded in relay_runs.jsonl so the chat can be found later")
    li = sub.add_parser("lint")
    li.add_argument("--file", required=True)
    li.add_argument("--want", choices=["go", "stop"], default="go")
    li.add_argument("--root")
    li.add_argument("--host", help="count only tasks that can run on this host (default: none)")
    k = sub.add_parser("kick")
    k.add_argument("--file")
    k.add_argument("--git-ref", default=KICK_REF)
    k.add_argument("--host", help="override this machine's name (tests); default MTS_RELAY_HOST or the node name")
    k.add_argument("--root", help="tree for the task-path checks (default: cwd)")
    k.add_argument("--peer-quiet-min", type=int, default=0,
                   help="IDLE while another host wrote the current handoff less than this many minutes ago (0 = off)")
    br = sub.add_parser("brief")
    br.add_argument("--file", required=True)
    br.add_argument("--max", type=int, default=3)
    br.add_argument("--width", type=int, default=400)
    bg = sub.add_parser("begin")
    bg.add_argument("--root", help="repo folder to run from (default: cwd)")
    bg.add_argument("--worktree", help="relay tree (default: ../mts-relay)")
    bg.add_argument("--branch", help="branch for a new relay tree (default: <host>/relay)")
    bg.add_argument("--skip", action="append", default=[], help="card id to pass over (repeatable)")
    st = sub.add_parser("status")
    st.add_argument("--file", required=True)
    st.add_argument("--host", help="count runnable tasks for this host (default: this machine)")
    st.add_argument("--root", help="tree holding desk_queue/ and tasks/ (default: two levels above --file)")
    ro = sub.add_parser("route")
    ro.add_argument("--file")
    ro.add_argument("--git-ref", default=KICK_REF)
    ro.add_argument("--root", help="tree to post from (default: cwd; the live tree posts through a scratch worktree off origin)")
    ro.add_argument("--no-ship", action="store_true", help="commit the row/card but do not run sync.py ship (tests)")
    ti = sub.add_parser("tick", help="the dispatcher's one call: fetch, route, kick, hourly gate, one TICK NOOP|KICK line")
    ti.add_argument("--file", help="local handoff instead of origin's (tests; skips the fetch)")
    ti.add_argument("--git-ref", default=KICK_REF)
    ti.add_argument("--host", help="override this machine's name (tests)")
    ti.add_argument("--root", help="repo folder (default: cwd); the refiner tree is ../mts-refiner beside it")
    ti.add_argument("--peer-quiet-min", type=int, default=0,
                    help="IDLE while another host wrote the current handoff less than this many minutes ago (0 = off)")
    ti.add_argument("--hourly-min", type=int, default=HOURLY_MIN, help="minutes between two hourly bundles (refiner status, housekeeping)")
    ti.add_argument("--gate", action="store_true", help="called by dispatch_gate.py: hourly refiner status on its own clock, no housekeeping")
    ti.add_argument("--no-ship", action="store_true", help="route: commit the row/card but do not run sync.py ship (tests)")
    ti.add_argument("--refiner-tree", help="refiner worktree (default: ../mts-refiner)")
    ti.add_argument("--prompt-file", help="repo copy of the dispatcher prompt for the drift check (default: origin's, via git show)")
    ti.add_argument("--session-file", help="relay_session.md text printed on KICK (default: origin's, via git show)")
    sub.add_parser("unlock", help="free the launch lock: last action of a KICK session, not after --stop")
    sp = sub.add_parser("stop")
    sp.add_argument("why")
    sub.add_parser("resume")
    hb = sub.add_parser("heartbeat", help="super-session coordinator liveness (rewrite on every wake)")
    hb.add_argument("coordinator")
    hb.add_argument("--note", default="")
    sub.add_parser("watchdog", help="resume if a super-session stop has a stale heartbeat (run by dispatch_gate.py)")
    a = ap.parse_args(argv)
    if a.cmd == "handoff":
        return cmd_handoff(a)
    if a.cmd == "lint":
        return cmd_lint(a)
    if a.cmd == "tick":
        return cmd_tick(a)
    if a.cmd == "heartbeat":
        return cmd_heartbeat(a)
    if a.cmd == "watchdog":
        return cmd_watchdog(a)
    if a.cmd == "unlock":
        return cmd_unlock(a)
    if a.cmd == "status":
        return cmd_status(a)
    if a.cmd == "brief":
        return cmd_brief(a)
    if a.cmd == "kick":
        return cmd_kick(a)
    if a.cmd == "route":
        return cmd_route(a)
    if a.cmd == "begin":
        return cmd_begin(a)
    home().mkdir(parents=True, exist_ok=True)
    flag = home() / "mts-relay-stop"
    if a.cmd == "stop":
        flag.write_text(a.why, encoding="utf-8", newline="\n")
        log("operator_stop", reason=a.why)
    else:
        do_resume()
    return 0


if __name__ == "__main__":
    sys.exit(main())
