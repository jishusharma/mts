# Live not-fired audit, window 2026-10-29 17:00Z .. 2026-10-30 08:00Z (card live-not-fired-audit-1029)

Read-only, on the live owner (DESKTOP-F7IU69N, live tree `C:\MTS\mts-live`, code at commit f435453c3 of 2026-10-22 plus the 10-30 05:29 deploy).
No live file was written, no process touched, no `.secrets`/`.env` read.

## Result

SILENT 18 of 27 LAYERS.md rows (23 layer ids + the 4 families that list no layer id); FIRED 9 of 27.
Silent by reason: no input wired 11 (rows 3,8,9,14,18,19,20,21,23,25,27), not built 1 (row 26), switched off by flag 1 (row 22), data feed dead 1 (row 7), gate not met on the same bars 3 (rows 5,11,13; proved by replay), no own output 1 (row 2).
Separately, the live registry has 27 poll keys; 11 fired, 16 silent (table 2). Window = 703 polls (17:00:52Z .. 08:00:19Z), 94 alerts, 14 runner errors (10 history_1m, 4 fetch), no log rotation (log starts 10-08).
Price (Binance public 1m klines): open 81,270, low 76,500 at the end of the move, close 78,132; the card's "82k" is the pre-window high, not in window.

## Evidence sources (all read-only)

- `E1` = `C:\MTS\mts-live\runtime_data\live_runner.log` `poll <utc> alerts=N errors=N <layer|sub|tf>=count ...` lines (one line per registered key per poll, 0 included). Summed over the 703 polls inside the window.
- `E2` = `C:\MTS\mts-live\MyTradingSys\execution\auto_trades.jsonl` (events trade_attempt / signal_rejected / skipped_busy, ts in the window).
- `E3` = `C:\MTS\mts-live\MyTradingSys\runtime\alerts\{1m,5m,15m,1h}.jsonl` (cross-check; 96 alerts by t_close vs 94 by poll: 2 boundary alerts on the window edge, rsi_events 5m and 1h).
- `E4` = replay: the live registry functions (`live_runner_cli.build_default_registry()`, imported from the live tree, bytecode writing off) run over sliding 100-bar windows of Binance public klines for the window. It reproduces every fired count exactly (rsi_events 1h 2, 15m 2; cvd_absorption 15m 1; volume_fvg 15m 1; sr_flip 15m 1; fib_pullback 15m 1; session_momentum 1) and gives 0 for every silent key, so those silences are "the detector found nothing on the same bars", not a wiring fault. candle_close replayed on 10,200 1m bars: 2 events, both outside the window.
- `E5` = `live_runner_cli.py` registry lines 436-523 (what is wired), `auto_trader_config.json` (account/size rules), process command lines (`Get-CimInstance Win32_Process`), `runtime_data\orderflow_live.log`, `MyTradingSys\runtime\wlow_bounce_forward.jsonl`.

## Table 1: one row per LAYERS.md layer (27 rows)

| # | LAYERS.md layer (family) | Status | Count in window | Evidence | Reason |
|---|---|---|---|---|---|
| 1 | tom_core (tom) | FIRED | 8 Tom alerts reached the trader (alert nos 528..544 advanced), 0 entered | E2: `tom#528` ts 17:08Z `net_rr 0.93 < 1.25`; 529/541 `verdict WATCH`; 531/532 `WAIT_PROOF`; 534/540/544 `WAIT_TRIGGER` | Fires from the Java state machine; every alert was rejected by the trader (1 net_rr, 7 verdict not in allowed list). The other alert nos in 528..544 do not appear in E2 (not explained here). |
| 2 | tom_proofs (tom) | SILENT | 0 own output | E2 verdict `WAIT_PROOF` on 2 of the 8 alerts | Proof flags ride inside Tom candidates, no separate live signal; book_imbalance/P06 have no source (LAYERS.md). |
| 3 | tom_vp_pivot (tom) | SILENT | 0 | grep of live_runner_cli, auto_trader.py, config, src/main/java: no reference | no input wired (closed backtest probe, backtest/vp_pivot_probe.py only). |
| 4 | fabio_cvd_absorption (fabio) | FIRED | 1 (15m 1, 1h 0) | E1 `fabio\|cvd_absorption\|15m`=1; E2 attempt entered, account jishu_11 | 1h silent: gate not met (E4 replay 0). |
| 5 | fabio_escalation (fabio) | SILENT | 0 (15m 0, 1h 0) | E1 both keys 0 on all 703 polls; E4 replay 0 | gate not met on the 100-bar window. Known limit: card t09-f4 says the 99-bar window misses 68 of 96 escalation signals (not re-measured here). |
| 6 | fabio_volume_fvg (fabio) | FIRED | 1 (15m 1, 1h 0) | E1 `fabio\|volume_fvg\|15m`=1; E2 entered, jishu_14 | 1h gate not met (E4 0). |
| 7 | fabio_v3 (fabio) | SILENT | 0 | E1 `fabio\|v3_grid\|1m`=0 x703; `orderflow_live.log` (17:05Z 10-30) `STALL next_ms=1792665180000 has not advanced for 15 min`, 474 STALL lines in the log, first `HTTPError 400 Bad Request` 2026-10-25T11:29Z; newest file `runtime\orderflow_live\2026-10-22.csv` (last write 10-22 10:33Z bar) | data stale: the order-flow writer is stuck on 2026-10-22 10:33Z, so `fabio_v3_live_flow` returns None (silent by design, fail closed; `last bar != flow bar`). Dead for 8 days. |
| 8 | fabio_of (fabio) | SILENT | 0 | no reference to fabio_of_model/orderflow_bars in the live registry (E5) | no input wired (backtest model; and the live order-flow feed under it is stale, row 7). |
| 9 | bb_lvn_triggers (guidance) | SILENT | 0 | Q33 closed "do not wire cross-guidance" (LAYERS.md); no live reference | no input wired by decision. (Different thing: the `bb_top_reversal` 15m adapter is wired, 0 fires, table 2.) |
| 10 | rsi_levels (rsi) | FIRED | 21 (5m 17, 15m 2, 1h 2) | E1 `rsi\|rsi_events\|*`; E2 9 entered (5m 6, 15m 1, 1h 2) | Most active TF = 5m. 9 further RSI "cross" events were rejected `unmapped rsi:cross (add a layer_rules entry)` (8 on 5m, 1 on 15m): fired but not tradeable. |
| 11 | rsi_divergence (rsi) | SILENT | 0 | E1 `rsi_divergence\|rsi_divergence\|1h`=0 x703; E4 0 | gate not met (no swing divergence confirmed on 1h bars in the window). |
| 12 | cryptocred (cryptocred) | FIRED | 2 (sr_flip 15m 1, fib_pullback 15m 1; failed_msb 15m/1h 0, sr_flip 1h 0, fib 1h 0) | E1; E2 entered jishu_16 / jishu_18 | 4 of 6 keys silent: gate not met (E4 0). Both fires were inside the 78k..77k hit zone (E3). |
| 13 | funding_cvd_fade (positioning) | SILENT | 0 | E1 `positioning\|funding_cvd_fade\|1h`=0 x703; E4 0 (funding fetched live) | gate not met (needs funding percentile >= .95 or <= .05 plus CVD divergence). |
| 14 | oi_delta (positioning) | SILENT | 0 | no layer reads the OI file; `runtime\oi_live\oi_1m.csv` is written (recorder alive) | no input wired: OI is recorded, nothing consumes it except the wlow log. |
| 15 | session_momentum (session_timing) | FIRED | 1 | E1; E2 entered, jishu_9 | single fire in 15m. |
| 16 | turn_of_candle (session_timing) | FIRED | 60 | E1 `turn_of_candle\|turn_of_candle\|1m`=60; E2 45 entered, 15 `entry_failed` `HALTED: PREFLIGHT REFUSED: R8: instrument already has a position or open orders - clean account required` (first at 17:00:59Z) | Fired but 25% of attempts blocked: one shared account (jishu_1) with an open position. 17 of 60 inside the hit zone. |
| 17 | session_levels (session_timing) | FIRED | 1 | E1 `session_levels\|session_levels\|1m`=1; E2 `skipped_busy` | fired, not traded (account busy). |
| 18 | volume (volume_candles_ma) | SILENT | 0 | no live reference | no input wired (research-only, HOLDOUT sealed). |
| 19 | candle_patterns (volume_candles_ma) | SILENT | 0 | no live reference (the live `candle_close` key is a different lab-arm adapter, 0 fires, table 2) | no input wired. |
| 20 | ma_daily (volume_candles_ma) | SILENT | 0 | no live reference | no input wired (NO-SOURCE numbers). |
| 21 | bigtrade_fires (volume_candles_ma) | SILENT | 0 | no live reference in alerts/, auto_trader, src (the `fires_kline.py` module is backtest) | no input wired. |
| 22 | pitchfork_swing (pitchfork) | SILENT | 0 | `src/main/java/datafeed/PitchforkSignalLayer.java:26-30` `enabled()` = `Boolean.getBoolean("mts.pitchfork")`; the running Java is `mvn -q exec:java -Dexec.mainClass=datafeed.Main -Dexec.args=statemachine BTCUSDT` (pid 6972/15172) with no `-Dmts.pitchfork`; no MAVEN_OPTS, `.mvn`, pom or script sets it | switched off: built and verified, flag never set in live. Not an error. |
| 23 | pizzino_indicators (pizzino) | SILENT | 0 | LAYERS.md "not backtested, not wired"; no live reference | no input wired. |
| 24 | live_engine (family, no layer id) | FIRED | 62 orders entered, 15 refused (R8), 8 skipped_busy | E2 | execution works; not a signal layer. Supervisor HALT status not read (HALT files off limits). |
| 25 | callers (family, no layer id) | SILENT | 0 | LAYERS.md: scorecard only; no live reader | no input wired. |
| 26 | krown (family, no layer id) | SILENT | 0 | LAYERS.md: "Detectors not built" | no input (not built). |
| 27 | wavetrend (family, no layer id) | SILENT | 0 | LAYERS.md: "no live integration" | no input wired. |

Count check (parsed from LAYERS.md, not eyeballed): 23 `- Layer` ids; 14 families, 4 without a layer id (live_engine, callers, krown, wavetrend); 23 + 4 = 27 rows. FIRED = rows {1,4,6,10,12,15,16,17,24} = 9; SILENT = 18 (11+1+1+1+3+1).

## Table 2: live registry keys not covered by the 23 ids (and all 27 poll keys)

27 poll keys in E1; fired 11, silent 16.

| Key | Count | Note |
|---|---|---|
| turn_of_candle 1m | 60 | row 16 |
| rsi_events 5m / 15m / 1h | 17 / 2 / 2 | row 10 |
| levels confluence 1m | 7 | no LAYERS.md id. Events 20:42Z (4h fractal lows 79,221..79,506, long x4), 00:00Z prior_day_low 77,910 long and round_1000 78,000 short, 00:22Z round_1000 77,000 long. 4 of the 7 entries `skipped_busy`, 3 entered |
| session_levels 1m | 1 | row 17 |
| cryptocred fib_pullback 15m, sr_flip 15m | 1, 1 | row 12 |
| fabio cvd_absorption 15m, volume_fvg 15m | 1, 1 | rows 4, 6 |
| session_momentum 15m | 1 | row 15 |
| SILENT keys (16): bb_top_reversal 15m, candle_close 1m, cc failed_msb 15m/1h, sr_flip 1h, fib 1h, fabio cvd 1h, escalation 15m/1h, volume_fvg 1h, v3_grid 1m, funding_cvd_fade 1h, rsi_divergence 1h, malkan_bull 1h, malkan_bear 1h, wlow_bounce 1h | 0 | gate not met (E4 replay 0) except v3_grid (stale feed, row 7). wlow_bounce: forward log shows 6 rows in the window all `state=ARMED` (prior weekly low 79,178.6), never `ACTIVE`, so no trigger. candle_close: replay gives 2 events, both outside the window. malkan has no LAYERS.md id (family rsi). |

## Table 3: CBP analyst levels hit vs silent layers

Analyst ladder: CBP store is not on this machine (`runtime_data/cbp/cbp_store/rows.json` absent here and in the live tree; `analyst_levels.py` printed "0 BTC rows"), so the three levels are taken from the card (78k, 77.3k, 77k). Hit test = Binance public 1m klines (high >= level >= low):

| Level | 1m bars touching | First touch (UTC) | Last touch | Layers that fired on that move |
|---|---|---|---|---|
| 78,000 | 23 | 10-29 23:46 | 10-30 04:09 | levels confluence `round_1000_78000` short at 00:00Z (matched the level itself); turn_of_candle, cryptocred sr_flip/fib 15m, session_momentum 15m, session_levels 1m, rsi 15m/5m all fired inside 23:46..04:10 |
| 77,300 | 19 | 10-30 00:18 | 02:35 | no layer names 77.3k (no round or fractal level there); same cross-section of generic layers firing |
| 77,000 | 30 | 10-30 00:22 | 02:17 | levels confluence `round_1000_77000` long at 00:22Z (matched) |

In the hit zone (23:46..04:10) by E3: turn_of_candle 17, levels confluence 3, rsi 5m 1, rsi 15m 1, cryptocred 2, session_momentum 1, session_levels 1. Silent through the whole fall: all 16 silent keys, plus every layer with no input.

Finding for the operator quote ("first look into everything not fired in live mode"):
1. No live code reads CBP or news (0 hits in alerts/, auto_trader, config, src). The 78k/77.3k/77k levels reached the engine only by coincidence where they were round numbers (78k, 77k); 77.3k was seen by nothing. Analyst levels are not a layer, not an input.
2. 11 of 27 rows have no live input at all; adding them to the live runner is a build task, not a bug.
3. Real faults (not design): (a) order-flow writer stuck since 2026-10-22 10:33Z with HTTP 400 and 474 restarts, killing fabio_v3 for 8 days; (b) 15 of 60 turn_of_candle entries refused by R8 on shared account jishu_1, plus 8 skipped_busy; (c) 9 RSI cross events rejected as `unmapped rsi:cross`; (d) Pitchfork never switched on in the Java launch; (e) 14 fetch/history errors in the window (10 `history_1m` timeouts/500/reset, one 01:31Z DNS failure `getaddrinfo failed` on all four fetches, one poll lost).
4. Silent-by-gate keys behave as designed on the window: the replay gives the same fire counts as live, so nothing was missed by a bug in the polled layers.

DECISIONs (OURS): window edges inclusive; counts from poll lines (E1) are primary and the alerts files (E3) a cross-check; "silent" = 0 alerts from that layer's own key, including layers whose only live key is a different sub-adapter; family rows with no layer id are counted as one row each so the 27-row count is explicit; card's "run as Agent" deviation from worker=session logged (OURS, read-only, no live change).
