import sys
sys.dont_write_bytecode = True
import os

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rules as R

WIDE = (0, 10 ** 15)
DAY = 10  # UTC day number used by the synthetic bars


def bars(n, o=100.0, h=101.0, l=99.0, c=100.0, v=1.0, day=DAY):
    t = day * R.D1 + np.arange(n, dtype=np.int64) * R.M15
    f = lambda x: np.full(n, float(x))
    return dict(t=t, o=f(o), h=f(h), l=f(l), c=f(c), v=f(v))


def test_a_acceptance_needs_eight_closes_and_exit_is_sixteenth_bar():
    # prior-day VA 90..100. Bar 0 closes 99 (inside), bar 1 closes 101 (event i=1), bars 1..8 close 102 (eight closes).
    b = bars(60, h=103.0, l=101.5, c=102.0)
    b["c"][0], b["l"][0], b["h"][0] = 99.0, 98.0, 99.5
    b["l"][9], b["c"][9] = 100.0, 103.0          # first touch of the edge 100 at bar 9 = i+8: accepted; closes above: HOLD
    b["c"][25] = 111.0                           # entry bar 10, exit = close of the 16th bar from entry = bar 25
    b["c"][24] = 105.0                           # off-by-one guard
    di = {DAY - 1: dict(val=90.0, vah=100.0)}
    trades, acc, non = R.run_a(b, di, *WIDE)
    assert acc == [True] and non == []
    assert len(trades) == 1 and trades[0]["entry_i"] == 10 and trades[0]["exit_i"] == 25 and trades[0]["side"] == 1
    assert abs(trades[0]["ret"] - ((111.0 / 100.0 - 1) * 1e4 - 10)) < 1e-9


def test_a_touch_at_seventh_bar_is_not_accepted():
    b = bars(60, h=103.0, l=101.5, c=102.0)
    b["c"][0], b["l"][0], b["h"][0] = 99.0, 98.0, 99.5
    b["l"][8], b["c"][8] = 100.0, 103.0          # touch at bar 8 = i+7: only seven closes before it -> NOT accepted
    di = {DAY - 1: dict(val=90.0, vah=100.0)}
    trades, acc, non = R.run_a(b, di, *WIDE)
    assert acc == [] and non == [True] and trades == []


def test_a_failed_retest_gives_no_trade():
    b = bars(60, h=103.0, l=101.5, c=102.0)
    b["c"][0], b["l"][0], b["h"][0] = 99.0, 98.0, 99.5
    b["l"][9], b["c"][9] = 99.0, 99.5            # retest closes back below the edge: hold False
    di = {DAY - 1: dict(val=90.0, vah=100.0)}
    trades, acc, non = R.run_a(b, di, *WIDE)
    assert acc == [False] and trades == []


def test_sim_trade_short_to_poc_hand_numbers():
    b = bars(40, o=105.0, h=106.0, l=104.0, c=105.0)
    b["l"][1] = 99.0                             # bar 1 reaches the POC 100 (stop 110 not hit)
    tr = R.sim_trade(b, -1, 0, 100.0, 24)
    assert tr["kind"] == "tp" and tr["exit_i"] == 1 and tr["exit_px"] == 100.0
    assert abs(tr["ret"] - ((-1) * (100.0 / 105.0 - 1) * 1e4 - 10)) < 1e-9
    assert R.sim_trade(b, -1, 0, 104.9, 24) is None      # R/entry < 0.10 % guard
    assert R.sim_trade(b, 1, 0, 100.0, 24) is None       # target on the wrong side


def test_b_first_exit_per_direction_and_revisit_flag():
    b = bars(60, o=100.0, h=100.5, l=99.5, c=100.0)
    b["c"][5] = 106.0                            # first close above VAH 105 (bar 4 closed 100 inside)
    b["o"][6], b["h"][6], b["l"][6] = 106.0, 106.5, 99.0   # touches POC 100 right after
    b["c"][9] = 107.0                            # second exit same day: not a new event
    di = {DAY - 1: dict(val=95.0, vah=105.0, poc=100.0)}
    trades, rev = R.run_b(b, di, *WIDE)
    assert rev == [True]
    assert len(trades) == 1 and trades[0]["side"] == -1 and trades[0]["entry_i"] == 6 and trades[0]["kind"] == "tp"


def test_thin_flag_boundary_is_inclusive():
    def day(poc_bars):
        n = 96
        h = np.full(n, 100.5); l = h.copy(); c = h.copy(); v = np.zeros(n)
        v[:poc_bars] = 1.0                       # POC bin 100.5
        c[-1] = h[-1] = l[-1] = 100.0            # last close 100.0 -> own bin, volume 1
        v[-1] = 1.0
        t = DAY * R.D1 + np.arange(n, dtype=np.int64) * R.M15
        return dict(t=t, o=c.copy(), h=h, l=l, c=c, v=v)
    assert R.day_info(day(4))[DAY]["thin"] is True       # 1 <= 0.25 x 4
    assert R.day_info(day(3))[DAY]["thin"] is False      # 1 > 0.25 x 3


def test_d_naked_poc_touch_exit_and_mirror():
    n = 3200
    b = bars(n, o=100.0, h=101.0, l=99.0, c=100.0)
    b["l"][50] = 94.0                            # touches POC 95 at bar 50
    b["c"][145] = 90.0                           # off-by-one guard
    b["c"][146] = 96.9                           # exit = close of the 96th bar after the touch bar
    wi = {5: dict(poc=95.0, close=100.0, birth_i=10)}
    trades, touches, mirror, mfe = R.run_d(b, wi, *WIDE)
    assert touches == [True] and mirror == [False]
    assert len(trades) == 1 and trades[0]["side"] == 1 and trades[0]["exit_i"] == 146
    assert abs(trades[0]["ret"] - ((96.9 / 95.0 - 1) * 1e4 - 10)) < 1e-9
    assert abs(mfe[0] - (101.0 / 95.0 - 1) * 1e4) < 1e-9


def test_d_near_poc_event_is_dropped():
    b = bars(3200)
    wi = {5: dict(poc=99.5, close=100.0, birth_i=10)}    # 0.5 % away < 1 %
    assert R.run_d(b, wi, *WIDE)[1] == []


def test_placebo_is_reproducible_and_direction_matched():
    b = bars(400, h=100.0, l=100.0, c=100.0, o=100.0)
    b["c"][200:] = 101.0
    tr = [dict(side=1, hz=16)]
    a1 = R.placebo(b, tr, int(b["t"][0]), int(b["t"][-1]), "hold", draws=20)
    a2 = R.placebo(b, tr, int(b["t"][0]), int(b["t"][-1]), "hold", draws=20)
    assert (a1 == a2).all()
    s1 = R.placebo(b, [dict(side=-1, hz=16)], int(b["t"][0]), int(b["t"][-1]), "hold", draws=20)
    assert np.allclose(a1 + s1, -2 * R.FEE_BP)    # short mirrors long minus two fees
