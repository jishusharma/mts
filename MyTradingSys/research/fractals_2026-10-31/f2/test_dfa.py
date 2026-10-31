"""Fail-first tests for dfa.py. Expected values are hand-derived or from the DFA definition, never from the module."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dfa  # noqa: E402


def fgn(n, hurst, seed):
    """Exact fractional Gaussian noise by Cholesky of the autocovariance g(k) = 0.5(|k+1|^2H - 2|k|^2H + |k-1|^2H)."""
    k = np.arange(n, dtype=float)
    g = 0.5 * (np.abs(k + 1) ** (2 * hurst) - 2 * np.abs(k) ** (2 * hurst) + np.abs(k - 1) ** (2 * hurst))
    idx = np.abs(np.subtract.outer(np.arange(n), np.arange(n)))
    cov = g[idx]
    return np.linalg.cholesky(cov + 1e-10 * np.eye(n)) @ np.random.default_rng(seed).standard_normal(n)


def test_fluct_hand_checked_alternating():
    # x = +1,-1,... (mean 0): profile y = 1,0,1,0 per box of 4. Line fit: slope = sum(y*(t-1.5))/5 = (-1.5+0.5)/5 = -0.2,
    # fitted 0.8,0.6,0.4,0.2 -> residuals 0.2,-0.6,0.6,-0.2 -> MSE (0.04+0.36+0.36+0.04)/4 = 0.2.
    x = np.tile([1.0, -1.0], 4)
    assert abs(dfa.fluct2(x, 4)[0] - 0.2) < 1e-12


def test_fluct_pure_linear_profile_is_zero():
    # constant returns after demeaning are zero -> profile 0; a ramp profile needs returns that are not constant:
    # x with y exactly linear inside a box cannot happen after demeaning unless x is constant, so check the zero case.
    assert dfa.fluct2(np.full(16, 3.0), 4)[0] == 0.0


def test_random_walk_returns_alpha_about_half():
    x = np.random.default_rng(1).standard_normal(20000)
    a = dfa.dfa_alpha(x)
    assert abs(a - 0.5) < 0.04, a


def test_persistent_fgn_above_half():
    # fGn H = 0.8 (autocov formula above). DFA-1 exponent of fGn equals H in expectation; tolerance wide for n = 2048.
    a = dfa.dfa_alpha(fgn(2048, 0.8, 2), scales=(8, 16, 32, 64, 128))
    assert a > 0.65, a


def test_antipersistent_fgn_below_half():
    a = dfa.dfa_alpha(fgn(2048, 0.25, 3), scales=(8, 16, 32, 64, 128))
    assert a < 0.38, a


def test_rolling_equals_direct_and_uses_only_past():
    r = np.random.default_rng(4).standard_normal(1200)
    h = dfa.rolling_alpha(r, window=480, chunk=100)
    assert np.isnan(h[:479]).all() and not np.isnan(h[479:]).any()
    for i in (479, 700, 1199):
        assert abs(h[i] - dfa.dfa_alpha(r[i - 479:i + 1])) < 1e-9
    # future-change test: altering returns after bar i leaves H[i] unchanged
    r2 = r.copy()
    r2[701:] = 99.0 * np.sign(np.arange(len(r) - 701) % 2 - 0.5)
    h2 = dfa.rolling_alpha(r2, window=480, chunk=100)
    assert h2[700] == h[700] and h2[479:701].tolist() == h[479:701].tolist()
