"""Re-state the LC1 KEEP list on the fair control. python levels_hold_fair_run.py  (from the repo root)
Standard DEV decisions 2022-04-01..2024-06-30, seed bars from 2022-03-21, end asserted < 2024-07-01 (no VALIDATION/HOLDOUT read).
Writes lc1_fair_dev.csv next to this file; compare with dsa_backtest_audit_2026-10-16/scripts/T05/out/lc1_fair.csv."""
import csv
import datetime as dt
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
from levels import levels_by_day  # noqa: E402
import levels_hold as LH  # noqa: E402
from MyTradingSys.backtest.bt.bt_data import load_klines  # noqa: E402

UTC = dt.timezone.utc
START = int(dt.datetime(2022, 3, 21, tzinfo=UTC).timestamp() * 1000)
DEC0 = int(dt.datetime(2022, 4, 1, tzinfo=UTC).timestamp() * 1000)
END = int(dt.datetime(2024, 7, 1, tzinfo=UTC).timestamp() * 1000)


def windowed_levels(bars):
    """Each decision day reads only the prior 14 days (same rows as the full-history builder, linear instead of quadratic)."""
    byday = defaultdict(list)
    for b in bars:
        byday[int(b['t']) // LH.DAY_MS].append(b)
    out = {}
    for d in sorted(byday):
        if d * LH.DAY_MS < DEC0:
            continue
        win = [b for k in range(d - 14, d + 1) for b in byday.get(k, [])]
        out[d] = levels_by_day(win).get(d, [])
    return out


def main():
    bars = load_klines("F:/MTS/data/tom_raw", start_ms=START, end_ms=END)
    assert max(b["t"] for b in bars) < END
    levels = windowed_levels(bars)
    dev = [b for b in bars if b["t"] >= DEC0]
    assert min(b["t"] for b in dev) >= DEC0 and max(b["t"] for b in dev) < END
    fams = LH.analyze(dev, levels)["families"]
    cols = ["family", "n_touch", "hold", "fair_ctl_touches", "fair_ctl_hold", "diff", "ci_lo", "ci_hi", "verdict",
            "legacy_ctl_hold", "legacy_diff", "legacy_verdict", "legacy_ctl_equal_real_share", "legacy_ctl_untouched_share",
            "fair_ctl_equal_real_share"]
    with open(HERE / "lc1_fair_dev.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for f, r in sorted(fams.items()):
            w.writerow([f, r["n"], r["hold_rate"], r["fair_control_touches"], r["random_hold_rate"], r["difference"],
                        r["ci95"][0], r["ci95"][1], r["verdict"], r["legacy_random_hold_rate"], r["legacy_difference"],
                        r["legacy_verdict"], r["legacy_equal_real_share"], r["legacy_untouched_share"],
                        r["fair_equal_real_share"]])
            print(f, r["n"], f"{r['hold_rate']:.3f} fair {r['random_hold_rate']:.3f} diff {r['difference']:+.4f} "
                  f"[{r['ci95'][0]:+.4f},{r['ci95'][1]:+.4f}] {r['verdict']} legacy {r['legacy_verdict']} "
                  f"fair_eq={r['fair_equal_real_share']:.4f}", flush=True)


if __name__ == "__main__":
    main()
