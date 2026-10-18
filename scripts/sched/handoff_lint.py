"""Handoff quality gate: NEXT_SESSION.md may only say `go` when its task list is curated (operator 2026-10-10).

Why: the relay runs whatever the list says. A vague or unrunnable item wastes a whole session, and an empty list stops the chain
while real work waits (2026-10-10: "queue empty" while a backlog existed; a task pointed at files that were not on origin).

Format (RELAY.md "Task list standard"): the first fenced block of the file is the session prompt. Tasks are lines `   Qn. <text>`;
following lines indented deeper belong to the same task.
  - block <= 30 lines (RELAY.md "Task list standard")
  - every unblocked task: <= 6 lines, contains `DONE when:` (an observable end), no vague wording, every path it names exists
  - a task starting `Qn. DONE` is finished; `Qn. (after ...)` is blocked: both skip the unblocked checks
  - the block restates no hard rule from CLAUDE.md
  - a task may start `Qn. host=<NAME> ...` (NAME = a machine name or `any`; absent = any): with `host` set, lint() counts it
    runnable only on that host. The tag is stripped before done/blocked is decided, so `Qn. host=JIS-NB (after Qm)` is blocked.
    One tag, only right after `Qn.` (two tags or a tag on a continuation line = error); a node name's domain suffix is ignored.
  - a task may also carry `lane=CODEX` or `lane=DSA` (after `Qn.`, before or after the host tag): it is run-and-report work for the GPT
    layer lab or the DSA AI Bridge, so `relay.py route` posts it to that lane once and no Claude relay session runs it. Parsed here
    (one parser for lint, QUEUE and route): `t["lane"]` is CODEX / DSA / None; two lane tags or another value = error.
  - `--go` needs at least one unblocked open task; `--stop` is refused while one exists (stop only when all are done or blocked)
"""
import re
from pathlib import Path

MAX_BLOCK = 30
MAX_TASK_LINES = 6
VAGUE = ["next open", "follow-up", "follow up", "take the next", "next unfinished", "as needed", "etc.", "and more", "everything", "whatever"]
RESTATED = ["never commit to master", "testnet only", "never the live tree", "worktree only", "never rebase", "never force-push", "never mainnet"]
TASK = re.compile(r"^(\s+)Q(\d+)\.\s*(.*)$")
HOST = re.compile(r"^host=(\S+)\s*", re.I)
HOST_ANY = re.compile(r"(?:^|\s)host=\S+", re.I)
LANE = re.compile(r"^lane=(\S+)\s*", re.I)
LANE_ANY = re.compile(r"(?:^|\s)lane=\S+", re.I)
LANES = ("CODEX", "DSA")
HOST_ERR = "go with no unblocked open task for host"
NONE_ERR = "go with no unblocked open task:"
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
        t["tags"] = len(HOST_ANY.findall(t["first"]))
        t["cont_tag"] = any(HOST_ANY.search(ln) for ln in t["lines"][1:])
        t["lane_tags"] = len(LANE_ANY.findall(t["first"]))
        t["host"] = t["lane"] = None
        f = t["first"]
        while True:   # `host=` and `lane=` tags in either order, only right after `Qn.`
            m = HOST.match(f) if t["host"] is None else None
            if m:
                t["host"] = m.group(1)
            else:
                m = LANE.match(f) if t["lane"] is None else None
                if not m:
                    break
                t["lane"] = m.group(1).upper()
            f = f[m.end():]
        t["first"] = f
        t["state"] = "done" if f.startswith("DONE") else "blocked" if f.startswith("(after") else "open"
    return tasks


def path_exists(root, tok):
    if any(c in tok for c in "<>*") or "..." in tok:
        return True
    return any((Path(root) / pre / tok).exists() for pre in ("", "MyTradingSys"))


def short(name):
    """JIS-NB.lan / jis-nb.localdomain -> jis-nb: platform.node() may carry a domain suffix the tag never has (RV08)."""
    return name.split(".")[0].lower()


def runs_on(t, host):
    return not host or not t.get("host") or short(t["host"]) in ("any", short(host))


def lint(text, root, want="go", host=None):
    """(errors, tasks). want = go | stop. host: for want=go only tasks that can run on that host count as runnable."""
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
    seen = {}
    for t in tasks:
        seen[t["id"]] = seen.get(t["id"], 0) + 1
    for tid, n in seen.items():
        if n > 1:
            errs.append("%s is used twice in the block: two threads reused one number; renumber so each task id is unique" % tid)
    for t in tasks:
        if t["tags"] > 1:
            errs.append("%s has %d host= tags: keep one (`host=<NAME>` or `host=any`) right after `%s.`" % (t["id"], t["tags"], t["id"]))
        if t["cont_tag"]:
            errs.append("%s has host= on a continuation line: it is read only right after `%s.`, move it there" % (t["id"], t["id"]))
        if t["lane_tags"] > 1 or (t["lane"] and t["lane"] not in LANES):
            errs.append("%s: use one `lane=CODEX` or `lane=DSA` tag right after `%s.` (got %d, value %r)" % (t["id"], t["id"], t["lane_tags"], t["lane"]))
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
        errs.append(NONE_ERR + " write `--stop` and name each blocker, or add the missing task")
    elif want == "go" and host and opened and not any(runs_on(t, host) for t in opened):
        errs.append("%s %s: open tasks all belong to other hosts (%s); write `--stop` naming them or add a task for this host"
                    % (HOST_ERR, host, ", ".join("%s=%s" % (t["id"], t["host"]) for t in opened)))
    if want == "stop" and opened:
        errs.append("stop refused: %s still open and unblocked (%s)" % (len(opened), ", ".join(t["id"] for t in opened)))
    if want == "stop":
        errs = [e for e in errs if e.startswith("stop refused")]
    return errs, tasks
