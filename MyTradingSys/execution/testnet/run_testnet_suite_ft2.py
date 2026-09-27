"""
FT-2 testnet trip suite (2026-09-28). TESTNET ONLY. Run AFTER the base suite
(run_testnet_suite.py, C1-C6) and the G1/G2 suite (run_testnet_suite_g1g2.py,
now including G1c) both pass - this file's harness enforces that by running
the base suite as a subprocess first, exactly like run_testnet_suite_g1g2.py
does, and reuses its helpers (clean/plan/run/oo) the same way.

Covers the four FT-2 gaps: the account-wide notional cap (S1) exercised at
its OWN configured limit rather than the default 10000, the daily-loss
monitor's kill+HALT+preflight-refusal path end-to-end, position_manager's
re-place-or-flatten guarantee after an externally cancelled stop, and the
kill_switch module's account-wide kill_all() against a live position with
resting target orders.

Run: python MyTradingSys/execution/testnet/run_testnet_suite_ft2.py

T-b (account cap): risk_guard.check_new_plan_against_cap reads
MAX_ACCOUNT_NOTIONAL_USD at call time (cap=None default, Opus fix 2026-09-28),
so the suite lowers the module constant in-process and restores it in finally.

T-c (daily loss): the monitor's math is
    total_pnl_usd = (equity_now - equity_at_start_of_day) * mark_price_now
(see daily_loss_monitor.py's own docstring for why - this suite does not
re-derive that). A cap of -0.01 USD is used rather than inventing a forced
loss: on TESTNET a same-instrument market-in/market-out round trip on
BTC-PERPETUAL always costs at least the taker fee on both legs, so equity
strictly decreases across the round trip - any cap tighter than that fee
cost breaches. This is the one part of this suite that is NOT fully
deterministic ahead of time: it depends on TESTNET's live fee schedule and
mark-price movement between the two fills being non-positive enough to
still show a net equity decrease at -0.01 precision. If this case is ever
flaky, first check (a) whether TESTNET fees are momentarily zero/rebated,
or (b) whether the small round trip's own mark-price slippage happened to
be net POSITIVE by more than the fee cost - both would need a larger round
trip size or a less microscopic cap, not a code change to daily_loss_monitor
itself.

T-d (unprotected): manage() is called with a small `max_seconds` (not
`once`) so it is allowed to loop naturally for a few polls; no exchange
call is monkeypatched, and the assertion below deliberately accepts EITHER
observed outcome (a live stop covering the full position, or a fully flat
account) as PASS - "never naked" is the actual invariant under test, not
which of the two valid recoveries position_manager takes on any given run.

T-e (kill switch): kill_switch.kill_all() is called directly against
deribit_orders (do), the same duck-typed client shape kill_all expects
(get_positions/get_open_orders/cancel/close_position) - do already
satisfies all four (see kill_switch.py's own docstring).
"""
import sys, time
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import subprocess, types

_base_g1g2 = Path(__file__).resolve().parent / "run_testnet_suite_g1g2.py"
if subprocess.call([sys.executable, str(_base_g1g2)]) != 0:  # base C1-C6 + G1/G2 (incl. G1c) first
    print("base suite / G1-G2 suite not all PASS - FT-2 cases not run")
    sys.exit(1)

_base = Path(__file__).resolve().parent / "run_testnet_suite.py"
_ns = {"__file__": str(_base), "__name__": "base_suite_helpers"}
exec(compile(open(_base, encoding="utf-8").read().split("\nfor n, f in [(")[0], str(_base), "exec"), _ns)
S = types.SimpleNamespace(**_ns)  # helpers only: tok, I, clean, plan, run, oo

import deribit_orders as do, executor as ex, journal, position_manager as pm
import risk_guard, daily_loss_monitor as dlm, kill_switch

tok, I, results = S.tok, S.I, []


# T-b: account-wide notional cap refuses a plan that would exceed a
# temporarily-lowered cap, before any order is placed.
def t_b_cap():
    real_cap = risk_guard.MAX_ACCOUNT_NOTIONAL_USD
    risk_guard.MAX_ACCOUNT_NOTIONAL_USD = 50.0  # smallest testnet plan (base=100) exceeds this
    try:
        p = S.plan("t_b_cap", base=100)
        try:
            S.run(p)
            return False, "not refused"
        except ex.ExecutionHalted as e:
            refused = "S1" in str(e) and "PREFLIGHT REFUSED" in str(e)
            detail = str(e)[:140]
        nothing_placed = not do.get_open_orders(tok, I) and do.get_position(tok, I)["size"] == 0
        return refused and nothing_placed, {"halt": detail, "nothing_placed": nothing_placed}
    finally:
        risk_guard.MAX_ACCOUNT_NOTIONAL_USD = real_cap


# T-c: a real (fee-driven) daily loss breach on TESTNET -> kill_all runs,
# HALT_DAILY_LOSS is written, and the very next plan is refused by
# executor's preflight() reading that same file.
def t_c_daily_loss():
    # FIX3 H6: temp files only - the helpers pointed ex.HALT_DAILY_LOSS_PATH
    # at the suite temp dir, so preflight reads the same file run_once writes.
    halt_daily = ex.HALT_DAILY_LOSS_PATH
    state_path = S.SUITE_TMP / "daily_loss_monitor_state.json"
    halt_daily.unlink(missing_ok=True)
    state_path.unlink(missing_ok=True)
    try:
        # snapshot today's opening equity BEFORE the round trip, so run_once
        # below sees the round trip's cost, not a baseline taken after it.
        state = dlm.ensure_day_state(do, tok, dlm._utc_now(), state_path=state_path)
        dlm.save_state(state, state_path)

        do.buy(tok, I, 10, "market", label="ft2_tc_in")
        time.sleep(1)
        do.sell(tok, I, 10, "market", label="ft2_tc_out", reduce_only=True)
        time.sleep(1)

        result = dlm.run_once(do, tok, cap_usd=-0.01, state_path=state_path, halt_path=halt_daily)
        breached = not result["ok"]
        halt_written = halt_daily.exists()

        next_refused, next_detail = False, None
        p = S.plan("t_c_next_plan_refused")
        try:
            S.run(p)
        except ex.ExecutionHalted as e:
            next_refused = "HALT_DAILY_LOSS" in str(e)
            next_detail = str(e)[:140]

        ok = breached and halt_written and next_refused
        return ok, {"breach": breached, "total_pnl_usd": result.get("total_pnl_usd"),
                    "halt_written": halt_written, "next_plan_refusal": next_detail}
    finally:
        halt_daily.unlink(missing_ok=True)
        state_path.unlink(missing_ok=True)
        S.clean()


# T-d: externally cancelling the live stop must never leave the position
# naked - position_manager either re-places a stop covering the full size,
# or (if it cannot) flattens within MAX_UNPROTECTED_SECONDS. Both outcomes
# pass; only "still open, no live stop" fails.
def t_d_unprotected():
    p = S.plan("t_d_unprotected", targets=[])
    r = S.run(p)
    pid = p["plan_id"]
    do.cancel(tok, r["stop_order_id"])
    time.sleep(1)

    try:
        m = pm.manage(pid, max_seconds=pm.MAX_UNPROTECTED_SECONDS + 4, token=tok)
        outcome = f"managing: {m}"
    except pm.ManagerHalted as e:
        outcome = f"halted: {e}"

    pos = do.get_position(tok, I)["size"]
    o = S.oo()
    stop = o.get("stop_order") or o.get("stop_order_pending_fill")
    live_stop_correct_size = stop is not None and stop["order_type"] == "stop_market" and abs(pos) == stop["amount"]
    flat = pos == 0
    ok = live_stop_correct_size or flat
    return ok, {"pos": pos, "stop_amount": stop and stop.get("amount"), "outcome": outcome[:140]}


# T-e: kill_all cancels every resting order and flattens the position.
def t_e_kill_switch():
    p = S.plan("t_e_kill", targets=[{"amount_percent": 50, "pnl_target_percent": 2.0},
                                    {"amount_percent": 50, "pnl_target_percent": 5.0}])
    S.run(p)
    time.sleep(1)
    result = kill_switch.kill_all(do, tok)
    time.sleep(0.5)
    pos = do.get_position(tok, I)["size"]
    open_orders = do.get_open_orders(tok, I)
    ok = pos == 0 and not open_orders and result["ok"]
    return ok, {"pos": pos, "open_orders_left": len(open_orders), "kill_ok": result["ok"],
                "kill_errors": result["errors"]}


for n, f in [("T-b account cap refused before any order", t_b_cap),
             ("T-c daily loss breach -> kill + HALT_DAILY_LOSS + next refused", t_c_daily_loss),
             ("T-d unprotected -> re-placed or flattened, never naked", t_d_unprotected),
             ("T-e kill switch -> flat, zero open orders", t_e_kill_switch)]:
    S.clean()
    try:
        ok, d = f()
    except Exception as e:  # noqa: BLE001
        ok, d = False, f"{type(e).__name__}: {e}"
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + n + " :: " + str(d))
    S.clean()

print(f"\nFT-2: {sum(results)}/{len(results)} PASS")
sys.exit(0 if all(results) else 1)
