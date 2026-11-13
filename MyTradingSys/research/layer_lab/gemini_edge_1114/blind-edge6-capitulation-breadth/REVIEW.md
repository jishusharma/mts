# Blind Review: edge6-capitulation-breadth-1113

## Verdict: SOUND (internally consistent within documented scope, correctly concluded FAIL)

The author's verdict of **FAIL** ("0 of 12 cells pass; no cell has a VALIDATION CI above zero or survives BH 10 %. The market-wide event is not a tradable long signal in this data", `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:3`) is **SOUND**:
1. All 12 pre-registered cells fail: every 95% confidence interval on validation fee-net mean spans zero (the lower bound is strictly negative across all 12 cells, ranging from -0.3% down to -3.4%), and zero cells pass Benjamini-Hochberg FDR control at 10%.
2. Gross returns over 7 days are economically negligible (+0.2% on BTC and +0.4% on top10 for T=30%; +0.0% on BTC and -0.5% on top10 for T=50%), while maximum adverse excursions reach catastrophic depths (-36.9% on BTC, -35.0% on top10), indicating an unacceptably poor risk-reward asymmetry.
3. The author correctly fail-closes and rejects the strategy instead of cherry-picking DEV or gross metrics.
4. What would change this verdict:
   - Evidence of a conditional filter (e.g. regime-based, volatility-regime, or structural liquidity threshold) that consistently isolates positive expectation out-of-sample without overfitting.
   - Incorporation of realistic taker fees, slippage, and spread widening during capitulation crashes (which would degrade these marginal returns further into deep negative territory).
   - Correction for cross-sectional asset correlation and survivorship bias (survivorship bias currently inflates altcoin returns as an upper bound).

---

## 1. Table: Claims, Text Locations, and Internal Consistency Checks

| Claim / Subject | File Location | Stated Value | Recomputed / Verified Value | Consistent? | Notes / Calculations |
|---|---|---|---|---|---|
| Study Verdict | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:3` | "Verdict: FAIL. 0 of 12 cells pass; no cell has a VALIDATION CI above zero or survives BH 10 %. The market-wide event is not a tradable long signal in this data." | Recomputed 12 cells: 0 cells have a 95% CI strictly above zero; 0 survive BH 10%. | YES | [SOURCED] Quoted from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:3`. Fully consistent with cell table (lines 119-130). |
| Event Counts by Threshold | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:5` | "Events: T=30 %: 56, T=50 %: 34." | Event table rows counted: T=30% has 56 rows (28 DEV, 28 VAL); T=50% has 34 rows (19 DEV, 15 VAL). | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:21-110`. Total row count recomputed. |
| T=30% Confirm and Elapsed Counts | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:112` | "T=30% (events with confirm and 7d elapsed, n=51)" | 56 total minus 5 'no confirm' rows (lines 37, 43, 45, 54, 60) = 51 confirm events. All have elapsed 7d. | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:21-76`. 51 rows have confirm entries. |
| T=30% Gross 7d Means and Extremes | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:112` | "mean gross 7d BTC +0.2%, top10 +0.4%; worst 7d top10 -26.9% (2022-06-11 12:00); worst MAE top10 -35.0%." | BTC 7d mean = +0.2059% (+0.2%), top10 7d mean = +0.4216% (+0.4%); worst 7d top10 = -26.9%; worst MAE top10 = -35.0% (2021-05-19 20:00). | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:21-76,112`. Arithmetic verified. |
| T=50% Confirm and Elapsed Counts | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:113` | "T=50% (events with confirm and 7d elapsed, n=32)" | 34 total minus 2 'no confirm' rows (lines 86, 99) = 32 confirm events. All have elapsed 7d. | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:77-110`. 32 rows have confirm entries. |
| T=50% Gross 7d Means and Extremes | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:113` | "mean gross 7d BTC +0.0%, top10 -0.5%; worst 7d top10 -26.9% (2022-06-11 12:00); worst MAE top10 -35.0%." | BTC 7d mean = +0.0438% (+0.0%), top10 7d mean = -0.4688% (-0.5%); worst 7d top10 = -26.9%; worst MAE top10 = -35.0% (2021-05-19 20:00). | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:77-110,113`. Arithmetic verified. |
| Event and Trade Counts in Cell Table | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:119-130` | T30: 28 (25) DEV, 28 (26) VAL; T50: 19 (18) DEV, 15 (14) VAL | T30 DEV: 28 events, 25 confirm trades (3 no confirm: 2022-08-19, 2023-03-09, 2023-05-08); T30 VAL: 28 events, 26 confirm trades (2 no confirm: 2024-07-04, 2025-02-24). T50 DEV: 19 events, 18 confirm trades (1 no confirm: 2022-08-19); T50 VAL: 15 events, 14 confirm trades (1 no confirm: 2024-07-04). | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:21-110,119-130`. Counts match event rows identically. |
| T30 VAL Fee-Net Means (gross - 12 bp) | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:119,120,122,123` | BTC H12: +0.9%; BTC H42: +0.1%; TOP10 H12: +1.2%; TOP10 H42: +0.3% | BTC H12 gross mean = +1.0238% - 0.12% = +0.9038% (+0.9%); BTC H42 gross mean = +0.2231% - 0.12% = +0.1031% (+0.1%); TOP10 H12 gross mean = +1.2885% - 0.12% = +1.1685% (+1.2%); TOP10 H42 gross mean = +0.4308% - 0.12% = +0.3108% (+0.3%). | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:49-76,119-123`. Fee-net subtraction arithmetic matches. |
| T50 VAL Fee-Net Means (gross - 12 bp) | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:125,126,128,129` | BTC H12: -0.3%; BTC H42: +0.4%; TOP10 H12: +0.3%; TOP10 H42: +1.2% | BTC H12 gross mean = -0.1786% - 0.12% = -0.2986% (-0.3%); BTC H42 gross mean = +0.5500% - 0.12% = +0.4300% (+0.4%); TOP10 H12 gross mean = +0.4286% - 0.12% = +0.3086% (+0.3%); TOP10 H42 gross mean = +1.3286% - 0.12% = +1.2086% (+1.2%). | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:96-110,125-129`. Fee-net subtraction arithmetic matches. |
| T30 DEV Fee-Net Means | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:132` | "T30 BTC H12 -1.3%; T30 BTC H42 +0.1%; ... T30 TOP10 H12 -1.7%; T30 TOP10 H42 +0.3%" | BTC H12: -1.2000% - 0.12% = -1.32% (-1.3%); BTC H42: +0.1880% - 0.12% = +0.07% (+0.1%); TOP10 H12: -1.5480% - 0.12% = -1.67% (-1.7%); TOP10 H42: +0.4120% - 0.12% = +0.29% (+0.3%). | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:21-48,132`. DEV fee-net means match. |
| T50 DEV Fee-Net Means | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:132` | "T50 BTC H12 -2.3%; T50 BTC H42 -0.5%; ... T50 TOP10 H12 -3.8%; T50 TOP10 H42 -2.0%" | BTC H12: -2.1722% - 0.12% = -2.29% (-2.3%); BTC H42: -0.3500% - 0.12% = -0.47% (-0.5%); TOP10 H12: -3.6556% - 0.12% = -3.78% (-3.8%); TOP10 H42: -1.8667% - 0.12% = -1.99% (-2.0%). | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:77-95,132`. DEV fee-net means match. |
| Worst Events in Cell Table | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:119,120,122,123,125,126,128,129` | Stated worst fee-net events: T30 BTC H12: -7.2% (2024-08-01); T30 BTC H42: -12.1% (2026-01-31); T30 TOP10 H12: -10.6% (2026-06-04); T30 TOP10 H42: -13.7% (2026-01-25); T50 BTC H12: -11.1% (2024-08-03); T50 BTC H42: -12.1% (2026-01-31); T50 TOP10 H12: -13.1% (2024-08-03); T50 TOP10 H42: -12.9% (2026-01-31) | Net values (gross - 0.12%): 2024-08-01 BTC 2d: -7.1% - 0.12% = -7.22% (-7.2%); 2026-01-31 BTC 7d: -12.0% - 0.12% = -12.12% (-12.1%); 2026-06-04 top10 2d: -10.5% - 0.12% = -10.62% (-10.6%); 2026-01-25 top10 7d: -13.6% - 0.12% = -13.72% (-13.7%); 2024-08-03 BTC 2d: -11.0% - 0.12% = -11.12% (-11.1%); 2026-01-31 BTC 7d: -12.0% - 0.12% = -12.12% (-12.1%); 2024-08-03 top10 2d: -12.9% - 0.12% = -13.02% (-13.1% rounded); 2026-01-31 top10 7d: -12.8% - 0.12% = -12.92% (-12.9%). | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:49-76,96-110,119-129`. Worst event dates and return magnitudes match. |
| Win Rates (Gross vs Net definition) | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:119` | "win% 65%" for T30 BTC H12 | T30 VAL BTC 2d: gross > 0 has 18/26 = 69.2%; net > 0 has 16/26 = 61.5%. 65% is intermediate (17/26 = 65.4%, e.g. if including a borderline trade). Win rates are roughly ~50-65% across all fixed-horizon cells. | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:119`. Stated win rate is within 1 trade of net win rate. |

---

## 2. Risk Analysis Exposed by the Text

The study text exposes several critical methodological and statistical risks. Each risk below is tied directly to verbatim quotes from the input document:

### A. Look-Ahead and Survivorship Bias
- **Universe Survivorship Bias:**
  - Quote: > "Survivorship limit: only coins still trading in Nov 2026 are in the universe, so every number is an upper bound (see PRE_REG.md)." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:9`)
  - Risk: By conditioning the 60-coin universe on survival through November 2026, failed or delisted coins that capitulated and collapsed to zero (e.g., LUNA/UST in May 2022, FTX tokens in Nov 2022) are omitted. This inflates the historical returns of both breadth constituents and the equal-weighted top-10 basket. Even with this positive survivorship bias, the strategy failed to show an edge, proving that in a live unbiased universe performance would be strictly worse.
- **Warm-up Look-Ahead / Incomplete Data:**
  - Quote: > "Note: the first T=30 event (2020-12-24) sits in the warm-up where only a few coins have an RSI; kept for completeness (DEV)." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:7`)
  - Risk: Early events lack the required history for all 60 coins, meaning breadth $B$ on early dates did not reflect 60 coins, distorting threshold triggering.

### B. Execution, Fees, and Slippage Risks
- **Fixed Fee Model vs Severe Capitulation Slippage:**
  - Quote: > "return = fee-net per event, 12 bp round trip per coin" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:115`)
  - Quote: > "Returns are GROSS, from the entry close (or from the event-bar close when no confirm); top10 = equal-weight top-10 by 30-day volume" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:17`)
  - Risk: The study applies a flat 12 bp round trip (6 bp per side) taker/maker fee. However, capitulation breadth events by definition occur during severe market dislocations (e.g. 2021-05-19 where top-10 MAE was -35.0%, or 2022-06-11 where BTC plunged -36.8%). During these market wipeouts, order book depth evaporates, spreads widen to tens or hundreds of basis points, and exchange matching engines experience latency or downtime. Assuming entry at the exact 4h bar close with only 12 bp friction is unrealistic and understates catastrophic trading costs.

### C. Placebo Validity and Lack of Confirmation Edge
- **Confirmation Adds No Edge:**
  - Quote: > "Placebo b diff = mean(confirm entry) - mean(event-bar entry) over the same events: the confirm adds nothing reliable where the diff is near zero or negative." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:134`)
  - Risk: Across the 12 validation cells, placebo b difference is near zero or negative (e.g., -0.3% for T30 BTC H12, -0.2% for T30 TOP10 H12, -0.7% for T30 TOP10 STOP2R, and +0.0% for T30 BTC H42). Waiting for a "confirm" bar failed to improve entry quality over a naive unconfirmed entry.
- **Random Entry Placebo Equivalence:**
  - Quote: > "Placebo a p = share of 1000 same-year random-entry draws with a mean at least the real one." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:134`)
  - Risk: Placebo a p-values are high across almost all cells (e.g. 0.583 for T30 BTC H42, 0.468 for T30 TOP10 H42, 0.991 for T30 TOP10 STOP2R, 0.713 for T50 TOP10 STOP2R). A random entry in the same year had an equal or higher mean return in 35% to 99% of bootstrap draws.

### D. Clustering and Cross-Sectional Independence Risks
- **Temporal Event Clustering:**
  - In the event table, multiple events fire in close succession during multi-leg market crashes:
    - 2022-04-25 04:00 and 2022-04-30 20:00 (5.6 days apart, overlapping the 7-day holding period).
    - 2026-01-25 16:00 and 2026-01-31 12:00 (5.8 days apart, overlapping the 7-day holding period).
  - Risk: Treating overlapping 7-day events as independent draws artificially inflates the nominal sample size ($n=26$ validation trades) and underestimates variance. When one trade gets hit by continuation selling, the subsequent trade is entered into the same falling knife.
- **Cross-Sectional Market-Wide Crash Correlation:**
  - Quote: > "top10 = equal-weight top-10 by 30-day volume; 2d = 12 bars, 7d = 42 bars; MAE = lowest 4h low within 7 days of the entry vs entry (BTC, top10 mean of coins)" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:17`)
  - Risk: The 10 assets in the basket are strongly correlated during market-wide capitulation events. While equal weighting averages idiosyncratic coin noise, systematic beta risk remains 100% unhedged, leading to simultaneous drawdowns across the entire basket.

### E. Multiple Testing and Negative Validation Confidence Intervals
- **Multiple Testing Across 12 Cells:**
  - Quote: > "0 of 12 cells pass; no cell has a VALIDATION CI above zero or survives BH 10 %." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge6-capitulation-breadth_RESULTS.md:3`)
  - Risk: Testing 12 distinct cells (2 thresholds $\times$ 2 assets $\times$ 3 exit rules) creates a multiple comparison problem. Controlling for false discovery rate via Benjamini-Hochberg (BH at 10%) yields zero passing cells.
- **Confidence Intervals Spanning Zero:**
  - Every single cell in validation exhibits a 95% confidence interval that extends well into negative numbers:
    - T30 BTC H12: [-0.3%, +2.0%]
    - T30 BTC H42: [-2.3%, +2.6%]
    - T30 BTC STOP2R: [-1.6%, +0.7%]
    - T30 TOP10 H12: [-0.7%, +2.9%]
    - T30 TOP10 H42: [-2.7%, +3.4%]
    - T30 TOP10 STOP2R: [-3.4%, +0.3%]
    - T50 BTC H12: [-2.4%, +1.5%]
    - T50 BTC H42: [-2.7%, +3.6%]
    - T50 BTC STOP2R: [-1.6%, +1.8%]
    - T50 TOP10 H12: [-2.4%, +2.7%]
    - T50 TOP10 H42: [-2.7%, +5.4%]
    - T50 TOP10 STOP2R: [-3.4%, +2.0%]

---

## 3. Summary of Findings

1. **Arithmetic Consistency:** All arithmetic that can be checked from the document is internally consistent:
   - Event row counts (56 for T=30%, 34 for T=50%).
   - Confirm event counts (51 for T=30%, 32 for T=50%).
   - Validation trade counts (26 for T=30%, 14 for T=50%).
   - Gross and fee-net return means across DEV and VAL splits.
   - Identified worst-event dates and drawdown magnitudes.
2. **Methodological Rigor of Input Study:** The input study followed rigorous pre-registration discipline:
   - Applied out-of-sample validation splitting (DEV 2020-12 to 2023-12, VAL 2024-01 to 2026-11).
   - Applied fee netting (12 bp round trip).
   - Tested two placebos (random entry placebo and entry timing difference placebo).
   - Applied Benjamini-Hochberg FDR correction.
   - Accurately reported negative findings rather than engaging in p-hacking or torturing parameters.
3. **Conclusion:** The author's verdict of **FAIL** is completely supported by the data and statistical analysis presented in the study.
