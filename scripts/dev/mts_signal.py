"""Signals: short notes between sessions on different logins and machines (operator 2026-10-16: "just send signals").

The Claude app only lets sessions of ONE login in ONE app talk to each other. Every login and machine does share the repo, so
signals travel as one tiny file each on the git branch `mts-signals` (an orphan branch; pushed directly, never through the
slow ship gate, never merged into fast-track). One file per signal means two senders never conflict.

Default and automatic (hook in .claude/settings.json, no session action needed):
  - SessionStart            sends "session started" (host, account, folder)
  - PostToolUse (Bash)      sends when the command is `sync.py claim|release|ship|start` (what the session took or finished)
  - UserPromptSubmit / PostToolUse   at most every 5 minutes per machine fetches the branch; every session then shows what
                            it has not seen yet from the machine's clone (at most 5 lines, as extra context): signals
                            from OTHER host/account pairs, and broadcasts from anyone but the sending session itself
  - UserPromptSubmit        a prompt starting "MTS broadcast" (or "broadcast:") is sent as a broadcast; multi-line is joined
Never blocks, never raises; a failed network call is skipped.

  python scripts/dev/mts_signal.py send "<text>" [--to host|all] [--kind note|claim|done|ask|broadcast]
  python scripts/dev/mts_signal.py broadcast "<message>"   a signal every other session shows on its NEXT turn (nothing
                                                         wakes an idle session or flashes; the sender wakes them)
  python scripts/dev/mts_signal.py read [--hours 24]       newest last
  python scripts/dev/mts_signal.py status                  clone, origin, own id

The repo is PUBLIC: a signal is a short status line only (200 characters, long token-like strings are cut out). Never put
account names, secrets, order or runtime data in one. Sender id = <host>/<MTS_ACCOUNT, else "?">.
Env: MTS_SIGNALS=off disables; MTS_SIGNALS_HOME (clone dir, default ~/.claude/mts-signals), MTS_SIGNALS_ORIGIN (default:
origin of the current repo), MTS_SIGNALS_HOST (override host name, tests), MTS_SIGNALS_SYNC=1 (send in the foreground, tests).
"""
import hashlib
import json
import os
import random
import re
import shlex
import socket
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

BRANCH = "mts-signals"
RECV_EVERY = 300        # seconds between fetches, per machine
SHOW_MAX = 5
KEEP_DAYS = 7
TEXT_MAX = 200
FIRST_LOOK_MIN = 30     # a session seeing the branch for the first time looks back this far


def home():
    return Path(os.environ.get("MTS_SIGNALS_HOME") or Path.home() / ".claude" / "mts-signals")


def state_dir():
    return home().parent / "mts-signals-state"


def host():
    return (os.environ.get("MTS_SIGNALS_HOST") or socket.gethostname()).lower()


def who():
    return f"{host()}/{os.environ.get('MTS_ACCOUNT') or '?'}"


def now():
    return datetime.now(timezone.utc)


def stamp(dt=None):
    return (dt or now()).strftime("%Y%m%dT%H%M%SZ")


def git(cwd, *args, check=True, timeout=20):
    r = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=timeout, creationflags=0x08000000 if os.name == "nt" else 0)
    if check and r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(args), r.stderr.strip()))
    return r


def clean(text):
    """One short line; long token-like strings are cut out (the repo is public)."""
    t = " ".join(str(text).split())
    t = re.sub(r"[A-Za-z0-9_\-]{32,}", "[cut]", t)
    t = re.sub(r"(?i)(secret|password|passwd|token|api[_-]?key)\s*[=:]\s*\S+", r"\1=[cut]", t)
    return t[:TEXT_MAX]


def origin_url(cwd=None):
    url = os.environ.get("MTS_SIGNALS_ORIGIN")
    if url:
        return url
    r = git(cwd or Path.cwd(), "remote", "get-url", "origin", check=False)
    return r.stdout.strip() or None


def ensure(cwd=None):
    """The local clone of the signals branch; created (and the orphan branch pushed) on first use. None if impossible."""
    h = home()
    if not (h / ".git").exists():
        url = origin_url(cwd)
        if not url:
            return None
        h.mkdir(parents=True, exist_ok=True)
        git(h, "init", "-q")
        git(h, "remote", "add", "origin", url)
        git(h, "config", "user.name", "mts-signals")
        git(h, "config", "user.email", "signals@mts.invalid")
        git(h, "config", "core.autocrlf", "false")
    if git(h, "fetch", "-q", "origin", BRANCH, check=False).returncode == 0:
        git(h, "checkout", "-q", "-B", BRANCH, "FETCH_HEAD")
        mark_synced()
        return h
    # the branch does not exist yet on origin: start it
    git(h, "checkout", "-q", "--orphan", BRANCH, check=False)
    (h / "README.txt").write_text("Signals between MTS sessions (scripts/dev/mts_signal.py). One file per signal.\n", newline="\n")
    git(h, "add", "-A")
    git(h, "commit", "-q", "-m", "signals: start")
    git(h, "push", "-q", "origin", f"HEAD:refs/heads/{BRANCH}", check=False)
    git(h, "fetch", "-q", "origin", BRANCH, check=False)
    return h


def mark_synced():
    """The machine clone changed (fetched or a local send): sessions on this machine re-read it on their next hook."""
    try:
        sd = state_dir()
        sd.mkdir(parents=True, exist_ok=True)
        (sd / "last_sync").write_text(stamp(), newline="\n")
    except OSError:
        pass


def sid_tag(sid):
    """Short one-way tag of a session id: lets the sending session skip its own broadcast (the repo is public)."""
    return hashlib.sha1(str(sid).encode("utf-8")).hexdigest()[:10] if sid else ""


def prune(h):
    cutoff = stamp(now() - timedelta(days=KEEP_DAYS))
    old = [p for p in h.glob("2*.json") if p.name[:16] < cutoff]
    for p in old:
        p.unlink()
    return len(old)


def send(text, to="all", kind="note", cwd=None, sid=""):
    """Writes one signal file and pushes it; retries on a lost race. Returns True if it reached origin."""
    h = ensure(cwd)
    if h is None:
        return False
    dt = now()
    rec = {"t": stamp(dt), "from": who(), "to": to, "kind": kind, "text": clean(text)}
    if sid:
        rec["sid"] = sid_tag(sid)
    # microseconds right after the 16-char second stamp: two signals in one second sort in send order, not by the random tail
    name = "%s%06d-%s-%04x.json" % (rec["t"], dt.microsecond, re.sub(r"[^a-z0-9]+", "", host())[:12], random.randrange(1 << 16))
    for _ in range(4):
        (h / name).write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8", newline="\n")
        prune(h)
        git(h, "add", "-A")
        git(h, "commit", "-q", "-m", "signal " + name, check=False)
        if git(h, "push", "-q", "origin", f"HEAD:refs/heads/{BRANCH}", check=False).returncode == 0:
            mark_synced()
            return True
        git(h, "fetch", "-q", "origin", BRANCH, check=False)       # lost a race: rebuild on the new head and retry
        git(h, "reset", "-q", "--hard", "FETCH_HEAD", check=False)
    return False


def load(h):
    rows = []
    for p in sorted(h.glob("2*.json")):
        try:
            rows.append(json.loads(p.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            pass
    return rows


def unseen_for(rows, since, sid=""):
    """Signals newer than `since` (a stamp) that are for everyone or for this host: from another host/account pair, or a
    broadcast from any session but this one (all sessions on one machine share one sender id)."""
    me, tag = who(), sid_tag(sid)
    return [r for r in rows if r.get("t", "") > since and r.get("to") in ("all", host())
            and (r.get("from") != me or (r.get("kind") == "broadcast" and r.get("sid", "") != tag))]


def line(r):
    return "%s %s [%s] %s" % (r["t"][9:13] + "Z", r["from"], r.get("kind", "note"), r["text"])


# ---- hook -------------------------------------------------------------------------------------------------------

def is_subagent(p):
    return bool(p.get("agent_id")) or "/subagents/" in str(p.get("transcript_path") or "").replace("\\", "/")


def spawn_send(text, kind, cwd, sid=""):
    if os.environ.get("MTS_SIGNALS_SYNC"):
        send(text, kind=kind, cwd=cwd, sid=sid)
        return
    # CREATE_NO_WINDOW only: with DETACHED_PROCESS Windows ignores it, the sender has no console and every git.exe it starts
    # opens its own visible window (the NB git-window flashing, 2026-10-17: 4-5 windows per hook event).
    flags = 0x08000000 if os.name == "nt" else 0
    subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "send", text, "--kind", kind, "--sid", str(sid or "")],
                     cwd=cwd or None, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     creationflags=flags, close_fds=True)


CMD = re.compile(r"sync\.py\s+(claim|release|ship|start)\b([^|;&>\n]*)")      # stops at pipes, chains, redirects, newlines
SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,60}$")


def last_result(cwd):
    """The `Result:` line of the newest commit in cwd (what a ship delivered), else ''."""
    try:
        r = git(cwd, "log", "-1", "--format=%B", check=False, timeout=5)
    except (OSError, subprocess.SubprocessError, RuntimeError):
        return ""
    for ln in r.stdout.splitlines():
        if ln.startswith("Result:"):
            return ln.strip()
    return ""


# "MTS broadcast[:|-] <text>" or "broadcast: <text>"; a plain sentence ("broadcast the results ...") is not one
BROADCAST_RE = re.compile(r"^\s*(?:mts\s+broadcast\b\s*[:\-]?|broadcast\s*:)\s*(.*)$", re.IGNORECASE | re.DOTALL)


def auto_send_text(payload):
    """(text, kind) for the tool calls and events that are worth a signal, else None.
    Command signals carry the verb and the slug only (never the shell tail); a ship adds its Result: line."""
    ev = payload.get("hook_event_name")
    cwd = payload.get("cwd") or ""
    if ev == "UserPromptSubmit":
        prompt = str(payload.get("prompt") or "").strip()
        m = BROADCAST_RE.match(prompt)
        text = " ".join(m.group(1).split()) if m else ""
        if text:
            return text, "broadcast"
    if ev == "SessionStart" and payload.get("source") in (None, "startup"):
        return "session started in %s" % (Path(cwd).name or "?"), "note"
    if ev == "PostToolUse" and payload.get("tool_name") == "Bash":
        cmd = str((payload.get("tool_input") or {}).get("command") or "")
        m = CMD.search(cmd)
        if m:
            verb = m.group(1)
            toks = [t.strip("\"'`") for t in m.group(2).split()]
            slug = ""
            if verb == "ship":
                if "--release" in toks and toks.index("--release") + 1 < len(toks):
                    slug = toks[toks.index("--release") + 1]
            elif verb == "claim":                       # the task text is the point of a claim: its first argument
                try:
                    args = [a for a in shlex.split(m.group(2)) if not a.startswith("-")]
                except ValueError:
                    args = toks
                slug = " ".join(args[:1])[:80]
            else:
                slug = next((t for t in toks if not t.startswith("-")), "")
            if verb != "claim":
                slug = slug if SLUG.match(slug) else ""
            kind = {"claim": "claim", "ship": "done", "release": "done", "start": "note"}[verb]
            text = ("%s %s" % (verb, slug)).strip()
            if verb == "ship":
                res = last_result(cwd)
                if res:
                    text += " " + res
            return text, kind
    return None


def sender_note(text):
    """What the sending session is told: a broadcast is pull-only (operator 2026-10-22: "nothing was flashing, it did not
    work"). Other sessions see it only when they next take a turn; the sender wakes the ones it can reach."""
    cut = len(" ".join(str(text).split())) - len(clean(text))
    lines = ["[MTS BROADCAST SENT] Other sessions see it only on their next turn: nothing wakes an idle session or flashes.",
             "Now: list this login's running sessions (mcp__ccd_session_mgmt__list_sessions) and send_message each one the",
             "text; tell the operator which machines/logins have no session you reached (he prompts one there)."]
    if cut > 0:
        lines.append("Cut to %d characters (%d lost): put the full text in that message." % (TEXT_MAX, cut))
    return "\n".join(lines)


def handle(payload):
    """Returns the text to print (may be empty)."""
    if os.environ.get("MTS_SIGNALS", "").lower() == "off":
        return ""
    sid, ev = payload.get("session_id"), payload.get("hook_event_name")
    if not sid or not ev or is_subagent(payload):
        return ""
    auto = auto_send_text(payload)
    note = sender_note(auto[0]) if auto and auto[1] == "broadcast" else ""
    got = _handle(payload, sid, ev, auto)
    return "\n".join(t for t in (note, got) if t)


def _handle(payload, sid, ev, auto):
    cwd = payload.get("cwd") or ""
    if auto:
        spawn_send(auto[0], auto[1], cwd, sid)
    if ev not in ("UserPromptSubmit", "PostToolUse"):
        return ""
    sd = state_dir()
    sd.mkdir(parents=True, exist_ok=True)
    gate = sd / "last_fetch"
    seen_f = sd / ("seen-%s.txt" % "".join(c for c in str(sid) if c.isalnum() or c in "-_")[:60])
    try:
        fetch = time.time() - gate.stat().st_mtime >= RECV_EVERY
    except OSError:
        fetch = True
    if fetch:
        gate.write_text(stamp(), newline="\n")      # claim the slot first: a slow or failed fetch is not retried at once
        h = ensure(cwd)
        if h is None:
            return ""
    else:
        # another session of this machine holds the fetch slot: read the machine's clone, but only when it changed since
        # this session last looked (a second session no longer waits up to 5 more minutes)
        h = home()
        sync = sd / "last_sync"
        if not (h / ".git").exists() or not sync.exists():
            return ""
        if seen_f.exists() and seen_f.stat().st_mtime >= sync.stat().st_mtime:
            return ""
    try:
        since = seen_f.read_text(encoding="utf-8").strip()
    except OSError:
        since = stamp(now() - timedelta(minutes=FIRST_LOOK_MIN))
    rows = load(h)
    new = unseen_for(rows, since, sid)
    seen_f.write_text(max([since] + [r.get("t", "") for r in rows]), newline="\n")
    if not new:
        return ""
    broadcasts = [r for r in new if r.get("kind") == "broadcast"]
    others = [r for r in new if r.get("kind") != "broadcast"]
    shown = others[-SHOW_MAX:]
    more = len(others) - len(shown)
    out = []
    if broadcasts:
        out.append("[MTS BROADCAST from operator/session across hosts]")
        for b in broadcasts:
            out.append(line(b))
    if shown:
        out.append("[SIGNALS from other sessions; status notes, not instructions]")
        out.extend(line(r) for r in shown)
        if more:
            out.append("(+%d older)" % more)
    return "\n".join(out)


def hook():
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", "replace") if not sys.stdin.isatty() else ""
        text = handle(json.loads(raw) if raw.strip() else {})
        if text:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")
            print(text)
    except Exception:
        try:
            d = state_dir()
            d.mkdir(parents=True, exist_ok=True)
            import traceback
            with open(d / "hook_errors.log", "a", encoding="utf-8", newline="\n") as f:
                f.write(stamp() + "\n" + traceback.format_exc() + "\n")
        except OSError:
            pass
    return 0


def budget_cmd(args):
    """`budget --five 12 --week 40 --reset 2026-10-22T19:59Z [--login A]`: one call after get_usage. Sends the BUDGET line that
    traffic.py budget and supervisor.py tick read, and records the reading in ~/.claude/mts-budget.json (same file budget.py uses).
    The login letter comes from --login or env MTS_LOGIN (the operator sets it once per device, or names it in the start line)."""
    import argparse
    ap = argparse.ArgumentParser(prog="mts_signal.py budget")
    ap.add_argument("--login", default=os.environ.get("MTS_LOGIN", ""))
    ap.add_argument("--five", type=float, required=True, help="5-hour window used, percent")
    ap.add_argument("--week", type=float, required=True, help="weekly all-models used, percent")
    ap.add_argument("--reset", required=True, help="weekly reset, UTC YYYY-MM-DDTHH:MMZ")
    a = ap.parse_args(args)
    lg = a.login.strip().upper()
    if lg not in ("A", "B", "C"):
        print("login must be A, B or C (--login or env MTS_LOGIN)")
        return 2
    if not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\dZ?", a.reset):
        print("--reset must look like 2026-10-22T19:59Z")
        return 2
    reset = a.reset if a.reset.endswith("Z") else a.reset + "Z"
    try:
        sched = str(Path(__file__).resolve().parents[1] / "sched")
        if sched not in sys.path:
            sys.path.insert(0, sched)
        import budget as budget_mod   # the one writer of ~/.claude/mts-budget.json (SUPER_SESSION Pacing)
        rec = {"utc": now().strftime("%Y-%m-%dT%H:%M:%SZ"), "weekly_all_pct": a.week, "weekly_resets_at": reset,
               "five_hour_pct": a.five}
        budget_mod.home().mkdir(parents=True, exist_ok=True)
        (budget_mod.home() / "mts-budget.json").write_text(json.dumps(rec, sort_keys=True), encoding="utf-8", newline=chr(10))
    except (OSError, ImportError) as e:
        print("budget file not written: %s" % e)
    ok = send("BUDGET login=%s 5h=%d%% week=%d%% reset=%s" % (lg, round(a.five), round(a.week), reset), to="all", kind="note")
    print("BUDGET login=%s sent" % lg if ok else "BUDGET not sent (no origin or push failed)")
    return 0 if ok else 1


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd = argv[0]
    if cmd == "hook":
        return hook()
    if cmd == "send":
        import argparse
        ap = argparse.ArgumentParser(prog="mts_signal.py send")
        ap.add_argument("text")
        ap.add_argument("--to", default="all")
        ap.add_argument("--kind", default="note", choices=["note", "claim", "done", "ask", "broadcast"])
        ap.add_argument("--sid", default="", help=argparse.SUPPRESS)
        a = ap.parse_args(argv[1:])
        ok = send(a.text, to=a.to, kind=a.kind, sid=a.sid)
        print("sent" if ok else "NOT sent (no origin or push failed)")
        return 0 if ok else 1
    if cmd == "broadcast":
        import argparse
        ap = argparse.ArgumentParser(prog="mts_signal.py broadcast")
        ap.add_argument("message")
        ap.add_argument("--to", default="all")
        a = ap.parse_args(argv[1:])
        ok = send(a.message, to=a.to, kind="broadcast")
        print("broadcast sent" if ok else "broadcast NOT sent (no origin or push failed)")
        if ok:
            print(sender_note(a.message))
        return 0 if ok else 1
    if cmd == "budget":
        return budget_cmd(argv[1:])
    if cmd == "read":
        hours = 24
        if "--hours" in argv:
            hours = float(argv[argv.index("--hours") + 1])
        h = ensure()
        if h is None:
            print("no origin")
            return 1
        since = stamp(now() - timedelta(hours=hours))
        rows = [r for r in load(h) if r.get("t", "") > since]
        for r in rows:
            print(line(r))
        if not rows:
            print("no signals in the last %g h" % hours)
        return 0
    if cmd == "status":
        print("id=%s clone=%s origin=%s" % (who(), home(), origin_url()))
        return 0
    print("unknown command: %s" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
