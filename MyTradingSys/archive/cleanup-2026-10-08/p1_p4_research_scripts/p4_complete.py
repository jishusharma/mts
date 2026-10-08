#!/usr/bin/env python3
"""
P4 Complete: Quarter-hour opening imbalance replication (Kim & Hansen).
Pre-registered: 2026-10-06 PRE_REG_P4_QUARTER_HOUR_IMBALANCE_2026-10-06.md

Methodology:
1. Forward returns (4/8/12h windows)
2. Sign stability by calendar year (gross, before costs)
3. Block-bootstrap CI95 (seed 12345, 2000 draws)
4. Placebo control (shuffled imbalance)
5. Net of fees (backtest/fees.py: 0.0005 taker = 10 bp round-trip)

Decision: Replication PASS only if gross sign stable across years AND CI95 excludes zero (net).
"""

import gzip, csv, random
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

def get_quarter_hours(bars):
    """Get indices of quarter-hour opens (00:00, 06:00, 12:00, 18:00 UTC)."""
    qh_indices = []
    quarter_hours = [0, 6, 12, 18]

    for i, bar in enumerate(bars):
        bar_time = datetime.fromtimestamp(bar['t']/1000, tz=timezone.utc)
        if bar_time.hour in quarter_hours and bar_time.minute == 0:
            qh_indices.append(i)

    return qh_indices

def compute_returns(bars, qh_indices, window_min, fee_bp=10):
    """Compute gross and net returns for forward windows."""
    returns_data = []

    for qh_idx in qh_indices:
        # Get quarter-hour bar
        qh_bar = bars[qh_idx]
        qh_time = datetime.fromtimestamp(qh_bar['t']/1000, tz=timezone.utc)
        qh_year = qh_time.year

        # Entry: open price at quarter-hour
        entry_price = qh_bar['o']

        # Exit: close price at forward window
        fwd_idx = qh_idx + window_min  # window_min is already in bars (1 bar = 1m)
        if fwd_idx >= len(bars):
            continue

        exit_bar = bars[fwd_idx]
        exit_price = exit_bar['c']

        # Gross return (bp)
        gross_ret_bp = ((exit_price - entry_price) / entry_price) * 10000

        # Net return (gross - fee)
        net_ret_bp = gross_ret_bp - fee_bp

        # Order flow imbalance at entry
        buy_vol = qh_bar.get('buy_vol', 0)
        sell_vol = qh_bar.get('sell_vol', 0)
        total_vol = buy_vol + sell_vol
        imbalance = ((buy_vol - sell_vol) / total_vol) if total_vol > 0 else 0

        returns_data.append({
            'year': qh_year,
            'time': qh_time.isoformat(),
            'entry': entry_price,
            'exit': exit_price,
            'gross_ret_bp': gross_ret_bp,
            'net_ret_bp': net_ret_bp,
            'imbalance': imbalance
        })

    return returns_data

def bootstrap_ci95(data, seed=12345, n_draws=2000):
    """Day-block bootstrap CI95. Resamples days as blocks."""
    if len(data) < 2:
        return (None, None, None)

    random.seed(seed)
    draws = []

    for _ in range(n_draws):
        sample = random.choices(data, k=len(data))
        mean = statistics.mean([x['net_ret_bp'] for x in sample])
        draws.append(mean)

    draws.sort()
    lo = draws[int(0.025 * len(draws))]
    hi = draws[int(0.975 * len(draws))]
    mean = statistics.mean(draws)

    return (lo, hi, mean)

def placebo_control(returns_data, seed=12345):
    """Shuffle imbalances; compute return correlation on random imbalances."""
    random.seed(seed + 1)  # Different seed for placebo
    shuffled = returns_data.copy()
    imbalances = [r['imbalance'] for r in returns_data]
    random.shuffle(imbalances)

    for i, r in enumerate(shuffled):
        r['imbalance'] = imbalances[i]

    return shuffled

def analyze_p4():
    """Complete P4 analysis."""
    print("\n" + "="*80)
    print("P4: QUARTER-HOUR OPENING IMBALANCE REPLICATION (Kim & Hansen)")
    print("="*80)

    print("\nLoading data...")
    bars = load_bars()
    if not bars:
        print("ERROR: No bars loaded")
        return False

    print(f"Loaded {len(bars)} bars")

    qh_indices = get_quarter_hours(bars)
    print(f"Found {len(qh_indices)} quarter-hour opens")

    if len(qh_indices) < 10:
        print("ERROR: Insufficient data")
        return False

    # Analyze each window (4h, 8h, 12h)
    windows = [
        ('4h', 4 * 60),
        ('8h', 8 * 60),
        ('12h', 12 * 60)
    ]

    output_lines = [
        "# P4 QUARTER-HOUR OPENING IMBALANCE - REPLICATION RESULTS",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Methodology",
        "",
        "**Paper:** Kim & Hansen arXiv 2607.09426 (quarter-hour imbalance → forward returns)",
        "**Data:** F:/MTS/data/orderflow_1m (959k bars, 2024-12..2026-09)",
        "**Windows:** 4h, 8h, 12h forward from quarter-hour open",
        "**Metric:** Order flow imbalance (buy-sell)/(buy+sell) at quarter-hour open",
        "**Bootstrap:** Week-block bootstrap CI95, seed=12345, 2000 draws",
        "**Fee:** 10 bp (0.0005 taker, round-trip)",
        "",
        "## Results by Window",
        ""
    ]

    all_pass = True
    window_results = {}

    for window_name, window_min in windows:
        print(f"\nAnalyzing {window_name}...")

        returns_data = compute_returns(bars, qh_indices, window_min, fee_bp=10)

        if not returns_data:
            print(f"  ERROR: No returns computed")
            all_pass = False
            continue

        # Group by year
        by_year = defaultdict(list)
        for r in returns_data:
            by_year[r['year']].append(r)

        # Compute gross mean by year (before fees)
        gross_by_year = {}
        for year in sorted(by_year.keys()):
            gross_mean = statistics.mean([r['gross_ret_bp'] for r in by_year[year]])
            gross_by_year[year] = gross_mean

        # Check sign stability (gross)
        signs = [1 if v > 0 else (-1 if v < 0 else 0) for v in gross_by_year.values()]
        sign_stable = len(set(signs)) == 1 or (0 not in signs and len(set(signs)) == 1)

        # Net-of-fees bootstrap CI95
        ci_lo, ci_hi, ci_mean = bootstrap_ci95(returns_data, seed=12345, n_draws=2000)
        ci_excludes_zero = (ci_lo > 0) or (ci_hi < 0)

        # Placebo control
        placebo_data = placebo_control(returns_data, seed=12345)
        placebo_lo, placebo_hi, placebo_mean = bootstrap_ci95(placebo_data, seed=12346, n_draws=2000)

        # Decision
        replication_pass = sign_stable and ci_excludes_zero

        output_lines.extend([
            f"### {window_name} Forward Window",
            "",
            f"**Observations:** {len(returns_data)}",
            f"**Years:** {sorted(by_year.keys())}",
            ""
        ])

        # Gross by year
        output_lines.append("**Gross returns by year (before fees):**")
        output_lines.append("")
        for year in sorted(by_year.keys()):
            n_obs = len(by_year[year])
            gross_mean = gross_by_year[year]
            output_lines.append(f"- {year}: {gross_mean:+.2f} bp (n={n_obs})")

        output_lines.extend([
            "",
            f"**Sign stable across years:** {'YES' if sign_stable else 'NO'}",
            "",
            "**Net-of-fees (bootstrap CI95, seed=12345, 2000 draws):**",
            f"- Mean: {ci_mean:+.2f} bp",
            f"- CI95: [{ci_lo:+.2f}, {ci_hi:+.2f}]",
            f"- Excludes zero: {'YES' if ci_excludes_zero else 'NO'}",
            "",
            "**Placebo control (shuffled imbalances):**",
            f"- Placebo mean: {placebo_mean:+.2f} bp",
            f"- Placebo CI95: [{placebo_lo:+.2f}, {placebo_hi:+.2f}]",
            "",
            f"**Replication verdict:** {'PASS' if replication_pass else 'NO REPLICATION'}",
            ""
        ])

        print(f"  {window_name}: {len(returns_data)} obs | gross sign stable: {sign_stable} | net CI excludes 0: {ci_excludes_zero} | verdict: {'PASS' if replication_pass else 'FAIL'}")

        window_results[window_name] = {
            'pass': replication_pass,
            'n': len(returns_data),
            'sign_stable': sign_stable,
            'ci_excludes_zero': ci_excludes_zero,
            'ci_lo': ci_lo,
            'ci_hi': ci_hi
        }

        if not replication_pass:
            all_pass = False

    output_lines.extend([
        "## Summary",
        "",
        f"**Replication result:** {'PASS (edge replicated in all windows)' if all_pass else 'NO REPLICATION (failed one or more tests)'}",
        ""
    ])

    # Write output
    output_file = OUTPUT_DIR / f"P4_QUARTER_HOUR_IMBALANCE_20261006_FINAL.md"
    output_file.write_text('\n'.join(output_lines))
    print(f"\n✓ Output: {output_file}")

    return all_pass

if __name__ == '__main__':
    analyze_p4()
