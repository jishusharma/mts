"""Causality + accounting tests. Run: pytest test_study.py. Under STUDY_BUG=1 or 2 the causality test must FAIL."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib


def synth(n=96 * 300, seed=3):
    r = np.random.default_rng(seed)
    t = (np.arange(n) * 900000 + 1546300800000).astype(np.int64)
    drift = np.repeat(r.choice([-0.0012, 0.0, 0.0012], n // 480 + 1), 480)[:n]
    c = 100 * np.exp(np.cumsum(drift + r.normal(0, 0.004, n)))
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) * (1 + np.abs(r.normal(0, 0.002, n)))
    l = np.minimum(o, c) * (1 - np.abs(r.normal(0, 0.002, n)))
    return t, o, h, l, c, np.ones(n)


def run(t, o, h, l, c, v):
    days, lab = lib.daily_phase_table(t, o, h, l, c, v)
    ph = lib.phase_for_bars(t, days, lab)
    F = lib.features(t, o, h, l, c)
    S = lib.signals(t, o, h, l, c, F, ph)
    return ph, S


def perturb(arrs, T, seed=9):
    t, o, h, l, c, v = [a.copy() for a in arrs]
    r = np.random.default_rng(seed)
    f = np.exp(r.normal(0.02, 0.06, len(c) - T))
    for a in (o, h, l, c):
        a[T:] = a[T:] * f
    h[T:] = np.maximum.reduce([h[T:], o[T:], c[T:]]) * 1.02
    l[T:] = np.minimum.reduce([l[T:], o[T:], c[T:]]) * 0.98
    return t, o, h, l, c, v


def causal_ok():
    full = synth()
    ph0, S0 = run(*full)
    Bs = [s for s in S0 if s["type"] == "B"]
    Ts = [s["e"] + 1 for s in Bs[:15]] + [96 * k + 41 for k in range(60, 280, 20)]
    assert len(Bs) >= 5
    for T in Ts:
        ph1, S1 = run(*perturb(full, T))
        if not np.array_equal(ph0[:T], ph1[:T]):
            return False
        key = lambda S: sorted((s["type"], s["i"], s["e"], s["dir"], s["fit"]) for s in S if s["e"] < T)
        if key(S0) != key(S1):
            return False
    return True


def test_causal():
    assert causal_ok()


def test_detector_catches_bugs():
    for b in ("1", "2"):
        os.environ["STUDY_BUG"] = b
        try:
            assert not causal_ok(), f"bug {b} not detected"
        finally:
            os.environ.pop("STUDY_BUG", None)


def test_sim_long_target_and_stop():
    O = np.full(40, 100.0); H = O.copy(); L = O.copy(); H[1] = 101; H[2] = 103; L[1] = 99.5; L[2] = 99.8; L[3] = 99; C = O.copy()
    # entry at bar0 px100 dist1 long X1: target 102 hit bar2 -> +2R
    g, ex = lib.sim(O, H, L, C, np.array([0]), np.array([100.0]), np.array([1]), np.array([1.0]), "X1", np.array([False]))
    assert abs(g[0] - 2.0) < 1e-9 and ex[0] == 2
    # stop 99 hit at bar3 when target not reached
    H2 = H.copy(); H2[2] = 101
    g, ex = lib.sim(O, H2, L, C, np.array([0]), np.array([100.0]), np.array([1]), np.array([1.0]), "X1", np.array([False]))
    assert abs(g[0] + 1.0) < 1e-9 and ex[0] == 3


def test_min_stop_and_fee_fraction():
    d = lib.stop_dist(np.array([0.001]), np.array([0.01]), np.array([100.0]))
    assert abs(d[0] - 0.5) < 1e-9  # 0.5% floor dominates
    assert 12e-4 * 100 / d[0] < 0.25
