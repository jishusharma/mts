"""
MyTradingSys/execution/daily_loss_monitor.py

Loop that watches today's (UTC) total account PnL and halts+flattens the
account when it breaches DEFAULT_DAILY_LOSS_CAP_USD (daily_loss_guard.py).

P&L SOURCE DECISION (read this before changing the math below):

  Nothing in this repo is a RECORDED REAL Deribit response for
  private/get_account_summary or private/get_position - grep of
  research/deribit_api_research.md and execution/journal/*.jsonl turned up
  only (a) a static field list in the research doc (equity, balance,
  available_funds, margin_balance, initial_margin, maintenance_margin;
  current_size, average_price, unrealized_pnl) and (b) per-order fill
  events (order_id, filled_amount, average_price) in the journal - never an
  actual account_summary/get_position JSON payload with real numbers.
  risk_guard.py.new independently flags the same gap for "size"
  ("denominated in USD in some Deribit endpoints and in contracts in
  others"). Per the no-fabrication rule, this module therefore does NOT
  invent inverse-contract PnL math (entry/exit price deltas -> BTC -> USD)
  from the raw fills - that conversion is real but UNEVIDENCED here.

  Instead this module uses the exchange's own equity number as the single
  source of truth for "today's total realized+unrealized PnL":

      total_pnl_usd(today) = (equity_now - equity_at_start_of_UTC_day) * mark_price_now

  equity and mark_price are the two field names already referenced by
  existing code (deribit_read.py prints account["equity"]; executor.py
  reads get_ticker()["mark_price"]), so the NAMES are code-evidenced, but
  their exact behavior (does equity already net open-position unrealized
  PnL? is it BTC-denominated?) is NOT evidenced by any captured response in
  this repo, so it is a documented, operator-verifiable ASSUMPTION, not a
  fabricated one:

    -> run scripts/dev's staged testnet probe:
         MyTradingSys/execution/testnet/probe_account_summary.py
       BEFORE trusting this module's live numbers. See that script's
       docstring for exactly what to check.

  The computed total_pnl_usd is fed into check_daily_loss_cap() as a
  single synthetic realized_pnl_events entry with unrealized_pnl_usd=0.0:
  check_daily_loss_cap(total) == sum(realized) + unrealized, so one event
  carrying the whole total is mathematically identical to a real
  realized/unrealized split and lets this module reuse daily_loss_guard.py
  UNCHANGED (that module is already staged+tested; do not edit it).

L6 PART 2 (2026-09-29) - PnL SOURCE, decision in research/fast_track_2026-09-27/
FIX4_DESIGN.md; arithmetic and field semantics in mainnet_pnl.py (audit HIGH #3, spec 129):
pnl_source="transaction_log" = (realized + session unrealized) [BTC] times mark_price, where
  realized   = sum over today's 00:00-UTC..now private/get_transaction_log entries of type
               "trade" or "settlement" (allow-list; every other type is ignored) of change,
               plus cashflow for trades when profit_as_cashflow is true (Deribit: a futures trade's realized session
               PnL is carried in cashflow until the 08:00 UTC settlement; change holds only
               the fee);
  unrealized = account summary futures_session_upl (fallback session_upl).
  Residual limits (honest): "settlement" entries are INCLUDED since B149 (captured testnet log: the 08:00
  settlement books the pre-08:00 P/L of a held position, the closing trade only the rest,
  no double count), so a position carried across 08:00 is counted; funding on perpetuals
  sits inside those entries, no separate funding type was seen. A missing or non-numeric field raises ValueError (fail closed: the
  consecutive-failure path writes HALT_DAILY_LOSS).
  Default source: "equity" on testnet (unchanged behaviour, keeps the FT-2
  testnet suite T-c identical); "transaction_log" whenever the client's
  active_env() is "mainnet". Override with --pnl-source.

HALT FILE CONTRACT (for executor.py's preflight() - documented here only;
executor.py is NOT edited by this module or its owner):
  On breach this module writes execution/HALT_DAILY_LOSS, a JSON object:
    {"date": "YYYY-MM-DD", "reason": "<str>", "ts_iso": "<str>"}
  A future change to executor.preflight() should treat the mere EXISTENCE
  of this file as an unconditional refusal reason (e.g.
  "daily loss halt active: <reason> - remove HALT_DAILY_LOSS after
  operator review to resume"), checked before any order is placed. This
  module never deletes the file itself - only an operator clears it,
  by design (the whole point of a hard halt is that it does not
  auto-resume).

AGGREGATE OVER NAMED TESTNET SUBACCOUNTS (operator 2026-10-08):
  On testnet the one loop also reads every named account in auto_trader_config.json "accounts" whose
  secret file exists (existence check only), authenticates each with MTS_ACCOUNT=<label>, and caps the SUM:
      total_pnl_usd = main account P&L + sum over named accounts of that account's P&L
  (each account's P&L computed exactly as above, with its own day-start equity kept in state["accounts"]).
  The existing threshold applies to that aggregate. A breach writes the same HALT_DAILY_LOSS and runs kill_all
  on the main account AND every named account. An unreadable account fails the whole iteration (the
  consecutive-failure path then fails closed): an aggregate that silently drops an account would under-count.
  A named account first seen mid-day is baselined at first sight (its earlier loss that day is not counted).
  Mainnet: unchanged, main account only (named accounts are testnet-only).

DEPENDENCY INJECTION for testability:
  client: duck-typed like kill_switch.kill_all's client - needs
    get_account_summary(token, currency="BTC") -> dict with "equity"
    get_ticker(instrument_name="BTC-PERPETUAL") -> dict with "mark_price"
    (kill_all's own client methods: get_positions/get_open_orders/cancel/
    close_position) - same object satisfies both.
  clock: zero-arg callable returning a timezone-aware UTC datetime.now().
    Injected so day-rollover can be tested without real waiting.
"""
import sys
sys.dont_write_bytecode = True

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import journal  # noqa: E402
import kill_switch  # noqa: E402
import mainnet_pnl  # noqa: E402
from daily_loss_guard import check_daily_loss_cap, format_breach_report, DEFAULT_DAILY_LOSS_CAP_USD  # noqa: E402

POLL_INTERVAL_SECONDS = 30
PNL_SOURCES = ("equity", "transaction_log")
EXCLUDED_TX_TYPES_EXACT = {"deposit", "withdrawal"}
EXCLUDED_TX_TYPE_PREFIXES = ("transfer",)
STATE_PATH = Path(__file__).resolve().parent / "daily_loss_monitor_state.json"
HALT_PATH = Path(__file__).resolve().parent / "HALT_DAILY_LOSS"
# PREMAINNET1 H1: mainnet has its OWN state + halt marker, so a testnet trip can never mask a mainnet breach
# (and vice versa). Testnet names are unchanged.
STATE_PATH_MAINNET = Path(__file__).resolve().parent / "daily_loss_monitor_state_mainnet.json"
HALT_PATH_MAINNET = Path(__file__).resolve().parent / "HALT_DAILY_LOSS_MAINNET"


def _client_env(client) -> str:
    f = getattr(client, "active_env", None)
    return "mainnet" if callable(f) and f() == "mainnet" else "test"


def paths_for_env(env: str):
    """(state_path, halt_path) for 'mainnet' or testnet; module globals read at call time."""
    return (STATE_PATH_MAINNET, HALT_PATH_MAINNET) if env == "mainnet" else (STATE_PATH, HALT_PATH)
JOURNAL_PLAN_ID = "ACCOUNT_DAILY_LOSS"
ACCOUNTS_CONFIG = Path(__file__).resolve().parent / "auto_trader_config.json"
SECRETS_DIR = Path(__file__).resolve().parent / ".secrets"
_LABEL_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789_")
MAX_CONSECUTIVE_FAILURES = 3  # FIX3 H3: then fail closed (write HALT_DAILY_LOSS) instead of dying. Mainnet.
# Testnet only: a 90 s DNS blip (3 x getaddrinfo, 2026-10-07 19:24Z) halted all calibration trading. 20 x 30 s poll =
# 10 min blind at most, then the same fail-closed halt. NO-SOURCE testnet calibration value (operator 2026-10-07).
MAX_CONSECUTIVE_FAILURES_TESTNET = 20


def failure_cap(env: str) -> int:
    return MAX_CONSECUTIVE_FAILURES if env == "mainnet" else MAX_CONSECUTIVE_FAILURES_TESTNET

# BLIND-HALT RECOVERY (operator 2026-10-17, policy: MyTradingSys/system/BLIND_HALT_POLICY.md, labelled OURS).
# Testnet only. The monitor clears ONLY a halt it wrote itself for blindness (kind "blind", owner below), after the
# account reads cleanly for BLIND_CLEAN_SECONDS. Interim operator value 30 min; the flap guards are ours, not sourced.
BLIND_CLEAN_SECONDS = 30 * 60
BLIND_MAX_CLEARS_PER_DAY = 2
BLIND_FLAP_SECONDS = 60 * 60       # a blind halt written within this long after a clear is never auto-cleared
BLIND_OWNER = "daily_loss_monitor"
HALT_HOLD_PATH = Path(__file__).resolve().parent / "HALT_DAILY_LOSS.hold"   # a human creates it to pin a halt


def halt_kind(halt_path: Path) -> str:
    """'none' (no file), 'blind' (written by this monitor for blindness), else 'loss'. Anything unreadable, torn,
    untagged or owned by someone else is 'loss': fail closed, never auto-cleared."""
    if not halt_path.exists():
        return "none"
    try:
        j = json.loads(halt_path.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return "loss"
    if isinstance(j, dict) and j.get("kind") == "blind" and j.get("owner") == BLIND_OWNER:
        return "blind"
    return "loss"


def write_blind_halt(halt_path: Path, date: str, reason: str, now) -> bool:
    """Testnet blind halt, tagged so it can be told from a loss halt. Never overwrites a loss halt (returns False)."""
    if halt_kind(halt_path) == "loss":
        return False
    halt_path.write_text(json.dumps({
        "date": date, "reason": reason, "ts_iso": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "kind": "blind", "owner": BLIND_OWNER,
    }), encoding="utf-8")
    return True


class BlindRecovery:
    """Counts clean reads after a blind halt and clears that halt (testnet only) when policy allows.
    The clean window lives in memory only: a restart starts it again (fail closed)."""

    def __init__(self, env, halt_path, state_path, clock=None, hold_path=None,
                 clean_seconds=None, max_clears=None, flap_seconds=None):
        self.env, self.halt_path, self.state_path = env, halt_path, state_path
        self.clock = clock or _utc_now
        self.hold_path = hold_path if hold_path is not None else HALT_HOLD_PATH
        self.clean_seconds = BLIND_CLEAN_SECONDS if clean_seconds is None else clean_seconds
        self.max_clears = BLIND_MAX_CLEARS_PER_DAY if max_clears is None else max_clears
        self.flap_seconds = BLIND_FLAP_SECONDS if flap_seconds is None else flap_seconds
        self.clean_since = None

    def note_failure(self):
        self.clean_since = None

    def note_clean(self, result) -> str:
        """Call after every successful run_once. Returns a status word; 'cleared' only when the file was removed."""
        if self.env == "mainnet":
            return "mainnet"
        if halt_kind(self.halt_path) != "blind":
            self.clean_since = None
            return "none"
        st = (result or {}).get("state") or {}
        if not (result or {}).get("ok") or st.get("breached_today"):
            self.clean_since = None
            return "loss"
        now = self.clock()
        if self.clean_since is None:
            self.clean_since = now
        if (now - self.clean_since).total_seconds() < self.clean_seconds:
            return "waiting"
        if self.hold_path.exists():
            return "held"
        try:
            state = load_state(self.state_path)
        except StateUnreadable:
            return "state"
        clears = state.get("blind_clears")
        clears = clears if isinstance(clears, list) else []
        if len(clears) >= self.max_clears:
            return "cap"
        if clears:
            try:
                last = datetime.strptime(clears[-1], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                halted = datetime.strptime(json.loads(self.halt_path.read_text(encoding="utf-8"))["ts_iso"],
                                           "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            except (ValueError, KeyError, OSError, TypeError):
                return "flap"
            if (halted - last).total_seconds() < self.flap_seconds:
                return "flap"
        if halt_kind(self.halt_path) != "blind":      # re-check right before removing (a loss halt may have landed)
            return "none"
        self.halt_path.unlink()
        state["blind_clears"] = clears + [now.strftime("%Y-%m-%dT%H:%M:%SZ")]
        save_state(state, self.state_path)
        journal.append_event(JOURNAL_PLAN_ID, "reconciliation", {
            "source": "daily_loss_monitor", "result": "blind halt auto-cleared",
            "clean_seconds": int((now - self.clean_since).total_seconds()), "clears_today": len(clears) + 1})
        self.clean_since = None
        return "cleared"


class StateUnreadable(Exception):
    """FIX3 H4: the state file exists but cannot be trusted - never re-baseline."""


def _utc_now():
    return datetime.now(timezone.utc)


def _today_str(now):
    return now.strftime("%Y-%m-%d")


def load_state(state_path: Path = STATE_PATH) -> dict:
    """Missing file -> {} (first run). Present but unreadable/torn/non-dict ->
    StateUnreadable (FIX3 H4): re-snapshotting the baseline from current
    equity would silently erase the day's loss."""
    if not state_path.exists():
        return {}
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:  # ValueError covers JSON and Unicode decode errors
        raise StateUnreadable(f"{state_path.name}: {e!r}")
    if not isinstance(state, dict):
        raise StateUnreadable(f"{state_path.name}: not a JSON object")
    return state


def save_state(state: dict, state_path: Path = STATE_PATH):
    # FIX3 H4: atomic - a crash mid-write can never leave a torn state file
    tmp = state_path.with_name(state_path.name + ".tmp")
    tmp.write_text(json.dumps(state), encoding="utf-8")
    os.replace(tmp, state_path)


def write_halt(halt_path: Path, date: str, reason: str, now) -> None:
    halt_path.write_text(json.dumps({
        "date": date,
        "reason": reason,
        "ts_iso": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }), encoding="utf-8")


def ensure_day_state(client, token, now, currency: str = "BTC", state_path: Path = STATE_PATH) -> dict:
    """Load state; if it's missing or belongs to a previous UTC day, snapshot
    today's opening equity and reset breached_today. Returns the (possibly
    reset) state dict; caller is responsible for persisting it."""
    state = load_state(state_path)
    today = _today_str(now)
    if state.get("date") != today:
        summary = client.get_account_summary(token, currency=currency)
        state = {
            "date": today,
            "day_start_equity": summary["equity"],
            "breached_today": False,
        }
    return state


def _is_money_movement(tx_type) -> bool:
    t = str(tx_type or "").lower()
    return t in EXCLUDED_TX_TYPES_EXACT or t.startswith(EXCLUDED_TX_TYPE_PREFIXES)


def _day_start_ms(date_str: str) -> int:
    d = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return int(d.timestamp() * 1000)


def transaction_log_pnl_btc(entries) -> float:
    """DEPRECATED (audit HIGH #3): change-only sum, misses cashflow when profit_as_cashflow
    is true; compute_total_pnl_usd now uses mainnet_pnl.daily_pnl_btc. Kept for existing
    tests. sum(change) over entries, minus money-movement types. An entry with no
    numeric 'change' raises ValueError - never silently skipped (fail closed:
    the monitor's consecutive-failure path then writes HALT_DAILY_LOSS)."""
    total = 0.0
    for i, e in enumerate(entries):
        if _is_money_movement(e.get("type")):
            continue
        ch = e.get("change")
        if isinstance(ch, bool) or not isinstance(ch, (int, float)):
            raise ValueError(f"transaction_log entry {i} (type={e.get('type')!r}) has no numeric 'change'")
        total += ch
    return total


def default_pnl_source(client) -> str:
    # XFERFIX 2026-09-29: equity delta counts deposits/withdrawals/subaccount transfers as P/L (a 40 BTC
    # testnet transfer-out tripped the kill switch). Any client that can read the transaction log uses it
    # (mainnet AND testnet); the equity fallback remains only for clients without a log.
    env = getattr(client, "active_env", None)
    if callable(env) and env() == "mainnet":
        return "transaction_log"
    return "transaction_log" if callable(getattr(client, "get_transaction_log", None)) else "equity"


def compute_total_pnl_usd(client, token, state: dict, currency: str = "BTC",
                           instrument: str = "BTC-PERPETUAL", pnl_source: str = None,
                           now_ms: int = None) -> float:
    pnl_source = pnl_source or default_pnl_source(client)
    if pnl_source not in PNL_SOURCES:
        raise ValueError(f"pnl_source must be one of {PNL_SOURCES}, got {pnl_source!r}")
    if pnl_source == "transaction_log":
        end_ms = now_ms if now_ms is not None else int(time.time() * 1000)
        entries = client.get_transaction_log(token, currency=currency,
                                             start_ms=_day_start_ms(state["date"]), end_ms=end_ms)
        ticker = client.get_ticker(instrument_name=instrument)
        summary = client.get_account_summary(token, currency=currency)
        return round(mainnet_pnl.daily_pnl_btc(entries, summary) * ticker["mark_price"], 2)
    summary = client.get_account_summary(token, currency=currency)
    ticker = client.get_ticker(instrument_name=instrument)
    equity_delta = summary["equity"] - state["day_start_equity"]
    return round(equity_delta * ticker["mark_price"], 2)


def run_once(client, token, clock=_utc_now, currency: str = "BTC",
             instrument: str = "BTC-PERPETUAL", cap_usd: float = DEFAULT_DAILY_LOSS_CAP_USD,
             state_path: Path = None, halt_path: Path = None, pnl_source: str = None,
             accounts: dict = None) -> dict:
    """Single monitor iteration. Returns the check_daily_loss_cap() result
    dict (plus 'state' for tests). Idempotent: a breach only triggers
    kill_all/HALT-file/journal once per UTC day (state['breached_today']).
    
    Re-arms breached_today flag if HALT_DAILY_LOSS file is cleared by operator.
    accounts: optional {label: (client, token)} of named TESTNET subaccounts; their P&L is added to the main
    account's and the cap applies to the sum (see AGGREGATE above). None/{} = main account only (unchanged)."""
    env_state, env_halt = paths_for_env(_client_env(client))
    state_path = state_path or env_state
    halt_path = halt_path or env_halt
    now = clock()
    try:
        state = ensure_day_state(client, token, now, currency=currency, state_path=state_path)
    except StateUnreadable as e:
        # FIX3 H4: fail closed - halt, do not re-baseline, leave the file for the operator
        write_halt(halt_path, _today_str(now), f"daily_loss_monitor state unreadable: {e}", now)
        return {"ok": False, "reason": f"state unreadable - HALT_DAILY_LOSS written: {e}",
                "total_pnl_usd": None, "state": None}

    # L6 part 1: re-arm breached_today if operator cleared the halt file
    if state.get("breached_today") and not halt_path.exists():
        state["breached_today"] = False
        save_state(state, state_path)
        journal.append_event(JOURNAL_PLAN_ID, "reconciliation", {
            "source": "daily_loss_monitor",
            "result": "re-armed by operator clear"
        })

    now_ms = int(now.timestamp() * 1000)
    total_pnl_usd = compute_total_pnl_usd(client, token, state, currency=currency, instrument=instrument,
                                          pnl_source=pnl_source, now_ms=now_ms)
    per_account = None
    if accounts:
        per_account = {"main": total_pnl_usd}
        base = state.setdefault("accounts", {})
        new = [lab for lab in accounts if lab not in base]
        for lab in new:
            c, t = accounts[lab]
            base[lab] = c.get_account_summary(t, currency=currency)["equity"]
        if new:
            save_state(state, state_path)          # a baseline must never be re-taken later in the day
        for lab, (c, t) in accounts.items():
            per_account[lab] = compute_total_pnl_usd(c, t, {"date": state["date"], "day_start_equity": base[lab]},
                                                     currency=currency, instrument=instrument,
                                                     pnl_source=pnl_source, now_ms=now_ms)
        total_pnl_usd = round(sum(per_account.values()), 2)
    result = check_daily_loss_cap([{"pnl_usd": total_pnl_usd}], 0.0, cap_usd=cap_usd)

    if not result["ok"] and not state.get("breached_today"):
        reason = result["reason"]
        journal.append_event(JOURNAL_PLAN_ID, "error", {
            "source": "daily_loss_monitor",
            "total_pnl_usd": total_pnl_usd,
            "cap_usd": cap_usd,
            "reason": reason,
            **({"per_account_pnl_usd": per_account} if per_account else {}),
        })
        # FIX3 H3: HALT first, and regardless of whether kill_all works
        write_halt(halt_path, state["date"], reason, now)
        state["breached_today"] = True
        save_state(state, state_path)
        # flatten every account in the aggregate; one account's kill failure never skips the others
        for lab, (c, t) in [("main", (client, token))] + list((accounts or {}).items()):
            try:
                kill_result = kill_switch.kill_all(c, t, currency=currency)
                journal.append_event(JOURNAL_PLAN_ID, "error", {
                    "source": "daily_loss_monitor", "account": lab,
                    "kill_switch_report": kill_switch.format_kill_report(kill_result),
                    "kill_switch_ok": kill_result["ok"],
                })
            except Exception as e:  # noqa: BLE001
                journal.append_event(JOURNAL_PLAN_ID, "error", {
                    "source": "daily_loss_monitor", "account": lab, "kill_switch_ok": False,
                    "kill_switch_error": repr(e)})

    save_state(state, state_path)
    result["state"] = state
    if per_account:
        result["per_account_pnl_usd"] = per_account
    return result


_LAST_GOOD_LABELS = {}   # str(config_path) -> labels from the last successful read (B148)


def named_account_labels(config_path: Path = None, secrets_dir: Path = None) -> list:
    """Sorted valid labels from auto_trader_config.json "accounts" whose testnet secret file exists
    (existence check only, never read). Unreadable config -> the last good list; with no last good list it RAISES
    (the caller's failure path counts it), because [] would silently drop accounts auto_trader keeps trading."""
    config_path, secrets_dir = config_path or ACCOUNTS_CONFIG, secrets_dir or SECRETS_DIR
    try:
        table = json.loads(Path(config_path).read_text(encoding="utf-8")).get("accounts") or {}
        labels = {v for v in table.values() if isinstance(v, str) and 0 < len(v) <= 32 and set(v) <= _LABEL_CHARS}
    except (OSError, ValueError, AttributeError) as e:
        if str(config_path) in _LAST_GOOD_LABELS:
            return list(_LAST_GOOD_LABELS[str(config_path)])
        raise RuntimeError(f"accounts config unreadable and no earlier good read: {e!r}")
    out = sorted(lab for lab in labels if (Path(secrets_dir) / f"testnet_{lab}.secret.json").exists())
    _LAST_GOOD_LABELS[str(config_path)] = out
    return out


def refresh_named_accounts(do, current: dict, labels: list) -> dict:
    """{label: (do, token)} for labels; keeps existing tokens, authenticates new labels with MTS_ACCOUNT=label
    (restored afterwards). Raises on an auth failure (the caller's failure path counts it)."""
    out = {lab: current[lab] for lab in labels if lab in current}
    prev = os.environ.get("MTS_ACCOUNT")
    try:
        for lab in labels:
            if lab not in out:
                os.environ["MTS_ACCOUNT"] = lab
                out[lab] = (do, do.authenticate())
    finally:
        if prev is None:
            os.environ.pop("MTS_ACCOUNT", None)
        else:
            os.environ["MTS_ACCOUNT"] = prev
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description="Daily loss monitor loop for MTS.")
    parser.add_argument("--once", action="store_true", help="Run a single iteration and exit (for cron/scheduling).")
    parser.add_argument("--interval", type=float, default=POLL_INTERVAL_SECONDS, help="Seconds between iterations.")
    parser.add_argument("--mainnet", action="store_true", help="MAINNET (typed confirmation required)")
    parser.add_argument("--currency", default="BTC")
    parser.add_argument("--instrument", default="BTC-PERPETUAL")
    parser.add_argument("--pnl-source", choices=PNL_SOURCES, default=None,
                        help="default: transaction_log (testnet and mainnet) whenever the client can read the log, else equity")
    parser.add_argument("--cap-usd", type=float, default=DEFAULT_DAILY_LOSS_CAP_USD)
    args = parser.parse_args(argv)

    import deribit_orders as do  # noqa: E402 (deferred: real exchange import only at runtime, not at test-collection time)
    if args.mainnet:
        do.select_environment(True)
    token = do.authenticate()

    failures = 0
    cap = failure_cap(_client_env(do))
    env_now = _client_env(do)
    recovery = BlindRecovery(env_now, *paths_for_env(env_now)[::-1]) if env_now != "mainnet" else None
    named = {}   # testnet: named subaccounts in the aggregate (mainnet: always empty)
    while True:
        # FIX3 H3: a transient error (ticker 10028, summary timeout, re-auth)
        # must not kill the monitor; N consecutive failures -> fail closed.
        try:
            if _client_env(do) != "mainnet":
                named = refresh_named_accounts(do, named, named_account_labels())
            result = run_once(do, token, currency=args.currency, instrument=args.instrument,
                              cap_usd=args.cap_usd, pnl_source=args.pnl_source, accounts=named)
            failures = 0
            print(format_breach_report(result))
            if recovery is not None and not args.once:
                status = recovery.note_clean(result)
                if status == "cleared":
                    print("blind HALT_DAILY_LOSS auto-cleared after a clean read window (testnet policy)")
            if args.once:
                return 0 if result["ok"] else 1
        except Exception as e:  # noqa: BLE001
            failures += 1
            print(f"daily_loss_monitor iteration failed ({failures}/{cap}): {e!r}")
            if recovery is not None:
                recovery.note_failure()
            if failures >= cap or args.once:
                now = _utc_now()
                blind_halt = paths_for_env(_client_env(do))[1]
                reason = f"daily_loss_monitor blind: {failures} consecutive failures, last {e!r}"
                if recovery is None:
                    write_halt(blind_halt, _today_str(now), reason, now)   # mainnet: untagged, never auto-cleared
                else:
                    written = write_blind_halt(blind_halt, _today_str(now), reason, now)
                    if not written:
                        print(f"{blind_halt.name} is a loss halt: left untouched")
                print(f"{blind_halt.name} written: {blind_halt} - monitor cannot see the account")
                if recovery is None or args.once:
                    return 1
                failures = 0   # testnet: stay alive and keep reading so the blind halt can clear itself
            named = {}   # re-authenticate the named accounts too
            try:
                token = do.authenticate()
            except Exception as ae:  # noqa: BLE001
                print(f"re-auth failed: {ae!r}")
        time.sleep(args.interval)


if __name__ == "__main__":
    sys.exit(main())
