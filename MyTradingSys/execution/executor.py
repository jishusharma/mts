"""
MyTradingSys/execution/executor.py  (v2 - Opus 5.5 review + rewrite, 2026-09-27)

Sends a trade plan to Deribit TESTNET via deribit_orders.py, protects every
fill with a server-side stop, places targets, journals every action.

Invariant (the one rule this file exists to enforce):
    FROM THE MOMENT ANY CONTRACT IS FILLED, A SERVER-SIDE REDUCE-ONLY
    stop_market COVERING THE FULL FILLED SIZE EXISTS - OR THE POSITION IS
    FLATTENED AND THE RUN HALTS.

Review findings fixed vs v1:
  R1 (critical) v1 placed the stop only after ALL entries left 'open' -> a
     filled ladder rung sat unprotected up to MAX_POLL (10 min). v2 places
     the stop on the first fill and resizes it (edit amount) on every new fill.
  R2 = B077: stop is stop_market(trigger=mark_price), not a reduce-only limit.
  R3 = B079: caps_check.within_max_loss is ENFORCED pre-flight (False ->
     refuse). Market entries: estimated with mark pre-flight, re-checked on
     the real fill.
  R4 trailing/breakeven stops: v1 discovered "not implemented" only AFTER
     filling (unprotected position). v2 refuses them pre-flight.
  R5 poll timeout: v1 raised with a live position. v2 cancels unfilled
     entries (plan-scoped label cancel) and keeps the protected position.
  R6 labels are plan-scoped on the exchange ("<plan_id>:<label>") so
     cancel_by_label can never touch another plan. Journal keeps short labels.
  R7 any failure after a fill -> ensure stop, else close_position + halt.
  R8 pre-flight refuses if a position or open orders already exist on the
     instrument (belief would be wrong from the first line otherwise).

Stop price: limit/ladder use the compiler's static stop (the price the cap
check was computed on). Market uses percent off the real average fill.

Out of scope (flagged in handoff): post-entry management (shrinking the stop
when targets fill, breakeven move, trailing). reduce_only prevents the
oversized stop from opening a reverse position.

Run:
    python executor.py <plan.json | compiled.json>          # dry run, prints orders
    python executor.py <plan.json> --go                      # places on TESTNET
"""
import sys
sys.dont_write_bytecode = True

import time
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deribit_orders as do  # noqa: E402
import journal  # noqa: E402
from plan_compiler import compile_plan, snap_price, round_size  # noqa: E402

POLL_INTERVAL_SECONDS = 2
DEFAULT_MAX_ENTRY_SECONDS = 600
UNSUPPORTED_STOPS = ("trailing_stop_metadata_only", "breakeven_metadata_only", "trailing_percent",
                     "breakeven_after_fills")


class ExecutionHalted(Exception):
    """Operator attention required. Never caught silently."""


def _xlabel(plan_id, label):
    return f"{plan_id}:{label}"[:64]


def _place(token, instrument, side, amount, order_type, price=None, label=None, reduce_only=False, **kw):
    fn = do.buy if side == "BUY" else do.sell
    r = fn(token, instrument, amount, order_type, price=price, label=label, reduce_only=reduce_only, **kw)
    return r.get("order", r)


def preflight(compiled: dict, plan: dict = None, mark: float = None) -> list:
    """Returns list of refusal reasons (empty = OK). Pure except for mark."""
    reasons = []
    stop = compiled.get("stop_order") or {}
    st = stop.get("order_type")
    if st in UNSUPPORTED_STOPS or (plan and plan["stop"]["type"] != "fixed_percent"):
        reasons.append(f"stop type {st or plan['stop']['type']} not implemented - refused before any order")
    cc = compiled.get("caps_check", {})
    if cc.get("within_max_loss") is False:
        reasons.append(f"B079: worst_case_loss {compiled.get('worst_case_loss_usd')} exceeds cap {cc.get('max_loss_usd')}")
    if compiled["max_position_size"] > cc.get("max_notional_usd", 0):
        reasons.append(f"size {compiled['max_position_size']} > max_notional_usd {cc.get('max_notional_usd')}")
    if cc.get("within_max_loss") == "unknown_until_fill" and plan and mark:
        est = -round(compiled["max_position_size"] * plan["stop"]["percent_below_entry"] / 100.0, 2)
        if est < cc["max_loss_usd"]:
            reasons.append(f"B079: market est. loss {est} exceeds cap {cc['max_loss_usd']}")
    if plan and "validity" in plan:
        now = datetime.now(timezone.utc)
        s = datetime.fromisoformat(plan["validity"]["start"].replace("Z", "+00:00"))
        e = datetime.fromisoformat(plan["validity"]["end"].replace("Z", "+00:00"))
        if not (s <= now < e):
            reasons.append(f"outside validity window {plan['validity']['start']}..{plan['validity']['end']}")
    return reasons


def execute_plan(compiled: dict, plan: dict = None, instrument: str = "BTC-PERPETUAL",
                 currency: str = "BTC", max_entry_seconds: int = DEFAULT_MAX_ENTRY_SECONDS) -> dict:
    plan_id = compiled["plan_id"]
    if journal.read_events(plan_id):
        raise ExecutionHalted(f"plan_id {plan_id} already has a journal - refusing to re-run (idempotency)")
    mark = do.get_ticker(instrument)["mark_price"]
    reasons = preflight(compiled, plan, mark)
    token = do.authenticate()
    if do.get_position(token, instrument).get("size", 0) != 0 or do.get_open_orders(token, instrument):
        reasons.append("R8: instrument already has a position or open orders - clean account required")
    if reasons:
        raise ExecutionHalted("PREFLIGHT REFUSED: " + " | ".join(reasons))

    journal.append_event(plan_id, "intent", {"compiled": compiled, "mark_at_start": mark})
    stop_spec = compiled["stop_order"]
    stop_side = stop_spec["side"]
    is_long = stop_side == "SELL"
    pct = plan["stop"]["percent_below_entry"] if plan else None

    entries = []   # {order_id, label, filled}
    stop = {"order_id": None, "amount": 0, "trigger": stop_spec.get("price")}

    def ensure_stop(filled_total, avg_fill):
        if stop["trigger"] is None:  # market entry: derive from real fill
            if pct is None:
                raise ExecutionHalted("market entry needs the raw plan (percent) to place a stop")
            stop["trigger"] = snap_price(avg_fill * (1 - pct / 100) if is_long else avg_fill * (1 + pct / 100))
            loss = -round(filled_total * pct / 100.0, 2)
            if loss < compiled["caps_check"]["max_loss_usd"]:
                journal.append_event(plan_id, "error", {"context": "B079_post_fill", "loss": loss})
        m = do.get_ticker(instrument)["mark_price"]
        if (is_long and m <= stop["trigger"]) or (not is_long and m >= stop["trigger"]):
            raise ExecutionHalted(f"mark {m} already through stop {stop['trigger']}")
        if stop["order_id"] is None:
            o = do.stop_market(token, instrument, stop_side, filled_total, stop["trigger"],
                               _xlabel(plan_id, stop_spec["label"]))
            stop["order_id"] = o["order"]["order_id"]
            journal.append_event(plan_id, "order_placed", {"order_id": stop["order_id"], "label": stop_spec["label"],
                                                           "side": stop_side, "amount": filled_total,
                                                           "trigger_price": stop["trigger"]})
        else:
            do.edit(token, stop["order_id"], amount=filled_total, trigger_price=stop["trigger"])
        journal.append_event(plan_id, "stop_resized", {"order_id": stop["order_id"], "amount": filled_total,
                                                       "new_stop_price": stop["trigger"]})
        stop["amount"] = filled_total

    def fail_closed(reason):
        journal.append_event(plan_id, "mismatch_halt", {"reason": reason})
        try:
            for e in entries:
                try:
                    do.cancel(token, e["order_id"])
                except do.DeribitError:
                    pass
            # G-h: an entry whose create call returned an ambiguous code has no
            # order_id in `entries` but may be resting on the book - sweep every
            # entry label server-side so it cannot fill after we flatten.
            for spec in compiled["entry_orders"]:
                try:
                    do.cancel_by_label(token, _xlabel(plan_id, spec["label"]))
                except do.DeribitError:
                    pass
            if do.get_position(token, instrument).get("size", 0) != 0:
                c = do.close_position(token, instrument)
                journal.append_event(plan_id, "order_placed", {"order_id": c["order"]["order_id"], "label": "emergency_close",
                                                               "side": "SELL" if is_long else "BUY",
                                                               "amount": c["order"]["filled_amount"]})
            if stop["order_id"]:
                try:
                    do.cancel(token, stop["order_id"])
                except do.DeribitError:
                    pass
        except Exception as e:  # noqa: BLE001
            journal.append_event(plan_id, "error", {"context": "fail_closed", "error": repr(e)})
            raise ExecutionHalted(f"FAIL-CLOSED ITSELF FAILED ({e}) after: {reason} - CHECK TESTNET UI NOW")
        raise ExecutionHalted(f"flattened + halted: {reason}")

    # --- entries ---
    for spec in compiled["entry_orders"]:
        try:
            o = _place(token, instrument, spec["side"], spec["amount"], spec["order_type"],
                       price=spec.get("price"), label=_xlabel(plan_id, spec["label"]))
        except do.DeribitError as e:
            journal.append_event(plan_id, "order_rejected", {"label": spec["label"], "error": str(e.error)})
            fail_closed(f"entry {spec['label']} rejected: {e.error}")
        entries.append({"order_id": o["order_id"], "label": spec["label"], "filled": 0})
        journal.append_event(plan_id, "order_placed", {"order_id": o["order_id"], "label": spec["label"],
                                                       "side": spec["side"], "amount": spec["amount"]})

    # --- poll: protect every fill immediately ---
    deadline = time.time() + max_entry_seconds
    if plan and "validity" in plan:
        end = datetime.fromisoformat(plan["validity"]["end"].replace("Z", "+00:00")).timestamp()
        deadline = min(deadline, end)
    avg_fill = None
    while True:
        any_open, notional, filled_total = False, 0.0, 0
        for e in entries:
            st = do.get_order_state(token, e["order_id"])
            fa = int(st.get("filled_amount") or 0)
            if fa != e["filled"]:
                e["filled"] = fa
                journal.append_event(plan_id, "order_filled", {"order_id": e["order_id"], "filled_amount": fa,
                                                               "order_state": st.get("order_state"),
                                                               "average_price": st.get("average_price")})
            if st.get("order_state") == "open":
                any_open = True
            if fa:
                notional += fa / float(st["average_price"])  # inverse: contracts / price = BTC
                filled_total += fa
        if filled_total:
            avg_fill = filled_total / notional
        if filled_total > stop["amount"]:
            try:
                ensure_stop(filled_total, avg_fill)
            except (do.DeribitError, ExecutionHalted) as ex:
                fail_closed(f"R7 stop could not be placed/resized: {ex}")
        if not any_open:
            break
        if time.time() >= deadline:
            for e in entries:
                try:
                    do.cancel(token, e["order_id"])
                    journal.append_event(plan_id, "order_cancelled", {"order_id": e["order_id"], "reason": "entry_deadline"})
                except do.DeribitError:
                    pass  # already filled/cancelled
            continue  # one more pass to capture fills that raced the cancel
        time.sleep(POLL_INTERVAL_SECONDS)

    if filled_total == 0:
        journal.append_event(plan_id, "reconciliation", {"result": "no_fill_clean_exit"})
        return {"plan_id": plan_id, "filled_total": 0, "status": "no_fill"}

    # --- verify exchange agrees before targets ---
    pos = do.get_position(token, instrument)
    if abs(pos.get("size", 0)) != filled_total:
        fail_closed(f"position size {pos.get('size')} != believed fills {filled_total}")

    # --- targets, proportional to actual fill ---
    target_ids = []
    remaining = filled_total
    tgts = plan.get("targets", []) if plan else []
    for i, t in enumerate(tgts, start=1):
        amt = remaining if i == len(tgts) else min(remaining, round_size(filled_total * t["amount_percent"] / 100.0))
        if amt < 10:
            continue
        px = snap_price(avg_fill * (1 + t["pnl_target_percent"] / 100) if is_long
                        else avg_fill * (1 - t["pnl_target_percent"] / 100))
        try:
            o = _place(token, instrument, stop_side, amt, "limit", price=px,
                       label=_xlabel(plan_id, f"target_{i}"), reduce_only=True)
        except do.DeribitError as e:
            journal.append_event(plan_id, "order_rejected", {"label": f"target_{i}", "error": str(e.error)})
            continue  # position is still protected by the stop; a missing target is not a safety issue
        target_ids.append(o["order_id"])
        journal.append_event(plan_id, "order_placed", {"order_id": o["order_id"], "label": f"target_{i}",
                                                       "side": stop_side, "amount": amt, "price": px})
        remaining -= amt

    return {"plan_id": plan_id, "filled_total": filled_total, "avg_fill": round(avg_fill, 2),
            "stop_order_id": stop["order_id"], "stop_trigger": stop["trigger"],
            "target_order_ids": target_ids, "status": "entry_filled_stop_placed"}


def load(path: Path):
    d = json.loads(path.read_text(encoding="utf-8"))
    if "entry_orders" in d:
        return d, None
    return compile_plan(d), d


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan_file")
    ap.add_argument("--go", action="store_true", help="actually place orders on TESTNET")
    ap.add_argument("--max-entry-seconds", type=int, default=DEFAULT_MAX_ENTRY_SECONDS)
    args = ap.parse_args()
    compiled, plan = load(Path(args.plan_file))
    if not args.go:
        print(json.dumps(compiled, indent=2))
        print("DRY RUN - add --go to place on testnet")
        return 0
    try:
        print("OK:", json.dumps(execute_plan(compiled, plan, max_entry_seconds=args.max_entry_seconds)))
        return 0
    except ExecutionHalted as e:
        print(f"HALTED: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
