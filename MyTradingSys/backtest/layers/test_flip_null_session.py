"""Session-adjusted null for the candle-flip study. Expected numbers are hand-computed from the normal table (FORMULAS.md style), not read from the code."""
import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
import pytest

RES = Path(__file__).resolve().parents[2] / "research" / "candle_flip_probability_2026-11"


def _load(name):
    spec = importlib.util.spec_from_file_location("flipsess_" + name, RES / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def sn():
    return _load("session_null")


def _two_session_profile():
    p = np.ones(24)
    p[:12] = 0.5       # quiet half-day (UTC 00-12)
    p[12:] = 1.5       # busy half-day (UTC 12-24); mean is exactly 1
    return p


def test_hour_profile_recovers_two_session_variance(sn):
    # synthetic 1m closes: log-return sd 0.001 for hours 0-11, 0.003 for hours 12-23 -> variance ratio 9, normalised mean 1 -> 0.2 and 1.8 (1e-6 and 9e-6, mean 5e-6)
    rng = np.random.default_rng(5)
    n = 24 * 60 * 40
    hr = (np.arange(n) // 60) % 24
    sd = np.where(hr < 12, 0.001, 0.003)
    c = 100.0 * np.exp(np.cumsum(rng.standard_normal(n) * sd))
    prof = sn.hour_profile(c, t0_ms=0)
    assert prof.mean() == pytest.approx(1.0, abs=1e-9)
    assert prof[:12].mean() == pytest.approx(0.2, abs=0.02)
    assert prof[12:].mean() == pytest.approx(1.8, abs=0.08)


def test_variance_clock_differs_from_flat_with_two_sessions(sn):
    # day bar (S = 1440) at the close of minute 719 (12:00): flat t_left = 1 - 720/1440 = 0.5.
    # session clock: remaining weight 720 * 1.5 = 1080 over the prior-14-bar mean bar weight 1440 -> 0.75.
    prof = _two_session_profile()
    cw = sn.weight_cumsum(prof, t0_ms=0, n_min=1440 * 40)
    ts = sn.session_t_left(cw, np.array([20]), np.array([719]), 1440)
    assert ts[0] == pytest.approx(0.75, abs=1e-12)
    # null P(keeps) at d = 1 sd: session Phi(1/sqrt(.75)) = Phi(1.1547) = 0.87589, flat Phi(1/sqrt(.5)) = Phi(1.4142) = 0.92135
    p_s = 0.5 * (1 + math.erf(1.0 / math.sqrt(ts[0]) / math.sqrt(2)))
    p_f = 0.5 * (1 + math.erf(1.0 / math.sqrt(0.5) / math.sqrt(2)))
    assert p_s == pytest.approx(0.87589, abs=2e-4)
    assert p_f == pytest.approx(0.92135, abs=2e-4)
    assert abs(p_s - p_f) > 0.04
    # and the other way round: at 18:00 (minute 1079) flat t_left = 0.25, session = 360 * 1.5 / 1440 = 0.375
    assert sn.session_t_left(cw, np.array([20]), np.array([1079]), 1440)[0] == pytest.approx(0.375, abs=1e-12)


def test_flat_profile_reproduces_flat_t_left(sn):
    cw = sn.weight_cumsum(np.ones(24), t0_ms=0, n_min=4320 * 25)
    for S, j in ((60, 14), (240, 100), (1440, 719), (4320, 1000)):
        b = np.array([20])
        got = sn.session_t_left(cw, b, np.array([j]), S)[0]
        assert got == pytest.approx(1.0 - (j + 1.0) / S, abs=1e-12)


def test_fit_window_only(sn):
    # the profile must be fitted on closes strictly before the cut: a late regime change must not move it
    n = 24 * 60 * 20
    c = np.ones(n) * 100.0 + np.cumsum(np.where(np.arange(n) < n // 2, 0.01, 0.0))
    a = sn.hour_profile(c[: n // 2], t0_ms=0)
    c2 = c.copy()
    c2[n // 2:] += np.random.default_rng(1).standard_normal(n - n // 2) * 5
    b = sn.hour_profile(c2, t0_ms=0, upto=n // 2)
    assert np.allclose(a, b)
