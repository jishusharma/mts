"""Tests for the big-candle story study: story labels, top-trader class, point-in-time z, outcomes, weekly streak, Wilson."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study as st  # noqa: E402


def test_story_label_eight_stories_and_zero_or_missing_drops():
    got = {st.story_label(p, o, d) for p in (1, -1) for o in (1, -1) for d in (1, -1)}
    assert got == {'UP|UP|BUY', 'UP|UP|SELL', 'UP|DOWN|BUY', 'UP|DOWN|SELL', 'DOWN|UP|BUY', 'DOWN|UP|SELL', 'DOWN|DOWN|BUY', 'DOWN|DOWN|SELL'}
    # the 11-04 02:55 flush: price down, new shorts (OI up), sellers hit (delta negative)
    assert st.story_label(-0.006, 114.0, -1970.0) == 'DOWN|UP|SELL'
    # the 11-04 15:00 rally: price up, OI down (short covering), buyers lift
    assert st.story_label(0.0104, -730.0, 2849.0) == 'UP|DOWN|BUY'
    assert st.story_label(0.0, 5.0, 5.0) is None and st.story_label(1.0, None, 5.0) is None and st.story_label(1.0, float('nan'), 5.0) is None


def test_top_trader_class_four_classes_flat_and_missing():
    assert st.tt_class(0.08, -0.05) == 'SL'      # size long, accounts short (the 11-04 rally hour)
    assert st.tt_class(-0.08, 0.05) == 'SS'
    assert st.tt_class(0.03, 0.04) == 'BU' and st.tt_class(-0.03, -0.04) == 'BD'
    assert st.tt_class(0.0005, 0.05) == 'FLAT' and st.tt_class(0.05, -0.0019) == 'FLAT'
    assert st.tt_class(None, 0.05) == 'NA' and st.tt_class(float('nan'), 0.05) == 'NA'


def test_wilson_known_values_and_empty():
    lo, hi = st.wilson(50, 100)
    assert abs(lo - 0.4038) < 1e-3 and abs(hi - 0.5962) < 1e-3
    assert st.wilson(0, 0) == (0.0, 0.0)
    lo, hi = st.wilson(1, 1)
    assert 0.2 < lo < 0.22 and hi == 1.0


def test_trailing_z_uses_prior_bars_only():
    rng = np.random.RandomState(1)
    x = rng.normal(0, 1, 400)
    x[300] = 12.0
    z = st.trailing_z(x, 200)
    assert z[300] > 8 and np.isnan(z[100])
    y = x.copy()
    y[301:] += 50.0                               # change only the FUTURE of bar 300
    assert st.trailing_z(y, 200)[300] == z[300]
    y2 = x.copy()
    y2[300] = 0.0                                  # a spike inside the window changes the z of the bar after it
    assert st.trailing_z(x, 200)[301] != st.trailing_z(y2, 200)[301]


def _grid(closes, opens=None):
    n = len(closes)
    S = {k: np.full(n, np.nan) for k in ('o', 'h', 'l', 'c', 'v', 'tb', 'oi', 'tpos', 'tacc', 'gacc')}
    S['c'][:] = closes
    S['o'][:] = closes if opens is None else opens
    S['t0'], S['n'] = 0, n
    return S


def test_outcomes_continue_and_undone_by_horizon():
    c = np.full(400, 100.0)
    c[10] = 101.0                                  # event bar closes 101, started at 100
    c[22] = 102.0                                  # 1h later: higher (continues, not undone)
    c[58] = 99.5                                   # 4h later: back below the start price 100 (undone)
    S = _grid(c)
    up = st.outcomes(S, 10, 100.0, 1)
    assert up['1h'] == (True, False) and up['4h'] == (False, True)
    dn = st.outcomes(S, 10, 100.0, -1)             # the same path read as a DOWN event
    assert dn['1h'] == (False, True) and dn['4h'] == (True, False)
    assert st.outcomes(S, 300, 100.0, 1)['24h'] is None                       # 288 bars ahead runs off the data: excluded, never padded


def test_weekly_streak_counts_red_run_before_the_week():
    wk = 7 * 288
    cols = ['G', 'R', 'R', 'R', 'R', 'G']
    n = wk * len(cols)
    c, o = np.zeros(n), np.zeros(n)
    for k, col in enumerate(cols):
        o[k * wk:(k + 1) * wk] = 100.0
        c[k * wk:(k + 1) * wk] = 101.0 if col == 'G' else 99.0
    S = _grid(c, o)
    col, before = st.weekly(S)
    assert col == cols
    assert before[5] == ('R', 4) and st.streak_group(*before[5]) == 'R3+'
    assert before[2] == ('R', 1) and st.streak_group(*before[2]) == 'R1-2'
    assert before[0] is None and st.streak_group(None, 0) is None
    assert before[len(cols)] == ('G', 1)           # the trailing entry is the current partial week
