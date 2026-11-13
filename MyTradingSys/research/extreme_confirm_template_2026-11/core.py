"""Trade mechanics for extreme_confirm_template_2026-11 (see PRE_REG.md). Pure functions."""
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest import fees  # noqa: E402

HOUR = 3600000
HOLD = 24
RT_FEE = 2 * fees.BINANCE_TAKER


def runs(c, up):
    """Length of the current run of consecutive lower (up=False) or higher (up=True) closes at each bar."""
    out = [0] * len(c)
    for i in range(1, len(c)):
        ok = c[i] > c[i - 1] if up else c[i] < c[i - 1]
        out[i] = out[i - 1] + 1 if ok else 0
    return out


def fwd_trade(o, h, l, c, i, side, k, atr_i, fund_between):
    """Setup bar i, confirm bar i+1 assumed checked, entry open[i+2]. side +1 long / -1 short. Returns net return (fraction) or None.
    fund_between(t0_idx, t1_idx) -> sum of funding rates for entry bar open .. exit bar end."""
    e = i + 2
    if e + HOLD - 1 >= len(c):
        return None
    entry = o[e]
    stop = l[i] - k * atr_i if side > 0 else h[i] + k * atr_i
    r = (entry - stop) * side
    if not r > 0:
        return None
    target = entry + side * 2 * r
    exit_px, xj = c[e + HOLD - 1], e + HOLD - 1
    for j in range(e, e + HOLD):
        if side > 0:
            if l[j] <= stop:
                exit_px, xj = min(stop, o[j]) if j > e else stop, j
                break
            if h[j] >= target:
                exit_px, xj = target, j
                break
        else:
            if h[j] >= stop:
                exit_px, xj = max(stop, o[j]) if j > e else stop, j
                break
            if l[j] <= target:
                exit_px, xj = target, j
                break
    ret = side * (exit_px / entry - 1.0) - RT_FEE - side * fund_between(e, xj)
    return ret, xj
