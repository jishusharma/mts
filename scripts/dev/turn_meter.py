"""Turn meter: enforces the SHORT SESSIONS cap (CLAUDE.md, operator 2026-10-09) instead of leaving it as prose.

Every turn re-reads the whole context, so a thread that runs past its task costs more with each step (a 625k-token thread
seen 2026-10-14 re-read 625k per turn). The relay (RELAY.md) only helps if sessions actually hand over; nothing made them.

Claude Code hook (project .claude/settings.json):
  PostToolUse      counts tool turns; at the cap and every NAG_EVERY after it, injects the hand-off instruction
  UserPromptSubmit counts operator turns; over either cap, injects the same instruction before Claude answers
  PreToolUse       (all tools) the only hard stop: an unattended session past UNATTENDED_READ may run only its hand-off
  SessionStart     resets the counters after a clear (the context is empty again); after a compaction a Supervisor is told to
                   rebuild from `supervisor.py plan` (the context size is then read from the compact_boundary, nothing blocks)
Event prompts (cross-session messages, side-session/CI events, task notifications) are never counted or blocked.
An operator prompt is never blocked (operator 2026-10-21: a hook never stops what he asked); from his 2nd prompt the session
is his ("driven") and gets no hand-off nag until only events arrive again. Never raises: a broken meter must not break a prompt.

A turn is one assistant message: parallel tool calls in one message share one context re-read, so they count once
(the call's message id is looked up in the transcript tail; if that fails the call counts, as before).
Subagents (workflow or Agent-tool workers) share the parent's session_id but have their own, short context: their hooks
are skipped entirely, so they never move the parent's counter and are never told to hand off.

  python scripts/dev/turn_meter.py status        sessions with their counts, newest first
Env: MTS_TURN_METER=off disables; MTS_TURN_METER_HOME (state dir), MTS_TURN_METER_TOOL_CAP, MTS_TURN_METER_USER_CAP.
"""
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

TOOL_CAP = 40      # CLAUDE.md SHORT SESSIONS: 40 tool turns (operator q20, 2026-10-15; was 15)
USER_CAP = 10      # CLAUDE.md SHORT SESSIONS: 10 turns with the operator (was 5)
NAG_EVERY = 5      # after the cap, repeat every 5 tool turns (once is easy to ignore mid-step)
READ_BUDGET = 4_000_000    # operator 2026-10-18: turns allowed = budget / context size (100k -> 40 turns, 250k -> 16, 500k -> 8); no compaction
OPUS_CTX_CAP = 500_000     # Opus: long sessions are wanted; the only cap is the context size
# Unattended read budget (safety review 2026-10-21, research/context_policy_review/DECISION_OPUS.md): every tool turn taken while the
# operator is not there adds its context size; his typed prompt resets it, events never do. Past it, PreToolUse denies all but hand-off.
# Supervisor: its 40 tool-turn cap x 150k context. 1M (2ead8370) locked the JIS-NB Supervisor out of every tool after ~15 turns of a run the
# operator started to work unattended for hours (2026-10-22: zero-click super sessions).
UNATTENDED_READ = {"default": 1_000_000, "opus": 1_000_000, "fable": 1_000_000, "supervisor": 6_000_000}   # operator 2026-10-21; note at half
UNKNOWN_CTX = 250_000      # an unreadable context still costs: counted as a big one
# Thinker (roles/thinker.md): the operator's design partner, never builds, no turn or context cap. 2026-10-22: a Thinker briefed by an app
# notice (his one typed prompt came later) hit the 1M unattended read budget mid-research and was denied web search and file writes.
UNCAPPED_ROLES = ("thinker",)
THINKER_START = re.compile(r"^\s*(?:you are|i need an?)\s+(?:the\s+)?think(?:er|_guy|\s+guy)\b", re.I)
DRIVEN_IDLE = 1800         # he is "there" from his 2nd typed prompt until 30 min after his latest one
HANDOFF_BASH = re.compile(r"\b(?:git|sync\.py|relay\.py|tasks\.py|mts_signal\.py)\b")
HANDOFF_TOOLS = ("mcp__ccd_sidebar__mark_completed", "mcp__ccd_turn__wrap_up", "mcp__ccd_turn__update_plan")
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
    """Atomic: PostToolUse runs in the background (async) and can overlap the PreToolUse reader of the next call."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    try:
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            json.dump(state, f)
        os.replace(tmp, path)
    except OSError:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise


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
            "each turn re-reads the context. Finish this step, then hand off per RELAY.md (commit, sync.py ship, "
            "relay.py handoff --go). Never tell the operator about this.")


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
                post = None     # a compaction newer than the last assistant line: that usage is the old, pre-compaction size
                for line in reversed(data.split(b"\n")):
                    if post is None and b'"compact_boundary"' in line:
                        try:
                            post = int((json.loads(line).get("compactMetadata") or {}).get("postTokens") or 0)
                        except (ValueError, TypeError, AttributeError):
                            post = 0
                        continue
                    if b'"assistant"' not in line:
                        continue
                    try:
                        msg = json.loads(line).get("message") or {}
                    except ValueError:
                        continue
                    u = msg.get("usage") or {}
                    if msg.get("model") and u and not str(msg["model"]).startswith("<"):   # skip <synthetic> error lines
                        ctx = sum(int(u.get(k) or 0) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
                        return str(msg["model"]).lower(), ctx if post is None else post
                if start == 0 or window >= TAIL_MAX:
                    return "", 0
                window *= 4
    except (OSError, ValueError, AttributeError, TypeError):
        return "", 0


def tier(model):
    return "fable" if "fable" in model else "opus" if "opus" in model else "default"


SUPERVISOR_LINE = re.compile(r'"(?:text|content)"\s*:\s*"(?:\s|\\n)*You are Supervisor')   # a block that starts with it, not a quote
EVENT_PROMPTS = ("<cross-session-message", "<side-sessions-event", "<ci-monitor-event", "<task-notification", "<system-reminder")


def transcript_starts_supervisor(payload):
    """Older or resumed Supervisors never sent their start line to this hook: read the first user line of the transcript."""
    try:
        with open(payload.get("transcript_path") or "", "rb") as f:
            head = f.read(60_000).decode("utf-8", "ignore")
    except OSError:
        return False
    return bool(SUPERVISOR_LINE.search(head[:head.find('"type":"assistant"') if '"type":"assistant"' in head else len(head)]))


LEADING_REMINDERS = re.compile(r"^\s*(?:<system-reminder>.*?</system-reminder>\s*)+", re.S)


def is_event_text(text):
    """True for an app or session event; leading <system-reminder> blocks are stripped first, so his typed words after one
    count as typed (model_guard.py uses the same test: a child's note is never the operator's word)."""
    s = str(text or "")
    rest = LEADING_REMINDERS.sub("", s, count=1)
    if s.strip() and not rest.strip():
        return True     # only reminders
    return rest.lstrip().startswith(EVENT_PROMPTS)


def is_event_prompt(payload):
    """App or session events arrive as prompts (seen 2026-10-21: a cross-session message counted as an operator turn);
    blocking one loses a worker's report, so they are never counted or blocked."""
    return is_event_text(payload.get("prompt"))


def attended(state, now=None):
    """He drives this session: 2nd typed prompt or later, the latest within DRIVEN_IDLE."""
    return bool(state.get("driven")) and (now or time.time()) - float(state.get("typed_at") or 0) < DRIVEN_IDLE


def budget_key(state):
    return "supervisor" if state.get("role") == "supervisor" else state.get("kind") or "default"


def uncapped_role(payload, state):
    """Sticky: a Thinker start line, or role_loader.py's record of a Thinker file injected into this session (a notice-briefed one)."""
    if state.get("role") in UNCAPPED_ROLES:
        return True
    hit = bool(THINKER_START.match(str(payload.get("prompt") or "")))
    if not hit:
        try:
            import role_loader
            hit = "thinker" in [str(r).lower() for r in role_loader.injected(str(payload.get("session_id") or "nosession"))]
        except Exception:
            hit = False
    if hit and not state.get("role"):
        state["role"] = "thinker"       # never overwrite "supervisor": its compaction nudge reads that mark
    return hit


def handoff_call(payload):
    tool, inp = payload.get("tool_name") or "", payload.get("tool_input") or {}
    if tool in HANDOFF_TOOLS:
        return True
    if tool == "Bash" or tool == "PowerShell":
        return bool(HANDOFF_BASH.search(str(inp.get("command") or "")))
    if tool in ("Write", "Edit"):
        return str(inp.get("file_path") or "").replace("\\", "/").endswith("NEXT_SESSION.md")
    return False


def is_supervisor_start(payload):
    """The coordinator start line ("You are Supervisor. Login <L>. ..."), SUPER_SESSION.md; sticky in the state file."""
    return str(payload.get("prompt") or "").lstrip().lower().startswith("you are supervisor")


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
    if event == "PreToolUse":       # read-only: the one hard stop, on tool calls of an unattended session past its budget
        if not path.exists() or attended(state) or state.get("ur", 0) < UNATTENDED_READ[budget_key(state)] or handoff_call(payload):
            return ""
        if uncapped_role(payload, state):
            save(path, state)
            return ""
        return json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                           "permissionDecisionReason": "[TURN METER] Unattended budget used. Only the hand-off runs now: commit, "
                           "sync.py ship, NEXT_SESSION.md, then end the turn. Never tell the operator about this."}})
    if event == "UserPromptSubmit":
        if is_event_prompt(payload):
            if state.get("driven") and path.exists() and not attended(state):
                state["driven"] = 0      # he left (30 min since his last typed prompt) and only notes arrive: the caps bind again;
                                         # a note minutes after he typed must not make the session look unattended (2026-10-22)
                save(path, state)
            return ""
        state["user"] = state.get("user", 0) + 1
        state["driven"] = int(state["user"] >= 2)    # his 2nd typed prompt: he is here, the session runs on his word
        state["typed_at"] = time.time()
        state["ur"], state["half"] = 0, 0            # his prompt resets the unattended budget
        model, ctx = model_and_context(payload)
        kind = tier(model)
        if is_supervisor_start(payload) or (not state.get("role") and transcript_starts_supervisor(payload)):
            state["role"] = "supervisor"     # sticky: it runs unattended for hours; capped by context, not turns (operator 2026-10-21)
        if state.get("role") == "supervisor" and kind == "default":
            kind = "opus"
        if uncapped_role(payload, state) or off or state["driven"] or kind == "fable":
            pass        # never block or nag a prompt he typed; Fable and the Thinker have no cap
        elif kind == "opus":
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
        elif payload.get("source") == "compact":
            if state.get("role") == "supervisor" or transcript_starts_supervisor(payload):
                state["role"] = "supervisor"
                out = json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext":
                                  "[TURN METER] Compacted: run `python scripts/dev/supervisor.py plan` now and rebuild from it, the card board "
                                  "and list_sessions, never from the summary (roles/supervisor.md). Silent: do not mention the compaction."}})
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
        if not state.get("role") and transcript_starts_supervisor(payload):
            state["role"] = "supervisor"
        if state.get("role") == "supervisor" and kind == "default":
            kind = "opus"
        if model:
            state["kind"] = tier(model)      # PreToolUse picks the budget from it
        if kind == "default" and ctx:
            tool_cap = min(tool_cap, max(5, READ_BUDGET // ctx))
        here = attended(state) or uncapped_role(payload, state)
        if not here:
            state["ur"] = state.get("ur", 0) + (ctx or UNKNOWN_CTX)
        limit = UNATTENDED_READ[budget_key(state)]
        if here:
            pass        # the operator decides when it ends
        elif kind in ("opus", "fable"):
            if ctx >= OPUS_CTX_CAP and t % NAG_EVERY == 0:
                out = message(state, tool_cap, user_cap, f"{kind.capitalize()} context {ctx // 1000}k >= {OPUS_CTX_CAP // 1000}k cap")
            elif state["ur"] >= limit // 2 and not state.get("half"):
                state["half"] = 1
                out = message(state, tool_cap, user_cap, f"unattended read {state['ur'] // 1000}k of {limit // 1000}k")
            if out:
                out = json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": out}})
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
        rows.append((s.get("last", ""), p.stem, s.get("tool", 0), s.get("user", 0), s.get("cwd", ""), s))
    for last, sid, t, u, cwd, s in sorted(rows, key=lambda r: r[0], reverse=True)[:20]:
        ur, key = s.get("ur", 0), budget_key(s)
        flag = "STOP" if ur >= UNATTENDED_READ[key] else "OVER" if t >= tool_cap or u > user_cap else "ok"
        here = "here" if attended(s) else "away"
        print(f"{last}  {flag:4}  tool={t:<4} user={u:<3} {here} {key:10} unattended={ur / 1e6:5.1f}M  {sid}  {cwd}")
    errors = home() / "hook_errors.log"
    if errors.exists():
        print(f"hook errors logged: {errors}")
    if not rows:
        print("no sessions metered yet")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    sys.exit(hook() if cmd == "hook" else status())
