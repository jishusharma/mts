"""Check 6: BUGS.md rows with Status IN-FIX opened more than 14 days ago (BUGS.md rule; Build-Check fails them too).

Row format: `| ID | Opened(YYYY-MM-DD) | Status | ...`. Digest check: WARN. Hash = check + overdue IDs.
"""
import re
import sys
from datetime import date

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from _common import REPO, emit, run

MAX_DAYS = 14


def main():
    today = date.today()
    overdue = []
    text = (REPO / "MyTradingSys" / "research" / "BUGS.md").read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 4 or not re.match(r"^\d{4}-\d{2}-\d{2}$", cells[2]):
            continue
        if cells[3] == "IN-FIX":
            age = (today - date.fromisoformat(cells[2])).days
            if age > MAX_DAYS:
                overdue.append((cells[1], age))
    if overdue:
        return emit("bug_age", "WARN", f"{len(overdue)} IN-FIX row(s) > {MAX_DAYS}d: "
                    + ", ".join(f"{i}({a}d)" for i, a in overdue[:8]), [i for i, _ in overdue])
    return emit("bug_age", "OK", f"no IN-FIX row older than {MAX_DAYS} days", ["ok"])


if __name__ == "__main__":
    run(main)
