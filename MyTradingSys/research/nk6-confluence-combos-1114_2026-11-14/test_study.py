import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study


def synth(n_days=150, seed=1):
    rng = np.random.default_rng(seed); n = n_days * 96
    c = 100 * np.exp(np.cumsum(rng.normal(0, 0.003, n)) + np.linspace(0, 0.6, n))
    o = np.r_[c[0], c[:-1]]; sp = np.abs(rng.normal(0, 0.002, n)) * c
    return dict(ts=(np.arange(n) * 900000 + 1577836800000).astype(np.int64), o=o,
                h=np.maximum(o, c) + sp, l=np.minimum(o, c) - sp, c=c, v=rng.uniform(1, 5, n))


def test_causality():
    """Features at bars before T must not change when later data is removed (fails under STUDY_BUG=1)."""
    D = synth(); a = study.features(D)
    for T in range(70 * 96 + 7, 140 * 96, 97 * 3):
        b = study.features({k: v[:T] for k, v in D.items()})
        assert np.array_equal(np.nan_to_num(a["phase"][:T], nan=9), np.nan_to_num(b["phase"], nan=9)), "phase uses future"
        assert np.array_equal(a["long"][:, :T], b["long"]), "long layers use future"
        assert np.array_equal(a["short"][:, :T], b["short"]), "short layers use future"


def test_simulate_stop_and_target():
    n = 60
    o = np.full(n, 100.0); h = np.full(n, 100.2); l = np.full(n, 99.8); c = np.full(n, 100.0)
    atr = np.full(n, 1.0)
    l2 = l.copy(); l2[6] = 98.9
    g, f, ex = study.simulate(dict(o=o, h=h, l=l2, c=c), atr, 1)
    assert g[5] == -1.0 and ex[5] == 6
    h2 = h.copy(); h2[8] = 102.5
    g, f, ex = study.simulate(dict(o=o, h=h2, l=l, c=c), atr, 1)
    assert g[7] == 2.0 and ex[7] == 8
    assert abs(f[7] - 1e-4 * 100 / 1.0) < 1e-12
