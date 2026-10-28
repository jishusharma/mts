"""O3 overhead cut: count 7 days of origin/fast-track commits by kind.

Same classification as make_status.get_commit_mix (research/claim-release/other),
plus a by-area and by-subject-family breakdown of the 'other' bucket so cuts are
ranked by measured count. Parse the full log, then count -- never from truncated output.
"""
import json
import re
import subprocess
import time
from collections import Counter
from pathlib import Path

RESEARCH_PATHS = ("MyTradingSys/research/", "MyTradingSys/methodology/", "MyTradingSys/extracts/", "MyTradingSys/backtest/")


def family_of(subj):
    """Group an 'other' commit subject into its producer family."""
    if subj.startswith("fold context"):
        return "fold-context (context_gap.py auto-commit at ship)"
    if subj.startswith("lane health"):
        return "lane-health ping (codex_run.py / lane_health.py)"
    if subj.startswith("lease pipeliner"):
        return "lease-pipeliner renew"
    if subj.startswith("desk task") or subj.startswith("desk:"):
        return "desk notes"
    if re.match(r"^(task|tasks) .* (done|-> |READY)", subj):
        return "tasks done/READY stamps"
    if subj.startswith("doctor"):
        return "doctor"
    if subj.startswith(("Supervisor C notes", "Thinker", "planner", "Lead", "lead", "docs")):
        return "lead/planner notes"
    if subj.startswith("tasks"):
        return "tasks other"
    if subj.startswith("lane"):
        return "lane other"
    return subj.split(":")[0][:24]


def main():
    root = Path(__file__).resolve().parents[4]
    since = time.time() - 7 * 86400
    out = subprocess.run(
        ["git", "-C", str(root), "log", "origin/fast-track", "--no-merges", "-n", "20000",
         "--format=@@%ct|%s", "--name-only"],
        capture_output=True, text=True, check=True)
    buckets = {"research": 0, "claim/release": 0, "other": 0}
    other_by_area = Counter()
    other_families = Counter()
    per_day = Counter()
    other_per_day = Counter()
    family_samples = {}
    family_files = {}
    for block in out.stdout.split("@@")[1:]:
        lines = [ln for ln in block.split("\n") if ln.strip()]
        if not lines:
            continue
        ts_s, _, subj = lines[0].partition("|")
        if not ts_s.isdigit() or int(ts_s) < since:
            continue
        day = time.strftime("%Y-%m-%d", time.localtime(int(ts_s)))
        per_day[day] += 1
        if re.match(r"(claim|release) ", subj):
            buckets["claim/release"] += 1
        elif any(f.startswith(RESEARCH_PATHS) and not f.endswith("/STATUS.md") for f in lines[1:]):
            buckets["research"] += 1
        else:
            buckets["other"] += 1
            fam = family_of(subj)
            other_families[fam] += 1
            family_samples.setdefault(fam, []).append(subj)
            for f in lines[1:]:
                family_files.setdefault(fam, Counter())[f] += 1
            other_per_day[day] += 1
            files = lines[1:]
            prefix = files[0].split("/")[0] if files else "(no files)"
            if prefix == "MyTradingSys" and len(files[0].split("/")) > 2:
                prefix = "MyTradingSys/" + files[0].split("/")[1]
            other_by_area[prefix] += 1
    tot = sum(buckets.values())
    print(json.dumps({
        "total": tot,
        "buckets": buckets,
        "pct": {k: round(100 * v / tot) if tot else 0 for k, v in buckets.items()},
        "other_per_day": dict(sorted(other_per_day.items())),
        "per_day_total": dict(sorted(per_day.items())),
        "other_families_top20": dict(other_families.most_common(20)),
        "family_samples": {k: v[:3] for k, v in sorted(family_samples.items())},
        "family_top_files": {k: dict(c.most_common(4)) for k, c in family_files.items()},
        "other_by_area": dict(other_by_area.most_common()),
    }, indent=1))


if __name__ == "__main__":
    main()
