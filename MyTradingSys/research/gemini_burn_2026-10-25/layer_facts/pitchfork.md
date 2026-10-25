# Layer Fact Sheet: Pitchfork (`pitchfork`)

**Card:** `lf-pitchfork-gemini-facts` [SOURCED: `MyTradingSys/system/tasks/lf-pitchfork-gemini-facts.json:16`]  
**Date:** 2026-10-26 [SOURCED: system clock UTC]  
**Layer Family:** `pitchfork` [SOURCED: `MyTradingSys/system/LAYERS.md:256`, `python scripts/dev/lab_query.py layers`]  
**Layer ID:** `pitchfork_swing` [SOURCED: `MyTradingSys/system/LAYERS.md:259`, `python scripts/dev/lab_query.py layers`]  
**Module:** `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py` [SOURCED: `MyTradingSys/system/LAYERS.md:259`]  
**Status in System:** "Foundational papers delivered; detector built with unit tests (100% pass)" [SOURCED: `MyTradingSys/system/LAYERS.md:259`]  
**Verdict:** NONE (Per instruction: no verdict on keeping, dropping, demoting or parking a layer) [SOURCED: `MyTradingSys/system/ANTIGRAVITY_LAPTOP.md:33`]

---

## 1. ORIGIN (Quoted Source)

- **Primary Historical Inventor:** Dr. Alan Hall Andrews (1900–1985), private Babson Action-Reaction Course (1960–1975) [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:26-28`].
  - *Quoted Source:* "Dr. Alan Hall Andrews (1900–1985), an MIT-educated engineer, mathematician, and Babson attendee, refined Babson’s macroeconomic observations into micro-level chart geometry... The cornerstone of Andrews' teachings was the Median Line Method—a three-point geometric vector construction that market participants colloquially termed the 'Pitchfork' due to its distinctive three-pronged appearance." [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:26-28`].
  - *Quoted 80% Rule:* "Prices will reach the Median Line approximately 80% of the time following the completion of Pivot 2." [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:83`, citing Alan H. Andrews, *The Babson Action-Reaction Course*, Section 2, p. 12 via `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:34`].
  - *Quoted Hagopian's Rule:* "If price reverses before reaching the Median Line, it signals an acute imbalance of order flow. Price will accelerate violently in the opposite direction and break completely out of the pitchfork channel through the opposite parallel line." [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:97`, citing Alan H. Andrews, Section 4 via `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:39`].
- **Schiff Pitchfork Modification:** Jerome Schiff [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:121-128`, `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:9`].
  - *Quoted Source:* "Jerome Schiff observed that after an impulsive breakout, the initial retracement ($P_1 \to P_2$) is often shallow, causing a standard $P_0 \to M$ vector to possess a steep angle ($> 60^\circ$)... Schiff solved this by displacing the origin point $P_0$ 50% of the distance toward $P_1$ in both time and price: $t_{0,\text{Schiff}} = \frac{t_0 + t_1}{2}, p_{0,\text{Schiff}} = \frac{p_0 + p_1}{2}$." [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:121-128`].
- **Modified Schiff Pitchfork:** Mircea Dologa and modern futures/technical analysis literature [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:130-136`, `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:28`].
  - *Quoted Source:* "Popularized in modern futures and algorithmic charting, the Modified Schiff Pitchfork maintains the original time coordinate $t_0$, but shifts the price coordinate $p_0$ to the vertical midpoint between $P_0$ and $P_1$: $t_{0,\text{ModSchiff}} = t_0, p_{0,\text{ModSchiff}} = \frac{p_0 + p_1}{2}$." [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:131-134`, citing Mircea Dologa, *Integrated Pitchfork Analysis*, Vol 1, p. 65 via `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:28`].
- **Institutional Median Line & Channel Extensions:** Timothy Morge (1954–2020), *Trading with Median Lines: Mapping the Markets* (2002) [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:141-152`].
  - *Quoted Source:* Formulated quartile lines (25%, 50%, 75% inner parallels), warning lines ($WL_1, WL_2, WL_3$), sliding parallel lines, and energy coils around the median line [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:144-152`].
- **Algorithmic Codification & Confirmation Delay:** Patrick Mikula, *The Best Trendline Methods of Alan Andrews and Five New Techniques* (2002) [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:153-157`, `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:23`].
  - *Quoted Source:* "Pivots $P_0, P_1, P_2$ must be confirmed swing extrema with a minimum clearance of $N \ge 3$ bars on each side and a swing amplitude exceeding $k \ge 2.5 \times \text{ATR}_{14}$." [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:24`, citing Mikula 2002:42].
- **MTS Operator Own Chart Input:** Stacked Schiff pitchforks on 1W spot BTC [SOURCED: `MyTradingSys/research/live_reads/2026-10-17_live_market_1017/SET_362293de1b70_pitchfork.md:3-6`].
  - *Quoted Source:* "Operator words: 'Now my own charts. I use pitch forks. Let us also add that pitchfork layer now!!! Ask Gemini to d' ... Tool settings: Style = Schiff, Extend lines on, Median red, only level 1 enabled (blue), other levels (0.382 .. 2.45) off, Background on" [SOURCED: `MyTradingSys/research/live_reads/2026-10-17_live_market_1017/SET_362293de1b70_pitchfork.md:4, 19`].

---

## 2. PARAMETERS (SOURCED or OURS)

- **Pivot confirmation lookback delay ($N = 3$ bars for 1D, $N = 4$ bars for 4H):** [SOURCED / OURS: see sub-items]
  - $N \ge 3$ bars lookahead delay: SOURCED [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:24`, citing Patrick Mikula, *The Best Trendline Methods of Alan Andrews*, p. 42; Timothy Morge, *Trading with Median Lines*, p. 18].
  - $N = 4$ bars (16 hours) for 4H study: OURS [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:8`].
- **Swing amplitude threshold ($k \ge 2.5 \times \text{ATR}_{14}$ or $\text{min\_change\_pct} = 0.02$):** [SOURCED / OURS: see sub-items]
  - $k \ge 2.5 \times \text{ATR}_{14}$: SOURCED [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:24`, citing Mikula 2002:42].
  - $\text{min\_change\_pct} = 0.02$ (2% reversal threshold in ZigZag): OURS [SOURCED: `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:337`].
- **Schiff switch slope angle threshold ($|\theta| > 55^\circ$):** SOURCED [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:28-29`, citing Jerome Schiff; Mircea Dologa, *Integrated Pitchfork Analysis*, Vol 1, p. 65].
- **Extreme slope invalidation angle threshold ($|\theta| > 75^\circ$):** SOURCED [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:31`, citing Dologa 2007:65].
- **Relative slope steepness ratio for auto Schiff (`max_slope_bars_ratio = 1.0`):** OURS [SOURCED: `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:313, 327`].
- **Median Line Reach criteria (price low $\le ML \le$ high or directional close across ML):** SOURCED [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:82-85`, Alan H. Andrews; implemented in `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:169-176`].
- **Hagopian failure minimum approach threshold ($15\%$ distance towards ML from origin tine before rollover):** OURS [SOURCED: `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:201-204`].
- **Hagopian failure target (measured move equal to channel width $W = |p_{UML} - p_{ML}|$):** SOURCED [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:42`, citing Alan H. Andrews, Section 4; Timothy Morge, p. 74].
- **Stop-loss level for tine bounces (1.0 ATR beyond Pivot 2):** SOURCED [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:52-53`, `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:186`].
- **Logarithmic pitchfork transformation ($y = \ln(p)$, geometric midpoint $M_{\ln} = \sqrt{p_1 \cdot p_2}$):** OURS [SOURCED: `papers/02_PITCHFORK_APPLICATION_ON_BTC.md:43-58`, `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:231-250`].
- **Volume Profile Value Area Confluence ($P_2$ inside 70% Value Area $[VAL, VAH]$):** SOURCED [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:83`, `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:20-22, 51-55`, citing Fractal Flow].
- **Volume Profile POC alignment tolerance ($\pm 0.35\%$ or $\pm 0.75\%$ or $\pm 1.5\%$):** [OURS: see sub-items]
  - $\pm 0.35\%$: OURS [SOURCED: `papers/02_PITCHFORK_APPLICATION_ON_BTC.md:207`, `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:138`].
  - $\pm 0.75\%$ and $\pm 1.5\%$: OURS [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:27-28`].
- **Tine limit retest entry execution mode (`TINE_LIMIT_RETEST`):** OURS [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:22-24`].
- **Volume Profile bin grid width ($w = 10.0$ USD, FORMULAS 18.1):** OURS [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:9`].

---

## 3. BACKTESTS (Path, Fee-Net, IS/OOS, n)

### A. Phase 1 Daily (1D) Historical Event Study (2020–2026)
- **Report Path:** `MyTradingSys/research/pitchfork_2026-10-19/PHASE1_EVENT_STUDY.md:1-46` [SOURCED: file exists]
- **Runner Script:** `MyTradingSys/research/pitchfork_2026-10-19/run_pitchfork_event_study.py:1-40` [SOURCED: file exists]
- **Ledger/Trial Path:** `MyTradingSys/research/pitchfork_2026-10-19/TRIALS_PITCHFORK.csv:1-5` [SOURCED: file exists]
- **Data Period & Span:** 2020-01-01 to 2026-09-26, 2,461 daily bars [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE1_EVENT_STUDY.md:4`]
- **In-Sample / Out-of-Sample (Split):** `DEV` split (`F:/MTS/data/tom_raw + dev_ext`) [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/TRIALS_PITCHFORK.csv:2-5`]; HOLDOUT unread / NOT_IN_DATA
- **Fee Model:** Net of fees ($0.10\%$ round-trip taker fee + $0.02\%$ slippage hurdle) [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE1_EVENT_STUDY.md:6`]
- **Sample Size ($n$ Setups):** $n = 361$ confirmed swing structures across all 4 geometric models [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE1_EVENT_STUDY.md:16-20`, `TRIALS_PITCHFORK.csv:2-5`]
- **Reported Numbers per Variant ($n = 361$):** [SOURCED: see sub-items]
  1. *Standard Andrews:* ML Reach Rate = $55.96\%$, Avg Bars to ML = $6.5$, Premature Breaches = $50.97\%$, Hagopian Hit Rate = $33.88\%$, Win Rate = $36.84\%$, Mean Net Return = $+0.86\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE1_EVENT_STUDY.md:17`].
  2. *Schiff:* ML Reach Rate = $86.15\%$, Avg Bars to ML = $4.7$, Premature Breaches = $19.11\%$, Hagopian Hit Rate = $33.9\%$, Win Rate = $34.9\%$, Mean Net Return = $-1.12\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE1_EVENT_STUDY.md:18`].
  3. *Modified Schiff:* ML Reach Rate = $89.2\%$, Avg Bars to ML = $4.3$, Premature Breaches = $12.74\%$, Hagopian Hit Rate = $34.04\%$, Win Rate = $36.84\%$, Mean Net Return = $-1.12\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE1_EVENT_STUDY.md:19`].
  4. *Log Modified Schiff:* ML Reach Rate = $90.03\%$, Avg Bars to ML = $4.6$, Premature Breaches = $12.74\%$, Hagopian Hit Rate = $34.0\%$, Win Rate = $37.12\%$, Mean Net Return = $-0.95\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE1_EVENT_STUDY.md:20`].

### B. Phase 2 4-Hour (4H) Pitchfork & Volume Profile Event Study (2020–2026)
- **Report Path:** `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:1-121` [SOURCED: file exists]
- **Runner Script:** `MyTradingSys/research/pitchfork_2026-10-19/run_pitchfork_4h_poc_study.py:1-40` [SOURCED: file exists]
- **Ledger/Trial Path:** `MyTradingSys/research/pitchfork_2026-10-19/TRIALS_PITCHFORK_4H.csv:1-33` [SOURCED: file exists]
- **Data Period & Span:** 2020-01-01 00:00:00 to 2026-09-26 20:00:00, 14,766 4-hour bars [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:4`]
- **In-Sample / Out-of-Sample (Split):** `DEV` dataset; HOLDOUT unread / NOT_IN_DATA [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:4`, `TRIALS_PITCHFORK.csv:2`]
- **Fee Model:** Net of fees (Binance VIP0: $0.02\%$ maker entry + $0.05\%$ taker exit + $0.02\%$ slippage = $0.09\%$ limit round-trip; $0.12\%$ market round-trip) [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:7`]
- **Sample Size ($n$ Setups):** $n = 1,273$ alternating 3-pivot swing structures across 32 experimental conditions [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:6, 36-70`]
- **Key Reported Conditions & Numbers ($n$ fills / trades):** [SOURCED: see sub-items]
  1. *Standard Andrews (UNFILTERED, TINE_LIMIT_RETEST):* Qualified Setups = $1,273$, Fills $n = 1,045$, Win Rate = $27.56\%$, ML Reach = $19.04\%$, Mean Net PnL = $+0.39\%$, Profit Factor = $1.34$, Avg Win = $+5.57\%$, Avg Loss = $-1.58\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:38`].
  2. *Standard Andrews (UNFILTERED, CONFIRM_CLOSE_MKT):* Qualified Setups = $1,273$, Fills $n = 1,273$, Win Rate = $30.95\%$, ML Reach = $47.53\%$, Mean Net PnL = $-0.93\%$, Profit Factor = $0.41$, Avg Win = $+2.10\%$, Avg Loss = $-2.29\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:39`].
  3. *Standard Andrews (VA_CONFLUENT, TINE_LIMIT_RETEST):* Qualified Setups = $326$, Fills $n = 282$, Win Rate = $29.79\%$, ML Reach = $21.63\%$, Mean Net PnL = $+0.69\%$, Profit Factor = $1.62$, Avg Win = $+6.05\%$, Avg Loss = $-1.58\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:40`].
  4. *Standard Andrews (POC_1.5PCT, TINE_LIMIT_RETEST):* Qualified Setups = $177$, Fills $n = 162$, Win Rate = $33.95\%$, ML Reach = $25.31\%$, Mean Net PnL = $+0.88\%$, Profit Factor = $1.83$, Avg Win = $+5.67\%$, Avg Loss = $-1.59\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:42`].
  5. *Schiff (UNFILTERED, TINE_LIMIT_RETEST):* Qualified Setups = $1,273$, Fills $n = 758$, Win Rate = $29.68\%$, ML Reach = $26.12\%$, Mean Net PnL = $+0.05\%$, Profit Factor = $1.04$, Avg Win = $+3.86\%$, Avg Loss = $-1.56\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:46`].
  6. *Schiff (VA_CONFLUENT, TINE_LIMIT_RETEST):* Qualified Setups = $326$, Fills $n = 285$, Win Rate = $30.18\%$, ML Reach = $24.21\%$, Mean Net PnL = $+0.36\%$, Profit Factor = $1.33$, Avg Win = $+4.79\%$, Avg Loss = $-1.56\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:48`].
  7. *Modified Schiff (UNFILTERED, TINE_LIMIT_RETEST):* Qualified Setups = $1,273$, Fills $n = 782$, Win Rate = $34.14\%$, ML Reach = $30.43\%$, Mean Net PnL = $+0.18\%$, Profit Factor = $1.18$, Avg Win = $+3.81\%$, Avg Loss = $-1.70\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:54`].
  8. *Modified Schiff (UNFILTERED, CONFIRM_CLOSE_MKT):* Qualified Setups = $1,273$, Fills $n = 1,273$, Win Rate = $41.87\%$, ML Reach = $87.98\%$, Mean Net PnL = $-0.76\%$, Profit Factor = $0.43$, Avg Win = $+1.66\%$, Avg Loss = $-2.50\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:55`].
  9. *Modified Schiff (VA_CONFLUENT, TINE_LIMIT_RETEST):* Qualified Setups = $326$, Fills $n = 279$, Win Rate = $39.07\%$, ML Reach = $34.05\%$, Mean Net PnL = $+0.61\%$, Profit Factor = $1.63$, Avg Win = $+4.67\%$, Avg Loss = $-1.99\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:56`].
  10. *Log Modified Schiff (VA_CONFLUENT, TINE_LIMIT_RETEST):* Qualified Setups = $326$, Fills $n = 278$, Win Rate = $37.05\%$, ML Reach = $31.65\%$, Mean Net PnL = $+0.59\%$, Profit Factor = $1.59$, Avg Win = $+4.61\%$, Avg Loss = $-1.77\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:64`].
  11. *Log Modified Schiff (POC_0.75PCT, TINE_LIMIT_RETEST):* Qualified Setups = $51$, Fills $n = 42$, Win Rate = $45.24\%$, ML Reach = $42.86\%$, Mean Net PnL = $+0.54\%$, Profit Factor = $1.62$, Avg Win = $+3.52\%$, Avg Loss = $-1.92\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:68`].

### C. Algorithmic Benchmarking of YouTube & Practitioner Models
- **Report Path:** `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:86-111` [SOURCED: file exists]
- **Runner Script:** `MyTradingSys/research/pitchfork_2026-10-19/eval_btc_pitchfork_traders.py:1-40` [SOURCED: file exists]
- **Data Period & Span:** Macro Bitcoin swings 2017 to 2026 [SOURCED: `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:86-88`]
- **Fee Model:** NOT_IN_DATA (Evaluates geometric channel metrics: slope angle, ML reach rate, premature breach rate, and edge score) [SOURCED: `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:89-111`]
- **In-Sample / Out-of-Sample:** NOT_IN_DATA
- **Sample Size ($n$):** NOT_IN_DATA (Evaluated across canonical 1W macro swings) [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/eval_btc_pitchfork_traders.py:34-40`]
- **Results Summary Table:** [SOURCED: see sub-items]
  1. *Fractal Flow (Mod. Schiff, Vol Profile Confluence):* Slope = $28^\circ - 35^\circ$, ML Reach = $81.2\%$, Premature Breach = $8.4\%$, Algorithmic Edge Score = $92/100$ [SOURCED: `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:93-95`].
  2. *MTS Operator Model (Stacked Schiff Grid, TV Style):* Slope = $32^\circ - 42^\circ$, ML Reach = $78.5\%$, Premature Breach = $11.2\%$, Algorithmic Edge Score = $90/100$ [SOURCED: `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:96-98`].
  3. *Timothy Morge / Mikula (Standard + Mod. Schiff, Hagopian):* Slope = $35^\circ - 45^\circ$, ML Reach = $77.8\%$, Premature Breach = $12.0\%$, Algorithmic Edge Score = $88/100$ [SOURCED: `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:99-100`].
  4. *Bob Loukas (Logarithmic Andrews):* Slope = $25^\circ - 32^\circ$, ML Reach = $75.0\%$, Premature Breach = $9.8\%$, Algorithmic Edge Score = $85/100$ [SOURCED: `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:102-104`].
  5. *CryptoCred (Standard, Strict S/R):* Slope = $40^\circ - 55^\circ$, ML Reach = $71.4\%$, Premature Breach = $18.5\%$, Algorithmic Edge Score = $82/100$ [SOURCED: `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:105-107`].
  6. *Generic Retail Tutorials (Standard Linear):* Slope = $65^\circ - 78^\circ$, ML Reach = $48.2\%$, Premature Breach = $62.4\%$, Algorithmic Edge Score = $24/100$ [SOURCED: `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:108-110`].

---

## 4. KNOWN BUGS, FABRICATIONS OR ASSUMPTIONS (Rulings)

- **Official Lab Rulings:** Query command `python scripts/dev/lab_query.py rulings pitchfork` returns `{"family": "pitchfork", "rulings": []}`. There are currently zero recorded lab rulings against family `pitchfork` [SOURCED: `python scripts/dev/lab_query.py rulings pitchfork`].
- **Late-Entry Penalty Bug / Structural Drag in Naive Market Entries:** The Phase 2 study identified that entering on the market close of the confirmation bar (`CONFIRM_CLOSE_MKT`, 16 hours after Pivot 2) caused negative expectancy ($-0.16\%$ to $-1.31\%$) across all models because $40\%-60\%$ of the move toward the Median Line had already transpired while the full stop-loss remained [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:19-22, 75-77`].
- **Linear Slope Distortion & Premature Boundary Breaches:** Standard Andrews Pitchfork on arithmetic scales produces steep slopes ($> 60^\circ$ to $78^\circ$) on Bitcoin, resulting in a high rate of premature false tine breaches ($42.5\%$ to $62.4\%$) during normal sideways consolidations [SOURCED: `papers/02_PITCHFORK_APPLICATION_ON_BTC.md:29-32`, `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:108-110, 118-120`, `MyTradingSys/research/pitchfork_2026-10-19/PHASE1_EVENT_STUDY.md:30-32`].
- **Subjective / Cherry-Picked Anchor Risk:** Discretionary chartists select anchor pivots with hindsight; algorithmic implementations must enforce non-repainting ZigZag confirmation with lookahead delays ($N \ge 3$ or $N \ge 4$ bars) [SOURCED: `papers/02_PITCHFORK_APPLICATION_ON_BTC.md:68-96`, `MyTradingSys/research/live_reads/2026-10-17_live_market_1017/SET_362293de1b70_pitchfork.md:27-28`].
- **Missing Raw Coordinates in TradingView Export:** Exact anchor coordinate numbers from the MTS Operator's TradingView charts are not stored in any repo file (`NOT_IN_DATA`) [SOURCED: `MyTradingSys/research/live_reads/2026-10-17_live_market_1017/SET_362293de1b70_pitchfork.md:17`].

---

## 5. CONFLUENCE (Which Layers It Confirms or Is Confirmed By)

The pitchfork layer is designed as a **Layer 1 Dynamic Location & Horizon Filter** that is confirmed by, and provides confluence to, the following layers:

1. **Tom Core / Microstructural Proof Gates (`src/main/java/datafeed/SetupCandidatesBuilder.java`):** [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:62-72`]
   - *Absorption Proof (`proof_absorption`):* At the Lower Median Line ($LML$), volume on the 5-minute bar must exceed the 80th percentile with negative Delta, but price closes in the upper half of the bar (passive buy absorption) [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:65-66`].
   - *CVD Alignment Proof (`proof_cvd_aligned`):* At the bounce point, Cumulative Volume Delta must not diverge downward against the trade direction [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:67-68`].
   - *Delta Flip Proof (`proof_delta_flip`):* Confirmation bar following the tine touch exhibits positive Delta on an up-close [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:69-70`].
2. **Volume Profile Layers (Anchored POC / Value Area High & Low):** [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:25-29`]
   - *Value Area Confluence (`VA_CONFLUENT`):* Swing origin pivot $P_2$ must reside within the 70% Value Area $[VAL, VAH]$ of the foundational impulse swing [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:26, 80-82`].
   - *Point of Control Confluence (`POC_1.5PCT` / `POC_0.75PCT`):* Tine touches aligning within $\pm 0.75\%$ to $\pm 1.5\%$ of the Point of Control [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:27-28, 88-92`].
   - Confluence with high-volume POC or prior session VAH/VAL increases reaction probability from $77.7\%$ to $86.4\%-88.4\%$ [SOURCED: `papers/02_PITCHFORK_APPLICATION_ON_BTC.md:206-208`, `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:124-125`].
3. **CryptoCred Dynamic Channels & Swing Failure:** [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:169-172`]
   - Treats the pitchfork Median Line as dynamic Fair Value / Point of Control, and outer tines as dynamic support/resistance corridors aligned with swing failure patterns [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:169-172`, `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:36-38`].
4. **Positioning / Open Interest Delta:** [SOURCED: `papers/02_PITCHFORK_APPLICATION_ON_BTC.md:156-163`]
   - In Hagopian failures, buyer/seller exhaustion before the Median Line accompanied by rising Open Interest and stagnating CVD precedes liquidation cascades [SOURCED: `papers/02_PITCHFORK_APPLICATION_ON_BTC.md:156-163`].
