import sys
sys.dont_write_bytecode = True
"""Tests for vp_pivot_probe.py. Expected numbers come ONLY from the worked examples in layers/FORMULAS.md section 18
(18.1 A/B/C, 18.2 pivots, 18.5 net_R, 18.7 bootstrap) plus section 12 (ATR worked example) and small hand-made series
whose numbers are derived in the comments."""
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vp_pivot_probe as P  # noqa: E402


# ---------------------------------------------------------------- 18.1 profile
def test_profile_worked_a():
    # bars (l,h,v) = (0,2,6), (1,3,4), (1,2,10); w = 1 -> bins [3,15,2]; POC bin1 -> poc 1.5, val 1.0, vah 2.0
    r = P.build_profile(np.array([0.0, 1.0, 1.0]), np.array([2.0, 3.0, 2.0]), np.array([6.0, 4.0, 10.0]), 1.0)
    assert r["poc_price"] == pytest.approx(1.5)
    assert r["val"] == pytest.approx(1.0)
    assert r["vah"] == pytest.approx(2.0)


def test_profile_worked_b():
    # point-mass bars at bin centres, volumes [1,2,10,4,3] -> POC bin2 (2.5), val 2.0, vah 4.0
    centres = np.array([0.5, 1.5, 2.5, 3.5, 4.5])
    vols = np.array([1.0, 2.0, 10.0, 4.0, 3.0])
    r = P.build_profile(centres, centres, vols, 1.0)
    assert r["poc_price"] == pytest.approx(2.5)
    assert r["val"] == pytest.approx(2.0)
    assert r["vah"] == pytest.approx(4.0)


def test_profile_worked_c_tie_goes_lower():
    # volumes [3,10,3]: tie vl == vh -> lower side first -> val 0.0, vah 2.0
    centres = np.array([0.5, 1.5, 2.5])
    r = P.build_profile(centres, centres, np.array([3.0, 10.0, 3.0]), 1.0)
    assert r["poc_price"] == pytest.approx(1.5)
    assert r["val"] == pytest.approx(0.0)
    assert r["vah"] == pytest.approx(2.0)


def test_profile_poc_tie_lowest_bin_and_empty():
    centres = np.array([0.5, 1.5])
    r = P.build_profile(centres, centres, np.array([5.0, 5.0]), 1.0)
    assert r["poc_price"] == pytest.approx(0.5)
    assert P.build_profile(np.array([]), np.array([]), np.array([]), 1.0) is None
    assert P.build_profile(np.array([1.0]), np.array([2.0]), np.array([0.0]), 1.0) is None


# ---------------------------------------------------------------- 18.2 pivots
def test_pivots_worked_n1():
    h = np.array([1, 3, 2, 5, 4, 1, 2], float)
    assert list(P.fractal_pivot_highs(h, 1)) == [1, 3]


def test_pivots_plateau_none_and_n2():
    assert list(P.fractal_pivot_highs(np.array([1, 3, 3, 2], float), 1)) == []
    assert list(P.fractal_pivot_highs(np.array([1, 2, 5, 2, 1], float), 2)) == [2]


def test_pivot_lows_mirror():
    l = np.array([5, 3, 4, 1, 2, 6, 5], float)
    assert list(P.fractal_pivot_lows(l, 1)) == [1, 3]


# ---------------------------------------------------------------- no look-ahead
def test_pivot_usable_index():
    assert P.pivot_usable_index(10, 3) == 14
    assert P.pivot_usable_index(7, 2) == 10


def test_last_confirmed_not_before_open_of_bar_i_plus_n_plus_1():
    t1 = np.arange(0, 20) * 3_600_000          # contiguous 1h bars
    piv = np.array([4, 9])
    n = 2
    open_use = int(t1[4 + n + 1])               # open of bar i+n+1
    # one ms before that open the pivot is not confirmed; at the open it is
    assert P.last_confirmed(piv, t1, n, open_use - 1) == -1
    assert P.last_confirmed(piv, t1, n, int(t1[4 + n])) == -1      # open of bar i+n: bar not yet closed
    assert P.last_confirmed(piv, t1, n, open_use) == 4
    assert P.last_confirmed(piv, t1, n, int(t1[9 + n + 1]) - 1) == 4
    assert P.last_confirmed(piv, t1, n, int(t1[9 + n + 1])) == 9


# ---------------------------------------------------------------- section 12 + 18.3
def test_atr_sma_worked_period3():
    h = np.array([10, 11, 12, 11], float)
    l = np.array([9, 9, 10, 9], float)
    c = np.array([9.5, 10.5, 11.5, 10], float)
    a = P.atr_sma(h, l, c, 3)
    assert a[3] == pytest.approx(2.1667, abs=1e-4)
    assert np.isnan(a[2])


def _size_series():
    # 22 bars, base (h,l,c) = (10,8,9): TR = 2 everywhere, ATR14 = 2.0 from i = 14.
    # pivot high i=16 (10.5,8.5,9), pivot low i=18 (9.5,7.5,9), pivot high i=20 (10.2,8.2,9); every TR stays 2.
    n = 22
    h = np.full(n, 10.0); l = np.full(n, 8.0); c = np.full(n, 9.0)
    h[16], l[16] = 10.5, 8.5
    h[18], l[18] = 9.5, 7.5
    h[20], l[20] = 10.2, 8.2
    return h, l, c


def test_size_filter_k0_all_fractals():
    h, l, c = _size_series()
    hi, lo = P.meaningful_pivots(h, l, c, 1, 0.0)
    assert list(hi) == [16, 20] and list(lo) == [18]


def test_size_filter_k1p4():
    # low 18 vs earlier high 16: |7.5-10.5| = 3.0 >= 1.4*2 = 2.8 -> meaningful
    # high 20 vs earlier low 18: |10.2-7.5| = 2.7 <  2.8 -> not; high 16 has no earlier low -> not
    h, l, c = _size_series()
    hi, lo = P.meaningful_pivots(h, l, c, 1, 1.4)
    assert list(hi) == [] and list(lo) == [18]


def test_size_filter_k1():
    # 2.7 >= 1.0*2 -> high 20 meaningful; high 16 still lacks an earlier low
    h, l, c = _size_series()
    hi, lo = P.meaningful_pivots(h, l, c, 1, 1.0)
    assert list(hi) == [20] and list(lo) == [18]


# ---------------------------------------------------------------- 18.5 outcomes
def _bars(rows):
    a = np.array(rows, float)
    return a[:, 0], a[:, 1], a[:, 2], a[:, 3]   # o, h, l, c


def _run(rows, side=1, L=100.0, R=2.0, H=3, j=0):
    o, h, l, c = _bars(rows)
    ex, kind, eb = P.resolve_events(o, h, l, c, np.array([j]), np.array([side]), np.array([L]), np.array([R]), H)
    return float(ex[0]), int(kind[0]), int(eb[0])


TOUCH = (100, 101, 99, 100)     # touch bar: low 99 > stop 98, high 101 < target 102


def test_target_net_r_taker():
    ex, kind, eb = _run([TOUCH, (100, 102.5, 99.5, 102)])
    assert (ex, kind, eb) == (102.0, P.KIND_TARGET, 1)
    assert P.net_r(1, 100.0, 2.0, ex, kind, "taker") == pytest.approx(0.9495)


def test_stop_net_r_taker():
    ex, kind, eb = _run([TOUCH, (100, 101, 97.5, 98)])
    assert (ex, kind, eb) == (98.0, P.KIND_STOP, 1)
    assert P.net_r(1, 100.0, 2.0, ex, kind, "taker") == pytest.approx(-1.0495)


def test_timeout_net_r_taker():
    rows = [TOUCH, (100, 101, 99, 100), (100, 101, 99, 100), (100, 101, 99, 100.5)]
    ex, kind, eb = _run(rows, H=3)
    assert (ex, kind, eb) == (100.5, P.KIND_TIMEOUT, 3)
    assert P.net_r(1, 100.0, 2.0, ex, kind, "taker") == pytest.approx(0.19987, abs=1e-5)


def test_maker_variant_fees():
    # entry and target maker 0.0002, stop and timeout taker 0.0005
    assert P.net_r(1, 100.0, 2.0, 102.0, P.KIND_TARGET, "maker") == pytest.approx((2 - 0.02 - 0.0204) / 2)
    assert P.net_r(1, 100.0, 2.0, 98.0, P.KIND_STOP, "maker") == pytest.approx((-2 - 0.02 - 0.049) / 2)
    assert P.net_r(1, 100.0, 2.0, 100.5, P.KIND_TIMEOUT, "maker") == pytest.approx((0.5 - 0.02 - 0.05025) / 2)


def test_stop_first_when_bar_holds_both():
    ex, kind, eb = _run([TOUCH, (100, 103, 97, 100)])
    assert (ex, kind, eb) == (98.0, P.KIND_STOP, 1)


def test_gap_open_beyond_stop_fills_at_open():
    ex, kind, eb = _run([TOUCH, (97, 98, 96.5, 97.5)])
    assert (ex, kind) == (97.0, P.KIND_STOP)
    assert (97.0 - 100.0) / 2.0 == pytest.approx(-1.5)
    assert P.net_r(1, 100.0, 2.0, ex, kind, "taker") == pytest.approx((-3 - 0.05 - 0.0485) / 2)


def test_touch_bar_tests_only_stop():
    # touch bar spans both stop and target: stopped in the touch bar itself
    ex, kind, eb = _run([(100, 103, 97.5, 100), (100, 101, 99, 100)])
    assert (ex, kind, eb) == (98.0, P.KIND_STOP, 0)
    # touch bar reaching the target but not the stop: the target is NOT taken there
    ex, kind, eb = _run([(100, 103, 99, 100), (100, 101, 99, 100), (100, 101, 99, 100), (100, 101, 99, 100.2)], H=3)
    assert kind == P.KIND_TIMEOUT and eb == 3 and ex == 100.2


def test_short_mirror():
    # short L=100 R=2: stop 102, target 98
    ex, kind, eb = _run([(100, 101, 99, 100), (100, 100.5, 97.5, 98)], side=-1)
    assert (ex, kind, eb) == (98.0, P.KIND_TARGET, 1)
    assert P.net_r(-1, 100.0, 2.0, ex, kind, "taker") == pytest.approx((2 - 0.05 - 0.049) / 2)
    ex, kind, eb = _run([(100, 101, 99, 100), (103, 104, 102.5, 103)], side=-1)   # gap open above stop
    assert (ex, kind) == (103.0, P.KIND_STOP)


def test_unresolvable_window_past_end():
    ex, kind, eb = _run([TOUCH, (100, 101, 99, 100)], H=3)
    assert kind == -1


def test_one_open_event_per_stream():
    j = np.array([5, 8, 9, 20])
    exit_bar = np.array([8, 12, 15, 25])
    # j=5 accepted (exit 8); j=8: exit bar 8 >= 8 -> skipped; j=9 accepted (exit 15); j=20 accepted
    assert list(P.select_events(j, exit_bar)) == [True, False, True, True]


# ---------------------------------------------------------------- 18.6 placebo
def test_placebo_cycle():
    assert list(P.PLACEBO_D) == [-3, -2, -1, -0.5, 0.5, 1, 2, 3]
    ds = [P.placebo_level(100.0, 2.0, i) for i in range(9)]
    assert ds == pytest.approx([94.0, 96.0, 98.0, 99.0, 101.0, 102.0, 104.0, 106.0, 94.0])


# ---------------------------------------------------------------- 18.7 bootstrap
def test_bootstrap_worked_example():
    day_sum = np.array([4.0, -2.0])     # day A events [1,3], day B events [-2]
    day_cnt = np.array([2.0, 1.0])
    assert P.boot_stat(day_sum, day_cnt, np.array([0, 0])) == pytest.approx(2.0)
    assert P.boot_stat(day_sum, day_cnt, np.array([1, 1])) == pytest.approx(-2.0)
    assert P.boot_stat(day_sum, day_cnt, np.array([0, 1])) == pytest.approx(0.6667, abs=1e-4)
    both = P.boot_stat(day_sum, day_cnt, np.array([[0, 0], [1, 1], [0, 1]]))
    assert both == pytest.approx([2.0, -2.0, 0.6667], abs=1e-4)


def test_longest_losing_streak():
    assert P.longest_losing_streak([1, -1, -1, 0.5, -2, -2, -2, 3]) == 3
    assert P.longest_losing_streak([]) == 0
    assert P.longest_losing_streak([0.0, 1.0]) == 0
