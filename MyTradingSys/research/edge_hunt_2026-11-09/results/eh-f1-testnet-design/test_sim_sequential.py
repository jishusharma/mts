"""Tests for the eh-f1 sequential rule: hand-built R streams, the Ville bound, the shapes, the comparators."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim_sequential as s  # noqa: E402


def test_shape_hit_prob_matches_mean():
    rng = np.random.default_rng(1)
    for shape in (s.SHAPE_A, s.SHAPE_B):
        for m in (-0.2, 0.0, 0.3):
            x = s.gen_stream(rng, shape, m, 2000, 400)
            assert abs(x.mean() - m) < 0.01
            assert x.min() >= shape.lower - 1e-12 and x.max() <= shape.upper + 1e-12


def test_shape_a_matches_the_brief_30_40_pct_at_2_5r():
    assert 0.30 <= s.SHAPE_A.hit_prob(0.0) <= 0.32
    assert 0.40 <= s.SHAPE_A.hit_prob(0.3) <= 0.42
    assert 0.45 <= s.SHAPE_B.hit_prob(-0.087) <= 0.50


def test_e_promote_hand_values():
    # one trade of +1 R vs mu0 = 0, a = -3: lambda_max = 1/3; grid fractions -> factors 1 + f/3
    e = s.e_promote(np.array([[1.0]]))
    expected = np.mean([1 + f / 3 for f in s.LAMBDA_FRACS])
    assert abs(e[0, 0] - expected) < 1e-12
    # a loss of -1 R lowers the wealth below 1
    assert s.e_promote(np.array([[-1.0]]))[0, 0] < 1.0


def test_e_kill_hand_values():
    b = s.SHAPE_A.upper
    e = s.e_kill(np.array([[-1.0]]), delta=0.25, b=b)
    lam = 1.0 / (b - 0.25)
    expected = np.mean([1 - f * lam * (-1.0 - 0.25) for f in s.LAMBDA_FRACS])
    assert abs(e[0, 0] - expected) < 1e-12
    assert s.e_kill(np.array([[2.0]]), delta=0.25, b=b)[0, 0] < 1.0


def test_bounds_are_enforced():
    with pytest.raises(ValueError):
        s.e_promote(np.array([[-3.5]]))
    with pytest.raises(ValueError):
        s.e_kill(np.array([[3.0]]), b=s.SHAPE_A.upper)


def test_ville_bound_false_promote_under_null():
    # under mean exactly 0 (the null boundary) the anytime false-promote rate stays <= alpha
    rng = np.random.default_rng(7)
    cfg = s.RuleCfg(alpha=0.05, n_max=150)
    x = s.gen_stream(rng, s.SHAPE_A, 0.0, 6000, 150)
    code, _ = s.decide(x, cfg)
    assert np.mean(code == 1) <= 0.05 + 0.01


def test_false_kill_under_delta():
    rng = np.random.default_rng(8)
    cfg = s.RuleCfg(n_max=150)
    x = s.gen_stream(rng, s.SHAPE_A, s.DELTA_KILL, 6000, 150)
    code, _ = s.decide(x, cfg)
    assert np.mean(code == -1) <= s.BETA_KILL + 0.01


def test_decide_respects_n_min_and_codes():
    # 150 straight 2.5 R winners: promote, never before n_min_promote
    x = np.full((1, 150), s.SHAPE_A.upper)
    code, n = s.decide(x, s.RuleCfg())
    assert code[0] == 1 and n[0] == s.N_MIN_PROMOTE
    # 150 straight losers: kill, never before n_min_kill
    x = np.full((1, 150), s.SHAPE_A.lower)
    code, n = s.decide(x, s.RuleCfg())
    assert code[0] == -1 and n[0] >= s.N_MIN_KILL
    # all time-stop zeros: mean 0 < delta, so the KILL process (not retire) ends it
    x = np.zeros((1, 150))
    code, n = s.decide(x, s.RuleCfg())
    assert code[0] == -1
    # a stream with mean +0.117 R (between 0 and delta): neither process fires -> retire at n_max
    x = np.tile(np.array([s.SHAPE_A.upper, s.SHAPE_A.lower, s.SHAPE_A.lower]), 50)[None, :]
    code, n = s.decide(x, s.RuleCfg())
    assert code[0] == 0 and n[0] == 150


def test_krown_rules_hand_built():
    # FAIL-B: 12 straight losers kills at trade 12
    x = np.full((1, 40), -1.0)
    assert s.krown_abc(x)[0] == 12
    # FAIL-A: alternating +2 / -1 never reaches a 12 R drawdown nor 12 losers; FAIL-C needs mean + 1.28 SE < 0
    x = np.tile(np.array([2.0, -1.0]), 20)[None, :]
    assert s.krown_abc(x)[0] == 41
    # FAIL-C: alternating -0.3 / +0.1 (mean -0.1, no streak, no 12 R drawdown) kills at n = 30
    x = np.tile(np.array([-0.3, 0.1]), 20)[None, :]
    assert s.krown_abc(x)[0] == 30


def test_malkan30_rule():
    x = np.concatenate([np.full((1, 30), -0.1), np.full((1, 10), 5.0)], axis=1)
    assert s.malkan30(x)[0] == 1
    assert s.malkan30(np.full((1, 30), 0.1))[0] == 0


def test_cluster_mean_keeps_the_bound_with_correlated_pairs():
    rng = np.random.default_rng(9)
    cfg = s.RuleCfg(alpha=0.05, n_max=150)
    x = s.gen_pairs(rng, s.SHAPE_A, 0.0, 6000, 150, rho=0.9)
    clus = 0.5 * (x[:, 0::2] + x[:, 1::2])
    code, _ = s.decide(clus, cfg)
    assert np.mean(code == 1) <= 0.05 + 0.01


def test_main_quick_runs():
    assert s.main(["--quick"]) == 0
