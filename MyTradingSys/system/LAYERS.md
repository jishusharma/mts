# LAYERS - one index per layer (generated; do not hand-edit)

Source: `MyTradingSys/system/layer_index.json` (pointers) + live task cards. Regenerate: `python scripts/dev/make_layers_md.py`.
Add a layer or move a file: edit the JSON, regenerate; `--check` / `tests/test_layers_index.py` fail on a dead pointer.
Rules: Tom is core, every other family is a separate layer and never a Tom filter (CLAUDE.md). A new result goes in the family's
Latest results AND as a row in `layer_map.json`. Two tracks work here: Claude sessions and the Codex layer lab (lane CODEX); both read this page first.

## Tom (core engine + proofs)
- Status: STOP on the BTC encoding; being redefined as Tom v2 (DAX home market). Never a filter for other layers.
- Tracks: Claude (spec/build), Codex lab (audits, DAX harness)
- Spec / sources: `MyTradingSys/research/tom_transfer_2026-10-11/ROADMAP.md`; `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md`; `MyTradingSys/research/TOM_VERBATIM_INDEX.md`
- Code: `src/main/java/datafeed/SetupCandidatesBuilder.java`; `MyTradingSys/backtest/tom_dax_bt.py`; `MyTradingSys/backtest/verdict.py`
- Ledger: `MyTradingSys/research/tom_transfer_2026-10-11/TOM_TRADE_LEDGER.csv`; `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LEDGER_CANONICAL_GROUPS.csv`
- Latest results: `MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md`; `MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md`; `MyTradingSys/research/tom_transfer_2026-10-11/RECALL_DAX.md`; `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-tom-ledger-frames.md`
- Roadmap: `MyTradingSys/research/tom_transfer_2026-10-11/ROADMAP.md`; `MyTradingSys/research/tom_transfer_2026-10-11/PRE_REG_DAX.md`
- Open cards (`tasks.py brief <id>`):
  - `lab-dax-readiness-gate` ready p1 CODEX: DAX audit H7: gate the home-market report on all twelve readiness items
  - `lab-dax-trial-identity` ready p1 CODEX: DAX audit H8: bind cached rows and trial counts to frozen run inputs
  - `tom-encode-spike-fade` refined p1 SONNET: Encode Tom's spike-top fade as a candidate type (recall test on his 7 DAX entries)
  - `tom-holdout-clean-split` ready p1 SONNET: Clean the DAX holdout of ledger days and split Tom's ledger into design and check sets
  - `tom-layer-v2-cost` blocked p1 OPUS: Tom layer v2 spec, part B: per-market proofs, cost, stop-width transfer rule, build cards (Opus research)
  - `tom-layer-v2-spec` refined p1 OPUS: Tom layer v2 spec, part A: setup families + sourced rules from the ledger (Opus research)
  - `tom-dax-backtest` refined p2 SONNET: Untuned Tom backtest on DAX vs matched-proof BTC rerun
  - `tom-direction-health-vs-sources` raw p2 SONNET: Tom core direction/health rules vs his words: determineDirections gives below_val -> long only (SetupCandidate
  - `tom-probe-prereg` refined p2 SONNET: Pre-register the surviving S/Q/M/F arms and write their runner card

## Fabio (order-flow layer)
- Status: v3 tried 2026-10-04, holdout FAIL; ledger audit FIX-FIRST; being redefined as Fabio v2 (waits on ledger repairs).
- Tracks: Claude (spec/ledger), Codex lab (audits)
- Spec / sources: `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md`; `MyTradingSys/research/fast_track_2026-09-27/FABIO_RULEBOOK.md`; `MyTradingSys/research/fast_track_2026-09-27/FABIO_TRADE_MODEL.md`; `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md`
- Code: `MyTradingSys/backtest/layers/fabio/fabio_v3.py`; `MyTradingSys/backtest/layers/fabio/fabio_of_model.py`; `MyTradingSys/backtest/layers/fabio/run_v3_l3.py`
- Ledger: `MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.csv`; `MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.md`
- Latest results: `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md`; `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md`; `MyTradingSys/research/P2_FABIO_V3_HOLDOUT_STATUS.md`; `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-fabio-ledger-frames.md`
- Roadmap: `MyTradingSys/research/tom_transfer_2026-10-11/ROADMAP.md`
- Open cards (`tasks.py brief <id>`):
  - `fabio-layer-v2-markets` refined p2 OPUS: Fabio layer v2 spec, part B: data plan per market, cost, stop width, build + recall cards (Opus research)
  - `fabio-layer-v2-spec` ready p2 OPUS: Fabio layer v2 spec, part A: setup families + sourced rules from his ledger (Opus research)
  - `fabio-ledger-minute-timestamps` ready p2 SONNET: Fabio ledger: read minute timestamps from frame clocks (replay-ready rows)
  - `lab-audit-fabio-ledger-frames` ready p2 CODEX: Audit Fabio's trade ledger against his chart frames and transcripts
  - `fabio-ledger-f13-outcome-provenance-2910` raw p3 SONNET: fabio-ledger: F13 outcome provenance (-2910 vs stop -1760)
  - `fabio-ledger-recompute-entry-from-stp-la` raw p3 SONNET: fabio-ledger: recompute entry from STP label for F8 F12-m2 F13 F13-m1
  - `fabio-ledger-replace-date-2026-with-unkn` raw p3 SONNET: fabio-ledger: replace date 2026 with UNKNOWN for Jpd96/DyS79 session (contract NQ-202512)
  - `fabio-ledger-scan-dys79eb92ug-is1hvdfqm5` raw p3 SONNET: Fabio ledger: scan DyS79Eb92Ug, Is1HvdfQm5c, xUyqIjCfZzg (downloaded on F:, 2.4-3.8 h live sessions) for trade
  - `find-more-fabio-trade-recap-videos-yt-dl` ready p3 SONNET: Find more Fabio trade-recap videos (yt-dlp), ledger has only 8 entries vs goal 20
  - `fabio-ledger-get-9i5vtvwsmbk-f398-not-av` raw p4 SONNET: Fabio ledger: get 9I5vTvwsMBk (f398 not available; try another format/client) and read it for trades

## Tom/Fabio cross-guidance (BB, LVN, regime filters)
- Status: Q33 found no surviving cell: do not wire cross-guidance (Q34 skipped).
- Tracks: Claude
- Spec / sources: `MyTradingSys/research/tom_fabio_guidance_2026-10-12/GUIDANCE_AUDIT.md`; `MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md`
- Code: `MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py`; `MyTradingSys/backtest/layers/test_layer_boundaries.py`
- Latest results: `MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md`
- Open cards: none

## RSI / Malkan / Kurisko
- Status: 40/60 levels: tolerance study done; divergence: no edge on any TF.
- Tracks: Claude
- Spec / sources: `MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md`; `MyTradingSys/backtest/layers/FORMULAS.md`
- Code: `MyTradingSys/backtest/layers/rsi/malkan_40_60.py`; `MyTradingSys/backtest/layers/rsi/malkan_mtf.py`
- Latest results: `MyTradingSys/research/rsi_divergence_mtf_2026-10-09`
- Open cards (`tasks.py brief <id>`):
  - `malkan-home-fit-audit` refined p4 SONNET: Home-fit audit of the Malkan RSI layer against the readiness checklist

## CryptoCred setups
- Status: S/R flip + fib pullback + failed MSB FAIL after trade-through rerun; stop buffer unsourced (B143).
- Tracks: Claude
- Spec / sources: `MyTradingSys/items/B143_cryptocred_stop_buffer_and_target_unsourced.md`; `MyTradingSys/backtest/layers/FORMULAS.md`
- Code: `MyTradingSys/backtest/layers/cryptocred`
- Latest results: `MyTradingSys/research/cryptocred_stop_2026-10-10`
- Open cards (`tasks.py brief <id>`):
  - `cryptocred-home-fit-audit` refined p4 SONNET: Home-fit audit of the CryptoCred layer against the readiness checklist

## Positioning (funding, OI, whale / FlowHorse)
- Status: T055 C1 FAIL; OI/long-short unused as filters.
- Tracks: Claude
- Spec / sources: `MyTradingSys/research/whale_positioning_evidence_2026-09-12.md`; `MyTradingSys/backtest/layers/FORMULAS.md`
- Code: `MyTradingSys/backtest/layers/positioning`
- Latest results: `MyTradingSys/research/OI_DIVERGENCE_V2_2026-10-10.md`; `MyTradingSys/research/OI_EVENT_STUDY_2026-10-10.md`
- Open cards (`tasks.py brief <id>`):
  - `positioning-home-fit-audit` refined p4 SONNET: Home-fit audit of the FlowHorse / whale positioning layer against the readiness checklist

## Session / timing (session levels, turn of candle, session momentum)
- Status: T055 C2/C3 closed; T087 failed prior-day-high fade FAIL.
- Tracks: Claude
- Spec / sources: `MyTradingSys/research/TURN_OF_CANDLE_ORIGIN_2026-10-09.md`
- Code: `MyTradingSys/backtest/layers/session`; `MyTradingSys/backtest/layers/session_levels`; `MyTradingSys/backtest/layers/turn_of_candle`
- Latest results: `MyTradingSys/research/t087_session_levels_2026-10-09`
- Open cards: none

## Volume, candle patterns, daily MA setups, bigtrade
- Status: No validated edge; volume HOLDOUT sealed; MA numbers NO-SOURCE.
- Tracks: Claude
- Spec / sources: `MyTradingSys/backtest/layers/FORMULAS.md`
- Code: `MyTradingSys/backtest/bigtrade`
- Latest results: `MyTradingSys/research/volume_2026-10-09`; `MyTradingSys/research/candle_patterns_2026-10-04`; `MyTradingSys/research/setup_alpha_beta_2026-10-10`; `MyTradingSys/research/bigtrade_2026-10-09`
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
