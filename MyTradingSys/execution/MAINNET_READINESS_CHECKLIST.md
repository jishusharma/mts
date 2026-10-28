# Mainnet readiness checklist (Deribit, 1 tiny trade) - 2026-09-29

Code default is TESTNET. Mainnet needs `--mainnet` AND a typed confirmation. Nothing here has touched
mainnet; every check below is offline. Design: `research/fast_track_2026-09-27/S5_MAINNET_FLAG.md`.

## A. Machine-checked (run: `python scripts/dev/run_all_tests.py --quick`; or the single command shown)

| # | Item | Proof (from MyTradingSys/execution) |
|---|---|---|
| 1 | No flag -> testnet URL + testnet secret, no prompt | `python -m unittest test_mainnet_flag_offline.TestRefusalMatrix.test_row1_no_flag_is_testnet_unchanged` |
| 2 | Mainnet secret file missing -> refused, no HTTP | `...test_row2_mainnet_secret_missing` |
| 3 | Secret env must equal target env, both directions | `...test_row3_...`, `...test_row1b_...` |
| 4 | Key with wallet:read_write (withdraw) refused on mainnet | `...test_row4_withdraw_scope_refused_on_mainnet` |
| 5 | Wrong / empty / EOF confirmation refused, zero HTTP, env stays test | `...test_row5_*` |
| 6 | Exact confirmation -> only then mainnet auth | `...test_row6_exact_confirmation_reaches_mainnet_auth` |
| 7 | Mainnet order/plan > MAINNET_MAX_NOTIONAL_USD (50) refused before any call | `python -m unittest test_mainnet_flag_offline.TestMainnetNotionalCap` |
| 8 | Account-wide notional cap (risk_guard, 10000) wired in executor preflight | `python -m unittest test_s1_cap_offline test_risk_guard` |
| 9 | Daily loss guard + monitor; mainnet uses transaction-log P/L (deposits/transfers excluded) | `python -m unittest test_daily_loss_guard test_daily_loss_monitor` |
| 10 | HALT / HALT_DAILY_LOSS refuse new orders | `run_all_tests.py --quick` Step 1 (test_halt_preflight_offline) |
| 11 | Kill switch: cancel all + flatten + HALT first | `python -m unittest test_kill_switch` |
| 12 | Unprotected position bound (MAX_UNPROTECTED_SECONDS=4) | `run_all_tests.py --quick` Step 1 (test_s3_unprotected_offline) |
| 13 | Ambiguous order outcome never blind-retried (OrderStateUnknown) | `python -m unittest test_gh_retry_offline` |

Not machine-checkable: which Deribit subaccount a key belongs to; whether the key's IP whitelist is set.

## B. Operator-only (Tom/operator does these; the agent never creates or reads the key)

1. Create a Deribit SUBACCOUNT used only for MTS. Never the main account.
2. Create an API key on that subaccount: scopes account:read + trade:read_write, wallet: NONE (no
   `wallet:read_write`; code also refuses it). Enable IP whitelisting to this machine's IP.
3. Fund the subaccount with <= 100 USD equivalent of BTC (inverse contracts: margin is BTC).
4. Save the key yourself as `MyTradingSys/execution/.secrets/mainnet.secret.json`:
   `{"env": "mainnet", "client_id": "...", "client_secret": "..."}` (gitignored; never paste it in chat).
5. Confirm no HALT / HALT_DAILY_LOSS file, testnet account flat, auto_trader stopped (it has no mainnet mode).
6. Start the guards first (separate shells, from repo root):
   - `python MyTradingSys/execution/daily_loss_monitor.py --mainnet --cap-usd -10`  (typed confirmation)
7. Smoke read (no order): `python MyTradingSys/execution/deribit_orders.py --mainnet` -> AUTH OK, flat.
8. One order: a plan with max_notional_usd <= 50 and a stop, then
   `python MyTradingSys/execution/executor.py <plan.json> --go --mainnet`, and in another shell
   `python MyTradingSys/execution/position_manager.py <plan_id> --mainnet`.
9. Kill switch (any time): `python MyTradingSys/execution/kill_switch.py --mainnet`
   (HALT is written first; you type only the word `kill` - lowercase, at the prompt - not the long S5 sentence). Fallback: Deribit web UI "close all".

## C. Abort criteria (kill switch immediately, do not resume without review)

Mainnet kill: `mts kill-mainnet` (fallback: `python MyTradingSys/execution/kill_switch.py --mainnet`); type `kill` when asked.

- Any REFUSED / OrderStateUnknown / "unprotected" / "mismatch_halt" message, or a HALT file appears.
- Position exists without a live stop for > 4 s, or position size > 50 USD.
- Daily P/L <= -10 USD (monitor cap you passed) or the monitor prints "blind".
- Any order you did not intend; any fill price > 1% from mark; API auth error loops.
- Equity or balance moves by something other than the trade (unexpected deposit/transfer).

## D. Known limits (read before going live)

- Fees on mainnet are real and can exceed a 50 USD trade's edge; loss caps of -10 USD are per day.
- Transaction-log exclusion types (deposit, withdrawal, transfer*) come from the FIX4 decision; only type=trade
  was observed live (testnet). Verify the type list in Deribit docs before raising the cap.
- auto_trader.py does not pass `--mainnet`; mainnet is manual (executor + position_manager) only.
- The kill switch on mainnet needs one typed word, `kill` (interactive, case-sensitive; operator decision 2026-09-29: kill can only
  reduce risk, so it does not use the long S5 sentence). Every other mainnet path keeps all 4 gates incl. the full sentence.

## Audit 2026-09-29 open items

Source: research/fast_track_2026-09-27/review/OPUS_PREMAINNET_AUDIT.md. Fixed already (premainnet1): kill switch close-first,
mainnet kill ignores MTS_ACCOUNT, per-env daily-loss state/HALT. "Blocks smoke" = must be done or worked around before the 50 USD trade.

- [x] (HIGH #3) Daily P/L from cashflow (profit_as_cashflow) + unrealized P/L, allow-list of tx types, not `change` only. Does NOT block the 50 USD smoke trade (the stop is the real limit); BLOCKS raising size. DONE: mainnet_pnl 129 + daily_loss_monitor wiring 132 (operator check vs Deribit UI session P/L still due before raising size).
- [x] (HIGH #5) `mts kill` is testnet-only: add `mts kill-mainnet` (or env prompt); put the exact mainnet kill command at the top of section C. BLOCKS smoke (operator must use `kill_switch.py --confirm KILL --mainnet` directly until then).
- [x] (HIGH #6) Journal records env (+account) in the intent event; executor/position_manager/reconciler refuse on env mismatch; add `--mainnet` to reconciler.py. BLOCKS smoke (until then: never run reconciler on a mainnet plan_id, and double-check the plan_id passed to position_manager --mainnet). DONE (env only, not account): journal 126, executor/pm 130, reconciler 127 --mainnet; commit q126-130.
- [x] (CHECK #7) Pre-compiled plan cap: on mainnet refuse compiled JSON input and assert sum(entry amounts) == max_position_size <= 50. Blocks smoke only if a compiled file is used; use the raw plan. DONE: mainnet_plan_check 128 wired into executor.preflight (130).
- [ ] (CHECK #8) Triggered-stop label check: one testnet stop-trigger run recording get_user_trades labels and the stop's get_order_state. Does not block smoke (worst case is a false "unexplained flat" halt on a flat position).
- [ ] (CHECK #9) Executor Ctrl+C window: catch BaseException around the poll loop -> fail_closed. Does not block smoke if the operator rule holds: never Ctrl+C the executor, use kill_switch.
- [x] (watchdog) orphan_watchdog: run manually once on testnet with a live trade to confirm no false HALT before scheduling (promoted q122/123, NOT scheduled; an unreadable account is a logged error, not an orphan). 2026-09-29 10:57Z: flat-account baseline run OK (all accounts, no orphans, no errors, no HALT); live-trade run 15:37Z on S-mkt-0929-1501 (jishu_2): first run FALSE HALT (CLI read heartbeat/ not pm_heartbeats/), HALT moved to halt_history, fixed a9629e8; rerun OK live=[jishu_2], no orphans.
