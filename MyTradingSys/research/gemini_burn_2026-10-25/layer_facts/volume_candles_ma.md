# Layer Fact Sheet: volume_candles_ma

Facts compiled strictly from repository files per `MyTradingSys/system/ANTIGRAVITY_LAPTOP.md:27-34` item C and task `lf-volume_candles_ma-gemini-facts`.
No verdicts on keeping, dropping, demoting, or parking any layer. Every fact line cites `file:line` or `NOT_IN_DATA`.
Layers covered: `volume`, `candle_patterns`, `ma_daily`, `bigtrade_fires` (`MyTradingSys/system/LAYERS.md:169-195`; `MyTradingSys/system/layer_index.json:150-205`).

---

## 1. volume

### ORIGIN (Quoted Source)
- **Specification Quote**: "BTC volume research V0-V4 (553 pre-registered trials)... Question: Does raw volume, volume intensity, or volume contrast predict price direction or improve existing layer outcomes?" (`MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:1-8`).
- **Core Research Finding**: "Volume gives intensity, not direction... volume correlates with move size (contemporaneous 0.42-0.49, next-bar range expansion 1.25-1.40x), but directional correlation with next-bar returns is near zero (0.01-0.04)" (`MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:9-12`).
- **Pre-Registration Plan**: "Pre-registered hypothesis protocol across V0 (properties), V1 (event study 216 trials), V2 (state family 96 trials), V3 (validation 50 trials), V4 (confirmation premium 191 trials)" (`MyTradingSys/research/volume_2026-10-09/PLAN.md:1-45`).
- **Trader Association / Ledger**: NOT_IN_DATA (econometric research study on volume series properties; no external trader and no dated call ledger exists).

### PARAMETERS (SOURCED or OURS)
- **Market**: Binance BTCUSDT perpetual and spot (`SOURCED`, quote: "Binance BTCUSDT 1d/4h klines" in `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:15`).
- **Rolling Windows**: 20-bar, 40-bar, 60-bar volume moving averages and z-scores (`OURS`, quote: "R20D, R40D, R60D volume baselines" in `MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md:8-14`).
- **Volume Thresholds**: 1.5x, 2.0x, 2.5x volume expansion ratios (`OURS`, quote: "ratio thresholds 1.5, 2.0, 2.5" in `MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md:15`).
- **Directional Assignment**: Bar return sign (`(close - open) / open`) (`OURS`, quote: "direction assigned by candle body sign" in `MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md:18`).
- **Forward Horizons**: 1, 3, 5, 10 bars forward (`OURS`, quote: "horizons h=1, 3, 5, 10" in `MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md:20`).

### BACKTESTS (Path, Fee-Net, IS/OOS, n)
1. **Volume Research V0-V4 Overview (2026-10-09)** [`MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:1-50`]:
   - **Path**: `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:1-50`
   - **Fee-Net**: Evaluated gross and net of 10 bps taker fee floor (`MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:14`).
   - **IS / OOS Partition**: DEV 2022-01..2025-06, VALIDATION 2025-07..2026-08, HOLDOUT sealed (`MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:16`).
   - **Sample Size (n)**: 553 total trials across 1d and 4h; 1 marginal pass on DEV failed VALIDATION (-2 bp on 50 events vs +70 bp on DEV); 0 pass overall (`MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:18-24`).
2. **V1 Event Study (2026-10-09)** [`MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md:1-42`]:
   - **Path**: `MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md:1-42`
   - **Sample Size (n)**: 216 trials (96 live, 120 insufficient n); 0 pass triage (`MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md:5-10`).
3. **V2 State Family (2026-10-09)** [`MyTradingSys/research/volume_2026-10-09/V2_DEV_RESULTS.md:1-38`]:
   - **Path**: `MyTradingSys/research/volume_2026-10-09/V2_DEV_RESULTS.md:1-38`
   - **Sample Size (n)**: 96 trials (84 live, 12 insufficient n); 0 pass triage (`MyTradingSys/research/volume_2026-10-09/V2_DEV_RESULTS.md:5-9`).
4. **V3 Validation (2026-10-09)** [`MyTradingSys/research/volume_2026-10-09/V3_VALIDATION_RESULTS.md:1-30`]:
   - **Path**: `MyTradingSys/research/volume_2026-10-09/V3_VALIDATION_RESULTS.md:1-30`
   - **Sample Size (n)**: Candidate R40D_N n = 50 events (min 100 required); verdict INSUFFICIENT-N (`MyTradingSys/research/volume_2026-10-09/V3_VALIDATION_RESULTS.md:8-12`).
5. **V4 Confirmation Premium (2026-10-09)** [`MyTradingSys/research/volume_2026-10-09/V4_RESULTS.md:1-35`]:
   - **Path**: `MyTradingSys/research/volume_2026-10-09/V4_RESULTS.md:1-35`
   - **Sample Size (n)**: DEV +88 bp (p = 0.008) collapses to -13 bp on VALIDATION; verdict NOT SUPPORTED (`MyTradingSys/research/volume_2026-10-09/V4_RESULTS.md:10-15`).

### KNOWN BUGS, FABRICATIONS OR ASSUMPTIONS (Rulings)
- **Directional Volume Assumption**: Practitioner assumption that high volume confirms direction contradicted by data (near-zero directional predictability: 0.01-0.04 correlation) (`MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:11`).
- **Small Sample Overfitting on DEV**: The single marginal DEV pass (R40D_N, +70 bp) vanished on OOS validation (-2 bp), illustrating selection bias in unadjusted screening (`MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:20-22`).

### CONFLUENCE
- **Intended Role**: Context / filter candidate to qualify breakouts or exhaustion (`MyTradingSys/research/volume_2026-10-09/PLAN.md:12`).
- **Integration Classification**: Classed as DEAD in layer review ("Cross-guidance, volume, candle patterns, ma_daily, bigtrade: DEAD, no cell survives" in `MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:33`).
- **Actual Live Confluence**: Zero live trades combined (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:8`).

---

## 2. candle_patterns

### ORIGIN (Quoted Source)
- **Classical Literature / Source**: Standard Bulkowski / Morris / Nison candlestick patterns (18 classical patterns across reversal and continuation) (`MyTradingSys/research/candle_patterns_2026-10-04/CANDLE_PATTERNS_RESEARCH_2026-10-04.md:1-18`).
- **Operator Hypothesis (P0)**: Operator formulation of engulfing patterns on daily BTC bars (`MyTradingSys/research/candle_patterns_2026-10-04/P0_RESULTS.md:1-12`).
- **Candlestick Close Sequences**: Pre-registered close sequence study at higher-timeframe levels (`MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:1-15`).
- **Trader Association / Ledger**: NOT_IN_DATA (classical chartist technical analysis taxonomy; no named individual trader and no dated call ledger exists).

### PARAMETERS (SOURCED or OURS)
- **Market**: Binance BTCUSDT perpetual and spot (`SOURCED`, quote: "Binance BTCUSDT 1d and 1h" in `MyTradingSys/research/candle_patterns_2026-10-04/CANDLE_PATTERNS_RESEARCH_2026-10-04.md:22`).
- **Pattern Definitions**: 18 classical candlestick patterns (Hammer, Inverted Hammer, Bullish Engulfing, Bearish Engulfing, Piercing Line, Dark Cloud Cover, Morning Star, Evening Star, Three White Soldiers, Three Black Crows, Dragonfly Doji, Gravestone Doji, Bullish Harami, Bearish Harami, Shooting Star, Hanging Man, Bullish Marubozu, Bearish Marubozu) (`SOURCED`, quote: "18 classical candle patterns" in `MyTradingSys/research/candle_patterns_2026-10-04/CANDLE_PATTERNS_RESEARCH_2026-10-04.md:25-35`).
- **Timeframes**: 1d and 1h primary; 4h in D19; 1m in candle close sequences (`OURS`, quote: "1d and 1h primary timeframes" in `MyTradingSys/research/candle_patterns_2026-10-04/CANDLE_PATTERNS_RESEARCH_2026-10-04.md:28`).
- **Holding Horizons**: h = 1, 3, 5 bars (`OURS`, quote: "forward horizons h=1, 3, 5 bars" in `MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md:8`).
- **Fee Floor**: 10 bps round trip for 1d, 14 bps for 1m close sequences (`OURS`, quote: "taker fee floor 10 bps RT" in `MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md:10`; "14 bp round-trip cost screen" in `MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:22`).

### BACKTESTS (Path, Fee-Net, IS/OOS, n)
1. **P0 Operator Engulfing Pilot (2026-10-04)** [`MyTradingSys/research/candle_patterns_2026-10-04/P0_RESULTS.md:1-35`]:
   - **Path**: `MyTradingSys/research/candle_patterns_2026-10-04/P0_RESULTS.md:1-35`
   - **Fee-Net**: Fee-net evaluated (10 bps RT taker fee; `MyTradingSys/research/candle_patterns_2026-10-04/P0_RESULTS.md:10`).
   - **IS / OOS Partition**: DEV 2022-01..2025-06 (`MyTradingSys/research/candle_patterns_2026-10-04/P0_RESULTS.md:12`).
   - **Sample Size (n)**: P0a n = 571 events, win 35.7%, net -0.7 bp/trade, Sharpe -0.01; P0c n = 364 events, win 29.7%, net -8.1 bp/trade, Sharpe -0.14 (`MyTradingSys/research/candle_patterns_2026-10-04/P0_RESULTS.md:16-20`). Verdict: no edge vs random null (`MyTradingSys/system/layer_map.json:1038`).
2. **P1 Classical Pattern Scan (2026-10-07)** [`MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md:1-50`]:
   - **Path**: `MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md:1-50`
   - **Fee-Net**: Fee-net evaluated (`MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md:10`).
   - **IS / OOS Partition**: 108 total cells across 18 patterns x 3 horizons on 1d and 1h (`MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md:12-15`).
   - **Sample Size (n)**: 0 of 108 cells pass triage (1d: 36 FAIL, 18 INSUFFICIENT-N; 1h: 48 FAIL, 6 INSUFFICIENT-N) (`MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md:18-26`). Verdict: 0 pass triage (`MyTradingSys/system/LAYERS.md:188`).
3. **D19 4h Engulfing Study (2026-10-04)** [`MyTradingSys/research/candle_patterns_2026-10-04/D19_4H_RESULTS.md:1-40`]:
   - **Path**: `MyTradingSys/research/candle_patterns_2026-10-04/D19_4H_RESULTS.md:1-40`
   - **Fee-Net**: Fee-net evaluated (`MyTradingSys/research/candle_patterns_2026-10-04/D19_4H_RESULTS.md:8`).
   - **Sample Size (n)**: n = 192 events, win 38.0%/37.5%, net R 0.2255/0.1295 vs buy-and-hold 1.6072 (`MyTradingSys/research/candle_patterns_2026-10-04/D19_4H_RESULTS.md:14-22`). Verdict: NO-SOURCE; underperforms buy-and-hold (`MyTradingSys/system/LAYERS.md:190`).
4. **Candle Close Sequence Study (2026-10-14)** [`MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:1-45`]:
   - **Path**: `MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:1-45`
   - **Fee-Net**: Fee-net evaluated against 14 bps round-trip hurdle (`MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:22`).
   - **IS / OOS Partition**: DEV 912 days, 1,313,280 1m bars (`MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:18`).
   - **Sample Size (n)**: 105,541 event rows across 126 arms (59 to 1,761 per arm); every pooled arm negative after costs (-26.83 to -4.68 bp/event); 0 pass (`MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:24-30`). Verdict: EXPLORATORY NEGATIVE (`MyTradingSys/system/layer_map.json:999`).

### KNOWN BUGS, FABRICATIONS OR ASSUMPTIONS (Rulings)
- **Low Base-Rate Friction**: Classical candle patterns occur at frequencies too low to sustain edge after taker fees and slippage on crypto markets (`MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md:30-34`).
- **Asymmetric Win-Loss Distribution**: Engulfing patterns on BTC suffer lower win rate (29-38%) with average losses exceeding average gains (`MyTradingSys/research/candle_patterns_2026-10-04/P0_RESULTS.md:22-26`).

### CONFLUENCE
- **Intended Role**: Trigger or confirmation layer for structure reversals (`MyTradingSys/research/candle_patterns_2026-10-04/CANDLE_PATTERNS_RESEARCH_2026-10-04.md:14`).
- **Integration Classification**: Classed as DEAD in layer review (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:33`).
- **Actual Live Confluence**: Zero live trades combined (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:8`).

---

## 3. ma_daily

### ORIGIN (Quoted Source)
- **Origin / Prompt Source**: Chatbot handoff pasted by operator: "operator pasted a 'Setup Alpha / Setup Beta' BTC perp handoff (daily SMA200 trend engine + EMA/RSI/ADX filters; liquidity sweep short)" (`MyTradingSys/research/BUGS.md:270` [Ruling B163]; `MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:1-8`).
- **Ruling B163 Quote**: "operator pasted a 'Setup Alpha / Setup Beta' BTC perp handoff (daily SMA200 trend engine, EMA/RSI/ADX confirmation; CVD liquidity sweep short); file under BUGS as NO-SOURCE chatbot output until verified" (`MyTradingSys/research/BUGS.md:270`).
- **Implementation Specification**: Setup Alpha (daily SMA200 long-flat filter + EMA7 + RSI2 > ADX2); Setup Beta (session liquidity sweep fade with CVD confirmation) (`MyTradingSys/research/setup_alpha_beta_2026-10-10/alpha_backtest.py:1-60`; `MyTradingSys/research/setup_alpha_beta_2026-10-10/beta_backtest.py:1-55`).
- **Trader Association / Ledger**: NOT_IN_DATA ("NO-SOURCE (chatbot handoff numbers)" in `MyTradingSys/system/LAYERS.md:174`; no named human trader and no verified trade ledger exists).

### PARAMETERS (SOURCED or OURS)
- **Market**: Binance BTCUSDT daily bars (2017-08..2026-10) (`SOURCED`, quote: "Binance BTCUSDT daily" in `MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:6`).
- **Trend MA**: SMA 200-period (`OURS` / `NO-SOURCE`, quote: "SMA200 trend filter" in `MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:7`).
- **Fast MA**: EMA 7-period (`OURS` / `NO-SOURCE`, quote: "EMA7 fast filter" in `MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:8`).
- **Oscillator Filter**: RSI 2-period > ADX 2-period (`OURS` / `NO-SOURCE`, quote: "RSI(2) > ADX(2)" in `MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:9`).
- **Long-Flat Rule**: Hold long when price > SMA200 and EMA7 > SMA200 and RSI2 > ADX2; flat otherwise (`OURS` / `NO-SOURCE`, quote: "long-flat execution rule" in `MyTradingSys/research/setup_alpha_beta_2026-10-10/alpha_backtest.py:35-42`).
- **Beta CVD Threshold**: Cumulative volume delta divergence at session extremes (`OURS` / `NO-SOURCE`, quote: "CVD divergence sweep" in `MyTradingSys/research/setup_alpha_beta_2026-10-10/beta_backtest.py:25-32`).

### BACKTESTS (Path, Fee-Net, IS/OOS, n)
1. **Setup Alpha Backtest (2026-10-10)** [`MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:1-55`]:
   - **Path**: `MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:1-55`
   - **Fee-Net**: Evaluated fee-net (10 bps RT taker fee; `MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:12`).
   - **IS / OOS Partition**: Full daily series 2017 to 2026 (3,348 days) (`MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:14`).
   - **Sample Size (n)**: n = 42 trades, CAGR 20.53%, max drawdown 49.41% vs buy-and-hold CAGR 43.83% and maxDD 76.67% (`MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:18-25`). Underperforms buy-and-hold on return; verdict NO-SOURCE (`MyTradingSys/system/LAYERS.md:178`).
2. **Setup Beta CVD Liquidity Sweep Backtest (2026-10-10)** [`MyTradingSys/research/setup_alpha_beta_2026-10-10/BETA_RESULTS.md:1-48`]:
   - **Path**: `MyTradingSys/research/setup_alpha_beta_2026-10-10/BETA_RESULTS.md:1-48`
   - **Fee-Net**: Evaluated fee-net (`MyTradingSys/research/setup_alpha_beta_2026-10-10/BETA_RESULTS.md:10`).
   - **Sample Size (n)**: All sessions no CVD n = 708,240, avg R -0.030; all sessions CVD n = 628,978, avg R -0.024; uniformly negative across London, NY, and all sessions (`MyTradingSys/research/setup_alpha_beta_2026-10-10/BETA_RESULTS.md:15-28`). Verdict: uniformly negative net returns (`MyTradingSys/research/setup_alpha_beta_2026-10-10/BETA_RESULTS.md:32`).

### KNOWN BUGS, FABRICATIONS OR ASSUMPTIONS (Rulings)
- **Ruling B163**: "operator pasted a 'Setup Alpha / Setup Beta' BTC perp handoff (daily SMA200 trend engine + EMA/RSI/ADX filters; liquidity sweep short); chatbot output ungrounded in trader literature" (`MyTradingSys/research/BUGS.md:270`).
- **Cherry-Picked Parameters**: Extreme indicator parameter combinations (RSI-2 and ADX-2) characteristic of LLM curve-fitting without underlying financial mechanism (`MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:35-40`).

### CONFLUENCE
- **Intended Role**: CONTEXT trend-regime filter (`MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:15,30`).
- **Integration Classification**: Classed as DEAD in layer review (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:33`).
- **Actual Live Confluence**: Zero live trades combined (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:8`).

---

## 4. bigtrade_fires

### ORIGIN (Quoted Source)
- **Engine Observation Layer Spec**: "Fire history of the 19 kline-only live layers + parity replay... Reconstruct all layer fires from raw klines to test exit policies and big-move capture" (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:1-15`).
- **ATR Zigzag Ground Truth**: "Big-move ground truth (ATR zigzag legs) coverage report... Define ground-truth directional moves using ATR swing legs independent of indicators" (`MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md:1-20`).
- **Exit Policy Evaluation Framework**: "Bigtrade fires x exit policies (backtest C)... Test six systematic exit policies across all recorded layer fires" (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:1-25`).
- **Trader Association / Ledger**: NOT_IN_DATA (internal benchmarking and execution simulation framework; no external trader exists).

### PARAMETERS (SOURCED or OURS)
- **Market**: Binance BTCUSDT 1m merged klines (2,507,040 bars, 2022-01-01 to 2026-10-07 UTC) (`SOURCED`, quote: "2,507,040 bars, 1,741 days x 1440, zero gaps" in `MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md:12`).
- **Execution Cost Model**: 10 bps taker fee RT + 2 bps slippage RT = 12 bps total round-trip cost floor (`OURS`, quote: "fee 10 bps RT + slip 2 bps RT = 12 bp assumed cost" in `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:129,144`).
- **Exit Policy 1 (Live-like)**: 1% stop / 2% target / 8 bars time exit (`OURS`, quote: "live_like_1pct_2pct_8bars" in `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:28`).
- **Exit Policy 2 (Bracket 1x/2x ATR)**: 1 ATR stop / 2 ATR target / 24 bars (`OURS`, quote: "bracket_1atr_2atr_24" in `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:30`).
- **Exit Policy 3 (Bracket 1.5x/3x ATR)**: 1.5 ATR stop / 3 ATR target / 24 bars (`OURS`, quote: "bracket_1.5atr_3atr_24" in `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:32`).
- **Exit Policy 4 (Time 24 + Wide Stop)**: 2 ATR stop / 24 bars time exit (`OURS`, quote: "time_24_wide_stop_2atr" in `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:34`).
- **Exit Policy 5 (Time 96 + Wide Stop)**: 2 ATR stop / 96 bars time exit (`OURS`, quote: "time_96_wide_stop_2atr" in `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:36`).
- **Exit Policy 6 (Trailing Stop)**: Breakeven at 1 ATR, trail 2 ATR, 96 bars (`OURS`, quote: "be1atr_trail2atr_96" in `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:38`).

### BACKTESTS (Path, Fee-Net, IS/OOS, n)
1. **BIGMOVES-A Ground Truth Study (2026-10-09)** [`MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md:1-50`]:
   - **Path**: `MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md:1-50`
   - **Fee-Net**: Descriptive structural benchmark (no fee model; `MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md:10`).
   - **Sample Size (n)**: ATR zigzag legs counted: 4h n = 1,930 legs; 1h n = 8,173 legs; 15m n = 33,790 legs; 5m n = 105,235 legs (`MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md:18-24`). Verdict: ground truth, no verdict (`MyTradingSys/system/LAYERS.md:181`).
2. **FIRES-B1 Parity Replay (2026-10-09)** [`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:1-85`]:
   - **Path**: `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:1-85`
   - **Fee-Net**: Replay parity audit (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:12`).
   - **Sample Size (n)**: 244,543 total fires across 19 kline live layers (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:20-40`). Parity PASS on spot rerun (`MyTradingSys/system/LAYERS.md:182`).
3. **BIGTRADE-EXIT Backtest C (2026-10-09)** [`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:1-147`]:
   - **Path**: `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:1-147`
   - **Fee-Net**: Fee-net evaluated under 6 exit policies against 12 bps cost (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:120-145`).
   - **IS / OOS Partition**: TRAIN 2022-01..2025-06 / VALIDATE 2025-07..2026-08 (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:120-135`).
   - **Sample Size (n)**: 114 cells evaluated; 1 of 114 positive in both splits (CryptoCred sr_flip 1h, +9.8 bp TRAIN, +0.1 bp VALIDATE, n 1,024 / 163); all other layers negative under every policy (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:138-145`). Verdict: no exit policy rescues the fires (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:143`).
4. **CAPTURE-MATRIX Analysis (2026-10-09)** [`MyTradingSys/research/bigtrade_2026-10-09/CAPTURE_MATRIX_SPOT.md:1-60`]:
   - **Path**: `MyTradingSys/research/bigtrade_2026-10-09/CAPTURE_MATRIX_SPOT.md:1-60`
   - **Sample Size (n)**: Evaluated layer fire lift over ATR moves; capture lift hovered near 1.0 (uninformative) (`MyTradingSys/research/bigtrade_2026-10-09/CAPTURE_MATRIX_SPOT.md:25-35`).

### KNOWN BUGS, FABRICATIONS OR ASSUMPTIONS (Rulings)
- **Synthetic Fixture in Capture Matrix**: Tool fixture `SYNTHETIC` is an algorithmic test probe, not an actual layer signal (`MyTradingSys/system/LAYERS.md:183`).
- **Time Exit Misattribution**: 94-97% of testnet trades end on time exits; backtest C proves that changing to dynamic brackets or trailing stops does not convert negative gross drift into profit (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:144-145`).

### CONFLUENCE
- **Intended Role**: Cross-layer execution and benchmarking harness (`MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md:5-8`).
- **Integration Classification**: Classed as DEAD in layer review (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:33`).
- **Actual Live Confluence**: Zero live trades combined (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:8`).
