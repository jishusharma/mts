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
  python cotrade.py kill     # HALT first, cancel label cotrade, flatten EVERY co-trade slot (parent and hedge)
  python cotrade.py hedge --pct 50 --stop 104000 [--of <order id>] [--at P] [--dry-run]   # P5: opposite leg, 2nd slot
  python cotrade.py ladder --said "<verbatim>" --side sell --from 110500 --to 111500 --steps 5 --x 100 --stop 112000 [--dry-run]
      # P2: doubling-total ladder (adds 1,2,3,6,12 X), all rungs resting limits; spacing: --to | --spacing-pct | --spacing-pts
  python cotrade.py ladder-sync [--watch SECS --max-polls N]   # stop over the filled size; stop hit -> cancel unfilled rungs
  python cotrade.py net      # net size across the co-trade slots, rebuilt from exchange positions
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
        ids.update(i for i in (res.get("order_ids") or []) if i)   # P2 ladder rungs
    return ids


def _nm(account) -> str:
    return account or "main"


def _acct(name):
    return None if name in (None, "main") else name


UNRECONCILED = ("unknown", "hedge_pending", "hedge_placed", "ladder_pending", "ladder_placed")   # hedge_pending/placed = half-placed hedge = unknown
RECONCILED = ("stop_placed", "stop_failed_flattened", "killed", "hedge_failed", "ladder_failed", "ladder_stopped")


def _unknown_state(recs: list):
    """Newest non-dry-run state decides: an unreconciled one refuses new orders (fail closed)."""
    after_stop = False
    for r in reversed(recs):
        st = (r.get("result") or {}).get("state")
        if st == "dry_run":
            continue
        if after_stop:   # a stop placed over a live ladder does not end the ladder (only ladder_stopped/failed/kill)
            if st in ("ladder_pending", "ladder_placed"):
                return "journal: a ladder is still live - run ladder-sync until it is stopped, or kill"
            if st in ("unknown", "hedge_pending", "hedge_placed") or st in RECONCILED:
                return None
            continue
        if st == "stop_placed":
            after_stop = True
            continue
        if st in UNRECONCILED:
            return ("journal: an order state is unknown - reconcile on the exchange, then run kill or stop"
                    + (" (half-placed hedge)" if st.startswith("hedge") else "")
                    + (" (ladder not stopped yet: ladder-sync)" if st.startswith("ladder") else ""))
        if st in RECONCILED:
            return None   # reconciled by a later stop/flatten/kill; error and kill_errors do NOT reconcile
    return None


def _last_real_place(recs: list):
    for r in reversed(recs):
        if (r.get("action") or {}).get("kind") in ("place", "ladder") and (r.get("result") or {}).get("state") != "dry_run":
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


_NOT_TESTNET = "REFUSED: cotrade is testnet-only"


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
                token=None, stop_px=None, extra=None, env=None) -> dict:
    """Reduce-only server-side stop over the FULL filled size. No stop for a flat account. Idempotent.
    If the stop cannot be placed on an open position: flatten and write HALT (fail closed)."""
    client = client or do
    if (env or do.active_env()) != "test":
        return {"ok": False, "reasons": [_NOT_TESTNET]}   # nothing touched, nothing journaled
    jdir = Path(journal_dir) if journal_dir else globals()["journal_dir"]()
    halt_path = halt_path or executor.HALT_PATH
    recs = _records(jdir)
    last = _last_real_place(recs)
    if last is None:
        return {"ok": False, "reasons": ["no co-trade order in the journal"]}
    stop_px = stop_px if stop_px is not None else (last.get("action") or {}).get("stop")
    extra = dict(extra or {})
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
                       "account": _nm(account), **extra,
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
                       "account": _nm(account), **extra,
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
        why_unknown = _unknown_state(recs)
        if why_unknown:
            reasons.append(why_unknown)
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


# ---------------------------------------------------------------- slots, exchange view (P5)

HEDGE_SLOTS = ["jishu_1", "jishu_2", "jishu_3", "jishu_4", SPARE_ACCOUNT, None]   # existing testnet slots; None = main


def _default_secret_exists(a) -> bool:
    return do.secret_path_for("test", a).exists()   # existence only, never read


def pick_hedge_account(parent_account, secret_exists=None):
    """First existing slot that is not the parent account. Returns (found, account). Never a new key."""
    secret_exists = secret_exists or _default_secret_exists
    for a in HEDGE_SLOTS:
        if _nm(a) != _nm(parent_account) and secret_exists(a):
            return True, a
    return False, None


def _journal_accounts(recs: list) -> list:
    """Account names of co-trade legs since the last completed kill (parents and hedges)."""
    names = []
    for r in recs:
        st = (r.get("result") or {}).get("state")
        if st == "killed":
            names = []
            continue
        kind = (r.get("action") or {}).get("kind")
        if kind in ("place", "hedge") and st not in ("dry_run", "refused") and r.get("account"):
            if r["account"] not in names:
                names.append(r["account"])
    return names


def _slot_view(client, name) -> dict:
    tok = client.authenticate(_acct(name))
    size = float(client.get_position(tok, INSTRUMENT).get("size", 0))
    orders = client.get_open_orders(tok, INSTRUMENT)
    mine = [o for o in orders if o.get("label") == LABEL]
    stops = [o for o in mine if o.get("order_type") == "stop_market"]
    return {"account": name, "size": size, "label_orders": len(mine),
            "stop_ok": size == 0 or any(_same_num(o.get("amount"), abs(size)) for o in stops)}


def rebuild(client=None, journal_dir=None, secret_exists=None, env=None) -> dict:
    """Rebuild the co-trade pair from the EXCHANGE (positions + label-cotrade orders on every existing slot),
    not only the journal: a slot is ours if the journal names it since the last kill or it carries a cotrade
    order. Other slots with a position are listed as unowned and never counted or touched."""
    if (env or do.active_env()) != "test":
        return {"ok": False, "reasons": [_NOT_TESTNET]}   # no exchange call
    client = client or do
    jdir = Path(journal_dir) if journal_dir else globals()["journal_dir"]()
    secret_exists = secret_exists or _default_secret_exists
    recs = _records(jdir)
    jnames = _journal_accounts(recs)
    placed_by = {r.get("account") for r in recs if (r.get("action") or {}).get("kind") == "place"
                 and (r.get("result") or {}).get("state") not in ("dry_run", "refused")}
    names = list(jnames)
    for a in HEDGE_SLOTS:
        if _nm(a) not in names and secret_exists(a):
            names.append(_nm(a))
    views, errors = [], []
    for n in names:
        try:
            views.append(_slot_view(client, n))
        except Exception as e:  # noqa: BLE001 - unreadable slot: report, fail closed
            errors.append({"account": n, "error": repr(e)})
    owned = [v for v in views if v["account"] in jnames or v["label_orders"] > 0]
    unowned = [{"account": v["account"], "size": v["size"]} for v in views if v not in owned and v["size"] != 0]
    open_ = [v for v in owned if v["size"] != 0]
    pair = None
    if len(open_) == 2 and open_[0]["size"] * open_[1]["size"] < 0:
        open_.sort(key=lambda v: (v["account"] in placed_by, abs(v["size"])), reverse=True)
        pair = {"parent": open_[0]["account"], "hedge": open_[1]["account"]}
    return {"ok": not errors and all(v["stop_ok"] for v in owned), "slots": owned, "pair": pair,
            "net_usd": sum(v["size"] for v in owned), "unowned_positions": unowned, "errors": errors,
            "stop_missing": [v["account"] for v in owned if not v["stop_ok"]]}


def net(client=None, journal_dir=None, secret_exists=None, env=None) -> dict:
    """Live aid: net size across the co-trade slots, from exchange positions (DECISION OURS: printed by cotrade.py)."""
    r = rebuild(client=client, journal_dir=journal_dir, secret_exists=secret_exists, env=env)
    if "net_usd" not in r:
        return r
    return {**r, "net_side": "long" if r["net_usd"] > 0 else "short" if r["net_usd"] < 0 else "flat"}


# ---------------------------------------------------------------- hedge (P5)

def _find_parent(recs: list, of):
    """The real placed co-trade entry: the order id given, else the newest one."""
    for r in reversed(recs):
        res = r.get("result") or {}
        if (r.get("action") or {}).get("kind") == "place" and res.get("state") == "placed":
            if of in (None, "last") or res.get("order_id") == of:
                return r
    return None


def _hedge_size(parent_amount, pct) -> int:
    """pct of the parent filled size, FLOORED to AMOUNT_STEP_USD (70 at 50 pct = 35 -> 30)."""
    return int(math.floor(round(float(parent_amount) * float(pct) / 100.0 / AMOUNT_STEP_USD, 9))) * AMOUNT_STEP_USD


def _hedge_fail(client, jdir, halt_path, base, why, toks, extra=None) -> dict:
    """The second leg failed: HALT first, flatten BOTH slots (each step tried), journal it. Unflattened = unknown."""
    errs = []
    for name, tok in toks:
        if tok is None:
            errs.append({"account": name, "op": "authenticate", "error": "no token"})
            continue
        for e in _flatten_and_halt(client, tok, halt_path, f"hedge failed: {why}"):
            errs.append({"account": name, **e})
    _append(jdir, {**base, "result": {"state": "unknown" if errs else "hedge_failed", "error": why,
                                      "flatten_errors": errs, "parent_order_id": base.get("parent_order_id"),
                                      **(extra or {})}})
    return {"ok": False, "reasons": [f"hedge failed, both slots flattened and HALT written: {why}"
                                     + (f" (errors: {errs})" if errs else "")]}


def hedge(of="last", pct=50, stop=None, at=None, dry_run=False, client=None, hedge_account="auto",
          journal_dir=None, halt_path=None, halt_daily_loss_path=None, env=None, said=None,
          secret_exists=None) -> dict:
    """Opposite leg of pct of the parent filled size on a second existing slot. Only marketable hedges are placed
    (a resting --at is refused). Both legs carry a server-side reduce-only stop; any second-leg failure flattens both."""
    client = client or do
    jdir = Path(journal_dir) if journal_dir else globals()["journal_dir"]()
    halt_path = halt_path or executor.HALT_PATH
    halt_dl = halt_daily_loss_path or executor.HALT_DAILY_LOSS_PATH
    env = env or do.active_env()
    secret_exists = secret_exists or _default_secret_exists
    if env != "test":
        return {"ok": False, "reasons": [_NOT_TESTNET]}   # nothing touched, nothing journaled
    reasons = []
    if not (isinstance(said, str) and said.strip()):
        reasons.append("REFUSED: --said is required (the operator's exact words); nothing is invented")
    if not _num(pct) or not 0 < pct <= 100:
        reasons.append(f"pct must be in (0, 100], got {pct!r}")
    if not _num(stop) or stop <= 0:
        reasons.append("REFUSED: a stop is mandatory (stop > 0)")
    if at is not None and (not _num(at) or at <= 0):
        reasons.append(f"--at must be a price > 0, got {at!r}")
    reasons += executor._check_halt_files(Path(halt_path), Path(halt_dl))
    recs = _records(jdir)
    parent = _find_parent(recs, of)
    base = {"said": said, "env": env, "account": None, "market": {},
            "action": {"kind": "hedge", "pct": pct, "stop": stop, "price": at, "instrument": INSTRUMENT}}
    hacct = hname = pact = poid = pa = ps = hs = None
    if parent is None:
        reasons.append("no filled co-trade parent order in the journal")
    else:
        pact = parent.get("account") or "main"
        pa = parent["action"]
        poid = parent["result"].get("order_id")
        ps = pa["side"]
        hs = "buy" if ps == "sell" else "sell"
        base.update({"parent_order_id": poid, "parent_account": pact})
        base["action"]["side"] = hs
        if hedge_account == "auto":
            found, hacct = pick_hedge_account(_acct(pact), secret_exists)
            if found:
                hname = _nm(hacct)
            else:
                reasons.append("no second existing slot with a key file to hold the hedge")
        else:
            hacct, hname = hedge_account, _nm(hedge_account)
            if hname == pact:
                reasons.append(f"hedge must be on a second slot, not the parent account {pact}")
            elif not secret_exists(hacct):
                reasons.append(f"account secret missing for {hname}")
        base["account"] = hname
        why_unknown = _unknown_state(recs)
        if why_unknown:
            reasons.append(why_unknown)
        killed_at = max([i for i, r in enumerate(recs) if (r.get("result") or {}).get("state") == "killed"] or [-1])
        if any(r.get("parent_order_id") == poid and (r.get("action") or {}).get("kind") == "hedge"
               and (r.get("result") or {}).get("state") == "hedge_placed" for r in recs[killed_at + 1:]):
            reasons.append("parent already hedged")
    psize = hsize = entry = None
    market = {}
    if parent is not None and not reasons:
        psize = float(parent["result"].get("filled_amount") or pa["amount_usd"])
        hsize = _hedge_size(psize, pct)
        if hsize <= 0:
            reasons.append(f"hedge size rounds to 0 ({pct} pct of {psize})")
    ptok = htok = None
    if parent is not None and not reasons and not dry_run:
        market = _market(client)
        base["market"] = market
        try:
            ptok = client.authenticate(_acct(pact))
            ppos = float(client.get_position(ptok, INSTRUMENT).get("size", 0))
            porders = client.get_open_orders(ptok, INSTRUMENT)
            htok = client.authenticate(hacct)
            hpos = float(client.get_position(htok, INSTRUMENT).get("size", 0))
            horders = client.get_open_orders(htok, INSTRUMENT)
        except Exception as e:  # noqa: BLE001 - unreadable exchange state fails closed
            reasons.append(f"exchange state unreadable: {e!r}")
        else:
            if ppos == 0 or (ppos < 0) != (ps == "sell"):
                reasons.append(f"parent position not open as {ps} on the exchange ({ppos})")
            else:
                psize = abs(ppos)
                hsize = _hedge_size(psize, pct)
                if hsize <= 0:
                    reasons.append(f"hedge size rounds to 0 ({pct} pct of {psize})")
            if not any(o.get("label") == LABEL and o.get("order_type") == "stop_market"
                       and _same_num(o.get("amount"), int(psize)) and _same_num(o.get("trigger_price"), pa["stop"])
                       for o in porders):
                reasons.append("parent has no matching server-side stop - refused (protect it first)")
            if hpos != 0 or horders:
                reasons.append(f"hedge slot {hname} is not flat (position {hpos}, {len(horders)} open orders)")
            if hsize:
                chk = risk_guard.check_new_plan_against_cap(risk_guard.account_position_notional(hpos, None),
                                                            float(hsize))
                if not chk["ok"]:
                    reasons.append(chk["reason"])
    if parent is not None and not reasons:
        mark = market.get("mark") if market else pa.get("entry_ref")   # dry-run: offline, parent entry as reference
        entry = at if at is not None else mark
        if not _num(entry) or entry <= 0:
            reasons.append("no usable hedge entry price (needs a readable mark)")
        else:
            if at is not None and not dry_run:   # marketable only: a resting hedge is refused like P1
                bid, ask = market.get("bid"), market.get("ask")
                if not _num(bid) or not _num(ask):
                    reasons.append("no readable bid/ask to prove the hedge --at is marketable")
                elif (hs == "buy" and at < ask) or (hs == "sell" and at > bid):
                    reasons.append(f"hedge --at {at} would rest (bid {bid}, ask {ask}) - refused, only marketable hedges")
            if hs == "sell" and stop <= entry:
                reasons.append(f"short stop {stop} must be above entry {entry}")
            if hs == "buy" and stop >= entry:
                reasons.append(f"long stop {stop} must be below entry {entry}")
            ploss = psize * abs(pa["entry_ref"] - pa["stop"]) / pa["entry_ref"]
            hloss = hsize * abs(entry - stop) / entry
            if ploss + hloss > MAX_LOSS_AT_STOP_USD:
                reasons.append(f"loss at both stops ${ploss + hloss:.2f} (parent ${ploss:.2f} + hedge ${hloss:.2f})"
                               f" > cap ${MAX_LOSS_AT_STOP_USD:.0f}")
    if hsize is not None:
        base["action"].update({"amount_usd": hsize, "entry_ref": entry, "parent_amount_usd": psize,
                               "type": "limit" if at is not None else "market"})
    reading = (f"hedge {pct}% of {pact} {psize} USD: {hs} {hsize} USD on {hname}, stop {stop}"
               if parent is not None else "hedge: no parent")
    base["heard"] = reading
    if reasons:
        _append(jdir, {**base, "result": {"state": "refused", "reasons": reasons}})
        return {"ok": False, "reasons": reasons, "reading": reading}
    psigned = psize if ps == "buy" else -psize
    hsigned = hsize if hs == "buy" else -hsize
    legs = [{"role": "parent", "account": pact, "side": ps, "amount_usd": psize, "stop": pa["stop"]},
            {"role": "hedge", "account": hname, "side": hs, "amount_usd": hsize, "stop": stop, "entry_ref": entry}]
    if dry_run:
        _append(jdir, {**base, "result": {"state": "dry_run", "note": "offline checks only"}})
        return {"ok": True, "dry_run": True, "reading": reading, "legs": legs, "net_usd": psigned + hsigned}

    _append(jdir, {**base, "result": {"state": "hedge_pending", "parent_order_id": poid}})   # half-placed = unknown
    toks = [(hname, htok), (pact, ptok)]
    try:
        order = client.place(htok, hs, INSTRUMENT, hsize, "limit" if at is not None else "market", at, label=LABEL)
    except Exception as e:  # noqa: BLE001 - incl. OrderStateUnknown: never retried, both slots flattened
        return _hedge_fail(client, jdir, halt_path, base, f"hedge place failed: {e!r}", toks)
    rec = _append(jdir, {**base, "result": {"state": "hedge_placed", "order_id": order.get("order_id"),
                                            "order_state": order.get("order_state"), "parent_order_id": poid,
                                            "filled_amount": order.get("filled_amount"), "stop_pending": True}})
    filled = order.get("order_state") == "filled" or (
        _num(order.get("filled_amount")) and order.get("filled_amount") >= hsize)
    if not filled:
        return _hedge_fail(client, jdir, halt_path, base, "hedge leg did not fill", toks,
                           {"order_id": order.get("order_id")})
    link = {"parent_order_id": poid, "parent_account": pact}
    st = ensure_stop(client=client, account=hacct, journal_dir=jdir, halt_path=halt_path, token=htok,
                     stop_px=stop, extra=link, env=env)
    if st["ok"]:
        pst = ensure_stop(client=client, account=_acct(pact), journal_dir=jdir, halt_path=halt_path, token=ptok,
                          stop_px=pa.get("stop"), env=env)
        if not pst["ok"]:
            st = pst
    if not st["ok"]:
        return _hedge_fail(client, jdir, halt_path, base, f"stop failed: {st.get('reasons')}", toks,
                           {"order_id": order.get("order_id")})
    return {"ok": True, "reading": reading, "order_id": order.get("order_id"), "parent_order_id": poid,
            "legs": legs, "net_usd": psigned + hsigned, "seq": rec["seq"]}


# ---------------------------------------------------------------- kill

def kill(client=None, account=None, journal_dir=None, halt_path=None, secret_exists=None, env=None) -> dict:
    """HALT first (survives the process), then for EVERY co-trade slot (given account, journal legs since the last
    kill, and with secret_exists also any slot carrying a cotrade order): cancel label cotrade, flatten.
    Keeps going after a failed step or slot; ok=False if any step failed."""
    client = client or do
    jdir = Path(journal_dir) if journal_dir else globals()["journal_dir"]()
    halt_path = halt_path or executor.HALT_PATH
    executor.write_manual_halt("cotrade kill", halt_path)
    if (env or do.active_env()) != "test":   # fail closed: HALT is written, nothing is cancelled/flattened/journaled
        return {"ok": False, "errors": [], "slots": [], "reasons": [_NOT_TESTNET + " (HALT written only)"]}
    slots = [_nm(account)]
    for n in _journal_accounts(_records(jdir)):
        if n not in slots:
            slots.append(n)
    errs = []
    if secret_exists is not None:
        for a in HEDGE_SLOTS:
            if _nm(a) not in slots and secret_exists(a):
                try:
                    tok = client.authenticate(a)
                    if any(o.get("label") == LABEL for o in client.get_open_orders(tok, INSTRUMENT)):
                        slots.append(_nm(a))
                except Exception as e:  # noqa: BLE001
                    errs.append({"account": _nm(a), "op": "scan", "error": repr(e)})
    for n in slots:
        try:
            tok = client.authenticate(_acct(n))
            errs += [{"account": n, **e} for e in _flatten_and_halt(client, tok, halt_path, "kill")]
        except Exception as e:  # noqa: BLE001 - one slot failing never skips the others
            errs.append({"account": n, "op": "authenticate", "error": repr(e)})
    _append(jdir, {"said": "kill", "heard": "kill", "env": do.active_env(), "action": {"kind": "kill"},
                   "market": {}, "result": {"state": "killed" if not errs else "kill_errors", "errors": errs,
                                            "slots": slots}})
    return {"ok": not errs, "errors": errs, "slots": slots}


# ---------------------------------------------------------------- P2 doubling-total ladder

MAX_RUNGS = 7                  # OURS: 7 rungs at X=100 is $9,600 total, the most the $10,000 account cap allows
TICK = 0.5                     # BTC-PERPETUAL price tick
MARGIN_LEVERAGES = (10, 20)
_LADDER_DONE = ("ladder_stopped", "ladder_failed", "killed", "stop_failed_flattened")


def double_total_sizes(x, n) -> list:
    """Adds 1,2,3,6,12,24,48 X: X, 2X, then every add equals the running total (ladder_math.py)."""
    out, tot = [], 0
    for k in range(n):
        a = x * (k + 1) if k < 2 else tot
        out.append(a)
        tot += a
    return out


def _tick(p: float) -> float:
    return round(p / TICK) * TICK


def rung_prices(side, frm, to=None, steps=1, spacing_pct=None, spacing_pts=None) -> list:
    """Rung prices walking AGAINST the position (a short ladder climbs, a long ladder falls).
    Exactly one of to / spacing_pct / spacing_pts when steps > 1. Raises ValueError on bad input."""
    if side not in ("buy", "sell"):
        raise ValueError(f"side must be buy|sell, got {side!r}")
    if not isinstance(steps, int) or steps < 1:
        raise ValueError("steps must be an integer >= 1")
    if not _num(frm) or frm <= 0:
        raise ValueError("--from must be a price > 0")
    if steps == 1:
        return [_tick(frm)]
    given = [v for v in (to, spacing_pct, spacing_pts) if v is not None]
    if len(given) != 1 or not _num(given[0]):
        raise ValueError("give exactly one of --to, --spacing-pct, --spacing-pts")
    sgn = 1 if side == "sell" else -1
    if to is not None:
        if (to - frm) * sgn <= 0:
            raise ValueError(f"a {'short' if sgn > 0 else 'long'} ladder must go {'up' if sgn > 0 else 'down'} "
                             f"from {frm}, got --to {to}")
        px = [frm + (to - frm) * i / (steps - 1) for i in range(steps)]
    else:
        gap = spacing_pct / 100.0 * frm if spacing_pct is not None else spacing_pts
        if not _num(gap) or gap <= 0:
            raise ValueError("spacing must be > 0")
        px = [frm + sgn * gap * i for i in range(steps)]
    px = [_tick(p) for p in px]
    if any(p <= 0 for p in px):
        raise ValueError("a rung price is <= 0")
    return px


def ladder_plan(side, frm, steps, x, stop, to=None, spacing_pct=None, spacing_pts=None) -> dict:
    """Pure, offline: the rung table, the total, the loss if every rung fills and the stop is hit, and the margin.
    Loss = sum(size * (stop/price - 1)) for a short (1 - stop/price for a long): same number as ladder_math.py and,
    for the inverse BTC-PERPETUAL, the same in USD. ok=False lists every breached limit (nothing is then placed)."""
    reasons = []
    if side not in ("buy", "sell"):
        reasons.append(f"side must be buy|sell, got {side!r}")
    if not isinstance(steps, int) or isinstance(steps, bool) or steps < 1 or steps > MAX_RUNGS:
        reasons.append(f"steps must be 1..{MAX_RUNGS}, got {steps!r}")
    if not _num(x) or x <= 0 or x % AMOUNT_STEP_USD:
        reasons.append(f"X must be a positive multiple of {AMOUNT_STEP_USD} USD, got {x!r}")
    if not _num(stop) or stop <= 0:
        reasons.append("REFUSED: a stop is mandatory (stop > 0)")
    if reasons:
        return {"ok": False, "reasons": reasons}
    try:
        prices = rung_prices(side, frm, to=to, steps=steps, spacing_pct=spacing_pct, spacing_pts=spacing_pts)
    except ValueError as e:
        return {"ok": False, "reasons": [str(e)]}
    if abs(stop - _tick(stop)) > 1e-9:
        return {"ok": False, "reasons": [f"stop {stop} is not on the {TICK} price tick (nearest {_tick(stop)})"]}
    sizes = double_total_sizes(int(x), steps)
    last = prices[-1]
    if side == "sell" and stop <= last:
        reasons.append(f"short stop {stop} must be above the last rung {last}")
    if side == "buy" and stop >= last:
        reasons.append(f"long stop {stop} must be below the last rung {last}")
    total = sum(sizes)
    sgn = 1 if side == "sell" else -1
    loss = sum(s * sgn * (stop / p - 1) for s, p in zip(sizes, prices))
    cum, rungs = 0, []
    for i, (s, p) in enumerate(zip(sizes, prices), 1):
        cum += s
        rungs.append({"n": i, "price": p, "amount": s, "total_after": cum})
    if total > risk_guard.MAX_ACCOUNT_NOTIONAL_USD:
        reasons.append(f"ladder total {total} > account cap {risk_guard.MAX_ACCOUNT_NOTIONAL_USD}")
    if loss > MAX_LOSS_AT_STOP_USD:
        reasons.append(f"loss at stop ${loss:.2f} > cap ${MAX_LOSS_AT_STOP_USD:.0f}")
    return {"ok": not reasons, "reasons": reasons, "side": side, "rungs": rungs, "total": total,
            "stop": stop, "worst_loss_usd": loss,
            "margin_usd": {f"{lv}x": total / lv for lv in MARGIN_LEVERAGES}}


def place_ladder(said, side, frm, steps, x, stop, to=None, spacing_pct=None, spacing_pts=None, dry_run=False,
                 client=None, account="auto", journal_dir=None, halt_path=None, halt_daily_loss_path=None,
                 env=None, secret_exists=None) -> dict:
    """Show every rung, then place ALL rungs as resting limits (label cotrade). Every cap is checked before the
    first order; a refusal places nothing. The stop is placed by ladder_sync over the filled size, never earlier
    (reduce-only on a flat account). The stop covers only the size filled as of the last ladder_sync poll (an
    unprotected window of up to one poll; use ladder-sync --watch). Rungs are assumed to rest: post_only is not used,
    so a rung priced through the market would fill at once. A failure part-way cancels the rungs already resting (flatten + HALT if that fails)."""
    client = client or do
    jdir = Path(journal_dir) if journal_dir else globals()["journal_dir"]()
    halt_path = halt_path or executor.HALT_PATH
    halt_dl = halt_daily_loss_path or executor.HALT_DAILY_LOSS_PATH
    env = env or do.active_env()
    if env != "test":
        return {"ok": False, "reasons": [_NOT_TESTNET]}   # nothing touched, nothing journaled
    if account == "auto":
        account = pick_account(secret_exists)
    plan = ladder_plan(side, frm, steps, x, stop, to=to, spacing_pct=spacing_pct, spacing_pts=spacing_pts)
    reasons = list(plan["reasons"])
    if secret_exists is not None and not secret_exists(account):
        reasons.append(f"account secret missing for {account or 'main'}")
    reasons += executor._check_halt_files(Path(halt_path), Path(halt_dl))
    recs = _records(jdir)
    if not reasons:
        why_unknown = _unknown_state(recs)
        if why_unknown:
            reasons.append(why_unknown)
    reading = (f"{side} ladder {steps} rungs from {frm}, X={x}, adds {[r['amount'] for r in plan.get('rungs', [])]}, "
               f"stop {stop}")
    action = {"kind": "ladder", "side": side, "x": x, "steps": steps, "stop": stop, "instrument": INSTRUMENT,
              "rungs": plan.get("rungs"), "total": plan.get("total"), "worst_loss_usd": plan.get("worst_loss_usd")}
    base = {"said": said, "heard": reading, "env": env, "account": account or "main", "market": {},
            "action": action}
    table = {"rungs": plan.get("rungs"), "total": plan.get("total"), "stop": stop,
             "worst_loss_usd": plan.get("worst_loss_usd"), "margin_usd": plan.get("margin_usd")}

    token = None
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
                risk_guard.account_position_notional(pos_size, None), float(plan["total"]))
            if not chk["ok"]:
                reasons.append(chk["reason"])
    if reasons:
        _append(jdir, {**base, "result": {"state": "refused", "reasons": reasons}})
        return {"ok": False, "reasons": reasons, "reading": reading, **table}
    if dry_run:
        _append(jdir, {**base, "result": {"state": "dry_run", "note": "offline checks only; exchange state not read"}})
        return {"ok": True, "dry_run": True, "reading": reading, **table}

    # written BEFORE the first rung (like hedge_pending): a crash mid-ladder leaves an unreconciled record
    _append(jdir, {**base, "result": {"state": "ladder_pending"}})
    ids = []
    for r in plan["rungs"]:
        try:
            o = client.place(token, side, INSTRUMENT, r["amount"], "limit", r["price"], label=LABEL)
            ids.append(o.get("order_id"))
        except do.OrderStateUnknown as e:   # never retried; cannot tell what rests: cancel what we can, HALT
            errs = _flatten_and_halt(client, token, halt_path, f"ladder rung {r['n']} state unknown: {e!r}")
            _append(jdir, {**base, "result": {"state": "unknown", "error": repr(e), "order_ids": ids,
                                              "flatten_errors": errs}})
            return {"ok": False, "reasons": [f"order state unknown at rung {r['n']}, not retried: {e}"],
                    "reading": reading}
        except Exception as e:  # noqa: BLE001 - cancel the rungs already resting; protect anything that filled
            errs, stop_res = [], None
            _append(jdir, {**base, "result": {"state": "ladder_failed", "error": repr(e), "order_ids": ids,
                                              "failed_rung": r["n"]}})
            try:
                client.cancel_by_label(token, LABEL)
                if float(client.get_position(token, INSTRUMENT).get("size", 0)) != 0:
                    stop_res = ensure_stop(client=client, account=account, journal_dir=jdir, halt_path=halt_path,
                                           token=token)
                    if not stop_res.get("ok"):
                        errs.append({"op": "ensure_stop", "error": stop_res.get("reasons")})
            except Exception as e2:  # noqa: BLE001 - cannot prove it is cancelled/protected
                errs = _flatten_and_halt(client, token, halt_path, f"ladder cancel failed: {e2!r}")
                errs.append({"op": "cancel_rungs", "error": repr(e2)})
            return {"ok": False, "reasons": [f"rung {r['n']} failed, rest cancelled: {e!r}"]
                    + ([f"errors: {errs}"] if errs else []), "reading": reading}
    rec = _append(jdir, {**base, "result": {"state": "ladder_placed", "order_ids": ids, "stop_pending": True}})
    return {"ok": True, "reading": reading, "order_ids": ids, "seq": rec["seq"], **table}


def ladder_sync(client=None, account=None, journal_dir=None, halt_path=None, env=None) -> dict:
    """One poll. State comes only from the journal and the exchange (restart-safe).
    filled size > 0 -> ensure_stop over the FULL filled size (replaces a smaller stop);
    flat after a stop was placed -> stop hit or closed: cancel the unfilled rungs, flatten any late fill;
    flat and no stop yet -> waiting. An unreadable exchange cancels the rungs and writes HALT (fail closed)."""
    client = client or do
    if (env or do.active_env()) != "test":
        return {"ok": False, "reasons": [_NOT_TESTNET]}
    jdir = Path(journal_dir) if journal_dir else globals()["journal_dir"]()
    halt_path = halt_path or executor.HALT_PATH
    recs = _records(jdir)
    idx = max((i for i, r in enumerate(recs) if (r.get("action") or {}).get("kind") == "ladder"
               and (r.get("result") or {}).get("state") in ("ladder_pending", "ladder_placed")), default=None)
    if idx is None:
        return {"ok": False, "reasons": ["no placed ladder in the journal"]}
    after = recs[idx + 1:]
    if any((r.get("result") or {}).get("state") in _LADDER_DONE for r in after):
        return {"ok": True, "done": True}
    stop_seen = any((r.get("action") or {}).get("kind") == "stop"
                    and (r.get("result") or {}).get("state") == "stop_placed" for r in after)
    ladder = recs[idx]
    if (ladder.get("result") or {}).get("state") == "ladder_pending":
        return _ladder_orphan(client, account, jdir, halt_path, ladder)
    try:
        token = client.authenticate(account)
        size = float(client.get_position(token, INSTRUMENT).get("size", 0))
        client.get_open_orders(token, INSTRUMENT)
    except Exception as e:  # noqa: BLE001 - protection cannot be verified: stop new fills, HALT
        errs = []
        try:
            executor.write_manual_halt(f"cotrade ladder: exchange unreadable: {e!r}", halt_path)
            tok = client.authenticate(account)
            client.cancel_by_label(tok, LABEL)
        except Exception as e2:  # noqa: BLE001
            errs.append({"op": "cancel_rungs", "error": repr(e2)})
        _append(jdir, {"said": ladder.get("said"), "heard": "ladder_sync", "env": do.active_env(),
                       "account": _nm(account), "action": {"kind": "ladder_sync"}, "market": {},
                       "result": {"state": "ladder_failed", "error": repr(e), "errors": errs}})
        return {"ok": False, "reasons": [f"exchange state unreadable, rungs cancelled, HALT written: {e!r}"]}
    if size != 0:
        st = ensure_stop(client=client, account=account, journal_dir=jdir, halt_path=halt_path, token=token)
        if not st.get("ok"):   # stop failed: flattened + HALT already; make the ladder terminal
            _append(jdir, {"said": ladder.get("said"), "heard": "ladder_sync", "env": do.active_env(),
                           "account": _nm(account), "action": {"kind": "ladder_sync"}, "market": {},
                           "result": {"state": "ladder_failed", "reasons": st.get("reasons")}})
        return {**st, "position": size}
    if not stop_seen:
        return {"ok": True, "waiting": True, "position": 0}
    errs = []
    try:
        client.cancel_by_label(token, LABEL)
        if float(client.get_position(token, INSTRUMENT).get("size", 0)) != 0:   # a rung filled as the stop hit
            errs = _flatten_and_halt(client, token, halt_path, "ladder: fill after the stop")
    except Exception as e:  # noqa: BLE001
        errs = _flatten_and_halt(client, token, halt_path, f"ladder cancel failed: {e!r}")
        errs.append({"op": "cancel_rest", "error": repr(e)})
    _append(jdir, {"said": ladder.get("said"), "heard": "ladder_sync", "env": do.active_env(),
                   "account": _nm(account), "action": {"kind": "ladder_sync"}, "market": {},
                   "result": {"state": "ladder_stopped", "errors": errs}})
    return {"ok": not errs, "stopped": True, "errors": errs}


def _ladder_orphan(client, account, jdir, halt_path, ladder) -> dict:
    """ladder_pending with no ladder_placed after it: a crash mid-placement. Cancel the orphan rungs, protect any
    fill, journal ladder_failed (terminal) and report; never continue silently."""
    errs = []
    try:
        token = client.authenticate(account)
        client.cancel_by_label(token, LABEL)
        if float(client.get_position(token, INSTRUMENT).get("size", 0)) != 0:
            st = ensure_stop(client=client, account=account, journal_dir=jdir, halt_path=halt_path, token=token)
            if not st.get("ok"):
                errs.append({"op": "ensure_stop", "error": st.get("reasons")})
    except Exception as e:  # noqa: BLE001
        try:
            executor.write_manual_halt(f"cotrade ladder: orphan cleanup failed: {e!r}", halt_path)
        except Exception:  # noqa: BLE001
            pass
        errs.append({"op": "orphan_cleanup", "error": repr(e)})
    _append(jdir, {"said": ladder.get("said"), "heard": "ladder_sync", "env": do.active_env(),
                   "account": _nm(account), "action": {"kind": "ladder_sync"}, "market": {},
                   "result": {"state": "ladder_failed", "orphan": True, "errors": errs}})
    return {"ok": False, "orphan": True, "errors": errs,
            "reasons": ["crash mid-placement: orphan rungs cancelled, ladder closed; check the position"]}


def ladder_watch(secs, max_polls=1000, account=None, sleep=None, **kw) -> dict:
    """Poll ladder_sync every secs until done/stopped/failed (the unprotected window is at most one poll)."""
    import time
    sleep = sleep or time.sleep
    r = {"ok": False, "reasons": ["no poll ran"]}
    for _ in range(max(1, int(max_polls))):
        r = ladder_sync(account=account, **kw)
        if not r.get("ok") or r.get("done") or r.get("stopped"):
            break
        sleep(secs)
    return r


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
    h = sub.add_parser("hedge", help="opposite leg of --pct of the parent filled size on a second existing slot")
    h.add_argument("--of", default="last", help="parent order id (default: the newest co-trade entry)")
    h.add_argument("--pct", type=float, required=True)
    h.add_argument("--stop", type=float, help="mandatory trigger price of the hedge's reduce-only stop")
    h.add_argument("--at", type=float, help="marketable limit price; a hedge that would rest is refused")
    h.add_argument("--said", required=True, help="the operator's exact words")
    h.add_argument("--dry-run", action="store_true")
    ld = sub.add_parser("ladder", help="P2 doubling-total ladder of resting limits on the co-trade slot")
    ld.add_argument("--said", required=True, help="the operator's exact words")
    ld.add_argument("--side", required=True, choices=["buy", "sell"])
    ld.add_argument("--from", dest="frm", type=float, required=True, help="first rung price")
    ld.add_argument("--to", type=float, help="last rung price (rungs evenly spaced)")
    ld.add_argument("--spacing-pct", type=float, help="rung spacing in percent of the first price")
    ld.add_argument("--spacing-pts", type=float, help="rung spacing in price points")
    ld.add_argument("--steps", type=int, required=True, help="number of rungs (max %d)" % MAX_RUNGS)
    ld.add_argument("--x", type=int, required=True, help="unit X in USD, multiple of 10; adds are 1,2,3,6,12.. X")
    ld.add_argument("--stop", type=float, help="mandatory trigger price beyond the last rung")
    ld.add_argument("--dry-run", action="store_true")
    ls = sub.add_parser("ladder-sync", help="keep the stop over the filled size; stop hit cancels the unfilled rungs")
    ls.add_argument("--watch", type=float, help="poll every SECS seconds until the ladder is done")
    ls.add_argument("--max-polls", type=int, default=1000)
    sub.add_parser("net", help="net size across the co-trade slots from exchange positions")
    sub.add_parser("stop")
    sub.add_parser("kill")
    a = ap.parse_args(argv)

    do.select_environment(False)   # forces testnet; there is no mainnet flag
    secret_exists = lambda acct: do.secret_path_for("test", acct).exists()  # noqa: E731
    acct = pick_account(secret_exists)
    if a.cmd == "place":
        r = place_order(a.said, a.side, a.order_type, a.price, a.amount, a.stop, dry_run=a.dry_run,
                        account=acct, heard=a.heard, secret_exists=None if a.dry_run else secret_exists)
    elif a.cmd == "hedge":
        r = hedge(of=a.of, pct=a.pct, stop=a.stop, at=a.at, dry_run=a.dry_run, said=a.said)
    elif a.cmd == "ladder":
        r = place_ladder(a.said, a.side, a.frm, a.steps, a.x, a.stop, to=a.to, spacing_pct=a.spacing_pct,
                         spacing_pts=a.spacing_pts, dry_run=a.dry_run, account=acct,
                         secret_exists=None if a.dry_run else secret_exists)
    elif a.cmd == "ladder-sync":
        r = ladder_watch(a.watch, a.max_polls, account=acct) if a.watch else ladder_sync(account=acct)
    elif a.cmd == "net":
        r = net()
    elif a.cmd == "stop":
        r = ensure_stop(account=acct)
    else:
        r = kill(account=acct, secret_exists=secret_exists)
    print(json.dumps(r, indent=2, default=str))
    return 0 if r.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
