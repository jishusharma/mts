# T09 Backtest-to-live parity (audit 2026-10-16)

## 1. Summary
- Checked: 30 DEV days replayed bar by bar through the live layer code (no network), against each layer's backtest code, plus the exit rules.
- Wrong: volume_fvg trades the opposite side of the reading that was backtested; the RSI layer trades events (cross, failure, rejection@40) that no backtest covered; every layer exits by one fixed 1%/2%/8-bar bracket that no backtest used.
- Changes: the backtest verdicts say nothing about what the testnet trades for 5 layer families; about 94% time exits follow from the bracket arithmetic alone (observed 97%), not from bad luck.

## 2. Scope
| What | Window | Method | Result |
|---|---|---|---|
| Deployed code | live checkout HEAD `4662684a3d` (read from the main checkout `.git/refs/heads/fast-track`; `.mts_live` marker is an empty file) | `git diff 4662684a3d 5879e97d3 -- MyTradingSys/backtest/layers MyTradingSys/execution` | empty (4662684a3 is an ancestor of the replayed `5879e97d3`, 138 commits, none touch layers/ or execution/). The replay IS the deployed code. |
| Live replay | 30 DEV days (list in `out/parity_result.json` "days"; seed 20261016: 10 trend, 10 range, 10 high-vol; 3 h state warm-up per day) | `live_runner_cli.build_default_registry` + `poll_once`, fake `fetch_fn` from `F:/MTS/data/tom_raw/klines`, 99 closed bars per tf, funding from `Dumps/backtest/raw/fundingRate`; `urlopen`, `socket.connect`, `create_connection`, `default_fetch_klines`, `_wlow_default_fetch/_oi`, `_hist_default_page`, `default_fetch_funding` all patched to raise | 0 network attempts, 0 runner errors, 4,075 tradable alerts |
| Backtest side | same days, 2,000-bar warm-up window per day | each study's own signal function (see map) | per-layer diff below |
| Exits | all DEV 1m bars, entry every 5-60 min | `scripts/T09/exit_analysis.py` (stop first inside a 1m bar) | section 6 |

Scripts (run from the worktree root): `scripts/T09/parity_core.py` (replay + diff, ~25 min, writes `out/parity_result.json`), `scripts/T09/exit_analysis.py` (`out/exit_result.json`), test `scripts/T09/test_layer_signal_parity.py`.

## 3. Layer map (account -> live function -> backtest -> parameter diffs)
Live bracket for every layer (auto_trader.py:72-75 merged with the config): market entry, stop 1.0%, target 2%, time exit 8 bars of the signal tf, size 20 USD default (size_overrides per layer, config).

| Account | Layer key (tf) | Live function | Backtest that justified it | Parameter / rule differences |
|---|---|---|---|---|
| jishu_1 | turn_of_candle (1m) | live_layers.py:169 | run_t055.py c3 + run_t055_c3_imbalance | same detector, lead 1; side = sign of minute-0 imbalance (matches c3_imbalance). Backtest exit: fixed horizon 1/2/5 bars, no bracket. |
| jishu_2/3/4 | rsi_events 5m/15m/1h | live_layers.py:146 (level 40, tol 0.5) | BACKTEST_L1_REPORT D3 (support@40 long, rejection@60 short, tol 15m 1.0, 1h 0.5/1.5; 5m never run) | live also trades cross, failure, rejection@40; never watches level 60; 15m tol 0.5 vs 1.0. Backtest: forward return h=5 (no bracket). |
| jishu_7/8 | malkan_bull/bear (1h) | live_layers.py:111/117 | run_rsi_backtest.py malkan_events | same defaults (14, 2.0, 20). Backtest bracket 1%/2%/100 bars, entry = close. |
| jishu_9 | session_momentum (15m) | live_layers.py:68 | run_t055.py c2 (5m bars, hold to session end 1,440 min) | bar_min 15 vs 5; exit 8x15m vs session end. |
| jishu_10 | funding_cvd_fade (1h) | live_layers.py:88 | run_t055.py c1 (15m bars, horizons 4/16/48 bars) | tf 1h vs 15m. |
| jishu_11/12 | cvd_absorption 15m/1h | live_runner_cli.py:437 | fabio/run_backtest.py cvd_fn | same defaults (2/2/0.001). Backtest: forward return h=1/5/20, no bracket. |
| jishu_13 | escalation (1h, 15m) | live_layers.py:32 | run_backtest.py escalation_fn (chunked 1000/500 bars) | same defaults; live sees 99 bars, backtest 1,500. |
| jishu_14 | volume_fvg (1h, 15m) | live_layers.py:41 | run_backtest.py run_fvg | scan starts at start vs start+1; side inverted (F1). |
| jishu_16-20 | cryptocred sr_flip/fib_pullback/failed_msb (1h, 15m) | live_layers.py:122 | run_cc_setups.py + cc_setups | same functions. Backtest: limit/market entry, structure stop, R target, 1,440 1m-bar hold; live ignores the event's entry_price and stop. 15m never backtested. |
| jishu_21 (catch-all) | rsi_divergence 1h, bb_top_reversal 15m, wlow_bounce 1h, session_levels/candle_close/levels 1m, fabio v3_grid 1m | live_runner_cli.py:505-523 | none located for rsi_divergence / bb_top_reversal; others FAIL/INCONCLUSIVE studies | not diffed. |
| main | tom | auto_trader.tom_signal | tom_bt | out of scope (not a runner layer). |

## 4. Signal diff, 30 DEV days (entry-close time, same side = "same")
| Layer | live | backtest | same | side differs | off by 1 bar | live-only | backtest-only |
|---|---|---|---|---|---|---|---|
| turn_of_candle 1m | 2,880 | 2,880 | 2,880 | 0 | 0 | 0 | 0 |
| session_momentum 15m | 30 | 30 | 30 | 0 | 0 | 0 | 0 |
| cvd_absorption 15m | 77 | 77 | 77 | 0 | 0 | 0 | 0 |
| cvd_absorption 1h | 22 | 22 | 22 | 0 | 0 | 0 | 0 |
| sr_flip 15m / 1h | 102 / 28 | 102 / 28 | all | 0 | 0 | 0 | 0 |
| failed_msb 15m / 1h | 8 / 9 | 8 / 9 | all | 0 | 0 | 0 | 0 |
| fib_pullback 15m | 85 | 93 | 85 | 0 | 0 | 0 | 8 |
| fib_pullback 1h | 23 | 24 | 23 | 0 | 0 | 0 | 1 |
| escalation 15m | 28 | 96 | 28 | 0 | 0 | 0 | 68 |
| escalation 1h | 0 | 6 | 0 | 0 | 0 | 0 | 6 |
| volume_fvg 15m | 16 | 19 | 0 | 15 | 1 | 0 | 3 |
| volume_fvg 1h | 4 | 5 | 0 | 3 | 1 | 0 | 1 |
| funding_cvd_fade 1h (bt 15m) | 3 | 34 | 0 | 0 | 1 | 2 | 33 |
| rsi_events 5m | 461 | 143 | 77 | 0 | 1 | 383 | 65 |
| rsi_events 15m | 147 | 80 | 21 | 0 | 12 | 114 | 47 |
| rsi_events 1h | 28 | 17 | 3 | 0 | 0 | 24 | 14 |
| malkan_bull / bear 1h | 0 / 0 | 0 / 0 | - | - | - | - | - (rare; parity untested) |
| rsi_divergence 1h, bb_top_reversal 15m, wlow 1h | 17, 70, 1 | none located | - | - | - | - | - |

Examples (entry-close ms, side) are in `out/parity_result.json` "examples" (5 per class per layer).
Live-only RSI by event: 5m cross 261, failure 85, rejection 36, support 1; 15m cross 80, failure 20, rejection 12, support 2; 1h cross 16, failure 5, rejection 3. A further 265/90/12 `cross` alerts per tf are unmapped and rejected by auto_trader (`unmapped rsi:cross`).
Backtest-only RSI = rejection@60 (live never watches level 60) plus, on 15m, support@40 at tol 1.0: all but 2 are visible in the live 99-bar window, so it is a rule difference, not a window effect. Escalation backtest-only: 47 of 68 (15m) and 6 of 6 (1h) need more than 99 bars of history; the other 21 are visible in a 99-bar window but not emitted (SUSPECTED freshness/dedup gate, not traced). fib_pullback: 7 of 8 (15m) and 1 of 1 (1h) need longer history.

## 5. Findings
| ID | Sev | Status | Evidence | Size | Fix | Card |
|---|---|---|---|---|---|---|
| T09-F1 | S1 | CONFIRMED | live_layers.py:61 `side = "short" if closes[start] > mid else "long"`; run_backtest.py run_fvg 'bounce' = long when closes[start] > mid. docstring (live_layers.py:43) says "Side as in the backtest". test_replay_signals_match_backtest | 0 of 24 matched signals have the same side (18 side-differ, 2 off by one bar, 4 backtest-only) | pick the reading the verdict used; both readings were "no edge" (FABIO_L1_REPORT.md:49-58), so either is untested at fee-net | desk post --target CLAUDE |
| T09-F2 | S1 | CONFIRMED | auto_trader.py:69-75, 439-444; run_rsi_backtest.py:42-44; run_cc_setups.py:170; fabio/run_backtest.py:43; run_t055.py:86-99 | no layer is traded with the exit it was tested with (section 6) | per-layer bracket or label testnet as SAMPLING only (already labelled bracket_source) | desk post --target CLAUDE |
| T09-F3 | S1 | CONFIRMED | live_layers.py:146-166, auto_trader.py DEFAULT layer_rules `rsi:support/rejection/cross` | RSI alerts traded that no backtest covered: 5m 384 of 461, 15m 126 of 147, 1h 25 of 28 | trade only support@40 long (+ tested rejection@60), or backtest failure/cross/rejection@40 first | desk post --target CLAUDE |
| T09-F4 | S2 | CONFIRMED (count) / SUSPECTED (cause of 21 escalation) | window 99 bars (live_runner_cli.py:531 limit 100) vs 1,500-2,000 backtest | escalation 15m: 68 of 96 backtest signals never fire live; fib_pullback 15m 8 of 93 | fetch more bars for swing layers | raw card |
| T09-F5 | S2 | CONFIRMED | run_t055.py:86-90 vs live_runner_cli.py:485 | funding_cvd_fade verdict was on 15m bars; live runs 1h: 0 of 34 signals coincide | backtest at 1h or run live at 15m | raw card |
| T09-F6 | S3 | CONFIRMED | live_layers.py:133 events carry entry_price/stop | cc live ignores the setup stop and entry (market, 1%) | use the event stop | with F2 |
| T09-F7 | S3 | CONFIRMED | live_layers.py:59 `range(start, ...)` vs run_fvg `range(start+1, ...)` | 2 of 24 fvg signals one bar earlier live | align | with F1 |

Positive: turn_of_candle, session_momentum, cvd_absorption, sr_flip, failed_msb signals are bit-for-bit the same bars and sides live and in the backtest (0 differences in 3,200+ signals).

## 6. Exits and the 97% time exits
Live rule (position_manager.py:560 time exit after `max_hold_s`; auto_trader.py:443 `max_hold_minutes = 8 * tf minutes`; plan validity `hours` only gates entry, executor.py:280): stop 1%, target 2%, close at market after 8 bars of the signal tf.

Share of exits on DEV BTCUSDT 1m bars, entries every 5-60 min, both sides (`out/exit_result.json`):
| tf | hold | stop | target | time |
|---|---|---|---|---|
| 1m | 8 min | 0.7% | 0.1% | 99.2% |
| 5m | 40 min | 5.2% | 0.9% | 93.9% |
| 15m | 2 h | 14.9% | 3.8% | 81.4% |
| 1h | 8 h | 37.8% | 13.8% | 48.4% |

Weighted by the accepted alert mix of the 30-day replay (1m 2,910, 5m 461, 15m 565, 1h 139): 94.4% time exits, against 97% observed on testnet (MORNING_REPORT). turn_of_candle alone is 71% of the alerts, and it holds 8 minutes against a 1% stop. The rest of the gap to 97% is within what one-position-per-account and size caps change in the mix (not measured here: no ledger read).
Backtest exits instead: RSI family 1%/2%/100 bars (15m: 16.7% time, 1h: 0.7% time, same arithmetic); cc setups structure stop + R target + 1,440 1m bars; Fabio and T055 pure fixed-horizon returns (no stop, no target). So the 8-bar bracket is a new exit rule that was never backtested.

## 7. Leads from section 1e
None owned by T09.

## 8. Not checked
- session_levels, candle_close, levels_confluence (need 2.9k-24.5k 1m bars of history per step through HistoryStore; studies already FAIL or footprint-window only), fabio v3_grid (needs footprint columns, which exist only 2024-12-02..2025-03-31, outside DEV): BLOCKED, skipped on purpose.
- rsi_divergence, bb_top_reversal, wlow_bounce: replayed (17, 70, 1 live signals) but no backtest twin located in the time budget: BLOCKED.
- malkan: zero events on both sides in 30 days; parity not demonstrated.
- No VALIDATION/HOLDOUT, no footprint window read (no exposure-ledger row needed).
- Live execution fills, fees, Deribit price vs Binance price: not in scope.

## 9. Decisions taken
- DECISION (OURS): the 30 days are drawn with seed 20261016 from the top-30 pools of trend, quiet and high-range DEV days (first 30 days skipped).
- DECISION (OURS): the "deployed" sha is the main checkout branch tip `4662684a3d` (the `.mts_live` marker is an empty file and `git -C` into the live tree is not allowed for a worktree agent); layers/ and execution/ are identical to the replayed HEAD.
- DECISION (OURS): signals are compared on entry-close time (bar open + tf), so studies run on another tf (session_momentum 5m, funding 15m) compare on one clock.
- DECISION (OURS): RSI backtest side uses the D3 chosen tolerances (15m 1.0, 1h 0.5 for 40 and 1.5 for 60; 5m 0.5 assumed).
- DECISION (OURS): the exit table is signal-independent (entries on a grid), since the layers have no stop or target of their own.

## 10. Bridge log
No bridge used (local replay only).

## 11. Handover
1. Top fix: volume_fvg side (live_layers.py:61) and the RSI event set (live_layers.py:146-166), both on the testnet decision path: post to Claude.
2. Test that proves it: `scripts/T09/test_layer_signal_parity.py` (move the layer out of KNOWN_DIVERGENT once it matches).
3. Risk: changing the side or exit changes which trades the testnet samples; the 20 pre_pipeline_sources have no positive OOS verdict anyway.
4. Rerun after: `python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T09/parity_core.py --force` then `exit_analysis.py`.
5. Raw cards for F4 and F5; F1-F3 go to the desk (CLAUDE).
