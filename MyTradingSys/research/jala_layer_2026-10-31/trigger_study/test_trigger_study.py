import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import trigger_study as ts

IDX = pd.date_range("2022-03-01", periods=5, freq="D")


def test_close_under_and_over_known_days():
    c = pd.Series([10.0, 10, 10, 8, 12], index=IDX)
    # sma3: nan nan 10 9.333 10 ; under-cross at idx3 (10>=10 then 8<9.33); over-cross at idx4 (8<9.33 then 12>10)
    assert list(ts.events(c, "under", 1, 3)) == [IDX[3]]
    assert list(ts.events(c, "over", 1, 3)) == [IDX[4]]


def test_iron_dome_cross_known_day():
    c = pd.Series([1.0, 2, 3, 4, 5, 6, 7, 8], index=pd.date_range("2022-03-01", periods=8))
    # sma2 vs sma4 on rising series: sma2>sma4 from the first day both exist (idx3) -> no prior state, no cross
    assert len(ts.events(c, "golden", 2, 4)) == 0
    c2 = pd.Series([5.0, 5, 5, 5, 1, 1, 9, 9, 9], index=pd.date_range("2022-03-01", periods=9))
    # sma2: -,5,5,5,3,1,5,9,9 ; sma4: -,-,-,5,4,3,3,5,5  -> sma2-sma4: idx3 0,idx4 -1,idx5 -2,idx6 +2
    assert list(ts.events(c2, "death", 2, 4)) == [c2.index[4]]
    assert list(ts.events(c2, "golden", 2, 4)) == [c2.index[6]]


def test_net_forward_return_sign_and_cost():
    c = pd.Series([100.0, 110, 99], index=IDX[:3])
    long_net = ts.fwd_net(c, [IDX[0]], 1, +1, cost=0.002)
    short_net = ts.fwd_net(c, [IDX[1]], 1, -1, cost=0.002)
    assert abs(long_net[0] - (0.10 - 0.002)) < 1e-12
    assert abs(short_net[0] - (0.10 - 0.002)) < 1e-12


def test_horizon_past_dev_end_dropped():
    idx = pd.date_range("2024-06-20", periods=20, freq="D")
    c = pd.Series(np.arange(1.0, 21), index=idx)
    ev = ts.dev_event_filter(c, [idx[0], idx[12]], 10)
    assert ev == [idx[0]]  # idx[12]+10d = 2024-07-12 >= DEV_END
