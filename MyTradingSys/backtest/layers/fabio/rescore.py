"""rescore.py - fee-net R for the fee/stop re-score (card fee-stop-rescore-fabio-habib-1106).

Costs come only from MyTradingSys/backtest/fees.py (Deribit: taker 5 bp, maker 0). Net R = gross R - fee x entry / risk,
summed over the two legs (FORMULAS.md). Pure functions, no I/O.
"""
from MyTradingSys.backtest.fees import DERIBIT_MAKER, DERIBIT_TAKER

FEE = {"taker": DERIBIT_TAKER, "maker": DERIBIT_MAKER}


def risk_of(entry, stop):
    return abs(entry - stop)


def gross_r(side, entry, stop, exit_px):
    """side +1 long / -1 short; R multiple before fees."""
    return side * (exit_px - entry) / risk_of(entry, stop)


def fee_r(entry, stop, entry_kind="taker", exit_kind="taker"):
    """Fee drag in R: (fee_in + fee_out) x entry / risk."""
    return (FEE[entry_kind] + FEE[exit_kind]) * entry / risk_of(entry, stop)


def net_r(side, entry, stop, exit_px, entry_kind="taker", exit_kind="taker"):
    g = gross_r(side, entry, stop, exit_px)
    f = fee_r(entry, stop, entry_kind, exit_kind)
    return g, f, g - f


def exit_kind_for(outcome):
    """A resting target is a maker fill; stops and time exits are taker."""
    return "maker" if outcome == "target" else "taker"
