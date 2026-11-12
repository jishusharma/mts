"""Synthetic checks for rules.py. No F: data needed. The look-ahead tests fail if rules.SHIFT is non-zero (a wrong version)."""
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rules  # noqa: E402


def setup_function(_):
    rules.SHIFT = 0


def teardown_function(_):
    rules.SHIFT = 0


def flat(price, vol, n):
    return np.full(n, price, float), np.full(n, vol, float)


def t1_synth():
    """8 profile days: 100 plateau and 101 plateau with thin transit; day 8: rise 100 -> 101 from minute 300."""
    days = 9
    p = np.full(days * 1440, 100.0)
    v = np.full(days * 1440, 10.0)
    for d in range(days):
        a = d * 1440
        for m in range(600, 620):
            p[a + m] = 100.0 + 0.05 * (m - 599)
            v[a + m] = 0.01
        p[a + 620:a + 1220] = 101.0
        for m in range(1220, 1240):
            p[a + m] = 101.0 - 0.05 * (m - 1219)
            v[a + m] = 0.01
    a = 8 * 1440
    p[a:a + 300] = 100.0
    v[a:a + 300] = 10.0
    for m in range(300, 320):
        p[a + m] = 100.0 + 0.05 * (m - 299)
        v[a + m] = 0.01
    p[a + 320:] = 101.0
    v[a + 320:] = 10.0
    return p, p.copy(), p.copy(), p.copy(), v   # o, h, l, c all equal: flat 1m bars


def check_t1():
    o, h, l, c, v = t1_synth()
    trades, drop = rules.run_t1(o, h, l, c, v, 8, 8)
    assert trades, drop
    t = trades[0]
    trigger_bar_close_idx = 8 * 1440 + 305          # the 5m bar 300-304 closes thin; next 1m bar is 305
    assert t["side"] == 1
    assert t["entry_idx"] == trigger_bar_close_idx   # next open, not inside the trigger bar (look-ahead check)
    assert t["entry_px"] == o[trigger_bar_close_idx]
    assert t["reason"] == "target" and t["exit_px"] <= 101.0 and t["exit_px"] > t["entry_px"]
    assert abs(t["net_bp"] - (t["gross_bp"] - 10.0)) < 1e-9


def test_t1_trigger_and_entry_after_bar_close():
    check_t1()


def test_t1_lookahead_shift_is_caught():
    rules.SHIFT = -5                                  # entry at the trigger bar's own open = look-ahead
    with pytest.raises(AssertionError):
        check_t1()


def t2_synth(extra_close_above=False):
    """Hours 0-29 range 100..101 (width 1 %), event hour 30 closes 99 on 3x volume, hours 31-32 below, hour 33 wicks to 100.2."""
    hrs = 100
    n = hrs * 60
    o, h, l, c = (np.full(n, 100.5) for _ in range(4))
    v = np.full(n, 1.0)
    for hr in range(hrs):
        a = hr * 60
        o[a:a + 60] = c[a:a + 60] = 100.5
        h[a:a + 60] = 101.0
        l[a:a + 60] = 100.0
    def setb(hr, op, hi, lo, cl, vol):
        a = hr * 60
        o[a], c[a + 59] = op, cl
        o[a + 1:a + 60] = op
        c[a:a + 59] = op
        h[a:a + 60] = hi
        l[a:a + 60] = lo
        v[a:a + 60] = vol / 60.0
        o[a] = op
    for hr in range(30):
        setb(hr, 100.5, 101.0, 100.0, 100.5, 10.0)
    setb(30, 100.2, 100.3, 98.9, 99.0, 30.0)
    setb(31, 99.0, 99.2, 98.8, 98.9, 10.0)
    setb(32, 98.9, 99.0, 98.7, 98.8, 10.0)
    setb(33, 98.8, 100.2, 98.8, 99.5 if not extra_close_above else 100.4, 10.0)
    for hr in range(34, hrs):
        setb(hr, 99.5, 99.6, 98.0, 99.0, 10.0)
    return o, h, l, c, v


def check_t2():
    o, h, l, c, v = t2_synth()
    trades, drop = rules.run_t2(o, h, l, c, v, 24, 36)
    assert len(trades) == 1, drop
    t = trades[0]
    assert t["side"] == -1
    assert t["entry_idx"] == 34 * 60                  # open after the retest hour closes
    assert abs(t["stop"] - 100.3 * 1.002) < 1e-9      # highest high hours 30..33 is 100.3 (event bar) / 100.2
    assert abs(t["target"] - 98.7) < 1e-9             # lowest low since the breakdown
    assert t["reason"] == "target" and t["exit_px"] == 98.7  # hour 34+ lows reach 98.0


def test_t2_retest_short_entry_stop_target():
    check_t2()


def test_t2_lookahead_shift_is_caught():
    rules.SHIFT = -60                                 # entry at the trigger hour's own open
    with pytest.raises(AssertionError):
        check_t2()


def test_t2_reclaim_cancels_setup():
    o, h, l, c, v = t2_synth(extra_close_above=True)  # retest hour closes above the range low: no trade
    trades, drop = rules.run_t2(o, h, l, c, v, 24, 36)
    assert trades == [] and drop["reclaimed"] == 1


def test_walk_stop_before_target_same_bar():
    o = np.array([100.0, 100.0]); h = np.array([102.0, 100.0]); l = np.array([98.0, 100.0]); c = np.array([100.0, 100.0])
    xi, xp, why = rules.walk(o, h, l, c, 0, 1, 99.0, 101.0, 2)   # bar spans both stop and target
    assert why == "stop" and xp == 99.0
    xi, xp, why = rules.walk(o, h, l, c, 0, -1, 101.0, 99.0, 2)  # short mirror: also stop first
    assert why == "stop" and xp == 101.0


def test_walk_missing_bar_dropped():
    o = np.array([100.0, np.nan]); a = o.copy()
    assert rules.walk(o, a, a, a, 0, 1, 99.0, 101.0, 2) is None
