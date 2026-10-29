"""Measurement only (no engine edit): how often a stop exit meets a gap-through bar, and the R the stop-price fill understates.

Gap-through = the bar's open is beyond the stop in force (long: o < stop; short: o > stop). Understatement for one such exit
= |stop - open| / D (R), the loss a fill AT THE STOP hides versus a fill at the open. Hand check: stop 99.00, open 98.01,
D 1.00 -> 0.99 R (FILL_CANARY plant).
Stop exits are produced by the real v3 walk (MyTradingSys/backtest/layers/fabio/v3/manage.py walk_trade, unedited).
where = "post_fill": gap on a bar after the fill bar (v3 already exits at the open, manage.py:141-143; sim.py --stops ideal
fills at the stop, sim.py:77); "fill_bar": gap on the fill bar (v3 fills at the stop, manage.py:140-141: the F scenario).
Run: python MyTradingSys/research/dsa_backtest_audit_2026-10-16/fill_gap_frequency.py [--write]
"""
import argparse
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest.layers.fabio.v3 import manage as _manage  # noqa: E402
from MyTradingSys.backtest.layers.fabio.v3.manage import walk_trade  # noqa: E402

DEV_START_MS = 1640995200000   # 2022-01-01 00:00 UTC
DEV_END_MS = 1719791999999     # 2024-06-30 23:59:59.999 UTC
SPOT_DIR = Path("F:/MTS/data/bigtrade/spot_raw")
HORIZON = 1440   # OURS: a trade still open after 1 day exits window_end and is not a stop exit
OF_DIR = Path("F:/MTS/data/orderflow_1m")


def pctl(xs, p):
    """Nearest-rank percentile: the ceil(p/100*n)-th smallest value."""
    s = sorted(xs)
    return s[max(1, math.ceil(p / 100.0 * len(s))) - 1]


def stop_exit_records(bars, entries):
    """entries = (fill_idx, side, entry, D, stop). One record per trade that ends on a stop (reason stop/be/trail/opp/own)."""
    out = []
    saved = _manage.exhaustion
    _manage.exhaustion = lambda *a, **k: False   # S8 needs order-flow fields plain OHLC bars lack: runtime switch-off, no file edit
    try:
        return _records(bars, entries, out)
    finally:
        _manage.exhaustion = saved


def _records(bars, entries, out):
    for fill_idx, s, entry, D, stop in entries:
        w = walk_trade(bars, fill_idx, s, entry, D, stop, target=None, force_close=True,
                       end_idx=fill_idx + HORIZON)
        if w["status"] != "closed" or w["reason"] in ("window_end", "target", "s8"):
            continue
        i, st = w["exit_idx"], w["stop"]
        o = bars[i]["o"]
        gap = (s > 0 and o < st) or (s < 0 and o > st)
        out.append({"fill_idx": fill_idx, "exit_idx": i, "side": s, "stop": st, "open": o, "gap": gap,
                    "where": "fill_bar" if i == fill_idx else "post_fill",
                    "under_r": abs(st - o) / D if gap else 0.0})
    return out


def summarize(recs):
    g = [r["under_r"] for r in recs if r["gap"]]
    n = len(recs)
    return {"n_stop": n, "n_gap": len(g), "share": (len(g) / n) if n else float("nan"),
            "mean_r": (sum(g) / len(g)) if g else 0.0, "p95_r": pctl(g, 95) if g else 0.0,
            "mean_r_all_stops": (sum(g) / n) if n else float("nan")}


def load_spot_dev():
    bars = []
    for p in sorted(SPOT_DIR.glob("BTCUSDT-1m-????-??.csv")):
        for line in p.open():
            f = line.split(",")
            t = int(f[0])
            if t > 10 ** 14:
                t //= 1000   # microsecond timestamps in newer Binance dumps
            if DEV_START_MS <= t <= DEV_END_MS:
                bars.append({"t": t, "o": float(f[1]), "h": float(f[2]), "l": float(f[3]), "c": float(f[4])})
    return bars


def proxy_entries(bars, every=240, d_pct=0.003):
    """OURS proxy (no v3 signal data on DEV): a resting limit at the previous close every `every` bars, both sides, stop
    d_pct (0.3 percent, v3 cell f0.003) away; filled on the first later bar that touches the limit (fill bar = that bar)."""
    ents = []
    n = len(bars)
    for k in range(0, n - 2, every):
        e = bars[k]["c"]
        D = e * d_pct
        for s in (1, -1):
            j = k + 1
            if (s > 0 and bars[j]["l"] <= e) or (s < 0 and bars[j]["h"] >= e):
                ents.append((j, s, e, D, e - s * D))
    return ents


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    of_dev = [p.name for p in OF_DIR.glob("????-??-??.csv.gz") if p.name[:10] <= "2024-06-30"]
    print("v3 order-flow bars inside DEV: %d day files (first file %s)" % (
        len(of_dev), min((p.name for p in OF_DIR.glob("????-??-??.csv.gz")), default="none")))
    bars = load_spot_dev()
    ents = proxy_entries(bars)
    recs = stop_exit_records(bars, ents)
    res = {"bars": len(bars), "entries": len(ents), "all": summarize(recs)}
    for wh in ("post_fill", "fill_bar"):
        res[wh] = summarize([r for r in recs if r["where"] == wh])
    print(res)
    return res


if __name__ == "__main__":
    main()
