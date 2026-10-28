# FT-2 Hard Guards Audit — 2026-09-27

Audited `MyTradingSys/execution/` (preferring `.new` pending files where both exist). `.secrets/` was not opened.

## Guard table

| Guard | Status | Evidence |
|---|---|---|
| G-a per-order max notional/size cap | **EXISTS** | `plan_compiler.py.new:218-219` puts `plan["caps"]["max_notional_usd"]` into `compiled["caps_check"]`; `executor.py.new:85-86` refuses preflight if `max_position_size > max_notional_usd`. Schema ceiling: `trade_plan_schema.json:131-136` (default $10,000). |
| G-b max total open position (per instrument, across plans) | **MISSING** | No aggregation across plans anywhere in `execution/` (grep for "aggregate/across plan/total open" empty). Each plan only checks its own `max_notional_usd`; nothing sums live exchange position against an account-wide ceiling before a new plan enters. |
| G-c daily loss limit (realized+unrealized) -> cancel/flatten/halt | **MISSING** | No "daily" logic anywhere; `journal.py` has no P&L aggregation (grep for daily/pnl/realized/unrealized in journal.py: none). `executor.py.new:83-90` only checks one plan's own `max_loss_usd` pre-fill, not an account-wide running total. |
| G-d invariant: no position without a live stop for >N seconds -> flatten | **PARTIAL** | Implemented per-plan: `position_manager.py.new` polls every `POLL_INTERVAL_SECONDS=2` (line 44), and if the stop isn't live it re-places once (`replaced_once`, ~line 163) then `flatten_halt()` (~line 93) if that fails or fails again. `reconciler.py.new:99-106` separately flags `unprotected_position` if live stop amount < position. Gaps: (1) no explicit elapsed-time/N-second parameter - bound is implicit in poll cadence and retry count, not a stated N; (2) invariant only holds while `position_manager.py` is actually running for that `plan_id` - nothing in the repo supervises/guarantees the process is alive, and there's no account-wide sweep independent of a plan_id. |
| G-e one-command kill switch (cancel all + reduce-only close all) | **MISSING** | Only cancel primitive is `cancel_by_label` (`deribit_orders.py.new:167-169`), deliberately **plan-scoped** by design (B078 fix, see docstring lines 13-16) - there is no account/instrument-wide "stop everything" call anywhere in the repo. |
| G-f mainnet vs testnet selection | **EXISTS (testnet-only, by construction)** | `deribit_orders.py.new:36`: `BASE = "https://test.deribit.com/api/v2"  # testnet only - deliberately not parameterised`; `_load_secret()` (~line 63-64) refuses if `cfg.get("env") != "test"`. `deribit_client.py:24-29` also defaults to `TESTNET_BASE`. No mainnet code path exists at all today - safe by omission, but the explicit-flag mechanism this guard asks for (mainnet needs an explicit flag) has not been built yet and must be designed before mainnet is ever wired in. |
| G-g API key hygiene (no withdraw scope) | **EXISTS** | `deribit_orders.py.new:104-113`, `authenticate()`: raises `RuntimeError` if `"wallet:read_write" in auth.get("scope", "")`. |
| G-h idempotency / duplicate-order protection on retry | **PARTIAL** | Plan-level: `executor.py.new:104` refuses to re-run a `plan_id` that already has a journal ("refusing to re-run (idempotency)"). Per-order labels are plan+label scoped (`_xlabel`, `executor.py.new:65-66`) so re-running the same plan can't collide with another plan's orders. Gap: `deribit_orders.py.new:83-99` (`_call`) retries `RETRYABLE_ERROR_CODES` (rate limit, queue full, **queue timeout**) up to 3x with backoff, resending the identical order params - if a queue-timeout occurs after Deribit actually accepted the order but the response was lost, the retry can place a duplicate order; there is no check (e.g. re-query by label before retrying) that the original request didn't already succeed. |

## Designs for MISSING/PARTIAL guards

All new modules are standalone (no edits to `executor.py`, `deribit_orders.py`, `position_manager.py`, or `reconciler.py`) except where noted.

- **G-b** -> new `MyTradingSys/execution/risk_guard.py`: pure functions `account_position_notional()` and `check_new_plan_against_cap()` that take already-fetched current position size + this plan's cap and return an ok/breach verdict against `MAX_ACCOUNT_NOTIONAL_USD`. Wiring this into `executor.py`'s preflight (one extra check + exchange read before compiling) is a **SONNET** task (touches the critical file).
- **G-c** -> new `MyTradingSys/execution/daily_loss_guard.py`: pure functions `daily_pnl()` and `check_daily_loss_cap()` deciding breach from a list of today's realized-pnl events + current unrealized pnl vs `DEFAULT_DAILY_LOSS_CAP_USD`. This module never touches the exchange. Wiring - sourcing today's realized pnl per plan from the journal/exchange, calling this each loop tick, and invoking the kill switch (below) on breach - is a **SONNET** task (judgment: where "today" boundary and pnl sourcing live).
- **G-e** -> new `MyTradingSys/execution/kill_switch.py`: `kill_all(client, token, ...)` duck-typed against `deribit_orders`'s existing method names (`get_positions`, `get_open_orders`, `cancel`, `close_position`) - cancels every open order on every live-position instrument, then market-flattens every nonzero position; testable with an in-memory fake client, no exchange import needed in the module itself. Production call site is a two-line script (`kill_switch.kill_all(deribit_orders, token)`) - trivial enough to leave to the operator/coordinator, or a tiny **SONNET** follow-up if a CLI entrypoint file is wanted.
- **G-d hardening** -> make the elapsed-time bound explicit (a real `unprotected_since` timestamp + `max_unprotected_seconds` param in `position_manager.py`, flatten immediately once exceeded rather than relying on poll-count) and add a process-supervision check. **SONNET** (edits the critical file, judgment on process supervision approach).
- **G-h** -> before `_call` retries a `RETRYABLE_ERROR_CODES` order-placement request, re-query by label (`get_open_orders`) to confirm the original didn't land; only resend if it truly didn't. **SONNET** (edits `deribit_orders.py`, the critical file, and needs judgment on which RPC methods are order-placing vs read-only).
- **G-f** -> design only, not urgent (no mainnet path exists): before mainnet is ever wired in, require an explicit `--mainnet` CLI flag plus a hardcoded confirmation string, defaulting to testnet base URL with no flag. **SONNET**, deferred (no code to write yet).

## Ordered task list

1. Pack `nuc_specs/015-risk-guard-position-cap.md` -> NUC (risk_guard.py, pure calc).
2. Pack `nuc_specs/016-daily-loss-guard-calc.md` -> NUC (daily_loss_guard.py, pure calc).
3. Pack `nuc_specs/017-kill-switch.md` -> NUC (kill_switch.py, fake-client-testable).
4. SONNET: wire `risk_guard.check_new_plan_against_cap()` into `executor.py` preflight (G-b).
5. SONNET: wire `daily_loss_guard` + `kill_switch` into a daily-loss check loop, decide where "today" pnl is sourced from (G-c).
6. SONNET: harden G-d - explicit `unprotected_since`/`max_unprotected_seconds` in `position_manager.py`, plus a process-supervision answer.
7. SONNET: G-h - re-query-before-retry in `deribit_orders._call` for order-placing RPCs.
8. SONNET (deferred, no urgency): design mainnet explicit-flag mechanism for G-f before mainnet is ever added.

## Blockers / uncertainty

- G-c's exact realized-pnl source (Deribit `get_account_summary` field names vs. summing journal `emergency_close`/target/stop fills) was not verified against real API responses in this repo - left as an open question for whoever wires the spec, not fabricated into the NUC spec.
- G-d's "supervision" design (is `position_manager.py` meant to run as one long-lived process per plan, or be re-invoked by a scheduler?) isn't answered anywhere in the audited files - flagged for the SONNET task, not guessed.
