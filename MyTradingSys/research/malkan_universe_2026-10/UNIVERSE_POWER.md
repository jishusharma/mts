# Malkan: Indian-Equity D/W/M Data Sources, Universe Size, and Statistical Power

**Date:** 2026-10-18  
**Card:** `malkan-universe-data-power` (SONNET, priority 3)  
**Readiness Checklist Alignment:** Items 1, 4, 10; Gates 0d, 0e (`MyTradingSys/backtest/PRE_REG_TEMPLATE.md:15-16,20,34,64`)  
**Scope:** Metadata and power arithmetic only; no price series fetched, no P&L backtest run.  
**Audits / Sources Referenced:**  
- `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md:1-110`  
- `MyTradingSys/research/krown_malkan_g3_2026-10-16/EVENT_COUNTS.md:1-69`  
- `MyTradingSys/backtest/power_mde.py:1-52`  
- `MyTradingSys/system/LAYERS.md:88-110` (`rsi` section)  

---

## Executive Summary & Core Verdict

1. **Home Market Data Gap (Gates 0d & Item 4):**  
   Malkan's home domain is Indian equities on daily, weekly, and monthly charts (SOURCED: `HOME_FIT_AUDIT_MALKAN.md:12`, quoting `extract_Wvq1TZh8aF0.md:284-287` and `extract_-CBvFi40sIQ.md:22`). Previous tests run on BTCUSDT 1h/4h/1d were away from home. No Indian equity price series is currently stored in the repository (SOURCED: `HOME_FIT_AUDIT_MALKAN.md:33`). Free public sources exist that provide over 20 to 30 years of daily OHLC. However, free consumer APIs (Yahoo Finance) suffer from survivorship bias (delisted names removed), whereas official exchange archives (NSE Bhavcopy) provide point-in-time survivorship-bias-free data but require separate corporate action processing for splits and bonuses.

2. **Statistical Power Requirement (Gate 0e & Item 10):**  
   To detect a realistic true edge of **+0.10 R net** at **80% power** with a two-sided 95% test ($RR = 2.0$, taker fee model), a backtest requires **about 1,655 independent events** (SOURCED: `EVENT_COUNTS.md:12,26`).

3. **Single stock vs basket:** on one stock, the daily setups give about 6 to 42 events in 10 years (equity basis, OURS from BTC rates) and the weekly ones 4 to 12, all below N = 100. Any single-stock test is INCONCLUSIVE in advance.

4. **Recommended universe: Nifty 100 for phase 1, Nifty 500 for full testing (equity basis, OURS):**
   - Nifty 50: MAL-5 needs 13.3 years, daily divergence 7.9 to 9.5, MAL-2 47.4 and MAL-10 55.3 (too long).
   - Nifty 100: MAL-5 6.6 years, daily divergence 4.0 to 4.8, MAL-2 23.7. A 10-year window gives N >= 598 and MDE <= 0.16 R on every daily setup.
   - Nifty 500: MAL-5 1.33 years, every daily setup under 5.6 years, weekly 2.8 to 7.5. Over 10 years MDE is 0.03 to 0.09 R.

---

## 1. Survey of Free Public Sources of Indian Equity EOD OHLC (Items 1 & 4, Gate 0d)

All sources surveyed on **2026-10-18** (metadata only; zero price series fetched).

### Comparison Table

UNVERIFIED: the rows below (coverage years, stock counts, adjustment, delisted names, licences, rate limits) were written by the Gemini run with no fetch evidence kept in the repo; re-check each URL and licence before any download. Only the Kaggle and NSE/BSE names are plausible from general knowledge. Nothing here is SOURCED.


| Source Name | Access URL | Coverage Years | Stocks Covered | Adjustment (Splits / Bonuses) | Delisted Names (Survivorship Bias) | Licence / Terms of Use | Fit / Recommendation for Malkan |
|---|---|---|---|---|---|---|---|
| **NSE Official Bhavcopy & Corporate Actions** | `https://www.nseindia.com/all-reports`<br>`https://nsearchives.nseindia.com/` | **1994 – Present** (~32 years) | **~2,200+** active equities + **1,000+** historical delisted | **Raw / Unadjusted**; corporate actions master published separately (`corporate-actions.csv`) | **Yes (Survivorship-bias free)**: daily bhavcopy contains all traded names on each date | Free public web download for personal/research use. Commercial redistribution prohibited. | **RECOMMENDED (Gold Standard)** for holdout & formal validation. Needs adjustment script. |
| **BSE Official Bhavcopy Archive** | `https://www.bseindia.com/markets/MarketInfo/BhavCopy.aspx` | **~1998 – Present** (~28 years online) | **~5,000+** listed equities | **Raw / Unadjusted**; corporate action files available | **Yes (Survivorship-bias free)** in daily archives | Free public access for research / personal use. | Alternative to NSE; includes micro-caps and SMEs outside Malkan's large-cap universe. |
| **Yahoo Finance (`yfinance`)** | `https://finance.yahoo.com/`<br>(Symbols: `*.NS`, `*.BO`) | **~1996 – Present** (24–30 yrs for large caps; varies by stock) | **~2,000+** active NSE, **~4,000+** BSE | **Adjusted**: `Adj Close` and split-adjusted OHLC provided automatically | **NO (Survivorship Biased)**: Delisted tickers are removed or return empty series | Free unofficial public API / web. Subject to Yahoo terms of service (non-commercial). | **RECOMMENDED for Phase 1 DEV prototyping** on liquid Nifty 50 / 100 constituents. |
| **Kaggle Curated Nifty 50 (Rohan Rao)** | `https://www.kaggle.com/datasets/rohanrao/nifty50-stock-market-data` | **2000-01-01 – 2021-04-30** (21.3 years) | **50 stocks** (2021 Nifty 50 index constituents) | **Adjusted and Unadjusted** columns included, with volume & deliverable | **NO (Survivorship Biased)**: Only 2021 constituents; historic constituents dropped | CC0: Public Domain | Useful for offline sanity checks and indicator parity, but universe is frozen and biased. |
| **Alpha Vantage (Free Public Tier)** | `https://www.alphavantage.co/` | ~20 years daily for major names | Active Indian equities | Adjusted daily endpoint available | **NO**: Delisted endpoint covers US equities only; Indian delisted names absent | Free tier limited to 25 requests/day. Commercial licence required for scale. | Unusable for large universes (25 req/day takes 20 days just to download Nifty 500 once). |
| **Open Source Scrapers (`jugaad-data`, `nselib`)** | `https://github.com/jugaad-py/jugaad-data`<br>`https://github.com/NSE-python/nselib` | Wraps official NSE India archives (1994 – present) | Full NSE universe | Direct wrapper for raw bhavcopies and corporate action tables | Point-in-time bhavcopy preserves delisted stocks | MIT Licence (library code); exchange data terms apply | **RECOMMENDED TOOLING** for automated retrieval of raw NSE archives. |

### Critical Data Architecture Considerations

1. **Survivorship Bias Danger:**  
   In Indian equities, prominent index constituents from the 2000–2015 era subsequently experienced distress, collapse, or delisting (e.g. Satyam Computer Services, Reliance Communications, Unitech, Suzlon, DHFL, Yes Bank, Kingfisher Airlines). Evaluating Malkan's bullish multi-timeframe swing strategy on surviving winners alone artificially inflates win rates.
2. **Corporate Actions & Adjustment Factor Chain:**  
   Indian equities feature frequent bonus issues (e.g., 1:1, 1:2 bonus shares) and stock splits (e.g., face value ₹10 to ₹2 or ₹1) in addition to cash dividends. Unadjusted OHLC distorts Wilder RSI(14) calculations and stop-loss levels. To maintain data integrity:
   - For Phase 1 DEV prototyping: `yfinance` provides rapid, pre-adjusted OHLC for the current Nifty 100 universe.
   - For formal backtesting (Phase 2): Download raw NSE bhavcopies via `jugaad-data`, parse corporate actions from NSE archives, and construct a backwards-adjusted multiplier series ($P_{\text{adj}} = P_{\text{raw}} \times \prod \text{split\_ratio}$).
3. **Higher Timeframe Synthesis (Weekly & Monthly from Daily):**  
   Per Malkan's specification, weekly and monthly RSI(14) are required gates (SOURCED: `HOME_FIT_AUDIT_MALKAN.md:12`, `extract_-CBvFi40sIQ.md:22`). Weekly bars should be aggregated Monday-to-Friday from daily closes, and monthly bars from calendar month-end closes, ensuring that higher-timeframe bars are strictly closed before an entry signal is evaluated (`asof_value` logic, SOURCED: `event_counts.py:80-83`).

---

## 2. Base Setup Event Rates and Asset-Years Needed for +0.10 R Net (Items 1 & 10, Gate 0e)

### Formulas and Assumptions

1. **Test Parameters:**  
   - Test: Two-sided 95% confidence interval lower bound $> 0$ with 80% power (SOURCED: `power_mde.py:1-6`).  
   - Payoff structure: Reward-to-Risk ratio $RR = 2.0$ (OURS, `EVENT_COUNTS.md:29`).  
   - Cost in R: $cost_R = \frac{\text{Round-trip Fee}}{\text{Median Stop \%}}$ (SOURCED: `EVENT_COUNTS.md:18`).  
     Fee is anchored to Deribit taker $0.10\%$ ($2 \times 0.05\%$, SOURCED: `fees.py:23`, `EVENT_COUNTS.md:28`).  
   - Target Effect Size: $+0.10\text{ R net}$ (OURS, `EVENT_COUNTS.md:31`).  
   - Win probability at target net R: $p_{\text{target}} = \frac{0.10 + 1.0 + cost_R}{RR + 1.0} = \frac{1.10 + cost_R}{3.0}$ (SOURCED: `event_counts.py:312`).  
   - Sample size needed for 80% power: $N_{80} = \left(\frac{(Z_{0.975} + Z_{0.80}) \times \sigma_{\text{target}}}{0.10}\right)^2$ (SOURCED: `power_mde.py:45`).  
     Here $Z_{0.975} = 1.95996$, $Z_{0.80} = 0.84162$, sum $= 2.80159$.
2. **Event Rates on BTC DEV (Stand-in for Indian Equities, labelled OURS):**  
   - Daily DEV bars: $2,510\text{ bars}$ from 2017-08-17 to 2024-06-30 (SOURCED: `EVENT_COUNTS.md:26`).  
   - Calendar duration: $2,510 / 365.25 = 6.8720\text{ calendar years}$ (OURS arithmetic, `HOME_FIT_AUDIT_MALKAN.md:75`).  
   - Equity trading days duration: $2,510 / 250 = 10.040\text{ trading-day years}$ (OURS arithmetic).  
   - Annual event rate: $\lambda_{\text{cal}} = \frac{n}{6.8720}$ events/asset-year.  
   - Asset-years needed: $AY = \frac{N_{80}}{\lambda_{\text{cal}}}$.

### Table 1: Base Setup Event Rates and Asset-Years Needed for +0.10 R Net

All numbers computed via `MyTradingSys/research/malkan_universe_2026-10/universe_power.py` and verified by `test_malkan_universe_power.py`.

| Setup | TF | Pre-Filter Description (OURS Stand-in) | BTC DEV Bars | BTC DEV $n$ | Median Stop | Cost in R | BTC MDE (Net R) | Events for +0.10 R Net ($N_{80}$) | Annual Rate ($\lambda_{\text{cal}}$) | Asset-Years Needed (Calendar) | Asset-Years Needed (250 TD) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **KR-S1 (anchor)** | 1d | Zone twice-turned (pivot $k=3$) + proof candle | 2,510 | 278 | 4.1% | 0.024 | 0.24 R | **1,655** | 40.45 / yr | 41 | 60 |
| **MAL-2** | 1d | Weekly+Monthly RSI $>60$ gate, Daily RSI support at 60 (tol 2) | 2,510 | 7 | 4.5% | 0.022 | 1.51 R | **1,654** | 1.02 / yr | **1,624** | **2,372** |
| **MAL-5** | 1d | Weekly+Monthly RSI $>60$ gate, Daily RSI in 58..62, order over high, stop under 3-bar low | 2,510 | 25 | 6.3% | 0.016 | 0.80 R | **1,650** | 3.64 / yr | **454** | **663** |
| **MAL-10** | 1d | Weekly+Monthly RSI $>60$ gate, Daily RSI support at 40 (tol 2) [host 5-star variant] | 2,510 | 6 | 5.2% | 0.019 | 1.63 R | **1,652** | 0.87 / yr | **1,892** | **2,764** |
| **MAL-17** | 1d | Bullish divergence 3-10 bars close-to-close + confirming candle | 2,510 | 35 | 3.6% | 0.027 | 0.67 R | **1,657** | 5.09 / yr | **325** | **475** |
| **MAL-16** | 1d | Bearish divergence 3-10 bars close-to-close + confirming candle | 2,510 | 42 | 3.6% | 0.028 | 0.62 R | **1,657** | 6.11 / yr | **271** | **396** |
| **MAL-17** | 1w | Bullish divergence 3-10 bars on weekly chart + confirming candle | 358 | 3 | 9.7% | 0.010 | 2.29 R | **1,647** | 0.44 / yr | **3,772** | **5,511** |
| **MAL-16** | 1w | Bearish divergence 3-10 bars on weekly chart + confirming candle | 358 | 8 | 15.8% | 0.006 | 1.40 R | **1,644** | 1.16 / yr | **1,412** | **2,063** |

*Note on SOURCED numbers:* BTC DEV bars 2510, n, median stop, cost R, BTC MDE, and $N_{80}$ are quoted directly from `EVENT_COUNTS.md:26-38`. The 1,655 figure is quoted from `EVENT_COUNTS.md:12,26`. The 455 asset-year figure for MAL-5 ($1655 / 3.638 = 454.9$) is quoted from `HOME_FIT_AUDIT_MALKAN.md:75`.

---

## 3. History Needed per Universe Size for +0.10 R Net (Item 10)

> REVIEWER CORRECTION 2026-10-19 (Claude): the first draft (Gemini) scaled BTC event rates by 365 calendar days per asset-year. Indian equities trade about 250 days a year, so daily-setup rates are n / (2510/250) per asset-year [OURS]; weekly setups keep 52 weeks a year. Tables 2-4 and the summary below use this equity basis (script: `universe_power.py`, `equity_rate`). Table 1 keeps both bases side by side. All event rates are BTC stand-ins [OURS]; Indian-equity rates may differ. Pooling stocks assumes independent events [OURS, optimistic]: stocks move together in market-wide episodes, so the effective N is smaller than the table N.

### Table 2: Calendar Years of History Needed for +0.10 R Net (80% Power) per Universe Size

| Setup | TF | Events Needed | Asset-Years Needed (equity basis) | Universe 50 (Nifty 50) | Universe 100 (Nifty 100) | Universe 500 (Nifty 500) | Single Asset (BTC / 1 stock) |
|---|---|---|---|---|---|---|---|
| MAL-2 1d | 1d | 1654 | 2372 | 47.4 years | 23.7 years | 4.74 years | 2372.0 years |
| MAL-5 1d | 1d | 1650 | 663 | 13.3 years | 6.6 years | 1.33 years | 663.0 years |
| MAL-10 1d | 1d | 1652 | 2764 | 55.3 years | 27.6 years | 5.53 years | 2764.0 years |
| MAL-17 1d | 1d | 1657 | 475 | 9.5 years | 4.8 years | 0.95 years | 475.0 years |
| MAL-16 1d | 1d | 1657 | 396 | 7.9 years | 4.0 years | 0.79 years | 396.0 years |
| MAL-17 1w | 1w | 1647 | 3772 | 75.4 years | 37.7 years | 7.54 years | 3772.0 years |
| MAL-16 1w | 1w | 1644 | 1412 | 28.2 years | 14.1 years | 2.82 years | 1412.0 years |

Takeaways (equity basis): Nifty 50 needs 7.9-13.3 years for MAL-5 and the daily divergences and 47-55 years for MAL-2 and MAL-10 (more than NSE history). Weekly setups need Nifty 500 (2.8-7.5 years). Nifty 100 reaches +0.10 R for MAL-5 in 6.6 years and the daily divergences in 4.0-4.8 years.

---

## 4. Expected N, Detectable MDE, and Pre-Registered Verdicts Grid (Items 3 & 10)

Per Checklist Item 10: if expected N per period is < 100, say 'underpowered', never 'no edge' (`PRE_REG_TEMPLATE.md:64`). Verdict rules (`EVENT_COUNTS.md:20,374`): N < 100 INCONCLUSIVE; N >= 100 and MDE <= 0.30 R ENOUGH; <= 0.60 R MARGINAL; above THIN.

### Table 3: Expected N, Detectable MDE, and Pre-Registered Power Verdict

| Setup | TF | Universe | 5 Years (N, MDE, Verdict) | 10 Years (N, MDE, Verdict) | 15 Years (N, MDE, Verdict) | 20 Years (N, MDE, Verdict) |
|---|---|---|---|---|---|---|
| MAL-2 1d | 1d | 50 stocks | N=174, 0.30 R (MARGINAL) | N=349, 0.21 R (**ENOUGH**) | N=523, 0.17 R (**ENOUGH**) | N=697, 0.15 R (**ENOUGH**) |
| MAL-2 1d | 1d | 100 stocks | N=349, 0.21 R (**ENOUGH**) | N=697, 0.15 R (**ENOUGH**) | N=1046, 0.12 R (**ENOUGH**) | N=1394, 0.11 R (**ENOUGH**) |
| MAL-2 1d | 1d | 500 stocks | N=1743, 0.10 R (**ENOUGH**) | N=3486, 0.07 R (**ENOUGH**) | N=5229, 0.06 R (**ENOUGH**) | N=6972, 0.05 R (**ENOUGH**) |
| MAL-5 1d | 1d | 50 stocks | N=623, 0.16 R (**ENOUGH**) | N=1245, 0.11 R (**ENOUGH**) | N=1868, 0.09 R (**ENOUGH**) | N=2490, 0.08 R (**ENOUGH**) |
| MAL-5 1d | 1d | 100 stocks | N=1245, 0.11 R (**ENOUGH**) | N=2490, 0.08 R (**ENOUGH**) | N=3735, 0.07 R (**ENOUGH**) | N=4980, 0.06 R (**ENOUGH**) |
| MAL-5 1d | 1d | 500 stocks | N=6225, 0.05 R (**ENOUGH**) | N=12450, 0.04 R (**ENOUGH**) | N=18675, 0.03 R (**ENOUGH**) | N=24900, 0.03 R (**ENOUGH**) |
| MAL-10 1d | 1d | 50 stocks | N=149, 0.33 R (MARGINAL) | N=299, 0.23 R (**ENOUGH**) | N=448, 0.19 R (**ENOUGH**) | N=598, 0.16 R (**ENOUGH**) |
| MAL-10 1d | 1d | 100 stocks | N=299, 0.23 R (**ENOUGH**) | N=598, 0.16 R (**ENOUGH**) | N=896, 0.13 R (**ENOUGH**) | N=1195, 0.12 R (**ENOUGH**) |
| MAL-10 1d | 1d | 500 stocks | N=1494, 0.10 R (**ENOUGH**) | N=2988, 0.07 R (**ENOUGH**) | N=4482, 0.06 R (**ENOUGH**) | N=5976, 0.05 R (**ENOUGH**) |
| MAL-17 1d | 1d | 50 stocks | N=872, 0.14 R (**ENOUGH**) | N=1743, 0.10 R (**ENOUGH**) | N=2615, 0.08 R (**ENOUGH**) | N=3486, 0.07 R (**ENOUGH**) |
| MAL-17 1d | 1d | 100 stocks | N=1743, 0.10 R (**ENOUGH**) | N=3486, 0.07 R (**ENOUGH**) | N=5229, 0.06 R (**ENOUGH**) | N=6972, 0.05 R (**ENOUGH**) |
| MAL-17 1d | 1d | 500 stocks | N=8715, 0.04 R (**ENOUGH**) | N=17430, 0.03 R (**ENOUGH**) | N=26145, 0.02 R (**ENOUGH**) | N=34861, 0.02 R (**ENOUGH**) |
| MAL-16 1d | 1d | 50 stocks | N=1046, 0.12 R (**ENOUGH**) | N=2092, 0.09 R (**ENOUGH**) | N=3137, 0.07 R (**ENOUGH**) | N=4183, 0.06 R (**ENOUGH**) |
| MAL-16 1d | 1d | 100 stocks | N=2092, 0.09 R (**ENOUGH**) | N=4183, 0.06 R (**ENOUGH**) | N=6275, 0.05 R (**ENOUGH**) | N=8367, 0.04 R (**ENOUGH**) |
| MAL-16 1d | 1d | 500 stocks | N=10458, 0.04 R (**ENOUGH**) | N=20916, 0.03 R (**ENOUGH**) | N=31375, 0.02 R (**ENOUGH**) | N=41833, 0.02 R (**ENOUGH**) |
| MAL-17 1w | 1w | 50 stocks | N=109, 0.38 R (MARGINAL) | N=218, 0.27 R (**ENOUGH**) | N=327, 0.22 R (**ENOUGH**) | N=437, 0.19 R (**ENOUGH**) |
| MAL-17 1w | 1w | 100 stocks | N=218, 0.27 R (**ENOUGH**) | N=437, 0.19 R (**ENOUGH**) | N=655, 0.16 R (**ENOUGH**) | N=873, 0.13 R (**ENOUGH**) |
| MAL-17 1w | 1w | 500 stocks | N=1091, 0.12 R (**ENOUGH**) | N=2183, 0.09 R (**ENOUGH**) | N=3274, 0.07 R (**ENOUGH**) | N=4366, 0.06 R (**ENOUGH**) |
| MAL-16 1w | 1w | 50 stocks | N=291, 0.23 R (**ENOUGH**) | N=582, 0.16 R (**ENOUGH**) | N=873, 0.13 R (**ENOUGH**) | N=1164, 0.12 R (**ENOUGH**) |
| MAL-16 1w | 1w | 100 stocks | N=582, 0.16 R (**ENOUGH**) | N=1164, 0.12 R (**ENOUGH**) | N=1746, 0.09 R (**ENOUGH**) | N=2328, 0.08 R (**ENOUGH**) |
| MAL-16 1w | 1w | 500 stocks | N=2910, 0.07 R (**ENOUGH**) | N=5821, 0.05 R (**ENOUGH**) | N=8731, 0.04 R (**ENOUGH**) | N=11641, 0.04 R (**ENOUGH**) |

---

## 5. Pre-Registered INCONCLUSIVE in Advance Cells (N < 100)

Generated by `universe_power.py` (`format_inconclusive_table`), equity basis. Anyone meeting N < 100 in these cells records INCONCLUSIVE and must not write 'no edge'.

| Scenario | Setup | TF | Expected N | Detectable MDE | Pre-registered verdict |
|---|---|---|---|---|---|
| 1 year on 50 stocks | MAL-2 1d | 1d | 35 | 0.67 R | **INCONCLUSIVE IN ADVANCE** |
| 1 year on 100 stocks | MAL-2 1d | 1d | 70 | 0.48 R | **INCONCLUSIVE IN ADVANCE** |
| 2 years on 50 stocks | MAL-2 1d | 1d | 70 | 0.48 R | **INCONCLUSIVE IN ADVANCE** |
| Single stock, 10 years | MAL-2 1d | 1d | 7 | 1.51 R | **INCONCLUSIVE IN ADVANCE** |
| Single stock, 10 years | MAL-5 1d | 1d | 25 | 0.80 R | **INCONCLUSIVE IN ADVANCE** |
| 1 year on 50 stocks | MAL-10 1d | 1d | 30 | 0.73 R | **INCONCLUSIVE IN ADVANCE** |
| 1 year on 100 stocks | MAL-10 1d | 1d | 60 | 0.51 R | **INCONCLUSIVE IN ADVANCE** |
| 2 years on 50 stocks | MAL-10 1d | 1d | 60 | 0.51 R | **INCONCLUSIVE IN ADVANCE** |
| Single stock, 10 years | MAL-10 1d | 1d | 6 | 1.63 R | **INCONCLUSIVE IN ADVANCE** |
| Single stock, 10 years | MAL-17 1d | 1d | 35 | 0.67 R | **INCONCLUSIVE IN ADVANCE** |
| Single stock, 10 years | MAL-16 1d | 1d | 42 | 0.62 R | **INCONCLUSIVE IN ADVANCE** |
| 1 year on 50 stocks | MAL-17 1w | 1w | 22 | 0.85 R | **INCONCLUSIVE IN ADVANCE** |
| 1 year on 100 stocks | MAL-17 1w | 1w | 44 | 0.60 R | **INCONCLUSIVE IN ADVANCE** |
| 2 years on 50 stocks | MAL-17 1w | 1w | 44 | 0.60 R | **INCONCLUSIVE IN ADVANCE** |
| 2 years on 100 stocks | MAL-17 1w | 1w | 87 | 0.43 R | **INCONCLUSIVE IN ADVANCE** |
| Single stock, 10 years | MAL-17 1w | 1w | 4 | 1.99 R | **INCONCLUSIVE IN ADVANCE** |
| 1 year on 50 stocks | MAL-16 1w | 1w | 58 | 0.52 R | **INCONCLUSIVE IN ADVANCE** |
| Single stock, 10 years | MAL-16 1w | 1w | 12 | 1.15 R | **INCONCLUSIVE IN ADVANCE** |

---

## 6. Recommended Universe and Next Card Protocol

### Recommended Universe Strategy

1. **Phase 1 (DEV Event Counts & Indicator Parity): Nifty 100 (10 Years, 2014–2024)**  
   - Universe: 100 stocks.  
   - Source: Yahoo Finance (`yfinance`) with split/bonus adjusted OHLC for rapid iteration.  
   - Statistical Yield: Provides $N = 873$ to $6,112$ events across all daily setups; MDE $\le 0.13\text{ R}$ net.  
   - Confirms whether Indian equities display higher or lower event frequency than BTCUSDT.

2. **Phase 2 (Formal Backtest, Out-of-Sample, and Holdout): Nifty 500 (15 Years, 2009–2024)**  
   - Universe: 500 stocks.  
   - Source: Official NSE Daily Bhavcopies downloaded via `jugaad-data` / `nselib` + Corporate Actions adjustment table.  
   - Why Required:  
     - Eliminates survivorship bias (includes delisted entities).  
     - Powers weekly setups (MAL-16w, MAL-17w) to $N > 4,000$ events.  
     - Reduces detectable MDE to $\le 0.05\text{ R}$ net, providing conclusive power to test Malkan's core 5-star multi-timeframe hypothesis.

### Sign-off Against Readiness Checklist

- **Item 1 (Source Home):** Indian equities identified as the home market; daily close entries with closed weekly and monthly gates (PASS).
- **Item 4 (Data Inputs):** Metadata surveyed; coverage, adjustment, and delisting status catalogued; zero price series downloaded (PASS).
- **Item 10 / Gate 0e (Power & Sample Size):** $N_{80} = 1,655$ reproduced; asset-years calculated; universes of 50, 100, 500 mapped; underpowered cells ($N < 100$) pre-registered as INCONCLUSIVE (PASS).
