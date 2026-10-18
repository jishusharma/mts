"""Unit test for carry basis PnL modeling.
Tests the synthetic 2-day series specified in the card:
  spot +1%, perp +1.2%, funding 0.01% on day 1
  spot -0.5%, perp -0.8%, funding 0.02% on day 2
All expected values computed by hand in the test.
"""
import sys, os
from pathlib import Path
import pytest
import numpy as np

# Ensure research module can be imported
RESEARCH_DIR = Path(__file__).resolve().parents[1] / "research" / "carry_basis_2026-10-18"
if str(RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(RESEARCH_DIR))

try:
    from carry_basis import compute_carry_pnl_daily, simulate_carry
except ImportError:
    compute_carry_pnl_daily = None
    simulate_carry = None


def test_synthetic_2day_basis_pnl_hand_computed():
    """Verify daily basis PnL against exact hand-calculated figures.

    Day 1:
      spot price return: +1.0% = +0.010
      perp price return: +1.2% = +0.012
      short perp price return: -1.2% = -0.012
      net price change (spot - perp): +1.0% - 1.2% = -0.2% = -0.002
      funding received: +0.01% = +0.0001
      gross PnL = -0.002 + 0.0001 = -0.0019 (-0.19%)
      entry fee (2 legs x 0.10%): -0.0020 (-0.20%)
      net PnL (with entry) = -0.0039 (-0.39%)

    Day 2:
      spot price return: -0.5% = -0.005
      perp price return: -0.8% = -0.008
      short perp price return: +0.8% = +0.008
      net price change (spot - perp): -0.5% - (-0.8%) = +0.3% = +0.003
      funding received: +0.02% = +0.0002
      gross PnL = +0.003 + 0.0002 = +0.0032 (+0.32%)
      holding fee (0 trades): 0.0
      net PnL (holding, no exit) = +0.0032 (+0.32%)
      exit fee (2 legs x 0.10% if exiting): -0.0020 (-0.20%)
      net PnL (with exit) = +0.0012 (+0.12%)
    """
    assert compute_carry_pnl_daily is not None, "compute_carry_pnl_daily function must exist"

    # Synthetic series
    spot_ret = np.array([0.010, -0.005])
    perp_ret = np.array([0.012, -0.008])
    funding = np.array([0.0001, 0.0002])

    gross_ret = compute_carry_pnl_daily(spot_ret, perp_ret, funding)

    expected_day1_gross = -0.0019
    expected_day2_gross = 0.0032

    assert np.isclose(gross_ret[0], expected_day1_gross, atol=1e-6)
    assert np.isclose(gross_ret[1], expected_day2_gross, atol=1e-6)

    # Test full simulation with fees
    assert simulate_carry is not None, "simulate_carry function must exist"

    # Always-on no exit (enters day 1 with 2 legs x 0.10%, holds day 2)
    res_always = simulate_carry(spot_ret, perp_ret, funding, fee_per_leg=0.001, mode="always_on")
    assert np.isclose(res_always["net_ret"][0], -0.0039, atol=1e-6)
    assert np.isclose(res_always["net_ret"][1], 0.0032, atol=1e-6)

    # Full round-trip trade (enters day 1 with 2 legs, exits day 2 with 2 legs = 4 legs total)
    res_trade = simulate_carry(spot_ret, perp_ret, funding, fee_per_leg=0.001, mode="round_trip")
    assert np.isclose(res_trade["net_ret"][0], -0.0039, atol=1e-6)
    assert np.isclose(res_trade["net_ret"][1], 0.0012, atol=1e-6)
    # Cumulative return: (1 - 0.0039) * (1 + 0.0012) - 1 = 0.9961 * 1.0012 - 1 = -0.00270468
    assert np.isclose(res_trade["cum_ret"][-1], (1 - 0.0039) * (1 + 0.0012) - 1, atol=1e-6)
