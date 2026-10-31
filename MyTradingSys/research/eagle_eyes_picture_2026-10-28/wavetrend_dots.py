"""C27: WaveTrend (LazyBear WT_CROSS_LB) dots as triggers, fee-net, 15m/1h/2h/4h (operator 10-31: "what abt wavetrend analysis?").
WT n1=10, n2=21, wt2 = SMA(wt1, 4), zones +-53: SOURCED (LazyBear). Holds, edge-vs-base, entry at next open-proxy (next close): OURS.
Window 2022-01..2024-06 ONLY: the WaveTrend pre-reg (wavetrend_2026-10-17/PRE_REG.md) keeps 2024-07+ sealed. Research only, no orders.
Usage: python wavetrend_dots.py <repo>"""
import json, os, sys, tempfile, statistics as st
from datetime import datetime, timezone

sys.path.insert(0, sys.argv[1])
from MyTradingSys.backtest.fees import BINANCE_TAKER

FEE = BINANCE_TAKER * 2 * 100  # % round trip
CACHE = os.path.join(tempfile.gettempdir(), "btc15m_bbdiv.json")  # Binance spot 15m from 2022, see failed_retest_takeout.fetch
END = int(datetime(2024, 7, 1, tzinfo=timezone.utc).timestamp() * 1000)
R15 = [x for x in json.load(open(CACHE)) if x[0] < END]


def agg(k):
    """k x 15m bars bucketed by timestamp; incomplete buckets dropped."""
    B = {}
    for x in R15:
        B.setdefault(x[0] // (k * 900000), []).append(x)
    return [(g[0][0], g[0][1], max(y[2] for y in g), min(y[3] for y in g), g[-1][4]) for _, g in sorted(B.items()) if len(g) == k]


def ema(xs, n):
    a = 2 / (n + 1); o = [xs[0]]
    for x in xs[1:]:
        o.append(o[-1] + a * (x - o[-1]))
    return o


def wavetrend(b):
    ap = [(x[2] + x[3] + x[4]) / 3 for x in b]
    esa = ema(ap, 10); d = ema([abs(a - e) for a, e in zip(ap, esa)], 10)
    w1 = ema([(a - e) / (0.015 * dd) if dd else 0 for a, e, dd in zip(ap, esa, d)], 21)
    return w1, [None] * 3 + [sum(w1[i - 3:i + 1]) / 4 for i in range(3, len(w1))]


def forward_ret(C, i, h, side):
    """% move from close of bar i+1 to close of bar i+1+h, in the trade's favour."""
    return (C[i + 1 + h] / C[i + 1] - 1) * 100 * side


SIGNALS = (("buy dot <= -53", 1, lambda w1, w2, i: w1[i] > w2[i] and w1[i - 1] <= w2[i - 1] and w1[i] <= -53),
           ("sell dot >= 53", -1, lambda w1, w2, i: w1[i] < w2[i] and w1[i - 1] >= w2[i - 1] and w1[i] >= 53),
           ("any buy dot", 1, lambda w1, w2, i: w1[i] > w2[i] and w1[i - 1] <= w2[i - 1]),
           ("any sell dot", -1, lambda w1, w2, i: w1[i] < w2[i] and w1[i - 1] >= w2[i - 1]))


def table():
    rows = []
    for tf, k, h in (("15m", 1, 16), ("1h", 4, 12), ("2h", 8, 6), ("2h", 8, 12), ("4h", 16, 6)):
        b = agg(k); C = [x[4] for x in b]; w1, w2 = wavetrend(b)
        base = st.mean(forward_ret(C, i, h, 1) for i in range(100, len(C) - h - 1))
        for name, side, cond in SIGNALS:
            x = [forward_ret(C, i, h, side) for i in range(100, len(C) - h - 1) if cond(w1, w2, i)]
            se = st.stdev(x) / len(x) ** 0.5
            rows.append(dict(tf=tf, h=h, sig=name, n=len(x), win=100 * sum(v > 0 for v in x) / len(x), gross=st.mean(x),
                             edge=st.mean(x) - base * side, net=st.mean(x) - FEE, se=se))
    return rows


if __name__ == "__main__":
    for r in table():
        print("%-4s hold %2d %-15s n=%5d win %2.0f%% gross %+.3f%% edge %+.3f%% net %+.3f%% (1 SE %.2f%%)" % (
            r["tf"], r["h"], r["sig"], r["n"], r["win"], r["gross"], r["edge"], r["net"], r["se"]))
