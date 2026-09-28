"""
G1/G2 testnet cases (Opus 5.5, 2026-09-27). TESTNET ONLY. Run AFTER the session-3 renames
(deribit_orders/executor/plan_compiler v2) and position_manager.py / reconciler.py v2 renames.
Reuses the helpers of run_testnet_suite.py (clean/plan/case/run/oo).

G1c added (S6, 2026-09-28): partial target fill -> forced flatten -> asserts
get_open_orders shows zero orders whose label starts with the plan_id, i.e.
the S6 orphan-stop-sweep fix (fail_closed sweeping the stop + target labels,
not just entry labels) leaves nothing resting after a forced flatten.

Run: python MyTradingSys/execution/testnet/run_testnet_suite_g1g2.py
"""
import sys, time
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import subprocess, types
_base = Path(__file__).resolve().parent / "run_testnet_suite.py"
if subprocess.call([sys.executable, str(_base)]) != 0:  # full base proof C1-C6 first
    print("base suite C1-C6 not all PASS - G1/G2 cases not run"); sys.exit(1)
_ns = {"__file__": str(_base), "__name__": "base_suite_helpers"}
exec(compile(open(_base, encoding="utf-8").read().split("\nfor n, f in [(")[0], str(_base), "exec"), _ns)
S = types.SimpleNamespace(**_ns)  # helpers only: tok, I, clean, plan, run, oo
import deribit_orders as do, executor as ex, journal, position_manager as pm, reconciler as rc
tok, I, results = S.tok, S.I, []

# G1a: a target fill shrinks the stop to the remaining size
def g1a():
    p = S.plan("g1a_shrink", targets=[]); r = S.run(p); pid = p["plan_id"]
    o = do.sell(tok, I, 50, "market", label=f"{pid}:target_1", reduce_only=True)["order"]
    journal.append_event(pid, "order_placed", {"order_id": o["order_id"], "label": "target_1", "side": "SELL", "amount": 50})
    time.sleep(1)
    m = pm.manage(pid, once=True, token=tok)
    stop = S.oo().get("stop_order_pending_fill") or S.oo().get("stop_order")
    ok = do.get_position(tok, I)["size"] == 50 and stop and stop["amount"] == 50 and m["stop_amount"] == 50
    rec = rc.reconcile(pid, token=tok)["status"]
    return ok and rec == "reconciled_ok", {"stop_amount": stop and stop["amount"], "reconcile": rec}

# G1b: reduce-only oversize behaviour (proxy for 'oversized reduce-only stop at trigger').
# Position 10, reduce_only market sell 20 -> must NOT go short. Records whether Deribit clamps or rejects.
def g1b():
    do.buy(tok, I, 10, "market", label="g1b_setup")
    try:
        do.sell(tok, I, 20, "market", label="g1b_oversize", reduce_only=True); outcome = "accepted"
    except do.DeribitError as e:
        outcome = f"rejected:{e.error}"
    pos = do.get_position(tok, I)["size"]
    return pos >= 0, {"outcome": outcome, "pos_after": pos,
                      "note": "clamped" if outcome == "accepted" and pos == 0 else "see outcome"}

# G1c (S6, 2026-09-28): entry fills, target_1 partially fills, then something
# forces a flatten (fail_closed via a forced stop-resize failure, mirroring
# base suite's C5) - after the flatten, no exchange order may be left resting
# under this plan's label prefix (entry / stop / any target), whether or not
# MTS ever learned that order's order_id.
def g1c():
    p = S.plan("g1c_partial_target_then_flatten", targets=[{"amount_percent": 50, "pnl_target_percent": 2.0},
                                                            {"amount_percent": 50, "pnl_target_percent": 5.0}])
    r = S.run(p); pid = p["plan_id"]
    # partially fill target_1 (30 of 100), like g1a, before forcing the flatten
    o = do.sell(tok, I, 30, "market", label=f"{pid}:target_1", reduce_only=True)["order"]
    journal.append_event(pid, "order_placed", {"order_id": o["order_id"], "label": "target_1", "side": "SELL", "amount": 30})
    time.sleep(1)
    real_edit = do.edit
    def boom(*a, **k): raise do.DeribitError("private/edit", {"code": 10009, "message": "forced_by_test"})
    do.edit = boom
    try:
        pm.manage(pid, once=True, token=tok)
        outcome = "manager did not halt"
    except pm.ManagerHalted as e:
        outcome = str(e)
    finally:
        do.edit = real_edit
    leftover = [o for o in do.get_open_orders(tok, I) if str(o.get("label", "")).startswith(f"{pid}:")]
    ok = "flattened" in outcome and do.get_position(tok, I)["size"] == 0 and not leftover
    return ok, {"outcome": outcome, "leftover_labels": [o.get("label") for o in leftover]}

# G2a: close the position behind MTS's back -> reconciler detects + halts; manager also halts
def g2a():
    p = S.plan("g2a_forced", targets=[]); S.run(p); pid = p["plan_id"]
    do.close_position(tok, I); time.sleep(1)
    try:
        rc.reconcile(pid, token=tok); rec = "NOT DETECTED"
    except rc.ReconciliationMismatch as e:
        rec = "detected" if "position_size_mismatch" in str(e) else str(e)[:120]
    halted = journal.reconstruct_belief(pid)["halted"]
    return rec == "detected" and halted, {"reconciler": rec, "journal_halted": halted}

for n, f in [("G1a stop shrinks on target fill", g1a), ("G1b reduce-only oversize never reverses", g1b),
             ("G1c partial target fill then forced flatten - zero plan-label orders left", g1c),
             ("G2a forced mismatch -> halt", g2a)]:
    S.clean()
    try:
        ok, d = f()
    except Exception as e:  # noqa: BLE001
        ok, d = False, f"{type(e).__name__}: {e}"
    results.append(ok); print(("PASS " if ok else "FAIL ") + n + " :: " + str(d))
    S.clean()
print(f"\nG1/G2: {sum(results)}/{len(results)} PASS")
sys.exit(0 if all(results) else 1)
