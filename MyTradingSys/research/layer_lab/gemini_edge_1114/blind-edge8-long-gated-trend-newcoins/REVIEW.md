# Blind Review: edge8-long-gated-trend-newcoins-1114

**Verdict: SOUND** (The study's verdict `FAIL on both rules` is fully sound and directly follows from the reported empirical numbers and pre-registered gates; see details below on what would change it).

What would change the verdict:
To overturn the verdict of `FAIL` to a `PASS` or viable candidate, the study would need:
1. Long-sample out-of-sample data covering full market cycles where daily return 95 % CI does not straddle zero (lower bound > 0).
2. Demonstration of alpha beyond a naive buy-and-hold basket of the coin universe (g3: Sharpe > basket Sharpe of 0.74).
3. Robustness against tail removal (positive returns when excluding best 10 days and best 5 coins; currently -18.7 % and -6.4 % without best 10 days).
4. Statistically significant separation from un-gated / random entry placebo benchmarks (placebo p < 0.05; currently 0.377 and 0.094).

---

## 1. Table Consistency and Recomputed Arithmetic

Input document under review: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge8-long-gated-trend-newcoins_RESULTS.md`

### 1.1 Regime percentages and date span
- Text cite: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge8-long-gated-trend-newcoins_RESULTS.md:5` confirms "VALIDATION days 2024-01-01..2026-11-12 (1047), BTC close vs 200d SMA (bull > +5 %, bear < -5 %, else range): bull 56.1 % / bear 29.4 % / range 14.5 %".
- Arithmetic recomputation [OURS]:
  - Date interval: 2024-01-01 to 2026-11-12 inclusive = 366 (2024 leap year) + 365 (2025) + 316 (2026 up to Nov 12) = 1,047 calendar days. Exact match.
  - Regime share sum: 56.1 % + 29.4 % + 14.5 % = 100.0 %. Exact match.
- Status: **YES** (internally consistent).

### 1.2 Annualised return from yearly sums
- Text cites: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge8-long-gated-trend-newcoins_RESULTS.md:14-15` reports Table 1 VAL ann. as `+16.3 %` for Rule 9 and `+25.1 %` for Rule 10. `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge8-long-gated-trend-newcoins_RESULTS.md:34-37` reports yearly returns: Rule 9 with `-8.1 %`, `+1.0 %`, `+53.9 %`, and Rule 10 with `+29.1 %`, `-29.7 %`, `+72.7 %`.
- Arithmetic recomputation [OURS]:
  - Rule 9 sum over VALIDATION (2024-01-01 to 2026-11-12): `-8.1 % + 1.0 % + 53.9 % = +46.8 %`.
    - Annualised across 1,047 days (1047 / 365 = 2.8685 years): `46.8 % / (1047 / 365) = 16.315 %` (~`+16.3 %`). Exact match.
  - Rule 10 sum over VALIDATION: `+29.1 % + (-29.7 %) + 72.7 % = +72.1 %`.
    - Annualised across 1,047 days: `72.1 % / (1047 / 365) = 25.135 %` (~`+25.1 %`). Exact match.
- Status: **YES** (internally consistent).

### 1.3 Confidence intervals and bootstrap p-values
- Text cites: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge8-long-gated-trend-newcoins_RESULTS.md:14` reports for Rule 9 VAL Sharpe `0.32`, CI `[-0.098 %, +0.195 %]`, and one-sided boot p `0.275`. `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge8-long-gated-trend-newcoins_RESULTS.md:15` reports for Rule 10 VAL Sharpe `0.70`, CI `[-0.041 %, +0.181 %]`, and one-sided boot p `0.113`.
- Arithmetic recomputation [OURS]:
  - Rule 9 daily mean = `46.8 % / 1047 = 0.04470 %`.
    - Midpoint of reported CI = `(-0.098 % + 0.195 %) / 2 = 0.0485 %`.
    - Half-width = `(0.195 % - (-0.098 %)) / 2 = 0.1465 %`.
    - Implied standard error SE = `0.1465 % / 1.96 = 0.0747 %`.
    - t-statistic = `0.04470 / 0.07474 = 0.598`. One-sided normal p-value = `1 - Phi(0.598) = 0.275` (matches reported `one-sided boot p` of `0.275`).
  - Rule 10 daily mean = `72.1 % / 1047 = 0.06886 %`.
    - Midpoint of reported CI = `(-0.041 % + 0.181 %) / 2 = 0.0700 %`.
    - Half-width = `(0.181 % - (-0.041 %)) / 2 = 0.1110 %`.
    - Implied standard error SE = `0.1110 % / 1.96 = 0.0566 %`.
    - t-statistic = `0.06886 / 0.05663 = 1.216`. One-sided normal p-value = `1 - Phi(1.216) = 0.112` (matches reported `one-sided boot p` of `0.113`).
- Status: **YES** (internally consistent).

### 1.4 Gate evaluation
- Gates stated in text (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge8-long-gated-trend-newcoins_RESULTS.md:19`):
  "Gates (all must be Y): g1 CI lower bound > 0, g2 Sharpe >= 1, g3 beats basket, g4 placebo p < 0.05, g5 Bonferroni (one-sided p and placebo p <= 0.025), g6 positive without best 10 days and without best 5 coins."
- Evaluation against table:
  - g1 (CI lower bound > 0): Rule 9 lower bound is `-0.098 %` (< 0); Rule 10 is `-0.041 %` (< 0). -> `n` on both.
  - g2 (Sharpe >= 1): Rule 9 is `0.32` (< 1); Rule 10 is `0.70` (< 1). -> `n` on both.
  - g3 (beats basket): Basket Sharpe is `0.74`, ann. `+60.2 %`. Rule 9 (0.32 / +16.3 %) and Rule 10 (0.70 / +25.1 %) both lose to basket. -> `n` on both.
  - g4 (placebo p < 0.05): Rule 9 is `0.377`; Rule 10 is `0.094`. -> `n` on both.
  - g5 (Bonferroni <= 0.025): Neither one-sided p (0.275, 0.113) nor placebo p (0.377, 0.094) meets <= 0.025. -> `n` on both.
  - g6 (positive w/o best 10 days and w/o best 5 coins): Rule 9 is `-18.7 %` w/o best 10 days and `-1.1 %` w/o best 5 coins; Rule 10 is `-6.4 %` w/o best 10 days. -> `n` on both.
- Status: **YES** (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge8-long-gated-trend-newcoins_RESULTS.md:21-24` marks `n` across all 6 gates for both rules; verdict of FAIL follows directly from criteria).

---

## 2. Concrete Risks Exposed by the Text

The text directly discloses several structural and statistical risks. Below are the concrete risks with exact citations:

### 2.1 Look-Ahead and Survivorship / Selection Risk
- Citation: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge8-long-gated-trend-newcoins_RESULTS.md:17` notes "the new coins mostly went up on their way to being the most traded today (selection bias, see below)".
- Citation: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge8-long-gated-trend-newcoins_RESULTS.md:58` highlights "The 60 coins are today's most-traded coins. Coins rank high today largely because they moved or got popular recently, so the sample is tilted toward winners and away from coins that faded or delisted; long-side numbers are upper bounds, and the basket (+60 % a year) shows how tilted."
- Risk assessment: Selecting coins based on current trading volume introduces massive survivorship and retrospective selection bias. Because coins must have experienced large volume and price runs to become today's most-traded coins, historical returns on these coins are inflated upper bounds. Despite this favourable selection bias, the trend rules still failed all confirmation gates.

### 2.2 Fee, Funding, and Slippage Handling Risk
- Citation: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge8-long-gated-trend-newcoins_RESULTS.md:7` confirms "59 of 60 coins have funding records; funding coverage 100 % of held coin-days".
- Citation: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge8-long-gated-trend-newcoins_RESULTS.md:47` states "Capping at 1.0x lowers VAL Sharpe from 0.85 to 0.33 / 0.66 on the same coins probably because the cap bites in the up-moves when many coins signal together and every weight is trimmed pro rata, and each trim costs turnover."
- Citation: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge8-long-gated-trend-newcoins_RESULTS.md:60` observes "Perp prices here, spot prices for the parent row and the BTC gate. No intraday stops."
- Citation: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge8-long-gated-trend-newcoins_RESULTS.md:61` notes "The gross cap trims pro rata and the trim is charged as turnover (registered in advance). Not a claim about live profitability."
- Risk assessment: Frequent pro-rata gross cap adjustments generate turnover drag. Furthermore, daily kline execution without intraday stops exposes the strategy to intra-bar liquidation or gap slippage that daily settlement does not capture.

### 2.3 Placebo Validity Risk
- Citation: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge8-long-gated-trend-newcoins_RESULTS.md:51` points out "The signal does not beat a random start date on the same coin for rule 9 (placebo p 0.38) and only weakly for rule 10 (0.094)."
- Citation: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge8-long-gated-trend-newcoins_RESULTS.md:60` observes "The placebo moves each run to a random start without the BTC gate (the parent's method), so it is a loose benchmark."
- Risk assessment: The placebo benchmark shifts trade entry timing without the BTC gate. A placebo p of 0.377 for Rule 9 indicates that randomly shifting entry dates performs as well or better than the actual signal ~38 % of the time. The test itself notes this placebo is a loose benchmark, making failure against it even more damning.

### 2.4 Clustering, Sample Truncation, and Multiple-Testing / Low Power Risk
- Citation: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge8-long-gated-trend-newcoins_RESULTS.md:3` identifies "the drawdown is large for a return of 16-25 % a year, and the profit rests on a few days."
- Citation: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge8-long-gated-trend-newcoins_RESULTS.md:53` states "It rests on a few days: the best 10 days are 125-213 % of VAL profit; without them the mean is negative for both rules."
- Citation: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge8-long-gated-trend-newcoins_RESULTS.md:54` notes "Concentration in 2025: rule 10 lost -29.7 % in 2025 on new coins, rule 9 made almost nothing; 2023 numbers use very few coins."
- Citation: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge8-long-gated-trend-newcoins_RESULTS.md:59` explains "Most contracts launched in 2025-2026, so VALIDATION is mostly a 2025-2026 window with 5-9 coins in the book on average; the DEV window for these coins is essentially 2023 only. Statistical power is low; a real small edge would not be detected either, so this says \"not shown\", not \"proven absent\"."
- Risk assessment: Extreme clustering of returns into top 10 days (accounting for 125 % and 213 % of total profit respectively) reveals acute tail dependency. Removing 10 out of 1,047 days turns both rules negative. In addition, contract histories are short and staggered, meaning effective degrees of freedom are much lower than the 1,047 calendar days suggest.

---

## 3. Conclusion

The input study's verdict of `FAIL on both rules` is **SOUND**. It adhered strictly to pre-registered evaluation gates, reproduced parent figures accurately for comparison, correctly identified fatal tail dependence (failure without best 10 days), noted severe selection bias in the test universe, and reached an objective conclusion without attempting to rationalize negative confirmation.
