"""Multi-Year Bitcoin (BTC) 4-Hour (4H) Pitchfork & Volume Profile Event Study (2020 - 2026).

Executes an exhaustive, non-repainting historical event study on 14,766 4-hour Bitcoin klines.
Evaluates:
1. 4H Swing Pitchfork Geometry across 4 variants:
   - Standard Andrews Pitchfork
   - Schiff Pitchfork
   - Modified Schiff Pitchfork
   - Logarithmic Modified Schiff Pitchfork
2. Anchored Volume Profile (FORMULAS 18.1) Confluence:
   - Unfiltered baseline
   - Value Area Confluence (P2 tine within 70% Value Area [VAL, VAH])
   - POC Confluence (P2 tine within +/-1.5% and +/-0.75% of Point of Control)
3. Entry Execution Modes:
   - Naive Confirmation Close Entry (Market taker at P2 + lookback close)
   - Tine Retest Limit Fill Entry (Resting maker limit order filled at tine touch)
4. Fee & Friction:
   - Standard Binance taker/maker fee schedule + 0.02% slippage hurdle
   - Proves whether Volume Profile confluence and tine limit execution eliminate negative fee drag.
"""

import csv
import datetime
import glob
import math
import os
from pathlib import Path
import sys
from typing import Dict, List, Any, Tuple, Optional

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from MyTradingSys.backtest.layers.pitchfork.pitchfork_detector import (
    PitchforkVariant,
    PitchforkPivot,
    PitchforkChannel,
    LogPitchforkChannel,
    find_pivots_zigzag,
)
from MyTradingSys.backtest.vp_pivot_probe import build_profile

RESEARCH_DIR = REPO_ROOT / "MyTradingSys" / "research" / "pitchfork_2026-10-19"
CACHE_4H_FILE = RESEARCH_DIR / "btc_4h_2020_2026.csv"
RESULTS_CSV = RESEARCH_DIR / "TRIALS_PITCHFORK_4H.csv"


def load_or_aggregate_4h_klines() -> List[Dict[str, Any]]:
    """Loads cached 4H bars or aggregates from raw 1m klines across 2020-2026."""
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)

    if CACHE_4H_FILE.exists():
        bars = []
        with open(CACHE_4H_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                bars.append({
                    "index": idx,
                    "timestamp": int(row["timestamp"]),
                    "datetime": row["datetime"],
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row["volume"]),
                })
        print(f"Loaded {len(bars)} 4H bars from cache: {CACHE_4H_FILE}")
        return bars

    four_h: Dict[int, List[float]] = {}
    print("Aggregating 1m raw klines into 4H OHLCV bars (2020-2026)...")

    # 1. Dev ext 2020-2021
    for fpath in sorted(glob.glob("F:/MTS/data/dev_ext_2019_2021/klines/BTCUSDT-1m-*.csv")):
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) < 6:
                    continue
                try:
                    ts = int(parts[0]) // 14400000 * 14400000
                    o, h, l, c, v = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4]), float(parts[5])
                except ValueError:
                    continue
                if ts not in four_h:
                    four_h[ts] = [o, h, l, c, v]
                else:
                    bar = four_h[ts]
                    if h > bar[1]: bar[1] = h
                    if l < bar[2]: bar[2] = l
                    bar[3] = c
                    bar[4] += v

    # 2. Tom raw 2022-2026
    for fpath in sorted(glob.glob("F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv")):
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) < 6:
                    continue
                try:
                    ts = int(parts[0]) // 14400000 * 14400000
                    o, h, l, c, v = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4]), float(parts[5])
                except ValueError:
                    continue
                if ts not in four_h:
                    four_h[ts] = [o, h, l, c, v]
                else:
                    bar = four_h[ts]
                    if h > bar[1]: bar[1] = h
                    if l < bar[2]: bar[2] = l
                    bar[3] = c
                    bar[4] += v

    sorted_ts = sorted(four_h.keys())
    bars = []
    with open(CACHE_4H_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["index", "timestamp", "datetime", "open", "high", "low", "close", "volume"])
        for idx, ts in enumerate(sorted_ts):
            dt_str = datetime.datetime.fromtimestamp(ts / 1000.0, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            b = four_h[ts]
            writer.writerow([idx, ts, dt_str, b[0], b[1], b[2], b[3], b[4]])
            bars.append({
                "index": idx,
                "timestamp": ts,
                "datetime": dt_str,
                "open": b[0],
                "high": b[1],
                "low": b[2],
                "close": b[3],
                "volume": b[4],
            })

    print(f"Aggregated and cached {len(bars)} 4H bars to {CACHE_4H_FILE}")
    return bars


def simulate_4h_pitchfork_study():
    bars = load_or_aggregate_4h_klines()
    highs = [b["high"] for b in bars]
    lows = [b["low"] for b in bars]

    lookback = 4  # 4 x 4h = 16h pivot confirmation delay
    min_change_pct = 0.03  # 3.0% swing threshold for 4H
    pivots = find_pivots_zigzag(highs, lows, lookback=lookback, min_change_pct=min_change_pct)
    print(f"Total confirmed ZigZag 4H pivots (lookback={lookback}, min_change={min_change_pct*100}%): {len(pivots)}")

    variants = [
        ("Standard_Andrews", PitchforkVariant.STANDARD, False),
        ("Schiff", PitchforkVariant.SCHIFF, False),
        ("Modified_Schiff", PitchforkVariant.MODIFIED_SCHIFF, False),
        ("Log_Modified_Schiff", PitchforkVariant.MODIFIED_SCHIFF, True),
    ]

    filter_modes = [
        ("UNFILTERED", "All confirmed setups without volume gating"),
        ("VA_CONFLUENT", "P2 tine inside [VAL, VAH] of foundational P0->P2 swing"),
        ("POC_1.5PCT", "P2 tine within +/-1.5% of P0->P2 Volume Profile POC"),
        ("POC_0.75PCT", "P2 tine within +/-0.75% of P0->P2 Volume Profile POC"),
    ]

    exec_modes = [
        ("TINE_LIMIT_RETEST", 0.0009),   # 0.02% maker entry + 0.05% taker exit + 0.02% slippage = 0.09%
        ("CONFIRM_CLOSE_MKT", 0.0012),   # 0.05% taker entry + 0.05% taker exit + 0.02% slippage = 0.12%
    ]

    results_table = []
    num_triplets = len(pivots) - 2

    for var_name, var_enum, use_log in variants:
        for f_name, f_desc in filter_modes:
            for exec_name, fee in exec_modes:
                trade_records = []
                total_qualified = 0

                for i in range(num_triplets):
                    p0, p1, p2 = pivots[i], pivots[i + 1], pivots[i + 2]
                    if p0.is_high == p1.is_high or p1.is_high == p2.is_high:
                        continue

                    confirm_idx = p2.index + lookback
                    if confirm_idx >= len(bars):
                        continue

                    # Volume Profile computation on P0 -> P2 swing (FORMULAS 18.1)
                    sub = bars[min(p0.index, p2.index) : max(p0.index, p2.index) + 1]
                    if len(sub) < 2:
                        continue
                    vp = build_profile([b["low"] for b in sub], [b["high"] for b in sub], [b["volume"] for b in sub], w=10.0)
                    if not vp:
                        continue

                    poc = vp["poc_price"]
                    val, vah = vp["val"], vp["vah"]
                    tine_price = p2.price

                    # Gating logic
                    if f_name == "VA_CONFLUENT":
                        if not (val <= tine_price <= vah):
                            continue
                    elif f_name == "POC_1.5PCT":
                        if abs(tine_price - poc) / poc > 0.015:
                            continue
                    elif f_name == "POC_0.75PCT":
                        if abs(tine_price - poc) / poc > 0.0075:
                            continue

                    try:
                        if use_log:
                            pf = LogPitchforkChannel(p0, p1, p2, variant=var_enum)
                        else:
                            pf = PitchforkChannel(p0, p1, p2, variant=var_enum)
                    except Exception:
                        continue

                    total_qualified += 1

                    # 4H evaluation window: up to 60 bars (10 days) post-confirmation
                    eval_window = bars[confirm_idx : min(len(bars), confirm_idx + 60)]
                    if not eval_window:
                        continue

                    is_long = (not p2.is_high)
                    filled = False
                    entry_price = 0.0
                    fill_idx = 0
                    reached_ml = False
                    breached_tine = False
                    pnl = 0.0

                    if exec_name == "CONFIRM_CLOSE_MKT":
                        # Immediate fill at confirmation bar close
                        filled = True
                        entry_price = eval_window[0]["close"]
                        for b in eval_window:
                            t = b["index"]
                            res = pf.eval_bar(t, high=b["high"], low=b["low"], close=b["close"])
                            if res.reached_ml:
                                reached_ml = True
                                exit_price = res.ml_value
                                raw_ret = (exit_price - entry_price) / entry_price if is_long else (entry_price - exit_price) / entry_price
                                pnl = raw_ret - fee
                                break
                            if not reached_ml:
                                if pf.is_ascending() and res.breached_lml:
                                    breached_tine = True
                                    pnl = -0.020 - fee  # 2.0% stop
                                    break
                                elif not pf.is_ascending() and res.breached_uml:
                                    breached_tine = True
                                    pnl = -0.020 - fee
                                    break
                        if not reached_ml and not breached_tine:
                            last_c = eval_window[-1]["close"]
                            raw_ret = (last_c - entry_price) / entry_price if is_long else (entry_price - last_c) / entry_price
                            pnl = raw_ret - fee

                    elif exec_name == "TINE_LIMIT_RETEST":
                        # Resting limit order at active tine
                        for w_idx, b in enumerate(eval_window):
                            t = b["index"]
                            tine_val = pf.get_lml(t) if is_long else pf.get_uml(t)
                            if not filled:
                                if b["low"] <= tine_val <= b["high"]:
                                    filled = True
                                    entry_price = tine_val
                                    fill_idx = w_idx
                            else:
                                res = pf.eval_bar(t, high=b["high"], low=b["low"], close=b["close"])
                                if res.reached_ml:
                                    reached_ml = True
                                    exit_price = res.ml_value
                                    raw_ret = (exit_price - entry_price) / entry_price if is_long else (entry_price - exit_price) / entry_price
                                    pnl = raw_ret - fee
                                    break
                                # Structural stop: 1.5% beyond tine fill
                                if is_long and b["low"] <= entry_price * 0.985:
                                    breached_tine = True
                                    pnl = -0.015 - fee
                                    break
                                elif not is_long and b["high"] >= entry_price * 1.015:
                                    breached_tine = True
                                    pnl = -0.015 - fee
                                    break
                        if filled and not reached_ml and not breached_tine:
                            last_c = eval_window[-1]["close"]
                            raw_ret = (last_c - entry_price) / entry_price if is_long else (entry_price - last_c) / entry_price
                            pnl = raw_ret - fee

                    if filled:
                        trade_records.append({
                            "reached_ml": reached_ml,
                            "breached_tine": breached_tine,
                            "pnl": pnl,
                        })

                # Compute performance metrics
                n_filled = len(trade_records)
                if n_filled > 0:
                    wins = [r for r in trade_records if r["pnl"] > 0]
                    losses = [r for r in trade_records if r["pnl"] <= 0]
                    wr = len(wins) / n_filled * 100.0
                    ml_rate = sum(1 for r in trade_records if r["reached_ml"]) / n_filled * 100.0
                    breach_rate = sum(1 for r in trade_records if r["breached_tine"]) / n_filled * 100.0
                    mean_pnl = sum(r["pnl"] for r in trade_records) / n_filled * 100.0
                    tot_win_pnl = sum(r["pnl"] for r in wins)
                    tot_loss_pnl = abs(sum(r["pnl"] for r in losses)) if losses else 0.0001
                    pf_ratio = tot_win_pnl / tot_loss_pnl if tot_loss_pnl > 0 else 999.0
                    avg_win = (tot_win_pnl / len(wins) * 100.0) if wins else 0.0
                    avg_loss = (tot_loss_pnl / len(losses) * 100.0) if losses else 0.0
                else:
                    wr = ml_rate = breach_rate = mean_pnl = pf_ratio = avg_win = avg_loss = 0.0

                row = {
                    "variant": var_name,
                    "filter": f_name,
                    "execution": exec_name,
                    "qualified_setups": total_qualified,
                    "filled_trades": n_filled,
                    "win_rate_pct": round(wr, 2),
                    "ml_reach_rate_pct": round(ml_rate, 2),
                    "breach_rate_pct": round(breach_rate, 2),
                    "mean_net_pnl_pct": round(mean_pnl, 2),
                    "profit_factor": round(pf_ratio, 2),
                    "avg_win_pct": round(avg_win, 2),
                    "avg_loss_pct": round(avg_loss, 2),
                }
                results_table.append(row)

    # Print summary
    print("\n" + "=" * 105)
    print("4-HOUR BITCOIN PITCHFORK & VOLUME PROFILE EVENT STUDY (2020 - 2026)")
    print("=" * 105)
    header = "%-19s | %-12s | %-18s | %-5s | %-5s | %-6s | %-7s | %-8s | %-5s" % (
        "Variant", "Filter", "Execution", "Setups", "Fills", "WR%", "ML_Reach", "MeanNet%", "PF"
    )
    print(header)
    print("-" * 105)
    for r in results_table:
        print("%-19s | %-12s | %-18s | %-6d | %-5d | %5.1f%% | %6.1f%%  | %+7.2f%% | %4.2f" % (
            r["variant"],
            r["filter"],
            r["execution"],
            r["qualified_setups"],
            r["filled_trades"],
            r["win_rate_pct"],
            r["ml_reach_rate_pct"],
            r["mean_net_pnl_pct"],
            r["profit_factor"],
        ))
    print("=" * 105)

    # Write results CSV
    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "variant", "filter", "execution", "qualified_setups", "filled_trades",
            "win_rate_pct", "ml_reach_rate_pct", "breach_rate_pct",
            "mean_net_pnl_pct", "profit_factor", "avg_win_pct", "avg_loss_pct"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results_table)
    print(f"\nSaved structured trial results to: {RESULTS_CSV}")

    return results_table


if __name__ == "__main__":
    simulate_4h_pitchfork_study()
