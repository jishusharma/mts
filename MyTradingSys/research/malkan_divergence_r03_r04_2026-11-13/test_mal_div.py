import os
import sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mal_div_lib as L


def win(o, h, l, c):
    return [np.array([x], float) for x in (o, h, l, c)]


def test_long_target_stop_time_and_samebar():
    e, s = np.array([100.0]), np.array([99.0])
    # target 2R = 102 hit on bar 2; stop never
    O, H, Lo, C = win([100] * 4, [100.5, 101, 102.5, 103], [99.5] * 4, [100, 100.5, 102, 103])
    assert abs(L.fwd_exit(1, e, s, O, H, Lo, C, "tgt", 2.0, 0.0)[0] - 2.0) < 1e-9
    # same bar stop and target: stop first (-1R)
    O, H, Lo, C = win([100] * 4, [103] * 4, [98.5] * 4, [100] * 4)
    assert abs(L.fwd_exit(1, e, s, O, H, Lo, C, "tgt", 1.0, 0.0)[0] + 1.0) < 1e-9
    # gap through stop fills at open (-2R here)
    O, H, Lo, C = win([98, 98, 98, 98], [98.5] * 4, [97.5] * 4, [98] * 4)
    assert abs(L.fwd_exit(1, e, s, O, H, Lo, C, "tgt", 1.0, 0.0)[0] + 2.0) < 1e-9
    # time exit at last close, cost 1 bp of price = 0.01 R at 1 % stop
    O, H, Lo, C = win([100] * 4, [100.4] * 4, [99.5] * 4, [100.3, 100.2, 100.1, 100.5])
    assert abs(L.fwd_exit(1, e, s, O, H, Lo, C, "time", 0, 0.0001)[0] - (0.5 - 0.01)) < 1e-9


def test_short_mirrors_long():
    e, s = np.array([100.0]), np.array([101.0])
    O, H, Lo, C = win([100] * 3, [100.5] * 3, [99, 98, 97.5], [99.5, 98, 97.6])
    assert abs(L.fwd_exit(-1, e, s, O, H, Lo, C, "tgt", 2.0, 0.0)[0] - 2.0) < 1e-9
    O, H, Lo, C = win([100, 102, 102], [101.5, 102, 102], [99.6] * 3, [100] * 3)
    assert abs(L.fwd_exit(-1, e, s, O, H, Lo, C, "tgt", 1.0, 0.0)[0] + 1.0) < 1e-9


def test_trade_requires_confirming_candle():
    from MyTradingSys.backtest.layers.rsi.rsi_divergence import rsi_divergence
    # bearish: pivot highs A(i=2, 10) and B(i=7, 11); RSI lower at B
    c = [5, 8, 10, 8, 6, 7, 9, 11, 9, 8, 7]
    t = np.arange(len(c)) * L.HOUR
    rsi = [50, 60, 70, 60, 50, 55, 60, 65, 55, 50, 45]
    for open8, expect in ((10.0, 1), (7.0, 0)):  # bar 8 closes 9: red if open 10, green if open 7
        o = list(c)
        o[8] = open8
        bars = dict(t=t, o=np.array(o, float), h=np.array(c, float) + 0.5, l=np.array(c, float) - 0.5, c=np.array(c, float))
        r = L.build_trades(bars, np.array(rsi, float), "bearish", 12, 1, rsi_divergence)
        assert len(r["idx"]) == expect
        if expect:
            assert r["stop"][0] == 11.5 and r["entry"][0] == 9.0 and r["idx"][0] == 8


def test_bh_and_boot():
    assert L.bh([0.001, 0.5, 0.9]).tolist() == [True, False, False]
    m, lo, hi, p = L.boot_cluster(np.ones(50), np.arange(50) // 5)
    assert m == 1.0 and lo == 1.0 and p == 0.0


def test_placebo_stop_side():
    assert L.placebo_stop(1, np.array([100.0]), [0.01])[0] == 99.0
    assert L.placebo_stop(-1, np.array([100.0]), [0.01])[0] == 101.0
