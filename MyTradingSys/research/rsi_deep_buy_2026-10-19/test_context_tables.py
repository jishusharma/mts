"""Tests for context_tables.py (RSI deep-buy Step F). Synthetic data only; expected numbers are hand computed
(see comments), never taken from the module."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import context_tables as ct  # noqa: E402

DAY = 86_400_000
CUT23 = int(np.datetime64("2023-01-01T00:00", "ms").astype("int64"))


def test_shrinkage_two_cell_hand_example():
    # parent p0 = 0.5, prior strength m = 10; cell A k=8,n=10 -> (8+10*0.5)/(10+10) = 13/20 = 0.65 ; cell B k=2,n=10 -> 7/20 = 0.35
    assert ct.shrink(8, 10, 0.5, 10.0) == pytest.approx(0.65)
    assert ct.shrink(2, 10, 0.5, 10.0) == pytest.approx(0.35)
    assert ct.shrink(0, 0, 0.5, 10.0) == pytest.approx(0.5)      # empty cell = parent


def test_empirical_bayes_strength_two_cells():
    # cells 2/10 and 8/10, parent 0.5: phat = .2,.8 ; between-variance 0.09 ; p(1-p) = 0.25 ; nbar = 10
    # Var = p(1-p)[rho + (1-rho)/n] -> 0.36 = rho + 0.1 - 0.1 rho -> rho = 0.26/0.9 = 13/45 ; m = 1/rho - 1 = 32/13
    m = ct.eb_strength([2, 8], [10, 10], [0.5, 0.5])
    assert m == pytest.approx(32 / 13, rel=1e-9)


def test_cell_under_30_days_returns_parent():
    assert ct.ctx_pred(k=9, n=10, days=29, p0=0.4, m=5.0) == pytest.approx(0.4)
    assert ct.ctx_pred(k=9, n=10, days=30, p0=0.4, m=5.0) == pytest.approx((9 + 5 * 0.4) / 15)


def test_walk_counts_use_only_resolved_events():
    # events at bars 10, 20, 30 ; resolve at 25, 28, 40 ; outcomes 1, 0, 1 ; days 0,0,1
    e = np.array([10, 20, 30]); res = np.array([25, 28, 40]); y = np.array([1.0, 0.0, 1.0])
    day = np.array([0, 0, 1])
    k, n, d = ct.walk_counts(e, res, y, day)
    # bar 10: nothing resolved ; bar 20: nothing (25 > 20) ; bar 30: events 1,2 resolved -> k=1, n=2, one day
    assert n.tolist() == [0, 0, 2] and k.tolist() == [0, 0, 1] and d.tolist() == [0, 0, 1]
    # planting a different outcome on the LAST event cannot change any earlier prediction
    y2 = y.copy(); y2[2] = 0.0
    k2, n2, d2 = ct.walk_counts(e, res, y2, day)
    assert k2.tolist() == k.tolist() and n2.tolist() == n.tolist()


def _rsi_path(n=3000, seed=3):
    rng = np.random.default_rng(seed)
    return 50 + np.cumsum(rng.normal(0, 2.0, n)).clip(-40, 40) * 0.5 + rng.normal(0, 1, n)


def test_trailing_features_ignore_future_bars():
    r = _rsi_path()
    ev = np.array([400, 900, 1500, 2100])
    y = (np.arange(len(ev)) % 2).astype(float)
    res = ev + 5
    f1 = ct.trailing_features(r, ev, res, y, tf=5, lbars=ct.lbars_for(5, 240))
    r2 = r.copy()
    r2[1501:] = r2[1501:] - 30                        # plant a future crash after the third event bar
    f2 = ct.trailing_features(r2, ev, res, y, tf=5, lbars=ct.lbars_for(5, 240))
    for a, b in zip(f1[:3], f2[:3]):
        assert a[:3].tolist() == b[:3].tolist()       # events 0-2 unchanged (event 3 may change: it sees the crash as past)


def test_floor_gap_state_hand_example():
    # 20 flat bars at 40 then an event bar at 35: floor = 40 (strictly earlier bars), gap = -5 -> state 0 (new low)
    r = np.r_[np.full(20, 40.0), 35.0, np.full(5, 45.0)]
    out = ct.trailing_features(r, np.array([20]), np.array([22]), np.array([1.0]), tf=1, lbars=10)
    assert out[0].tolist() == [0]
    # event bar 33 vs floor 31 (gap +2) -> state 1 ; vs floor 28 (gap +5) -> state 2
    r2 = np.r_[np.full(10, 31.0), 33.0]
    assert ct.trailing_features(r2, np.array([10]), np.array([12]), np.array([1.0]), 1, 10)[0].tolist() == [1]
    r3 = np.r_[np.full(10, 28.0), 33.0]
    assert ct.trailing_features(r3, np.array([10]), np.array([12]), np.array([1.0]), 1, 10)[0].tolist() == [2]


def test_touch_count_and_bounce_record_hand_example():
    # same-level events at bars 100, 150, 400 ; window 120 bars ; resolves at 110, 155, 410 ; outcomes 1, 0, 1
    r = np.full(500, 30.0)
    ev = np.array([100, 150, 400]); res = np.array([110, 155, 410]); y = np.array([1.0, 0.0, 1.0])
    out = ct.trailing_features(r, ev, res, y, tf=1, lbars=120)
    # event@150: one earlier event inside (30,150): touches=1 ; it resolved at 110<=150 and bounced -> share 1.0 -> state 2
    # event@400: earlier events at 100,150 are outside (280,400) -> touches 0, no record -> bounce state 0 ; event@100 none
    assert out[1].tolist() == [0, 1, 0]
    assert out[2].tolist() == [0, 2, 0]


def test_macro_labels_na_before_2023_and_causal():
    n = 900
    rng = np.random.default_rng(1)
    t0 = int(np.datetime64("2022-01-01T00:00", "ms").astype("int64"))
    dopen = t0 + np.arange(n) * DAY
    close = 20000 * np.exp(np.cumsum(rng.normal(0, 0.02, n)))
    high, low = close * 1.01, close * 0.99
    lab = ct.macro_labels(dopen, close, high, low)
    for s in ("trend", "vol", "range"):
        assert (lab[s][dopen < CUT23] == -1).all()
        assert (lab[s][dopen >= CUT23 + 40 * DAY] >= 0).all()
    # causal: planting a crash on day 700 leaves every label up to and including day 700 unchanged
    c2, h2, l2 = close.copy(), high.copy(), low.copy()
    c2[700:] *= 0.3; h2[700:] *= 0.3; l2[700:] *= 0.3
    lab2 = ct.macro_labels(dopen, c2, h2, l2)
    for s in lab:
        assert lab[s][:701].tolist() == lab2[s][:701].tolist()


def test_macro_trend_state_hand_example():
    # steadily rising close: ret30 > 0 and close above its 200d mean -> state 2 (up) for every labelled day
    n = 600
    t0 = int(np.datetime64("2022-01-01T00:00", "ms").astype("int64"))
    dopen = t0 + np.arange(n) * DAY
    close = 100.0 + np.arange(n)
    lab = ct.macro_labels(dopen, close, close + 1, close - 1)
    assert (lab["trend"][dopen >= CUT23] == 2).all()


def test_holm_adjustment_hand_example():
    # p = [0.01, 0.04, 0.03] -> sorted .01,.03,.04 -> adj .03, .06, .06 (monotone) -> original order [.03, .06, .06]
    assert ct.holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
