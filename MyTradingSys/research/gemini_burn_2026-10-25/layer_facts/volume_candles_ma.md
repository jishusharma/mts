# Layer Fact Sheet: volume_candles_ma (re-derived 2026-11-02, card gemini-layer-facts-for-volume-candle-pat)

Every fact below was re-read from a trunk file this turn; the cite is `file:line` (paths under `MyTradingSys/research/` unless stated). Facts that could not be re-derived were deleted (list at the end). No verdicts on keeping, dropping or parking any layer.
Layers covered: `volume`, `candle_patterns`, `ma_daily`, `bigtrade_fires` (`MyTradingSys/system/LAYERS.md:162-182`).

## 0. Windows and fee (trunk truth)
- Repo DEV (SOURCED): 2022-01-01 .. 2024-06-30, VALIDATION 2024-07-01 .. 2025-06-30, HOLDOUT 2025-07-01 sealed (`MyTradingSys/backtest/splits.py:4-6`).
- Repo cost screen (SOURCED): 14 bp round trip (`MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:4`; `MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md:3`; `MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:11`). The bare Deribit taker fee is 10 bp round trip before slippage (`MyTradingSys/backtest/fees.py:20`); that is a fee, not the repo cost screen.
- The older studies below ran on their own wider DEV start 2020-01-01 (volume V1 header `MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md:1`; candle P0 `MyTradingSys/research/candle_patterns_2026-10-04/P0_RESULTS.md:3`). That is OURS per study and differs from the repo DEV start 2022-01-01; their numbers are not on the repo DEV window.

## 1. volume
### ORIGIN
- Operator ask: research what "volume cannot be hidden" gives MTS; session MTS-2026-10-09-APP-ANA-btc-volume (`MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:3`). Trader association / ledger: NOT_IN_DATA.
- Finding: "Volume is not hidden, but what it reveals is intensity, not direction." corr with move size 0.42-0.49, next-bar return corr 0.01-0.04 (`MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:12`).
### PARAMETERS
- Market: Binance USDT-M BTCUSDT perp, 1d and 1h from 2020-01-01 to 2026-09-30, 4h built from 1h (SOURCED, `MyTradingSys/research/volume_2026-10-09/PRE_REG_VOLUME_2026-10-09.md:21`).
- Cost: 14 bp round trip plus funding (OURS, `MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md:3`).
- Study DEV 2020-01-01 .. 2024-06-30 (OURS, `MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md:1`); VALIDATION 2024-07-01 .. 2025-06-30; HOLDOUT 2025-07-01 .. 2026-09-30 sealed (`MyTradingSys/research/volume_2026-10-09/PRE_REG_VOLUME_2026-10-09.md:23-24`).
### BACKTESTS (all net of 14 bp + funding)
1. Overall: 553 pre-registered trials, 1 marginal pass that failed VALIDATION (net -2 bp on 50 events vs +70 bp on DEV), 0 usable survivors; HOLDOUT never opened (`MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:9-11`).
2. V1 event study, 1d: 216 trials (96 live, 120 INSUFFICIENT-N), 0 pass triage (`MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md:5`).
3. V2 state family, daily: 96 trials (84 live, 12 INSUFFICIENT-N), 0 pass triage (`MyTradingSys/research/volume_2026-10-09/V2_DEV_RESULTS.md:3`).
4. V3 VALIDATION: candidate R40D_N n = 50 events, net -2 bp [-68, +64], min n 100; verdict INSUFFICIENT-N (`MyTradingSys/research/volume_2026-10-09/V3_VALIDATION_RESULTS.md:5-11`).
5. V4 pooled volume-confirmation premium, 4h h=18: DEV +88 bp (p 0.008, descriptive, not a test) vs VALIDATION -13 bp (p 0.597); NOT SUPPORTED (`MyTradingSys/research/volume_2026-10-09/V4_RESULTS.md:7-9`).
### KNOWN BUGS / ASSUMPTIONS
- Plain relative volume is biased by time of day; with a 20-bar baseline 36% of 12-16 UTC 4h bars look like 2x spikes vs 6% of 04-08 UTC (`MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:13`).
### CONFLUENCE
- Layer review class: "Cross-guidance, volume, candle patterns, ma_daily, bigtrade | DEAD | no cell survives" (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:33`). Nothing combines on a live trade today (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:8`).

## 2. candle_patterns
### ORIGIN
- Operator rule P0: the daily-level rule "long the previous candle's daily open when price goes up past it" (`MyTradingSys/research/candle_patterns_2026-10-04/CANDLE_PATTERNS_RESEARCH_2026-10-04.md:6`); P1: 18 classical directional patterns plus three volatility-state candles (`MyTradingSys/research/candle_patterns_2026-10-04/CANDLE_PATTERNS_RESEARCH_2026-10-04.md:7`). Trader association / ledger: NOT_IN_DATA.
### PARAMETERS
- Data: Binance USDT-M BTCUSDT perp; daily 2020-01-01..2024-06-30 (1643 bars), hourly from 1m 2022-01-01..2024-06-30 (21888 bars) (SOURCED, `MyTradingSys/research/candle_patterns_2026-10-04/CANDLE_PATTERNS_RESEARCH_2026-10-04.md:16-17`).
- P0 costs: 5 bps fee + 2 bps slip per side plus realised funding (OURS, `MyTradingSys/research/candle_patterns_2026-10-04/P0_RESULTS.md:3`). P1 cost: 14 bps plus funding (OURS, `MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md:3`).
### BACKTESTS
1. P0 (EXPLORATORY): P0a 571 trades, win 35.7%, net -0.7 bps/trade, Sharpe -0.01, p vs random null 0.789; P0c 364 trades, win 29.7%, net -8.1 bps, Sharpe -0.14 (`MyTradingSys/research/candle_patterns_2026-10-04/P0_RESULTS.md:8-9`).
2. P1: 54 trials per timeframe on 1d and 1h (18 INSUFFICIENT-N on 1d, 6 on 1h); "Pass triage: NONE" (`MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md:7,75,144`).
3. D19 4h bullish engulfing, NO-SOURCE, data 2022-01-01..2026-10-02: n 192, net R 0.2255 (0.05pct side) / 0.1295 (0.10pct side) vs buy-and-hold 1.6072 (`MyTradingSys/research/candle_patterns_2026-10-04/D19_4H_RESULTS.md:1-8`).
4. Candle-close sequences: 0 of 126 pooled arms pass; 105,541 event rows on 1,313,280 1m bars Jan 2022-Jun 2024; every pooled arm negative after the 14 bp screen, -26.83 to -4.68 bp/event (`MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:3,7,11`).
### CONFLUENCE
- Same DEAD row as volume (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:33`).

## 3. ma_daily
### ORIGIN
- Operator pasted a "Setup Alpha / Setup Beta" chatbot handoff; filed NO-SOURCE (`MyTradingSys/research/BUGS.md:276`, B163 OPEN; `MyTradingSys/system/LAYERS.md:166`). Trader association / ledger: NOT_IN_DATA.
### PARAMETERS
- Daily long-flat SMA200 variants, Binance BTCUSDT 1d, fee 0.05% per side plus funding (`MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:3`). Variant A: SMA200+EMA7+RSI2>ADX2 (`MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:8`). All indicator choices are OURS / NO-SOURCE (chatbot handoff, not a trader transcript).
### BACKTESTS
1. Alpha variant A: CAGR 20.53%, maxDD 49.41%, 42 trades vs buy-and-hold CAGR 43.83%, maxDD 76.67% (`MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:8,11`). NO-SOURCE, not a result.
2. Beta (liquidity sweep + CVD absorption, 15m levels / 5m entry, fee 0.05%/side): all sessions no CVD n 708240, avg R -0.030; with CVD n 628978, avg R -0.024 (`MyTradingSys/research/setup_alpha_beta_2026-10-10/BETA_RESULTS.md:4,9-10`).
### CONFLUENCE
- Layer review role CONTEXT; class DEAD (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:33`).

## 4. bigtrade_fires
### ORIGIN
- Internal replay and benchmarking harness (parity replay of the 19 kline live layers); no trader association: NOT_IN_DATA.
### PARAMETERS
- Data: merged 1m BTCUSDT klines 2022-01-01..2026-10-07 UTC, 2507040 bars (= 1741 days x 1440), 0 gaps (SOURCED, `MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md:7`).
- Exit-policy cost: 10.0 bp RT taker + 2.0 bp slippage = 12 bp (assumed, OURS; not the repo 14 bp screen) (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:7,144`). Six exit policy names (OURS): live_like_1pct_2pct_8bars, bracket_1atr_2atr_24, bracket_1.5atr_3atr_24, time_24_wide_stop_2atr, time_96_wide_stop_2atr, be1atr_trail2atr_96 (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:28-38`).
### BACKTESTS
1. FIRES-B1: 19 live kline keys replayed, 244,543 fires (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:14`); parity PASS on spot rerun (`MyTradingSys/system/LAYERS.md:174`).
2. BIGTRADE-EXIT: 114 cells run, 1 positive in both splits (cryptocred sr_flip 1h, +9.8 bp TRAIN, +0.1 bp VALIDATE, n 1024 / 163); "No exit policy rescues the existing fires" (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:138-143`).
### KNOWN BUGS
- The report is flagged CONTAMINATED: its TRAIN column ran to 2025-01-01 and so includes VALIDATION 2024-07..12 (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:3`). DEV-only rerun: `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_RERUN_DEV_2026-10-17.md`.
- The CAPTURE-MATRIX SYNTHETIC variant is a tool fixture, not layer output (`MyTradingSys/system/LAYERS.md:175`).
### CONFLUENCE
- Same DEAD row (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:33`).

## Deleted (could not be re-derived)
Invented quotes (volume windows 20/40/60, thresholds 1.5/2.0/2.5, horizons, direction by body sign; 18-pattern name list; alpha/beta parameter quotes; "10 bps fee floor"); wrong window (DEV 2022-01..2025-06); PLAN.md and beta_backtest.py cites (files absent); the "94-97% of testnet trades end on time exits" claim, ATR zigzag leg counts, and the "Cherry-Picked Parameters" and "Low Base-Rate Friction" rulings (no matching text in source).
