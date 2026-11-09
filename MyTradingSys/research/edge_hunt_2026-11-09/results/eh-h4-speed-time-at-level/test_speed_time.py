"""Hand-built tests for speed_time.py (T05). Run: python -m pytest test_speed_time.py -q"""
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import speed_time as st  # noqa: E402

BASE = 1577836800000  # 2020-01-01 00:00 UTC
BAR = 900000          # 15m in ms
DAY = 96 * BAR
NOFUND = np.array([], dtype=np.int64)


def mk(n, price=100.0, start=BASE):
    ts = np.array([start + i * BAR for i in range(n)], dtype=np.int64)
    o = np.full(n, price, dtype=float)
    return ts, o.copy(), o.copy(), o.copy(), o.copy()  # ts, o, h, l, c


def two_days():
    """Day 0: PDH 110 (high at idx 5), PDL 90 (low at idx 7). Day 1 flat at 100."""
    ts, o, h, l, c = mk(192, start=0)
    h[5] = 110.0
    l[7] = 90.0
    return ts, o, h, l, c


def short_setup(n=300):
    """Touch t=10 (high 111), reclaim r=11 at close 109 (PDH 110). Stop 111, R 2, target 105."""
    ts, o, h, l, c = mk(n)
    h[10] = 111.0
    c[10] = 111.0
    c[11] = 109.0
    h[11] = 109.5
    l[11] = 109.0
    return ts, h, l, c


def test_speed_in_formula():
    ts, o, h, l, c = mk(20)
    c[12] = 101.2       # close[t-1] with t = 13; close[t-13] = c[0] = 100
    # |101.2 - 100| / 100 / 12 x 100 = 0.1 (% per bar)
    assert st.speed_in(c, 13) == pytest.approx(0.1, rel=1e-9)


def test_touch_is_first_bar_beyond_and_needs_inside_lookback():
    ts, o, h, l, c = two_days()
    h[96 + 20] = 111.0   # first bar of day 1 beyond PDH; close[t-12] = c[104] = 100 inside
    c[96 + 20] = 105.0
    h[96 + 40] = 112.0   # later bar beyond again: no second touch that day
    touches, _ = st.find_touches(ts, h, l, c)
    day1 = [t for t in touches if t["day"] == 1]
    assert len(day1) == 1
    assert day1[0]["t"] == 96 + 20
    assert day1[0]["side"] == "high"


def test_no_touch_when_lookback_close_was_outside():
    ts, o, h, l, c = two_days()
    h[96 + 20] = 111.0
    c[96 + 8] = 111.0    # close[t-12] outside the range -> no touch that day
    touches, _ = st.find_touches(ts, h, l, c)
    assert [t for t in touches if t["day"] == 1] == []


def test_reclaim_within_three_bars_only():
    ts, o, h, l, c = two_days()
    c[116] = 111.0
    c[117] = 109.0       # inside (90 < 109 < 110)
    assert st.reclaim_bar(c, 116, pdh=110.0, pdl=90.0) == 117
    c2 = c.copy()
    c2[116:120] = 111.0  # no close back inside in t..t+3
    assert st.reclaim_bar(c2, 116, pdh=110.0, pdl=90.0) is None
    c3 = c.copy()
    c3[116] = 109.0      # k = 0: the touch bar closes back inside
    assert st.reclaim_bar(c3, 116, pdh=110.0, pdl=90.0) == 116


def test_time_at_level_counts_only_up_to_reclaim_bar():
    ts, o, h, l, c = two_days()
    c[116] = 111.0       # 0.9 % away: not counted
    c[117] = 110.1       # within 0.2 % of 110: counted; this is the reclaim bar r
    c[118] = 109.9       # within, but after r: must not be counted
    c[119] = 115.0
    r = 117
    assert st.time_at_level(c, level=110.0, t=116, r=r) == 1
    c_future = c.copy()  # bars after the reclaim must not change the count (no lookahead)
    c_future[118:130] = 110.0
    assert st.time_at_level(c_future, level=110.0, t=116, r=r) == 1


def test_trade_target_hit_gross_plus_two():
    ts, h, l, c = short_setup()
    l[12], h[12] = 104.0, 109.5   # low 104 <= target 105, high 109.5 < stop 111
    res = st.simulate_trade(ts, h, l, c, NOFUND, np.array([]), t=10, r=11, side="high", level=110.0)
    assert res["outcome"] == "target"
    assert res["gross_r"] == pytest.approx(2.0)
    assert res["stop"] == pytest.approx(111.0)
    assert res["entry"] == pytest.approx(109.0)
    assert res["target"] == pytest.approx(105.0)


def test_same_bar_tie_stop_wins():
    ts, h, l, c = short_setup()
    l[12], h[12] = 104.0, 112.0   # bar 12 touches both target (105) and stop (111)
    res = st.simulate_trade(ts, h, l, c, NOFUND, np.array([]), t=10, r=11, side="high", level=110.0)
    assert res["outcome"] == "stop"
    assert res["gross_r"] == pytest.approx(-1.0)


def test_time_stop_closes_at_bar_r_plus_96():
    ts, h, l, c = short_setup()
    h[12:110] = 109.5             # no stop (111) and no target (105) in bars 12..107
    l[12:110] = 109.0
    c[11 + 96] = 108.0            # close of r + 96 = time-stop exit
    res = st.simulate_trade(ts, h, l, c, NOFUND, np.array([]), t=10, r=11, side="high", level=110.0)
    assert res["outcome"] == "time"
    assert res["exit_index"] == 11 + 96
    assert res["gross_r"] == pytest.approx((109.0 - 108.0) / 2.0)


def test_fee_and_funding_arithmetic():
    stop_frac = 2.0 / 109.0      # stop distance 2 on entry 109
    assert st.fee_r(stop_frac) == pytest.approx(0.0012 / stop_frac)  # 12 bps round trip
    ts, h, l, c = short_setup()
    l[12], h[12] = 104.0, 109.5
    fund_ts = np.array([BASE + 12 * BAR], dtype=np.int64)   # inside (entry, exit]
    fund_rate = np.array([0.0001])
    res = st.simulate_trade(ts, h, l, c, fund_ts, fund_rate, t=10, r=11, side="high", level=110.0)
    # a short receives positive funding: cost is -rate
    assert res["funding_cost_r"] == pytest.approx(-0.0001 / stop_frac)
    assert res["net_r"] == pytest.approx(2.0 - 0.0012 / stop_frac + 0.0001 / stop_frac)


def test_split_refusal():
    with pytest.raises(st.SplitViolation):
        st.guard_bars(np.array([st.DEV_END_MS - BAR, st.DEV_END_MS], dtype=np.int64), "DEV")
    with pytest.raises(st.SplitViolation):
        st.guard_bars(np.array([st.HOLDOUT_MS], dtype=np.int64), "VALIDATION")
    with pytest.raises(st.SplitViolation):
        st.guard_bars(np.array([st.HOLDOUT_MS + BAR], dtype=np.int64), "HOLDOUT")
    st.guard_bars(np.array([st.DEV_END_MS - BAR], dtype=np.int64), "DEV")   # inside DEV: no raise


def test_htf_value_not_visible_before_its_close():
    week_close = np.array([BASE + 7 * DAY], dtype=np.int64)   # the week's close time
    vals = np.array([55.0])
    assert st.htf_closed_asof(week_close, vals, BASE + 3 * DAY) is None   # Wednesday of the open week
    assert st.htf_closed_asof(week_close, vals, BASE + 7 * DAY - 1) is None
    assert st.htf_closed_asof(week_close, vals, BASE + 7 * DAY) == 55.0


def test_cluster_se_by_day():
    x = np.array([1.0, 1.0, -1.0])
    day = np.array([1, 1, 2])
    mean, se = st.cluster_mean_se(x, day)
    assert mean == pytest.approx(1.0 / 3.0)
    # residual sums per day: 4/3 and -4/3; sqrt(32/9) / N=3 = sqrt(32)/9
    assert se == pytest.approx(np.sqrt(32.0) / 9.0)
