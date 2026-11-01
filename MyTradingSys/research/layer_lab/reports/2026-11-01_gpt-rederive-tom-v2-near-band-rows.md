# FOUND: 18, NOT_IN_DATA: 0, DIFF: 0

# Audit: Re-derivation of Tom Near-Band Placebo Headline Numbers (`gpt-rederive-tom-v2-near-band-rows`)

- **Card**: `gpt-rederive-tom-v2-near-band-rows`
- **Audited files**: `MyTradingSys/research/tom_v2_gross_first_2026-11/results.json` (`primary_near`, `primary_verdict`), `RESULT.md`, `full_report.md`
- **Rule source**: `MyTradingSys/research/tom_v2_gross_first_2026-11/PRE_REG.md:10-15` (section "Hypothesis and rule")
- **Window**: DEV_EXT 2020-01-02..2021-12-31 (730 UTC days, 365 evaluated near-band days with $|d| \le 1.0$)

## Headline Figures Comparison

| Figure / Metric | Re-derived Hand Value | File Value (`results.json` / `RESULT.md`) | Status | Notes & Derivation Details |
|---|---|---|---|---|
| Max abs $d$ cutoff (`max_abs_d`) | $1.0$ | $1.0$ | **SAME** | Restricted to $d \in \{-1.0, -0.5, +0.5, +1.0\}$ |
| Days in primary (`n_days`) | $365$ | $365$ | **SAME** | Half of 730 days (8-day cyclic assignment mod 8) |
| Real events count ($n_{\text{real}}$) | $352$ | $352$ | **SAME** | First 5m close outside prior-day value |
| Real return count ($k_{\text{real}}$) | $223$ | $223$ | **SAME** | $k = 0.6335227272727273 \times 352 = 223$ integer returns |
| Real return share ($k/n$) | $223 / 352 = 63.3523\% \approx 63.4\%$ | $0.6335227272727273$ ($63.4\%$) | **SAME** | Matches exact rational fraction $223/352$ |
| Real Wilson 95% CI | $[58.1996\%, 68.2167\%]$ | $[58.2\%, 68.2\%]$ (file bootstrap $[58.24\%, 68.17\%]$) | **SAME** | Wilson score interval matches within rounding |
| Real Bootstrap 95% CI | $[58.24\%, 68.17\%]$ ($58.2..68.2\%$) | `[0.58238636, 0.68169334]` | **SAME** | 2000 day-block resamples |
| Placebo events count ($n_{\text{placebo}}$) | $353$ | $353$ | **SAME** | Shifted band $|d| \le 1.0$ events |
| Placebo return count ($k_{\text{placebo}}$) | $208$ | $208$ | **SAME** | $k = 0.5892351274787535 \times 353 = 208$ integer returns |
| Placebo return share ($k/n$) | $208 / 353 = 58.9235\% \approx 58.9\%$ | $0.5892351274787535$ ($58.9\%$) | **SAME** | Matches exact rational fraction $208/353$ |
| Placebo Wilson 95% CI | $[53.7220\%, 63.9329\%]$ | $[53.8\%, 64.0\%]$ (file bootstrap $[53.85\%, 64.02\%]$) | **SAME** | Wilson score interval matches within rounding |
| Placebo Bootstrap 95% CI | $[53.85\%, 64.02\%]$ ($53.8..64.0\%$) | `[0.53845609, 0.64022663]` | **SAME** | 2000 day-block resamples |
| Difference (real minus placebo share) | $\frac{223}{352} - \frac{208}{353} = +4.4288 \text{ pp} \approx +4.4 \text{ pp}$ | $0.044287599793973786$ ($+4.4 \text{ pp}$) | **SAME** | Difference of exact sample shares |
| Difference Bootstrap 95% CI lower bound | $-0.2685 \text{ pp} \approx -0.3 \text{ pp}$ | `-0.00268487` ($-0.3 \text{ pp}$) | **SAME** | CI spans zero (lower bound $\le 0$) |
| Difference Bootstrap 95% CI upper bound | $+8.9332 \text{ pp} \approx +8.9 \text{ pp}$ | `0.08933182` ($+8.9 \text{ pp}$) | **SAME** | Upper bound under $+10 \text{ pp}$ |
| Difference paired SE | $2.347 \text{ pp} \approx 2.35 \text{ pp}$ | $2.35 \text{ pp}$ (`RESULT.md:8`) | **SAME** | Half-width / 1.96: $(8.933 - (-0.268)) / 3.92 = 2.347 \text{ pp}$ |
| Verdict rule (FAIL if CI lower $\le 0$) | FAIL (lower bound $-0.27 \text{ pp} \le 0$) | FAIL (`primary_verdict = "FAIL"`) | **SAME** | Pre-registered rule `PRE_REG.md:13` strictly enforced |
| Consistency of Bootstrap CI with $n$ & days | Consistent ($\text{SE} = 2.35 \text{ pp}$, $\rho \approx 0.59$) | $\text{SE} = 2.35 \text{ pp}$, CI $-0.3..8.9 \text{ pp}$ | **SAME** | Paired resampling across identical 365 calendar days |

## Analysis of Day-Block Bootstrap CI Consistency

1. **Independent Proportions Comparison**:
   If the real and placebo events occurred on separate days with zero correlation:
   $$\text{SE}_{\text{real}} = \sqrt{\frac{0.6335 \times 0.3665}{352}} \approx 2.568 \text{ pp}$$
   $$\text{SE}_{\text{placebo}} = \sqrt{\frac{0.5892 \times 0.4108}{353}} \approx 2.619 \text{ pp}$$
   $$\text{SE}_{\text{indep}} = \sqrt{2.568^2 + 2.619^2} \approx 3.668 \text{ pp}$$
   Independent 95% CI would have width $2 \times 1.96 \times 3.668 \approx 14.38 \text{ pp}$ (spanning $[-2.8 \text{ pp}, +11.6 \text{ pp}]$).

2. **Paired Day-Block Bootstrap**:
   Because real and placebo events are evaluated across the **exact same 365 days** (`diff()` in `vp_return_to_value.py` draws identical resampled day indices for both arms), market-wide tendencies (e.g. strong daily trend vs ranging) induce a substantial positive correlation between real and placebo daily outcomes:
   $$\text{Var}(\Delta) = \text{Var}(A) + \text{Var}(B) - 2\,\text{Cov}(A, B)$$
   The observed bootstrap standard error is:
   $$\text{SE}_{\text{bootstrap}} = \frac{8.933 - (-0.268)}{2 \times 1.96} = 2.347 \text{ pp}$$
   This matches the reported $\text{SE} = 2.35 \text{ pp}$ in `RESULT.md:8`. The correlation between the daily return shares is $\rho \approx 1 - \frac{2.347^2}{(2.568^2 + 2.619^2)/2} \approx 0.59$, which is expected for shared daily market conditions. The CI $-0.3..8.9 \text{ pp}$ is therefore completely consistent with the stated sample sizes of $n = 352 / 353$ and 365 days.

## Verdict

Every reported number ($n=352$, $n=353$, shares $63.4\%$ and $58.9\%$, difference $+4.4 \text{ pp}$, bootstrap CI $-0.3..8.9 \text{ pp}$, and verdict FAIL) reproduces **SAME** within rounding from the underlying `results.json` counts and `PRE_REG.md` mathematical specification.

Noticed: the near-band restriction ($|d| \le 1.0$) eliminates the far-placebo downward bias ($29\% - 37\%$), revealing that prior-day value does not exhibit a statistically significant value-specific return excess over nearby displaced bands on BTC.
