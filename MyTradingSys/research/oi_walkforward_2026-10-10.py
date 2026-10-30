import sys
sys.dont_write_bytecode = True

import csv
import glob
import os
import statistics
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

ROOT = Path(r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed")
KLINES = ROOT / "Dumps" / "backtest" / "raw" / "klines"
METRICS = ROOT / "Dumps" / "backtest" / "raw" / "metrics"
OUT = ROOT / "MyTradingSys" / "research" / "OI_WALKFORWARD_2026-10-10.md"

BAR_MS = 15 * 60 * 1000
HORIZONS = [4, 8, 16]
TRAIN_FRAC = 0.6
THRESH_PCT = 0.25


def load_metrics():
    by_ts = {}
    for f in sorted(METRICS.glob("*.csv")):
        with open(f, newline="", encoding="utf-8") as fh:
            r = csv.DictReader(fh)
            for row in r:
                ts = row["create_time"].strip()
                dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                ms = int(dt.timestamp() * 1000)
                try:
                    oi = float(row["sum_open_interest"])
                except Exception:
                    continue
                by_ts[ms] = oi
    ts_sorted = sorted(by_ts.keys())
    return by_ts, ts_sorted


def nearest_oi(by_ts, ts_sorted, target_ms):
    lo, hi, best = 0, len(ts_sorted) - 1, None
    while lo <= hi:
        mid = (lo + hi) // 2
        if ts_sorted[mid] <= target_ms:
            best = ts_sorted[mid]; lo = mid + 1
        else:
            hi = mid - 1
    return by_ts.get(best) if best is not None else None


def load_klines_15m():
    bars = {}
    for f in sorted(KLINES.glob("*.csv")):
        with open(f, newline="", encoding="utf-8") as fh:
            r = csv.reader(fh)
            header = next(r, None)
            if header is None: continue
            for row in r:
                try:
                    t = int(row[0]); o = float(row[1]); h = float(row[2]); l = float(row[3]); c = float(row[4])
                    v = float(row[5]); tbv = float(row[9])
                except Exception:
                    continue
                bucket = (t // BAR_MS) * BAR_MS
                b = bars.get(bucket)
                if b is None:
                    bars[bucket] = {"o": o, "h": h, "l": l, "c": c, "v": v, "tbv": tbv}
                else:
                    if h > b["h"]: b["h"] = h
                    if l < b["l"]: b["l"] = l
                    b["c"] = c
                    b["v"] += v
                    b["tbv"] += tbv
    return bars


def main():
    print("loading metrics...")
    oi_by_ts, oi_ts = load_metrics()
    print("metrics rows={0} range={1}..{2}".format(len(oi_ts), oi_ts[0] if oi_ts else None, oi_ts[-1] if oi_ts else None))
    print("loading klines...")
    bars = load_klines_15m()
    bar_ts = sorted(bars.keys())
    print("bars={0} range={1}..{2}".format(len(bar_ts), bar_ts[0] if bar_ts else None, bar_ts[-1] if bar_ts else None))

    starts = [t for t in bar_ts if t >= (oi_ts[0] if oi_ts else 0) and t + BAR_MS*20 <= (oi_ts[-1] if oi_ts else 0)]
    print("aligned bars={0}".format(len(starts)))

    events = []
    for t in starts:
        b = bars[t]
        oi_now = nearest_oi(oi_by_ts, oi_ts, t)
        oi_ago = nearest_oi(oi_by_ts, oi_ts, t - 60 * 60 * 1000)
        if oi_now is None or oi_ago is None or oi_ago == 0: continue
        price_prev = bars.get(t - 60 * 60 * 1000)
        if price_prev is None: continue
        price_pct = (b["c"] - price_prev["c"]) / price_prev["c"] * 100.0
        oi_pct = (oi_now - oi_ago) / oi_ago * 100.0
        taker_ratio = (b["tbv"] / b["v"]) if b["v"] > 0 else 0.5
        sig = None
        if price_pct > THRESH_PCT and oi_pct < 0 and taker_ratio < 0.5:
            sig = "short"
        elif price_pct < -THRESH_PCT and oi_pct > 0 and taker_ratio > 0.5:
            sig = "long"
        if sig:
            idx = bar_ts.index(t)
            fwd = {}
            for h in HORIZONS:
                if idx + h < len(bar_ts):
                    fut = bars[bar_ts[idx + h]]["c"]
                    fwd[h] = (fut - b["c"]) / b["c"] * 100.0
            if len(fwd) == len(HORIZONS):
                events.append({"ts": t, "sig": sig, "price_pct": price_pct, "oi_pct": oi_pct, "tbv_ratio": taker_ratio, "fwd": fwd})
    print("events={0}".format(len(events)))
    if not events:
        print("no events"); return

    events.sort(key=lambda e: e["ts"])
    split_idx = int(len(events) * TRAIN_FRAC)
    train = events[:split_idx]; test = events[split_idx:]
    print("train={0} test={1}".format(len(train), len(test)))

    def stats(evs):
        r = {}
        for s in ["long", "short"]:
            sub = [e for e in evs if e["sig"] == s]
            r[s] = {}
            for h in HORIZONS:
                vals = [e["fwd"][h] for e in sub]
                if not vals: r[s][h] = (0, 0.0, 0.0); continue
                m = statistics.mean(vals)
                sd = statistics.pstdev(vals) if len(vals) > 1 else 0.0
                r[s][h] = (len(vals), m, sd)
        return r

    tr = stats(train); te = stats(test)

    out = []
    out.append("# OI Divergence Walk-Forward - 2026-10-10")
    out.append("")
    out.append("Method: 15-minute bars built from 1m klines. OI from Binance metrics 5-min snapshots (sum_open_interest).")
    out.append("Taker buy/sell ratio from kline taker_buy_volume / volume.")
    out.append("")
    out.append("Signal short: 1h price change > +{0}% AND 1h OI change < 0 AND taker_buy_ratio < 0.5".format(THRESH_PCT))
    out.append("Signal long:  1h price change < -{0}% AND 1h OI change > 0 AND taker_buy_ratio > 0.5".format(THRESH_PCT))
    out.append("Horizons: 4, 8, 16 bars of 15m = 1h, 2h, 4h.")
    out.append("Split: first {0}% of events train, rest test.".format(int(TRAIN_FRAC*100)))
    out.append("")
    out.append("Events: {0} total, {1} train, {2} test".format(len(events), len(train), len(test)))
    out.append("")
    for name, st in [("TRAIN", tr), ("TEST", te)]:
        out.append("## {0}".format(name))
        out.append("")
        out.append("| signal | horizon | n | mean pct | sd |")
        out.append("|---|---|---|---|---|")
        for s in ["long", "short"]:
            for h in HORIZONS:
                n, m, sd = st[s][h]
                out.append("| {0} | {1} | {2} | {3:+.4f} | {4:.4f} |".format(s, h, n, m, sd))
        out.append("")
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("wrote " + str(OUT))


if __name__ == "__main__":
    main()