# Blind Review: edge5-rsi-4h-exits-newcoins-1113

Verdict: SOUND (The negative verdict FAIL/FAIL follows directly from the statistical gates, confidence intervals covering zero, bootstrap p-values > 0.025, and extreme day-clustering; what would change it: nothing in this dataset can turn it into an ACCEPT, but establishing positive edge would require out-of-sample data on an unselected universe showing lower confidence bounds strictly above zero with robust multi-coin clustering controls).

## 1. Table Verification and Arithmetic Recomputation

Input document: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:1-22`

### Table Claims & Verification:
- **Trade count `n = 452`**: SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:7`, `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:11-12`). Internally consistent: YES.
- **Per-year sample size sum**: SOURCED counts `2021 (7); 2022 (83); 2023 (84); 2024 (108); 2025 (123); 2026 (47)` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:11-12`). Recomputed sum: 7 + 83 + 84 + 108 + 123 + 47 = 452 (OURS). Exactly matches total `n = 452`. Internally consistent: YES.
- **2024-01-01-onward slice sample size**: SOURCED `n 278` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:14`). Recomputed sum: 108 (2024) + 123 (2025) + 47 (2026) = 278 (OURS). Exactly matches. Internally consistent: YES.
- **Weighted mean R from per-year table vs reported overall mean R**:
  - `time8`: Per-year means are `+0.05, +0.40, -0.37, +0.14, +0.04, +0.00` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:11`). Recomputed weighted average across 452 trades = +0.0498 R (OURS), consistent with reported rounded mean `+0.051` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:11`). Internally consistent: YES.
  - `confstop_2R`: Per-year means are `+0.67, +0.15, -0.12, +0.01, +0.30, -0.17` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:12`). Recomputed weighted average across 452 trades = +0.0820 R (OURS), consistent with reported rounded mean `+0.081` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:12`). Internally consistent: YES.
- **Without best 5 days arithmetic**:
  - `time8`: SOURCED text states: "the best 5 signal days carry more than 100 % of total R (time8 351 %)" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:18`) and table reports mean `-0.151 (n 386)` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:11`). Total R is 452 * 0.051 = 23.052 R (OURS). If best 5 days carried 351% (80.91 R), the remaining 386 trades (66 trades removed across 5 days, i.e. 13.2 trades/day) would have 23.052 - 80.913 = -57.861 R, yielding mean R = -57.861 / 386 = -0.1499 R (OURS), matching `-0.151` within rounding tolerance. Internally consistent: YES.
  - `confstop_2R`: SOURCED text states: "(confstop_2R 239 %)" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:18`) and table reports mean `-0.135 (n 374)` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:12`). Total R is 452 * 0.081 = 36.612 R (OURS). If best 5 days carried 239% (87.50 R), the remaining 374 trades (78 trades removed across 5 days, i.e. 15.6 trades/day) would have 36.612 - 87.503 = -50.891 R, yielding mean R = -50.891 / 374 = -0.1361 R (OURS), matching `-0.135` within rounding. Internally consistent: YES.
- **Regime percentages**:
  - 2021-01..2026-11: SOURCED `bull 51 % / bear 36 % / range 12 %` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:5`). Sum = 99% (OURS, 1% rounding difference).
  - 2024-01..now: SOURCED `bull 56 % / bear 30 % / range 15 %` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:5`). Sum = 101% (OURS, 1% rounding difference). Both reflect standard integer percentage rounding.

## 2. Concrete Risks Exposed in the Text

### A. Look-Ahead and Universe Selection Bias
The text explicitly exposes survivorship bias in its coin selection:
- Quoted sentence: `"Limits: current-volume universe (survivorship, dead coins absent); spot series not the parent's perp series; stop-first on 1h bars; no funding; per-year n tiny for 2021."` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:20`)
- Analysis: Selecting 40 coins based on current volume means only coins that survived and maintained high volume into 2026 are included. Coins that suffered total collapse (e.g. LUNA, FTT, or delisted alts during 2021-2023) are omitted from historical backtests. Furthermore, the parent study used perp data, whereas this study used spot data without funding rates.

### B. Fee and Slippage Handling
The text states:
- Quoted sentence: `"Cost 12 bp round trip (2 x 5 bp taker + 2 bp slippage) divided by stop distance."` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:7`)
- Analysis: For `time8`, gross mean R is `+0.131` and net mean R is `+0.051` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:11`), meaning fees consume 0.080 R (61% of gross R). For `confstop_2R`, gross mean R is `+0.129` and net mean R is `+0.081` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:12`), meaning fees consume 0.048 R (37% of gross R). Moreover, 2 bp slippage may be optimistic during high-volatility capitulation panics on altcoins.

### C. Placebo Validity
The text reports:
- Quoted sentence: `"placebo (the real entries beat random 4h closes of the same coin-week: the random baseline loses 0.19 / 0.39 R, so the confirm-after-capitulation entry adds something over random, but not enough to be positive with confidence)."` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:16`)
- Analysis: The placebo test (comparing against random 4h closes of the same coin-week) is valid and well-controlled for coin and weekly drift. The real entries achieve p = 0.005 against random baseline entries (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:11-12`). However, as the author correctly notes, outperforming a bleeding random entry (-0.19 R or -0.39 R) does not establish a statistically significant positive edge net of costs.

### D. Clustering and Independence Risk
The study is dominated by cross-sectional and temporal clustering:
- Quoted sentence: `"Concentration: the best 5 signal days carry more than 100 % of total R (time8 351 %, confstop_2R 239 %); with those 5 days removed the mean is -0.151 (time8) and -0.135 (confstop_2R)."` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:18`)
- Quoted sentence: `"Best days: 2022-05-10, 2024-07-05, 2025-04-07, 2025-02-03, 2026-02-06 (time8); 2025-04-07, 2025-10-11, 2024-07-05, 2024-08-05, 2022-11-10 (confstop_2R): market-wide capitulation days where many coins signal at once and bounce together."` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:18`)
- Quoted sentence: `"Day-level means (one value per day) are lower than the trade means (time8 day mean -0.09), i.e. multi-coin crash days carry the profit."` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:18`)
- Analysis: 452 trades occurred across only 145 signal days (average 3.12 trades per signal day, SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:7`). Removing just 5 market-wide capitulation days flips the performance from slightly positive (+0.05 / +0.08) to strongly negative (-0.151 / -0.135). The trades are highly correlated market-wide events rather than 452 independent trials.

### E. Multiple-Testing and Gate Failures
- Quoted sentence: `"Failed gates (both cells): trade CI lower bound < 0, both day-cluster lower bounds < 0, Bonferroni bootstrap p (0.34 / 0.28) > 0.025."` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:16`)
- Analysis: With 2 cells tested, Bonferroni correction sets alpha = 0.025. The observed one-sided bootstrap p-values are 0.34 (`time8`) and 0.28 (`confstop_2R`), which fail to reach significance by a wide margin. Both week-block and day-cluster confidence intervals cross zero and encompass substantial negative values.

## 3. Evaluation of Verdict
The study's verdict:
- Quoted sentence: `"Verdict: time8 FAIL, confstop_2R FAIL. Neither confirms the parent's near-miss."` (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-4h-exits-newcoins_RESULTS.md:3`)
- Assessment: **SOUND**. The conclusion that both variants fail is fully justified by the reported data and rigorous statistical gates. The apparent positive mean R is entirely an artifact of 5 market-wide capitulation days; across the remaining 140 signal days (386 / 374 trades), the strategy loses money net of transaction costs.
