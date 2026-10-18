"""Month-by-month verdict-count diff of two Tom core BT row directories (read-only).

Usage: python scripts/dev/diff_tom_rows.py [OLD_DIR] [NEW_DIR]
Defaults: OLD F:/MTS/data/tom_bt, NEW F:/MTS/data/tom_bt_2026-10-07.
Prints, per month, row counts and verdict counts for both, and marks months where SETUP_FORMING differs.
"""
import collections
import glob
import json
import os
import sys

OLD = sys.argv[1] if len(sys.argv) > 1 else "F:/MTS/data/tom_bt"
NEW = sys.argv[2] if len(sys.argv) > 2 else "F:/MTS/data/tom_bt_2026-10-07"


def load(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh]


def counts(rows):
    return dict(collections.Counter(r.get("verdict") for r in rows)) if rows is not None else None


def main():
    months = sorted({os.path.basename(f) for d in (OLD, NEW) for f in glob.glob(d + "/*.rows.jsonl")})
    tot_old = tot_new = 0
    for m in months:
        a, b = load(OLD + "/" + m), load(NEW + "/" + m)
        ca, cb = counts(a), counts(b)
        fa = (ca or {}).get("SETUP_FORMING", 0)
        fb = (cb or {}).get("SETUP_FORMING", 0)
        tot_old += fa
        tot_new += fb
        mark = "  <-- SETUP_FORMING differs" if fa != fb else ""
        print(m, "rows", None if a is None else len(a), None if b is None else len(b), "old", ca, "new", cb, mark)
    print("SETUP_FORMING rows total: old", tot_old, "new", tot_new)


if __name__ == "__main__":
    main()
