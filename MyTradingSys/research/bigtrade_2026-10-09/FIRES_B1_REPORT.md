> **RERUN 2026-10-17 (DEV only, new labels):** the fire CSVs on F: were relabelled with the repo split (split-relabel-fires). The per-year table below is by t_fire_ms and unchanged; only the split column changed. New split counts over all 19 perp files: see SPLIT_ALIGNMENT_2026-10-17.md section 'Rerun status'. This report holds no split-based result, so there is no verdict to rerun.

> **CONTAMINATED (DEV read VALIDATION 2024-07..12)** - the split column (TRAIN to 2025-01-01) puts 25,607 of 153,685 TRAIN fires in 2024-07..12. See MyTradingSys/backtest/bigtrade/SPLIT_ALIGNMENT_2026-10-17.md. Numbers below are kept as originally run, not recomputed.

# FIRES_B1_REPORT - fire history of the kline-only live layers (worker B1, 2026-10-09)

Session MTS-2026-10-08-1933Z-APP-ANA-bigtrade-bt. Code: `MyTradingSys/backtest/bigtrade/fires_kline.py`, `parity_kline.py`, `test_fires_kline.py` (36 tests, all pass; new files only, not committed).
Data: `F:\MTS\data\bigtrade\fires\` (19 CSVs + `_summary_B1.json`, `_parity_B1.json`, `_parity_diffs_B1.csv`). Code commit of the layers: `84269f1` (imported layer files identical to HEAD).

## 0. UPDATE 2026-10-09: spot rerun PASSES parity
Fires re-run on spot 1m history: `F:\MTS\dataigtradeires_spot\`. All kline keys 92-100 % parity, turn_of_candle side mismatches 0 (was 112). Use fires_spot; sections 1-4 below describe the superseded perp run. See FINDINGS F-BT-18.

## 1. Bottom line
- 19 live kline keys replayed over 2022-01-01 .. 2026-10-07 (2,507,040 1m bars, no gaps), 244,543 fires. Two live keys are not kline-only and go to B2: `fabio|v3_grid|1m` (needs aggTrades order-flow columns), `positioning|funding_cvd_fade|1h` (needs funding history). `malkan_mtf` is not live (no adapter; needs weekly+monthly RSI regimes a 99-bar window cannot hold), so it has no fires.
- Parity gate (last 5 days, runner-dark time removed): **only turn_of_candle TIMING (99.7 %) passes 95 %**; its SIDE agrees on 70.8 %. rsi_events 5m 65.3 % and 15m 77.8 % fail; cryptocred and fabio keys are at 0-4 %. rsi 1h, malkan_bull, session_momentum read 100 % on n = 1, 2, 3 (not evidence).
- Cause: not the replay logic (proved equal to `live_runner_core.run_registry`, section 5) but the data venue: **the live runner polls SPOT klines, all history on disk is USD-M PERP** (F-BT-18, HIGH, escalated). A clean parity needs spot 1m history (approval needed to download, exact command in F-BT-18).
- Use of the CSVs by worker A: filter `tradable == 1`; rsi / cross / support / rejection rows are alert-only (blank side). Treat fires of every key marked NOT TRUSTED in section 3 as "what the layer logic does on perp bars", not as "what the live system signalled".

## 2. How a fire is produced
The live runner (`live_runner_cli.main`, default `--limit 100`) fetches the newest 100 klines per timeframe, drops the open one, and `live_runner_core.run_registry` calls each registered layer function on the **99 newest closed bars**, keeps events that are new against the previous call and at most `confirm_lag_bars + 1` bars old, and de-duplicates on `(key, t, event)`. `replay_key` repeats exactly that per closed bar, with the registry's own `fn`, `confirm_lag_bars` and `params_id` (registry built by the live code, read-only). Chunked parallel runs warm the state 150 bars before each chunk (test: chunked == single pass).
- `t_fire_ms` = close of the bar on which the event was first reported (earliest moment a live alert could exist). `t_event_ms` = the layer's own event bar open, `t_confirm_open_ms` = open of the reporting bar. Entry is the next bar open at the earliest. Lag between event and reporting bar: 0 for all keys except `volume_fvg` (always 1, by design) and 0.5 % of rsi / malkan events (1 bar, RSI warm-up changes with the sliding window).
- Bars: 1m perp archive resampled by a numpy aggregator that also sums `tbv` (`tf_resample` drops it, F-BT-23; equal on o/h/l/c/v, tested). ATR = Wilder(14) on the layer's own TF (`atr_kind = wilder`, F-BT-07 contract). Fees: `trade_costs.net_return` defaults, fee_rt 0.0010 round trip, slip_rt 0.0002.
- CSV columns (PLAN section 5 + extras): layer, key (`layer:rsi:rsi_events:5m`), tf, event, side, tradable, t_fire_ms, t_event_ms, t_confirm_open_ms, split (TRAIN / VALIDATE / HOLDOUT / POST), price (close of the reporting bar), entry_price, stop, target (only if the layer emits them: cryptocred emits entry_price + stop, no target), atr, atr_kind, atr_pct, stop_dist_atr, stop_dist_pct, fee_R (fee_rt / stop distance as a share of entry), cost_R (fee + slip), fee_R_1atr (fee when R = 1 ATR), fee_dominated (stop distance strictly under the fee, tolerance 1e-9), rsi, rsi_ma (as the live alert carries them), extra (JSON), params_id, params_json, code_commit, data_venue.

## 3. Fires per layer per year and trust verdict
Fires counted at `t_fire_ms` (UTC year); 2026 ends 2026-10-07. "tradable" = rows with a side.

| key | fires | tradable | 2022 | 2023 | 2024 | 2025 | 2026 | /day | parity (5 d) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| turn_of_candle 1m | 167,130 | 167,107 | 35,033 | 35,040 | 35,136 | 35,040 | 26,881 | 96.0 | time 99.7 %, side 70.8 % | timing TRUSTED, side NOT |
| rsi_events 5m | 41,538 | 5,241 | 8,651 | 8,572 | 8,655 | 8,915 | 6,745 | 23.9 | 65.3 % | NOT TRUSTED |
| rsi_events 15m | 13,411 | 1,566 | 2,876 | 2,824 | 2,701 | 2,828 | 2,182 | 7.7 | 77.8 % | NOT TRUSTED |
| rsi_events 1h | 3,136 | 380 | 728 | 615 | 633 | 673 | 487 | 1.8 | 100 % (n=1) | UNTESTED |
| malkan_bull 1h | 116 | 116 | 22 | 22 | 30 | 25 | 17 | 0.1 | 100 % (n=2) | UNTESTED |
| malkan_bear 1h | 143 | 143 | 36 | 28 | 29 | 31 | 19 | 0.1 | n=0 | UNTESTED |
| session_momentum 15m | 1,740 | 1,740 | 364 | 365 | 366 | 365 | 280 | 1.0 | 100 % (3 of 3 live-up) | UNTESTED (n=3) |
| sr_flip 15m | 6,071 | 6,071 | 1,363 | 1,280 | 1,268 | 1,221 | 939 | 3.5 | 4.3 % | NOT TRUSTED |
| sr_flip 1h | 1,529 | 1,529 | 331 | 325 | 324 | 320 | 229 | 0.9 | 33.3 % (n=3) | NOT TRUSTED |
| fib_pullback 15m | 1,630 | 1,630 | 387 | 367 | 338 | 297 | 241 | 0.9 | 0 % | NOT TRUSTED |
| fib_pullback 1h | 390 | 390 | 87 | 82 | 91 | 73 | 57 | 0.2 | 0 % | NOT TRUSTED |
| failed_msb 15m | 597 | 597 | 134 | 122 | 141 | 114 | 86 | 0.3 | 0 % (live 0) | NOT TRUSTED |
| failed_msb 1h | 166 | 166 | 37 | 46 | 25 | 29 | 29 | 0.1 | n=0 | UNTESTED |
| escalation 15m | 1,186 | 1,186 | 176 | 369 | 182 | 249 | 210 | 0.7 | 0 % | NOT TRUSTED |
| escalation 1h | 70 | 70 | 13 | 22 | 4 | 20 | 11 | 0.0 | 0 % | NOT TRUSTED |
| cvd_absorption 15m | 3,535 | 3,535 | 722 | 720 | 710 | 799 | 584 | 2.0 | 0 % | NOT TRUSTED |
| cvd_absorption 1h | 806 | 806 | 145 | 156 | 178 | 191 | 136 | 0.5 | 0 % | NOT TRUSTED |
| volume_fvg 15m | 1,101 | 1,101 | 211 | 238 | 222 | 246 | 184 | 0.6 | 0 % | NOT TRUSTED |
| volume_fvg 1h | 248 | 248 | 44 | 50 | 49 | 64 | 41 | 0.1 | 0 % (live 0) | NOT TRUSTED |

Rates are sane: the only layer near 100 a day is turn_of_candle at 96.0 (one per quarter hour by design); rsi 5m peaks at 54 events a day, escalation 15m at 12. escalation 15m has 369 fires in 2023 against 176-249 in other years. Errors raised by any layer function over the whole history: 0.

Fee picture from the CSVs (R = stop distance, or 1 ATR where the layer has no stop):
- sr_flip: stop = level -/+ 0.10 % = the round-trip fee, so fee_R = 1.00 on all 7,600 fires, median stop 0.33 ATR (15m) / 0.16 ATR (1h) (F-BT-22). fib_pullback median fee_R 0.62 / 0.46, stop 0.59 / 0.39 ATR. failed_msb median fee_R 0.14 / 0.07, stop 2.71 / 2.29 ATR.
- No-stop layers, fee when R = 1 ATR of the TF (median): turn_of_candle 1.68 (fee exceeds a 1-ATR move), rsi 5m 0.61, rsi 15m 0.32, rsi 1h 0.15, escalation 15m 0.59, cvd 15m 0.37, volume_fvg 15m 0.35, session 0.31, 1h layers 0.15-0.25.

## 4. Parity gate
Window: 2026-10-03 00:00 .. 2026-10-07 23:59 UTC (the last 5 days with kline history; the live alert log runs on to 10-08 19:29 but the archive stops at 10-07). Match key `(registry key, event bar time, event name)`; "name~" = same bar and event family but different price in the name (none occurred: pairs are strict or absent). Live duplicate rows dropped: 41 (F-BT-21).

Runner-dark time is removed from the only-replay column, from turn_of_candle (a fire every 15 min): runs of >= 2 missing slots at 10-03 21:29..10-04 08:59 (47 slots), 10-05 17:44..10-06 04:59 (46), 10-07 23:29..23:59 (3); auto_trader logged 0 events inside all three (F-BT-19). A single lost slot (10-06 15:29) stays a miss.

| key | replay | live | matched | only-live | only-replay (live up) | dark | raw % | parity % | side differs |
|---|---|---|---|---|---|---|---|---|---|
| turn_of_candle 1m | 480 | 383 | 383 | 0 | 1 | 96 | 79.8 | **99.7** | 112 of 383 |
| rsi_events 5m | 113 | 100 | 79 | 21 | 21 | 13 | 59.0 | 65.3 | 0 |
| rsi_events 15m | 38 | 32 | 28 | 4 | 4 | 6 | 66.7 | 77.8 | 0 |
| rsi_events 1h | 1 | 1 | 1 | 0 | 0 | 0 | 100 | 100 (n=1) | 0 |
| malkan_bull 1h | 2 | 2 | 2 | 0 | 0 | 0 | 100 | 100 (n=2) | 0 |
| malkan_bear 1h | 0 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | 0 |
| session_momentum 15m | 5 | 3 | 3 | 0 | 0 | 2 | 60.0 | 100 (n=3) | 0 |
| sr_flip 15m | 15 | 13 | 1 | 12 | 10 | 4 | 3.7 | 4.3 | 0 |
| sr_flip 1h | 3 | 1 | 1 | 0 | 2 | 0 | 33.3 | 33.3 | 0 |
| fib_pullback 15m | 5 | 2 | 0 | 2 | 4 | 1 | 0 | 0 | 0 |
| fib_pullback 1h | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 |
| failed_msb 15m | 2 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 |
| escalation 15m | 6 | 6 | 0 | 6 | 6 | 0 | 0 | 0 | 0 |
| escalation 1h | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 |
| cvd_absorption 15m | 17 | 9 | 0 | 9 | 15 | 2 | 0 | 0 | 0 |
| cvd_absorption 1h | 4 | 2 | 0 | 2 | 3 | 1 | 0 | 0 | 0 |
| volume_fvg 15m | 4 | 1 | 0 | 1 | 3 | 1 | 0 | 0 | 0 |
| volume_fvg 1h | 2 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 |

parity % = matched / (matched + only-live + only-replay while live was up). failed_msb 1h, which had no replay fire in the window, is absent. Per-event listing: `_parity_diffs_B1.csv`. Counts for the sparse keys are single digits, so even a 100 % there cannot certify a layer.

Audit of the misses (report -> audit -> fix):
1. Replay logic vs live core: for all 19 kline keys, `replay_key` equals `run_registry` fed one 99-bar window per bar (alerts, t_confirm, side, rsi, rsi_ma and error counts), on seeded synthetic bars; chunked equals single pass; truncating the bars after t leaves earlier fires unchanged (row level, with ATR and costs). Eight mutations of the code (look-ahead window, window 100, no de-dup, no age filter, ATR over the whole series, doubled fee, resample without tbv, microseconds not converted) are each caught by at least one test (mutation run, 8 of 8). So the misses are data.
2. Venue size, measured with fields the live alerts log: turn_of_candle imbalance spot vs perp corr 0.55 over 400 fires, side agreement by |imbalance| 0.0-0.1: 36 of 68, 0.1-0.2: 36 of 58, 0.2-0.3: 34 of 55, 0.3-0.5: 74 of 91, >= 0.5: 91 of 111 (even strong imbalance differs in about 18 %). RSI(14) of the logged alert vs perp over the same 99-bar window: median |diff| 0.32 (5m, n=102), 0.15 (15m, n=70), 0.12 (1h, n=15); max 2.15 / 0.95 / 0.23.
3. rsi_events: of the 42 (5m) and 8 (15m) unmatched events, all 50 had an RSI path within the venue noise of a band edge (39.5 / 40.5) on the reporting bar or the two before it, i.e. they can flip with spot-vs-perp price noise; none is far from an edge. This is a necessary condition, not proof.
4. Structure / flow keys: 0-4 % is expected from F-BT-20 (strict swing detector: a gap-free series has zero swings, 51 % of perp bars open exactly at the previous close, the strict detector keeps 32 % of the candidates) combined with different spot flow (example 10-03 06:30 in F-BT-18). Cannot be separated further without spot history.
5. Fix status: the code is venue-pluggable (`BIGTRADE_VENUE=spot`, `BIGTRADE_KLINE_DIRS=...`, microsecond stamps converted, separate cache and output folders, tested). The data step needs approval (F-BT-18).

## 5. Params used (JSON) and commit
Commit `84269f1`; the layer modules imported by the replay are identical to HEAD (the staged deletions in the tree are other files). Fee `fee_rt 0.0010`, `slip_rt 0.0002`, ATR Wilder 14, window 99 (live `--limit` 100 minus the open bar). Per-key values read with `inspect` from the module defaults plus the literals in `live_layers.py` (full JSON per row in `params_json` and in `_summary_B1.json`):
```json
{
 "turn_of_candle|1m": {"params_id": "turn_of_candle_defaults_2026-09-29", "lead_minutes": 1, "side": "sign of minute-0 taker imbalance"},
 "rsi_events 5m/15m/1h": {"params_id": "rsi_40_tol0.5_L1_2026-09-29", "level": 40.0, "tolerance": 0.5, "rsi_period": 14, "side": "failure events only"},
 "malkan_bull 1h": {"params_id": "malkan_bull_defaults_2026-09-29", "level": 40.0, "tolerance": 2.0, "regime lo/hi/lookback": [40.0, 60.0, 20]},
 "malkan_bear 1h": {"params_id": "malkan_bear_defaults_2026-09-29", "level": 60.0, "tolerance": 2.0, "regime lo/hi/lookback": [40.0, 60.0, 20]},
 "session_momentum 15m": {"params_id": "session_momentum_defaults_2026-09-29", "session_start_min": 0, "first_min": 30, "entry_min": 30, "min_abs": 0.0, "bar_min": 15},
 "sr_flip 15m/1h": {"params_id": "sr_flip_defaults_2026-09-29", "stop_buffer_pct": 0.001, "target_r": 1.5, "retest tolerance/invalidate/expiry": [0.0015, 0.005, 200], "swing left/right/use_body": [2, 2, true], "msb require_prior_sequence": true},
 "fib_pullback 15m/1h": {"params_id": "fib_pullback_defaults_2026-09-29", "fib_lo": 0.618, "fib_hi": 0.786, "stop_buffer_pct": 0.001, "target_r": 1.5},
 "failed_msb 15m/1h": {"params_id": "failed_msb_defaults_2026-09-29", "failure_lookback": 20, "stop_buffer_pct": 0.001, "target_r": 2.0},
 "escalation 15m/1h": {"params_id": "escalation_defaults_2026-09-29", "aggression_k": 2.0, "level_tolerance": 0.001, "record_lookback": 20, "left/right": [2, 2], "use_body": true},
 "cvd_absorption 15m/1h": {"params_id": "fabio_cvd_default_2026-09-29", "price_tolerance": 0.001, "left/right": [2, 2], "use_body": true},
 "volume_fvg 15m/1h": {"params_id": "volume_fvg_defaults_2026-09-29", "n_bins": 20, "va_pct": 0.7, "touch_scan_bars": 200, "left/right": [2, 2], "use_body": true, "confirm_lag_bars": 1}
}
```
Registry vs `auto_trader_config.json`: every kline key has an account (failed_msb falls into `layer:cryptocred:`); no parameter disagrees. Docs vs code: F-BT-24.

## 6. Data and anomalies seen
Coverage 2022-01-01 .. 2026-10-07 23:59 UTC, 2,507,040 bars, 0 gaps, 10,080 identical duplicate rows (daily files over the 2025-09 month file), 0 conflicting, 308 flat zero-volume bars in 13 outage hours (F-BT-05, expected), 0 bars with tbv > v or high < low. Resampled bars: 501,408 (5m), 167,136 (15m), 41,784 (1h).
Findings raised: F-BT-18 (spot vs perp, HIGH), F-BT-19 (live stack dark 23 h), F-BT-20 (swing tie sensitivity), F-BT-21 (duplicate alert rows), F-BT-22 (sr_flip stop = fee; float tie bug in B1's own code fixed with a test that failed first), F-BT-23 (tf_resample drops tbv), F-BT-24 (stale docs, malkan_mtf not live, RSI one-bar repaint).

## 7. Reproduce
```
python -m MyTradingSys.backtest.bigtrade.fires_kline cache
python -m MyTradingSys.backtest.bigtrade.fires_kline run --workers 5 --resume-dir F:/MTS/data/bigtrade/cache/chunks_x   # about 9 min, below-normal priority
python -m MyTradingSys.backtest.bigtrade.fires_kline parity --days 5
python -m pytest MyTradingSys/backtest/bigtrade/test_fires_kline.py -q                                                # 36 tests, about 45 s
```
Add `MyTradingSys/backtest/bigtrade/test_fires_kline.py` to the run_all_tests.py list at promote time (supervisor).
