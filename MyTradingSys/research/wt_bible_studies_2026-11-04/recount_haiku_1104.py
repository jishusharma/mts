"""Blind recount (Card 1 event n, Card 3 cycles/week) from SPEC.md text only. DEV 2022-01-01..2024-06-30."""
import csv
import math
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from MyTradingSys.backtest.layers.wavetrend import wavetrend as W
from MyTradingSys.backtest import splits

ROOT = Path("F:/MTS/Dumps/backtest")
DEV0 = int(splits.DEV_START.timestamp() * 1000)
DEV1 = int(splits.DEV_END.timestamp() * 1000)
WARM = 400 * 86400 * 0 + 30 * 86400 * 1000  # 30 days of lead-in for EMA/warmup (WARMUP=200 bars)
TFMS = {"5m": 300000, "15m": 900000, "30m": 1800000, "1h": 3600000, "4h": 14400000}


def read_csv_dir(d, lo, hi):
    rows = {}
    for f in sorted(Path(d).glob("*.csv")):
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.reader(fh):
                if not r or not r[0].isdigit():
                    continue
                t = int(r[0])
                if t > 10**14:
                    t //= 1000
                if lo <= t < hi:
                    rows[t] = (t, float(r[2]), float(r[3]), float(r[4]))
    return [rows[k] for k in sorted(rows)]


def bars_for(tf):
    lo, hi = DEV0 - 40 * 86400000, DEV1
    if tf != "5m":
        return read_csv_dir(ROOT / "spot_2017" / "BTCUSDT" / tf / "klines", lo, hi)
    one = read_csv_dir(ROOT / "raw_1m_2022" / "klines", lo, hi)
    one += read_csv_dir(ROOT / "raw_1m_2019" / "klines", lo, hi)
    df = pd.DataFrame(one, columns=["t", "h", "l", "c"]).drop_duplicates("t").sort_values("t")
    df["g"] = df.t // 300000 * 300000
    g = df.groupby("g")
    # only complete 5-minute buckets (5 one-minute bars)
    out = pd.DataFrame({"h": g.h.max(), "l": g.l.min(), "c": g.c.last(), "n": g.t.count()})
    out = out[out.n == 5]
    return [(int(t), float(r.h), float(r.l), float(r.c)) for t, r in out.iterrows()]


def rows_for(tf):
    bars = bars_for(tf)
    rows = W.compute(bars, TFMS[tf])
    return bars, rows


def cycles(tf):
    bars, rows = rows_for(tf)
    dots, crosses = [], 0  # dots: (idx, 'B'/'T')
    for i, r in enumerate(rows):
        if r.event == 0 or not (DEV0 <= r.open_time < DEV1) or i == 0:
            continue
        crosses += 1
        p = rows[i - 1].wt1
        if math.isnan(p):
            continue
        if r.event == 1 and p <= -53:
            dots.append((i, "B"))
        elif r.event == -1 and p >= 53:
            dots.append((i, "T"))
    # cycle: valid bottom up-cross -> last valid top before the next bottom
    n_cyc, lens = 0, []
    start, last_top = None, None   # one pass over dots in time order; a bottom closes the open cycle
    for i, kind in dots:
        if kind == "B":
            if start is not None and last_top is not None:
                n_cyc += 1
                lens.append(last_top - start)
            start, last_top = i, None
        elif start is not None:
            last_top = i
    if start is not None and last_top is not None:
        n_cyc += 1
        lens.append(last_top - start)
    weeks = (DEV1 - DEV0) / 604800000
    return crosses, len(dots), n_cyc, n_cyc / weeks, (pd.Series(lens).median() if lens else None)


def card1():
    bars, rows = rows_for("30m")
    n = len(rows)
    t0 = [r.open_time for r in rows]
    cr = [i for i, r in enumerate(rows) if r.event != 0]
    downs = [i for i in cr if rows[i].event == -1]
    events, last_ev = [], -10**9
    for c in downs:
        if not (DEV0 <= t0[c] < DEV1):
            continue
        w1 = rows[c].wt1
        if not (0 <= w1 <= 53):
            continue
        if c - last_ev < 48:
            continue
        # earlier down-cross within 48 h (96 bars) with wt1 >= 45 and >= 10 higher
        found = None
        for e in reversed([d for d in downs if c - 96 <= d < c]):
            if rows[e].wt1 >= 45 and rows[e].wt1 >= w1 + 10:
                seg = [rows[j].wt1 for j in range(e, c + 1)]
                if min(seg) < 0:
                    found = e
                    break
        if found is None:
            continue
        e = found
        seg = range(e, c + 1)
        dip = min(seg, key=lambda j: rows[j].wt1)
        hi_after = max(bars[j][1] for j in range(dip, c + 1))
        hi_ref = max(bars[j][1] for j in range(max(0, e - 3), min(n, e + 4)))
        if hi_after > hi_ref:
            events.append(c)
            last_ev = c
    return len(events)


if __name__ == "__main__":
    print("card1_n", card1())
    for tf in TFMS:
        cr, nd, nc, cpw, med = cycles(tf)
        print(tf, "crosses", cr, "valid_dots", nd, "pct %.1f" % (100 * nd / cr), "cycles", nc, "per_week %.2f" % cpw, "median_len_bars", med)
