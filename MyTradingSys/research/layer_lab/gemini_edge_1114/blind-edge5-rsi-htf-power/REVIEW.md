# Blind Review: RSI-HTF Extreme Power Test (`edge5-rsi-htf-power-1113`)

## Verdict: SOUND

The verdict in the results document ("0 of 6 cells PASS. S1 ... UNDERPOWERED ... S2 ... FAIL. S3 ... FAIL") is **SOUND** and directly supported by the data tables, bootstrap confidence intervals, and sensitivity checks.

### What Would Change This Verdict
1. **Longer history / more independent crash regimes**: If new historical data across additional independent market cycles provided $\ge 30$ distinct signal days for S1 with day-cluster bootstrap confidence intervals strictly above zero ($p < 0.0083$).
2. **De-clustering robustness**: If an execution model limiting exposure to 1 trade per crash date maintained positive expectancy across all non-outlier days, rather than reversing to negative mean R upon exclusion of the top 5 days.

---

## 1. Table Arithmetic & Internal Consistency

All recomputable arithmetic in `MyTradingSys/research/layer_lab/gemini_edge_1114/MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md` was recomputed and verified. Overall evaluation: **YES (Internally Consistent)**.

### A. Sample Size and Pooling
- **S1 (4h<=12 & d<30)**:
  - B1: $n = 5$ (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:23`), B2: $n = 31$ (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:24`), POOL: $n = 36$ (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:25`). Recomputed: $5 + 31 = 36$ (OURS).
  - Target 2R weighted mean: $\frac{5 \times 0.150 + 31 \times 1.067}{36} = 0.9396\text{R}$ (OURS) vs reported POOL mean `0.940` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:25`).
  - Time10 exit weighted mean: $\frac{5 \times (-0.204) + 31 \times 1.447}{36} = 1.2177\text{R}$ (OURS) vs reported POOL mean `1.218` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:28`).
- **S2 (4h<=15 & d<30)**:
  - B1: $n = 9$ (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:29`), B2: $n = 76$ (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:30`), POOL: $n = 85$ (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:31`). Recomputed: $9 + 76 = 85$ (OURS).
  - Target 2R weighted mean: $\frac{9 \times (-0.711) + 76 \times 0.434}{85} = 0.3128\text{R}$ (OURS) vs reported POOL mean `0.313` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:31`).
  - Time10 exit weighted mean: $\frac{9 \times (-0.637) + 76 \times 0.497}{85} = 0.3769\text{R}$ (OURS) vs reported POOL mean `0.377` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:34`).
- **S3 (12h<=20)**:
  - B1: $n = 17$ (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:35`), B2: $n = 193$ (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:36`), POOL: $n = 210$ (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:37`). Recomputed: $17 + 193 = 210$ (OURS).
  - Target 2R weighted mean: $\frac{17 \times (-0.112) + 193 \times 0.171}{210} = 0.1481\text{R}$ (OURS) vs reported POOL mean `0.148` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:37`).
  - Time10 exit weighted mean: $\frac{17 \times (-0.423) + 193 \times (-0.031)}{210} = -0.0627\text{R}$ (OURS) vs reported POOL mean `-0.063` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:40`).

### B. Regime Breakdown Recomputation
- **S1 tgt2R**: Bull $n = 7$, mean $0.700$; Bear $n = 29$, mean $0.998$ (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:46`). Weighted mean: $\frac{7 \times 0.700 + 29 \times 0.998}{36} = 0.9401\text{R}$ (OURS) vs `0.940` reported.
- **S1 time10**: Bull $n = 7$, mean $0.697$; Bear $n = 29$, mean $1.343$ (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:47`). Weighted mean: $\frac{7 \times 0.697 + 29 \times 1.343}{36} = 1.2174\text{R}$ (OURS) vs `1.218` reported.
- **S2 tgt2R**: Bull $n = 32$, mean $-0.007$; Bear $n = 53$, mean $0.506$ (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:48`). Weighted mean: $\frac{32 \times (-0.007) + 53 \times 0.506}{85} = 0.3129\text{R}$ (OURS) vs `0.313` reported.
- **S2 time10**: Bull $n = 32$, mean $0.001$; Bear $n = 53$, mean $0.604$ (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:49`). Weighted mean: $\frac{32 \times 0.001 + 53 \times 0.604}{85} = 0.3770\text{R}$ (OURS) vs `0.377` reported.
- **S3 tgt2R**: Bull $n = 64$, mean $0.155$; Bear $n = 146$, mean $0.145$ (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:50`). Weighted mean: $\frac{64 \times 0.155 + 146 \times 0.145}{210} = 0.1480\text{R}$ (OURS) vs `0.148` reported.
- **S3 time10**: Bull $n = 64$, mean $0.040$; Bear $n = 146$, mean $-0.108$ (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:51`). Weighted mean: $\frac{64 \times 0.040 + 146 \times (-0.108)}{210} = -0.0629\text{R}$ (OURS) vs `-0.063` reported.

### C. Concentration & "Without Best 5 Days" Arithmetic
- **S1 tgt2R**: Total R $= 36 \times 0.940 = 33.84\text{R}$ (OURS). Text quotes: `"One date, 2024-07-05, supplies 14 of the 36 trades and 27.7R of the 33.8R total (82%) at 2R"` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:10`). $\frac{27.7}{33.84} = 81.86\% \approx 82\%$ (OURS).
- **Without best 5 days**: $n = 16$, mean $=-0.191\text{R}$ (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:25`). Residual sum $= 16 \times (-0.191) = -3.056\text{R}$ (OURS). Sum of top 5 days $= 33.84 - (-3.056) = 36.896\text{R}$ (OURS). Top 5 share $= \frac{36.896}{33.84} = 1.0903$ (OURS), matching table top5 share `1.09` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:25`).
- **S2 tgt2R**: Total R $= 85 \times 0.313 = 26.605\text{R}$ (OURS). Without best 5 days: $n = 59$, mean $=-0.194\text{R}$ (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:31`). Residual sum $= 59 \times (-0.194) = -11.446\text{R}$ (OURS). Sum of top 5 days $= 26.605 - (-11.446) = 38.051\text{R}$ (OURS). Top 5 share $= \frac{38.051}{26.605} = 1.4302$ (OURS), matching table top5 share `1.43` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:31`).
- **S3 tgt2R**: Total R $= 210 \times 0.148 = 31.08\text{R}$ (OURS). Without best 5 days: $n = 147$, mean $=-0.234\text{R}$ (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:37`). Residual sum $= 147 \times (-0.234) = -34.398\text{R}$ (OURS). Sum of top 5 days $= 31.08 - (-34.398) = 65.478\text{R}$ (OURS). Top 5 share $= \frac{65.478}{31.08} = 2.1067$ (OURS), matching table top5 share `2.10` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:37`).

---

## 2. Risk Analysis (Direct Quotes from Text)

The results document explicitly surfaces critical risks across all required categories:

### A. Look-Ahead and Survivorship Risk
- **Survivorship in Universe Selection**: `"B2 universe chosen by present liquidity (survivorship)"` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:57`). Testing coins that are liquid today creates look-ahead survivorship bias on historic drawdowns.
- **Timing & Pre-Registration Integrity**: The text notes that PRE_REG.md was `"committed before outcomes"` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:54`), and regime was classified at `"the signal bar close of the traded signals"` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:5`), which uses closed bar state without look-ahead, though tests were noted as `"test_power.py (2 tests, not registered)"` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:54`).

### B. Fee, Funding, and Slippage Handling
- **Spot vs Perp Dynamics**: `"Spot not perps, no funding"` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:57`).
- **Cost Assumption**: `"Rules, costs (5 bp taker + 1 bp slippage per side) and exit code are the parent's."` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:7`). During extreme flash crashes (e.g. 2024-07-05), 1 bp slippage per side for 14 simultaneous spot coin entries may severely underestimate realized execution degradation.

### C. Placebo Validity
- **Easy-to-Beat Placebo A**: `"Placebo A (month-matched) is easy to beat because the gated cells fire only in crashes"` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:13`).
- **Fairer Placebo B Comparison**: `"placebo B is the fairer test and S1/S2 pass it, but the day-cluster CI and the 30-day floor bind."` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:13`).
- **Failure on S3**: `"placebo B p 0.117 (random 12h closes on BTC-oversold days do as well)"` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:12`).

### D. Clustering and Independence Risk
- **Single-Date Flush Dominance**: `"One date, 2024-07-05, supplies 14 of the 36 trades and 27.7R of the 33.8R total (82%) at 2R"` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:10`).
- **Overstatement of Independence**: `"the 14-trade date 2024-07-05 is one market observation, so even the day CI may overstate independence"` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:57`).
- **Extreme Top 5 Fragility**: `"the best 5 days are 109% of total R (all other days net negative) and without them the mean is -0.19R (2R) / -0.33R (time10), n 16."` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:10`).
- **Day-Level Bootstrap Crosses Zero**: For S1 tgt2R, trade CI is `[0.49, 1.38]`, but day CI is `[-0.16, 1.53]` with `"only 18 distinct signal days"` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:10`, `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:25`).

### E. Multiple-Testing and Overlap Risks
- **Shared Trades Across Cells**: `"S1 and S2 share trades"` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:57`).
- **Bonferroni Adjustment**: `"Bonferroni threshold 0.05/6 = 0.0083 on day-bootstrap p and both placebo p."` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:7`) and `"Bonferroni over 6 is conservative."` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge5-rsi-htf-power_RESULTS.md:57`).

---

## 3. Review Verdict Justification

The study author's rejection of all 6 cells is fully substantiated:
1. **S1 (4h<=12 & d<30)**: Even though trade-level statistics appear superficially profitable, the cell strictly fails statistical power criteria ($18 < 30$ signal days required by pre-registration protocol) and the day-bootstrap confidence interval crosses zero (`[-0.16, 1.53]`). Moreover, 82% of returns come from a single day (2024-07-05). It is correctly classified as **UNDERPOWERED**.
2. **S2 (4h<=15 & d<30)**: While having 34 days, day CI crosses zero (`[-0.20, 0.82]` tgt2R, `[-0.27, 1.13]` time10), the top 5 days account for 143% to 148% of profits, and B1 performance is negative (`-0.711R` and `-0.637R`). It correctly receives **FAIL**.
3. **S3 (12h<=20)**: Fails against Placebo B ($p = 0.117$ tgt2R, $p = 0.786$ time10) and has a day CI crossing zero or negative expectancy. It correctly receives **FAIL**.

Therefore, the study author's conclusion to reject promotion to the layer lab (`Next: END: leads do not survive the day-cluster view`) is entirely sound.
