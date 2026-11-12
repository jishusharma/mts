import sys
sys.dont_write_bytecode = True
"""Baileysforex sweep -> 15m BOS -> demand retest, with the daily trend. Rule exactly as PREREG.md (frozen).

Bars are dicts of numpy arrays: t (open ms), o, h, l, c. A bar is usable only after it closes (t + width).
"""
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "backtest"))
from fees import BINANCE_TAKER  # shared cost source (T06): 2 x taker = 0.10 % round trip

M15 = 15 * 60_000
H1 = 60 * 60_000
D1 = 24 * H1
PIV = 3            # fractal strength (OURS)
SMA_D = 50         # daily bias SMA (OURS)
WINDOW = 24 * H1   # sweep window (OURS)
RETEST_BARS = 16   # 4 h of 15m bars (OURS)
ATR_N = 14
ATR_K = 0.1        # stop buffer in ATR (OURS)
MIN_RISK = 0.001   # R/entry floor (OURS)
RR = 3.0           # SOURCED (quote): mechanically target a one to three
CAP = 672          # 7 days of 15m bars (OURS)
FEE = BINANCE_TAKER * 2  # 10 bp round trip


def resample(t, o, h, l, c, width):
    """Bucket 1m arrays to bars of `width` ms, UTC aligned; buckets with no data are absent."""
    b = t // width
    idx = np.flatnonzero(np.diff(b)) + 1
    st = np.r_[0, idx]
    en = np.r_[idx, len(t)]
    return dict(t=b[st] * width, o=o[st], h=np.maximum.reduceat(h, st), l=np.minimum.reduceat(l, st), c=c[en - 1])


def pivot_low(bars, i):
    """Strict fractal low at i (needs bars up to i+PIV; use it only once bar i+PIV has closed)."""
    l = bars["l"]
    return l[i] < l[i - PIV:i].min() and l[i] < l[i + 1:i + PIV + 1].min()


def pivot_high(bars, i):
    h = bars["h"]
    return h[i] > h[i - PIV:i].max() and h[i] > h[i + 1:i + PIV + 1].max()


def latest_pivot(bars, upto, kind):
    """Most recent confirmed pivot (index, price) using only bars <= `upto` (pivot m is confirmed once bar m+PIV <= upto)."""
    key = "l" if kind == "low" else "h"
    fn = pivot_low if kind == "low" else pivot_high
    for m in range(upto - PIV, max(PIV, upto - 400) - 1, -1):
        if fn(bars, m):
            return m, float(bars[key][m])
    return None


def atr(bars, upto):
    h, l, c = bars["h"], bars["l"], bars["c"]
    s = slice(upto - ATR_N + 1, upto + 1)
    pc = c[upto - ATR_N:upto]
    tr = np.maximum(h[s] - l[s], np.maximum(abs(h[s] - pc), abs(l[s] - pc)))
    return float(tr.mean())


def daily_bias(d1, close_ms):
    """+1 / -1 / 0 from the last daily bar COMPLETED at close_ms: its close vs the SMA50 of the last 50 completed closes."""
    k = int(np.searchsorted(d1["t"] + D1, close_ms, side="right")) - 1  # last bar with t+D1 <= close_ms
    if k < SMA_D - 1:
        return 0
    c = d1["c"][k - SMA_D + 1:k + 1]
    return 1 if d1["c"][k] > c.mean() else (-1 if d1["c"][k] < c.mean() else 0)


def simulate(b15, i0, side, stop, tp):
    """Walk 15m bars from index i0; the stop wins a tie. Returns (exit_idx, exit_px, kind)."""
    n = len(b15["t"])
    last = min(i0 + CAP - 1, n - 1)
    for j in range(i0, last + 1):
        hi, lo = b15["h"][j], b15["l"][j]
        if side > 0:
            if lo <= stop:
                return j, stop, "stop"
            if hi >= tp:
                return j, tp, "tp"
        else:
            if hi >= stop:
                return j, stop, "stop"
            if lo <= tp:
                return j, tp, "tp"
    return last, float(b15["c"][last]), "cap"


def make_trade(b15, i, side, zlo, zhi, shift=0):
    """Entry/stop/target for a retest on bar i (entry at the next bar open). `shift`=1 peeks at the entry bar: tests only."""
    e_i = i + 1
    entry = float(b15["o"][e_i])
    buf = ATR_K * atr(b15, i + shift)  # shift=1 folds the entry bar's own range into the stop: a deliberate look-ahead
    stop = (zlo - buf) if side > 0 else (zhi + buf)
    r = (entry - stop) if side > 0 else (stop - entry)
    if r <= 0 or r / entry < MIN_RISK:
        return None
    return e_i, entry, stop, entry + side * RR * r, r


def finish(b15, e_i, side, entry, stop, tp, r):
    x_i, x_px, kind = simulate(b15, e_i, side, stop, tp)
    gross = side * (x_px - entry) / r
    net = gross - FEE * entry / r
    return dict(side=side, entry_ms=int(b15["t"][e_i]), entry_px=entry, exit_ms=int(b15["t"][x_i]), exit_px=float(x_px),
                entry_i=e_i, exit_i=x_i, kind=kind, stop=stop, r_pct=r / entry, gross_r=gross, ret=net,
                net_bp=net * r / entry * 1e4)


def run(b15, h1, d1, start_ms, end_ms, shift=0):
    """All trades with entry in [start_ms, end_ms]. `shift` > 0 deliberately peeks ahead (tests only)."""
    n = len(b15["t"])
    trades = []
    i = 2 * PIV + ATR_N + 5
    state = None  # None | dict(stage="bos"/"retest", ...)
    while i < n - 1:
        close_ms = int(b15["t"][i]) + M15
        if state is None:
            if close_ms % H1 == 0:  # a 1h bar closes together with this 15m bar
                j = int(np.searchsorted(h1["t"], close_ms - H1))
                bias = daily_bias(d1, close_ms)
                if bias != 0 and j > 2 * PIV + 5:
                    p = latest_pivot(h1, j - 1, "low" if bias > 0 else "high")
                    if p is not None:
                        if bias > 0:
                            swept = h1["l"][j] < p[1] and h1["c"][j] > p[1]
                        else:
                            swept = h1["h"][j] > p[1] and h1["c"][j] < p[1]
                        if swept:
                            state = dict(stage="bos", side=bias, i_sweep=i, end=close_ms + WINDOW)
        elif state["stage"] == "bos":
            if close_ms > state["end"]:
                state = None
            else:
                side = state["side"]
                p = latest_pivot(b15, i - 1, "high" if side > 0 else "low")
                if p is not None and (b15["c"][i] > p[1] if side > 0 else b15["c"][i] < p[1]):
                    seg = slice(state["i_sweep"] + 1, i + 1)
                    if side > 0:
                        b = state["i_sweep"] + 1 + int(np.argmin(b15["l"][seg]))
                        zlo, zhi = b15["l"][b], max(b15["o"][b], b15["c"][b])
                    else:
                        b = state["i_sweep"] + 1 + int(np.argmax(b15["h"][seg]))
                        zhi, zlo = b15["h"][b], min(b15["o"][b], b15["c"][b])
                    state.update(stage="retest", zlo=float(zlo), zhi=float(zhi), i_bos=i)
        else:
            side = state["side"]
            if i - state["i_bos"] > RETEST_BARS:
                state = None
            elif (b15["c"][i] <= state["zlo"]) if side > 0 else (b15["c"][i] >= state["zhi"]):
                state = None
            else:
                touch = (b15["l"][i] <= state["zhi"]) if side > 0 else (b15["h"][i] >= state["zlo"])
                if touch:  # close is beyond the far edge only in the branch above, so the hold test is already met
                    mt = make_trade(b15, i, side, state["zlo"], state["zhi"], shift)
                    state = None
                    if mt is not None and start_ms <= b15["t"][mt[0]] <= end_ms:
                        tr = finish(b15, mt[0], side, *mt[1:])
                        trades.append(tr)
                        i = tr["exit_i"]  # flat again after the exit bar
        i += 1
    return trades


def placebo(b15, trades, start_ms, end_ms, draws=500, seed=1):
    """Direction-matched placebo: per real trade, a random entry bar in the span, same side, same R%, same 3R/cap rules."""
    rng = np.random.default_rng(seed)
    lo = int(np.searchsorted(b15["t"], start_ms))
    hi = int(np.searchsorted(b15["t"], end_ms))
    means = []
    for _ in range(draws):
        rs = []
        for t in trades:
            e_i = int(rng.integers(lo, hi))
            entry = float(b15["o"][e_i])
            r = t["r_pct"] * entry
            s = t["side"]
            _, x_px, _ = simulate(b15, e_i, s, entry - s * r, entry + s * RR * r)
            rs.append(s * (x_px - entry) / r - FEE * entry / r)
        means.append(float(np.mean(rs)))
    return np.array(means)
