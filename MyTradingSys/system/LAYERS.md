# LAYERS - one index per layer family (generated; do not hand-edit)

Read this before touching any layer (Claude and Codex). Regenerate: `python scripts/dev/make_layers_md.py` (tasks.py does it on
every card change). Pointers: `layer_index.json`; layer status and backtests: `layer_map.json`; cards: `system/tasks/`.
Rules: no fixed core; layers may combine or filter each other, results decide (CLAUDE.md, 2026-10-13). A new backtest is a row in
`layer_map.json` (it then shows here); a new layer joins a family in `layer_index.json`; a new card names `--layer <family>`.

Families: tom = Tom (order flow + volume profile) | fabio = Fabio (order-flow layer) | guidance = Tom/Fabio cross-guidance (BB, LVN, regime filters) | rsi = RSI / Malkan / Kurisko | cryptocred = CryptoCred setups | positioning = Positioning (funding, OI, whale / FlowHorse) | session_timing = Session / timing (session levels, turn of candle, session momentum) | volume_candles_ma = Volume, candle patterns, daily MA setups, bigtrade | live_engine = Live engine, execution and live-market reads (feeds every layer) | callers = Callers (posted trade calls: Qriptal, RLinda, Bennett, Crypto Chase, Roman) | krown = Krown (TA 101: zones, volume, candles, averages, ranges) | wavetrend = WaveTrend (LazyBear oscillator) | pitchfork = Pitchfork (Andrews / Schiff / Morge median line)

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
- Codex lab reports (newest 4 of 22): `MyTradingSys/research/layer_lab/reports/2026-10-19_tom-v2-btc-min-stop-width.md`; `MyTradingSys/research/layer_lab/reports/2026-10-18_tom-v2-btc-min-stop-width.md`; `MyTradingSys/research/layer_lab/reports/2026-10-18_tom-dax-naked-chart-crosscheck.md`; `MyTradingSys/research/layer_lab/reports/2026-10-18_gap-g6-trial-ledger.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `tom-btc-eye-read` blocked p1 SONNET: Tom on BTC T3: eye read of the 80 lab charts by two readers (Claude + Jis), blind; agreement per Tom concept
  - `indicator-values-multi-model-audit` ready p2 SONNET: Audit our indicator values with fresh eyes: random sample recomputed blind by Haiku and Sonnet, plus GPT and D
  - `review-ground-layer-youtube-strategy-and` ready p2 SONNET: Review Ground Layer YouTube strategy and execution priorities
  - `tom-btc-dev-backtest` blocked p2 CODEX: Tom on BTC T6: DEV backtest + adjustments (both fills, maker vs taker entry, management arms) - every variant 
  - `tom-btc-encode` blocked p2 CODEX: Tom on BTC T5: encode the concepts that separated into a flag-gated BTC detector (entry paths A1-A3, stop at t
  - `tom-btc-validation` refined p2 DSA-NUC: Tom on BTC T7: VALIDATION read once (2025-04..2025-06) of the frozen DEV config
  - `tom-probe-prereg` refined p2 SONNET: Pre-register the surviving S/Q/M/F arms and write their runner card
  - `tom-probe-runner` refined p2 SONNET: Run pre-registered Tom management arms on DAX and BTC
  - `tom-short-coverage-above-vah` raw p2 SONNET: Tom short coverage on trend-down days: no candidate above VAH, ct_short at VAH killed by POC-only target (2026
  - `lab-verify-trend-healthy-in-balance` refined p3 SONNET: LAB-VERIFY 10-18: how often trend_healthy is set inside a multi-day balance (DEV)
  - `multi-tf-bias-stack-one-written-rule-tha` refined p3 SONNET: Multi-TF bias stack: one written rule that forms bias from HTF location + LTF flow, tested on DEV (operator 10
  - `tom-btc-other-setups` ready p3 CODEX: Tom on BTC T8: chart lab + event study for his other trade types (trend continuation pullback to value/VWAP, b

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
  - `context-conditioned-session-flow-states` refined p2 SONNET: Context-conditioned session flow states: per-session price/delta/OI quadrant + sweep-reclaim, next-session out
  - `oi-pivot-reversal-probability-by-tf` raw p2 SONNET: Causal pivot-candidate study: P(reversal) per TF from OI slope flip + price/OI divergence + delta + location, 
  - `review-ground-layer-youtube-strategy-and` ready p2 SONNET: Review Ground Layer YouTube strategy and execution priorities
  - `rv05-h2-position-line-evidence` ready p3 SONNET: RV05 H2: read position lines and stop prices before applying existing Fabio entry repair
  - `rv05-h3-outcome-evidence` refined p3 SONNET: RV05 H3: incorporate partial stop coverage evidence into existing F13 outcome repair
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
- Code: `MyTradingSys/backtest/layers/rsi/malkan_40_60.py`; `MyTradingSys/backtest/layers/rsi/malkan_mtf.py`; `MyTradingSys/backtest/layers/kurisko/quad_rotation.py`; `MyTradingSys/backtest/layers/kurisko/stoch_core.py`
- Other results: `MyTradingSys/research/rsi_divergence_mtf_2026-10-09`
- Codex lab reports (newest 1 of 1): `MyTradingSys/research/layer_lab/reports/2026-10-17_malkan-hindi-rows-gpt-read.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `indicator-values-multi-model-audit` ready p2 SONNET: Audit our indicator values with fresh eyes: random sample recomputed blind by Haiku and Sonnet, plus GPT and D
  - `kurisko-dev-event-study` refined p2 SONNET: Kurisko Quad Rotation: DEV event study, fee-net, same-window placebo
  - `kurisko-prereg-fire-counts` refined p2 SONNET: Kurisko Quad Rotation: count-only pre-registration on BTC DEV 1m/5m (no outcomes)
  - `malkan-gfs-btc-htf-prereg` refined p2 SONNET: Malkan GFS on BTC 1D/4h: edge-before-extraction pre-registration and count/power gate before any further video
  - `review-ground-layer-youtube-strategy-and` ready p2 SONNET: Review Ground Layer YouTube strategy and execution priorities
  - `wavetrend-audit-c1-disposition` refined p2 SONNET: WaveTrend: state report and disposition of AUDIT_2026-10-18 C1 + control-arm + manifest findings
  - `malkan-w1hr-local-whisper-asr` ready p3 JIS-NB: Malkan W1HrDl70Lhk: local Whisper ASR on JIS-NB to recover Hinglish 5-Star RSI stop wording (no YouTube captio
  - `rsi-cross-unmapped-and-pivot-stack` raw p3 SONNET: RSI cross events are rejected as unmapped in the auto-trader (no layer_rules entry); and no layer stacks level
  - `malkan-prereg-dwm-equities` refined p4 SONNET: Malkan: pre-registration for the D/W/M equity home test (items 6/7/8/9/11/12, gates 0a/0f)

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
- Open cards: none

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
  - `positioning-c1-longwindow-count-power` ready p4 SONNET: Positioning C1 (NO-SOURCE): count-only events on the DEV window, fire rate, power, null spec (items 3/9/10/12)
  - `positioning-c1-prereg-no-source` raw p4 SONNET: Positioning C1: pre-registration labelled NO-SOURCE (items 1/6/8/9/11/12, gates 0a/0f)

## Session / timing (session levels, turn of candle, session momentum) (`session_timing`)
- Status: T055 C2/C3 closed; T087 failed prior-day-high fade FAIL.
- Tracks: Claude
- Layer `session_momentum`: FAIL, closed | module backtest/layers/session/session_momentum.py
- Layer `turn_of_candle`: no edge, closed | module backtest/layers/turn_of_candle/
- Layer `session_levels`: no edge | module research/t087_session_levels_2026-10-09
- Backtests (layer_map.json, newest first):
  - 2026-10-18 `EUR-LOW-US-SWEEP-FOLLOWUPS-20261018`: BLOCKED by power gate (A, B, C); legs stay open | `MyTradingSys/research/eur_low_us_sweep_followups_2026-10-18/RESULT.md`
  - 2026-10-14 `LC-SIZING-QUICK-20261014`: EXPLORATORY NEGATIVE; full LC hypothesis untested | `MyTradingSys/research/levels_sizing_2026-10-14/REPORT.md`
  - 2026-10-14 `EUR-LOW-US-SWEEP-20261014`: EXPLORATORY NEGATIVE (short leg); long-after-reclaim untested | `MyTradingSys/research/eur_low_us_sweep_2026-10-14/RESULT.md`
  - 2026-10-09 `T087`: no edge (net -0.036%, t -1.72); EU-touch cells insufficient n | `MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md`
  - 2026-10-09 `FIRES-B1`: parity PASS on spot rerun | `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md`
  - 2026-09-29, rerun 2026-10-07 `T055-C2`: FAIL (rerun OOS net +0.0177%, Sharpe 0.0084, 1 of 2 years positive) | `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md`
  - 2026-09-29 `T055-C3`: NO EDGE (gross OOS about 0 at every horizon) | `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md`
- Spec / sources: `MyTradingSys/research/TURN_OF_CANDLE_ORIGIN_2026-10-09.md`
- Code: `MyTradingSys/backtest/layers/session`; `MyTradingSys/backtest/layers/session_levels`; `MyTradingSys/backtest/layers/turn_of_candle`
- Other results: `MyTradingSys/research/t087_session_levels_2026-10-09`; `MyTradingSys/research/eur_low_us_sweep_2026-10-14`
- Open cards: none

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
  - `pooled-short-lookback-trend-tsmom-30d-sm` blocked p3 DSA: Pooled short-lookback trend (TSMOM 30d, SMA50/100, 4h Donchian 20/10) on sealed 2025-07..2026-09 BTC holdout: 
  - `time-adjusted-volume-context-line-for-th` refined p3 SONNET: Time-adjusted volume context line for the live read (same-slot baseline, effort vs result, OI scope) as read-o

## Live engine, execution and live-market reads (feeds every layer) (`live_engine`)
- Status: Testnet HALT since 2026-10-12 09:46Z (executor fail_closed); supervisor clears it. Live-market screenshot reads file findings as task cards.
- Tracks: Claude (live reads on JIS-NB), supervisor for HALT/deploy
- Spec / sources: `MyTradingSys/methodology/live_session_protocol.md`; `MyTradingSys/methodology/screenshot_intake.md`; `MyTradingSys/system/DEPLOY_RUNBOOK.md`
- Code: `MyTradingSys/execution`
- Other results: `MyTradingSys/research/screenshots`
- Roadmap: `MyTradingSys/system/NEXT_SESSION.md`
- Codex lab reports (newest 2 of 2): `MyTradingSys/research/layer_lab/reports/2026-10-18_one-timeframe-map-for-the-whole-toolchai.md`; `MyTradingSys/research/layer_lab/reports/2026-10-13_rv06-live-read-claims.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `review-statecode-backfill-gpt` ready p1 CODEX: GPT high cross-vendor code review of e4bcc09f: StateCodeEmitter kline backfill, fail-closed INVALID state, vwa
  - `indicator-values-multi-model-audit` ready p2 SONNET: Audit our indicator values with fresh eyes: random sample recomputed blind by Haiku and Sonnet, plus GPT and D
  - `state-code-accumulator-backfill` ready p2 JIS-NB: StateCodeEmitter: backfill session CVD/cum_pv/cum_vol after restart and WS reconnect, fail closed on backfill 
  - `live-loop-timeouts-b191` refined p3 SONNET: Network: re-check live-loop timeouts after B191 plus wrapper priority and snapshot.cp (read-only report first)
  - `live-orderflow-state-line-1m-5m-15m-pric` refined p3 SONNET: Live read: one order-flow state line per TF (1m/5m/15m price swing vs Binance CVD swing vs OI change), descrip
  - `score-context-reads-automatically-carrie` refined p3 SONNET: Score context reads automatically: carried falsifier lines (HELD/BROKEN/UNTESTED) computed from klines at the 
  - `snapshot-vwap-anchor-label` ready p3 JIS-NB: MarketDataSnapshot: vwap_anchor_utc must be the UTC day start used by the VWAP, not today's NY open (audit M3)
  - `one-timeframe-map-for-the-whole-toolchai` ready p4 CODEX: One timeframe map for the whole toolchain: capture.TF_MINUTES lacked 8h (CoinGlass button) while holding 7h; g

## Callers (posted trade calls: Qriptal, RLinda, Bennett, Crypto Chase, Roman) (`callers`)
- Status: Score the posted calls on Binance klines before anything else (B162 + multi-analyst ingestion). Self-reported 67.1 % wins, avg win 3.99 %, avg loss 0.63 %: unverified. Multi-provider parser + kline scorecard built (2026-10-18); 4 ingestion cards ready.
- Tracks: Claude, Codex lab (scoring)
- Spec / sources: `MyTradingSys/items/B162_qriptal_signal_layer.md`; `MyTradingSys/research/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md`; `MyTradingSys/research/analysts/REVIEW_AND_INGESTION_EVALUATION_2026-10-18.md`
- Code: `MyTradingSys/research/analysts/schema.py`; `MyTradingSys/research/analysts/ingest_analysts.py`; `MyTradingSys/research/analysts/score_analysts.py`; `MyTradingSys/research/analysts/run_scorecard.py`
- Ledger: `MyTradingSys/research/analysts/SAMPLE_CALL_LEDGER.csv`
- Other results: `MyTradingSys/research/analysts/SCORECARD.md`
- Roadmap: `MyTradingSys/research/analysts/ROADMAP.md`
- Codex lab reports (newest 2 of 2): `MyTradingSys/research/layer_lab/reports/2026-10-14_qriptal-score-binance.md`; `MyTradingSys/research/layer_lab/reports/2026-10-13_qriptal-score-binance.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `habib-plan-hit-rate-study` ready p2 DSA-NB: Habib plan-hit-rate study: score each Sunday/weekly plan full/partial/miss (execution excluded), then imbalanc
  - `qriptal-discord-calls-2026-10-18` ready p2 SONNET: Qriptal: transcribe Habib's 2026-10-13..18 Discord calls into the call ledger (B162)
  - `analyst-ingest-roman-x` ready p3 SONNET: Implement Roman Trading volume-absorption social call listener

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
  - `krown-data-cme-btc-volume` refined p2 DSA: Krown CME BTC futures daily volume (public data only) as third volume arm
  - `krown-dev-event-study` refined p2 SONNET: Krown DEV event study: hypotheses H-V1..H-T1, DEV only, fee-net, same-window placebo, power first; DONE when: 
  - `review-ground-layer-youtube-strategy-and` ready p2 SONNET: Review Ground Layer YouTube strategy and execution priorities
  - `trendline-audit-gaps-disposition` refined p2 SONNET: Trend-Line layer: disposition of AUDIT_2026-10-18 critical gaps (3 HIGH, 3 MED) and REGATE_AUDIT flip
  - `krown-other-sources-event-study-videos` refined p3 SONNET: Krown other sources: extract his daily BTC event-study videos and the CBP krown item with the V2 method (trigg

## WaveTrend (LazyBear oscillator) (`wavetrend`)
- Status: Causal observation module and parity fixtures exist. BTC DEV atlas remains exploratory: W01-W03/W09 FAIL; W04-W08 INCONCLUSIVE per the MTS re-gate; W07/W08 also use an invalid C1 detector. No validated edge or live integration.
- Tracks: Claude (research and layer work)
- Spec / sources: `MyTradingSys/research/wavetrend_2026-10-17/PARITY_CONTRACT.md`; `MyTradingSys/research/wavetrend_2026-10-17/ATLAS_STUDY_SPEC.md`; `MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md`
- Code: `MyTradingSys/backtest/layers/wavetrend/wavetrend.py`
- Ledger: `MyTradingSys/research/gross_effect_screen_2026-10-15/EXPOSURE_LEDGER.csv`
- Other results: `MyTradingSys/research/wavetrend_2026-10-17/RESULT.md`; `MyTradingSys/research/wavetrend_2026-10-17/AUDIT_2026-10-18.md`; `MyTradingSys/research/wavetrend_2026-10-17/DISPOSITION_2026-10-19.md`; `MyTradingSys/research/wavetrend_2026-10-17/STATUS_2026-10-19.md`
- Roadmap: `MyTradingSys/research/wavetrend_2026-10-17/STATUS_2026-10-19.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `wavetrend-c1-v2` refined p1 SONNET: WaveTrend C1 detector correction and new count-only prereg
  - `wavetrend-data-inference` refined p1 SONNET: WaveTrend DEV input manifest and matched inference

## Pitchfork (Andrews / Schiff / Morge median line) (`pitchfork`)
- Status: Foundational study papers delivered (papers/01, 02, 03); detector, tests, and YouTube BTC evaluation benchmark built.
- Tracks: Gemini (study/detector), Claude
- Layer `pitchfork_swing`: Foundational papers delivered; detector built with unit tests (100% pass) | module MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py
- Spec / sources: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md`; `papers/02_PITCHFORK_APPLICATION_ON_BTC.md`; `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md`; `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md`
- Code: `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py`
- Open cards: none

## Cross-cutting

- Every backtest row (layers on, params, verdict, report): MyTradingSys/system/layer_map.json (artifact: make_layer_map.py)
- Every trial count (multiple-testing ledger): MyTradingSys/research/fast_track_2026-09-27/bt_runs/TRIAL_REGISTRY.csv
- Formulas (canonical definitions): MyTradingSys/backtest/layers/FORMULAS.md
- Layer provenance (sourced vs NO-SOURCE parameters): MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md
- Codex layer lab deliveries and queue: MyTradingSys/research/layer_lab/INDEX.md (spec: system/LAYER_LAB.md)
- Work queue (relay Qn tasks): MyTradingSys/system/NEXT_SESSION.md; cards: python scripts/dev/tasks.py list
- Group-level project map (DATA/CORE/LAYR/EVID...): MyTradingSys/system/PROJECT_MAP.md
- Backtest pre-registration template and 12-point readiness checklist: MyTradingSys/backtest/PRE_REG_TEMPLATE.md
