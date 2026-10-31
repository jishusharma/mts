"""Proposed regression tests for fee and sim input edge cases.

Expected contracts derived independently from MyTradingSys/backtest/layers/FORMULAS.md
section 13 and fee regimes in MyTradingSys/backtest/fees.py. These should fail on
current code. They are report artifacts; not run during this audit.
"""
import math
import pytest

from MyTradingSys.backtest import fees, sim


def _rows(entry=100.0, prices=(102.0,)):
    rows = [dict(t=0, ts="in", verdict="SETUP_FORMING", stop=99, target=102,
                 price=entry, dir="long", setup="s")]
    for i, price in enumerate(prices, 1):
        rows.append(dict(t=60*i, ts=str(i), verdict="OTHER", stop=None,
                         target=None, price=price, dir="long", setup="s"))
    return rows


def test_fees_dict_rejects_negative_and_nonfinite_rates():
    with pytest.raises(ValueError):
        fees.fees_dict(-1, 0, 0, 0)
    with pytest.raises(ValueError):
        fees.fees_dict(0, float("nan"), 0, 0)


def test_run_rejects_nan_entry():
    with pytest.raises(ValueError):
        sim.run(_rows(entry=float("nan")), "A", "observed", .0005, 0)


def test_run_rejects_nan_path_even_if_later_target_is_seen():
    with pytest.raises(ValueError):
        sim.run(_rows(prices=(float("nan"), 102)), "A", "observed", .0005, 0)


def test_run_rejects_negative_fee_rates():
    with pytest.raises(ValueError):
        sim.run(_rows(), "A", "observed", -.001, 0)


def test_valid_profile_b_target_fee_arithmetic():
    trade, = sim.run(_rows(), "A", "observed", .0005, 0)
    # Formula: entry taker + maker target = .0005 * entry / risk = .05 R.
    assert trade["gross"] == 2.0
    assert math.isclose(trade["fee_R"], .05, abs_tol=1e-12)
    assert math.isclose(trade["net"], 1.95, abs_tol=1e-12)


def test_documented_funding_example_requires_supported_cost_path():
    # FORMULAS.md 13: long 100->101, funding .0001 + .0003, fee .001, slip .0002.
    expected_net = .01 - .001 - .0002 - .0004
    assert math.isclose(expected_net, .0084, abs_tol=1e-12)
    # Current run() has no funding/slippage arguments or corresponding output field.
    with pytest.raises(TypeError):
        sim.run(_rows(), "A", "observed", .0005, 0, funding_records=[])
