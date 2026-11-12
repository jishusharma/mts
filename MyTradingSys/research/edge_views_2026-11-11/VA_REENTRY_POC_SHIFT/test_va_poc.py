import sys
sys.dont_write_bytecode = True
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import va_poc as V


def prof(vols, base=10, width=1.0):
    """One bar per bin: typical price = bin center, volume = vols[k]."""
    tp = np.array([base + k + 0.5 for k in range(len(vols))]) * width
    return V.profile(tp, tp, tp, np.array(vols, float), width)


def test_value_area_goes_up_when_upper_pair_is_larger():
    # bins 10..16, vols [1,2,3,10,4,5,1], total 26, 70 % = 18.2; POC bin 13 (10); up pair 4+5=9 > down pair 3+2=5 -> acc 19
    poc, val, vah = prof([1, 2, 3, 10, 4, 5, 1])
    assert (poc, val, vah) == (13.5, 13.0, 16.0)


def test_value_area_goes_down_when_lower_pair_is_larger():
    # bins 10..16, vols [5,4,10,1,1,0,0], total 21, 70 % = 14.7; POC bin 12; up 1+1=2 < down 4+5=9 -> acc 19, area 10..12
    poc, val, vah = prof([5, 4, 10, 1, 1, 0, 0])
    assert (poc, val, vah) == (12.5, 10.0, 13.0)


def test_value_area_needs_70_percent_not_50():
    # bins 10..16, vols [3,3,5,6,3,3,3], total 26: 70 % = 18.2. POC bin 13 (6). down pair 5+3=8 > up 6 -> acc 14 (50 % = 13 would stop here);
    # then up 3+3=6 > down 3 -> acc 20 >= 18.2: area bins 11..15
    assert prof([3, 3, 5, 6, 3, 3, 3]) == (13.5, 11.0, 16.0)


def test_poc_tie_takes_lowest_bin_and_single_bin_day():
    assert prof([7, 7, 7])[0] == 10.5
    assert prof([9]) == (10.5, 10.0, 11.0)


def test_typical_price_and_day_width():
    # bar high 14, low 10, close 13
    assert V.profile([14], [10], [13], [3], 1.0) == (12.5, 12.0, 13.0)  # (14+10+13)/3 = 12.33 -> bin 12 (close alone would be bin 13)
    # day close 20000 -> width 10; typical 20005 -> bin 2000: poc 20005, area 20000..20010
    t = np.array([0, 60_000]) + 5 * V.D1
    p = V.day_profiles(t, np.array([20005., 20005.]), np.array([20005., 20005.]), np.array([20005., 20000.]), np.array([5., 0.]))
    assert p[5] == (20005.0, 20000.0, 20010.0)
    assert abs(p[5][2] - p[5][1] - 10.0) < 1e-9


def test_levels_use_previous_day_only():
    rng = np.random.default_rng(2)
    n = 4 * 1440
    t = np.arange(n, dtype=np.int64) * 60_000
    c = 100 + np.cumsum(rng.normal(0, 0.1, n))
    h, l, v = c + 0.2, c - 0.2, rng.uniform(1, 2, n)
    a = V.levels_for_days(V.day_profiles(t, h, l, c, v))
    h2, l2, c2 = h.copy(), l.copy(), c.copy()
    h2[3 * 1440:] += 50
    l2[3 * 1440:] += 50
    c2[3 * 1440:] += 50
    b = V.levels_for_days(V.day_profiles(t, h2, l2, c2, v))
    assert a[1] == b[1] and a[2] == b[2] and a[3] == b[3]  # day 3 level comes from day 2, untouched by day-3 data
    assert a[4] != b[4]


def bars15(rows, day=2):
    t0 = day * V.D1
    return dict(t=np.array([t0 + k * V.M15 for k in range(len(rows))], dtype=np.int64),
                o=np.array([r[0] for r in rows], float), h=np.array([r[1] for r in rows], float),
                l=np.array([r[2] for r in rows], float), c=np.array([r[3] for r in rows], float))


def test_r1_short_hand_computed_trade():
    # VA 95..105. k2 closes 106 (break, high 107), k3 closes 104 (back inside), entry = k4 open 104.
    rows = [(100, 101, 99, 100), (100, 101, 99, 100), (100, 107, 100, 106), (106, 106, 103, 104),
            (104, 105, 100, 101), (101, 102, 94, 96), (96, 97, 95, 96)]
    b = bars15(rows)
    tr = V.run_r1(b, {2: (95.0, 105.0)}, 2 * V.D1, 3 * V.D1)
    assert len(tr) == 1
    x = tr[0]
    assert x["side"] == -1 and x["entry_px"] == 104.0 and x["kind"] == "tp" and x["exit_px"] == 95.0
    # R = 107 - 104 = 3, target distance 9 -> gross 3 R; fee 0.001 * 104 / 3 = 0.034667 R
    assert abs(x["gross_r"] - 3.0) < 1e-9
    assert abs(x["ret"] - (3.0 - 0.001 * 104 / 3)) < 1e-9


def test_r1_long_stop_wins_tie_hand_computed():
    # VA 95..105. k2 closes 94 (break down, low 93), k3 closes 96 (back inside), entry k4 open 96, stop 93, R 3, target 105.
    # k4 touches both stop (92) and target (106): the stop counts -> gross -1 R.
    rows = [(100, 101, 99, 100), (100, 101, 99, 100), (100, 100, 93, 94), (94, 97, 94, 96), (96, 106, 92, 100), (100, 100, 100, 100)]
    tr = V.run_r1(bars15(rows), {2: (95.0, 105.0)}, 2 * V.D1, 3 * V.D1)
    assert len(tr) == 1 and tr[0]["side"] == 1 and tr[0]["kind"] == "stop"
    assert abs(tr[0]["gross_r"] + 1.0) < 1e-9


def test_r1_no_trade_without_close_back_inside_or_through_far_edge():
    stay_out = [(100, 101, 99, 100), (100, 101, 99, 100), (100, 107, 100, 106), (106, 108, 105, 107), (107, 108, 106, 107), (107, 108, 106, 107)]
    assert V.run_r1(bars15(stay_out), {2: (95.0, 105.0)}, 2 * V.D1, 3 * V.D1) == []
    through = [(100, 101, 99, 100), (100, 101, 99, 100), (100, 107, 100, 106), (106, 106, 90, 94), (94, 100, 94, 99), (99, 99, 99, 99)]
    assert V.run_r1(bars15(through), {2: (95.0, 105.0)}, 2 * V.D1, 3 * V.D1) == []


def test_r1_wick_only_does_not_arm():
    rows = [(100, 101, 99, 100), (100, 101, 99, 100), (100, 110, 100, 104), (104, 104, 90, 96), (96, 97, 95, 96), (96, 96, 96, 96)]
    assert V.run_r1(bars15(rows), {2: (95.0, 105.0)}, 2 * V.D1, 3 * V.D1) == []


def test_r2_signals_and_returns_hand_computed():
    pocs = {d: (100.0 + d, 0.0, 0.0) for d in range(1, 11)}  # strictly rising POC
    days = np.arange(1, 11)
    ms0 = days * V.D1
    px0 = np.array([100.0 * (1.1 ** k) for k in range(10)])
    sig = V.poc_signals(pocs, days)
    assert [d for d, s in sig] == [3, 4, 5, 6, 7, 8, 9, 10] and all(s == 1 for d, s in sig)
    r1 = V.run_r2(pocs, days, ms0, px0, 1, 0, 99 * V.D1)
    # signal day 3 -> entry day 4 (px0[3]) exit day 5 (px0[4]): +10 % = 1000 bp - 10 bp fee
    assert abs(r1[0]["ret"] - (1000.0 - 10.0)) < 1e-6
    r3 = V.run_r2(pocs, days, ms0, px0, 3, 0, 99 * V.D1)
    assert [x["entry_ms"] // V.D1 for x in r3] == [4, 7]  # non-overlapping: exit day 7 frees the next entry
    assert abs(r3[0]["ret"] - ((1.1 ** 3 - 1) * 1e4 - 10.0)) < 1e-6


def test_r2_down_signal_and_non_monotone_none():
    pocs = {1: (103.0, 0, 0), 2: (102.0, 0, 0), 3: (101.0, 0, 0), 4: (101.5, 0, 0)}
    assert V.poc_signals(pocs, [1, 2, 3, 4]) == [(3, -1)]
    assert V.poc_signals({1: (1.0, 0, 0), 2: (1.0, 0, 0), 3: (2.0, 0, 0)}, [3]) == []
