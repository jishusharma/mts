import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from breadth_lib import find_events, find_entry, breadth, fwd_stop2r

def test_events_need_quiet():
    B = np.array([0.0] * 40 + [0.6, 0.7, 0.0, 0.0, 0.6] + [0.0] * 40 + [0.6])
    assert find_events(B, 0.5, 30) == [40, 85]

def test_entry_needs_fall_and_btc_up():
    B = np.array([0.0, 0.6, 0.7, 0.5, 0.3]); c = np.array([10, 9, 8, 7, 8.0])
    assert find_entry(B, c, 1) == 4   # bar2 B up, bar3 B down but btc down, bar4 ok
    assert find_entry(B, c, 1, maxwait=2) is None

def test_breadth_needs_10_coins():
    m = np.full((12, 3), np.nan); m[:, 2] = 20; m[:5, 1] = 20
    b = breadth(m); assert np.isnan(b[1]) and b[2] == 1.0

def test_stop2r():
    bo = [0, 100, 100, 100.0]; bh = [0, 101, 111, 111]; bl = [0, 99, 98, 98]; bc = [100, 100, 105, 105]
    assert fwd_stop2r(0, 95, bo, bh, bl, bc)[0] == 2  # bar1 low 99>95 no stop; bar2 high 111>=110 tp
