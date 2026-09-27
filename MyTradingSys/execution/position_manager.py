"""
MyTradingSys/execution/position_manager.py  (G1, T050 - Opus 5.5, 2026-09-27)

Post-entry management for a plan that executor.execute_plan() has entered.
executor v2 guarantees protection up to the moment it returns; this module
keeps the same invariant for the life of the position:

    INVARIANT: while |position| > 0 there is exactly one live server-side
    reduce-only stop_market for this plan whose amount == |position|.
    Otherwise the position is flattened and the run halts.

Exchange position size is the source of truth. Order states are only used
for journaling (how a stop/target fill shows up in Deribit order states after
trigger is NOT relied on - unverified).

Per poll:
  pos == 0            -> cancel leftover plan orders (targets/stop), journal the close.
                         If the close is not explained by observed stop/target fills
                         (someone closed by hand) -> mismatch_halt (G2 semantics).
  sign flipped        -> fail-closed flatten + halt (should be impossible with reduce_only).
  |pos| < stop amount -> edit stop amount down to |pos|   (G1: shrink on target fill)
  |pos| > stop amount -> edit stop amount up to cover, then mismatch_halt (someone added size)
  stop not live       -> re-place stop for |pos| once; if that fails -> flatten + halt

Breakeven / trailing remain refused pre-flight by executor (R4); nothing here moves
the stop PRICE.

Run (after executor returned status entry_filled_stop_placed):
  python MyTradingSys/execution/position_manager.py <plan_id> [--max-seconds N] [--once]
"""
import sys
sys.dont_write_bytecode = True

import time
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deribit_orders as do  # noqa: E402
import journal  # noqa: E402

POLL_INTERVAL_SECONDS = 2
LIVE_STOP_STATES = {"untriggered", "open"}


class ManagerHalted(Exception):
    """Operator attention required."""


def _plan_orders(plan_id):
    """From the journal: entry side, stop order (id, label, amount, trigger), target order ids."""
    stop, targets, entry_side, entry_filled = None, {}, None, 0
    for ev in journal.read_events(plan_id):
        d, t = ev["data"], ev["event_type"]
        if t == "order_placed":
            lab = d.get("label", "")
            if lab.startswith("stop"):
                stop = {"order_id": d["order_id"], "label": lab, "amount": d["amount"],
                        "trigger": d.get("trigger_price"), "side": d["side"]}
            elif lab.startswith("target"):
                targets[d["order_id"]] = {"label": lab, "amount": d["amount"], "filled": 0}
            elif lab.startswith("entry"):
                entry_side = d["side"]
        elif t == "stop_resized" and stop and d.get("order_id") == stop["order_id"]:
            stop["amount"] = d["amount"]
            stop["trigger"] = d.get("new_stop_price", stop["trigger"])
        elif t == "stop_replaced" and stop:
            stop["order_id"] = d["order_id"]
            stop["amount"] = d["amount"]
        elif t == "order_filled" and stop and d.get("order_id") == stop["order_id"]:
            stop["filled"] = d["filled_amount"]
        elif t == "order_filled" and d.get("order_id") in targets:
            targets[d["order_id"]]["filled"] = d["filled_amount"]
    return stop, targets, entry_side


def _signed(size):
    return int(size or 0)


def manage(plan_id, instrument="BTC-PERPETUAL", max_seconds=None, once=False, token=None):
    belief = journal.reconstruct_belief(plan_id)
    if belief["halted"]:
        raise ManagerHalted(f"plan {plan_id} already halted: {belief['halt_reason']}")
    stop, targets, entry_side = _plan_orders(plan_id)
    if stop is None or entry_side is None:
        raise ManagerHalted(f"plan {plan_id}: journal has no entry/stop - nothing to manage")
    is_long = entry_side == "BUY"
    token = token or do.authenticate()
    replaced_once = False
    t_end = time.time() + max_seconds if max_seconds else None

    def flatten_halt(reason):
        journal.append_event(plan_id, "mismatch_halt", {"reason": reason, "by": "position_manager"})
        try:
            for oid in list(targets) + [stop["order_id"]]:
                try:
                    do.cancel(token, oid)
                except do.DeribitError:
                    pass
            if _signed(do.get_position(token, instrument).get("size")) != 0:
                c = do.close_position(token, instrument)
                journal.append_event(plan_id, "order_placed", {"order_id": c["order"]["order_id"],
                                                               "label": "emergency_close",
                                                               "side": "SELL" if is_long else "BUY",
                                                               "amount": c["order"]["filled_amount"]})
        except Exception as e:  # noqa: BLE001
            journal.append_event(plan_id, "error", {"context": "manager_flatten", "error": repr(e)})
            raise ManagerHalted(f"FLATTEN ITSELF FAILED ({e}) after: {reason} - CHECK EXCHANGE UI NOW")
        raise ManagerHalted(f"flattened + halted: {reason}")

    while True:
        pos = _signed(do.get_position(token, instrument).get("size"))
        # journal target fills we can see (audit only; position is the truth)
        for oid, tg in targets.items():
            try:
                st = do.get_order_state(token, oid)
            except do.DeribitError:
                continue
            fa = int(st.get("filled_amount") or 0)
            if fa != tg["filled"]:
                tg["filled"] = fa
                journal.append_event(plan_id, "order_filled", {"order_id": oid, "filled_amount": fa,
                                                               "order_state": st.get("order_state"),
                                                               "average_price": st.get("average_price")})
        try:
            sst = do.get_order_state(token, stop["order_id"])
        except do.DeribitError as e:
            sst = {"order_state": f"query_failed:{e.error}"}
        stop_state = sst.get("order_state")
        sfa = int(sst.get("filled_amount") or 0)
        if sfa != stop.get("filled", 0):
            stop["filled"] = sfa
            journal.append_event(plan_id, "order_filled", {"order_id": stop["order_id"], "filled_amount": sfa,
                                                           "order_state": stop_state,
                                                           "average_price": sst.get("average_price")})

        if pos == 0:
            target_filled = sum(t["filled"] for t in targets.values())
            stop_fired = stop_state not in LIVE_STOP_STATES and not str(stop_state).startswith("query_failed")
            for oid in list(targets) + ([stop["order_id"]] if stop_state in LIVE_STOP_STATES else []):
                try:
                    do.cancel(token, oid)
                    journal.append_event(plan_id, "order_cancelled", {"order_id": oid, "reason": "position_flat"})
                except do.DeribitError:
                    pass
            explained = stop_fired or target_filled >= stop["amount"]
            if not explained:
                journal.append_event(plan_id, "mismatch_halt",
                                     {"reason": "position flat but no stop trigger / target fill explains it "
                                                "(manual close?)", "by": "position_manager",
                                      "stop_state": stop_state, "target_filled": target_filled})
                raise ManagerHalted(f"plan {plan_id}: unexplained flat (manual close?) - halted")
            journal.append_event(plan_id, "reconciliation", {"result": "position_closed",
                                                             "stop_state": stop_state,
                                                             "target_filled": target_filled})
            return {"plan_id": plan_id, "status": "closed", "stop_state": stop_state,
                    "target_filled": target_filled}

        if (pos > 0) != is_long:
            flatten_halt(f"position sign flipped: size {pos} on a {'long' if is_long else 'short'} plan")

        size = abs(pos)
        if stop_state not in LIVE_STOP_STATES:
            if replaced_once:
                flatten_halt(f"stop not live again ({stop_state}) with |pos|={size}")
            replaced_once = True
            try:
                o = do.stop_market(token, instrument, stop["side"], size, stop["trigger"],
                                   f"{plan_id}:{stop['label']}"[:64])
            except do.DeribitError as e:
                flatten_halt(f"stop not live ({stop_state}) and re-place failed: {e.error}")
            stop["order_id"], stop["amount"], stop["filled"] = o["order"]["order_id"], size, 0
            journal.append_event(plan_id, "stop_replaced", {"order_id": stop["order_id"], "amount": size,
                                                            "trigger_price": stop["trigger"],
                                                            "previous_state": stop_state})
            journal.append_event(plan_id, "order_placed", {"order_id": stop["order_id"], "label": stop["label"],
                                                           "side": stop["side"], "amount": size,
                                                           "trigger_price": stop["trigger"]})
        elif size != stop["amount"]:
            grew = size > stop["amount"]
            try:
                do.edit(token, stop["order_id"], amount=size, trigger_price=stop["trigger"])
            except do.DeribitError as e:
                flatten_halt(f"stop resize {stop['amount']}->{size} failed: {e.error}")
            journal.append_event(plan_id, "stop_resized", {"order_id": stop["order_id"], "amount": size,
                                                           "new_stop_price": stop["trigger"],
                                                           "reason": "position_grew" if grew else "target_fill"})
            stop["amount"] = size
            if grew:
                journal.append_event(plan_id, "mismatch_halt",
                                     {"reason": f"position grew to {size} outside the plan - stop resized to "
                                                f"cover, manager halted", "by": "position_manager"})
                raise ManagerHalted(f"plan {plan_id}: position grew outside plan; stop covers {size}; halted")

        if once or (t_end and time.time() >= t_end):
            return {"plan_id": plan_id, "status": "managing", "position": pos, "stop_amount": stop["amount"],
                    "stop_state": stop_state}
        time.sleep(POLL_INTERVAL_SECONDS)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan_id")
    ap.add_argument("--max-seconds", type=int, default=None)
    ap.add_argument("--once", action="store_true")
    a = ap.parse_args()
    try:
        print(manage(a.plan_id, max_seconds=a.max_seconds, once=a.once))
        return 0
    except ManagerHalted as e:
        print(f"HALTED: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
