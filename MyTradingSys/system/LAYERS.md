# LAYERS - one index per layer family (generated; do not hand-edit)

Read this before touching any layer (Claude and Codex). Regenerate: `python scripts/dev/make_layers_md.py` (tasks.py does it on
every card change). Pointers: `layer_index.json`; layer status and backtests: `layer_map.json`; cards: `system/tasks/`.
Rules: Tom is core; every other family is a separate layer, never a Tom filter (CLAUDE.md). A new backtest is a row in
`layer_map.json` (it then shows here); a new layer joins a family in `layer_index.json`; a new card names `--layer <family>`.

Families: tom = Tom (core engine + proofs) | fabio = Fabio (order-flow layer) | guidance = Tom/Fabio cross-guidance (BB, LVN, regime filters) | rsi = RSI / Malkan / Kurisko | cryptocred = CryptoCred setups | positioning = Positioning (funding, OI, whale / FlowHorse) | session_timing = Session / timing (session levels, turn of candle, session momentum) | volume_candles_ma = Volume, candle patterns, daily MA setups, bigtrade | live_engine = Live engine, execution and live-market reads (feeds every layer)

## Tom (core engine + proofs) (`tom`)
- Status: STOP on the BTC encoding; being redefined as Tom v2 (DAX home market). Never a filter for other layers.
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
- Codex lab reports (newest 4 of 11): `MyTradingSys/research/layer_lab/reports/2026-10-12_rv02-dax-harness-fixes.md`; `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-dax-unavailable-flow.md`; `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-dax-trial-identity.md`; `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-dax-session-null.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `rv02-fix-dax-full-dev-authorization` raw p1 SONNET: RV02 R3: require complete DAX sampling and bind holdout authorization
  - `rv02-fix-dax-preprocessing-isolation` raw p1 SONNET: RV02 R1: isolate DAX preprocessing and report metadata before holdout
  - `rv02-fix-dax-producer-data-binding` raw p1 SONNET: RV02 R4: reject DAX snapshots made from different execution data
  - `rv02-fix-dax-rounded-rr-gate` raw p1 SONNET: RV02 R2: preserve exact DAX net RR through the decision boundary
  - `tom-encode-spike-fade` refined p1 SONNET: Encode Tom's spike-top fade as a candidate type (recall test on his 7 DAX entries)
  - `tom-holdout-clean-split` ready p1 SONNET: Clean the DAX holdout of ledger days and split Tom's ledger into design and check sets
  - `tom-layer-v2-cost` blocked p1 OPUS: Tom layer v2 spec, part B: per-market proofs, cost, stop-width transfer rule, build cards (Opus research)
  - `tom-check-set-find-frames-only-tom-trade` raw p2 SONNET: Tom check set: find frames-only Tom trade recaps and log entry/stop/target without reading captions (check set
  - `tom-dax-backtest` refined p2 SONNET: Untuned Tom backtest on DAX vs matched-proof BTC rerun
  - `tom-direction-health-vs-sources` raw p2 SONNET: Tom core direction/health rules vs his words: determineDirections gives below_val -> long only (SetupCandidate
  - `tom-ledger-add-the-losing-first-attempts` raw p2 SONNET: Tom ledger: add the losing first attempts Tom states but the ledger lacks (S1, S6 pre-session stops)
  - `tom-probe-prereg` refined p2 SONNET: Pre-register the surviving S/Q/M/F arms and write their runner card
  - `tom-ledger-single-trade-date-used-column` raw p3 SONNET: Tom ledger: single trade_date_used column, blank date for non-observed rows (RV01 F1,F2)

## Fabio (order-flow layer) (`fabio`)
- Status: v3 tried 2026-10-04, holdout FAIL; ledger audit FIX-FIRST; being redefined as Fabio v2 (waits on ledger repairs).
- Tracks: Claude (spec/ledger), Codex lab (audits)
- Layer `fabio_cvd_absorption`: L1 no edge / insufficient n | module backtest/layers/fabio/fabio_cvd_absorption.py
- Layer `fabio_escalation`: L1 no edge / insufficient n | module backtest/layers/fabio/fabio_escalation.py
- Layer `fabio_volume_fvg`: L1 no edge | module backtest/layers/fabio/fabio_volume_fvg.py
- Layer `fabio_v3`: tried 2026-10-04; encoding being redefined (Fabio v2) | module backtest/layers/fabio/fabio_v3*.py; run_v3_l3.py
- Layer `fabio_of`: insufficient n; legacy fee pair | module backtest/layers/fabio/fabio_of_model.py; orderflow_bars.py
- Backtests (layer_map.json, newest first):
  - 2026-10-09 `FIRES-B1`: parity PASS on spot rerun | `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md`
  - 2026-10-06 `FABIO-OF`: no edge / insufficient n (stands under correct fees; numbers not reusable) | `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md`
  - 2026-10-04 `FABIO-V3`: not recorded in map | `MyTradingSys/research/fast_track_2026-09-27/bt_runs/TRIAL_REGISTRY.csv`
  - 2026-09-27 `L1-FABIO`: no edge / insufficient n (rule: OOS n>=30, net>0, PBO<0.5) | `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md`
- Spec / sources: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md`; `MyTradingSys/research/fast_track_2026-09-27/FABIO_RULEBOOK.md`; `MyTradingSys/research/fast_track_2026-09-27/FABIO_TRADE_MODEL.md`; `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md`
- Code: `MyTradingSys/backtest/layers/fabio/fabio_v3.py`; `MyTradingSys/backtest/layers/fabio/fabio_of_model.py`; `MyTradingSys/backtest/layers/fabio/run_v3_l3.py`
- Ledger: `MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.csv`; `MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.md`
- Other results: `MyTradingSys/research/P2_FABIO_V3_HOLDOUT_STATUS.md`; `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-fabio-ledger-frames.md`
- Roadmap: `MyTradingSys/research/tom_transfer_2026-10-11/ROADMAP.md`
- Codex lab reports (newest 1 of 1): `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-fabio-ledger-frames.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `fabio-layer-v2-markets` refined p2 OPUS: Fabio layer v2 spec, part B: data plan per market, cost, stop width, build + recall cards (Opus research)
  - `fabio-layer-v2-spec` blocked p2 OPUS: Fabio layer v2 spec, part A: setup families + sourced rules from his ledger (Opus research)
  - `fabio-ledger-minute-timestamps` ready p2 SONNET: Fabio ledger: read minute timestamps from frame clocks (replay-ready rows)
  - `fabio-video-prescreen` raw p2 SONNET: Fabio video pre-screen: list per 250 s window whether a frame shows an order ticket or position line, so only 
  - `lab-audit-fabio-ledger-frames` ready p2 CODEX: Audit Fabio's trade ledger against his chart frames and transcripts
  - `rv05-fabio-ledger-frame-pass` ready p2 CODEX: RV05 Fabio ledger frame-by-frame pass over unread rows (host=JIS-NUC)
  - `fabio-ledger-f13-outcome-provenance-2910` raw p3 SONNET: fabio-ledger: F13 outcome provenance (-2910 vs stop -1760)
  - `fabio-ledger-recompute-entry-from-stp-la` raw p3 SONNET: fabio-ledger: recompute entry from STP label for F8 F12-m2 F13 F13-m1
  - `fabio-ledger-replace-date-2026-with-unkn` raw p3 SONNET: fabio-ledger: replace date 2026 with UNKNOWN for Jpd96/DyS79 session (contract NQ-202512)
  - `fabio-ledger-scan-dys79eb92ug-is1hvdfqm5` raw p3 SONNET: Fabio ledger: scan DyS79Eb92Ug, Is1HvdfQm5c, xUyqIjCfZzg (downloaded on F:, 2.4-3.8 h live sessions) for trade
  - `find-more-fabio-trade-recap-videos-yt-dl` ready p3 SONNET: Find more Fabio trade-recap videos (yt-dlp), ledger has only 8 entries vs goal 20
  - `fabio-ledger-get-9i5vtvwsmbk-f398-not-av` raw p4 SONNET: Fabio ledger: get 9I5vTvwsMBk (f398 not available; try another format/client) and read it for trades

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
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `malkan-home-fit-audit` refined p4 SONNET: Home-fit audit of the Malkan RSI layer against the readiness checklist

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
  - `cryptocred-home-fit-audit` refined p4 SONNET: Home-fit audit of the CryptoCred layer against the readiness checklist

## Positioning (funding, OI, whale / FlowHorse) (`positioning`)
- Status: T055 C1 FAIL; OI/long-short unused as filters.
- Tracks: Claude
- Layer `funding_cvd_fade`: FAIL, closed | module backtest/layers/positioning/funding_cvd_fade.py
- Layer `oi_delta`: descriptive study | module research/OI_DELTA_4STATE_BACKTEST_2026-09-21.md
- Backtests (layer_map.json, newest first):
  - 2026-09-29, rerun 2026-10-07 (full funding) `T055-C1`: FAIL (rerun OOS net -0.0453%, Sharpe -0.035); closed | `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md`
  - 2026-09-21 `OI-DELTA`: descriptive; no verdict line in the head of the file | `MyTradingSys/research/OI_DELTA_4STATE_BACKTEST_2026-09-21.md`
- Spec / sources: `MyTradingSys/research/whale_positioning_evidence_2026-09-12.md`; `MyTradingSys/backtest/layers/FORMULAS.md`
- Code: `MyTradingSys/backtest/layers/positioning`
- Other results: `MyTradingSys/research/OI_DIVERGENCE_V2_2026-10-10.md`; `MyTradingSys/research/OI_EVENT_STUDY_2026-10-10.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `positioning-home-fit-audit` refined p4 SONNET: Home-fit audit of the FlowHorse / whale positioning layer against the readiness checklist

## Session / timing (session levels, turn of candle, session momentum) (`session_timing`)
- Status: T055 C2/C3 closed; T087 failed prior-day-high fade FAIL.
- Tracks: Claude
- Layer `session_momentum`: FAIL, closed | module backtest/layers/session/session_momentum.py
- Layer `turn_of_candle`: no edge, closed | module backtest/layers/turn_of_candle/
- Layer `session_levels`: no edge | module research/t087_session_levels_2026-10-09
- Backtests (layer_map.json, newest first):
  - 2026-10-09 `T087`: no edge (net -0.036%, t -1.72); EU-touch cells insufficient n | `MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md`
  - 2026-10-09 `FIRES-B1`: parity PASS on spot rerun | `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md`
  - 2026-09-29, rerun 2026-10-07 `T055-C2`: FAIL (rerun OOS net +0.0177%, Sharpe 0.0084, 1 of 2 years positive) | `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md`
  - 2026-09-29 `T055-C3`: NO EDGE (gross OOS about 0 at every horizon) | `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md`
- Spec / sources: `MyTradingSys/research/TURN_OF_CANDLE_ORIGIN_2026-10-09.md`
- Code: `MyTradingSys/backtest/layers/session`; `MyTradingSys/backtest/layers/session_levels`; `MyTradingSys/backtest/layers/turn_of_candle`
- Other results: `MyTradingSys/research/t087_session_levels_2026-10-09`
- Open cards: none

## Volume, candle patterns, daily MA setups, bigtrade (`volume_candles_ma`)
- Status: No validated edge; volume HOLDOUT sealed; MA numbers NO-SOURCE.
- Tracks: Claude
- Layer `volume`: no validated edge; HOLDOUT sealed | module research/volume_2026-10-09
- Layer `candle_patterns`: pilot run | module research/candle_patterns_2026-10-04
- Layer `ma_daily`: NO-SOURCE (chatbot handoff numbers) | module research/setup_alpha_beta_2026-10-10/alpha_backtest.py
- Layer `bigtrade_fires`: fires + exit policies run, HOLDOUT unread | module backtest/bigtrade; research/bigtrade_2026-10-09
- Backtests (layer_map.json, newest first):
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
- Other results: `MyTradingSys/research/volume_2026-10-09`; `MyTradingSys/research/candle_patterns_2026-10-04`; `MyTradingSys/research/setup_alpha_beta_2026-10-10`; `MyTradingSys/research/bigtrade_2026-10-09`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `time-adjusted-volume-context-line-for-th` raw p3 SONNET: Time-adjusted volume context line for the live read (same-slot baseline, effort vs result, OI scope) as read-o

## Live engine, execution and live-market reads (feeds every layer) (`live_engine`)
- Status: Testnet HALT since 2026-10-12 09:46Z (executor fail_closed); supervisor clears it. Live-market screenshot reads file findings as task cards.
- Tracks: Claude (live reads on JIS-NB), supervisor for HALT/deploy
- Spec / sources: `MyTradingSys/methodology/live_session_protocol.md`; `MyTradingSys/methodology/screenshot_intake.md`; `MyTradingSys/system/DEPLOY_RUNBOOK.md`
- Code: `MyTradingSys/execution`
- Other results: `MyTradingSys/research/screenshots`
- Roadmap: `MyTradingSys/system/NEXT_SESSION.md`
- Open cards (`python scripts/dev/tasks.py brief <id>`):
  - `exec-halt-entry-10031` raw p1 JIS-NB: HALT since 2026-10-12 09:46Z: executor fail_closed on entry_market rejected 10031 invalid_args_for_instrument 
  - `chart-verify-py-recompute-bb-rsi-stochrs` raw p2 SONNET: chart_verify.py: recompute BB/RSI/StochRSI/volume/OI/delta-step for any CoinGlass timeframe from fapi at the s
  - `live-loop-one-owner-guard` ready p2 JIS-NB: Live loop one-owner guard: start verb refuses when another host's heartbeat is fresh, fails closed (DEVICES.md
  - `live-mirror-stale-published-2026-10-11-2` raw p2 JIS-NB: Live mirror stale: published 2026-10-11 20:09Z, 19 h old at 15:25Z 10-12; NUC reads cannot check HALT, layer f
  - `rv06-live-read-claims` ready p2 CODEX: RV06 recompute live-read MATCH/MISMATCH claims from engine JSON and klines (host=JIS-NUC)
  - `rv07-layer-tooling-revalidate` ready p2 SONNET: RV07 layer tooling second look and shot.py outcome guards (host=any)
  - `identify-the-coinglass-net-delta-panel-u` raw p3 SONNET: Identify the CoinGlass Net Delta panel unit and scope: 4 reads in a row NOT_IN_DATA (8h 4.181K, 30m -8.366K, 1
  - `mts-cbp-integration-land-one-cbp-candida` ready p3 SONNET: MTS-CBP integration: land one CBP candidate on the real queue
  - `score-context-reads-automatically-carrie` raw p3 SONNET: Score context reads automatically: carried falsifier lines (HELD/BROKEN/UNTESTED) computed from klines at the 
  - `state-machine-vwap-cvd-vs-klines` raw p3 SONNET: State machine session VWAP/CVD disagree with klines: 2026-10-12 13:08Z state_code.json cum_pv/cum_vol gives 83
  - `one-timeframe-map-for-the-whole-toolchai` raw p4 SONNET: One timeframe map for the whole toolchain: capture.TF_MINUTES lacked 8h (CoinGlass button) while holding 7h; g

## Cross-cutting

- Every backtest row (layers on, params, verdict, report): MyTradingSys/system/layer_map.json (artifact: make_layer_map.py)
- Every trial count (multiple-testing ledger): MyTradingSys/research/fast_track_2026-09-27/bt_runs/TRIAL_REGISTRY.csv
- Formulas (canonical definitions): MyTradingSys/backtest/layers/FORMULAS.md
- Layer provenance (sourced vs NO-SOURCE parameters): MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md
- Codex layer lab deliveries and queue: MyTradingSys/research/layer_lab/INDEX.md (spec: system/LAYER_LAB.md)
- Work queue (relay Qn tasks): MyTradingSys/system/NEXT_SESSION.md; cards: python scripts/dev/tasks.py list
- Group-level project map (DATA/CORE/LAYR/EVID...): MyTradingSys/system/PROJECT_MAP.md
- Backtest pre-registration template and 12-point readiness checklist: MyTradingSys/backtest/PRE_REG_TEMPLATE.md
