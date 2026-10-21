"""Turn meter: enforces the SHORT SESSIONS cap (CLAUDE.md, operator 2026-10-09) instead of leaving it as prose.

Every turn re-reads the whole context, so a thread that runs past its task costs more with each step (a 625k-token thread
seen 2026-10-14 re-read 625k per turn). The relay (RELAY.md) only helps if sessions actually hand over; nothing made them.

Claude Code hook (project .claude/settings.json):
  PostToolUse      counts tool turns; at the cap and every NAG_EVERY after it, injects the hand-off instruction
  UserPromptSubmit counts operator turns; over either cap, injects the same instruction before Claude answers
  SessionStart     resets the counters after a clear (the context is empty again)
Never blocks, never raises: a broken meter must not break a prompt.

A turn is one assistant message: parallel tool calls in one message share one context re-read, so they count once
(the call's message id is looked up in the transcript tail; if that fails the call counts, as before).
Subagents (workflow or Agent-tool workers) share the parent's session_id but have their own, short context: their hooks
are skipped entirely, so they never move the parent's counter and are never told to hand off.

  python scripts/dev/turn_meter.py status        sessions with their counts, newest first
Env: MTS_TURN_METER=off disables; MTS_TURN_METER_HOME (state dir), MTS_TURN_METER_TOOL_CAP, MTS_TURN_METER_USER_CAP.
"""
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

TOOL_CAP = 40      # CLAUDE.md SHORT SESSIONS: 40 tool turns (operator q20, 2026-10-15; was 15)
USER_CAP = 10      # CLAUDE.md SHORT SESSIONS: 10 turns with the operator (was 5)
NAG_EVERY = 5      # after the cap, repeat every 5 tool turns (once is easy to ignore mid-step)
READ_BUDGET = 4_000_000    # operator 2026-10-18: turns allowed = budget / context size (100k -> 40 turns, 250k -> 16, 500k -> 8); no compaction
OPUS_CTX_CAP = 500_000     # Opus: long sessions are wanted; the only cap is the context size
FABLE_MESSAGES = 1         # Fable: one operator message per session, HARD (ignores MTS_TURN_METER=off and the cap env vars)
PRUNE_DAYS = 7
TAIL_START = 1 << 17   # transcript bytes read from the end to find a tool call's message (grows if big results push it out)
TAIL_MAX = 1 << 22


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


def message(state, tool_cap, user_cap, why=None):
    """Kept under 250 bytes: it sits in the context for every later turn. The how-to is in RELAY.md."""
    head = why or f"{state['tool']} tool turns / {state['user']} operator turns (cap {tool_cap} / {user_cap})"
    return (f"[TURN METER] {head}; "
            "each turn re-reads the whole context. Finish this step, then hand off per RELAY.md: commit, sync.py ship, "
            "relay.py handoff --go (unless the operator said to keep going here).")


def is_subagent(payload):
    """Claude Code sets agent_id only on hooks fired inside a subagent (it is absent on the main thread, even in --agent
    sessions); subagent transcripts live under .../subagents/. agent_type alone is NOT a signal: a --agent main thread has it."""
    if payload.get("agent_id"):
        return True
    return "/subagents/" in str(payload.get("transcript_path") or "").replace("\\", "/")


def message_id(payload):
    """Id of the assistant message that issued this tool call, read from the transcript tail; None if it cannot be found.
    Parallel tool calls share it (Claude Code writes one transcript line per content block, same message.id)."""
    tool_use_id, path = payload.get("tool_use_id"), payload.get("transcript_path")
    if not tool_use_id or not path:
        return None
    try:
        needle = str(tool_use_id).encode("utf-8")
        with open(path, "rb") as f:
            size = f.seek(0, 2)
            window = TAIL_START
            while True:
                start = max(0, size - window)
                f.seek(start)
                data = f.read(size - start)
                for line in reversed(data.split(b"\n")):
                    if needle not in line:
                        continue
                    try:
                        rec = json.loads(line)
                    except ValueError:      # a partial first line of the window
                        continue
                    if rec.get("type") == "assistant" and (rec.get("message") or {}).get("id"):
                        return str(rec["message"]["id"])
                if start == 0 or window >= TAIL_MAX:
                    return None
                window *= 4
    except (OSError, ValueError, AttributeError):
        return None


def model_and_context(payload):
    """(model name, context tokens) of the newest assistant line in the transcript tail; ("", 0) when unknown.
    Context = input + cache creation + cache read of that message: what the next turn re-reads."""
    path = payload.get("transcript_path")
    if not path:
        return "", 0
    try:
        with open(path, "rb") as f:
            size = f.seek(0, 2)
            window = TAIL_START
            while True:
                start = max(0, size - window)
                f.seek(start)
                data = f.read(size - start)
                for line in reversed(data.split(b"\n")):
                    if b'"assistant"' not in line:
                        continue
                    try:
                        msg = json.loads(line).get("message") or {}
                    except ValueError:
                        continue
                    u = msg.get("usage") or {}
                    if msg.get("model") and u and not str(msg["model"]).startswith("<"):   # skip <synthetic> error lines
                        ctx = sum(int(u.get(k) or 0) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
                        return str(msg["model"]).lower(), ctx
                if start == 0 or window >= TAIL_MAX:
                    return "", 0
                window *= 4
    except (OSError, ValueError, AttributeError, TypeError):
        return "", 0


def tier(model):
    return "fable" if "fable" in model else "opus" if "opus" in model else "default"


def is_supervisor_start(payload):
    """The coordinator start line ("You are Supervisor. Login <L>. ..."), SUPER_SESSION.md; sticky in the state file."""
    return str(payload.get("prompt") or "").lstrip().lower().startswith("you are supervisor")


def fable_block():
    return json.dumps({"decision": "block", "reason": f"[TURN METER] Fable sessions take {FABLE_MESSAGES} operator message "
                       "(hard rule, operator 2026-10-18; WORKERS.md). Start a new Fable session for the next message."})


def handle(payload):
    """Returns the text to print (may be empty). Pure apart from the state file."""
    off = os.environ.get("MTS_TURN_METER", "").lower() == "off"
    sid = payload.get("session_id")
    event = payload.get("hook_event_name")
    if not sid or not event or is_subagent(payload):
        return ""
    if off and event != "UserPromptSubmit":
        return ""
    d = home()
    path = d / f"{safe_id(sid)}.json"
    tool_cap, user_cap = caps()
    state = load(path)
    out = ""
    if event == "UserPromptSubmit":
        state["user"] = state.get("user", 0) + 1
        model, ctx = model_and_context(payload)
        kind = tier(model)
        if is_supervisor_start(payload):
            state["role"] = "supervisor"     # sticky: it runs unattended for hours; capped by context, not turns (operator 2026-10-21)
        if state.get("role") == "supervisor" and kind == "default":
            kind = "opus"
        if kind == "fable":
            state["tier"] = "fable"      # sticky: a later failed detection must not lift the hard block
        elif state.get("tier") == "fable" and not model:
            kind = "fable"
        if kind == "fable" and state["user"] > FABLE_MESSAGES:     # the hard rule: no switch turns it off
            state["user"] -= 1
            save(path, state)
            return fable_block()
        if off:
            save(path, state)
            return ""
        if kind == "opus":
            if ctx >= OPUS_CTX_CAP:
                out = message(state, tool_cap, user_cap, f"Opus context {ctx // 1000}k >= {OPUS_CTX_CAP // 1000}k cap")
        else:
            if kind == "default" and ctx:
                tool_cap = min(tool_cap, max(5, READ_BUDGET // ctx))
            if state["user"] > user_cap or state.get("tool", 0) >= tool_cap:
                out = message(state, tool_cap, user_cap)
        state["last"] = now_iso()
        state["cwd"] = payload.get("cwd", state.get("cwd", ""))
        save(path, state)
        return out
    if event == "SessionStart":
        if payload.get("source") == "clear" or not path.exists():
            state = {"tool": 0, "user": 0, "since": now_iso()}
        prune(d)
    elif event == "PostToolUse":
        mid = message_id(payload)
        if mid is not None and mid == state.get("msg"):
            return ""       # another call of a message already counted: one context re-read, one turn
        state["tool"] = state.get("tool", 0) + 1
        state["msg"] = mid
        t = state["tool"]
        model, ctx = model_and_context(payload)
        kind = tier(model)
        if state.get("role") == "supervisor" and kind == "default":
            kind = "opus"
        if kind == "default" and ctx:
            tool_cap = min(tool_cap, max(5, READ_BUDGET // ctx))
        if kind == "fable":
            pass        # no tool-turn cap: one message, however long it takes
        elif kind == "opus":
            if ctx >= OPUS_CTX_CAP and t % NAG_EVERY == 0:
                out = json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": message(
                    state, tool_cap, user_cap, f"Opus context {ctx // 1000}k >= {OPUS_CTX_CAP // 1000}k cap")}})
        elif t >= tool_cap and (t - tool_cap) % NAG_EVERY == 0:
            out = json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                                     "additionalContext": message(state, tool_cap, user_cap)}})
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
            import traceback    # only on failure: imported at the top it adds ~30-45 ms to every hook call
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
