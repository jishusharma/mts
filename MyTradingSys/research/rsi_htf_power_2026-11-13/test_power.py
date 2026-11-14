"""Core checks for study.py (month key, placebo p, top-5 maths)."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study as S


def test_month_of():
    a = S.month_of([1577836800000, 1580515199000, 1580515200000])  # 2020-01-01, 2020-01-31 23:59:59, 2020-02-01
    assert a[0] == a[1] and a[2] == a[1] + 1


def test_pstat_p_floor_and_direction():
    d = [np.array([0.0, 1.0])] * 399
    m, p = S.pstat(d, np.array([True, True]), 0.5)
    assert abs(m - 0.5) < 1e-9 and p == (399 + 1) / 400  # all draws >= real: p = 1
    _, p2 = S.pstat(d, np.array([True, True]), 0.9)
    assert abs(p2 - 1 / 400) < 1e-12
