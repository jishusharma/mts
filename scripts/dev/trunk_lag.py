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
    if git(repo, "status", "--porcelain", "--untracked-files=no").stdout.strip():
        return 0, False
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


def sync_hook_files(repo):
    """A checkout that cannot fast-forward (tracked runtime edits, e.g. SUPERVISOR_LOG.md; failure review 2026-10-23 cause 5) still
    runs its hooks from scripts/dev: take trunk's copy of each changed hook path that has no local edit of its own (or whose local
    edit already equals trunk). Deletions and locally edited files are left alone. -> number of files updated."""
    changed = git(repo, "diff", "--name-only", "HEAD", f"origin/{TRUNK}", "--", *HOOK_PATHS).stdout.split()
    take = []
    for p in changed:
        if git(repo, "cat-file", "-e", f"origin/{TRUNK}:{p}").returncode:
            continue            # deleted on trunk: removing a file here is not this hook's call
        same = not git(repo, "diff", "--quiet", f"origin/{TRUNK}", "--", p).returncode
        if same and not git(repo, "diff", "--cached", "--quiet", f"origin/{TRUNK}", "--", p).returncode:
            continue            # already trunk's copy (taken earlier)
        if git(repo, "status", "--porcelain", "--", p).stdout.strip() and not same:
            continue            # someone's own edit: never overwritten
        take.append(p)
    if take and git(repo, "checkout", f"origin/{TRUNK}", "--", *take, timeout=30).returncode == 0:
        return len(take)
    return 0


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
