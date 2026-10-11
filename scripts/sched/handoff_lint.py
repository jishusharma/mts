"""Handoff quality gate: NEXT_SESSION.md may only say `go` when its task list is curated (operator 2026-10-10).

Why: the relay runs whatever the list says. A vague or unrunnable item wastes a whole session, and an empty list stops the chain
while real work waits (2026-10-10: "queue empty" while a backlog existed; a task pointed at files that were not on origin).

Format (RELAY.md "Task list standard"): the first fenced block of the file is the session prompt. Tasks are lines `   Qn. <text>`;
following lines indented deeper belong to the same task.
  - block <= 30 lines (CLAUDE.md "What a CL prompt carries")
  - every unblocked task: <= 6 lines, contains `DONE when:` (an observable end), no vague wording, every path it names exists
  - a task starting `Qn. DONE` is finished; `Qn. (after ...)` is blocked: both skip the unblocked checks
  - the block restates no hard rule from CLAUDE.md
  - `--go` needs at least one unblocked open task; `--stop` is refused while one exists (stop only when all are done or blocked)
"""
import re
from pathlib import Path

MAX_BLOCK = 30
MAX_TASK_LINES = 6
VAGUE = ["next open", "follow-up", "follow up", "take the next", "next unfinished", "as needed", "etc.", "and more", "everything", "whatever"]
RESTATED = ["never commit to master", "testnet only", "never the live tree", "worktree only", "never rebase", "never force-push", "never mainnet"]
TASK = re.compile(r"^(\s+)Q(\d+)\.\s*(.*)$")
PATH = re.compile(r"[\w.\-]+(?:/[\w.\-]+)+\.(?:py|md|json|csv|java|ps1|yml|yaml|txt)\b")


def block_lines(text):
    parts = text.split("```")
    return parts[1].strip("\n").splitlines() if len(parts) >= 3 else None


def parse_tasks(lines):
    """[{id, lines, state}] state = done | blocked | open"""
    tasks, cur = [], None
    for ln in lines:
        m = TASK.match(ln)
        if m:
            cur = {"id": "Q" + m.group(2), "indent": len(m.group(1)), "lines": [ln], "first": m.group(3).strip()}
            tasks.append(cur)
        elif cur and ln.strip() and len(ln) - len(ln.lstrip()) > cur["indent"]:
            cur["lines"].append(ln)
        else:
            cur = None
    for t in tasks:
        f = t["first"]
        t["state"] = "done" if f.startswith("DONE") else "blocked" if f.startswith("(after") else "open"
    return tasks


def path_exists(root, tok):
    if any(c in tok for c in "<>*") or "..." in tok:
        return True
    return any((Path(root) / pre / tok).exists() for pre in ("", "MyTradingSys"))


def lint(text, root, want="go"):
    """(errors, tasks). want = go | stop."""
    errs = []
    lines = block_lines(text)
    if lines is None:
        return ["no fenced prompt block in the handoff file"], []
    if len(lines) > MAX_BLOCK:
        errs.append("prompt block is %d lines, limit %d" % (len(lines), MAX_BLOCK))
    low = "\n".join(lines).lower()
    for ph in RESTATED:
        if ph in low:
            errs.append("restates a hard rule (%r): CLAUDE.md already carries it" % ph)
    tasks = parse_tasks(lines)
    if not tasks:
        errs.append("no tasks: add lines `   Q1. <task> ... DONE when: <observable>`")
    for t in tasks:
        if t["state"] != "open":
            continue
        body = "\n".join(t["lines"])
        if len(t["lines"]) > MAX_TASK_LINES:
            errs.append("%s is %d lines (max %d): split it into session-sized tasks" % (t["id"], len(t["lines"]), MAX_TASK_LINES))
        if "DONE when:" not in body:
            errs.append("%s has no `DONE when:` (what a reviewer can observe)" % t["id"])
        for ph in VAGUE:
            if ph in body.lower():
                errs.append("%s is vague (%r): name the exact item" % (t["id"], ph))
        for tok in sorted(set(PATH.findall(body))):
            if not path_exists(root, tok):
                errs.append("%s names %s which does not exist in this tree (make a prior task create it, or mark this one `(after ...)`)" % (t["id"], tok))
    opened = [t for t in tasks if t["state"] == "open"]
    if want == "go" and tasks and not opened:
        errs.append("go with no unblocked open task: write `--stop` and name each blocker, or add the missing task")
    if want == "stop" and opened:
        errs.append("stop refused: %s still open and unblocked (%s)" % (len(opened), ", ".join(t["id"] for t in opened)))
    if want == "stop":
        errs = [e for e in errs if e.startswith("stop refused")]
    return errs, tasks
