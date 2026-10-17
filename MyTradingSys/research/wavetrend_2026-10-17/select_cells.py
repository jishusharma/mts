"""Deterministic cell selection from the count table (no outcome data). Rule frozen in PRE_REG.md s4 before this runs.

Eligible row: var != ALL, event in PRIMARY, event_days >= FLOOR (n_days where the Holm(12) 80%-power MDE <= 0.30 SD),
and the TF's unconditioned event also >= FLOOR. Per event take the top 2 by event_days with distinct (tf, var);
at most 3 cells per TF; total <= 12. Ties break on (tf order, var, bin).
"""
import csv
import sys
from pathlib import Path

FLOOR = 153
PRIMARY = ["A1_L53", "A2_L53", "B2", "C1", "C2", "B1"]
TFORD = {"5m": 0, "15m": 1, "1h": 2, "4h": 3, "1d": 4}


def select(rows):
    base = {(r["tf"], r["event"]): int(r["event_days"]) for r in rows if r["var"] == "ALL"}
    chosen, per_tf = [], {}
    for ev in PRIMARY:
        cand = [r for r in rows if r["event"] == ev and r["var"] != "ALL" and int(r["event_days"]) >= FLOOR
                and base[(r["tf"], ev)] >= FLOOR]
        cand.sort(key=lambda r: (-int(r["event_days"]), TFORD[r["tf"]], r["var"], r["bin"]))
        used, taken = set(), 0
        for r in cand:
            if taken == 2 or len(chosen) == 12:
                break
            if (r["tf"], r["var"]) in used or per_tf.get(r["tf"], 0) >= 3:
                continue
            chosen.append(r); used.add((r["tf"], r["var"])); taken += 1
            per_tf[r["tf"]] = per_tf.get(r["tf"], 0) + 1
    return chosen


if __name__ == "__main__":
    src = Path(sys.argv[1])
    rows = list(csv.DictReader(open(src, newline="", encoding="utf-8")))
    ch = select(rows)
    out = src.parent / "CELLS.csv"
    with open(out, "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["cell", "tf", "event", "context_var", "bin", "events", "event_days", "side_up", "side_lo", "mde_d_holm12"])
        for i, r in enumerate(ch, 1):
            w.writerow([f"W{i:02d}", r["tf"], r["event"], r["var"], r["bin"], r["events"], r["event_days"],
                        r["side_up"], r["side_lo"], r["mde_d"]])
    print(open(out, encoding="utf-8").read())
