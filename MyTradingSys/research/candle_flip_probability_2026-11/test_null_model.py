"""Null-model contract for the candle-flip study. Expected numbers are hand-computed (standard normal table), not read from the code."""
import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent


def _load(name):
    spec = importlib.util.spec_from_file_location("flipstudy_" + name, HERE / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def fm():
    return _load("flip_model")


@pytest.fixture(scope="module")
def ft():
    return _load("flip_table")


def test_phi_at_open_is_half(fm):
    # d = 0: the price sits on the open, the remaining move is symmetric, P(keeps colour) = 0.5 whatever the time left
    for t in (1.0, 0.5, 0.1, 0.001):
        assert float(fm.p_keep(0.0, t)) == pytest.approx(0.5, abs=1e-12)
        assert fm.P_close_colour("1h", 0.0, t, None) == pytest.approx(0.5, abs=1e-12)


def test_known_values_from_the_normal_table(fm):
    # d = 1 sd, t = 1: Phi(1) = 0.841345; d = 0.5 sd, t = 0.25: |d|/sqrt(t) = 1 -> 0.841345; d = 2 sd, t = 1: Phi(2) = 0.977250
    assert float(fm.p_keep(1.0, 1.0)) == pytest.approx(0.841345, abs=1e-6)
    assert float(fm.p_keep(-0.5, 0.25)) == pytest.approx(0.841345, abs=1e-6)   # sign of d does not matter: it is the colour kept
    assert float(fm.p_keep(2.0, 1.0)) == pytest.approx(0.977250, abs=1e-6)
    # in ATR units: d_atr = d_sd / 1.5958 (sigma = ATR / 1.5958), so d_atr = 1/1.5958 = 0.62666 is d_sd = 1
    assert fm.P_close_colour("4h", 1.0 / (2 * math.sqrt(2 / math.pi)), 1.0, None) == pytest.approx(0.841345, abs=1e-5)
    # a cell shift is added then clipped to [0.001, 0.999]
    assert fm.P_close_colour("4h", 0.0, 0.5, {"delta": 0.02}) == pytest.approx(0.52)
    assert fm.P_close_colour("4h", 5.0, 0.01, {"delta": 0.5}) == pytest.approx(0.999)


def test_p_close_colour_fails_closed(fm):
    assert fm.P_close_colour("1h", float("nan"), 0.5, None) is None
    assert fm.P_close_colour("1h", 0.3, float("nan"), None) is None
    assert fm.P_close_colour("1h", 0.3, 1.5, None) is None        # more than the whole bar left
    assert fm.P_close_colour("7x", 0.3, 0.5, None) is None        # unknown timeframe
    assert fm.P_close_colour("1h", 0.3, 0.0, None) == 1.0         # bar over, colour final
    assert fm.P_close_colour("1h", 0.0, 0.0, None) == 0.5


def test_week_bar_anchor_is_monday(ft):
    # 2024-01-01T00:00Z is a Monday; a 1w bar is 10080 one-minute bars from there, so bar k opens START + k * 7 days
    import datetime
    assert datetime.datetime.fromtimestamp(ft.START_MS / 1000, datetime.timezone.utc).weekday() == 0
    assert ft.TF_MIN["1w"] == 7 * 1440 and ft.TF_MIN["5d"] == 5 * 1440 and ft.TF_MIN["7h"] == 420
    assert list(ft.offsets(3)) == [0, 1] and list(ft.offsets(2)) == [0] and len(ft.offsets(1)) == 0
    assert list(ft.offsets(10080)) == [1439, 2879, 4319, 5759, 7199, 8639]   # fractions k/7 of the week, minute index of the close


def _sim_walk(n_min, seed, sub=10):
    """1m OHLC of a driftless Gaussian random walk: `sub` sub-steps per minute so the 1m high/low are real intra-minute extremes."""
    rng = np.random.default_rng(seed)
    steps = rng.standard_normal((n_min, sub)) / math.sqrt(sub)         # sd 1 per minute
    path = 100_000.0 + np.cumsum(steps.ravel())
    p = path.reshape(n_min, sub)
    prev = np.concatenate([[100_000.0], p[:-1, -1]])
    return prev, p.max(1), p.min(1), p[:, -1]


def test_delta_zero_on_random_walk(fm, ft):
    # 2000 one-hour bars of a pure random walk, the same pipeline as the real table: realised keep-rate minus the null must be inside 2 se
    o, h, l, c = _sim_walk(60 * 2000, seed=1106)
    df = ft.tf_rows(o, h, l, c, 60, t0_ms=ft.START_MS, cut_ms=ft.START_MS + 10**13, max_rows=10**9, tf="1h")
    assert len(df) > 5000
    score = df.assign(win="score")                                       # cut far in the future would be fit; use all rows as one sample
    for col in ("open", "pc"):
        e = (df["y_" + col] - df["p0_" + col]).to_numpy()
        cid = df["bar_ms"].to_numpy()
        mean, se, z, p = fm.cluster_mean_z(e, cid)
        assert se > 0 and abs(mean) < 2 * se, (col, mean, se, z)


def test_delta_detects_a_planted_edge(fm):
    # a sample where the outcome keeps its colour 5 points more often than the null says: delta must read about +0.05 and clear 2 se
    rng = np.random.default_rng(7)
    n = 4000
    p0 = np.full(n, 0.6)
    y = (rng.random(n) < 0.65).astype(float)
    mean, se, z, p = fm.cluster_mean_z(y - p0, np.arange(n))
    assert mean == pytest.approx(0.05, abs=0.03) and z > 2 and p < 0.05


def test_own_timeframe_has_no_htf_cell(ft):
    # review #5: for a 1d or 1w row one of the two HTF colours IS the row's own colour, so the HTF cell is undefined ("na"); other rows get aligned / split
    o, h, l, c = _sim_walk(1440 * 40, seed=3, sub=2)
    far = ft.START_MS + 10**13
    d1 = ft.tf_rows(o, h, l, c, 1440, cut_ms=far, max_rows=10**9, tf="1d")
    h1 = ft.tf_rows(o, h, l, c, 60, cut_ms=far, max_rows=10**9, tf="1h")
    assert len(d1) > 50 and set(d1["htf"]) == {"na"}
    assert set(h1["htf"]) == {"aligned", "split"}


def test_week_clusters_are_wider_than_bar_clusters(fm):
    # review #1: rows of one UTC week share the 1d/1w colours; a cluster of the week must give a larger se than a cluster of the bar when the error is shared inside the week
    rng = np.random.default_rng(5)
    weeks = np.repeat(np.arange(60), 100)                                 # 60 weeks x 100 bars
    shared = np.repeat(rng.standard_normal(60) * 0.05, 100)
    e = shared + rng.standard_normal(6000) * 0.05
    _, se_bar, _, _ = fm.cluster_mean_z(e, np.arange(6000))
    _, se_week, _, _ = fm.cluster_mean_z(e, weeks)
    assert se_week > 3 * se_bar
