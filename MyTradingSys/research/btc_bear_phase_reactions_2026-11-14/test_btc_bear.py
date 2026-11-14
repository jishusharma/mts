"""Small tests for btc_bear. Expected values are worked out by hand, not from the code under test."""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import btc_bear as b


def test_streak_exactly_five_counts_and_four_does_not():
    red = [False, True, True, True, True, True, False, True, True, True, True, False]
    # run of 5 at idx 1..5 qualifies; run of 4 at idx 7..10 does not
    assert b.find_streaks(red, 5) == [(1, 5)]
    assert b.find_streaks(red, 4) == [(1, 5), (7, 10)]


def test_streak_runs_at_edges_and_length():
    red = [True] * 6 + [False] + [True] * 5
    assert b.find_streaks(red, 5) == [(0, 5), (7, 11)]
    assert [e - s + 1 for s, e in b.find_streaks(red, 5)] == [6, 5]


def test_red_means_close_below_open():
    w = pd.DataFrame({"open": [10, 10, 10], "close": [9, 10, 11]})
    assert list(b.red_flags(w)) == [True, False, False]  # a flat week is not red


def test_fall_trigger_boundary():
    base = [100.0] * 8
    assert b.fall_triggers(np.array(base + [82.0]), 8, 0.18) == [8]       # exactly -18% counts
    assert b.fall_triggers(np.array(base + [82.5]), 8, 0.18) == []        # -17.5% does not
    # reference is the highest close of the PRIOR 8 weeks, not including the week itself
    assert b.fall_triggers(np.array(base[:7] + [120.0] + [98.0]), 8, 0.18) == [8]  # 98 <= 0.82*120 = 98.4


def test_fractal_low_needs_two_higher_bars_each_side():
    low = [5, 4, 3, 4, 5, 4, 4, 6, 7]
    assert b.fractal_lows(low) == [2]  # idx 5/6 are not strict fractals (equal neighbours)


def test_weekly_monday_start_and_incomplete_week():
    idx = pd.date_range("2026-11-02", periods=9, freq="D")  # Mon 11-02 .. Tue 11-10
    d = pd.DataFrame({"open": range(9), "high": range(1, 10), "low": range(9), "close": range(1, 10),
                      "volume": 1.0}, index=idx)
    w = b.to_weekly(d)
    assert list(w.index) == [pd.Timestamp("2026-11-02"), pd.Timestamp("2026-11-09")]
    assert list(w["complete"]) == [True, False]
    assert w.iloc[0]["open"] == 0 and w.iloc[0]["close"] == 7


def test_cycle_phase_labels():
    assert b.cycle_phase("2025-12-01")[0] == "post-peak bear"
    assert b.cycle_phase("2021-03-01")[0] == "post-halving bull"
    assert b.cycle_phase("2019-06-01")[0] == "post-bottom base"


def test_round_steps():
    assert b.round_steps(69000) == (5000, 10000)
    assert b.round_steps(6900) == (500, 1000)
