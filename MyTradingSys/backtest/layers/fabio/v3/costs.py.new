"""Fabio v3 costs and shared SIM constants (FABIO_V3_SPEC.md section 5.3, "sim.py wins", B080/B081).

Pure functions, no IO, no globals that change. Provenance labels (spec section 7.1): every value here is P41 SIM
(venue / data / cost / protocol convention), none is a Fabio quote.

Fee values are NOT defined here. They are imported from the repo's single fee source, MyTradingSys/backtest/fees.py
(B081: "no file defines its own fee constant"): FEE_MAKER = fees.DERIBIT_MAKER (0.0), FEE_TAKER = fees.DERIBIT_TAKER
(0.0005), the sim.py values the spec names (spec :169, sim.py:111-112 via fees.py). fabio_of_model.py FEE_* (the
LEGACY_FABIO_* pair) are deliberately not used (spec :169).
Note: fees.py is a third import besides stdlib and orderflow_bars (spec header :6-7). It is a constants-only module
(imports `sys` only); test T50 (nothing from execution / alerts / core / tom / fabio_of_model) does not forbid it.
Side effect of that import: fees.py:25-26 sets sys.dont_write_bytecode = True for the whole process.
"""
import math

from MyTradingSys.backtest.fees import DERIBIT_MAKER as FEE_MAKER  # P41 SIM, spec 5.3, B081 single source (0.0)
from MyTradingSys.backtest.fees import DERIBIT_TAKER as FEE_TAKER  # P41 SIM, spec 5.3, B081 single source (0.0005)

TICK = 0.1       # P41 SIM, spec section 1 (Binance BTCUSDT tick). Deribit tick: VERIFY ON DESKTOP (spec :33).
EPS = 1e-9       # P41 SIM, spec 5.1 fill tolerance "(1e-9 tolerance)"; also used for inclusive price-distance tests.
MIN_MS = 60000   # P41 SIM, 1m bars (spec section 1 contiguity formula).
SLIP_STRESS_BPS = (0.0, 2.0, 5.0)  # P41 SIM, spec 5.3 "Slippage stress 0 / 2 / 5 bps per taker leg" (grid-free stress set).
FUNDING_STRESS_MULT = 2.0          # P41 SIM, spec 5.3 / BP:48-49 "stress 2x".


def fee_rate(kind):
    """Per-side fee fraction for an order kind: 'maker' or 'taker'."""
    if kind == "maker":
        return FEE_MAKER
    if kind == "taker":
        return FEE_TAKER
    raise ValueError("order kind must be 'maker' or 'taker', got %r" % (kind,))


def leg_r(s, q, e, x, entry_kind, exit_kind, r_unit, slip_bps=0.0):
    """One leg in R (spec 5.3). R unit = q1 * D1 (passed as r_unit).

    gross_r = q * s*(x - e) / r_unit
    fee_r   = (fee_in + fee_out) * e * q / r_unit        (fees on the ENTRY notional, sim.py:77-78)
    slip_r  = slip_bps/1e4 * e * q / r_unit per taker leg (entry and/or exit)
    net_r   = gross_r - fee_r - slip_r
    Funding is NOT included (own line, see funding_r).
    """
    if not r_unit > 0:
        raise ValueError("r_unit must be > 0")
    fee_in, fee_out = fee_rate(entry_kind), fee_rate(exit_kind)
    gross = q * s * (x - e) / r_unit
    fee = (fee_in + fee_out) * e * q / r_unit
    n_taker = (1 if entry_kind == "taker" else 0) + (1 if exit_kind == "taker" else 0)
    slip = n_taker * (slip_bps / 1e4) * e * q / r_unit
    return {"gross_r": gross, "fee_r": fee, "slip_r": slip, "net_r": gross - fee - slip}


def funding_r(s, q, e, t_in, t_out, funding, r_unit, mult=1.0):
    """Funding COST in R for one leg (positive = paid), FORMULAS.md section 13 on the entry notional.

    funding = iterable of (calc_time_ms, rate) records; a record counts iff t_in < calc_time <= t_out.
    side_sign s = +1 long pays positive rates, -1 short receives them. mult = 2.0 is the 2x stress (spec 5.3).
    Own line: this is not added to leg_r's net_r; the caller subtracts it (net after funding = net_r - funding_r).
    The funding records are NOT in the 1m order-flow bars; they come from a separate funding-history source (unknown
    in this repo for the live feed).
    """
    if not r_unit > 0:
        raise ValueError("r_unit must be > 0")
    total = math.fsum(rate for (t, rate) in funding if t_in < t <= t_out)
    return s * total * e * q * mult / r_unit
