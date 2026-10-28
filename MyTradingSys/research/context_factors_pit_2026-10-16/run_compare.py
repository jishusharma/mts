"""Angle (a): run the REPLAY and the VEC build on the same DEV slice and compare every factor at every decision point.

  python run_compare.py --days 40            # smoke slice, compares at every 1m bar
  python run_compare.py --full               # whole DEV, compares at every 1h close (both sides) and every 1m bar of days 200-230;
                                             # writes grid_context.csv (the count-only input of counts.py; no outcome column)

Floats are compared with a 1e-9 relative tolerance (the two builds sum in different orders); strings and bools exactly.
"""
import argparse
import csv
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import context_asof as CA   # noqa: E402

SCRATCH = os.environ.get("CF_SCRATCH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_scratch"))
CACHE = os.path.join(SCRATCH, "dev1m.npz")
FLOAT_TOL = 1e-9


def flat(d):
    out = {}
    for k, v in d.items():
        if isinstance(v, tuple):
            for i, x in enumerate(v):
                out[f"{k}_{i}"] = x
        elif v is None:
            out[k] = None
        else:
            out[k] = v
    return out


def same(a, b):
    if isinstance(a, float) or isinstance(b, float):
        if a is None or b is None:
            return False
        if a != a and b != b:
            return True
        if a != a or b != b:
            return False
        return abs(a - b) <= FLOAT_TOL * max(1.0, abs(a), abs(b))
    return a == b


def compare(rows_r, rows_v, label):
    bad = {}
    ex = {}
    n = 0
    for (tr, sr, fr), (tv, sv, fv) in zip(rows_r, rows_v):
        assert tr == tv and sr == sv
        n += 1
        keys = set(fr) | set(fv)
        for k in keys:
            if not same(fr.get(k), fv.get(k)):
                bad[k] = bad.get(k, 0) + 1
                if k not in ex:
                    ex[k] = (tr, sr, fr.get(k), fv.get(k))
    print(f"[{label}] points={n} fields={len(keys)} mismatching fields={len(bad)}")
    for k in sorted(bad):
        print(f"  {k}: {bad[k]} mismatches, first at t={ex[k][0]} side={ex[k][1]} replay={ex[k][2]!r} vec={ex[k][3]!r}")
    return bad


def run(bars, fund, grid_only, slice_1m=None):
    n = len(bars["C"])
    t0 = time.time()
    V = CA.VecTables(bars, fund)
    print(f"vec tables built in {time.time() - t0:.1f}s")
    pts = []
    for t in range(59, n, 60):
        pts.append(t)
    if slice_1m:
        a, b = slice_1m
        pts = sorted(set(pts) | set(range(a, min(b, n))))
    pts_set = set(pts)
    rows_v, rows_r = [], []
    t0 = time.time()
    for t in pts:
        for side in ("long", "short"):
            rows_v.append((t, side, flat(V.context(t, side))))
    print(f"vec contexts at {len(pts)} points in {time.time() - t0:.1f}s")
    t0 = time.time()
    R = CA.Replay(fund)
    O, H, L, C, Vv = bars["O"], bars["H"], bars["L"], bars["C"], bars["V"]
    for t in range(n):
        R.feed(t, float(O[t]), float(H[t]), float(L[t]), float(C[t]), float(Vv[t]))
        if t in pts_set:
            for side in ("long", "short"):
                rows_r.append((t, side, flat(R.context(side))))
    print(f"replay over {n} bars in {time.time() - t0:.1f}s")
    return rows_r, rows_v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=40)
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "grid_context.csv"))
    a = ap.parse_args()
    os.makedirs(SCRATCH, exist_ok=True)
    bars = CA.load_dev(cache=CACHE)
    fund = CA.load_funding()
    if not a.full:
        sub = CA.slice_bars(bars, a.days * 1440)
        rows_r, rows_v = run(sub, fund, grid_only=False, slice_1m=(0, a.days * 1440))
        compare(rows_r, rows_v, f"{a.days} days, every 1m bar")
        return
    rows_r, rows_v = run(bars, fund, grid_only=True, slice_1m=(200 * 1440, 230 * 1440))
    bad = compare(rows_r, rows_v, "full DEV: every 1h close + every 1m bar of days 200-230")
    # write the VEC grid rows (1h closes only) for the count-only tables
    keys = sorted({k for _, _, f in rows_v for k in f})
    with open(a.out, "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["t", "utc_close", "side"] + keys)
        for t, side, f in rows_v:
            if t % 60 == 59:
                w.writerow([t, time.strftime("%Y-%m-%d %H:%M", time.gmtime((CA.TS0 + (t + 1) * CA.MS) // 1000)), side]
                           + [f.get(k) for k in keys])
    print("wrote", a.out)
    with open(os.path.join(os.path.dirname(a.out), "compare_result.txt"), "w", newline="\n", encoding="utf-8") as fh:
        fh.write(f"points={len(rows_v)} mismatching_fields={len(bad)}\n")
        for k in sorted(bad):
            fh.write(f"{k}\t{bad[k]}\n")


if __name__ == "__main__":
    main()
