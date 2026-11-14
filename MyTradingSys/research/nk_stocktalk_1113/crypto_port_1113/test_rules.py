import numpy as np, pandas as pd, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import rules

def test_rsi_extremes_and_known_value():
    up = pd.Series(np.arange(1, 60, dtype=float)); assert rules.rsi_wilder(up, 14).iloc[-1] == 100
    dn = pd.Series(np.arange(60, 1, -1, dtype=float)); assert rules.rsi_wilder(dn, 14).iloc[-1] == 0

def test_wma_weights():
    s = pd.Series([1.0, 2, 3]); assert abs(rules.wma(s, 3).iloc[-1] - (1 * 1 + 2 * 2 + 3 * 3) / 6) < 1e-12

def test_hilega_buy_in_uptrend():
    c = pd.Series(np.linspace(100, 200, 200) + np.sin(np.arange(200)) * 0.3)
    assert rules.hilega_state(c).iloc[-1] in (1, 0)

def test_fwd_ret_and_bh():
    c = np.array([1.0, 2.0, 4.0]); r = rules.fwd_ret(c, np.array([0, 1, 2]), np.array([2, 2, 3]))
    assert r[0] == 3.0 and r[1] == 1.0 and np.isnan(r[2])
    assert list(rules.bh([0.001, 0.5, 0.9], 0.1)) == [True, False, False]
