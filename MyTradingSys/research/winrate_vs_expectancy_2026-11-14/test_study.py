import os
import sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study


def mk(rows, pad=study.W + 5):
    a = np.array(list(rows) + [(100, 100, 100, 100)] * pad, float)
    return a[:, 0], a[:, 1], a[:, 2], a[:, 3]


def run(rows, T=0.01, S=0.01):
    O, H, L, C = mk(rows)
    ex, fp, ok = study.walk(O, H, L, C, np.array([0]), np.array([100.0]), T, S)
    assert ok[0]
    return int(ex[0]), float(fp[0])


def test_stop_first_when_both_in_one_bar():
    assert run([(100, 102, 98, 100)]) == (0, 99.0)


def test_target_fill():
    j, p = run([(100, 100.5, 99.5, 100), (100, 101.2, 99.8, 101)])
    assert (j, round(p, 6)) == (1, 101.0)


def test_gap_through_stop_fills_at_open():
    assert run([(100, 100.2, 99.9, 100), (98, 99, 97, 98)]) == (1, 98.0)


def test_time_stop_closes_last_bar():
    O, H, L, C = mk([])
    C[study.W - 1] = 100.3
    ex, fp, ok = study.walk(O, H, L, C, np.array([0]), np.array([100.0]), 0.01, 0.01)
    assert (int(ex[0]), float(fp[0])) == (study.W - 1, 100.3)


def test_nan_window_dropped():
    O, H, L, C = mk([])
    L[10] = np.nan
    assert not study.walk(O, H, L, C, np.array([0]), np.array([100.0]), 0.01, 0.01)[2][0]


def test_greedy_one_position():
    k = study.greedy(np.array([0, 5, 20]), np.array([10, 12, 25]), np.array([True] * 3))
    assert k.tolist() == [True, False, True]


def test_maker_needs_trade_through():
    n = study.W + 10
    O = np.full(n, 100.0); H = O.copy(); L = O.copy(); C = O.copy()
    L[1] = 100.0  # touches the limit exactly at 100: not a trade-through
    s = {"X": np.array([0])}
    assert study.simulate(O, H, L, C, s, ("maker",))[0][4].size == 0
    L[1] = 99.9
    assert study.simulate(O, H, L, C, s, ("maker",))[0][4].size == 1


def test_rsi_hand_value():
    c = np.array([44, 44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84, 46.08, 45.89, 46.03, 45.61, 46.28], float)
    d = np.diff(c)
    exp = 100 - 100 / (1 + d[d > 0].sum() / -d[d < 0].sum())
    assert abs(study.wilder_rsi(c)[14] - exp) < 1e-9
