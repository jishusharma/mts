"""Counts-only power screen for session_range_transfer (no return, no outcome column read, no bar >= 2024-07-01).

H1: Asia range (00:00-07:00 UTC) -> first 15m close beyond it inside London 07:00-10:00 UTC.
H2: London range (07:00-13:00 UTC) -> first 15m close beyond it inside NY 13:00-16:00 UTC.
Stop = opposite range extreme (geometry only). Events with stop < 56 bp of entry are SKIPPED and counted.
Compression arm: range width <= 33rd percentile of the trailing 20 same-session widths (prior days only).
Reads only t_ms/open/high/low/close columns of F:/MTS/data_cache/binance/<SYM>_15m.npz (col order t,o,h,l,c,v).
"""
import csv, sys, os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "backtest"))
import fees  # noqa: E402  costs only from backtest/fees.py

RT_COST = 2 * fees.FEES_ALL_TAKER["entry"] + 2 * fees.SLIPPAGE_RT_S13  # 14 bp: taker 5+5 + slippage 2+2 (R1_EDGE_OR_STOP.md:37)

SYMS = "BTC ETH SOL BNB XRP ADA DOGE LINK LTC AVAX".split()
CACHE = os.environ.get("MTS_CACHE", "F:/MTS/data_cache/binance")
CUT = 1719792000000  # 2024-07-01T00:00Z; bars at or after are dropped
SPLIT = 1704067200000  # 2024-01-01
START = 1640995200000  # 2022-01-01
EXT = 1577836800000  # 2020-01-01 (DEV_EXT, OPERATOR_DECISIONS D3-dev-ext)
FLOOR = 0.0056  # 4 x 14 bp, FABLE_FEE_STOP_RULE
DAY = 86400000


def load(sym):
    a = np.load(f"{CACHE}/{sym}USDT_15m.npz")["a"][:, :5]
    a = a[a[:, 0] < CUT]
    assert a[:, 0].max() < CUT
    return a


def events(a, rs, re_, ws, we, comp):
    t = a[:, 0]; day = (t // DAY).astype(np.int64); hod = ((t % DAY) // 3600000).astype(float) + ((t % 3600000) / 3600000)
    out = []; widths = []
    for d in np.unique(day):
        m = day == d
        sel = m & (hod >= rs) & (hod < re_)
        if sel.sum() < int((re_ - rs) * 4):  # incomplete range window
            continue
        hi, lo = a[sel, 2].max(), a[sel, 3].min(); w = (hi - lo) / ((hi + lo) / 2)
        hist = widths[-20:]; widths.append(w)
        wsel = np.where(m & (hod >= ws) & (hod < we))[0]
        cond = len(hist) >= 20 and w <= np.percentile(hist, 33.3)
        if comp and not cond:
            continue
        for i in wsel:  # bar closes at open + 15m, entry on that close
            c = a[i, 4]
            if c > hi or c < lo:
                stop = (c - lo) / c if c > hi else (hi - c) / c
                out.append((int(d) * DAY, stop))
                break
    return out


def main():
    rows = []
    for name, spec in (("H1_asia_to_london", (0, 7, 7, 10)), ("H2_london_to_ny", (7, 13, 13, 16))):
        for comp in (False, True):
            cache = {sy: events(load(sy), *spec, comp) for sy in SYMS}
            for sw, lo_, hi_ in (("DEV_EXT", EXT, START), ("DEV", START, SPLIT), ("DEV+DEV_EXT", EXT, SPLIT), ("VAL", SPLIT, CUT)):
                ev_all = []; per = {}
                for sy in SYMS:
                    e = [x for x in cache[sy] if lo_ <= x[0] < hi_]
                    per[sy] = len(e); ev_all += e
                kept = [x for x in ev_all if x[1] >= FLOOR]
                days = len({x[0] for x in kept})
                cost_r = float(np.mean([RT_COST / x[1] for x in kept])) if kept else float("nan")
                rows.append([name, "compress" if comp else "all", sw, len(ev_all), len(ev_all) - len(kept), len(kept), days,
                             round(float(np.mean([x[1] for x in kept])) * 100, 2) if kept else "", round(cost_r, 4), per])
                print(rows[-1], flush=True)
    with open(os.path.join(os.path.dirname(__file__), "COUNTS.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow("hyp arm split events skipped_lt56bp kept distinct_days mean_stop_pct cost_R per_symbol".split()); w.writerows(rows)


if __name__ == "__main__":
    main()
