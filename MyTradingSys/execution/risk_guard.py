"""
MyTradingSys/execution/risk_guard.py

Pure computation module to enforce account-wide position notional caps.
Checks that the sum of current position notional and a new plan's max notional
does not exceed MAX_ACCOUNT_NOTIONAL_USD.

This module is pure computation only - it does not call the exchange itself;
the caller passes in numbers it already fetched (from deribit_orders.get_position()/get_ticker()).

Rationale: MTS trades BTC-PERPETUAL on Deribit through one exchange account.
Each trade plan has its own per-plan cap (plan["caps"]["max_notional_usd"]),
already enforced in executor.py before that one plan's orders are placed.
What is MISSING is an account-wide ceiling: the exchange's live position size,
in USD notional, checked BEFORE compiling/entering a NEW plan, so that several
simultaneously-live plans on the same instrument cannot together exceed one hard ceiling.
"""
import math
from dataclasses import dataclass
from typing import Optional

MAX_ACCOUNT_NOTIONAL_USD = 10000


def account_position_notional(position_size_contracts: float, mark_price: Optional[float]) -> float:
    """
    Return abs(position_size_contracts) * mark_price, rounded to 2 decimals with round(x, 2).
    
    Deribit BTC-PERPETUAL "size" is denominated in USD already in some Deribit endpoints
    and in contracts in others - THIS FUNCTION ASSUMES size IS ALREADY IN THE SAME UNITS
    AS notional (i.e. the caller has already converted); it just does abs() * price only
    when the caller passes size in BTC/contracts, or returns abs(position_size_contracts)
    unchanged when mark_price is None.
    
    Concretely: if mark_price is None, return round(abs(position_size_contracts), 2)
    (size already USD notional); else return round(abs(position_size_contracts) * mark_price, 2).
    """
    # fail closed: an unreadable size/price must make the cap refuse, never pass
    try:
        size = abs(float(position_size_contracts))
        px = None if mark_price is None else float(mark_price)
    except (TypeError, ValueError):
        return math.inf
    if not math.isfinite(size) or (px is not None and not math.isfinite(px)):
        return math.inf
    if px is None:
        return round(size, 2)
    return round(size * px, 2)


def check_new_plan_against_cap(current_position_notional_usd: float, new_plan_max_notional_usd: float, cap: float = None) -> dict:
    """
    Compute projected = round(current_position_notional_usd + new_plan_max_notional_usd, 2).
    
    Return a dict: {"ok": bool, "current_notional_usd": current_position_notional_usd,
    "new_plan_notional_usd": new_plan_max_notional_usd, "projected_notional_usd": projected,
    "cap_usd": cap, "reason": str_or_None}.
    
    ok is False and reason is f"account notional would reach {projected} > cap {cap}"
    when projected > cap. Otherwise ok is True and reason is None.
    
    Raise ValueError if current_position_notional_usd < 0 or new_plan_max_notional_usd < 0 or cap <= 0
    (before computing anything).
    """
    if cap is None:
        cap = MAX_ACCOUNT_NOTIONAL_USD  # read at call time, so the module constant is the single place to tune it

    if current_position_notional_usd < 0:
        raise ValueError("current_position_notional_usd must be non-negative")
    if new_plan_max_notional_usd < 0:
        raise ValueError("new_plan_max_notional_usd must be non-negative")
    if cap <= 0:
        raise ValueError("cap must be positive")

    if not (math.isfinite(current_position_notional_usd) and math.isfinite(new_plan_max_notional_usd)):
        projected = math.inf  # fail closed on NaN/inf inputs
    else:
        projected = round(current_position_notional_usd + new_plan_max_notional_usd, 2)
    if projected > cap:
        return {
            "ok": False,
            "current_notional_usd": current_position_notional_usd,
            "new_plan_notional_usd": new_plan_max_notional_usd,
            "projected_notional_usd": projected,
            "cap_usd": cap,
            "reason": f"account notional would reach {float(projected)} > cap {cap}"
        }
    return {
        "ok": True,
        "current_notional_usd": current_position_notional_usd,
        "new_plan_notional_usd": new_plan_max_notional_usd,
        "projected_notional_usd": projected,
        "cap_usd": cap,
        "reason": None
    }


def format_guard_report(result: dict) -> str:
    """
    One-line human string for a preflight log, e.g.
    "ACCOUNT CAP OK: current=1200.0 + new=800.0 = 2000.0 <= cap=10000"
    or "ACCOUNT CAP BREACH: ..." (breach when result["ok"] is False).
    
    Must contain the literal substrings "ACCOUNT CAP OK" or "ACCOUNT CAP BREACH".
    """
    if result["ok"]:
        return f"ACCOUNT CAP OK: current={float(result['current_notional_usd'])} + new={float(result['new_plan_notional_usd'])} = {float(result['projected_notional_usd'])} <= cap={result['cap_usd']}"
    else:
        return f"ACCOUNT CAP BREACH: {result['reason']}"
