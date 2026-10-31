"""Fail-first tests for run_f3.py. Expected values are hand-computed or planted in synthetic data, never taken from the module."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_f3 as f3  # noqa: E402


def noise(n, sigma, seed):
    return np.random.default_rng(seed).standard_normal(n) * sigma


def test_forward_log_hand_computed():
    # r = [nan, .1, .2, .3, .4]; H = 2: fwd[1] = .2 + .3 = .5, fwd[2] = .3 + .4 = .7, fwd[0] contains no nan after index 0 -> .1 + .2 = .3
    r = np.array([np.nan, 0.1, 0.2, 0.3, 0.4])
    fwd = f3.forward_log(r, 2)
    assert abs(fwd[0] - 0.3) < 1e-12 and abs(fwd[1] - 0.5) < 1e-12 and abs(fwd[2] - 0.7) < 1e-12
    assert np.isnan(fwd[3]) and np.isnan(fwd[4])


def test_forward_log_missing_hour_invalidates():
    r = np.array([0.0, 0.1, np.nan, 0.3, 0.4, 0.5])
    fwd = f3.forward_log(r, 3)
    assert np.isnan(fwd[0]) and np.isnan(fwd[1])      # both outcomes contain the NaN hour
    assert abs(fwd[2] - 1.2) < 1e-12                  # r[3..5]


def test_z_windows_zero_mean_unit_std_and_invalid():
    r = np.concatenate([[np.nan], noise(100, 0.01, 1)])
    Z, valid = f3.z_windows(r)
    e = 80
    assert valid[e] and abs(float(Z[e].mean())) < 1e-5 and abs(float(Z[e].std()) - 1.0) < 1e-5
    assert not valid[0] and not valid[f3.L - 1]       # window of 48 starting at the NaN


def test_library_never_overlaps_query_outcome_shift_test():
    r = noise(3000, 0.004, 2)
    Z, valid = f3.z_windows(r)
    fwd = f3.forward_log(r)
    qe = np.arange(700, 2900, 24)
    nb = f3.neighbours(Z, valid, np.isfinite(fwd), Z, qe, np.zeros(len(r), dtype=np.int64), False)
    assert len(nb) == len(qe)
    for e, ix in zip(qe, nb):
        assert len(ix) == f3.K
        assert ix.max() + f3.H <= e                   # neighbour outcome (e', e'+H] ends at or before the query end: no overlap with (e, e+H]
        d = np.abs(ix[:, None] - ix[None, :]) + np.eye(len(ix), dtype=int) * 10 ** 6
        assert d.min() >= f3.SPACING


def test_forecast_unchanged_when_future_is_replaced():
    # Replacing everything after the query bar (its outcome and beyond) must not move the forecast.
    r = noise(2000, 0.004, 3)
    e = 1500
    r2 = np.concatenate([r[: e + 1], noise(len(r) - e - 1, 0.02, 99) + 0.01])
    out = []
    for rr in (r, r2):
        Z, valid = f3.z_windows(rr)
        fwd = f3.forward_log(rr)
        nb = f3.neighbours(Z, valid, np.isfinite(fwd), Z, np.array([e]), np.zeros(len(rr), dtype=np.int64), False)
        ans, pos = f3.decide(nb, fwd)
        out.append((nb[0].tolist(), int(pos[0])))
    assert out[0] == out[1]


def test_phase_filter_only_same_phase_neighbours():
    r = noise(6000, 0.004, 4)
    ph = (np.arange(6000) // 2000).astype(np.int64)   # phases switch at 2000, 4000
    Z, valid = f3.z_windows(r)
    fwd = f3.forward_log(r)
    e = 5500
    nb = f3.neighbours(Z, valid, np.isfinite(fwd), Z, np.array([e]), ph, True)[0]
    assert len(nb) == f3.K and (ph[nb] == ph[e]).all()


def test_planted_repeating_pattern_is_found():
    rng = np.random.default_rng(5)
    pat = np.tile(np.array([0.004, -0.002, 0.003, -0.005, 0.001, 0.006]), 8)    # 48 returns, fixed shape
    segs, ends = [], []
    pos_now = 0
    for _ in range(80):
        gap = noise(int(rng.integers(40, 70)), 0.002, int(rng.integers(1 << 30)))
        after = noise(f3.H, 0.001, int(rng.integers(1 << 30))) + 0.002              # +4.8 % drift after the pattern
        segs += [gap, pat, after]
        pos_now += len(gap) + len(pat)
        ends.append(pos_now - 1)
        pos_now += len(after)
    r = np.concatenate(segs)
    Z, valid = f3.z_windows(r)
    fwd = f3.forward_log(r)
    qe = np.array(ends[30:])
    nb = f3.neighbours(Z, valid, np.isfinite(fwd), Z, qe, np.zeros(len(r), dtype=np.int64), False)
    ans, pos = f3.decide(nb, fwd)
    assert ans.all()
    assert (pos == 1).mean() >= 0.9
    taken, net, hit = f3.trade_net(pos, qe, np.nan_to_num(fwd))
    assert hit[taken].mean() >= 0.9 and np.nanmean(net[taken]) > 2.0


def test_random_walk_has_no_edge():
    r = noise(14000, 0.004, 6)
    r[0] = np.nan
    Z, valid, fwd, qe = f3.make_queries(r, warm=500)
    nb = f3.neighbours(Z, valid, np.isfinite(fwd), Z, qe, np.zeros(len(r), dtype=np.int64), False)
    ans, pos = f3.decide(nb, fwd)
    taken, net, hit = f3.trade_net(pos, qe, fwd)
    n = int(taken.sum())
    assert n >= 60
    gross = net[taken] + f3.RT_PCT
    se = gross.std() / np.sqrt(n)
    assert abs(gross.mean()) < 4 * se                  # no gross edge
    assert abs(hit[taken].mean() - 0.5) < 0.12
    assert net[taken].mean() < 0                       # the round trip makes it a loss


def test_block_permute_is_a_permutation_and_holm():
    x = np.arange(1000, dtype=float)
    y = f3.block_permute(x, 168, np.random.default_rng(7))
    assert sorted(y.tolist()) == x.tolist() and not (y == x).all()
    # Holm by hand: p = [0.01, 0.04, 0.03, 0.5] -> sorted 0.01*4=0.04, 0.03*3=0.09, 0.04*2=0.08->max 0.09, 0.5*1
    adj = f3.holm([0.01, 0.04, 0.03, 0.5])
    assert np.allclose(adj, [0.04, 0.09, 0.09, 0.5])


def test_surrogate_vol_uses_only_the_past():
    r = noise(2000, 0.004, 8)
    r2 = np.concatenate([r[:1000], noise(1000, 0.05, 9)])
    s1 = f3.trailing_std(r, shift=1)
    s2 = f3.trailing_std(r2, shift=1)
    assert np.allclose(s1[:1001], s2[:1001], equal_nan=True)   # bar 1000's vol sees only bars <= 999
