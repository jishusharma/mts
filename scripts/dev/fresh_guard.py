"""Fresh guard: a reply that states repo/rule/state facts must follow a read of the source in the same turn.

Why (operator 2026-10-22): "If you are just adding an instruction that doesn't work, then it is not a fix."
Sessions answered questions about rules, hooks, models, roles, budget, CI, branches, cards, deploy/live state from memory or
stale context. The instruction "RULES ANSWERS: read the source this turn, cite file:line" (role_loader.py) was ignored, so
this makes it a check.

What: Claude Code Stop hook. When the last reply is longer than 200 chars, reads like it states repo/system facts (a file
name, a backticked identifier, words such as hook/branch/budget/deployed) and the current turn (everything after the
operator's last typed message) made no disk read (Read, Grep, Glob, Bash, PowerShell, WebFetch, WebSearch, Agent, Task,
session lookups), the stop is blocked ONCE with the instruction to read the source and cite file:line. A second stop in the
same turn (stop_hook_active) and every subagent (agent_id) are allowed.
This is a quality check, not a safety gate: any unreadable transcript, bad input or error allows the stop (fails open).

Disable: env MTS_FRESH_GUARD=0.
  python scripts/dev/fresh_guard.py hook                          Stop hook, JSON on stdin, prints a block decision or nothing
  python scripts/dev/fresh_guard.py check <transcript> "<message>"  prints the decision (debug)
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model_guard  # noqa: E402  typed-message filters shared with the model guard
import turn_meter  # noqa: E402  is_subagent / is_event_text

READ_TOOLS = frozenset(("Read", "Grep", "Glob", "Bash", "PowerShell", "WebFetch", "WebSearch", "Agent", "Task",
                        "mcp__ccd_session_mgmt__get_session", "mcp__ccd_session_mgmt__list_sessions"))
MIN_LEN = 200
CLAIM_RE = re.compile(
    r"\b[\w./-]+\.(?:py|md|json|txt|ps1|vbs)\b"
    r"|\bhooks?\b|model_guard|turn_meter|role_loader|(?-i:WORKERS|SUPER_SESSION)|CLAUDE\.md"
    r"|\btask cards?\b|\bcard (?:status|fields?|ids?)\b|\bci-[0-9a-f]{6,}\b"
    r"|\bbranch(?:es)?\b|\bcommit [0-9a-f]{7,40}\b|\bgit commit\b|\bshipped\b"
    r"|origin/|CI (?:green|red)|\bbudget\b|\bquota\b|\bdeployed\b|live tree|\benforce[sd]?\b",
    re.I)
REASON = ("fresh_guard: this reply states repo/rule/state facts but this turn read nothing from disk. Read the source now "
          "(Read or git show origin/fast-track:<file>), cite file:line, correct anything that differs, or say NOT_IN_DATA.")


def entries(transcript_path):
    """Parsed JSONL entries, or None when the file cannot be read."""
    try:
        with open(transcript_path, encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except (OSError, TypeError, ValueError):
        return None
    out = []
    for line in lines:
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if isinstance(d, dict):
            out.append(d)
    return out


def blocks(d):
    c = (d.get("message") or {}).get("content")
    if isinstance(c, str):
        return [{"type": "text", "text": c}]
    return [b for b in (c or []) if isinstance(b, dict)]


def is_operator_message(d):
    """A genuine operator-typed user entry: not a tool_result, not meta, not an event (turn_meter.is_event_text)."""
    if d.get("type") != "user" or d.get("isMeta"):
        return False
    bs = blocks(d)
    if any(b.get("type") == "tool_result" for b in bs):
        return False
    parts = [b.get("text", "") for b in bs if b.get("type") == "text"]
    parts = [t for t in parts if t and not t.lstrip().startswith(model_guard.SKIP_PREFIX)]
    if not parts or turn_meter.is_event_text("".join(parts)):
        return False
    return bool(model_guard.REMINDER_BLOCK.sub("", " ".join(parts)).strip())


def turn_entries(es):
    """Entries after the last operator-typed message (all of them when there is none)."""
    last = -1
    for i, d in enumerate(es):
        if is_operator_message(d):
            last = i
    return es[last + 1:]


def count_reads(es):
    return sum(1 for d in es if d.get("type") == "assistant"
               for b in blocks(d) if b.get("type") == "tool_use" and b.get("name") in READ_TOOLS)


def last_assistant_text(es):
    for d in reversed(es):
        if d.get("type") == "assistant":
            t = "\n".join(b.get("text", "") for b in blocks(d) if b.get("type") == "text").strip()
            if t:
                return t
    return ""


def decide(transcript_path, message=None):
    """None = allow, else the block reason."""
    if os.environ.get("MTS_FRESH_GUARD") == "0":
        return None
    es = entries(transcript_path)
    if es is None:
        return None
    msg = message if message else last_assistant_text(es)
    if len(msg or "") <= MIN_LEN or not CLAIM_RE.search(msg):
        return None
    return None if count_reads(turn_entries(es)) else REASON


def hook(stdin_text):
    try:
        ev = json.loads(stdin_text or "{}")
        if ev.get("stop_hook_active") or turn_meter.is_subagent(ev):
            return ""
        why = decide(ev.get("transcript_path"), ev.get("last_assistant_message"))
        return json.dumps({"decision": "block", "reason": why}) if why else ""
    except Exception:
        return ""


def main(argv):
    if argv[:1] == ["hook"]:
        out = hook(sys.stdin.read())
        if out:
            print(out)
        return 0
    if argv[:1] == ["check"] and len(argv) >= 3:
        why = decide(argv[1], argv[2])
        print(json.dumps({"decision": "block", "reason": why}) if why else "allow")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
