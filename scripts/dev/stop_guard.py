"""Stop guard: a session may not end with uncommitted files or unshipped commits in its own worktree.

Sessions kept leaving work behind (2026-10-15: 26 trees held unshipped work). Claude Code Stop hook (.claude/settings.json):
when the session tries to stop and `sync.py where` logic says its tree holds real work, block ONCE with the instruction to
commit and `sync.py ship`. A second stop in the same turn (stop_hook_active) is always allowed: a stuck gate must not trap a
session in a loop. Never raises. Ignores the live tree (.mts_live), trunk checkouts and regenerable noise.
Env: MTS_STOP_GUARD=off disables.
Run by hand: python scripts/dev/stop_guard.py check   (prints the reason, or nothing)
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nowin  # noqa: E402

nowin.install()


def reason(path):
    """Why `path` may not stop yet, or None."""
    import sync
    top = sync.toplevel(Path(path))
    if (top / sync.LIVE_MARKER).exists():
        return None
    branch = sync.git(top, "branch", "--show-current", check=False).stdout.strip()
    if branch in (sync.TRUNK, "master", "main") or branch.startswith("gemini-q/"):
        return None
    state = sync.tree_state(top)
    t = dict(path=str(top), name=top.name, branch=branch, ahead=state[0], work=state[1], noise=state[2], fix="")
    return sync.unshipped_reason(t)


def message(why):
    return (f"STOP GUARD: this worktree still holds work ({why}). Commit it (body ends `Result: ...`) and run "
            f"`python scripts/dev/sync.py ship`; if the files are scratch, delete them or add them to .gitignore. "
            f"Then end the session.")


def seen_before(session_id, why):
    """True when this session was already blocked on this exact state: repeating the block only costs a ~150k-token turn
    (Opus review 2026-10-18: 95 blocks in 12 sessions, 74 of them 'commits not shipped'). The state is remembered per session."""
    if not session_id:
        return False
    f = Path(os.environ.get("MTS_STOP_GUARD_HOME") or Path.home() / ".claude") / "mts-stop-guard.json"
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        d = {}
    if d.get(session_id) == why:
        return True
    d.pop(session_id, None)
    d[session_id] = why
    d = dict(list(d.items())[-50:])     # last 50 sessions: interleaved sessions no longer erase each other (review 2026-10-21)
    try:
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(d), encoding="utf-8", newline=chr(10))
    except OSError:
        pass
    return False


def hook(stdin_text):
    """-> JSON string for Claude Code or Antigravity, or '' to allow the stop."""
    try:
        if os.environ.get("MTS_STOP_GUARD", "").lower() == "off":
            return ""
        data = json.loads(stdin_text or "{}")
        if data.get("stop_hook_active"):
            return ""
        is_agy = "conversationId" in data or "terminationReason" in data or "workspacePaths" in data
        if is_agy and data.get("terminationReason", "NO_TOOL_CALL") != "NO_TOOL_CALL":
            return ""
        ws = data.get("workspacePaths") or []
        cwd = data.get("cwd") or (ws[0] if ws else None) or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
        sid = data.get("session_id") or data.get("conversationId")
        why = reason(cwd)
        if not why or seen_before(sid, why):
            return ""
        decision = "continue" if is_agy else "block"
        return json.dumps({"decision": decision, "reason": message(why)})
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
