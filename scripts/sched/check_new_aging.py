"""Check 8: in-flight .new files older than 24 h, from the BUILD_REPORT.md "In-flight .new files" list.

List line format: `  - <path>.new (age <N>m)`. Digest check: WARN. Hash = check + overdue paths.
"""
import re
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from _common import REPO, emit, run

MAX_MIN = 24 * 60


def main():
    report = REPO / "MyTradingSys" / "runtime" / "BUILD_REPORT.md"   # untracked since move-live-host-generated-files: absent on a fresh clone
    try:
        text = report.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return emit("new_aging", "WARN", "BUILD_REPORT.md absent: no .new aging data (run scripts/Build-Check.ps1)", ["report_absent"])
    overdue = []
    for m in re.finditer(r"^\s*-\s+(\S+\.new)\s+\(age (\d+)m\)", text, re.M):
        if int(m.group(2)) > MAX_MIN:
            overdue.append(m.group(1))
    if overdue:
        return emit("new_aging", "WARN", f"{len(overdue)} .new file(s) older than 24h: " + ", ".join(overdue[:4]),
                    overdue)
    return emit("new_aging", "OK", "no .new file older than 24h", ["ok"])


if __name__ == "__main__":
    run(main)
