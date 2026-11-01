"""Spec-derived tests for conditions.py (card gpt-mutation-tests-sim-desk-conditions).

Every expected value is written by hand from the module docstring / function docstrings (conditions.py:1-18,
79, 114, 132, 137, 148, 160, 204) and DESIGN.md:42-43, never from the function bodies. Times are built with
datetime (UTC) so the calendar is independent of the code. All thresholds used here are OURS (test inputs).

MTS_COND_PATH=<file> loads a different conditions.py (used for the hand mutation runs in the report).
"""
import datetime as dt
import importlib.util
import math
import os
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
_path = os.environ.get('MTS_COND_PATH') or str(HERE / 'conditions.py')
_spec = importlib.util.spec_from_file_location('conditions_under_test', _path)
cd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cd)

MIN = 60_000


def ms(y, mo, d, h=0, mi=0):
    return int(dt.datetime(y, mo, d, h, mi, tzinfo=dt.timezone.utc).timestamp() * 1000)


def ident(bars, tf):
    """Test resampler: the bars are already at the requested timeframe."""
    return bars


def keep(c, t, side=None, **kw):
    t = np.asarray(t, np.int64)
    s = np.ones(len(t), int) if side is None else np.asarray(side)
    return cd.mask(cd.normalize(c), t, s, resample=kw.pop('resample', ident), **kw).tolist()


# ---------------------------------------------------------------- normalize / label (docstring lines 11-17, 79, 114)
def test_normalize_empty_and_defaults_mean_no_condition():
    # "an empty dict = no condition"; side both, ema off, empty days are the "any" values.
    assert cd.normalize({}) == {}
    assert cd.normalize(None) == {}
    assert cd.normalize({'side': 'both', 'ema_rel': 'off', 'days': ''}) == {}


def test_normalize_rejects_bad_input():
    for bad in ({'side': 'up'}, {'ema_rel': 'sideways'}, {'hour_from': 8},       # one hour bound only
                {'hour_from': 25, 'hour_to': 3}, {'atr_lo': 80, 'atr_hi': 20},  # from above to
                {'days': 'funday'}, {'days': '7'}):
        with pytest.raises(ValueError):
            cd.normalize(bad)


def test_normalize_all_seven_days_is_any():
    # "days: weekdays allowed ... empty = any": all seven allowed filters nothing, so it is not an active condition.
    assert 'days' not in cd.normalize({'days': 'mon,tue,wed,thu,fri,sat,sun'})
    assert cd.normalize({'days': '0,1'})['days'] == 'mon,tue'          # Monday=0


def test_label_matches_docstring_example():
    # docstring example: 'long, UTC 8-16, close above EMA50 of 60m bars'
    lab = cd.label(cd.normalize({'side': 'long', 'hour_from': 8, 'hour_to': 16, 'ema_rel': 'above',
                                 'ema_tf': 60, 'ema_len': 50}))
    assert lab.startswith('long')
    assert 'UTC 8-16' in lab
    assert 'close above EMA50 of 60m bars' in lab
    assert cd.label({}) == ''


# ---------------------------------------------------------------- side (line 11)
def test_side_filter():
    t = [ms(2026, 1, 5, 10)] * 3
    s = [1, -1, 1]                                  # +1 long, -1 short (OURS: sign convention of result['side'])
    assert keep({'side': 'long'}, t, s) == [True, False, True]
    assert keep({'side': 'short'}, t, s) == [False, True, False]
    assert keep({'side': 'both'}, t, s) == [True, True, True]


# ---------------------------------------------------------------- hour window (line 12): [from, to), wraps midnight
def test_hour_window_half_open():
    d = (2026, 1, 5)
    t = [ms(*d, 7, 59), ms(*d, 8, 0), ms(*d, 15, 59), ms(*d, 16, 0)]
    assert keep({'hour_from': 8, 'hour_to': 16}, t) == [False, True, True, False]


def test_hour_window_wraps_midnight():
    d = (2026, 1, 5)
    t = [ms(*d, 21, 59), ms(*d, 22, 0), ms(*d, 23, 30), ms(*d, 0, 30), ms(*d, 1, 59), ms(*d, 2, 0)]
    assert keep({'hour_from': 22, 'hour_to': 2}, t) == [False, True, True, True, True, False]


def test_hour_to_24_means_end_of_day():
    t = [ms(2026, 1, 5, 19, 59), ms(2026, 1, 5, 20, 0), ms(2026, 1, 5, 23, 59)]
    assert keep({'hour_from': 20, 'hour_to': 24}, t) == [False, True, True]


# ---------------------------------------------------------------- weekdays (line 15): Monday=0, UTC
def test_days_filter_utc_calendar():
    # 2026-01-05 is a Monday, 2026-01-10 a Saturday, 2026-01-11 a Sunday (datetime.weekday confirms below).
    t = [ms(2026, 1, 5, 0, 0), ms(2026, 1, 4, 23, 59), ms(2026, 1, 10, 12), ms(2026, 1, 11, 12)]
    assert [dt.datetime.fromtimestamp(x / 1000, dt.timezone.utc).weekday() for x in t] == [0, 6, 5, 6]
    assert keep({'days': 'mon'}, t) == [True, False, False, False]
    assert keep({'days': 'sat,sun'}, t) == [False, True, True, True]
    assert keep({'days': '5'}, t) == [False, False, True, False]


# ---------------------------------------------------------------- EMA (line 137) and closed bar index (line 132)
def test_ema_formula_by_hand():
    # alpha = 2/(3+1) = 0.5, seed = first close: 1 ; 0.5*2+0.5*1 = 1.5 ; 0.5*3+0.5*1.5 = 2.25 ; 0.5*0+0.5*2.25 = 1.125
    assert np.allclose(cd.ema(np.array([1.0, 2.0, 3.0, 0.0]), 3), [1.0, 1.5, 2.25, 1.125])


def test_closed_index():
    # bars of 5 minutes opening at 0, 5, 10 min. Close time = open + 5 min. Last bar with close <= touch.
    bars = np.array([[0, 1, 1, 1, 1], [5 * MIN, 1, 1, 1, 1], [10 * MIN, 1, 1, 1, 1]], float)
    touch = np.array([5 * MIN - 1, 5 * MIN, 10 * MIN - 1, 10 * MIN, 99 * MIN])
    assert list(cd._closed_index(bars, touch, 5)) == [-1, 0, 0, 1, 2]


def _bars_from_closes(closes, tf_min=60, t0=None):
    t0 = ms(2026, 1, 5) if t0 is None else t0
    rows = []
    for i, c in enumerate(closes):
        rows.append([t0 + i * tf_min * MIN, c, c + 0.5, c - 0.5, c])
    return np.array(rows, float)


def test_ema_trend_above_below_and_causal():
    # 30 hourly closes rising 100..129, then one bar closing at 50.
    # While the rise is the last CLOSED bar, close > EMA (an EMA of a rising series lags below it).
    # Once the 50 bar has closed, close 50 < EMA (EMA is a weighted mean of values >= 100 and 50, so > 50).
    closes = [100.0 + i for i in range(30)] + [50.0]
    bars = _bars_from_closes(closes)
    t0 = ms(2026, 1, 5)
    inside_last = t0 + 30 * 60 * MIN + 30 * MIN       # during bar 30: last closed is bar 29 (close 129)
    after_last = t0 + 31 * 60 * MIN                   # bar 30 has closed (close 50)
    c_above = {'ema_rel': 'above', 'ema_tf': 60, 'ema_len': 5}
    c_below = {'ema_rel': 'below', 'ema_tf': 60, 'ema_len': 5}
    t = [inside_last, after_last]
    assert keep(c_above, t, minute_bars=bars) == [True, False]
    assert keep(c_below, t, minute_bars=bars) == [False, True]


def test_ema_above_is_strict():
    # Flat closes: EMA of a constant series is that constant, so close == EMA. "above" means strictly above:
    # a close sitting on the EMA is not above it, so no trade. (Equal-vs-"below" is not stated; not tested.)
    bars = _bars_from_closes([100.0] * 30)
    t = [ms(2026, 1, 5) + 30 * 60 * MIN]
    assert keep({'ema_rel': 'above', 'ema_len': 5}, t, minute_bars=bars) == [False]


def test_ema_needs_closed_history():
    # A touch before any bar has closed has no "last closed close": no trade either way.
    bars = _bars_from_closes([100.0 + i for i in range(30)])
    t = [ms(2026, 1, 5, 0, 30)]
    assert keep({'ema_rel': 'above', 'ema_len': 5}, t, minute_bars=bars) == [False]
    assert keep({'ema_rel': 'below', 'ema_len': 5}, t, minute_bars=bars) == [False]


# ---------------------------------------------------------------- ATR (line 148) and percentile band (line 14)
def test_atr_simple_mean_nan_until_enough():
    # (t, o, h, l, c). True range = max(h-l, |h-prev c|, |l-prev c|).
    bars = np.array([[0, 10, 11, 9, 10],      # TR 2 (first bar: h-l)
                     [1, 10, 12, 10, 11],     # TR max(2, 2, 0) = 2
                     [2, 11, 11, 7, 8],       # TR max(4, 0, 4) = 4
                     [3, 8, 14, 13, 13]], float)  # TR max(1, 6, 5) = 6
    a = cd.atr(bars, 2)
    assert math.isnan(a[0])
    assert np.allclose(a[1:], [2.0, 3.0, 5.0])     # (2+2)/2, (2+4)/2, (4+6)/2
    assert np.isnan(cd.atr(bars, 5)).all()


def test_atr_percentile_band():
    # Ranges widen every bar, so the ATR of the last closed bar is the largest in its look-back: percentile 100.
    # A band 90-100 keeps it, a band 0-50 drops it. Before ATR exists (too few bars) there is no trade.
    n = 40
    t0 = ms(2026, 1, 5)
    bars = np.array([[t0 + i * 60 * MIN, 100, 100 + 0.1 * (i + 1), 100 - 0.1 * (i + 1), 100] for i in range(n)], float)
    late = t0 + n * 60 * MIN
    early = t0 + 2 * 60 * MIN                           # only 2 bars closed, ATR14 not defined yet
    base = {'atr_tf': 60, 'atr_len': 14, 'atr_win': 20}
    assert keep(dict(base, atr_lo=90, atr_hi=100), [late, early], minute_bars=bars) == [True, False]
    assert keep(dict(base, atr_lo=0, atr_hi=50), [late, early], minute_bars=bars) == [False, False]
    # Exactly at the band edge: band [100, 100] is inclusive of 100.
    assert keep(dict(base, atr_lo=100, atr_hi=100), [late], minute_bars=bars) == [True]


# ---------------------------------------------------------------- layer B (lines 16-17)
def test_layer_b_within_n_bars_before_touch():
    # layer_b_bars 4 x 60m = a 4-hour look-back before the touch.
    touch = ms(2026, 1, 5, 12)
    c = {'layer_b': 'rsi', 'layer_b_bars': 4, 'layer_b_tf': 60}
    assert keep(c, [touch], b_times=[ms(2026, 1, 5, 11)]) == [True]          # 1 h before
    assert keep(c, [touch], b_times=[ms(2026, 1, 5, 8, 1)]) == [True]        # 3 h 59 m before
    assert keep(c, [touch], b_times=[ms(2026, 1, 5, 7, 59)]) == [False]      # 4 h 1 m before: too old
    assert keep(c, [touch], b_times=[ms(2026, 1, 5, 12, 1)]) == [False]      # after the touch: not causal
    assert keep(c, [touch], b_times=[]) == [False]                            # B never fired
    assert keep({'layer_b': 'rsi', 'layer_b_bars': 1, 'layer_b_tf': 60}, [touch],
                b_times=[ms(2026, 1, 5, 11, 30), ms(2026, 1, 5, 9)]) == [True]


# ---------------------------------------------------------------- combined + apply (line 204)
def test_conditions_combine_with_and():
    d = (2026, 1, 5)                                # Monday
    t = [ms(*d, 9), ms(*d, 9), ms(*d, 20), ms(2026, 1, 6, 9)]
    s = [1, -1, 1, 1]
    assert keep({'side': 'long', 'hour_from': 8, 'hour_to': 16, 'days': 'mon'}, t, s) == [True, False, False, False]


def test_apply_subsets_trades_keeps_day_universe():
    res = {'r': np.array([1.0, -1.0, 2.0]), 'side': [1, -1, 1], 'refs': ['a', 'b', 'c'],
           'all_days': [10, 11, 12], 'name': 'x'}
    out = cd.apply(res, np.array([True, False, True]))
    assert out['r'].tolist() == [1.0, 2.0]
    assert list(out['side']) == [1, 1]
    assert out['refs'] == ['a', 'c']
    assert out['all_days'] == [10, 11, 12]
    assert out['name'] == 'x'
