"""WaveTrend observation module (LazyBear oscillator). OBSERVATION ONLY: no side, no routing, no Tom/Fabio gate.

Emits per closed bar: wt1, wt2, zone tag, cross event, and `available_at` (bar close). Formula, conventions and
worked numbers: backtest/layers/FORMULAS.md section 20; contract: research/wavetrend_2026-10-17/PARITY_CONTRACT.md.
Re-implemented from the published formula (three EMAs and an SMA); credit: LazyBear's WaveTrend Oscillator
(TradingView scripts 2KE8wTuF / jFQn4jYZ, republished by lonestar108). No Pine text is copied.

Causal: the value and event at bar t use bars <= t only (a cross uses t and the last strict side). No numpy, no I/O.
Input bars: sequence of (open_time_ms, high, low, close). A NaN bar or a missing bar (open_time jump != tf_ms)
drops the EMA state; outputs are suppressed for WARMUP bars after any such reset (OURS).
"""
import math
from collections import namedtuple

NAN = float("nan")
N1, N2, SMA_N, K = 10, 21, 4, 0.015   # SOURCED: Crosses:14-21
OB1, OB2 = 60.0, 53.0                  # SOURCED: Crosses:9-12 (os = negatives)
WARMUP = 200                           # OURS (PARITY_CONTRACT s3)
D_TOL = 1e-9                           # OURS: d <= D_TOL*|ap| counts as a flat window

Row = namedtuple("Row", "open_time available_at wt1 wt2 zone event")


def sma(xs, n):
    out = []
    for i in range(len(xs)):
        w = xs[max(0, i - n + 1):i + 1]
        out.append(sum(w) / n if len(w) == n and not any(math.isnan(v) for v in w) else NAN)
    return out


def zone(v):
    if v is None or math.isnan(v):
        return None
    if v >= OB1:
        return "ob2"
    if v >= OB2:
        return "ob1"
    if v <= -OB1:
        return "os2"
    if v <= -OB2:
        return "os1"
    return "mid"


def cross_events(wt1, wt2):
    """+1 up-cross, -1 down-cross, 0 none. "le": fires at the first bar strictly on the opposite side of the last
    strict side; a tie bar is skipped; NaN in either series resets the side (no event across a hole)."""
    out, last = [], 0
    for a, b in zip(wt1, wt2):
        if math.isnan(a) or math.isnan(b):
            out.append(0)
            last = 0
            continue
        side = (a > b) - (a < b)
        out.append(side if (side != 0 and last != 0 and side != last) else 0)
        if side != 0:
            last = side
    return out


def htf_index(t, htf_ms, htf_open_times):
    """Index of the last HTF bar closed at or before time t (open + htf_ms <= t), else None. Sorted opens."""
    best = None
    for j, o in enumerate(htf_open_times):
        if o + htf_ms <= t:
            best = j
        else:
            break
    return best


def compute(bars, tf_ms, warmup=WARMUP):
    """bars: sequence of (open_time_ms, high, low, close). Returns one Row per input bar."""
    n = len(bars)
    a1, a2 = 2.0 / (N1 + 1), 2.0 / (N2 + 1)
    esa = dev = tci = None            # EMA states; None = needs a seed
    since = 0                         # valid bars since the last reset
    prev_t = None
    raw = [NAN] * n                   # wt1 before the warm-up mask (wt2 needs it)
    keep = [False] * n
    for i, (t, h, l, c) in enumerate(bars):
        gap = prev_t is not None and t - prev_t != tf_ms
        prev_t = t
        if gap:
            esa = dev = tci = None
            since = 0
        if any(math.isnan(v) for v in (h, l, c)):
            esa = dev = tci = None
            since = 0
            continue
        ap = (h + l + c) / 3.0
        esa = ap if esa is None else a1 * ap + (1 - a1) * esa
        x = abs(ap - esa)
        dev = x if dev is None else a1 * x + (1 - a1) * dev
        if dev <= D_TOL * abs(ap):    # flat window: ci undefined (fail closed), wt1 state dropped
            tci = None
            since = 0
            continue
        ci = (ap - esa) / (K * dev)
        tci = ci if tci is None else a2 * ci + (1 - a2) * tci
        since += 1
        raw[i] = tci
        keep[i] = since >= warmup
    wt2 = sma(raw, SMA_N)
    wt1 = [v if k else NAN for v, k in zip(raw, keep)]
    wt2 = [v if k else NAN for v, k in zip(wt2, keep)]
    ev = cross_events(wt1, wt2)
    return [Row(bars[i][0], bars[i][0] + tf_ms, wt1[i], wt2[i], zone(wt1[i]), ev[i]) for i in range(n)]
