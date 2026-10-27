# Layer reality, 2026-10-25 (read-only Agent over files on trunk; nothing run; unverified items at the end)
"Live" = wired on testnet, not promoted (`promoted_setups.json` ships EMPTY, PROMOTION_PIPELINE.md:3). DEV = 2022..2024-06.
**No layer is AHEAD**: none has a positive fee-net DEV result ready to trade. Counts: LAGGING-BUILD 2, LAGGING-TEST 7, LAGGING-PARITY 2, DEAD 8.

| Layer | Class | Where it stands (source) | Blocker | Open cards |
|---|---|---|---|---|
| Tom (old BTC encoding) | DEAD; v2 LAGGING-BUILD | net -0.30 R holdout -0.32 R n=254 (LAYERS.md:21,23); 26 of 84 transcripts never extracted, 32 V1 extracts fail the quote check (REBUILD_PLAN:27) | Tom v2 being redefined (LAYERS.md:13) | tom-btc-encode/-dev-backtest/-eye-read blocked; tom-btc-validation refined |
| Fabio (cvd_absorption, escalation, volume_fvg, v3) | DEAD encodings; LAGGING-PARITY | v3 OOS 79 trades -0.1038 R; cvd identical live/test; escalation misses 68 of 96; fvg side inverted 0/24 (T09:38-64) | fabio v2 spec waits for ledger repairs | t09-f1, t09-f4, fabio-layer-v2-spec (blocked) |
| CryptoCred (sr_flip, fib_pullback, failed_msb) | DEAD as tested; exits LAGGING-PARITY | FAIL after trade-through rerun (LAYERS.md:99); stop/target unsourced (B143); 15m never backtested; live ignores setup stop | unsourced stop and target | none |
| RSI 40/60 levels (Malkan) | LAGGING-PARITY | live trades events no backtest covered (384 of 461 on 5m); 1h support PBO 0.030, rest 0.39-0.91 (LAYERS.md:88) | live event set differs from tested set | t09-f3 (ready), rsi-cross-unmapped, malkan cards |
| RSI divergence | DEAD | 31 of 32 net negative (LAYERS.md:85) | - | none |
| Kurisko Quad Rotation | LAGGING-TEST | fee 2.1-2.3 R on 1m, 0.60-0.79 R on 5m; nothing frozen | stops too narrow for 14 bp round trip | kurisko-dev-event-study (refined) |
| Krown | LAGGING-TEST | 127 rules from 16 of 20 videos, quote gates pass; detectors S1-S9, 49 tests; `enabled:false`; no DEV event study; recall check FAIL 3 of 12 | needs DEV study; HTF context role | krown-dev-event-study, krown-data-cme-btc-volume, confluence-s3/s4/s5 |
| WaveTrend | LAGGING-TEST | W01-03, W09 FAIL; W04-08 INCONCLUSIVE; none passes gross screen | divergence detector wrong (W07/W08 invalid) | wavetrend-c1-v2 (p1, refined) |
| Habib | LAGGING-BUILD | candle fade FAIL (n 4..2,386); plan levels NOT_IN_DATA | needs his typed level prices | habib-holdout-prereg-draft (ready) |
| Levels-confluence | DEAD on DEV, provisional | robust arm -0.090 R, frozen -0.039 R (n 772); VALIDATION never read | validation read | lc-validation, sim-dashboard-v1 |
| Funding/CVD fade | DEAD | OOS net -0.0453%; live 1h vs test 15m, 0 of 34 coincide | tf mismatch | positioning-c1-prereg-no-source (raw) |
| Pitchfork | LAGGING-TEST | detector + unit tests; studies span 2020-2026 not DEV-only; no VERDICTS row | DEV-only rerun | none |
| Trend-line | LAGGING-TEST | 43-parameter contract; count-only 3 of 18 cells powered; audit FIX-FIRST; not in layer_index/wiring_registry | critical gaps, 0 of 40 blind marks | trendline-v11-detector-fixes, -count-only-v2, -audit-gaps-disposition |
| session_momentum, turn_of_candle | DEAD (parity good) | signals bit-for-bit; turn_of_candle = 71 % of live alerts; exits differ | - | none |
| session levels, candle_close, wlow_bounce, bb_top_reversal, fabio v3_grid | DEAD (provisional) | exploratory negative/inconclusive (LAYERS.md:134,153); parity not diffed | parity | t02-f3-fixtures (Codex) |
| Cross-guidance, volume, candle patterns, ma_daily, bigtrade | DEAD | no cell survives; volume HOLDOUT sealed | - | pooled-short-lookback-trend (blocked) |
| Callers (Qriptal, RLinda, Bennett, Crypto Chase, Roman) | LAGGING-TEST | ingestion unfinished; 67.1 % self-reported wins unverified | ingestion | analyst-ingest-roman-x (ready) |

## System-wide facts
- 94 % of live exits are time exits; the 1 %/2 %/8-bar bracket on every layer was never backtested (T09:3-5,86). Live-vs-test numbers are not comparable for any layer.
- Gate board: Tom, Fabio, Malkan, Krown all at G2; no gate moved in 24 h (STATUS.md:36).
- sim_desk wires only levels, RSI, WaveTrend (PLUGIN.md). `_catalogue.json` marks levels_ladder and wavetrend_atlas FAILED.
- VERDICTS.csv has one PASS: carry_basis (n 911, +0.042 %), not a layer, not live; report unread.

## Integration steps a lagging layer must pass (stitched from LAYER_REBUILD_PLAN s2, PRE_REG_TEMPLATE, PROMOTION_PIPELINE, QUICK_ANSWERS:24, PROJECT_VISION:223-262, PLUGIN.md; no single "guidelines" file: NOT_FOUND)
1 G0/G1 sources on disk, extraction with verbatim quotes passing verify_extract_quotes.py. 2 G2 setup catalogue (entry/stop/target in the trader's words, NOT STATED where silent). 3 G3 two readers mark blind on BTC charts (READER_PROTOCOL.md).
4 G4 encode; recall and fire rate must pass before any P&L. 5 Label every parameter SOURCED/OURS; tune on DEV only. 6 Pre-register (12-item template, count-only power check with prereg_gate.py).
7 G5 DEV event study, fee-net, same-window placebo, every variant in the trial ledger (can run as one sim_desk `studies/<id>.py`). 8 Record: layer_map.json + VERDICTS.csv, make_layers_md.py, layer_index.json + wiring_registry.json.
9 One VALIDATION read, then one holdout read, each logged once. 10 Live code with a parity test (T09 test_layer_signal_parity.py), the tested exit not the generic bracket, tests for restart/reset, non-trade balance moves, API errors, fail-closed.
11 Promotion: promote.py check (fee-net OOS > 0, CI low > 0, n >= 30), then register --mode shadow, testnet only with size_overrides. 12 Confluence: a layer gates another only after passing S3 alone.

## Not verified
Live runner changes since T09 (replayed code at 4662684a3d); lc-validation runs since 2026-10-21; fee-net n/mean R for Fabio and CryptoCred L1; numbers in tom-btc lab results (80 charts).
