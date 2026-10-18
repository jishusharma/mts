"""Algorithmic evaluation of YouTube and practitioner Pitchfork methodologies on Bitcoin (BTC).

Compares:
1. Standard Andrews Pitchfork (Retail YouTube tutorials / The Trading Manual)
2. Fractal Flow (Volume Profile + Modified Schiff Pitchfork)
3. Operator's Stacked Schiff Pitchforks (SET_362293de1b70_pitchfork.md, 1W spot BTC)
4. Bob Loukas / 4-Year Cycle Chartist (Logarithmic Cycle Pitchfork)
5. Timothy Morge / Patrick Mikula (Algorithmic 80% Rule & Hagopian Failure)

Evaluates each method against historical BTC price swings using PitchforkChannel.
"""

import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from typing import Dict, List, Any
from MyTradingSys.backtest.layers.pitchfork.pitchfork_detector import (
    PitchforkVariant,
    PitchforkPivot,
    PitchforkChannel,
    construct_pitchfork,
)

# Canonical Bitcoin 1W & Macro Swings (2017 - 2026)
# Sources: Binance spot 1W klines & SET_362293de1b70_pitchfork.md
BTC_MACRO_SWINGS = [
    {"date": "2017-12-11", "index": 0, "price": 19798.68, "is_high": True, "label": "2017 Peak"},
    {"date": "2018-12-10", "index": 52, "price": 3122.00, "is_high": False, "label": "2018 Cycle Low"},
    {"date": "2019-06-24", "index": 80, "price": 13880.00, "is_high": True, "label": "2019 Echo High"},
    {"date": "2020-03-16", "index": 118, "price": 3782.00, "is_high": False, "label": "2020 Covid Base"},
    {"date": "2021-04-12", "index": 174, "price": 64854.00, "is_high": True, "label": "2021 Spring High"},
    {"date": "2021-07-19", "index": 188, "price": 29278.00, "is_high": False, "label": "2021 Summer Low"},
    {"date": "2021-11-08", "index": 204, "price": 69000.00, "is_high": True, "label": "2021 ATH Peak"},
    {"date": "2022-11-21", "index": 258, "price": 15476.00, "is_high": False, "label": "2022 Cycle Bottom"},
    {"date": "2023-07-10", "index": 291, "price": 31804.00, "is_high": True, "label": "2023 Summer High"},
    {"date": "2023-09-11", "index": 300, "price": 24901.00, "is_high": False, "label": "2023 Pullback Low"},
    {"date": "2024-03-11", "index": 326, "price": 73777.00, "is_high": True, "label": "2024 Pre-Halving ATH"},
    {"date": "2024-08-05", "index": 347, "price": 49000.00, "is_high": False, "label": "2024 Aug Unwind Low"},
    {"date": "2025-10-06", "index": 408, "price": 126199.63, "is_high": True, "label": "2025 Expansion ATH"},
]


def eval_pitchfork_setup(p0_dict, p1_dict, p2_dict, subsequent_bars: List[Dict[str, float]], variant: PitchforkVariant):
    """Constructs a pitchfork and evaluates bar-by-bar outcome."""
    p0 = PitchforkPivot(index=p0_dict["index"], price=p0_dict["price"], is_high=p0_dict["is_high"])
    p1 = PitchforkPivot(index=p1_dict["index"], price=p1_dict["price"], is_high=p1_dict["is_high"])
    p2 = PitchforkPivot(index=p2_dict["index"], price=p2_dict["price"], is_high=p2_dict["is_high"])

    try:
        pf = PitchforkChannel(p0, p1, p2, variant=variant)
    except Exception as e:
        return {"error": str(e)}

    # Track interaction
    reached_ml = False
    breached_tine_premature = False
    hagopian = False
    bars_to_ml = 0

    for bar in subsequent_bars:
        t = bar["index"]
        res = pf.eval_bar(t, high=bar["high"], low=bar["low"], close=bar["close"])
        if res.reached_ml and not reached_ml:
            reached_ml = True
            bars_to_ml = t - p2.index
        if res.hagopian_triggered:
            hagopian = True
        if not reached_ml and (res.breached_lml if pf.is_ascending() else res.breached_uml):
            breached_tine_premature = True

    return {
        "variant": variant.value,
        "slope": pf.slope,
        "is_ascending": pf.is_ascending(),
        "channel_width": pf.channel_width,
        "reached_ml": reached_ml,
        "bars_to_ml": bars_to_ml if reached_ml else None,
        "premature_breach": breached_tine_premature,
        "hagopian": hagopian,
    }


def run_benchmark():
    """Runs algorithmic evaluation across the YouTube and practitioner profiles."""
    results = {}

    # Setup 1: Cycle 2022-2024 Bull Pitchfork
    # P0: 2022-11 Low ($15,476, index 258)
    # P1: 2023-07 High ($31,804, index 291)
    # P2: 2023-09 Low ($24,901, index 300)
    # Subsequent target: 2024-03 High ($73,777, index 326)
    p0_22 = BTC_MACRO_SWINGS[7]   # 2022-11 Low
    p1_23 = BTC_MACRO_SWINGS[8]   # 2023-07 High
    p2_23 = BTC_MACRO_SWINGS[9]   # 2023-09 Low

    # Synthetic weekly path from index 301 to 330
    bars_23_24 = []
    prices = [
        26500, 27000, 27500, 28000, 30000, 34000, 35000, 37000, 38000, 42000,
        43000, 44000, 42500, 41000, 40000, 43000, 48000, 52000, 57000, 62000,
        66000, 68000, 72000, 73777, 65000, 63000
    ]
    for idx, pr in enumerate(prices):
        t = 301 + idx
        bars_23_24.append({"index": t, "open": pr * 0.99, "high": pr * 1.02, "low": pr * 0.98, "close": pr})

    # Test Standard vs Schiff vs Modified Schiff
    r_standard = eval_pitchfork_setup(p0_22, p1_23, p2_23, bars_23_24, PitchforkVariant.STANDARD)
    r_schiff = eval_pitchfork_setup(p0_22, p1_23, p2_23, bars_23_24, PitchforkVariant.SCHIFF)
    r_modschiff = eval_pitchfork_setup(p0_22, p1_23, p2_23, bars_23_24, PitchforkVariant.MODIFIED_SCHIFF)

    results["2022_2024_bull_run"] = {
        "Standard": r_standard,
        "Schiff (Operator/TradingView)": r_schiff,
        "Modified Schiff (Fractal Flow/MTS)": r_modschiff,
    }

    # Setup 2: Operator's Macro Stacked Schiff Setup (SET_362293de1b70_pitchfork.md)
    # Fork 1: 2020 Covid Base ($3,782, index 118) -> 2021 Peak ($69,000, index 204) -> 2022 Bottom ($15,476, index 258)
    p0_20 = BTC_MACRO_SWINGS[3]   # 2020 Low
    p1_21 = BTC_MACRO_SWINGS[6]   # 2021 Peak
    p2_22 = BTC_MACRO_SWINGS[7]   # 2022 Bottom

    # Path from 2022 to 2024
    bars_macro = []
    prices_macro = [17000, 20000, 23000, 28000, 30000, 26000, 29000, 34000, 42000, 52000, 68000, 73777]
    for idx, pr in enumerate(prices_macro):
        t = 259 + idx * 5
        bars_macro.append({"index": t, "open": pr * 0.98, "high": pr * 1.03, "low": pr * 0.97, "close": pr})

    r_op_std = eval_pitchfork_setup(p0_20, p1_21, p2_22, bars_macro, PitchforkVariant.STANDARD)
    r_op_schiff = eval_pitchfork_setup(p0_20, p1_21, p2_22, bars_macro, PitchforkVariant.SCHIFF)
    r_op_mod = eval_pitchfork_setup(p0_20, p1_21, p2_22, bars_macro, PitchforkVariant.MODIFIED_SCHIFF)

    results["operator_macro_stack"] = {
        "Standard": r_op_std,
        "Schiff (Operator Style)": r_op_schiff,
        "Modified Schiff": r_op_mod,
    }

    return results


if __name__ == "__main__":
    out = run_benchmark()
    import json
    print(json.dumps(out, indent=2))
