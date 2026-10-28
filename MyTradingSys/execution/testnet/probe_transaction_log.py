"""
MyTradingSys/execution/testnet/probe_transaction_log.py

OPERATOR-RUN probe to collect transaction log entries and determine which
types should be excluded from daily P/L computation.

Process:
  1. Authenticate
  2. Get transaction log for BTC today (00:00 UTC - now)
  3. Collect all entries, following continuation if present
  4. Print per-type count, sum of change, sum of cashflow
  5. Print first 3 raw entries (keys + type + change)
  6. Get account summary to compare equity delta vs sum of changes
  7. Recommend which types to exclude

Run on TESTNET only.

Usage:
    cd MyTradingSys/execution/testnet
    python3 probe_transaction_log.py
"""
import sys
sys.dont_write_bytecode = True

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import deribit_orders as do  # noqa: E402


def _get_today_midnight_ms():
    """Get 00:00 UTC today as milliseconds since epoch."""
    now = datetime.now(timezone.utc)
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return int(midnight.timestamp() * 1000)


def _get_now_ms():
    """Get current time in milliseconds since epoch."""
    return int(time.time() * 1000)


def main(argv=None):
    try:
        token = do.authenticate()
        print("Authenticated to Deribit TESTNET\n")

        # Get timestamps
        start_ms = _get_today_midnight_ms()
        end_ms = _get_now_ms()

        start_dt = datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc)
        end_dt = datetime.fromtimestamp(end_ms / 1000, tz=timezone.utc)

        print(f"Transaction log period: {start_dt.isoformat()} to {end_dt.isoformat()}")
        print(f"  start_timestamp={start_ms} ms")
        print(f"  end_timestamp={end_ms} ms\n")

        # Collect all entries across continuation pages
        all_entries = []
        continuation = None
        page_count = 0

        while True:
            page_count += 1
            params = {
                "currency": "BTC",
                "start_timestamp": start_ms,
                "end_timestamp": end_ms,
                "count": 100
            }
            if continuation:
                params["continuation"] = continuation

            print(f"Fetching page {page_count}...")
            result = do._call("private/get_transaction_log", params, token)

            if isinstance(result, dict):
                entries = result.get("logs", [])
                continuation = result.get("continuation")
            else:
                # In case the API returns just a list
                entries = result if isinstance(result, list) else []
                continuation = None

            all_entries.extend(entries)
            print(f"  Got {len(entries)} entries (total so far: {len(all_entries)})")

            if not continuation:
                print(f"  No continuation - end of results\n")
                break

        # Analyze entries by type
        type_counts = defaultdict(int)
        type_change_sum = defaultdict(float)
        type_cashflow_sum = defaultdict(float)

        for entry in all_entries:
            entry_type = entry.get("type", "unknown")
            type_counts[entry_type] += 1

            change = entry.get("change", 0)
            if isinstance(change, (int, float)):
                type_change_sum[entry_type] += change

            cashflow = entry.get("cashflow")
            if cashflow is not None and isinstance(cashflow, (int, float)):
                type_cashflow_sum[entry_type] += cashflow

        # Print per-type summary
        print("--- Per-Type Summary ---")
        print(f"{'Type':<20} | {'Count':>6} | {'Sum Change (BTC)':>18} | {'Sum Cashflow (BTC)':>18}")
        print("-" * 80)

        for entry_type in sorted(type_counts.keys()):
            count = type_counts[entry_type]
            change_sum = type_change_sum.get(entry_type, 0)
            cashflow_sum = type_cashflow_sum.get(entry_type, 0)

            change_str = f"{change_sum:.8f}" if change_sum != 0 else "0"
            cashflow_str = f"{cashflow_sum:.8f}" if cashflow_sum != 0 else "0"

            print(f"{entry_type:<20} | {count:>6} | {change_str:>18} | {cashflow_str:>18}")

        total_change = sum(type_change_sum.values())
        total_cashflow = sum(type_cashflow_sum.values())
        print("-" * 80)
        print(f"{'TOTAL':<20} | {len(all_entries):>6} | {total_change:>18.8f} | {total_cashflow:>18.8f}\n")

        # Print first 3 raw entries
        print("--- First 3 Raw Entries (keys + type + change) ---")
        for i, entry in enumerate(all_entries[:3]):
            print(f"\nEntry {i+1}:")
            print(f"  type: {entry.get('type')}")
            print(f"  change: {entry.get('change')}")
            print(f"  keys: {sorted(entry.keys())}")

        # Get current account summary for equity comparison
        print("\n--- Account Summary for Sanity Check ---")
        acct = do.get_account_summary(token, currency="BTC")
        equity = acct.get("equity", 0)
        balance = acct.get("balance", 0)
        available_funds = acct.get("available_funds", 0)

        print(f"equity: {equity:.8f} BTC")
        print(f"balance: {balance:.8f} BTC")
        print(f"available_funds: {available_funds:.8f} BTC")

        # Note: This is a rough sanity check.
        # total_change should be close to equity change since start of trading
        # but we don't have the starting equity, so we just report the total change.
        print(f"\nTotal change from transactions: {total_change:.8f} BTC")
        print(f"(Expected to match equity delta from start of day)")

        print("\n--- Recommendation ---")
        print("Types to EXCLUDE from daily P/L (deposits/withdrawals/transfers):")
        print("  - deposit")
        print("  - withdrawal")
        print("  - transfer")
        print("  - transfer_in")
        print("  - transfer_out")
        print("  (and any settlement-related or fee-rebate types)")
        print("\nTypes to INCLUDE in daily P/L (trading):")
        print("  - trade")
        print("  - settlement")
        print("  - delivery")
        print("  - liquidation")
        print("(Check actual entries above to confirm which types are present)")

        return 0

    except Exception as e:
        print(f"FATAL: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
