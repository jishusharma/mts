"""
MyTradingSys/execution/reconciler.py  (v2, G2 - Opus 5.5, 2026-09-27)

Compares MTS's belief (journal) with Deribit's actual state. On any mismatch:
journal mismatch_halt and raise. Never auto-corrects (position_manager is the
only component that acts; this one only judges).

v2 changes vs v1:
  - believed position nets ALL fills (entries, stop, targets, emergency_close) by side,
    not entries only (v1's known simplification).
  - stop coverage check: if actual |position| > 0 there must be a live plan stop whose
    amount >= |position| (G1 invariant), else mismatch "unprotected".
  - unknown-order check: any open exchange order whose label starts with "<plan_id>:"
    but whose order_id the journal never recorded -> mismatch.
  - "untriggered" (Deribit's live stop state) == "open" for comparison.
  - fills recorded only in the journal and a fill observed only on the exchange are
    both mismatches (filled_amount compare, unchanged from v1).

Exit test (G2): testnet/run_testnet_suite_g1g2.py case G2a closes the position
behind MTS's back and asserts this raises ReconciliationMismatch.

Run: python MyTradingSys/execution/reconciler.py <plan_id> [--mainnet]
"""
import sys
sys.dont_write_bytecode = True

import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deribit_orders as do  # noqa: E402
import journal  # noqa: E402

LIVE = {"open", "untriggered"}


class ReconciliationMismatch(Exception):
    """Hard halt. Never retried or papered over."""


def _norm(state):
    return "open" if state in LIVE else state


def reconcile(plan_id: str, instrument: str = "BTC-PERPETUAL", currency: str = "BTC", token=None) -> dict:
    journal.assert_env(plan_id, do.active_env())
    belief = journal.reconstruct_belief(plan_id)
    if belief["halted"]:
        return {"status": "already_halted", "reason": belief["halt_reason"]}
    token = token or do.authenticate()
    mismatches, actual_orders = [], {}

    for order_id, b in belief["orders"].items():
        try:
            a = do.get_order_state(token, order_id)
        except do.DeribitError as e:
            mismatches.append({"order_id": order_id, "type": "query_failed", "error": str(e.error)})
            continue
        actual_orders[order_id] = a
        af = int(a.get("filled_amount") or 0)
        if b["label"] == "emergency_close":
            continue  # journaled with its fill in 'amount' (see netting below)
        if af != int(b["filled_amount"] or 0):
            mismatches.append({"order_id": order_id, "label": b["label"], "type": "filled_amount_mismatch",
                               "believed": b["filled_amount"], "actual": af})
        if b["state"] in LIVE and _norm(a.get("order_state")) != "open" and af == int(b["filled_amount"] or 0):
            # journal thinks live, exchange says gone without a fill we didn't know about
            mismatches.append({"order_id": order_id, "label": b["label"], "type": "state_mismatch",
                               "believed": b["state"], "actual": a.get("order_state")})

    # believed net position from journal fills, all order kinds
    believed_position = 0
    for b in belief["orders"].values():
        f = int(b["filled_amount"] or 0)
        if b["label"] == "emergency_close":
            f = int(b["amount"] or 0)  # close_position fills immediately; journaled with its filled amount
        believed_position += f if b["side"] == "BUY" else -f

    try:
        actual_position = int(do.get_position(token, instrument).get("size") or 0)
    except do.DeribitError as e:
        mismatches.append({"type": "position_query_failed", "error": str(e.error)})
        actual_position = None

    if actual_position is not None and believed_position != actual_position:
        mismatches.append({"type": "position_size_mismatch", "believed": believed_position,
                           "actual": actual_position})

    # unknown plan orders on the exchange
    try:
        open_orders = do.get_open_orders(token, instrument)
    except do.DeribitError as e:
        open_orders = []
        mismatches.append({"type": "open_orders_query_failed", "error": str(e.error)})
    prefix = f"{plan_id}:"
    for o in open_orders:
        if str(o.get("label", "")).startswith(prefix) and o["order_id"] not in belief["orders"]:
            mismatches.append({"type": "unknown_plan_order", "order_id": o["order_id"], "label": o.get("label")})

    # G1 invariant: live stop covers the full position
    if actual_position:
        live_stops = [o for o in open_orders if str(o.get("label", "")).startswith(prefix + "stop")
                      and o.get("reduce_only") and _norm(o.get("order_state")) == "open"]
        covered = sum(int(o.get("amount") or 0) for o in live_stops)
        if covered < abs(actual_position):
            mismatches.append({"type": "unprotected_position", "position": actual_position,
                               "live_stop_amount": covered})

    journal.append_event(plan_id, "reconciliation", {"mismatches": mismatches,
                                                     "believed_position": believed_position,
                                                     "actual_position": actual_position})
    if mismatches:
        journal.append_event(plan_id, "mismatch_halt", {"reason": "reconciliation found mismatches",
                                                        "detail": mismatches})
        raise ReconciliationMismatch(f"plan {plan_id}: {len(mismatches)} mismatch(es): {mismatches}")
    return {"status": "reconciled_ok", "believed_position": believed_position, "actual_position": actual_position}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan_id")
    ap.add_argument("--mainnet", action="store_true", help="MAINNET (typed confirmation required)")
    a = ap.parse_args(argv)
    try:
        if a.mainnet:
            try:
                do.select_environment(True)
            except RuntimeError as e:
                print(f"REFUSED: {e}")
                return 1
        print(f"OK: {reconcile(a.plan_id)}")
        return 0
    except ReconciliationMismatch as e:
        print(f"MISMATCH - HALTED: {e}")
        return 1
    except journal.EnvMismatch as e:
        print(f"REFUSED: {e}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
