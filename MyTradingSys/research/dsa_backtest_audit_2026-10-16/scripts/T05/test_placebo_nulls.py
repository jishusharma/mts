"""T05 tests: the placebo machinery on a synthetic tape (no market data, no network). Run: python -m pytest <this file>"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import t05_core as C  # noqa: E402

N_BARS = 912 * 1440


def _tape(seed=3):
    rng = np.random.default_rng(seed)
    r = rng.normal(0, 0.0005, N_BARS)
    return 100.0 * np.exp(np.cumsum(r))


def _events(rng, n=120):
    t = np.sort(rng.choice(np.arange(2000, N_BARS - 5000), n, replace=False))
    return t


def test_placebo_sets_are_matched_and_seeded():
    O = _tape()
    raw = C.raw_table(O, h=60, d=1)
    fund = np.zeros(N_BARS)
    valid = np.nonzero(~np.isnan(raw))[0]
    pool = C.Pools(valid)
    ev = _events(np.random.default_rng(1))
    side = np.where(np.arange(len(ev)) % 2 == 0, -1, 1)
    cd = 60
    idx = C.draw_placebo(np.random.default_rng(20261016), ev, side, pool, n_sets=1000, cd=cd)
    assert idx.idx.shape == (1000, len(ev))                       # 1,000 placebo sets, same size as the arm
    # matched on 15-minute slot and weekday
    assert (C.key_of(idx.idx) == C.key_of(ev)[None, :]).all()
    # cooldown: no two same-side events of one set within cd minutes (after the redraw rounds)
    assert idx.conflict_share == 0.0
    for r in range(0, 1000, 97):
        for s in (-1, 1):
            tt = np.sort(idx.idx[r][side == s])
            assert (np.diff(tt) > cd).all()
    # same seed -> identical sets and identical empirical p
    mean_real, _ = C.set_stats(raw, fund, ev[None, :], side, d=1)
    a = C.draw_placebo(np.random.default_rng(7), ev, side, pool, n_sets=1000, cd=cd)
    b = C.draw_placebo(np.random.default_rng(7), ev, side, pool, n_sets=1000, cd=cd)
    c = C.draw_placebo(np.random.default_rng(8), ev, side, pool, n_sets=1000, cd=cd)
    assert (a.idx == b.idx).all() and not (a.idx == c.idx).all()
    ma, _ = C.set_stats(raw, fund, a.idx, side, d=1)
    mb, _ = C.set_stats(raw, fund, b.idx, side, d=1)
    assert C.empirical_p(mean_real[0], ma) == C.empirical_p(mean_real[0], mb)
    assert 0.0 < C.empirical_p(mean_real[0], ma) <= 1.0


def test_set_stats_matches_study_cluster_formula():
    O = _tape(5)
    raw = C.raw_table(O, h=60, d=1)
    fund = np.zeros(N_BARS)
    ev = _events(np.random.default_rng(2), 80)
    side = np.full(len(ev), -1)
    m, se = C.set_stats(raw, fund, ev[None, :], side, d=1)
    g = side * raw[ev]
    day = (ev + 2) // 1440
    s = np.bincount(np.unique(day, return_inverse=True)[1], weights=g - g.mean())
    assert abs(m[0] - g.mean()) < 1e-12
    assert abs(se[0] - np.sqrt((s ** 2).sum()) / len(g)) < 1e-12


def test_overlap_and_bootstrap():
    e = np.array([0, 30, 200, 1000])
    share, comps = C.overlap(e, h=60)
    assert share == 0.5 and comps == 3                           # first two overlap; others stand alone
    rng = np.random.default_rng(1)
    g = rng.normal(0.1, 1.0, 300)
    ent = np.sort(rng.integers(0, 912 * 1440, 300))
    sd = C.week_bootstrap_sd(g, ent, 2000, np.random.default_rng(3))
    assert 0.03 < sd < 0.2
