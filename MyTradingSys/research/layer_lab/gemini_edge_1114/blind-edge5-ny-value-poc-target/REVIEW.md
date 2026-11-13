# Blind Review: edge5-ny-value-poc-target-1113

## Verdict: SOUND (internally consistent, arithmetic checks pass, conclusions strictly follow from data)

The author's verdict of **FAIL (0 of 8 pre-registered cells pass)** is **SOUND**:
1. Every pre-registered cell on the 10 new coins displays negative fee-net mean R (ranging from -0.006 R to -0.501 R), with gross mean R hovering near zero (+0.123 R down to -0.090 R) and fully consumed by the 12 bp round-trip taker/slippage costs.
2. The headline "69% reach POC" diagnostic claim is shown to be an artifact of tautological counting (35.1% of setups already have POC at or behind entry; 24.2% have POC < 36 bp ahead). Once non-tradable setups are excluded, tradable setups reach the POC only 40.7% to 46.5% of the time, which is insufficient given the poor reward-to-risk ratios (median RR 0.47 to 0.52 for extreme stops).
3. What would change this verdict:
   - A different entry mechanism or timing filter that captures setups with substantially higher reward-to-risk (median RR > 1.5) without incurring the extreme stop-out rates (53% to 60%) seen with edge stops.
   - Significant reduction in transaction friction (e.g., pure maker limit execution or zero-fee VIP tier) capable of salvaging the small positive gross R observed in short setups (+0.015 to +0.123 R).
   - Multi-asset or cross-market evidence showing positive net expectation out-of-sample under rigorous day-clustered Bonferroni significance ($p < 0.00625$).

---

## 1. Table: Claims, Text Locations, and Internal Consistency Checks

| Claim / Subject | File Location | Stated Value | Recomputed / Verified Value | Consistent? | Notes / Calculations |
|---|---|---|---|---|---|
| Study Verdict | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:3` | `Verdict: FAIL, 0 of 8 cells pass.` | 0 of 8 cells pass all 6 pre-registered criteria. Net mean R is negative in all 8 cells. | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:3`. All 8 cells in lines 55-62 fail multiple criteria. |
| Diagnostic 3-Group Setup Sum (New coins) | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:14-16` | Group counts: 977 (35.1%), 673 (24.2%), 1136 (40.8%); total = 2786 | $977 + 673 + 1136 = 2786$. Percentages: $977/2786 = 35.068\% \approx 35.1\%$; $673/2786 = 24.156\% \approx 24.2\%$; $1136/2786 = 40.775\% \approx 40.8\%$. | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:14-16`. Sum and percentages match exactly. |
| Diagnostic Reach-POC Weighted Average | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:10-16` | Stated overall reach-POC: 69.3% (line 10) with group reaches 94.8%, 77.6%, 42.6% | Weighted average: $(977 \times 94.8 + 673 \times 77.6 + 1136 \times 42.6) / 2786 = 1932.38 / 2786 = 69.36\% \approx 69.4\%$. | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:10-16`. Recomputed weighted average matches reported 69.3% within 0.1% rounding. |
| Coverage New Coins Totals | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:24-34` | Total setups = 2786, total skipped = 1650 (59.2%) | Sum of setups across 10 coins: $264+291+307+268+274+277+301+259+265+280 = 2786$. Sum of skipped: $162+178+180+151+151+147+172+147+192+170 = 1650$. $1650 / 2786 = 59.22\% \approx 59.2\%$. Tradable setups: $2786 - 1650 = 1136$. | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:24-34`. Sums and percentages match identically. |
| Tradable Trades Sum across Sides | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:42-45` | Long $n = 467$, Short $n = 669$ (stop extreme / all days) | $467 + 669 = 1136$. Exactly matches tradable setups ($2786 - 1650 = 1136$). | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:42,44`. Partition of tradable setups into long and short is exact. |
| Per Coin Tradable Setups Sum | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:109-118` | Per-coin counts: BNB 102, XRP 113, DOGE 127, ADA 117, AVAX 123, LINK 130, LTC 129, DOT 112, TRX 73, BCH 110 | Sum $= 102+113+127+117+123+130+129+112+73+110 = 1136$. | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:109-118`. Recomputed sum matches exactly 1136. |
| Coverage Seen Data Totals | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:70-73` | Total setups = 910, total skipped = 545 (59.9%) | Sum of setups: $328 + 293 + 289 = 910$. Sum of skipped: $221 + 165 + 159 = 545$. $545 / 910 = 59.89\% \approx 59.9\%$. Tradable setups: $910 - 545 = 365$. | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:70-73`. Sums and percentages match identically. |
| Seen Data Tradable Trades Sum across Sides | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:81,83` | Long $n = 142$, Short $n = 223$ (stop extreme / all days) | $142 + 223 = 365$. Exactly matches seen tradable setups ($910 - 545 = 365$). | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:81,83`. Partition matches exact difference. |
| Annual Slices Sum to Cell n (Long all / stop extreme) | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:42` | Yearly counts: 2020: 52, 2021: 59, 2022: 81, 2023: 71, 2024: 77, 2025: 60, 2026: 67 | Sum: $52 + 59 + 81 + 71 + 77 + 60 + 67 = 467$. Exactly matches stated cell $n = 467$. 2024+ subtotal: $77 + 60 + 67 = 204$, matches stated 2024+ $n = 204$ (line 55). | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:42,55`. Year counts match cell total and 2024+ slice count. |
| Annual Slices Sum to Cell n (Short all / stop extreme) | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:44` | Yearly counts: 2020: 68, 2021: 119, 2022: 105, 2023: 108, 2024: 100, 2025: 107, 2026: 62 | Sum: $68 + 119 + 105 + 108 + 100 + 107 + 62 = 669$. Exactly matches stated cell $n = 669$. 2024+ subtotal: $100 + 107 + 62 = 269$, matches stated 2024+ $n = 269$ (line 57). | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:44,57`. Year counts match cell total and 2024+ slice count. |
| Regime Subtotals Sum | `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:120` | DEV $n = 663$, 2024+ $n = 473$ | $663 + 473 = 1136$. Exactly matches total tradable setups $n = 1136$. | YES | [OURS] Sourced from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:120`. Partition into DEV and 2024+ matches total sample. |

---

## 2. Recomputed Arithmetic and Descriptive Statistics

### A. Reach-POC vs Tradability
The text investigates the parent study's claim that price returns to the prior session POC 69% of the time:
- Stated in `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:10`: "Parent definition of reach-POC (any 1m bar after entry touches the POC, including a POC already at or behind entry) gives 69.3% on the 10 new coins (n = 2786 setups; seen coins 68.5%), so the number replicates."
- Recomputation:
  - 977 setups (35.1%) have $POC \le entry$, touched immediately on the next bar (94.8% touch rate). These cannot represent genuine trades.
  - 673 setups (24.2%) have $0 < \text{dist} < 36\text{ bp}$, which is below 3x round-trip cost (12 bp).
  - Only 1136 setups (40.8%) have $POC \ge 36\text{ bp}$ ahead. For these tradable setups, reach-POC drops to **42.6%**.
  - Total skipped setups: $977 + 673 = 1650$ out of 2786, which is **59.2%** of all potential setups.

### B. Gross vs Net Expectancy and Friction Breakdown
- Across the 8 test cells (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:42-49`):
  - Stop extreme cells: Gross mean R ranges from **-0.070 R to +0.077 R**. After deducting the 12 bp round trip, net mean R ranges from **-0.154 R to -0.006 R**. The cost drag per trade is approximately **0.075 R to 0.084 R**.
  - Stop edge cells: Gross mean R ranges from **-0.090 R to +0.123 R**. However, because the stop distance to the value edge is much tighter (median RR $\approx 2.00$ to $2.17$), 12 bp represents a much larger fraction of the stop distance. Consequently, net mean R collapses to **-0.225 R to -0.501 R**, reflecting a devastating cost drag of **0.348 R to 0.411 R** per trade.

---

## 3. Concrete Methodological, Execution, and Statistical Risks Exposed by the Text

The study text explicitly exposes the following concrete risks, directly quoted from the document:

1. **Look-Ahead and Execution Timing:**
   - Text quote in `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:6`: "Time exit at session end, stop-first, closed bars."
   - Text quote in `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:127`: "fills at close with fixed 1 bp slippage; stop gaps inside a 1m bar not modelled."
   - Analysis: Closed-bar stop evaluation assumes intrabar stops trigger at the fixed bar close or trigger boundary without intrabar gap through the stop level. In live trading, during fast market moves or news events, stop fills can suffer severe slippage beyond the 1m bar close.

2. **Fee and Slippage Sensitivity:**
   - Text quote in `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:6`: "Costs 5 bp taker + 1 bp slip per side (12 bp round trip)."
   - Text quote in `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:122`: "gross mean R is about zero in every cell (best +0.12 R, stop edge, balanced short, with a 53% stop rate); the 12 bp round trip then takes 0.07-0.4 R depending on the stop width. Stop B (value edge + 10 bp) is tight (median RR about 2) and is hit 53-60% of the time, so it loses more after costs."
   - Analysis: The strategy has virtually no gross edge (best cell +0.123 R gross, four cells negative gross). A modest 12 bp friction completely eliminates profitability across all cells, proving that the setup is unviable under taker execution.

3. **Placebo Validity and Benchmark Comparison:**
   - Text quote in `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:122`: "The placebo (random entry inside value with the same stop/target logic) loses 0.05-0.5 R too, so the entry timing beats random in the stop-extreme cells (placebo p 0.0005-0.0025) yet still does not make money."
   - Text quote in `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:128`: "The placebo draws one random candidate per trade (candidates = 1m closes from bar 89 to session end inside value, passing the 36 bp rule); trades with no candidate are left out of the placebo only."
   - Analysis: While the signal entry outperforms a random baseline entry inside the value area (achieving low placebo p-values in stop-extreme cells), beating a negative placebo baseline does not yield a positive absolute return. Furthermore, in all stop-edge cells, the placebo p-values range from 0.1415 to 0.4745, failing to outperform random entry.

4. **Clustering and Cross-Coin Dependence:**
   - Text quote in `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:123`: "The 8 cells overlap (balanced is a subset of all days; stops A and B share the same entries), so they are not independent and the Bonferroni divisor 8 is conservative; it does not matter here, no cell is positive."
   - Text quote in `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:7`: "Bonferroni day-cluster p < 0.00625"
   - Analysis: Cross-asset correlation during NY session opens means multiple coins open outside value simultaneously on the same market-wide shock days. The study appropriately addresses this by requiring day-clustered confidence intervals and day-cluster Bonferroni corrections ($0.05 / 8 = 0.00625$). Because no cell achieved positive net mean R, multiple-testing inflation did not cause false discovery.

5. **Ex-Post Diagnostic and Subgroup Splitting:**
   - Text quote in `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:130`: "The '69%' diagnostic and the three-group split were added after seeing the parent numbers: descriptive only."
   - Text quote in `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-ny-value-poc-target_RESULTS.md:129`: "Balanced rule, 36 bp POC gate, stop buffers, bin size are OURS (see PRE_REG parameter table)."
   - Analysis: The author candidly flags that the three-group decomposition was an ex-post diagnostic used to understand why parent numbers failed to translate to tradeable returns, rather than a pre-registered predictive cell. The 36 bp filter eliminated 59.2% of setups before execution testing.

---

## 4. Conclusion
The study's execution and reporting are rigorous, transparent, and completely consistent internally. The author's conclusion—that targeting the prior NY session POC fails across all test cells once realistic entry distance, fees, and stop logic are applied—is incontrovertibly supported by the reported data and arithmetic.
