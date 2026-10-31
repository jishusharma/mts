"""F4 tests: written before f4lib.py. Run: python -m pytest test_f4.py -q"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f4lib  # noqa: E402

TAKER = 0.0005


def _walk(n8=400, seed=1):
    rng = np.random.default_rng(seed)
    n = n8 * 8
    c = 20000 * np.exp(np.cumsum(rng.normal(0, 0.004, n)))
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, 0.001, n)))
    l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, 0.001, n)))
    v = rng.uniform(50, 150, n)
    tbv = v * rng.uniform(0.3, 0.7, n)
    t = 1_500_000_000 // 28800 * 28800 + np.arange(n) * 3600
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v, "tbv": tbv})


def test_build_8h_complete_buckets_only():
    d = _walk(10)
    d = d.drop(index=[12]).reset_index(drop=True)          # hole inside 2nd bucket
    b = f4lib.build_8h(d)
    assert len(b) == 9
    assert (b.t % 28800 == 0).all()
    assert b.iloc[0].o == d.iloc[0].o and b.iloc[0].c == d.iloc[7].c
    assert abs(b.iloc[0].v - d.v.iloc[:8].sum()) < 1e-9


def test_cvd_proxy_by_hand_on_3_bars():
    v = np.array([10.0, 20.0, 30.0])
    tbv = np.array([7.0, 5.0, 12.0])
    delta = f4lib.delta(v, tbv)
    assert list(delta) == [4.0, -10.0, -6.0]               # 2*7-10, 2*5-20, 2*12-30
    s = f4lib.cvd_slope(v, tbv, win=3)
    assert abs(s[2] - (4 - 10 - 6) / 60.0) < 1e-12
    assert np.isnan(s[1])


def test_features_causal_truncation():
    d = _walk(300)
    b = f4lib.build_8h(d)
    F = f4lib.features(b)
    s = 200
    b2 = b.iloc[: s + 1].copy()
    F2 = f4lib.features(b2)
    for col in F.columns:
        assert np.isclose(F[col].iloc[s], F2[col].iloc[s], equal_nan=True), col
    b3 = b.copy()
    b3.loc[s + 1:, ["o", "h", "l", "c", "v", "tbv"]] *= 3.7        # future altered
    F3 = f4lib.features(b3)
    for col in F.columns:
        assert np.isclose(F[col].iloc[s], F3[col].iloc[s], equal_nan=True), col


def test_trade_sim_stop_target_time_fee():
    E = 100.0
    # short, stop 102 (R=2), target 96. Hour 1 high 102.5 -> stop.
    r, pct = f4lib.sim_trade(-1, E, 102.0, np.array([99.0, 99.5]), np.array([101.0, 102.5]), 100.0)
    assert abs(r - (-1.0 - TAKER * (100.0 + 102.0) / 2.0)) < 1e-12
    # short target hit: low 95.5 <= 96 on first hour, high < stop
    r, _ = f4lib.sim_trade(-1, E, 102.0, np.array([95.5]), np.array([101.0]), 97.0)
    assert abs(r - (2.0 - TAKER * (100.0 + 96.0) / 2.0)) < 1e-12
    # both touched in the same hour: stop first
    r, _ = f4lib.sim_trade(-1, E, 102.0, np.array([95.0]), np.array([103.0]), 99.0)
    assert r < -0.99
    # time exit at final close 98: gross (100-98)/2 = 1.0
    r, pct = f4lib.sim_trade(-1, E, 102.0, np.array([98.5, 97.9]), np.array([100.5, 100.2]), 98.0)
    assert abs(r - (1.0 - TAKER * (100.0 + 98.0) / 2.0)) < 1e-12
    assert abs(pct - ((100 - 98) / 100 * 100 - TAKER * (100 + 98) / 100 * 100)) < 1e-9
    # long mirror: stop 98 (R=2), target 104
    r, _ = f4lib.sim_trade(1, E, 98.0, np.array([99.0]), np.array([104.2]), 101.0)
    assert abs(r - (2.0 - TAKER * (100.0 + 104.0) / 2.0)) < 1e-12
    # invalid risk
    assert np.isnan(f4lib.sim_trade(-1, E, 99.0, np.array([99.0]), np.array([100.0]), 99.5)[0])


def _squeeze_frame():
    """60 flat low-vol 8h bars, then one big down bar on a volume spike."""
    n = 60
    c = 100 + 0.05 * np.sin(np.arange(n))
    c = np.r_[c, 92.0]
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) + 0.02
    l = np.minimum(o, c) - 0.02
    v = np.r_[np.full(n, 100.0) + np.sin(np.arange(n)), 600.0]
    b = pd.DataFrame({"t": np.arange(n + 1) * 28800, "o": o, "h": h, "l": l, "c": c, "v": v, "tbv": v * 0.4})
    return b


def test_rule_detector_on_squeeze_and_not_on_noise():
    # bw percentile of s-1 among the 90 bars before: needs 90 bars of history with wider bw earlier
    rng = np.random.default_rng(3)
    n0 = 100
    c0 = 100 + np.cumsum(rng.normal(0, 1.5, n0))                # wide bands early
    c1 = c0[-1] + 0.03 * np.sin(np.arange(40))                  # squeeze
    c = np.r_[c0, c1, c1[-1] - 9.0]
    n = len(c)
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) + 0.02
    l = np.minimum(o, c) - 0.02
    v = np.r_[np.full(n - 1, 100.0) + np.sin(np.arange(n - 1)), 700.0]
    b = pd.DataFrame({"t": np.arange(n) * 28800, "o": o, "h": h, "l": l, "c": c, "v": v, "tbv": v * 0.4})
    F = f4lib.features(b)
    ev = f4lib.rule_events(F)
    assert ev[n - 1] and ev.sum() == 1
    v2 = v.copy()
    v2[-1] = 101.0                                              # no volume spike -> no event
    b2 = b.assign(v=v2, tbv=v2 * 0.4)
    assert f4lib.rule_events(f4lib.features(b2)).sum() == 0
    # noise only
    assert f4lib.rule_events(f4lib.features(_walk(100, 5).pipe(f4lib.build_8h))).sum() <= 3


def test_pvalue_detects_planted_edge_not_null():
    rng = np.random.default_rng(7)
    pool = rng.normal(0, 1, 5000)
    base = f4lib.draw_means(pool, np.zeros(5000, dtype=int), np.array([150]), 1000, 5)
    null = rng.normal(0, 1, 150)
    planted = null + 0.3
    assert f4lib.p_greater(planted.mean(), base) < 0.05
    assert f4lib.p_greater(null.mean(), base) > 0.05
