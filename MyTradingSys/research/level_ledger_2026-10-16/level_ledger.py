"""Point-in-time level ledger (PIT_CONTRACT.md section 1), minimal version: the prior-day levels the studies read.

One row per level instance: prior_day_h / l / poc / vah / val of each completed UTC day, BTCUSDT 1m, DEV only
(bar open 2022-01-01 .. 2024-06-30; the loader refuses any later bar). A row is available at the NEXT UTC midnight
(period end), never earlier; formed_at is the open of the last bar the level uses. Counts and prices only, no outcome.
  python level_ledger.py [out.csv]
"""
import csv
import hashlib
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE.parent / "pit_levels_2026-10-16"))

MIN_MS, DAY_MS = 60_000, 86_400_000
TS0 = 1640995200000          # 2022-01-01 00:00 UTC
MAX_MISSING = 5              # same day skip as count_prior_va.py:141
ORIGINS = ("prior_day_h", "prior_day_l", "prior_day_poc", "prior_day_vah", "prior_day_val")
FIELDS = ("level_id", "origin", "source_tf", "price", "zone_lo", "zone_hi", "formed_at", "available_at",
          "algo_version", "used_by")
USED_BY = ("pit_levels_2026-10-16/count_prior_va.py:130-143; context_factors_2026-10-16/context_asof.py pd_va "
           "(5m bars, CONTEXT_FACTORS_SPEC.md:35)")


def algo_version():
    from MyTradingSys.backtest import vp_pivot_probe
    return "vp_pivot_probe.build_profile w=10 sha256:" + hashlib.sha256(Path(vp_pivot_probe.__file__).read_bytes()).hexdigest()[:12]


def day_rows(day, o_ms, lows, highs, vols, build_profile, version):
    """Ledger rows of the completed UTC day `day` (index from TS0). Arrays are that day's 1m bars (nan = missing).
    Returns [] for a day with more than MAX_MISSING missing minutes or no profile."""
    if np.isnan(lows).sum() > MAX_MISSING:
        return []
    prof = build_profile(lows, highs, vols)
    if not prof:
        return []
    ok = ~np.isnan(lows)
    formed = o_ms + int(np.nonzero(ok)[0].max()) * MIN_MS
    avail = o_ms + DAY_MS
    vals = {"prior_day_h": float(np.nanmax(highs)), "prior_day_l": float(np.nanmin(lows)),
            "prior_day_poc": float(prof["poc_price"]), "prior_day_vah": float(prof["vah"]),
            "prior_day_val": float(prof["val"])}
    rows = []
    for origin in ORIGINS:
        p = vals[origin]
        rows.append({"level_id": f"{origin}:1m:{formed}", "origin": origin, "source_tf": "1m", "price": p,
                     "zone_lo": p, "zone_hi": p, "formed_at": formed, "available_at": avail,
                     "algo_version": version, "used_by": USED_BY})
    return rows


def build(A, ndays, build_profile, version):
    rows = []
    for d in range(ndays):
        s = slice(d * 1440, (d + 1) * 1440)
        rows += day_rows(d, TS0 + d * DAY_MS, A["L"][s], A["H"][s], A["V"][s], build_profile, version)
    return rows


def readable(rows, decision_ms):
    """Rows a reader may use at decision_ms: available_at <= decision_ms."""
    return [r for r in rows if r["available_at"] <= decision_ms]


def main(argv):
    import count_prior_va as C
    from MyTradingSys.backtest.vp_pivot_probe import build_profile
    A, missing = C.load_dev()
    rows = build(A, C.NDAYS, lambda l, h, v: build_profile(l, h, v, C.W), algo_version())
    out = Path(argv[0]) if argv else HERE / "LEVEL_LEDGER.csv"
    with out.open("w", newline="\n", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    days = len({r["available_at"] for r in rows})
    print(f"missing month files: {missing}")
    print(f"ledger: {len(rows)} levels over {days} days -> {out}")
    return len(rows)


if __name__ == "__main__":
    main(sys.argv[1:])
