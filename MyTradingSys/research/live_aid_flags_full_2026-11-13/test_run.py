"""Tests of grouping, outcome, bootstrap, Benjamini-Hochberg and verdict logic on tiny hand-made inputs (numbers worked by hand)."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run


def test_groups_match_learner_rule():
    # REJECTED at Day open -> idea, idea REJECTED, idea fade @ Day open
    assert run.groups_of({"state": "REJECTED", "at": "Day open"}) == ["idea", "idea REJECTED", "idea fade @ Day open"]
    assert run.groups_of({"state": "FAILED BREAK", "at": "Asia low"}) == ["idea", "idea FAILED BREAK", "idea fade @ Asia low"]
    # ACCEPTED is never a fade group
    assert run.groups_of({"state": "ACCEPTED", "at": "Day open"}) == ["idea", "idea ACCEPTED"]
    assert len(run.GROUPS) == 15 and len(run.CELLS) == 30


def test_groups_agree_with_live_aid_learn_score():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "scripts", "dev"))
    import live_aid_learn as L
    evs = [{"kind": "idea", "state": s, "at": a, "r1h": 1} for s, a in
           (("REJECTED", "Day open"), ("ACCEPTED", "Day open"), ("FAILED BREAK", "Europe high"))]
    learner = {r["name"] for r in L.score(evs)}
    mine = {g for e in evs for g in run.groups_of(e)}
    assert learner == mine


def test_outcome_side_and_fee():
    g, n = run.outcome("SHORT", 100.0, 99.0, 4.0)       # +100 bps gross, 96 net
    assert abs(g - 100.0) < 1e-9 and abs(n - 96.0) < 1e-9
    g, n = run.outcome("LONG", 100.0, 99.9, 4.0)        # -10 gross, -14 net
    assert abs(g + 10.0) < 1e-9 and abs(n + 14.0) < 1e-9
    g, n = run.outcome("LONG", 100.0, 100.02, 4.0)      # gross 2 bps: a hit that loses money
    assert g > 0 and n < 0


def test_bootstrap_p_and_ci():
    m, lo, hi, p = run.day_block_bootstrap([1, 1, 2, 2, 3, 3], [5.0] * 6, draws=200)
    assert m == 5.0 and lo == 5.0 and hi == 5.0 and abs(p - 1 / 201) < 1e-12      # always positive: p is the floor
    m, lo, hi, p = run.day_block_bootstrap(list(range(40)), [1.0, -1.0] * 20, draws=500)
    assert lo < 0 < hi and p > 0.1                                                  # symmetric noise
    m, lo, hi, p = run.day_block_bootstrap([1, 2, 3], [-2.0, -2.0, -2.0], draws=100)
    assert p == 1.0                                                                  # always negative


def test_benjamini_hochberg_worked_example():
    # m = 5, q = 0.10: thresholds 0.02, 0.04, 0.06, 0.08, 0.10 ; sorted p .01 .03 .05 .09 .50 -> .01<=.02, .03<=.04, .05<=.06, .09>.08, .50>.10 -> k = 3
    ps = [0.50, 0.01, 0.09, 0.03, 0.05]
    assert run.benjamini_hochberg(ps) == [False, True, False, True, True]
    # step-up: a later passing rank rescues an earlier miss (p .03 > .02 at rank 1 would fail alone but rank 2 (.04 <= .04) passes both)
    assert run.benjamini_hochberg([0.03, 0.04, 0.9, 0.9, 0.9]) == [True, True, False, False, False]
    # nothing small -> nothing survives
    assert not any(run.benjamini_hochberg([0.2, 0.3, 0.4]))


def test_verdict_gates():
    ok = {"up": 50, "down": 50, "range": 0}
    assert run.verdict_for(99, 1.0, True, True, ok) == "UNDERPOWERED"
    assert run.verdict_for(500, 1.0, True, False, ok) == "FAIL"           # fails the correction
    assert run.verdict_for(500, 1.0, False, True, ok) == "FAIL"           # fails placebo
    assert run.verdict_for(500, -0.1, True, True, ok) == "FAIL"           # CI includes zero
    assert run.verdict_for(500, 1.0, True, True, {"up": 500, "down": 0, "range": 0}) == "PASS-ONE-REGIME"
    assert run.verdict_for(500, 1.0, True, True, ok) == "PASS"


def test_judge_small_n_enters_with_p_one():
    rows = [{"n": 50, "p": 0.0001, "lo": 5, "beats": True, "regns": {"up": 50, "down": 0, "range": 0}},
            {"n": 500, "p": 0.001, "lo": 3, "beats": True, "regns": {"up": 300, "down": 100, "range": 100}}]
    out = run.judge(rows)
    assert out[0]["verdict"] == "UNDERPOWERED" and out[0]["bh"] is False
    assert out[1]["verdict"] == "PASS"


def test_regime_no_lookahead():
    D0 = 1_700_000_000_000 // run.DAY * run.DAY
    closes = {D0 + i * run.DAY: 100.0 for i in range(25)}
    closes[D0 + 24 * run.DAY] = 150.0
    assert run.regime_by_day(closes)[D0 + 24 * run.DAY] == "range"
    closes[D0 + 23 * run.DAY] = 150.0
    assert run.regime_by_day(closes)[D0 + 24 * run.DAY] == "up"
