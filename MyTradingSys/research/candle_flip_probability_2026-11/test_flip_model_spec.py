"""Spec test for flip_model.py, written from the module docstring, the function docstrings and PRE_REG (not from the code body).
Expected numbers are hand-computed. FLIP_MODEL_PATH (env) points the test at a mutated copy of the module."""
import importlib.util
import math
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent


@pytest.fixture(scope="module")
def fm():
    src = Path(os.environ.get("FLIP_MODEL_PATH", HERE / "flip_model.py"))
    spec = importlib.util.spec_from_file_location("flipspec_flip_model", src)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_p_keep_contract(fm):
    # docstring: P(keeps) = Phi(|d|/sqrt(t)); d = 0 gives 0.5; hand values Phi(1)=0.841345, Phi(2)=0.977250, Phi(0.5)=0.691462
    assert float(fm.p_keep(0.0, 0.3)) == pytest.approx(0.5, abs=1e-12)
    assert float(fm.p_keep(1.0, 1.0)) == pytest.approx(0.841345, abs=1e-6)
    assert float(fm.p_keep(-2.0, 1.0)) == pytest.approx(0.977250, abs=1e-6)
    assert float(fm.p_keep(0.5, 1.0)) == pytest.approx(0.691462, abs=1e-6)
    assert float(fm.p_keep(0.5, 0.25)) == pytest.approx(0.841345, abs=1e-6)   # sqrt(t) scaling, not t
    assert float(fm.p_keep(1.0, 4.0)) == pytest.approx(0.691462, abs=1e-6)    # more time left -> less certain
    # monotone: larger |d| -> higher; more time left -> lower
    assert float(fm.p_keep(1.5, 0.5)) > float(fm.p_keep(1.0, 0.5))
    assert float(fm.p_keep(1.0, 0.2)) > float(fm.p_keep(1.0, 0.8))


def test_p_close_colour_units_and_clip(fm):
    # sigma_bar = ATR / (2*sqrt(2/pi)) = ATR / 1.5958, so d_atr = 1.5958 is d_sd = 1 at t = 1
    assert fm.SIGMA_K == pytest.approx(1.5958, abs=1e-4)
    assert fm.P_close_colour("1h", 1.0, 1.0, None) == pytest.approx(0.94473, abs=2e-4)   # Phi(1.5958)
    assert fm.P_close_colour("1h", 0.4, 0.5, {"delta": 0.03}) == pytest.approx(
        fm.P_close_colour("1h", 0.4, 0.5, None) + 0.03, abs=1e-12)
    assert fm.P_close_colour("1h", 0.0, 0.5, {"delta": -0.9}) == pytest.approx(0.001)   # lower clip
    assert fm.P_close_colour("1h", 3.0, 0.1, {"delta": 0.5}) == pytest.approx(0.999)    # upper clip
    assert fm.P_close_colour("1h", 0.3, 0.5, {"delta": float("nan")}) == pytest.approx(fm.P_close_colour("1h", 0.3, 0.5, None))


def test_p_close_colour_fail_closed_and_edges(fm):
    for bad in ((float("nan"), 0.5), (0.3, float("inf")), (0.3, -0.1), (0.3, 1.0001), ("x", 0.5), (None, 0.5)):
        assert fm.P_close_colour("1h", *bad) is None, bad
    assert fm.P_close_colour("nope", 0.3, 0.5) is None
    assert fm.P_close_colour("1h", -0.3, 0.0) == 1.0     # bar over, colour final
    assert fm.P_close_colour("1h", 0.0, 0.0) == 0.5
    assert fm.P_close_colour("1h", 0.3, 1.0) is not None  # t = 1 allowed
    assert fm.TFS[0] == "1w" and fm.TFS[-1] == "1m" and len(fm.TFS) == 20


def test_cluster_mean_z_hand_computed(fm):
    # e = [1,3,2,6], clusters [0,0,1,1]: mean 3, cluster sums of (e-mean) = -2, +2, G = 2
    # var = G/(G-1) * sum(s^2) / n^2 = 2 * 8 / 16 = 1 -> se 1, z 3, p = erfc(3/sqrt2) = 0.0026998
    mean, se, z, p = fm.cluster_mean_z([1, 3, 2, 6], ["a", "a", "b", "b"])
    assert (mean, se, z) == (pytest.approx(3.0), pytest.approx(1.0), pytest.approx(3.0))
    assert p == pytest.approx(0.0026998, abs=1e-6)
    # one cluster: se undefined, p = 1; fewer than 2 rows: nan, p = 1
    m, se, z, p = fm.cluster_mean_z([1.0, 2.0], [0, 0])
    assert m == pytest.approx(1.5) and math.isnan(se) and math.isnan(z) and p == 1.0
    m, se, z, p = fm.cluster_mean_z([1.0], [0])
    assert math.isnan(m) and p == 1.0
    # sign of the mean does not change p (two-sided)
    assert fm.cluster_mean_z([-1, -3, -2, -6], [0, 0, 1, 1])[3] == pytest.approx(0.0026998, abs=1e-6)


def test_load_family_keys(fm):
    # contract: sess >= 3 dropped; session names 0/1/2 = Asia/EU/US; cell = htf/session/bb; cid = tf|bar_ms; wid = UTC week index of the bar open from START_MS
    s = fm.START_MS
    df = pd.DataFrame({"sess": [0, 1, 2, 3], "htf": ["aligned", "split", "aligned", "split"], "bb": ["at", "in", "at", "in"],
                       "tf": ["1h", "4h", "1h", "1h"], "bar_ms": [s, s + fm.WEEK_MS - 1, s + fm.WEEK_MS, s + 2 * fm.WEEK_MS + 5]})
    import io
    out = fm.load_family(io.StringIO(df.to_csv(index=False)))
    assert len(out) == 3
    assert list(out["session"]) == ["Asia", "EU", "US"]
    assert list(out["cell"]) == ["aligned/Asia/at", "split/EU/in", "aligned/US/at"]
    assert list(out["cid"]) == ["1h|%d" % s, "4h|%d" % (s + fm.WEEK_MS - 1), "1h|%d" % (s + fm.WEEK_MS)]
    assert list(out["wid"]) == [0, 0, 1]
    assert fm.WEEK_MS == 604800000


def test_fit_baseline_uses_fit_rows_and_falls_back(fm):
    # contract: bins with < 30 fit rows fall back to the null p0; a bin with >= 30 fit rows gets the fit mean of y
    n = 40
    g = pd.DataFrame({"d_open": np.full(2 * n, 1.0), "t_left": np.full(2 * n, 0.9),
                      "y_open": np.r_[np.ones(n), np.zeros(n)], "p0_open": np.full(2 * n, 0.7),
                      "win": ["fit"] * n + ["score"] * n})
    pb = fm.fit_baseline(g, "open")
    assert np.allclose(pb, 1.0)                      # fit rows only: mean y = 1, score rows' y = 0 must not leak in
    g2 = g.copy()
    g2["win"] = ["fit"] * 10 + ["score"] * (2 * n - 10)   # 10 fit rows < 30
    assert np.allclose(fm.fit_baseline(g2, "open"), 0.7)

