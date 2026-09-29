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
9. Kill switch (any time): `python MyTradingSys/execution/kill_switch.py --confirm KILL --mainnet`
   (HALT is written first; the mainnet confirmation is still typed). Fallback: Deribit web UI "close all".

## C. Abort criteria (kill switch immediately, do not resume without review)

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
- The kill switch on mainnet still needs the typed confirmation (design: no bypass).
