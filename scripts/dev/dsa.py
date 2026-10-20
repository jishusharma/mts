"""dsa.py: one-call helpers for DSA (DeepSeek) driving this repo through AIBridge.

Each AIBridge command block is one chat round trip (10-20 s) on Windows PowerShell 5.1, so every multi-step ritual is ONE call
here. Stdlib only. Output is compact `key: value` lines on stdout (errors too, prefixed `error:`; PowerShell 5.1 turns
stderr into red noise). Exit codes: 0 ok, 1 could not do it, 2 refused (nothing changed). Every subcommand ends well inside 300 s.

  python scripts/dev/dsa.py host                                  # facts for THIS machine (host, java, mvn, live tree, BUILD_REPORT host match)
  python scripts/dev/dsa.py boot [--hours N]                      # host + CI line + claims + desk row + next task cards + open Q lines + news gaps (read-only)
  python scripts/dev/dsa.py begin "<task title>"                  # own worktree ../mts-dsa-<slug>, branch <host>/dsa-<slug>, sync start + claim
  python scripts/dev/dsa.py put <path> [--append]                 # write STDIN to the file (UTF-8, no BOM, LF; keeps a CRLF-only target CRLF)
                                                                  #   PS 5.1 pipes ASCII by default: first run $OutputEncoding=[Text.UTF8Encoding]::new($false)
  python scripts/dev/dsa.py edit <path> --old=<text> --new=<text> [--all] [--escapes]   # exact replace, count must be 1 (--all: N>=1)
  python scripts/dev/dsa.py edit <path> --old-file <f> --new-file <g> [--all]
  python scripts/dev/dsa.py commit "<subject>" --result "<result line>" [--files a b ...] [--session ID]   # stage + commit, never push
  python scripts/dev/dsa.py end [--slug <claim slug>]             # release the claim and remove the worktree, only when nothing is unshipped

Share work only with `python scripts/dev/sync.py ship` (this tool never pushes). Pass option values that start with `-` as
`--old=-x`. Tools used by subprocess: sync.py, desk.py, tasks.py, make_status.py.
"""
import argparse
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

TRUNK = "fast-track"
LIVE_MARKER = ".mts_live"
MIRROR_PREFIX = "runtime_data/_mirror/"
CLAIMS_DIR = "MyTradingSys/system/claims"
NEXT_SESSION = "MyTradingSys/system/NEXT_SESSION.md"
STATUS_MD = "MyTradingSys/research/STATUS.md"
BUILD_REPORT = "MyTradingSys/runtime/BUILD_REPORT.md"
HERE = Path(__file__).resolve().parent
BOOT_BUDGET_S = 240

# git subcommands / flags this tool refuses to run: nothing here may rewrite history or push.
FORBIDDEN_GIT = {"reset", "rebase", "filter-branch", "filter-repo", "replace", "push", "gc", "prune", "update-ref",
                 "reflog", "revert", "cherry-pick"}
FORBIDDEN_FLAGS = {"--amend", "--force", "-f", "--force-with-lease", "--hard"}
SAFE_FORCE = {("worktree", "remove")}      # `git worktree remove --force` deletes a folder, not history


class Refused(Exception):
    """The request breaks a rule: nothing was changed (exit 2)."""


class Failed(Exception):
    """The request was fine but could not be done (exit 1)."""


def hostname():
    return socket.gethostname()


def utc_now():
    return datetime.now(timezone.utc)


# ------------------------------------------------------------------ subprocess helpers
class Deadline:
    def __init__(self, seconds):
        self.end = time.time() + seconds

    def left(self, cap):
        return max(5, min(cap, self.end - time.time()))


def run(cmd, cwd=None, timeout=60, input_text=None):
    """-> (returncode, stdout, stderr). Never raises on a missing program or a timeout."""
    try:
        r = subprocess.run(cmd, cwd=None if cwd is None else str(cwd), capture_output=True, timeout=timeout,
                           input=None if input_text is None else input_text.encode("utf-8"))
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout:.0f}s: {' '.join(map(str, cmd))[:120]}"
    except OSError as e:
        return 127, "", f"{type(e).__name__}: {e}"
    dec = lambda b: b.decode("utf-8", errors="replace").replace("\r\n", "\n")
    return r.returncode, dec(r.stdout), dec(r.stderr)


def git(repo, *args, timeout=60, check=True):
    """Run git in `repo`. Refuses history-rewriting subcommands and force flags."""
    sub = next((a for a in args if not a.startswith("-")), "")
    if sub in FORBIDDEN_GIT:
        raise Refused(f"git {sub} is not allowed here (no history rewriting, no push; use sync.py ship)")
    bad = [a for a in args if a in FORBIDDEN_FLAGS]
    if bad and not any(tuple(args[i:i + 2]) in SAFE_FORCE for i in range(len(args))):
        raise Refused(f"git flag {bad[0]} is not allowed here")
    rc, out, err = run(["git", "-C", str(repo), *args], timeout=timeout)
    if check and rc != 0:
        raise Failed(f"git {' '.join(args)[:100]} failed: {(err or out).strip()[:300]}")
    return rc, out, err


def real(p):
    return Path(os.path.realpath(str(p)))


def repo_root(cwd=None):
    rc, out, _ = run(["git", "rev-parse", "--show-toplevel"], cwd=cwd or Path.cwd(), timeout=20)
    if rc != 0 or not out.strip():
        raise Failed("not inside a git repository")
    return real(out.strip())


def is_live(root):
    return (Path(root) / LIVE_MARKER).exists()


def worktree_rows(root):
    """[(path, branch)] from `git worktree list --porcelain`, the main working tree first."""
    rc, out, _ = git(root, "worktree", "list", "--porcelain", check=False)
    rows, cur = [], {}
    for line in out.splitlines() + [""]:
        if not line:
            if cur.get("worktree"):
                rows.append((real(cur["worktree"]), cur.get("branch", "(detached)").replace("refs/heads/", "")))
            cur = {}
        else:
            k, _, v = line.partition(" ")
            cur[k] = v
    return rows


def live_tree_path(root):
    for p, _ in worktree_rows(root):
        if (p / LIVE_MARKER).exists():
            return p
    return None


def script_path(work, name):
    """The tool from the tree we work in (its REPO is its own location); fall back to this file's folder."""
    p = Path(work) / "scripts" / "dev" / name
    return p if p.exists() else HERE / name


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40].strip("-")
    return s or "task"


# ------------------------------------------------------------------ path safety
SAFE_CODE_SUFFIXES = {".py", ".md", ".ps1", ".sh", ".java", ".html", ".tpl"}
KEY_SUFFIXES = {".key", ".pem", ".pfx", ".p12", ".ppk", ".jks", ".kdbx"}


def refused_reason(path):
    """Why DSA may not write/stage this path (secrets, keys, HALT files, .git), or None."""
    p = Path(path)
    parts = [x.lower() for x in p.parts]
    name, suffix = p.name.lower(), p.suffix.lower()
    if ".git" in parts:
        return ".git internals"
    if ".secrets" in parts:
        return ".secrets folder"
    if name == ".env" or name.startswith(".env.") or name.endswith(".env"):
        return "env file"
    if suffix in KEY_SUFFIXES or name.startswith(("id_rsa", "id_ed25519", "id_ecdsa", "id_dsa")):
        return "key file"
    if re.match(r"^halt([_.\-].*)?$", name) and suffix not in SAFE_CODE_SUFFIXES:
        return "HALT file (supervisor-only)"
    if re.search(r"(secret|api[_-]?key|credential|password|\btoken)", name) and suffix not in SAFE_CODE_SUFFIXES:
        return "looks like a secrets file"
    return None


def resolve_in_repo(root, user_path):
    """Absolute path of `user_path` (relative = from cwd), refused if outside `root` or a protected file."""
    p = Path(user_path)
    if not p.is_absolute():
        p = Path.cwd() / p
    t = real(p)
    r = real(root)
    try:
        rel = t.relative_to(r)
    except ValueError:
        if os.path.normcase(str(t)).startswith(os.path.normcase(str(r)) + os.sep):
            rel = Path(os.path.relpath(str(t), str(r)))
        else:
            raise Refused(f"{user_path} is outside the repo root {r}")
    why = refused_reason(rel)
    if why:
        raise Refused(f"{rel.as_posix()} refused: {why}")
    return t, rel


# ------------------------------------------------------------------ file text helpers
def eol_of(data):
    """'crlf' (only CRLF), 'lf' (only LF), 'mixed', or 'none' for bytes/str `data`."""
    if isinstance(data, bytes):
        crlf, lf = data.count(b"\r\n"), data.count(b"\n")
    else:
        crlf, lf = data.count("\r\n"), data.count("\n")
    bare = lf - crlf
    if crlf and not bare:
        return "crlf"
    if crlf and bare:
        return "mixed"
    return "lf" if lf else "none"


def decode_text(data, what="input"):
    """bytes -> (text, had_bom). UTF-8 (BOM stripped), or UTF-16 with BOM; anything else is refused."""
    if data.startswith(b"\xef\xbb\xbf"):
        return data[3:].decode("utf-8"), True
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16"), True
    try:
        return data.decode("utf-8"), False
    except UnicodeDecodeError as e:
        raise Refused(f"{what} is not valid UTF-8 ({e.reason} at byte {e.start}); send UTF-8 (nothing written)")


def stats(rel, data, extra=""):
    text = data.decode("utf-8", errors="replace")
    non_ascii = sum(1 for c in text if ord(c) > 127)
    cyr = sum(1 for c in text if 0x400 <= ord(c) <= 0x4FF)
    out = [f"path: {rel.as_posix()}", f"lines: {len(text.splitlines())}", f"bytes: {len(data)}",
           f"non_ascii: {non_ascii}", f"eol: {eol_of(data)}"]
    if cyr:
        out.append(f"cyrillic: {cyr} (the repo gate rejects Cyrillic codepoints)")
    if data.startswith(b"\xef\xbb\xbf"):
        out.append("bom: yes")
    return "\n".join(out) + (("\n" + extra) if extra else "")


def unescape(s):
    return re.sub(r"\\([nrt\\])", lambda m: {"n": "\n", "r": "\r", "t": "\t", "\\": "\\"}[m.group(1)], s)


# ------------------------------------------------------------------ host
def java_info():
    exe = shutil.which("java")
    if not exe:
        return "none"
    rc, out, err = run([exe, "-version"], timeout=20)
    first = ((err or out).strip().splitlines() or ["(no version output)"])[0]
    return f"{exe} | {first}"


def powershell_version():
    for exe in ("powershell", "pwsh"):
        if shutil.which(exe):
            rc, out, err = run([exe, "-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"], timeout=30)
            if rc == 0 and out.strip():
                return f"{out.strip()} ({exe})"
    return "unknown"


def build_report_host(*roots):
    for r in roots:
        if not r:
            continue
        f = Path(r) / BUILD_REPORT
        if f.exists():
            for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
                if line.lower().startswith("host:"):
                    return line.split(":", 1)[1].strip(), str(f)
            return "", str(f)
    return None, None


def host_facts(cwd=None):
    """-> ordered list of (key, value)."""
    me = hostname()
    f = [("host", me), ("utc_now", utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")),
         ("python", sys.version.split()[0]), ("java", java_info()),
         ("JAVA_HOME", os.environ.get("JAVA_HOME", "(not set)")),
         ("mvn", shutil.which("mvn") or shutil.which("mvn.cmd") or "none"),
         ("powershell", powershell_version())]
    try:
        root = repo_root(cwd)
    except Failed:
        root = None
    f.append(("repo_root", str(root) if root else "unknown"))
    if root:
        rc, b, _ = git(root, "branch", "--show-current", check=False)
        f.append(("branch", b.strip() or "(detached)"))
        live = live_tree_path(root)
        f.append(("is_live_tree", "yes" if is_live(root) else "no"))
        f.append(("live_tree", str(live) if live else "unknown"))
    else:
        f += [("branch", "unknown"), ("is_live_tree", "no"), ("live_tree", "unknown")]
        live = None
    h, src = build_report_host(live, root)
    if h is None:
        f.append(("build_report_host", "none"))
        f.append(("build_report", "none (no BUILD_REPORT.md found)"))
    else:
        f.append(("build_report_host", h or "(no host line)"))
        if h and h.lower() == me.lower():
            f.append(("build_report", "MATCH"))
        else:
            f.append(("build_report", f"OTHER HOST ({h or '?'}) - do not gate on it"))
    return f


def emit(pairs):
    for k, v in pairs:
        print(f"{k}: {v}")


def cmd_host(a):
    emit(host_facts())
    return 0


# ------------------------------------------------------------------ boot
def open_q_lines(text, host):
    """Open `Qn.` lines of NEXT_SESSION.md whose host tag is `host`, `any`, or missing. DONE lines are skipped."""
    out = []
    for line in text.splitlines():
        m = re.match(r"^\s*(Q\d+)\.\s*(.*)$", line)
        if not m:
            continue
        qid, rest = m.group(1), m.group(2).strip()
        if re.match(r"(?i)^done\b", rest):
            continue
        tag = re.search(r"(?i)\bhost=([A-Za-z0-9_,/|-]+)", rest)
        if tag:
            tags = {t.lower() for t in re.split(r"[,/|]", tag.group(1)) if t}
            if not ({"any", host.lower()} & tags):
                continue
        out.append(f"{qid}. {rest}")
    return out


def news_gaps(text):
    """-> (commit count, [header lines whose Result is '(not stated)']) from `sync.py news` output."""
    heads, gaps = [], []
    last = None
    for line in text.splitlines():
        if line and not line.startswith(" "):
            if line.startswith("nothing shipped"):
                return 0, []
            last = line
            heads.append(line)
        elif "Result: (not stated)" in line and last:
            gaps.append(last)
    return len(heads), gaps


def lane_for_host(host):
    return "DSA-" + host.upper().split("-", 1)[-1]


def read_at(work, rel, from_origin):
    if from_origin:
        rc, out, _ = git(work, "show", f"origin/{TRUNK}:{rel}", check=False)
        return out if rc == 0 else ""
    p = Path(work) / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def cmd_boot(a):
    dl = Deadline(BOOT_BUDGET_S)
    me = hostname()
    emit(host_facts())
    root = repo_root()
    git(root, "fetch", "--quiet", "origin", TRUNK, timeout=dl.left(60), check=False)
    scratch = None
    try:
        if is_live(root):
            scratch = Path(tempfile.mkdtemp(prefix="dsa-boot-"))
            wt = scratch / "tree"
            git(root, "worktree", "add", "--quiet", "--detach", str(wt), f"origin/{TRUNK}", timeout=dl.left(120))
            work = real(wt)
            print(f"source: origin/{TRUNK} (live tree: read from a scratch checkout, nothing written there)")
        else:
            work = root
            behind = git(root, "rev-list", "--count", f"HEAD..origin/{TRUNK}", check=False)[1].strip()
            print(f"source: worktree {work}")
            print(f"behind_origin: {behind or '?'} commit(s) (sync.py start merges them)")
        py = sys.executable
        # STATUS.md CI line (regenerate first, restore the tracked file afterwards so the tree stays clean)
        status_rel = STATUS_MD
        was_dirty = bool(git(work, "status", "--porcelain", "--", status_rel, check=False)[1].strip())
        rc, out, err = run([py, str(script_path(work, "make_status.py"))], cwd=work, timeout=dl.left(90))
        if rc != 0:
            print(f"make_status: FAILED rc={rc}: {(err or out).strip()[-300:]}")
        txt = read_at(work, status_rel, False)
        ci = next((l.strip() for l in txt.splitlines() if l.startswith("CI green:")), None)
        print(ci or "CI green: (no line found in STATUS.md)")
        if rc == 0 and not was_dirty and not is_live(work):
            git(work, "checkout", "--", status_rel, check=False)
        # claims
        rc, out, err = run([py, str(script_path(work, "sync.py")), "claims"], cwd=work, timeout=dl.left(60))
        claims = [l for l in out.splitlines() if l.startswith("claim ")]
        print(f"claims: {len(claims)} open" if rc == 0 else f"claims: FAILED {(err or out).strip()[:200]}")
        for l in claims:
            print("  " + l)
        # desk
        rc, out, err = run([py, str(script_path(work, "desk.py")), "next", "--host", me], cwd=work, timeout=dl.left(60))
        print(f"desk_next: {(out or err).strip().splitlines()[0] if (out or err).strip() else '(no output)'}")
        # task cards
        for lane in ("DSA", lane_for_host(me), "HAIKU", "SONNET"):
            rc, out, err = run([py, str(script_path(work, "tasks.py")), "next", "--lane", lane, "--n", "2"], cwd=work,
                               timeout=dl.left(40))
            lines = [l.strip() for l in out.splitlines() if l.strip()]
            body = " | ".join(lines) if rc == 0 and lines else "none"
            if rc not in (0, 1):
                body = f"FAILED rc={rc}: {(err or out).strip()[:150]}"
            print(f"tasks {lane}: {body}")
        # NEXT_SESSION Q lines
        qs = open_q_lines(read_at(work, NEXT_SESSION, False), me)
        print(f"open_q: {len(qs)} for {me} or any")
        for q in qs:
            print("  " + (q if len(q) <= 260 else q[:257] + "..."))
        # news gaps
        rc, out, err = run([py, str(script_path(work, "sync.py")), "news", str(a.hours)], cwd=work, timeout=dl.left(90))
        if rc != 0:
            print(f"news: FAILED {(err or out).strip()[:200]}")
        else:
            n, gaps = news_gaps(out)
            print(f"news: {n} commit(s) in the last {a.hours} h, {len(gaps)} without a Result line")
            for g in gaps:
                print("  no_result: " + g)
    finally:
        if scratch is not None:
            git(root, "worktree", "remove", "--force", str(scratch / "tree"), check=False)
            git(root, "worktree", "prune", check=False)
            shutil.rmtree(scratch, ignore_errors=True)
    return 0


# ------------------------------------------------------------------ begin
def sync_cmd(work, *args, timeout=240):
    return run([sys.executable, str(script_path(work, "sync.py")), *args], cwd=work, timeout=timeout)


def cmd_begin(a):
    title = a.title.strip()
    if not title:
        raise Refused("task title is empty")
    root = repo_root()
    me = hostname()
    slug = slugify(title)
    branch = f"{me.lower()}/dsa-{slug}"
    path = real(root).parent / f"mts-dsa-{slug}"
    git(root, "fetch", "--quiet", "origin", TRUNK, timeout=120)
    reused = False
    known = {p: b for p, b in worktree_rows(root)}
    if path in known:
        reused = True
        wt = path
    elif path.exists():
        raise Failed(f"{path} exists but is not a worktree of this repo; remove it or change the title")
    else:
        have_branch = git(root, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}", check=False)[0] == 0
        if have_branch:
            git(root, "worktree", "add", "--quiet", str(path), branch, timeout=180)
        else:
            git(root, "worktree", "add", "--quiet", str(path), "-b", branch, f"origin/{TRUNK}", timeout=180)
        wt = real(path)
    print(f"WORKTREE: {wt}" + ("   (reused)" if reused else ""))
    print(f"BRANCH: {branch}")
    rc, out, err = sync_cmd(wt, "start")
    head = next((l for l in out.splitlines() if l.startswith("host=")), None)
    print(f"start: {head or ('FAILED rc=%d %s' % (rc, (err or out).strip()[:200]))}")
    if rc != 0:
        raise Failed("sync.py start failed; fix that, then run begin again")
    rc, out, err = sync_cmd(wt, "claim", title)
    m = re.search(r"claimed (\S+?);", out)
    if rc == 0 and m:
        cslug = m.group(1)
        print(f"CLAIM: {cslug}")
    else:
        msg = (err or out).strip()
        own = re.search(r"already claimed by (\S+)", msg)
        if own and own.group(1).lower() == me.lower():
            cslug = slugify(title)
            cslug_file = next((s for s in (Path(wt) / CLAIMS_DIR).glob("*.md") if s.stem.strip("-") == cslug), None)
            cslug = cslug_file.stem if cslug_file else cslug
            print(f"CLAIM: {cslug}   (already held by this host)")
        else:
            raise Failed(f"claim failed: {msg[:300]}")
    git(wt, "config", f"branch.{branch}.dsaclaim", cslug, check=False)
    print(f"NEXT: cd {wt}   (work only there; commit with dsa.py commit; share with sync.py ship; finish with dsa.py end)")
    return 0


# ------------------------------------------------------------------ put / edit
def write_bytes(target, data):
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "wb") as fh:
        fh.write(data)


def cmd_put(a):
    root = repo_root()
    target, rel = resolve_in_repo(root, a.path)
    if sys.stdin is None or sys.stdin.isatty():
        raise Refused("put reads the file content from stdin; nothing was piped in")
    raw = sys.stdin.buffer.read()
    text, _ = decode_text(raw, "stdin")
    text = text.replace("\r\n", "\n")
    existing = target.read_bytes() if target.exists() else None
    keep_crlf = existing is not None and eol_of(existing) == "crlf"
    if keep_crlf:
        text = text.replace("\n", "\r\n")
    new = text.encode("utf-8")
    if a.append and existing is not None:
        new = existing + new
    mode = "append" if a.append and existing is not None else ("overwrite" if existing is not None else "create")
    write_bytes(target, new)
    print(f"put: {mode}")
    print(stats(rel, new))
    return 0


def cmd_edit(a):
    root = repo_root()
    target, rel = resolve_in_repo(root, a.path)
    if not target.is_file():
        raise Refused(f"{rel.as_posix()} does not exist (use put to create it)")
    if (a.old is None) == (a.old_file is None) or (a.new is None) == (a.new_file is None):
        raise Refused("give exactly one of --old/--old-file and exactly one of --new/--new-file")
    if a.old_file is not None:
        old = decode_text(Path(a.old_file).read_bytes(), "--old-file")[0]
    else:
        old = unescape(a.old) if a.escapes else a.old
    if a.new_file is not None:
        new = decode_text(Path(a.new_file).read_bytes(), "--new-file")[0]
    else:
        new = unescape(a.new) if a.escapes else a.new
    raw = target.read_bytes()
    text, bom = decode_text(raw, rel.as_posix())
    file_eol = eol_of(raw)
    crlf = file_eol == "crlf"

    def norm(s):
        if file_eol == "mixed":
            return s
        s = s.replace("\r\n", "\n")
        return s.replace("\n", "\r\n") if crlf else s

    old_n, new_n = norm(old), norm(new)
    if not old_n:
        raise Refused("--old is empty")
    count = text.count(old_n)
    if count == 0:
        print("count: 0")
        raise Refused(f"old text not found in {rel.as_posix()} (nothing changed)")
    if count > 1 and not a.all:
        print(f"count: {count}")
        raise Refused(f"old text matches {count} times in {rel.as_posix()}; add context so it is unique, or pass --all")
    out_text = text.replace(old_n, new_n)
    out = (b"\xef\xbb\xbf" if bom else b"") + out_text.encode("utf-8")
    write_bytes(target, out)
    print(stats(rel, out, f"replaced: {count}"))
    return 0


# ------------------------------------------------------------------ commit
def porcelain(root):
    """[(xy, path)] of `git status` with every untracked file listed; renames report the new path."""
    rc, out, _ = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    parts = out.split("\0")
    rows, i = [], 0
    while i < len(parts):
        e = parts[i]
        i += 1
        if len(e) < 4:
            continue
        xy, path = e[:2], e[3:]
        if xy[0] in "RC":
            i += 1                       # the old name follows as its own field
        rows.append((xy, path))
    return rows


def default_session():
    n = utc_now()
    return f"MTS-{n:%Y-%m-%d}-{n:%H%M}Z-DSA-{hostname().upper()}"


def cmd_commit(a):
    root = repo_root()
    if is_live(root):
        raise Refused(f"{root} is the live tree ({LIVE_MARKER}); never commit here. Run: dsa.py begin \"<task>\"")
    if not a.subject.strip() or not a.result.strip():
        raise Refused("commit needs a subject and --result (the operator reads Result lines)")
    skipped = []
    if a.files:
        paths = []
        for f in a.files:
            t, rel = resolve_in_repo(root, f)
            paths.append(rel.as_posix())
    else:
        paths = []
        for xy, p in porcelain(root):
            if p.startswith(MIRROR_PREFIX) or p.rstrip("/") + "/" == MIRROR_PREFIX:
                continue
            if xy == "!!":
                continue
            if refused_reason(p):
                skipped.append(p)
                continue
            if xy == "??" and git(root, "check-ignore", "-q", "--", p, check=False)[0] == 0:
                continue
            paths.append(p)
    if not paths:
        print("staged: 0")
        for s in skipped:
            print(f"skipped (protected): {s}")
        raise Failed("nothing to commit")
    rc, out, err = git(root, "add", "-A", "--", *paths, timeout=120, check=False)
    if rc != 0:
        # a path that is already staged as deleted no longer matches the working tree: fine; any other failure is real
        gone = [p for p in paths if not (root / p).exists()]
        keep = [p for p in paths if p not in gone]
        if keep:
            git(root, "add", "-A", "--", *keep, timeout=120)
    print(f"staged: {len(paths)}")
    for p in paths:
        print("  " + p)
    for s in skipped:
        print(f"skipped (protected): {s}")
    session = a.session or default_session()
    rc, out, err = git(root, "commit", "-q", "-m", a.subject.strip(), "-m", f"Result: {a.result.strip()}",
                       "-m", f"MTS-Session: {session}", "--", *paths, timeout=120, check=False)
    if rc != 0:
        raise Failed(f"git commit failed: {(err or out).strip()[:400]}")
    sha = git(root, "rev-parse", "--short", "HEAD")[1].strip()
    branch = git(root, "branch", "--show-current", check=False)[1].strip()
    print(f"commit: {sha} on {branch or '(detached)'}")
    print(f"session: {session}")
    print("NEXT: python scripts/dev/sync.py ship   (this tool never pushes)")
    return 0


# ------------------------------------------------------------------ end
def cmd_end(a):
    root = repo_root()
    me = hostname()
    if is_live(root):
        raise Refused("this is the live tree; end only closes a dsa worktree")
    rows = worktree_rows(root)
    branch = git(root, "branch", "--show-current", check=False)[1].strip()
    if not (root.name.startswith("mts-dsa-") or "/dsa-" in branch):
        raise Refused(f"{root.name} [{branch}] is not a dsa worktree (mts-dsa-<slug> / <host>/dsa-<slug>); nothing removed")
    main = live_tree_path(root) or (rows[0][0] if rows else None)
    if main is None or main == root:
        raise Failed("cannot find the main working tree to run `git worktree remove` from")
    git(root, "fetch", "--quiet", "origin", TRUNK, timeout=120, check=False)
    dirty = [f"{xy} {p}" for xy, p in porcelain(root) if not p.startswith(MIRROR_PREFIX)]
    ahead_n = git(root, "rev-list", "--count", f"origin/{TRUNK}..HEAD", check=False)[1].strip() or "?"
    if dirty or ahead_n != "0":
        print(f"unshipped: {len(dirty)} uncommitted file(s), {ahead_n} commit(s) not on origin/{TRUNK}")
        for d in dirty[:30]:
            print("  " + d)
        if ahead_n not in ("0", "?"):
            for l in git(root, "log", "--oneline", f"origin/{TRUNK}..HEAD", check=False)[1].splitlines()[:10]:
                print("  commit " + l)
        print("NEXT: dsa.py commit ..., then python scripts/dev/sync.py ship, then dsa.py end")
        return 1
    slug = a.slug or git(root, "config", "--get", f"branch.{branch}.dsaclaim", check=False)[1].strip()
    if not slug:
        want = slugify(branch.split("dsa-", 1)[-1])
        slug = next((f.stem for f in (root / CLAIMS_DIR).glob("*.md") if f.stem.strip("-") == want), "")
    claim_rel = f"{CLAIMS_DIR}/{slug}.md"
    git(root, "fetch", "--quiet", "origin", "claims", timeout=120, check=False)   # claims live on the side branch (D10 2026-10-20)
    on_origin = bool(slug) and git(root, "cat-file", "-e", f"origin/claims:{claim_rel}", check=False)[0] == 0
    if slug and ((root / claim_rel).exists() or on_origin):
        rc, out, err = sync_cmd(root, "release", slug)
        if rc != 0:
            print(f"release: FAILED {(err or out).strip()[:300]}")
            return 1
        print(f"released: {slug}")
    else:
        print(f"released: (no open claim file for {slug or 'this worktree'}; nothing to release)")
    os.chdir(str(main))
    rc, out, err = git(main, "worktree", "remove", "--force", str(root), check=False, timeout=120)
    if rc != 0:
        print(f"remove: FAILED {(err or out).strip()[:300]}")
        return 1
    git(main, "worktree", "prune", check=False)
    if branch:
        git(main, "branch", "-d", branch, check=False)
        git(main, "config", "--unset", f"branch.{branch}.dsaclaim", check=False)
    print(f"removed: {root}")
    print(f"NEXT: cd {main}   (the old folder is gone; do not stay in it)")
    return 0


# ------------------------------------------------------------------ main
def build_parser():
    ap = argparse.ArgumentParser(prog="dsa.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("host").set_defaults(f=cmd_host)
    p = sub.add_parser("boot")
    p.add_argument("--hours", type=int, default=24)
    p.set_defaults(f=cmd_boot)
    p = sub.add_parser("begin")
    p.add_argument("title")
    p.set_defaults(f=cmd_begin)
    p = sub.add_parser("put")
    p.add_argument("path")
    p.add_argument("--append", action="store_true")
    p.set_defaults(f=cmd_put)
    p = sub.add_parser("edit")
    p.add_argument("path")
    p.add_argument("--old")
    p.add_argument("--new")
    p.add_argument("--old-file")
    p.add_argument("--new-file")
    p.add_argument("--all", action="store_true")
    p.add_argument("--escapes", action="store_true", help=r"read \n \r \t \\ in --old/--new as escapes")
    p.set_defaults(f=cmd_edit)
    p = sub.add_parser("commit")
    p.add_argument("subject")
    p.add_argument("--result", required=True)
    p.add_argument("--files", nargs="+")
    p.add_argument("--session")
    p.set_defaults(f=cmd_commit)
    p = sub.add_parser("end")
    p.add_argument("--slug")
    p.set_defaults(f=cmd_end)
    return ap


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    try:
        a = build_parser().parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    try:
        return a.f(a) or 0
    except Refused as e:
        print(f"error: refused: {e}")
        return 2
    except Failed as e:
        print(f"error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
