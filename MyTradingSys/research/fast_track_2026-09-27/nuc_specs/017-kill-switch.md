TASK: Write MyTradingSys/execution/kill_switch.py (G-e: one-command account-wide kill switch - cancel every open order, then reduce-only-flatten every open position, on every instrument for a currency) and test_kill_switch.py, using a duck-typed client so it needs zero exchange imports and is unit-testable with a fake client.
SCOPE: MyTradingSys/execution/deribit_orders.py.new (read only - copy these exact method names/signatures, do not invent others): get_positions(token, currency="BTC", kind="future") -> list of dicts each with at least "instrument_name" and "size" keys; get_open_orders(token, instrument_name, type_="all") -> list of dicts each with at least "order_id" key; cancel(token, order_id) -> dict; close_position(token, instrument_name="BTC-PERPETUAL") -> dict.
OUTPUT: Two FILE blocks, full content: MyTradingSys/execution/kill_switch.py and MyTradingSys/execution/test_kill_switch.py. Nothing else.
OUTPUT_TOKENS: 4000
EXPECT: def kill_all(
EXPECT: class FakeClient
EXPECT: import unittest
EXPECT: "cancelled_orders"
EXPECT: "closed_positions"

Context: today, the only cancel primitive (deribit_orders.cancel_by_label) is deliberately label-scoped to one plan, by design (see deribit_orders.py.new module docstring, B078) - there is no account-wide "stop everything" command anywhere in the repo. This task adds ONE new standalone module that does exactly that, for a human (or a future daily-loss-guard caller) to invoke in one call when something is wrong. This module must NOT import deribit_orders.py directly (keep it stdlib-only and independently testable) - instead it takes a `client` argument: any object exposing the four methods listed in SCOPE with those exact names and signatures (minus the `token` argument - the caller already has an authenticated token and is expected to pass a thin object/partial that has these methods bound, OR pass an object with these methods taking token as first positional arg; support the SECOND shape: client.get_positions(token, currency=...) etc, i.e. the real deribit_orders module itself can be passed in directly as `client` with token passed separately - this is the shape that makes production wiring a two-line call: `kill_switch.kill_all(deribit_orders, token)`).

Write Python 3.10, stdlib only (`dataclasses`, `typing`, `time`).

def kill_all(client, token, currency: str = "BTC", instruments: list = None) -> dict:
    If instruments is None: discover them by calling client.get_positions(token, currency=currency, kind="future") and collecting every distinct "instrument_name" that has a nonzero "size" (abs(size) > 0); if that list is empty, fall back to instruments = ["BTC-PERPETUAL"] (always attempt at least the default instrument so a kill-switch call is never a silent no-op).
    Phase 1 - cancel every open order on every instrument in the (possibly-discovered) instrument list PLUS always "BTC-PERPETUAL" if not already included: for each instrument, call client.get_open_orders(token, instrument_name=instrument, type_="all"); for each order in the result call client.cancel(token, order["order_id"]); collect every order_id into cancelled_orders (list). Catch any exception per-order (a class named Exception is fine, no custom exchange error type is imported here) and instead of raising, append {"order_id": ..., "error": repr(e)} to a separate errors list; keep going (do not abort the whole kill switch because one cancel failed).
    Phase 2 - flatten every position: re-fetch client.get_positions(token, currency=currency, kind="future"); for every position with abs(size) > 0, call client.close_position(token, instrument_name=position["instrument_name"]); collect {"instrument_name": ..., "result": <return value>} into closed_positions. Same per-position try/except into errors, keep going.
    Return {"cancelled_orders": cancelled_orders, "closed_positions": closed_positions, "errors": errors, "ok": len(errors) == 0}.
    Order of operations matters: ALWAYS cancel first, then flatten (cancelling resting entry/target orders before flattening avoids a stale limit order re-opening a position right after the market flatten). Never flatten before every discovered instrument's orders are cancelled.

def format_kill_report(result: dict) -> str:
    Multi-line human summary. Must contain the literal substring "KILL SWITCH" and report len(cancelled_orders), len(closed_positions), len(errors). If errors is non-empty, the string must also contain the literal substring "ERRORS DURING KILL" (operator must not assume a clean kill just because it ran).

class FakeClient (in the test file, not the main module): a minimal in-memory stand-in with get_positions(token, currency="BTC", kind="future"), get_open_orders(token, instrument_name, type_="all"), cancel(token, order_id), close_position(token, instrument_name="BTC-PERPETUAL"), constructed from a dict of {instrument_name: {"size": int, "orders": [order_id, ...]}}; cancel() removes the id from that instrument's orders list and raises KeyError if the id is not present (for the error-path test); close_position() sets that instrument's size to 0 and returns {"order": {"order_id": "flat-<instrument>", "filled_amount": <abs size before flattening>}}.

Tests (unittest):
- kill_all with two instruments each having 2 open orders and a nonzero position: cancelled_orders has 4 ids, closed_positions has 2 entries, errors is empty, ok is True.
- kill_all when one cancel() call hits an id already removed (simulate by passing a duplicate order_id in the fake's order list) -> that one goes into errors, the rest still get cancelled and both positions still get flattened (errors does not stop phase 2).
- kill_all with instruments=None and a FakeClient where only one instrument has nonzero size -> only that instrument (plus the always-included "BTC-PERPETUAL" default if different) gets processed; confirm "BTC-PERPETUAL" is present in the processed set even when the discovered position is on a different instrument, e.g. "ETH-PERPETUAL".
- kill_all with instruments=None and NO nonzero positions at all -> falls back to instruments=["BTC-PERPETUAL"], still attempts cancel on it (0 orders is fine), closed_positions is empty, ok is True.
- format_kill_report on a clean result contains "KILL SWITCH" and does not contain "ERRORS DURING KILL".
- format_kill_report on a result with a nonempty errors list contains both "KILL SWITCH" and "ERRORS DURING KILL".
