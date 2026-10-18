# LAYERS - one index per layer family (generated; do not hand-edit)

Read this before touching any layer (Claude and Codex). Regenerate: `python scripts/dev/make_layers_md.py` (tasks.py does it on
every card change). Pointers: `layer_index.json`; layer status and backtests: `layer_map.json`; cards: `system/tasks/`.
Rules: no fixed core; layers may combine or filter each other, results decide (CLAUDE.md, 2026-10-13). A new backtest is a row in
`layer_map.json` (it then shows here); a new layer joins a family in `layer_index.json`; a new card names `--layer <family>`.

Families: tom = Tom (order flow + volume profile) | fabio = Fabio (order-flow layer) | guidance = Tom/Fabio cross-guidance (BB, LVN, regime filters) | rsi = RSI / Malkan / Kurisko | cryptocred = CryptoCred setups | positioning = Positioning (funding, OI, whale / FlowHorse) | session_timing = Session / timing (session levels, turn of candle, session momentum) | volume_candles_ma = Volume, candle patterns, daily MA setups, bigtrade | live_engine = Live engine, execution and live-market reads (feeds every layer) | callers = Callers (posted trade calls: Qriptal) | krown = Krown (TA 101: zones, volume, candles, averages, ranges)

## Tom (order flow + volume profile) (`tom`)
- Status: Tom on BTC with our own judgement (operator 2026-10-13). DAX chain held, no FDAX data bought (q11). The old BTC encoding stays stopped.
- Tracks: Claude (spec/build), Codex lab (audits, DAX harness)
- Layer `tom_core`: STOP: do not backtest or tune the current BTC encoding (tom_transfer ROADMAP section 2); being redefined as Tom v2 | module src/main/java/datafeed/SetupCandidatesBuilder.java; backtest/verdict.py; backtest/tom_bt.py
- Layer `tom_proofs`: book_imbalance never counts in historical snapshots (no raw source); P06 volume spike is NO-SOURCE | module SetupCandidatesBuilder.java (proof flags)
- Layer `tom_vp_pivot`: closed: no anchor beats placebo | module backtest/vp_pivot_probe.py (FORMULAS 18)
- Backtests (layer_map.json, newest first):
  - 2026-10-11 `TOM-DIAG-BTC`: descriptive only; no rule change | `MyTradingSys/research/tom_transfer_2026-10-11/DIAG_BTC.md`
  - 2026-10-10 `DAX-SMOKE`: SMOKE: pipeline test, not a result; full dev + holdout run is Q7 | `MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md`
  - 2026-10-09 `TOM-VP-PHASE2`: no anchor has an edge; 46/48 real-minus-placebo CIs straddle 0; every year negative | `MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md`
  - 2026-10-09 `VP-PIVOT-P2`: negative net R; no level beats placebo | `MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md`
  - 2026-10-07 `TOM-CORE-1007`: no edge: gross -0.15 R, net -2.91 R; holdout -2.80 R (mechanical: R tiny after floor removal) | `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06.md`
  - 2026-10-07 `TOM-CORE-BT`: no edge shown; fees make it clearly negative | `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06_full.md`
  - 2026-09-30 `TOM-CORE-0929`: no edge: gross -0.07 R, net -0.30 R, holdout net -0.32 R (n=254) | `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md`
- Spec / sources: `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md`; `MyTradingSys/research/tom_transfer_2026-10-11/ROADMAP.md`; `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md`; `MyTradingSys/research/TOM_VERBATIM_INDEX.md`
- Code: `src/main/java/datafeed/SetupCandidatesBuilder.java`; `MyTradingSys/backtest/tom_dax_bt.py`; `MyTradingSys/backtest/verdict.py`
- Ledger: `MyTradingSys/research/tom_transfer_2026-10-11/TOM_TRADE_LEDGER.csv`; `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LEDGER_CANONICAL_GROUPS.csv`
- Other results: `MyTradingSys/research/tom_transfer_2026-10-11/RECALL_DAX.md`; `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-tom-ledger-frames.md`
- Roadmap: `MyTradingSys/research/tom_transfer_2026-10-11/ROADMAP.md`; `MyTradingSys/research/tom_transfer_2026-10-11/PRE_REG_DAX.md`
- Codex lab reports (newest 4 of 18): `MyTradingSys/research/layer_lab/reports/2026-10-15_tom-btc-event-study.md`; `MyTradingSys/research/layer_lab/reports/2026-10-15_gap-g4-through-ticks-flag.md`; `MyTradingSys/research/layer_lab/reports/2026-10-14_tom-v2-btc-min-stop-width.md`; `MyTradingSys/research/layer_lab/reports/2026-10-14_tom-btc-event-study.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `rv02-fix-dax-full-dev-authorization` ready p1 SONNET: RV02 R3: require complete DAX sampling and bind holdout authorization
  - `rv02-fix-dax-producer-data-binding` refined p1 SONNET: RV02 R4: reject DAX snapshots made from different execution data
  - `tom-btc-eye-read` blocked p1 SONNET: Tom on BTC T3: eye read of the 80 lab charts by two readers (Claude + Jis), blind; agreement per Tom concept
  - `tom-profile-shape-parity` blocked p1 CODEX: Tom v2: basis-free profile shape parity on the T1/T2 frames (decides the DAX PROFILE arm)
  - `gap-g6-trial-ledger` ready p2 CODEX: Gap G6: append-only research/TRIAL_LEDGER.csv builder + holdout-read log (no verdicts changed)
  - `indicator-values-multi-model-audit` ready p2 SONNET: Audit our indicator values with fresh eyes: random sample recomputed blind by GPT, DSA, Haiku, Sonnet and Opus
  - `tom-btc-dev-backtest` raw p2 CODEX: Tom on BTC T6: DEV backtest + adjustments (both fills, maker vs taker entry, management arms) - every variant 
  - `tom-btc-encode` raw p2 CODEX: Tom on BTC T5: encode the concepts that separated into a flag-gated BTC detector (entry paths A1-A3, stop at t
  - `tom-btc-validation` raw p2 DSA-NUC: Tom on BTC T7: VALIDATION read once (2025-04..2025-06) of the frozen DEV config
  - `tom-check-set-find-frames-only-tom-trade` refined p2 SONNET: Tom check set: find frames-only Tom trade recaps and log entry/stop/target without reading captions (check set
  - `tom-dax-backtest` ready p2 SONNET: Untuned Tom backtest on DAX vs matched-proof BTC rerun
  - `tom-encode-fade-entry-paths` ready p2 SONNET: Tom v2: encode fade entry paths A2 (pullback) and A3 (range break) with one re-entry per session
  - `tom-encode-fade-profile-proofs` refined p2 SONNET: Tom v2: encode the PROFILE arm of the fade (thin top, failed P breakout, lower b-shape)
  - `tom-ledger-add-the-losing-first-attempts` refined p2 SONNET: Tom ledger: add the losing first attempts Tom states but the ledger lacks (S1, S6 pre-session stops)
  - `tom-probe-prereg` refined p2 SONNET: Pre-register the surviving S/Q/M/F arms and write their runner card
  - `tom-short-coverage-above-vah` raw p2 SONNET: Tom short coverage on trend-down days: no candidate above VAH, ct_short at VAH killed by POC-only target (2026
  - `tom-btc-other-setups` blocked p3 CODEX: Tom on BTC T8: chart lab + event study for his other trade types (trend continuation pullback to value/VWAP, b
  - `tom-cvd-aligned-direction-blind` raw p3 SONNET: Tom: SetupCandidatesBuilder cvdAligned is direction-blind (SetupCandidatesBuilder.java:600 counts it for longs
  - `tom-ctlong-zone-lost-state` raw p4 SONNET: Tom: ct_long/ct_short at a zone price price has already passed stays a live candidate (no zone-lost state, sub
  - `tom-v2-btc-min-stop-width` blocked p5 CODEX: Tom v2: minimum stop width gate for BTC replays (noise unit N5 and fee floor)
  - `tom-v2-dax-dev-backtest` blocked p5 SONNET: Tom v2: DAX dev backtest of the fade under the part B protocol (both fills, session null)

## Fabio (order-flow layer) (`fabio`)
- Status: v3 tried 2026-10-04: OOS FAIL (only model C evaluable, 79 trades, mean -0.1038R); holdout 2026-06-26.. NOT read for Fabio (P2_FABIO_V3_HOLDOUT_STATUS.md, B147); ledger audit FIX-FIRST; being redefined as Fabio v2 (waits on ledger repairs).
- Tracks: Claude (spec/ledger), Codex lab (audits)
- Layer `fabio_cvd_absorption`: L1 no edge / insufficient n | module backtest/layers/fabio/fabio_cvd_absorption.py
- Layer `fabio_escalation`: L1 no edge / insufficient n | module backtest/layers/fabio/fabio_escalation.py
- Layer `fabio_volume_fvg`: L1 no edge | module backtest/layers/fabio/fabio_volume_fvg.py
- Layer `fabio_v3`: tried 2026-10-04; encoding being redefined (Fabio v2) | module backtest/layers/fabio/fabio_v3*.py; run_v3_l3.py
- Layer `fabio_of`: insufficient n; legacy fee pair | module backtest/layers/fabio/fabio_of_model.py; orderflow_bars.py
- Backtests (layer_map.json, newest first):
  - 2026-10-14 `PRICE-CVD-DIV-1M5M-20261014`: NEGATIVE: CVD divergence adds nothing over price alone on 1m/5m | `MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md`
  - 2026-10-09 `FIRES-B1`: parity PASS on spot rerun | `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md`
  - 2026-10-06 `FABIO-OF`: no edge / insufficient n (stands under correct fees; numbers not reusable) | `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md`
  - 2026-10-04 `FABIO-V3`: not recorded in map | `MyTradingSys/research/fast_track_2026-09-27/bt_runs/TRIAL_REGISTRY.csv`
  - 2026-09-27 `L1-FABIO`: no edge / insufficient n (rule: OOS n>=30, net>0, PBO<0.5) | `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md`
- Spec / sources: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md`; `MyTradingSys/research/fast_track_2026-09-27/FABIO_RULEBOOK.md`; `MyTradingSys/research/fast_track_2026-09-27/FABIO_TRADE_MODEL.md`; `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md`
- Code: `MyTradingSys/backtest/layers/fabio/fabio_v3.py`; `MyTradingSys/backtest/layers/fabio/fabio_of_model.py`; `MyTradingSys/backtest/layers/fabio/run_v3_l3.py`
- Ledger: `MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.csv`; `MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.md`
- Other results: `MyTradingSys/research/P2_FABIO_V3_HOLDOUT_STATUS.md`; `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-fabio-ledger-frames.md`; `MyTradingSys/research/orderflow_views_2026-10-14`
- Roadmap: `MyTradingSys/research/tom_transfer_2026-10-11/ROADMAP.md`
- Codex lab reports (newest 3 of 3): `MyTradingSys/research/layer_lab/reports/2026-10-13_rv05-fabio-ledger-frame-pass.md`; `MyTradingSys/research/layer_lab/reports/2026-10-13_lab-audit-fabio-ledger-frames.md`; `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-fabio-ledger-frames.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `fabio-xuyq-asr-extract` ready p2 JIS-NB: Fabio xUyqIjCfZzg: finish ASR transcription (JIS-NB, resumable) then canonical transcript + V2 extract + FAB c
  - `rv05-h2-position-line-evidence` ready p3 SONNET: RV05 H2: read position lines and stop prices before applying existing Fabio entry repair
  - `rv05-h3-outcome-evidence` refined p3 SONNET: RV05 H3: incorporate partial stop coverage evidence into existing F13 outcome repair
  - `fabio-ledger-get-9i5vtvwsmbk-f398-not-av` ready p4 SONNET: Fabio ledger: get 9I5vTvwsMBk (f398 not available; try another format/client) and read it for trades
  - `fabio-layer-v2-markets` refined p5 OPUS: Fabio layer v2 spec, part B: data plan per market, cost, stop width, build + recall cards (Opus research)
  - `fabio-layer-v2-spec` blocked p5 OPUS: Fabio layer v2 spec, part A: setup families + sourced rules from his ledger (Opus research)

## Tom/Fabio cross-guidance (BB, LVN, regime filters) (`guidance`)
- Status: Q33 found no surviving cell: do not wire cross-guidance (Q34 skipped).
- Tracks: Claude
- Layer `bb_lvn_triggers`: no cell survives | module research/tom_fabio_guidance_2026-10-12/matrix_q33.py
- Backtests (layer_map.json, newest first):
  - 2026-10-12 `Q33`: no cell survives (smallest q 0.62); do not wire cross-guidance | `MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md`
- Spec / sources: `MyTradingSys/research/tom_fabio_guidance_2026-10-12/GUIDANCE_AUDIT.md`; `MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md`
- Code: `MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py`; `MyTradingSys/backtest/layers/test_layer_boundaries.py`
- Open cards: none

## RSI / Malkan / Kurisko (`rsi`)
- Status: 40/60 levels: tolerance study done; divergence: no edge on any TF.
- Tracks: Claude
- Layer `rsi_levels`: D3 tolerance study done | module backtest/layers/rsi; rsi_events
- Layer `rsi_divergence`: no edge, all TFs | module backtest/layers/rsi/run_divergence_mtf.py
- Backtests (layer_map.json, newest first):
  - 2026-10-09 `RSI-DIV-MTF`: no edge on any timeframe that reached 300 events; 31 of 32 net negative; 6h and 2d leads have n 6-54 | `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md`
  - 2026-10-09 `FIRES-B1`: parity PASS on spot rerun | `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md`
  - 2026-10-07 `MARKET-GUIDE`: table in report not read for this map | `MyTradingSys/research/MARKET_GUIDE_RESULTS_2026-10-07.md`
  - 2026-09-27 `L1-D3`: mixed: 1h support PBO 0.030, everything else PBO 0.39-0.91 | `MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md`
- Spec / sources: `MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md`; `MyTradingSys/backtest/layers/FORMULAS.md`
- Code: `MyTradingSys/backtest/layers/rsi/malkan_40_60.py`; `MyTradingSys/backtest/layers/rsi/malkan_mtf.py`
- Other results: `MyTradingSys/research/rsi_divergence_mtf_2026-10-09`
- Codex lab reports (newest 1 of 1): `MyTradingSys/research/layer_lab/reports/2026-10-17_malkan-hindi-rows-gpt-read.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `indicator-values-multi-model-audit` ready p2 SONNET: Audit our indicator values with fresh eyes: random sample recomputed blind by GPT, DSA, Haiku, Sonnet and Opus
  - `malkan-captions-fetch-noauth` ready p2 HAIKU: Malkan: fetch captions for the 12 ranked-top videos only (video_priority_2026-10-15), no cookies, spaced retri
  - `malkan-home-fit-audit` ready p4 SONNET: Home-fit audit of the Malkan RSI layer against the readiness checklist

## CryptoCred setups (`cryptocred`)
- Status: S/R flip + fib pullback + failed MSB FAIL after trade-through rerun; stop buffer unsourced (B143).
- Tracks: Claude
- Layer `cryptocred`: adapter + stop sweep run | module backtest/layers/cryptocred/
- Backtests (layer_map.json, newest first):
  - 2026-10-09 `BIGTRADE-EXIT`: first row negative both splits; full table not read for this map | `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md`
  - 2026-10-09 `FIRES-B1`: parity PASS on spot rerun | `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md`
  - 2026-09-27 `L1-D3`: mixed: 1h support PBO 0.030, everything else PBO 0.39-0.91 | `MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md`
- Spec / sources: `MyTradingSys/items/B143_cryptocred_stop_buffer_and_target_unsourced.md`; `MyTradingSys/backtest/layers/FORMULAS.md`
- Code: `MyTradingSys/backtest/layers/cryptocred`
- Other results: `MyTradingSys/research/cryptocred_stop_2026-10-10`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `cryptocred-prereg-4h-1d` refined p3 SONNET: CryptoCred: pre-registration for the 4h/1d redesign (items 6/8/11/12)

## Positioning (funding, OI, whale / FlowHorse) (`positioning`)
- Status: T055 C1 FAIL; OI/long-short unused as filters.
- Tracks: Claude
- Layer `funding_cvd_fade`: FAIL, closed | module backtest/layers/positioning/funding_cvd_fade.py
- Layer `oi_delta`: descriptive study | module research/OI_DELTA_4STATE_BACKTEST_2026-09-21.md
- Backtests (layer_map.json, newest first):
  - 2026-10-14 `PRICE-CVD-DIV-1M5M-20261014`: NEGATIVE: CVD divergence adds nothing over price alone on 1m/5m | `MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md`
  - 2026-09-29, rerun 2026-10-07 (full funding) `T055-C1`: FAIL (rerun OOS net -0.0453%, Sharpe -0.035); closed | `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md`
  - 2026-09-21 `OI-DELTA`: descriptive; no verdict line in the head of the file | `MyTradingSys/research/OI_DELTA_4STATE_BACKTEST_2026-09-21.md`
- Spec / sources: `MyTradingSys/research/whale_positioning_evidence_2026-09-12.md`; `MyTradingSys/backtest/layers/FORMULAS.md`
- Code: `MyTradingSys/backtest/layers/positioning`
- Other results: `MyTradingSys/research/OI_DIVERGENCE_V2_2026-10-10.md`; `MyTradingSys/research/OI_EVENT_STUDY_2026-10-10.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `positioning-home-fit-audit` ready p4 SONNET: Home-fit audit of the FlowHorse / whale positioning layer against the readiness checklist

## Session / timing (session levels, turn of candle, session momentum) (`session_timing`)
- Status: T055 C2/C3 closed; T087 failed prior-day-high fade FAIL.
- Tracks: Claude
- Layer `session_momentum`: FAIL, closed | module backtest/layers/session/session_momentum.py
- Layer `turn_of_candle`: no edge, closed | module backtest/layers/turn_of_candle/
- Layer `session_levels`: no edge | module research/t087_session_levels_2026-10-09
- Backtests (layer_map.json, newest first):
  - 2026-10-14 `LC-SIZING-QUICK-20261014`: EXPLORATORY NEGATIVE; full LC hypothesis untested | `MyTradingSys/research/levels_sizing_2026-10-14/REPORT.md`
  - 2026-10-14 `EUR-LOW-US-SWEEP-20261014`: EXPLORATORY NEGATIVE (short leg); long-after-reclaim untested | `MyTradingSys/research/eur_low_us_sweep_2026-10-14/RESULT.md`
  - 2026-10-09 `T087`: no edge (net -0.036%, t -1.72); EU-touch cells insufficient n | `MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md`
  - 2026-10-09 `FIRES-B1`: parity PASS on spot rerun | `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md`
  - 2026-09-29, rerun 2026-10-07 `T055-C2`: FAIL (rerun OOS net +0.0177%, Sharpe 0.0084, 1 of 2 years positive) | `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md`
  - 2026-09-29 `T055-C3`: NO EDGE (gross OOS about 0 at every horizon) | `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md`
- Spec / sources: `MyTradingSys/research/TURN_OF_CANDLE_ORIGIN_2026-10-09.md`
- Code: `MyTradingSys/backtest/layers/session`; `MyTradingSys/backtest/layers/session_levels`; `MyTradingSys/backtest/layers/turn_of_candle`
- Other results: `MyTradingSys/research/t087_session_levels_2026-10-09`; `MyTradingSys/research/eur_low_us_sweep_2026-10-14`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `eu-low-us-sweep-follow-ups-long-after-sw` ready p2 SONNET: EU-low/US-sweep follow-ups: long after sweep+reclaim (stability test), LTF RSI-divergence short from daily hig

## Volume, candle patterns, daily MA setups, bigtrade (`volume_candles_ma`)
- Status: No validated edge; volume HOLDOUT sealed; MA numbers NO-SOURCE.
- Tracks: Claude
- Layer `volume`: no validated edge; HOLDOUT sealed | module research/volume_2026-10-09
- Layer `candle_patterns`: pilot run | module research/candle_patterns_2026-10-04
- Layer `ma_daily`: NO-SOURCE (chatbot handoff numbers) | module research/setup_alpha_beta_2026-10-10/alpha_backtest.py
- Layer `bigtrade_fires`: fires + exit policies run, HOLDOUT unread | module backtest/bigtrade; research/bigtrade_2026-10-09
- Backtests (layer_map.json, newest first):
  - 2026-10-14 `CANDLE-CLOSE-DEV-20261014`: EXPLORATORY NEGATIVE; cycle outcomes untested | `MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md`
  - 2026-10-10 `ALPHA`: NO-SOURCE; A CAGR 20.5% maxDD 49% vs buy-and-hold 43.8% / 76.7%; not a result | `MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md`
  - 2026-10-09 `VOLUME`: no validated directional edge; volume gives intensity, not direction; 1 marginal DEV pass failed VALIDATION | `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md`
  - 2026-10-09 `BIGTRADE-EXIT`: first row negative both splits; full table not read for this map | `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md`
  - 2026-10-09 `BIGMOVES-A`: ground truth, no verdict | `MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md`
  - 2026-10-09 `FIRES-B1`: parity PASS on spot rerun | `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md`
  - 2026-10-09 `CAPTURE-MATRIX`: see report; SYNTHETIC variant is a tool fixture, not layer output | `MyTradingSys/research/bigtrade_2026-10-09/CAPTURE_MATRIX_SPOT.md`
  - 2026-10-09 `VOL-V1`: 0 pass triage | `MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md`
  - 2026-10-09 `VOL-V2`: 0 pass triage | `MyTradingSys/research/volume_2026-10-09/V2_DEV_RESULTS.md`
  - 2026-10-09 `VOL-V3`: INSUFFICIENT-N; candidate stays unvalidated | `MyTradingSys/research/volume_2026-10-09/V3_VALIDATION_RESULTS.md`
  - 2026-10-09 `VOL-V4`: NOT SUPPORTED | `MyTradingSys/research/volume_2026-10-09/V4_RESULTS.md`
  - 2026-10-07 `CANDLE-P1`: 1d engulfing rows read all FAIL; remaining rows and 1h table not read for this map | `MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md`
  - 2026-10-07 `MARKET-GUIDE`: table in report not read for this map | `MyTradingSys/research/MARKET_GUIDE_RESULTS_2026-10-07.md`
  - 2026-10-04 `CANDLE-D19`: NO-SOURCE; below buy-and-hold | `MyTradingSys/research/candle_patterns_2026-10-04/D19_4H_RESULTS.md`
  - 2026-10-04 `CANDLE-P0`: exploratory; no edge vs random null | `MyTradingSys/research/candle_patterns_2026-10-04/P0_RESULTS.md`
- Spec / sources: `MyTradingSys/backtest/layers/FORMULAS.md`
- Code: `MyTradingSys/backtest/bigtrade`
- Other results: `MyTradingSys/research/volume_2026-10-09`; `MyTradingSys/research/candle_patterns_2026-10-04`; `MyTradingSys/research/setup_alpha_beta_2026-10-10`; `MyTradingSys/research/bigtrade_2026-10-09`; `MyTradingSys/research/layer_lab/candle_close_2026-10-14`
- Codex lab reports (newest 3 of 3): `MyTradingSys/research/layer_lab/reports/2026-10-14_lab-candle-close-research.md`; `MyTradingSys/research/layer_lab/reports/2026-10-14_lab-candle-close-dev.md`; `MyTradingSys/research/layer_lab/reports/2026-10-14_candle-close-independent-audit.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `pooled-short-lookback-trend-tsmom-30d-sm` raw p3 DSA: Pooled short-lookback trend (TSMOM 30d, SMA50/100, 4h Donchian 20/10) on sealed 2025-07..2026-09 BTC holdout: 
  - `time-adjusted-volume-context-line-for-th` refined p3 SONNET: Time-adjusted volume context line for the live read (same-slot baseline, effort vs result, OI scope) as read-o
  - `fetch-ethusdt-perp-1h-klines-funding-202` raw p4 DSA: Fetch ETHUSDT perp 1h klines + funding 2020-2026 (fetch_binance_archive.py) and re-run research/published_stra
  - `funding-carry-with-real-spot-basis-margi` ready p4 SONNET: Funding carry with real spot basis, margin and borrow: net 15.4 -> 12.1 -> 6.2 %/yr decay in published_strats_

## Live engine, execution and live-market reads (feeds every layer) (`live_engine`)
- Status: Testnet HALT since 2026-10-12 09:46Z (executor fail_closed); supervisor clears it. Live-market screenshot reads file findings as task cards.
- Tracks: Claude (live reads on JIS-NB), supervisor for HALT/deploy
- Spec / sources: `MyTradingSys/methodology/live_session_protocol.md`; `MyTradingSys/methodology/screenshot_intake.md`; `MyTradingSys/system/DEPLOY_RUNBOOK.md`
- Code: `MyTradingSys/execution`
- Other results: `MyTradingSys/research/screenshots`
- Roadmap: `MyTradingSys/system/NEXT_SESSION.md`
- Codex lab reports (newest 1 of 1): `MyTradingSys/research/layer_lab/reports/2026-10-13_rv06-live-read-claims.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `indicator-values-multi-model-audit` ready p2 SONNET: Audit our indicator values with fresh eyes: random sample recomputed blind by GPT, DSA, Haiku, Sonnet and Opus
  - `state-code-accumulator-backfill` ready p2 JIS-NB: StateCodeEmitter: backfill session CVD/cum_pv/cum_vol after restart and WS reconnect, fail closed on backfill 
  - `identify-the-coinglass-net-delta-panel-u` raw p3 SONNET: Identify the CoinGlass Net Delta panel unit and scope: 4 reads in a row NOT_IN_DATA (8h 4.181K, 30m -8.366K, 1
  - `live-loop-timeouts-b191` ready p3 SONNET: Network: re-check live-loop timeouts after B191 plus wrapper priority and snapshot.cp (read-only report first)
  - `live-orderflow-state-line-1m-5m-15m-pric` ready p3 SONNET: Live read: one order-flow state line per TF (1m/5m/15m price swing vs Binance CVD swing vs OI change), descrip
  - `score-context-reads-automatically-carrie` refined p3 SONNET: Score context reads automatically: carried falsifier lines (HELD/BROKEN/UNTESTED) computed from klines at the 
  - `snapshot-vwap-anchor-label` ready p3 JIS-NB: MarketDataSnapshot: vwap_anchor_utc must be the UTC day start used by the VWAP, not today's NY open (audit M3)
  - `one-timeframe-map-for-the-whole-toolchai` ready p4 CODEX: One timeframe map for the whole toolchain: capture.TF_MINUTES lacked 8h (CoinGlass button) while holding 7h; g

## Callers (posted trade calls: Qriptal) (`callers`)
- Status: Score the posted calls on Binance klines before anything else (B162). Self-reported 67.1 % wins, avg win 3.99 %, avg loss 0.63 %: unverified.
- Tracks: Claude, Codex lab (scoring)
- Spec / sources: `MyTradingSys/items/B162_qriptal_signal_layer.md`
- Codex lab reports (newest 2 of 2): `MyTradingSys/research/layer_lab/reports/2026-10-14_qriptal-score-binance.md`; `MyTradingSys/research/layer_lab/reports/2026-10-13_qriptal-score-binance.md`
- Open cards: none

## Krown (TA 101: zones, volume, candles, averages, ranges) (`krown`)
- Status: Spec v0.2 + 120-rule ledger from 15 of 19 reachable TA 101 videos (14 TA + 1 fees). 4 videos blocked on YouTube captions (429). One structural stop (compression breakout), no stop distance or size rule: the rest is OURS. Not built, not backtested.
- Tracks: Claude (extraction, ledger, spec, detectors), DSA (data runs)
- Spec / sources: `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md`; `MyTradingSys/research/krown_ta101_2026-10-13/PRE_REG_KROWN.md`; `MyTradingSys/research/krown_ta101_2026-10-13/PROTOCOL.md`; `MyTradingSys/research/krown_ta101_2026-10-13/STATE.md`
- Code: `MyTradingSys/research/krown_ta101_2026-10-13/tools/build_ledger.py`; `MyTradingSys/research/krown_ta101_2026-10-13/tools/check_numbers.py`
- Ledger: `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv`; `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_CONSOLIDATED.md`; `MyTradingSys/research/krown_ta101_2026-10-13/MANIFEST.csv`
- Other results: `MyTradingSys/research/krown_ta101_2026-10-13/reflexivity_log.md`; `MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md`; `MyTradingSys/options/research/KROWN_FREE_VS_PAID.md`
- Roadmap: `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md`
- Codex lab reports (newest 1 of 1): `MyTradingSys/research/layer_lab/reports/2026-10-17_krown-catalogue-gpt-audit.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `krown-data-cme-btc-volume` raw p2 DSA: Krown CME BTC futures daily volume (public data only) as third volume arm
  - `krown-dev-event-study` blocked p2 SONNET: Krown DEV event study: hypotheses H-V1..H-T1, DEV only, fee-net, same-window placebo, power first; DONE when: 
  - `krown-recall-check` ready p2 SONNET: Krown recall check: verify his dated chart examples against klines, then detector recall and fire rate (PRE_RE
  - `krown-other-sources-event-study-videos` blocked p3 SONNET: Krown other sources: extract his daily BTC event-study videos and the CBP krown item with the V2 method (trigg
  - `krown-ta101-extract-remaining-10` ready p3 SONNET: Krown TA 101: get captions and extract the remaining 4 videos (ids in STATE.md); DONE when: 4 extracts pass bo

## Cross-cutting

- Every backtest row (layers on, params, verdict, report): MyTradingSys/system/layer_map.json (artifact: make_layer_map.py)
- Every trial count (multiple-testing ledger): MyTradingSys/research/fast_track_2026-09-27/bt_runs/TRIAL_REGISTRY.csv
- Formulas (canonical definitions): MyTradingSys/backtest/layers/FORMULAS.md
- Layer provenance (sourced vs NO-SOURCE parameters): MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md
- Codex layer lab deliveries and queue: MyTradingSys/research/layer_lab/INDEX.md (spec: system/LAYER_LAB.md)
- Work queue (relay Qn tasks): MyTradingSys/system/NEXT_SESSION.md; cards: python scripts/dev/tasks.py list
- Group-level project map (DATA/CORE/LAYR/EVID...): MyTradingSys/system/PROJECT_MAP.md
- Backtest pre-registration template and 12-point readiness checklist: MyTradingSys/backtest/PRE_REG_TEMPLATE.md
