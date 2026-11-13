# Blind Review: edge4-malkan-divergence

**Verdict: SOUND** (The reported data, statistical tests, fee modeling, and arithmetic are internally consistent; the conclusion of "FAIL / no edge" is mathematically sound and follows directly and unambiguously from the results table).

**What would change the verdict:**
- To **FLAWED**: If trade reconstruction revealed future data leakage in pivot detection (e.g. divergence confirmed before the right shoulder / swing confirmation bar closed), or if the trade execution walk looked into intraday bar lows/highs simultaneously without strict causal time ordering.
- To **UNVERIFIABLE**: If underlying raw trade logs or cache files (e.g. `cells.csv`, `summary.json`) contradicted the sample sizes, mean returns, or day-clustered confidence intervals reported in `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md`.

---

## 1. Scope and Inputs

- **Source File**: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md:1-41`
- **Methodology**: Strict blind review based solely on the provided study summary text and tables, without access to external reviews, prior claims, or underlying study source code. All cited figures are explicitly labeled as SOURCED (with exact `file:line` citation) or OURS (independent recalculation).

---

## 2. Table and Arithmetic Consistency Verification

### 2.1 Table Claims and Internal Consistency (YES / NO / CANNOT-TELL)

- **Claimed Cell Count & Pass/Fail Verdict**:
  - SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md:3`): "Verdict: FAIL / no edge. 0 of 24 cells PASS (VALIDATION fee-net mean R > 0, day-clustered CI lower > 0, n >= 30, placebo p <= 0.05, BH 10 %)."
  - OURS (recomputation): The table at `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md:10-33` contains exactly 24 rows across two timeframes (1h and 4h), two rule variations (R03 shorts and R04 longs), two window lengths (W12 and W18), and three exit configurations (1R, 2R, T12):
    - 1h cells: 12 rows (all with mean R VAL between -0.216 and -0.247; all day-clustered CI lower bounds well below zero).
    - 4h cells: 12 rows (10 rows negative mean R; 2 rows with mean R = +0.030, but with day-clustered CI lower bounds of -0.125).
    - Criteria check: Not a single cell satisfies `VALIDATION fee-net mean R > 0` AND `day-clustered CI lower > 0`. All 24 cells have `verdict = FAIL` and `BH = no`.
    - **Verdict follows from the table**: **YES**.

- **Regime Mix Percentages**:
  - VALIDATION 150 weeks:
    - SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md:1`): "Regime mix: VALIDATION 150 weeks: bull 84 (56%) | bear 46 (31%) | range 20 (13%) | n/a 0 (0%) (BTC weekly close vs 200d SMA +-5 %)"
    - OURS (recomputation): 84 + 46 + 20 + 0 = 150 weeks. 84/150 = 56.00%, 46/150 = 30.67% (rounds to 31%), 20/150 = 13.33% (rounds to 13%). Sum of rounded percentages: 56% + 31% + 13% = 100%. **Consistent (YES)**.
  - DEV 197 weeks:
    - SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md:5`): "Regime mix DEV: 197 weeks: bull 89 (45%) | bear 66 (34%) | range 14 (7%) | n/a 28 (14%)"
    - OURS (recomputation): 89 + 66 + 14 + 28 = 197 weeks. 89/197 = 45.18% (rounds to 45%), 66/197 = 33.50% (rounds to 34%), 14/197 = 7.11% (rounds to 7%), 28/197 = 14.21% (rounds to 14%). Sum of rounded percentages: 45% + 34% + 7% + 14% = 100%. **Consistent (YES)**.
  - RECENT 71 weeks:
    - SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md:5`): "RECENT: 71 weeks: bull 26 (37%) | bear 39 (55%) | range 6 (8%) | n/a 0 (0%)"
    - OURS (recomputation): 26 + 39 + 6 = 71 weeks. 26/71 = 36.62% (rounds to 37%), 39/71 = 54.93% (rounds to 55%), 6/71 = 8.45% (rounds to 8%). Sum of rounded percentages: 37% + 55% + 8% = 100%. **Consistent (YES)**.

- **Cost and Fee Drag in R**:
  - SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md:6`): "Costs: 2 x BINANCE_TAKER + SLIPPAGE_RT_S13 = 12.00 bp round trip, charged on entry, converted to R."
  - SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md:39`): "Median stop distance is 0.9 % (1h) and 2.0 % (4h): at 12 bp round trip the cost alone is about 0.14 R (1h) and 0.06 R (4h) per trade."
  - OURS (recomputation): 12 bp = 0.0012. For 1h stop of 0.9% (0.009), cost in R = 0.0012 / 0.009 = 0.1333 R (approx 0.13-0.14 R). For 4h stop of 2.0% (0.020), cost in R = 0.0012 / 0.020 = 0.0600 R (exactly 0.06 R). **Consistent (YES)**.

- **Sample Size Clustering by Setup**:
  - SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md:10-33`):
    - For 1h R03 W12 (1R, 2R, T12): DEV n = 5226, VAL n = 6181 across all 3 exit variations.
    - For 1h R03 W18 (1R, 2R, T12): DEV n = 5247, VAL n = 6200 across all 3 exit variations.
    - For 1h R04 W12 (1R, 2R, T12): DEV n = 5247, VAL n = 6319 across all 3 exit variations.
    - For 1h R04 W18 (1R, 2R, T12): DEV n = 5264, VAL n = 6336 across all 3 exit variations.
    - For 4h R03 W12 (1R, 2R, T12): DEV n = 1289, VAL n = 1364 across all 3 exit variations.
    - For 4h R03 W18 (1R, 2R, T12): DEV n = 1292, VAL n = 1364 across all 3 exit variations.
    - For 4h R04 W12 (1R, 2R, T12): DEV n = 1280, VAL n = 1577 across all 3 exit variations.
    - For 4h R04 W18 (1R, 2R, T12): DEV n = 1284, VAL n = 1579 across all 3 exit variations.
  - OURS (analysis): Entry counts are invariant to the exit rules (1R, 2R, T12) within the same setup, as expected for identical entry conditions. **Consistent (YES)**.

- **Best 3 Cells Reported vs Table**:
  - SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md:35`): "Best 3 by VALIDATION mean R: R03_4h_W12_T12 +0.030 (n 1364, cluster CI lower -0.125, placebo p 0.0); R03_4h_W18_T12 +0.030 (n 1364, cluster CI lower -0.125, placebo p 0.0); R03_4h_W12_2R -0.003 (n 1364, cluster CI lower -0.096, placebo p 0.0)"
  - OURS (verification): Inspecting all 24 table rows confirms that +0.030, +0.030, and -0.003 are indeed the highest three VALIDATION mean R values (tied with R03_4h_W18_2R at -0.003). **Consistent (YES)**.

---

## 3. Concrete Methodological Risks Exposed in Text

### 3.1 Look-Ahead Bias Risk
- SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md:6`): "Data end 2026-11-13 18:00 UTC. 20 Bybit USDT perps, 1h; 4h folded."
- SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md:37`): "Not a deployable PASS even if a row says PASS: needs a causal replay test and an independent trade-loop re-run first (CLAUDE.md)."
- **Exposure / Analysis**:
  - The study uses "4h folded" bars derived from 1h or higher timeframe aggregations. In divergence studies, identifying swing highs/lows or divergence points often requires several bars to confirm a pivot. The text does not detail whether pivot confirmation requires future bars; however, the author explicitly mandates a causal replay test before any strategy could be accepted (`file:line` 37).
  - Furthermore, `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md:6` notes "Data end 2026-11-13 18:00 UTC." Because the edge is conclusively rejected (FAIL across all cells), look-ahead bias would only be an issue if it artificially inflated returns; here, even potential look-ahead failed to produce positive expectancy.

### 3.2 Fee and Slippage Handling Risk
- SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md:6`): "Costs: 2 x BINANCE_TAKER + SLIPPAGE_RT_S13 = 12.00 bp round trip, charged on entry, converted to R."
- SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md:39`): "Median stop distance is 0.9 % (1h) and 2.0 % (4h): at 12 bp round trip the cost alone is about 0.14 R (1h) and 0.06 R (4h) per trade."
- **Exposure / Analysis**:
  - The fee modeling is conservative and rigorous: charging 12.00 bp round-trip taker fees upfront converted to R.
  - The text exposes a fatal structural vulnerability for 1h trading: because the median stop distance is small (0.9%), the fixed 12 bp fee consumes 0.14 R per trade. For 1h cells where net R is around -0.22 to -0.24 R, transaction friction accounts for over 55-60% of the entire net loss.
  - No funding rate modeling is mentioned in the text, though given holding periods on 1h and 4h (e.g. T12 bars = 12h or 48h), funding rate drag could further degrade performance.

### 3.3 Placebo Validity Risk
- SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md:39`): "placebo p = share of 200 random same-coin same-week entries (same side, stop distance and exit rule) with mean R >= the real cell, so 0.000 means the divergence signal beats random entries. It does, in every cell, but random entries are themselves -0.24 to -0.41 R after the 12 bp cost, so beating them still leaves 22 of 24 cells below zero"
- SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md:40`): "Code fix during the run: the first run set the placebo stop of shorts on the wrong side of entry (placebo for R03 was invalid, showing p 1.000); fixed with `placebo_stop` (+ test) and re-run; the real-trade numbers did not change."
- **Exposure / Analysis**:
  - The placebo test compares real trades against random same-coin, same-week entries. While every cell achieves `placebo p = 0.000`, the text correctly identifies that this benchmark is artificially easy to beat: random entries suffer massive drag (-0.24 to -0.41 R) from fees and tight stops. Beating a severely negative baseline does not demonstrate positive economic value.
  - The text transparently documents an in-flight bug fix where short placebo stops were originally placed on the wrong side of entry, requiring a re-run with `placebo_stop`.

### 3.4 Clustering and Cross-Asset Independence Risk
- SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md:39`): "Pooling 20 coins (n about 6,200 per 1h cell in VALIDATION) removes the BTC-only power problem: the 1h result is a tight negative (CI upper bounds -0.12 to -0.18), not a noisy one."
- SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md:10`): "| R03_1h_W12_1R | 5226 | 6181 | -0.246 | [-0.284, -0.207] | [-0.272, -0.221] | -0.304, 0.000 | no | FAIL |"
- SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md:37`): "Coverage: BTC from 2020-03-25, ETH from 2021-03-15, SOL from 2021-10-15, XRP from 2021-05-13, DOGE from 2021-06-02, BNB from 2021-06-29, ADA from 2021-03-18, LINK from 2020-10-21, LTC from 2020-10-21, AVAX from 2021-09-15, DOT from 2021-03-18, TRX from 2021-08-31, ATOM from 2021-10-11, NEAR from 2021-10-11, UNI from 2021-11-30, ETC from 2021-06-29, BCH from 2020-12-14, FIL from 2021-06-29, AAVE from 2021-05-13, XLM from 2021-08-31"
- **Exposure / Analysis**:
  - The study pools 20 cryptocurrency pairs over the same historical calendar period. Crypto assets exhibit high cross-sectional correlation during market-wide momentum or liquidation waves.
  - The author explicitly accounts for this by computing day-clustered confidence intervals (`CI (day-cluster)`) alongside standard unclustered intervals (`CI (per-trade)`).
  - As observed across the table (e.g. `file:line` 10: `[-0.284, -0.207]` vs `[-0.272, -0.221]`; `file:line` 24: `[-0.125, +0.210]` vs `[-0.087, +0.156]`), the day-clustered intervals are consistently wider, properly reflecting the reduced effective sample size resulting from cross-coin correlation.
  - Staggered asset start dates (from 2020-03-25 for BTC up to 2021-11-30 for UNI) mean earlier periods have fewer coins represented, slightly weighting later periods.

### 3.5 Multiple Testing and Subgroup Leakage Risk
- SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md:3`): "BH 10 %"
- SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md:40`): "Only these 24 cells were run; none tuned."
- SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-malkan-divergence_RESULTS.md:39`): "DEV is also negative (-0.006 to -0.07) and RECENT (>= 2025-07) positive on R03 4h (n 605, +0.19 R at T12), a lead only, not a pass."
- **Exposure / Analysis**:
  - The study applied the Benjamini-Hochberg (BH 10%) procedure across all 24 cells; zero cells passed.
  - The text notes that 4h R03 counter-trend shorts exhibited a positive subset in RECENT data (+0.19 R at T12, n=605). However, the author conservatively labels this as "a lead only, not a pass" due to negative DEV results (-0.006 to -0.07) and failure to clear the full validation gate. This protects against post-hoc subgroup selection.

---

## 4. Final Assessment

The reporting in `edge4-malkan-divergence_RESULTS.md` is statistically disciplined, transparent, and thorough. All mathematical checks recomputed from the text (percentages, fee drag conversions, row counts, confidence interval expansions) align with the reported conclusions. The decision to declare FAIL / no edge is fully supported by the empirical data.
