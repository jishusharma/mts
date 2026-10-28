"""
MyTradingSys/research/positioning_c1_2026-10/count_power.py

Count-only check of candidate C1 (funding_cvd_fade, NO-SOURCE research test, VISION exception 2)
on the DEV window 2022-01..2024-06.
NO net P&L is computed; VALIDATION (2024-07..2025-06) and HOLDOUT (2025-07+) are NEVER loaded.

Reports per cell of run_t055.c1_grid():
- N events, events per month, fire rate (events per 1000 bars)
- per-year counts (2022, 2023, 2024 DEV)
- gross mean move at 4/16/48 bars vs 2x 0.12% round-trip cost (gate 0b)
- N and MDE (power_mde.py), with INCONCLUSIVE in advance where N < 100
"""

import argparse
import csv
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from MyTradingSys.backtest.layers.positioning.funding_cvd_fade import (
    funding_cvd_fade_events,
)
from MyTradingSys.backtest.layers.run_t055 import c1_grid
from MyTradingSys.backtest.layers.runner import forward_return_stats
from MyTradingSys.backtest.power_mde import power_mde

# DEV window: 2022-01-01 00:00:00 UTC to 2024-06-30 23:59:59 UTC
# CUTOFF_MS is the first millisecond of VALIDATION: 2024-07-01 00:00:00 UTC
CUTOFF_MS = int(datetime(2024, 7, 1, tzinfo=timezone.utc).timestamp() * 1000)
DEV_START_MS = int(datetime(2022, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
DEV_MONTHS = 30.0  # Jan 2022 - Jun 2024 = 30 full calendar months

# Gate 0b cost threshold: 2 x 0.12% round trip = 0.24% (24 bps)
RT_COST_PCT = 0.0012  # 10 bps fee + 2 bps slippage
GATE_0B_THRESHOLD = 2 * RT_COST_PCT  # 0.0024 = 0.24%

REGISTRY_PATH = REPO / "MyTradingSys" / "backtest" / "layers" / "timeframe" / "registry.json"


def validate_dev_bars(bars):
    """Refuse any bar with open timestamp at or after CUTOFF_MS (2024-07-01)."""
    for b in bars:
        t = b["t"]
        if t >= CUTOFF_MS:
            dt_str = datetime.fromtimestamp(t / 1000, tz=timezone.utc).isoformat()
            raise ValueError(
                f"bar open {t} ({dt_str}) >= 2024-07-01 refused (VALIDATION/HOLDOUT sealed)"
            )


def load_dev_1m_klines(klines_dir, cutoff_ms=CUTOFF_MS):
    """
    Load 1m klines from CSV files, strictly enforcing the DEV window (2022-01..2024-06).
    Any bar at or after cutoff_ms raises ValueError.
    """
    p = Path(klines_dir)
    if (p / "klines").exists():
        p = p / "klines"

    csv_files = sorted(p.glob("BTCUSDT-1m-*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No BTCUSDT 1m kline files found in {p}")

    bars = []
    for f in csv_files:
        # File name convention: BTCUSDT-1m-YYYY-MM.csv or BTCUSDT-1m-YYYY-MM-DD.csv
        parts = f.stem.split("-")
        try:
            year, month = int(parts[2]), int(parts[3])
        except (IndexError, ValueError):
            continue

        # Skip files strictly outside DEV range (2022-01 .. 2024-06)
        if (year, month) < (2022, 1) or (year, month) > (2024, 6):
            continue

        with open(f, newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            first_row = next(reader, None)
            if first_row is None:
                continue
            has_header = not first_row[0].isdigit()
            if not has_header:
                rows = [first_row] + list(reader)
            else:
                rows = list(reader)

            for row in rows:
                if not row or not row[0]:
                    continue
                t = int(float(row[0]))
                if t >= cutoff_ms:
                    raise ValueError(
                        f"bar open {t} >= 2024-07-01 refused (VALIDATION/HOLDOUT sealed): {f.name}"
                    )
                if t < DEV_START_MS:
                    continue

                bars.append({
                    "t": t,
                    "o": float(row[1]),
                    "h": float(row[2]),
                    "l": float(row[3]),
                    "c": float(row[4]),
                    "v": float(row[5]),
                    "tbv": float(row[9]),
                })

    bars.sort(key=lambda b: b["t"])
    validate_dev_bars(bars)
    return bars


def load_dev_funding(funding_dir, cutoff_ms=CUTOFF_MS):
    """
    Load funding rates from 2020-01 onwards up to cutoff_ms.
    """
    p = Path(funding_dir)
    if (p / "fundingRate").exists():
        p = p / "fundingRate"

    csv_files = sorted(p.glob("BTCUSDT-fundingRate-*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No funding rate CSV files found in {p}")

    rates = []
    for f in csv_files:
        parts = f.stem.split("-")
        try:
            year, month = int(parts[2]), int(parts[3])
        except (IndexError, ValueError):
            continue
        # Only up to 2024-06
        if (year, month) > (2024, 6):
            continue

        with open(f, newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            first_row = next(reader, None)
            if first_row is None:
                continue
            has_header = not first_row[0].isdigit()
            rows = list(reader) if has_header else [first_row] + list(reader)

            for row in rows:
                if not row or not row[0]:
                    continue
                t = int(row[0])
                if t >= cutoff_ms:
                    continue
                rate = float(row[2])
                rates.append((t, rate))

    rates.sort(key=lambda x: x[0])
    return rates


def build_15m_dev_bars(bars_1m, registry_path=REGISTRY_PATH):
    """Resample 1m bars to 15m with TBV delta preservation."""
    from MyTradingSys.backtest.layers.timeframe.tf_resample import bucket_start, resample

    reg = json.loads(Path(registry_path).read_text(encoding="utf-8"))
    bars_15m = resample(bars_1m, "15m", reg)

    tbv = {}
    for b in bars_1m:
        s = bucket_start(b["t"], "15m", reg)
        tbv[s] = tbv.get(s, 0.0) + b.get("tbv", 0.0)

    for b in bars_15m:
        b["tbv"] = tbv.get(b["t"], 0.0)

    # Filter to only bars fully closed within DEV
    bars_15m = [b for b in bars_15m if b["t"] + 15 * 60 * 1000 <= CUTOFF_MS]
    validate_dev_bars(bars_15m)
    return bars_15m


def count_events_for_cell(bars, funding, params):
    """Run funding_cvd_fade_events for a specific parameter cell and return event count."""
    events = funding_cvd_fade_events(bars, funding, **params)
    return len(events)


def evaluate_power_verdict(n):
    """Evaluate whether trade count meets the N >= 100 power threshold."""
    if n < 100:
        return "INCONCLUSIVE (N < 100)"
    return "POWERED (N >= 100)"


def compute_cell_metrics(bars, funding, params, horizons=(4, 16, 48)):
    """
    Compute full metrics for one grid cell:
    - N, fire rate, monthly rate, yearly counts
    - gross mean move at 4/16/48 bars vs 2 x 0.12% (gate 0b)
    - MDE with power_mde.py
    """
    events = funding_cvd_fade_events(bars, funding, **params)
    n = len(events)

    fire_rate_per_1000 = (n / len(bars)) * 1000.0 if bars else 0.0
    events_per_month = n / DEV_MONTHS

    # Yearly counts
    yearly = {2022: 0, 2023: 0, 2024: 0}
    for e in events:
        t_event = bars[e["i"]]["t"]
        yr = datetime.fromtimestamp(t_event / 1000, tz=timezone.utc).year
        if yr in yearly:
            yearly[yr] += 1

    # Gross forward returns
    closes = [b["c"] for b in bars]
    gross_stats = {}
    if events:
        fr = forward_return_stats(
            [{"i": e["i"], "side": e["side"]} for e in events], closes, horizons=horizons
        )
        for h in horizons:
            mean_ret = fr[h]["mean_return"]
            hit = fr[h]["hit_rate"]
            gate_0b = (mean_ret is not None) and (mean_ret >= GATE_0B_THRESHOLD)
            gross_stats[h] = {
                "mean_gross": mean_ret,
                "hit_rate": hit,
                "gate_0b_pass": gate_0b,
            }
    else:
        for h in horizons:
            gross_stats[h] = {
                "mean_gross": None,
                "hit_rate": None,
                "gate_0b_pass": False,
            }

    # Power and MDE via power_mde.py
    # Fixed cost in R = RT fee (0.12%) / per-trade noise (~1.31% per HOME_FIT_AUDIT_POSITIONING.md:59) ~= 0.0916 R
    # Under standard symmetric RR = 1.0, breakeven p0 = (1 + 0.0916) / 2 = 0.5458
    status = evaluate_power_verdict(n)
    cost_r = 0.0916
    rr = 1.0
    p0 = (1.0 + cost_r) / (rr + 1.0)

    if n > 0:
        pm = power_mde(p0, rr, cost_r, n)
        mde_net_r = pm["mde_net_r"]
        trades_80 = pm["trades_for_80_power"]
        # MDE in % move (using ~1.31% per-trade noise unit)
        mde_pct = mde_net_r * 0.0131
    else:
        mde_net_r = float("inf")
        trades_80 = float("inf")
        mde_pct = float("inf")

    return {
        "params": params,
        "n": n,
        "events_per_month": events_per_month,
        "fire_rate_per_1000": fire_rate_per_1000,
        "yearly_counts": yearly,
        "gross_stats": gross_stats,
        "mde_net_r": mde_net_r,
        "mde_pct": mde_pct,
        "trades_for_80_power": trades_80,
        "status": status,
    }


def run_all_cells(bars, funding, grid=None, horizons=(4, 16, 48)):
    """Run all 36 cells of C1 grid."""
    if grid is None:
        grid = c1_grid()
    results = []
    for p in grid:
        res = compute_cell_metrics(bars, funding, p, horizons=horizons)
        results.append(res)
    return results


def format_table(results):
    """Format markdown table of results."""
    lines = [
        "| lookback | n_div | hi/lo | div | N | per mo | /1000b | 2022 | 2023 | 2024 | gross 4b | gross 16b | gross 48b | gate 0b (48b) | MDE net R | MDE % | status |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        p = r["params"]
        lb = p["lookback"]
        nd = p["n"]
        hilo = f"{int(p['hi']*100)}/{int(p['lo']*100)}"
        ud = "yes" if p["use_divergence"] else "no"
        n = r["n"]
        mo = f"{r['events_per_month']:.1f}"
        fr = f"{r['fire_rate_per_1000']:.2f}"
        y22 = r["yearly_counts"][2022]
        y23 = r["yearly_counts"][2023]
        y24 = r["yearly_counts"][2024]

        def _fg(h):
            g = r["gross_stats"][h]["mean_gross"]
            return f"{g*100:.3f}%" if g is not None else "n/a"

        g4 = _fg(4)
        g16 = _fg(16)
        g48 = _fg(48)
        gate_pass = "PASS" if r["gross_stats"][48]["gate_0b_pass"] else "FAIL"

        mde_r = f"{r['mde_net_r']:.3f}" if not math.isinf(r["mde_net_r"]) else "inf"
        mde_p = f"{r['mde_pct']*100:.3f}%" if not math.isinf(r["mde_pct"]) else "inf"
        st = r["status"]

        lines.append(
            f"| {lb} | {nd} | {hilo} | {ud} | {n} | {mo} | {fr} | {y22} | {y23} | {y24} | {g4} | {g16} | {g48} | {gate_pass} | {mde_r} | {mde_p} | {st} |"
        )
    return "\n".join(lines)


def resolve_paths(args):
    # Locate klines
    klines_candidates = [
        Path(args.klines) if args.klines else None,
        REPO / "Dumps" / "backtest" / "raw_1m_2022",
        Path("C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/Dumps/backtest/raw_1m_2022"),
    ]
    klines_path = next((p for p in klines_candidates if p and p.exists()), None)
    if not klines_path:
        raise FileNotFoundError("Could not find raw_1m_2022 klines directory")

    # Locate funding
    funding_candidates = [
        Path(args.funding) if args.funding else None,
        REPO / "Dumps" / "backtest" / "raw_fund",
        Path("C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/Dumps/backtest/raw_fund"),
    ]
    funding_path = next((p for p in funding_candidates if p and p.exists()), None)
    if not funding_path:
        raise FileNotFoundError("Could not find raw_fund funding directory")

    return klines_path, funding_path


def main(argv=None):
    parser = argparse.ArgumentParser(description="Positioning C1 DEV count and power analysis")
    parser.add_argument("--klines", default=None, help="Path to raw_1m_2022 klines")
    parser.add_argument("--funding", default=None, help="Path to raw_fund funding directory")
    parser.add_argument("--out-json", default=None, help="Path to write JSON output")
    args = parser.parse_args(argv)

    klines_path, funding_path = resolve_paths(args)
    print(f"Loading DEV 1m klines from {klines_path}...", file=sys.stderr)
    bars_1m = load_dev_1m_klines(klines_path)
    print(f"Loaded {len(bars_1m)} 1m bars.", file=sys.stderr)

    print(f"Resampling to 15m bars...", file=sys.stderr)
    bars_15m = build_15m_dev_bars(bars_1m)
    print(f"Built {len(bars_15m)} 15m bars.", file=sys.stderr)

    print(f"Loading funding from {funding_path}...", file=sys.stderr)
    funding = load_dev_funding(funding_path)
    print(f"Loaded {len(funding)} funding records.", file=sys.stderr)

    print(f"Running 36 grid cells of C1...", file=sys.stderr)
    grid = c1_grid()
    results = run_all_cells(bars_15m, funding, grid)

    table_md = format_table(results)
    print("\n" + table_md)

    if args.out_json:
        out_p = Path(args.out_json)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
        print(f"Wrote results to {out_p}", file=sys.stderr)

    return results


if __name__ == "__main__":
    main()
