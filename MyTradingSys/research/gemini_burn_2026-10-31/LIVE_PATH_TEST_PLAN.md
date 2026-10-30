# Live-Path Edge Cases Test Plan

**Standard Reference:** Live-path rule (`CLAUDE.md:37`: *"Live-path changes need a test for restart/reset state, non-trade balance moves and API errors; safety checks fail closed"*; `cicd_run.py:276-277`).  
**Registry Reference:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md`  
**Status Audit Date:** 2026-10-31  

---

## 1. Executive Summary & Audit Matrix

| Module | Category | Required Test Scenario | Input / Trigger Condition | Expected Fail-Closed Result | Status | Existing Test Citation / Gap |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `auto_trader.py` | Restart / Reset State | Log recovery after restart (`recover_slots`) | Restart with unclosed `trade_attempt` in `log.jsonl`; manager dead | Manager dead: slot created with `DeadProc()`, checks exchange; if open -> respawns manager; if flat -> marks `trade_closed` | **EXISTS** | `test_auto_trader.py:619`, `test_auto_trader_failclosed.py:239` |
| `auto_trader.py` | Restart / Reset State | Superseded plan on restart (`recover_slots`) | Restart with multiple unclosed plans for the same account | Adopts only newest plan; older plan closed as superseded with `record_ledger` | **EXISTS** | `test_auto_trader.py:639`, `test_auto_trader_failclosed.py:228` |
| `auto_trader.py` | Restart / Reset State | Duplicate alert replay suppression across restart | Restart after processing alert; same alert on disk / in memory | Alerts at or before `tom_last_alert_no` are skipped; no re-execution | **EXISTS** | `test_auto_trader.py:487`, `test_auto_trader.py:783`, `test_auto_trader.py:810` |
| `auto_trader.py` | Restart / Reset State | Truncated alert stream file recovery | File reset/truncation on alert log | Resets read offset to 0 without replaying stale alerts | **EXISTS** | `test_auto_trader.py:378` |
| `auto_trader.py` | Non-Trade Balance Moves | Direct account equity / balance shift (deposit / withdrawal / funding fee) | Balance shift occurs while position open or idle | Auto-trader delegates execution sizes / limits without querying balance directly, but relies on position-sizing preflight and account isolation; has no direct balance-listener or fee-deduction trigger handler | **MISSING** | `auto_trader.py` has no balance tracking handler; `test_auto_trader.py` lacks non-trade balance scenario |
| `auto_trader.py` | API Error | `deribit_mark` / venue price retrieval failure | Deribit API returns HTTP error, timeout, or invalid mark JSON | Entry is refused (`{"outcome": "mark_unreadable"}` / `plan_refused`), places nothing, logs reason | **EXISTS** | `test_auto_trader.py:700`, `test_auto_trader.py:742` |
| `auto_trader.py` | API Error | `exchange_flat` read failure (auth/transient network error) | Auth throws or `get_position` fails during `settle_slot` | Returns `None` (unreadable); slot kept busy, throttled logging, no respawn or premature freeing | **EXISTS** | `test_auto_trader.py:564`, `test_auto_trader_failclosed.py:60`, `test_auto_trader_failclosed.py:66`, `test_auto_trader_failclosed.py:119` |
| `auto_trader.py` | API Error | Executor / new_plan CLI execution failure | Subprocess times out, exits non-zero, or fails API order placement | `place()` returns `plan_refused` or `entry_failed`; slot left free, no manager spawned | **EXISTS** | `test_auto_trader.py:572`, `test_auto_trader_failclosed.py:163`, `test_auto_trader_failclosed.py:172` |
| `auto_trader.py` | API Error | Position manager spawn / respawn failure | `spawn_manager()` raises `OSError` / subprocess failure | Keeps dead proc in slot, logs `respawn_error`, retries next cycle, slot stays busy | **EXISTS** | `test_auto_trader_failclosed.py:102` |
| `auto_trader.py` | API Error | Repeated manager crashes beyond limit (`MAX_RESPAWNS = 3`) | Manager crashes 3 consecutive times with position still open on exchange | Stops respawning; fires `operator_alert()`, slot kept busy to prevent double trade | **EXISTS** | `test_auto_trader.py:554` |
| `position_manager.py` | Restart / Reset State | Mid-run startup / adoption from plan JSON | Plan loaded from disk after process restart (`manage(plan_id)`) | Reconstructs targets, stop, entry average price, and verifies active exchange position against plan orders | **EXISTS** | `testnet/offline/test_fix3_offline.py:160`, `testnet/offline/test_fix3_mutants_offline.py:145` |
| `position_manager.py` | Restart / Reset State | Process death / crash before heartbeat beat | Manager process killed abruptly mid-trade | Heartbeat file stops updating; watchdog / auto-trader detects dead PID, triggers `settle_slot` recovery | **EXISTS** | `test_pm_heartbeat_wiring.py:12`, `test_auto_trader_failclosed.py:239` |
| `position_manager.py` | Non-Trade Balance Moves | Margin balance depletion / funding fee move affecting margin ratio | Account margin balance changes via funding or external transfer | Manager tracks contract position units (`|pos|`), not wallet balance; does not monitor liquidation distance changes from wallet equity shifts | **MISSING** | No test in `testnet/offline/` or `test_auto_trader*.py` checks wallet balance shifts during active manage loop |
| `position_manager.py` | Non-Trade Balance Moves | Position size growth outside plan (external trade / liquidation fill) | Position increases (`size > stop["amount"]`) while managing plan | Stop resized to cover new size immediately, logs `mismatch_halt`, writes `HALT_PATH`, raises `ManagerHalted` | **EXISTS** | `position_manager.py:613-626`, `testnet/offline/test_fix4_offline.py:44` |
| `position_manager.py` | API Error | Transient read call failure / token expiry | Network timeout or token expiration on `get_position` or `get_order_state` | `rd()` invokes `_retry_call()` with re-auth; retries up to 4 times with exponential backoff before escalating | **EXISTS** | `testnet/offline/test_fix3_offline.py:21`, `test_netretry.py:22` |
| `position_manager.py` | API Error | Persistent unreadable stop order state (`query_failed`) | Stop state returns `query_failed` for > `MAX_UNPROTECTED_SECONDS` (15s) | Flattens position (`close_position`), keeps stop until flat confirmed, writes `HALT_PATH`, raises `ManagerHalted` | **EXISTS** | `testnet/offline/test_fix3_offline.py:164`, `testnet/offline/test_s3_unprotected_offline.py:27` |
| `position_manager.py` | API Error | Re-place stop order failure on non-live stop | Active stop missing/cancelled and `stop_market()` throws `DeribitError` | Flattens position immediately, writes `HALT_PATH`, raises `ManagerHalted` | **EXISTS** | `position_manager.py:601-602`, `testnet/offline/test_fix3_offline.py:190` |
| `position_manager.py` | API Error | Stop resize failure on target fill or position shift | `edit()` throws `DeribitError` during stop size adjustment | Flattens position, cancels resting targets, writes `HALT_PATH`, raises `ManagerHalted` | **EXISTS** | `position_manager.py:616-617`, `testnet/offline/test_fix3_offline.py:195` |
| `position_manager.py` | API Error | Emergency flatten close position failure (`close_position` error) | Emergency close fails or leaves residual position | Does NOT cancel protective stop; raises `ManagerHalted("FLATTEN ITSELF FAILED")`, writes HALT file, logs context | **EXISTS** | `testnet/offline/test_fix3_offline.py:180`, `testnet/offline/test_fix3_offline.py:185` |
| `Java StateMachine` (`StateCodeEmitter`) | Restart / Reset State | Restart with stale persisted state (`state_code.json`) | JVM restarts mid-day; stale state file on disk | Replaces stale restored sums with fresh Binance 1m kline backfill up to the seam; invalidates state until backfill succeeds | **EXISTS** | `StateCodeEmitterTest.java:354`, `StateCodeEmitter.java:237-250` |
| `Java StateMachine` (`StateCodeEmitter`) | Restart / Reset State | Day rollover (UTC midnight) reset | UTC midnight transition during continuous streaming or while invalid | Resets daily cumulative CVD and volume sums; invalidates state until next complete boundary; clears CVD ring | **EXISTS** | `StateCodeEmitterTest.java:531`, `StateCodeEmitter.java:763`, `StateCodeEmitter.java:796` |
| `Java StateMachine` (`StateCodeEmitter`) | Restart / Reset State | Stream disconnect & reconnect seam | WebSocket disconnects and reconnects after gap | Connects new socket, discards ticks prior to seam, backfills missing 1m klines, verifies boundary alignment | **EXISTS** | `StateCodeEmitterTest.java:379`, `StateCodeEmitterTest.java:708`, `StateCodeEmitterTest.java:723` |
| `Java StateMachine` (`StateCodeEmitter`) | Non-Trade Balance Moves | Non-trade / non-market message on public trade feed | Ping/pong frames, heartbeat, subscription confirmation, or non-trade JSON payload | Discarded; accumulators and volume sums remain unchanged; state remains valid | **EXISTS** | `StateCodeEmitterTest.java:471`, `StateCodeEmitterTest.java:652` |
| `Java StateMachine` (`StateCodeEmitter`) | Non-Trade Balance Moves | User account balance change / margin transfer | Account deposit, withdrawal, or funding transfer | **NOT APPLICABLE / OUT OF SCOPE**: StateMachine connects to public market trade stream (`wss://fstream.binance.com`), contains no private user credentials or balance awareness | **EXISTS** (by architectural design - isolated public feed) | `StateCodeEmitter.java:43-52` |
| `Java StateMachine` (`StateCodeEmitter`) | API Error | REST backfill failure / HTTP 5xx / timeout | Binance kline REST API throws `IOException` or HTTP 429/500 | `failBackfill()` marks state invalid (`valid = false`), outputs `UNKNOWN` state, suppresses signals, schedules retry | **EXISTS** | `StateCodeEmitterTest.java:411`, `StateCodeEmitterTest.java:672`, `StateCodeEmitterTest.java:744` |
| `Java StateMachine` (`StateCodeEmitter`) | API Error | WebSocket stream error / disconnect (`onError` / `onClose`) | Socket dropped or protocol error | Clears CVD sample ring, sets `connectedAtMs = Long.MAX_VALUE`, marks state invalid, triggers reconnect executor | **EXISTS** | `StateCodeEmitterTest.java:576`, `StateCodeEmitterTest.java:611`, `StateCodeEmitter.java:203-220` |
| `Java StateMachine` (`Main.java` statemachine entry) | API Error / Restart | Liquidation log accumulator background failure | JVM shutdown or liquidation WebSocket disconnect | Async connection; liquidation logging errors never crash or block `StateCodeEmitter`; graceful drain on shutdown | **EXISTS** | `LiquidationLogWiringTest.java:35`, `Main.java:74-81` |

---

## 2. Module Detailed Analysis

### 2.1 `execution/auto_trader.py`

#### A. Restart / Reset State
- **Mechanics:** `recover_slots(log_path, procs, alive_fn)` (`auto_trader.py:839-870`) parses `log.jsonl` via `open_plans_from_log` (`auto_trader.py:818-836`). It identifies open plans without a matching `trade_closed` event.
- **Fail-Closed Behavior:**
  - If a manager PID is not alive, a `DeadProc()` stub is assigned (`auto_trader.py:862`).
  - On the immediate next `cycle()`, `settle_slot()` triggers `exchange_flat(acct)` (`auto_trader.py:709`).
  - If the exchange is unreadable (`None`), the slot remains busy (`auto_trader.py:710-715`).
  - If the position is still open (`False`), it respawns up to `MAX_RESPAWNS = 3` (`auto_trader.py:716-729`).
  - If multiple live managers are detected for the same account, it adopts only the newest and alerts the operator (`auto_trader.py:853-856`).
- **Existing Coverage:**
  - `MyTradingSys/execution/test_auto_trader.py:604` (`test_alive_manager_is_adopted_named_account_from_log`)
  - `MyTradingSys/execution/test_auto_trader.py:619` (`test_dead_manager_open_position_is_respawned`)
  - `MyTradingSys/execution/test_auto_trader.py:629` (`test_dead_manager_flat_account_is_closed_with_ledger_row`)
  - `MyTradingSys/execution/test_auto_trader.py:639` (`test_older_dead_plan_of_same_account_is_superseded`)
  - `MyTradingSys/execution/test_auto_trader_failclosed.py:218` (`test_two_live_managers_one_account_adopts_newest_only_and_alerts`)
  - `MyTradingSys/execution/test_auto_trader_failclosed.py:228` (`test_older_dead_plan_same_account_is_superseded_with_ledger_row`)
  - `MyTradingSys/execution/test_auto_trader_failclosed.py:239` (`test_dead_manager_slot_with_open_position_is_respawned_not_freed`)
  - `MyTradingSys/execution/test_auto_trader_failclosed.py:250` (`test_dead_manager_slot_with_unreadable_exchange_stays_busy`)

#### B. Non-Trade Balance Moves
- **Mechanics:** `auto_trader.py` does not directly maintain wallet balance or margin accounts. Sizing and risk bounds are delegated to `plan_compiler.py` / `new_plan.py` / `risk_guard.py` before execution.
- **Fail-Closed Gap:** If an account's equity is drained by a manual withdrawal, transfer, or high funding fee during runtime, `auto_trader.py` does not check equity before placing an order. Instead, `new_plan.py` or `executor.py` fails with an exchange error (`not_enough_funds`).
- **Status:** **MISSING** direct unit test in `test_auto_trader.py` verifying that an external equity drop prevents new order dispatch cleanly without corrupted state.

#### C. API Errors
- **Mechanics:**
  - Mark price reads (`deribit_mark` at `auto_trader.py:327`) call public Deribit endpoints.
  - Position reads (`exchange_flat` at `auto_trader.py:675`) call `deribit_orders.get_position`.
  - Subprocess calls (`run` at `auto_trader.py:636`) enforce a 900s timeout.
- **Fail-Closed Behavior:**
  - Mark read error -> returns `None` -> `apply_venue_price()` refuses signal (`auto_trader.py:348-350`), no orders placed.
  - Exchange check error -> returns `None` -> `settle_slot()` treats account as unverified, suppresses respawn, keeps slot busy (`auto_trader.py:710-715`).
  - Limit entry `no_fill` -> no manager spawned, plan recorded clean (`auto_trader.py:659-660`).
- **Existing Coverage:**
  - `MyTradingSys/execution/test_auto_trader.py:700` (`test_unreadable_or_invalid_mark_refuses_the_entry`)
  - `MyTradingSys/execution/test_auto_trader.py:742` (`test_mark_api_error_places_nothing_and_logs_the_reason`)
  - `MyTradingSys/execution/test_auto_trader_failclosed.py:60` (`test_auth_error_is_unreadable_not_flat`)
  - `MyTradingSys/execution/test_auto_trader_failclosed.py:66` (`test_position_error_or_garbage_size_is_unreadable_not_flat`)
  - `MyTradingSys/execution/test_auto_trader_failclosed.py:119` (`test_unreadable_position_counts_and_logs_throttled`)
  - `MyTradingSys/execution/test_auto_trader_failclosed.py:172` (`test_executor_api_error_is_entry_failed_and_no_manager`)

---

### 2.2 `execution/position_manager.py`

#### A. Restart / Reset State
- **Mechanics:** Loaded via CLI with `python position_manager.py <plan_id>` (`position_manager.py:640`). It reads `plans/<plan_id>.json` and checks existing orders using plan-scoped labels (`<plan_id>:<label>`).
- **Fail-Closed Behavior:**
  - Reconstructs active target orders and protective stop orders.
  - If the position is flat on restart but orders were not explained by fills, halts immediately (`ManagerHalted`, `position_manager.py:550`).
- **Existing Coverage:**
  - `MyTradingSys/execution/testnet/offline/test_fix3_offline.py:160` (`test_H5_read_failure_never_replaces_stop`)
  - `MyTradingSys/execution/test_pm_heartbeat_wiring.py:12` (`test_heartbeat_file_written_and_updated`)

#### B. Non-Trade Balance Moves
- **Mechanics:**
  - If position size increases unexpectedly outside the plan (`size > stop["amount"]`, e.g. via external manual trade or unexpected fill), the manager immediately resizes the stop to cover the entire position, writes `HALT_PATH`, journals `mismatch_halt`, and raises `ManagerHalted` (`position_manager.py:612-626`).
- **Fail-Closed Behavior:** Never leaves excess open contracts unprotected.
- **Existing Coverage:**
  - `MyTradingSys/execution/testnet/offline/test_fix4_offline.py:44` (`test_L3_market_fill_beyond_cap_flattens`)
- **Gap:** Pure non-trade balance moves (deposits/withdrawals) without position change are not evaluated by `position_manager.py` (which only checks Deribit contract counts).

#### C. API Errors
- **Mechanics:**
  - All read calls wrap `_retry_call(fn, *a, reauth=_reauth)` (`position_manager.py:146-170, 440-441`), handling transient network timeouts and re-authenticating expired tokens.
  - If a stop order cannot be queried (`query_failed`), it starts a timer `unprotected_since`.
- **Fail-Closed Behavior:**
  - If stop query fails or stop is missing for longer than `MAX_UNPROTECTED_SECONDS` (15.0s), triggers `flatten_halt()` (`position_manager.py:580-582, 594-597`).
  - During emergency flatten (`flatten_halt` at `position_manager.py:443-494`), targets are cancelled first, then market close is attempted, and the stop is cancelled **only after flat position is verified** (`position_manager.py:489-492`). If closing fails, the stop is left resting (`position_manager.py:485`).
- **Existing Coverage:**
  - `MyTradingSys/execution/testnet/offline/test_fix3_offline.py:21` (`test_C1_timeout_on_read_retries_then_deribit_error`)
  - `MyTradingSys/execution/testnet/offline/test_fix3_offline.py:32` (`test_C2_poll_read_failure_after_fill_flattens`)
  - `MyTradingSys/execution/testnet/offline/test_fix3_offline.py:48` (`test_C3_stop_cancelled_only_after_close`)
  - `MyTradingSys/execution/testnet/offline/test_fix3_offline.py:54` (`test_C3_close_fails_stop_kept`)
  - `MyTradingSys/execution/testnet/offline/test_fix3_offline.py:164` (`test_H5_consecutive_read_failures_flatten_after_bound_keeping_stop_until_flat`)
  - `MyTradingSys/execution/testnet/offline/test_s3_unprotected_offline.py:27` (`test_flattens_only_after_max_unprotected_seconds_elapsed`)

---

### 2.3 Java StateMachine (`Main.java` & `StateCodeEmitter.java`)

#### A. Restart / Reset State
- **Mechanics:**
  - In `Main.java:67-83`, `statemachine <symbol>` creates `StateCodeEmitter` and wires `BinanceLiquidationAccumulator`.
  - On restart, `StateCodeEmitter` loads previous `state_code.json` if available, but marks the state invalid until backfill completes (`StateCodeEmitter.java:237-250`).
  - `backfillRestoredState()` fetches historical 1m klines from Binance REST up to the connect timestamp to bridge the restart downtime gap (`StateCodeEmitter.java:310-370`).
  - At UTC midnight (`00:00:00Z`), `dayRollover()` resets daily CVD and volume accumulators to zero (`StateCodeEmitter.java:763-780`).
- **Fail-Closed Behavior:**
  - While reconnecting or backfilling, state is emitted with `valid: false` and `state: "UNKNOWN"`, preventing downstream systems (`start-trading-day.ps1`, `auto_trader.py`) from acting on partial calculations.
- **Existing Coverage:**
  - `src/test/java/datafeed/StateCodeEmitterTest.java:354` (`restartReplacesStaleRestoredSumsWithBackfill`)
  - `src/test/java/datafeed/StateCodeEmitterTest.java:379` (`reconnectGapSeamIsExact`)
  - `src/test/java/datafeed/StateCodeEmitterTest.java:531` (`dayRolloverContinuousResetsAndInvalidRebackfillsNewDay`)
  - `src/test/java/datafeed/StateCodeEmitterTest.java:576` (`closeInvalidatesAndClearsTheCvdRing`)
  - `src/test/java/datafeed/StateCodeEmitterTest.java:628` (`restartThenCloseBeforePublishStaysInvalidThenRecovers`)

#### B. Non-Trade Balance Moves
- **Mechanics:**
  - The StateMachine operates exclusively on the Binance public WebSocket feed (`wss://fstream.binance.com/ws/<symbol>@aggTrade`).
  - Frames that are pings, pong responses, heartbeat checks, or empty subscription notifications are intercepted in `onMessage` (`StateCodeEmitter.java:166-200`).
- **Fail-Closed Behavior:**
  - Non-trade messages are discarded without updating delta sums, trade counters, or VWAP accumulators.
- **Existing Coverage:**
  - `src/test/java/datafeed/StateCodeEmitterTest.java:471` (`nonTradeMessageLeavesSumsUnchanged`)
  - `src/test/java/datafeed/StateCodeEmitterTest.java:652` (`nonTradeMessageDuringPausedEmitLeavesSumsUnchanged`)

#### C. API Errors
- **Mechanics:**
  - Handles WebSocket `onError` and `onClose` events (`StateCodeEmitter.java:203-224`).
  - Handles REST backfill failures (e.g. Binance API 429/500 or network timeout) in `failBackfill()` (`StateCodeEmitter.java:292-308`).
- **Fail-Closed Behavior:**
  - Disconnect or socket error immediately sets `connectedAtMs = Long.MAX_VALUE`, invalidates published state, clears the CVD ring, and schedules an exponential-backoff reconnect (`scheduleReconnect()`).
  - A failed backfill marks accumulators as invalid, retains no unverified seam, and retries after a configured delay.
- **Existing Coverage:**
  - `src/test/java/datafeed/StateCodeEmitterTest.java:411` (`backfillErrorsFailClosedAndRecover`)
  - `src/test/java/datafeed/StateCodeEmitterTest.java:611` (`closeBetweenSnapshotAndPublishStaysInvalid`)
  - `src/test/java/datafeed/StateCodeEmitterTest.java:672` (`apiErrorOnRecoveryBackfillAfterRaceStaysInvalidThenRecovers`)
  - `src/test/java/datafeed/StateCodeEmitterTest.java:744` (`failedBackfillKeepsNoSeamAndNoTickIsSummed`)
  - `src/test/java/datafeed/LiquidationLogWiringTest.java:35` (Verifies liquidation log failure does not block state emitter)

---

## 3. Concrete Test Cases Matrix & Reproducing Inputs

The following table provides the reproducing input, failure injection, and expected fail-closed assertion for each case:

| Case ID | Module & Focus | Trigger / Reproducing Input | Expected Fail-Closed Assertion | Status | Existing File:Line Reference |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-AT-01** | `auto_trader.py`<br>Restart State | Write `trade_attempt` with `outcome="entered"` to `log.jsonl`; kill manager PID; call `recover_slots()` | Slot assigned `DeadProc()`; next cycle calls `exchange_flat()`; if flat, frees slot with `trade_closed`; if open, respawns manager. | **EXISTS** | `test_auto_trader.py:619`<br>`test_auto_trader_failclosed.py:239` |
| **TC-AT-02** | `auto_trader.py`<br>Restart State | Write 2 unclosed `trade_attempt` entries for same account; call `recover_slots()` | Only newest plan adopted into slot; older plan closed with `superseded_at_restart` + `record_ledger` call. | **EXISTS** | `test_auto_trader.py:639`<br>`test_auto_trader_failclosed.py:228` |
| **TC-AT-03** | `auto_trader.py`<br>Restart State | Emit actionable alert #42; restart `auto_trader`; emit alert #42 again | Alert #42 rejected (`tom_last_alert_no >= 42`); no second plan generated or placed. | **EXISTS** | `test_auto_trader.py:487`<br>`test_auto_trader.py:783` |
| **TC-AT-04** | `auto_trader.py`<br>Non-Trade Move | Mock account equity dropping below minimum required margin before order placement | `place()` refuses or aborts without spawning position manager; logs refusal reason. | **MISSING** | Missing test in `test_auto_trader.py` (relies on downstream executor failure). |
| **TC-AT-05** | `auto_trader.py`<br>API Error | Mock `deribit_mark()` returning `None` or raising HTTP error | `apply_venue_price()` rejects signal; `place()` not called; logged as `mark_unreadable`. | **EXISTS** | `test_auto_trader.py:700`<br>`test_auto_trader.py:742` |
| **TC-AT-06** | `auto_trader.py`<br>API Error | Mock `exchange_flat()` returning `None` (auth failure / HTTP timeout) | `settle_slot()` returns `False`; slot kept busy; no respawn; throttled warning logged. | **EXISTS** | `test_auto_trader.py:564`<br>`test_auto_trader_failclosed.py:60` |
| **TC-AT-07** | `auto_trader.py`<br>API Error | Subprocess `executor.py --go` returns non-zero code | `place()` returns `entry_failed`; no manager spawned; slot freed immediately. | **EXISTS** | `test_auto_trader.py:572`<br>`test_auto_trader_failclosed.py:172` |
| **TC-PM-01** | `position_manager.py`<br>Restart State | Launch `position_manager.py <plan_id>` with existing resting orders | Adopts existing orders from plan; queries exchange position; resumes polling without duplicate orders. | **EXISTS** | `test_fix3_offline.py:160`<br>`position_manager.py:495` |
| **TC-PM-02** | `position_manager.py`<br>Restart State | Kill running `position_manager.py` with active position | Heartbeat stops; auto-trader / watchdog detects dead process and initiates exchange check. | **EXISTS** | `test_pm_heartbeat_wiring.py:12`<br>`test_auto_trader_failclosed.py:239` |
| **TC-PM-03** | `position_manager.py`<br>Non-Trade Move | External position increase (`size > stop["amount"]`) while managing | Resizes stop immediately to cover `size`; logs `mismatch_halt`; writes `HALT_PATH`; raises `ManagerHalted`. | **EXISTS** | `position_manager.py:613-626`<br>`test_fix4_offline.py:44` |
| **TC-PM-04** | `position_manager.py`<br>Non-Trade Move | Margin balance reduced by fee or external withdrawal | Manager validates contract position count only; does not abort on wallet balance delta alone. | **MISSING** | No dedicated unit test verifying behavior under external margin reduction. |
| **TC-PM-05** | `position_manager.py`<br>API Error | Mock `get_order_state(stop_id)` returning `query_failed` for > 15 seconds | `flatten_halt()` cancels targets, issues market close; keeps stop until position confirms 0; halts. | **EXISTS** | `test_fix3_offline.py:164`<br>`test_s3_unprotected_offline.py:27` |
| **TC-PM-06** | `position_manager.py`<br>API Error | Mock `close_position()` throwing `DeribitError` during emergency flatten | Stop is **NOT** cancelled; raises `ManagerHalted("FLATTEN ITSELF FAILED")`; writes `HALT_PATH`. | **EXISTS** | `test_fix3_offline.py:180`<br>`position_manager.py:485` |
| **TC-PM-07** | `position_manager.py`<br>API Error | Mock `do.edit()` throwing `DeribitError` during stop resize | Calls `flatten_halt()`; flattens position; writes `HALT_PATH`; halts execution. | **EXISTS** | `position_manager.py:616-617`<br>`test_fix3_offline.py:195` |
| **TC-SM-01** | `Java StateMachine`<br>Restart State | Provide stale `state_code.json` on JVM restart; inject REST kline response | Discards stale sums; backfills up to connect time; only emits valid state once backfill is aligned. | **EXISTS** | `StateCodeEmitterTest.java:354`<br>`StateCodeEmitter.java:237-250` |
| **TC-SM-02** | `Java StateMachine`<br>Restart State | Advance simulated clock past UTC `00:00:00Z` | CVD and cumulative volume reset to 0.0; valid state re-established for new day. | **EXISTS** | `StateCodeEmitterTest.java:531`<br>`StateCodeEmitter.java:763` |
| **TC-SM-03** | `Java StateMachine`<br>Non-Trade Move | Send non-trade WebSocket frame (e.g. `{"result":null,"id":1}`) | Ignored by message parser; accumulators remain unchanged; state remains valid. | **EXISTS** | `StateCodeEmitterTest.java:471`<br>`StateCodeEmitterTest.java:652` |
| **TC-SM-04** | `Java StateMachine`<br>API Error | Mock Binance REST backfill returning HTTP 500 / connection timeout | `failBackfill()` marks `valid: false`; suppresses trading signals; sets exponential retry. | **EXISTS** | `StateCodeEmitterTest.java:411`<br>`StateCodeEmitterTest.java:672` |
| **TC-SM-05** | `Java StateMachine`<br>API Error | Trigger WebSocket disconnect (`onClose`) mid-stream | Invalidator clears CVD ring; sets `connectedAtMs = MAX_VALUE`; schedules reconnect. | **EXISTS** | `StateCodeEmitterTest.java:576`<br>`StateCodeEmitter.java:203` |

---

## 4. Priority Test Gaps & Action Plan

1. **Gap 1: Auto-Trader Pre-Flight Wallet Equity & Balance Check (`auto_trader.py`)**
   - *Issue:* `auto_trader.py` does not perform a direct non-trade balance check before invoking `new_plan.py` / `executor.py`.
   - *Proposed Test:* Inject a mock Deribit balance check returning insufficient margin or zero equity; verify `cycle()` rejects the candidate cleanly with `outcome="insufficient_balance"` without corrupting active slots.
2. **Gap 2: Position Manager Margin Depletion Monitor (`position_manager.py`)**
   - *Issue:* While `position_manager.py` halts if position contract size increases unexpectedly (`TC-PM-03`), it does not observe account equity or liquidation margin ratios.
   - *Proposed Test:* Add offline test verifying behavior when account balance approaches maintenance margin threshold.
