#!/usr/bin/env python3
"""
P1 and P4 research analysis runner - task execution at low priority.

P1: Passive limit order adverse selection on orderflow_1m archive.
P4: Quarter-hour opening order imbalance replication (Kim & Hansen).

Pre-registered 2026-10-06 in research/PRE_REG_P*.md.
"""

import sys
import os
import json
import gzip
import csv
from pathlib import Path
from datetime import date, datetime, timezone
from collections import defaultdict
import numpy as np

# Add repo to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from MyTradingSys.backtest.layers.fabio.orderflow_bars import load_days

DATA_DIR = Path('F:/MTS/data/orderflow_1m')
OUTPUT_DIR = Path('../MyTradingSys/research')

def run_p1_analysis():
    """Task 1: Passive limit order cost floor on orderflow_1m."""
    print("\n" + "="*70)
    print("TASK 1 (P1): Passive Limit Order Cost Floor Analysis")
    print("="*70)

    if not DATA_DIR.exists():
        print(f"ERROR: {DATA_DIR} not found")
        return False

    print(f"\nLoading orderflow_1m data from {DATA_DIR}...")
    bars = load_days(str(DATA_DIR))

    if not bars:
        print("ERROR: No bars loaded")
        return False

    print(f"Loaded {len(bars)} bars")
    start_time = datetime.fromtimestamp(bars[0]['t']/1000, tz=timezone.utc)
    end_time = datetime.fromtimestamp(bars[-1]['t']/1000, tz=timezone.utc)
    print(f"Date range: {start_time.date()} to {end_time.date()}")

    # Analyze adverse selection by month
    results_by_month = defaultdict(lambda: {'fills': [], 'adverse_bp': []})

    # Process bars: passive limit orders at offsets 0, 2, 5 bp
    # For each bar, assume we place limit orders and check fills in next bars
    for i in range(len(bars) - 15):  # Need 15m ahead
        bar = bars[i]
        bar_time = datetime.fromtimestamp(bar['t']/1000, tz=timezone.utc)
        month_key = bar_time.strftime('%Y-%m')

        close_price = bar['c']

        # Test offsets: 0, 2, 5 bp (both buy and sell)
        for offset_bp in [0, 2, 5]:
            offset_pct = offset_bp / 10000.0

            # Bid (sell limit) - place below close
            bid_price = close_price * (1 - offset_pct)

            # Check if filled in next bars (by touch)
            for j in range(1, min(16, len(bars) - i)):  # Check 1-15m ahead
                next_bar = bars[i + j]
                if next_bar['l'] <= bid_price:  # Filled on low
                    hold_idx = i + (5 if j <= 5 else 15)
                    if hold_idx < len(bars):
                        exit_price = bars[hold_idx]['c']
                        adverse_bp = ((exit_price - bid_price) / bid_price) * 10000
                        results_by_month[month_key]['adverse_bp'].append(adverse_bp)
                        results_by_month[month_key]['fills'].append({
                            'time': bar_time.isoformat(),
                            'entry': bid_price,
                            'exit': exit_price,
                            'adverse_bp': adverse_bp,
                            'hold_min': min(j, 15)
                        })
                    break

            # Ask (buy limit) - place above close
            ask_price = close_price * (1 + offset_pct)
            for j in range(1, min(16, len(bars) - i)):
                next_bar = bars[i + j]
                if next_bar['h'] >= ask_price:  # Filled on high
                    hold_idx = i + (5 if j <= 5 else 15)
                    if hold_idx < len(bars):
                        exit_price = bars[hold_idx]['c']
                        adverse_bp = ((exit_price - ask_price) / ask_price) * 10000
                        results_by_month[month_key]['adverse_bp'].append(adverse_bp)
                        results_by_month[month_key]['fills'].append({
                            'time': bar_time.isoformat(),
                            'entry': ask_price,
                            'exit': exit_price,
                            'adverse_bp': adverse_bp,
                            'hold_min': min(j, 15)
                        })
                    break

    # Compute statistics
    print("\nMonth-by-month results:")
    print("-" * 70)

    all_adverse = []
    output_lines = [
        "# P1 COST FLOOR ANALYSIS - FULL ORDERFLOW_1M ARCHIVE",
        "",
        f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Summary",
        "",
        f"**Data:** F:/MTS/data/orderflow_1m (full archive, {len(bars)} bars)",
        "**Strategy:** Passive limit orders (offsets 0/2/5 bp below/above prior close)",
        "**Holds:** 5m, 15m",
        "**Metric:** Mean adverse selection (bp from entry to exit)",
        "",
        "## Month-by-Month Results",
        "",
        "| Month | n_fills | mean_adverse_bp | Status |",
        "|-------|---------|-----------------|--------|"
    ]

    for month in sorted(results_by_month.keys()):
        adverse_list = results_by_month[month]['adverse_bp']
        if not adverse_list:
            continue

        mean_adverse = np.mean(adverse_list)
        all_adverse.extend(adverse_list)

        # Decision: PASS if adverse < 10 bp (maker-taker fee saving)
        threshold_bp = 10.0
        status = "PASS" if mean_adverse < threshold_bp else "FAIL"

        print(f"{month} | n={len(adverse_list):4} | mean={mean_adverse:7.2f} bp | {status}")
        output_lines.append(f"| {month} | {len(adverse_list)} | {mean_adverse:.2f} | {status} |")

    # Aggregate
    if all_adverse:
        agg_mean = np.mean(all_adverse)
        agg_std = np.std(all_adverse)
        threshold_bp = 10.0

        output_lines.extend([
            "",
            "## Aggregate Result",
            "",
            f"**Total fills:** {len(all_adverse)}",
            f"**Mean adverse selection:** {agg_mean:.2f} bp",
            f"**Std dev:** {agg_std:.2f} bp",
            f"**Fee threshold (maker-taker):** {threshold_bp:.2f} bp",
            f"**Decision:** {'PASS - passive execution worth modelling' if agg_mean < threshold_bp else 'FAIL'}",
            ""
        ])

        print("-" * 70)
        print(f"Aggregate: n={len(all_adverse)} | mean={agg_mean:.2f} bp | std={agg_std:.2f}")
        print(f"Decision: {'PASS' if agg_mean < threshold_bp else 'FAIL'}")

    # Write output
    output_file = OUTPUT_DIR / f"P1_COST_FLOOR_FULL_{datetime.utcnow().strftime('%Y%m%d')}.md"
    output_file.write_text('\n'.join(output_lines))
    print(f"\n✓ Output: {output_file}")
    return True

def run_p4_analysis():
    """Task 3: Quarter-hour opening imbalance replication (Kim & Hansen)."""
    print("\n" + "="*70)
    print("TASK 3 (P4): Quarter-Hour Opening Order Imbalance Replication")
    print("="*70)

    if not DATA_DIR.exists():
        print(f"ERROR: {DATA_DIR} not found")
        return False

    print(f"\nLoading orderflow_1m data from {DATA_DIR}...")
    bars = load_days(str(DATA_DIR))

    if not bars:
        print("ERROR: No bars loaded")
        return False

    print(f"Loaded {len(bars)} bars")

    # Find quarter-hour opens (00:00, 06:00, 12:00, 18:00 UTC)
    quarter_hours = [0, 6, 12, 18]  # UTC hours
    qh_opens = []

    for i, bar in enumerate(bars):
        bar_time = datetime.fromtimestamp(bar['t']/1000, tz=timezone.utc)
        if bar_time.hour in quarter_hours and bar_time.minute == 0:
            qh_opens.append((i, bar, bar_time))

    print(f"\nFound {len(qh_opens)} quarter-hour opens")

    if not qh_opens:
        print("ERROR: No quarter-hour opens found")
        return False

    # Calculate imbalance and returns
    results_by_window = defaultdict(list)
    results_by_year = defaultdict(lambda: defaultdict(list))

    for open_idx, open_bar, open_time in qh_opens:
        buy_vol = open_bar['buy_vol']
        sell_vol = open_bar['sell_vol']
        total_vol = buy_vol + sell_vol

        if total_vol == 0:
            continue

        imbalance = (buy_vol - sell_vol) / total_vol
        year = open_time.year

        # Calculate forward returns (4h, 8h, 12h)
        for fwd_h in [4, 8, 12]:
            fwd_idx = open_idx + (fwd_h * 60)  # 60 bars per hour

            if fwd_idx >= len(bars):
                continue

            entry_price = open_bar['o']  # Entry at quarter-hour open
            exit_price = bars[fwd_idx]['c']  # Exit at forward bar close

            ret_bp = ((exit_price - entry_price) / entry_price) * 10000

            results_by_window[fwd_h].append(ret_bp)
            results_by_year[year][fwd_h].append((imbalance, ret_bp))

    # Analyze sign stability and net returns
    output_lines = [
        "# P4 QUARTER-HOUR OPENING IMBALANCE ANALYSIS (Kim & Hansen Replication)",
        "",
        f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Replication of Kim & Hansen arXiv 2607.09426",
        "",
        f"**Data:** orderflow_1m ({len(bars)} bars, full archive)",
        f"**Quarter-hour opens:** {len(qh_opens)} found (00:00, 06:00, 12:00, 18:00 UTC)",
        "**Return windows:** 4h, 8h, 12h forward",
        "**Fee:** 0.0005 (taker, round-trip 0.001 = 10 bp)",
        "",
        "## Result",
        ""
    ]

    if len(results_by_window) > 0:
        print("\nForward returns by window:")
        for fwd_h in sorted(results_by_window.keys()):
            rets = results_by_window[fwd_h]
            mean_ret = np.mean(rets)
            print(f"  {fwd_h}h: n={len(rets)}, mean={mean_ret:.2f} bp")

            output_lines.append(f"**{fwd_h}h forward returns:** n={len(rets)}, mean={mean_ret:.2f} bp")

        output_lines.append("")
        output_lines.append("**Note:** Replication incomplete (imbalance-return correlation analysis and sign stability test pending implementation)")

    # Write output
    output_file = OUTPUT_DIR / f"P4_QUARTER_HOUR_IMBALANCE_{datetime.utcnow().strftime('%Y%m%d')}.md"
    output_file.write_text('\n'.join(output_lines))
    print(f"\n✓ Output: {output_file}")
    return True

if __name__ == '__main__':
    print(f"Starting P1/P4 research analysis at {datetime.utcnow().isoformat()}")

    success = True
    success = run_p1_analysis() and success
    success = run_p4_analysis() and success

    print(f"\n{'='*70}")
    print(f"Analysis complete: {'SUCCESS' if success else 'INCOMPLETE'}")
    print(f"{'='*70}")
    sys.exit(0 if success else 1)
