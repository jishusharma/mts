"""M1 maker-entry study: NK2 pivot reclaim, 1h SHORT-P. See ../PRE_REG.md.
Signals / levels / phase / ATR come unchanged from nk2_orig.py (verbatim copy of the original study.py).
Only new logic here: signal -> limit-level mapping (L = pivot P, sell limit above the signal close) and the stop/target
re-expressed with entry = L (same rule, entry-relative min distance), then lib/maker_fill.simulate_maker."""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
import nk2_orig as O
import maker_fill as MF

SIDE, LEVEL, TFK, BARS_MAX, PHASES = -1, "P", 4, 24, (-1, 0)   # 1h SHORT-P, matched phases (DOWN, RANGE)
TF_MS = 3600000
SPLIT = O.SPLIT


def orig_signals(D, side=SIDE, level=LEVEL, phases=PHASES, bars_max=BARS_MAX):
    """Original sequential one-position loop (taker timing) -> list of (i, R_gross, dist_frac, phase, entry_ms).
    Identical to nk2_orig.run_trades but keeps the signal bar index i."""
    out, busy = [], -1
    a = D["a"]
    for i in O.signals(D, side, level, TFK):
        if i <= busy or D["ph"][i] not in phases:
            continue
        s = O.simulate(D, i, side, bars_max)
        if s is None:
            continue
        r, df, xi, e = s
        out.append((int(i), float(r), float(df), int(D["ph"][i]), float(a[i + 1, 0])))
        busy = xi
    return out


def limit_order(D, i, L=None, side=SIDE):
    """Map signal bar i to (L, stop, target) for a resting limit at L (default: pivot P at bar i).
    Same stop/target rule as the original but entry = L. Returns None if R:R filter fails / no target."""
    a = D["a"]
    if np.isnan(D["atr"][i]):
        return None
    if L is None:
        L = float(D["lv"][LEVEL][i])
    if side < 0:
        swing = a[max(0, i - 5):i + 1, 2].max()
        dist = max(swing - L, 0.6 * D["atr"][i], 0.005 * L)
        stop = L + dist
        cands = [D["lv"][k][i] for k in O.LEVELS if D["lv"][k][i] < L]
        if not cands:
            return None
        tgt = float(max(cands))
        if L - tgt < dist:
            return None
    else:
        swing = a[max(0, i - 5):i + 1, 3].min()
        dist = max(L - swing, 0.6 * D["atr"][i], 0.005 * L)
        stop = L - dist
        cands = [D["lv"][k][i] for k in O.LEVELS if D["lv"][k][i] > L]
        if not cands:
            return None
        tgt = float(min(cands))
        if tgt - L < dist:
            return None
    return float(L), float(stop), tgt


def maker_trade(D, i, m1, tick, L=None, side=SIDE, fill_bar_target=True):
    """One resting-limit trial for signal bar i. Uses only 1m bars with t >= signal bar close."""
    a = D["a"]
    sig_close = float(a[i, 0] + TF_MS)
    o = limit_order(D, i, L, side)
    if o is None:
        r = MF._miss("rr_or_no_target")
        r["signal_close_ms"] = sig_close
        return r
    L, stop, tgt = o
    time_stop = float(a[min(i + 1, len(a) - 1), 0] + (BARS_MAX + 1) * TF_MS)  # original seg = 25 bars from entry bar
    r = MF.simulate_maker(side, L, stop, tgt, sig_close, TF_MS, time_stop, True, m1, tick=tick,
                          fill_bar_target=fill_bar_target)
    r["signal_close_ms"] = sig_close
    r["L"], r["stop"], r["target"] = L, stop, tgt
    return r
