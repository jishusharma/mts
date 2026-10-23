"""One role-line detector for role_loader.py and turn_meter.py (failure review 2026-10-23, root causes 3 and 4).

Real first messages do not start with the role line: the app puts a worktree notice in a <system-reminder> block first, a pasted
brief arrives in <pasted_content ...> tags, and a session started by start_session wraps the brief as
"Background (from the session that started this one): ... Task:\n<brief>". `clean()` strips all of that; `role_line()` then reads
only the FIRST non-empty line, which must be `You are <Role>.` (ends there or with punctuation / "Login"). A role line further down,
inside a quote, an example, a pasted log or a session event never counts (review of 9f0cb459c: a worker escaped its turn cap that way).
"""
import re

REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.S | re.I)
LEADING_REMINDERS = re.compile(r"^\s*(?:<system-reminder>.*?</system-reminder>\s*)+", re.S | re.I)
PASTE_TAG = re.compile(r"</?pasted_content\b[^>]*>|</?pasted[-_ ]?text\b[^>]*>", re.I)
TASK_SPLIT = re.compile(r"(?:^|\n)[ \t]*Task:[ \t]*\n", re.I)    # the wrapper's own "Task:" line; an inline one may be quoted text
WORKTREE_NOTICE = re.compile(r"^[ \t]*(?:You are working in|This is a git worktree|Worktree:)[^\n]*(?:\n|$)", re.I | re.M)
# App and session events: their text is another session's or the app's, never the start line of this session (turn_meter.py).
EVENTS = ("<cross-session-message", "<side-sessions-event", "<ci-monitor-event", "<task-notification", "another claude session")
LEAD = re.compile(r"^(?:[ \t>#*_`]+|task:[ \t]*)+", re.I)   # "**You are Supervisor.**", "> You are X.", "Task: You are X."
START = re.compile(r"(?:you are|you're)[ \t]+(?:the[ \t]+)?", re.I)
WORD = re.compile(r"[A-Za-z0-9]+(?:_[A-Za-z0-9]+)*")     # "1985Artifacts_Guy", "Eagle_Eyes"
END = re.compile(r"[*_`]*[ \t]*(?:[.:!,;(]|[-\u2013\u2014][ \t]|login\b|$)", re.I)   # strict: the name ends the sentence
BOUNDARY = re.compile(r"(?![A-Za-z0-9_'-])")                                        # loose: "You are Lab_Guy for ONE pass"


def is_event(text):
    """True when the text (after leading reminders) is an app or session event, not a prompt of this session's own."""
    s = LEADING_REMINDERS.sub("", str(text or ""), count=1).lstrip().lower()
    return s.startswith(EVENTS)


def clean(text):
    """Text with reminders, paste tags, the worktree notice and a start_session "Background ... Task:" wrapper removed."""
    s = str(text or "").replace("\r\n", "\n").replace("\r", "\n").replace(chr(0xfeff), "").replace(chr(0x200b), "")
    s = REMINDER.sub("", s)
    s = PASTE_TAG.sub("", s)
    s = WORKTREE_NOTICE.sub("", s)
    if s.lstrip().lower().startswith("background"):
        m = TASK_SPLIT.search(s)
        if m:
            s = s[m.end():]
    return s.strip()


def first_line(text):
    for ln in clean(text).split("\n"):
        ln = LEAD.sub("", ln.strip()).strip()
        if ln:              # a bare "Task:" or "**" line is a label: the next line is the first one
            return ln
    return ""


def role_line(text, known=None, events=False, strict=False):
    """Role named by the first non-empty line `You are <Role>...` (after the wrappers), else None. `known` (role names, any case,
    '_' or ' ') limits the answer and gives its spelling. events=False: an event text never names this session's role.
    strict=True (turn_meter's Supervisor exemption): the name must end the sentence ("You are the supervisor of x" is not one)."""
    end = END if strict else BOUNDARY
    if not events and is_event(text):
        return None
    ln = first_line(text)
    m = START.match(ln)
    if not m:
        return None
    norm = lambda x: re.sub(r"[_ ]+", "_", x.strip().lower())
    table = {norm(k): k for k in (known or [])}
    rest = ln[m.end():]
    words = []
    pos = 0
    for _ in range(2):          # one-word, then two-word names ("Eagle Eyes", "Session Planner")
        w = WORD.match(rest, pos)
        if not w:
            break
        words.append(w.group(0))
        pos = w.end()
        name = " ".join(words)
        if (known is None or norm(name) in table) and end.match(rest, pos):
            return name if known is None else table[norm(name)]
        if pos < len(rest) and rest[pos] in " \t":
            pos += 1
        else:
            break
    return None


def is_role(text, role, strict=True):
    return bool(role_line(text, [role], strict=strict))
