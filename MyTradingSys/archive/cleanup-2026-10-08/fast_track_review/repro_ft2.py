"""Adversarial offline repros for FT-2 staged files. No network, no secrets.
Copies staged *.new (stripped) + deps into a temp dir, swaps deribit_orders
for an in-memory fake (except R-DO which exercises the REAL deribit_orders._call
with _post monkeypatched), runs each case, prints CONFIRMED/NOT REPRODUCED."""
import sys, os, shutil, tempfile, json, importlib, types, socket, time
from pathlib import Path
sys.dont_write_bytecode = True
EX = Path(__file__).resolve().parents[3] / "execution"
TMP = Path(tempfile.mkdtemp(prefix="ft2rev_"))
for f in ["executor", "position_manager", "risk_guard", "daily_loss_guard", "daily_loss_monitor",
          "kill_switch", "soak_report"]:
    shutil.copy(EX / f"{f}.py.new", TMP / f"{f}.py")
for f in ["journal.py", "plan_compiler.py", "deribit_orders.py", "trade_plan_validator.py", "trade_plan_schema.json"]:
    shutil.copy(EX / f, TMP / f)
shutil.copy(TMP / "deribit_orders.py", TMP / "real_deribit_orders.py")
FAKE = r'''
class DeribitError(Exception):
    def __init__(self, method, error):
        self.method=method; self.error=error; self.code=error.get("code") if isinstance(error,dict) else None
        super().__init__(f"{method}: {error}")
class OrderStateUnknown(DeribitError): pass
S = {}
CALLS = []
HOOK = {}
def reset(mark=80000.0):
    S.clear(); S.update(pos=0, orders={}, n=0, mark=mark); CALLS.clear(); HOOK.clear()
def _h(name, *a, **k):
    CALLS.append((name, a, k))
    if name in HOOK: return HOOK[name](*a, **k)
def _new(side, amount, typ, label, reduce_only, trig=None, price=None):
    S["n"] += 1; oid=f"O{S['n']}"
    S["orders"][oid]=dict(order_id=oid, direction=side.lower(), amount=amount, order_type=typ, label=label,
        reduce_only=reduce_only, trigger_price=trig, price=price,
        order_state="untriggered" if typ=="stop_market" else "open", filled_amount=0, average_price=0)
    if typ=="market":
        o=S["orders"][oid]; o["filled_amount"]=amount; o["average_price"]=S["mark"]; o["order_state"]="filled"
        S["pos"] += amount if side.lower()=="buy" else -amount
    return oid
def authenticate(): return "tok"
def get_ticker(instrument_name="BTC-PERPETUAL"): return {"mark_price": S["mark"]}
def _place(side, t, i, amount, typ, price=None, label=None, reduce_only=False, trigger_price=None, trigger=None, **k):
    r=_h(side, i, amount, typ, label=label, reduce_only=reduce_only)
    if r is not None: return r
    return {"order": dict(S["orders"][_new(side, amount, typ, label, reduce_only, trigger_price, price)])}
def buy(t,i,a,typ,price=None,label=None,reduce_only=False,**k): return _place("buy",t,i,a,typ,price,label,reduce_only,**k)
def sell(t,i,a,typ,price=None,label=None,reduce_only=False,**k): return _place("sell",t,i,a,typ,price,label,reduce_only,**k)
def stop_market(t,i,side,amount,trig,label,trigger="mark_price"):
    r=_h("stop_market", side, amount, trig, label)
    if r is not None: return r
    return {"order": dict(S["orders"][_new(side, amount, "stop_market", label, True, trig)])}
def edit(t,oid,amount=None,price=None,trigger_price=None):
    _h("edit", oid, amount); o=S["orders"][oid]
    if amount is not None: o["amount"]=amount
    return {"order": dict(o)}
def cancel(t,oid):
    _h("cancel", oid); o=S["orders"].get(oid)
    if not o or o["order_state"] not in ("open","untriggered"): raise DeribitError("cancel",{"code":11044})
    o["order_state"]="cancelled"; return o
def cancel_by_label(t,label,currency="BTC"):
    _h("cancel_by_label", label); n=0
    for o in S["orders"].values():
        if o["label"]==label and o["order_state"] in ("open","untriggered"): o["order_state"]="cancelled"; n+=1
    return n
def close_position(t,i="BTC-PERPETUAL"):
    r=_h("close_position", i)
    if r is not None: return r
    amt=abs(S["pos"]); side="sell" if S["pos"]>0 else "buy"; oid=_new(side, amt, "market", "x", True)
    return {"order": dict(S["orders"][oid])}
def get_position(t,i="BTC-PERPETUAL"):
    r=_h("get_position", i)
    return r if r is not None else {"size": S["pos"]}
def get_positions(t,currency="BTC",kind="future"):
    r=_h("get_positions")
    return r if r is not None else [{"instrument_name":"BTC-PERPETUAL","size":S["pos"]}]
def get_order_state(t,oid):
    r=_h("get_order_state", oid)
    return r if r is not None else dict(S["orders"][oid])
def get_open_orders(t,instrument_name="BTC-PERPETUAL",type_="all"):
    return [dict(o) for o in S["orders"].values() if o["order_state"] in ("open","untriggered")]
def get_account_summary(t,currency="BTC"):
    r=_h("get_account_summary"); return r if r is not None else {"equity": S.get("equity", 1.0)}
def live_stops(): return [o for o in S["orders"].values() if o["order_type"]=="stop_market" and o["order_state"]=="untriggered"]
'''
(TMP / "deribit_orders.py").write_text(FAKE)
sys.path.insert(0, str(TMP)); os.chdir(TMP)
import deribit_orders as do, journal, executor as ex, position_manager as pm, kill_switch as ks
import daily_loss_monitor as dlm, soak_report as sr
from datetime import datetime, timezone, timedelta

def mkplan(pid, entry=None, targets=None):
    now = datetime.now(timezone.utc)
    return {"plan_id": pid, "account": "main", "instrument": "BTC-PERPETUAL", "side": "LONG",
            "validity": {"start": (now - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                         "end": (now + timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ")},
            "entry": entry or {"type": "market"}, "base_unit": 100,
            "stop": {"type": "fixed_percent", "percent_below_entry": 2.0},
            "targets": targets if targets is not None else [{"amount_percent": 50, "pnl_target_percent": 2.0},
                                                             {"amount_percent": 50, "pnl_target_percent": 5.0}],
            "caps": {"max_notional_usd": 5000, "max_loss_usd": -200, "max_concurrent_orders": 7}}

def run(p): return ex.execute_plan(ex.compile_plan(p), p)
RES = []
def case(name, fn):
    do.reset()
    for f in (ex.HALT_PATH, ex.HALT_DAILY_LOSS_PATH):
        if f.exists(): f.unlink()
    try:
        ok, detail = fn()
    except Exception as e:
        ok, detail = None, f"harness exception {type(e).__name__}: {e}"
    tag = {True: "CONFIRMED", False: "NOT REPRODUCED", None: "ERROR"}[ok]
    RES.append((name, tag)); print(f"[{tag}] {name} :: {detail}")

# R1: transport timeout on entry create escapes fail_closed (no flatten, no halt)
def r1():
    def hook(*a, **k):
        do.S["pos"] += 100            # exchange accepted the order; response lost
        raise socket.timeout("timed out")
    do.HOOK["buy"] = hook
    try:
        run(mkplan("r1")); return False, "returned normally"
    except ex.ExecutionHalted as e:
        return False, f"halted cleanly: {e}"
    except Exception as e:
        closed = any(c[0] == "close_position" for c in do.CALLS)
        return (not closed and do.S["pos"] != 0 and not do.live_stops()), \
            f"escaped {type(e).__name__}; close_position called={closed}; pos={do.S['pos']}; live stops={len(do.live_stops())}"
case("R1 executor: socket.timeout on entry create -> escapes fail_closed, naked position", r1)

# R2: executor fail_closed cancels stop by label BEFORE close_position; close fails -> naked
def r2():
    def st(side, amount, trig, label):
        return None
    # make target placement fine, force verify mismatch after stop placed -> fail_closed
    real_gp = do.get_position
    cnt = {"n": 0}
    def gp(i):
        cnt["n"] += 1
        if cnt["n"] == 2: return {"size": 999}   # verify step sees mismatch
    do.HOOK["get_position"] = gp
    def cp(i): raise do.OrderStateUnknown("private/close_position", {"code": 10050})
    do.HOOK["close_position"] = cp
    try:
        run(mkplan("r2", targets=[]))
    except ex.ExecutionHalted as e:
        msg = str(e)
    order = [c[0] for c in do.CALLS if c[0] in ("cancel_by_label", "close_position")]
    return (do.S["pos"] != 0 and not do.live_stops()), f"call order={order}; pos={do.S['pos']}; live stops={len(do.live_stops())}; halt='{msg[:70]}'"
case("R2 executor fail_closed: stop cancelled (S6 sweep) before flatten; close fails -> naked", r2)

# R3: poll-loop get_order_state DeribitError escapes with filled, unprotected position
def r3():
    def gos(oid):
        raise do.DeribitError("private/get_order_state", {"code": 10028})
    do.HOOK["get_order_state"] = gos
    try:
        run(mkplan("r3")); return False, "returned"
    except ex.ExecutionHalted as e:
        return False, f"halted: {e}"
    except do.DeribitError as e:
        return (do.S["pos"] != 0 and not do.live_stops()), f"escaped DeribitError; pos={do.S['pos']}; live stops={len(do.live_stops())}; close called={any(c[0]=='close_position' for c in do.CALLS)}"
case("R3 executor: get_order_state error in poll loop escapes, filled position has no stop", r3)

# R4: fail_closed: a non-DeribitError on a cancel aborts before close_position
def r4():
    def gp(i):
        if sum(1 for c in do.CALLS if c[0]=="get_position") == 2: return {"size": 999}
    do.HOOK["get_position"] = gp
    def cbl(label): raise ConnectionResetError("reset")
    do.HOOK["cancel_by_label"] = cbl
    try: run(mkplan("r4", targets=[]))
    except ex.ExecutionHalted as e: msg = str(e)
    closed = any(c[0]=="close_position" for c in do.CALLS)
    return (not closed and do.S["pos"] != 0), f"close_position called={closed}; pos={do.S['pos']}; halt='{msg[:60]}'"
case("R4 executor fail_closed: ConnectionResetError in label sweep skips flatten", r4)

# R5: position_manager flatten_halt cancels stop before close; close fails -> naked
def r5():
    run(mkplan("r5", targets=[]))
    s = do.live_stops()[0]
    do.S["pos"] = 300  # position grew -> resize path ok; instead force edit failure
    def ed(oid, amt): raise do.DeribitError("private/edit", {"code": 10009})
    do.HOOK["edit"] = ed
    def cp(i): raise socket.timeout("timed out")
    do.HOOK["close_position"] = cp
    try: pm.manage("r5", once=True, token="tok")
    except pm.ManagerHalted as e: msg = str(e)
    return (do.S["pos"] != 0 and not do.live_stops()), f"pos={do.S['pos']}; live stops={len(do.live_stops())}; halt='{msg[:80]}'"
case("R5 position_manager flatten_halt: stop cancelled first, close fails -> naked", r5)

# R6: position_manager: transient stop-state read failure -> extra stop placed while old one live
def r6():
    run(mkplan("r6", targets=[]))
    def gos(oid): raise do.DeribitError("private/get_order_state", {"code": 10028})
    do.HOOK["get_order_state"] = gos
    pm.POLL_INTERVAL_SECONDS = 0.01
    try: r = pm.manage("r6", max_seconds=0.05, token="tok")
    except pm.ManagerHalted as e: r = str(e)
    n = len(do.live_stops())
    return n >= 2, f"live stops after read failures={n} (sum amount={sum(o['amount'] for o in do.live_stops())}, pos={do.S['pos']}); result={str(r)[:80]}"
case("R6 position_manager: get_order_state failure treated as 'stop not live' -> duplicate stops", r6)
pm.POLL_INTERVAL_SECONDS = 2

# R7: kill_all: get_positions failure in phase 1 raises -> nothing cancelled; CLI never writes HALT
def r7():
    run(mkplan("r7", targets=[]))
    def gps(): raise socket.timeout("timed out")
    do.HOOK["get_positions"] = gps
    halt = TMP / "HALT_r7"
    import deribit_orders
    try:
        ks.main(["--confirm", "KILL"], halt_path=halt); return False, "main returned"
    except Exception as e:
        return bool(not halt.exists() and do.live_stops() and do.S["pos"] != 0), f"escaped {type(e).__name__}; HALT written={halt.exists()}; open orders left={len(do.get_open_orders('t'))}"
case("R7 kill_switch: get_positions failure -> exception, no cancels, no HALT", r7)

# R8: kill_switch CLI: authenticate failure -> no HALT written
def r8():
    halt = TMP / "HALT_r8"
    real = do.authenticate
    do.authenticate = lambda: (_ for _ in ()).throw(RuntimeError("auth down"))
    try:
        ks.main(["--confirm", "KILL"], halt_path=halt); return False, "returned"
    except Exception as e:
        return (not halt.exists()), f"escaped {type(e).__name__}; HALT written={halt.exists()}"
    finally:
        do.authenticate = real
case("R8 kill_switch CLI: authenticate() failure -> HALT never written", r8)

# R9: daily_loss_monitor: kill_all raises -> HALT_DAILY_LOSS not written, run_once raises (loop dies)
def r9():
    st = TMP / "dlm_state_r9.json"; hp = TMP / "HALT_DAILY_LOSS_r9"
    do.S["equity"] = 1.0
    now = datetime.now(timezone.utc)
    dlm.save_state({"date": now.strftime("%Y-%m-%d"), "day_start_equity": 1.0, "breached_today": False}, st)
    do.S["equity"] = 0.99   # -0.01 BTC * 80000 = -800 USD
    do.HOOK["get_positions"] = lambda: (_ for _ in ()).throw(socket.timeout("timed out"))
    try:
        dlm.run_once(do, "tok", state_path=st, halt_path=hp); return False, "returned"
    except Exception as e:
        return (not hp.exists()), f"run_once raised {type(e).__name__}; HALT_DAILY_LOSS written={hp.exists()}"
case("R9 daily_loss_monitor: kill_all failure on breach -> no HALT_DAILY_LOSS, monitor loop dies", r9)

# R10: daily_loss_monitor state file corrupt/partial -> baseline silently reset to current equity
def r10():
    st = TMP / "dlm_state_r10.json"; hp = TMP / "HALT_DAILY_LOSS_r10"
    now = datetime.now(timezone.utc)
    full = json.dumps({"date": now.strftime("%Y-%m-%d"), "day_start_equity": 1.0, "breached_today": False})
    st.write_text(full[:20], encoding="utf-8")   # torn write
    do.S["equity"] = 0.99   # already -800 USD today
    r = dlm.run_once(do, "tok", state_path=st, halt_path=hp)
    return (r["ok"] and not hp.exists()), f"ok={r['ok']} total_pnl={r['total_pnl_usd']} new baseline={r['state']['day_start_equity']}"
case("R10 daily_loss_monitor: torn state file -> baseline reset, -800 USD day not detected", r10)

# R11: HALT_DAILY_LOSS written as UTF-16 (PowerShell 5.1 Out-File) -> UnicodeDecodeError escapes preflight
def r11():
    hp = TMP / "HDL_r11"
    hp.write_bytes(json.dumps({"date": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "reason": "x"}).encode("utf-16"))
    try:
        ex._check_halt_files(TMP / "nohalt", hp); return False, "returned (handled)"
    except UnicodeDecodeError as e:
        return True, f"UnicodeDecodeError escapes _check_halt_files (not in except tuple); execute_plan crashes before orders (fail-stop, not a clean refusal)"
case("R11 executor: UTF-16 HALT_DAILY_LOSS -> UnicodeDecodeError escapes", r11)

# R11b: UTF-8 BOM -> treated as malformed -> blocks (good)
def r11b():
    hp = TMP / "HDL_r11b"
    hp.write_bytes(b"\xef\xbb\xbf" + json.dumps({"date": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "reason": "x"}).encode())
    r = ex._check_halt_files(TMP / "nohalt", hp)
    return (len(r) == 1 and "malformed" in r[0]), f"reasons={r}"
case("R11b executor: UTF-8-BOM HALT_DAILY_LOSS -> blocks as malformed (fail-closed, but mislabels a valid halt)", r11b)

# R12: malformed-but-parseable date -> treated as stale -> NOT blocking (fail-open)
def r12():
    out = []
    for body in [{"date": 20260928}, {"date": datetime.now(timezone.utc).strftime("%Y/%m/%d")},
                 {"date": ""}, {"date": datetime.now(timezone.utc).strftime("%Y-%m-%d") + " "}]:
        hp = TMP / "HDL_r12"; hp.write_text(json.dumps(body), encoding="utf-8")
        out.append((body, len(ex._check_halt_files(TMP / "nohalt", hp))))
    return all(n == 0 for _, n in out), f"(body, n_refusals)={out}"
case("R12 executor: HALT_DAILY_LOSS with non-matching/garbage date -> NOT blocking", r12)

# R13: label truncation collisions
def r13():
    pid = "p" * 51
    a, b = ex._xlabel(pid, "entry_rung_1"), ex._xlabel(pid, "entry_rung_10")
    pid2 = "q" * 63
    c, d, e = ex._xlabel(pid2, "stop_order"), ex._xlabel(pid2, "entry_rung_1"), ex._xlabel(pid2, "target_1")
    pA, pB = "x" * 70 + "A", "x" * 70 + "B"
    f, g = ex._xlabel(pA, "stop_order"), ex._xlabel(pB, "stop_order")
    return (a == b and c == d == e and f == g), f"len51 rung1==rung10:{a==b}; len63 stop==entry==target:{c==d==e}; two 71-char plan_ids share stop label:{f==g}"
case("R13 _xlabel truncation collisions (within plan and across plans)", r13)

# R14: executor never re-checks HALT during the run: HALT created after preflight, remaining ladder rungs still placed
def r14():
    p = mkplan("r14", entry={"type": "ladder", "range": {"low": 70000, "high": 71000}, "rungs": 3, "size_multipliers": [1, 1, 1]}, targets=[])
    placed = {"n": 0}
    def b(i, amount, typ, label=None, reduce_only=False):
        placed["n"] += 1
        if placed["n"] == 1: ex.HALT_PATH.write_text("kill")
        return None
    do.HOOK["buy"] = b
    ex.POLL_INTERVAL_SECONDS = 0
    try: ex.execute_plan(ex.compile_plan(p), p, max_entry_seconds=0)
    except Exception as e: pass
    ex.HALT_PATH.unlink()
    return placed["n"] == 3, f"entry orders placed after HALT appeared mid-run: {placed['n']-1}"
case("R14 executor: HALT written mid-run does not stop remaining entry placement", r14)

# R15: position_manager 'explained' check: manual close after a target fill passes as explained
def r15():
    run(mkplan("r15", targets=[{"amount_percent": 60, "pnl_target_percent": 2.0}, {"amount_percent": 40, "pnl_target_percent": 5.0}]))
    t1 = [o for o in do.S["orders"].values() if o["label"] == "r15:target_1"][0]
    t1["filled_amount"] = 60; t1["order_state"] = "filled"; do.S["pos"] = 40
    pm.manage("r15", once=True, token="tok")         # shrinks stop to 40
    do.S["pos"] = 0                                     # operator closes 40 by hand; stop still untriggered
    r = pm.manage("r15", once=True, token="tok")
    return r.get("status") == "closed", f"result={r} (manual close of 40 accepted as explained because target_filled 60 >= stop amount 40)"
case("R15 position_manager: manual close after partial target fill passes G2 'explained' check", r15)

# R16: soak_report ignores unresolved (orphan) orders in its verdict
def r16():
    jd = TMP / "soakj"; jd.mkdir(exist_ok=True)
    (jd / "p.jsonl").write_text(json.dumps({"ts": 1.0, "plan_id": "p", "event_type": "order_placed",
                                            "data": {"order_id": "O1", "label": "stop_order"}}) + "\n")
    data = sr.load_journal_dir(jd); s = [sr.summarize_plan(r) for r in data.values()]
    v = sr.soak_verdict(s)
    return bool(v["clean"] and s[0]["unresolved_orders"]), f"verdict clean={v['clean']} while unresolved={s[0]['unresolved_orders']}"
case("R16 soak_report: orphan/unresolved orders never make the soak NOT CLEAN", r16)

# R-DO: real deribit_orders._call: transport errors are not DeribitError/OrderStateUnknown
def rdo():
    import real_deribit_orders as rdo_
    def boom(m, p, t=None): raise socket.timeout("timed out")
    rdo_._post = boom
    try:
        rdo_.buy("tok", "BTC-PERPETUAL", 10, "market", label="x")
    except rdo_.DeribitError: return False, "mapped to DeribitError"
    except Exception as e:
        return True, f"private/buy timeout raises {type(e).__name__} (not DeribitError/OrderStateUnknown) - bypasses every `except do.DeribitError`"
case("R-DO deribit_orders: socket timeout on private/buy is not OrderStateUnknown", rdo)

print("\nSUMMARY"); [print(f"  {t:15s} {n}") for n, t in RES]
print("tempdir:", TMP)
