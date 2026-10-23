"""Trunk lag: tell a running session, at each operator prompt, when its tree has fallen behind trunk (operator 2026-10-22).

Operator 2026-10-22: "Claude always looks at the stale data ... sessions are not looking into the latest code." `sync.py start`
merges trunk once at boot; a session that then runs for hours reads code, docs and STATUS from that old base. Claude Code
UserPromptSubmit hook (.claude/settings.json): fetches origin/fast-track at most every FETCH_EVERY_S, counts the trunk commits
this tree lacks and, when the oldest of them landed more than LAG_S ago or MAX_BEHIND are missing, prints one line telling
the session to merge before it reads code or quotes state. Silent otherwise. Never raises, never blocks; skips the live tree.
SessionStart (`session-start`): a clean checkout with no commits of its own (a device's main checkout on fast-track, or a fresh App
worktree cut from it) fast-forwards to origin/fast-track first, and so does the device's main checkout, so a session started on any device
runs trunk's scripts (2026-10-22: NB and the laptop ran Supervisors on old hooks; nobody pulls there; App worktrees were cut from that
old base). Checkouts with their own commits (`sync.py start` merges those), tracked edits, master and the live tree are left alone.
Env: MTS_TRUNK_LAG=off disables.
Run by hand: python scripts/dev/trunk_lag.py check   (prints the line, or nothing)
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nowin  # noqa: E402

nowin.install()

TRUNK = "fast-track"
FETCH_EVERY_S = 600
LAG_S = 3600
MAX_BEHIND = 30
STAMP = "mts_trunk_fetch"


def git(repo, *args, timeout=8):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=timeout)


def message(behind, oldest_age_s):
    """The warning line, or '' when the tree is close enough to trunk."""
    if behind <= 0 or (oldest_age_s < LAG_S and behind < MAX_BEHIND):
        return ""
    age = f"{oldest_age_s / 3600:.1f} h" if oldest_age_s >= 3600 else f"{oldest_age_s / 60:.0f} min"
    return (f"TRUNK LAG: this tree is {behind} commit(s) behind origin/{TRUNK}; the oldest one landed {age} ago. Code, docs, "
            f"cards and STATUS read here are that old. Run `git merge origin/{TRUNK}` (or `python scripts/dev/sync.py start "
            f"<slug>`) before reading code or quoting state.")


def lag(repo, now=None, fetch=True):
    """(commits behind origin/fast-track, age in s of the oldest of them); (0, 0) when unknown."""
    now = now or time.time()
    gd = git(repo, "rev-parse", "--absolute-git-dir").stdout.strip()
    if not gd:
        return 0, 0
    stamp = Path(gd) / STAMP
    if fetch:
        try:
            last = float(stamp.read_text().strip())
        except (OSError, ValueError):
            last = 0
        if now - last >= FETCH_EVERY_S:
            git(repo, "fetch", "--quiet", "origin", TRUNK)
            try:
                stamp.write_text(str(now), newline=chr(10))
            except OSError:
                pass
    out = git(repo, "log", "--format=%ct", f"HEAD..origin/{TRUNK}").stdout.split()
    if not out:
        return 0, 0
    return len(out), max(0, now - min(int(x) for x in out))


def check(repo=None, fetch=True):
    repo = Path(repo or os.getcwd())
    if ".mts_live" in repo.resolve().parts:
        return ""
    behind, age = lag(repo, fetch=fetch)
    return message(behind, age)


def fast_forward(repo, fetch=True):
    """Fast-forward one clean checkout that has no commits of its own to origin/fast-track; -> (commits moved, hooks changed)."""
    repo = Path(repo)
    if ".mts_live" in repo.resolve().parts or (repo / ".mts_live").exists():
        return 0, False
    if git(repo, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip() in ("", "HEAD", "master", "main"):
        return 0, False
    if git(repo, "status", "--porcelain", "--untracked-files=no").stdout.strip() and not release_synced(repo):
        return 0, False         # tracked edits; the hook files this hook took itself do not count (released first)
    if fetch:
        git(repo, "fetch", "--quiet", "origin", TRUNK, timeout=30)
    if git(repo, "merge-base", "--is-ancestor", "HEAD", f"origin/{TRUNK}").returncode:
        return 0, False         # commits of its own: `sync.py start` merges those, never this hook
    behind = len(git(repo, "rev-list", f"HEAD..origin/{TRUNK}").stdout.split())
    if not behind:
        return 0, False
    hooks = bool(git(repo, "diff", "--name-only", f"HEAD..origin/{TRUNK}", "--", ".claude/settings.json").stdout.strip())
    if git(repo, "merge", "--ff-only", "--quiet", f"origin/{TRUNK}", timeout=30).returncode:
        return 0, False
    return behind, hooks


HOOK_PATHS = ("scripts/dev", ".claude/settings.json")


SYNC_RECORD = "mts_hook_sync.json"     # in the git dir: {path: blob} this hook took from trunk (its own edits, not anyone's)
NUL = chr(0)


def _z(repo, *args, timeout=30):
    """NUL-separated git output as a list (paths with spaces or non-ASCII stay whole)."""
    return [x for x in git(repo, *args, timeout=timeout).stdout.split(NUL) if x]


def _blobs(repo, *args):
    """{path: blob} from `git ls-tree -r -z <tree>` or `git ls-files -s -z`."""
    out = {}
    for rec in _z(repo, *args):
        meta, _, path = rec.partition("\t")
        parts = meta.split()
        if len(parts) >= 3:
            out[path] = parts[2] if parts[1] == "blob" else parts[1]
    return out


def _record_path(repo):
    gd = git(repo, "rev-parse", "--absolute-git-dir").stdout.strip()
    return Path(gd) / SYNC_RECORD if gd else None


def _load_record(repo):
    p = _record_path(repo)
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p else {}
    except (OSError, ValueError):
        return {}


def _hook_state(repo):
    """(HEAD blobs, index blobs, worktree-vs-index dirty paths, record) for the hook paths: four git calls in all."""
    head = _blobs(repo, "ls-tree", "-r", "-z", "HEAD", "--", *HOOK_PATHS)
    index = {p: b for p, b in _blobs(repo, "ls-files", "-s", "-z", "--", *HOOK_PATHS).items()}
    dirty = set(_z(repo, "diff", "--name-only", "-z", "--", *HOOK_PATHS))
    return head, index, dirty, _load_record(repo)


def _ours(path, head, index, dirty, record):
    """True when this path is unedited (index = HEAD) or holds exactly what this hook took earlier, worktree = index."""
    if path in dirty:
        return False
    i = index.get(path)
    return i is not None and (i == head.get(path) or i == record.get(path))


def sync_hook_files(repo):
    """A checkout that cannot fast-forward (tracked runtime edits, e.g. SUPERVISOR_LOG.md; failure review 2026-10-23 cause 5) still
    runs its hooks from scripts/dev: take trunk's copy of each changed hook path that is unedited or holds what this hook took
    before (recorded in the git dir). Anyone's own edit (worktree or staged), an untracked file and trunk deletions are left
    alone. -> number of files updated."""
    trunk = _blobs(repo, "ls-tree", "-r", "-z", f"origin/{TRUNK}", "--", *HOOK_PATHS)
    if not trunk:
        return 0
    head, index, dirty, record = _hook_state(repo)
    take = []
    for p, t in trunk.items():
        if index.get(p) == t and p not in dirty:
            continue            # already trunk's copy
        if p not in index:
            if p in head or (Path(repo) / p).exists():
                continue        # deleted here, or someone's untracked file
            take.append(p)      # new on trunk
        elif _ours(p, head, index, dirty, record):
            take.append(p)
    done = []
    for i in range(0, len(take), 100):          # Windows command-line length
        chunk = take[i:i + 100]
        if git(repo, "checkout", f"origin/{TRUNK}", "--", *chunk, timeout=60).returncode == 0:
            done += chunk
    if done:
        record.update({p: trunk[p] for p in done})
        rp = _record_path(repo)
        try:
            rp.write_text(json.dumps(record), encoding="utf-8", newline=chr(10))
        except (OSError, AttributeError):
            pass
    return len(done)


def release_synced(repo):
    """Before a fast-forward: put the files this hook took back to HEAD (or remove a new one), so `merge --ff-only` re-applies
    trunk's copy. Returns False when a tracked edit of anyone else remains (the fast-forward must not run)."""
    status = _z(repo, "status", "--porcelain=v1", "-z", "--untracked-files=no", timeout=30)
    paths = [rec[3:] for rec in status if len(rec) > 3]
    if not paths:
        return True
    head, index, dirty, record = _hook_state(repo)
    if not all(p in record and index.get(p) == record[p] and p not in dirty for p in paths):
        return False
    back = [p for p in paths if p in head]
    new = [p for p in paths if p not in head]
    if back and git(repo, "checkout", "HEAD", "--", *back, timeout=60).returncode:
        return False
    for p in new:
        git(repo, "rm", "-q", "-f", "--cached", "--", p)
        try:
            (Path(repo) / p).unlink()
        except OSError:
            pass
    return True


def main_checkout(repo):
    """The repo's main working tree (first `git worktree list` entry), or None."""
    for line in git(repo, "worktree", "list", "--porcelain").stdout.splitlines():
        if line.startswith("worktree "):
            return Path(line[9:])
    return None


def catch_up(repo=None, fetch=True):
    """SessionStart: fast-forward this checkout (trunk, or an App worktree with no commits of its own) and the device's main
    checkout when it sits clean on fast-track, so the next App worktree is cut from trunk too; returns the note, or ''."""
    repo = Path(repo or os.getcwd())
    behind, hooks = fast_forward(repo, fetch)
    notes = []
    if behind:
        notes.append(f"TRUNK CATCH-UP: this checkout fast-forwarded {behind} commit(s) to origin/{TRUNK} at session start.")
        if hooks:
            notes.append(".claude/settings.json changed: this session runs the old hook list; the next session loads the new one.")
    main = main_checkout(repo)
    if main and main.resolve() != repo.resolve() and git(main, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip() == TRUNK:
        n, _ = fast_forward(main, fetch=False)
        left = len(git(main, "rev-list", f"HEAD..origin/{TRUNK}").stdout.split())
        if n:
            notes.append(f"Main checkout {main} fast-forwarded {n} commit(s), so the next session cut from it starts on trunk.")
        elif left:
            k = sync_hook_files(main)
            hooks_note = f"; its hook scripts were updated from trunk ({k} file(s))" if k else ""
            notes.append(f"Main checkout {main} is {left} commit(s) behind origin/{TRUNK} and was left alone (local edits){hooks_note}: "
                         f"sessions cut from it start old, so run `python scripts/dev/sync.py start <slug>` before reading code.")
    return " ".join(notes)


def main(argv):
    if os.environ.get("MTS_TRUNK_LAG", "").lower() == "off":
        return 0
    if argv[:1] == ["session-start"]:
        try:
            sys.stdin.read()
            text = catch_up()
        except Exception:
            return 0
        if text:
            print(text)
        return 0
    if argv[:1] in (["hook"], ["check"]):
        try:
            if argv[:1] == ["hook"]:
                sys.stdin.read()
            text = check()
        except Exception:
            return 0
        if text:
            print(text)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
