"""Turn meter: enforces the SHORT SESSIONS cap (CLAUDE.md, operator 2026-10-09) instead of leaving it as prose.

Every turn re-reads the whole context, so a thread that runs past its task costs more with each step (a 625k-token thread
seen 2026-10-14 re-read 625k per turn). The relay (RELAY.md) only helps if sessions actually hand over; nothing made them.

Claude Code hook (project .claude/settings.json):
  PostToolUse      counts tool turns; at the cap and every NAG_EVERY after it, injects the hand-off instruction
  UserPromptSubmit counts operator turns; over either cap, injects the same instruction before Claude answers
  SessionStart     resets the counters after a compact or clear (the context is small again)
Never blocks, never raises: a broken meter must not break a prompt.

  python scripts/dev/turn_meter.py status        sessions with their counts, newest first
Env: MTS_TURN_METER=off disables; MTS_TURN_METER_HOME (state dir), MTS_TURN_METER_TOOL_CAP, MTS_TURN_METER_USER_CAP.
"""
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

TOOL_CAP = 15      # CLAUDE.md SHORT SESSIONS: 15 tool turns
USER_CAP = 5       # CLAUDE.md SHORT SESSIONS: 5 turns with the operator
NAG_EVERY = 5      # after the cap, repeat every 5 tool turns (once is easy to ignore mid-step)
PRUNE_DAYS = 7


def home():
    return Path(os.environ.get("MTS_TURN_METER_HOME") or Path.home() / ".claude" / "mts-turn-meter")


def caps():
    return (int(os.environ.get("MTS_TURN_METER_TOOL_CAP") or TOOL_CAP),
            int(os.environ.get("MTS_TURN_METER_USER_CAP") or USER_CAP))


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def safe_id(sid):
    return "".join(c for c in str(sid) if c.isalnum() or c in "-_")[:80] or "unknown"


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"tool": 0, "user": 0, "since": now_iso()}


def save(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(state, f)


def prune(d):
    cutoff = time.time() - PRUNE_DAYS * 86400
    for p in d.glob("*.json"):
        try:
            if p.stat().st_mtime < cutoff:
                p.unlink()
        except OSError:
            pass


def message(state, tool_cap, user_cap):
    return (f"[TURN METER] This session is at {state['tool']} tool turns / {state['user']} operator turns "
            f"(SHORT SESSIONS cap {tool_cap} / {user_cap}, CLAUDE.md). Every further turn re-reads the whole context.\n"
            "Finish the step you are on, then hand off: commit + `python scripts/dev/sync.py ship`; write what is left as a scoped "
            "Qn task in MyTradingSys/system/NEXT_SESSION.md (RELAY.md Task list standard) and run `python scripts/sched/relay.py handoff "
            "--file MyTradingSys/system/NEXT_SESSION.md --go` so the dispatcher runs it in a fresh session; an operator-driven thread "
            "may instead start a fresh session (start_session, context \"fresh\", a full brief). Then `sync.py where`, one line, stop.\n"
            "Only if the operator said in this session to keep going here: say so once and continue.")


def handle(payload):
    """Returns the text to print (may be empty). Pure apart from the state file."""
    if os.environ.get("MTS_TURN_METER", "").lower() == "off":
        return ""
    sid = payload.get("session_id")
    event = payload.get("hook_event_name")
    if not sid or not event:
        return ""
    d = home()
    path = d / f"{safe_id(sid)}.json"
    tool_cap, user_cap = caps()
    state = load(path)
    out = ""
    if event == "SessionStart":
        if payload.get("source") in ("compact", "clear") or not path.exists():
            state = {"tool": 0, "user": 0, "since": now_iso()}
        prune(d)
    elif event == "PostToolUse":
        state["tool"] = state.get("tool", 0) + 1
        t = state["tool"]
        if t >= tool_cap and (t - tool_cap) % NAG_EVERY == 0:
            out = json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                                     "additionalContext": message(state, tool_cap, user_cap)}})
    elif event == "UserPromptSubmit":
        state["user"] = state.get("user", 0) + 1
        if state["user"] > user_cap or state.get("tool", 0) >= tool_cap:
            out = message(state, tool_cap, user_cap)
    else:
        return ""
    state["last"] = now_iso()
    state["cwd"] = payload.get("cwd", state.get("cwd", ""))
    save(path, state)
    return out


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
            home().mkdir(parents=True, exist_ok=True)
            with open(home() / "hook_errors.log", "a", encoding="utf-8", newline="\n") as f:
                f.write(now_iso() + "\n" + traceback.format_exc() + "\n")
        except OSError:
            pass
    return 0


def status():
    tool_cap, user_cap = caps()
    rows = []
    for p in home().glob("*.json"):
        s = load(p)
        rows.append((s.get("last", ""), p.stem, s.get("tool", 0), s.get("user", 0), s.get("cwd", "")))
    for last, sid, t, u, cwd in sorted(rows, reverse=True)[:20]:
        flag = "OVER" if t >= tool_cap or u > user_cap else "ok"
        print(f"{last}  {flag:4}  tool={t:<4} user={u:<3} {sid}  {cwd}")
    if not rows:
        print("no sessions metered yet")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    sys.exit(hook() if cmd == "hook" else status())
