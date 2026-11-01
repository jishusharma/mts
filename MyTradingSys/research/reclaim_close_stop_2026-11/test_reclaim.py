"""Hand-built bars. Expected numbers computed by hand (simple returns, round-trip fee 0.001 = 2 x Binance taker 0.0005)."""
import os
import sys

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reclaim  # noqa: E402

RT = 0.001


def test_long_exit_on_close_back_below():
    # low break of level 100 at j-1; reclaim bar close 101 = entry; closes 103, 102, then 99.5 < 100 = exit
    c = np.array([98.0, 101.0, 103.0, 102.0, 99.5, 99.0])
    k, gross = reclaim.simulate(c, 100.0, -1, 1, 6)
    assert k == 4
    assert abs(gross - (99.5 / 101.0 - 1)) < 1e-12          # -0.0148515
    assert abs(gross - RT - (-0.0158515)) < 1e-6


def test_short_exit_on_close_back_above():
    c = np.array([102.0, 99.0, 98.0, 100.5, 101.0])
    k, gross = reclaim.simulate(c, 100.0, 1, 1, 6)
    assert k == 3
    assert abs(gross - (-(100.5 / 99.0 - 1))) < 1e-12        # -0.0151515


def test_horizon_cap_exit():
    c = np.array([98.0, 101.0, 102.0, 103.0, 90.0])
    k, gross = reclaim.simulate(c, 100.0, -1, 1, 2)          # cap 2 bars: exit at bar 3 close, the 90 never reached
    assert k == 3
    assert abs(gross - (103.0 / 101.0 - 1)) < 1e-12          # +0.0198020


def test_wick_close_equal_level_is_not_exit():
    c = np.array([98.0, 101.0, 100.0, 105.0])                # close exactly at the level stays in (exit needs strictly below)
    k, _ = reclaim.simulate(c, 100.0, -1, 1, 2)
    assert k == 3


def planted(n=80):
    rows = []
    for k in range(n):
        o, h, l, c = 100.0, 100.5, 99.5, 100.0
        if k == 40:
            l = 90.0                       # swing low (L=2), level 90, confirmed at bar 42
        if k == 50:
            o, h, l, c = 99.0, 99.5, 88.0, 88.0    # close beyond 90 - 0.1 ATR: break
        if k == 51:
            o, h, l, c = 88.0, 92.0, 87.5, 91.0    # close back inside: reclaim, entry 91
        if k == 52:
            c = 95.0
        if k == 53:
            o, h, l, c = 95.0, 95.5, 88.0, 89.0    # close back below 90: exit at 89
        rows.append((k * 14400.0, o, h, l, c, 10.0, 5.0))
    return pd.DataFrame(rows, columns=['t', 'o', 'h', 'l', 'c', 'v', 'tbv'])


def test_events_planted_reclaim():
    ev = reclaim.events(planted(), 'x', cfg=(240, 2, 3), cap=6)
    assert len(ev) == 1
    r = ev[0]
    assert r['side'] == 'low' and r['hold'] == 2
    assert abs(r['gross'] - (89.0 / 91.0 - 1)) < 1e-12      # -0.0219780
    assert abs(r['net'] - (89.0 / 91.0 - 1 - RT)) < 1e-12
    assert r['exit'] == 'stop'


def test_no_reclaim_no_trade():
    b = planted()
    b.loc[51:, 'c'] = 85.0
    assert reclaim.events(b, 'x', cfg=(240, 2, 3), cap=6) == []
