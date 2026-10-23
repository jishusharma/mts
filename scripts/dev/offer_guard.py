"""Offer guard: a session may not end its reply by asking the operator's permission for work it can just do (operator 2026-10-22).

Operator 2026-10-22: "There must be a hook which says that never ask such a question as if you say go ... you should just go and
do it and if I see that you are doing something which you should not, then I will stop you. At least the work will not be lost."
Claude Code Stop hook (.claude/settings.json): reads the session's last reply; when one of its last lines offers or asks leave
("want me to", "shall I", "say go", "let me know if you'd like"), block ONCE: do the work now (or file the card and ship it), then
end with what was done. A line marked `OPERATOR-ONLY:` (money, mainnet, credentials, a physical machine, an operator decision) is
allowed. Text inside quotes or backticks is not read (a reply may quote the phrases). A second stop in the same turn is always
allowed; the same reply is never blocked twice. Never raises.
Env: MTS_OFFER_GUARD=off disables.
Run by hand: python scripts/dev/offer_guard.py check <reply.txt>   (prints the flagged lines, exit 1 when any)
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prereq_guard  # noqa: E402  (last_reply: the transcript reader both Stop guards share)

TAIL_LINES = 4
PATTERNS = re.compile(
    r"\b(want me to|would you like( me)? to|do you want( me)? to|shall I|should I (go ahead|proceed|start|build|do|file|ship|fix|add|make)"
    r"|(just |simply )?say (go|yes|the word)|(give me|once I have) (a |the |your )?(go|green light|ok)"
    r"|let me know (if|whether|when) you('d| would)? (want|like|prefer)|if you('d| would)? like,? I (can|could|will)"
    r"|if you want,? I (can|could|will)|I can (also |then )?\w+.{0,60}\bif you (want|like)|ready when you are"
    r"|waiting (on|for) your (go|ok|approval|word))\b", re.I)
QUOTED = re.compile(r"`[^`]*`|\"[^\"]*\"|“[^”]*”")
ALLOWED = "OPERATOR-ONLY:"


def flagged(text):
    """The reply's last lines that ask the operator's leave for work, minus quoted text and OPERATOR-ONLY lines."""
    lines, fence = [], False
    for line in (text or "").splitlines():
        s = line.strip()
        if s.startswith("```"):
            fence = not fence
            continue
        if s and not fence:
            lines.append(s)
    out = []
    for s in lines[-TAIL_LINES:]:
        if ALLOWED in s:
            continue
        if PATTERNS.search(QUOTED.sub("", s)):
            out.append(s[:200])
    return out


def message(lines):
    shown = "; ".join(f'"{x}"' for x in lines[:3])
    return ("OFFER GUARD: your reply ends by asking the operator's leave for work: " + shown + ". Operator 2026-10-22: do it now; "
            "he stops you if it is wrong, and work left as a question is lost. Do the work this turn (or file the card with "
            "`tasks.py new`, ship it and name it), then rewrite the ending as what was done. Only a real operator decision (money, "
            "mainnet, credentials, a physical machine, a choice between options he must make) stays, as one line prefixed "
            "`OPERATOR-ONLY:` with the reason.")


def seen_before(session_id, key):
    """True when this session was already blocked on this exact reply (no repeat blocks)."""
    if not session_id:
        return False
    f = Path(os.environ.get("MTS_STOP_GUARD_HOME") or Path.home() / ".claude") / "mts-offer-guard.json"
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
        if os.environ.get("MTS_OFFER_GUARD", "").lower() == "off":
            return ""
        data = json.loads(stdin_text or "{}")
        if data.get("stop_hook_active"):
            return ""
        text = data.get("last_assistant_message") or prereq_guard.last_reply(data.get("transcript_path"))
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
