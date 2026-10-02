"""Fabio v3 signals S1-S9 (spec section 3). Hand-built bars; EXPECT values from spec section 10 (T-ids in comments),
never from repo code. Fixture F1 is the spec's (bin 1.0, TICK 0.1)."""
import random

import pytest

from MyTradingSys.backtest.layers.fabio.v3 import (atr, balance, big_push, breakout, control_level, effort_result,
                                                   exhaustion, failed_auction, lvn_levels, poc_center, pressure,
                                                   select_lvn, value_area, volume_tier)


def bar(k, o, h, l, c, buy=0.0, sell=0.0, fp="", b99b=0.0, b99s=0.0):
    return {"t": k * 60000, "o": o, "h": h, "l": l, "c": c, "buy_vol": buy, "sell_vol": sell, "delta": buy - sell,
            "b99_buy_vol": b99b, "b99_sell_vol": b99s, "b999_buy_vol": 0.0, "b999_sell_vol": 0.0, "thr_days": 30,
            "fp": fp}


def f1():
    rows = [(100, 101, 99, 100, 5, 5, "100:5:5"), (100, 102, 99, 101, 6, 4, "100:6:4"),
            (101, 102, 100, 100, 3, 7, "100:3:7"), (100, 101, 99, 100, 4, 6, "99:4:6"),
            (100, 101, 99, 100.5, 3, 7, "100:3:7"), (100, 100.5, 98, 98.5, 2, 8, "98:2:8")]
    bars = [bar(k, *r) for k, r in enumerate(rows)]
    bars[5]["b99_sell_vol"] = 3.0
    return bars


# ---- S1 / S2 / S4 / S5 on F1
def test_t01_atr():
    assert atr(f1(), 4, 4) == pytest.approx(2.25)                      # TR 3, 2, 2, 2


def test_t02_balance_needs_i_ge_n():
    assert balance(f1(), 3, 4, 0.8, 1.0) is None


def test_t03_balance_f1():
    b = balance(f1(), 4, 4, 0.8, 1.0)
    assert (b["H"], b["L"], b["R"], b["poc"]) == (102, 99, 3, 100.5)   # limit 0.8*2*2.25 = 3.6


def test_t04_k_bal_too_tight():
    assert balance(f1(), 4, 4, 0.6, 1.0) is None


def test_t05_close_away_from_poc():
    bars = f1()
    bars[4]["c"] = 99.7                                                # |99.7 - 100.5| = 0.8 > 0.25 * 3
    assert balance(bars, 4, 4, 0.8, 1.0) is None


def test_t06_t07_t08_pressure():
    assert pressure(f1(), 4, 4, 0.10, k_bal=0.8, bin_size=1.0) == -1   # P -0.2, drift 0.1667
    assert pressure(f1(), 4, 4, 0.25, k_bal=0.8, bin_size=1.0) == 0    # |P| < p
    bars = f1()
    bars[1]["o"] = 99.5                                                # drift 0.333 > 0.25
    assert pressure(bars, 4, 4, 0.10, k_bal=0.8, bin_size=1.0) == 0


def test_t09_big_push():
    assert big_push(f1(), 5, 1, -1) is True
    assert big_push(f1(), 5, 1, 1) is False


def test_t10_t11_t12_breakout():
    assert breakout(f1(), 5, 4, 0.8, 0.10, 1, "99", 1.0) == -1
    bars = f1()
    bars[5]["c"] = 99.2                                                # above L(4) = 99: no break
    assert breakout(bars, 5, 4, 0.8, 0.10, 1, "99", 1.0) == 0
    bars = f1()
    bars[5]["b99_buy_vol"], bars[5]["b99_sell_vol"] = 3.0, 0.0         # push is the other way
    assert breakout(bars, 5, 4, 0.8, 0.10, 1, "99", 1.0) == 0


def test_t13_volume_tier():
    assert volume_tier(300, [150, 250, 200], min_days=3) == "999"      # 300 / 200 = 1.5
    assert volume_tier(290, [150, 250, 200], min_days=3) == "99"
    assert volume_tier(10 ** 6, [150, 250]) == "99"                    # fewer than 10 prior days


# ---- S5D
def f1_t57():
    bars = f1()
    bars[5] = bar(5, 101, 103, 100.8, 102.5, 6, 4, "101:6:4", b99b=3.0)
    return bars


def test_t57_failed_auction_and_breakout_disagree():
    absb = [0, 0, 0, -1, 0, 0]
    assert failed_auction(f1_t57(), 5, 4, 0.8, 0.10, 1, absb, "99", 1.0) == {"s": 1, "lvl": 99.0, "edge": 102.0}
    assert breakout(f1_t57(), 5, 4, 0.8, 0.10, 1, "99", 1.0) == 0


def test_t57_failed_auction_none_cases():
    assert failed_auction(f1_t57(), 5, 4, 0.8, 0.10, 1, [0] * 6, "99", 1.0) is None
    assert failed_auction(f1_t57(), 5, 4, 0.8, 0.10, 1, [-1, 0, 0, 0, 0, 0], "99", 1.0) is None   # j 0 outside [1, 4]
    b = f1_t57()
    b[5]["c"] = 101.9
    assert failed_auction(b, 5, 4, 0.8, 0.10, 1, [0, 0, 0, -1, 0, 0], "99", 1.0) is None
    b = f1_t57()
    b[5]["b99_buy_vol"], b[5]["b99_sell_vol"] = 0.0, 3.0
    assert failed_auction(b, 5, 4, 0.8, 0.10, 1, [0, 0, 0, -1, 0, 0], "99", 1.0) is None


# ---- S3
def s3_bars(d, r):
    """4 prior bars with delta [1,-1,1,-1] and r = c - o [0.5,-0.5,0.5,-0.5], then the bar under test."""
    pd, pr = [1, -1, 1, -1], [0.5, -0.5, 0.5, -0.5]
    bars = [bar(k, 100, 101, 99, 100 + pr[k], 5 + pd[k] / 2, 5 - pd[k] / 2) for k in range(4)]
    bars.append(bar(4, 100, 101, 99, 100 + r, 5 + d / 2, 5 - d / 2))
    return bars


def test_t14_to_t18_effort_result():
    def s3(d, r):
        return effort_result(s3_bars(d, r), 4, L=4, z_hi=2.5)
    assert s3(3, 0) == {"control": 0, "absorbed": 1}
    assert s3(3, 1.0) == {"control": 1, "absorbed": 0}
    assert s3(3, -0.5) == {"control": 0, "absorbed": 1}
    assert s3(-3, -1.0) == {"control": -1, "absorbed": 0}
    assert s3(3, 0.25) == {"control": 0, "absorbed": 0}


def test_t19_zero_sd_gives_none_pair():
    bars = s3_bars(3, 0)
    for b in bars[:4]:
        b["buy_vol"], b["sell_vol"], b["delta"] = 6.0, 5.0, 1.0        # prev d all 1: sd 0
    assert effort_result(bars, 4, L=4, z_hi=2.5) == {"control": 0, "absorbed": 0}


def test_effort_result_requires_z_hi():                                # P04 NS-grid: no default
    with pytest.raises(ValueError):
        effort_result(s3_bars(3, 0), 4, L=4)


# ---- S6
def test_t20_control_level():
    bars = [bar(k, 100, 100, 100, 100) for k in range(15)]
    bars[11]["h"], bars[13]["h"] = 105, 103
    ctrl = [0] * 15
    ctrl[11], ctrl[12], ctrl[13] = -1, 1, -1
    assert control_level(bars, ctrl, 10, 14, -1) == 103
    assert control_level(bars, ctrl, 10, 12, -1) == 105
    assert control_level(bars, ctrl, 10, 10, -1) is None
    bars[11]["l"] = 95
    assert control_level(bars, [0] * 11 + [1] + [0] * 3, 10, 14, 1) == 95


# ---- profile maths
def test_t21_value_area_and_poc():
    p = {100: 10, 110: 20, 120: 40, 130: 15, 140: 5, 150: 10}
    va = value_area(p, 10)
    assert (va["VAL"], va["VAH"]) == (100, 130) and poc_center(p, 10) == 125


def test_t22_value_area_tie_goes_up():
    va = value_area({100: 10, 110: 30, 120: 10}, 10)
    assert (va["VAL"], va["VAH"]) == (110, 130)


def test_t23_lvn_levels():
    p = {100: 30, 110: 25, 120: 5, 130: 20, 140: 4, 150: 30, 160: 10}
    assert lvn_levels(p, 10) == [125, 145]


def test_t24_select_lvn_nearest_to_extreme():
    assert select_lvn([125, 145], 1, 165, 100, 160) == 145
    assert select_lvn([125, 145], 1, 165, 100, 140) == 125


# ---- S8
def s8_bars(n, last_b99_buy):
    bs = [bar(k, 100, 101, 99, 100, 5, 5) for k in range(n)]
    bs[-1]["b99_buy_vol"] = last_b99_buy
    return bs


def test_t25_s8_clause_a_big_trades_stopped():
    trade = {"s": 1, "e_i": 5, "lvl": None}                            # i = 20: age 15
    assert exhaustion(s8_bars(21, -1.0), 20, trade) is True
    assert exhaustion(s8_bars(21, 0.0), 20, trade) is True             # net 0 <= 0
    assert exhaustion(s8_bars(21, 1.0), 20, trade) is False
    assert exhaustion(s8_bars(20, 0.0), 19, {"s": 1, "e_i": 5, "lvl": None}) is False   # age 14


def test_t25_short_bars_never_raise():
    assert exhaustion(s8_bars(3, 0.0), 2, {"s": 1, "e_i": 0, "lvl": None}) is False


def test_s8_clause_c_opposite_control_breaks_level():                   # spec S8(c); inputs are ours, hand-derived
    def build(c_last):
        bs = []
        for k in range(61):                                            # baseline: d +-1, r +-0.5 (sd 1 and 0.5)
            sgn = 1 if k % 2 == 0 else -1
            bs.append(bar(k, 100, 101, 99, 100 + 0.5 * sgn, 5 + sgn / 2, 5 - sgn / 2))
        bs.append(bar(61, c_last + 1.0, c_last + 1.0, c_last - 0.1, c_last, 3.5 - 0.0, 6.5))   # d -3, r -1.0
        return bs
    trade = {"s": 1, "e_i": 55, "lvl": 101.0}
    assert exhaustion(build(100.9), 61, trade, z_hi=2.5) is True
    assert exhaustion(build(101.0), 61, trade, z_hi=2.5) is False


# ---- causality (T49 / T64): deleting bars after i must not change any signal at i
def test_t49_look_ahead_canary():
    rng = random.Random(7)
    bars, px = [], 100.0
    for k in range(140):
        o = px
        c = o + rng.uniform(-0.6, 0.6)
        h, l = max(o, c) + rng.uniform(0, 0.3), min(o, c) - rng.uniform(0, 0.3)
        buy, sell = rng.uniform(1, 9), rng.uniform(1, 9)
        fp = "%d:%.2f:%.2f" % (int(l), buy, sell)
        bars.append(bar(k, o, h, l, c, buy, sell, fp, rng.choice([0, 0, 3]), rng.choice([0, 0, 3])))
        px = c
    for i in (70, 100, 130):
        cut = bars[:i + 1]
        assert balance(bars, i, 20, 0.8, 1.0) == balance(cut, i, 20, 0.8, 1.0)
        assert pressure(bars, i, 20, 0.05, k_bal=0.8, bin_size=1.0) == pressure(cut, i, 20, 0.05, k_bal=0.8, bin_size=1.0)
        assert effort_result(bars, i, z_hi=2.0) == effort_result(cut, i, z_hi=2.0)
        assert breakout(bars, i, 20, 0.8, 0.05, 5, "99", 1.0) == breakout(cut, i, 20, 0.8, 0.05, 5, "99", 1.0)
        tr = {"s": 1, "e_i": i - 70, "lvl": None}
        for climax in (False, True):
            assert (exhaustion(bars, i, tr, bin_size=1.0, climax=climax)
                    == exhaustion(cut, i, tr, bin_size=1.0, climax=climax))
