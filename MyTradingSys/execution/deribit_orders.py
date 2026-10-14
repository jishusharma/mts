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

v4 (FIX3, 2026-09-28): transport errors (timeout, reset, URLError, non-JSON
  body) never escape _call raw. Order-creating calls raise OrderStateUnknown
  (no retry); reads/cancels retry MAX_RETRIES then raise DeribitError.

v5 (mainnet-ready gates, 2026-09-29; design MyTradingSys/research/fast_track_2026-09-27/S5_MAINNET_FLAG.md):
  Default is and stays TESTNET (no flag, no confirmation, same URL, same secret
  file, same checks). Mainnet is reachable only via select_environment(mainnet=True)
  (CLI: `deribit_orders.py --mainnet`), which requires ALL of: (1) the explicit
  flag, (2) .secrets/mainnet.secret.json present with "env": "mainnet" (two-way
  match: a "test" secret can never be used on mainnet), (3) an interactive
  input() typed confirmation - never argv/env/config, (4) authenticate() still
  refuses any key with wallet:read_write (withdraw) scope. On mainnet every
  new-exposure order above MAINNET_MAX_NOTIONAL_USD is refused offline before
  any HTTP call. No mainnet call is ever made at import or by a refusal path.

v6 (2026-09-29, operator decision): select_environment(True, kill_only=True) - used ONLY by kill_switch.py
  --mainnet - replaces the long typed sentence with the single word `kill` (interactive input(), case-sensitive).
  Rationale: the kill switch can only reduce risk. Gates 1, 2 and 4 (flag, secret env match, interactive prompt)
  and the withdraw-scope refusal all still apply; every other mainnet path keeps the full sentence.

v7 (2026-10-14, reject diagnostics): a DeribitError raised by an order call (private/buy|sell, private/edit) now also
  carries `.request`, a WHITELISTED view of what was sent (REQUEST_DIAG_FIELDS: no token, no credentials), so the
  executor can journal the request next to the error. Plan L-mkt-1012-0945 got 10031 invalid_args_for_instrument on a
  market entry and the journal kept only the error, so the cause could not be proven. Diagnostics only: the same
  exception is raised at the same point, retries / OrderStateUnknown / return values are untouched.
"""
import sys
sys.dont_write_bytecode = True

import json
import time
import itertools
import os
import re
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECRET = ROOT / "MyTradingSys" / "execution" / ".secrets" / "testnet.secret.json"
BASE = "https://test.deribit.com/api/v2"  # DEFAULT environment (testnet); mainnet only via select_environment()
MAINNET_BASE = "https://www.deribit.com/api/v2"
MAINNET_SECRET = ROOT / "MyTradingSys" / "execution" / ".secrets" / "mainnet.secret.json"
DEFAULT_ENV = "test"
# Typed back at an interactive input() prompt; never accepted from argv/env/config.
MAINNET_CONFIRMATION = "I understand this places a real order with real money on BTC-PERPETUAL mainnet"
KILL_CONFIRMATION = "kill"   # typed word for the mainnet KILL SWITCH only (kill_only=True); it can only reduce risk
# Hard per-order / per-plan notional ceiling (USD) while env == mainnet. Read at call time.
MAINNET_MAX_NOTIONAL_USD = 50.0
_ACTIVE_ENV = DEFAULT_ENV

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
# FIX3 C1: timeouts/resets/URL errors (OSError), non-JSON bodies (ValueError)
# and non-JSON HTTP errors (RuntimeError from _post). Never escape _call raw:
# order-creating calls -> OrderStateUnknown, everything else -> DeribitError.
TRANSPORT_ERRORS = (OSError, urllib.error.URLError, ValueError, RuntimeError)
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
        self.request = None   # set by _call_with_request on order calls: whitelisted view of what was sent
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


class MainnetRefused(RuntimeError):
    """Offline refusal of a mainnet action (gate/cap). Raised BEFORE any HTTP call."""


def active_env() -> str:
    return _ACTIVE_ENV


def _base() -> str:
    return MAINNET_BASE if _ACTIVE_ENV == "mainnet" else BASE


def secret_path_for(env: str, account: str = None) -> Path:
    """Credentials file. account (env var MTS_ACCOUNT) only selects a named TESTNET subaccount file
    .secrets/testnet_<account>.secret.json; it is refused on mainnet."""
    if env == "mainnet":
        if account:
            raise RuntimeError("REFUSED: named accounts are testnet-only")
        return MAINNET_SECRET
    if not account:
        return SECRET
    if not re.fullmatch(r"[a-z0-9_]{1,32}", account):
        raise RuntimeError(f"REFUSED: bad account label {account!r}")
    return SECRET.parent / f"testnet_{account}.secret.json"


_ENV_ACCOUNT = object()   # sentinel: take the account from MTS_ACCOUNT at call time
_TOKEN_ACCOUNT = {}       # access_token -> account label it was issued for (None = main); B148


def _load_secret(env: str = None, account=_ENV_ACCOUNT) -> dict:
    env = env or _ACTIVE_ENV
    if env not in ("test", "mainnet"):
        raise RuntimeError(f"REFUSED: unknown environment {env!r}")
    if account is _ENV_ACCOUNT:
        account = os.environ.get("MTS_ACCOUNT") or None
    path = secret_path_for(env, account)
    if not path.exists():
        raise RuntimeError(f"MISSING: {path} - operator must create it first (see execution/README.md)")
    cfg = json.loads(path.read_text(encoding="utf-8"))
    if cfg.get("env") != env:  # two-way: a "test" secret never authenticates mainnet, and vice versa
        raise RuntimeError(f'REFUSED: secret file env must be "{env}"')
    return cfg


def select_environment(mainnet: bool = False, kill_only: bool = False) -> str:
    """Gate 1 (explicit flag) + gate 2 (secret env match, file read only) +
    gate 4 (typed confirmation via input()). Gate 3 (withdraw-scope refusal)
    lives in authenticate(). mainnet=False (default) -> testnet, no prompt.
    State changes only after every check passed; any refusal leaves/returns
    the process on testnet and makes no network call. kill_only=True (kill switch only) accepts the word
    KILL_CONFIRMATION instead of MAINNET_CONFIRMATION; nothing else changes."""
    global _ACTIVE_ENV
    if not mainnet:
        _ACTIVE_ENV = DEFAULT_ENV
        return _ACTIVE_ENV
    _ACTIVE_ENV = DEFAULT_ENV
    _load_secret("mainnet")  # missing file / env mismatch -> RuntimeError, no network
    want = KILL_CONFIRMATION if kill_only else MAINNET_CONFIRMATION
    try:
        typed = input(f'Type exactly to enable MAINNET: "{want}"' + chr(10) + '> ' if not kill_only else
                      f'MAINNET KILL SWITCH - type {want} to cancel every order and close every position' + chr(10) + '> ')
    except EOFError:
        raise MainnetRefused("REFUSED: mainnet confirmation needs an interactive prompt")
    if typed != want:
        raise MainnetRefused("REFUSED: mainnet confirmation string mismatch")
    _ACTIVE_ENV = "mainnet"
    return _ACTIVE_ENV


def _check_mainnet_notional(instrument_name: str, amount, reduce_only: bool = False) -> None:
    """Mainnet only: refuse a new-exposure order above MAINNET_MAX_NOTIONAL_USD.
    BTC-PERPETUAL amount is USD notional (repo: executor.py S1 note). Any other
    instrument has unverified units on this cap, so it is refused on mainnet.
    reduce_only orders (protective stop, targets) cannot add exposure and are
    exempt - the entry they protect is already capped, and blocking a stop
    would leave a position naked."""
    if _ACTIVE_ENV != "mainnet" or reduce_only:
        return
    if instrument_name != "BTC-PERPETUAL":
        raise MainnetRefused(f"REFUSED: mainnet notional cap only defined for BTC-PERPETUAL, got {instrument_name}")
    if not isinstance(amount, (int, float)) or amount <= 0 or amount > MAINNET_MAX_NOTIONAL_USD:
        raise MainnetRefused(f"REFUSED: mainnet order notional {amount} > MAINNET_MAX_NOTIONAL_USD {MAINNET_MAX_NOTIONAL_USD}")


def mainnet_plan_refusal(max_position_size) -> str:
    """Executor preflight hook: reason string if the plan's max size breaks the
    mainnet cap, else None. Always None on testnet."""
    if _ACTIVE_ENV != "mainnet":
        return None
    if not isinstance(max_position_size, (int, float)) or max_position_size > MAINNET_MAX_NOTIONAL_USD:
        return f"mainnet plan notional {max_position_size} > MAINNET_MAX_NOTIONAL_USD {MAINNET_MAX_NOTIONAL_USD}"
    return None


def _post(method: str, params: dict, token: str = None) -> dict:
    payload = json.dumps({"jsonrpc": "2.0", "id": next(_ids), "method": method, "params": params}).encode()
    headers = {"User-Agent": "MTS-T050/2.0", "Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(f"{_base()}/{method}", data=payload, headers=headers, method="POST")
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
        try:
            body = _post(method, params, token)
        except TRANSPORT_ERRORS as ex:
            # FIX3 C1: a lost response on an order-creating call is the
            # classic ambiguous outcome - never retry, caller must reconcile.
            if creates_order:
                raise OrderStateUnknown(method, params_label, f"transport:{ex!r}")
            if retry and attempt < MAX_RETRIES:
                attempt += 1
                time.sleep(backoff)
                backoff *= 2
                continue
            raise DeribitError(method, {"code": None, "message": f"transport error: {ex!r}"})
        if "error" not in body:
            return body["result"]
        code = body["error"].get("code")
        if token and code in AUTH_ERROR_CODES and not reauthed:
            try:
                # B148: a token may only be refreshed as the account that issued it. Re-reading MTS_ACCOUNT here
                # logged a subaccount's expired token back in as MAIN (the daily-loss monitor restores the env).
                old = token
                token = authenticate(_TOKEN_ACCOUNT.pop(old)) if old in _TOKEN_ACCOUNT else authenticate()
            except DeribitError:
                raise
            except Exception as ex:  # FIX3 C1: never escape raw
                raise DeribitError(method, {"code": code, "message": f"re-auth failed: {ex!r}"})
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


# Request fields that may be journaled on a rejection. A whitelist, never a copy of params: a field added to a request
# later (token, credentials) must be opted in here on purpose. public/auth is never wrapped, so its secret never gets here.
REQUEST_DIAG_FIELDS = ("order_id", "instrument_name", "amount", "type", "price", "label", "reduce_only", "post_only",
                       "trigger_price", "trigger")


def _request_view(method: str, params: dict) -> dict:
    """What was sent, whitelisted (REQUEST_DIAG_FIELDS) - diagnostics for a rejected order call."""
    return {"method": method, **{k: params[k] for k in REQUEST_DIAG_FIELDS if k in params}}


def _call_with_request(method: str, params: dict, token: str = None, **kw) -> dict:
    """_call for order calls: a DeribitError (incl. OrderStateUnknown) leaves here with .request set. Same exception,
    re-raised as-is - no change to retries, ambiguity handling or the caller's flow."""
    try:
        return _call(method, params, token, **kw)
    except DeribitError as e:
        e.request = _request_view(method, params)
        raise


def authenticate(account=_ENV_ACCOUNT) -> str:
    """Fresh access_token. Refuses withdraw-capable keys (testnet and mainnet). account=None forces MAIN,
    a label forces that named testnet account; default reads MTS_ACCOUNT. The token's account is remembered
    so a mid-session re-auth in _call refreshes the same account (B148)."""
    cfg = _load_secret(account=account)
    auth = _call("public/auth", {
        "grant_type": "client_credentials",
        "client_id": cfg["client_id"],
        "client_secret": cfg["client_secret"],
    }, retry=False)
    if "wallet:read_write" in auth.get("scope", ""):
        raise RuntimeError("REFUSED: key can withdraw (wallet:read_write). Recreate it with wallet none/read.")
    token = auth["access_token"]
    _TOKEN_ACCOUNT[token] = (os.environ.get("MTS_ACCOUNT") or None) if account is _ENV_ACCOUNT else account
    if len(_TOKEN_ACCOUNT) > 64:   # tokens are replaced on re-auth; bound the map anyway
        _TOKEN_ACCOUNT.pop(next(iter(_TOKEN_ACCOUNT)))
    return token


# ---------------------------------------------------------------- orders

def _place_order(direction, token, instrument_name, amount, order_type, price=None, label=None,
                 reduce_only=False, trigger_price=None, trigger=None, post_only=False) -> dict:
    _check_mainnet_notional(instrument_name, amount, reduce_only)  # offline, before any call
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
    return _call_with_request(f"private/{direction}", params, token, creates_order=True, params_label=label_str)


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
    return _call_with_request("private/edit", params, token)


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


def get_user_trades_by_instrument_and_time(token, instrument_name: str, start_ms: int, end_ms: int,
                                           count: int = 100) -> list:
    """Deribit official private/get_user_trades_by_instrument_and_time (params
    instrument_name, start_timestamp, end_timestamp, count; result {trades, has_more};
    each trade carries order_id, label, direction, amount, reduce_only). Follows
    has_more by moving end_timestamp back (sorting=desc); raises DeribitError past
    50 pages (fail closed)."""
    trades = []
    for _ in range(50):
        r = _call("private/get_user_trades_by_instrument_and_time",
                  {"instrument_name": instrument_name, "start_timestamp": start_ms,
                   "end_timestamp": end_ms, "count": count, "sorting": "desc"}, token)
        page = r.get("trades", []) if isinstance(r, dict) else (r or [])
        trades.extend(page)
        if not (isinstance(r, dict) and r.get("has_more")) or not page:
            return trades
        end_ms = min(int(t["timestamp"]) for t in page)
    raise DeribitError("private/get_user_trades_by_instrument_and_time",
                       {"code": None, "message": "more than 50 pages"})


def get_account_summary(token, currency: str = "BTC") -> dict:
    return _call("private/get_account_summary", {"currency": currency}, token)


def get_transaction_log(token, currency: str = "BTC", start_ms: int = 0, end_ms: int = 0,
                        max_pages: int = 50) -> list:
    """All private/get_transaction_log entries in [start_ms, end_ms], following
    `continuation`. Field names (logs, continuation, count, start_timestamp,
    end_timestamp) as used by the repo's testnet probe_transaction_log.py.
    More than max_pages pages raises DeribitError (fail closed, never truncate)."""
    entries, continuation = [], None
    for _ in range(max_pages):
        params = {"currency": currency, "start_timestamp": start_ms, "end_timestamp": end_ms, "count": 100}
        if continuation:
            params["continuation"] = continuation
        result = _call("private/get_transaction_log", params, token)
        if isinstance(result, dict):
            entries.extend(result.get("logs", []))
            continuation = result.get("continuation")
        else:
            entries.extend(result if isinstance(result, list) else [])
            continuation = None
        if not continuation:
            return entries
    raise DeribitError("private/get_transaction_log", {"code": None, "message": f"more than {max_pages} pages"})


def get_ticker(instrument_name: str = "BTC-PERPETUAL") -> dict:
    return _call("public/ticker", {"instrument_name": instrument_name})


# ---------------------------------------------------------------- T050 phase 3 (single-position order management)

def place(token, side: str, instrument_name: str, amount, order_type: str = "limit", price=None,
          label: str = None, post_only: bool = False, reduce_only: bool = False) -> dict:
    """Phase 3 testnet placement. Refuses off testnet and malformed input before any HTTP call.
    Returns the exchange's order dict (result['order']), never a guess."""
    if _ACTIVE_ENV != "test":
        raise RuntimeError("REFUSED: T050 phase 3 place() is testnet-only")
    if side not in ("buy", "sell"):
        raise ValueError(f"REFUSED: side must be buy|sell, got {side!r}")
    if not isinstance(amount, (int, float)) or isinstance(amount, bool) or amount <= 0:
        raise ValueError(f"REFUSED: amount must be > 0, got {amount!r}")
    if order_type == "limit" and (not isinstance(price, (int, float)) or price <= 0):
        raise ValueError("REFUSED: limit order needs price > 0")
    res = _place_order(side, token, instrument_name, amount, order_type, price, label,
                       reduce_only, post_only=post_only)
    order = res.get("order") if isinstance(res, dict) else None
    if not order or "order_id" not in order:
        raise OrderStateUnknown(f"private/{side}", label or instrument_name, "no_order_in_response")
    return order


def amend(token, order_id: str, amount=None, price=None) -> dict:
    """Edit an open order. At least one of amount/price is required (fails closed)."""
    if amount is None and price is None:
        raise ValueError("REFUSED: amend needs amount and/or price")
    if amount is not None and (not isinstance(amount, (int, float)) or amount <= 0):
        raise ValueError(f"REFUSED: amount must be > 0, got {amount!r}")
    if price is not None and (not isinstance(price, (int, float)) or price <= 0):
        raise ValueError(f"REFUSED: price must be > 0, got {price!r}")
    res = edit(token, order_id, amount=amount, price=price)
    return res.get("order", res) if isinstance(res, dict) else res


def get_order_history(token, instrument_name: str = "BTC-PERPETUAL", count: int = 100) -> list:
    """private/get_order_history_by_instrument (filled/cancelled/rejected orders, newest first)."""
    return _call("private/get_order_history_by_instrument",
                 {"instrument_name": instrument_name, "count": count, "include_old": True,
                  "include_unfilled": True}, token)


def reconcile_open(token, order_id: str, instrument_name: str = "BTC-PERPETUAL") -> dict:
    """A placed order must appear in the account open-orders read. {ok, order}."""
    order = next((o for o in get_open_orders(token, instrument_name) if o.get("order_id") == order_id), None)
    return {"ok": order is not None, "order": order}


def reconcile_filled(token, order_id: str, instrument_name: str = "BTC-PERPETUAL") -> dict:
    """A filled order must appear in order history with state 'filled' and be absent from open orders."""
    order = next((o for o in get_order_history(token, instrument_name) if o.get("order_id") == order_id), None)
    still_open = reconcile_open(token, order_id, instrument_name)["ok"]
    return {"ok": bool(order) and order.get("order_state") == "filled" and not still_open, "order": order}


def main(argv=None) -> int:
    """Smoke test: auth + reads, no orders. `--mainnet` runs it against mainnet
    (after the typed confirmation); without it, testnet exactly as before."""
    argv = sys.argv[1:] if argv is None else argv
    try:
        select_environment("--mainnet" in argv)
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
