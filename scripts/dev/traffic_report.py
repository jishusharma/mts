"""traffic_report.py - how much of origin/fast-track's traffic is overhead (TRAFFIC_BUSTERS.md).

  python scripts/dev/traffic_report.py [hours]     default 24

Prints commits by kind (merge / claim / release / other) so a buster can show its number moved.
"""
import re
import subprocess
import sys

TRUNK = "origin/fast-track"


def classify(subject, parents):
    if parents > 1:
        return "merge"
    word = subject.split(" ", 1)[0].lower()
    return word if word in ("claim", "release") else "other"


def report(hours=24, runner=subprocess.run):
    out = runner(["git", "log", TRUNK, f"--since={hours} hours ago", "--format=%P|%s"],
                 capture_output=True, text=True).stdout.splitlines()
    counts = {"merge": 0, "claim": 0, "release": 0, "other": 0}
    for line in out:
        parents, _, subject = line.partition("|")
        counts[classify(subject, len(parents.split()))] += 1
    total = sum(counts.values())
    pct = lambda n: f"{100 * n / total:.0f}%" if total else "0%"
    overhead = counts["merge"] + counts["claim"] + counts["release"]
    return (f"last {hours} h on {TRUNK}: {total} commits | " + " | ".join(f"{k} {v} ({pct(v)})" for k, v in counts.items())
            + f" | overhead {overhead} ({pct(overhead)})")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if re.fullmatch(r"\d+", a)]
    print(report(int(args[0]) if args else 24))
