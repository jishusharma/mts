# Blind Review: edge4-rsi-confirm-exits

**Verdict: SOUND** (The empirical verdict FAIL follows directly from the tables: 0 of 48 pre-registered exits show statistical significance after clustering and multiplicity adjustments, and primary set S1 has zero positive net returns in validation).
What would change it: Pre-registration of an asymmetric/adaptive stop-loss mechanism with microsecond tick-level order book execution data showing that stop-before-target execution bias and fee-drag per small stop distance can be overcome out-of-sample with confidence intervals strictly bounding away from zero under day/coin clustered errors.

---

## 1. Table Analysis & Internal Arithmetic Consistency

### Claim & Location in Text
- Claim: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:3`
  "Verdict: FAIL. 0 of 48 pre-registered exit rules pass (16 per set; headline set S1 = 1h RSI<=20, 20 coins, 0 of 16, no exit has a positive fee-net VALIDATION mean)."
- Consistency verdict: **YES** (internally consistent with documented assumptions).

### Arithmetic Recomputations (SOURCED vs OURS)
1. **Sample Splits (DEV + VALIDATION = All)**:
   - S1: `482 DEV + 500 VAL = 982 total` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:7`). Recomputed sum: 982 [OURS]. Matches exactly.
   - S2: `137 DEV + 116 VAL = 253 total` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:7`). Recomputed sum: 253 [OURS]. Matches exactly.
   - S3: `124 DEV + 144 VAL = 268 total` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:7`). Recomputed sum: 268 [OURS]. Matches exactly.

2. **Regime Mix Sums**:
   - DEV: `bull 51 % / bear 40 % / range 10 %` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:5`). Sum = 101% [OURS] (standard rounding of integers summing to 100%).
   - VALIDATION: `bull 56 % / bear 30 % / range 15 %` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:5`). Sum = 101% [OURS] (standard rounding of integers summing to 100%).

3. **Part 1 Path Probabilities**:
   - S1: Reach +0.5R before stop is 58% (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:13`); stopped within 72h is 73%; reach +0.5R then stopped (before +1R) is 14% (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:13`). Text notes: `1 in 7 S1 trades first gets +0.5R and then is stopped out` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:28`). 1/7 = 14.28% [OURS], matching the 14% rounded figure.

4. **Fee & Cost Deductions (`mean R gross - mean R net`)**:
   - The fee model specified is `12 bp of entry price per round trip, divided by the stop distance to get R` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:7`).
   - For S1 (14 of 16 exits): `gross - net = 0.129 R` [OURS] across time2, time4, time8, tgt0.5R, tgt0.75R, rsi30, rsi40, rsi50, ma20touch, ma20close, be_tgt2, trail, half_trail, base_1R (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:34-49`). The remaining two (confstop_1R, confstop_2R) have fee deductions of 0.138 R and 0.137 R [OURS] respectively, reflecting the modified stop structure changing trade stop distance or R normalisation.
   - For S2 (14 of 16 exits): `gross - net = 0.118 R` [OURS], with confstop_1R and confstop_2R having 0.103 R [OURS] (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:55-70`).
   - For S3 (14 of 16 exits): `gross - net = 0.057 R` [OURS], with confstop_1R and confstop_2R having 0.044 R and 0.045 R [OURS] (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:76-91`). Notice S3 is on 4h bars, where stop distances in price % are roughly ~2.3x wider than 1h bars, causing cost in R (`0.0012 / stop_pct`) to drop by ~2.3x (0.129 R / 0.057 R = 2.26 [OURS]), which is completely consistent mathematically.

5. **Validation Confidence Intervals vs Verdict**:
   - S1: All 16 exits have `mean R net < 0` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:34-49`). Best exit net return is rsi50 at -0.083 R (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:41`), perfectly matching the summary sentence `The best S1 exit loses about 0.08R per trade net` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:3`).
   - S2: 12 of 16 exits have negative net return. The 4 exits with positive net return (`time8`, `rsi50`, `ma20touch`, `confstop_2R`) have trade 95% CIs that span zero (e.g., `time8` CI `[-0.44, +0.54]`; `confstop_2R` CI `[-0.23, +0.47]`, `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:57,69`) and day-clustered CIs that span zero (`[-0.61, +0.18]` and `[-0.26, +0.38]`).
   - S3: Gross returns are mostly positive (16 of 16), and 12 exits have net return > 0 (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:76-91`), but every single 95% trade CI spans zero (e.g., confstop_2R `[-0.12, +0.66]`, time8 `[-0.07, +0.40]`) and all day-cluster CIs span zero (e.g., `[-0.30, +0.44]` and `[-0.30, +0.20]`). None clears zero.

---

## 2. Concrete Methodological Risks Exposed in the Text

### A. Look-Ahead Risk
- **Exposure in text**:
  > "1h bars cannot order stop vs target inside a bar (stop first = pessimistic for tight targets)" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:96`)
  > "Closed bars, stop before target in a bar, trades need a full 168 h forward window." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:7`)
- **Analysis**: Intrabar price trajectory is not observed in bar data. Assuming "stop before target" avoids look-ahead / optimistic bias by resolving ambiguous intrabar high/low collisions conservatively, but introduces artificial pessimism for tight targets. Conditioning on `trades need a full 168 h forward window` introduces truncation / survival censoring at the end of the sample if trades near the sample edge are dropped.

### B. Fee and Slippage Handling Risk
- **Exposure in text**:
  > "Costs: 2 x fees.BINANCE_TAKER (5.00 bp/side, a little above the 4 bp in the brief) + fees.SLIPPAGE_RT_S13 (2 bp round trip) = 12 bp of entry price per round trip, divided by the stop distance to get R." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:7`)
  > "tiny stop distances inflate cost in R and are not filtered (the operator rule has none)" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:96`)
  > "No funding;" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:96`)
- **Analysis**: Taker fees of 5 bps/side + 2 bps round trip slippage are standard or conservative for VIP0/retail linear perp trading, but dividing fixed 12 bps price cost by very tight stop distances creates disproportionate R drag (`12 bp / 0.1% stop = 1.2 R` drag). Furthermore, funding costs are omitted, which could either penalize or reward long positions held up to 168 hours.

### C. Placebo Validity Risk
- **Exposure in text**:
  > "Placebo: 30 draws of a random same-coin same-week bar with the same stop distance and exit rule (RSI/MA exits: bars below SMA20 with RSI<=40)." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:7`)
  > "Placebo p has a floor of 1/31 = 0.032 (30 draws)." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:93`)
- **Analysis**: 30 bootstrap draws is extremely coarse; the minimum attainable empirical p-value is 1/(30+1) = 0.03225 (~0.032). It cannot discriminate extreme tails or allow fine-grained Bonferroni / Benjamini-Hochberg ranking when multiple hypotheses are tested. Also, constraining the placebo for RSI/MA exits to `bars below SMA20 with RSI<=40` conditions the placebo on partial signal criteria rather than an unconditional uninformative null.

### D. Clustering and Independence Risk
- **Exposure in text**:
  > "VALIDATION from 2024-01-01 (500 trades on 168 signal days)" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:30`)
  > "S2 1h RSI<=15, VALIDATION from 2024-01-01 (116 trades on 52 signal days)" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:51`)
  > "S3 4h RSI<=20, VALIDATION from 2024-01-01 (144 trades on 38 signal days)" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:72`)
  > "coins overlap in time (day view and week blocks reduce, not remove, the dependence);" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:96`)
- **Analysis**: Crypto sell-offs are market-wide systemic events: when BTC sells off, multiple altcoins hit RSI<=20 simultaneously. In S3, 144 validation trades occur on only 38 distinct signal days (~3.8 concurrent trades per day). Day clustering visibly widens the confidence intervals (e.g. S3 time2 trade CI `[-0.19, +0.28]` vs day-cluster CI `[-0.38, +0.09]`, `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:76`). Treating trades as independent i.i.d. observations severely underestimates standard errors.

### E. Multiple-Testing Risk
- **Exposure in text**:
  > "BH is applied inside each set over its 16 p-values (one-sided trade-level bootstrap); none is significant." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:93`)
  > "0 of 48 pre-registered exit rules pass (16 per set; headline set S1 = 1h RSI<=20, 20 coins, 0 of 16, no exit has a positive fee-net VALIDATION mean)." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-exits_RESULTS.md:3`)
- **Analysis**: Testing 16 exit variations across 3 signal parameter sets produces 48 hypotheses. Applying Benjamini-Hochberg within each set separately rather than across the pooled 48 tests inflates family-wise error rate across the entire study; however, because zero tests passed even the intra-set BH correction, multiplicity did not result in false discovery.

---

## 3. Conclusion

The conclusion in the document (`Verdict: FAIL`) is fully justified by the empirical data presented. The primary headline configuration (S1: 1h RSI<=20, 500 validation trades) yields negative fee-net expectancy across all 16 tested exit strategies (ranging from -0.083 R to -0.235 R). Although 4h bars (S3) show gross positive expectancy, the effective sample size is small (38 signal days), and day-cluster confidence intervals encompass zero for every exit. The study's verdict is sound.
