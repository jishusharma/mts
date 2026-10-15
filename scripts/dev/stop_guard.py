"""Stop guard: a session may not end with uncommitted files or unshipped commits in its own worktree.

Sessions kept leaving work behind (2026-10-15: 26 trees held unshipped work). Claude Code Stop hook (.claude/settings.json):
when the session tries to stop and `sync.py where` logic says its tree holds real work, block ONCE with the instruction to
commit and `sync.py ship`. A second stop in the same turn (stop_hook_active) is always allowed: a stuck gate must not trap a
session in a loop. Never raises. Ignores the live tree (.mts_live), trunk checkouts and regenerable noise.
Safety net (2026-10-15): on every stop that finds work, before blocking or not, the tree is snapshotted losslessly to
refs/leftovers/<tree> on the private local backup repo (remote `backup`, F:/MTS_backup.git; backup_snapshot.leftovers_snapshot:
temp index + commit-tree, the tree itself is never touched, never the public origin). A crash that skips this hook is covered
by daily_hygiene.py, which snapshots every dirty idle tree the same way.
Env: MTS_STOP_GUARD=off disables.
Run by hand: python scripts/dev/stop_guard.py check   (prints the reason, or nothing)
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def reason(path, with_top=False):
    """Why `path` may not stop yet, or None (with_top: (reason, toplevel))."""
    import sync
    top = sync.toplevel(Path(path))
    why = None
    if not (top / sync.LIVE_MARKER).exists():
        branch = sync.git(top, "branch", "--show-current", check=False).stdout.strip()
        if branch not in (sync.TRUNK, "master", "main"):
            state = sync.tree_state(top)
            t = dict(path=str(top), name=top.name, branch=branch, ahead=state[0], work=state[1], noise=state[2], fix="")
            why = sync.unshipped_reason(t)
    return (why, top) if with_top else why


def snapshot(top):
    """Park the tree on the private backup repo; -> a short note for the block message (never raises)."""
    try:
        import backup_snapshot
        ref, what = backup_snapshot.leftovers_snapshot(top)
        return f"{ref}: {what}"
    except Exception as e:
        return f"snapshot failed: {e}"


def message(why, snap=""):
    saved = f" A lossless copy is parked at {snap} (backup repo only)." if snap else ""
    return (f"STOP GUARD: this worktree still holds work ({why}).{saved} Commit it (body ends `Result: ...`) and run "
            f"`python scripts/dev/sync.py ship`; if the files are scratch, delete them or add them to .gitignore. "
            f"Then end the session.")


def hook(stdin_text):
    """-> JSON string for Claude Code, or '' to allow the stop."""
    try:
        if os.environ.get("MTS_STOP_GUARD", "").lower() == "off":
            return ""
        data = json.loads(stdin_text or "{}")
        why, top = reason(data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd(), with_top=True)
        if not why:
            return ""
        snap = snapshot(top)              # every stop with work, including the second one that is allowed through
        if data.get("stop_hook_active"):
            return ""                     # never a loop
        return json.dumps({"decision": "block", "reason": message(why, snap)})
    except Exception:
        return ""


def main(argv):
    if argv[:1] == ["hook"]:
        out = hook(sys.stdin.read())
        if out:
            print(out)
        return 0
    if argv[:1] == ["check"]:
        try:
            why = reason(Path.cwd())
        except Exception as e:
            print(f"stop_guard: {e}", file=sys.stderr)
            return 1
        if why:
            print(message(why))
            return 1
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
