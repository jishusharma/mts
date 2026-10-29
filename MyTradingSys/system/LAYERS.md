# LAYERS - one index per layer family (generated; do not hand-edit)

Read this before touching any layer (Claude and Codex). Regenerate: `python scripts/dev/make_layers_md.py` (tasks.py does it on
every card change). Pointers: `layer_index.json`; layer status and backtests: `layer_map.json`; cards: `system/tasks/`.
Rules: no fixed core; layers may combine or filter each other, results decide (CLAUDE.md, 2026-10-13). A new backtest is a row in
`layer_map.json` (it then shows here); a new layer joins a family in `layer_index.json`; a new card names `--layer <family>`.

Families: tom = Tom (order flow + volume profile) | fabio = Fabio (order-flow layer) | guidance = Tom/Fabio cross-guidance (BB, LVN, regime filters) | rsi = RSI / Malkan / Kurisko | cryptocred = CryptoCred setups | positioning = Positioning (funding, OI, whale / FlowHorse) | session_timing = Session / timing (session levels, turn of candle, session momentum) | volume_candles_ma = Volume, candle patterns, daily MA setups, bigtrade | live_engine = Live engine, execution and live-market reads (feeds every layer) | callers = Callers (posted trade calls: Qriptal, RLinda, Bennett, Crypto Chase, Roman) | krown = Krown (TA 101: zones, volume, candles, averages, ranges) | wavetrend = WaveTrend (LazyBear oscillator) | pitchfork = Pitchfork (Andrews / Schiff / Morge median line) | pizzino = Pizzino (Jason bar count + Michael nested swing states)

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
- Codex lab reports (newest 4 of 4): `MyTradingSys/research/layer_lab/reports/2026-10-28_tom-corr-live-captions.md`; `MyTradingSys/research/layer_lab/reports/2026-10-28_lf-tom-gpt-rederive.md`; `MyTradingSys/research/layer_lab/reports/2026-10-25_lf-tom-gemini-facts.md`; `MyTradingSys/research/layer_lab/reports/2026-10-22_tom-btc-other-setups.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `tom-btc-eye-read` blocked p1 SONNET: Tom on BTC T3: eye read of the 80 lab charts by two readers (Claude + Jis), blind; agreement per Tom concept
  - `live-divergence-event-log` ready p2 DSA: Live divergence event log: record each BTC vs ES/NQ divergence read with outcomes at +30/60/120 min (forward e
  - `tom-btc-dev-backtest` blocked p2 CODEX: Tom on BTC T6: DEV backtest + adjustments (both fills, maker vs taker entry, management arms) - every variant 
  - `tom-btc-encode` blocked p2 CODEX: Tom on BTC T5: encode the concepts that separated into a flag-gated BTC detector (entry paths A1-A3, stop at t
  - `tom-btc-validation` blocked p2 DSA-NUC: Tom on BTC T7: VALIDATION read once (2025-04..2025-06) of the frozen DEV config
  - `tom-probe-prereg` blocked p2 SONNET: Pre-register the surviving S/Q/M/F arms and write their runner card
  - `tom-probe-runner` blocked p2 SONNET: Run pre-registered Tom management arms on DAX and BTC
  - `lab-verify-trend-healthy-in-balance` refined p3 SONNET: LAB-VERIFY 10-18: how often trend_healthy is set inside a multi-day balance (DEV)
  - `layer-review-tom-guidance` ready p3 SONNET: Layer review sheet: Tom and cross-guidance (idea, source, backtests, bugs, confluence)
  - `tom-btc-other-setups` blocked p3 CODEX: Tom on BTC T8: chart lab + event study for his other trade types (trend continuation pullback to value/VWAP, b

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
- Other results: `MyTradingSys/research/_archive/loose_2026-10/P2_FABIO_V3_HOLDOUT_STATUS.md`; `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-fabio-ledger-frames.md`; `MyTradingSys/research/orderflow_views_2026-10-14`
- Roadmap: `MyTradingSys/research/tom_transfer_2026-10-11/ROADMAP.md`
- Codex lab reports (newest 2 of 2): `MyTradingSys/research/layer_lab/reports/2026-10-28_lf-fabio-gpt-rederive.md`; `MyTradingSys/research/layer_lab/reports/2026-10-25_lf-fabio-gemini-facts.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `t09-f4-live-window-99-bars-swing-layers` ready p2 JIS-NB: T09-F4 S2: 99-bar live window misses 68 of 96 escalation signals; fetch more bars for swing layers
  - `layer-review-fabio-session` ready p3 SONNET: Layer review sheet: Fabio and session timing (idea, source, backtests, bugs, confluence)
  - `oi-pivot-1h-4h-long-oi-followup` ready p3 SONNET: OI pivot candidates at 1h/4h: aggregate the 5m metrics archive 2022-01..2024-06 (DEV), same candidates/outcome
  - `fabio-layer-v2-markets` blocked p5 OPUS: Fabio layer v2 spec, part B: data plan per market, cost, stop width, build + recall cards (Opus research)
  - `fabio-layer-v2-spec` blocked p5 OPUS: Fabio layer v2 spec, part A: setup families + sourced rules from his ledger (Opus research)

## Tom/Fabio cross-guidance (BB, LVN, regime filters) (`guidance`)
- Status: Q33 found no surviving cell: do not wire cross-guidance (Q34 skipped).
- Tracks: Claude
- Layer `bb_lvn_triggers`: no cell survives | module research/tom_fabio_guidance_2026-10-12/matrix_q33.py
- Backtests (layer_map.json, newest first):
  - 2026-10-12 `Q33`: no cell survives (smallest q 0.62); do not wire cross-guidance | `MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md`
- Spec / sources: `MyTradingSys/research/tom_fabio_guidance_2026-10-12/GUIDANCE_AUDIT.md`; `MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md`
- Code: `MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py`; `MyTradingSys/backtest/layers/test_layer_boundaries.py`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `lf-guidance-gpt-rederive` blocked p2 CODEX: Layer re-derive: guidance (independent recount of the headline numbers behind the fact sheet)
  - `layer-review-tom-guidance` ready p3 SONNET: Layer review sheet: Tom and cross-guidance (idea, source, backtests, bugs, confluence)

## RSI / Malkan / Kurisko (`rsi`)
- Status: 40/60 levels: tolerance study done; divergence: no edge on any TF.
- Tracks: Claude
- Layer `rsi_levels`: D3 tolerance study done | module backtest/layers/rsi; rsi_events
- Layer `rsi_divergence`: no edge, all TFs | module backtest/layers/rsi/run_divergence_mtf.py
- Backtests (layer_map.json, newest first):
  - 2026-10-09 `RSI-DIV-MTF`: no edge on any timeframe that reached 300 events; 31 of 32 net negative; 6h and 2d leads have n 6-54 | `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md`
  - 2026-10-09 `FIRES-B1`: parity PASS on spot rerun | `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md`
  - 2026-10-07 `MARKET-GUIDE`: table in report not read for this map | `MyTradingSys/research/_archive/loose_2026-10/MARKET_GUIDE_RESULTS_2026-10-07.md`
  - 2026-09-27 `L1-D3`: mixed: 1h support PBO 0.030, everything else PBO 0.39-0.91 | `MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md`
- Spec / sources: `MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md`; `MyTradingSys/backtest/layers/FORMULAS.md`
- Code: `MyTradingSys/backtest/layers/rsi/malkan_40_60.py`; `MyTradingSys/backtest/layers/rsi/malkan_mtf.py`; `MyTradingSys/backtest/layers/kurisko/quad_rotation.py`; `MyTradingSys/backtest/layers/kurisko/stoch_core.py`
- Other results: `MyTradingSys/research/rsi_divergence_mtf_2026-10-09`
- Codex lab reports (newest 3 of 3): `MyTradingSys/research/layer_lab/reports/2026-10-28_malkan-hindi-reread-garble-check.md`; `MyTradingSys/research/layer_lab/reports/2026-10-28_lf-rsi-gpt-rederive.md`; `MyTradingSys/research/layer_lab/reports/2026-10-26_lf-rsi-gemini-facts.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `malkan-rsi-divergence-chart-flags-1d-1w` ready p1 SONNET: Malkan RSI regular + hidden divergence detector with chart-drawn flags on 1d and 1w (operator confirms/correct
  - `sourced-rule-guard` ready p1 SONNET: Guard: no layer param or rule ships without a SOURCED quote+file:line or an OURS label (CI test)
  - `krown-hidden-divergence-confluence-feed` ready p2 SONNET: Krown hidden divergence as a shared confluence feed any layer (RSI 40-60 included) can consume; Malkan layer s
  - `kurisko-dev-event-study` ready p2 SONNET: Kurisko Quad Rotation: DEV event study, fee-net, same-window placebo
  - `layer-review-rsi-cc-pitchfork-engine` ready p3 SONNET: Layer review sheet: RSI, CryptoCred, pitchfork, live engine (idea, source, backtests, bugs, confluence)
  - `rsi-cross-unmapped-and-pivot-stack` ready p3 SONNET: RSI cross events are rejected as unmapped in the auto-trader (no layer_rules entry); and no layer stacks level
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
- Codex lab reports (newest 1 of 1): `MyTradingSys/research/layer_lab/reports/2026-10-25_lf-cryptocred-gemini-facts.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `lf-cryptocred-gpt-rederive` blocked p2 CODEX: Layer re-derive: cryptocred (independent recount of the headline numbers behind the fact sheet)
  - `layer-review-rsi-cc-pitchfork-engine` ready p3 SONNET: Layer review sheet: RSI, CryptoCred, pitchfork, live engine (idea, source, backtests, bugs, confluence)

## Positioning (funding, OI, whale / FlowHorse) (`positioning`)
- Status: T055 C1 FAIL; OI/long-short unused as filters.
- Tracks: Claude
- Layer `funding_cvd_fade`: FAIL, closed | module backtest/layers/positioning/funding_cvd_fade.py
- Layer `oi_delta`: descriptive study | module research/_archive/loose_2026-10/OI_DELTA_4STATE_BACKTEST_2026-09-21.md
- Backtests (layer_map.json, newest first):
  - 2026-10-14 `PRICE-CVD-DIV-1M5M-20261014`: NEGATIVE: CVD divergence adds nothing over price alone on 1m/5m | `MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md`
  - 2026-09-29, rerun 2026-10-07 (full funding) `T055-C1`: FAIL (rerun OOS net -0.0453%, Sharpe -0.035); closed | `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md`
  - 2026-09-21 `OI-DELTA`: descriptive; no verdict line in the head of the file | `MyTradingSys/research/_archive/loose_2026-10/OI_DELTA_4STATE_BACKTEST_2026-09-21.md`
- Spec / sources: `MyTradingSys/research/_archive/loose_2026-10/whale_positioning_evidence_2026-09-12.md`; `MyTradingSys/backtest/layers/FORMULAS.md`
- Code: `MyTradingSys/backtest/layers/positioning`
- Other results: `MyTradingSys/research/_archive/loose_2026-10/OI_DIVERGENCE_V2_2026-10-10.md`; `MyTradingSys/research/_archive/loose_2026-10/OI_EVENT_STUDY_2026-10-10.md`
- Codex lab reports (newest 1 of 1): `MyTradingSys/research/layer_lab/reports/2026-10-28_lf-positioning-gpt-rederive.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `layer-review-positioning-volume-callers` ready p3 SONNET: Layer review sheet: positioning, volume and candles, callers (idea, source, backtests, bugs, confluence)
  - `positioning-c1-prereg-no-source` ready p4 SONNET: Positioning C1: pre-registration labelled NO-SOURCE (items 1/6/8/9/11/12, gates 0a/0f)

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
- Spec / sources: `MyTradingSys/research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md`
- Code: `MyTradingSys/backtest/layers/session`; `MyTradingSys/backtest/layers/session_levels`; `MyTradingSys/backtest/layers/turn_of_candle`
- Other results: `MyTradingSys/research/t087_session_levels_2026-10-09`; `MyTradingSys/research/eur_low_us_sweep_2026-10-14`
- Codex lab reports (newest 3 of 3): `MyTradingSys/research/layer_lab/reports/2026-10-28_lf-session_timing-gpt-rederive.md`; `MyTradingSys/research/layer_lab/reports/2026-10-28_lf-session_timing-gemini-facts.md`; `MyTradingSys/research/layer_lab/reports/2026-10-27_lf-session_timing-gpt-rederive.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `layer-review-fabio-session` ready p3 SONNET: Layer review sheet: Fabio and session timing (idea, source, backtests, bugs, confluence)

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
  - 2026-10-07 `MARKET-GUIDE`: table in report not read for this map | `MyTradingSys/research/_archive/loose_2026-10/MARKET_GUIDE_RESULTS_2026-10-07.md`
  - 2026-10-04 `CANDLE-D19`: NO-SOURCE; below buy-and-hold | `MyTradingSys/research/candle_patterns_2026-10-04/D19_4H_RESULTS.md`
  - 2026-10-04 `CANDLE-P0`: exploratory; no edge vs random null | `MyTradingSys/research/candle_patterns_2026-10-04/P0_RESULTS.md`
- Spec / sources: `MyTradingSys/backtest/layers/FORMULAS.md`
- Code: `MyTradingSys/backtest/bigtrade`
- Other results: `MyTradingSys/research/volume_2026-10-09`; `MyTradingSys/research/candle_patterns_2026-10-04`; `MyTradingSys/research/setup_alpha_beta_2026-10-10`; `MyTradingSys/research/bigtrade_2026-10-09`; `MyTradingSys/research/layer_lab/candle_close_2026-10-14`
- Codex lab reports (newest 2 of 2): `MyTradingSys/research/layer_lab/reports/2026-10-28_lf-volume_candles_ma-gpt-rederive.md`; `MyTradingSys/research/layer_lab/reports/2026-10-28_lf-volume_candles_ma-gemini-facts.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `layer-review-positioning-volume-callers` ready p3 SONNET: Layer review sheet: positioning, volume and candles, callers (idea, source, backtests, bugs, confluence)
  - `pooled-short-lookback-trend-tsmom-30d-sm` blocked p3 DSA: Pooled short-lookback trend (TSMOM 30d, SMA50/100, 4h Donchian 20/10) on sealed 2025-07..2026-09 BTC holdout: 
  - `time-adjusted-volume-context-line-for-th` refined p3 SONNET: Time-adjusted volume context line for the live read (same-slot baseline, effort vs result, OI scope) as read-o

## Live engine, execution and live-market reads (feeds every layer) (`live_engine`)
- Status: Testnet HALT since 2026-10-12 09:46Z (executor fail_closed); supervisor clears it. Live-market screenshot reads file findings as task cards.
- Tracks: Claude (live reads on JIS-NB), supervisor for HALT/deploy
- Spec / sources: `MyTradingSys/methodology/live_session_protocol.md`; `MyTradingSys/methodology/screenshot_intake.md`; `MyTradingSys/system/DEPLOY_RUNBOOK.md`
- Code: `MyTradingSys/execution`
- Other results: `MyTradingSys/research/screenshots`
- Roadmap: `MyTradingSys/system/NEXT_SESSION.md`
- Codex lab reports (newest 2 of 2): `MyTradingSys/research/layer_lab/reports/2026-10-28_lf-live_engine-gpt-rederive.md`; `MyTradingSys/research/layer_lab/reports/2026-10-28_lf-live_engine-gemini-facts.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `live-mirror-follow-live-host-move` ready p1 DSA: live_mirror.py hard-codes JIS-NB (LIVE_HOST, share \JIS-NB\MTS-Mirror); live loop is on desktop-f7iu69n (Lenov
  - `state-code-accumulator-backfill` refined p2 JIS-NB: StateCodeEmitter: backfill session CVD/cum_pv/cum_vol after restart and WS reconnect, fail closed on backfill 
  - `statecode-backfill-race-coverage` ready p2 JIS-NB: StateCodeEmitter: cover in-flight rollover reconnect and retry scheduling
  - `layer-review-rsi-cc-pitchfork-engine` ready p3 SONNET: Layer review sheet: RSI, CryptoCred, pitchfork, live engine (idea, source, backtests, bugs, confluence)
  - `live-loop-timeouts-b191` refined p3 SONNET: Network: re-check live-loop timeouts after B191 plus wrapper priority and snapshot.cp (read-only report first)
  - `live-orderflow-state-line-1m-5m-15m-pric` refined p3 SONNET: Live read: one order-flow state line per TF (1m/5m/15m price swing vs Binance CVD swing vs OI change), descrip
  - `score-context-reads-automatically-carrie` refined p3 SONNET: Score context reads automatically: carried falsifier lines (HELD/BROKEN/UNTESTED) computed from klines at the 

## Callers (posted trade calls: Qriptal, RLinda, Bennett, Crypto Chase, Roman) (`callers`)
- Status: Score the posted calls on Binance klines before anything else (B162 + multi-analyst ingestion). Self-reported 67.1 % wins, avg win 3.99 %, avg loss 0.63 %: unverified. Multi-provider parser + kline scorecard built (2026-10-18); 4 ingestion cards ready.
- Tracks: Claude, Codex lab (scoring)
- Spec / sources: `MyTradingSys/items/B162_qriptal_signal_layer.md`; `MyTradingSys/research/_archive/loose_2026-10/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md`; `MyTradingSys/research/analysts/REVIEW_AND_INGESTION_EVALUATION_2026-10-18.md`
- Code: `MyTradingSys/research/analysts/schema.py`; `MyTradingSys/research/analysts/ingest_analysts.py`; `MyTradingSys/research/analysts/score_analysts.py`; `MyTradingSys/research/analysts/run_scorecard.py`
- Ledger: `MyTradingSys/research/analysts/SAMPLE_CALL_LEDGER.csv`
- Other results: `MyTradingSys/research/analysts/SCORECARD.md`
- Roadmap: `MyTradingSys/research/analysts/ROADMAP.md`
- Codex lab reports (newest 1 of 1): `MyTradingSys/research/layer_lab/reports/2026-10-28_lf-callers-gpt-rederive.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `analyst-ingest-roman-x` ready p3 SONNET: Implement Roman Trading volume-absorption social call listener
  - `layer-review-positioning-volume-callers` ready p3 SONNET: Layer review sheet: positioning, volume and candles, callers (idea, source, backtests, bugs, confluence)

## Krown (TA 101: zones, volume, candles, averages, ranges) (`krown`)
- Status: Spec v0.2 + 120-rule ledger from 15 of 19 reachable TA 101 videos (14 TA + 1 fees). The 4 missing transcripts are on disk since 2026-10-16 (krown_capture_2026-10-16/transcripts/ta101_missing4). Gate G2 reached: KROWN_SETUP_CATALOG.md (commit f4a5182a). One structural stop (compression breakout), no stop distance or size rule: the rest is OURS. Detectors not built, not backtested.
- Tracks: Claude (extraction, ledger, spec, detectors), DSA (data runs)
- Spec / sources: `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md`; `MyTradingSys/research/krown_ta101_2026-10-13/PRE_REG_KROWN.md`; `MyTradingSys/research/krown_ta101_2026-10-13/PROTOCOL.md`; `MyTradingSys/research/krown_ta101_2026-10-13/STATE.md`
- Code: `MyTradingSys/research/krown_ta101_2026-10-13/tools/build_ledger.py`; `MyTradingSys/research/krown_ta101_2026-10-13/tools/check_numbers.py`
- Ledger: `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv`; `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_CONSOLIDATED.md`; `MyTradingSys/research/krown_ta101_2026-10-13/MANIFEST.csv`
- Other results: `MyTradingSys/research/krown_ta101_2026-10-13/reflexivity_log.md`; `MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md`; `MyTradingSys/options/research/KROWN_FREE_VS_PAID.md`
- Roadmap: `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md`
- Codex lab reports (newest 4 of 6): `MyTradingSys/research/layer_lab/reports/2026-10-30_krown-other-sources-event-study-videos.md`; `MyTradingSys/research/layer_lab/reports/2026-10-28_lf-krown-gpt-rederive.md`; `MyTradingSys/research/layer_lab/reports/2026-10-28_astra-low-levels-fee-drag-recompute.md`; `MyTradingSys/research/layer_lab/reports/2026-10-26_astra-low-levels-fee-drag-recompute.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `sourced-rule-guard` ready p1 SONNET: Guard: no layer param or rule ships without a SOURCED quote+file:line or an OURS label (CI test)
  - `confluence-s4-dev-trials` ready p2 SONNET: Confluence S4: DEV and DEV_EXT trial runs (T2, sizing arm, pooled read, T4) per PRE_REG_CONFLUENCE
  - `confluence-s5-fable-verdict` refined p2 SONNET: Confluence S5: Fable verdict on DEV results, what goes to the one VALIDATION read (then ship, S6)
  - `krown-data-cme-btc-volume` refined p2 SONNET: Krown CME BTC futures daily volume (public data only) as third volume arm
  - `krown-dev-event-study` refined p2 SONNET: Krown DEV event study: hypotheses H-V1..H-T1, DEV only, fee-net, same-window placebo, power first; DONE when: 
  - `krown-dev-event-study-candles` refined p2 SONNET: Krown DEV event study 3/3: candle hypotheses H-C1, H-C2 (H-T1 not run); DONE when: DEV_RESULTS.md has N, power
  - `krown-dev-event-study-levels` refined p2 SONNET: Krown DEV event study 2/3: level and moving-average hypotheses H-M1, H-M3, H-Z1 (H-M2 not run); DONE when: DEV
  - `krown-hidden-divergence-confluence-feed` ready p2 SONNET: Krown hidden divergence as a shared confluence feed any layer (RSI 40-60 included) can consume; Malkan layer s
  - `layer-review-krown-wavetrend` ready p3 SONNET: Layer review sheet: Krown and WaveTrend (idea, source, backtests, bugs, confluence)
  - `trendline-ledger-registry-hygiene` ready p3 SONNET: Trend-line daily ledger schema v2 enforcement + register the module in layer_index and wiring_registry (audit 

## WaveTrend (LazyBear oscillator) (`wavetrend`)
- Status: Causal observation module and parity fixtures exist. BTC DEV atlas remains exploratory: W01-W03/W09 FAIL; W04-W08 INCONCLUSIVE per the MTS re-gate; W07/W08 also use an invalid C1 detector. No validated edge or live integration.
- Tracks: Claude (research and layer work)
- Spec / sources: `MyTradingSys/research/wavetrend_2026-10-17/PARITY_CONTRACT.md`; `MyTradingSys/research/wavetrend_2026-10-17/ATLAS_STUDY_SPEC.md`; `MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md`
- Code: `MyTradingSys/backtest/layers/wavetrend/wavetrend.py`
- Ledger: `MyTradingSys/research/gross_effect_screen_2026-10-15/EXPOSURE_LEDGER.csv`
- Other results: `MyTradingSys/research/wavetrend_2026-10-17/RESULT.md`; `MyTradingSys/research/wavetrend_2026-10-17/AUDIT_2026-10-18.md`; `MyTradingSys/research/wavetrend_2026-10-17/DISPOSITION_2026-10-19.md`; `MyTradingSys/research/wavetrend_2026-10-17/STATUS_2026-10-19.md`
- Roadmap: `MyTradingSys/research/wavetrend_2026-10-17/STATUS_2026-10-19.md`
- Codex lab reports (newest 1 of 1): `MyTradingSys/research/layer_lab/reports/2026-10-27_lf-wavetrend-gpt-rederive.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `wavetrend-c1-v2` refined p1 SONNET: WaveTrend C1 detector correction and new count-only prereg
  - `layer-review-krown-wavetrend` ready p3 SONNET: Layer review sheet: Krown and WaveTrend (idea, source, backtests, bugs, confluence)

## Pitchfork (Andrews / Schiff / Morge median line) (`pitchfork`)
- Status: Detector, simulator desk plugin (studies/pitchfork.py), and live Java engine (PitchforkSignalLayer.java with Tine Bounce + Hagopian Failure + Volume Profile confluence) built, wired, and verified on DEV.
- Tracks: Gemini (study/detector), Claude
- Layer `pitchfork_swing`: Detector, sim_desk plugin (studies/pitchfork.py), and live Java engine (PitchforkSignalLayer.java) built and verified (100% pass) | module MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py
- Backtests (layer_map.json, newest first):
  - 2026-10-28 `PITCHFORK-4H-VP-20261028`: PASS (VA confluence PF 1.63, +0.61% net/trade; sim_desk plugin verified) | `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md`
  - 2026-10-19 `PITCHFORK-1D-20261019`: PASS (Modified Schiff +1.50% mean net/trade, 72.12% ML reach) | `MyTradingSys/research/pitchfork_2026-10-19/PHASE1_EVENT_STUDY.md`
- Spec / sources: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md`; `papers/02_PITCHFORK_APPLICATION_ON_BTC.md`; `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md`; `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md`
- Code: `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py`; `MyTradingSys/research/sim_desk/studies/pitchfork.py`; `src/main/java/datafeed/PitchforkSignalLayer.java`
- Ledger: `MyTradingSys/research/pitchfork_2026-10-19/TRIALS_PITCHFORK.csv`; `MyTradingSys/research/pitchfork_2026-10-19/TRIALS_PITCHFORK_4H.csv`
- Codex lab reports (newest 1 of 1): `MyTradingSys/research/layer_lab/reports/2026-10-28_lf-pitchfork-gpt-rederive.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `pin-a-regression-test-tom-signal-parse-t` ready p2 SONNET: Pin a regression test: tom_signal/parse_tom_alert must reject any PF-* setup string, not just today's exact sp
  - `pitchfork-engine-implement-hagopian-fail` refined p2 OPUS: Pitchfork engine: implement Hagopian failure breakout candidates (PF-HAG-L / PF-HAG-S) in Java
  - `pitchfork-fixes-desk-python` ready p2 SONNET: Pitchfork desk/Python review fixes: F1 target reading, F4 profile parity, F5 lookahead + VA leak test, F6 pyth
  - `pitchfork-fixes-live-java` raw p2 SONNET: Pitchfork live Java review fixes: F3 stale-bounce gate parity, F6 inverted-fork tine, F7/F9 labels
  - `sim-desk-plug-in-pitchfork-4h-tine-bounc` refined p2 OPUS: Sim desk: plug in Pitchfork 4H tine-bounce study adapter (Modified Schiff + Volume Profile)
  - `layer-review-rsi-cc-pitchfork-engine` ready p3 SONNET: Layer review sheet: RSI, CryptoCred, pitchfork, live engine (idea, source, backtests, bugs, confluence)

## Pizzino (Jason bar count + Michael nested swing states) (`pizzino`)
- Status: Indicator module built with fail-first tests from SPEC worked examples. No backtest, no live wiring (pz-4 next).
- Tracks: Claude
- Layer `pizzino_indicators`: Pure-function module built with tests; not backtested, not wired | module MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py
- Spec / sources: `MyTradingSys/research/pizzino_layer_2026-10-27/SPEC.md`; `MyTradingSys/research/pizzino_layer_2026-10-27/PLAN.md`
- Code: `MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `pz-4-backtest` refined p1 SONNET: Pizzino layer: BTC backtest DEV/VALIDATION/holdout, fee-net, trial ledger
  - `pz-5-confluence-and-live` refined p2 SONNET: Pizzino layer: confluence table with other layers; cbp.query bias and levels as live input

## Cross-cutting

- Every backtest row (layers on, params, verdict, report): MyTradingSys/system/layer_map.json (artifact: make_layer_map.py)
- Every trial count (multiple-testing ledger): MyTradingSys/research/fast_track_2026-09-27/bt_runs/TRIAL_REGISTRY.csv
- Formulas (canonical definitions): MyTradingSys/backtest/layers/FORMULAS.md
- Layer provenance (sourced vs NO-SOURCE parameters): MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md
- Codex layer lab deliveries and queue: MyTradingSys/research/layer_lab/INDEX.md (spec: system/LAYER_LAB.md)
- Work queue (relay Qn tasks): MyTradingSys/system/NEXT_SESSION.md; cards: python scripts/dev/tasks.py list
- Group-level project map (DATA/CORE/LAYR/EVID...): MyTradingSys/system/PROJECT_MAP.md
- Backtest pre-registration template and 12-point readiness checklist: MyTradingSys/backtest/PRE_REG_TEMPLATE.md
