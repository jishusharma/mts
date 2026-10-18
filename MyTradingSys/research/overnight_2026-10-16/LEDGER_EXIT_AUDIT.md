# Ledger exit-label audit (W10, 2026-10-16, testnet, aggregates only)

Source: live trade_ledger.jsonl read-only, 813 rows (812 closed round trips + 1 unresolved). No ids or raw rows here.

## A. "target" exits with negative gross: ROOT CAUSE FOUND AND FIXED
- Ledger exit_reason counts: time_exit 785, target 24, stop 2, manual 1, none 1.
- Of the 24 "target" rows, 17 have NEGATIVE gross. All 17 have a fill label containing `stop_order` (14 `stop_order_pending_fill`, 3 `stop_order`) and the exit price is on the loss side of entry (long: below, short: above). Only 7 "target" rows carry a `target_1` fill label, and all 7 have gross >= 0. So 17 stops were mislabelled target; true split is 7 targets, 19 stops.
- Cause (code, not slippage, not a side or sign error): `position_manager.py` (~line 540-544): when the stop order state is unreadable (Deribit archives the triggered stop, `query_failed`), it falls back to the plan's reduce-side fills and sets `stop_state = "triggered_by_fills"` AND `target_filled = max(target_filled, rf)`, where rf is the stop's own fill. The reconciliation journal event then says target_filled > 0, and `trade_ledger.classify_exit` treated any truthy target_filled as "target" (source "journal"). Gross is computed from fills and is correct; only the label was wrong.
- Fix (small, ledger writer only; no order path touched): `classify_exit` now treats `stop_state == "triggered_by_fills"` as "target_filled is not evidence" and decides from the last fill label (`:target` -> target, otherwise stop). New test `test_triggered_by_fills_stop_is_not_labelled_target` fails on the pre-change code and passes now; the normal journal path (stop_state filled + target_filled) is unchanged.
- DECISION (OURS): position_manager's `target_filled` fold-in is left as is (live path, auto_trader may read it); only the classifier changed. Existing mislabelled rows in the ledger are NOT rewritten (append-only runtime data); any analysis of past rows must relabel via fill label containing `stop_order` => stop. Effect on stats: target count 24 -> 7, stops 2 -> 19; net P&L unchanged.
- Consequence for W1 numbers: its "16 targets, 0 stops" in 7 d overstates targets and understates stops (not recounted per window here).

## B. 11 `rsi:cross` alerts rejected as "unmapped"
- A rule exists: `layer_rules["rsi:cross"] = "level"` (added in aaf007a5b, "rsi:cross side-by-level"). The side then comes from `CROSS_SIDE_BY_LEVEL = {(40, down): short, (60, up): long}` using the alert's `level_value` and `direction`. A cross at any other level/direction (for example 30 or 70, or an alert lacking level_value) returns None and is rejected "unmapped rsi:cross (add a layer_rules entry)". The message is misleading: the rule is there, the level is not in the map. All-time 104 such rejections (2-18 per day since 2026-10-07), so this is steady, deliberate fail-closed behaviour, not a new regression. The rejection log row does not store level_value, so the exact levels cannot be counted from it (inference from code).
- DECISION (OURS): unmapped stays rejected (fail closed); no change. Optional follow-up for a later session: log level_value/direction in the rejection row and word the message "rsi:cross level not mapped".

## C. 97 % time exits (GO_LIVE_BAR line 4 < 5 %, T085): why
- Layer bracket defaults (auto_trader.py DEFAULT_CONFIG `layers`): stop 1.0 %, target "2" (2R), time exit after 8 bars of the signal timeframe (TOC may carry its own override in auto_trader_config.json; not checked here). TOC 1m (about 80 % of trades, 386 of 486 in 7 d, 384 of them time exits) holds at most 8 minutes, in which BTC rarely moves 1 % (stop) or 2 % (target); the exit is therefore the clock almost by construction. Slower layers (5m 40 min, 15m 2 h, 1h 8 h) hit the same arithmetic: a 1-2 % bracket versus typical BTC range over 8 bars.
- The ledger label is correct for these: 785 time_exit rows came from the journal time_exit event. The bar is structurally unreachable while TOC 1m dominates the count with a 1 %/2 % bracket on an 8-minute clock. Remedies (not done; they are strategy changes, need fee-net out-of-sample evidence per CLAUDE.md): measure the share per layer excluding TOC, size brackets to the layer horizon, or define the bar per layer.
- Combined with A: the true non-time exits are about 26 of 812 rows all-time (7 target + 19 stop), and the stop count is higher than the ledger showed.

## Gates
- run_all_tests.py full (execution/ touched). Result recorded in the commit body.
