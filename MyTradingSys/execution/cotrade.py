"""
MyTradingSys/execution/cotrade.py  (P1, 2026-11-01)

Testnet co-trade: the operator says a trade, Claude turns it into ONE structured order, shows it,
places it on the existing TESTNET slot (spare jishu_22, else main; no new account) with a server-side
reduce-only stop once filled, and appends a journal line holding his exact words, the reading and
the market state. Design: research/testnet_cotrade_2026-10-31/DESIGN.md sections 1, 3, 5.

Hard limits (all fail closed, all checked before the first order):
  - testnet only (never mainnet; there is no flag for it)
  - a stop is mandatory and must be on the loss side of the entry
  - no HALT / HALT_DAILY_LOSS file
  - amount multiple of 10 USD, account notional (existing + new) <= risk_guard cap, loss at stop <= $500 (OURS)
  - exchange state must match the journal: an open position or ANY open order, an unjournaled order, or a journal
    line in state "unknown" refuses a new order (one co-trade at a time; reconcile first)
  - OrderStateUnknown is journaled and never retried

Journal (append-only, gitignored): <repo>/runtime_data/cotrade/<UTC date>.jsonl, override dir with env COTRADE_JOURNAL_DIR.

Usage (all testnet):
  python cotrade.py place --said "<verbatim>" --side sell --type limit --price 110500 --amount 100 --stop 111000 [--dry-run]
  python cotrade.py stop     # place the missing reduce-only stop for a filled resting entry
  python cotrade.py kill     # HALT first, cancel label cotrade, flatten the co-trade account
"""
import sys
sys.dont_write_bytecode = True

import argparse
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deribit_orders as do  # noqa: E402
import executor  # noqa: E402 - HALT file checks / writer reused read-only
import risk_guard  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
INSTRUMENT = "BTC-PERPETUAL"
LABEL = "cotrade"
SPARE_ACCOUNT = "jishu_22"
MAX_LOSS_AT_STOP_USD = 500.0   # OURS: same as the plan ceiling in trade_plan_validator
AMOUNT_STEP_USD = 10           # OURS: BTC-PERPETUAL contract size


def journal_dir() -> Path:
    return Path(os.environ.get("COTRADE_JOURNAL_DIR") or (ROOT / "runtime_data" / "cotrade"))


def pick_account(secret_exists=None):
    """Spare slot jishu_22 when its key file exists, else main (None). Existence check only; never reads the file."""
    secret_exists = secret_exists or (lambda a: do.secret_path_for("test", a).exists())
    return SPARE_ACCOUNT if secret_exists(SPARE_ACCOUNT) else None


# ---------------------------------------------------------------- journal

def _records(jdir: Path) -> list:
    out = []
    if not jdir.exists():
        return out
    for p in sorted(jdir.glob("*.jsonl")):
        for ln in p.read_text(encoding="utf-8").splitlines():
            if ln.strip():
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    out.append({"corrupt": True, "result": {"state": "unknown"}})  # fail closed
    return out


def _append(jdir: Path, rec: dict) -> dict:
    jdir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    rec = {"ts_utc": now.isoformat(), "seq": len(_records(jdir)) + 1, **rec}
    with open(jdir / f"{now:%Y-%m-%d}.jsonl", "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rec, default=str) + "\n")
    return rec


def _journaled_order_ids(recs: list) -> set:
    ids = set()
    for r in recs:
        res = r.get("result") or {}
        for k in ("order_id", "stop_order_id"):
            if res.get(k):
                ids.add(res[k])
    return ids


def _last_real_place(recs: list):
    for r in reversed(recs):
        if (r.get("action") or {}).get("kind") == "place" and (r.get("result") or {}).get("state") != "dry_run":
            return r
    return None


# ---------------------------------------------------------------- helpers

def _market(client) -> dict:
    try:
        t = client.get_ticker(INSTRUMENT)
        return {"mark": t.get("mark_price"), "bid": t.get("best_bid_price"), "ask": t.get("best_ask_price"),
                "ts_utc": datetime.now(timezone.utc).isoformat()}
    except Exception as e:  # noqa: BLE001 - market state is context, not a gate (limit orders)
        return {"error": repr(e)}


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def _validate(side, order_type, price, amount, stop) -> list:
    r = []
    if side not in ("buy", "sell"):
        r.append(f"side must be buy|sell, got {side!r}")
    if order_type not in ("limit", "market"):
        r.append(f"type must be limit|market, got {order_type!r}")
    if not _num(amount) or amount <= 0 or amount % AMOUNT_STEP_USD:
        r.append(f"amount must be a positive multiple of {AMOUNT_STEP_USD} USD, got {amount!r}")
    if order_type == "limit" and (not _num(price) or price <= 0):
        r.append("limit order needs price > 0")
    if not _num(stop) or stop <= 0:
        r.append("REFUSED: a stop is mandatory (stop > 0)")
    return r


def _same_num(a, b) -> bool:
    return _num(a) and _num(b) and abs(float(a) - float(b)) < 1e-9


def _stop_side(position_size: float) -> str:
    return "BUY" if position_size < 0 else "SELL"


def _flatten_and_halt(client, token, halt_path, why: str) -> list:
    errs = []
    executor.write_manual_halt(f"cotrade: {why}", halt_path)
    for name, fn in (("cancel_by_label", lambda: client.cancel_by_label(token, LABEL)),
                     ("close_position", lambda: client.close_position(token, INSTRUMENT))):
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            errs.append({"op": name, "error": repr(e)})
    return errs


# ---------------------------------------------------------------- stop

def ensure_stop(client=None, account=None, journal_dir=None, halt_path=None, halt_daily_loss_path=None,
                token=None) -> dict:
    """Reduce-only server-side stop over the FULL filled size. No stop for a flat account. Idempotent.
    If the stop cannot be placed on an open position: flatten and write HALT (fail closed)."""
    client = client or do
    jdir = Path(journal_dir) if journal_dir else globals()["journal_dir"]()
    halt_path = halt_path or executor.HALT_PATH
    recs = _records(jdir)
    last = _last_real_place(recs)
    if last is None:
        return {"ok": False, "reasons": ["no co-trade order in the journal"]}
    stop_px = (last.get("action") or {}).get("stop")
    try:
        token = token or client.authenticate(account)
        pos = client.get_position(token, INSTRUMENT)
        size = float(pos.get("size", 0))
        if size == 0:
            return {"ok": True, "stop_pending": True, "note": "flat: nothing to protect yet"}
        orders = client.get_open_orders(token, INSTRUMENT)
        mine = [o for o in orders if o.get("label") == LABEL and o.get("order_type") == "stop_market"
                and o.get("reduce_only", True)]
        want_amt = int(abs(size))
        have = [o for o in mine if _same_num(o.get("amount"), want_amt) and _same_num(o.get("trigger_price"), stop_px)]
        wrong = [o for o in mine if o not in have]
        if have:
            return {"ok": True, "stop_pending": False, "stop_order_id": have[0].get("order_id"), "note": "stop exists"}
        res = client.stop_market(token, INSTRUMENT, _stop_side(size), want_amt, stop_px, LABEL)
        oid = ((res or {}).get("order") or {}).get("order_id")
        if not oid:
            raise do.OrderStateUnknown("private/stop", LABEL, "no_order_in_response")
        _append(jdir, {"said": (last.get("said")), "heard": "ensure_stop", "env": do.active_env(),
                       "action": {"kind": "stop", "amount_usd": want_amt, "stop": stop_px},
                       "market": {}, "result": {"state": "stop_placed", "stop_order_id": oid}})
        # the correct stop is live; only now remove the wrong-size / wrong-price ones (never unprotected)
        cancel_errs = []
        for o in wrong:
            try:
                client.cancel(token, o.get("order_id"))
            except Exception as e:  # noqa: BLE001 - protected already; report it
                cancel_errs.append({"order_id": o.get("order_id"), "error": repr(e)})
        out = {"ok": True, "stop_pending": False, "stop_order_id": oid}
        if wrong:
            out["replaced_wrong_stops"] = [o.get("order_id") for o in wrong]
        if cancel_errs:
            out["cancel_errors"] = cancel_errs
        return out
    except Exception as e:  # noqa: BLE001 - includes OrderStateUnknown: never retry, protect the account
        errs = []
        try:
            token = token or client.authenticate(account)
            errs = _flatten_and_halt(client, token, halt_path, f"stop failed: {e!r}")
        except Exception as e2:  # noqa: BLE001
            executor.write_manual_halt(f"cotrade: stop failed and flatten impossible: {e2!r}", halt_path)
            errs = [{"op": "authenticate", "error": repr(e2)}]
        _append(jdir, {"said": last.get("said"), "heard": "ensure_stop", "env": do.active_env(),
                       "action": {"kind": "stop", "stop": stop_px}, "market": {},
                       "result": {"state": "stop_failed_flattened", "error": repr(e), "flatten_errors": errs}})
        return {"ok": False, "reasons": [f"stop failed, account flattened and HALT written: {e!r}"]}


# ---------------------------------------------------------------- place

def place_order(said, side, order_type, price, amount, stop, dry_run=False, client=None, account="auto",
                journal_dir=None, halt_path=None, halt_daily_loss_path=None, env=None, heard=None,
                secret_exists=None) -> dict:
    client = client or do
    jdir = Path(journal_dir) if journal_dir else globals()["journal_dir"]()
    halt_path = halt_path or executor.HALT_PATH
    halt_dl = halt_daily_loss_path or executor.HALT_DAILY_LOSS_PATH
    env = env or do.active_env()
    if account == "auto":
        account = pick_account(secret_exists)
    reasons = []

    if env != "test":
        return {"ok": False, "reasons": ["REFUSED: cotrade is testnet-only"]}   # nothing touched, nothing journaled

    reasons += _validate(side, order_type, price, amount, stop)
    if secret_exists is not None and not secret_exists(account):
        reasons.append(f"account secret missing for {account or 'main'}")
    reasons += executor._check_halt_files(Path(halt_path), Path(halt_dl))

    market = _market(client)
    entry = price if order_type == "limit" else market.get("mark")
    if not reasons:
        if not _num(entry) or entry <= 0:
            reasons.append("no usable entry price (market order needs a readable mark)")
        else:
            if side == "sell" and stop <= entry:
                reasons.append(f"short stop {stop} must be above entry {entry}")
            if side == "buy" and stop >= entry:
                reasons.append(f"long stop {stop} must be below entry {entry}")
            loss = amount * abs(entry - stop) / entry
            if loss > MAX_LOSS_AT_STOP_USD:
                reasons.append(f"loss at stop ${loss:.2f} > cap ${MAX_LOSS_AT_STOP_USD:.0f}")
    if not reasons and amount > risk_guard.MAX_ACCOUNT_NOTIONAL_USD:
        reasons.append(f"amount {amount} > account cap {risk_guard.MAX_ACCOUNT_NOTIONAL_USD}")

    recs = _records(jdir)
    token = None
    pos_size = None
    if not reasons:
        for r in reversed(recs):
            st = (r.get("result") or {}).get("state")
            if st == "dry_run":
                continue
            if st == "unknown":
                reasons.append("journal: an order state is unknown - reconcile on the exchange, then run kill or stop")
                break
            if st in ("stop_placed", "stop_failed_flattened", "killed"):
                break   # reconciled by a later stop/flatten/kill; error and kill_errors do NOT reconcile
    if not reasons and not dry_run:
        try:
            token = client.authenticate(account)
            pos_size = float(client.get_position(token, INSTRUMENT).get("size", 0))
            open_orders = client.get_open_orders(token, INSTRUMENT)
        except Exception as e:  # noqa: BLE001 - unreadable exchange state fails closed
            reasons.append(f"exchange state unreadable: {e!r}")
        else:
            known = _journaled_order_ids(recs)
            foreign = [o.get("order_id") for o in open_orders if o.get("order_id") not in known]
            if foreign:
                reasons.append(f"exchange has open orders not in the journal: {foreign} - refused (restart mismatch)")
            elif open_orders:
                reasons.append("a co-trade order is still open - one at a time")
            if pos_size != 0:
                reasons.append(f"account already holds a position ({pos_size}) - one at a time")
            chk = risk_guard.check_new_plan_against_cap(
                risk_guard.account_position_notional(pos_size, None), float(amount))
            if not chk["ok"]:
                reasons.append(chk["reason"])

    reading = heard or (f"{side} {amount} USD {INSTRUMENT} {order_type}"
                        + (f" @ {price}" if order_type == "limit" else "") + f", stop {stop}")
    action = {"kind": "place", "side": side, "type": order_type, "amount_usd": amount, "price": price,
              "entry_ref": entry, "stop": stop, "instrument": INSTRUMENT}
    base = {"said": said, "heard": reading, "env": env, "account": account or "main", "market": market,
            "action": action}

    if reasons:
        _append(jdir, {**base, "result": {"state": "refused", "reasons": reasons}})
        return {"ok": False, "reasons": reasons, "reading": reading}

    if dry_run:
        _append(jdir, {**base, "result": {"state": "dry_run", "note": "offline checks only; exchange state not read"}})
        return {"ok": True, "dry_run": True, "reading": reading, "action": action}

    try:
        order = client.place(token, side, INSTRUMENT, amount, order_type, price if order_type == "limit" else None,
                             label=LABEL)
    except do.OrderStateUnknown as e:
        _append(jdir, {**base, "result": {"state": "unknown", "error": repr(e)}})
        return {"ok": False, "reasons": [f"order state unknown, not retried: {e}"], "reading": reading}
    except Exception as e:  # noqa: BLE001
        _append(jdir, {**base, "result": {"state": "error", "error": repr(e)}})
        return {"ok": False, "reasons": [f"place failed: {e!r}"], "reading": reading}

    rec = _append(jdir, {**base, "result": {"state": "placed", "order_id": order.get("order_id"),
                                            "order_state": order.get("order_state"),
                                            "filled_amount": order.get("filled_amount"),
                                            "stop_pending": True}})
    filled = order.get("order_state") == "filled" or (
        _num(order.get("filled_amount")) and order.get("filled_amount") >= amount)
    if not filled:
        return _refuse_resting(client, token, account, jdir, halt_path, base, order, reading)
    st = ensure_stop(client=client, account=account, journal_dir=jdir, halt_path=halt_path, token=token)
    out = {"ok": st["ok"], "reading": reading, "order_id": order.get("order_id"),
           "stop_pending": st.get("stop_pending", True), "seq": rec["seq"]}
    if not st["ok"]:
        out["reasons"] = st.get("reasons")
    return out


def _refuse_resting(client, token, account, jdir, halt_path, base, order, reading) -> dict:
    """DECISION (OURS): a resting (unfilled) entry cannot be guaranteed a stop when it fills later, so it is
    refused: cancel it, then protect whatever filled before the cancel landed. Any failure flattens + HALTs."""
    why = "resting entry refused: a later fill would have no stop"
    errs, stop_res = [], None
    try:
        client.cancel_by_label(token, LABEL)
        pos = float(client.get_position(token, INSTRUMENT).get("size", 0))
        if pos != 0:   # filled (partly) before the cancel landed: stop over the full filled size
            stop_res = ensure_stop(client=client, account=account, journal_dir=jdir, halt_path=halt_path, token=token)
            if not stop_res.get("ok"):
                errs.append({"op": "ensure_stop", "error": stop_res.get("reasons")})
    except Exception as e:  # noqa: BLE001 - cannot prove it is cancelled/protected: flatten + HALT
        errs = _flatten_and_halt(client, token, halt_path, f"resting entry cancel failed: {e!r}")
        errs.append({"op": "cancel_resting", "error": repr(e)})
    _append(jdir, {**base, "result": {"state": "resting_refused", "order_id": order.get("order_id"),
                                      "errors": errs, "filled_before_cancel": bool(stop_res)}})
    return {"ok": False, "reasons": [why] + ([f"errors: {errs}"] if errs else []), "reading": reading,
            "order_id": order.get("order_id")}


# ---------------------------------------------------------------- kill

def kill(client=None, account=None, journal_dir=None, halt_path=None) -> dict:
    """HALT first (survives the process), then cancel label cotrade, then flatten the co-trade account.
    Keeps going after a failed step; ok=False if any step failed."""
    client = client or do
    jdir = Path(journal_dir) if journal_dir else globals()["journal_dir"]()
    halt_path = halt_path or executor.HALT_PATH
    executor.write_manual_halt("cotrade kill", halt_path)
    errs = []
    try:
        token = client.authenticate(account)
        errs = _flatten_and_halt(client, token, halt_path, "kill")
    except Exception as e:  # noqa: BLE001
        errs = [{"op": "authenticate", "error": repr(e)}]
    _append(jdir, {"said": "kill", "heard": "kill", "env": do.active_env(), "action": {"kind": "kill"},
                   "market": {}, "result": {"state": "killed" if not errs else "kill_errors", "errors": errs}})
    return {"ok": not errs, "errors": errs}


# ---------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Testnet co-trade (BTC-PERPETUAL). Testnet only.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("place")
    p.add_argument("--said", required=True, help="the operator's exact words")
    p.add_argument("--heard", help="Claude's reading (default: built from the args)")
    p.add_argument("--side", required=True, choices=["buy", "sell"])
    p.add_argument("--type", dest="order_type", default="limit", choices=["limit", "market"])
    p.add_argument("--price", type=float)
    p.add_argument("--amount", type=int, required=True, help="USD contracts, multiple of 10")
    p.add_argument("--stop", type=float, help="mandatory trigger price of the reduce-only stop")
    p.add_argument("--dry-run", action="store_true")
    sub.add_parser("stop")
    sub.add_parser("kill")
    a = ap.parse_args(argv)

    do.select_environment(False)   # forces testnet; there is no mainnet flag
    secret_exists = lambda acct: do.secret_path_for("test", acct).exists()  # noqa: E731
    acct = pick_account(secret_exists)
    if a.cmd == "place":
        r = place_order(a.said, a.side, a.order_type, a.price, a.amount, a.stop, dry_run=a.dry_run,
                        account=acct, heard=a.heard, secret_exists=None if a.dry_run else secret_exists)
    elif a.cmd == "stop":
        r = ensure_stop(account=acct)
    else:
        r = kill(account=acct)
    print(json.dumps(r, indent=2, default=str))
    return 0 if r.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
