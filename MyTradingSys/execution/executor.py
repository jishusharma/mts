"""
MyTradingSys/execution/executor.py  (v2 - Opus 5.5 review + rewrite, 2026-09-27)
(S1/S6 follow-up, 2026-09-28 - see comments tagged S1/S6 below)

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

S1 (2026-09-28): account-wide notional cap. Each plan's OWN cap
(plan["caps"]["max_notional_usd"]) is already enforced above (see the
"size {..} > max_notional_usd {..}" check in preflight()) - that only bounds
THIS plan in isolation. It says nothing about several simultaneously-live
plans on the same instrument together exceeding one account-wide ceiling.
risk_guard.py.new's check_new_plan_against_cap() adds that ceiling; wired in
below, right after the current position is read for R8 (same read is reused
for both checks - no extra exchange call). plan_compiler's caps_check has no
account-wide field, so the cap value is risk_guard.MAX_ACCOUNT_NOTIONAL_USD.

S6 (2026-09-28, orphan-stop sweep): G-h already taught fail_closed() to sweep
every ENTRY label by cancel_by_label, because an entry-creating call that
raises OrderStateUnknown may have rested an order under that label with no
order_id ever recorded in `entries`. The exact same risk applies to the STOP
(ensure_stop's do.stop_market call) and to every TARGET (the targets loop
below, entered only after fail_closed's definition but built the same
plan-scoped way): the create call can raise OrderStateUnknown having already
rested the order, before this file ever learns its order_id. fail_closed now
also sweeps the stop's compiled label and every target label, so an orphaned
stop or target cannot fill after the position has been flattened and the run
halted.

M8 (single-plan-only): R8 refuses whenever the instrument already has a
position or open orders, so the S1 account cap is effectively "this plan <=
cap" today, and position_manager treats the whole instrument position as this
plan's position. Running two plans on one instrument concurrently needs
per-plan position accounting before R8 may be relaxed.

HALT files (FT-2, 2026-09-28): preflight() now refuses BEFORE any order if
either halt file exists next to this module (same refusal pattern as
B079/R8/S1 cap above - appended to `reasons`, never journaled, so the
plan_id stays retriable once the halt is cleared):
  - HALT: a generic, operator-only manual brake (any content, existence is
    the only thing checked). Nothing in this repo ever writes this file -
    only an operator creates/deletes it by hand.
  - HALT_DAILY_LOSS: written by daily_loss_monitor.py.new on a daily-loss
    breach (see that module's docstring for the exact JSON contract:
    {"date": "YYYY-MM-DD", "reason": str, "ts_iso": str}). FIX4 M2: its mere
    EXISTENCE blocks, whatever the date - a breach at 23:59 UTC must not
    resume trading one minute later at 00:00. A well-formed past-dated file
    refuses with "HALT_DAILY_LOSS from <date> still present - operator must
    review and delete"; only an operator deleting the file resumes trading.
    A file that fails to parse as the documented JSON is treated as blocking
    (fail closed on ambiguity, same stance as R7/S6 above) rather than
    silently ignored.
  Neither module ever deletes either file - by design, same as
  daily_loss_monitor's own halt-file contract: only an operator clears a
  hard halt, so it does not auto-resume.

FIX4 (2026-09-28): M4 re-checks both HALT files immediately before every
order-creating call for the rest of execute_plan's run (entries, stop
create/resize, targets) - not just once in preflight() - so a HALT/kill_all/
daily_loss_monitor write racing a still-in-progress run (a ladder, a slow
poll) is caught before the next order goes out (see _halt_check_mid_run()).
L1 (position_manager): the pos==0 "explained" check now compares target
fills against the ORIGINAL entry filled total (from the journal's
order_filled events on entry orders), not the live stop["amount"] - G1
shrinks the stop on every target fill, so comparing against it let a manual
close of a shrunken remainder pass as "explained". L2: the targets loop now
catches do.OrderStateUnknown separately from a plain do.DeribitError and
sweeps that target's own label (the create call may have rested the order
before the ambiguous response), without reducing `remaining`. L3: a market
entry's post-fill worst-case loss breach (B079, previously journaled only)
now fails closed once the stop is live, per the C3 cancel-order.

Run:
    python executor.py <plan.json | compiled.json>          # dry run, prints orders
    python executor.py <plan.json> --go                      # places on TESTNET
"""
import sys
sys.dont_write_bytecode = True

import re
import time
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deribit_orders as do  # noqa: E402
import journal  # noqa: E402
import mainnet_plan_check  # noqa: E402 - 128: mainnet refuses compiled input / entry sum != max_position_size
import risk_guard  # noqa: E402 - S1: account-wide notional cap
from plan_compiler import compile_plan, snap_price, round_size, CompileError  # noqa: E402

POLL_INTERVAL_SECONDS = 2
DEFAULT_MAX_ENTRY_SECONDS = 600
UNSUPPORTED_STOPS = ("trailing_stop_metadata_only", "breakeven_metadata_only", "trailing_percent",
                     "breakeven_after_fills")
AUTO_TRADER_CONFIG = Path(__file__).resolve().parent / "auto_trader_config.json"
HALT_PATH = Path(__file__).resolve().parent / "HALT"
HALT_DAILY_LOSS_PATH = Path(__file__).resolve().parent / "HALT_DAILY_LOSS"
HALT_DAILY_LOSS_PATH_MAINNET = Path(__file__).resolve().parent / "HALT_DAILY_LOSS_MAINNET"  # PREMAINNET1 H1


def _daily_loss_halt_path() -> Path:
    """Per-env daily-loss halt marker (globals read at call time): a testnet trip must not halt mainnet."""
    return HALT_DAILY_LOSS_PATH_MAINNET if do.active_env() == "mainnet" else HALT_DAILY_LOSS_PATH
PLAN_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,24}$")  # FIX3 M6: labels never truncate/collide
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


SETTLEMENT_IN_PROGRESS = 10041 # Deribit: the 08:00 UTC settlement window is open; entries are refused until it ends


class ExecutionHalted(Exception):
    """Operator attention required. Never caught silently."""


def _xlabel(plan_id, label):
    x = f"{plan_id}:{label}"
    if len(x) > 64:  # FIX3 M6: never slice - a truncated label can collide
        raise ExecutionHalted(f"label {x!r} exceeds 64 chars")
    return x


def write_manual_halt(reason: str, halt_path: Path = None) -> None:
    """FIX3 M5: flatten+halt must survive the process - write execution/HALT
    (the operator-only brake preflight refuses on). Never raises."""
    try:
        (halt_path or HALT_PATH).write_text(
            f"{datetime.now(timezone.utc).isoformat()} executor fail_closed: {reason}\n", encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        print(f"WARNING: could not write HALT ({e!r}) - reason was: {reason}")


def _read_halt_json(path: Path) -> dict:
    """FIX3 M3: PowerShell writes UTF-8-BOM or UTF-16. Raises ValueError/OSError
    on anything that is not a JSON object."""
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "utf-16"):
        try:
            data = json.loads(raw.decode(enc))
            break
        except ValueError:
            continue
    else:
        raise ValueError("not utf-8/utf-16 JSON")
    if not isinstance(data, dict):
        raise ValueError("not a JSON object")
    return data


def _place(token, instrument, side, amount, order_type, price=None, label=None, reduce_only=False, **kw):
    fn = do.buy if side == "BUY" else do.sell
    r = fn(token, instrument, amount, order_type, price=price, label=label, reduce_only=reduce_only, **kw)
    return r.get("order", r)


def _rejection_detail(e) -> dict:
    """Diagnostics merged into every order_rejected event (2026-10-14; plan L-mkt-1012-0945 got 10031 on a market
    entry and the journal kept only str(error), so the cause could not be proven): the structured error (code,
    message, data), the failing method, and `request` - the whitelisted view of what deribit_orders sent (None when
    the failing call is not an order call, or a test double bypassed _place_order). Diagnostics only and never
    raises: a journal helper must not turn a benign target rejection into a fail_closed."""
    try:
        err = getattr(e, "error", None)
        d = {"error_code": getattr(e, "code", None),
             "error_detail": err if isinstance(err, dict) else {"message": str(err)},
             "method": getattr(e, "method", None),
             "request": getattr(e, "request", None)}
        return json.loads(json.dumps(d, default=str))
    except Exception:  # noqa: BLE001
        return {"error_detail": {"message": repr(e)}}


def _check_halt_files(halt_path: Path, halt_daily_loss_path: Path) -> list:
    """HALT-file preflight (FT-2). Returns refusal reasons (empty = OK).
    Impure (filesystem reads) by necessity - see the HALT-files note in this
    module's docstring for the exact contract each file follows."""
    reasons = []
    if halt_path.exists():
        reasons.append("HALT: manual halt file present (execution/HALT) - refused before any order - "
                       "remove HALT after operator review to resume")
    if halt_daily_loss_path.exists():
        try:
            halt_data = _read_halt_json(halt_daily_loss_path)
            halt_date = halt_data.get("date")
            halt_reason = halt_data.get("reason")
        except (ValueError, OSError):
            halt_date, halt_reason = None, None
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        # FIX4 M2: existence blocks, whatever the date - a hard halt does not
        # auto-resume at 00:00 UTC. Only an operator deleting the file resumes
        # trading. A well-formed past date still refuses (with a clearer
        # message that names the date) rather than the FIX3 M1 "stale -
        # warn only" behaviour.
        valid_past = isinstance(halt_date, str) and bool(_DATE_RE.match(halt_date)) and halt_date < today
        if halt_date == today:
            reasons.append(f"HALT_DAILY_LOSS: daily loss halt active ({halt_reason}) - remove "
                           "HALT_DAILY_LOSS after operator review to resume")
        elif valid_past:
            reasons.append(f"HALT_DAILY_LOSS from {halt_date} still present - operator must review and delete")
        else:
            # unparseable contents / bad date: fail closed rather than silently ignore
            reasons.append(f"HALT_DAILY_LOSS: file present but unreadable/malformed (date={halt_date!r}) - "
                           "refused (fail closed) - remove HALT_DAILY_LOSS after operator review to resume")
    return reasons


def _halt_check_mid_run() -> list:
    """FIX4 M4: re-read the same two HALT files, globals read at call time
    (same contract as preflight's _check_halt_files) - executor never checked
    them again after preflight, so an operator/CLI kill_all/daily_loss_monitor
    HALT written mid-run was invisible to every order-creating call after the
    first. Callers re-check this immediately before EVERY order-creating call
    inside execute_plan: each entry and each target. The protective stop is
    never blocked: ensure_stop checks the HALT right AFTER the stop is live."""
    return _check_halt_files(HALT_PATH, _daily_loss_halt_path())


def preflight(compiled: dict, plan: dict = None, mark: float = None,
             halt_path: Path = None, halt_daily_loss_path: Path = None) -> list:
    """Returns list of refusal reasons (empty = OK). Pure except for mark and
    the two HALT-file reads (see _check_halt_files / this module's HALT
    files docstring note). Paths default to the module globals, read at call
    time (FIX3 H6: a suite can redirect HALT_PATH/HALT_DAILY_LOSS_PATH)."""
    reasons = _check_halt_files(halt_path or HALT_PATH, halt_daily_loss_path or _daily_loss_halt_path())
    pid = compiled.get("plan_id")
    if not (isinstance(pid, str) and PLAN_ID_RE.match(pid)):
        reasons.append(f"M6: plan_id {pid!r} must match [A-Za-z0-9_-]{{1,24}}")
    stop = compiled.get("stop_order") or {}
    st = stop.get("order_type")
    if st in UNSUPPORTED_STOPS or (plan and plan["stop"]["type"] != "fixed_percent"):
        reasons.append(f"stop type {st or plan['stop']['type']} not implemented - refused before any order")
    cc = compiled.get("caps_check", {})
    if cc.get("within_max_loss") is False:
        reasons.append(f"B079: worst_case_loss {compiled.get('worst_case_loss_usd')} exceeds cap {cc.get('max_loss_usd')}")
    if compiled["max_position_size"] > cc.get("max_notional_usd", 0):
        reasons.append(f"size {compiled['max_position_size']} > max_notional_usd {cc.get('max_notional_usd')}")
    _mn = getattr(do, "mainnet_plan_refusal", None)  # mainnet-ready gates: hard USD cap, always None on testnet
    if _mn is not None and _mn(compiled["max_position_size"]):
        reasons.append(_mn(compiled["max_position_size"]))
    reasons.extend(mainnet_plan_check.plan_refusals(compiled, plan, do.active_env(), do.MAINNET_MAX_NOTIONAL_USD))
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
    pos = do.get_position(token, instrument)
    if pos.get("size", 0) != 0 or do.get_open_orders(token, instrument):
        reasons.append("R8: instrument already has a position or open orders - clean account required")
    # S1: account-wide notional cap, checked BEFORE this plan's orders are
    # placed. `pos["size"]` is already USD notional for BTC-PERPETUAL (same
    # convention plan_compiler uses for `amount`/`max_position_size`), so
    # account_position_notional(..., mark_price=None) is the right call -
    # it does NOT need a mark-price multiply. Not journaled on refusal: a
    # refused plan_id must stay journal-free so it can be re-run later (the
    # idempotency check above keys off journal.read_events(plan_id)) - the
    # existing B079/R8/validity/trailing refusals all follow the same rule.
    current_notional = risk_guard.account_position_notional(pos.get("size", 0), None)
    cap_result = risk_guard.check_new_plan_against_cap(current_notional, compiled["max_position_size"])
    if not cap_result["ok"]:
        reasons.append(f"S1: {cap_result['reason']}")
    if reasons:
        raise ExecutionHalted("PREFLIGHT REFUSED: " + " | ".join(reasons))

    journal.append_event(plan_id, "intent", {"compiled": compiled, "mark_at_start": mark,
                                             "account_cap_check": cap_result, "env": do.active_env()})
    stop_spec = compiled["stop_order"]
    stop_side = stop_spec["side"]
    is_long = stop_side == "SELL"
    pct = plan["stop"]["percent_below_entry"] if plan else None

    entries = []   # {order_id, label, filled}
    stop = {"order_id": None, "amount": 0, "trigger": stop_spec.get("price")}

    def ensure_stop(filled_total, avg_fill):
        was_market_derived = stop["trigger"] is None  # L3: only a market entry needs the post-fill check below
        if was_market_derived:  # market entry: derive from real fill
            if pct is None:
                raise ExecutionHalted("market entry needs the raw plan (percent) to place a stop")
            # FORMULAS.md 11.1: stop snaps TOWARD entry (LONG->ceil, SHORT->floor)
            # so the realized loss can never exceed the plan's risk budget.
            stop_mode = "ceil" if is_long else "floor"
            stop["trigger"] = snap_price(avg_fill * (1 - pct / 100) if is_long else avg_fill * (1 + pct / 100), stop_mode)
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
        # FIX4 M4 (coordinator review): the protective reduce-only stop is NEVER blocked by a
        # HALT - skipping it would leave a filled position naked if the flatten then failed.
        # The HALT is checked once the stop is live, and fail_closed flattens with it in place.
        halt_reasons = _halt_check_mid_run()
        if halt_reasons:
            raise ExecutionHalted("HALT observed mid-run: " + " | ".join(halt_reasons))
        if was_market_derived:
            # FIX4 L3: the stop is now live, so fail_closed's C3 cancel-order
            # holds - a market entry's real post-fill worst-case loss breach
            # is acted on, not just journaled. Flattening costs the spread;
            # running an over-cap position is worse.
            loss = -round(filled_total * pct / 100.0, 2)
            max_loss = compiled["caps_check"]["max_loss_usd"]
            if loss < max_loss:
                raise ExecutionHalted(f"B079 post-fill: worst-case loss {loss} exceeds cap {max_loss}")

    def fail_closed(reason):
        journal.append_event(plan_id, "mismatch_halt", {"reason": reason})
        write_manual_halt(f"{plan_id}: {reason}")  # FIX3 M5: first, so it survives anything below

        def _quiet(fn, *a):
            # FIX3 H1: any exception in one cancel must never skip the flatten
            try:
                fn(*a)
            except Exception as ce:  # noqa: BLE001
                journal.append_event(plan_id, "error", {"context": f"fail_closed:{fn.__name__}",
                                                        "error": repr(ce)})

        # FIX3 C3 order: cancel entries/targets -> close position -> verify
        # flat -> cancel the stop LAST. If the close fails the stop stays.
        for e in entries:
            _quiet(do.cancel, token, e["order_id"])
        # G-h: an entry whose create call returned an ambiguous code has no
        # order_id in `entries` but may be resting on the book - sweep every
        # entry label server-side so it cannot fill after we flatten.
        for spec in compiled["entry_orders"]:
            _quiet(do.cancel_by_label, token, _xlabel(plan_id, spec["label"]))
        # S6: a target create call can raise OrderStateUnknown having already
        # rested the order - sweep every target label (N from the raw plan,
        # else compiled["target_orders"]).
        n_targets = (len(plan["targets"]) if plan and plan.get("targets")
                    else len(compiled.get("target_orders") or []))
        for i in range(1, n_targets + 1):
            _quiet(do.cancel_by_label, token, _xlabel(plan_id, f"target_{i}"))
        try:
            try:
                size = do.get_position(token, instrument).get("size", 0)
            except Exception as pe:  # noqa: BLE001 - position unknown: attempt the close anyway
                journal.append_event(plan_id, "error", {"context": "fail_closed:get_position", "error": repr(pe)})
                size = None
            if size != 0:
                try:
                    c = do.close_position(token, instrument)
                    journal.append_event(plan_id, "order_placed", {"order_id": c["order"]["order_id"],
                                                                   "label": "emergency_close",
                                                                   "side": "SELL" if is_long else "BUY",
                                                                   "amount": c["order"]["filled_amount"]})
                except Exception as xe:  # noqa: BLE001 - e.g. OrderStateUnknown: the re-read decides
                    journal.append_event(plan_id, "error", {"context": "fail_closed:close_position",
                                                            "error": repr(xe)})
                size = do.get_position(token, instrument).get("size", 0)
            if size != 0:
                raise ExecutionHalted(f"position still {size} after close_position - stop left in place")
        except Exception as e:  # noqa: BLE001
            journal.append_event(plan_id, "error", {"context": "fail_closed", "error": repr(e)})
            raise ExecutionHalted(f"FAIL-CLOSED ITSELF FAILED ({e}) after: {reason} - CHECK TESTNET UI NOW")
        # flat confirmed: now (and only now) remove the protective stop
        if stop["order_id"]:
            _quiet(do.cancel, token, stop["order_id"])
        stop_label = (compiled.get("stop_order") or {}).get("label")
        if stop_label:
            _quiet(do.cancel_by_label, token, _xlabel(plan_id, stop_label))
        raise ExecutionHalted(f"flattened + halted: {reason}")

    # FIX3 C2: any unexpected exception after the intent (a poll read that
    # still fails after retries, a KeyError on a malformed reply, ...) must
    # flatten and halt - never escape with a filled, unprotected position.
    try:
        # --- entries ---
        for spec in compiled["entry_orders"]:
            halt_reasons = _halt_check_mid_run()  # FIX4 M4: re-check right before every entry create
            if halt_reasons:
                fail_closed("HALT observed mid-run: " + " | ".join(halt_reasons))
            try:
                o = _place(token, instrument, spec["side"], spec["amount"], spec["order_type"],
                           price=spec.get("price"), label=_xlabel(plan_id, spec["label"]))
            except do.DeribitError as e:
                journal.append_event(plan_id, "order_rejected", {"label": spec["label"], "error": str(e.error),
                                                                 **_rejection_detail(e)})
                if e.code == SETTLEMENT_IN_PROGRESS and not entries:
                    # 2026-10-15: 10041 settlement_in_progress is a transient exchange state, not a fault. Nothing is placed yet
                    # (no entry, no stop, no position), so skip this plan: no order, no retry, NO HALT. Any other code, or a
                    # rejection after an earlier entry went in, still goes to fail_closed below.
                    journal.append_event(plan_id, "entry_skipped_settlement",
                                         {"label": spec["label"], "error_code": e.code})
                    return {"plan_id": plan_id, "filled_total": 0, "status": "no_fill",
                            "reason": "entry_skipped_settlement"}
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
                except do.DeribitError as ex:
                    # diagnostics: journal the rejected stop create/resize (buy/sell/edit), not a failed mark read
                    if str(getattr(ex, "method", "")).startswith("private/"):
                        journal.append_event(plan_id, "order_rejected", {"label": stop_spec["label"],
                                                                         "error": str(ex.error),
                                                                         **_rejection_detail(ex)})
                    fail_closed(f"R7 stop could not be placed/resized: {ex}")
                except ExecutionHalted as ex:
                    # ensure_stop's own raises (mark-through-stop, FIX4 M4
                    # mid-run HALT, FIX4 L3 B079 post-fill) already carry the
                    # exact reason text - pass it through unprefixed.
                    fail_closed(str(ex))
            if not any_open:
                break
            if time.time() >= deadline:
                for e in entries:
                    try:
                        do.cancel(token, e["order_id"])
                        journal.append_event(plan_id, "order_cancelled", {"order_id": e["order_id"], "reason": "entry_deadline"})
                    except do.DeribitError:
                        pass  # already filled/cancelled
                time.sleep(POLL_INTERVAL_SECONDS)  # L5: never spin when the cancel keeps failing
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
            if i == len(tgts):
                amt = remaining
            else:
                try:
                    amt = min(remaining, round_size(filled_total * t["amount_percent"] / 100.0))
                except CompileError:
                    # FORMULAS.md 11.2: round_size now refuses (rather than
                    # forcing up to the 10 USD minimum) a too-small target
                    # share - skip this target rather than over-size it.
                    continue
            if amt < 10:
                continue
            halt_reasons = _halt_check_mid_run()  # FIX4 M4: re-check right before every target create
            if halt_reasons:
                fail_closed("HALT observed mid-run: " + " | ".join(halt_reasons))
            # FORMULAS.md 11.1: target snaps TOWARD entry (LONG->floor,
            # SHORT->ceil) so it is more likely to fill at the stated price or better.
            target_mode = "floor" if is_long else "ceil"
            px = snap_price(avg_fill * (1 + t["pnl_target_percent"] / 100) if is_long
                            else avg_fill * (1 - t["pnl_target_percent"] / 100), target_mode)
            try:
                o = _place(token, instrument, stop_side, amt, "limit", price=px,
                           label=_xlabel(plan_id, f"target_{i}"), reduce_only=True)
            except do.OrderStateUnknown as e:
                # FIX4 L2: the create call may have already rested the order
                # before the ambiguous response - sweep its own label so it
                # cannot fill unmonitored. `remaining` is NOT reduced: the
                # target's actual fate is unknown, so its share must still be
                # offered to whatever target comes after it.
                journal.append_event(plan_id, "order_rejected", {"label": f"target_{i}", "error": str(e.error),
                                                                 **_rejection_detail(e)})
                try:
                    do.cancel_by_label(token, _xlabel(plan_id, f"target_{i}"))
                except Exception as ce:  # noqa: BLE001 - sweep failure is isolated, not fatal
                    journal.append_event(plan_id, "error", {"context": "target_ambiguous_sweep", "error": repr(ce)})
                continue
            except do.DeribitError as e:
                journal.append_event(plan_id, "order_rejected", {"label": f"target_{i}", "error": str(e.error),
                                                                 **_rejection_detail(e)})
                continue  # position is still protected by the stop; a missing target is not a safety issue
            target_ids.append(o["order_id"])
            journal.append_event(plan_id, "order_placed", {"order_id": o["order_id"], "label": f"target_{i}",
                                                           "side": stop_side, "amount": amt, "price": px})
            remaining -= amt

        return {"plan_id": plan_id, "filled_total": filled_total, "avg_fill": round(avg_fill, 2),
                "stop_order_id": stop["order_id"], "stop_trigger": stop["trigger"],
                "target_order_ids": target_ids, "status": "entry_filled_stop_placed"}
    except ExecutionHalted:
        raise
    except Exception as ex:  # noqa: BLE001
        fail_closed(f"R7 unexpected: {ex!r}")


def load(path: Path):
    d = json.loads(path.read_text(encoding="utf-8"))
    if "entry_orders" in d:
        return d, None
    return compile_plan(d), d


def mainnet_config_refusals() -> list:
    """B150: refuse mainnet while the testnet calibration (parked blocklist, size overrides) is still in the config."""
    try:
        cfg = json.loads(AUTO_TRADER_CONFIG.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        cfg = None
    return mainnet_plan_check.calibration_refusals(cfg, "mainnet")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan_file")
    ap.add_argument("--go", action="store_true", help="actually place orders on TESTNET")
    ap.add_argument("--max-entry-seconds", type=int, default=DEFAULT_MAX_ENTRY_SECONDS)
    ap.add_argument("--mainnet", action="store_true", help="MAINNET (typed confirmation; notional hard-capped)")
    args = ap.parse_args()
    compiled, plan = load(Path(args.plan_file))
    if not args.go:
        print(json.dumps(compiled, indent=2))
        print("DRY RUN - add --go to place on testnet")
        return 0
    try:
        if args.mainnet:
            _cal = mainnet_config_refusals()
            if _cal:
                raise RuntimeError("; ".join(_cal))
            do.select_environment(True)
    except RuntimeError as e:
        print(f"REFUSED: {e}")
        return 1
    try:
        print("OK:", json.dumps(execute_plan(compiled, plan, max_entry_seconds=args.max_entry_seconds)))
        return 0
    except ExecutionHalted as e:
        print(f"HALTED: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
