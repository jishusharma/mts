"""Java vs Python prior-day zone check (counts and price levels only, no outcome; DEV days only).

Java side: the UNCHANGED `buildVp` of src/main/java/datafeed/MarketDataSnapshot.java, compiled by
MyTradingSys/backtest/tom_profile_parity.py (EngineProfile) and run on the prior UTC day's 1m bars, as the live
zone builder does for daily_vp (dynamic grid, bins ~5 USDT). Python side: vp_pivot_probe.build_profile (w = 10 USDT), the
builder every research study reads. They are different grids, so exact equality is not expected:
  match(level) = |java - python| <= max(java_bin, W) with java_bin = range / max(50, int(range / 5)) (the Java rule).
  python java_zone_check.py [--every N] [--out zone_check.csv]
"""
import argparse
import csv
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import level_ledger as LL  # noqa: E402  (sets sys.path for the repo and pit_levels)

W = 10.0
LEVELS = (("poc", "poc_price"), ("vah", "vah"), ("val", "val"))


def java_bin(lo, hi):
    rng = hi - lo
    return rng / max(50, int(rng / 5))


def compare(java, py, lo, hi):
    """Per-level (abs_diff, matched) for poc/vah/val; tolerance max(java bin, W)."""
    tol = max(java_bin(lo, hi), W)
    out = {}
    for jk, pk in LEVELS:
        d = abs(float(java[jk]) - float(py[pk]))
        out[jk] = (d, d <= tol)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--every", type=int, default=19)
    ap.add_argument("--out", default=str(HERE / "ZONE_CHECK.csv"))
    a = ap.parse_args(argv)
    import count_prior_va as C
    from MyTradingSys.backtest.vp_pivot_probe import build_profile
    from MyTradingSys.backtest.tom_profile_parity import EngineProfile
    A, _ = C.load_dev()
    rows, tot, hit = [], 0, 0
    with EngineProfile() as eng:
        for d in range(0, C.NDAYS, a.every):
            s = slice(d * 1440, (d + 1) * 1440)
            if np.isnan(A["L"][s]).sum() > LL.MAX_MISSING:
                continue
            ok = ~np.isnan(A["L"][s])
            t0 = LL.TS0 + d * LL.DAY_MS
            bars = [[int(t0 + int(i) * LL.MIN_MS)] + [float(A[k][d * 1440 + i]) for k in ("O", "H", "L", "C", "V")]
                    for i in np.nonzero(ok)[0]]
            jv = eng.profile(bars)
            py = build_profile(A["L"][s], A["H"][s], A["V"][s], W)
            if jv is None or py is None:
                continue
            cmp = compare(jv, py, float(np.nanmin(A["L"][s])), float(np.nanmax(A["H"][s])))
            for k, (diff, m) in cmp.items():
                tot += 1
                hit += m
            rows.append({"day": d, "date_ms": t0, **{f"{k}_diff": round(v[0], 4) for k, v in cmp.items()},
                         **{f"{k}_match": int(v[1]) for k, v in cmp.items()}})
    with open(a.out, "w", newline="\n", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    pct = 100.0 * hit / tot if tot else float("nan")
    print(f"days {len(rows)}; levels {tot}; matched {hit}; match {pct:.1f}% (tolerance max(java bin, {W}))")
    return pct


if __name__ == "__main__":
    main()
