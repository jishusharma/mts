"""Prereq guard: a session may not end by handing the operator pre-run to-dos that no card carries (operator 2026-10-22).

Operator 2026-10-22: "whatever needs to be done regarding a task before it is run, MTS must know ... There has to be some hook
about this that must be added as a hook and not as a rule." Claude Code Stop hook (.claude/settings.json): reads the session's
last reply from the transcript; when a line tells the operator to do something before a run ("before you start", "needs a
review stamp", "must run on", "paste ... after", "you need to") and the line names no card, block ONCE with the fix:
`tasks.py need <card> "<what>" --lane <LANE> [--host H]` (an agent owns the item; the card waits on it via depends_on), ship,
then name the card in the reply. A line marked `OPERATOR-ONLY:` (money, mainnet, credentials, a physical machine, an operator
decision) is allowed. A second stop in the same turn is always allowed; the same reply is never blocked twice. Never raises.
Env: MTS_PREREQ_GUARD=off disables.
Run by hand: python scripts/dev/prereq_guard.py check <reply.txt>   (prints the flagged lines, exit 1 when any)
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

PATTERNS = re.compile(
    r"\b(before (you|we) (start|run|begin|launch|kick|paste|go)"
    r"|before (it|this|the run|the card|that) (starts|runs|can run|begins)"
    r"|you('ll| will)? (need|have) to"
    r"|you must|you should (first|run|paste|stamp|approve|start|check)"
    r"|(needs?|waits? (on|for)) (a |an |your )?(lab_guy |real )?(review )?(stamp|approval|sign-?off)"
    r"|(must|has to|needs? to|can only) (run|be run) on"
    r"|paste (it|the \w+ prompt|the prompt|this)\b.*\b(after|once|when)"
    r"|remember to|don't forget to|do not forget to)\b", re.I)
CARD = re.compile(r"\b(card|tasks\.py need)\b|`[a-z0-9]+(-[a-z0-9]+){2,}`", re.I)
ALLOWED = "OPERATOR-ONLY:"


def flagged(text):
    """Lines of `text` that hand the operator a pre-run item without a card or an OPERATOR-ONLY mark."""
    out = []
    for line in (text or "").splitlines():
        s = line.strip()
        if not s or s.startswith(("```", "    ")) or ALLOWED in s:
            continue
        if PATTERNS.search(s) and not CARD.search(s):
            out.append(s[:200])
    return out


def last_reply(transcript_path):
    """Text of the assistant messages after the last real user prompt (tool results are not prompts)."""
    texts = []
    try:
        lines = Path(transcript_path).read_text(encoding="utf-8", errors="replace").splitlines()
    except (OSError, TypeError):
        return ""
    for raw in lines:
        try:
            e = json.loads(raw)
        except ValueError:
            continue
        msg = e.get("message") or {}
        content = msg.get("content")
        if e.get("type") == "user":
            if isinstance(content, str) or (isinstance(content, list) and any(
                    isinstance(b, dict) and b.get("type") == "text" for b in content)):
                texts = []
        elif e.get("type") == "assistant" and isinstance(content, list):
            texts += [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
    return "\n".join(texts)


def message(lines):
    shown = "; ".join(f'"{x}"' for x in lines[:4])
    return ("PREREQ GUARD: your reply hands the operator pre-run items no card carries: " + shown + ". MTS must hold them, "
            "not the operator. For each: `python scripts/dev/tasks.py need <card id> \"<what>\" --lane <LANE> [--host <HOST>]` "
            "(an agent owns it; the card waits on it via depends_on; `--host` alone just pins the card to a machine), then "
            "`sync.py ship`, and rewrite the reply to name the card(s) instead of asking the operator. Only what no agent can do "
            "(money, mainnet, credentials, a physical machine, an operator decision) stays, prefixed `OPERATOR-ONLY:` with the reason.")


def seen_before(session_id, key):
    """True when this session was already blocked on this exact reply (no repeat blocks)."""
    if not session_id:
        return False
    f = Path(os.environ.get("MTS_STOP_GUARD_HOME") or Path.home() / ".claude") / "mts-prereq-guard.json"
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        d = {}
    if d.get(session_id) == key:
        return True
    d.pop(session_id, None)
    d[session_id] = key
    d = dict(list(d.items())[-50:])
    try:
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(d), encoding="utf-8", newline=chr(10))
    except OSError:
        pass
    return False


def hook(stdin_text):
    """-> JSON string for Claude Code, or '' to allow the stop."""
    try:
        if os.environ.get("MTS_PREREQ_GUARD", "").lower() == "off":
            return ""
        data = json.loads(stdin_text or "{}")
        if data.get("stop_hook_active"):
            return ""
        text = data.get("last_assistant_message") or last_reply(data.get("transcript_path"))
        lines = flagged(text)
        if not lines:
            return ""
        key = hashlib.sha1(chr(10).join(lines).encode("utf-8")).hexdigest()[:16]
        if seen_before(data.get("session_id"), key):
            return ""
        return json.dumps({"decision": "block", "reason": message(lines)})
    except Exception:
        return ""


def main(argv):
    if argv[:1] == ["hook"]:
        out = hook(sys.stdin.read())
        if out:
            print(out)
        return 0
    if argv[:1] == ["check"] and len(argv) > 1:
        lines = flagged(Path(argv[1]).read_text(encoding="utf-8"))
        for x in lines:
            print(x)
        return 1 if lines else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
