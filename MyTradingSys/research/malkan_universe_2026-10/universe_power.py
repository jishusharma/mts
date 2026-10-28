"""Universe size, event counts, asset-years, and power/MDE calculations for Malkan Indian equity setups.

Computes:
1. Exact events needed for +0.10 R net at 80% power using power_mde.py (reproducing EVENT_COUNTS.md 1,655-event figure).
2. Asset-years needed for each Malkan setup from EVENT_COUNTS DEV rates (BTC rate, labelled OURS).
3. Expected N, MDE, and power verdicts for universes of 50, 100, and 500 stocks across multi-year horizons (5y, 10y, 15y, 20y).
4. Pre-registered INCONCLUSIVE in advance markers where expected N < 100.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from MyTradingSys.backtest.power_mde import power_mde

TARGET_NET_R = 0.10
RR = 2.0
FEE_RT = 2 * 0.0005  # Deribit taker fee 0.10% (fees.py:23), standard conservative cost anchor

# SOURCED: EVENT_COUNTS.md:26-38 (BTCUSDT DEV 2510 daily bars, 358 weekly bars)
# Calendar duration: 2510 / 365.25 = 6.8720 calendar years
# Equity trading days duration: 2510 / 250 = 10.040 equity trading years
DEV_BARS_1D = 2510
DEV_BARS_1W = 358
DEV_YEARS_CALENDAR = 2510.0 / 365.25
DEV_YEARS_TRADING_DAYS = 2510.0 / 250.0

ROWS_DEF = [
    {
        "name": "KR-S1 1d (anchor)",
        "tf": "1d",
        "bars": DEV_BARS_1D,
        "n": 278,
        "stop_pct": 0.041,
        "cost_r": 0.024,
        "filter": "zone twice-turned (pivot k=3) + hammer/engulf/doji/star, no trend leg",
    },
    {
        "name": "MAL-2 1d",
        "tf": "1d",
        "bars": DEV_BARS_1D,
        "n": 7,
        "stop_pct": 0.045,
        "cost_r": 0.022,
        "filter": "weekly+monthly RSI>60 gate, daily RSI support event at 60 (tol 2)",
    },
    {
        "name": "MAL-5 1d",
        "tf": "1d",
        "bars": DEV_BARS_1D,
        "n": 25,
        "stop_pct": 0.063,
        "cost_r": 0.016,
        "filter": "gate, daily RSI close in 58..62, green candle; order over high, stop under 3-bar low",
    },
    {
        "name": "MAL-10 1d",
        "tf": "1d",
        "bars": DEV_BARS_1D,
        "n": 6,
        "stop_pct": 0.052,
        "cost_r": 0.019,
        "filter": "gate, daily RSI support event at 40 (tol 2) [host 5-star variant, extra]",
    },
    {
        "name": "MAL-17 1d",
        "tf": "1d",
        "bars": DEV_BARS_1D,
        "n": 35,
        "stop_pct": 0.036,
        "cost_r": 0.027,
        "filter": "bullish divergence 3-10 bars close to close + confirming candle",
    },
    {
        "name": "MAL-16 1d",
        "tf": "1d",
        "bars": DEV_BARS_1D,
        "n": 42,
        "stop_pct": 0.036,
        "cost_r": 0.028,
        "filter": "bearish divergence 3-10 bars close to close + confirming candle",
    },
    {
        "name": "MAL-17 1w",
        "tf": "1w",
        "bars": DEV_BARS_1W,
        "n": 3,
        "stop_pct": 0.097,
        "cost_r": 0.010,
        "filter": "bullish divergence 3-10 bars close to close + confirming candle",
    },
    {
        "name": "MAL-16 1w",
        "tf": "1w",
        "bars": DEV_BARS_1W,
        "n": 8,
        "stop_pct": 0.158,
        "cost_r": 0.006,
        "filter": "bearish divergence 3-10 bars close to close + confirming candle",
    },
]


def equity_rate(row):
    """Events per equity asset-year (OURS): daily rows scale by bars, 250 equity trading days a year, not BTC's 365;
    weekly rows scale by weeks (52 a year both ways), so the calendar rate is right for them."""
    return row["n"] / (DEV_YEARS_TRADING_DAYS if row["tf"] == "1d" else DEV_YEARS_CALENDAR)


def events_for_target_net_r(target_net_r=TARGET_NET_R, rr=RR, cost_r=0.024):
    """Compute trades needed for 80% power at target net R."""
    p_target = (target_net_r + 1.0 + cost_r) / (rr + 1.0)
    res = power_mde(p_target, rr, cost_r, n=100)
    return res["trades_for_80_power"]


def evaluate_universe_cell(n_events, rr=RR, cost_r=0.016):
    """Evaluate power, MDE, and verdict for a specific sample size N.
    
    If N < 100, verdict is INCONCLUSIVE in advance per Checklist Item 10 & Gate 0e.
    """
    if n_events < 2:
        return {
            "n": n_events,
            "mde_net_r": None,
            "verdict": "INCONCLUSIVE",
            "inconclusive_in_advance": True,
        }
    p0 = (1.0 + cost_r) / (rr + 1.0)
    res = power_mde(p0, rr, cost_r, n_events)
    mde = res["mde_net_r"]
    
    inconclusive = n_events < 100
    if inconclusive:
        verdict = "INCONCLUSIVE"
    elif mde <= 0.30:
        verdict = "ENOUGH"
    elif mde <= 0.60:
        verdict = "MARGINAL"
    else:
        verdict = "THIN"
        
    return {
        "n": n_events,
        "mde_net_r": mde,
        "verdict": verdict,
        "inconclusive_in_advance": inconclusive,
    }


def compute_asset_years_needed(row_name, target_net_r=TARGET_NET_R):
    """Compute asset-years needed to achieve 80% power at target net R."""
    r = next((x for x in ROWS_DEF if x["name"] == row_name), None)
    if not r:
        raise ValueError(f"Unknown row: {row_name}")
    
    trades_needed = events_for_target_net_r(target_net_r, RR, r["cost_r"])
    rate_cal = r["n"] / DEV_YEARS_CALENDAR
    rate_td = r["n"] / DEV_YEARS_TRADING_DAYS
    
    ay_cal = trades_needed / rate_cal if rate_cal > 0 else float("inf")
    ay_td = trades_needed / rate_td if rate_td > 0 else float("inf")
    
    return {
        "name": row_name,
        "trades_needed": trades_needed,
        "rate_per_cal_year": rate_cal,
        "rate_per_trading_year": rate_td,
        "asset_years_calendar": ay_cal,
        "asset_years_trading_days": ay_td,
        "asset_years_equity": trades_needed / equity_rate(r),
    }


def compute_malkan_power_table():
    """Build the base power and rates table for all setups."""
    rows = []
    for r in ROWS_DEF:
        trades_needed = events_for_target_net_r(TARGET_NET_R, RR, r["cost_r"])
        p0 = (1.0 + r["cost_r"]) / (RR + 1.0)
        mde_btc = power_mde(p0, RR, r["cost_r"], r["n"])["mde_net_r"]
        
        rate_cal = r["n"] / DEV_YEARS_CALENDAR
        rate_td = r["n"] / DEV_YEARS_TRADING_DAYS
        ay_cal = trades_needed / rate_cal
        ay_td = trades_needed / rate_td
        
        rows.append({
            "name": r["name"],
            "tf": r["tf"],
            "bars": r["bars"],
            "n": r["n"],
            "stop_pct": r["stop_pct"],
            "cost_r": r["cost_r"],
            "mde_net_r_btc": mde_btc,
            "events_for_80pct_power": trades_needed,
            "rate_cal": rate_cal,
            "rate_td": rate_td,
            "asset_years_cal": ay_cal,
            "asset_years_td": ay_td,
            "asset_years_equity": trades_needed / equity_rate(r),
        })
    return rows


def compute_universe_grid(universe_sizes=(50, 100, 500), years_list=(5, 10, 15, 20)):
    """Compute grid of expected N, MDE, and verdict for combinations of universe size and years."""
    table = []
    for r in ROWS_DEF:
        if r["name"].startswith("KR-S1"):
            continue
        rate = equity_rate(r)  # events per equity asset-year (250 td for daily, 52 weeks for weekly)
        row_res = {"name": r["name"], "tf": r["tf"], "rate": rate, "cells": {}}
        for u in universe_sizes:
            for y in years_list:
                ay = u * y
                expected_n = int(round(ay * rate))
                eval_res = evaluate_universe_cell(expected_n, RR, r["cost_r"])
                row_res["cells"][(u, y)] = eval_res
        table.append(row_res)
    return table


def inconclusive_cells(scenarios=((50, 1), (100, 1), (500, 1), (50, 2), (100, 2), (500, 2), (1, 10))):
    """Cells with expected N < 100 (INCONCLUSIVE in advance), (universe size, years) scenarios."""
    out = []
    for r in ROWS_DEF:
        if r["name"].startswith("KR-S1"):
            continue
        for u, y in scenarios:
            n = int(round(u * y * equity_rate(r)))
            ev = evaluate_universe_cell(n, RR, r["cost_r"])
            if ev["inconclusive_in_advance"]:
                out.append((u, y, r["name"], r["tf"], n, ev["mde_net_r"]))
    return out


def format_inconclusive_table():
    lines = ["| Scenario | Setup | TF | Expected N | Detectable MDE | Pre-registered verdict |", "|---|---|---|---|---|---|"]
    for u, y, name, tf, n, mde in inconclusive_cells():
        scope = "Single stock, 10 years" if u == 1 else f"{y} year{'s' if y > 1 else ''} on {u} stocks"
        m = f"{mde:.2f} R" if mde is not None else "-"
        lines.append(f"| {scope} | {name} | {tf} | {n} | {m} | **INCONCLUSIVE IN ADVANCE** |")
    return chr(10).join(lines)


def format_markdown_tables():
    """Format markdown tables for UNIVERSE_POWER.md."""
    base_table = compute_malkan_power_table()
    lines = []
    
    # 1. Base rates table
    lines.append("### Table 1: Setup Event Rates and Asset-Years Needed for +0.10 R Net (80% Power)")
    lines.append("")
    lines.append("| Setup | TF | Description / Pre-filter (OURS) | BTC DEV n | BTC Stop | Cost R | BTC MDE | Events for +0.10 R | Rate (events / asset-yr, cal) | Asset-Years Needed (cal) | Asset-Years Needed (250 td) |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in base_table:
        ev = round(r["events_for_80pct_power"])
        ay_cal = round(r["asset_years_cal"])
        ay_td = round(r["asset_years_td"])
        lines.append(
            f"| {r['name']} | {r['tf']} | {r['name'].split()[0]} rule stand-in | {r['n']} | "
            f"{r['stop_pct']*100:.1f}% | {r['cost_r']:.3f} | {r['mde_net_r_btc']:.2f} R | {ev} | "
            f"{r['rate_cal']:.2f} | {ay_cal} | {ay_td} |"
        )
    lines.append("")
    
    # 2. Years needed per universe size table
    lines.append("### Table 2: Calendar Years of History Needed for +0.10 R Net (80% Power) per Universe Size")
    lines.append("")
    lines.append("| Setup | TF | Events Needed | Asset-Years Needed (equity basis) | Universe 50 (Nifty 50) | Universe 100 (Nifty 100) | Universe 500 (Nifty 500) | Single Asset (BTC / 1 stock) |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in base_table:
        if r["name"].startswith("KR-S1"):
            continue
        ev = round(r["events_for_80pct_power"])
        ay_cal = round(r["asset_years_equity"])
        y50 = ay_cal / 50.0
        y100 = ay_cal / 100.0
        y500 = ay_cal / 500.0
        y1 = ay_cal / 1.0
        lines.append(
            f"| {r['name']} | {r['tf']} | {ev} | {ay_cal} | "
            f"{y50:.1f} years | {y100:.1f} years | {y500:.2f} years | {y1:.1f} years |"
        )
    lines.append("")
    
    # 3. Grid for Universes 50, 100, 500 across 5y, 10y, 15y, 20y
    lines.append("### Table 3: Expected N, Detectable MDE, and Pre-Registered Power Verdict")
    lines.append("")
    lines.append("| Setup | TF | Universe | 5 Years (N, MDE, Verdict) | 10 Years (N, MDE, Verdict) | 15 Years (N, MDE, Verdict) | 20 Years (N, MDE, Verdict) |")
    lines.append("|---|---|---|---|---|---|---|")
    grid = compute_universe_grid()
    for row in grid:
        for u in (50, 100, 500):
            cells_str = []
            for y in (5, 10, 15, 20):
                c = row["cells"][(u, y)]
                mde_str = f"{c['mde_net_r']:.2f} R" if c["mde_net_r"] is not None else "-"
                verdict_str = f"**{c['verdict']}**" if c["verdict"] in ("ENOUGH", "INCONCLUSIVE") else c["verdict"]
                cells_str.append(f"N={c['n']}, {mde_str} ({verdict_str})")
            lines.append(f"| {row['name']} | {row['tf']} | {u} stocks | " + " | ".join(cells_str) + " |")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    print(format_markdown_tables())
    print(format_inconclusive_table())

