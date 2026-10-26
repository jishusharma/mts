# T01-F2: raw_1d is a distinct snapshot, NOT the 1m resample (905 of 912 DEV days differ on open, 847 on volume, max 12.01%); derive daily bars from 1m for new work. See MyTradingSys/research/dsa_backtest_audit_2026-10-16/T01_data_forensics.md
import sys
sys.dont_write_bytecode = True
import csv
import statistics
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
from bisect import bisect_right
from math import sqrt

ROOT = Path(r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed")
sys.path.insert(0, str(ROOT))
from MyTradingSys.backtest.layers.positioning.trade_costs import net_return

KLINES = ROOT / "Dumps" / "backtest" / "raw" / "klines"
METRICS = ROOT / "Dumps" / "backtest" / "raw" / "metrics"
FUNDING = ROOT / "Dumps" / "backtest" / "raw" / "fundingRate"
KLINES_1D = ROOT / "Dumps" / "backtest" / "raw_1d" / "klines"
OUT = ROOT / "MyTradingSys" / "research" / "_archive" / "loose_2026-10" / "OI_DIVERGENCE_V2_2026-10-10.md"
BAR_MS = 15 * 60 * 1000
HORIZONS = [4, 8, 16]
PRICE_THRESH = 0.25
FEE_RT = 0.0010
SLIP_RT = 0.0002
EMBARGO_BARS = 96


def load_metrics():
    by_ts = {}
    for f in sorted(METRICS.glob("*.csv")):
        with open(f, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                try:
                    dt = datetime.strptime(row["create_time"].strip(), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                    ms = int(dt.timestamp() * 1000)
                    oi = float(row["sum_open_interest"])
                except Exception:
                    continue
                by_ts[ms] = oi
    ts = sorted(by_ts.keys())
    return by_ts, ts


def load_klines_15m():
    bars = {}
    for f in sorted(KLINES.glob("*.csv")):
        with open(f, newline="", encoding="utf-8") as fh:
            r = csv.reader(fh); next(r, None)
            for row in r:
                try:
                    t = int(row[0]); o = float(row[1]); h = float(row[2]); l = float(row[3]); c = float(row[4])
                    v = float(row[5]); tbv = float(row[9])
                except Exception:
                    continue
                b = (t // BAR_MS) * BAR_MS
                x = bars.get(b)
                if x is None:
                    bars[b] = {"o": o, "h": h, "l": l, "c": c, "v": v, "tbv": tbv}
                else:
                    if h > x["h"]: x["h"] = h
                    if l < x["l"]: x["l"] = l
                    x["c"] = c; x["v"] += v; x["tbv"] += tbv
    return bars


def load_funding():
    recs = []
    for f in sorted(FUNDING.glob("*.csv")):
        with open(f, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                try:
                    recs.append((int(row["calc_time"]), float(row["last_funding_rate"])))
                except Exception:
                    continue
    recs.sort(key=lambda x: x[0])
    return recs


def load_daily_regimes():
    bars = {}
    for f in sorted(KLINES_1D.glob("*.csv")):
        with open(f, newline="", encoding="utf-8") as fh:
            r = csv.reader(fh); next(r, None)
            for row in r:
                try:
                    t = int(row[0]); c = float(row[4])
                except Exception:
                    continue
                bars[t] = c
    ts = sorted(bars.keys())
    sma = {}
    for i in range(len(ts)):
        if i < 199: continue
        window = [bars[ts[j]] for j in range(i-199, i+1)]
        sma[ts[i]] = sum(window) / 200.0
    regime = {}
    for i in range(len(ts)):
        t = ts[i]
        if t not in sma or i < 220: continue
        prior = ts[i-20]
        if prior not in sma: continue
        c = bars[t]
        s = sma[t]; s_prev = sma[prior]
        if c > s and s > s_prev: regime[t] = "trend_up"
        elif c < s and s < s_prev: regime[t] = "trend_down"
        else: regime[t] = "range"
    return regime, ts


def nearest(ts_sorted, target):
    lo, hi, best = 0, len(ts_sorted)-1, None
    while lo <= hi:
        mid = (lo + hi) // 2
        if ts_sorted[mid] <= target:
            best = ts_sorted[mid]; lo = mid + 1
        else:
            hi = mid - 1
    return best


def day_regime_for(bar_ms, regime, dts):
    day_ms = (bar_ms // (24*60*60*1000)) * (24*60*60*1000)
    prior = day_ms - 24*60*60*1000
    dt = nearest(dts, prior)
    if dt is None: return "unknown"
    return regime.get(dt, "unknown")

def main():
    print("loading metrics...")
    oi_by_ts, oi_ts = load_metrics()
    print("oi records={0} span={1}..{2}".format(len(oi_ts), oi_ts[0] if oi_ts else 0, oi_ts[-1] if oi_ts else 0))
    print("loading klines...")
    bars = load_klines_15m()
    bar_ts = sorted(bars.keys())
    print("bars={0} span={1}..{2}".format(len(bar_ts), bar_ts[0] if bar_ts else 0, bar_ts[-1] if bar_ts else 0))
    print("loading funding...")
    funding = load_funding()
    print("funding records={0} span={1}..{2}".format(len(funding), funding[0][0] if funding else 0, funding[-1][0] if funding else 0))
    print("loading daily regimes...")
    regime, dts = load_daily_regimes()
    print("regime days={0}".format(len(regime)))

    oi_lo = oi_ts[0] if oi_ts else 0
    oi_hi = oi_ts[-1] if oi_ts else 0
    f_lo = funding[0][0] if funding else 0
    f_hi = funding[-1][0] if funding else 0

    events = []
    skipped_oi = 0
    skipped_fund = 0
    for t in bar_ts:
        if t < oi_lo or t + BAR_MS * (max(HORIZONS)+1) > oi_hi:
            continue
        i = bar_ts.index(t)
        if i < 4: continue
        p_now = bars[t]["c"]
        p_ago = bars[bar_ts[i-4]]["c"]
        oi_now = oi_by_ts.get(nearest(oi_ts, t))
        oi_ago = oi_by_ts.get(nearest(oi_ts, t - 60*60*1000))
        if oi_now is None or oi_ago is None or oi_ago == 0:
            skipped_oi += 1; continue
        price_pct = (p_now - p_ago) / p_ago * 100.0
        oi_pct = (oi_now - oi_ago) / oi_ago * 100.0
        v = bars[t]["v"]; tbv = bars[t]["tbv"]
        taker_ratio = (tbv / v) if v > 0 else 0.5
        sig = None
        if price_pct > PRICE_THRESH and oi_pct < 0 and taker_ratio < 0.5: sig = "short"
        elif price_pct < -PRICE_THRESH and oi_pct > 0 and taker_ratio > 0.5: sig = "long"
        if not sig: continue
        # horizons with net cost
        fwd_net = {}
        for h in HORIZONS:
            j = i + h
            if j >= len(bar_ts): continue
            t_out = bar_ts[j]
            p_out = bars[t_out]["c"]
            if t < f_lo or t_out > f_hi:
                skipped_fund += 1; break
            try:
                net = net_return(sig, p_now, p_out, t, t_out, funding, fee_rt=FEE_RT, slip_rt=SLIP_RT)
            except Exception:
                skipped_fund += 1; break
            fwd_net[h] = net * 100.0
        if len(fwd_net) != len(HORIZONS): continue
        reg = day_regime_for(t, regime, dts)
        events.append({"ts": t, "sig": sig, "reg": reg, "net": fwd_net})

    print("events={0} skipped_oi={1} skipped_fund={2}".format(len(events), skipped_oi, skipped_fund))
    if not events:
        print("no events, abort"); return

    events.sort(key=lambda e: e["ts"])
    n = len(events)
    folds = [(0, n), (0, 2*n//3), (n//3, n)]

    def bucket(evs, sig, hz, reg=None):
        vals = []
        for e in evs:
            if e["sig"] != sig: continue
            if reg is not None and e["reg"] != reg: continue
            vals.append(e["net"][hz])
        return vals

    def tstat(vals):
        if len(vals) < 2: return 0.0
        m = statistics.mean(vals)
        sd = statistics.pstdev(vals)
        if sd == 0: return 0.0
        return m / (sd / sqrt(len(vals)))

    regs = ["trend_up", "trend_down", "range", "unknown"]
    cells = []
    for sig in ["long", "short"]:
        for hz in HORIZONS:
            for reg in regs:
                cells.append((sig, hz, reg))
    bonf = len(cells)

    out = []
    out.append("# OI Divergence v2 - Pre-registered - 2026-10-10")
    out.append("")
    out.append("Pre-registration: research/_archive/loose_2026-10/PRE_REG_OI_DIVERGENCE_2026-10-10.md")
    out.append("Costs: fees 10 bps RT, slippage 2 bps RT, funding from records.")
    out.append("Folds: full / first-two-thirds / last-third. Embargo {0} bars at each boundary.".format(EMBARGO_BARS))
    out.append("Cells reported: {0}. Bonferroni divisor: {0}.".format(bonf))
    out.append("")
    out.append("Events: {0}".format(n))
    out.append("")
    out.append("## Pooled (all events)")
    out.append("")
    out.append("| signal | horizon | n | mean net % | t |")
    out.append("|---|---|---|---|---|")
    for sig in ["long", "short"]:
        for hz in HORIZONS:
            vals = bucket(events, sig, hz)
            out.append("| {0} | {1} | {2} | {3:+.4f} | {4:+.2f} |".format(sig, hz, len(vals), statistics.mean(vals) if vals else 0, tstat(vals)))
    out.append("")
    out.append("## Per regime, full window")
    out.append("")
    out.append("| signal | horizon | regime | n | mean net % | t |")
    out.append("|---|---|---|---|---|---|")
    for sig in ["long", "short"]:
        for hz in HORIZONS:
            for reg in regs:
                vals = bucket(events, sig, hz, reg)
                if len(vals) < 5: continue
                out.append("| {0} | {1} | {2} | {3} | {4:+.4f} | {5:+.2f} |".format(sig, hz, reg, len(vals), statistics.mean(vals), tstat(vals)))
    out.append("")
    out.append("## Walk-forward (3 folds, test only)")
    out.append("")
    out.append("| fold | train range | test range | signal | horizon | train mean | test mean | test n | test t |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for fi, (tr_lo, tr_hi) in enumerate(folds[:2]):
        if fi == 0:
            train = events[:tr_hi]; test = events[tr_hi:tr_hi+ (tr_hi-tr_lo)]
        else:
            train = events[:tr_hi]; test = events[tr_hi:]
        for sig in ["long", "short"]:
            for hz in HORIZONS:
                tv = bucket(train, sig, hz); ev = bucket(test, sig, hz)
                if not tv or not ev: continue
                out.append("| {0} | {1}-{2} | rest | {3} | {4} | {5:+.4f} | {6:+.4f} | {7} | {8:+.2f} |".format(fi+1, tr_lo, tr_hi, sig, hz, statistics.mean(tv), statistics.mean(ev), len(ev), tstat(ev)))
    out.append("")
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("wrote " + str(OUT))


if __name__ == "__main__":
    main()