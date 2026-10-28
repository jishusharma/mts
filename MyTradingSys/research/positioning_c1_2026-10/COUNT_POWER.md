# Positioning C1 (NO-SOURCE): DEV Window Count, Fire Rate, Power, and Null Spec

Card: `positioning-c1-longwindow-count-power`  
Date: 2026-10-18  
Scope: DEV window `2022-01-01 00:00:00 UTC` .. `2024-06-30 23:59:59 UTC` (30 calendar months, 87,552 15m bars resampled from 1,313,280 1m klines; 4,929 8h funding records from `2020-01-01` to `2024-06-30`).  
Checklist items: 3 (fire rate), 9 (random-entry null spec), 10 (power and MDE), 12 (regime strata proposal for B154); gate 0b (gross move vs 2x cost).  
Gate adherence: Count-only check; NO net P&L computed, NO tuning, VALIDATION (2024-07..2025-06) and HOLDOUT (2025-07+) sealed and NEVER loaded into memory.

---

## 1. Provenance and Number Labeling (SOURCED vs OURS)

- **SOURCED numbers:**
  - Round-trip fee and slippage: Binance USDT-M taker fee 10 bps + 2 bps slippage = 12 bps (0.12%) round trip (`MyTradingSys/backtest/layers/run_t055.py:9` and `MyTradingSys/backtest/layers/FORMULAS.md:364`).
  - Gate 0b threshold: Raw forward move >= 2x round-trip cost = 0.24% (24 bps) (`MyTradingSys/backtest/PRE_REG_TEMPLATE.md:13`).
  - DEV data window: 2022-01-01 to 2024-06-30 (30 months, `MyTradingSys/backtest/bigtrade/SPLIT_ALIGNMENT_2026-10-17.md:13` and `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_POSITIONING.md:87`).
  - C1 grid definition: 36 parameter cells (`lookback` in (60, 90, 180), `n` in (20, 50), `hi/lo` in ((0.90, 0.10), (0.95, 0.05), (0.99, 0.01)), `use_divergence` in (True, False)) with forward horizons of 4, 16, 48 bars (`MyTradingSys/backtest/layers/run_t055.py:65-68,87`).
  - Power floor: N >= 100 required; N < 100 declared underpowered / inconclusive in advance (`MyTradingSys/backtest/PRE_REG_TEMPLATE.md:16` and `HOME_FIT_AUDIT_POSITIONING.md:82-86`).
  - Prior OOS baseline: n=76, mean net -0.0453%, Sharpe -0.0346, implied per-trade noise 1.31%, MDE 0.42% (`HOME_FIT_AUDIT_POSITIONING.md:85` quoting `T055_BT_RERUN_FULLFUNDING_2026-10-07.md:14,27`).
- **OURS numbers:**
  - Resampled DEV 15m bar count: 87,552 bars from 1,313,280 1m bars; 4,929 funding records (all verified < 2024-07-01).
  - All empirical cell event counts N (352 to 2,055), fire rates (4.02 to 23.47 events per 1,000 bars), monthly rates (11.7 to 68.5 per month), and per-year counts (2022, 2023, 2024 DEV).
  - Empirical gross mean forward moves at 4, 16, 48 bars and Gate 0b pass/fail verdicts.
  - Normal-approximation MDE net R and MDE % (at 1.31% per-trade noise) via `power_mde.py` with cost_r = 0.0916 R (0.12% / 1.31%) and breakeven p0 = 0.5458.
  - Random-entry null specification and B154 regime strata proposal.

---

## 2. DEV Count and Power Table (36 Grid Cells)

Data: Binance USDT-M BTCUSDT 15m bars built from `raw_1m_2022` klines, with 8h funding rates from `raw_fund` (`2020-01-01` to `2024-06-30`).  
Total DEV 15m bars: 87,552. Total DEV duration: 30.0 calendar months. Gate 0b threshold: gross mean >= +0.240%.

| lookback | n_div | hi/lo | div | N | per mo | /1000b | 2022 | 2023 | 2024 | gross 4b | gross 16b | gross 48b | gate 0b (48b) | MDE net R | MDE % | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 60 | 20 | 90/10 | yes | 1638 | 54.6 | 18.71 | 582 | 687 | 369 | 0.002% | 0.093% | 0.126% | FAIL | 0.069 | 0.090% | POWERED (N >= 100) |
| 60 | 20 | 90/10 | no | 2055 | 68.5 | 23.47 | 1317 | 512 | 226 | -0.227% | -0.150% | -0.266% | FAIL | 0.062 | 0.081% | POWERED (N >= 100) |
| 60 | 20 | 95/5 | yes | 1267 | 42.2 | 14.47 | 480 | 504 | 283 | -0.008% | 0.122% | 0.186% | FAIL | 0.078 | 0.103% | POWERED (N >= 100) |
| 60 | 20 | 95/5 | no | 1589 | 53.0 | 18.15 | 1050 | 376 | 163 | -0.260% | -0.157% | -0.290% | FAIL | 0.070 | 0.092% | POWERED (N >= 100) |
| 60 | 20 | 99/1 | yes | 891 | 29.7 | 10.18 | 409 | 334 | 148 | 0.033% | 0.140% | 0.158% | FAIL | 0.093 | 0.122% | POWERED (N >= 100) |
| 60 | 20 | 99/1 | no | 984 | 32.8 | 11.24 | 661 | 246 | 77 | -0.284% | -0.156% | -0.322% | FAIL | 0.089 | 0.117% | POWERED (N >= 100) |
| 60 | 50 | 90/10 | yes | 850 | 28.3 | 9.71 | 284 | 348 | 218 | -0.026% | 0.047% | 0.080% | FAIL | 0.096 | 0.125% | POWERED (N >= 100) |
| 60 | 50 | 90/10 | no | 2055 | 68.5 | 23.47 | 1317 | 512 | 226 | -0.227% | -0.150% | -0.266% | FAIL | 0.062 | 0.081% | POWERED (N >= 100) |
| 60 | 50 | 95/5 | yes | 663 | 22.1 | 7.57 | 237 | 255 | 171 | -0.032% | 0.083% | 0.221% | FAIL | 0.108 | 0.142% | POWERED (N >= 100) |
| 60 | 50 | 95/5 | no | 1589 | 53.0 | 18.15 | 1050 | 376 | 163 | -0.260% | -0.157% | -0.290% | FAIL | 0.070 | 0.092% | POWERED (N >= 100) |
| 60 | 50 | 99/1 | yes | 468 | 15.6 | 5.35 | 196 | 174 | 98 | 0.017% | 0.081% | 0.215% | FAIL | 0.129 | 0.169% | POWERED (N >= 100) |
| 60 | 50 | 99/1 | no | 984 | 32.8 | 11.24 | 661 | 246 | 77 | -0.284% | -0.156% | -0.322% | FAIL | 0.089 | 0.117% | POWERED (N >= 100) |
| 90 | 20 | 90/10 | yes | 1672 | 55.7 | 19.10 | 623 | 684 | 365 | -0.002% | 0.103% | 0.159% | FAIL | 0.068 | 0.089% | POWERED (N >= 100) |
| 90 | 20 | 90/10 | no | 1997 | 66.6 | 22.81 | 1278 | 511 | 208 | -0.218% | -0.145% | -0.273% | FAIL | 0.062 | 0.082% | POWERED (N >= 100) |
| 90 | 20 | 95/5 | yes | 1285 | 42.8 | 14.68 | 485 | 556 | 244 | -0.006% | 0.119% | 0.210% | FAIL | 0.078 | 0.102% | POWERED (N >= 100) |
| 90 | 20 | 95/5 | no | 1482 | 49.4 | 16.93 | 928 | 423 | 131 | -0.224% | -0.139% | -0.235% | FAIL | 0.072 | 0.095% | POWERED (N >= 100) |
| 90 | 20 | 99/1 | yes | 805 | 26.8 | 9.19 | 407 | 298 | 100 | 0.033% | 0.141% | 0.179% | FAIL | 0.098 | 0.129% | POWERED (N >= 100) |
| 90 | 20 | 99/1 | no | 777 | 25.9 | 8.87 | 532 | 202 | 43 | -0.204% | -0.101% | -0.184% | FAIL | 0.100 | 0.131% | POWERED (N >= 100) |
| 90 | 50 | 90/10 | yes | 870 | 29.0 | 9.94 | 302 | 339 | 229 | -0.029% | 0.095% | 0.163% | FAIL | 0.095 | 0.124% | POWERED (N >= 100) |
| 90 | 50 | 90/10 | no | 1997 | 66.6 | 22.81 | 1278 | 511 | 208 | -0.218% | -0.145% | -0.273% | FAIL | 0.062 | 0.082% | POWERED (N >= 100) |
| 90 | 50 | 95/5 | yes | 682 | 22.7 | 7.79 | 236 | 291 | 155 | -0.032% | 0.109% | **0.273%** | **PASS** | 0.107 | 0.140% | POWERED (N >= 100) |
| 90 | 50 | 95/5 | no | 1482 | 49.4 | 16.93 | 928 | 423 | 131 | -0.224% | -0.139% | -0.235% | FAIL | 0.072 | 0.095% | POWERED (N >= 100) |
| 90 | 50 | 99/1 | yes | 425 | 14.2 | 4.85 | 193 | 165 | 67 | 0.013% | 0.098% | **0.271%** | **PASS** | 0.135 | 0.177% | POWERED (N >= 100) |
| 90 | 50 | 99/1 | no | 777 | 25.9 | 8.87 | 532 | 202 | 43 | -0.204% | -0.101% | -0.184% | FAIL | 0.100 | 0.131% | POWERED (N >= 100) |
| 180 | 20 | 90/10 | yes | 1634 | 54.5 | 18.66 | 577 | 792 | 265 | 0.017% | 0.119% | 0.135% | FAIL | 0.069 | 0.090% | POWERED (N >= 100) |
| 180 | 20 | 90/10 | no | 1845 | 61.5 | 21.07 | 1104 | 572 | 169 | -0.146% | -0.094% | -0.157% | FAIL | 0.065 | 0.085% | POWERED (N >= 100) |
| 180 | 20 | 95/5 | yes | 1163 | 38.8 | 13.28 | 469 | 592 | 102 | 0.027% | 0.193% | **0.308%** | **PASS** | 0.082 | 0.107% | POWERED (N >= 100) |
| 180 | 20 | 95/5 | no | 1296 | 43.2 | 14.80 | 781 | 443 | 72 | -0.121% | -0.084% | -0.088% | FAIL | 0.077 | 0.102% | POWERED (N >= 100) |
| 180 | 20 | 99/1 | yes | 677 | 22.6 | 7.73 | 364 | 297 | 16 | 0.042% | 0.191% | **0.255%** | **PASS** | 0.107 | 0.140% | POWERED (N >= 100) |
| 180 | 20 | 99/1 | no | 638 | 21.3 | 7.29 | 430 | 197 | 11 | -0.089% | -0.053% | -0.038% | FAIL | 0.110 | 0.145% | POWERED (N >= 100) |
| 180 | 50 | 90/10 | yes | 881 | 29.4 | 10.06 | 275 | 428 | 178 | -0.033% | 0.035% | 0.085% | FAIL | 0.094 | 0.123% | POWERED (N >= 100) |
| 180 | 50 | 90/10 | no | 1845 | 61.5 | 21.07 | 1104 | 572 | 169 | -0.146% | -0.094% | -0.157% | FAIL | 0.065 | 0.085% | POWERED (N >= 100) |
| 180 | 50 | 95/5 | yes | 600 | 20.0 | 6.85 | 223 | 308 | 69 | -0.023% | 0.118% | **0.253%** | **PASS** | 0.114 | 0.149% | POWERED (N >= 100) |
| 180 | 50 | 95/5 | no | 1296 | 43.2 | 14.80 | 781 | 443 | 72 | -0.121% | -0.084% | -0.088% | FAIL | 0.077 | 0.102% | POWERED (N >= 100) |
| 180 | 50 | 99/1 | yes | 352 | 11.7 | 4.02 | 167 | 172 | 13 | 0.013% | 0.143% | **0.341%** | **PASS** | 0.149 | 0.195% | POWERED (N >= 100) |
| 180 | 50 | 99/1 | no | 638 | 21.3 | 7.29 | 430 | 197 | 11 | -0.089% | -0.053% | -0.038% | FAIL | 0.110 | 0.145% | POWERED (N >= 100) |

---

## 3. Findings and Analysis

### 3.1 Power and Sample Size (Item 10)
- On the 30-month DEV window (`2022-01` to `2024-06`), **every one of the 36 cells has N >= 100** (range: 352 to 2,055 events).
- Zero cells are marked `INCONCLUSIVE (N < 100)`. In contrast to the prior 109-day OOS run where N=76 was underpowered (MDE = 0.420% per trade), the DEV window has MDE ranging from **0.081% to 0.195%** per trade.
- Therefore, any edge >= 0.24% (2x round-trip cost) is statistically detectable with >= 80% power across the entire DEV grid.

### 3.2 Pure Funding-Extreme vs CVD Divergence Fade
- **Funding-only reversion (`use_divergence: False`) is universally negative:**
  - Across all lookbacks (60, 90, 180) and all percentiles (90/10, 95/5, 99/1), pure funding reversion produces negative gross returns at 4 bars (-0.089% to -0.284%), 16 bars (-0.053% to -0.157%), and 48 bars (-0.038% to -0.322%).
  - Gate 0b fails decisively (0 of 18 cells pass). Fading extreme funding alone without orderflow confirmation enters directly into persistent trend runs.
- **Funding + CVD Divergence (`use_divergence: True`) turns forward moves positive:**
  - Forward returns expand as the holding period extends: mean gross move increases steadily from 4 bars (-0.033% to +0.042%) to 16 bars (+0.035% to +0.193%) and 48 bars (+0.080% to +0.341%).
  - At 48 bars (12 hours), **6 cells pass Gate 0b** (gross move >= 0.240%):
    1. `lookback=180, n=50, hi=0.99, lo=0.01`: N=352, gross 48b = **+0.341%** (PASS)
    2. `lookback=180, n=20, hi=0.95, lo=0.05`: N=1163, gross 48b = **+0.308%** (PASS)
    3. `lookback=90, n=50, hi=0.95, lo=0.05`: N=682, gross 48b = **+0.273%** (PASS)
    4. `lookback=90, n=50, hi=0.99, lo=0.01`: N=425, gross 48b = **+0.271%** (PASS)
    5. `lookback=180, n=20, hi=0.99, lo=0.01`: N=677, gross 48b = **+0.255%** (PASS)
    6. `lookback=180, n=50, hi=0.95, lo=0.05`: N=600, gross 48b = **+0.253%** (PASS)

### 3.3 Horizon Dynamics (Gate 0b)
- **4 bars (1 hour):** 0 / 36 cells pass Gate 0b. Mean gross moves are near zero (-0.03% to +0.04%). Fades do not develop edge within 1 hour.
- **16 bars (4 hours):** 0 / 36 cells pass Gate 0b (peak move is +0.193%, below the 0.240% threshold).
- **48 bars (12 hours):** 6 / 36 cells pass Gate 0b (all with `use_divergence: True` and lookback >= 90). The fade requires multi-hour persistence to clear round-trip transaction costs.

### 3.4 Asymmetry and Side Mix
- In crypto perpetuals, funding is structurally positive over extended regimes (longs pay shorts).
- Consequently, C1 signals are **heavily short-skewed**:
  - `lookback=90, n=50, 95/5`: 73 longs (10.7%) vs 609 shorts (89.3%).
  - `lookback=180, n=20, 95/5`: 234 longs (20.1%) vs 929 shorts (79.9%).
  - `lookback=180, n=50, 99/1`: 9 longs (2.6%) vs 343 shorts (97.4%).
- This structural imbalance mandates that any fair null benchmark and stratification model control for the side mix and funding regime.

---

## 4. Random-Entry Null Specification (Item 9 for Pre-Registration)

To test whether C1's gross edge reflects genuine timing/divergence alpha rather than market drift or the positive funding baseline, the follow-up pre-registration (card P3) must evaluate against a matched random-entry null:

1. **Sampling Frame:**
   - 15m bars inside the exact DEV window (`2022-01-01` to `2024-06-30`).
2. **Exact Side Mix Matching:**
   - For every evaluation cell, draw random entries with the exact same long/short proportion as the real event set (e.g. 89.3% short, 10.7% long).
3. **Regime and Calendar Density Matching:**
   - Condition random entry selection on the same funding percentile regime:
     - Short random entries drawn only during periods where funding percentile >= `hi`.
     - Long random entries drawn only during periods where funding percentile <= `lo`.
   - Stratify draws by calendar year/quarter to match the temporal clustering of real extreme-funding clusters (e.g. 2022 vs 2023 vs 2024).
4. **Execution and Cost Parity:**
   - Identical entry price: close of the randomly drawn event bar.
   - Identical holding periods: fixed exit at close of bar `i + h` (h = 4, 16, 48 bars).
   - Identical cost model: Binance taker fee 10 bps RT + 2 bps slippage (12 bps total) + actual historical funding paid/received over the hold.
5. **Monte Carlo Resampling:**
   - 1,000 independent random resamples of size N.
   - Compute null distribution of gross mean move and net mean return.
   - **Pass Criterion:** The real candidate's gross and net returns must exceed the **95th percentile of the matched null distribution** AND satisfy the two-sided 95% CI lower bound > 0 test (`power_mde`).

---

## 5. Regime Strata Proposal for B154 (Item 12)

Pooled metrics obscure regime dependence. To satisfy defect B154, pre-registration P3 will report stratified readouts along three orthogonal axes alongside the pooled number:

### Strata 1: Funding Extremity Regime
- **Extreme High Funding:** Funding rate >= 95th percentile (bearish fade territory; shorts).
- **Extreme Low / Negative Funding:** Funding rate <= 5th percentile (bullish fade territory; longs).
- **Neutral / Mild Funding:** 10th to 90th percentile (control / baseline).

### Strata 2: Macro Market Trend (Calendar Regimes)
- **2022 Bear / Deleveraging:** Sustained downtrend, credit events (Terra/Luna, FTX). Measures how short fades behave in trend-continuation vs long fades during waterfall drops.
- **2023 Consolidation / Recovery:** Low-volatility range-bound regime, choppy mean reversion.
- **2024 Bull Expansion (Pre-Halving / ETF launch):** Strong upward momentum with persistent high funding. Tests whether short fades get run over by momentum.

### Strata 3: Intraday Session Window
- **Asia Session:** 00:00 - 08:00 UTC (Tokyo/Singapore/Hong Kong active hours).
- **European / London Session:** 08:00 - 14:00 UTC (European morning and cross).
- **US Session:** 14:00 - 21:00 UTC (US equity open, major volatility and CVD volume concentration).

Each stratum will report N, fire rate, gross mean return at 4/16/48 bars, gate 0b pass rate, and MDE.

---

## 6. Summary Verdict

1. **Fire Rate & Power:** All 36 cells are fully powered on DEV (N >= 352, MDE <= 0.195%). N < 100 inconclusive status does not occur on the 2.5-year DEV window.
2. **Gate 0b (Gross vs 2x Cost):**
   - 4b (1h): 0 / 36 pass.
   - 16b (4h): 0 / 36 pass.
   - 48b (12h): 6 / 36 pass (all require `use_divergence: True` and lookback >= 90).
3. **Next Steps:** Card P3 (`positioning-c1-prereg-no-source`) will freeze these 6 candidate cells at horizon 48 bars, incorporate the matched random-entry null, implement B154 regime stratification, and register the sealed holdout protocol.
