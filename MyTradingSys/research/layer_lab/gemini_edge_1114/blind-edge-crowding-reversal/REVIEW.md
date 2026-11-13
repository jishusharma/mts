# Blind Review: Crowding as a contrarian signal (edge-crowding-reversal)

**Verdict: SOUND**
The negative verdict ("Verdict: FAIL. 0 of 24 cells pass.") directly follows from the reported validation data, pre-registration protocol, and statistical results. What would change it: demonstrating that the negative mean returns across 21 of 24 cells arose from an implementation error in cost/funding attribution or data alignment, or producing positive, statistically significant, fee-net out-of-sample results on a pre-registered re-test.

---

## 1. Executive Summary & Review Scope
- **Target File**: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:1-32`
- **Study Goal**: Evaluate crowding (funding rate and account ratio extremes, open interest surges) as a contrarian fade signal across 10 Bybit USDT perpetuals on 4h and 1d timeframes.
- **Author Verdict**: "Verdict: FAIL. 0 of 24 cells pass." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:3`)
- **Reviewer Finding**: The author's rejection of the edge is sound, conservative, and statistically consistent. The evidence exposes severe negative fee-net performance across multiple hold horizons, with funding drag compounding against the position.

---

## 2. Table & Claims Internal Consistency

### Consistency Verdict: **YES**

### Detailed Recomputation & Consistency Checks

1. **Cell Count Total**:
   - Claim: "0 of 24 cells pass" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:3`).
   - Claim: "range over the 6 TF x hold cells" across 4 signals (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:7-13`).
   - Arithmetic check [OURS]: 4 signals (a, b, c, d) x 6 cells (e.g. 2 timeframes x 3 hold horizons) = 24 cells.
   - Status: SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:3,7`) / OURS (4 x 6 = 24). Internally consistent.

2. **Negative Return Distribution Across Cells**:
   - Claim: "VALIDATION (2024-07-01..2025-06-30) fee-net mean is negative in 21 of 24 cells" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:3`).
   - Signal breakdowns in table (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:8-13`):
     - Signal a (`FUND extreme, fade`): `mean range (bp)` is "-230 to -45" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:10`) -> all 6 cells strictly negative.
     - Signal b (`RATIO extreme, fade`): `mean range (bp)` is "-90 to -6" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:11`) -> all 6 cells strictly negative.
     - Signal c (`FUND + 3d push`): `mean range (bp)` is "-281 to -83" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:12`) -> all 6 cells strictly negative.
     - Subtotal for signals a, b, c [OURS]: 6 + 6 + 6 = 18 cells, all strictly negative.
     - Signal d (`OI surge, price flat, vs funding`): `mean range (bp)` is "-92 to +9" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:13`).
   - Recomputation [OURS]: If 21 of 24 cells are negative and signals a, b, c account for 18 negative cells, signal d has exactly 21 - 18 = 3 negative cells and 24 - 21 = 3 non-negative cells (reaching up to +9 bp, consistent with the reported best cell "OIFLAT 4h/7d, is +8.7 bp" at `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:3`).
   - Status: SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:3,10-13`) / OURS (18 + 3 = 21 negative cells). Internally consistent.

3. **Multiple Testing (Benjamini-Hochberg) Control**:
   - Claim: "Smallest VALIDATION p across all cells is 0.48, so BH at 10% selects nothing." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:3`).
   - Arithmetic check [OURS]: For any test $i \in \{1, \dots, m\}$ with $m=24$ tests, the Benjamini-Hochberg threshold at $\alpha = 0.10$ is $\frac{i}{m} \alpha \le 0.10$. Since $\min_i(p_i) = 0.48 > 0.10$, no p-value meets or falls below the discovery threshold. BH selects 0 discoveries.
   - Status: SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:3`) / OURS. Internally consistent.

4. **Best CI and Placebo Rejection**:
   - Claim: "the best, OIFLAT 4h/7d, is +8.7 bp on n=57 with CI [-315, +334] bp, one-sided p 0.48." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:3`).
   - Table entry for Signal d: `Best CI lower (bp)` is "-250" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:13`). Note that for signal d, the best CI lower bound is -250 bp (which is higher/better than -315 bp), while the best point estimate (+8.7 bp) has CI [-315, +334]. The CI spans zero by over 300 bp in either direction, showing absence of statistical significance.
   - Table entry for Signal d: `Cells beating placebo p95` is "0 of 6" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:13`).
   - Status: SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:3,13`). Internally consistent.

---

## 3. Concrete Methodological Risks Exposed in the Text

### A. Look-Ahead Risk
- **Exposed Risk**:
  > Quote: "test_crowd.py (6 tests: PIT percentile excludes the current value, fade side, fee and funding sign, funding window and hold, next-bar entry plus one-position rule, bootstrap CI)" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:29`)
  > Quote: "entry next bar open; one position per coin" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:5`)
- **Assessment**: The methodology explicitly uses point-in-time percentiles excluding current value and next-bar open execution to avoid look-ahead bias.

### B. Fee & Slippage Handling
- **Exposed Risk**:
  > Quote: "Fees: `fees.BINANCE_TAKER x 2` plus funding paid while held" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:5`)
  > Quote: "Hold-7 cells lose the most because funding is paid for the whole hold while the crowded side keeps trending." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:23`)
- **Assessment**: Fading extreme crowding means taking the side opposite to the market consensus, which incurs continuous funding payments. Over 7-day holding periods, paying funding while the underlying asset trends strongly against the fade creates substantial fee-drag. Slippage is not explicitly broken down apart from taker fees (`fees.BINANCE_TAKER x 2`).

### C. Placebo Validity
- **Exposed Risk**:
  > Quote: "placebo = same coin, same month, same side (200 draws)." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:5`)
  > Quote: "does not beat the RECENT placebo p95 (+175 bp; the placebo is itself positive in RECENT, so side drift explains part of it)" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:16`)
- **Assessment**: Matching on same coin, same month, and same side controls for unconditional market drift and coin-specific trend. In RECENT, the positive performance of the placebo (+175 bp) correctly unmasks what appeared to be signal return as general side drift.

### D. Clustering & Independence
- **Exposed Risk**:
  > Quote: "weekly-cluster bootstrap 4000" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:5`)
  > Quote: "n: signal d has 23-75 trades per VALIDATION cell (UNDERPOWERED for the 1d cells, n < 30 in 2 of them)." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:19`)
- **Assessment**: Multi-coin crypto returns are cross-sectionally correlated and autocorrelated across holding periods up to 7 days. The use of a weekly-cluster bootstrap addresses inter-temporal and cross-asset clustering. However, low sample size (n < 30 in two 1d cells for signal d) leaves individual cells underpowered.

### E. Multiple-Testing & Pre-Registration
- **Exposed Risk**:
  > Quote: "Rule, parameters and pass line are in `PRE_REG.md` (committed first, sha 4a540b4da); nothing was changed after the run." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:3`)
  > Quote: "Smallest VALIDATION p across all cells is 0.48, so BH at 10% selects nothing." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-crowding-reversal_RESULTS.md:3`)
- **Assessment**: Testing 24 combinations creates multiple comparison risk, which the authors explicitly controlled via Benjamini-Hochberg false discovery rate control and immutable pre-registration (`sha 4a540b4da`).

---

## 4. Conclusion & Recommendation
The study's failure verdict is rigorous, objective, and well-grounded in out-of-sample data. The author avoided common pitfalls (such as chasing DEV/RECENT overfit or ignoring funding drain). The study should remain rejected as non-viable on trunk.
