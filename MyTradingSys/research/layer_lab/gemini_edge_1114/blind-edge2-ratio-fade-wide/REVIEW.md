# Blind Review: Account-ratio fade, 1d signal, 20 NEW Bybit perps (wave 2) (edge2-ratio-fade-wide)

**Verdict: SOUND**
The negative verdict ("Verdict: FAIL. 0 of 2 cells pass.") directly follows from the reported validation data, pre-registration protocol, and statistical results. What would change it: demonstrating that the negative/flat fee-net mean returns across both validation cells (-16.8 bp and +0.1 bp) arose from an arithmetic or execution bug in data ingestion or fee accounting, or producing statistically significant fee-net positive out-of-sample results on a pre-registered re-test.

---

## 1. Executive Summary & Review Scope
- **Target File**: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:1-25`
- **Study Goal**: Evaluate an account-ratio fade 1d signal on 20 new Bybit USDT perpetuals (wave 2) across 7d and 3d holding horizons.
- **Author Verdict**: "Verdict: FAIL. 0 of 2 cells pass. VALIDATION both-sides fee-net mean is -16.8 bp (7d) and +0.1 bp (3d); neither CI excludes zero." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:3`)
- **Reviewer Finding**: The author's rejection of the edge is sound, conservative, and statistically verified. The wave 1 DEV/RECENT positive results failed to replicate on the new 20-coin universe in RECENT (-13.4 bp at 7d) and VALIDATION (-16.8 bp at 7d).

---

## 2. Table & Claims Internal Consistency

### Consistency Verdict: **YES**

### Detailed Recomputation & Consistency Checks

1. **Cell Count Total**:
   - Claim: "0 of 2 cells pass." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:3`).
   - Signal table evaluates two hold horizons: 7d and 3d for VALIDATION (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:11,14`).
   - Arithmetic check [OURS]: Exactly 2 VALIDATION evaluation cells.
   - Status: SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:3,11,14`) / OURS. Internally consistent.

2. **Validation Sample Counts and Weighted Means**:
   - Claim: "Sides (7d hold, VALIDATION / RECENT; n 237/283 long, 182/249 short)" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:18`).
   - Claim: 7d VALIDATION total n is 419 (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:11`).
   - Claim: 7d RECENT total n is 532 (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:12`).
   - Arithmetic check [OURS]:
     - 7d VALIDATION: $237 \text{ (long)} + 182 \text{ (short)} = 419$ total trades.
     - 7d RECENT: $283 \text{ (long)} + 249 \text{ (short)} = 532$ total trades.
   - Weighted mean recomputation [OURS]:
     - Claim: 7d VALIDATION long-only mean is +212.5 bp; short-only mean is -315.5 bp (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:19`).
       $$\text{Mean}_{\text{VAL}} = \frac{237 \times (+212.5) + 182 \times (-315.5)}{419} = \frac{50362.5 - 57421.0}{419} = \frac{-7058.5}{419} \approx -16.846 \text{ bp}$$
       Matches reported table entry: `-16.8` bp (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:11`).
     - Claim: 7d RECENT long-only mean is +67.0 bp; short-only mean is -104.7 bp (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:19`).
       $$\text{Mean}_{\text{RECENT}} = \frac{283 \times (+67.0) + 249 \times (-104.7)}{532} = \frac{18961.0 - 26070.3}{532} = \frac{-7109.3}{532} \approx -13.363 \text{ bp}$$
       Matches reported table entry: `-13.4` bp (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:12`).
   - Status: SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:11,12,18,19`) / OURS. Internally consistent.

3. **Placebo Comparison & Pass Conditions**:
   - 7d VALIDATION: mean -16.8 bp vs placebo mean -139 / p95 -1. Beats p95: `no` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:11`). Status: SOURCED / OURS (-16.8 < -1).
   - 3d VALIDATION: mean +0.1 bp vs placebo mean -72 / p95 -6. Beats p95: `yes (but CI includes 0, p 0.5)` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:14`). Status: SOURCED / OURS (+0.1 > -6, but CI [-146..+152] spans zero, $p \approx 0.5$).
   - Multiple testing: "BH 10% over the 2 VALIDATION p-values selects nothing (p about 0.5)." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:16`). With $m=2$ and $p \approx 0.5 > 0.10$, Benjamini-Hochberg at 10% FDR selects zero discoveries.
   - Status: SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:14,16`) / OURS. Internally consistent.

---

## 3. Concrete Methodological Risks Exposed in the Text

### A. Look-Ahead Risk
- **Exposed Risk**:
  > Quote: "PRE_REG sha 44b703ef6 (committed before outcomes); rule/thresholds unchanged from wave 1." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:3`)
  > Quote: "placebo = same coin, same month, same side, random 00:00Z day, 200 draws." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:5`)
- **Assessment**: Rule and threshold pre-registration before outcomes prevents ex-post tuning. Daily signals anchored at 00:00Z mitigate intra-day look-ahead leakage.

### B. Fee & Slippage Handling
- **Exposed Risk**:
  > Quote: "Fees = BINANCE_TAKER x2 + funding while held" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:5`)
  > Quote: "The short leg is the loser in VALIDATION and RECENT; the long leg (fade a crowded-short ratio) is positive in every split but its placebo (long drift) is nearly as large" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:19`)
- **Assessment**: The methodology charges two taker fees plus funding accrual across the multi-day holding period (3d or 7d). Fading crowded ratios on short positions carries a severe loss (-315.5 bp in 7d VALIDATION), indicating that funding payments and adverse drift penalize the short fade.

### C. Placebo Validity
- **Exposed Risk**:
  > Quote: "placebo = same coin, same month, same side, random 00:00Z day, 200 draws." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:5`)
  > Quote: "the long leg (fade a crowded-short ratio) is positive in every split but its placebo (long drift) is nearly as large: 7d long VALIDATION +212 vs placebo +79 (p95 +253), RECENT +67 vs +124." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:19`)
  > Quote: "3d long: VALIDATION +66, RECENT +90 (CI -20..+219), pooled VAL+RECENT +79 (n 835, CI -23..+182) vs placebo +37 (p95 +110)." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:19`)
- **Assessment**: Controlling for coin, month, and side reveals that the seemingly positive long leg (+212 bp in 7d VALIDATION and +67 bp in RECENT) is largely explained by general market upward drift rather than predictive signal timing (placebo p95 is +253 bp in VALIDATION, and placebo mean is +124 bp in RECENT, exceeding the signal return).

### D. Clustering & Independence
- **Exposed Risk**:
  > Quote: "week-cluster bootstrap 4000" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:5`)
  > Quote: "Coins (20, rank filter explained in PRE_REG, survivor bias stated): ZEC NEAR 1000PEPE SUI UNI XMR AAVE WLD INJ XLM ONDO ARB TAO BCH TIA HBAR ICP QNT STRK APT." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:5`)
  > Quote: "Per-year, both sides, 7d hold (bp): 2021 +225 (n 34), 2022 +86, 2023 +60, 2024 +64, 2025 +102, 2026 -98 (n 333)" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:21`)
- **Assessment**: Multi-coin crypto returns exhibit strong cross-sectional correlation, and overlapping multi-day holds (3d and 7d) introduce serial autocorrelation. The weekly-cluster bootstrap accounts for cluster structure. Survivor bias is explicitly acknowledged for the 20 newly selected coins. Furthermore, sample sizes vary heavily over calendar time (n=34 in 2021 vs n=333 in 2026).

### E. Multiple-Testing & Pre-Registration
- **Exposed Risk**:
  > Quote: "PRE_REG sha 44b703ef6 (committed before outcomes); rule/thresholds unchanged from wave 1." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:3`)
  > Quote: "BH 10% over the 2 VALIDATION p-values selects nothing (p about 0.5)." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:16`)
  > Quote: "Pooled over both waves the ratio fade is near zero both sides with the short leg negative and long leg positive; the earlier 10-coin DEV result of +196 bp is not a stable edge." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-ratio-fade-wide_RESULTS.md:25`)
- **Assessment**: Pre-registration at commit `44b703ef6` constrained researchers from cherry-picking parameters after observing that wave 1 results (+196 bp in 10-coin DEV) failed to hold up out of sample on the wave 2 universe.

---

## 4. Conclusion & Recommendation
The study's failure verdict is rigorous, objective, and statistically sound. The author correctly identifies that:
1. Both-sides ratio-fade fails in VALIDATION (-16.8 bp and +0.1 bp) with confidence intervals spanning zero.
2. The long-only positive returns fail to exceed drift-matched placebos.
3. The wave-1 positive signals do not replicate out of sample on new coins.
The edge should remain rejected as non-viable.
