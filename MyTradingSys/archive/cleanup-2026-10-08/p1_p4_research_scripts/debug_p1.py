#!/usr/bin/env python3
"""Debug P1: check raw data and understand metric."""

import gzip, csv
from pathlib import Path
from datetime import datetime, timezone

DATA_DIR = Path('F:/MTS/data/orderflow_1m')

# Load first 10 bars from first day
int_cols = ('t', 'n_agg', 'n_trades', 'thr_days', 'b99_buy_n', 'b99_sell_n', 'b999_buy_n', 'b999_sell_n')

print("="*80)
print("P1 DEBUG: Raw data sample from first day")
print("="*80)

for p in sorted(DATA_DIR.glob('????-??-??.csv.gz'))[:1]:
    print(f'\nFile: {p.name}')
    print("-"*80)

    with gzip.open(p, 'rt', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= 10:
                break

            t_ms = int(row['t'])
            bar_time = datetime.fromtimestamp(t_ms/1000, tz=timezone.utc)
            buy = float(row['buy_vol'])
            sell = float(row['sell_vol'])
            close = float(row['c'])
            o = float(row['o'])
            h = float(row['h'])
            l = float(row['l'])
            total = buy + sell

            # The metric I computed
            imb = (buy - sell) / total if total > 0 else 0
            imb_bp = imb * 10000

            print(f"\nBar {i}: {bar_time.isoformat()}")
            print(f"  OHLC: {o:.2f} / {h:.2f} / {l:.2f} / {close:.2f}")
            print(f"  Order flow: buy={buy:.0f} USD, sell={sell:.0f} USD, total={total:.0f} USD")
            print(f"  Imbalance ratio: ({buy:.0f} - {sell:.0f}) / {total:.0f} = {imb:.4f} = {imb_bp:.0f} bp")
            print(f"  >>> THIS IS ORDER FLOW DIRECTION, NOT EXECUTION SLIPPAGE <<<")

print("\n" + "="*80)
print("ISSUE IDENTIFIED:")
print("="*80)
print("""
I measured order flow imbalance (% of volume that is buy vs sell), which ranges
from -100% to +100% (= -10000 to +10000 bp). A mean of 3247 bp means on average
the orders are roughly 66% buy, 34% sell (or vice versa).

This is NOT the P1 cost floor metric. The P1_COST_FLOOR analysis should measure:
  "Place a passive limit order. If filled, hold 5/15 min. Exit at market close.
   How much did price move against my entry price?" (= adverse selection)

Example for a BUY limit order at 32450.00:
  - Placed at bar 0, close 32450.00 (touched entry by low or high)
  - Hold 5 min, exit at bar 5 close 32448.50
  - Adverse = (32448.50 - 32450.00) / 32450.00 * 10000 = -4.6 bp (bad fill)

The order flow imbalance is a DIFFERENT metric (market direction/pressure).
""")
