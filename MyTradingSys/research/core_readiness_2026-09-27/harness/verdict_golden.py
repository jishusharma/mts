import sys
sys.dont_write_bytecode = True
"""
verdict_golden.py - L2+L3 golden regression (proof direction + verdict ladder).

Replays every archived snapshot through backtest/verdict.py (the Python port of
Compute-Verdict, parity-guarded by backtest/parity.py) and compares
(verdict, proof_dir, reason) per snapshot timestamp against a frozen baseline.

  --write-baseline   freeze current behaviour to verdict_golden_baseline.csv
  (default)          compare; print the transition matrix old -> new; exit 1 on any diff
  --expect FILE      JSON {"OLD->NEW": count, ...}; exit 0 only if the diff equals it exactly

The transition matrix is the acceptance tool for every verdict-changing task:
the task spec states the exact expected matrix, the implementer shows it matches.
Snapshots newer than the baseline are reported as NEW and not compared.
"""
import argparse, csv, json
from collections import Counter
import _common  # noqa: F401
from _common import HERE
from snapshots import iter_snapshots  # noqa: E402
from verdict import compute_verdict, proof_dir_of  # noqa: E402

BASE = HERE / "verdict_golden_baseline.csv"


def current():
    snaps, stats = iter_snapshots()
    out = {}
    for p, s, t in snaps:
        pd = proof_dir_of(s)
        v = compute_verdict(s, pd)
        out[str(s.get("timestamp_utc"))[:19]] = (v["verdict"], pd, v["reason"])
    return out, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-baseline", action="store_true")
    ap.add_argument("--expect")
    a = ap.parse_args()
    cur, stats = current()
    print("load stats:", stats)
    if a.write_baseline:
        with open(BASE, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["ts", "verdict", "proof_dir", "reason"])
            for ts in sorted(cur):
                w.writerow([ts, *cur[ts]])
        print("wrote", BASE.name, "rows", len(cur))
        print("verdicts:", dict(Counter(v[0] for v in cur.values())))
        return 0
    base = {}
    with open(BASE, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            base[r["ts"]] = (r["verdict"], r["proof_dir"], r["reason"])
    trans = Counter(); new = 0; missing = 0; ex = {}
    for ts, b in base.items():
        c = cur.get(ts)
        if c is None:
            missing += 1; continue
        if c[:2] != b[:2]:
            k = "%s/%s->%s/%s" % (b[0], b[1], c[0], c[1])
            trans[k] += 1
            ex.setdefault(k, ts)
    new = sum(1 for ts in cur if ts not in base)
    print("baseline rows %d | compared %d | new (not in baseline) %d | baseline rows without snapshot %d"
          % (len(base), len(base) - missing, new, missing))
    if not trans:
        print("NO CHANGE vs baseline")
    for k, n in trans.most_common():
        print("  %-50s %6d  e.g. %s" % (k, n, ex[k]))
    if a.expect:
        want = Counter(json.load(open(a.expect, encoding="utf-8")))
        ok = (want == trans)
        print("EXPECTED MATRIX:", "MATCH" if ok else "MISMATCH", dict(want))
        return 0 if ok else 1
    return 0 if not trans else 1


if __name__ == "__main__":
    raise SystemExit(main())
