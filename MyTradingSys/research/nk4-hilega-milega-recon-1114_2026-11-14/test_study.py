"""Run: python -m pytest test_study.py. Under STUDY_BUG=1 (look-ahead) the causality and no-edge tests must FAIL."""
import os, subprocess, sys
import numpy as np
import study as S

HERE = os.path.dirname(os.path.abspath(__file__))


def walk(n=60000, seed=3):
    r = np.random.default_rng(seed)
    c = 100 * np.exp(np.cumsum(r.normal(0, 0.002, n)))
    o = np.concatenate([[100], c[:-1]])
    h = np.maximum(o, c) * (1 + np.abs(r.normal(0, 0.0007, n)))
    l = np.minimum(o, c) * (1 - np.abs(r.normal(0, 0.0007, n)))
    return o, h, l, c


def test_state_causal_prefix():
    c = walk()[3]
    full = S.hm_state(c)
    for cut in range(5000, 30000, 250):
        pre = S.hm_state(c[:cut + 1])
        assert pre[cut] == full[cut], cut


def test_no_edge_on_random_walk():
    o, h, l, c = walk()
    n = len(c) - len(c) % 3
    o, h, l, c = o[:n], h[:n], l[:n], c[:n]
    P = {k: S.tf_pack(o, h, l, c, k) for k in (1, 2, 3)}
    z = np.zeros(n, bool)
    B = dict(c=c, o=o, h=h, l=l, P=P, zl=z, zs=z, st={k: S.on5(P[k]["s"], k, n) for k in (1, 2, 3)},
             grid=np.arange(n, dtype=np.int64) * S.MS5, ph=np.full(n // 288 + 2, 3, dtype=np.int8))
    t = S.trades_for(B, 1)
    g = t["g"]
    assert len(g) > 1000
    tstat = g.mean() / (g.std() / np.sqrt(len(g)))
    assert abs(tstat) < 4, tstat


def test_lookahead_variant_is_caught():
    env = dict(os.environ, STUDY_BUG="1")
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", os.path.join(HERE, "test_study.py"),
                        "-k", "causal or no_edge"], env=env, cwd=HERE, capture_output=True, text=True)
    assert r.returncode != 0
