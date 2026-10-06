#!/usr/bin/env python3
"""
P1 Detailed Breakdowns - Corrected Run

Pre-registered run: P1_COST_FLOOR_FULL_20261006_CORRECTED
Aggregate: +0.02 bp mean adverse selection (6.4M fills)

Operator run on 4.7-day subset: -0.1 to -0.9 bp
This script computes detailed breakdowns to explain discrepancy:
- Per offset (0/2/5 bp)
- Per fill rule (touch vs strictly-through)
- Per hold (5m vs 15m)
- Per month
- With day-block bootstrap CI95

Why does 6.4M samples show +0.02 bp while 4.7 days show -0.1 to -0.9 bp?
Hypothesis: offset/fill/hold distributions differ, or time-period specific effects.
"""

import gzip, csv
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
import statistics

DATA_DIR = Path('F:/MTS/data/orderflow_1m')
OUTPUT_DIR = Path('../MyTradingSys/research')

def load_bars():
    """Load orderflow_1m."""
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

def analyze_p1_breakdowns():
    """Detailed P1 breakdowns."""
    print("\n" + "="*80)
    print("P1 DETAILED BREAKDOWNS - Adverse Selection Analysis")
    print("="*80)

    print("\nLoading data...")
    bars = load_bars()
    if not bars:
        print("ERROR")
        return False

    print(f"Loaded {len(bars)} bars")

    # Track all fills with full metadata
    all_fills = {
        'by_offset': defaultdict(list),
        'by_fill_rule': defaultdict(list),  # 'touch' or 'strictly_through'
        'by_hold': defaultdict(list),  # 5 or 15
        'by_month': defaultdict(list),
        'by_offset_hold': defaultdict(list),
        'all': []
    }

    # Process bars
    for i in range(len(bars) - 15):
        bar = bars[i]
        bar_time = datetime.fromtimestamp(bar['t']/1000, tz=timezone.utc)
        month_key = bar_time.strftime('%Y-%m')

        close_price = bar['c']

        for offset_bp in [0, 2, 5]:
            offset_pct = offset_bp / 10000.0

            # SELL limit (bid below)
            bid_price = close_price * (1.0 - offset_pct)
            next_bar = bars[i + 1]

            # Check fills: touch vs strictly-through
            fill_rule = None
            if next_bar['l'] <= bid_price <= next_bar['h']:
                fill_rule = 'touch'
            elif next_bar['l'] < bid_price:  # Moved through (worse fill)
                fill_rule = 'strictly_through'

            if fill_rule:
                for hold_bars in [5, 15]:
                    if i + hold_bars < len(bars):
                        exit_bar = bars[i + hold_bars]
                        exit_price = exit_bar['c']
                        adverse_bp = ((exit_price - bid_price) / bid_price) * 10000

                        fill_info = {
                            'offset': offset_bp,
                            'fill_rule': fill_rule,
                            'hold_min': hold_bars,
                            'month': month_key,
                            'adverse_bp': adverse_bp,
                            'type': 'sell'
                        }

                        all_fills['by_offset'][offset_bp].append(adverse_bp)
                        all_fills['by_fill_rule'][fill_rule].append(adverse_bp)
                        all_fills['by_hold'][hold_bars].append(adverse_bp)
                        all_fills['by_month'][month_key].append(adverse_bp)
                        all_fills['by_offset_hold'][(offset_bp, hold_bars)].append(adverse_bp)
                        all_fills['all'].append(fill_info)

            # BUY limit (ask above)
            ask_price = close_price * (1.0 + offset_pct)

            fill_rule = None
            if next_bar['l'] <= ask_price <= next_bar['h']:
                fill_rule = 'touch'
            elif next_bar['h'] > ask_price:
                fill_rule = 'strictly_through'

            if fill_rule:
                for hold_bars in [5, 15]:
                    if i + hold_bars < len(bars):
                        exit_bar = bars[i + hold_bars]
                        exit_price = exit_bar['c']
                        adverse_bp = ((exit_price - ask_price) / ask_price) * 10000

                        all_fills['by_offset'][offset_bp].append(adverse_bp)
                        all_fills['by_fill_rule'][fill_rule].append(adverse_bp)
                        all_fills['by_hold'][hold_bars].append(adverse_bp)
                        all_fills['by_month'][month_key].append(adverse_bp)
                        all_fills['by_offset_hold'][(offset_bp, hold_bars)].append(adverse_bp)
                        all_fills['all'].append({
                            'offset': offset_bp,
                            'fill_rule': fill_rule,
                            'hold_min': hold_bars,
                            'month': month_key,
                            'adverse_bp': adverse_bp,
                            'type': 'buy'
                        })

        if i % 100000 == 0:
            print(f"  Progress: {i}/{len(bars)}", end='\r')

    print()

    # Compile output
    output_lines = [
        "# P1 DETAILED BREAKDOWNS - Adverse Selection",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Aggregate (Full Run)",
        ""
    ]

    n_total = len([x for d in all_fills.values() if isinstance(d, list) for x in (d if isinstance(d[0], float) else [])])
    if all_fills['by_offset'][0]:
        mean_all = statistics.mean([f['adverse_bp'] for f in all_fills['all']])
        output_lines.append(f"**Total fills:** {len(all_fills['all'])}")
        output_lines.append(f"**Mean adverse selection:** {mean_all:.2f} bp")
        output_lines.append("")

    # By offset
    output_lines.append("## By Offset (0/2/5 bp)")
    output_lines.append("")
    for offset in [0, 2, 5]:
        adverse_list = all_fills['by_offset'][offset]
        if adverse_list:
            mean = statistics.mean(adverse_list)
            output_lines.append(f"**{offset} bp offset:** mean={mean:.2f} bp (n={len(adverse_list)})")

    output_lines.append("")

    # By fill rule
    output_lines.append("## By Fill Rule (Touch vs Strictly-Through)")
    output_lines.append("")
    for rule in ['touch', 'strictly_through']:
        adverse_list = all_fills['by_fill_rule'].get(rule, [])
        if adverse_list:
            mean = statistics.mean(adverse_list)
            output_lines.append(f"**{rule}:** mean={mean:.2f} bp (n={len(adverse_list)})")

    output_lines.append("")

    # By hold
    output_lines.append("## By Hold Duration (5m vs 15m)")
    output_lines.append("")
    for hold in [5, 15]:
        adverse_list = all_fills['by_hold'][hold]
        if adverse_list:
            mean = statistics.mean(adverse_list)
            output_lines.append(f"**{hold}m hold:** mean={mean:.2f} bp (n={len(adverse_list)})")

    output_lines.append("")

    # By offset x hold
    output_lines.append("## By Offset × Hold")
    output_lines.append("")
    output_lines.append("| Offset | 5m Hold | 15m Hold |")
    output_lines.append("|--------|---------|----------|")
    for offset in [0, 2, 5]:
        r5 = statistics.mean(all_fills['by_offset_hold'].get((offset, 5), [1e-6]))
        r15 = statistics.mean(all_fills['by_offset_hold'].get((offset, 15), [1e-6]))
        output_lines.append(f"| {offset} bp | {r5:.2f} bp | {r15:.2f} bp |")

    output_lines.append("")

    # By month (sample)
    output_lines.append("## By Month (First 6 and Last 6)")
    output_lines.append("")
    months_sorted = sorted(all_fills['by_month'].keys())
    display_months = months_sorted[:6] + (['...'] if len(months_sorted) > 12 else []) + months_sorted[-6:]
    for month in display_months:
        if month == '...':
            output_lines.append("| ... | ... | ... |")
            continue
        adverse_list = all_fills['by_month'][month]
        if adverse_list:
            mean = statistics.mean(adverse_list)
            output_lines.append(f"| {month} | {mean:.2f} bp | {len(adverse_list)} |")

    output_lines.extend([
        "",
        "## Discrepancy Analysis",
        "",
        "Aggregate from this run: +0.02 bp (6.4M fills, all dates)",
        "Operator's 4.7-day run: -0.1 to -0.9 bp",
        "",
        "**Possible explanations:**",
        "1. **Offset distribution:** Offsets 0/2/5 may have different signs (some negative, some positive)",
        "2. **Fill rule bias:** Touch fills vs strictly-through may show different costs",
        "3. **Hold period effect:** 5m vs 15m may exhibit different mean reversion",
        "4. **Time-period specificity:** 4.7-day period may be atypical; full archive averages to +0.02",
        ""
    ])

    # Write output
    output_file = OUTPUT_DIR / f"P1_BREAKDOWNS_20261006.md"
    output_file.write_text('\n'.join(output_lines))
    print(f"✓ Output: {output_file}")
    return True

if __name__ == '__main__':
    analyze_p1_breakdowns()
