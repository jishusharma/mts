"""Unit tests for fee_sweep.sweep(): the fee-multiplier table over FILLED trades only.

Planted numbers (hand-computed, not from desk.py): gross [1, -1, 0.6], fee 0.2 on each filled trade
-> mean gross 0.2, net at fee x0 0.2, x0.5 0.1, x1 0.0, x2 -0.2, break-even multiple 1.0.
"""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fee_sweep  # noqa: E402


def test_planted_numbers_mean_and_fee_multiples():
    out = fee_sweep.sweep([1, -1, 0.6], [0.2, 0.2, 0.2], [True, True, True])
    assert out['n'] == 3
    assert out['mean_gross'] == pytest.approx(0.2)
    assert out['mean_fee'] == pytest.approx(0.2)
    assert out['net_x0'] == pytest.approx(0.2)
    assert out['net_x0_5'] == pytest.approx(0.1)
    assert out['net_x1'] == pytest.approx(0.0)
    assert out['net_x2'] == pytest.approx(-0.2)
    assert out['break_even'] == pytest.approx(1.0)


def test_gross_at_or_below_zero_gives_break_even_zero():
    out = fee_sweep.sweep([-1, -1], [0.2, 0.2], [True, True])
    assert out['mean_gross'] == pytest.approx(-1.0)
    assert out['break_even'] == 0.0

    out0 = fee_sweep.sweep([0.0, 0.0], [0.2, 0.2], [True, True])
    assert out0['mean_gross'] == pytest.approx(0.0)
    assert out0['break_even'] == 0.0


def test_zero_fees_give_none():
    out = fee_sweep.sweep([1, -1, 0.6], [0.0, 0.0, 0.0], [True, True, True])
    assert out['mean_fee'] == pytest.approx(0.0)
    assert out['break_even'] is None


def test_never_filled_trades_excluded():
    """Two filled (gross 1, -1, fee 0.2 each), two never-filled (would skew the mean if counted)."""
    out = fee_sweep.sweep([1, -1, 99, 99], [0.2, 0.2, 0.0, 0.0], [True, True, False, False])
    assert out['n'] == 2
    assert out['mean_gross'] == pytest.approx(0.0)
    assert out['mean_fee'] == pytest.approx(0.2)
