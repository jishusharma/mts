"""Stop-slippage proxy from Binance USD-M BTCUSDT aggTrades (card gap-g7-stop-slippage). Pure functions; the runner is run_g7.py.
Defaults labelled OURS: round-100 USD levels as stop levels, deltas 0/250/1000 ms, terciles of DEV daily range."""
import sys
sys.dont_write_bytecode = True
import math
import numpy as np

CUTOFF_DAY = "2024-07-01"     # DEV only: no day on or after this is read
LEVEL_STEP = 100.0            # OURS


def assert_dev_day(day):
    if str(day) >= CUTOFF_DAY:
        raise ValueError("day %s is on or after %s (VALIDATION/HOLDOUT): refused" % (day, CUTOFF_DAY))


def first_trade_beyond(prices, level, direction):
    """Adverse slip (USD) of the first trade at or beyond `level` in `direction` (+1 up/buy stop, -1 down/sell stop):
    direction*(price-level) >= 0; exact hit 0; None if the series never gets there."""
    p = np.asarray(prices, float)
    hit = np.nonzero(p >= level)[0] if direction > 0 else np.nonzero(p <= level)[0]
    if len(hit) == 0:
        return None
    return float(direction * (p[hit[0]] - level))


def price_after(t, p, t_cross, delta_ms):
    """Price of the last trade at or before t_cross+delta_ms; None if that time is after the last trade (event dropped)."""
    tt = t_cross + delta_ms
    if tt > t[-1]:
        return None
    j = int(np.searchsorted(t, tt, side="right")) - 1
    return float(p[j]) if j >= 0 else None


def crossing_events(t, p):
    """Every up/down crossing of a round-LEVEL_STEP level between consecutive trades.
    up: p[i-1] < L <= p[i]; down: p[i-1] > L >= p[i]. Returns list of dict(idx, dir, level) ordered by idx then level."""
    p = np.asarray(p, float)
    a, b = p[:-1], p[1:]
    ev = []
    for k in np.nonzero(np.floor(b / LEVEL_STEP) > np.floor(a / LEVEL_STEP))[0]:
        lo, hi = int(math.floor(a[k] / LEVEL_STEP)) + 1, int(math.floor(b[k] / LEVEL_STEP))
        for m in range(lo, hi + 1):
            ev.append((int(k) + 1, 1, m * LEVEL_STEP))
    for k in np.nonzero(np.ceil(b / LEVEL_STEP) < np.ceil(a / LEVEL_STEP))[0]:
        lo, hi = int(math.ceil(b[k] / LEVEL_STEP)), int(math.ceil(a[k] / LEVEL_STEP)) - 1
        for m in range(lo, hi + 1):
            ev.append((int(k) + 1, -1, m * LEVEL_STEP))
    ev.sort(key=lambda e: (e[0], e[2]))
    return [dict(idx=i, dir=d, level=l) for i, d, l in ev]


def slips_bp(t, p, events, delta_ms):
    """Signed adverse slip in bp per event at delta_ms (nan if the event is within delta of the last trade).
    delta 0 = the crossing trade itself (first trade at or beyond the level); delta>0 = last trade at or before t_cross+delta."""
    out = []
    for e in events:
        if delta_ms == 0:
            px = float(p[e["idx"]])
        else:
            px = price_after(t, p, int(t[e["idx"]]), delta_ms)
        out.append(float("nan") if px is None else e["dir"] * (px - e["level"]) / e["level"] * 1e4)
    return np.array(out, float)


def to_r(slip_bp, stop_pct):
    """R multiples: slip in bp over the stop width in bp (stop_pct 0.40 -> 40 bp)."""
    return slip_bp / (stop_pct * 100.0)


def assign_terciles(ranges):
    """low/mid/high by cuts q1=sorted[n//3], q2=sorted[2n//3]; value < q1 low, < q2 mid, else high (ties go to the higher bucket)."""
    s = sorted(ranges)
    n = len(s)
    q1, q2 = s[n // 3], s[2 * n // 3]
    return ["low" if r < q1 else ("mid" if r < q2 else "high") for r in ranges]


def pick_days(days_sorted, k, used):
    """k evenly spaced days (floor((i+.5)*m/k)) from the not-yet-used days (date order)."""
    u = set(used)
    rem = [d for d in days_sorted if d not in u]
    m = len(rem)
    return [rem[int((i + 0.5) * m / k)] for i in range(k)] if m >= k else rem
