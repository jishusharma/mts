"""Fail if MTS_USER_GUIDE.md has drifted from mts.ps1.

Checks:
  1. every verb in mts.ps1's verb table appears in the guide's command table as `mts <verb>`
  2. the command table lists no verb that mts.ps1 does not have
  3. every folder path in the "Where things are" table exists (file paths: their folder exists)
  4. the guide carries a "Last reviewed: YYYY-MM-DD" line

Usage: python scripts/dev/check_guide.py
"""
import sys
sys.dont_write_bytecode = True

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def section(text, heading):
    """Body of the '## ...heading...' section, up to the next '## '."""
    m = re.search(rf"^## [^\n]*{re.escape(heading)}[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def check(mts_text, guide_text, repo=REPO):
    errors = []
    table = re.search(r"# VERBS-BEGIN(.*?)# VERBS-END", mts_text, re.S)
    verbs = set(re.findall(r'@\("[^"]+",\s*"([a-z-]+)"', table.group(1))) if table else set()
    if not verbs:
        return ["mts.ps1: verb table (VERBS-BEGIN/END) not found or empty"]

    commands = section(guide_text, "All commands")
    listed = set(re.findall(r"`mts ([a-z-]+)", commands))
    for v in sorted(verbs - listed):
        errors.append(f"guide 'All commands' is missing: mts {v}")
    for v in sorted(listed - verbs):
        errors.append(f"guide 'All commands' lists a command mts.ps1 does not have: mts {v}")

    where = section(guide_text, "Where things are")
    for p in re.findall(r"`([^`]*\\[^`]*)`", where):
        path = repo / p.replace("\\", "/").rstrip("/")
        target = path if p.endswith("\\") else path.parent
        if not target.is_dir():
            errors.append(f"guide 'Where things are' path not found: {p}")

    if not re.search(r"Last reviewed: \d{4}-\d{2}-\d{2}", guide_text):
        errors.append("guide has no 'Last reviewed: YYYY-MM-DD' line")
    return errors


def main():
    mts = (REPO / "mts.ps1").read_text(encoding="utf-8")
    guide = (REPO / "MTS_USER_GUIDE.md").read_text(encoding="utf-8")
    errors = check(mts, guide)
    for e in errors:
        print("FAIL:", e)
    print("guide check:", "FAIL" if errors else "PASS")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
