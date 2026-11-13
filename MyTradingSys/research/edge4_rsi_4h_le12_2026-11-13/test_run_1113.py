"""Fail-first tests for run_1113.py (PRE_REG.md in this folder). Expected numbers are hand-computed from FORMULAS.md s1 (Wilder RSI)
and the PRE_REG rules, not taken from the code under test."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "backtest"))
import fees  # noqa: E402
import run_1113 as R  # noqa: E402

H4 = 4 * 3600000
COST = 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13


def flat(n=40, price=100.0):
    t = np.arange(n) * H4
    o = np.full(n, price)
    return t, o, o + 1.0, o - 1.0, o.copy()


def test_rsi_hand_values_period3():
    # closes 10,11,10,12,11,13; deltas +1,-1,+2,-1,+2. seed: ag=1, al=1/3 -> RSI[3]=75;
    # i=4: ag=2/3, al=5/9, RS=1.2 -> 54.5454..; i=5: ag=10/9, al=10/27, RS=3 -> 75
    r = R.rsi(np.array([10, 11, 10, 12, 11, 13], float), period=3)
    assert np.isnan(r[:3]).all()
    assert abs(r[3] - 75.0) < 1e-9
    assert abs(r[4] - (100 - 100 / 2.2)) < 1e-9
    assert abs(r[5] - 75.0) < 1e-9


def test_signal_requires_daily_rsi_lt30():
    rs = np.array([50.0, 12.0, 50.0, 50.0])      # bar 1 is the setup, bar 2 closes higher than bar 1
    c = np.array([100.0, 90.0, 95.0, 95.0])
    ok = R.signals(rs, np.full(4, 29.9), c)
    assert list(ok) == [1]
    assert len(R.signals(rs, np.full(4, 30.0), c)) == 0         # daily RSI exactly 30 is NOT < 30
    assert len(R.signals(rs, np.full(4, 55.0), c)) == 0
    assert len(R.signals(rs, np.full(4, np.nan), c)) == 0       # no daily RSI yet = no signal


def test_signal_tf_rsi_le12_and_next_close_higher():
    c = np.array([100.0, 90.0, 95.0, 95.0])
    d = np.full(4, 20.0)
    assert list(R.signals(np.array([50, 12.0, 50, 50]), d, c)) == [1]       # <= 12 includes 12
    assert len(R.signals(np.array([50, 12.01, 50, 50]), d, c)) == 0
    assert len(R.signals(np.array([50, 5.0, 50, 50]), d, np.array([100.0, 90.0, 90.0, 95.0]))) == 0   # next close equal: not higher
    assert len(R.signals(np.array([50, 5.0, 50, 50]), d, np.array([100.0, 90.0, 85.0, 95.0]))) == 0   # next close lower


def test_daily_asof_has_no_lookahead():
    day = 86400000
    d_open = np.array([0, day, 2 * day])
    d_rsi = np.array([10.0, 20.0, 30.0])
    # 4h bar opening at day 1 + 20h closes exactly at 2*day: the daily bar of day 1 has just closed -> 20
    # 4h bar opening at day 1 + 16h closes at day 1 + 20h: day 1 not closed yet -> 10
    close_ms = np.array([day + 20 * 3600000, 2 * day, 2 * day + 4 * 3600000])
    out = R.daily_asof(close_ms, d_open, d_rsi)
    assert list(out) == [10.0, 20.0, 20.0]


def test_stop_is_signal_candle_low():
    t, o, h, l, c = flat()
    # setup bar S=5: low 90 (c 98); confirm bar 6 closes 99 (> 98), low 97 is ABOVE the stop. Entry = close[6] = 99, stop = low[S] = 90, R = 9.
    l[5], c[5], o[5] = 90.0, 98.0, 99.0
    o[6], c[6], l[6], h[6] = 98.0, 99.0, 97.0, 100.0
    # bar 7 dips to 91 (below the confirm-candle low 97, above the signal low 90): must NOT stop out
    o[7], l[7], c[7], h[7] = 99.0, 91.0, 99.0, 100.0
    # bar 8 trades to 90 (= signal low): stop hit
    o[8], l[8], c[8], h[8] = 99.0, 90.0, 95.0, 99.5
    out = R.outcomes(o, h, l, c, t, [5], H4, "3R")
    assert out["valid"][0]
    assert out["e"][0] == 6 and out["x"][0] == 8
    r_pct = (90.0 / 99.0 - 1.0) - COST
    assert abs(out["net_pct"][0] - r_pct) < 1e-12
    assert abs(out["net_r"][0] - r_pct / (9.0 / 99.0)) < 1e-9      # about -1.07 R


def test_target_2r_and_stop_first_on_same_bar():
    t, o, h, l, c = flat()
    l[5], c[5] = 90.0, 98.0
    o[6], c[6], l[6], h[6] = 98.0, 99.0, 97.0, 100.0           # entry 99, stop 90, R 9, 1R=108 2R=117 3R=126
    o[7], h[7], l[7], c[7] = 100.0, 118.0, 99.0, 117.0         # touches 2R
    out = R.outcomes(o, h, l, c, t, [5], H4, "2R")
    exp = (117.0 / 99.0 - 1.0) - COST
    assert out["x"][0] == 7 and abs(out["net_pct"][0] - exp) < 1e-12
    assert abs(out["net_r"][0] - exp / (9.0 / 99.0)) < 1e-9
    h[7], l[7] = 118.0, 89.0                                   # same bar also hits the stop: stop is taken first
    out = R.outcomes(o, h, l, c, t, [5], H4, "2R")
    assert abs(out["net_pct"][0] - ((90.0 / 99.0 - 1.0) - COST)) < 1e-12


def test_gap_through_stop_fills_at_open_and_time_exit():
    t, o, h, l, c = flat()
    l[5], c[5] = 90.0, 98.0
    o[6], c[6], l[6], h[6] = 98.0, 99.0, 97.0, 100.0
    o[7], h[7], l[7], c[7] = 85.0, 86.0, 84.0, 85.0            # opens below the stop
    out = R.outcomes(o, h, l, c, t, [5], H4, "1R")
    assert abs(out["net_pct"][0] - ((85.0 / 99.0 - 1.0) - COST)) < 1e-12
    # quiet market: time exit at the close of the 12th bar after entry (bar 6 + 12 = 18)
    t, o, h, l, c = flat()
    l[5], c[5] = 90.0, 98.0
    o[6], c[6], l[6], h[6] = 98.0, 99.0, 97.0, 100.0
    c[18] = 101.0
    h[18] = 102.0
    out = R.outcomes(o, h, l, c, t, [5], H4, "time")
    assert out["x"][0] == 18
    assert abs(out["net_pct"][0] - ((101.0 / 99.0 - 1.0) - COST)) < 1e-12


def test_gap_in_bars_invalidates_trade():
    t, o, h, l, c = flat()
    l[5], c[5] = 90.0, 98.0
    o[6], c[6], l[6], h[6] = 98.0, 99.0, 97.0, 100.0
    t[10:] += H4                                               # a missing bar inside the walk
    out = R.outcomes(o, h, l, c, t, [5], H4, "2R")
    assert not out["valid"][0]


def test_make_8h_pairs_aligned_bars():
    h8 = 8 * 3600000
    t = np.array([0, H4, h8, h8 + H4, 2 * h8 + H4])            # last bar is an orphan 4h (its 8h partner is missing)
    rows = np.array([[t[i], 10 + i, 20 + i, 5 + i, 11 + i, 1.0] for i in range(5)])
    out = R.make_8h(rows)
    assert out.shape == (2, 6)
    assert list(out[0]) == [0, 10, 21, 5, 12, 2.0]             # open of first, max high, min low, close of second, sum volume
    assert list(out[1]) == [h8, 12, 23, 7, 14, 2.0]


def test_pick_one_position():
    assert list(R.pick_one_position(np.array([1, 2, 5, 6]), np.array([4, 3, 8, 7]))) == [0, 2]


def test_bh_known_case():
    # p sorted .001 .01 .02 .5 with q=.10, m=4: thresholds .025 .05 .075 .10 -> first three significant
    assert list(R.bh([0.5, 0.01, 0.001, 0.02], q=0.10)) == [False, True, True, True]
