TASK: Write MyTradingSys/execution/risk_guard.py (pure computation: cross-plan/account-wide position notional cap, G-b) and test_risk_guard.py.
SCOPE: MyTradingSys/execution/plan_compiler.py.new (read only, for max_notional_usd shape), MyTradingSys/execution/deribit_orders.py.new (read only, for get_position()/get_positions() return shape: dicts with keys "size" (signed contracts) and "mark_price" or similar - use size only, do not assume other keys).
OUTPUT: Two FILE blocks, full content: MyTradingSys/execution/risk_guard.py and MyTradingSys/execution/test_risk_guard.py. Nothing else.
OUTPUT_TOKENS: 3000
EXPECT: def account_position_notional(
EXPECT: def check_new_plan_against_cap(
EXPECT: import unittest
EXPECT: MAX_ACCOUNT_NOTIONAL_USD

Context: MTS trades BTC-PERPETUAL on Deribit through one exchange account. Each trade plan has its own per-plan cap (plan["caps"]["max_notional_usd"]), already enforced in executor.py before that one plan's orders are placed (see executor.py.new preflight()). What is MISSING is an account-wide ceiling: the exchange's live position size, in USD notional, checked BEFORE compiling/entering a NEW plan, so that several simultaneously-live plans on the same instrument cannot together exceed one hard ceiling. This module is pure computation only - it does not call the exchange itself; the caller passes in numbers it already fetched (from deribit_orders.get_position()/get_ticker()).

Write Python 3.10, stdlib only (no imports beyond `dataclasses`, `typing` if useful). No network calls, no imports of deribit_orders or plan_compiler (those are the caller's job).

Module-level constant: MAX_ACCOUNT_NOTIONAL_USD = 10000 (conservative default matching the per-plan schema ceiling in trade_plan_schema.json; a plain int, operator raises later).

def account_position_notional(position_size_contracts: float, mark_price: float) -> float:
    Return abs(position_size_contracts) * mark_price, rounded to 2 decimals with round(x, 2). Deribit BTC-PERPETUAL "size" is denominated in USD already in some Deribit endpoints and in contracts in others - THIS FUNCTION ASSUMES size IS ALREADY IN THE SAME UNITS AS notional (i.e. the caller has already converted); it just does abs() * price only when the caller passes size in BTC/contracts, or returns abs(position_size_contracts) unchanged when mark_price is None. Concretely: if mark_price is None, return round(abs(position_size_contracts), 2) (size already USD notional); else return round(abs(position_size_contracts) * mark_price, 2).

def check_new_plan_against_cap(current_position_notional_usd: float, new_plan_max_notional_usd: float, cap: float = MAX_ACCOUNT_NOTIONAL_USD) -> dict:
    Compute projected = round(current_position_notional_usd + new_plan_max_notional_usd, 2).
    Return a dict: {"ok": bool, "current_notional_usd": current_position_notional_usd, "new_plan_notional_usd": new_plan_max_notional_usd, "projected_notional_usd": projected, "cap_usd": cap, "reason": str_or_None}.
    ok is False and reason is f"account notional would reach {projected} > cap {cap}" when projected > cap. Otherwise ok is True and reason is None.
    Raise ValueError if current_position_notional_usd < 0 or new_plan_max_notional_usd < 0 or cap <= 0 (before computing anything).

def format_guard_report(result: dict) -> str:
    One-line human string for a preflight log, e.g. "ACCOUNT CAP OK: current=1200.0 + new=800.0 = 2000.0 <= cap=10000" or "ACCOUNT CAP BREACH: ..." (breach when result["ok"] is False). Must contain the literal substrings "ACCOUNT CAP OK" or "ACCOUNT CAP BREACH".

Tests (unittest, TestCase per function is fine):
- account_position_notional(5, None) == 5.0 (already-USD path)
- account_position_notional(-5, None) == 5.0 (abs)
- account_position_notional(2, 50000.0) == 100000.0
- account_position_notional(0, 50000.0) == 0.0
- check_new_plan_against_cap(0, 5000, cap=10000)["ok"] is True, reason is None
- check_new_plan_against_cap(9000, 2000, cap=10000)["ok"] is False, "reason" contains "11000" and "10000"
- check_new_plan_against_cap(9000, 1000, cap=10000)["ok"] is True (exactly at cap, boundary: projected == cap is OK, only strictly greater than cap breaches)
- check_new_plan_against_cap(-1, 100) raises ValueError
- check_new_plan_against_cap(100, -1) raises ValueError
- check_new_plan_against_cap(100, 100, cap=0) raises ValueError
- format_guard_report on an ok result contains "ACCOUNT CAP OK"; on a breach result contains "ACCOUNT CAP BREACH"
