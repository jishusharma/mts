"""Tests for netdelta_fit.py (card identify-the-coinglass-net-delta-panel-u).

Card requirement:
test_step_formula: fixture bar close<open with OI up gives a negative step,
close>open with OI down gives a negative step, flat bar gives 0; fails before netdelta_fit.py exists.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from netdelta_fit import step_formula, candidate_a_step, run_fit  # noqa: E402


def test_step_formula():
    # 1. close < open with OI up gives a negative step
    # open=100.0, close=90.0, oi_open=1000.0, oi_close=1100.0 (OI up: +100)
    step1 = step_formula(open_price=100.0, close_price=90.0, oi_open=1000.0, oi_close=1100.0)
    assert step1 < 0, f"Expected negative step for close<open with OI up, got {step1}"

    # 2. close > open with OI down gives a negative step
    # open=100.0, close=110.0, oi_open=1100.0, oi_close=1000.0 (OI down: -100)
    step2 = step_formula(open_price=100.0, close_price=110.0, oi_open=1100.0, oi_close=1000.0)
    assert step2 < 0, f"Expected negative step for close>open with OI down, got {step2}"

    # 3. flat bar gives 0
    # open=100.0, close=100.0, oi_open=1000.0, oi_close=1100.0
    step3 = step_formula(open_price=100.0, close_price=100.0, oi_open=1000.0, oi_close=1100.0)
    assert step3 == 0, f"Expected 0 for flat bar, got {step3}"


def test_candidate_a_abs():
    # close < open with OI up: negative
    assert candidate_a_step(open_price=100.0, close_price=90.0, d_oi=100.0, use_abs=True) == -100.0
    # close < open with OI down: negative
    assert candidate_a_step(open_price=100.0, close_price=90.0, d_oi=-100.0, use_abs=True) == -100.0
    # close > open with OI up: positive
    assert candidate_a_step(open_price=100.0, close_price=110.0, d_oi=100.0, use_abs=True) == 100.0
    # flat bar gives 0
    assert candidate_a_step(open_price=100.0, close_price=100.0, d_oi=100.0, use_abs=True) == 0.0


def test_fit_execution_and_verdict():
    res = run_fit()
    assert res["n_rows"] == 7
    assert res["verdict"] == "UNIDENTIFIED (n = 7)"
    assert "cand_a" in res["summary"]
    assert "cand_b" in res["summary"]
