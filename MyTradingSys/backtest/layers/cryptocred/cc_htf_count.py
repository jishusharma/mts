"""
MyTradingSys/backtest/layers/cryptocred/cc_htf_count.py

COUNT-ONLY check (no P&L, no exits simulated) for CryptoCred setups on the trader's real
timeframes (4h, 1d, plus 1h as the reference the existing runner already uses): number of
signals, number of resting limits that would fill (price trades through the level by one tick on
1m bars, same rule as run_cc_setups.find_limit_fill), fire rate per month, and power/MDE via
backtest/power_mde.py. DEV window only: 2022-01-01 .. 2024-06-30 (repo split; VALIDATION and
HOLDOUT are never loaded: bars are cut at DEV_END_MS before any signal is computed).

Signals come from run_cc_setups.SETUPS with their CURRENT defaults, so the 1h count equals the
existing runner's n_signals on the same bars (tested).
"""
import argparse
import json
import os
import statistics
import sys
from pathlib import Path

REPO = Path(os.environ.get("MTS_REPO") or Path(__file__).resolve().parents[4])
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest import fees as F
from MyTradingSys.backtest.power_mde import power_mde
from MyTradingSys.backtest.layers.cryptocred import run_cc_setups as R

DEV_START_MS = 1640995200000   # 2022-01-01T00:00Z
DEV_END_MS = 1719792000000     # 2024-07-01T00:00Z (exclusive); repo split DEV to 2024-06-30
DEV_MONTHS = 30
MIN_N = 100                    # INCONCLUSIVE in advance below this (card rule)
P_EDGE = 0.05                  # OURS: claimed win-rate edge over breakeven used for N-for-80%-power
TF_MS = {"1h": 3600000, "4h": 14400000, "1d": 86400000}


def count_signals(tf_bars, names=None):
    """{setup: signal list} on tf_bars with the runner's SETUPS and default parameters."""
    return {n: R.SETUPS[n](tf_bars) for n in (names or R.SETUPS)}


def count_fills(signals, sim_bars, tf_ms):
    """Number of limit signals that fill (find_limit_fill); market-style signals (setup 3) always count."""
    times = [b["t"] for b in sim_bars]
    n = 0
    for s in signals:
        meta = s.get("meta", {})
        if meta.get("setup") in R.LIMIT_SETUPS and "placed_t" in meta:
            if R.find_limit_fill(s, sim_bars, tf_ms, times) is not None:
                n += 1
        else:
            n += 1
    return n


def summarize(name, signals, sim_bars, tf_ms, months):
    n_sig = len(signals)
    n_fill = count_fills(signals, sim_bars, tf_ms)
    risks = [abs(s["entry_price"] - s["stop"]) / s["entry_price"] for s in signals]
    risk_pct = statistics.median(risks) if risks else None
    target_r = signals[0]["meta"]["target_r"] if signals else None
    out = {"setup": name, "signals": n_sig, "fills": n_fill,
           "signals_per_month": n_sig / months, "fills_per_month": n_fill / months,
           "median_risk_pct": risk_pct, "target_r": target_r, "inconclusive": n_fill < MIN_N}
    if n_fill and risk_pct:
        rr = target_r
        cost_r = 2 * F.DERIBIT_TAKER / risk_pct          # all_taker, two legs, conservative
        p_be = (1 + cost_r) / (rr + 1)                    # breakeven win rate net of cost
        out["cost_r"] = cost_r
        out["p_breakeven"] = p_be
        if p_be < 1.0 - P_EDGE:
            pw = power_mde(min(p_be + P_EDGE, 0.99), rr, cost_r, n_fill)
            out["p_claimed"] = min(p_be + P_EDGE, 0.99)
            out["power_at_claimed"] = pw["power"]
            out["mde_net_r"] = pw["mde_net_r"]
            out["trades_for_80_power"] = pw["trades_for_80_power"]
        else:
            out["unwinnable"] = "breakeven win rate within 5 points of 100% after fees"
    return out


def run(root1, root2, tfs):
    bars = R.load_data(root1, None, "1m")[0]
    bars = [b for b in bars if DEV_START_MS <= b["t"] < DEV_END_MS]
    assert bars and bars[-1]["t"] < DEV_END_MS
    import json as _j
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    reg = _j.loads(R.REGISTRY_PATH.read_text(encoding="utf-8"))
    rows = []
    for tf in tfs:
        tf_bars = resample(bars, tf, reg)
        for name, sigs in count_signals(tf_bars).items():
            r = summarize(name, sigs, bars, TF_MS[tf], DEV_MONTHS)
            r["tf"] = tf
            r["n_bars"] = len(tf_bars)
            rows.append(r)
    return {"dev": "2022-01-01..2024-06-30", "months": DEV_MONTHS, "n_1m_bars": len(bars), "rows": rows}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", default=os.environ.get("MTS_CC_DATA_ROOT", str(R.DEFAULT_ROOT1)))
    ap.add_argument("--tfs", default="1h,4h,1d")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    res = run(a.data_root, None, a.tfs.split(","))
    Path(a.out).write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    return res


if __name__ == "__main__":
    main()
