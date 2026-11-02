import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tsfm_lib as L  # noqa: E402


def test_pinball_hand_computed():
    # y=2, quantile forecasts q=[1,3] at levels [0.1,0.9]
    # level .1: y>q -> 0.1*(2-1)=0.1 ; level .9: y<q -> (1-0.9)*(3-2)=0.1 ; mean 0.1
    assert L.pinball(np.array([2.0]), np.array([[1.0, 3.0]]), [0.1, 0.9]) == pytest.approx(0.1)
    # y=5 above both: .1*4=.4 and .9*2=1.8 -> mean 1.1
    assert L.pinball(np.array([5.0]), np.array([[1.0, 3.0]]), [0.1, 0.9]) == pytest.approx(1.1)


def test_coverage_five_points():
    y = np.array([0.0, 1.0, 2.0, 2.4, 10.0])
    lo = np.array([-1.0] * 5)
    hi = np.array([2.5, 2.5, 2.5, 2.5, 2.5])
    assert L.coverage(y, lo, hi) == pytest.approx(0.8)


def test_refuses_bar_after_dev():
    ts = pd.to_datetime(['2024-06-30 20:00', '2024-07-01 00:00'])
    with pytest.raises(Exception):
        L.guard_dev(ts)
    L.guard_dev(ts[:1])


def test_bars_complete_only():
    idx = pd.date_range('2022-01-01', periods=480 + 100, freq='min')
    df = pd.DataFrame({'open': 1.0, 'high': 2.0, 'low': 0.5, 'close': np.arange(len(idx)) + 1.0}, index=idx)
    b = L.build_bars(df, '4h')
    assert len(b) == 2  # 580 min = 2 full 4h bars, partial third dropped
    assert b['close'].iloc[0] == 240.0


def test_week_block_bootstrap_ci_orders():
    rng = np.random.default_rng(0)
    r = rng.normal(0.5, 0.1, 200)
    weeks = np.repeat(np.arange(20), 10)
    lo, hi = L.week_boot(r, weeks, n=500, seed=1)
    assert 0.4 < lo < 0.5 < hi < 0.6
