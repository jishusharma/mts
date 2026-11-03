FOUND: 58 | DIFF: 0 | NOT_IN_DATA: 0 (58 rows checked)

# Blind Read of volume_candles_ma Layer Facts Sheet (Sections 0 and 1: Windows, Fees, Volume)

- **Task**: `gemini-blind-read-volume-candles-facts-1103`
- **Lane**: `CODEX`
- **Audited Target**: `MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/volume_candles_ma.md` (Sections 0 and 1, lines 6-28; commit `46ee60ea8954`)
- **Comparison Sources**:
  - `MyTradingSys/backtest/splits.py:4-6`
  - `MyTradingSys/backtest/fees.py:20`
  - `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md`
  - `MyTradingSys/research/volume_2026-10-09/PRE_REG_VOLUME_2026-10-09.md`
  - `MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md`
  - `MyTradingSys/research/volume_2026-10-09/V2_DEV_RESULTS.md`
  - `MyTradingSys/research/volume_2026-10-09/V3_VALIDATION_RESULTS.md`
  - `MyTradingSys/research/volume_2026-10-09/V4_RESULTS.md`
  - `MyTradingSys/research/candle_patterns_2026-10-04/P0_RESULTS.md`
  - `MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md`
  - `MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md`
  - `MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md`
- **Auditor**: Gemini 3.8 Flash Medium worker (Antigravity JIS-NUC)
- **Date**: 2026-11-03 (UTC)

---

## Summary Counts

- **Total Cited Numbers / Values Audited**: 58
- **FOUND**: 58
- **DIFF**: 0
- **NOT_IN_DATA**: 0

---

## Detailed Audit Table

| # | Section / Fact Sheet Line | Quoted Value / Claim | Context in Fact Sheet | Source File:Line | Value / Quote in Source | Status | Notes |
|---|---|---|---|---|---|---|---|
| 1 | L7 (Sec 0) | `2022-01-01` | Repo DEV start (SOURCED: `volume_candles_ma.md:7`) | `MyTradingSys/backtest/splits.py:4` | `DEV 2022-01-01 .. 2024-07-01 (last DEV bar 2024-06-30 23:59)` | FOUND | Exact start date match |
| 2 | L7 (Sec 0) | `2024-06-30` | Repo DEV inclusive end (SOURCED: `volume_candles_ma.md:7`) | `MyTradingSys/backtest/splits.py:4,8` | `(last DEV bar 2024-06-30 23:59)` and `DEV (2022-01-01..2024-06-30)` | FOUND | Exact inclusive end date match |
| 3 | L7 (Sec 0) | `2024-07-01` | Repo VALIDATION start (SOURCED: `volume_candles_ma.md:7`) | `MyTradingSys/backtest/splits.py:5` | `VALIDATION 2024-07-01 .. 2025-07-01 (read once, under a PRE_REG)` | FOUND | Exact start date match |
| 4 | L7 (Sec 0) | `2025-06-30` | Repo VALIDATION inclusive end (SOURCED: `volume_candles_ma.md:7`) | `MyTradingSys/backtest/splits.py:5,9` | `VALIDATION (2024-07-01..2025-06-30)` (L9 quote of OPERATOR_DECISIONS.md) | FOUND | Exact inclusive end date match |
| 5 | L7 (Sec 0) | `2025-07-01` | Repo HOLDOUT start sealed (SOURCED: `volume_candles_ma.md:7`) | `MyTradingSys/backtest/splits.py:6` | `HOLDOUT 2025-07-01 .. (sealed; read once, logged)` | FOUND | Exact start date match |
| 6 | L8 (Sec 0) | `14 bp` | Repo cost screen (SOURCED: `volume_candles_ma.md:8`) | `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:4` | `Method: MTS protocol (pre-register, DEV / VALIDATION / sealed HOLDOUT, 14 bp costs + funding,` | FOUND | Exact cost match |
| 7 | L8 (Sec 0) | `14 bp` | Repo cost screen in candle P1 (SOURCED: `volume_candles_ma.md:8`) | `MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md:3` | `Net = sign*fwd - 14 bps - sign*realised funding.` | FOUND | Exact cost match |
| 8 | L8 (Sec 0) | `14 bp` | Repo cost screen in candle close (SOURCED: `volume_candles_ma.md:8`) | `MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:11` | `Every pooled arm has negative mean after the fixed 14bp round-trip cost screen, ranging from -26.83 to -4.68 bp/event.` | FOUND | Exact cost match |
| 9 | L8 (Sec 0) | `10 bp` | Bare Deribit taker fee round trip before slippage (SOURCED: `volume_candles_ma.md:8`) | `MyTradingSys/backtest/fees.py:20` | `A all-taker Deribit 10 bp round trip (2 x DERIBIT_TAKER), before slippage` | FOUND | Exact match |
| 10 | L9 (Sec 0) | `2020-01-01` | Wider DEV start in volume V1 header (SOURCED: `volume_candles_ma.md:9`) | `MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md:1` | `# V1 DEV RESULTS - BTC volume event study (run V1-2026-10-09, DEV 2020-01-01 .. 2024-06-30)` | FOUND | Exact match |
| 11 | L9 (Sec 0) | `2020-01-01` | Wider DEV start in candle P0 (SOURCED: `volume_candles_ma.md:9`) | `MyTradingSys/research/candle_patterns_2026-10-04/P0_RESULTS.md:3` | `DEV 2020-01-01..2024-06-30 daily UTC bars, Binance BTCUSDT perp.` | FOUND | Exact match |
| 12 | L9 (Sec 0) | `2022-01-01` | Repo DEV start comparison baseline (SOURCED: `volume_candles_ma.md:9`) | `MyTradingSys/backtest/splits.py:4` | `DEV 2022-01-01 .. 2024-07-01` | FOUND | Exact match |
| 13 | L13 (Sec 1 ORIGIN) | `MTS-2026-10-09-APP-ANA-btc-volume` | Operator ask session identifier (SOURCED: `volume_candles_ma.md:13`) | `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:3` | `Session MTS-2026-10-09-APP-ANA-btc-volume (App, JIS-NUC work tree, Sonnet 5.5).` | FOUND | Exact session string match |
| 14 | L14 (Sec 1 ORIGIN) | `0.42-0.49` | Correlation with move size (SOURCED: `volume_candles_ma.md:14`) | `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:12` | `strongly tied to the size of the move (corr 0.42-0.49)` | FOUND | Exact range match |
| 15 | L14 (Sec 1 ORIGIN) | `0.01-0.04` | Next-bar return correlation (SOURCED: `volume_candles_ma.md:14`) | `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:13` | `not its direction (corr with next-bar return 0.01-0.04).` | FOUND | Exact range match (Item 2 text spans L12-13) |
| 16 | L16 (Sec 1 PARAMETERS) | `1d` | Market timeframe 1d (SOURCED: `volume_candles_ma.md:16`) | `MyTradingSys/research/volume_2026-10-09/PRE_REG_VOLUME_2026-10-09.md:21` | `- 1d and 1h: 2020-01-01 .. 2026-09-30` | FOUND | Exact match |
| 17 | L16 (Sec 1 PARAMETERS) | `1h` | Market timeframe 1h (SOURCED: `volume_candles_ma.md:16`) | `MyTradingSys/research/volume_2026-10-09/PRE_REG_VOLUME_2026-10-09.md:21` | `- 1d and 1h: 2020-01-01 .. 2026-09-30` | FOUND | Exact match |
| 18 | L16 (Sec 1 PARAMETERS) | `2020-01-01` | Data start date (SOURCED: `volume_candles_ma.md:16`) | `MyTradingSys/research/volume_2026-10-09/PRE_REG_VOLUME_2026-10-09.md:21` | `- 1d and 1h: 2020-01-01 .. 2026-09-30` | FOUND | Exact match |
| 19 | L16 (Sec 1 PARAMETERS) | `2026-09-30` | Data end date (SOURCED: `volume_candles_ma.md:16`) | `MyTradingSys/research/volume_2026-10-09/PRE_REG_VOLUME_2026-10-09.md:21` | `- 1d and 1h: 2020-01-01 .. 2026-09-30` | FOUND | Exact match |
| 20 | L16 (Sec 1 PARAMETERS) | `4h` | 4h constructed from 1h (SOURCED: `volume_candles_ma.md:16`) | `MyTradingSys/research/volume_2026-10-09/PRE_REG_VOLUME_2026-10-09.md:21` | `4h = 4 consecutive 1h bars at 00/04/08/12/16/20 UTC, complete buckets only.` | FOUND | Exact match |
| 21 | L17 (Sec 1 PARAMETERS) | `14 bp` | Cost: round trip plus funding (OURS / SOURCED: `volume_candles_ma.md:17`) | `MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md:3` | `Net = sign*fwd - 14 bps - sign*funding in (entry, exit].` | FOUND | Exact match |
| 22 | L18 (Sec 1 PARAMETERS) | `2020-01-01 .. 2024-06-30` | Study DEV window (OURS / SOURCED: `volume_candles_ma.md:18`) | `MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md:1` | `# V1 DEV RESULTS - BTC volume event study (run V1-2026-10-09, DEV 2020-01-01 .. 2024-06-30)` | FOUND | Exact match |
| 23 | L18 (Sec 1 PARAMETERS) | `2024-07-01 .. 2025-06-30` | Study VALIDATION window (SOURCED: `volume_candles_ma.md:18`) | `MyTradingSys/research/volume_2026-10-09/PRE_REG_VOLUME_2026-10-09.md:23` | `VALIDATION: 2024-07-01 .. 2025-06-30 (run once per frozen candidate set).` | FOUND | Exact match |
| 24 | L18 (Sec 1 PARAMETERS) | `2025-07-01 .. 2026-09-30` | Study HOLDOUT sealed window (SOURCED: `volume_candles_ma.md:18`) | `MyTradingSys/research/volume_2026-10-09/PRE_REG_VOLUME_2026-10-09.md:23-24` | `HOLDOUT: 2025-07-01 .. 2026-09-30, sealed; the loader refuses it without unseal=True` | FOUND | Exact match |
| 25 | L20 (Sec 1 BACKTESTS) | `553` | Pre-registered trials count (SOURCED: `volume_candles_ma.md:20`) | `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:9` | `553 pre-registered trials (event studies, state variables, contrasts, time hypotheses; DEV first, VALIDATION for survivors)` | FOUND | Exact match |
| 26 | L20 (Sec 1 BACKTESTS) | `1` | Marginal pass count that failed VALIDATION (SOURCED: `volume_candles_ma.md:20`) | `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:9` | `produced 1 marginal pass` | FOUND | Exact match |
| 27 | L20 (Sec 1 BACKTESTS) | `-2 bp` | Net return on VALIDATION (SOURCED: `volume_candles_ma.md:20`) | `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:10` | `that one failed VALIDATION (net -2 bp on 50 events vs +70 bp on DEV).` | FOUND | Exact match |
| 28 | L20 (Sec 1 BACKTESTS) | `50` | Events count on VALIDATION (SOURCED: `volume_candles_ma.md:20`) | `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:10` | `net -2 bp on 50 events vs +70 bp on DEV` | FOUND | Exact match |
| 29 | L20 (Sec 1 BACKTESTS) | `+70 bp` | Net return on DEV (SOURCED: `volume_candles_ma.md:20`) | `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:10` | `net -2 bp on 50 events vs +70 bp on DEV` | FOUND | Exact match |
| 30 | L20 (Sec 1 BACKTESTS) | `0` | Usable survivors count (SOURCED: `volume_candles_ma.md:20`) | `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:10` | `and 0 usable survivors: that one failed VALIDATION` | FOUND | Exact match |
| 31 | L21 (Sec 1 BACKTESTS) | `1d` | V1 event study timeframe (SOURCED: `volume_candles_ma.md:21`) | `MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md:5` | `## 1d: 1472 bars in range, 216 trials (96 live, 120 INSUFFICIENT-N), **0 pass triage**` | FOUND | Exact match |
| 32 | L21 (Sec 1 BACKTESTS) | `216` | V1 total trials (SOURCED: `volume_candles_ma.md:21`) | `MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md:5` | `216 trials (96 live, 120 INSUFFICIENT-N)` | FOUND | Exact match |
| 33 | L21 (Sec 1 BACKTESTS) | `96` | V1 live trials (SOURCED: `volume_candles_ma.md:21`) | `MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md:5` | `(96 live, 120 INSUFFICIENT-N)` | FOUND | Exact match |
| 34 | L21 (Sec 1 BACKTESTS) | `120` | V1 INSUFFICIENT-N trials (SOURCED: `volume_candles_ma.md:21`) | `MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md:5` | `(96 live, 120 INSUFFICIENT-N)` | FOUND | Exact match |
| 35 | L21 (Sec 1 BACKTESTS) | `0` | V1 pass triage count (SOURCED: `volume_candles_ma.md:21`) | `MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md:5` | `**0 pass triage**` | FOUND | Exact match |
| 36 | L22 (Sec 1 BACKTESTS) | `96` | V2 daily state trials count (SOURCED: `volume_candles_ma.md:22`) | `MyTradingSys/research/volume_2026-10-09/V2_DEV_RESULTS.md:3` | `96 trials (84 live, 12 INSUFFICIENT-N), **0 pass triage**` | FOUND | Exact match |
| 37 | L22 (Sec 1 BACKTESTS) | `84` | V2 live trials count (SOURCED: `volume_candles_ma.md:22`) | `MyTradingSys/research/volume_2026-10-09/V2_DEV_RESULTS.md:3` | `(84 live, 12 INSUFFICIENT-N)` | FOUND | Exact match |
| 38 | L22 (Sec 1 BACKTESTS) | `12` | V2 INSUFFICIENT-N count (SOURCED: `volume_candles_ma.md:22`) | `MyTradingSys/research/volume_2026-10-09/V2_DEV_RESULTS.md:3` | `(84 live, 12 INSUFFICIENT-N)` | FOUND | Exact match |
| 39 | L22 (Sec 1 BACKTESTS) | `0` | V2 pass triage count (SOURCED: `volume_candles_ma.md:22`) | `MyTradingSys/research/volume_2026-10-09/V2_DEV_RESULTS.md:3` | `**0 pass triage**` | FOUND | Exact match |
| 40 | L23 (Sec 1 BACKTESTS) | `n = 50` | Candidate R40D_N event count (SOURCED: `volume_candles_ma.md:23`) | `MyTradingSys/research/volume_2026-10-09/V3_VALIDATION_RESULTS.md:9` | `| 50 | +14 | -2 [-68, +64] | 52% | -1 | 0.523 | 100 |` | FOUND | Exact match |
| 41 | L23 (Sec 1 BACKTESTS) | `-2 bp` | Candidate R40D_N net return (SOURCED: `volume_candles_ma.md:23`) | `MyTradingSys/research/volume_2026-10-09/V3_VALIDATION_RESULTS.md:9` | `-2 [-68, +64]` | FOUND | Exact match |
| 42 | L23 (Sec 1 BACKTESTS) | `[-68, +64]` | Candidate R40D_N 95% CI (SOURCED: `volume_candles_ma.md:23`) | `MyTradingSys/research/volume_2026-10-09/V3_VALIDATION_RESULTS.md:9` | `[-68, +64]` | FOUND | Exact match |
| 43 | L23 (Sec 1 BACKTESTS) | `min n 100` | Registered min sample size threshold (SOURCED: `volume_candles_ma.md:23`) | `MyTradingSys/research/volume_2026-10-09/V3_VALIDATION_RESULTS.md:9,11` | `min n (registered) 100` and `n < 100: registered rule cannot be met` | FOUND | Exact match |
| 44 | L24 (Sec 1 BACKTESTS) | `4h` | V4 pooled premium timeframe (SOURCED: `volume_candles_ma.md:24`) | `MyTradingSys/research/volume_2026-10-09/V4_RESULTS.md:5` | `## 4h (h = 18)` | FOUND | Exact match |
| 45 | L24 (Sec 1 BACKTESTS) | `h=18` | V4 evaluation horizon (SOURCED: `volume_candles_ma.md:24`) | `MyTradingSys/research/volume_2026-10-09/V4_RESULTS.md:5` | `## 4h (h = 18)` | FOUND | Exact match |
| 46 | L24 (Sec 1 BACKTESTS) | `+88 bp` | DEV VCP premium (SOURCED: `volume_candles_ma.md:24`) | `MyTradingSys/research/volume_2026-10-09/V4_RESULTS.md:7` | `DEV (descriptive prior, NOT a test...): VCP +88 bp [+15, +155]` | FOUND | Exact match |
| 47 | L24 (Sec 1 BACKTESTS) | `p 0.008` | DEV one-sided p-value (SOURCED: `volume_candles_ma.md:24`) | `MyTradingSys/research/volume_2026-10-09/V4_RESULTS.md:7` | `one-sided p=0.008, pairs positive 5/6` | FOUND | Exact match |
| 48 | L24 (Sec 1 BACKTESTS) | `-13 bp` | VALIDATION VCP premium (SOURCED: `volume_candles_ma.md:24`) | `MyTradingSys/research/volume_2026-10-09/V4_RESULTS.md:8` | `**VALIDATION (the test)**: VCP -13 bp [-109, +81]` | FOUND | Exact match |
| 49 | L24 (Sec 1 BACKTESTS) | `p 0.597` | VALIDATION one-sided p-value (SOURCED: `volume_candles_ma.md:24`) | `MyTradingSys/research/volume_2026-10-09/V4_RESULTS.md:8` | `one-sided p=0.597, pairs positive 3/6` | FOUND | Exact match |
| 50 | L26 (Sec 1 BUGS) | `20-bar` | Plain relative volume baseline window (SOURCED: `volume_candles_ma.md:26`) | `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:14` | `With a plain 20-bar baseline, 36% of 12-16 UTC 4h bars look like "2x volume spikes"` | FOUND | Exact match (cited L13 is item 3 header; text at L14-15) |
| 51 | L26 (Sec 1 BUGS) | `36%` | Peak slot spike proportion (SOURCED: `volume_candles_ma.md:26`) | `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:14` | `36% of 12-16 UTC 4h bars look like "2x volume spikes"` | FOUND | Exact match |
| 52 | L26 (Sec 1 BUGS) | `12-16 UTC` | Peak intraday slot (SOURCED: `volume_candles_ma.md:26`) | `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:14` | `36% of 12-16 UTC 4h bars look like "2x volume spikes"` | FOUND | Exact match |
| 53 | L26 (Sec 1 BUGS) | `4h` | Bar timeframe for time bias (SOURCED: `volume_candles_ma.md:26`) | `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:14` | `12-16 UTC 4h bars` | FOUND | Exact match |
| 54 | L26 (Sec 1 BUGS) | `2x` | Spike threshold multiple (SOURCED: `volume_candles_ma.md:26`) | `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:14` | `"2x volume spikes"` | FOUND | Exact match |
| 55 | L26 (Sec 1 BUGS) | `6%` | Trough slot spike proportion (SOURCED: `volume_candles_ma.md:26`) | `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:15` | `vs 6% of 04-08 UTC bars;` | FOUND | Exact match |
| 56 | L26 (Sec 1 BUGS) | `04-08 UTC` | Trough intraday slot (SOURCED: `volume_candles_ma.md:26`) | `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:15` | `vs 6% of 04-08 UTC bars;` | FOUND | Exact match |
| 57 | L28 (Sec 1 CONFLUENCE) | `DEAD` | Integration map layer review classification (SOURCED: `volume_candles_ma.md:28`) | `MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:33` | `\| Cross-guidance, volume, candle patterns, ma_daily, bigtrade \| DEAD \| no cell survives (:22) \| CONTEXT \| no \|` | FOUND | Exact match |
| 58 | L28 (Sec 1 CONFLUENCE) | `0` live trades combining | Live trade combining status (SOURCED: `volume_candles_ma.md:28`) | `MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:8` | `- Nothing combines on a live trade. promoted_setups.json ships empty (LAYER_REALITY_2026-10-25.md:2; MAINNET_PATH_2026-10-25.md:8).` | FOUND | Exact match |
