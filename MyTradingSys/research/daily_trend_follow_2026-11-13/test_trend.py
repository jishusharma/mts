import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import trend_lib as T

def test_donchian_enter_and_exit():
    c = np.array([10.0] * 25 + [11.0, 12.0, 13.0, 9.0, 9.0]); h = c + 0.1; l = c - 0.1
    W = T.donchian(h, l, c, 20, 10)
    assert W[24] == 0 and W[25] > 0           # breakout close above the prior 20-day high
    assert W[27] > 0 and W[28] < 0            # close 9 < 10-day low: long exits, short enters (below 20-day low)

def test_size_floor_and_cap():
    assert T.size(0.001) == 0.5 and abs(T.size(0.05) - 0.2) < 1e-12

def test_gate():
    W = np.array([0.1, -0.1, 0.1, -0.1]); btc = np.array([10, 10, 8, 8.0]); m = np.array([9, 9, 9, 9.0])
    assert list(T.gate(W, btc, m)) == [0.1, 0.0, 0.0, -0.1]

def test_tsm_monday_rebalance():
    c = np.linspace(10, 20, 60); dow = np.arange(60) % 7
    W = T.tsm(c, dow, 30)
    assert W[30] == 0 or W[30] > 0
    assert (W[W != 0] > 0).all()
