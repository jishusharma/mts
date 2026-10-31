"""Reclaim with the video's timing (Brando cP6xvs2I02s 03:58-04:02, 08:29-08:35): enter at the reclaim bar close, exit at the first
bar close back beyond the level (the stop), else at a horizon cap. Level, swing, ATR buffer and break definitions are reused UNCHANGED
from tf_break_event_study_2026-10-30/study.py (confirmed_pivots, CFG). Parameters OURS, frozen in PRE_REG.md.
 side=-1: low level broken, reclaimed -> LONG at the reclaim close; side=+1: high level -> SHORT. Stop = close back beyond the level.
Fee-net: round trip 2 x fees.BINANCE_TAKER (regime A), no slippage. Bars come from data.binance.vision 4h/1d klines (UTC buckets)."""
import os
import sys

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', 'tf_break_event_study_2026-10-30')))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', '..')))
import study  # noqa: E402
from backtest import fees  # noqa: E402

RT_FEE = 2 * fees.BINANCE_TAKER
CAP = {'4h': 6, '1D': 5}  # OURS horizon cap in bars after the reclaim bar
CFG = {k: (study.CFG[k][0], study.CFG[k][1], study.CFG[k][2]) for k in CAP}  # (tf minutes, L, N): same as the break study


def simulate(c, lv, side, j, cap):
    """Entry at close of bar j (reclaim). Exit at the first close strictly beyond the level (below for a long, above for a short)
    within bars j+1..j+cap, else at close of bar j+cap. Returns (exit index, gross simple return in the trade direction)."""
    d = -side  # long after a low break
    k = j + cap
    for q in range(j + 1, j + cap + 1):
        if (c[q] < lv) if d > 0 else (c[q] > lv):
            k = q
            break
    return k, (c[k] / c[j] - 1) * d


def events(b, tfname, cfg=None, cap=None):
    _, L, N = cfg or CFG[tfname]
    cap = cap or CAP.get(tfname)
    h, l, c, t = (b[k].to_numpy(float) for k in ['h', 'l', 'c', 't'])
    n = len(b)
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    atr = pd.Series(tr).rolling(14).mean().to_numpy()
    out = []
    for side in (-1, 1):
        x = l if side < 0 else h
        conf, pivot = study.confirmed_pivots(x, L, side < 0)
        level = None
        for i in range(30, n - N - cap - 1):
            if conf[i - 1]:
                level = pivot[i - 1]
            if level is None or np.isnan(atr[i]):
                continue
            if not ((l[i] < level) if side < 0 else (h[i] > level)):
                continue
            lv, level = level, None
            buf = 0.1 * atr[i]
            if not ((c[i] < lv - buf) if side < 0 else (c[i] > lv + buf)):
                continue  # wick sweep, not a break
            j = next((i + q for q in range(1, N + 1) if (c[i + q] >= lv if side < 0 else c[i + q] <= lv)), None)
            if j is None:
                continue  # break held: no reclaim, no trade
            k, g = simulate(c, lv, side, j, cap)
            out.append(dict(tf=tfname, side='low' if side < 0 else 'high', t=t[j], gross=g, net=g - RT_FEE, hold=k - j,
                            exit='stop' if k - j < cap or (c[k] < lv if side < 0 else c[k] > lv) else 'cap'))
    return sorted(out, key=lambda r: r['t'])
