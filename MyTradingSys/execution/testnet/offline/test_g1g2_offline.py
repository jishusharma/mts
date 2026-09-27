import sys, os, shutil, json
sys.dont_write_bytecode = True
import deribit_orders as do, journal, position_manager as pm, reconciler as rc
journal.JOURNAL_DIR = __import__("pathlib").Path("jr")
res = []
def setup(pid):
    """Simulate what executor v2 leaves behind: long 100 filled, stop 100, targets 50+50."""
    shutil.rmtree("jr", ignore_errors=True); do.reset()
    e = do._new("BUY", 100, "market", f"{pid}:entry_1", False, state="filled"); do.fill(e, 100)
    s = do.stop_market("t", "I", "SELL", 100, 78000, f"{pid}:stop_order")["order"]["order_id"]
    t1 = do._new("SELL", 50, "limit", f"{pid}:target_1", True, price=82000)
    t2 = do._new("SELL", 50, "limit", f"{pid}:target_2", True, price=84000)
    J = journal.append_event
    J(pid, "order_placed", {"order_id": e, "label": "entry_1", "side": "BUY", "amount": 100})
    J(pid, "order_filled", {"order_id": e, "filled_amount": 100, "order_state": "filled"})
    J(pid, "order_placed", {"order_id": s, "label": "stop_order", "side": "SELL", "amount": 100, "trigger_price": 78000})
    J(pid, "order_placed", {"order_id": t1, "label": "target_1", "side": "SELL", "amount": 50})
    J(pid, "order_placed", {"order_id": t2, "label": "target_2", "side": "SELL", "amount": 50})
    return s, t1, t2
def check(name, cond, detail=""):
    res.append(cond); print(("PASS " if cond else "FAIL ") + name, detail)

# T1 reconcile right after entry: OK
s, t1, t2 = setup("p1"); check("T1 reconcile clean after entry", rc.reconcile("p1", token="t")["status"] == "reconciled_ok")
# T2 target_1 fills -> manager shrinks stop to 50; reconcile OK
s, t1, t2 = setup("p2"); do.fill(t1, 50); r = pm.manage("p2", once=True, token="t")
check("T2 G1 stop shrinks on target fill", do.S["orders"][s]["amount"] == 50 and r["stop_amount"] == 50, r)
check("T2b reconcile OK after shrink", rc.reconcile("p2", token="t")["status"] == "reconciled_ok")
# T3 stop triggers after target_1 -> flat, explained, leftovers cancelled, reconcile OK
s, t1, t2 = setup("p3"); do.fill(t1, 50); pm.manage("p3", once=True, token="t"); do.trigger_stop(s)
r = pm.manage("p3", once=True, token="t")
check("T3 stop-out closes cleanly", r["status"] == "closed" and do.S["orders"][t2]["order_state"] == "cancelled" and not do.get_open_orders("t"), r)
check("T3b reconcile OK after stop-out", rc.reconcile("p3", token="t")["status"] == "reconciled_ok")
# T4 G2 manual close behind MTS's back -> reconciler mismatch
s, t1, t2 = setup("p4"); do.S["pos"] = 0
try: rc.reconcile("p4", token="t"); check("T4 G2 forced mismatch detected", False)
except rc.ReconciliationMismatch as e: check("T4 G2 forced mismatch detected", "position_size_mismatch" in str(e))
# T5 manual close -> manager halts as unexplained, cancels leftovers
s, t1, t2 = setup("p5"); do.S["pos"] = 0
try: pm.manage("p5", once=True, token="t"); check("T5 manager halts on manual close", False)
except pm.ManagerHalted as e: check("T5 manager halts on manual close", "unexplained" in str(e) and not do.get_open_orders("t"))
# T6 stop cancelled externally -> re-placed for full size, reconcile OK
s, t1, t2 = setup("p6"); do.cancel("t", s); r = pm.manage("p6", once=True, token="t")
live = [o for o in do.get_open_orders("t") if o["order_type"] == "stop_market"]
check("T6 stop re-placed after external cancel", len(live) == 1 and live[0]["amount"] == 100, r)
try: rc.reconcile("p6", token="t"); check("T6b reconcile flags external cancel", False)
except rc.ReconciliationMismatch as e: check("T6b reconcile flags external cancel", "state_mismatch" in str(e))
# T7 size added outside plan -> stop covers, manager halts
s, t1, t2 = setup("p7"); do.S["pos"] = 150
try: pm.manage("p7", once=True, token="t"); check("T7 grew -> cover + halt", False)
except pm.ManagerHalted as e: check("T7 grew -> cover + halt", do.S["orders"][s]["amount"] == 150)
# T8 unprotected detection: stop amount < position
s, t1, t2 = setup("p8"); do.S["orders"][s]["amount"] = 40
try: rc.reconcile("p8", token="t"); check("T8 unprotected detected", False)
except rc.ReconciliationMismatch as e: check("T8 unprotected detected", "unprotected_position" in str(e))
# T9 unknown plan order
s, t1, t2 = setup("p9"); do._new("BUY", 10, "limit", "p9:rogue", False, price=70000)
try: rc.reconcile("p9", token="t"); check("T9 unknown plan order detected", False)
except rc.ReconciliationMismatch as e: check("T9 unknown plan order detected", "unknown_plan_order" in str(e))
print(f"{sum(res)}/{len(res)} PASS")
