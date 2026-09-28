"""
Testnet proof suite for executor.py v2 (T050 Phase 3/4). TESTNET ONLY.
Each case: clean account -> run -> assert -> teardown. Prints PASS/FAIL per case.
Run: python MyTradingSys/execution/testnet/run_testnet_suite.py
"""
import sys, json, time, uuid
sys.dont_write_bytecode = True
from datetime import datetime, timezone, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import deribit_orders as do, executor as ex, journal
from plan_compiler import compile_plan

I = "BTC-PERPETUAL"

# FIX3 H6: a suite never touches the operator's real HALT files. Refuse to
# start while one exists; fail_closed/flatten_halt (which now write HALT) and
# the daily-loss case write into a per-run temp dir, cleared between cases.
import tempfile, position_manager as pm
for _p in (ex.HALT_PATH, ex.HALT_DAILY_LOSS_PATH):
    if _p.exists():
        sys.exit(f"REFUSED: {_p} exists - an operator halt is active; review and clear it first")
SUITE_TMP = Path(tempfile.mkdtemp(prefix="mts_suite_"))
ex.HALT_PATH = pm.HALT_PATH = SUITE_TMP / "HALT"
ex.HALT_DAILY_LOSS_PATH = SUITE_TMP / "HALT_DAILY_LOSS"

tok = do.authenticate()
results = []

def clean():
    for _p in (ex.HALT_PATH, ex.HALT_DAILY_LOSS_PATH):
        _p.unlink(missing_ok=True)
    do._call("private/cancel_all_by_instrument", {"instrument_name": I, "type": "all"}, tok)
    if do.get_position(tok, I).get("size", 0):
        do.close_position(tok, I)
    time.sleep(0.5)
    assert do.get_position(tok, I)["size"] == 0 and not do.get_open_orders(tok, I)

def plan(pid, side="LONG", entry=None, base=100, stop=2.0, targets=None, caps=None, stype="fixed_percent"):
    now = datetime.now(timezone.utc)
    return {"plan_id": f"{pid[:17]}_{uuid.uuid4().hex[:6]}",  # FIX3 M6: <= 24 chars
            "account": "main", "instrument": I, "side": side,
            "validity": {"start": (now - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                         "end": (now + timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ")},
            "entry": entry or {"type": "market"}, "base_unit": base,
            "stop": ({"type": stype, "percent_below_entry": stop} if stype != "breakeven_after_fills"
                     else {"type": stype, "percent_below_entry": stop, "min_fills_for_breakeven": 2}),
            "targets": targets if targets is not None else [{"amount_percent": 50, "pnl_target_percent": 2.0},
                                                             {"amount_percent": 50, "pnl_target_percent": 5.0}],
            "caps": caps or {"max_notional_usd": 5000, "max_loss_usd": -200, "max_concurrent_orders": 7}}

def case(name, fn):
    clean()
    try:
        ok, detail = fn()
    except Exception as e:
        ok, detail = False, f"{type(e).__name__}: {e}"
    results.append((name, ok, detail))
    print(("PASS " if ok else "FAIL ") + name + " :: " + str(detail))
    clean()

def run(p, **kw):
    return ex.execute_plan(compile_plan(p), p, **kw)

def oo():
    return {o["label"].split(":")[-1]: o for o in do.get_open_orders(tok, I)}

# C1 market long: stop_market + 2 targets resting, sizes match
def c1():
    p = plan("c1_mkt_long"); r = run(p); o = oo(); pos = do.get_position(tok, I)["size"]
    s = o.get("stop_order_pending_fill")
    ok = (pos == 100 and s and s["order_type"] == "stop_market" and s["amount"] == 100 and s["reduce_only"]
          and s["trigger_price"] < r["avg_fill"] and "target_1" in o and "target_2" in o
          and o["target_1"]["amount"] + o["target_2"]["amount"] == 100)
    return ok, {k: (v["order_type"], v["amount"], v.get("trigger_price") or v.get("price")) for k, v in o.items()} | {"pos": pos}

# C2 market short: mirror
def c2():
    p = plan("c2_mkt_short", side="SHORT"); r = run(p); o = oo(); pos = do.get_position(tok, I)["size"]
    s = o.get("stop_order_pending_fill")
    ok = pos == -100 and s and s["direction"] == "buy" and s["trigger_price"] > r["avg_fill"]
    return ok, {"pos": pos, "stop": s and s["trigger_price"], "avg": r["avg_fill"]}

# C3 ladder: rung1 marketable, rungs 2-4 far -> rung1 protected immediately, rest cancelled at deadline
def c3():
    m = do.get_ticker(I)["mark_price"]
    p = plan("c3_ladder", entry={"type": "ladder", "range": {"low": round(m * 0.97), "high": round(m * 1.002)},
                                 "rungs": 4, "size_multipliers": [1, 1, 2, 3]}, base=10, stop=2.0,
             caps={"max_notional_usd": 1000, "max_loss_usd": -50, "max_concurrent_orders": 7})
    r = run(p, max_entry_seconds=12)
    o = oo(); pos = do.get_position(tok, I)["size"]; ev = [e["event_type"] for e in journal.read_events(p["plan_id"])]
    ok = (pos == 10 and r["filled_total"] == 10 and o["stop_order"]["amount"] == 10
          and not any(k.startswith("entry_rung") for k in o) and ev.count("order_cancelled") >= 3)
    return ok, {"pos": pos, "open": list(o), "stop_trigger": r["stop_trigger"]}

# C4 preflight refusals: B079 cap, trailing stop, validity, R8 dirty account - nothing placed
def c4():
    out = {}
    for tag, p in [("B079_cap", plan("c4a", entry={"type": "limit", "price": do.get_ticker(I)["mark_price"] * 0.9},
                                     base=1000, stop=10, caps={"max_notional_usd": 5000, "max_loss_usd": -50, "max_concurrent_orders": 5})),
                   ("trailing", plan("c4b", stype="trailing_percent")),
                   ("market_est_cap", plan("c4c", base=1000, stop=10, caps={"max_notional_usd": 5000, "max_loss_usd": -50, "max_concurrent_orders": 5}))]:
        try:
            run(p); out[tag] = "NOT REFUSED"
        except ex.ExecutionHalted as e:
            out[tag] = "refused" if "PREFLIGHT" in str(e) else str(e)
        except Exception as e:
            out[tag] = f"validator/compiler: {e}"
    do.buy(tok, I, 10, "market", label="dirty")
    try:
        run(plan("c4d")); out["R8"] = "NOT REFUSED"
    except ex.ExecutionHalted as e:
        out["R8"] = "refused" if "R8" in str(e) else str(e)
    nothing_placed = all(not o["label"].startswith("c4") for o in do.get_open_orders(tok, I))
    return all(v == "refused" or v.startswith("validator") for v in out.values()) and nothing_placed, out

# C5 fail-closed: stop placement rejected by exchange after a fill -> flatten + halt, no position left
def c5():
    p = plan("c5_failclosed", targets=[])
    real = do.stop_market
    def boom(*a, **k): raise do.DeribitError("private/sell", {"code": 10009, "message": "forced_by_test"})
    do.stop_market = boom
    try:
        run(p); return False, "not halted"
    except ex.ExecutionHalted as e:
        pos = do.get_position(tok, I)["size"]
        return pos == 0 and "flattened" in str(e), {"halt": str(e)[:110], "pos": pos}
    finally:
        do.stop_market = real

# C6 idempotency: same plan_id twice refused
def c6():
    p = plan("c6_idem", entry={"type": "limit", "price": round(do.get_ticker(I)["mark_price"] * 0.8)}, targets=[])
    r = run(p, max_entry_seconds=3)
    try:
        run(p); return False, "second run allowed"
    except ex.ExecutionHalted as e:
        return "idempotency" in str(e) and r["status"] == "no_fill", r["status"]

for n, f in [("C1 market long", c1), ("C2 market short", c2), ("C3 ladder partial + deadline", c3),
             ("C4 preflight refusals", c4), ("C5 fail-closed flatten", c5), ("C6 idempotency", c6)]:
    case(n, f)
print(f"\n{sum(ok for _, ok, _ in results)}/{len(results)} PASS")
sys.exit(0 if all(ok for _, ok, _ in results) else 1)
