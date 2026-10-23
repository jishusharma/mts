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
  - Stop                    only if an unacked HIGH broadcast exists for this host: blocks the stop once (see below)
Never blocks (except that one Stop case), never raises; a failed network call is skipped.

HIGH broadcasts (operator 2026-10-22: a "every machine needs X" broadcast was shown once and nobody acted):
  python scripts/dev/mts_signal.py broadcast "<text>" --prio high --cmd "<exact operator command>"
      gets an id (b-xxxxxx). Every host shows it as "[MTS ACTION REQUIRED ...]" on EVERY prompt and at SessionStart (any age up
      to KEEP_DAYS, not only the last FIRST_LOOK_MIN minutes) until THAT HOST acks it. It tells the model to put the operator
      line first in its reply and to ack. A Stop with the reply lacking the id / "ACTION FOR THIS MACHINE" is blocked once.
  python scripts/dev/mts_signal.py ack <id> told|done [--note "..."]
      told = the operator was told (host shown a reminder once per session only); done = it ran or a check passed (silent).
  python scripts/dev/mts_signal.py acks [<id>]   hosts seen in the last KEEP_DAYS vs none/told/done; no id = all open high
      broadcasts. The sending machine's sessions also get a one-line ack status on their prompts while any host is not done.
A record stamped more than 10 minutes in the future (wrong clock) is ignored for display and for the seen marker.

  python scripts/dev/mts_signal.py send "<text>" [--to host|all] [--kind note|claim|done|ask|broadcast]
  python scripts/dev/mts_signal.py broadcast "<message>"   a signal every other session shows on its NEXT turn (nothing
                                                         wakes an idle session or flashes; the sender wakes them)
  python scripts/dev/mts_signal.py read [--hours 24]       newest last
  python scripts/dev/mts_signal.py status                  clone, origin, own id
  python scripts/dev/mts_signal.py who [--hours 24]        who is logged in where: one line per host+login (last seen, BUDGET
                                                         numbers with age, supervisor mode, last ROLE/start note); flags
                                                         `CONFLICT login <L>` when two hosts claim one login with different resets

Login roll call (operator 2026-10-23): login() = env MTS_LOGIN, else the app account (oauthAccount.emailAddress in ~/.claude.json,
env MTS_CLAUDE_JSON overrides the path) mapped to A/B/C through the LOGINS table of CLOUD_ACCOUNTS.md. Only that one field is read
and only the letter ever travels (a signal, a commit, a log never carries the address). Every record carries "login", the sender id
is <host>/<letter> when MTS_ACCOUNT is unset, SessionStart announces login=<L> and tells the session its own login plus who runs where.

The repo is PUBLIC: a signal is a short status line only (200 characters, long token-like strings are cut out). Never put
account names, secrets, order or runtime data in one. Sender id = <host>/<MTS_ACCOUNT, else the login letter, else "?">.
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
CMD_MAX = 300           # the operator command of a HIGH broadcast
FUTURE_MIN = 10        # a record stamped later than now + this is a wrong clock: ignored
DOT = chr(183)
RANK = {"none": 0, "told": 1, "done": 2}


def home():
    return Path(os.environ.get("MTS_SIGNALS_HOME") or Path.home() / ".claude" / "mts-signals")


def state_dir():
    return home().parent / "mts-signals-state"


def host():
    return (os.environ.get("MTS_SIGNALS_HOST") or socket.gethostname()).lower()


LOGIN_LETTERS = ("A", "B", "C")
_LOGIN_CACHE = {}
OAUTH_EMAIL_RE = re.compile(r'"oauthAccount"\s*:\s*\{[^{}]*?"emailAddress"\s*:\s*"([^"]+)"')


def _logins_md():
    return Path(os.environ.get("MTS_LOGINS_MD") or Path(__file__).resolve().parents[2] / "MyTradingSys" / "system" / "CLOUD_ACCOUNTS.md")


def _letter_for(email, md_text):
    """A/B/C for `email` from the LOGINS rows (`| A: <key> | ...`): the key is the full address, its local part, or a prefix of it."""
    em = str(email or "").strip().lower()
    if "@" not in em:
        return ""
    local = em.split("@")[0]
    for m in re.finditer(r"^\|\s*([ABC]):\s*(\S+)", md_text, re.MULTILINE):
        key = m.group(2).strip().lower().rstrip(",;")
        if key == em or key == local or em.startswith(key + "@"):
            return m.group(1)
    return ""


def login():
    """This app's login letter A/B/C, or "" when unknown: env MTS_LOGIN, else the app account's address mapped through
    CLOUD_ACCOUNTS.md (cached per process). The address is never returned, stored or logged: only the letter."""
    env = os.environ.get("MTS_LOGIN", "").strip().upper()[:1]
    if env in LOGIN_LETTERS:
        return env
    path = os.environ.get("MTS_CLAUDE_JSON") or str(Path.home() / ".claude.json")
    key = (path, str(_logins_md()))
    if key not in _LOGIN_CACHE:
        letter, ok = "", False
        try:
            raw = Path(path).read_text(encoding="utf-8")
            m = OAUTH_EMAIL_RE.search(raw)       # cheap and flat; the file can be many MB and is rewritten by the app
            if m:
                email = m.group(1)
            else:
                acct = json.loads(raw).get("oauthAccount")
                email = acct.get("emailAddress") if isinstance(acct, dict) else ""
            letter, ok = _letter_for(email, _logins_md().read_text(encoding="utf-8")), True
        except (OSError, ValueError, AttributeError, RecursionError):
            letter = ""
        if not ok:
            return letter       # a half-written or missing file is not cached: the next call reads again
        _LOGIN_CACHE[key] = letter
    return _LOGIN_CACHE[key]


def resolve_login(passed):
    """(letter, message): the detected login wins over a typed one (the account is the truth); message is the MISMATCH line, else ''.
    With nothing detected the typed letter stands (upper-cased, may be invalid: the caller checks)."""
    typed = str(passed or "").strip().upper()[:1]
    det = login()
    if det and typed and typed != det:
        return det, "LOGIN MISMATCH: you passed %s, this app is logged in as %s; using %s" % (typed, det, det)
    return det or typed, ""


def who():
    return f"{host()}/{os.environ.get('MTS_ACCOUNT') or login() or '?'}"


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


def clean(text, limit=TEXT_MAX):
    """One short line; long token-like strings are cut out (the repo is public)."""
    t = " ".join(str(text).split())
    t = re.sub(r"[A-Za-z0-9_\-]{32,}", "[cut]", t)
    t = re.sub(r"[^\s@]+@[^\s@]+\.[^\s@]+", "[cut]", t)       # an e-mail address never travels (public repo)
    t = re.sub(r"(?i)(secret|password|passwd|token|api[_-]?key)\s*[=:]\s*\S+", r"\1=[cut]", t)
    return t[:limit]


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


REPEAT_SEC = 300   # OURS: an identical note from the same sender inside 5 minutes adds nothing (traffic.py: 87 repeated lines in 72 h)


def is_repeat(rows, rec):
    """True when `rec` is a note that a row from the same sender already says, within REPEAT_SEC. Broadcasts and acks never repeat-drop."""
    if rec.get("kind") != "note":
        return False
    t = datetime.strptime(rec["t"], "%Y%m%dT%H%M%SZ")
    for r in rows:
        if r.get("kind") == "note" and r.get("from") == rec.get("from") and r.get("text") == rec.get("text"):
            try:
                if 0 <= (t - datetime.strptime(r["t"], "%Y%m%dT%H%M%SZ")).total_seconds() <= REPEAT_SEC:
                    return True
            except (KeyError, ValueError):
                pass
    return False


def send(text, to="all", kind="note", cwd=None, sid="", extra=None):
    """Writes one signal file and pushes it; retries on a lost race. Returns True if it reached origin."""
    h = ensure(cwd)
    if h is None:
        return False
    dt = now()
    rec = {"t": stamp(dt), "from": who(), "to": to, "kind": kind, "text": clean(text)}
    if login():
        rec["login"] = login()
    if sid:
        rec["sid"] = sid_tag(sid)
    if extra:
        rec.update(extra)
    if is_repeat(load(h), rec):
        return True
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


def future_limit():
    return stamp(now() + timedelta(minutes=FUTURE_MIN))


def unseen_for(rows, since, sid=""):
    """Signals newer than `since` (a stamp) that are for everyone or for this host: from another host/account pair, or a
    broadcast from any session but this one (all sessions on one machine share one sender id). Acks and HIGH broadcasts are
    not news (the action block handles them); a record stamped in the future is ignored."""
    me, tag, lim = who(), sid_tag(sid), future_limit()
    return [r for r in rows if since < r.get("t", "") <= lim and r.get("to") in ("all", host())
            and r.get("kind") != "ack" and r.get("prio") != "high"
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


BOOKKEEPING = ("claim ", "release ", "Merge ")


CD_RE = re.compile(r"""(?:^|[;&|]\s*)(?:cd|pushd)\s+(?:/d\s+)?("[^"]+"|'[^']+'|[^\s;&|]+)""")
SCRIPT_DIR_RE = re.compile(r"""("[^"]+"|'[^']+'|\S+?)[/\\]scripts[/\\]dev[/\\]sync\.py""")


def ship_dir(cmd, cwd):
    """The tree a ship command ran in: `cd <tree> && ... sync.py ship`, or `python <tree>/scripts/dev/sync.py ship`;
    else the session cwd. The session cwd is usually the primary checkout, whose
    newest commit is an old claim: DESKTOP-F7IU69N signalled "works on: gemini-yt-pipeliner" for every ship while its worktrees
    shipped real Results (2026-10-23, 11 ships)."""
    head = cmd[:cmd.find("sync.py")] if "sync.py" in cmd else cmd
    found = [m.group(1).strip("\"'") for m in CD_RE.finditer(head)]
    m = SCRIPT_DIR_RE.search(cmd)
    script = m.group(1).strip("\"'") if m else ""
    if script and Path(script).is_absolute():
        p = Path(script)
    elif found:
        p = Path(found[-1]).expanduser()
        p = p if p.is_absolute() or not cwd else Path(cwd) / p
    else:
        return cwd
    return str(p) if p.is_dir() else cwd


def last_result(cwd):
    """The `Result:` line of the newest work commit in cwd (what a ship delivered), else ''. Claim, release and merge commits
    are skipped: a ship that ends on its claim commit sent the claim's "works on: <old task>" text as its Result (2026-10-23,
    DESKTOP-F7IU69N, 9 ships in a row)."""
    try:
        r = git(cwd, "log", "-10", "--format=%x1e%B", check=False, timeout=5)
    except (OSError, subprocess.SubprocessError, RuntimeError):
        return ""
    for body in r.stdout.split(chr(0x1e))[1:]:
        if body.lstrip().startswith(BOOKKEEPING):
            continue
        for ln in body.splitlines():
            if ln.startswith("Result:"):
                return ln.strip()
        return ""
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
        return "session started in %s%s" % (Path(cwd).name or "?", " login=" + login() if login() else ""), "note"
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
                res = last_result(ship_dir(cmd, cwd))
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
    if ev == "Stop":
        return stop_check(payload)
    auto = auto_send_text(payload)
    note = sender_note(auto[0]) if auto and auto[1] == "broadcast" else ""
    got = _handle(payload, sid, ev, auto)
    return "\n".join(t for t in (note, got) if t)


def high_open(rows):
    """HIGH broadcasts that have not expired (any age up to KEEP_DAYS), oldest first."""
    cutoff = stamp(now() - timedelta(days=KEEP_DAYS))
    return [r for r in rows if r.get("kind") == "broadcast" and r.get("prio") == "high" and r.get("id") and r.get("t", "") >= cutoff]


def ack_state(rows, bid, hostname):
    """Best state this host reached for broadcast bid: none < told < done."""
    best = "none"
    for r in rows:
        if r.get("kind") == "ack" and r.get("id") == bid and str(r.get("host", "")).lower() == hostname \
                and RANK.get(r.get("state"), 0) > RANK[best]:
            best = r["state"]
    return best


def own_state(rows, b):
    """This host's ack state for broadcast b; for an `--audience top` broadcast an ack from ANY host on my login (env MTS_LOGIN)
    counts too, so two sessions or machines on one login do not both act (EXHAUST_PHASE.md: one actor per login)."""
    best = ack_state(rows, b["id"], host())
    lg = login()
    if b.get("aud") == "top" and lg:
        for r in rows:
            if r.get("kind") == "ack" and r.get("id") == b["id"] and str(r.get("login", "")).upper() == lg                     and RANK.get(r.get("state"), 0) > RANK[best]:
                best = r["state"]
    return best


def hosts_seen(rows):
    """Hosts with any record in the last KEEP_DAYS (a record stamped in the future does not count)."""
    cutoff, lim = stamp(now() - timedelta(days=KEEP_DAYS)), future_limit()
    out = set()
    for r in rows:
        if cutoff <= r.get("t", "") <= lim:
            out.add(str(r.get("host") or str(r.get("from", "")).split("/")[0]).lower())
    out.discard("")
    return out


def targets(rows, b):
    return {b["to"]} if b.get("to") not in (None, "all") else hosts_seen(rows) | {host()}


def action_text(b):
    cmd = b.get("cmd") or b.get("text", "")
    return "ACTION FOR THIS MACHINE (%s): %s" % (host(), cmd)


def is_worker_env():
    """True in a subagent or embedded worker (a Supervisor's Builder/Session_Planner): broadcasts sent with --audience top skip it."""
    return bool(os.environ.get("MTS_SUBAGENT")) or os.environ.get("MTS_ROLE", "") in ("Builder", "Session_Planner")


def action_block(rows, ev):
    """The [MTS ACTION REQUIRED] text for this host: state none on every turn, told once per session (SessionStart), done never."""
    out = []
    for b in high_open(rows):
        if b.get("to") not in ("all", host()) or (b.get("aud") == "top" and is_worker_env()):
            continue
        st = own_state(rows, b)
        if st == "done" or (st == "told" and ev != "SessionStart"):
            continue
        if st == "told":
            out.append("[MTS reminder %s HIGH %s] this machine was told, not yet confirmed done: %s (when it ran: python scripts/dev/mts_signal.py ack %s done)"
                       % (DOT, b["id"], b.get("cmd") or b.get("text", ""), b["id"]))
            continue
        out.append("[MTS ACTION REQUIRED %s prio HIGH %s %s from %s at %s] %s" % (DOT, DOT, b["id"], b.get("from", "?"), b["t"][9:13] + "Z", b.get("text", "")))
        out.append('Do now, before the current task: put this as the FIRST line of your reply to the operator: "%s". Then run: '
                   "python scripts/dev/mts_signal.py ack %s told. When the operator confirms it ran (or a check passes): ack %s done."
                   % (action_text(b), b["id"], b["id"]))
    return "\n".join(out)


def sender_status(rows):
    """One line for the machine that sent a HIGH broadcast while any target host is not done."""
    out = []
    for b in high_open(rows):
        if str(b.get("from", "")).split("/")[0].lower() != host():
            continue
        hs = sorted(targets(rows, b))
        open_ = ["%s=%s" % (h, ack_state(rows, b["id"], h)) for h in hs if ack_state(rows, b["id"], h) != "done"]
        if open_:
            out.append("[MTS BROADCAST %s status] %d/%d hosts done; open: %s (python scripts/dev/mts_signal.py acks %s)"
                       % (b["id"], len(hs) - len(open_), len(hs), ", ".join(open_), b["id"]))
    return "\n".join(out)


def _handle(payload, sid, ev, auto):
    head = login_line() if ev == "SessionStart" else ""
    got = _handle_rows(payload, sid, ev, auto)
    return "\n".join(t for t in (head, got) if t)


def _handle_rows(payload, sid, ev, auto):
    cwd = payload.get("cwd") or ""
    if auto:
        spawn_send(auto[0], auto[1], cwd, sid)
    if ev not in ("UserPromptSubmit", "SessionStart"):     # receiving on a prompt or session start; PostToolUse only sends claim/ship (review 2026-10-22: no fetch per tool call)
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
        h = home()      # another session of this machine holds the fetch slot: read the machine's clone
        if not (h / ".git").exists():
            return ""
    rows = load(h)
    out = []
    if ev in ("UserPromptSubmit", "SessionStart"):
        out.append(action_block(rows, ev))
    if ev == "SessionStart":
        out.append("\n".join(roll_lines(rows)[:4]))
    if ev == "UserPromptSubmit":
        out.append(sender_status(rows))
    if ev != "SessionStart":
        out.append(news(rows, sid, seen_f, sd, fetch))
    return "\n".join(t for t in out if t)


def news(rows, sid, seen_f, sd, fetch):
    """Not-yet-seen signals and broadcasts (the old behaviour); a second session re-reads the clone only when it changed."""
    if not fetch:
        sync = sd / "last_sync"
        if not sync.exists():
            return ""
        if seen_f.exists() and seen_f.stat().st_mtime >= sync.stat().st_mtime:
            return ""
    try:
        since = seen_f.read_text(encoding="utf-8").strip()
    except OSError:
        since = stamp(now() - timedelta(minutes=FIRST_LOOK_MIN))
    lim = future_limit()
    new = unseen_for(rows, since, sid)
    seen_f.write_text(max([since] + [r.get("t", "") for r in rows if r.get("t", "") <= lim]), newline="\n")
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


def reply_text(payload):
    """The assistant text of the turn that just ended: the payload field if present, else read back from the transcript."""
    t = payload.get("last_assistant_message")
    if isinstance(t, str) and t:
        return t
    path = payload.get("transcript_path")
    if not path or not Path(path).is_file():
        return ""
    chunks = []
    with open(path, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - 400000))
        lines = f.read().decode("utf-8", "replace").splitlines()
    for ln in reversed(lines):
        try:
            e = json.loads(ln)
        except ValueError:
            continue
        msg = e.get("message") if isinstance(e.get("message"), dict) else {}
        content = msg.get("content")
        if e.get("type") == "user" and not (isinstance(content, list) and content
                                            and all(c.get("type") == "tool_result" for c in content if isinstance(c, dict))):
            break
        if e.get("type") == "assistant":
            if isinstance(content, str):
                chunks.append(content)
            elif isinstance(content, list):
                chunks.extend(c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text")
    return "\n".join(chunks)


def stop_check(payload):
    """Block the stop once while an unacked (state none) HIGH broadcast for this host was not put to the operator."""
    if payload.get("stop_hook_active"):
        return ""
    h = home()
    if not (h / ".git").exists():
        return ""
    rows = load(h)
    pending = [b for b in high_open(rows) if b.get("to") in ("all", host()) and not (b.get("aud") == "top" and is_worker_env()) and own_state(rows, b) == "none"]
    if not pending:
        return ""
    reply = reply_text(payload)
    if "ACTION FOR THIS MACHINE" in reply or any(b["id"] in reply for b in pending):
        return ""
    reason = ("[MTS ACTION REQUIRED] unacked HIGH broadcast for this machine and your reply does not tell the operator. Reply again with "
              + " ; ".join('"%s" as the FIRST line (%s)' % (action_text(b), b["id"]) for b in pending)
              + ", then run: " + " ; ".join("python scripts/dev/mts_signal.py ack %s told" % b["id"] for b in pending) + ".")
    return json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False)


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


# ---- roll call: who is logged in where -------------------------------------------------------------------------------

STALE_H = 6          # OURS: a BUDGET reading older than this is shown as stale
BUDGET_KV = re.compile(r"^BUDGET login=([ABC])\b")
NOTE_RE = re.compile(r"^(ROLE\b|start\b|session started\b)")


def _t(r):
    try:
        return datetime.strptime(r["t"], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except (KeyError, ValueError):
        return None


def _age(dt, at):
    m = max(0, int((at - dt).total_seconds() // 60))
    return "%dm" % m if m < 120 else "%dh" % (m // 60)


def roll_lines(rows, hours=24, at=None):
    """One line per host+login seen in the last `hours`, CONFLICT lines first. A record's login: its "login" field, else the
    letter after the slash of its sender id, else the letter typed in a BUDGET text (older records), else "?"."""
    at = at or now()
    since, lim = stamp(at - timedelta(hours=hours)), stamp(at + timedelta(minutes=FUTURE_MIN))
    groups, budgets = {}, {}
    for r in rows:
        if not since < r.get("t", "") <= lim or r.get("kind") == "ack":
            continue
        frm = str(r.get("from", ""))
        h = str(r.get("host") or frm.split("/")[0]).lower()
        txt = str(r.get("text", ""))
        bm = BUDGET_KV.match(txt)
        lg = r.get("login") or (frm.split("/")[1] if "/" in frm and frm.split("/")[1] in LOGIN_LETTERS else "") \
            or (bm.group(1) if bm else "") or "?"
        g = groups.setdefault((h, lg), {"t": "", "budget": None, "hb": None, "note": None})
        g["t"] = max(g["t"], r["t"])
        if bm:
            g["budget"] = r
            if "sup=" in txt:
                g["hb"] = r
            old = budgets.setdefault(bm.group(1), {}).get(h)     # keyed by the label the line states: that is what readers reason from
            if (at - (_t(r) or at)).total_seconds() <= STALE_H * 3600 and (old is None or r["t"] >= old["t"]):
                budgets[bm.group(1)][h] = r                      # only fresh readings can conflict (a reset just rolled over is not one)
        if NOTE_RE.match(txt):
            g["note"] = r
    conflicts = []
    for lg, per in sorted(budgets.items()):
        resets = {}
        for h, r in per.items():
            m = re.search(r"\breset=(\S+)", r.get("text", ""))
            if m:
                resets[h] = m.group(1)[:16]
        if lg != "?" and len(set(resets.values())) > 1:
            ordered = sorted(resets.items(), key=lambda kv: kv[1])
            (h1, r1), (h2, r2) = ordered[0], ordered[-1]
            conflicts.append("CONFLICT login %s: reset %s on %s vs %s on %s" % (lg, r1, h1, r2, h2))
    out = []
    for (h, lg), g in sorted(groups.items(), key=lambda kv: (kv[0][1] == "?", kv[0][1], kv[0][0])):
        seen = _t({"t": g["t"]})
        parts = ["login %s %s seen %s ago" % (lg, h, _age(seen, at) if seen else "?")]
        b = g["budget"]
        if b:
            txt = b.get("text", "")
            nums = " ".join(m.group(0) for m in (re.search(p, txt) for p in (r"\b5h=\d+%", r"\bweek=\d+%", r"\breset=\S+")) if m)
            bt = _t(b)
            stale = bt is None or (at - bt).total_seconds() > STALE_H * 3600
            label = BUDGET_KV.match(txt).group(1)
            parts.append("BUDGET %s (%s ago%s)%s" % (nums, _age(bt, at) if bt else "?", ", STALE" if stale else "",
                                                     " MISLABELLED login=" + label if label != lg and lg != "?" else ""))
        hb = g["hb"]
        if hb:
            kv = dict(re.findall(r"(\w+)=(\S+)", hb.get("text", "")))
            parts.append("sup=%s mode=%s" % (kv.get("sup", "?"), kv.get("mode", "?")))
        if g["note"]:
            parts.append(clean(g["note"].get("text", ""), 60))
        out.append(" | ".join(parts))
    return conflicts + out


def login_line():
    lg = login()
    if lg:
        return "LOGIN: this session is login %s on %s (from the app account)" % (lg, host().upper())
    return "LOGIN: unknown on %s (the app account is not in CLOUD_ACCOUNTS.md LOGINS; set env MTS_LOGIN=A|B|C)" % host().upper()


def who_cmd(args):
    hours = 24.0
    if "--hours" in args and args.index("--hours") + 1 < len(args):
        hours = float(args[args.index("--hours") + 1])
    h = ensure()
    if h is None:
        print("no origin")
        return 1
    print(login_line())
    lines = roll_lines(load(h), hours)
    print("\n".join(lines) if lines else "no signals in the last %g h" % hours)
    return 0


def budget_line(login, five, week, reset, models):
    """The BUDGET signal text; models = {name: percent used} adds `models=opus:10,fable:3` (exhaust phase spends the model with headroom)."""
    s = "BUDGET login=%s 5h=%d%% week=%d%% reset=%s" % (login, round(five), round(week), reset)
    if models:
        s += " models=" + ",".join("%s:%d" % (k, round(v)) for k, v in models.items())
    return s


def budget_cmd(args):
    """`budget --five 12 --week 40 --reset 2026-10-22T19:59Z [--login A]`: one call after get_usage. Sends the BUDGET line that
    traffic.py budget and supervisor.py tick read, and records the reading in ~/.claude/mts-budget.json (same file budget.py uses).
    The login letter comes from --login or env MTS_LOGIN (the operator sets it once per device, or names it in the start line)."""
    import argparse
    ap = argparse.ArgumentParser(prog="mts_signal.py budget")
    ap.add_argument("--login", default="", help="optional: the app account decides (a differing letter is overridden with a MISMATCH line)")
    ap.add_argument("--five", type=float, required=True, help="5-hour window used, percent")
    ap.add_argument("--week", type=float, required=True, help="weekly all-models used, percent")
    ap.add_argument("--reset", required=True, help="weekly reset, UTC YYYY-MM-DDTHH:MMZ")
    ap.add_argument("--model", action="append", default=[], help="per-model window used, name=percent (repeatable)")
    a = ap.parse_args(args)
    models = {k.strip().lower(): float(v) for k, _, v in (s.partition("=") for s in a.model) if v}
    lg, mism = resolve_login(a.login)
    if mism:
        print(mism)
    if lg not in ("A", "B", "C"):
        print("login unknown: the app account is not in CLOUD_ACCOUNTS.md LOGINS; pass --login A|B|C or set env MTS_LOGIN")
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
    ok = send(budget_line(lg, a.five, a.week, reset, models), to="all", kind="note")
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
        ap.add_argument("--prio", default="normal", choices=["normal", "high"])
        ap.add_argument("--audience", default="all", choices=["all", "top"], help="top: subagents and embedded workers neither see nor block on it")
        ap.add_argument("--cmd", default="", help="high: the exact command the operator must run on each machine")
        a = ap.parse_args(argv[1:])
        extra, bid = None, ""
        if a.prio == "high":
            bid = "b-" + hashlib.sha1(("%s%s%s" % (time.time(), who(), a.message)).encode("utf-8")).hexdigest()[:6]
            extra = {"id": bid, "prio": "high", "cmd": clean(a.cmd, CMD_MAX)}
            if a.audience == "top":
                extra["aud"] = "top"
        ok = send(a.message, to=a.to, kind="broadcast", extra=extra)
        print("broadcast sent" if ok else "broadcast NOT sent (no origin or push failed)")
        if ok:
            print(sender_note(a.message))
            if bid:
                print("id %s (HIGH): every host shows it on every prompt until it acks. Follow it with: python scripts/dev/mts_signal.py acks %s" % (bid, bid))
        return 0 if ok else 1
    if cmd == "ack":
        import argparse
        ap = argparse.ArgumentParser(prog="mts_signal.py ack")
        ap.add_argument("id")
        ap.add_argument("state", choices=["told", "done"])
        ap.add_argument("--note", default="")
        a = ap.parse_args(argv[1:])
        h = ensure()
        if h is None:
            print("no origin")
            return 1
        if a.id not in {b["id"] for b in high_open(load(h))}:
            print("unknown or expired broadcast id %s (python scripts/dev/mts_signal.py acks)" % a.id)
            return 2
        ok = send("ack %s %s %s" % (a.id, a.state, a.note), kind="ack", extra={"id": a.id, "state": a.state, "host": host(), "login": login(), "note": clean(a.note, 100)})
        print("ack %s %s (%s)" % (a.id, a.state, host()) if ok else "ack NOT sent (push failed)")
        return 0 if ok else 1
    if cmd == "acks":
        h = ensure()
        if h is None:
            print("no origin")
            return 1
        rows = load(h)
        want = argv[1] if len(argv) > 1 else ""
        bs = [b for b in high_open(rows) if b["id"] == want] if want else \
            [b for b in high_open(rows) if any(ack_state(rows, b["id"], t) != "done" for t in targets(rows, b))]
        for b in bs:
            print("%s HIGH from %s at %s: %s" % (b["id"], b.get("from", "?"), b["t"], b.get("text", "")))
            for t in sorted(targets(rows, b)):
                notes = [r.get("note") for r in rows if r.get("kind") == "ack" and r.get("id") == b["id"] and r.get("host") == t and r.get("note")]
                print("  %-16s %s%s" % (t, ack_state(rows, b["id"], t), "  " + notes[-1] if notes else ""))
        if not bs:
            print("no such broadcast" if want else "no open HIGH broadcasts")
        return 0
    if cmd == "budget":
        return budget_cmd(argv[1:])
    if cmd == "who":
        return who_cmd(argv[1:])
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
