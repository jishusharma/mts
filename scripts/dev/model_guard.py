"""Model guard: no session or subagent gets started on Opus/Fable by accident (CLAUDE.md "Cost and routing", operator 2026-10-15).

Seen 2026-10-15: an Opus session proposed a side session without `model`; it inherited Opus. The rule "Sonnet, Opus only
when the operator names it" was prose, so nothing stopped it. This hook makes it a hard block.

Claude Code PreToolUse hook (project .claude/settings.json), on the calls that start or re-price a model:
  Agent / Task                          `model` must be given and be sonnet or haiku; a fork (inherits) only from a cheap session
  mcp__ccd_session__start_session       same; `proposal_id` alone (starting a proposal already checked) and cloud starts pass
  mcp__ccd_session_mgmt__set_session_model   only sonnet or haiku
No click cards (operator 2026-10-18: "I am not sitting in front of the screen"): start_session with initiation "offer" or "own_initiative"
(or none) is denied for every model, Opus included, because the operator must click to start it and may be away. Use initiation
"user_asked" (starts now) on his typed turns; on a turn a message or event started even user_asked shows an Allow card
(2026-10-23), so it is denied there: use the Agent tool with model='sonnet'. MTS_ALLOW_CARDS=1 allows.
Spawn storms (review 2026-10-21, DECISION_OPUS.md): while the operator is away (turn_meter.attended), at most 4 start_session
and 8 Agent/Task calls per hour, and no Workflow. Scheduling tools (ScheduleWakeup, CronCreate, RemoteTrigger, create_scheduled_task)
are denied unless his latest typed message asks for it (SCHEDULING_POLICY.md: none exist). Anything else passes. A blocked call gets a deny with the fix in the reason, so the model retries with model=sonnet.
Opus is allowed in two cases only (operator 2026-10-17: "whenever I say use Opus, it must be done" and "only critical tasks, a little
tighter"): (1) the operator's LATEST typed message names it ("opus"/"fable"); (2) the brief cites a task card that is lane OPUS,
`approved_by` set and `crucial` filled (tasks.py lint enforces the pair). Everything else is denied, and a call without `model` is
always denied, so an inherited model can never slip in. MTS_ALLOW_OPUS=1 allows all.

  python scripts/dev/model_guard.py check '<tool_input json>' <tool_name> [parent_model]   prints the decision (debug)
"""
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import turn_meter  # noqa: E402  one event test for both hooks: a child's note is never the operator's word

CHEAP = ("sonnet", "haiku")
FIX = "Pass model='claude-sonnet-5-5' (Agent tool: model='sonnet'), or 'haiku' for mechanical work."
AGENT_TOOLS = ("Agent", "Task")
START = "mcp__ccd_session__start_session"
SET_MODEL = "mcp__ccd_session_mgmt__set_session_model"
SEND_TOOLS = ("SendMessage", "mcp__ccd_session_mgmt__send_message")
WORKFLOW = "Workflow"
SCHEDULE_TOOLS = ("ScheduleWakeup", "CronCreate", "RemoteTrigger", "mcp__scheduled-tasks__create_scheduled_task")
SCHEDULE_WORDS = ("loop", "schedul", "remind", "cron", "wake")
ASK = "AskUserQuestion"
WRAP_UP = "mcp__ccd_turn__wrap_up"
BRANCH_CARD = "mcp__ccd_directory__propose_branch"
BUTTON_TOOLS = (ASK, WRAP_UP, BRANCH_CARD)
HOURLY = {START: 4, "Agent": 8, "Task": 8}
REMINDER_BLOCK = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)
SESSION_ID_RE = re.compile(r'session_id["\s:=]+([A-Za-z0-9_.-]+)')


def cheap(model):
    m = str(model or "").lower()
    return any(c in m for c in CHEAP)


def parent_model(transcript_path):
    """The model of the session's latest assistant message (transcript tail), or None."""
    try:
        with open(transcript_path, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - (1 << 20)))
            lines = f.read().decode("utf-8", "replace").splitlines()
    except (OSError, TypeError, ValueError):
        return None
    for line in reversed(lines):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        m = d.get("type") == "assistant" and (d.get("message") or {}).get("model")
        if m and m != "<synthetic>":
            return m
        att = d.get("attachment") or {}
        if att.get("type") == "model" and (att.get("identity") or {}).get("modelId"):
            return att["identity"]["modelId"]
    return None


def claude_home():
    return Path(os.environ.get("MTS_CLAUDE_HOME") or Path.home() / ".claude")


def started_session_ids(transcript_path):
    """Session ids returned by start_session tool_result blocks in this session's transcript, or None if unreadable."""
    if not transcript_path:
        return None
    try:
        with open(transcript_path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except (OSError, TypeError, ValueError):
        return None
    start_tu = set()
    for line in lines:
        if START not in line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        for b in ((d.get("message") or {}).get("content") if isinstance((d.get("message") or {}).get("content"), list) else []):
            if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == START and b.get("id"):
                start_tu.add(b["id"])
    sids = set()
    for line in lines:
        if "session_id" not in line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        for b in ((d.get("message") or {}).get("content") if isinstance((d.get("message") or {}).get("content"), list) else []):
            if isinstance(b, dict) and b.get("type") == "tool_result":
                tuid = b.get("tool_use_id")
                if start_tu and tuid and tuid not in start_tu:
                    continue
                blob = json.dumps(b.get("content"))
                for m in SESSION_ID_RE.finditer(blob):
                    sids.add(m.group(1))
    return sids


def resolve_target_transcript(target_id, parent_transcript_path=None):
    """Find the JSONL transcript Path for target_id, or None."""
    if not target_id:
        return None
    p = Path(target_id)
    if p.suffix == ".jsonl" and p.is_file():
        return p
    ch = claude_home()
    candidates = [target_id]
    if target_id.startswith("local_"):
        candidates.append(target_id[6:])
    sess_dir = ch / "sessions"
    if sess_dir.is_dir():
        for sf in sess_dir.glob("*.json"):
            try:
                sd = json.loads(sf.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if sd.get("hostSessionId") == target_id or sd.get("sessionId") == target_id:
                if sd.get("transcriptPath") or sd.get("transcript_path"):
                    tp = Path(sd.get("transcriptPath") or sd.get("transcript_path"))
                    if tp.is_file():
                        return tp
                if sd.get("sessionId") and sd["sessionId"] not in candidates:
                    candidates.insert(0, sd["sessionId"])
    search_dirs = []
    if parent_transcript_path:
        pt = Path(parent_transcript_path)
        if pt.parent.is_dir():
            search_dirs.append(pt.parent)
            if pt.parent.parent.is_dir():
                for d in sorted(pt.parent.parent.iterdir()):
                    if d.is_dir() and d not in search_dirs:
                        search_dirs.append(d)
    proj_root = ch / "projects"
    if proj_root.is_dir():
        for d in sorted(proj_root.iterdir()):
            if d.is_dir() and d not in search_dirs:
                search_dirs.append(d)
    for cid in candidates:
        for d in search_dirs:
            cand = d / f"{cid}.jsonl"
            if cand.is_file():
                return cand
    return None


def message_reason(tool, inp, transcript_path):
    """Deny reason for SendMessage / mcp__ccd_session_mgmt__send_message (SV8), else None."""
    if tool not in SEND_TOOLS:
        return None
    inp = inp or {}
    target = str(inp.get("to") or inp.get("session_id") or inp.get("recipient") or "").strip()
    if not target:
        return "SendMessage without a target session id (`to` / `session_id`) is denied (fail closed)."
    owned = started_session_ids(transcript_path)
    if owned is None:
        return f"Cannot read this session's transcript to verify ownership of {target!r} (fail closed)."
    if target not in owned and f"local_{target}" not in owned and (not target.startswith("local_") or target[6:] not in owned):
        return f"Target session {target!r} was not started by this session (not in start_session results); message only own workers."
    target_t = resolve_target_transcript(target, transcript_path)
    if not target_t:
        return f"Target session {target!r} transcript cannot be resolved on disk (fail closed)."
    t_model = parent_model(target_t)
    if not t_model:
        return f"Target session {target!r} model cannot be resolved from {target_t.name} (fail closed)."
    if "fable" in t_model.lower():
        return f"Target session {target!r} runs on Fable ({t_model}); never message a Fable session."
    return None


NAMED = ("opus", "fable")
SKIP_PREFIX = ("<local-command", "[SIGNALS")     # events (cross-session, CI, side-session, reminders) via turn_meter.is_event_text


TASKS = os.environ.get("MTS_TASKS_DIR") or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                                         "MyTradingSys", "system", "tasks")


def crucial_card_cited(*texts):
    """True when a brief cites a task card (its id, a file in system/tasks) that is lane OPUS, operator-approved and has a `crucial` reason.
    A session may start Opus on its own only for such a card; the card gate is `tasks.py` lint (WORKERS.md rule 6)."""
    blob = " ".join(str(t or "") for t in texts)
    try:
        names = [n[:-5] for n in os.listdir(TASKS) if n.endswith(".json")]
    except OSError:
        return False
    for cid in names:
        if cid in blob:
            try:
                with open(os.path.join(TASKS, cid + ".json"), encoding="utf-8") as f:
                    c = json.load(f)
            except (OSError, ValueError):
                continue
            if c.get("lane") == "OPUS" and c.get("approved_by") and str(c.get("crucial", "")).strip() and c.get("state") not in ("done", "dropped"):
                return True
    return False


def typed_texts(transcript_path):
    """The operator's typed messages, newest first, with reminder blocks cut out; events and command echoes skipped."""
    try:
        with open(transcript_path, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - (1 << 20)))
            lines = f.read().decode("utf-8", "replace").splitlines()
    except (OSError, TypeError, ValueError):
        return False
    for line in reversed(lines):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") != "user" or d.get("isMeta"):
            continue
        c = (d.get("message") or {}).get("content")
        parts = [c] if isinstance(c, str) else [b.get("text", "") for b in (c or []) if isinstance(b, dict) and b.get("type") == "text"]
        parts = [t for t in parts if t and not t.lstrip().startswith(SKIP_PREFIX)]
        if not parts or turn_meter.is_event_text("".join(parts)):
            continue
        text = REMINDER_BLOCK.sub("", " ".join(parts))
        if text.strip():
            yield text.lower()


def operator_said(transcript_path, words):
    """True when the operator's latest typed message contains one of the words."""
    for text in typed_texts(transcript_path):
        return any(w in text for w in words)
    return False


def operator_named_opus(transcript_path, last=1):
    """True when the operator's latest typed message in the transcript tail mentions opus/fable."""
    return operator_said(transcript_path, NAMED)


def away(ev):
    """True unless the operator drives this session now (turn_meter state)."""
    sid = ev.get("session_id")
    if not sid:
        return True
    return not turn_meter.attended(turn_meter.load(turn_meter.home() / f"{turn_meter.safe_id(sid)}.json"))


def calls_last_hour(transcript_path, names, skip_id=None):
    """tool_use blocks named `names` with a transcript timestamp in the last hour, the current call excluded."""
    try:
        with open(transcript_path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except (OSError, TypeError, ValueError):
        return 0
    cutoff, n = datetime.now(timezone.utc).timestamp() - 3600, 0
    for line in lines:
        if '"tool_use"' not in line or not any(nm in line for nm in names):
            continue
        try:
            d = json.loads(line)
            ts = datetime.fromisoformat(str(d.get("timestamp")).replace("Z", "+00:00")).timestamp()
        except (ValueError, TypeError):
            continue
        if ts < cutoff:
            continue
        for b in (d.get("message") or {}).get("content") or []:
            if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") in names and b.get("id") != skip_id:
                n += 1
    return n


def storm_reason(tool, ev):
    """Deny reason for a scheduling tool he did not ask for, or a spawn past the hourly cap while he is away, else None."""
    tp = ev.get("transcript_path")
    if tool in SCHEDULE_TOOLS:
        return None if operator_said(tp, SCHEDULE_WORDS) else (
            f"{tool}: no schedulers or wake-ups (SCHEDULING_POLICY.md) unless the operator's latest message asks for one.")
    if tool not in HOURLY and tool != WORKFLOW or not away(ev):
        return None
    if tool == WORKFLOW:
        return "Workflow needs the operator's opt-in while he is here; do the work with one Sonnet session or agent."
    names = (START,) if tool == START else ("Agent", "Task")
    if calls_last_hour(tp, names, ev.get("tool_use_id")) >= HOURLY[tool]:
        return (f"{tool}: {HOURLY[tool]} per hour while the operator is away (spawn cap). Finish with the workers you have, "
                "or hand off. Never tell the operator about this.")
    return None


CARD_FIX = ("No click cards: the operator is away. Use initiation='user_asked' (starts at once), or the Agent tool with model='sonnet' "
            "when the app refuses user_asked on an event turn; note the work in your log instead of offering it.")


EVENT_TURN_FIX = ("start_session on a turn that a message or event started shows the operator an Allow card even with "
                  "initiation='user_asked' (seen 2026-10-23: 'CBP module plan 2.0 status' waited on it while he was away). Use the Agent "
                  "tool with model='sonnet' (run_in_background, isolation worktree) now, or leave the start brief for his next typed turn.")


def event_turn(transcript_path):
    """True when the newest prompt in the transcript (tool results skipped) is an app or session event, not his typed words."""
    try:
        with open(transcript_path, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - (1 << 20)))
            lines = f.read().decode("utf-8", "replace").splitlines()
    except (OSError, TypeError, ValueError):
        return False
    for line in reversed(lines):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") != "user" or d.get("isMeta"):
            continue
        c = (d.get("message") or {}).get("content")
        parts = [c] if isinstance(c, str) else [b.get("text", "") for b in (c or []) if isinstance(b, dict) and b.get("type") == "text"]
        parts = [t for t in parts if t and not t.lstrip().startswith(SKIP_PREFIX)]
        if parts:
            return turn_meter.is_event_text("".join(parts))
    return False


def card_reason(tool, inp, transcript_path=None):
    """Deny reason when start_session would show the operator a card to click, else None."""
    if tool != START or os.environ.get("MTS_ALLOW_CARDS") == "1":
        return None
    inp = inp or {}
    if inp.get("proposal_id"):
        return None
    if inp.get("initiation") == "user_asked":
        return EVENT_TURN_FIX if event_turn(transcript_path) else None
    return f"start_session with initiation={inp.get('initiation')!r} waits for an operator click. " + CARD_FIX


def decide(tool, inp, parent):
    """None = allow, else the deny reason."""
    if card_reason(tool, inp):
        return card_reason(tool, inp)
    if os.environ.get("MTS_ALLOW_OPUS") == "1":
        return None
    inp = inp or {}
    model = inp.get("model")
    if tool in AGENT_TOOLS:
        if inp.get("subagent_type") == "fork":
            return None if cheap(parent) else f"A fork inherits this session's model ({parent or 'unknown'}). Use a named subagent_type with a cheap model. {FIX}"
        if not model:
            return f"Agent call without `model` inherits the parent or agent default (may be Opus). {FIX}"
        return None if cheap(model) else f"Model '{model}' is not allowed for subagents (Opus only when the operator names it; the operator picks it in the app). {FIX}"
    if tool == START:
        if inp.get("proposal_id") and not inp.get("prompt"):
            return None
        if inp.get("target") == "cloud":
            return None
        if inp.get("context") == "fork":
            return None if cheap(parent) else f"A fork inherits this session's model ({parent or 'unknown'}); `model` is ignored. Use context='fresh' with a background. {FIX}"
        if not model:
            return f"start_session without `model` inherits this session's model (may be Opus). {FIX}"
        return None if cheap(model) else f"Model '{model}' is not allowed for new sessions (Opus only when the operator names it; the operator picks it in the app). {FIX}"
    if tool == SET_MODEL:
        return None if cheap(model) else f"Switching a session to '{model}' is not allowed (Opus only by the operator, in the app's model menu)."
    return None


def first_prompt(transcript_path):
    """The session's first user message as text, system reminders removed, or '' if unreadable."""
    try:
        with open(transcript_path, encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                c = (d.get("message") or {}).get("content") if d.get("type") == "user" else None
                if isinstance(c, list):
                    c = " ".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
                if isinstance(c, str) and c.strip():
                    return REMINDER_BLOCK.sub("", c).strip()
    except (OSError, TypeError, ValueError):
        pass
    return ""


def nested_reason(tool, inp, transcript_path):
    """E2E run 2026-10-22: a Supervisor that a session had started called start_session for its Builders; the app stopped each call
    for an operator approval and the run sat waiting. A session started by another session starts its workers as background Agents.
    Operator 2026-10-22: the operator-started login B Supervisor on the NUC got the same "Allow Claude to start the session" card
    (user_asked, Sonnet). Any role session starts its workers as background Agents."""
    if tool != START or (inp or {}).get("target") == "cloud" or os.environ.get("MTS_ALLOW_NESTED") == "1":
        return None
    import role_loader
    if not (role_loader.from_session(first_prompt(transcript_path)) or role_session(transcript_path)):
        return None
    if interactive_role((inp or {}).get("prompt")):    # operator 2026-10-23: interactive roles are sessions, never background Agents
        return None
    return ("a start_session from a role session waits for an operator approval in the app (the operator is away). Start the worker "
            "with the Agent tool instead: model='sonnet', run_in_background=true, the same brief (its first line `You are <Role>.`).")


INTERACTIVE_ROLES = ("Eagle_Eyes",)   # roles that read the operator's screenshots/chat (only eagle_eyes.md says so); aliases come from role_loader
AGENT_INTERACTIVE_FIX = "interactive roles start as sessions (start_session user_asked), never background Agents."


def interactive_role(prompt):
    """The interactive role named by the first `You are <Role>.` line of a start/Agent prompt (aliases included), else None."""
    import role_loader
    names = {n.lower(): n for n in INTERACTIVE_ROLES}
    names.update({a: n for n, al in role_loader.ALIASES.items() if n in INTERACTIVE_ROLES for a in al})
    m = ROLE_LINE.search(str(prompt or "")[:3000])
    return names.get(m.group(1).lower()) if m else None


def agent_role_reason(tool, inp):
    if tool in AGENT_TOOLS and interactive_role((inp or {}).get("prompt")):
        return AGENT_INTERACTIVE_FIX
    return None


def role_session(transcript_path):
    """The role the session's first prompt names explicitly (role_loader.explicit_role: the one shared definition; a role the
    loader would only pick from task words is not a role session), else None."""
    import role_loader
    return role_loader.explicit_role(first_prompt(transcript_path))


def button_reason(tool, inp, transcript_path):
    """Operator 2026-10-22, login A Supervisor on the laptop showing buttons: "displaying me buttons to click!!!". A role session never
    puts a card in front of the operator: no question card, no wrap_up question/buttons, no branch card. It decides and writes it down."""
    if tool not in BUTTON_TOOLS or os.environ.get("MTS_ALLOW_CARDS") == "1":
        return None
    if tool == WRAP_UP and not ((inp or {}).get("ask") or (inp or {}).get("actions")):
        return None
    role = role_session(transcript_path)
    if not role:
        return None
    fix = {ASK: "Do not ask: pick the option your role file and the card point to, do it, and note the choice in your log or hand-over.",
           WRAP_UP: "Call wrap_up again with `recap` only (no `ask`, no `actions`); decide the next step yourself and do it.",
           BRANCH_CARD: "Do not propose a branch: work where you are (a role session ships through `sync.py ship`)."}[tool]
    return f"{role} is a role session; the operator is away and wants zero clicks, so {tool} cards are blocked. {fix}"


def hook():
    try:
        ev = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return 0
    tool = ev.get("tool_name") or ""
    if tool not in AGENT_TOOLS + (START, SET_MODEL, WORKFLOW) + SEND_TOOLS + SCHEDULE_TOOLS + BUTTON_TOOLS:
        return 0
    inp = ev.get("tool_input") or {}
    if tool in BUTTON_TOOLS:
        button = button_reason(tool, inp, ev.get("transcript_path"))
        if button:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                     "permissionDecisionReason": "model_guard: " + button}}))
        return 0
    storm = storm_reason(tool, ev)
    if storm:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                 "permissionDecisionReason": "model_guard: " + storm}}))
        return 0
    if tool in SCHEDULE_TOOLS or tool == WORKFLOW:
        return 0
    msg = message_reason(tool, inp, ev.get("transcript_path"))
    if msg:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                 "permissionDecisionReason": "model_guard: " + msg}}))
        return 0
    if tool in SEND_TOOLS:
        return 0
    card = agent_role_reason(tool, inp) or card_reason(tool, inp, ev.get("transcript_path")) or nested_reason(tool, inp, ev.get("transcript_path"))
    if card:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                 "permissionDecisionReason": "model_guard: " + card}}))
        return 0
    if inp.get("model") and (operator_named_opus(ev.get("transcript_path"))
                             or crucial_card_cited(inp.get("title"), inp.get("prompt"), inp.get("background"), inp.get("description"))):
        return 0
    needs_parent = inp.get("subagent_type") == "fork" or inp.get("context") == "fork"
    reason = decide(tool, inp, parent_model(ev.get("transcript_path")) if needs_parent else None)
    if reason:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                 "permissionDecisionReason": "model_guard: " + reason}}))
    return 0


def main(argv):
    if argv[:1] == ["hook"]:
        return hook()
    if argv[:1] == ["check"] and len(argv) >= 3:
        print(decide(argv[2], json.loads(argv[1]), argv[3] if len(argv) > 3 else None) or "allow")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
