import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core

NOFUND = lambda a, b: 0.0


def bars(n=40, p=100.0):
    return [p] * n, [p] * n, [p] * n, [p] * n


def test_runs():
    assert core.runs([5, 4, 3, 4, 3, 2, 1], False) == [0, 1, 2, 0, 1, 2, 3]
    assert core.runs([1, 2, 3, 2], True) == [0, 1, 2, 0]


def test_long_target_hit():
    o, h, l, c = bars()
    l[0] = 99.0                      # setup low 99, atr 1, k 1 -> stop 98, entry 100, R 2, target 104
    h[3] = 104.5
    ret, xj = core.fwd_trade(o, h, l, c, 0, 1, 1.0, 1.0, NOFUND)
    assert xj == 3 and abs(ret - (0.04 - core.RT_FEE)) < 1e-12


def test_long_stop_before_target_same_bar():
    o, h, l, c = bars()
    l[0] = 99.0
    h[2] = 105.0
    l[2] = 97.0
    ret, xj = core.fwd_trade(o, h, l, c, 0, 1, 1.0, 1.0, NOFUND)
    assert xj == 2 and abs(ret - (-0.02 - core.RT_FEE)) < 1e-12


def test_short_mirror_and_time_exit_and_funding():
    o, h, l, c = bars()
    h[0] = 101.0                     # stop 102, R 2, target 96
    c[2 + core.HOLD - 1] = 99.0
    ret, xj = core.fwd_trade(o, h, l, c, 0, -1, 1.0, 1.0, lambda a, b: 0.001)
    assert xj == 2 + core.HOLD - 1 and abs(ret - (0.01 - core.RT_FEE + 0.001)) < 1e-12


def test_bad_geometry_skipped():
    o, h, l, c = bars()
    l[0] = 100.0
    assert core.fwd_trade(o, h, l, c, 0, 1, 0.0, 1.0, NOFUND) is None
