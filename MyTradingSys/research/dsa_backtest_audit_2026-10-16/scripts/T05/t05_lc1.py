"""T05 / lead L8: LC1 level-hold rates against a FAIR random-line null.  python t05_lc1.py   (run from the repo root)

Published control (levels_hold.py:78-93): midnight +/- the same distance with a random sign (half the 'controls' ARE the real
level), and a control line that is never touched counts as NEITHER (a non-hold) in the denominator.
Fair control (this file): for every candidate level of a family, K=20 random lines whose distance from the midnight open is
drawn from that family's own distances in the same calendar month (so the distance distribution is matched without re-using the
level itself), sign random, and a line counts ONLY when touched, exactly like a real level (hold rate = holds / touches).
Window: standard DEV decisions 2022-04-01..2024-06-30 (the LC1 Q79 re-run window, levels_hold.md Q79 addendum). The footprint
window 2024-12..2025-03 lies inside VALIDATION and is NOT read (DECISION (OURS) D1 in the report), so no exposure row.
Seed printed. Outputs out/lc1_fair.csv, out/lc1_orig_reproduction.csv."""
import csv
import datetime as dt
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]                                   # repo root
RES = ROOT / "MyTradingSys" / "research"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RES / "levels_confluence_2026-10-14"))
from levels import levels_by_day  # noqa: E402
import levels_hold as LH  # noqa: E402
from MyTradingSys.backtest.bt.bt_data import load_klines  # noqa: E402

SEED = 20261016
K_LINES = 20
N_BOOT = 2000
START = int(dt.datetime(2022, 3, 21, tzinfo=dt.timezone.utc).timestamp() * 1000)
DEC0 = int(dt.datetime(2022, 4, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
END = int(dt.datetime(2024, 7, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)


def month_of(day):
    d = dt.date(1970, 1, 1) + dt.timedelta(days=int(day))
    return d.year * 12 + d.month


def boot_ci(days, seed):
    """days: dict day -> (real_hold, real_n, ctl_hold, ctl_n). Ratio-of-sums bootstrap over days."""
    keys = sorted(days)
    arr = np.array([days[k] for k in keys], float)
    rng = np.random.default_rng(seed)
    pick = rng.integers(0, len(keys), (N_BOOT, len(keys)))
    s = arr[pick].sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        diff = s[:, 0] / s[:, 1] - s[:, 2] / s[:, 3]
    diff = diff[~np.isnan(diff)]
    return float(np.quantile(diff, 0.025)), float(np.quantile(diff, 0.975))


def windowed_levels(bars):
    """levels_by_day is quadratic in history (all_before over every earlier bar). Each day only reads the prior 14 days (prior week,
    10-day naked POC, 4h fractals from d-10), so build each decision day from a 14-day window; same function, same rows."""
    byday = defaultdict(list)
    for b in bars:
        byday[int(b["t"]) // LH.DAY_MS].append(b)
    out = {}
    for d in sorted(byday):
        if d * LH.DAY_MS < DEC0:
            continue
        win = [b for k in range(d - 14, d + 1) for b in byday.get(k, [])]
        out[d] = levels_by_day(win).get(d, [])
    return out


def main():
    print(f"T05 LC1 fair null SEED={SEED} K_LINES={K_LINES} boot={N_BOOT}", flush=True)
    bars = load_klines("F:/MTS/data/tom_raw", start_ms=START, end_ms=END)
    assert max(b["t"] for b in bars) < END
    levels = windowed_levels(bars)
    dev = [b for b in bars if b["t"] >= DEC0]
    assert min(b["t"] for b in dev) >= DEC0 and max(b["t"] for b in dev) < END
    print("bars", len(bars), "dev bars", len(dev), flush=True)

    # ---- reproduction of the published (Q79 DEV) run
    res = LH.analyze(dev, levels)
    fams = res["families"]
    with open(HERE / "out" / "lc1_orig_reproduction.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["family", "n", "hold", "random_hold", "diff", "ci_lo", "ci_hi", "verdict"])
        for f, r in sorted(fams.items()):
            w.writerow([f, r["n"], f"{r['hold_rate']:.4f}", f"{r['random_hold_rate']:.4f}", f"{r['difference']:.4f}",
                        f"{r['ci95'][0]:.4f}", f"{r['ci95'][1]:.4f}", r["verdict"]])
    print("published run reproduced:", {f: (r["n"], round(r["hold_rate"], 3), round(r["random_hold_rate"], 3), r["verdict"])
                                         for f, r in fams.items()}, flush=True)

    # ---- fair null
    by_day = defaultdict(list)
    for b in dev:
        by_day[int(b["t"]) // LH.DAY_MS].append(b)
    for rows in by_day.values():
        rows.sort(key=lambda b: b["t"])
    # distance pools: family x calendar month, from ALL candidate levels (touched or not)
    pool = defaultdict(list)
    for day, rows in by_day.items():
        mid = float(rows[0]["o"])
        for lv in levels.get(day, []):
            pool[(lv["family"], month_of(day))].append(abs(float(lv["price"]) - mid))
    rng = random.Random(SEED)
    acc = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0]))     # family -> day -> real_h, real_n, ctl_h, ctl_n
    orig_touch = defaultdict(lambda: [0, 0, 0])                       # family -> [orig-style lines drawn, untouched, equal to real]
    for day in sorted(by_day):
        rows = by_day[day]
        mid = float(rows[0]["o"])
        lo = np.array([float(b["l"]) for b in rows])
        hi = np.array([float(b["h"]) for b in rows])
        for lv in levels.get(day, []):
            fam = lv["family"]
            price = float(lv["price"])
            ps = pool[(fam, month_of(day))]

            def one(p):
                idx = np.nonzero((lo <= p) & (p <= hi))[0]
                if len(idx) == 0:
                    return None
                i = int(idx[0])
                return LH.outcome(rows[i:], p, LH.stop_width(mid, p), LH._prev_close(rows, i))

            real = one(price)
            for _ in range(K_LINES):
                dist = ps[rng.randrange(len(ps))]
                p = mid + (-1 if rng.random() < .5 else 1) * dist
                r = one(p)
                if r is not None:
                    acc[fam][day][2] += int(r == "HOLD")
                    acc[fam][day][3] += 1
            if real is not None:
                acc[fam][day][0] += int(real == "HOLD")
                acc[fam][day][1] += 1
            # share of the published-style control that is the real level itself / never touched
            o = orig_touch[fam]
            o[0] += 1
            dist = abs(price - mid)
            for _ in range(5):
                sign = -1 if rng.random() < .5 else 1
                pp = mid + sign * dist
                o[2] += int(abs(pp - price) < 1e-9)
                o[1] += int(one(pp) is None)
    out = []
    for fam in sorted(acc):
        d = acc[fam]
        rh = sum(v[0] for v in d.values()); rn = sum(v[1] for v in d.values())
        ch = sum(v[2] for v in d.values()); cn = sum(v[3] for v in d.values())
        lo_, hi_ = boot_ci(d, SEED)
        o = orig_touch[fam]
        pub = fams.get(fam)
        out.append(dict(family=fam, n_touch=rn, hold=rh / rn, fair_ctl_touches=cn, fair_ctl_hold=ch / cn, diff=rh / rn - ch / cn,
                        ci_lo=lo_, ci_hi=hi_, verdict="KEEP" if lo_ > 0 else "DROP",
                        pub_hold=pub["hold_rate"] if pub else float("nan"), pub_random=pub["random_hold_rate"] if pub else float("nan"),
                        pub_diff=pub["difference"] if pub else float("nan"), pub_verdict=pub["verdict"] if pub else "",
                        orig_ctl_equal_real_share=o[2] / (5 * o[0]), orig_ctl_untouched_share=o[1] / (5 * o[0])))
    with open(HERE / "out" / "lc1_fair.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    for r in out:
        print(r["family"], r["n_touch"], f"{r['hold']:.3f}", f"fair {r['fair_ctl_hold']:.3f} diff {r['diff']:+.3f} "
              f"[{r['ci_lo']:+.3f},{r['ci_hi']:+.3f}] {r['verdict']} (pub {r['pub_verdict']} {r['pub_diff']:+.3f}) "
              f"eq={r['orig_ctl_equal_real_share']:.2f} untouched={r['orig_ctl_untouched_share']:.2f}", flush=True)


if __name__ == "__main__":
    main()
