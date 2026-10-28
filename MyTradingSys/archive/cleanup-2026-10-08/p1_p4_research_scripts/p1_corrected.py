#!/usr/bin/env python3
"""
P1 Cost Floor Analysis - CORRECTED

Bug fix: Previous analysis measured order flow imbalance (market direction),
not passive limit order adverse selection (execution slippage).

Correct metric: Place passive limit orders at offsets 0/2/5 bp below/above
prior close. If filled (by touch), hold 5m or 15m, exit at market close.
Measure: how much price moved AGAINST the entry (adverse selection in bp).

Trial row: bug-fix rerun after 41fa58f. Pre-registration unchanged.
"""

import gzip, csv
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
import statistics

DATA_DIR = Path('F:/MTS/data/orderflow_1m')
OUTPUT_DIR = Path('../MyTradingSys/research')

def load_bars():
    """Load orderflow_1m as list of dicts."""
    bars = []
    carry = 0.0
    int_cols = ('t', 'n_agg', 'n_trades', 'thr_days', 'b99_buy_n', 'b99_sell_n', 'b999_buy_n', 'b999_sell_n')

    for p in sorted(DATA_DIR.glob('????-??-??.csv.gz')):
        with gzip.open(p, 'rt', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                b = {}
                for k, v in row.items():
                    if k in int_cols:
                        b[k] = int(v)
                    elif k == 'fp':
                        b[k] = v
                    else:
                        b[k] = float(v)
                b['cvd'] = carry + b.get('cvd_day', 0)
                bars.append(b)
        if bars:
            carry = bars[-1].get('cvd', 0)

    return bars

def analyze_p1_corrected():
    """Correct P1: passive limit order adverse selection."""

    print("\n" + "="*80)
    print("P1 COST FLOOR ANALYSIS - CORRECTED (Bug-Fix Rerun)")
    print("="*80)

    print(f"\nLoading orderflow_1m data...")
    bars = load_bars()

    if not bars:
        print("ERROR: No bars loaded")
        return False

    print(f"Loaded {len(bars)} bars")
    start_time = datetime.fromtimestamp(bars[0]['t']/1000, tz=timezone.utc)
    end_time = datetime.fromtimestamp(bars[-1]['t']/1000, tz=timezone.utc)
    print(f"Date range: {start_time.date()} to {end_time.date()}")

    # Correct P1 logic:
    # For each 1m bar at time t:
    #   - Place passive limit orders at offsets 0, 2, 5 bp below/above prior close
    #   - Check if filled in next bar (by touching low/high)
    #   - If filled, hold until t+5m or t+15m
    #   - Measure adverse selection = (exit_price - entry_price) / entry_price * 10000 bp

    results_by_month = defaultdict(lambda: {'fills': []})
    month_keys = set()

    for i in range(len(bars) - 15):  # Need 15 bars ahead for 15m hold
        bar = bars[i]
        bar_time = datetime.fromtimestamp(bar['t']/1000, tz=timezone.utc)
        month_key = bar_time.strftime('%Y-%m')
        month_keys.add(month_key)

        close_price = bar['c']
        o = bar['o']
        h = bar['h']
        l = bar['l']

        # Test passive orders at offsets 0, 2, 5 bp (both sides)
        for offset_bp in [0, 2, 5]:
            offset_pct = offset_bp / 10000.0

            # SELL limit (passively offer above): placed at close * (1 + offset)
            # Filled if next bar's high >= offer price
            ask_price = close_price * (1.0 + offset_pct)

            # Check fills in next bar
            next_bar = bars[i + 1]
            if next_bar['h'] >= ask_price:
                # Filled at this bar (on the touch/through)
                # Now hold and measure exit price
                for hold_bars in [5, 15]:
                    if i + hold_bars < len(bars):
                        exit_bar = bars[i + hold_bars]
                        exit_price = exit_bar['c']
                        # Adverse = price moved AGAINST entry
                        # For sell order: adverse if price went UP (bad for seller)
                        adverse_bp = ((exit_price - ask_price) / ask_price) * 10000
                        results_by_month[month_key]['fills'].append({
                            'type': 'sell',
                            'offset_bp': offset_bp,
                            'hold_min': hold_bars,
                            'entry': ask_price,
                            'exit': exit_price,
                            'adverse_bp': adverse_bp
                        })

            # BUY limit (passively bid below): placed at close * (1 - offset)
            # Filled if next bar's low <= bid price
            bid_price = close_price * (1.0 - offset_pct)

            if next_bar['l'] <= bid_price:
                # Filled at this bar
                for hold_bars in [5, 15]:
                    if i + hold_bars < len(bars):
                        exit_bar = bars[i + hold_bars]
                        exit_price = exit_bar['c']
                        # Adverse = price moved AGAINST entry
                        # For buy order: adverse if price went DOWN (bad for buyer)
                        adverse_bp = ((exit_price - bid_price) / bid_price) * 10000
                        results_by_month[month_key]['fills'].append({
                            'type': 'buy',
                            'offset_bp': offset_bp,
                            'hold_min': hold_bars,
                            'entry': bid_price,
                            'exit': exit_price,
                            'adverse_bp': adverse_bp
                        })

        if i % 100000 == 0:
            print(f"  Progress: bar {i}/{len(bars)}", end='\r')

    print()

    # Compile results
    print("\nMonth-by-month adverse selection (bp):")
    print("-" * 80)

    all_adverse = []
    output_lines = [
        "# P1 COST FLOOR ANALYSIS - CORRECTED",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Bug Fix (Trial Row)",
        "",
        "Previous analysis measured order flow imbalance (market direction %), not",
        "passive limit order adverse selection (execution slippage). This rerun",
        "implements correct metric: place passive limits at offsets 0/2/5 bp,",
        "measure price move against entry after 5m and 15m holds.",
        "",
        f"**Data:** F:/MTS/data/orderflow_1m ({len(bars)} bars, {start_time.date()} to {end_time.date()})",
        "",
        "## Results by Month",
        "",
        "| Month | n_fills | mean_adverse_bp | Status |",
        "|-------|---------|-----------------|--------|"
    ]

    threshold_bp = 10.0  # Maker-taker fee saving

    for month_key in sorted(month_keys):
        fills = results_by_month[month_key]['fills']
        if not fills:
            continue

        adverse_list = [f['adverse_bp'] for f in fills]
        mean_adverse = statistics.mean(adverse_list)
        all_adverse.extend(adverse_list)

        status = "PASS" if mean_adverse < threshold_bp else "FAIL"
        print(f"{month_key} | n={len(adverse_list):5} | mean={mean_adverse:7.2f} bp | {status}")
        output_lines.append(f"| {month_key} | {len(adverse_list)} | {mean_adverse:.2f} | {status} |")

    # Aggregate
    if all_adverse:
        agg_mean = statistics.mean(all_adverse)
        try:
            agg_std = statistics.stdev(all_adverse)
        except:
            agg_std = 0.0

        output_lines.extend([
            "",
            "## Aggregate Result",
            "",
            f"**Total filled passive orders:** {len(all_adverse)}",
            f"**Mean adverse selection:** {agg_mean:.2f} bp",
            f"**Std dev:** {agg_std:.2f} bp",
            f"**Fee threshold (maker-taker round-trip):** {threshold_bp:.2f} bp",
            f"**Decision:** {'PASS - passive execution worth modelling' if agg_mean < threshold_bp else 'FAIL - adverse selection exceeds fee saving'}",
            ""
        ])

        print("-" * 80)
        print(f"Aggregate: n={len(all_adverse)} | mean={agg_mean:.2f} bp | std={agg_std:.2f}")
        print(f"Decision: {'PASS' if agg_mean < threshold_bp else 'FAIL'}")

    # Write output
    output_file = OUTPUT_DIR / f"P1_COST_FLOOR_FULL_20261006_CORRECTED.md"
    output_file.write_text('\n'.join(output_lines))
    print(f"\n✓ Output: {output_file}")
    return True

if __name__ == '__main__':
    analyze_p1_corrected()
