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
FIX4_DESIGN.md ("transaction-log probe RESULT and DECISION", testnet probe
testnet/probe_transaction_log.py): pnl_source="transaction_log" =
  sum(change) [BTC] over today's 00:00-UTC..now private/get_transaction_log
  entries, EXCLUDING money-movement types (deposit, withdrawal, transfer*),
  times mark_price. Includes fees/funding/settlement, excludes deposits and
  transfers (which the equity delta wrongly counted as P/L). Field names
  (logs, continuation, type, change) are those of the repo's probe; only
  type="trade" has been observed live (testnet) - the exclusion type names
  are the FIX4 decision, NOT verified against the official Deribit
  transaction-log type list (operator open question).
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
MAX_CONSECUTIVE_FAILURES = 3  # FIX3 H3: then fail closed (write HALT_DAILY_LOSS) instead of dying


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
    """sum(change) over entries, minus money-movement types. An entry with no
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
    env = getattr(client, "active_env", None)
    return "transaction_log" if callable(env) and env() == "mainnet" else "equity"


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
        return round(transaction_log_pnl_btc(entries) * ticker["mark_price"], 2)
    summary = client.get_account_summary(token, currency=currency)
    ticker = client.get_ticker(instrument_name=instrument)
    equity_delta = summary["equity"] - state["day_start_equity"]
    return round(equity_delta * ticker["mark_price"], 2)


def run_once(client, token, clock=_utc_now, currency: str = "BTC",
             instrument: str = "BTC-PERPETUAL", cap_usd: float = DEFAULT_DAILY_LOSS_CAP_USD,
             state_path: Path = None, halt_path: Path = None, pnl_source: str = None) -> dict:
    """Single monitor iteration. Returns the check_daily_loss_cap() result
    dict (plus 'state' for tests). Idempotent: a breach only triggers
    kill_all/HALT-file/journal once per UTC day (state['breached_today']).
    
    Re-arms breached_today flag if HALT_DAILY_LOSS file is cleared by operator."""
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

    total_pnl_usd = compute_total_pnl_usd(client, token, state, currency=currency, instrument=instrument,
                                          pnl_source=pnl_source, now_ms=int(now.timestamp() * 1000))
    result = check_daily_loss_cap([{"pnl_usd": total_pnl_usd}], 0.0, cap_usd=cap_usd)

    if not result["ok"] and not state.get("breached_today"):
        reason = result["reason"]
        journal.append_event(JOURNAL_PLAN_ID, "error", {
            "source": "daily_loss_monitor",
            "total_pnl_usd": total_pnl_usd,
            "cap_usd": cap_usd,
            "reason": reason,
        })
        # FIX3 H3: HALT first, and regardless of whether kill_all works
        write_halt(halt_path, state["date"], reason, now)
        state["breached_today"] = True
        save_state(state, state_path)
        try:
            kill_result = kill_switch.kill_all(client, token, currency=currency)
            journal.append_event(JOURNAL_PLAN_ID, "error", {
                "source": "daily_loss_monitor",
                "kill_switch_report": kill_switch.format_kill_report(kill_result),
                "kill_switch_ok": kill_result["ok"],
            })
        except Exception as e:  # noqa: BLE001
            journal.append_event(JOURNAL_PLAN_ID, "error", {
                "source": "daily_loss_monitor", "kill_switch_ok": False,
                "kill_switch_error": repr(e)})

    save_state(state, state_path)
    result["state"] = state
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Daily loss monitor loop for MTS.")
    parser.add_argument("--once", action="store_true", help="Run a single iteration and exit (for cron/scheduling).")
    parser.add_argument("--interval", type=float, default=POLL_INTERVAL_SECONDS, help="Seconds between iterations.")
    parser.add_argument("--mainnet", action="store_true", help="MAINNET (typed confirmation required)")
    parser.add_argument("--currency", default="BTC")
    parser.add_argument("--instrument", default="BTC-PERPETUAL")
    parser.add_argument("--pnl-source", choices=PNL_SOURCES, default=None,
                        help="default: equity on testnet, transaction_log on mainnet")
    parser.add_argument("--cap-usd", type=float, default=DEFAULT_DAILY_LOSS_CAP_USD)
    args = parser.parse_args(argv)

    import deribit_orders as do  # noqa: E402 (deferred: real exchange import only at runtime, not at test-collection time)
    if args.mainnet:
        do.select_environment(True)
    token = do.authenticate()

    failures = 0
    while True:
        # FIX3 H3: a transient error (ticker 10028, summary timeout, re-auth)
        # must not kill the monitor; N consecutive failures -> fail closed.
        try:
            result = run_once(do, token, currency=args.currency, instrument=args.instrument,
                              cap_usd=args.cap_usd, pnl_source=args.pnl_source)
            failures = 0
            print(format_breach_report(result))
            if args.once:
                return 0 if result["ok"] else 1
        except Exception as e:  # noqa: BLE001
            failures += 1
            print(f"daily_loss_monitor iteration failed ({failures}/{MAX_CONSECUTIVE_FAILURES}): {e!r}")
            if failures >= MAX_CONSECUTIVE_FAILURES or args.once:
                now = _utc_now()
                blind_halt = paths_for_env(_client_env(do))[1]
                write_halt(blind_halt, _today_str(now),
                           f"daily_loss_monitor blind: {failures} consecutive failures, last {e!r}", now)
                print(f"{blind_halt.name} written: {blind_halt} - monitor cannot see the account")
                return 1
            try:
                token = do.authenticate()
            except Exception as ae:  # noqa: BLE001
                print(f"re-auth failed: {ae!r}")
        time.sleep(args.interval)


if __name__ == "__main__":
    sys.exit(main())
