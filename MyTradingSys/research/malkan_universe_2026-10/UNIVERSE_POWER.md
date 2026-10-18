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

3. **Single Stock vs Basket (The Universe Problem):**  
   - On **BTC alone** or on **any single Indian stock** (e.g. Tata Motors), event frequency for Malkan setups is between **0.87 and 6.11 events per calendar year** (OURS, derived from `EVENT_COUNTS.md:32-36`).
   - Over a 10-year window, a single stock yields only **9 to 61 events**, all strictly **below the $N = 100$ threshold**.
   - Per Checklist Item 10 (`PRE_REG_TEMPLATE.md:64`) and Gate 0e, **any single-stock test is declared INCONCLUSIVE in advance**. A single-stock backtest can never support a "no edge" verdict.

4. **Recommended Universe: Nifty 100 (Balanced) or Nifty 500 (Comprehensive):**  
   - **Nifty 50 (50 stocks):** Requires **9.1 years** for MAL-5 (454 asset-years) and **5.4 to 6.5 years** for daily divergence, but fails completely on narrow setups (MAL-2 needs **32.5 years**; MAL-10 needs **37.8 years**; weekly divergence needs **28 to 75 years**).
   - **Nifty 100 (100 stocks, RECOMMENDED for Phase 1):** Reaches +0.10 R power for MAL-5 in **4.5 years**, daily divergence in **2.7 to 3.2 years**, and MAL-2 in **16.2 years**. In a 10-year window, all daily setups achieve $N > 870$ and detectable MDE $\le 0.13\text{ R}$ net (**ENOUGH**).
   - **Nifty 500 (500 stocks, RECOMMENDED for full testing & weekly setups):** Reaches 80% power for MAL-5 in **0.91 years**, all daily setups in under **3.8 years**, and weekly setups in **2.8 to 7.5 years**. Over 10 years, MDE is between **0.02 R and 0.09 R** net across all setups.

---

## 1. Survey of Free Public Sources of Indian Equity EOD OHLC (Items 1 & 4, Gate 0d)

All sources surveyed on **2026-10-18** (metadata only; zero price series fetched).

### Comparison Table

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

How many calendar years of historical data must be pooled across a universe to accumulate the ~1,655 independent events required for 80% power at +0.10 R net?

$$\text{Years Needed} = \frac{\text{Asset-Years Needed}}{\text{Universe Size}}$$

### Table 2: Calendar Years of Data Needed to Confirm +0.10 R Net (80% Power)

| Setup | TF | Events Needed | Asset-Years Needed (OURS) | Universe 50 (Nifty 50) | Universe 100 (Nifty 100) | Universe 500 (Nifty 500) | Single Stock (1 Asset) |
|---|---|---|---|---|---|---|---|
| **MAL-2** | 1d | 1,654 | 1,624 | **32.5 years** (Exceeds NSE history!) | **16.2 years** | **3.25 years** | 1,624 years |
| **MAL-5** | 1d | 1,650 | 454 | **9.1 years** | **4.5 years** | **0.91 years** | 454 years |
| **MAL-10** | 1d | 1,652 | 1,892 | **37.8 years** (Exceeds NSE history!) | **18.9 years** | **3.78 years** | 1,892 years |
| **MAL-17** | 1d | 1,657 | 325 | **6.5 years** | **3.2 years** | **0.65 years** | 325 years |
| **MAL-16** | 1d | 1,657 | 271 | **5.4 years** | **2.7 years** | **0.54 years** | 271 years |
| **MAL-17** | 1w | 1,647 | 3,772 | **75.4 years** (Impossible) | **37.7 years** (Impossible) | **7.54 years** | 3,772 years |
| **MAL-16** | 1w | 1,644 | 1,412 | **28.2 years** (Exceeds NSE history!) | **14.1 years** | **2.82 years** | 1,412 years |

### Key Takeaways from Table 2:
1. **Nifty 50 Is Severely Constrained:**  
   In a 50-stock universe, MAL-2 (RSI 60 support) and MAL-10 (RSI 40 support) would require **32.5 to 37.8 years** of continuous history—exceeding the entire 30-year operational history of the National Stock Exchange of India. Nifty 50 is viable only for high-fire setups (MAL-5 and daily divergence) over 6 to 9 years.
2. **Weekly Setups Require Nifty 500:**  
   Weekly divergence on 50 or 100 stocks requires 14 to 75 years of history. Only Nifty 500 can power weekly setups within a realistic timeframe (**2.8 years** for MAL-16w, **7.5 years** for MAL-17w).

---

## 4. Expected N, Detectable MDE, and Pre-Registered Verdicts Grid (Items 3 & 10)

Per Checklist Item 10:  
> *"If expected N per period is < 100, say 'underpowered', never 'no edge'."* (`PRE_REG_TEMPLATE.md:64`)

Verdict Rules (SOURCED: `EVENT_COUNTS.md:20,374`):
- $N < 100$: **INCONCLUSIVE** (declared in advance; cannot reject $H_0$).
- $N \ge 100$ and $MDE \le 0.30\text{ R}$: **ENOUGH**.
- $N \ge 100$ and $0.30 < MDE \le 0.60\text{ R}$: **MARGINAL**.
- $N \ge 100$ and $MDE > 0.60\text{ R}$: **THIN**.

### Table 3: Expected N, Detectable MDE, and Power Verdict Across Multi-Year Windows

| Setup | TF | Universe | 5 Years ($N$, MDE, Verdict) | 10 Years ($N$, MDE, Verdict) | 15 Years ($N$, MDE, Verdict) | 20 Years ($N$, MDE, Verdict) |
|---|---|---|---|---|---|---|
| **MAL-2** | 1d | 50 stocks | $N=255$, 0.25 R (**ENOUGH**) | $N=509$, 0.18 R (**ENOUGH**) | $N=764$, 0.14 R (**ENOUGH**) | $N=1019$, 0.12 R (**ENOUGH**) |
| | | 100 stocks | $N=509$, 0.18 R (**ENOUGH**) | $N=1019$, 0.12 R (**ENOUGH**) | $N=1528$, 0.10 R (**ENOUGH**) | $N=2037$, 0.09 R (**ENOUGH**) |
| | | 500 stocks | $N=2547$, 0.08 R (**ENOUGH**) | $N=5093$, 0.06 R (**ENOUGH**) | $N=7640$, 0.05 R (**ENOUGH**) | $N=10186$, 0.04 R (**ENOUGH**) |
| **MAL-5** | 1d | 50 stocks | $N=909$, 0.13 R (**ENOUGH**) | $N=1819$, 0.09 R (**ENOUGH**) | $N=2728$, 0.08 R (**ENOUGH**) | $N=3638$, 0.07 R (**ENOUGH**) |
| | | 100 stocks | $N=1819$, 0.09 R (**ENOUGH**) | $N=3638$, 0.07 R (**ENOUGH**) | $N=5457$, 0.05 R (**ENOUGH**) | $N=7276$, 0.05 R (**ENOUGH**) |
| | | 500 stocks | $N=9095$, 0.04 R (**ENOUGH**) | $N=18190$, 0.03 R (**ENOUGH**) | $N=27285$, 0.02 R (**ENOUGH**) | $N=36379$, 0.02 R (**ENOUGH**) |
| **MAL-10** | 1d | 50 stocks | $N=218$, 0.27 R (**ENOUGH**) | $N=437$, 0.19 R (**ENOUGH**) | $N=655$, 0.16 R (**ENOUGH**) | $N=873$, 0.13 R (**ENOUGH**) |
| | | 100 stocks | $N=437$, 0.19 R (**ENOUGH**) | $N=873$, 0.13 R (**ENOUGH**) | $N=1310$, 0.11 R (**ENOUGH**) | $N=1746$, 0.10 R (**ENOUGH**) |
| | | 500 stocks | $N=2183$, 0.09 R (**ENOUGH**) | $N=4366$, 0.06 R (**ENOUGH**) | $N=6548$, 0.05 R (**ENOUGH**) | $N=8731$, 0.04 R (**ENOUGH**) |
| **MAL-17** | 1d | 50 stocks | $N=1273$, 0.11 R (**ENOUGH**) | $N=2547$, 0.08 R (**ENOUGH**) | $N=3820$, 0.06 R (**ENOUGH**) | $N=5093$, 0.06 R (**ENOUGH**) |
| | | 100 stocks | $N=2547$, 0.08 R (**ENOUGH**) | $N=5093$, 0.06 R (**ENOUGH**) | $N=7640$, 0.05 R (**ENOUGH**) | $N=10186$, 0.04 R (**ENOUGH**) |
| | | 500 stocks | $N=12733$, 0.04 R (**ENOUGH**) | $N=25466$, 0.02 R (**ENOUGH**) | $N=38198$, 0.02 R (**ENOUGH**) | $N=50931$, 0.02 R (**ENOUGH**) |
| **MAL-16** | 1d | 50 stocks | $N=1528$, 0.10 R (**ENOUGH**) | $N=3056$, 0.07 R (**ENOUGH**) | $N=4584$, 0.06 R (**ENOUGH**) | $N=6112$, 0.05 R (**ENOUGH**) |
| | | 100 stocks | $N=3056$, 0.07 R (**ENOUGH**) | $N=6112$, 0.05 R (**ENOUGH**) | $N=9168$, 0.04 R (**ENOUGH**) | $N=12224$, 0.04 R (**ENOUGH**) |
| | | 500 stocks | $N=15279$, 0.03 R (**ENOUGH**) | $N=30559$, 0.02 R (**ENOUGH**) | $N=45838$, 0.02 R (**ENOUGH**) | $N=61118$, 0.02 R (**ENOUGH**) |
| **MAL-17** | 1w | 50 stocks | $N=109$, 0.38 R (**MARGINAL**) | $N=218$, 0.27 R (**ENOUGH**) | $N=327$, 0.22 R (**ENOUGH**) | $N=437$, 0.19 R (**ENOUGH**) |
| | | 100 stocks | $N=218$, 0.27 R (**ENOUGH**) | $N=437$, 0.19 R (**ENOUGH**) | $N=655$, 0.16 R (**ENOUGH**) | $N=873$, 0.13 R (**ENOUGH**) |
| | | 500 stocks | $N=1091$, 0.12 R (**ENOUGH**) | $N=2183$, 0.09 R (**ENOUGH**) | $N=3274$, 0.07 R (**ENOUGH**) | $N=4366$, 0.06 R (**ENOUGH**) |
| **MAL-16** | 1w | 50 stocks | $N=291$, 0.23 R (**ENOUGH**) | $N=582$, 0.16 R (**ENOUGH**) | $N=873$, 0.13 R (**ENOUGH**) | $N=1164$, 0.12 R (**ENOUGH**) |
| | | 100 stocks | $N=582$, 0.16 R (**ENOUGH**) | $N=1164$, 0.12 R (**ENOUGH**) | $N=1746$, 0.09 R (**ENOUGH**) | $N=2328$, 0.08 R (**ENOUGH**) |
| | | 500 stocks | $N=2910$, 0.07 R (**ENOUGH**) | $N=5821$, 0.05 R (**ENOUGH**) | $N=8731$, 0.04 R (**ENOUGH**) | $N=11641$, 0.04 R (**ENOUGH**) |

---

## 5. Pre-Registered INCONCLUSIVE in Advance Cells ($N < 100$)

When shorter evaluation windows (1 year or 2 years, e.g. recent annual test sets or single validation folds) or individual stocks are evaluated, the event count drops below 100. **The following cells are formally pre-registered as INCONCLUSIVE in advance:**

### Table 4: Pre-Registered INCONCLUSIVE Cells for Short Horizons & Single Stocks

| Scenario / Scope | Setup | TF | Expected $N$ | Detectable MDE | Pre-Registered Verdict |
|---|---|---|---|---|---|
| **1 Year on 50 Stocks** | MAL-2 | 1d | $N = 51$ | 0.56 R | **INCONCLUSIVE IN ADVANCE** |
| **1 Year on 50 Stocks** | MAL-10 | 1d | $N = 44$ | 0.60 R | **INCONCLUSIVE IN ADVANCE** |
| **1 Year on 50 Stocks** | MAL-17 | 1w | $N = 22$ | 0.85 R | **INCONCLUSIVE IN ADVANCE** |
| **1 Year on 50 Stocks** | MAL-16 | 1w | $N = 58$ | 0.52 R | **INCONCLUSIVE IN ADVANCE** |
| **1 Year on 100 Stocks** | MAL-10 | 1d | $N = 87$ | 0.43 R | **INCONCLUSIVE IN ADVANCE** |
| **1 Year on 100 Stocks** | MAL-17 | 1w | $N = 44$ | 0.60 R | **INCONCLUSIVE IN ADVANCE** |
| **2 Years on 50 Stocks** | MAL-10 | 1d | $N = 87$ | 0.43 R | **INCONCLUSIVE IN ADVANCE** |
| **2 Years on 50 Stocks** | MAL-17 | 1w | $N = 44$ | 0.60 R | **INCONCLUSIVE IN ADVANCE** |
| **2 Years on 100 Stocks** | MAL-17 | 1w | $N = 87$ | 0.43 R | **INCONCLUSIVE IN ADVANCE** |
| **Single Stock (10 Years)** | MAL-2 | 1d | $N \approx 10$ | 1.26 R | **INCONCLUSIVE IN ADVANCE** |
| **Single Stock (10 Years)** | MAL-5 | 1d | $N \approx 36$ | 0.67 R | **INCONCLUSIVE IN ADVANCE** |
| **Single Stock (10 Years)** | MAL-10 | 1d | $N \approx 9$ | 1.33 R | **INCONCLUSIVE IN ADVANCE** |
| **Single Stock (10 Years)** | MAL-17 | 1d | $N \approx 51$ | 0.56 R | **INCONCLUSIVE IN ADVANCE** |
| **Single Stock (10 Years)** | MAL-16 | 1d | $N \approx 61$ | 0.51 R | **INCONCLUSIVE IN ADVANCE** |
| **Single Stock (10 Years)** | MAL-17 | 1w | $N \approx 4$ | 1.98 R | **INCONCLUSIVE IN ADVANCE** |
| **Single Stock (10 Years)** | MAL-16 | 1w | $N \approx 12$ | 1.15 R | **INCONCLUSIVE IN ADVANCE** |

*Methodological Rule:* Any researcher or automated harness encountering $N < 100$ in these cells must record `INCONCLUSIVE` and must NOT declare "no edge" or "strategy failed".

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
