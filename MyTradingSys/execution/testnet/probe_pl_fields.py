"""
MyTradingSys/execution/testnet/probe_pl_fields.py

OPERATOR-RUN probe to identify which Deribit account-summary fields measure
trading P/L (including fees) and which fields reset at settlement time.

Precondition: position=0 on BTC-PERPETUAL, no open orders, no HALT files.
Process:
  1. Snapshot account_summary (extended=true)
  2. Market buy 10 USD of BTC-PERPETUAL (label "pl_probe_in")
  3. Wait 2s, snapshot
  4. Market sell 10 reduce_only (label "pl_probe_out")
  5. Wait 2s, snapshot
  6. Print table of every numeric field with "pl", "pnl", "equity", "balance", "fee", "session" keywords
  7. Assert position=0 and no open orders (close/cancel if not)

Run on TESTNET only. Prints nothing but key names and numbers.

Usage:
    cd MyTradingSys/execution/testnet
    python3 probe_pl_fields.py
"""
import sys
sys.dont_write_bytecode = True

import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import deribit_orders as do  # noqa: E402


def _check_preconditions(token):
    """Abort if position != 0, open orders exist, or HALT files exist."""
    halt_dir = Path(__file__).resolve().parent.parent
    if (halt_dir / "HALT").exists():
        raise RuntimeError("HALT file exists - aborting")
    if (halt_dir / "HALT_DAILY_LOSS").exists():
        raise RuntimeError("HALT_DAILY_LOSS file exists - aborting")

    pos = do.get_position(token, instrument_name="BTC-PERPETUAL")
    if pos.get("size", 0) != 0:
        raise RuntimeError(f"Position != 0: size={pos.get('size')} - aborting")

    open_orders = do.get_open_orders(token, instrument_name="BTC-PERPETUAL")
    if len(open_orders) > 0:
        raise RuntimeError(f"Open orders exist: {len(open_orders)} - aborting")


def _extract_numeric_fields(summary):
    """Extract all numeric fields containing 'pl', 'pnl', 'equity', 'balance', 'fee', or 'session'."""
    keywords = {"pl", "pnl", "equity", "balance", "fee", "session"}
    result = {}

    def flatten(d, prefix=""):
        if isinstance(d, dict):
            for k, v in d.items():
                full_key = f"{prefix}{k}" if not prefix else f"{prefix}.{k}"
                if isinstance(v, (int, float)) and any(kw in k.lower() for kw in keywords):
                    result[full_key] = v
                elif isinstance(v, dict):
                    flatten(v, full_key)

    flatten(summary)
    return result


def _print_table(snapshots):
    """Print table of fields that changed across the 3 snapshots."""
    labels = ["Before Buy", "After Buy", "After Sell"]

    # Collect all keys across all snapshots
    all_keys = set()
    for snap in snapshots:
        all_keys.update(snap.keys())

    # Always include these even if unchanged
    must_include = {
        "session_rpl", "session_upl", "total_pl", "equity", "balance",
        "available_funds", "delta"
    }

    # Filter to changed fields or must_include
    filtered_keys = []
    for key in sorted(all_keys):
        if key == "delta":
            continue
        values = [snapshots[i].get(key) for i in range(3)]
        if len(set(str(v) for v in values)) > 1 or any(key.lower() in k.lower() for k in must_include):
            filtered_keys.append(key)

    # Print header
    print("\n--- Account Summary P&L Fields ---")
    print(f"{'Field':<30} | {labels[0]:<15} | {labels[1]:<15} | {labels[2]:<15} | Delta1->2 | Delta2->3")
    print("-" * 115)

    # Print rows
    for key in sorted(filtered_keys):
        v0 = snapshots[0].get(key)
        v1 = snapshots[1].get(key)
        v2 = snapshots[2].get(key)

        d1 = (v1 - v0) if isinstance(v1, (int, float)) and isinstance(v0, (int, float)) else None
        d2 = (v2 - v1) if isinstance(v2, (int, float)) and isinstance(v1, (int, float)) else None

        v0_str = f"{v0:.8f}" if isinstance(v0, float) else str(v0)
        v1_str = f"{v1:.8f}" if isinstance(v1, float) else str(v1)
        v2_str = f"{v2:.8f}" if isinstance(v2, float) else str(v2)

        d1_str = f"{d1:+.8f}" if d1 is not None else "N/A"
        d2_str = f"{d2:+.8f}" if d2 is not None else "N/A"

        print(f"{key:<30} | {v0_str:<15} | {v1_str:<15} | {v2_str:<15} | {d1_str:<9} | {d2_str}")


def _close_position_if_needed(token):
    """Close position if size != 0; cancel any open orders."""
    pos = do.get_position(token, instrument_name="BTC-PERPETUAL")
    if pos.get("size", 0) != 0:
        print(f"Closing position size={pos['size']}")
        do.close_position(token, instrument_name="BTC-PERPETUAL")
        time.sleep(1)

    open_orders = do.get_open_orders(token, instrument_name="BTC-PERPETUAL")
    if len(open_orders) > 0:
        print(f"Cancelling {len(open_orders)} open orders")
        for order in open_orders:
            try:
                do.cancel(token, order["order_id"])
            except Exception as e:
                print(f"  Failed to cancel {order['order_id']}: {e}")
        time.sleep(1)


def main(argv=None):
    try:
        token = do.authenticate()
        print("Authenticated to Deribit TESTNET")

        # Check preconditions
        _check_preconditions(token)
        print("Preconditions OK: position=0, no open orders, no HALT files")

        # Snapshot 1: before any trades
        print("\n--- Snapshot 1: Before trades ---")
        snap1_full = do.get_account_summary(token, currency="BTC")
        snap1 = _extract_numeric_fields(snap1_full)
        print(f"Extracted {len(snap1)} relevant fields")

        # Debug: print some raw fields to understand structure
        print(f"\nDebug - some account fields:")
        for k in ["balance", "equity", "total_pl", "session_rpl", "session_upl"]:
            if k in snap1_full:
                print(f"  {k}: {snap1_full[k]}")

        # Market buy with amount=10 (most likely contract size for BTC-PERPETUAL)
        amount = 10
        print(f"\nBuying {amount} units of BTC-PERPETUAL")
        try:
            buy_result = do.buy(token, "BTC-PERPETUAL", amount, "market", label="pl_probe_in")
            print(f"Buy order placed: {buy_result.get('order_id')}")
        except Exception as e:
            print(f"Buy failed: {e}")
            return 1

        time.sleep(2)

        # Snapshot 2: after buy
        print("\n--- Snapshot 2: After buy ---")
        snap2_full = do.get_account_summary(token, currency="BTC")
        snap2 = _extract_numeric_fields(snap2_full)
        pos = do.get_position(token, instrument_name="BTC-PERPETUAL")
        print(f"Position size: {pos.get('size', 0)}, unrealized_pnl: {pos.get('unrealized_pnl')}")

        # Market sell reduce_only
        print(f"\nSelling {amount} units (reduce_only)")
        try:
            sell_result = do.sell(token, "BTC-PERPETUAL", amount, "market",
                                  reduce_only=True, label="pl_probe_out")
            print(f"Sell order placed: {sell_result.get('order_id')}")
        except Exception as e:
            print(f"Sell failed: {e}")
            return 1

        time.sleep(2)

        # Snapshot 3: after sell
        print("\n--- Snapshot 3: After sell ---")
        snap3_full = do.get_account_summary(token, currency="BTC")
        snap3 = _extract_numeric_fields(snap3_full)
        pos = do.get_position(token, instrument_name="BTC-PERPETUAL")
        print(f"Position size: {pos.get('size', 0)}, unrealized_pnl: {pos.get('unrealized_pnl')}")

        # Print comparison table
        snapshots = [snap1, snap2, snap3]
        _print_table(snapshots)

        # Close position and cancel orders if needed
        print("\n--- Final cleanup ---")
        _close_position_if_needed(token)

        pos_final = do.get_position(token, instrument_name="BTC-PERPETUAL")
        orders_final = do.get_open_orders(token, instrument_name="BTC-PERPETUAL")

        if pos_final.get("size", 0) == 0 and len(orders_final) == 0:
            print("OK: Account is flat (position=0, no open orders)")
            return 0
        else:
            print(f"WARNING: Account not flat - size={pos_final.get('size')}, orders={len(orders_final)}")
            return 1

    except Exception as e:
        print(f"FATAL: {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
