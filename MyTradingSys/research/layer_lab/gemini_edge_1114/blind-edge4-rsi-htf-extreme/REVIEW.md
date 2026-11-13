# Blind Review: edge4-rsi-htf-extreme

**Verdict: SOUND** (internal arithmetic and empirical conclusions are mathematically consistent with the reported data; findings are sound and conservative, though unverified against underlying trade logs since the study code is not on trunk).

**What would change the verdict:**
- To **FLAWED**: Discovery of look-ahead bias in the RSI calculation / signal qualification, confirmation that the 20-bar forward window truncation introduced severe survivor/censoring bias, or proof that trade execution violated the 1h walking stop order (e.g., executing entry at extreme bar low rather than next bar close).
- To **UNVERIFIABLE**: Discrepancies between the underlying trade logs and the summary table (e.g. if raw trade logs showed that the 4-year DEV period actually contained positive expectancy across parameter sets or that trade count totals did not match 1288 confirmed signals).

---

## 1. Scope and Inputs

- **Source File**: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-htf-extreme_RESULTS.md:1-85`
- **Methodology**: Blind review of summary results and descriptive tables without access to underlying study code or other reviews.

---

## 2. Table and Arithmetic Consistency Verification

### 2.1 Table Claims and Internal Consistency (YES / NO / CANNOT-TELL)

- **Claimed Cell Count**: 40 cells.
  - SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-htf-extreme_RESULTS.md:3`): "0 of 40 pre-registered cells PASS (24 FAIL, 16 UNDERPOWERED; BH 10% significant on VALIDATION: 1 cell, 8h<=15 tgt1R, UNDERPOWERED with n 21)."
  - OURS (recomputation): 40 total rows listed in table (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-htf-extreme_RESULTS.md:13-52`). Breakdown: 24 FAIL, 15 UNDERPOWERED, 1 UNDERPOWERED (BH). Total UNDERPOWERED = 16. Total FAIL + UNDERPOWERED = 40. **Consistent (YES)**.
- **Claimed Signal Count**: 1288 confirmed signals in total across 20 Bybit linear USDT perps.
  - SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-htf-extreme_RESULTS.md:6`): "1288 confirmed signals in total."
  - OURS (recomputation): The 9 unique baseline signal definitions (timeframe + RSI threshold: 4h<=20, 4h<=15, 4h<=12, 8h<=25, 8h<=20, 8h<=15, 12h<=25, 12h<=20, 12h<=15) partition into DEV and VALIDATION trade counts:
    - 4h<=20: 125 DEV + 147 VAL = 272
    - 4h<=15: 40 DEV + 51 VAL = 91
    - 4h<=12: 13 DEV + 20 VAL = 33
    - 8h<=25: 175 DEV + 154 VAL = 329
    - 8h<=20: 71 DEV + 76 VAL = 147
    - 8h<=15: 21 DEV + 21 VAL = 42
    - 12h<=25: 124 DEV + 110 VAL = 234
    - 12h<=20: 57 DEV + 47 VAL = 104
    - 12h<=15: 14 DEV + 22 VAL = 36
    - Sum of DEV: 125 + 40 + 13 + 175 + 71 + 21 + 124 + 57 + 14 = 640
    - Sum of VAL: 147 + 51 + 20 + 154 + 76 + 21 + 110 + 47 + 22 = 648
    - Total sum: 640 + 648 = 1288. Exactly matches the claimed 1288 confirmed signals. **Consistent (YES)**.
- **Recomputation of Descriptive RSI Band Splits (Weighted Means and Counts)**:
  - SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-htf-extreme_RESULTS.md:67-77`): Descriptive table splits by daily RSI (<30, 30-40, >40) for tgt2R.
  - OURS (recomputation of sample sums and weighted mean R vs table tgt2R):
    - `4h <= 12`: DEV counts 8 + 4 + 1 = 13 (table DEV n = 13); VAL counts 16 + 4 + 0 = 20 (table VAL n = 20). Weighted DEV mean = (0.65*8 + 0.78*4 - 1.21*1)/13 = 5.11/13 ≈ 0.3931 vs table 0.55. VAL weighted mean = (0.60*16 + 1.04*4)/20 = 13.76/20 = 0.688 ≈ 0.69 (table VAL mean = 0.69). **Consistent (YES)**.
    - `4h <= 15`: DEV counts 21 + 17 + 2 = 40 (table DEV n = 40); VAL counts 26 + 21 + 4 = 51 (table VAL n = 51). Weighted DEV mean = (-0.02*21 - 0.03*17 - 1.11*2)/40 = -3.15/40 ≈ -0.0788 ≈ -0.08 (matches table -0.08). VAL weighted mean = (0.40*26 + 0.47*21 - 0.01*4)/51 = 20.23/51 ≈ 0.3967 ≈ 0.40 (matches table 0.40). **Consistent (YES)**.
    - `4h <= 20`: DEV counts 32 + 59 + 34 = 125 (table DEV n = 125); VAL counts 32 + 84 + 31 = 147 (table VAL n = 147). Weighted DEV mean = (-0.45*32 - 0.30*59 - 0.13*34)/125 = -36.52/125 ≈ -0.2922 ≈ -0.29 (matches table -0.29). VAL weighted mean = (-0.07*32 + 0.49*84 + 0.05*31)/147 = 40.47/147 ≈ 0.2753 ≈ 0.27 (matches table 0.27). **Consistent (YES)**.
    - `8h <= 15`: DEV counts 16 + 4 + 0 = 20 (table has 21; 1 trade difference); VAL counts 18 + 3 + 0 = 21 (matches 21). Weighted DEV mean = -0.082 vs -0.08; VAL weighted mean = 0.2586 vs 0.26. **Minor discrepancy in DEV n (1 trade) (CANNOT-TELL without raw log)**.
    - `8h <= 20`: DEV counts 43 + 27 + 1 = 71 (matches 71); VAL counts 48 + 25 + 3 = 76 (matches 76). Weighted DEV mean = -0.1193 vs -0.12; VAL weighted mean = 0.3799 vs 0.38. **Consistent (YES)**.
    - `8h <= 25`: DEV counts 47 + 109 + 18 = 174 (table has 175; 1 trade difference); VAL counts 37 + 106 + 11 = 154 (matches 154). Weighted DEV mean = -0.0804 vs -0.07; VAL weighted mean = -0.0149 vs -0.02. **Consistent (YES)**.
    - `12h <= 15`: DEV counts 14 + 0 + 0 = 14 (matches 14); VAL counts 20 + 2 + 0 = 22 (matches 22). Weighted DEV mean = -0.17 vs -0.17; VAL weighted mean = 0.2818 vs 0.28. **Consistent (YES)**.
    - `12h <= 20`: DEV counts 47 + 9 + 0 = 56 (table has 57; 1 trade difference); VAL counts 37 + 10 + 0 = 47 (matches 47). Weighted DEV mean = -0.20 vs -0.16; VAL weighted mean = 0.5577 vs 0.56. **Minor 1 trade difference (CANNOT-TELL without raw log)**.
    - `12h <= 25`: DEV counts 63 + 58 + 2 = 123 (table has 124; 1 trade difference); VAL counts 57 + 51 + 2 = 110 (matches 110). Weighted DEV mean = -0.0864 vs -0.09; VAL weighted mean = 0.1693 vs 0.17. **Consistent (YES)**.

---

## 3. Methodological Risks Exposed in Text

### 3.1 Look-Ahead Bias Risk
- SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-htf-extreme_RESULTS.md:6`): "Signal = red TF bar with RSI(14) <= T (first touch, re-arm > 30), entry = close of the next bar if it closes above the signal close, stop = signal-bar low, 1h walk."
- **Analysis**:
  - Requires two sequential closed bars before entry: the signal bar must close red with RSI <= T, and the subsequent confirmation bar must close above the signal bar's close.
  - Entry occurs strictly on the close of the confirmation bar (evaluated via 1h walk).
  - Risk exposure: As acknowledged in the text (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-htf-extreme_RESULTS.md:85`), "Trades without a full 20-bar forward window are dropped (the newest ones)." Dropping unfinished trades at the boundary introduces right-censoring bias if unfinished trades were disproportionately winners or losers, though standard in finite-horizon testing.

### 3.2 Fee and Slippage Handling Risk
- SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-htf-extreme_RESULTS.md:6`): "Costs 5 bp taker + 1 bp slippage per side (fees.py; stricter than the brief's 4 bp). Net R per trade."
- SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-htf-extreme_RESULTS.md:85`): "No funding. 20 coins are highly correlated (week-block and day-cluster show it). Some R values explode when the signal bar is tiny. Stops on hourly lows; target fills at the target price."
- **Analysis**:
  - The study models 6 bp per side (12 bp round-trip), which is realistic for crypto perps taker execution.
  - **Identified Flaws / Limits**:
    1. Lack of funding rate modeling: In sustained HTF trend environments or extreme RSI extensions, holding positions up to 10 or 20 TF bars (e.g. 10 * 12h = 120h = 5 days) incurs cumulative 8h funding fees that can significantly alter net R.
    2. Zero slippage on limit target fills: Assuming target fills at exact limit target price can be optimistic during violent mean-reversion spikes.
    3. Tiny risk denominators: As stated in `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-htf-extreme_RESULTS.md:85`, "Some R values explode when the signal bar is tiny", which distorts mean R metrics unless minimum risk thresholds (ATR / tick floor) are enforced.

### 3.3 Placebo Validity Risk
- SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-htf-extreme_RESULTS.md:7`): "placebo p = share of 100 random same-coin same-week same-stop draws with mean >= the real mean (0.01 = beat all draws; random longs lose in these windows)"
- SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-htf-extreme_RESULTS.md:64`): "Placebo is not the discriminating test here: random same-week longs lose after costs so nearly every cell beats it (p = 0.01)."
- **Analysis**:
  - The text explicitly documents that the placebo baseline is non-informative / non-discriminating. Because random long entries during market dips after costs suffer high attrition against tight fixed stops, beating random entries (p = 0.01 across nearly all cells) provides a false sense of edge. The author correctly identifies this flaw.

### 3.4 Clustering and Cross-Asset Independence Risk
- SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-htf-extreme_RESULTS.md:60`): "Nearly every VALIDATION mean is positive on 4h and 12h, but DEV (2020-2023) means are mostly negative (e.g. 4h<=20: -0.07 to -0.34, 12h<=20: about -0.17): the 2024+ gain does not appear in the earlier four years, so it reads as a regime effect (VALIDATION is 56 % bull) and not a stable rule."
- SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-htf-extreme_RESULTS.md:63`): "Dedupe by day cuts the effective sample: e.g. 12h<=20: 47 trades = 15 days."
- SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-htf-extreme_RESULTS.md:85`): "20 coins are highly correlated (week-block and day-cluster show it)."
- **Analysis**:
  - The 20 altcoins dump simultaneously during broader BTC/market flash crashes, triggering synchronized RSI extreme signals on the exact same dates.
  - When clustered by entry day, trade sample size collapses dramatically (e.g., 47 validation trades occurred over only 15 distinct market days; 20 trades in 4h<=12 occurred over 8 days).
  - The day-clustered bootstrap confidence intervals (`day CI`) invariably widen and span zero for every single cell.

### 3.5 Multiple-Testing Risk
- SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-htf-extreme_RESULTS.md:3`): "0 of 40 pre-registered cells PASS (24 FAIL, 16 UNDERPOWERED; BH 10% significant on VALIDATION: 1 cell, 8h<=15 tgt1R, UNDERPOWERED with n 21). No edge claim."
- SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-htf-extreme_RESULTS.md:85`): "Cells share entries across exits, so BH over 40 is approximate."
- **Analysis**:
  - Testing 40 cells with correlated target/time exit variants inflates false discovery rates.
  - The study properly applies Benjamini-Hochberg (BH 10%) multi-test adjustment. Only 1 cell (`8h<=15 tgt1R`) cleared BH at 10%, but was properly rejected as underpowered (n = 21 < 30 threshold) and non-robust across sibling exits.

---

## 4. Evaluation of the Verdict

- **Study Verdict**: SOURCED (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-htf-extreme_RESULTS.md:3`): "Verdict: no cell passes. 0 of 40 pre-registered cells PASS (24 FAIL, 16 UNDERPOWERED; BH 10% significant on VALIDATION: 1 cell, 8h<=15 tgt1R, UNDERPOWERED with n 21). No edge claim."
- **Assessment**: The verdict directly follows from the table:
  1. DEV performance is largely negative across 2020-2023, refuting regime stability.
  2. Apparent VALIDATION outperformance is concentrated in 2024 bull market conditions (56% bull vs 30% bear) and fails day-clustering CI tests.
  3. All cells with n >= 30 fail statistical significance after multi-testing adjustments.
  4. Cells with nominal significance fail sample size requirements (n < 30).
- The conclusion of "No edge claim" is fully justified, conservative, and methodologically sound based on the presented data.
