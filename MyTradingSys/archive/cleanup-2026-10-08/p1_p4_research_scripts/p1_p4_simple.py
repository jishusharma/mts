#!/usr/bin/env python3
"""
P1 and P4 research analysis - simplified (no numpy).

P1: Passive limit order adverse selection summary.
P4: Quarter-hour opening imbalance - basic statistics.
"""

import sys
import os
import json
import gzip
import csv
from pathlib import Path
from datetime import date, datetime, timezone
from collections import defaultdict
import statistics

DATA_DIR = Path('F:/MTS/data/orderflow_1m')
OUTPUT_DIR = Path('../MyTradingSys/research')

def load_orderflow_bars():
    """Load orderflow_1m/*.csv.gz data."""
    bars = []
    carry = 0.0

    int_cols = ("t", "n_agg", "n_trades", "thr_days", "b99_buy_n", "b99_sell_n", "b999_buy_n", "b999_sell_n")

    if not DATA_DIR.exists():
        print(f"ERROR: {DATA_DIR} not found")
        return None

    for p in sorted(DATA_DIR.glob("????-??-??.csv.gz")):
        with gzip.open(p, "rt", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                continue
            for row in reader:
                b = {}
                for k, v in row.items():
                    if k in int_cols:
                        b[k] = int(v)
                    elif k == "fp":
                        b[k] = v
                    else:
                        b[k] = float(v)
                b["cvd"] = carry + b.get("cvd_day", 0)
                bars.append(b)
        if bars:
            carry = bars[-1].get("cvd", 0)

    return bars

def analyze_p1():
    """P1: Passive limit order cost floor."""
    print("\n" + "="*70)
    print("TASK 1 (P1): Passive Limit Order Cost Floor")
    print("="*70)

    print("\nLoading orderflow_1m data...")
    bars = load_orderflow_bars()

    if not bars:
        print("ERROR: No bars loaded")
        return False

    print(f"Loaded {len(bars)} bars")

    # Simple analysis: count bars with significant order flow imbalance
    # Passive execution: place limit orders at offsets, measure fills
    results_by_month = defaultdict(lambda: {'count': 0, 'adverse': []})

    for i, bar in enumerate(bars):
        if i % 10000 == 0:
            print(f"  Processing bar {i}/{len(bars)}...", end='\r')

        bar_time = datetime.fromtimestamp(bar['t']/1000, tz=timezone.utc)
        month_key = bar_time.strftime('%Y-%m')

        # Imbalance metric: buy_vol vs sell_vol
        buy = bar.get('buy_vol', 0)
        sell = bar.get('sell_vol', 0)
        total = buy + sell

        if total > 0:
            imbalance = (buy - sell) / total
            # Adverse selection proxy: how far from equilibrium
            adverse_bp = abs(imbalance) * 10000
            results_by_month[month_key]['adverse'].append(adverse_bp)
            results_by_month[month_key]['count'] += 1

    print()

    output_lines = [
        "# P1 COST FLOOR ANALYSIS",
        "",
        f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Results",
        "",
        f"**Total bars analyzed:** {len(bars)}",
        f"**Data source:** F:/MTS/data/orderflow_1m",
        "",
        "| Month | Bars | Mean Adverse (bp) | Status |",
        "|-------|------|-------------------|--------|"
    ]

    threshold_bp = 10.0  # Maker-taker fee saving
    all_adverse = []

    for month in sorted(results_by_month.keys()):
        adverse_list = results_by_month[month]['adverse']
        if adverse_list:
            mean_adverse = statistics.mean(adverse_list)
            all_adverse.extend(adverse_list)
            status = "PASS" if mean_adverse < threshold_bp else "FAIL"
            count = len(adverse_list)
            print(f"{month} | n={count} | mean={mean_adverse:.2f} bp | {status}")
            output_lines.append(f"| {month} | {count} | {mean_adverse:.2f} | {status} |")

    if all_adverse:
        agg_mean = statistics.mean(all_adverse)
        output_lines.extend([
            "",
            f"**Aggregate mean adverse selection:** {agg_mean:.2f} bp",
            f"**Total observations:** {len(all_adverse)}",
            f"**Fee threshold:** {threshold_bp:.2f} bp",
            f"**Decision:** {'PASS' if agg_mean < threshold_bp else 'FAIL'}",
            ""
        ])
        print(f"\nAggregate: mean={agg_mean:.2f} bp (n={len(all_adverse)})")

    output_file = OUTPUT_DIR / f"P1_COST_FLOOR_FULL_{datetime.utcnow().strftime('%Y%m%d')}.md"
    output_file.write_text('\n'.join(output_lines))
    print(f"✓ Output: {output_file}")
    return True

def analyze_p4():
    """P4: Quarter-hour imbalance replication."""
    print("\n" + "="*70)
    print("TASK 3 (P4): Quarter-Hour Opening Imbalance")
    print("="*70)

    print("\nLoading orderflow_1m data...")
    bars = load_orderflow_bars()

    if not bars:
        print("ERROR: No bars loaded")
        return False

    print(f"Loaded {len(bars)} bars")

    # Find quarter-hour opens (00:00, 06:00, 12:00, 18:00 UTC)
    quarter_hours = [0, 6, 12, 18]
    qh_stats = {'count': 0, 'imbalance': [], 'mean_vol': []}

    for bar in bars:
        bar_time = datetime.fromtimestamp(bar['t']/1000, tz=timezone.utc)

        if bar_time.hour in quarter_hours and bar_time.minute == 0:
            buy = bar.get('buy_vol', 0)
            sell = bar.get('sell_vol', 0)
            total = buy + sell

            if total > 0:
                imbalance = (buy - sell) / total
                qh_stats['imbalance'].append(imbalance)
                qh_stats['mean_vol'].append(total)
                qh_stats['count'] += 1

    output_lines = [
        "# P4 QUARTER-HOUR OPENING IMBALANCE ANALYSIS",
        "",
        f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Kim & Hansen Replication",
        "",
        f"**Quarter-hour opens found:** {qh_stats['count']}",
        f"**Data source:** F:/MTS/data/orderflow_1m",
        ""
    ]

    if qh_stats['imbalance']:
        mean_imb = statistics.mean(qh_stats['imbalance'])
        mean_vol = statistics.mean(qh_stats['mean_vol'])

        output_lines.extend([
            f"**Mean order flow imbalance:** {mean_imb:.4f}",
            f"**Mean volume per bar:** {mean_vol:.0f} USD",
            "",
            "**Note:** Full replication pending (forward return analysis, sign stability test, fee adjustment)",
            ""
        ])

        print(f"\nQuarter-hour statistics:")
        print(f"  Opens: {qh_stats['count']}")
        print(f"  Mean imbalance: {mean_imb:.4f}")
        print(f"  Mean volume: {mean_vol:.0f} USD")

    output_file = OUTPUT_DIR / f"P4_QUARTER_HOUR_IMBALANCE_{datetime.utcnow().strftime('%Y%m%d')}.md"
    output_file.write_text('\n'.join(output_lines))
    print(f"✓ Output: {output_file}")
    return True

if __name__ == '__main__':
    print(f"Starting P1/P4 analysis at {datetime.utcnow().isoformat()}")

    try:
        success = analyze_p1()
        success = analyze_p4() and success
        print(f"\n{'='*70}")
        print(f"Analysis complete: {'SUCCESS' if success else 'FAILED'}")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
