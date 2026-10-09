#!/usr/bin/env python
"""prompt_contract.py [file|-] - executable form of DSA_SESSION_PROMPT.md section 5d (B155).

Checks a composed Claude Code prompt against the six section 5d requirements and exits 1 with one line per failure:
  1 lines     at most 30 lines
  2 restated  no line copied verbatim from CLAUDE.md (hard rules) or STATUS.md (state), 40 characters or longer
  3 restrict  no restriction word (do not, don't, must not, never, forbidden, prohibited, off-limits, keep separate,
              not allowed) unless the line is tagged OPERATOR-SET or is an operator verbatim line (starts with ")
  4 opening   first four non-empty lines start with: Session ID, Mode, Repo root, TASK
  5 blocks    three named blocks present: DSA-side work already done / Collision check / Registry work DSA will do after
  6 screen    the prompt is screen only: a file argument inside the repo is refused (never saved to the repo)
The surface and clause checks that already exist live in prompt_check.ps1 (B083, B104, B133); this file adds what they lack.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MAX_LINES = 30
OPENING = ("session id", "mode", "repo root", "task")
BLOCKS = ("dsa-side work already done", "collision check", "registry work dsa will do after")
RESTRICTION = re.compile(r"\b(do not|don't|must not|never|forbidden|prohibited|off-limits|keep separate|not allowed)\b", re.I)
MIN_RESTATED = 40


def _reference_lines():
    out = set()
    for p in (REPO / "CLAUDE.md", REPO / "MyTradingSys" / "research" / "STATUS.md"):
        try:
            for ln in p.read_text(encoding="utf-8", errors="replace").splitlines():
                ln = ln.strip().lstrip("-* ").strip()
                if len(ln) >= MIN_RESTATED:
                    out.add(ln)
        except OSError:
            pass
    return out


def check_prompt(text, source_path=None, reference=None):
    fails = []
    lines = text.splitlines()
    if len(lines) > MAX_LINES:
        fails.append(f"lines: {len(lines)} lines, max {MAX_LINES}")
    ref = _reference_lines() if reference is None else reference
    for n, ln in enumerate(lines, 1):
        s = ln.strip().lstrip("-* ").strip()
        if len(s) >= MIN_RESTATED and s in ref:
            fails.append(f"restated: line {n} repeats CLAUDE.md/STATUS.md: {s[:60]}")
        if RESTRICTION.search(ln) and "OPERATOR-SET" not in ln and not ln.lstrip().startswith('"'):
            fails.append(f"restrict: line {n} has a restriction word without the operator's words: {ln.strip()[:60]}")
    nonempty = [ln.strip() for ln in lines if ln.strip()]
    for i, want in enumerate(OPENING):
        got = nonempty[i].lower() if i < len(nonempty) else ""
        if not got.startswith(want):
            fails.append(f"opening: non-empty line {i + 1} must start with '{want}', got '{got[:30]}'")
    low = text.lower()
    for b in BLOCKS:
        if b not in low:
            fails.append(f"blocks: missing named block '{b}'")
    if source_path is not None:
        try:
            Path(source_path).resolve().relative_to(REPO)
            fails.append(f"screen: prompt file {source_path} is inside the repo (screen only, never saved)")
        except ValueError:
            pass
    return fails


def main(argv):
    src = argv[0] if argv else "-"
    if src == "-":
        text, path = sys.stdin.read(), None
    else:
        text, path = Path(src).read_text(encoding="utf-8"), src
    fails = check_prompt(text, path)
    for f in fails:
        print("FAIL " + f)
    print("prompt_contract: " + ("FAIL" if fails else "PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
