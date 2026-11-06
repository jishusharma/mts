#!/usr/bin/env python
"""check_handoff.py [path] - T0 checker for MyTradingSys/system/NEXT_SESSION.md.

Exit 1 with one line per failure:
  a. first fenced block is at most 30 lines
  b. that block has a `sync.py start` line and a final `End:` line naming `sync.py ship`
  c. a `## State at handoff` heading exists
  d. every commit hash cited under that heading resolves (cat-file -e <hash>^{commit})
  e. no text matches the doc-test forbidden-string list (test_2 in
     MyTradingSys/tests/docs/test_integrity.py; that list is local to the test,
     so it is mirrored here and test_check_handoff.py guards against drift)
"""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT = REPO / "MyTradingSys" / "system" / "NEXT_SESSION.md"
MAX_BLOCK_LINES = 30
FORBIDDEN = [
    r"\bgit init\b",
    r"\bgit status\b",
    r"\bgit add\b",
    r"\bgit commit\b",
    r"\bgit diff\b",
    r"\bgit log\b",
    r"\bgit checkout\b",
    r"\bversion control\b",
]
STATE_RE = re.compile(r"^##\s+State at handoff\s*$", re.M)
HASH_RE = re.compile(r"(?<![0-9A-Za-z_.\-/])([0-9a-f]{7,40})(?![0-9A-Za-z_\-])")


def dropped_blocks(old, new, history=""):
    """`## ` headings of `old` that `new` lost and `history` (handoff_history text) does not hold. A session writing its own
    hand-over replaced the whole file once (plain pilot 2026-10-22: 82 lines to 7), deleting every other session's block."""
    heads = lambda t: re.findall(r"^##\s+(.+?)\s*$", t, re.M)
    keep = set(heads(new))
    return [h for h in heads(old) if h not in keep and h not in history]


def first_block(lines):
    """Return the lines inside the first fenced block, or None."""
    start = None
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("```"):
            if start is None:
                start = i
            else:
                return lines[start + 1:i]
    return None


def state_section(text):
    m = STATE_RE.search(text)
    if not m:
        return None
    rest = text[m.end():]
    nxt = re.search(r"^##\s", rest, re.M)
    return rest[:nxt.start()] if nxt else rest


def hash_resolves(h, repo):
    r = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", h + "^{commit}"],
                       capture_output=True, text=True)
    return r.returncode == 0


def check(text, repo=REPO):
    fails = []
    lines = text.splitlines()
    block = first_block(lines)
    if block is None:
        fails.append("a: no fenced prompt block found")
    else:
        if len(block) > MAX_BLOCK_LINES:
            fails.append(f"a: prompt block is {len(block)} lines, max {MAX_BLOCK_LINES}")
        if not any("sync.py start" in ln for ln in block):
            fails.append("b: prompt block has no 'sync.py start' line")
        body = [ln for ln in block if ln.strip()]
        last = body[-1].strip() if body else ""
        if not (last.startswith("End:") and "sync.py ship" in last):
            fails.append("b: last line of prompt block must start 'End:' and name 'sync.py ship'")
    state = state_section(text)
    if state is None:
        fails.append("c: missing '## State at handoff' heading")
    else:
        for h in sorted(set(HASH_RE.findall(state))):
            if not (re.search(r"[0-9]", h) and re.search(r"[a-f]", h)):
                continue  # plain numbers and plain words are not hashes
            if not hash_resolves(h, repo):
                fails.append(f"d: cited hash {h} does not resolve to a commit")
    for i, ln in enumerate(lines, 1):
        for p in FORBIDDEN:
            if re.search(p, ln):
                fails.append(f"e: line {i} matches forbidden pattern {p}")
                break
    return fails


def main(argv):
    path = Path(argv[1]) if len(argv) > 1 else DEFAULT
    if not path.is_file():
        print(f"FAIL: {path} not found")
        return 1
    fails = check(path.read_text(encoding="utf-8"))
    for f in fails:
        print("FAIL " + f)
    if not fails:
        print(f"OK {path.name}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
