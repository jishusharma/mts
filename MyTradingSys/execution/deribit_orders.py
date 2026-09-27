"""
MyTradingSys/execution/deribit_orders.py  (v2, Opus 5.5 review 2026-09-27)

Order-placement wrapper for Deribit TESTNET. REST, synchronous, stdlib-only.

v3 (G-h fix, 2026-09-28): order-CREATING calls (private/buy, private/sell,
  private/close_position) no longer auto-retry on an ambiguous-outcome error
  code - a lost response does not mean the exchange rejected the order, and
  resending private/buy|sell|close_position can double the position. Only
  error codes CONFIRMED by repo docs (research/deribit_api_research.md) to
  mean "rejected before processing" (10028 rate-limited, 10047 portfolio
  queue full) still auto-retry for order-creating calls. 10050 (queue/request
  timeout) has NO documented meaning anywhere in this repo - its old comment
  ("queue timeout") was never confirmed against a Deribit error table or repo
  doc, so it is treated as ambiguous: order-creating calls now raise
  OrderStateUnknown instead of retrying; reads/cancel/edit are unaffected.

v2 changes vs v1 (review findings):
  - All calls are JSON-RPC over HTTP POST. v1 sent client_secret and every
    param in the GET query string (ends up in proxy/server logs). Fixed.
  - Token auto re-auth once on 13009/13010/13011 instead of failing mid-plan.
  - B077: stop_market() helper. A protective stop is a server-side
    stop_market (reduce_only, trigger=mark_price by default), never a
    reduce-only LIMIT (a sell limit below market fills instantly).
  - B078: cancel_by_label() uses Deribit's private/cancel_by_label, which is
    label-scoped server-side. v1's cancel_all_by_label actually cancelled
    every order in the currency. The old name is kept as an alias of the
    label-scoped call so no caller can reach the cancel-everything path.
  - get_position(), close_position() (emergency flatten), get_ticker().

Design answer to v1's open question (REST vs WebSocket): REST polling is
sufficient for T050 because the protective stop lives SERVER-side as a
stop_market. Polling latency then only delays stop RESIZING (after a new
ladder fill), not stop EXISTENCE. Revisit WebSocket only for sub-second
fill-driven logic (satellites, T048).

Never prints the secret or the access token.
"""
import sys
sys.dont_write_bytecode = True

import json
import time
import itertools
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECRET = ROOT / "MyTradingSys" / "execution" / ".secrets" / "testnet.secret.json"
BASE = "https://test.deribit.com/api/v2"  # testnet only - deliberately not parameterised

# Confirmed by MyTradingSys/research/deribit_api_research.md ("Critical Error
# Codes & Handling" table) as rejected BEFORE the order reached processing -
# safe to retry even for order-creating calls: the exchange never acted.
CONFIRMED_PRE_PROCESSING_REJECT_CODES = {10028, 10047}  # rate limited; portfolio queue full

# Outcome NOT confirmed by any repo doc/comment/error table (grepped
# research/*.md and execution/*.py - 10050 appears nowhere except this file's
# own prior comment, which was never sourced). Genuinely ambiguous: the
# request may have been accepted and only the response lost. Never invent
# Deribit semantics for these - for order-creating calls they raise
# OrderStateUnknown instead of retrying.
AMBIGUOUS_OUTCOME_CODES = {10050}

# Non-order calls (reads, cancel, edit) keep retrying on both sets - unchanged
# from v2 behaviour.
RETRYABLE_ERROR_CODES = CONFIRMED_PRE_PROCESSING_REJECT_CODES | AMBIGUOUS_OUTCOME_CODES
AUTH_ERROR_CODES = {13009, 13010, 13011}        # token expired / invalid
MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 1

_ids = itertools.count(1)


class DeribitError(Exception):
    """Non-retryable API error. Hard stop for callers - never default to success."""
    def __init__(self, method, error):
        self.method = method
        self.error = error
        self.code = error.get("code") if isinstance(error, dict) else None
        super().__init__(f"{method}: {error}")


class OrderStateUnknown(DeribitError):
    """An order-creating call got an error code whose meaning (accepted-but-
    response-lost vs rejected-before-processing) cannot be confirmed from
    repo documentation. The exchange may or may not have created the order.
    The caller MUST reconcile (get_open_orders/get_position/label lookup)
    before doing anything else - never assume success, never assume failure,
    and never blindly retry (retrying is exactly what could double the
    position)."""
    def __init__(self, method, params_label, code):
        # Subclass of DeribitError so every existing `except do.DeribitError`
        # handler routes it into fail_closed / flatten_halt (reconcile by
        # position + label) instead of crashing past them (G-h review 2026-09-28).
        super().__init__(method, {"code": code, "message":
            f"({params_label}) ambiguous error code {code} - "
            f"order state unknown, caller must reconcile before proceeding"})
        self.params_label = params_label


def _load_secret() -> dict:
    if not SECRET.exists():
        raise RuntimeError(f"MISSING: {SECRET} - operator must create it first (see execution/README.md)")
    cfg = json.loads(SECRET.read_text(encoding="utf-8"))
    if cfg.get("env") != "test":
        raise RuntimeError('REFUSED: secret file env must be "test"')
    return cfg


def _post(method: str, params: dict, token: str = None) -> dict:
    payload = json.dumps({"jsonrpc": "2.0", "id": next(_ids), "method": method, "params": params}).encode()
    headers = {"User-Agent": "MTS-T050/2.0", "Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(f"{BASE}/{method}", data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode("utf-8"))
        except Exception:
            raise RuntimeError(f"{method}: HTTP {e.code}")


def _call(method: str, params: dict, token: str = None, retry: bool = True,
         creates_order: bool = False, params_label: str = None) -> dict:
    """Backs off on RETRYABLE_ERROR_CODES only; re-auths once on an expired
    token; every other error raises DeribitError immediately.

    creates_order=True (private/buy, private/sell, private/close_position):
    an AMBIGUOUS_OUTCOME_CODES code (10050) is NEVER retried - it raises
    OrderStateUnknown instead, because we cannot confirm the exchange didn't
    already accept the order. CONFIRMED_PRE_PROCESSING_REJECT_CODES (10028,
    10047) still retry even for order-creating calls: those are confirmed
    (research/deribit_api_research.md) to mean the request never reached
    processing."""
    attempt, backoff, reauthed = 0, INITIAL_BACKOFF_SECONDS, False
    while True:
        body = _post(method, params, token)
        if "error" not in body:
            return body["result"]
        code = body["error"].get("code")
        if token and code in AUTH_ERROR_CODES and not reauthed:
            token = authenticate()
            reauthed = True
            continue
        if creates_order and code in AMBIGUOUS_OUTCOME_CODES:
            raise OrderStateUnknown(method, params_label, code)
        if retry and code in RETRYABLE_ERROR_CODES and attempt < MAX_RETRIES:
            attempt += 1
            time.sleep(backoff)
            backoff *= 2
            continue
        raise DeribitError(method, body["error"])


def authenticate() -> str:
    """Fresh access_token. Refuses withdraw-capable keys."""
    cfg = _load_secret()
    auth = _call("public/auth", {
        "grant_type": "client_credentials",
        "client_id": cfg["client_id"],
        "client_secret": cfg["client_secret"],
    }, retry=False)
    if "wallet:read_write" in auth.get("scope", ""):
        raise RuntimeError("REFUSED: key can withdraw (wallet:read_write). Recreate it with wallet none/read.")
    return auth["access_token"]


# ---------------------------------------------------------------- orders

def _place_order(direction, token, instrument_name, amount, order_type, price=None, label=None,
                 reduce_only=False, trigger_price=None, trigger=None, post_only=False) -> dict:
    params = {"instrument_name": instrument_name, "amount": amount, "type": order_type}
    if price is not None:
        params["price"] = price
    if label:
        params["label"] = label
    if reduce_only:
        params["reduce_only"] = True
    if post_only:
        params["post_only"] = True
    if trigger_price is not None:
        params["trigger_price"] = trigger_price
        params["trigger"] = trigger or "mark_price"
    label_str = f"{direction} {instrument_name} {amount}@{order_type}" + (f" label={label}" if label else "")
    return _call(f"private/{direction}", params, token, creates_order=True, params_label=label_str)


def buy(token, instrument_name, amount, order_type, price=None, label=None, reduce_only=False, **kw):
    return _place_order("buy", token, instrument_name, amount, order_type, price, label, reduce_only, **kw)


def sell(token, instrument_name, amount, order_type, price=None, label=None, reduce_only=False, **kw):
    return _place_order("sell", token, instrument_name, amount, order_type, price, label, reduce_only, **kw)


def stop_market(token, instrument_name, side: str, amount: int, trigger_price: float,
                label: str, trigger: str = "mark_price") -> dict:
    """B077 fix: protective stop = server-side stop_market, reduce_only."""
    fn = sell if side == "SELL" else buy
    return fn(token, instrument_name, amount, "stop_market", label=label, reduce_only=True,
              trigger_price=trigger_price, trigger=trigger)


def edit(token, order_id, amount=None, price=None, trigger_price=None) -> dict:
    params = {"order_id": order_id}
    if amount is not None:
        params["amount"] = amount
    if price is not None:
        params["price"] = price
    if trigger_price is not None:
        params["trigger_price"] = trigger_price
    return _call("private/edit", params, token)


def cancel(token, order_id) -> dict:
    return _call("private/cancel", {"order_id": order_id}, token)


def cancel_by_label(token, label: str, currency: str = "BTC") -> int:
    """B078 fix: server-side label-scoped cancel. Returns number cancelled."""
    return _call("private/cancel_by_label", {"label": label, "currency": currency}, token)


cancel_all_by_label = cancel_by_label  # v1 name, now label-scoped


def close_position(token, instrument_name: str = "BTC-PERPETUAL") -> dict:
    """Emergency flatten (market). Order-creating (submits a market order) -
    same G-h ambiguous-code treatment as buy/sell."""
    return _call("private/close_position", {"instrument_name": instrument_name, "type": "market"}, token,
                 creates_order=True, params_label=f"close_position {instrument_name}")


# ---------------------------------------------------------------- reads

def get_position(token, instrument_name: str = "BTC-PERPETUAL") -> dict:
    return _call("private/get_position", {"instrument_name": instrument_name}, token)


def get_positions(token, currency: str = "BTC", kind: str = "future") -> list:
    return _call("private/get_positions", {"currency": currency, "kind": kind}, token)


def get_open_orders(token, instrument_name: str = "BTC-PERPETUAL", type_: str = "all") -> list:
    return _call("private/get_open_orders_by_instrument", {"instrument_name": instrument_name, "type": type_}, token)


def get_order_state(token, order_id) -> dict:
    return _call("private/get_order_state", {"order_id": order_id}, token)


def get_account_summary(token, currency: str = "BTC") -> dict:
    return _call("private/get_account_summary", {"currency": currency}, token)


def get_ticker(instrument_name: str = "BTC-PERPETUAL") -> dict:
    return _call("public/ticker", {"instrument_name": instrument_name})


def main() -> int:
    """Smoke test: auth + reads, no orders."""
    try:
        token = authenticate()
        s = get_account_summary(token)
        print(f"AUTH OK  equity={s.get('equity')} available_funds={s.get('available_funds')}")
        print(f"open orders: {len(get_open_orders(token))}  position size: {get_position(token).get('size')}")
    except Exception as e:
        print(f"FAIL: {type(e).__name__}: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
