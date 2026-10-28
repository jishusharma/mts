TASK: Write MyTradingSys/execution/daily_loss_guard.py (pure computation only: G-c daily realized+unrealized loss breach decision) and test_daily_loss_guard.py.
SCOPE: none beyond this spec - self-contained, no other file needed.
OUTPUT: Two FILE blocks, full content: MyTradingSys/execution/daily_loss_guard.py and MyTradingSys/execution/test_daily_loss_guard.py. Nothing else.
OUTPUT_TOKENS: 3000
EXPECT: def daily_pnl(
EXPECT: def check_daily_loss_cap(
EXPECT: import unittest
EXPECT: DEFAULT_DAILY_LOSS_CAP_USD

Context: MTS has no account-wide daily loss circuit breaker today. This module computes ONLY the decision (breach yes/no); it does NOT call the exchange and does NOT place/cancel any order - a later, separately-routed task wires this decision to deribit_orders.cancel_by_label / close_position and to a halt flag. Keep this file free of any exchange-specific imports so it stays unit-testable with plain numbers.

Write Python 3.10, stdlib only (`dataclasses`, `typing`, `datetime` allowed).

Module-level constant: DEFAULT_DAILY_LOSS_CAP_USD = -500.0 (negative number = a loss ceiling; matches the conservative per-plan max_loss_usd floor already used in trade_plan_schema.json). A negative number represents a loss; 0 or positive pnl never breaches.

def daily_pnl(realized_pnl_events: list, unrealized_pnl_usd: float) -> float:
    realized_pnl_events is a list of dicts, each with at least a "pnl_usd" float key (one entry per closed/flattened plan today - the caller is responsible for only including today's UTC-day events before calling this). Sum every event's "pnl_usd", add unrealized_pnl_usd, return round(total, 2). Empty list + unrealized_pnl_usd=0.0 -> 0.0. Ignore/skip any event dict missing "pnl_usd" (do not raise).

def check_daily_loss_cap(realized_pnl_events: list, unrealized_pnl_usd: float, cap_usd: float = DEFAULT_DAILY_LOSS_CAP_USD) -> dict:
    Raise ValueError if cap_usd >= 0 (a cap must be a negative ceiling).
    total = daily_pnl(realized_pnl_events, unrealized_pnl_usd).
    breach = total <= cap_usd (at-or-worse-than the cap breaches; a total exactly equal to the cap DOES breach, unlike the account-notional cap which is strictly-greater).
    Return {"ok": not breach, "total_pnl_usd": total, "cap_usd": cap_usd, "action": "halt_and_flatten_all" if breach else "none", "reason": None if not breach else f"daily pnl {total} breached cap {cap_usd}"}.

def format_breach_report(result: dict) -> str:
    One-line string. Must contain literal "DAILY LOSS OK" when result["ok"] is True, or literal "DAILY LOSS BREACH - HALT ALL TRADING" when result["ok"] is False, followed by the numbers.

Tests (unittest):
- daily_pnl([], 0.0) == 0.0
- daily_pnl([{"pnl_usd": -100.0}, {"pnl_usd": 50.0}], -20.0) == -70.0
- daily_pnl([{"pnl_usd": -100.0}, {"other": 1}], 0.0) == -100.0 (skips malformed event, no raise)
- check_daily_loss_cap([], 0.0)["ok"] is True and ["action"] == "none"
- check_daily_loss_cap([{"pnl_usd": -600.0}], 0.0)["ok"] is False, ["action"] == "halt_and_flatten_all", "reason" contains "-600" and "-500"
- check_daily_loss_cap([{"pnl_usd": -500.0}], 0.0)["ok"] is False (boundary: exactly at cap breaches)
- check_daily_loss_cap([{"pnl_usd": -499.99}], 0.0)["ok"] is True (boundary: just inside cap is ok)
- check_daily_loss_cap([], 0.0, cap_usd=0) raises ValueError
- check_daily_loss_cap([], 0.0, cap_usd=100) raises ValueError (positive cap invalid too)
- format_breach_report on ok result contains "DAILY LOSS OK"; on breach result contains "DAILY LOSS BREACH - HALT ALL TRADING"
