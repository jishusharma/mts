"""Model guard: no session or subagent gets started on Opus/Fable by accident (CLAUDE.md "Cost and routing", operator 2026-10-15).

Seen 2026-10-15: an Opus session proposed a side session without `model`; it inherited Opus. The rule "Sonnet, Opus only
when the operator names it" was prose, so nothing stopped it. This hook makes it a hard block.

Claude Code PreToolUse hook (project .claude/settings.json), on the calls that start or re-price a model:
  Agent / Task                          `model` must be given and be sonnet or haiku; a fork (inherits) only from a cheap session
  mcp__ccd_session__start_session       same; `proposal_id` alone (starting a proposal already checked) and cloud starts pass
  mcp__ccd_session_mgmt__set_session_model   only sonnet or haiku
Anything else passes. A blocked call gets a deny with the fix in the reason, so the model retries with model=sonnet.
Opus is allowed in two cases only (operator 2026-10-17: "whenever I say use Opus, it must be done" and "only critical tasks, a little
tighter"): (1) the operator's LATEST typed message names it ("opus"/"fable"); (2) the brief cites a task card that is lane OPUS,
`approved_by` set and `crucial` filled (tasks.py lint enforces the pair). Everything else is denied, and a call without `model` is
always denied, so an inherited model can never slip in. MTS_ALLOW_OPUS=1 allows all.

  python scripts/dev/model_guard.py check '<tool_input json>' <tool_name> [parent_model]   prints the decision (debug)
"""
import json
import os
import sys

CHEAP = ("sonnet", "haiku")
FIX = "Pass model='claude-sonnet-5-5' (Agent tool: model='sonnet'), or 'haiku' for mechanical work."
AGENT_TOOLS = ("Agent", "Task")
START = "mcp__ccd_session__start_session"
SET_MODEL = "mcp__ccd_session_mgmt__set_session_model"


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
    return None


NAMED = ("opus", "fable")
SKIP_PREFIX = ("<system-reminder>", "<local-command", "<command-name>", "[SIGNALS", "<task-notification", "<side-sessions-event")


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


def operator_named_opus(transcript_path, last=1):
    """True when the operator's latest typed message in the transcript tail mentions opus/fable."""
    try:
        with open(transcript_path, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - (1 << 20)))
            lines = f.read().decode("utf-8", "replace").splitlines()
    except (OSError, TypeError, ValueError):
        return False
    seen = 0
    for line in reversed(lines):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") != "user" or d.get("isMeta"):
            continue
        c = (d.get("message") or {}).get("content")
        parts = [c] if isinstance(c, str) else [b.get("text", "") for b in (c or []) if isinstance(b, dict) and b.get("type") == "text"]
        text = " ".join(t for t in parts if t and not t.lstrip().startswith(SKIP_PREFIX))
        if not text.strip():
            continue
        if any(n in text.lower() for n in NAMED):
            return True
        seen += 1
        if seen >= last:
            return False
    return False


def decide(tool, inp, parent):
    """None = allow, else the deny reason."""
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
        if "opus" in str(model).lower() and inp.get("initiation") == "user_asked":
            return None  # operator 2026-10-18: Opus passes when the operator asked in words (explicit model, user_asked only)
        return None if cheap(model) else f"Model '{model}' is not allowed for new sessions (Opus only when the operator names it; the operator picks it in the app). {FIX}"
    if tool == SET_MODEL:
        return None if cheap(model) else f"Switching a session to '{model}' is not allowed (Opus only by the operator, in the app's model menu)."
    return None


def hook():
    try:
        ev = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return 0
    tool = ev.get("tool_name") or ""
    if tool not in AGENT_TOOLS + (START, SET_MODEL):
        return 0
    inp = ev.get("tool_input") or {}
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
