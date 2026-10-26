"""
MyTradingSys/execution/testnet/probe_account_summary.py

OPERATOR-RUN, READ-ONLY probe. Not called by any other module.

Why this exists: daily_loss_monitor.py computes today's total PnL as
    (equity_now - equity_at_start_of_day) * mark_price_now
using deribit_orders.get_account_summary()'s "equity" field and
get_ticker()'s "mark_price" field. Those field NAMES appear elsewhere in
this repo's code (deribit_read.py, executor.py), but no real captured
Deribit response with actual numbers for them exists in this repo - so
their exact behavior is an unverified assumption, not an evidenced fact.
This script prints ONLY the key names and numeric values Deribit actually
returns on TESTNET, with no secrets, so an operator can check before
trusting daily_loss_monitor.py's live numbers:

  1. Does "equity" move when a position's unrealized PnL moves (i.e. does
     it already net open-position PnL), or does it only change on
     realized fills/settlement?
  2. Is "equity" denominated in BTC (as deribit_read.py's print string
     implies) or in USD?
  3. Does get_position()'s "unrealized_pnl" (if present) roughly match
     equity movement over a short window, as a cross-check?

Run on TESTNET only (deribit_orders.BASE is hardcoded to testnet - see
that module's header). Prints nothing but key names and numbers; never
prints the access token or the secret file contents.

Usage:
    cd MyTradingSys/execution/testnet
    python3 probe_account_summary.py [--currency BTC] [--instrument BTC-PERPETUAL]
"""
import sys
sys.dont_write_bytecode = True

import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import deribit_orders as do  # noqa: E402


def _print_dict(label, d):
    print(f"--- {label} ---")
    if not isinstance(d, dict):
        print(repr(d))
        return
    for k, v in d.items():
        if isinstance(v, (int, float, str, bool)) or v is None:
            print(f"  {k} = {v!r}")
        else:
            print(f"  {k} = <{type(v).__name__}, not printed>")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--currency", default="BTC")
    parser.add_argument("--instrument", default="BTC-PERPETUAL")
    args = parser.parse_args(argv)

    token = do.authenticate()

    summary = do.get_account_summary(token, currency=args.currency)
    _print_dict("get_account_summary", summary)

    position = do.get_position(token, instrument_name=args.instrument)
    _print_dict("get_position", position)

    ticker = do.get_ticker(instrument_name=args.instrument)
    _print_dict("get_ticker", ticker)

    print()
    print("Operator checklist:")
    print("  1. Note 'equity' now. Place/hold a small position, wait, re-run.")
    print("     Does 'equity' change with unrealized PnL, or only on close?")
    print("  2. Compare 'equity' magnitude to your known testnet BTC balance")
    print("     (BTC-denominated) vs. equity * mark_price (a USD-scale number).")
    print("  3. If get_position returned 'unrealized_pnl', does its short-window")
    print("     delta roughly match (equity_now - equity_before) * mark_price?")
    print("  Record the answer in research/_archive/loose_2026-10/deribit_api_research.md so the next")
    print("  reader does not have to re-run this probe.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
