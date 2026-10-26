"""Pizzino layer indicators: pure functions, stdlib only, no I/O, no live wiring.

Implements MyTradingSys/research/pizzino_layer_2026-10-27/SPEC.md sections 1-6.
A rule at bar i uses bars 0..i only. Two features stay apart and are never merged
under one name (SPEC section 0): `bar_count_from` (Jason) and `swing_state` /
`nested_conf` (Michael).

Parameter labels: the fractal rule, state formula, W, L, N, tol, R, RRmin and the
2R fallback are OURS (SPEC section 8); the 3-bar length, HH+HL test, 50% line and
next-pivot target are SOURCED (ME quotes cited in SPEC).
"""
from collections import namedtuple

Pivot = namedtuple("Pivot", "index price confirmed_at kind")  # kind: "H" or "L"


# ---------------------------------------------------------------- section 1
def _raw_pivots(high, low, n):
    out = []
    for i in range(n, len(high) - n):
        around = [j for j in range(i - n, i + n + 1) if j != i]
        if all(high[i] > high[j] for j in around):
            out.append(Pivot(i, high[i], i + n, "H"))
        if all(low[i] < low[j] for j in around):
            out.append(Pivot(i, low[i], i + n, "L"))
    return out


def _alternate(pivots):
    out = []
    for p in pivots:
        if out and out[-1].kind == p.kind:
            keep_new = p.price > out[-1].price if p.kind == "H" else p.price < out[-1].price
            if keep_new:
                out[-1] = p
        else:
            out.append(p)
    return out


def find_pivots(high, low, n):
    """Strict degree-n fractal pivots, alternating, each confirmed at index + n."""
    return _alternate(_raw_pivots(high, low, n))


def pivots_known(high, low, n, i):
    """Pivots a trader can know at the close of bar i (confirmed_at <= i)."""
    return find_pivots(high[: i + 1], low[: i + 1], n)


# ---------------------------------------------------------------- section 2
def swing_state(ph, pl, close):
    """(state, break_level) from pivot-high and pivot-low price lists (oldest first).

    state +1 up: HH, HL and close above the last swing low (break level = last PL).
    state -1 down: LH, LL and close below the last swing high (break level = last PH).
    Otherwise (0, None), including fewer than two pivots of either kind."""
    if len(ph) < 2 or len(pl) < 2:
        return 0, None
    if ph[-1] > ph[-2] and pl[-1] > pl[-2] and close > pl[-1]:
        return 1, pl[-1]
    if ph[-1] < ph[-2] and pl[-1] < pl[-2] and close < ph[-1]:
        return -1, ph[-1]
    return 0, None


def nested_conf(states):
    """Plain sum of the nested states (range -3..+3); +/-3 is confluence."""
    return sum(states)


def lead_flag(s1, s2, s3, L, i):
    """+1 if state1 turned up within the last L bars while states 2 and 3 are not up
    yet at bar i; -1 for the mirror (down); else 0. Inputs are state series."""
    for sign in (1, -1):
        if s1[i] != sign or s2[i] == sign or s3[i] == sign:
            continue
        j = i
        while j > 0 and s1[j - 1] == sign:
            j -= 1
        if j > 0 and i - j < L:  # j == 0: no observed turn
            return sign
    return 0


# ---------------------------------------------------------------- section 3
def is_significant(series, idx, kind, W):
    """Pivot bar idx is the lowest low (kind L, series = lows) or highest high
    (kind H, series = highs) of the W bars before it, itself included."""
    window = series[max(0, idx - W): idx]
    if kind == "L":
        return all(series[idx] <= x for x in window)
    return all(series[idx] >= x for x in window)


def bar_count_from(high, low, t, kind):
    """Signed consecutive-extension count per bar from index t onward (element 0 is
    bar t, value 0). After a pivot low (kind L) a bar extends if HH and HL; after a
    pivot high a bar extends if LH and LL (negative counts). The count stops at the
    first non-extending bar and its value is kept. three_bar = abs(count) >= 3."""
    sign = 1 if kind == "L" else -1
    counts = [0]
    run, alive = 0, True
    for k in range(t + 1, len(high)):
        if alive:
            ext = (high[k] > high[k - 1] and low[k] > low[k - 1]) if sign == 1 else (
                high[k] < high[k - 1] and low[k] < low[k - 1])
            if ext:
                run += 1
            else:
                alive = False
        counts.append(sign * run)
    return counts


# ---------------------------------------------------------------- section 4
def mid_line(ph, pl):
    return (ph + pl) / 2


def half_state(close, mid, prev):
    """'strong' above the 50% line, 'weak' below; on equality keep the previous value."""
    if close > mid:
        return "strong"
    if close < mid:
        return "weak"
    return prev


def half_events(high, low, close, prev_close, mid):
    hold_above = low <= mid and close > mid
    hold_below = high >= mid and close < mid
    return {
        "hold_above": hold_above,
        "hold_below": hold_below,
        "reject_from_below": hold_below and prev_close < mid,
    }


# ---------------------------------------------------------------- section 5
def break_retest(level, closes, highs, lows, N=2, tol=0.005, R=20, direction="up"):
    """First confirmed break of `level` (N consecutive closes beyond it, the one
    before the run on the other side), then the first retest within R bars.
    Retest (up): low <= level*(1+tol); outcome 'hold' if close > level else 'fail'.
    Down mirrors (high >= level*(1-tol); 'hold' if close < level)."""
    up = direction == "up"
    res = {"break_confirmed_at": None, "retest_bar": None, "outcome": None}
    beyond = (lambda c: c > level) if up else (lambda c: c < level)
    for i in range(N, len(closes)):
        if all(beyond(closes[j]) for j in range(i - N + 1, i + 1)) and not beyond(closes[i - N]):
            res["break_confirmed_at"] = i
            break
    c = res["break_confirmed_at"]
    if c is None:
        return res
    for j in range(c + 1, min(len(closes), c + R + 1)):
        touched = lows[j] <= level * (1 + tol) if up else highs[j] >= level * (1 - tol)
        if touched:
            res["retest_bar"] = j
            res["outcome"] = "hold" if beyond(closes[j]) else "fail"
            break
    return res


# ---------------------------------------------------------------- section 6
def plan_trade(side, entry, stop, pivot_prices, rr_min=1.0, fallback_r=2.0):
    """Target = nearest confirmed pivot beyond entry (PH above for long, PL below
    for short); with none, entry +/- fallback_r * risk. take = rr >= rr_min and
    risk > 0. Fees and slippage are applied in the backtest, not here."""
    long_ = side == "long"
    risk = entry - stop if long_ else stop - entry
    if long_:
        cands = [p for p in pivot_prices if p > entry]
        target = min(cands) if cands else entry + fallback_r * risk
    else:
        cands = [p for p in pivot_prices if p < entry]
        target = max(cands) if cands else entry - fallback_r * risk
    reward = target - entry if long_ else entry - target
    if risk <= 0:
        return {"risk": risk, "reward": reward, "target": target, "rr": None, "take": False}
    rr = reward / risk
    return {"risk": risk, "reward": reward, "target": target, "rr": rr, "take": rr >= rr_min}
