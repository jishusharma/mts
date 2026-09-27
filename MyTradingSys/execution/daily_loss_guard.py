"""
Daily loss guard module for computing G-c daily realized+unrealized loss breach decision.
Pure computation; no exchange-specific imports or side effects.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime

DEFAULT_DAILY_LOSS_CAP_USD = -500.0


def daily_pnl(realized_pnl_events: List[Dict[str, Any]], unrealized_pnl_usd: float) -> float:
    """
    Compute total daily PnL from realized events and unrealized PnL.

    :param realized_pnl_events: List of dicts with at least "pnl_usd" key.
    :param unrealized_pnl_usd: Current unrealized PnL in USD.
    :return: Total PnL rounded to 2 decimal places.
    """
    total = sum(event["pnl_usd"] for event in realized_pnl_events if "pnl_usd" in event)
    return round(total + unrealized_pnl_usd, 2)


def check_daily_loss_cap(realized_pnl_events: List[Dict[str, Any]], unrealized_pnl_usd: float, cap_usd: float = DEFAULT_DAILY_LOSS_CAP_USD) -> Dict[str, Any]:
    """
    Check if daily loss cap is breached.

    :param realized_pnl_events: List of dicts with at least "pnl_usd" key.
    :param unrealized_pnl_usd: Current unrealized PnL in USD.
    :param cap_usd: Daily loss cap (must be negative).
    :return: Dict with keys: ok, total_pnl_usd, cap_usd, action, reason.
    :raises ValueError: If cap_usd is not negative.
    """
    if cap_usd >= 0:
        raise ValueError("cap_usd must be a negative number representing a loss ceiling")

    total = daily_pnl(realized_pnl_events, unrealized_pnl_usd)
    breach = total <= cap_usd
    action = "halt_and_flatten_all" if breach else "none"
    reason = None if not breach else f"daily pnl {total} breached cap {cap_usd}"

    return {
        "ok": not breach,
        "total_pnl_usd": total,
        "cap_usd": cap_usd,
        "action": action,
        "reason": reason
    }


def format_breach_report(result: Dict[str, Any]) -> str:
    """
    Format a one-line report string based on the result of check_daily_loss_cap.

    :param result: Result dict from check_daily_loss_cap.
    :return: Formatted string indicating OK or breach status with values.
    """
    if result["ok"]:
        return f"DAILY LOSS OK total={result['total_pnl_usd']}, cap={result['cap_usd']}"
    else:
        return f"DAILY LOSS BREACH - HALT ALL TRADING total={result['total_pnl_usd']}, cap={result['cap_usd']}"
