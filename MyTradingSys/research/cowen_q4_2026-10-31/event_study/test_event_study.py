"""Cowen band daily event study (run_event_study.py), PRE-REG.md next to it.

Expected numbers are worked out on paper from the PRE-REG and FORMULAS 18.5 to 18.7, not taken from the code:
band from completed weekly closes, ATR14, stop / target / timeout fills with fees from backtest/fees.py, the day-block
bootstrap draw, the placebo shift table, the verdict rule, the 2024-06-30 data seal.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_event_study as es  # noqa: E402

DAY = 86400000
MON = 19079      # 2022-03-28 UTC, a Monday


def test_fee_is_the_single_source():
    from MyTradingSys.backtest import fees
    assert fees.BINANCE_TAKER == 0.0005 and es.FEE == fees.BINANCE_TAKER


def _weekly_const(n_weeks, close_of=lambda w: w + 1.0):
    n = 7 * n_weeks
    t = (MON + np.arange(n)) * DAY
    c = np.array([close_of(i // 7) for i in range(n)], float)
    return np.column_stack([t, c, c, c, c])


def test_band_hand_computed_from_completed_weeks():
    """Weekly closes c_w = w+1. Week 21 uses week 20: SMA20 = mean(2..21) = 11.5, EMA21 = mean(1..21) = 11.
    Week 25 uses week 24: SMA20 = mean(6..25) = 15.5, EMA21 = 25 - 10 = 15 (each week adds +1)."""
    f = es.features(_weekly_const(27))
    wk = lambda w: slice(7 * w, 7 * w + 7)                       # noqa: E731
    assert np.isnan(f['top'][wk(0)]).all() and np.isnan(f['top'][wk(20)]).all()
    assert f['top'][wk(21)] == pytest.approx([11.5] * 7) and f['bottom'][wk(21)] == pytest.approx([11.0] * 7)
    assert f['top'][wk(25)] == pytest.approx([15.5] * 7) and f['bottom'][wk(25)] == pytest.approx([15.0] * 7)


def test_unfinished_week_never_enters_the_band():
    a = es.features(_weekly_const(27))
    b = es.features(_weekly_const(27, lambda w: 1000.0 if w == 25 else w + 1.0))
    w25 = slice(7 * 25, 7 * 25 + 7)
    assert b['top'][w25] == pytest.approx(a['top'][w25]) and b['bottom'][w25] == pytest.approx(a['bottom'][w25])
    assert b['top'][7 * 26] > 100 > a['top'][7 * 26]


def test_atr14_hand_computed_and_sma50():
    # every bar: low 98, high 102 (range 4); closes alternate 100, 101 so gaps never exceed the range -> TR = 4
    n = 60
    c = np.where(np.arange(n) % 2 == 0, 100.0, 101.0)
    d = np.column_stack([(MON + np.arange(n)) * DAY, c, np.full(n, 102.0), np.full(n, 98.0), c])
    f = es.features(d)
    assert np.isnan(f['atr'][:14]).all() and f['atr'][14] == pytest.approx(4.0) and f['atr'][59] == pytest.approx(4.0)
    # SMA50 at bar 49 = mean of 25 x 100 and 25 x 101 = 100.5
    assert f['sma50'][49] == pytest.approx(100.5) and np.isnan(f['sma50'][48])
    # bar 30 gaps up: low 110 high 112, previous close 101 -> TR = 112 - 101 = 11
    d2 = d.copy()
    d2[30, 1:] = [111, 112, 110, 111]
    f2 = es.features(d2)
    # ATR at bar 30: mean of TR bars 17..30 = (13 x 4 + 11) / 14 = 63/14
    assert f2['atr'][30] == pytest.approx(63.0 / 14.0)


def test_net_r_formula_matches_formulas_18_5():
    assert es.net_r(1, 100.0, 104.0, 2.0) == pytest.approx((4 - 0.05 - 0.052) / 2)       # 1.949
    assert es.net_r(1, 100.0, 98.0, 2.0) == pytest.approx((-2 - 0.05 - 0.049) / 2)       # -1.0495
    assert es.net_r(-1, 100.0, 96.0, 2.0) == pytest.approx((4 - 0.05 - 0.048) / 2)       # 1.951
    assert es.net_r(1, 100.0, 100.5, 2.0) == pytest.approx((0.5 - 0.05 - 0.05025) / 2)   # 0.19987


def _bars(rows, t0=MON):
    return np.column_stack([(t0 + np.arange(len(rows))) * DAY, np.asarray(rows, float)])


def _pad(rows, n=40):
    return rows + [(100, 101, 99, 100)] * n


def test_simulate_long_target_stop_gap_timeout_and_both_in_bar():
    # entry bar 1 at open 100, R 2: stop 98, target 104
    d = _bars(_pad([(100, 100, 100, 100), (100, 103, 99, 102), (102, 105, 101, 104)]))
    assert es.simulate(d, 1, 1, 2.0) == (2, 104.0, 'target')
    d = _bars(_pad([(100, 100, 100, 100), (100, 103, 99, 99), (99, 100, 97, 98)]))
    assert es.simulate(d, 1, 1, 2.0) == (2, 98.0, 'stop')
    d = _bars(_pad([(100, 100, 100, 100), (100, 101, 99, 100), (97, 98, 96, 97)]))        # opens at 97, below the stop: fill at the open
    assert es.simulate(d, 1, 1, 2.0) == (2, 97.0, 'stop')
    d = _bars(_pad([(100, 100, 100, 100), (100, 106, 97, 100)]))                           # both touched in one bar: stop first
    assert es.simulate(d, 1, 1, 2.0) == (1, 98.0, 'stop')
    d = _bars(_pad([(100, 100, 100, 100), (100, 101, 99, 100)]))                           # never touched: close of bar entry+29
    assert es.simulate(d, 1, 1, 2.0) == (30, 100.0, 'timeout')


def test_simulate_short_mirrored_and_horizon_past_data_is_dropped():
    d = _bars(_pad([(100, 100, 100, 100), (100, 101, 96, 97)]))                            # short: stop 102, target 96 touched
    assert es.simulate(d, 1, -1, 2.0) == (1, 96.0, 'target')
    d = _bars([(100, 100, 100, 100)] + [(100, 101, 99, 100)] * 29)                          # entry bar 1 needs bars up to index 30; data ends at 29
    assert es.simulate(d, 1, 1, 2.0) is None
    d = _bars([(100, 100, 100, 100)] + [(100, 101, 99, 100)] * 30)
    assert es.simulate(d, 1, 1, 2.0)[2] == 'timeout'


def _feat(rows, top=100.0, bottom=90.0, sma=None, atr=2.0):
    d = _bars(rows)
    n = len(rows)
    return {'d': d, 'top': np.full(n, float(top)), 'bottom': np.full(n, float(bottom)),
            'sma50': np.full(n, np.nan) if sma is None else np.asarray(sma, float), 'atr': np.full(n, float(atr))}


def test_events_lose_enters_next_open_and_net_r():
    # bar 3 is the first close below 90 (LOSE short); next open 88 -> entry 88, R 2: stop 90, target 84. Bar 4 low 83 hits the target.
    rows = _pad([(110, 112, 109, 110), (110, 111, 99, 108), (108, 109, 94, 95), (95, 96, 87, 88), (88, 89, 83, 85)], 40)
    ev = es.events(_feat(rows), 'LOSE')
    assert len(ev) == 1
    e = ev[0]
    assert (e['i'], e['e'], e['exit_i'], e['reason'], e['entry'], e['exit']) == (3, 4, 4, 'target', 88.0, 84.0)
    assert e['net_r'] == pytest.approx((4 - 0.0005 * 88 - 0.0005 * 84) / 2)
    assert e['gross_r'] == pytest.approx(2.0) and e['year'] == 2022


def test_events_skip_signal_while_previous_trade_is_open():
    # ATR 5. LOSE fires at bar 1 (close 88 < 90); entry bar 2 open 88: stop 93, target 78. Bar 2 closes 91 (high 92 < 93, trade open);
    # bar 3 closes 86: first close below again, previous close 91 >= 90 -> second signal, skipped because trade 1 is open until bar 5 (low 77).
    rows = [(110, 112, 109, 110), (95, 96, 87, 88), (88, 92, 87, 91), (91, 92, 86, 86), (86, 87, 85, 86), (86, 87, 77, 78)]
    ev = es.events(_feat(_pad(rows, 40), atr=5.0), 'LOSE')
    assert len(ev) == 1 and ev[0]['i'] == 1 and ev[0]['exit_i'] == 5 and ev[0]['reason'] == 'target' and ev[0]['exit'] == 78.0
    # bar 2 reaches 94 >= stop 93: trade 1 ends at bar 2, the signal at bar 3 is taken (entry bar 4 open 86)
    rows[2] = (88, 94, 87, 91)
    ev2 = es.events(_feat(_pad(rows, 40), atr=5.0), 'LOSE')
    assert [x['i'] for x in ev2] == [1, 3] and ev2[0]['reason'] == 'stop' and ev2[0]['exit'] == 93.0 and ev2[1]['entry'] == 86.0


def test_events_bounce_long_uses_band_top_signal():
    rows = _pad([(110, 112, 109, 110), (110, 111, 99, 108), (108, 114, 107, 112)], 40)    # bar 1 dips to 100, closes above 90: BOUNCE; entry bar 2 open 108
    ev = es.events(_feat(rows), 'BOUNCE')
    assert ev[0]['i'] == 1 and ev[0]['entry'] == 108.0 and ev[0]['side'] == 1
    assert ev[0]['reason'] == 'target' and ev[0]['exit'] == 112.0                          # target 108 + 2 x 2


def test_placebo_shift_table_and_shifted_features():
    assert es.PLACEBO_D == (-3, -2, -1, -0.5, 0.5, 1, 2, 3)
    assert [es.placebo_d(w) for w in (0, 1, 4, 7, 8, 15)] == [-3, -2, 0.5, 3, -3, 3]
    f = _feat(_pad([(100, 101, 99, 100)], 9), atr=2.0)
    wk = es.week_index(f['d'][:, 0])
    g = es.shifted(f)
    expect = np.array([es.placebo_d(int(w)) for w in wk]) * 2.0
    assert g['top'] == pytest.approx(f['top'] + expect) and g['bottom'] == pytest.approx(f['bottom'] + expect)
    assert f['top'][0] == 100.0                                                             # original untouched


def test_bootstrap_worked_example_formulas_18_7():
    by_day = [np.array([1.0, 3.0]), np.array([-2.0])]        # day A events 1, 3; day B event -2
    assert es.stat_of_picks(by_day, [0, 0]) == pytest.approx(2.0)
    assert es.stat_of_picks(by_day, [1, 1]) == pytest.approx(-2.0)
    assert es.stat_of_picks(by_day, [0, 1]) == pytest.approx(2.0 / 3.0)


def test_bootstrap_range_is_deterministic_and_inside_extremes():
    ev = [{'day': k // 2, 'net_r': float(r)} for k, r in enumerate([1, 3, -2, 0.5, 0.5, 2, -1, 1])]
    lo, hi = es.boot_mean(ev)
    assert (lo, hi) == es.boot_mean(ev)
    assert -2 <= lo <= hi <= 3
    mean = sum(x['net_r'] for x in ev) / len(ev)
    assert lo <= mean <= hi
    dlo, dhi = es.boot_diff(ev, ev)                          # a stream against itself: difference is exactly 0
    assert dlo == pytest.approx(0.0) and dhi == pytest.approx(0.0)


def test_verdict_rule_from_pre_reg():
    assert es.verdict(25, 0.1, 0.9, 0.1, 0.9) == 'NOT ENOUGH DATA'
    assert es.verdict(30, 0.1, 0.9, 0.1, 0.9) == 'BAND SIGNAL'
    assert es.verdict(30, 0.1, 0.9, -0.1, 0.9) == 'NO EDGE SHOWN'
    assert es.verdict(40, -0.9, -0.1, -0.5, 0.2) == 'NEGATIVE'
    assert es.verdict(40, -0.2, 0.3, -0.5, 0.2) == 'NO EDGE SHOWN'


def test_data_seal_drops_bars_after_2024_06_30():
    t_ok = int(np.datetime64('2024-06-30', 'ms').astype(np.int64))
    t_bad = int(np.datetime64('2024-07-01', 'ms').astype(np.int64))
    text = f"{t_ok},1,2,0.5,1.5,10,{t_ok + DAY - 1},0,0,0,0,0\n{t_bad},1,2,0.5,1.5,10,{t_bad + DAY - 1},0,0,0,0,0\n"
    a = es.parse_klines(text)
    assert a.shape == (1, 5) and int(a[0, 0]) == t_ok
    assert es.LAST_DAY_MS == t_ok


def test_year_split_and_stats_shape():
    ev = [{'day': 1, 'net_r': 1.0, 'gross_r': 1.1, 'year': 2018, 'reason': 'target'},
          {'day': 2, 'net_r': -1.0, 'gross_r': -0.9, 'year': 2018, 'reason': 'stop'},
          {'day': 3, 'net_r': 0.5, 'gross_r': 0.6, 'year': 2019, 'reason': 'timeout'}]
    s = es.stats(ev)
    assert s['n'] == 3 and s['wins'] == 2 and s['hit'] == pytest.approx(1 / 3) and s['stop'] == pytest.approx(1 / 3)
    assert s['mean_net'] == pytest.approx(0.5 / 3) and s['mean_gross'] == pytest.approx(0.8 / 3)
    assert es.by_year(ev) == {2018: (2, 0.0), 2019: (1, 0.5)}
