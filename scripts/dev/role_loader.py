"""scripts/dev/role_loader.py: loads a role's workflow deterministically when the operator opens a session with
"You are Eagle_Eyes" (or "I need a pipeliner" ...), and lets the operator verify it in one glance.

Header = line 1 of every MyTradingSys/system/roles/*.md:
  <!-- role: <Name> | version: v<N> | token: <word>-<word> | triggers: a, b, c -->
The token is DERIVED from the file body (every line after line 1): sha256 -> two 16-bit chunks -> two words of WORDS.
Any body edit changes the token, so a stale token is detectable (`check`). `token: PENDING` is a placeholder.

Which roles exist, their files and how each starts: roles/ROSTER.json (the single source; KNOWN_ROLES and ALIASES come from it).

  hook    UserPromptSubmit hook: on a role trigger, inject the role file from origin/fast-track + a banner instruction;
          a session's first prompt with no role line gets the best-fitting operator role (`pick`), banner `(fallback: <why>)`.
  list    print the roster (name, file, start, model, lane, job) and the aliases.
  pick --text <task text | ->   the role the fallback would load for that text, and why (never an embedded role).
  render [--check]   rewrite the roster blocks in ROLES.md and START_HERE.txt (--check: exit 1 when stale).
  retoken [--all | file...]   rewrite tokens in headers.
  check   roster vs files, rows of ROLES.md vs files vs header validity vs token freshness, rendered blocks current
          (exit 1 on malformed, stale or mismatched).
  lint    policy contradictions across roles/*.md and ROLES.md, dead commands, missing files + CI-red owner line (exit 1 on defect).
  banner <Name>   the expected first-reply banner line.
  verify --text <note|-> [--role Name] [--sid id]   supervisor trust check of a worker's banner (0 ok, 2 stale, 1 untrusted).
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROLES_REL = "MyTradingSys/system/roles"
ROLES_MD_REL = "MyTradingSys/system/ROLES.md"
TRUNK = "origin/fast-track"
ROSTER_REL = f"{ROLES_REL}/ROSTER.json"
START_HERE_REL = "MyTradingSys/system/START_HERE.txt"


def load_roster(repo=None):
    """Roles from roles/ROSTER.json, the single source of which roles exist: the local file, else the trunk copy (an old
    checkout run through role_hook_launcher), else []."""
    p = Path(repo or REPO) / ROSTER_REL
    try:
        if p.exists():
            text = p.read_text(encoding="utf-8")
        else:
            r = subprocess.run(["git", "-C", str(repo or REPO), "show", f"{TRUNK}:{ROSTER_REL}"], capture_output=True,
                               timeout=8, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0)
            text = r.stdout.decode("utf-8") if r.returncode == 0 else ""
        return [r for r in json.loads(text)["roles"] if isinstance(r, dict) and r.get("name")]
    except Exception:
        return []


# Only when no roster is readable anywhere, so a role request still triggers; test_role_roster.py keeps it equal to the roster.
NO_ROSTER_NAMES = ["Admin_Guy", "Eagle_Eyes", "Thinker", "MTS_Doctor", "Pipeliner", "Supervisor", "Lab_Guy",
                   "1985Artifacts_Guy", "Session_Planner", "Builder"]
KNOWN_ROLES = [r["name"] for r in load_roster()] or list(NO_ROSTER_NAMES)
# Old names that still open the merged/renamed role (operator 2026-10-20); work even when the role file is not local yet.
ALIASES = {r["name"]: [a.lower() for a in r["aliases"]] for r in load_roster() if r.get("aliases")}
SINGLETON_ROLES = ("Pipeliner",)  # one instance across all machines: scripts/dev/lease.py

# Fixed list: index = 16-bit chunk % 256. Never reorder or edit (it would change every token); the length is asserted below.
WORDS = (
    "able acid aged also arch area atom aunt away back bake band bank barn base bath bead beam bear bell belt bend "
    "bird blue boat bold bone book boot bowl brew brick bulb bush cafe cake calm camp card cart cave chip city clay "
    "clip clock cloud coal coat code coin cool cope corn crab crew crow cube cup dark dawn deal deck deer dial dice "
    "dish dive dock door dove down draw drum duck dune dusk dust each earn east edge elm epic face fair farm fast "
    "fawn fern file film fish flag flat flax flip foam fold fork form fort fox frog fuel gate gift glad glow goat "
    "gold gown grab grape gray grid gulf hall hand harp hawk hay heat herb hill hive home hood hook horn hull ice "
    "idea inch iron isle jade jar jazz joy kelp kind king kite knot lake lamb lamp land lark leaf lens lily lime "
    "link lion list loaf lock loop lump mail mango maple mask mate meal mesh mild mill mint mist moon moss moth "
    "nail navy nest net nine noon note oak oat oboe ocean olive onyx opal orbit otter oven owl pace pail palm park "
    "pear pearl pier pine pipe plum pond pony port quail quartz quest quiet rail rain reed ring road robin rock "
    "roof rope rose rust sage sail salt sand seal seed shell silk sled snow soap soda sock song spoon star stem "
    "tail tape tent tide tile toad tool tower trail tree tulip twig vase vine wave west wheat wind"
).split()

HEADER_RE = re.compile(r"^<!--\s*role:\s*(?P<name>[^|]+?)\s*\|\s*version:\s*(?P<version>v\d+(?:\.\d+)*)\s*\|\s*"
                       r"token:\s*(?P<token>PENDING|[a-z]+-[a-z]+)\s*\|\s*triggers:\s*(?P<triggers>[^>]*?)\s*-->\s*$")
PREFIX = r"(?:you are|you're|act as|be the|be|role:|i need(?: an| a| the)?|start(?: an| a| the)?)"


# ---------- token ----------
def split_header(text):
    text = text.replace("\r\n", "\n")
    first, _, body = text.partition("\n")
    return first, body


def compute_token(text):
    _, body = split_header(text)
    d = hashlib.sha256(body.encode("utf-8")).digest()
    a = int.from_bytes(d[0:2], "big") % len(WORDS)
    b = int.from_bytes(d[2:4], "big") % len(WORDS)
    return f"{WORDS[a]}-{WORDS[b]}"


def parse_header(text):
    first, _ = split_header(text)
    m = HEADER_RE.match(first.strip())
    if not m:
        return None
    trig = [t.strip().lower() for t in m.group("triggers").split(",") if t.strip()]
    return {"name": m.group("name").strip(), "version": m.group("version"), "token": m.group("token"), "triggers": trig}


def file_for(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower().replace("&", "")).strip("_") + ".md"


def banner(name, version, token, fname, sha8, row_only=False, fallback=None):
    tag = "ROLE LOADED (ROW ONLY)" if row_only else "ROLE LOADED"
    why = f" (fallback: {re.sub(r'[()]', '', fallback)})" if fallback else ""
    return f"{tag}: {name}{why} {version} · token {token} · {ROLES_REL}/{fname} @ {sha8}"


# ---------- git (monkeypatchable) ----------
def _flags():
    return getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0


def git_fetch(repo):
    try:
        r = subprocess.run(["git", "-C", str(repo), "fetch", "-q", "origin", "fast-track"], capture_output=True,
                           timeout=8, creationflags=_flags())
        return r.returncode == 0
    except Exception:
        return False


def git_show(repo, rel):
    """Text of rel on origin/fast-track, or None."""
    try:
        r = subprocess.run(["git", "-C", str(repo), "show", f"{TRUNK}:{rel}"], capture_output=True, timeout=8,
                           creationflags=_flags())
        return r.stdout.decode("utf-8") if r.returncode == 0 else None
    except Exception:
        return None


def git_show_at(repo, rev, rel):
    """Text of rel at commit rev, or None."""
    try:
        r = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{rel}"], capture_output=True, timeout=8,
                           creationflags=_flags())
        return r.stdout.decode("utf-8") if r.returncode == 0 else None
    except Exception:
        return None


def git_is_ancestor(repo, sha):
    """True when commit sha is on origin/fast-track."""
    try:
        r = subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", sha, TRUNK], capture_output=True,
                           timeout=8, creationflags=_flags())
        return r.returncode == 0
    except Exception:
        return False


def git_sha8(repo):
    try:
        r = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short=8", TRUNK], capture_output=True, timeout=8,
                           creationflags=_flags())
        return (r.stdout.decode().strip() or "unknown") if r.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


# ---------- trigger matching (no git) ----------
def local_roles(repo=REPO):
    """{Name: [triggers]} from local role-file headers plus the known names (a role whose file is not local still triggers)."""
    out = {n: [n.lower()] + ALIASES.get(n, []) for n in KNOWN_ROLES}
    d = Path(repo) / ROLES_REL
    if d.is_dir():
        for f in sorted(d.glob("*.md")):
            try:
                with open(f, encoding="utf-8", newline="") as fh:
                    h = parse_header(fh.readline())
            except Exception:
                continue
            if h:
                out[h["name"]] = sorted(set(out.get(h["name"], []) + [h["name"].lower()] + h["triggers"] + ALIASES.get(h["name"], [])))
    return out


def _phrase(t):
    return "[_ ]".join(re.escape(p) for p in re.split(r"[_ ]+", t.strip()) if p)


def _role_line():
    try:
        import role_line
    except ImportError:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        try:
            import role_line
        except ImportError:     # a missing helper must not break the hook: the 300-char scan below still runs
            return None
    return role_line


def clean_prompt(prompt):
    """The prompt without the app's wrappers (reminder blocks, paste tags, start_session "Background ... Task:"): role_line.py."""
    rl = _role_line()
    return rl.clean(prompt) if rl else str(prompt or "")


def match_roles(prompt, roles):
    """Distinct role names asked for. A `You are <Role>.` first line behind the app's wrappers (role_line.py) names exactly one;
    else the first 300 raw chars: the phrase must start a line or sentence (a quote, a negation or a mid-sentence mention does
    not count). The 300-char scan stays on the raw text: on the cleaned text it reached later sentences (review of 9f0cb459c:
    "Supervisor. Login C. ..." also matched Session_Planner, a quoted "What about a thinker?" loaded Thinker)."""
    rl = _role_line()
    if rl:
        names = {}
        for name, trigs in roles.items():
            for t in [name] + list(trigs):
                names.setdefault(t, name)
        hit = rl.role_line(prompt, names)
        if hit:     # a second explicit `You are <Role>` line still makes it ambiguous; "start a session planner" does not
            head = (prompt or "")[:300].lower()
            other = [n for n, trigs in roles.items() if n != names[hit] and any(re.search(
                r"(?:^|[.!?])[ \t]*(?:you are|you're)\s+(?:the\s+)?" + _phrase(t) + r"(?![a-z0-9_])", head, re.M) for t in trigs)]
            return [names[hit]] + other
    # the raw head, plus the first sentence behind the wrappers ("I need a pipeliner" after a long reminder or Background block)
    heads = [str(prompt or "")[:300].lower()]
    if rl:
        heads.append(re.split(r"[.!?]", rl.first_line(prompt), maxsplit=1)[0][:300].lower())
    hits = []
    for name, trigs in roles.items():
        for t in trigs:
            if any(re.search(r"(?:^|[.!?])[ 	]*" + PREFIX + r"\s+" + _phrase(t) + r"(?![a-z0-9_])", h, re.M) for h in heads):
                hits.append(name)
                break
    return hits


def is_reload(prompt):
    return "reload role" in (prompt or "").lower()


def mentioned_role(prompt, roles):
    low = (prompt or "").lower()
    for name, trigs in roles.items():
        for t in trigs:
            if re.search(r"(?<![a-z0-9_])" + _phrase(t) + r"(?![a-z0-9_])", low):
                return name
    return None


# ---------- best-role fallback (no role line) ----------
def _kw_re(kw):
    kw = kw.lower().strip()
    if kw == "?":
        return re.compile(r"\?")
    prefix = kw.endswith("*")
    body = r"[_ -]".join(re.escape(p) for p in re.split(r"[_ ]+", kw.rstrip("*")) if p)
    return re.compile(r"(?<![a-z0-9])" + body + ("" if prefix else r"(?![a-z0-9])"))


# A path inside a brief ("C:/Users/x/IdeaProjects/...") must not score: "idea*" matched IdeaProjects (pilot 2026-10-22).
_PATH_RE = re.compile(r"[a-z]:[\\/][\w.~\\/-]*|[\w.~-]+(?:[\\/][\w.~-]+){2,}")


def pick_role(text, repo=REPO):
    """Best operator role for a task text: 1 point per keyword, 0.5 per weak keyword (roster). A role needs one full
    keyword; embedded roles (Builder, Session_Planner) are never picked. Equal top scores = a tie, nothing is picked."""
    low = _PATH_RE.sub(" ", (text or "").lower())
    scored = []
    for r in load_roster(repo):
        if r.get("start") != "operator":
            continue
        strong = [k for k in r.get("keywords", []) if _kw_re(k).search(low)]
        weak = [k for k in r.get("weak_keywords", []) if _kw_re(k).search(low)]
        if strong:
            scored.append((len(strong) + 0.5 * len(weak), r["name"], strong + weak))
    if not scored:
        return {"name": None, "reason": "no role keywords in the text", "tie": []}
    scored.sort(key=lambda s: -s[0])
    top = [s for s in scored if s[0] == scored[0][0]]
    if len(top) > 1:
        return {"name": None, "reason": "tie: " + "; ".join(f"{n} ({', '.join(k)})" for _, n, k in top),
                "tie": [n for _, n, _ in top]}
    return {"name": scored[0][1], "reason": "task text says " + ", ".join(k.rstrip("*") for k in scored[0][2]), "tie": []}


def from_session(prompt):
    """A brief sent by another session: its sender names the role, the fallback stays out."""
    p = re.sub(r"^\s*(?:<system-reminder>.*?</system-reminder>\s*)+", "", (prompt or ""), flags=re.S).lstrip()
    return ("<cross-session-message" in p[:400] or p.startswith("Another Claude session")
            or p.startswith("Background (from the session that started this one)"))


# ---------- session state ----------
def state_path(sid):
    base = Path(os.environ.get("MTS_ROLES_HOME") or Path(tempfile.gettempdir()) / "mts_roles")
    return base / (re.sub(r"[^A-Za-z0-9_.-]", "_", sid or "nosession") + ".json")


def _load(sid):
    try:
        d = json.loads(state_path(sid).read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {"roles": list(d), "meta": {}}
    except Exception:
        return {"roles": [], "meta": {}}


def injected(sid):
    return _load(sid)["roles"]


def role_meta(sid, name):
    return _load(sid)["meta"].get(name)


def _save(sid, d):
    try:
        p = state_path(sid)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(d))
    except Exception:
        pass


def mark_injected(sid, name, meta=None):
    d = _load(sid)
    if name not in d["roles"]:
        d["roles"].append(name)
    if meta:
        d["meta"][name] = meta
    _save(sid, d)


def first_prompt(sid):
    """True once per session: the first prompt the hook sees (the only one the fallback acts on)."""
    d = _load(sid)
    if d.get("seen"):
        return False
    d["seen"] = True
    _save(sid, d)
    return True


# ---------- hook ----------
def boot_step(body):
    lines = body.split("\n")
    for i, ln in enumerate(lines):
        s = ln.strip()
        # a Boot heading, or a short "Boot ...:" label; prose that merely starts with "Boot" is not a section
        m = re.match(r"^(?:#+\s*boot\b[^:\n]*?(?::\s*(.*))?|boot\b[^:\n]{0,25}:\s*(.*)|boot\b[^.:\n]{0,40}())$", s, re.I)
        if m and not s.startswith("|"):
            inline = (m.group(1) or m.group(2) or "").strip()
            if len(inline) > 12:
                return inline[:240]
            for nx in lines[i + 1:]:
                if nx.strip():
                    return nx.strip()[:240]
    return "(first step of the file's boot section)"


REMIND_EVERY = 6
LAST_META = {}


def lease_suffix(name, repo):
    """Singleton roles: the banner also shows the lease holder (read from the local origin ref the hook just fetched)."""
    if name not in SINGLETON_ROLES:
        return ""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import lease
        return " · " + lease.banner_text(repo, name)
    except Exception as e:
        return f" · lease UNKNOWN ({type(e).__name__})"


RULES_ANSWER = ("RULES ANSWERS (bug-haiku-stale-rule-answers): before any answer about current rules, roles, the super session "
                "or budget, read the source file this turn (your role file's `Read first:` line names it); cite file:line and its "
                "commit date (`git log -1 --format=%cs -- <file>`); a reading (budget, mirror, usage) gives its timestamp and age "
                "and is called stale past 6 h; nothing read = `NOT_IN_DATA`, never memory or a first search hit.\n"
                "ASKED WORK RUNS NOW (bug-ask-go-for-asked-work): work the operator already asked for is done this turn, "
                "full depth; never end a reply asking him to say go. Ask only for a genuine option decision with no default.\n")


def build_text(name, repo, fetched_ok, fallback=None):
    LAST_META.clear()
    pre = (f"ROLE LOADER (hook): the prompt has no role line; the best fit from the task text is {name} ({fallback}). "
           f"After the banner, one line: if the operator meant another role, `You are <Role>.` switches "
           f"(`python scripts/dev/role_loader.py list` shows all).\n") if fallback else ""
    return pre + _build_text(name, repo, fetched_ok, fallback)


def _build_text(name, repo, fetched_ok, fallback=None):
    sha8 = git_sha8(repo)
    stale = "" if fetched_ok else "STALE: fetch failed (using the local origin/fast-track ref; it may be old).\n"
    fname = file_for(name)
    text = git_show(repo, f"{ROLES_REL}/{fname}")
    if text is not None:
        text = text.replace("\r\n", "\n")
        h = parse_header(text)
        if not h:
            return (f"{stale}ROLE LOADER (hook): {fname} on {TRUNK} has no valid header. "
                    f"Reply `ROLE NOT LOADED: malformed header in {fname}` and stop.")
        tok = compute_token(text)
        if h["token"] != tok and h["token"] != "PENDING":
            stale += f"WARN: header token {h['token']} differs from the body token {tok}; the body is what you follow.\n"
        _, body = split_header(text)
        LAST_META.update(version=h["version"], token=tok, file=fname)
        b = banner(h["name"], h["version"], tok, fname, sha8, fallback=fallback) + lease_suffix(h["name"], repo)
        return (f"{stale}ROLE LOADER (hook): you are {h['name']}. The file below is the authoritative workflow "
                f"({ROLES_REL}/{fname} on {TRUNK} @ {sha8}).\n"
                f"Your FIRST reply must begin with exactly this line:\n{b}\n"
                f"then on the next line: FIRST ACTION: {boot_step(body)}\n"
                f"If anything is missing or unreadable, reply `ROLE NOT LOADED: <why>` and stop.\n"
                f"{RULES_ANSWER}"
                f"----- {fname} -----\n{text}")
    rows = git_show(repo, ROLES_MD_REL) or ""
    row = next((ln for ln in rows.split("\n") if re.match(r"^\|\s*" + re.escape(name) + r"\s*\|", ln)), None)
    if row is None:
        return (f"{stale}ROLE LOADER (hook): role {name} has no file ({ROLES_REL}/{fname}) and no ROLES.md row on {TRUNK}. "
                f"Reply `ROLE NOT LOADED: no file and no row for {name}` and stop.")
    b = banner(name, "v?", "none", fname, sha8, row_only=True, fallback=fallback)
    return (f"{stale}ROLE LOADER (hook): you are {name}. No role file on {TRUNK}; the ROLES.md row below is all there is.\n"
            f"Your FIRST reply must begin with exactly this line:\n{b}\n"
            f"then follow the row's Boot column. If anything is missing, reply `ROLE NOT LOADED: <why>` and stop.\n"
            f"{RULES_ANSWER}"
            f"----- ROLES.md row -----\n{row}")


def _out(event, text):
    return json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}})


def _reminder(sid):
    """Compact per-prompt reminder for a session that already has a role (no git)."""
    done = injected(sid)
    if not done:
        return ""
    name = done[-1]
    m = role_meta(sid, name)
    if not m:
        return ""
    d = _load(sid)
    d["n"] = d.get("n", 0) + 1       # the same ~230 chars on every prompt is re-read cost: repeat only every REMIND_EVERY-th prompt
    _save(sid, d)
    if (d["n"] - 1) % REMIND_EVERY:
        return ""
    path = f"{ROLES_REL}/{m['file']}"
    return _out("UserPromptSubmit", f"Role: {name} {m['version']} (token {m['token']}, {path}). Follow that file; if you no longer "
                f"have it in context, say ROLE CONTEXT LOST and re-read it with git show {TRUNK}:{path}.")


# Built-in helper agents that never take a role.
SUBAGENT_NO_ROLE = {"explore", "plan", "statusline-setup", "claude-code-guide"}


def subagent_role(payload, roles):
    """Role a SubagentStart payload names: the agent prompt text if the payload carries one, else agent_type, else description.
    (Claude Code documents agent_id + agent_type only, so the prompt fields are read when present, never required.)"""
    for key in ("prompt", "agent_prompt", "task_prompt", "description"):
        v = payload.get(key)
        if isinstance(v, str):
            hits = match_roles(v, roles)
            if len(hits) == 1:
                return hits[0]
    at = payload.get("agent_type")
    if isinstance(at, str):
        norm = re.sub(r"[_ -]+", "_", at.strip().lower())
        for name in roles:
            if norm == re.sub(r"[_ -]+", "_", name.lower()):
                return name
    return None


def handle_subagent(payload, repo=REPO):
    """SubagentStart: a background Agent gets role text like a session does. session_id is the PARENT's, so dedupe by agent_id.
    Role unknown (the payload has no prompt text): a one-line pointer so the worker loads it itself when its brief says
    'You are <Role>'. Built-in helper types and repeat starts get nothing."""
    sid = str(payload.get("session_id") or "nosession")
    aid = str(payload.get("agent_id") or "")
    at = str(payload.get("agent_type") or "")
    if at.strip().lower() in SUBAGENT_NO_ROLE:
        return ""
    d = _load(sid)
    seen = d.setdefault("subagents", [])
    if aid and aid in seen:
        return ""
    if aid:
        seen.append(aid)
        _save(sid, d)
    roles = local_roles(repo)
    name = subagent_role(payload, roles)
    if name:
        return _out("SubagentStart", build_text(name, repo, git_fetch(repo)))
    names = ", ".join(sorted(roles)) or ", ".join(KNOWN_ROLES)
    return _out("SubagentStart", f"ROLE LOADER (hook): if your task prompt begins `You are <Role>.` with <Role> one of "
                f"{names}, your FIRST action is `git show {TRUNK}:{ROLES_REL}/<role lowercase>.md` (or read the file in the "
                f"worktree); your FIRST reply line is then that role's banner (`python scripts/dev/role_loader.py banner <Role>`). "
                f"If the file cannot be read, reply `ROLE NOT LOADED: <why>`. No role line in the prompt: ignore this.")


def handle(payload, repo=REPO):
    """Return the hook JSON string, or '' when nothing is to be injected."""
    if not isinstance(payload, dict):
        return ""
    if payload.get("hook_event_name") == "SubagentStart":
        return handle_subagent(payload, repo)
    sid = str(payload.get("session_id") or "nosession")
    if payload.get("hook_event_name") == "SessionStart":
        done = injected(sid)
        if not done:
            return ""
        text = build_text(done[-1], repo, git_fetch(repo))
        if LAST_META:                   # trunk may have changed the role since the first load: record what was served
            mark_injected(sid, done[-1], dict(LAST_META))
        return _out("SessionStart", "Session resumed/compacted: re-confirm the role. " + text)
    prompt = payload.get("prompt")
    if not isinstance(prompt, str):
        return ""
    first = first_prompt(sid)
    roles = local_roles(repo)
    hits = match_roles(prompt, roles)
    fallback = None
    if len(hits) > 1:
        return _out("UserPromptSubmit", "ROLE LOADER (hook): the prompt names several roles (" + ", ".join(hits) +
                    "). Load none; ask the operator in one line which one, then stop.")
    if hits:
        name = hits[0]
        if name in injected(sid) and not is_reload(prompt):
            return ""
    elif is_reload(prompt):
        name = mentioned_role(prompt, roles) or (injected(sid) or [None])[-1]
        if not name:
            return ""
    elif first and not injected(sid) and not from_session(prompt):
        p = pick_role(prompt, repo)
        if p["tie"]:
            return _out("UserPromptSubmit", "ROLE LOADER (hook): the prompt has no role line and fits several roles equally ("
                        + p["reason"] + "). Ask the operator once, in one line, which role (`You are <Role>.`), then stop.")
        if not p["name"]:
            return ""
        name, fallback = p["name"], p["reason"]
    else:
        return _reminder(sid)
    text = build_text(name, repo, git_fetch(repo), fallback)
    mark_injected(sid, name, dict(LAST_META))
    return _out("UserPromptSubmit", text)


def cmd_hook():
    try:
        out = handle(json.loads(sys.stdin.read() or "{}"))
    except Exception:
        return 0
    if out:
        sys.stdout.write(out)
        sys.stdout.flush()
    return 0


# ---------- retoken / check / banner ----------
def role_files(repo=REPO):
    d = Path(repo) / ROLES_REL
    return sorted(d.glob("*.md")) if d.is_dir() else []


def retoken_file(path):
    text = Path(path).read_bytes().decode("utf-8").replace("\r\n", "\n")
    if not parse_header(text):
        return None
    tok = compute_token(text)
    first, body = split_header(text)
    new_first = re.sub(r"(token:\s*)(?:PENDING|[a-z]+-[a-z]+)", lambda m: m.group(1) + tok, first, count=1)
    if new_first != first:
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(new_first + "\n" + body)
    return tok


def row_names(repo=REPO):
    p = Path(repo) / ROLES_MD_REL
    names = []
    if p.exists():
        in_rows = False
        for ln in p.read_text(encoding="utf-8").split("\n"):
            if ln.startswith("## Rows"):
                in_rows = True
            elif ln.startswith("## "):
                in_rows = False
            elif in_rows and ln.startswith("|"):
                c = ln.split("|")[1].strip()
                if c and c != "Role" and not set(c) <= {"-"}:
                    names.append(c)
    return names


def list_lines(repo=REPO):
    roster = load_roster(repo)
    w = max([len(r["name"]) for r in roster] + [4])
    out = [f"{'Role':<{w}}  {'File':<22} {'Start':<9} {'Model':<29} {'Lane':<6} Job"]
    for r in roster:
        out.append(f"{r['name']:<{w}}  {r['file']:<22} {r['start']:<9} {r['model']:<29} {r['lane']:<6} {r['job']}")
    for r in roster:
        if r.get("aliases"):
            out.append(f"alias  {', '.join(r['aliases'])} -> {r['name']}")
    emb = [r["name"] for r in roster if r["start"] != "operator"]
    out.append(f"{len(roster)} roles ({len(roster) - len(emb)} operator-started, {len(emb)} embedded: {', '.join(emb)}; "
               f"never picked by the fallback) from {ROSTER_REL}; files in {ROLES_REL}/")
    return out


def _roles_md_block(roster):
    out = ["| Role | Start (paste) | Runs where | At most one at a time | Model | Job |", "|---|---|---|---|---|---|"]
    for r in roster:
        start = f"`{r['start_line']}`" if r["start"] == "operator" else f"embedded: {r['start_line'].strip('()')}"
        out.append(f"| `{r['name']}` | {start} | {r['where']} | {r['limit']} | {r['model']} | {r['job']} |")
    return out


def _start_here_block(roster):
    ops = [r for r in roster if r["start"] == "operator"]
    w = max(len(r["name"]) for r in ops) + 9
    out = []
    for r in ops:
        out.append(f"  {'You are ' + r['name'] + '.':<{w}}  {r['model']:<29} {r['job']}")
        if r["start_line"] != f"You are {r['name']}.":
            out.append(f"  {'':<{w}}    paste: {r['start_line']}")
    out.append("  Inside the Supervisor (never by hand, never picked by fallback): "
               + ", ".join(r["name"] for r in roster if r["start"] != "operator") + ".")
    out.append("  Old names still work: " + "; ".join(f"{', '.join(r['aliases'])} -> {r['name']}"
                                                     for r in roster if r.get("aliases")) + ".")
    out.append("  No role line? The first prompt loads the best fit:  ROLE LOADED: <Name> (fallback: <why>) ...")
    return out


RENDER_TARGETS = ((ROLES_MD_REL, _roles_md_block), (START_HERE_REL, _start_here_block))


def render(repo=REPO, write=True):
    """Rewrite the lines between the roster:begin and roster:end markers from the roster; return the stale (or rewritten) paths."""
    roster = load_roster(repo)
    stale = []
    for rel, fn in RENDER_TARGETS:
        p = Path(repo) / rel
        if not p.exists() or not roster:
            stale.append(rel)
            continue
        lines = p.read_text(encoding="utf-8").split("\n")
        b = next((i for i, ln in enumerate(lines) if "roster:begin" in ln), None)
        e = next((i for i, ln in enumerate(lines) if "roster:end" in ln), None)
        if b is None or e is None or e < b:
            stale.append(rel)
            continue
        new = lines[:b + 1] + fn(roster) + lines[e:]
        if new != lines:
            stale.append(rel)
            if write:
                with open(p, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write("\n".join(new))
    return stale


def check_roster(repo=REPO, out=print):
    roster = {r["name"]: r.get("file") for r in load_roster(repo)}
    if not roster:
        out(f"WARN roster: {ROSTER_REL} missing or unreadable (role headers still trigger)")
        return 0
    heads = {}
    for f in role_files(repo):
        h = parse_header(f.read_bytes().decode("utf-8").replace("\r\n", "\n"))
        if h:
            heads[h["name"]] = f.name
    bad = 0
    for n in sorted(set(roster) | set(heads)):
        if roster.get(n) != heads.get(n):
            out(f"FAIL roster {n}: roster file {roster.get(n)}, role-file header in {heads.get(n)}")
            bad = 1
    for rel in render(repo, write=False):
        out(f"FAIL {rel}: roster block missing or stale (run role_loader.py render)")
        bad = 1
    if not bad:
        out(f"ok   roster: {len(roster)} roles = {len(heads)} role files; rendered blocks current")
    return bad


def check(repo=REPO, out=print):
    bad = check_roster(repo, out)
    files = {f.name: f for f in role_files(repo)}
    seen = set()
    for name in row_names(repo):
        fname = file_for(name)
        f = files.get(fname)
        if not f:
            out(f"WARN {name}: no file {fname}")
            continue
        seen.add(fname)
        bad += _check_one(f, name, out)
    for fname, f in files.items():
        if fname not in seen:
            bad += _check_one(f, None, out)
    return 1 if bad else 0


def _check_one(f, name, out):
    text = f.read_bytes().decode("utf-8").replace("\r\n", "\n")
    h = parse_header(text)
    if not h:
        out(f"FAIL {name or f.name}: malformed header in {f.name}")
        return 1
    if name and h["name"] != name:
        out(f"FAIL {name}: header name {h['name']} differs from the ROLES.md row")
        return 1
    tok = compute_token(text)
    if h["token"] == "PENDING":
        out(f"ok   {h['name']} {h['version']} {f.name}: token PENDING (run retoken)")
        return 0
    if h["token"] != tok:
        out(f"FAIL {h['name']} {f.name}: STALE token {h['token']}, body gives {tok} (run retoken)")
        return 1
    out(f"ok   {h['name']} {h['version']} {f.name}: token {tok} fresh")
    return 0


BANNER_RE = re.compile(r"ROLE LOADED(?P<row> \(ROW ONLY\))?: (?P<name>\S+)(?: \(fallback: [^)]*\))? (?P<version>v\S+) \S token (?P<token>[a-z]+-[a-z?]+|none) \S "
                       r"(?P<path>\S+) @ (?P<sha>[0-9a-f]{7,40}|unknown)")


def verify(text, repo=REPO, role=None, sid=None, out=print):
    """SUPERVISOR.md trust check of a worker's banner (quoted in its note). 0 = genuine and current, 2 = genuine but the role
    file changed on trunk since the worker loaded it (tell it `reload role`), 1 = do not trust the claim.
    Proves the worker saw the role file at that trunk sha (and, with sid, that the hook injected it); not that it followed it."""
    if re.search(r"ROLE NOT LOADED", text or ""):
        out("FAIL: worker reports ROLE NOT LOADED")
        return 1
    m = BANNER_RE.search(text or "")
    if not m:
        out("FAIL: no ROLE LOADED banner in the text")
        return 1
    name, ver, tok, path, sha = (m.group(k) for k in ("name", "version", "token", "path", "sha"))
    if m.group("row"):
        out(f"FAIL {name}: ROW ONLY banner (no role file was loaded)")
        return 1
    if role and name != role:
        out(f"FAIL: banner names {name}, expected {role}")
        return 1
    want = f"{ROLES_REL}/{file_for(name)}"
    if path != want:
        out(f"FAIL {name}: banner path {path}, expected {want}")
        return 1
    if sha == "unknown" or not git_is_ancestor(repo, sha):
        out(f"FAIL {name}: sha {sha} is not on {TRUNK}")
        return 1
    then = git_show_at(repo, sha, path)
    h = parse_header(then.replace("\r\n", "\n")) if then else None
    if not h or h["name"] != name:
        out(f"FAIL {name}: no valid role file {path} at {sha}")
        return 1
    if (h["version"], compute_token(then)) != (ver, tok):
        out(f"FAIL {name}: banner {ver}/{tok} does not match the file at {sha} ({h['version']}/{compute_token(then)})")
        return 1
    if sid is not None:
        meta = role_meta(sid, name)
        if not meta or meta.get("token") != tok:
            out(f"FAIL {name}: the hook state for session {sid} has no injection with token {tok}")
            return 1
    now = git_show(repo, path)
    if now is not None and compute_token(now) != tok:
        out(f"STALE {name}: genuine {ver}/{tok} @ {sha}, but trunk now gives {compute_token(now)} (send `reload role`)")
        return 2
    out(f"ok   {name} {ver} token {tok} @ {sha}: fresh")
    return 0


def cmd_verify(args):
    role = args[args.index("--role") + 1] if "--role" in args and args.index("--role") + 1 < len(args) else None
    sid = args[args.index("--sid") + 1] if "--sid" in args and args.index("--sid") + 1 < len(args) else None
    if "--text" not in args or args.index("--text") + 1 >= len(args):
        print("usage: role_loader.py verify --text <note | -> [--role Name] [--sid <session id>]")
        return 2
    text = args[args.index("--text") + 1]
    if text == "-":
        text = sys.stdin.buffer.read().decode("utf-8", "replace")
    git_fetch(REPO)
    return verify(text, REPO, role=role, sid=sid)


def cmd_banner(name):
    f = Path(REPO) / ROLES_REL / file_for(name)
    if not f.exists():
        print(f"no role file {f.name}")
        return 1
    text = f.read_bytes().decode("utf-8").replace("\r\n", "\n")
    h = parse_header(text)
    if not h:
        print("malformed header")
        return 1
    line = banner(h["name"], h["version"], compute_token(text), f.name, git_sha8(REPO))
    sys.stdout.buffer.write((line + "\n").encode("utf-8"))
    return 0


# ---------- lint (RU4: policy contradictions, dead commands, missing files, CI-red owner line) ----------
LINT_CMD_RE = re.compile(r"\bpython\s+((?:scripts|MyTradingSys)/[A-Za-z0-9_./-]+\.py)\b")
LINT_PATH_RE = re.compile(r"`((?:scripts|MyTradingSys)/[A-Za-z0-9_./-]+\.(?:py|ps1|md|json|jsonl|csv|yml|html))`"
                          r"|(?<!/)\b((?:scripts|MyTradingSys)/[A-Za-z0-9_./-]+\.(?:py|ps1|md|json|jsonl|csv|yml|html))\b")
LINT_ROLE_SHORT_RE = re.compile(r"`(roles/[a-z0-9_]+\.md)`|(?<![A-Za-z0-9_/])\b(roles/[a-z0-9_]+\.md)\b")

# Policy rules enforced across ROLES.md and roles/*.md: (policy_id, trigger_in_roles_md, bad_pattern_in_role, neg_guard_in_line, description)
POLICY_RULES = [
    ("no-compaction",
     re.compile(r"\bno compaction\b", re.I),
     re.compile(r"\b(?:the operator compacts|after a compaction|only after a compaction|re-?run[^\n]*after a compaction|^#*\s*compaction\s*$)\b", re.I),
     re.compile(r"\b(?:no compaction|never compacted|not compacted|replaces compaction|without compaction)\b", re.I),
     "contradicts ROLES.md 'No compaction' policy"),
    ("no-live-tree-edit",
     re.compile(r"\bnever (?:edit |work in )?the live tree\b", re.I),
     re.compile(r"\b(?:edit|write to|commit in) the live tree\b", re.I),
     re.compile(r"\b(?:never|do not|don't|read[- ]only)\b", re.I),
     "contradicts ROLES.md 'never the live tree' policy"),
    ("no-secrets-read",
     re.compile(r"\b(?:\.secrets/|never read \.secrets)\b", re.I),
     re.compile(r"\breads?\s+`?\.secrets/", re.I),
     re.compile(r"\b(?:never|do not|don't|not)\b", re.I),
     "contradicts ROLES.md 'never read .secrets/' policy"),
]


def _is_planned_or_runtime_ref(ref, line):
    low = line.lower()
    if any(c in ref for c in "<>*") or "YYYY" in ref or re.search(r"\d{4}-\d\d-\d\d", ref):
        return True
    if re.search(r"MyTradingSys/(?:runtime|execution)/", ref):
        return True
    if "until it exists" in low or f"until `{ref}` exists" in low or f"until {ref} exists" in low:
        return True
    short = ref.split("MyTradingSys/system/", 1)[-1]
    if f"until `{short}` exists" in low or f"until {short} exists" in low:
        return True
    return False


def ci_red_owner(repo=REPO, runs=None):
    """Return a one-line 'CI red and owner: ...' status string (RU4)."""
    if runs is None:
        cache = Path(os.environ.get("MTS_CI_WATCH_HOME") or Path.home() / ".claude") / "mts-ci-watch.json"
        try:
            d = json.loads(cache.read_text(encoding="utf-8"))
            runs = d.get("runs") or []
        except Exception:
            runs = []
    finished = [r for r in (runs or []) if r.get("conclusion") in ("success", "failure", "timed_out", "startup_failure")]
    streak = 0
    for r in finished:
        if r.get("conclusion") == "success":
            break
        streak += 1
    if streak < 2:
        return "CI red and owner: green (0 red streak)"
    sha8 = (finished[0].get("head_sha") or "unknown")[:8]
    owner = "unclaimed (needs ci-" + sha8 + " worker)"
    tasks_dir = Path(repo) / "MyTradingSys" / "system" / "tasks"
    if tasks_dir.is_dir():
        for tf in sorted(tasks_dir.glob("ci-*.json")):
            try:
                cd = json.loads(tf.read_text(encoding="utf-8"))
            except Exception:
                continue
            if cd.get("state") not in ("done", "dropped"):
                owner = f"card {cd.get('id') or tf.stem} ({cd.get('state', 'ready')})"
                break
    return f"CI red and owner: RED ({streak} failed in a row, head {sha8}) -> owner: {owner}"


def lint(repo=REPO, out=print, ci_runs=None):
    """Lint ROLES.md and roles/*.md for policy contradictions, dead commands, and missing files (exit 1 on any defect)."""
    repo = Path(repo)
    findings = []
    roles_md_path = repo / ROLES_MD_REL
    roles_md_text = roles_md_path.read_text(encoding="utf-8", errors="replace") if roles_md_path.exists() else ""
    docs = ([roles_md_path] if roles_md_path.exists() else []) + role_files(repo)

    # 1. Policy contradictions across ROLES.md and roles/*.md
    active_rules = [r for r in POLICY_RULES if not roles_md_text or r[1].search(roles_md_text)]
    for f in role_files(repo):
        rel = f"{ROLES_REL}/{f.name}"
        for i, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            s = line.strip()
            if not s or s.startswith("<!--"):
                continue
            for pid, _, bad_re, neg_re, desc in active_rules:
                if bad_re.search(s) and not neg_re.search(s):
                    findings.append(("CONTRADICTION", f"{rel}:{i}", f"[{pid}] {desc}: {s[:120]}"))

    # 2. Dead commands and missing files in ROLES.md and roles/*.md
    for doc in docs:
        rel = ROLES_MD_REL if doc == roles_md_path else f"{ROLES_REL}/{doc.name}"
        for i, line in enumerate(doc.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if line.strip().startswith("<!--"):
                continue
            cmd_paths = set()
            for m in LINT_CMD_RE.finditer(line):
                cpath = m.group(1)
                cmd_paths.add(cpath)
                if _is_planned_or_runtime_ref(cpath, line):
                    continue
                if not (repo / cpath).exists():
                    findings.append(("DEAD-CMD", f"{rel}:{i}", f"dead command script {cpath}"))
            for m in LINT_PATH_RE.finditer(line):
                ref = m.group(1) or m.group(2)
                if not ref or ref in cmd_paths or _is_planned_or_runtime_ref(ref, line):
                    continue
                if not (repo / ref).exists():
                    if ref.startswith("scripts/") and ref.endswith((".py", ".ps1")):
                        findings.append(("DEAD-CMD", f"{rel}:{i}", f"dead command script {ref}"))
                    else:
                        findings.append(("MISSING-FILE", f"{rel}:{i}", f"missing referenced file {ref}"))
            for m in LINT_ROLE_SHORT_RE.finditer(line):
                short = m.group(1) or m.group(2)
                full = f"MyTradingSys/system/{short}"
                if _is_planned_or_runtime_ref(full, line):
                    continue
                if not (repo / full).exists():
                    findings.append(("MISSING-FILE", f"{rel}:{i}", f"missing referenced role file {full}"))

    # 3. Every role file names the files its rule answers come from (bug-haiku-stale-rule-answers)
    for f in role_files(repo):
        head = f.read_text(encoding="utf-8", errors="replace").splitlines()[:8]
        line = next((ln for ln in head if ln.startswith("Read first:")), None)
        if line is None or not re.search(r"`[\w./-]+\.(?:md|py|json|txt)`", line):
            findings.append(("READ-FIRST", f"{ROLES_REL}/{f.name}", "no `Read first:` line naming a source file in the first 8 lines"))

    for kind, where, msg in findings:
        out(f"FAIL [{kind}] {where}: {msg}")
    out(ci_red_owner(repo, runs=ci_runs))
    if not findings:
        out(f"ok   role_loader lint: {len(docs)} role guidance files clean (0 contradictions, 0 dead commands, 0 missing files)")
        return 0
    return 1


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    c = argv[1]
    if c == "hook":
        return cmd_hook()
    if c == "retoken":
        args = argv[2:]
        files = role_files() if (not args or args == ["--all"]) else [Path(a) for a in args]
        for f in files:
            print(f"{Path(f).name}: {retoken_file(f) or 'malformed header, skipped'}")
        return 0
    if c == "check":
        return check()
    if c == "list":
        sys.stdout.buffer.write(("\n".join(list_lines()) + "\n").encode("utf-8"))
        return 0
    if c == "render":
        stale = render(write="--check" not in argv)
        for rel in stale:
            print(f"{'stale' if '--check' in argv else 'rendered'} {rel}")
        return 1 if (stale and "--check" in argv) else 0
    if c == "pick":
        args = argv[2:]
        if "--text" not in args or args.index("--text") + 1 >= len(args):
            print("usage: role_loader.py pick --text <task text | ->")
            return 2
        text = args[args.index("--text") + 1]
        if text == "-":
            text = sys.stdin.buffer.read().decode("utf-8", "replace")
        p = pick_role(text)
        print(f"{p['name'] or 'NONE'}: {p['reason']}")
        return 0 if p["name"] else 1
    if c == "lint":
        return lint()
    if c == "verify":
        return cmd_verify(argv[2:])
    if c == "banner" and len(argv) > 2:
        return cmd_banner(argv[2])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
