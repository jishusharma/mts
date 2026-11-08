"""mtf-timeframe-lead-lag-research: how an RSI / WaveTrend state flip travels across timeframes on BTC.
Rules frozen in PRE_REG.md (this folder). Usage: python lead_lag.py <data_dir> <dev|val>  -> writes RESULT_<split>.json
"""
import csv
import datetime as dt
import json
import statistics as st
import sys
from bisect import bisect_left, bisect_right
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from MyTradingSys.backtest import fees  # noqa: E402
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core  # noqa: E402

STEP = {"15m": 900_000, "1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000, "1w": 604_800_000}
TFS = ("15m", "1h", "4h", "1d", "1w")
HI, LO = 60.0, 40.0                     # Malkan's lines (SOURCED)
WINDOW_MS = 7 * 86_400_000
DEV = (dt.datetime(2019, 11, 8, tzinfo=dt.timezone.utc), dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc))
VAL = (DEV[1], dt.datetime(2026, 11, 8, tzinfo=dt.timezone.utc))
RT_FEE = fees.FEES_ALL_TAKER["entry"] + fees.FEES_ALL_TAKER["stop"]


def load(path):
    with open(path, newline="") as f:
        return [{"t": int(r["t"]), "h": float(r["h"]), "l": float(r["l"]), "c": float(r["c"])} for r in csv.DictReader(f)]


def _ema(x, p):
    a, out = 2 / (p + 1), [x[0]]
    for v in x[1:]:
        out.append(a * v + (1 - a) * out[-1])
    return out


def rsi_state(v):
    if v is None:
        return None
    return "BULL" if v >= HI else ("BEAR" if v <= LO else "MID")


def rsi_flips(bars, step):
    """[(close_ms, 'BULL'|'BEAR')]: the bar whose CLOSE changes the state into BULL or BEAR, dated at that close."""
    r = rsi_core([b["c"] for b in bars], 14)
    out, prev = [], None
    for b, v in zip(bars, r):
        s = rsi_state(v)
        if s is None:
            continue
        if prev is not None and s != prev and s in ("BULL", "BEAR"):
            out.append((b["t"] + step, s))
        prev = s
    return out


def wt_flips(bars, step):
    ap = [(b["h"] + b["l"] + b["c"]) / 3 for b in bars]
    esa = _ema(ap, 10)
    d = _ema([abs(a - e) for a, e in zip(ap, esa)], 10)
    ci = [(a - e) / (0.015 * dd) if dd else 0.0 for a, e, dd in zip(ap, esa, d)]
    w1 = _ema(ci, 21)
    w2 = [None] * 3 + [sum(w1[i - 3:i + 1]) / 4 for i in range(3, len(w1))]
    out = []
    for i in range(4, len(bars)):
        if w1[i] > w2[i] and w1[i - 1] <= w2[i - 1]:
            out.append((bars[i]["t"] + step, "BULL"))
        elif w1[i] < w2[i] and w1[i - 1] >= w2[i - 1]:
            out.append((bars[i]["t"] + step, "BEAR"))
    return out


def state_at(flips, t):
    """state set by the last flip closed at or before t (None before the first)."""
    i = bisect_right([f[0] for f in flips], t) - 1
    return flips[i][1] if i >= 0 else None


def lead_table(hi_flips, lo_flips, lo_ts, a, b):
    """for each higher-TF flip in [a, b): hours since the latest same-direction lower-TF flip within 7 days."""
    leads, none_ = [], 0
    for t, s in hi_flips:
        if not (a <= t < b):
            continue
        j = bisect_right(lo_ts, t) - 1
        found = None
        while j >= 0 and lo_ts[j] >= t - WINDOW_MS:
            if lo_flips[j][1] == s:
                found = lo_ts[j]
                break
            j -= 1
        if found is None:
            none_ += 1
        else:
            leads.append((t - found) / 3_600_000)
    n = len(leads) + none_
    if not leads:
        return {"n": n, "with_lead": 0}
    q = st.quantiles(leads, n=4) if len(leads) > 1 else [leads[0]] * 3
    return {"n": n, "with_lead": round(len(leads) / n, 3), "median_h": round(st.median(leads), 1),
            "iqr_h": [round(q[0], 1), round(q[2], 1)]}


def rule_events(rule, f, a, b):
    """times (close ms) when an early-flip rule fires, with its direction. R1: 4h flip. R2: 4h flip while 1h already
    in that state (or 1h flip while 4h in it). R3: R2 and the last closed 1d RSI on the same side of 50."""
    ev = []
    cand = [(t, s, "4h") for t, s in f["rsi"]["4h"]] + ([(t, s, "1h") for t, s in f["rsi"]["1h"]] if rule != "R1" else [])
    for t, s, tf in sorted(cand):
        if not (a <= t < b):
            continue
        if rule == "R1" and tf == "4h":
            ev.append((t, s))
            continue
        other = "1h" if tf == "4h" else "4h"
        if state_at(f["rsi"][other], t) != s:
            continue
        if rule == "R3":
            r1d = f["rsi1d_val"](t)
            if r1d is None or (s == "BULL" and r1d <= 50) or (s == "BEAR" and r1d >= 50):
                continue
        ev.append((t, s))
    out, last = [], -10 ** 18                               # one event per 24 h per direction
    for t, s in ev:
        if out and out[-1][1] == s and t - last < 86_400_000:
            continue
        out.append((t, s))
        last = t
    return out


def hit_rate(events, d_flips):
    ts = [x[0] for x in d_flips]
    hits = 0
    for t, s in events:
        i = bisect_left(ts, t)
        while i < len(ts) and ts[i] <= t + WINDOW_MS:
            if d_flips[i][1] == s:
                hits += 1
                break
            i += 1
    return hits / len(events) if events else float("nan")


def fwd(events, b1h, days):
    ts = [b["t"] + STEP["1h"] for b in b1h]
    out = []
    for t, s in events:
        i = bisect_left(ts, t)
        k = i + 24 * days
        if i >= len(ts) or k >= len(ts):
            continue
        r = b1h[k]["c"] / b1h[i]["c"] - 1
        out.append((r if s == "BULL" else -r) - RT_FEE)
    return out


def _m(x):
    if len(x) < 2:
        return {"n": len(x)}
    return {"n": len(x), "mean_pct": round(100 * st.mean(x), 3), "se_pct": round(100 * st.stdev(x) / len(x) ** 0.5, 3)}


def main(data_dir, split):
    data_dir = Path(data_dir)
    bars = {tf: load(data_dir / f"BTCUSDT_{tf}.csv") for tf in TFS}
    f = {"rsi": {tf: rsi_flips(bars[tf], STEP[tf]) for tf in TFS}, "wt": {tf: wt_flips(bars[tf], STEP[tf]) for tf in TFS}}
    r1d = rsi_core([b["c"] for b in bars["1d"]], 14)
    d_close = [b["t"] + STEP["1d"] for b in bars["1d"]]

    def rsi1d_val(t):
        i = bisect_right(d_close, t) - 1
        return r1d[i] if i >= 0 else None
    f["rsi1d_val"] = rsi1d_val
    a, b = [int(x.timestamp() * 1000) for x in (DEV if split == "dev" else VAL)]
    res = {"split": split, "leads": {}, "rules": {}}
    for ind in ("rsi", "wt"):
        for hi in ("1w", "1d", "4h"):
            for lo in TFS[:TFS.index(hi)]:
                lo_f = f[ind][lo]
                res["leads"][f"{ind} {hi}<-{lo}"] = lead_table(f[ind][hi], lo_f, [x[0] for x in lo_f], a, b)
    d_f = [x for x in f["rsi"]["1d"]]
    # base rate: share of random 7-day windows (every 4h close in the split) with a 1d flip of a given direction
    grid = [t for t in range(a, b, STEP["4h"])]
    base = st.mean(1.0 if any(t < x[0] <= t + WINDOW_MS and x[1] == s for x in d_f[max(0, bisect_left([y[0] for y in d_f], t) - 1):bisect_left([y[0] for y in d_f], t + WINDOW_MS) + 1]) else 0.0
                   for t in grid for s in ("BULL", "BEAR")) * 1.0
    res["base_rate_1d_flip_7d"] = round(base, 3)
    all_ev = [(t, s) for t in grid[::6] for s in ("BULL", "BEAR")]   # daily grid, both directions = unconditional
    res["baseline_fwd"] = {f"{d}d": _m(fwd(all_ev, bars["1h"], d)) for d in (1, 3, 7)}
    for rule in ("R1", "R2", "R3"):
        ev = rule_events(rule, f, a, b)
        res["rules"][rule] = {"events": len(ev), "hit_rate_1d_flip_7d": round(hit_rate(ev, d_f), 3),
                              "fwd": {f"{d}d": _m(fwd(ev, bars["1h"], d)) for d in (1, 3, 7)}}
    out = Path(__file__).parent / f"RESULT_{split}.json"
    out.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
