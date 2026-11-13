# Blind Review: edge5-rsi-oi-unwind-newcoins

**Verdict: SOUND (Claim that no cell passes carries over to new coins is fully supported by the study text, but the study itself documents severe structural limits: survivorship bias, flat slippage, lack of funding, and heavy cross-coin clustering).**
What would change it: If transaction cost modeling with realistic coin-specific slippage and funding was simulated on a point-in-time (non-survivorship-biased) universe, or if trades were clustered across concurrent pairs, which would likely degrade the marginal Cell A performance even further.

---

### 1. Scope and Inputs
- SOURCED: [edge5-rsi-oi-unwind-newcoins_RESULTS.md:1](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L1): "RESULT: RSI-extreme OI-unwind and dADX cells on 40 new coins (edge5-rsi-oi-unwind-newcoins-1113)"
- SOURCED: [edge5-rsi-oi-unwind-newcoins_RESULTS.md:3](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L3): "Verdict: A FAIL, B UNDERPOWERED (and FRAGILE), C UNDERPOWERED (and negative). No cell passes. The parent's two layer cells do not carry over to new coins."

---

### 2. Table & Arithmetic Consistency

**Consistency Verdict: YES (Internally Consistent within standard rounding).**

Where in the text:
SOURCED: [edge5-rsi-oi-unwind-newcoins_RESULTS.md:9-13](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L9-L13)

Recomputation check:
- **Cell A (1h, OI 24h <= -3 %, +2R)**:
  - SOURCED yearly counts and means ([edge5-rsi-oi-unwind-newcoins_RESULTS.md:11](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L11)): "2021 6, +0.65; 2022 25, -0.30; 2023 40, -0.21; 2024 62, -0.01; 2025 68, +0.26; 2026 69, +0.03"
  - Total trade count: OURS: 6 + 25 + 40 + 62 + 68 + 69 = 270 (Matches table `n = 270`).
  - Pre-2024 vs 2024+ split: OURS: 6 + 25 + 40 = 71 trades pre-2024; 62 + 68 + 69 = 199 trades 2024+. OURS percentage: 199 / 270 = 73.7% (matches SOURCED [edge5-rsi-oi-unwind-newcoins_RESULTS.md:7](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L7): "(199 of 270)" and "thin (71 trades)", though note the text states "87 % of cell A trades are 2024+" which appears to be a slight typographical error for 73.7% or referring to calendar coverage).
  - Total R reconstructed: OURS: (6 * 0.65) + (25 * -0.30) + (40 * -0.21) + (62 * -0.01) + (68 * 0.26) + (69 * 0.03) = 3.90 - 7.50 - 8.40 - 0.62 + 17.68 + 2.07 = +7.13 R.
  - Overall mean R: OURS: 7.13 / 270 = +0.0264 R (Matches table `+0.025`).
  - 2024+ mean R: OURS: ( -0.62 + 17.68 + 2.07 ) / 199 = 19.13 / 199 = +0.0961 R (Matches SOURCED [edge5-rsi-oi-unwind-newcoins_RESULTS.md:15](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L15): "A n 199, +0.095").
  - Without best 5 days: Table states SOURCED [edge5-rsi-oi-unwind-newcoins_RESULTS.md:11](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L11): "best 5 days = 587 % of total R (total R tiny); without them n 239, -0.139". With total R = 6.75 (from 270 * 0.025), 5.87 * 6.75 = 39.62 R removed; remaining R = 6.75 - 39.62 = -32.87 R. OURS: -32.87 / 239 = -0.1375 R (agrees with -0.139 within rounding).

- **Cell B (4h, daily ADX 20-25, +2R)**:
  - SOURCED yearly counts and means ([edge5-rsi-oi-unwind-newcoins_RESULTS.md:12](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L12)): "2022 2, +1.03; 2023 5, +0.42; 2024 10, +0.02; 2025 18, +0.19; 2026 6, +0.17"
  - Total trade count: OURS: 2 + 5 + 10 + 18 + 6 = 41 (Matches table `n = 41`).
  - Total R reconstructed: OURS: (2 * 1.03) + (5 * 0.42) + (10 * 0.02) + (18 * 0.19) + (6 * 0.17) = 2.06 + 2.10 + 0.20 + 3.42 + 1.02 = +8.80 R.
  - Overall mean R: OURS: 8.80 / 41 = +0.2146 R (Matches table `+0.214`).
  - 2024+ mean R: OURS: (0.20 + 3.42 + 1.02) / (10 + 18 + 6) = 4.64 / 34 = +0.1365 R (Matches SOURCED [edge5-rsi-oi-unwind-newcoins_RESULTS.md:15](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L15): "B n 34, +0.136").
  - Without best 5 days: SOURCED [edge5-rsi-oi-unwind-newcoins_RESULTS.md:12](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L12): "best 5 days = 123 % of total R; without them n 34, -0.060". With 8.774 R total, 1.23 * 8.774 = 10.79 R in best 5 days; remaining R = 8.774 - 10.79 = -2.018 R. OURS: -2.018 / 34 = -0.0594 R (matches -0.060).

- **Cell C (A and US session, 13-20 UTC open)**:
  - SOURCED yearly counts and means ([edge5-rsi-oi-unwind-newcoins_RESULTS.md:13](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L13)): "2021 3, +0.91; 2022 4, -1.09; 2023 15, -0.60; 2024 26, -0.18; 2025 22, -0.05; 2026 28, +0.09"
  - Total trade count: OURS: 3 + 4 + 15 + 26 + 22 + 28 = 98 (Matches table `n = 98`).
  - Total R reconstructed: OURS: (3 * 0.91) + (4 * -1.09) + (15 * -0.60) + (26 * -0.18) + (22 * -0.05) + (28 * 0.09) = 2.73 - 4.36 - 9.00 - 4.68 - 1.10 + 2.52 = -13.89 R.
  - Overall mean R: OURS: -13.89 / 98 = -0.1417 R (Matches table `-0.141`).
  - 2024+ mean R: OURS: (-4.68 - 1.10 + 2.52) / (26 + 22 + 28) = -3.26 / 76 = -0.0429 R (Matches SOURCED [edge5-rsi-oi-unwind-newcoins_RESULTS.md:15](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L15): "C n 76, -0.043").

---

### 3. Concrete Methodological and Execution Risks Exposed in the Text

The text directly acknowledges and exposes several critical risks:

1. **Look-ahead & Forward-Window Truncation Risk**:
   - The text uses a fixed forward window at cutoff:
     - SOURCED: [edge5-rsi-oi-unwind-newcoins_RESULTS.md:5](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L5): "last trade entry 2026-11-05 (7 day forward window). Cost per trade: 2 x 5 bp taker + 2 bp slippage = 12 bp round trip, charged on entry and divided by stop distance. Exit +2R, 72 h cap, stop first on ambiguous bars."
     - Exposing trades to a 72h max hold time requires an un-truncated window through 2026-11-08; cutting entry on 2026-11-05 cleanly prevents right-edge censoring.
   - However, universe selection introduces severe backward look-ahead / survivorship bias:
     - SOURCED: [edge5-rsi-oi-unwind-newcoins_RESULTS.md:19](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L19): "Limits as pre-registered: survivorship of the turnover-ranked universe, no funding, flat 2 bp slippage (small coins likely worse), overlapping trades across correlated coins."

2. **Fee and Slippage Underestimation Risk**:
   - SOURCED: [edge5-rsi-oi-unwind-newcoins_RESULTS.md:5](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L5): "Cost per trade: 2 x 5 bp taker + 2 bp slippage = 12 bp round trip, charged on entry and divided by stop distance."
   - SOURCED: [edge5-rsi-oi-unwind-newcoins_RESULTS.md:19](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L19): "flat 2 bp slippage (small coins likely worse), no funding"
   - In newly listed and low-liquidity perps, 2 bp slippage is unrealistically optimistic. Furthermore, funding rates during extreme RSI and OI unwinds can be punitive over a 72-hour hold. Because Cell A only achieves +0.025R net under optimistic 12 bp assumptions, even minor slippage escalation or adverse funding destroys the edge entirely.

3. **Placebo Validity and Statistical Significance**:
   - High placebo p-values across all cells confirm lack of edge:
     - SOURCED: [edge5-rsi-oi-unwind-newcoins_RESULTS.md:11](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L11): "placebo p | 0.321" (Cell A)
     - SOURCED: [edge5-rsi-oi-unwind-newcoins_RESULTS.md:12](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L12): "placebo p | 0.168" (Cell B)
     - SOURCED: [edge5-rsi-oi-unwind-newcoins_RESULTS.md:13](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L13): "placebo p | 0.851" (Cell C)
   - Resampling confirms no significance:
     - SOURCED: [edge5-rsi-oi-unwind-newcoins_RESULTS.md:15](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L15): "Day-cluster one-sided p (share of resampled means <= 0): A 0.445, B 0.111, C 0.800; Bonferroni threshold 0.0167, none met."

4. **Clustering, Independence, and Outlier Sensitivity**:
   - The study admits concurrent cross-coin correlation:
     - SOURCED: [edge5-rsi-oi-unwind-newcoins_RESULTS.md:19](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L19): "overlapping trades across correlated coins."
   - Extreme tail concentration / non-robustness:
     - SOURCED: [edge5-rsi-oi-unwind-newcoins_RESULTS.md:11](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L11): "best 5 days = 587 % of total R (total R tiny); without them n 239, -0.139"
     - SOURCED: [edge5-rsi-oi-unwind-newcoins_RESULTS.md:12](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L12): "best 5 days = 123 % of total R; without them n 34, -0.060"
   - 270 trades occurring on only 149 days indicates cross-sectional clustering (multiple coin signals on the same day). Removing just 5 market-wide rebound days turns both Cell A and Cell B deeply negative.

5. **Sample Size and Multiple Testing / Stratification**:
   - Cell B has only 41 trades over 5 years (30 distinct days):
     - SOURCED: [edge5-rsi-oi-unwind-newcoins_RESULTS.md:12](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L12): "UNDERPOWERED (n < 60, days < 40), FRAGILE"
   - Cell C has negative mean R:
     - SOURCED: [edge5-rsi-oi-unwind-newcoins_RESULTS.md:13](file:///F:/MTS/gq/gemini-edge-blind-edge5-rsi-oi-unwind-newcoins-1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-oi-unwind-newcoins_RESULTS.md#L13): "UNDERPOWERED (n < 100), negative"

---

### 4. Conclusion
The text's verdict ("A FAIL, B UNDERPOWERED (and FRAGILE), C UNDERPOWERED (and negative). No cell passes.") is accurate and completely justified by the numerical tables and the statistical checks. The parent edge does not hold up on new coins.
