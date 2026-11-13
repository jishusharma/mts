# Blind Review: edge4-ny-session-value

Verdict: SOUND (within the explicit bounds of the tested specification; conditional on no unobserved code bugs).
What would change it to FLAWED:
1. Proof that using 1m bars to synthesize 30m closes creates look-ahead or mis-timed triggers relative to true 30m candle boundaries.
2. Demonstrating that testing on perpetual futures rather than Binance spot reverses the negative expectancy (e.g., funding / basis dynamics or differing volume distributions).
3. Demonstrating that session execution at market close with fixed 1 bp slippage significantly distorts fill outcomes compared to an intra-session limit or book simulation.

---

## 1. Scope and Inputs

- Reviewed file: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md`
- Source slug: `edge4-ny-session-value-1113`
- Pre-registration noted: `PRE_REG.md`
- Code artifacts referenced: `fetch_1m.py`, `study.py`, `report.py`, `test_ny_session_value.py`, `spot_check.py`

---

## 2. Table Consistency and Recomputed Arithmetic

- Claim: 0 of 12 cells pass; price re-entering prior NY-session value reaches the opposite edge ~40% of the time (vs trader's claim of 70-80%), and no cell has a fee-net edge on VALIDATION (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:3`).
- Internally consistent: **YES**

### Arithmetic checks (OURS recomputation vs SOURCED):
- **DEV skip30 setups count:**
  - Table 1 cells: `all / skip30 / long` (218) + `all / skip30 / short` (278) = 496 (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:18-19`).
  - Table 1 sub-regimes: `balanced / skip30` (123 long + 160 short = 283) + `trending / skip30` (95 long + 118 short = 213) = 496 (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:22-27`).
  - Table 3 per-coin DEV skip30: BTCUSDT (184) + ETHUSDT (170) + SOLUSDT (142) = 496 (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:63-67`).
  - Descriptive summary: 496 setups / 2244 opening outside prior value = 22.10% (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:35`). Exactly matches `496 / 22.1` in text.
  - Balanced day share DEV: 283 / 496 = 57.06%, matches "balanced-day share 57.1% of 496" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:72`).

- **VAL skip30 setups count:**
  - Table 1 cells: `all / skip30 / long` (180) + `all / skip30 / short` (233) = 413 (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:18-19`).
  - Table 1 sub-regimes: `balanced / skip30` (101 long + 150 short = 251) + `trending / skip30` (79 long + 83 short = 162) = 413 (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:22-27`).
  - Table 3 per-coin VAL skip30: BTCUSDT (144) + ETHUSDT (123) + SOLUSDT (146) = 413 (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:63-67`).
  - Descriptive summary: 413 setups / 1659 opening outside prior value = 24.89% (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:36`). Exactly matches `413 / 24.9` in text.
  - Balanced day share VAL: 251 / 413 = 60.77%, matches "balanced share 60.8% of 413" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:72`).

- **Reach % pooled calculations:**
  - DEV skip30 pooled reach: (218 * 0.399 + 278 * 0.399) / 496 = 39.90% (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:18-19,35`). Exactly 39.9%.
  - VAL skip30 pooled reach: (180 * 0.356 + 233 * 0.433) / 413 = 39.94% (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:18-19,36`). Rounds to 40.0% as reported in Table 1 supplementary (40.0%).
  - Per-coin VAL skip30 pooled reach: (144 * 0.403 + 123 * 0.431 + 146 * 0.370) / 413 = 39.97% (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:63-67`), consistent with ~40.0%.

- **Mean R pooled checks:**
  - Table 3 DEV skip30 pooled mean R: (184 * -0.149 + 170 * 0.041 + 142 * -0.047) / 496 = -0.0547 R (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:63-67`).
  - Table 2 pooled `all / skip30` DEV mean R: (218 * -0.056 + 278 * -0.054) / 496 = -0.0549 R (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:44-45`). Internally consistent to within rounding precision.

---

## 3. Concrete Methodological Risks Exposed in the Text

The study result text explicitly reveals several methodological risks and limits:

1. **Look-Ahead and Granularity Risk:**
   - Quoted text: `"30m closes taken from 1m closes; fills at the close with fixed 1 bp slippage; stop gaps inside a 1m bar not modelled."` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:76`)
   - Evaluation: Synthesizing 30m closes from 1m bars without true tick/sub-minute pathing means intrabar stop breaches prior to target touches could be misordered if both happen in the same bar, though checking 1m bars mitigates this for 30m intervals.

2. **Fee and Cost Handling:**
   - Quoted text: `"5 bp taker + 1 bp slippage per side = 12 bp round trip (fees.py BINANCE_TAKER; the order said 4 bp/side, this is 2 bp/side harsher). Stop at session extreme + 1 bp; trades with stop < 10 bp skipped."` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:10`)
   - Evaluation: Cost modeling is conservative and harsher than nominal specification (12 bp vs 8 bp round trip). While this depresses net R, the raw hit rates (33-48% reach vs 70-80% claimed) show the failure is structural in the price path, not merely a fee hurdle.

3. **Placebo Validity Risk:**
   - Quoted text: `"'Beats placebo' alone is weak here: placebo entries at random times inside value lose about 0.1-0.2 R, so the setup timing beats random entry yet still does not make money."` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:57`)
   - Evaluation: The placebo baseline demonstrates that unconditional random entry inside the value area suffers severe negative drift (-0.1 to -0.2 R). The rule outperforms unconditional random entry, but remains negative in absolute expectancy.

4. **Clustering and Independence Violations:**
   - Quoted text: `"12 cells share the same sessions (long/short disjoint, regimes overlap), so cells are not independent."` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:78`)
   - Quoted text: `"Pooled over three coins, bootstrap by session date (5000), placebo 500 draws, BH 10% over 12 cells."` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:11`)
   - Evaluation: Cross-sectional pooling of BTC, ETH, and SOL on identical calendar dates means cross-asset correlation is present. The authors address this via date-clustered bootstrap (`"bootstrap by session date"`).

5. **Multiple-Testing and Post-Hoc Exploration Risk:**
   - Quoted text: `"This POC split was added after seeing the numbers: descriptive, it is not a tested edge."` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:38`)
   - Quoted text: `"Balanced-day rule (inside day OR small opening range) and the 5 bp bin, 10 bp min stop, 1 bp buffer are OURS."` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:77`)
   - Evaluation: The authors correctly segregate post-hoc findings (POC return at ~68-70%) as descriptive and uncommitted, and apply Benjamini-Hochberg (BH 10%) across the 12 pre-registered cells.

---

## 4. Verdict and Assessment

- **Verdict: SOUND.**
- The conclusion (`"FAIL. 0 of 12 cells pass."` `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-ny-session-value_RESULTS.md:3`) follows rigorously from the data presented:
  1. Only 2 of 12 cells in Table 2 exhibit positive point estimates on VALIDATION (+0.001 R and +0.037 R), and both have 95% confidence intervals heavily spanning negative territory (`[-0.122, 0.148]` and `[-0.155, 0.291]`).
  2. 0 of 12 cells achieve a 95% CI lower bound > 0.
  3. 0 of 12 cells pass the Benjamini-Hochberg 10% FDR threshold (`BH 10%` = "no" for all 12 cells).
  4. The underlying premise of reaching the opposite edge fails unconditionally across DEV and VAL (~33% to 48%, pooled ~40%), directly refuting the 70-80% setup claim regardless of fee drag.
