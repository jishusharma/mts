# Execution Layer Boundary & Failure Cases Test Plan

**Standard Reference:** Live-path rule (`CLAUDE.md:37`: *"Live-path changes need a test for restart/reset state, non-trade balance moves and API errors; safety checks fail closed"*; `cicd_run.py:276-277`).  
**Registry Reference:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md`  
**Target Directory:** `MyTradingSys/execution/` (all 22 production modules)  
**Status Audit Date:** 2026-10-31  

---

## 1. Executive Summary

This test plan provides a comprehensive boundary and failure case audit across all production modules in `MyTradingSys/execution/`.
Every core function has been evaluated across four mandatory fail-closed categories:
1. **Restart / Reset State:** Process restarts, stale cache rehydration, process crashes, and signal deduplication.
2. **Non-Trade Balance Moves:** Account balance adjustments, funding fee deductions, deposits, withdrawals, and margin drain.
3. **API Errors:** Venue timeouts, HTTP 4xx/5xx errors, unreadable responses, token expiration, and connection resets.
4. **Stale State:** Outdated market data, stale heartbeats, clock skew, and desynchronized order books.

Each case specifies:
- The exact target function and file location (`file:line`).
- The trigger condition and input scenario.
- The expected fail-closed outcome.
- Current status: **EXISTS** (with concrete test citation) or **MISSING** (uncovered gap).

---

## 2. Top-10 Missing Gaps Ranked by Blast Radius

The table below catalogs the top 10 test gaps in `MyTradingSys/execution/` ranked by potential blast radius (financial loss or catastrophic halt):

| Rank | Blast Radius | Module & Function | Category | Scenario & Vulnerability | Remediation Plan |
| :---: | :---: | :--- | :--- | :--- | :--- |
| **1** | **CRITICAL** | `position_manager.py:336` (`_manage_impl`) | Non-Trade Balance Moves | **Active Position Margin Depletion:** External withdrawal or sustained adverse funding fee drains margin balance while a position is open. `position_manager` monitors only contract unit counts (`|pos|`), ignoring wallet equity and liquidation distance. If margin falls below maintenance, account undergoes liquidation before stop triggers. | Add offline test simulating margin balance drop during position monitoring loop; manager must raise `ManagerHalted` or flatten if margin ratio drops below safe threshold. |
| **2** | **CRITICAL** | `auto_trader.py:643` (`place`) | Non-Trade Balance Moves | **Pre-Flight Margin Exhaustion:** `auto_trader` checks price sanity and plan structure but never queries available account equity or margin before placing entry orders. Relies entirely on downstream executor crash or raw exchange rejection (`not_enough_funds`). | Add unit test verifying that when available equity < required margin, `place()` rejects entry gracefully with `margin_exhausted` without spawning a manager. |
| **3** | **CRITICAL** | `executor.py:286` (`execute_plan`) | Restart / Reset State | **Mid-Ladder Entry Process Crash:** `execute_plan` places limit ladder orders sequentially. If the process is terminated after rung 1 fills but before bracket stop/targets are placed, `executor` has no internal crash recovery mechanism (leaving position naked until auto_trader or orphan watchdog detects it). | Add test simulating executor termination between rung 1 fill and bracket placement; verify crash state journal records naked state for immediate watchdog flatten. |
| **4** | **HIGH** | `orphan_watchdog.py:64` (`run_once`) | API Errors / Network Partition | **Transient Exchange Read Partition:** If `get_positions` succeeds (returns open position) but `get_open_orders` times out or returns HTTP 500, `find_orphans` could misclassify protective orders or fail to detect orphans during a network split. | Add test asserting that if either orders or positions API call fails, `run_once` fails closed (skips cancellation, writes warning or enters safe hold, avoids premature action). |
| **5** | **HIGH** | `kill_switch.py:39` (`kill_all`) | API Errors / Partial Execution | **Emergency Close Failure After Order Cancellation:** If `cancel_open_orders` succeeds in cancelling resting stops, but the subsequent `close_position` call fails with an API error, the account is left completely unhedged and naked. | Add test verifying that if `close_position` fails after stop cancellation, `kill_all` attempts emergency market stop replacement or retries aggressively with escalation. |
| **6** | **HIGH** | `reconciler.py:45` (`reconcile`) | Stale State / Latency Desync | **Stale Exchange Trade History Lag:** During Deribit index or order history pagination lag, a newly filled order may not yet appear in `get_order_history`. Reconciler could flag a false positive `ReconciliationMismatch` and halt trading. | Add test verifying handling of brief history propagation delays before raising terminal `ReconciliationMismatch`. |
| **7** | **HIGH** | `daily_loss_monitor.py:314` (`transaction_log_pnl_btc`) | Stale State / Clock Skew | **Day Boundary Timestamp Skew:** If system clock skews backwards around 00:00:00 UTC or transactions arrive out of order, cashflow settlement logs may be attributed to the wrong day, corrupting cumulative daily PnL calculation. | Add test covering non-monotonic transaction log timestamps and backward clock drift around midnight boundary. |
| **8** | **HIGH** | `deribit_orders.py:377,385` (`stop_market`, `edit`) | API Errors / Socket Reset | **Ambiguous Socket Reset on Stop Replacement:** If HTTP connection drops after Deribit processes order placement/edit but before response is received, client raises `OrderStateUnknown`. Client currently lacks idempotency token tracking to confirm state before retrying. | Add test verifying that ambiguous placement timeout resolves order by label before submitting duplicate order. |
| **9** | **MEDIUM** | `pm_heartbeat.py:136` (`read_heartbeats`) | Stale State / File Corruption | **Truncated Heartbeat JSON Handling:** Abrupt crash of a position manager while flushing heartbeat JSON can leave 0-byte or corrupted file. Must fail closed as dead process rather than raising unhandled `JSONDecodeError`. | Add unit test verifying that corrupted/partial heartbeat file is treated as stale/dead rather than crashing monitor. |
| **10** | **MEDIUM** | `trade_plan_validator.py:64` (`validate`) | Boundary Cases / Invalid Numbers | **Numeric Boundary Injection (NaN / Inf / Negative):** Validator relies on basic comparisons; lacks explicit checks against IEEE 754 floating point `float("nan")` or `float("inf")` injected into price or amount fields. | Add unit test verifying that NaN or Infinite values in trade plan structure raise `ValidationError` fail-closed. |

---

## 3. Comprehensive Function-by-Function Boundary & Failure Case Matrix

The table below catalogs every core module and function in `MyTradingSys/execution/`, testing their behavior across the 4 mandatory failure categories:

| Module | Function & Line | Failure / Boundary Category | Scenario & Trigger Condition | Expected Fail-Closed Result | Status | Test Citation or Gap |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **auto_trader.py** | `recover_slots:839` | Restart / Reset State | Process restarts with active trade in `log.jsonl` and dead PID | Instantiates `DeadProc()`, queries exchange; if open -> respawns manager; if flat -> marks closed | **EXISTS** | `test_auto_trader.py:619`, `test_auto_trader_failclosed.py:239` |
| **auto_trader.py** | `recover_slots:839` | Restart / Reset State | Multiple unclosed plans for same account on restart | Adopts only newest plan; closes older as superseded; logs ledger row | **EXISTS** | `test_auto_trader.py:639`, `test_auto_trader_failclosed.py:228` |
| **auto_trader.py** | `tom_signal:271` | Restart / Reset State | Duplicate alert stream replay after reboot | Rejects alerts with `alert_no <= last_alert_no`; suppresses duplicate execution | **EXISTS** | `test_auto_trader.py:487`, `test_auto_trader.py:783` |
| **auto_trader.py** | `read_new_layer_alerts:388` | Restart / Reset State | Alert file truncated or rotated on disk | Resets file pointer cleanly to 0 without replaying stale alerts | **EXISTS** | `test_auto_trader.py:378` |
| **auto_trader.py** | `load_config:593` | Restart / Reset State | Corrupted or missing configuration file on startup | Rebuilds config using hardcoded safe defaults; suppresses unverified layers | **EXISTS** | `test_auto_trader.py:312`, `test_auto_trader.py:593` |
| **auto_trader.py** | `place:643` | Non-Trade Balance Moves | Account balance drained by withdrawal prior to trade | Fails to verify available margin; proceeds to order submission until downstream failure | **MISSING** | No pre-flight wallet balance check in `auto_trader.py` (Gap #2) |
| **auto_trader.py** | `deribit_mark:327` | API Errors | Venue mark price API timeout or HTTP 5xx | Returns `None`; `apply_venue_price` rejects plan with `mark_unreadable`; places nothing | **EXISTS** | `test_auto_trader.py:700`, `test_auto_trader.py:742` |
| **auto_trader.py** | `settle_slot:702` | API Errors | `exchange_flat` call throws auth / network error | Returns `None`; slot remains busy; no manager respawned; throttles log | **EXISTS** | `test_auto_trader.py:564`, `test_auto_trader_failclosed.py:60,119` |
| **auto_trader.py** | `spawn_manager:666` | API Errors | Process spawn fails (`OSError` / memory error) | Keeps dead stub in slot, logs `respawn_error`, retries next cycle, slot stays locked | **EXISTS** | `test_auto_trader_failclosed.py:102` |
| **auto_trader.py** | `settle_slot:702` | API Errors | Consecutive manager crashes exceed limit (`MAX_RESPAWNS = 3`) | Halts respawns; alerts operator; leaves slot busy to prevent concurrent trade | **EXISTS** | `test_auto_trader.py:554` |
| **auto_trader.py** | `layer_signal:501` | Stale State | Layer signal timestamp older than freshness window (`> 1.2 bars`) | Rejects alert with reason `stale`; places nothing | **EXISTS** | `test_auto_trader.py:75`, `test_auto_trader.py:276` |
| **auto_trader.py** | `net_rr_floor_reject:222` | Stale State | Dynamic RR floor file updated on disk | Re-reads floor file on each cycle; rejects orders below latest floor immediately | **EXISTS** | `test_auto_trader.py:94` |
| **position_manager.py** | `manage:316` | Restart / Reset State | Adopt existing position from plan JSON on reboot | Reconstructs target and stop orders, validates exchange position matches plan | **EXISTS** | `testnet/offline/test_fix3_offline.py:160`, `testnet/offline/test_fix3_mutants_offline.py:145` |
| **position_manager.py** | `_beat_heartbeat:303` | Restart / Reset State | Process abruptly terminated mid-run | Heartbeat updates stop; external monitors detect dead PID via `pm_heartbeat` | **EXISTS** | `test_pm_heartbeat_wiring.py:12`, `test_auto_trader_failclosed.py:239` |
| **position_manager.py** | `_manage_impl:336` | Non-Trade Balance Moves | Margin balance depleted by adverse funding fees | Manager ignores wallet balance, tracks only contracts; risks liquidation | **MISSING** | Gap #1: No equity check in `position_manager.py` |
| **position_manager.py** | `_manage_impl:336` | Non-Trade Balance Moves | External fill increases position beyond stop amount | Immediately resizes protective stop; writes HALT file; raises `ManagerHalted` | **EXISTS** | `position_manager.py:613-626`, `testnet/offline/test_fix4_offline.py:44` |
| **position_manager.py** | `_retry_call:146` | API Errors | Transient Deribit read error or token expiration | Retries call up to 4 times with exponential backoff and automatic re-authentication | **EXISTS** | `testnet/offline/test_fix3_offline.py:21`, `test_netretry.py:22` |
| **position_manager.py** | `_manage_impl:336` | API Errors | Stop order state returns `query_failed` > 15s | Flattens position (`close_position`), keeps stop, writes HALT file, raises `ManagerHalted` | **EXISTS** | `testnet/offline/test_fix3_offline.py:164`, `testnet/offline/test_s3_unprotected_offline.py:27` |
| **position_manager.py** | `_manage_impl:336` | API Errors | Replacement of cancelled stop throws `DeribitError` | Flattens position immediately, writes HALT file, raises `ManagerHalted` | **EXISTS** | `position_manager.py:601-602`, `testnet/offline/test_fix3_offline.py:190` |
| **position_manager.py** | `_manage_impl:336` | API Errors | Emergency flatten (`close_position`) throws error | Retains protective stop order; raises `ManagerHalted("FLATTEN ITSELF FAILED")` | **EXISTS** | `testnet/offline/test_fix3_offline.py:180`, `testnet/offline/test_fix3_offline.py:185` |
| **position_manager.py** | `_manage_impl:336` | Stale State | Max hold duration expired (`_plan_max_hold_minutes`) | Triggers time exit: closes position, verifies flat, cancels resting targets/stops | **EXISTS** | `testnet/offline/test_time_exit_offline.py:118-128` |
| **executor.py** | `execute_plan:286` | Restart / Reset State | Mid-ladder entry crash before bracket attachment | No recovery inside executor; must be salvaged by auto-trader / orphan watchdog | **MISSING** | Gap #3: No executor ladder crash recovery test |
| **executor.py** | `execute_plan:286` | Restart / Reset State | Re-running plan with already filled entry order | Prevents duplicate order placement; inspects journal before placing orders | **EXISTS** | `tests/test_executor_reject_diag.py:346` |
| **executor.py** | `preflight:250` | Non-Trade Balance Moves | Plan exceeds risk ceiling or daily loss limit | Halts before any order submission; writes refusal to journal; exits non-zero | **EXISTS** | `testnet/offline/test_halt_preflight_offline.py:35` |
| **executor.py** | `_place:182` | API Errors | Venue rejects entry order (`10031` bad price / margin) | Logs rejection diagnostics, cleans up ladder rungs, enters fail-closed halt | **EXISTS** | `tests/test_executor_reject_diag.py:169,200` |
| **executor.py** | `_place:182` | API Errors | Ambiguous timeout on entry submission (`10050`) | Treats state as ambiguous; sweeps/cancels order to prevent orphan fills | **EXISTS** | `tests/test_executor_reject_diag.py:214` |
| **executor.py** | `_check_halt_files:205` | Stale State | Active HALT file present on disk | Refuses execution immediately; writes `halted_before_entry` event | **EXISTS** | `testnet/offline/test_halt_preflight_offline.py:20` |
| **daily_loss_monitor.py** | `run_once:360` | Restart / Reset State | Monitor process restarts mid-day | Rehydrates state from `daily_loss_state.json`; recalculates cumulative PnL cleanly | **EXISTS** | `test_daily_loss_monitor.py:30`, `test_dlm_blind_recovery.py:45` |
| **daily_loss_monitor.py** | `_is_money_movement:304`| Non-Trade Balance Moves | Account receives deposit, withdrawal, or currency transfer | Filters out transfer/deposit/withdrawal from cashflow; ignores non-trade balance delta | **EXISTS** | `test_daily_loss_monitor.py:227,234,258` |
| **daily_loss_monitor.py** | `compute_total_pnl_usd:341`| API Errors | Deribit transaction log API fails or times out | Enters `BlindRecovery`; increments failure count; writes blind halt at limit | **EXISTS** | `test_dlm_blind_recovery.py:65`, `test_dlm_failure_cap.py:25` |
| **daily_loss_monitor.py** | `transaction_log_pnl_btc:314`| Stale State | Clock skew across midnight boundary | Non-monotonic timestamps could skew daily window boundaries | **MISSING** | Gap #7: Missing clock skew test at midnight seam |
| **daily_loss_guard.py** | `check_daily_loss_cap:27`| Restart / Reset State | Re-evaluating empty journal on startup | Returns PnL = 0.0, cap not breached; no false halts triggered | **EXISTS** | `test_daily_loss_guard.py:12` |
| **daily_loss_guard.py** | `check_daily_loss_cap:27`| Non-Trade Balance Moves | External balance change recorded without journal entry | Daily loss guard inspects journaled trades only, ignoring raw wallet transfers | **EXISTS** | `test_daily_loss_guard.py:15`, `test_daily_pnl_wiring.py:18` |
| **daily_loss_guard.py** | `check_daily_loss_cap:27`| Stale State | Journal events from previous days present in log | Filters events strictly by current UTC date; excludes yesterday's losses | **EXISTS** | `test_daily_loss_guard.py:25` |
| **orphan_watchdog.py** | `run_once:64` | Restart / Reset State | Watchdog restarted while orphan exists | Identifies orphan immediately on first cycle; cancels and writes halt | **EXISTS** | `test_orphan_watchdog.py:55`, `test_orphan_sweep_loop.py:25` |
| **orphan_watchdog.py** | `find_orphans:35` | Non-Trade Balance Moves | Wallet balance moves leaving resting order without position | Identifies resting order without matching open position; flags orphan order | **EXISTS** | `test_orphan_watchdog.py:44` |
| **orphan_watchdog.py** | `run_once:64` | API Errors | Transient network failure during orphan check | Partition could cause false orphan cancellations or missed protective orders | **MISSING** | Gap #4: Missing API error / partition test in watchdog |
| **orphan_watchdog.py** | `write_orphan_halt:49` | Stale State | Stale orphan halt file remains on disk | Refuses trading until operator clears halt file; fails closed | **EXISTS** | `test_orphan_watchdog.py:80` |
| **kill_switch.py** | `kill_all:39` | Restart / Reset State | Kill switch executed multiple times sequentially | Idempotent execution; duplicate executions confirm flat and no orders safely | **EXISTS** | `test_kill_switch.py:80` |
| **kill_switch.py** | `kill_all:39` | Non-Trade Balance Moves | Non-zero balance with zero position | Verifies position is 0; leaves wallet balance intact; cancels resting orders | **EXISTS** | `test_kill_switch_account.py:25` |
| **kill_switch.py** | `kill_all:39` | API Errors | `close_position` fails after stop cancellation | Leaves account unhedged; needs emergency retry or stop preservation | **MISSING** | Gap #5: Missing API failure handling on emergency close |
| **reconciler.py** | `reconcile:45` | Restart / Reset State | Reconciler run after plan completes and restarts | Verifies final journal matches closed exchange orders | **EXISTS** | `testnet/tests/test_deribit_orders_phase3.py:102,105` |
| **reconciler.py** | `reconcile:45` | Stale State | Latency / pagination lag in exchange order history | Missing fill records can trigger false `ReconciliationMismatch` | **MISSING** | Gap #6: Missing order history lag test in reconciler |
| **reconciler.py** | `assert_env:83` | Restart / Reset State | Cross-environment replay (mainnet plan on testnet) | Raises `EnvMismatch` immediately before executing any exchange action | **EXISTS** | `test_reconciler_env.py:57,68` |
| **risk_guard.py** | `check_new_plan_against_cap:51`| Restart / Reset State | Re-evaluating cap after restart with active positions | Queries live open positions from exchange; rejects new plan if cap exceeded | **EXISTS** | `test_risk_guard.py:35` |
| **risk_guard.py** | `account_position_notional:25`| Non-Trade Balance Moves | Balance change alters leverage ratio | Checks absolute USD notional independently of equity balance shifts | **EXISTS** | `test_risk_guard.py:16,20` |
| **deribit_orders.py** | `authenticate:329` | Restart / Reset State | Client restarted; session token reset | Automatically re-authenticates using stored credentials on next call | **EXISTS** | `test_b148_reauth_account.py:15` |
| **deribit_orders.py** | `stop_market:377` | API Errors | HTTP connection drops mid-request (`OrderStateUnknown`) | Raises `OrderStateUnknown`; lacks automatic idempotency check | **MISSING** | Gap #8: Missing socket drop / ambiguous timeout test |
| **deribit_orders.py** | `select_environment:190` | API Errors | Mainnet credentials used on testnet or vice versa | Refuses execution; raises `MainnetRefused` fail-closed | **EXISTS** | `test_mts_kill_mainnet.py:20`, `tests/test_deribit_orders_phase3.py:74` |
| **deribit_client.py** | `get_ticker:29` | API Errors | Public ticker endpoint timeout or malformed payload | Raises `DeribitError`; caller handles unreadable mark | **EXISTS** | `test_auto_trader.py:700` |
| **deribit_read.py** | `call:34` | API Errors | Read call with invalid or missing credentials | Fails cleanly without leaking credential tokens in log | **EXISTS** | `test_deribit_read_account.py:20` |
| **journal.py** | `append_event:39` | Restart / Reset State | Process crash during atomic log append | Uses append-only JSONL; trailing newline ensures previous lines remain intact | **EXISTS** | `test_journal_env.py:20` |
| **trade_ledger.py** | `record_closed:222` | Restart / Reset State | Processing backlogged closed trades on restart | Backfills closed trade rows into ledger idempotently using `existing_plan_ids` | **EXISTS** | `test_trade_ledger.py:50` |
| **trade_ledger.py** | `_fee_usd:60` | Non-Trade Balance Moves | Fee deduction vs funding payments in transaction log | Accurately distinguishes trade execution fees from periodic funding payments | **EXISTS** | `test_trade_ledger.py:26,39` |
| **pm_heartbeat.py** | `read_heartbeats:136` | Stale State | Heartbeat older than threshold (`> 60s`) or corrupted | Marks process dead / inactive; treats unreadable file as dead | **EXISTS** (corrupted partial JSON is **MISSING**, Gap #9) | `test_pm_heartbeat.py:18`, `test_pm_heartbeat_wiring.py:12` |
| **plan_compiler.py** | `compile_plan:103` | Boundary Cases | Zero or sub-tick size / price inputs | Snaps prices and rounds sizes to valid contract multiples; throws `CompileError` if invalid | **EXISTS** | `test_plan_compiler.py:26,30`, `test_suite_static.py:96,101` |
| **new_plan.py** | `build:80` | Boundary Cases | Missing required plan parameters | Prompts operator or fills safe default bounds; enforces structure schema | **EXISTS** | `testnet/test_suite_static.py:85` |
| **trade_plan_validator.py** | `validate:64` | Boundary Cases | Non-numeric or NaN/Inf inputs injected into plan | Lacks dedicated unit tests for extreme numeric boundary values | **MISSING** | Gap #10: Missing IEEE 754 NaN/Inf boundary test |
| **capture_txlog_settlement.py** | `capture:35` | Non-Trade Balance Moves | Settlement logs mixed with deposit and transfer records | Filters and categorizes transactions cleanly by type (`trade`, `settlement`, `deposit`) | **EXISTS** | `test_capture_txlog_settlement.py:25,33` |
| **mainnet_pnl.py** | `daily_pnl_btc:60` | Non-Trade Balance Moves | Cashflow containing deposits vs trading losses | Accurately isolates realized trade profit/loss from external capital additions | **EXISTS** | `test_mainnet_pnl.py:18,22` |
| **mainnet_plan_check.py** | `plan_refusals:5` | API Errors | Sizing above mainnet calibration limits | Returns explicit refusal reasons; blocks live order dispatch | **EXISTS** | `test_mainnet_plan_check.py:20` |
| **soak_report.py** | `soak_verdict:87` | Stale State | Unexpected halt or reconciliation error during soak | Produces fail verdict; highlights abnormal process crashes or error events | **EXISTS** | `test_soak_report.py:80,106,131,157` |

---

## 4. Verification and Execution Guidance

To verify existing coverage, execute the following unit and offline test suites:

```powershell
# 1. Execution offline fail-closed and restart tests:
python MyTradingSys/execution/test_auto_trader_failclosed.py
python -m unittest MyTradingSys/execution/test_auto_trader.py
python -m unittest MyTradingSys/execution/test_daily_loss_monitor.py
python -m unittest MyTradingSys/execution/testnet/offline/test_fix3_offline.py
python -m unittest MyTradingSys/execution/testnet/offline/test_fix4_offline.py
python -m unittest MyTradingSys/execution/testnet/offline/test_time_exit_offline.py
python -m unittest MyTradingSys/execution/testnet/offline/test_s6_orphan_offline.py
python -m unittest MyTradingSys/execution/tests/test_executor_reject_diag.py

# 2. Plan validator and compiler checks:
python MyTradingSys/execution/trade_plan_validator.py --examples
python -m unittest MyTradingSys/execution/test_plan_compiler.py
```
