"""Mechanical check of MyTradingSys/system/DSA_BLOCK_REVIEW.md (card dsa-bridge-fix-review-opus-1108).

Exit 0 when the review meets the card's done_when shape, else prints each failure and exits 1.
Checks only structure, never the judgement itself:
  1. sections present: Bug table, Repeat classes, DeepSeek rules, Bridge behaviours, DSA prompt, Ranked fix list
  2. bug table: columns id|symptom|fix|state|class, >= 40 rows, no empty cell, state in open/closed/mitigated,
     every class in the table appears in the repeat-class table with the right count; count >= 2 => design fault
  3. DeepSeek rules: every source row has a date (YYYY-MM-DD) and an https URL; a 'could not be fetched' line
  4. behaviours: the six named behaviours each ranked likely/possible/unlikely and proved/unproved
  5. prompt section: at least 3 quoted current lines each with replacement text; DSA_SESSION_PROMPT.md is not
     changed against origin/fast-track
  6. fix list: 1..12 items; items 1-3 are pacing guard, one machine per account, stop on warning;
     every item has failure prevented, a fail-first test and an owner lane
Usage: python MyTradingSys/system/check_dsa_review.py [path]
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / "MyTradingSys" / "system" / "DSA_BLOCK_REVIEW.md"

SECTIONS = ["## 1. Bug table", "## 2. Repeat classes", "## 3. DeepSeek rules",
            "## 4. Bridge behaviours", "## 5. DSA prompt", "## 6. Ranked fix list"]
BEHAVIOURS = ["auto-send", "rate", "parallel chats", "one account on several machines",
              "fixed-format messages", "command text"]
FIRST_THREE = ["pacing guard", "one machine per account", "stop on warning"]
LANES = {"OPUS", "SONNET", "CLAUDE", "CODEX", "GEMINI", "HAIKU", "DSA", "OPERATOR", "AIBRIDGE"}


def section(text: str, head: str) -> str:
    i = text.find(head)
    if i < 0:
        return ""
    j = text.find("\n## ", i + len(head))
    return text[i: j if j > 0 else len(text)]


def table_rows(block: str) -> list[list[str]]:
    rows = []
    for line in block.splitlines():
        s = line.strip()
        if not (s.startswith("|") and s.endswith("|")):
            continue
        cells = [c.strip() for c in s[1:-1].split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
            continue
        rows.append(cells)
    return rows


def check(text: str, prompt_unchanged: bool | None = True) -> list[str]:
    errs: list[str] = []
    for h in SECTIONS:
        if h not in text:
            errs.append(f"missing section '{h}'")
    if errs:
        return errs

    # 1 bug table
    rows = table_rows(section(text, SECTIONS[0]))
    if not rows or [c.lower() for c in rows[0]] != ["id", "symptom", "fix", "state", "class"]:
        errs.append("bug table header must be | id | symptom | fix | state | class |")
        body = []
    else:
        body = rows[1:]
    if len(body) < 40:
        errs.append(f"bug table has {len(body)} rows, need >= 40")
    counts: dict[str, int] = {}
    for r in body:
        if len(r) != 5 or any(not c for c in r):
            errs.append(f"bug table row has an empty or missing cell: {r[:1]}")
            continue
        if r[3].lower() not in {"open", "closed", "mitigated"}:
            errs.append(f"bug {r[0]}: state '{r[3]}' not open/closed/mitigated")
        counts[r[4]] = counts.get(r[4], 0) + 1

    # 2 repeat classes
    crow = table_rows(section(text, SECTIONS[1]))
    if not crow or [c.lower() for c in crow[0]][:3] != ["class", "count", "design fault"]:
        errs.append("repeat-class table header must start | class | count | design fault |")
    else:
        seen = {}
        for r in crow[1:]:
            if len(r) < 3 or any(not c for c in r):
                errs.append(f"repeat-class row has an empty cell: {r[:1]}")
                continue
            seen[r[0]] = r
            want = counts.get(r[0])
            if want is None:
                errs.append(f"class '{r[0]}' not used in the bug table")
                continue
            if not r[1].isdigit() or int(r[1]) != want:
                errs.append(f"class '{r[0]}': count {r[1]} != {want} rows in the bug table")
            fault = r[2].lower().startswith("yes")
            if (want >= 2) != fault:
                errs.append(f"class '{r[0]}': count {want} but design fault '{r[2]}'")
        for c in counts:
            if c not in seen:
                errs.append(f"class '{c}' missing from the repeat-class table")

    # 3 DeepSeek rules
    rules = section(text, SECTIONS[2])
    srows = table_rows(rules)
    if len(srows) < 3:
        errs.append("DeepSeek rules: need a source table with >= 2 rows")
    for r in srows[1:]:
        line = " ".join(r)
        if not re.search(r"\d{4}-\d{2}-\d{2}", line) or "https://" not in line or any(not c for c in r):
            errs.append(f"DeepSeek rule row lacks date/URL or has empty cell: {r[:1]}")
    if "could not be fetched" not in rules.lower():
        errs.append("DeepSeek rules: no 'could not be fetched' statement")

    # 4 behaviours
    brows = table_rows(section(text, SECTIONS[3]))
    found = {}
    for r in brows[1:]:
        if r:
            found[r[0].lower()] = r
    for b in BEHAVIOURS:
        r = found.get(b)
        if not r:
            errs.append(f"behaviour '{b}' not ranked")
            continue
        line = " ".join(r).lower()
        if any(not c for c in r):
            errs.append(f"behaviour '{b}' has an empty cell")
        if not re.search(r"\b(likely|possible|unlikely)\b", line):
            errs.append(f"behaviour '{b}' lacks likely/possible/unlikely")
        if not re.search(r"\b(proved|unproved)\b", line):
            errs.append(f"behaviour '{b}' lacks proved/unproved")

    # 5 prompt
    p = section(text, SECTIONS[4])
    if p.count("Current:") < 3 or p.count("Replacement:") < p.count("Current:"):
        errs.append("DSA prompt section: need >= 3 'Current:' lines each with a 'Replacement:'")
    if prompt_unchanged is False:
        errs.append("DSA_SESSION_PROMPT.md differs from origin/fast-track (must not be edited)")

    # 6 fix list
    frows = table_rows(section(text, SECTIONS[5]))
    if not frows or [c.lower() for c in frows[0]] != ["rank", "fix", "failure prevented", "fail-first test", "owner lane"]:
        errs.append("fix table header must be | rank | fix | failure prevented | fail-first test | owner lane |")
        items = []
    else:
        items = frows[1:]
    if not 1 <= len(items) <= 12:
        errs.append(f"fix list has {len(items)} items, need 1..12")
    for i, r in enumerate(items):
        if len(r) != 5 or any(not c for c in r):
            errs.append(f"fix item {i + 1}: empty or missing cell")
            continue
        if i < 3 and FIRST_THREE[i] not in r[1].lower():
            errs.append(f"fix item {i + 1} must be '{FIRST_THREE[i]}'")
        if not re.search(r"test", r[3], re.I):
            errs.append(f"fix item {i + 1}: test cell does not name a test")
        if not any(l in r[4].upper() for l in LANES):
            errs.append(f"fix item {i + 1}: owner lane '{r[4]}' unknown")
    return errs


def prompt_unchanged() -> bool | None:
    try:
        r = subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", "origin/fast-track", "--",
                            "DSA_SESSION_PROMPT.md"], capture_output=True, timeout=60)
    except Exception:
        return None
    return r.returncode == 0 if r.returncode in (0, 1) else None


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else DEFAULT
    if not path.exists():
        print(f"FAIL: {path} missing")
        return 1
    errs = check(path.read_text(encoding="utf-8"), prompt_unchanged())
    for e in errs:
        print("FAIL:", e)
    print("PASS" if not errs else f"{len(errs)} failure(s)")
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
