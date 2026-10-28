"""Fail when a decision point in the engine code has no TOM-/FAB- rule id (DSA_TASKS T8).

Each decision point is an anchor line (regex) that must exist exactly once; a rule id
(TOM-nnn or FAB-xxx) must appear on that line, in the WINDOW lines above it, or on the line right after it.
A missing anchor also fails, so a renamed/removed decision point cannot silently lose its id.
Usage: python scripts/dev/check_rule_ids.py   (exit 1 on any failure)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WINDOW = 3
ID_RE = re.compile(r"\b(?:TOM-\d+|FAB-[A-Za-z0-9][A-Za-z0-9_-]*)")

POINTS = {
    "src/main/java/datafeed/SetupCandidatesBuilder.java": [
        ("state", r"private static String classifyState"),
        ("directions", r"private static List<String> determineDirections"),
        ("zones", r"private static List<Zone> extractZones"),
        ("setup_type", r"private static String determineSetupType"),
        ("stop", r"double swingHigh = 0, swingLow = 0;"),
        ("target_pool", r"List<Double> targets = new ArrayList<>\(\);"),
    ],
    "MyTradingSys/runtime/math_object_builder.py": [
        ("zones", r"^def _extract_zones"),
        ("swing_tf", r"^def _swing_tf_for_zone"),
        ("target_pool", r"# Collect all VP POCs"),
        ("stop", r"# STOP selection"),
        ("target", r"# TARGET selection"),
        # state: NONE - math_object_builder.py has no state classifier
    ],
}


def check(root=ROOT, points=POINTS):
    errors = []
    for rel, items in points.items():
        path = Path(root) / rel
        if not path.exists():
            errors.append(f"{rel}: file missing")
            continue
        lines = path.read_text(encoding="utf-8").split("\n")
        for label, pat in items:
            hits = [i for i, l in enumerate(lines) if re.search(pat, l)]
            if len(hits) != 1:
                errors.append(f"{rel}: [{label}] anchor /{pat}/ matched {len(hits)} lines (need 1)")
                continue
            i = hits[0]
            if not any(ID_RE.search(l) for l in lines[max(0, i - WINDOW):i + 2]):
                errors.append(f"{rel}:{i + 1}: [{label}] decision point has no TOM-/FAB- id")
    return errors


if __name__ == "__main__":
    errs = check()
    for e in errs:
        print("FAIL", e)
    print("rule-id check:", "FAILED" if errs else "ok")
    sys.exit(1 if errs else 0)
