"""scripts/dev/role_loader.py: loads a role's workflow deterministically when the operator opens a session with
"You are Eagle_Eyes" (or "I need a pipeliner" ...), and lets the operator verify it in one glance.

Header = line 1 of every MyTradingSys/system/roles/*.md:
  <!-- role: <Name> | version: v<N> | token: <word>-<word> | triggers: a, b, c -->
The token is DERIVED from the file body (every line after line 1): sha256 -> two 16-bit chunks -> two words of WORDS.
Any body edit changes the token, so a stale token is detectable (`check`). `token: PENDING` is a placeholder.

  hook    UserPromptSubmit hook: on a role trigger, inject the role file from origin/fast-track + a banner instruction.
  retoken [--all | file...]   rewrite tokens in headers.
  check   rows of ROLES.md vs files vs header validity vs token freshness (exit 1 on malformed or stale).
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
KNOWN_ROLES = ["Eagle_Eyes", "Lab_Guy", "Session_Planner", "MTS_Doctor", "Artifacts_Guy", "Network_Admin_Guy",
               "Q&A_Helper", "Pipeliner", "Supervisor"]

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


def banner(name, version, token, fname, sha8, row_only=False):
    tag = "ROLE LOADED (ROW ONLY)" if row_only else "ROLE LOADED"
    return f"{tag}: {name} {version} · token {token} · {ROLES_REL}/{fname} @ {sha8}"


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
    out = {n: [n.lower()] for n in KNOWN_ROLES}
    d = Path(repo) / ROLES_REL
    if d.is_dir():
        for f in sorted(d.glob("*.md")):
            try:
                with open(f, encoding="utf-8", newline="") as fh:
                    h = parse_header(fh.readline())
            except Exception:
                continue
            if h:
                out[h["name"]] = sorted(set(out.get(h["name"], []) + [h["name"].lower()] + h["triggers"]))
    return out


def _phrase(t):
    return "[_ ]".join(re.escape(p) for p in re.split(r"[_ ]+", t.strip()) if p)


def match_roles(prompt, roles):
    """Distinct role names asked for in the first 300 chars: the phrase must start a line or sentence (a quote, a
    negation or a mid-sentence mention does not count)."""
    head = (prompt or "")[:300].lower()
    hits = []
    for name, trigs in roles.items():
        for t in trigs:
            if re.search(r"(?:^|[.!?])[ 	]*" + PREFIX + r"\s+" + _phrase(t) + r"(?![a-z0-9_])", head, re.M):
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


def mark_injected(sid, name, meta=None):
    try:
        p = state_path(sid)
        p.parent.mkdir(parents=True, exist_ok=True)
        d = _load(sid)
        if name not in d["roles"]:
            d["roles"].append(name)
        if meta:
            d["meta"][name] = meta
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(d))
    except Exception:
        pass


# ---------- hook ----------
def boot_step(body):
    lines = body.split("\n")
    for i, ln in enumerate(lines):
        s = ln.strip()
        m = re.match(r"^(?:#+\s*)?boot\b[^:\n]*?(?::\s*(.*))?$", s, re.I)
        if m and not s.startswith("|"):
            inline = (m.group(1) or "").strip()
            if len(inline) > 12:
                return inline[:240]
            for nx in lines[i + 1:]:
                if nx.strip():
                    return nx.strip()[:240]
    return "(first step of the file's boot section)"


LAST_META = {}


def build_text(name, repo, fetched_ok):
    LAST_META.clear()
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
        b = banner(h["name"], h["version"], tok, fname, sha8)
        return (f"{stale}ROLE LOADER (hook): you are {h['name']}. The file below is the authoritative workflow "
                f"({ROLES_REL}/{fname} on {TRUNK} @ {sha8}).\n"
                f"Your FIRST reply must begin with exactly this line:\n{b}\n"
                f"then on the next line: FIRST ACTION: {boot_step(body)}\n"
                f"If anything is missing or unreadable, reply `ROLE NOT LOADED: <why>` and stop.\n"
                f"----- {fname} -----\n{text}")
    rows = git_show(repo, ROLES_MD_REL) or ""
    row = next((ln for ln in rows.split("\n") if re.match(r"^\|\s*" + re.escape(name) + r"\s*\|", ln)), None)
    if row is None:
        return (f"{stale}ROLE LOADER (hook): role {name} has no file ({ROLES_REL}/{fname}) and no ROLES.md row on {TRUNK}. "
                f"Reply `ROLE NOT LOADED: no file and no row for {name}` and stop.")
    b = banner(name, "v?", "none", fname, sha8, row_only=True)
    return (f"{stale}ROLE LOADER (hook): you are {name}. No role file on {TRUNK}; the ROLES.md row below is all there is.\n"
            f"Your FIRST reply must begin with exactly this line:\n{b}\n"
            f"then follow the row's Boot column. If anything is missing, reply `ROLE NOT LOADED: <why>` and stop.\n"
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
    path = f"{ROLES_REL}/{m['file']}"
    return _out("UserPromptSubmit", f"Role: {name} {m['version']} (token {m['token']}, {path}). Follow that file; if you no longer "
                f"have it in context, say ROLE CONTEXT LOST and re-read it with git show {TRUNK}:{path}.")


def handle(payload, repo=REPO):
    """Return the hook JSON string, or '' when nothing is to be injected."""
    if not isinstance(payload, dict):
        return ""
    sid = str(payload.get("session_id") or "nosession")
    if payload.get("hook_event_name") == "SessionStart":
        done = injected(sid)
        if not done:
            return ""
        text = build_text(done[-1], repo, git_fetch(repo))
        return _out("SessionStart", "Session resumed/compacted: re-confirm the role. " + text)
    prompt = payload.get("prompt")
    if not isinstance(prompt, str):
        return ""
    roles = local_roles(repo)
    hits = match_roles(prompt, roles)
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
    else:
        return _reminder(sid)
    text = build_text(name, repo, git_fetch(repo))
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


def check(repo=REPO, out=print):
    bad = 0
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


BANNER_RE = re.compile(r"ROLE LOADED(?P<row> \(ROW ONLY\))?: (?P<name>\S+) (?P<version>v\S+) \S token (?P<token>[a-z]+-[a-z?]+|none) \S "
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
    if c == "verify":
        return cmd_verify(argv[2:])
    if c == "banner" and len(argv) > 2:
        return cmd_banner(argv[2])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
