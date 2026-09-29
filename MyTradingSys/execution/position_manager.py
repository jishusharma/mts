"""
MyTradingSys/execution/position_manager.py  (G1, T050 - Opus 5.5, 2026-09-27)
(S3/S6 follow-up, 2026-09-28 - see comments tagged S3/S6 below)

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
  stop not live       -> re-place stop for |pos|; see S3 below for how long this is allowed
                         to keep retrying before flatten_halt fires.

Breakeven / trailing remain refused pre-flight by executor (R4); nothing here moves
the stop PRICE.

S3 (G-d, 2026-09-28): the old code allowed exactly one re-place attempt per
manage() call before flattening (a `replaced_once` flag) - an IMPLICIT time
bound of roughly one poll interval between "stop isn't live" and "still isn't
live -> halt". That is now an EXPLICIT, named, documented bound: MAX_UNPROTECTED_SECONDS
and an `unprotected_since` timestamp (see below). It keeps retrying the
re-place every poll (rather than giving up after exactly one attempt) but
hard-halts once the position has gone unprotected for longer than the bound,
regardless of how many re-place attempts happened in between.
NOTE this bound is per manage() invocation - if position_manager is re-run as
a fresh short-lived process every poll (see
research/fast_track_2026-09-27/S3_SUPERVISION.md for how it is actually kept
alive today), `unprotected_since` resets to None on every new process and
this bound does not carry over between separate invocations. Deribit-side,
the stop_market already placed keeps protecting the position even if this
process is not running at all; what this bound protects against is the
narrower window where the stop is confirmed NOT live and this process IS
running but failing to get a new one accepted.

S6 (orphan-stop sweep): flatten_halt already knew every order's LABEL (stop
and targets, from the journal replay in _plan_orders) as well as its known
order_id. A stop re-place (above) can raise an OrderStateUnknown-style
DeribitError after already resting the new order server-side, leaving
stop["order_id"] None/stale at the moment flatten_halt runs - id-based cancel
can't reach that order. flatten_halt now also sweeps cancel_by_label for the
stop and every known target, using the exact same plan-scoped label
convention executor.py's _xlabel builds (f"{plan_id}:{label}"[:64]).

FIX4 L1 (2026-09-28): the pos==0 "explained" check used to compare
target_filled against the LIVE stop["amount"] - but G1 shrinks that amount
every time a target fills, so a partial target fill followed by a manual
close of the (already-shrunk) remainder was wrongly counted as "explained",
even though it never covered the original entry fill. explained is now
`stop_fired or target_filled >= entry_filled_total`, where entry_filled_total
is the ORIGINAL entry fill total reconstructed from the journal's
order_filled events on entry orders (falling back to the largest amount ever
seen on the stop - i.e. its first placement, before any shrink - only if no
entry fill was journaled at all, which should not happen in normal use).

Run (after executor returned status entry_filled_stop_placed):
  python MyTradingSys/execution/position_manager.py <plan_id> [--max-seconds N] [--once]
"""
import sys
sys.dont_write_bytecode = True

import os
import time
import argparse
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deribit_orders as do  # noqa: E402
import journal  # noqa: E402
import pm_heartbeat  # noqa: E402

POLL_INTERVAL_SECONDS = 2
LIVE_STOP_STATES = {"untriggered", "open"}
# S3: how long a live position may go with no live server-side stop covering
# it before position_manager gives up retrying and flattens. Set to match the
# effective bound the old one-attempt-then-halt logic already gave in the
# common case: up to one poll interval to notice the stop isn't live, plus
# one more poll interval before the next check - ~2 x POLL_INTERVAL_SECONDS.
# Documented here as a named constant instead of left implicit in a retry
# counter.
MAX_UNPROTECTED_SECONDS = 2 * POLL_INTERVAL_SECONDS  # 4s
# Time exit: retry a FAILED time-exit close no more often than this (the stop stays live meanwhile).
TIME_EXIT_RETRY_SECONDS = 10
PLANS_DIR = Path(__file__).resolve().parent / "plans"
HALT_PATH = Path(__file__).resolve().parent / "HALT"  # FIX3 M5: same file executor preflight refuses on


class ManagerHalted(Exception):
    """Operator attention required."""


def _plan_orders(plan_id):
    """From the journal: entry side, stop order (id, label, amount, trigger), target order ids,
    and (FIX4 L1) the ORIGINAL entry fill total - see the FIX4 L1 docstring note above."""
    stop, targets, entries, entry_side = None, {}, {}, None
    max_stop_amount_ever = 0  # FIX4 L1 fallback: the largest amount the stop was EVER journaled at
    for ev in journal.read_events(plan_id):
        d, t = ev["data"], ev["event_type"]
        if t == "order_placed":
            lab = d.get("label", "")
            if lab.startswith("stop"):
                stop = {"order_id": d["order_id"], "label": lab, "amount": d["amount"],
                        "trigger": d.get("trigger_price"), "side": d["side"]}
                max_stop_amount_ever = max(max_stop_amount_ever, d["amount"])
            elif lab.startswith("target"):
                targets[d["order_id"]] = {"label": lab, "amount": d["amount"], "filled": 0}
            elif lab.startswith("entry"):
                entry_side = d["side"]
                entries[d["order_id"]] = {"label": lab, "filled": 0}
        elif t == "stop_resized" and stop and d.get("order_id") == stop["order_id"]:
            stop["amount"] = d["amount"]
            stop["trigger"] = d.get("new_stop_price", stop["trigger"])
            max_stop_amount_ever = max(max_stop_amount_ever, d["amount"])
        elif t == "stop_replaced" and stop:
            stop["order_id"] = d["order_id"]
            stop["amount"] = d["amount"]
            max_stop_amount_ever = max(max_stop_amount_ever, d["amount"])
        elif t == "order_filled" and stop and d.get("order_id") == stop["order_id"]:
            stop["filled"] = d["filled_amount"]
        elif t == "order_filled" and d.get("order_id") in targets:
            targets[d["order_id"]]["filled"] = d["filled_amount"]
        elif t == "order_filled" and d.get("order_id") in entries:
            entries[d["order_id"]]["filled"] = d["filled_amount"]
    entry_filled_total = sum(e["filled"] for e in entries.values())
    if not entry_filled_total:
        # no entry order_filled event was journaled (should not happen in
        # normal use - executor always journals the fill that triggers the
        # first stop placement) - fall back to the stop's largest-ever
        # amount rather than 0, which would make "explained" trivially False.
        entry_filled_total = max_stop_amount_ever
    return stop, targets, entry_side, entry_filled_total


def _reduce_fills(plan_id, instrument, is_long, token):
    """Total amount of this plan's reduce-side fills, from
    private/get_user_trades_by_instrument_and_time filtered on the plan label
    prefix and the exit direction. None if the lookup itself fails (-> halt)."""
    events = journal.read_events(plan_id)
    t0 = min((e["ts"] for e in events), default=time.time())
    exit_dir = "sell" if is_long else "buy"
    try:
        trades = do.get_user_trades_by_instrument_and_time(
            token, instrument, int((t0 - 3600) * 1000), int((time.time() + 60) * 1000))
    except do.DeribitError:
        return None
    return sum(int(t.get("amount") or 0) for t in trades
               if str(t.get("label") or "").startswith(f"{plan_id}:")
               and str(t.get("direction")).lower() == exit_dir)


def _plan_max_hold_minutes(plan_id):
    """Plan field max_hold_minutes (> 0) or None. Missing / unreadable / invalid -> None (no time exit)."""
    try:
        import json
        v = json.loads((PLANS_DIR / f"{plan_id}.json").read_text(encoding="utf-8")).get("max_hold_minutes")
        v = float(v)
        return v if v > 0 else None
    except Exception:  # noqa: BLE001
        return None


def _entry_fill_ts(plan_id):
    """Journal timestamp of the first entry-order fill (the moment the hold clock starts), or None."""
    entries = set()
    for ev in journal.read_events(plan_id):
        d = ev["data"]
        if ev["event_type"] == "order_placed" and str(d.get("label", "")).startswith("entry"):
            entries.add(d["order_id"])
        elif ev["event_type"] == "order_filled" and d.get("order_id") in entries and d.get("filled_amount"):
            return ev["ts"]
    return None


def _signed(size):
    return int(size or 0)


def manage(plan_id, instrument="BTC-PERPETUAL", max_seconds=None, once=False, token=None):
    """Heartbeat wrapper: file exists for exactly the lifetime of the manager
    (removed in finally on every exit path: return, ManagerHalted, any exception)."""
    try:  # a plan journaled in the other environment stays untouched: no journal write, no heartbeat
        journal.assert_env(plan_id, do.active_env())
    except journal.EnvMismatch as e:
        raise ManagerHalted(str(e))
    try:  # a heartbeat failure must never stop position protection
        pm_heartbeat.write_heartbeat(plan_id, account=os.environ.get("MTS_ACCOUNT") or None)
    except Exception as he:  # noqa: BLE001
        print(f"WARNING: could not write heartbeat ({he!r})")
    try:
        return _manage_impl(plan_id, instrument, max_seconds, once, token)
    finally:
        try:
            pm_heartbeat.remove_heartbeat(plan_id)
        except Exception as he:  # noqa: BLE001
            print(f"WARNING: could not remove heartbeat ({he!r})")


def _manage_impl(plan_id, instrument="BTC-PERPETUAL", max_seconds=None, once=False, token=None):
    belief = journal.reconstruct_belief(plan_id)
    if belief["halted"]:
        raise ManagerHalted(f"plan {plan_id} already halted: {belief['halt_reason']}")
    stop, targets, entry_side, entry_filled_total = _plan_orders(plan_id)
    if stop is None or entry_side is None:
        raise ManagerHalted(f"plan {plan_id}: journal has no entry/stop - nothing to manage")
    is_long = entry_side == "BUY"
    token = token or do.authenticate()
    unprotected_since = None  # S3: set when a poll first observes the stop not live
    t_end = time.time() + max_seconds if max_seconds else None
    max_hold_s = (_plan_max_hold_minutes(plan_id) or 0) * 60 or None
    entry_ts = _entry_fill_ts(plan_id) if max_hold_s else None
    time_exit_pending = False   # a time-exit close was attempted: a later flat is explained by it
    last_te_try = None

    def time_exit(elapsed):
        """Close-first time exit (same ordering as kill_switch): reduce-only market close, verify flat,
        and ONLY THEN cancel stop + targets. Returns the result dict, or None if the close did not
        confirm flat (stop and targets are left untouched; no HALT)."""
        nonlocal time_exit_pending
        time_exit_pending = True
        journal.append_event(plan_id, "time_exit_start", {"elapsed_s": round(elapsed, 1),
                                                          "max_hold_s": max_hold_s, "by": "position_manager"})
        try:
            c = do.close_position(token, instrument)
            journal.append_event(plan_id, "order_placed", {"order_id": c["order"]["order_id"],
                                                           "label": "time_exit_close",
                                                           "side": "SELL" if is_long else "BUY",
                                                           "amount": c["order"].get("filled_amount")})
        except Exception as xe:  # noqa: BLE001 - e.g. OrderStateUnknown: the re-read decides
            journal.append_event(plan_id, "error", {"context": "time_exit:close_position", "error": repr(xe)})
        try:
            size = _signed(do.get_position(token, instrument).get("size"))
        except Exception as pe:  # noqa: BLE001
            journal.append_event(plan_id, "error", {"context": "time_exit:get_position", "error": repr(pe)})
            size = None
        if size != 0:
            journal.append_event(plan_id, "error", {"context": "time_exit_failed",
                                                    "error": f"position {size} after time-exit close - STOP KEPT"})
            print(f"!!! TIME EXIT FAILED for {plan_id}: position {size} not flat - stop + targets left in "
                  f"place, retrying in {TIME_EXIT_RETRY_SECONDS}s", flush=True)
            return None
        # flat confirmed: now (and only now) remove stop + targets
        for oid in list(targets) + ([stop["order_id"]] if stop["order_id"] else []):
            try:
                do.cancel(token, oid)
                journal.append_event(plan_id, "order_cancelled", {"order_id": oid, "reason": "time_exit"})
            except Exception:  # noqa: BLE001 - already gone / best effort; position is flat
                pass
        for lab in [stop["label"]] + [t["label"] for t in targets.values()]:
            try:
                do.cancel_by_label(token, f"{plan_id}:{lab}"[:64])
            except Exception:  # noqa: BLE001
                pass
        tf = sum(t["filled"] for t in targets.values())
        journal.append_event(plan_id, "time_exit", {"elapsed_s": round(elapsed, 1), "max_hold_s": max_hold_s})
        journal.append_event(plan_id, "reconciliation", {"result": "position_closed", "stop_state": "time_exit",
                                                         "target_filled": tf})
        return {"plan_id": plan_id, "status": "closed", "stop_state": "time_exit", "target_filled": tf,
                "reason": "time_exit"}

    def flatten_halt(reason):
        journal.append_event(plan_id, "mismatch_halt", {"reason": reason, "by": "position_manager"})
        try:  # FIX3 M5: write the manual HALT first so the halt survives this process
            HALT_PATH.write_text(f"{datetime.now(timezone.utc).isoformat()} position_manager {plan_id}: "
                                 f"{reason}\n", encoding="utf-8")
        except Exception as he:  # noqa: BLE001
            print(f"WARNING: could not write HALT ({he!r})")

        def _quiet(fn, *a):
            # FIX3 H1: one failing cancel must never skip the flatten
            try:
                fn(*a)
            except Exception as ce:  # noqa: BLE001
                journal.append_event(plan_id, "error", {"context": f"manager_flatten:{fn.__name__}",
                                                        "error": repr(ce)})

        # FIX3 C3 order: targets -> close position -> verify flat -> stop LAST.
        # S6: sweep by the plan-scoped label as well as by id - a re-place can
        # rest an order whose id was never recorded.
        for oid in list(targets):
            _quiet(do.cancel, token, oid)
        for tg in targets.values():
            _quiet(do.cancel_by_label, token, f"{plan_id}:{tg['label']}"[:64])
        try:
            try:
                size = _signed(do.get_position(token, instrument).get("size"))
            except Exception as pe:  # noqa: BLE001 - position unknown: attempt the close anyway
                journal.append_event(plan_id, "error", {"context": "manager_flatten:get_position",
                                                        "error": repr(pe)})
                size = None
            if size != 0:
                try:
                    c = do.close_position(token, instrument)
                    journal.append_event(plan_id, "order_placed", {"order_id": c["order"]["order_id"],
                                                                   "label": "emergency_close",
                                                                   "side": "SELL" if is_long else "BUY",
                                                                   "amount": c["order"]["filled_amount"]})
                except Exception as xe:  # noqa: BLE001 - e.g. OrderStateUnknown: the re-read decides
                    journal.append_event(plan_id, "error", {"context": "manager_flatten:close_position",
                                                            "error": repr(xe)})
                size = _signed(do.get_position(token, instrument).get("size"))
            if size != 0:
                raise ManagerHalted(f"position still {size} after close_position - stop left in place")
        except Exception as e:  # noqa: BLE001
            journal.append_event(plan_id, "error", {"context": "manager_flatten", "error": repr(e)})
            raise ManagerHalted(f"FLATTEN ITSELF FAILED ({e}) after: {reason} - CHECK EXCHANGE UI NOW")
        # flat confirmed: now (and only now) remove the protective stop
        if stop["order_id"]:
            _quiet(do.cancel, token, stop["order_id"])
        _quiet(do.cancel_by_label, token, f"{plan_id}:{stop['label']}"[:64])
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
            # FIX4 L1: compare against the ORIGINAL entry fill total, not the
            # live stop["amount"] - G1 shrinks that amount on every target
            # fill, so it under-counts what a manual close needs to explain.
            stop_state_out = stop_state
            explained = stop_fired or target_filled >= entry_filled_total or time_exit_pending
            if not explained and str(stop_state).startswith("query_failed"):
                # Deribit archives / re-ids a triggered stop, so get_order_state
                # answers order_not_found. Fall back to this plan's own reduce-side
                # fills (trades labelled "<plan_id>:..." opposite to the entry).
                rf = _reduce_fills(plan_id, instrument, is_long, token)
                if rf is not None and rf >= entry_filled_total:
                    explained = True
                    stop_state_out = "triggered_by_fills"
                    target_filled = max(target_filled, rf)
            if not explained:
                journal.append_event(plan_id, "mismatch_halt",
                                     {"reason": "position flat but no stop trigger / target fill explains it "
                                                "(manual close?)", "by": "position_manager",
                                      "stop_state": stop_state, "target_filled": target_filled})
                raise ManagerHalted(f"plan {plan_id}: unexplained flat (manual close?) - halted")
            journal.append_event(plan_id, "reconciliation", {"result": "position_closed",
                                                             "stop_state": stop_state_out,
                                                             "target_filled": target_filled})
            return {"plan_id": plan_id, "status": "closed", "stop_state": stop_state_out,
                    "target_filled": target_filled}

        if (pos > 0) != is_long:
            flatten_halt(f"position sign flipped: size {pos} on a {'long' if is_long else 'short'} plan")

        if max_hold_s and entry_ts is not None:
            elapsed = time.time() - entry_ts
            if elapsed > max_hold_s and (last_te_try is None or time.time() - last_te_try >= TIME_EXIT_RETRY_SECONDS):
                last_te_try = time.time()
                res = time_exit(elapsed)
                if res is not None:
                    return res
                # close not confirmed: fall through - the stop-protection logic below keeps running

        size = abs(pos)
        if str(stop_state).startswith("query_failed"):
            # FIX3 H5: we could not READ the stop - it may well still be live.
            # Never re-place (that stacks duplicate stops and loses the old
            # id). Count it as unprotected time; flatten only once
            # MAX_UNPROTECTED_SECONDS of consecutive failures have passed
            # (flatten_halt keeps the stop until the close is confirmed).
            now = time.monotonic()
            if unprotected_since is None:
                unprotected_since = now
            elapsed = now - unprotected_since
            if elapsed > MAX_UNPROTECTED_SECONDS:
                flatten_halt(f"stop state unreadable ({stop_state}) for {elapsed:.1f}s > "
                             f"MAX_UNPROTECTED_SECONDS={MAX_UNPROTECTED_SECONDS}s, |pos|={size}")
        elif stop_state not in LIVE_STOP_STATES:
            # S3: explicit, named bound on how long |position| may go
            # unprotected, replacing the old implicit "one re-place attempt"
            # counter. unprotected_since is only cleared once a poll actually
            # OBSERVES the stop live again (the `else` branch below) - a
            # re-place CALL succeeding here is not proof of that; it is only
            # confirmed on the next poll's fresh order_state read.
            now = time.monotonic()
            if unprotected_since is None:
                unprotected_since = now
            elapsed = now - unprotected_since
            if elapsed > MAX_UNPROTECTED_SECONDS:
                flatten_halt(f"position unprotected (no live stop, state={stop_state}) for "
                             f"{elapsed:.1f}s > MAX_UNPROTECTED_SECONDS={MAX_UNPROTECTED_SECONDS}s, "
                             f"|pos|={size}")
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
        else:
            unprotected_since = None
            if size != stop["amount"]:
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
    ap.add_argument("--mainnet", action="store_true", help="MAINNET (typed confirmation required)")
    a = ap.parse_args()
    try:
        if a.mainnet:
            do.select_environment(True)
    except RuntimeError as e:
        print(f"REFUSED: {e}")
        return 1
    try:
        print(manage(a.plan_id, max_seconds=a.max_seconds, once=a.once))
        return 0
    except ManagerHalted as e:
        print(f"HALTED: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
