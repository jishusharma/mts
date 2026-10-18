"""Scorecard evaluation engine for external analyst signals.

Standardized execution rules:
- Fees: 0.05% per side (SOURCED: MyTradingSys/backtest/layers/FORMULAS.md:s17)
- Fill Window: 24 hours (OURS: MyTradingSys/research/qriptal_2026-10-10/score_calls.py:30)
- Max Open Window: 7 days (OURS: MyTradingSys/research/qriptal_2026-10-10/score_calls.py:31)
- In-candle collision: Stop is checked first (SOURCED: MyTradingSys/research/qriptal_2026-10-10/score_calls.py:83-84)
- Statistical power: Exact binomial comparison against claimed vs coin flip (SOURCED: MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:38)
"""
from datetime import datetime, timezone
from math import comb
from typing import List, Dict, Any, Optional, Tuple

from schema import AnalystSignal, SignalDirection, SignalStatus

# Fee constant: 0.05% per side (SOURCED: MyTradingSys/backtest/layers/FORMULAS.md:s17)
FEE_PER_SIDE: float = 0.0005

# Window durations (OURS)
FILL_WINDOW_MS: int = 24 * 3600 * 1000
OPEN_WINDOW_MS: int = 7 * 24 * 3600 * 1000


def score_signal_against_klines(
    signal: AnalystSignal,
    klines: List[List[float]],
    target_index: int = 0,
) -> Dict[str, Any]:
    """Scores a single analyst signal against historical 1m klines [open_time, o, h, l, c].

    Exit priority inside a bar:
    1. Stop Loss is ALWAYS checked first inside every candle.
    2. In the fill candle, only Stop is checked (fill order vs target within candle is unknown).
    """
    side = 1 if signal.direction == SignalDirection.LONG else -1
    entry = signal.entry_price
    stop = signal.stop_loss
    target = signal.targets[min(target_index, len(signal.targets) - 1)]
    risk = signal.risk_amount

    # Find fill candle
    fill_idx = None
    start_ms = klines[0][0] if klines else 0
    max_fill_ms = start_ms + FILL_WINDOW_MS

    for idx, k in enumerate(klines):
        t, o, h, l, c = k
        if t > max_fill_ms:
            break
        # Does bar span the entry price?
        if l <= entry <= h:
            fill_idx = idx
            break

    if fill_idx is None:
        return {
            "status": SignalStatus.NOT_FILLED,
            "fill_idx": None,
            "exit_price": None,
            "exit_time_ms": None,
            "net_r": 0.0,
            "gross_r": 0.0,
            "net_pct": 0.0,
            "is_win": False,
        }

    fill_candle = klines[fill_idx]
    fill_time_ms = fill_candle[0]
    max_open_ms = fill_time_ms + OPEN_WINDOW_MS

    # Check resolution starting from fill candle
    exit_status = None
    exit_price = None
    exit_time_ms = None

    for idx in range(fill_idx, len(klines)):
        t, o, h, l, c = klines[idx]
        if t >= max_open_ms:
            exit_status = SignalStatus.TIMEOUT
            exit_price = c
            exit_time_ms = t
            break

        # 1. Stop loss check (always first)
        hit_stop = (l <= stop) if side > 0 else (h >= stop)
        if hit_stop:
            exit_status = SignalStatus.STOPPED
            exit_price = stop
            exit_time_ms = t
            break

        # 2. Target check (only after the fill candle, to avoid ambiguous intra-candle sequence)
        if idx > fill_idx:
            hit_target = (h >= target) if side > 0 else (l <= target)
            if hit_target:
                exit_status = SignalStatus.TARGET_HIT
                exit_price = target
                exit_time_ms = t
                break

    if exit_status is None:
        # Data ended before trade resolved
        last_k = klines[-1]
        exit_status = SignalStatus.TIMEOUT
        exit_price = last_k[4]
        exit_time_ms = last_k[0]

    # Calculate returns with fee (SOURCED: MyTradingSys/backtest/layers/FORMULAS.md:s17)
    gross = side * (exit_price - entry)
    fee_amount = FEE_PER_SIDE * (entry + exit_price)
    net = gross - fee_amount

    net_r = net / risk if risk > 0 else 0.0
    gross_r = gross / risk if risk > 0 else 0.0
    net_pct = net / entry

    is_win = (exit_status == SignalStatus.TARGET_HIT) or (net_r > 0)

    return {
        "status": exit_status,
        "fill_idx": fill_idx,
        "exit_price": exit_price,
        "exit_time_ms": exit_time_ms,
        "net_r": net_r,
        "gross_r": gross_r,
        "net_pct": net_pct,
        "is_win": is_win,
    }


def compute_scorecard_metrics(scored_trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregates scorecard performance metrics (OURS)."""
    if not scored_trades:
        return {
            "total_trades": 0,
            "resolved_trades": 0,
            "not_filled": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0,
            "net_r_sum": 0.0,
            "avg_net_r": 0.0,
            "profit_factor": 0.0,
        }

    wins = sum(1 for t in scored_trades if t.get("is_win", False))
    losses = sum(1 for t in scored_trades if not t.get("is_win", False) and t.get("status") != SignalStatus.NOT_FILLED)
    not_filled = sum(1 for t in scored_trades if t.get("status") == SignalStatus.NOT_FILLED)

    resolved_count = wins + losses
    win_rate = (wins / resolved_count) if resolved_count > 0 else 0.0

    r_values = [t.get("net_r", 0.0) for t in scored_trades if t.get("status") != SignalStatus.NOT_FILLED]
    net_r_sum = sum(r_values)
    avg_net_r = (net_r_sum / len(r_values)) if r_values else 0.0

    gross_gains = sum(r for r in r_values if r > 0)
    gross_losses = abs(sum(r for r in r_values if r < 0))
    profit_factor = (gross_gains / gross_losses) if gross_losses > 0 else (99.0 if gross_gains > 0 else 0.0)

    return {
        "total_trades": len(scored_trades),
        "resolved_trades": resolved_count,
        "not_filled": not_filled,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "net_r_sum": net_r_sum,
        "avg_net_r": avg_net_r,
        "profit_factor": profit_factor,
    }


def calculate_binomial_power(
    n: int,
    claimed_win_rate: float = 0.671,
    null_win_rate: float = 0.50,
    alpha: float = 0.05,
) -> float:
    """Exact binomial power: probability of rejecting H0 (p = null_win_rate) when true p is claimed_win_rate.

    With n = 0, power is 0.0 (SOURCED: MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:38)
    """
    if n <= 0:
        return 0.0

    # Find critical value k_crit such that P(X >= k_crit | p=null_win_rate) <= alpha
    k_crit = None
    for k in range(n, -1, -1):
        p_val = sum(comb(n, i) * (null_win_rate**i) * ((1 - null_win_rate)**(n - i)) for i in range(k, n + 1))
        if p_val <= alpha:
            k_crit = k
        else:
            break

    if k_crit is None:
        return 0.0

    # Power = P(X >= k_crit | p=claimed_win_rate)
    power = sum(
        comb(n, i) * (claimed_win_rate**i) * ((1 - claimed_win_rate)**(n - i))
        for i in range(k_crit, n + 1)
    )
    return float(power)
