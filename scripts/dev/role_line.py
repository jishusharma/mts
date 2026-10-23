"""One role-line detector for role_loader.py and turn_meter.py (failure review 2026-10-23, root causes 3 and 4).

Real first messages do not start with the role line: the app puts a worktree notice in a <system-reminder> block first, a pasted
brief arrives in <pasted_content ...> tags, and a session started by start_session wraps the brief as
"Background (from the session that started this one): ... Task:\n<brief>". `clean()` strips all of that; `role_line()` then looks
for a line of its own that is `You are <Role>.` among the first few non-empty lines (a mid-sentence mention never counts)."""
import re

REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.S | re.I)
PASTE_TAG = re.compile(r"</?pasted_content\b[^>]*>|</?pasted[-_ ]?text\b[^>]*>", re.I)
TASK_SPLIT = re.compile(r"(?:^|\n)[ \t]*Task:[ \t]*\n", re.I)
WORKTREE_NOTICE = re.compile(r"^[ \t]*(?:You are working in|This is a git worktree|Worktree:)[^\n]*(?:\n|$)", re.I | re.M)
ROLE_RE = re.compile(r"^[ \t]*(?:you are|you're)[ \t]+(?:the[ \t]+)?([A-Za-z][A-Za-z0-9_]*(?:[ _][A-Za-z0-9]+)?)(?![A-Za-z0-9_'])[ \t]*[.:!]?", re.I)
MAX_LINES = 6       # DECISION (OURS): the role line must be among the first 6 non-empty lines after the wrappers (conservative)


def clean(text):
    """Text with leading reminders, paste tags, the worktree notice and a start_session "Background ... Task:" wrapper removed."""
    s = str(text or "")
    s = REMINDER.sub("", s)
    s = PASTE_TAG.sub("", s)
    s = WORKTREE_NOTICE.sub("", s)
    m = TASK_SPLIT.search(s)
    if m and s.lstrip().lower().startswith(("background", "another claude session")):
        s = s[m.end():]
    return s.strip()


def first_lines(text, n=MAX_LINES):
    return [ln.strip() for ln in clean(text).splitlines() if ln.strip()][:n]


def role_line(text, known=None):
    """Role named by a `You are <Role>.` line of its own among the first lines, else None. `known` (iterable of role names, any
    case, '_' or ' ') limits the answer; the name is returned in the spelling of `known`."""
    norm = lambda x: re.sub(r"[_ ]+", "_", x.strip().lower())
    table = {norm(k): k for k in (known or [])}
    for ln in first_lines(text):
        m = ROLE_RE.match(ln)
        if not m:
            continue
        # one-word then two-word candidates ("Eagle_Eyes", "Eagle Eyes", "Supervisor")
        cands = [m.group(1)] + ([m.group(1).split()[0]] if " " in m.group(1) else [])
        for c in cands:
            if known is None:
                return c
            if norm(c) in table:
                return table[norm(c)]
    return None


def is_role(text, role):
    return bool(role_line(text, [role]))
