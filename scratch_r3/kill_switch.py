"""
Kill switch for MyTradingSys - cancel all open orders and flatten all positions.

This module provides a standalone kill switch that can be used to immediately
stop trading activity across an entire account. It's designed to be
independently testable and not import any exchange-specific modules directly
(kill_all/format_kill_report take a duck-typed client - deribit_orders is
only imported below, inside main(), and only when this file is run as a
script - not at import time, so tests can still import this module with
zero exchange dependency).

CLI (FT-2, 2026-09-28): one-command, account-wide kill switch for an
operator to invoke by hand.
    python kill_switch.py --confirm KILL
--confirm KILL must match EXACTLY ("KILL", case-sensitive) or the CLI
refuses and does nothing - no exchange call, no HALT file. On a real
confirm it authenticates via deribit_orders.authenticate() (the same
helper executor.py/daily_loss_monitor.py already use - this file does not
read the secrets file itself), calls kill_all(deribit_orders, token),
prints the report, and - regardless of whether kill_all fully succeeded -
writes execution/HALT (the generic manual-halt file executor.py's
preflight() now checks) so nothing resumes trading until an operator
deletes it after reviewing the account. Exit code is 0 only when
kill_all's own result["ok"] is True.
"""
import sys
sys.dont_write_bytecode = True

import argparse
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

ACCOUNT_RE = re.compile(r"[a-z0-9_]{1,32}")  # same rule as deribit_orders.secret_path_for
HALT_PATH = Path(__file__).resolve().parent / "HALT"


def kill_all(client, token, currency: str = "BTC", instruments: List[str] = None) -> Dict[str, Any]:
    """
    Account-wide kill switch: cancel all open orders and flatten all positions.
    
    Args:
        client: Duck-typed client object with methods:
            - get_positions(token, currency="BTC", kind="future") -> list of dicts
            - get_open_orders(token, instrument_name, type_="all") -> list of dicts
            - cancel(token, order_id) -> dict
            - close_position(token, instrument_name="BTC-PERPETUAL") -> dict
        token: Authenticated access token
        currency: Currency to operate on (default "BTC")
        instruments: Optional explicit list of instruments to process
        
    Returns:
        Dict with keys:
        - cancelled_orders: List of order IDs that were cancelled
        - closed_positions: List of results from close_position calls
        - errors: List of error dicts for failed operations
        - ok: Boolean indicating if all operations succeeded
    """
    cancelled_orders = []
    closed_positions = []
    errors = []
    
    # Phase 1: Discover instruments to process
    if instruments is None:
        # FIX3 H2: a failed discovery read must not abort the kill - fall back
        # to BTC-PERPETUAL (added below) and record the error.
        try:
            positions = client.get_positions(token, currency=currency, kind="future")
            instruments = list(set(pos["instrument_name"] for pos in positions if abs(pos.get("size", 0)) > 0))
        except Exception as e:
            errors.append({"operation": "get_positions(discover)", "error": repr(e)})
            instruments = []
        
        # If no positions found, fall back to default instrument
        if not instruments:
            instruments = ["BTC-PERPETUAL"]
        else:
            # Always include BTC-PERPETUAL if not already present
            if "BTC-PERPETUAL" not in instruments:
                instruments.append("BTC-PERPETUAL")
    else:
        instruments = list(instruments)  # never mutate the caller's list
        # Ensure BTC-PERPETUAL is included if not already there
        if "BTC-PERPETUAL" not in instruments:
            instruments.append("BTC-PERPETUAL")
    
    # PREMAINNET1 B1: close FIRST, cancel the protective (reduce-only) stop LAST and only once the
    # position is confirmed flat. If the close fails the stop stays in place and we say so loudly.
    def _sizes():
        return {p["instrument_name"]: p.get("size", 0)
                for p in client.get_positions(token, currency=currency, kind="future")}

    def _close_open_positions():
        sizes = _sizes()
        for instrument_name, size in sizes.items():
            if abs(size) > 0:
                try:
                    result = client.close_position(token, instrument_name=instrument_name)
                    closed_positions.append({"instrument_name": instrument_name, "result": result})
                except Exception as e:
                    errors.append({"instrument_name": instrument_name, "error": repr(e)})

    # Phase 2: flatten all positions
    try:
        _close_open_positions()
    except Exception as e:
        errors.append({"operation": "get_positions", "error": repr(e)})

    # Phase 3: cancel non-protective orders (entries etc.), remember reduce-only ones
    protective = []
    for instrument in instruments:
        try:
            orders = client.get_open_orders(token, instrument_name=instrument, type_="all")
        except Exception as e:
            errors.append({"instrument": instrument, "error": repr(e)})
            continue
        for order in orders:
            order_id = order["order_id"]
            if order.get("reduce_only"):
                protective.append((instrument, order_id))
                continue
            try:
                client.cancel(token, order_id)
                cancelled_orders.append(order_id)
            except Exception as e:
                errors.append({"order_id": order_id, "error": repr(e)})

    # Phase 4: re-read the position (retry the close once if something filled meanwhile); only a
    # CONFIRMED flat account releases the protective stops.
    flat = False
    try:
        sizes = _sizes()
        if any(abs(v) > 0 for v in sizes.values()):
            _close_open_positions()
            sizes = _sizes()
        flat = not any(abs(v) > 0 for v in sizes.values())
    except Exception as e:
        errors.append({"operation": "get_positions(verify flat)", "error": repr(e)})

    kept = []
    if flat:
        for instrument, order_id in protective:
            try:
                client.cancel(token, order_id)
                cancelled_orders.append(order_id)
            except Exception as e:
                errors.append({"order_id": order_id, "error": repr(e)})
    else:
        kept = [oid for _, oid in protective]
        errors.append({"operation": "position_not_confirmed_flat",
                       "error": "POSITION NOT CONFIRMED FLAT - protective stop(s) LEFT IN PLACE: "
                                f"{kept} - CHECK THE EXCHANGE UI NOW"})

    return {
        "cancelled_orders": cancelled_orders,
        "closed_positions": closed_positions,
        "errors": errors,
        "protective_orders_kept": kept,
        "ok": len(errors) == 0
    }


def format_kill_report(result: dict) -> str:
    """
    Format a human-readable summary of kill switch execution.
    
    Returns a multi-line string containing the kill switch report.
    """
    lines = [
        "KILL SWITCH REPORT",
        f"Cancelled orders: {len(result['cancelled_orders'])}",
        f"Closed positions: {len(result['closed_positions'])}",
        f"Errors encountered: {len(result['errors'])}"
    ]
    
    if result.get("protective_orders_kept"):
        lines.append(f"!!! POSITION NOT FLAT - protective stop(s) kept: {result['protective_orders_kept']} !!!")
    if result["errors"]:
        lines.append("ERRORS DURING KILL")
        lines.extend(f"  {e}" for e in result["errors"])

    return "\n".join(lines)


def main(argv=None, halt_path: Path = HALT_PATH) -> int:
    parser = argparse.ArgumentParser(
        description="One-command, account-wide kill switch for MTS (TESTNET). Cancels every open "
                    "order and flattens every position, then writes a HALT file so nothing new "
                    "trades until an operator deletes it.")
    parser.add_argument("--confirm", default=None,
                        help="Must be exactly 'KILL' (case-sensitive) or the CLI refuses and does nothing.")
    parser.add_argument("--currency", default="BTC")
    parser.add_argument("--mainnet", action="store_true", help="MAINNET (type the word kill at the prompt)")
    parser.add_argument("--account", default=None,
                        help="named TESTNET account label (sets MTS_ACCOUNT for this run only); refused with --mainnet")
    args = parser.parse_args(argv)

    # Mainnet: the interactive `kill` prompt (select_environment kill_only) is the confirmation; --confirm is optional
    # there but must still be exactly KILL if given. Testnet: --confirm KILL is required, unchanged.
    if args.confirm != "KILL" and not (args.mainnet and args.confirm is None):
        print("REFUSED: --confirm KILL required (exact match, case-sensitive) - nothing was done")
        return 1
    if args.account is not None:
        if args.mainnet:
            print("REFUSED: --account is testnet-only - nothing was done")
            return 2
        if not ACCOUNT_RE.fullmatch(args.account):
            print(f"REFUSED: bad account label {args.account!r} - nothing was done")
            return 2

    # FIX3 H2: HALT FIRST - the kill switch is used exactly when the exchange
    # or network misbehaves, so nothing below may prevent the halt.
    halt_path.write_text("kill switch invoked from CLI - operator review required before resuming\n",
                         encoding="utf-8")
    print(f"HALT file written: {halt_path} - delete it once you have reviewed the account before resuming trading")

    saved_acct = os.environ.get("MTS_ACCOUNT")
    try:
        if args.mainnet and saved_acct:
            # PREMAINNET1 B2: a stale MTS_ACCOUNT must never stop the mainnet kill (select_environment
            # refuses named accounts on mainnet). Ignore it, loudly.
            print(f"WARNING: MTS_ACCOUNT={saved_acct!r} is set in this shell - IGNORED for the mainnet kill switch")
            os.environ.pop("MTS_ACCOUNT", None)
        elif args.account is not None:
            os.environ["MTS_ACCOUNT"] = args.account
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import deribit_orders  # noqa: E402 (deferred: real exchange import only at runtime, not at test-collection time)
        if args.mainnet:  # default path untouched (testnet)
            deribit_orders.select_environment(True, kill_only=True)  # typed word: kill
        token = deribit_orders.authenticate()
        result = kill_all(deribit_orders, token, currency=args.currency)
    except Exception as e:
        print(f"KILL SWITCH FAILED ({e!r}) - HALT is in place - CHECK THE EXCHANGE UI NOW")
        return 1
    finally:
        if saved_acct is None:
            os.environ.pop("MTS_ACCOUNT", None)
        else:
            os.environ["MTS_ACCOUNT"] = saved_acct
    print(format_kill_report(result))

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
