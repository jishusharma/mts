# Critical test wave 1: items 1, 2, 5 (2026-10-30)

Plan: `MyTradingSys/system/CRITICAL_TEST_PLAN.md`. Author model: Opus 5.5. Second-model reviews are filed as cards (below) and not answered yet.

## Item 1 (T1, I): FT2 CRITICALs and the kill-switch BLOCKER on trunk

Method: for each finding, the fix commit, the test that covers it, and a run of that test on the code before the fix.
Pre-fix code for FIX3 = tree `03bd84035` (the FIX3 commit `c4c55076c` plus `risk_guard.py`, which arrived 45 s later; the 5 fixed files are byte-identical in both) with `review/fix3_diff.patch` reversed (the staged `.pre_fix3` files the review read). Pre-fix code for B1 = `kill_switch.py` at `0ef6f946d^` inside tree `0ef6f946d`. Script: `item1_prefix_check.py` (builds the trees in a scratch folder, never touches the repo).

| Finding | Fix commit | Test(s) | On trunk today | On pre-fix code |
|---|---|---|---|---|
| FT2 C1: transport errors bypass fail-closed | `c4c55076c` (`deribit_orders.TRANSPORT_ERRORS`, `_call` raises OrderStateUnknown on order-creating calls) | `test_fix3_offline.py::C1TransportErrors` (3) + `test_C1_R1_raw_timeout_on_entry_create_that_filled` | pass | 4 of 4 FAIL |
| FT2 C2: poll-loop read failure leaves an unprotected fill | `c4c55076c` | `C2PollReadFailure` (3) | pass | 3 of 3 FAIL |
| FT2 C3: stop cancelled before the flatten (executor + position_manager) | `c4c55076c` | `C3ExecutorFlattenOrder` (5), `PositionManagerFixes::test_C3_pm_*` (2) | pass | 7 of 7 FAIL |
| Pre-mainnet #1 BLOCKER: kill_switch cancels the stop before the close | `0ef6f946d` (B1 close first, stop last once flat) | `test_premainnet1_offline.py::TestB1CloseFirst` (4) | pass | 4 of 4 FAIL (plus B2 1 FAIL) |

Trunk run 2026-10-30: `test_fix3_offline.py` 46 passed, 2 skipped; `test_fix3_mutants_offline.py` 13 passed; `test_premainnet1_offline.py` 9 passed. All three are in `scripts/dev/run_all_tests.py` (lines 465-470), so CI keeps them.
Limit: these tests use the in-memory fake exchange; that the fake behaves like Deribit is item 2's question.

Result: PASS. No new test needed.

## Item 2 (T1, U+I): restart/reset with recorded Deribit testnet responses; funding/settlement booking

Recorded testnet responses in git: only `research/loose_code/txlog_capture_2026-10-10_jishu_11.json` and `_13.json` (transaction log + account summary, read-only captures, B149). No recorded order, position, open-orders or order-state responses exist, so no restart/reset replay of executor + position_manager + reconciler can be run on real responses.

- Restart/reset replay: UNTESTABLE. Needed: a read-only recorder that saves the raw testnet responses of `get_positions`, `get_open_orders_by_instrument`, `get_order_state`, `get_user_trades` and the order calls through one testnet trade cycle with a process restart in the middle (on the host that holds the testnet secrets), then a replay client that serves them to the three modules.
- Settlement booking (non-trade balance move), checked on the recorded log with `item2_settlement_identity.py`:
  - The recorded summary obeys equity = balance + session_rpl + session_upl (0.99999231 vs 0.99999232).
  - Window from the 2026-10-10 08:00Z settlement to the capture (3 trades): by that identity P/L = sum(change) + session_rpl + session_upl = -6.30e-07 BTC. `mainnet_pnl.daily_pnl_btc` on the same entries = -5.45e-06 BTC. Gap -4.82e-06 BTC (the code shows about 8.6 times the loss).
  - The log holds no settlement entry for 2026-10-10 08:00 although a position was open 07:15-09:15 (the B149 reasoning used the 10-09 settlement only).
  - Assumption (labelled OURS): session_rpl and session_upl were 0 right after the 10-10 08:00 settlement. One capture cannot prove it; a second capture with equity at both ends can.
  - Result: FINDING, MED (the daily-loss guard reads this number; here the error is on the safe side, a larger loss, but the formula is not shown right). Card `wave1-settlement-pnl-identity-gap`.
  - Pinned offline: `test_mainnet_pnl.py::RecordedSettlementTests::test_recorded_settlement_identity` (expectedFailure, expected from the identity).
  - Formula fix waits on settlement-capture-testnet-second-log.
  - UPDATE 2026-10-31 (card wave1-item2-settlement-window-and-double-count, CRITICAL_24H_AUDIT Finding 1): the gap above was a WINDOW error in the test, not a formula error in `mainnet_pnl.py`. session_rpl restarts only at a settlement entry, and the log has none at 2026-10-10 08:00Z, so the OURS assumption (rpl = 0 after 10-10 08:00) was wrong. Last settlement = 2026-10-09T08:00:00Z (36h before capture).
    - Hand arithmetic, `_11.json`, 11 entries strictly after that settlement: 8 trades x -6.1e-07 + 3 x -6e-07 = -6.68e-06 change. Cashflow on the 6 profit_as_cashflow trades: -4e-08 +4.7e-06 -8.2e-07 +9.9e-07 -3.05e-06 -6e-07 = +1.18e-06 vs session_rpl +1.17e-06 (summary rounded to 1e-8). Identity: -6.68e-06 + 1.17e-06 + upl 0 = -5.51e-06; `daily_pnl_btc` = -5.50e-06 (diff 1e-8, rounding).
    - `_13.json` cross-check: 2 profit_as_cashflow trades +6.28e-06 -3.70e-06 = +2.58e-06 vs session_rpl +2.56e-06; its 01:00Z cashflow, before 08:00Z, is still in session_rpl, again no reset without a settlement entry.
    - Test fixed: slice strictly after the last settlement, expectedFailure dropped. It failed first on the old 4h slice (-5.45e-06 vs -6.3e-07, gap 4.82e-06).
  - Double-count (pre-08:00Z P/L booked by both trade cashflow and settlement): refuted for the recorded shapes; unproven for profit_as_cashflow=True before a settlement. Day window from 2026-10-09T00:00Z (07:31Z opener cashflow 0, 08:00Z settlement -1.59e-06, then the 11 trades): equity change by hand = -6.1e-07 -1.59e-06 -6.68e-06 +1.17e-06 = -7.71e-06; `daily_pnl_btc` = -7.70e-06 (diff 1e-8). No overstatement on the recorded shapes; `mainnet_pnl.py` unchanged. Limit: the log has no profit_as_cashflow=True trade before a settlement, so that exact shape stays unrecorded; the code fails safe on it (settlement adds `change` only), pinned in `test_settlement_entry_does_not_add_its_cashflow_again`.

  - Second capture (card settlement-capture-testnet-second-log), 2026-10-31 18:58Z on JIS-NUC: NOT TAKEN, documented absence. capture_txlog_settlement.py refuses on this host because deribit_orders._load_secret finds neither the default nor the named testnet credential file, so no read-only API call can be made here. No testnet position record exists on this host either (loop health: java absent, supervisor absent; MyTradingSys/execution/journal holds only .gitkeep; runtime_data/live_monitor.txt is a 2026-09-20 price snapshot, not a position log), so there is no evidence of a position open across any 08:00Z settlement in the last 36 h, and none was opened. Both files are committed as the absence record: research/txlog_capture_2026-10-31_before.json and _after.json (kind=documented_absence, entries empty, account_summary null). Still open: a capture pair from a host holding the testnet credential, taken across a settlement with a position open. Until then the identity above rests on the 2026-10-09 settlement only.

## Item 5 (T5 + T6): live-vs-archive parity, one alert per candidate

This host is JIS-NB; the live owner is desktop-f7iu69n (`live_mirror.py brief`: "no live numbers from this host"). The live feed recordings and the alert log are not reachable here.
Result: UNTESTABLE here. Posted as a DSA desk task for the live host: `MyTradingSys/system/desk_queue/` id `20261029-193841-wave1-item5-live-vs-archive-parity-aggtr`, output `ITEM5_PARITY_RESULT.md`.

## Second-model review asks (another model family, code + source, no conclusion)

| Item | Card |
|---|---|
| 1 | `wave1-review-item1-ft2-fixes` (Gemini via `gemini_queue.py run wave1-review-item1-ft2-fixes:low`) |
| 2 | `wave1-review-item2-settlement-booking` (Gemini) |
| 5 | the DSA desk run is the reviewer's own measurement |
