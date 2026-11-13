# Blind Review: edge2-capitulation-long

**Verdict: SOUND** (The study's FAIL verdict is mathematically and methodologically justified by the reported data and pre-registration criteria; what would change it is an independent re-test demonstrating a positive, statistically significant fee-net mean across out-of-sample partitions where week-block confidence intervals exclude zero and pass Benjamini-Hochberg FDR control).

---

## 1. Scope and Input Data

- **Input reviewed**: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-capitulation-long_RESULTS.md`
- **Study on trunk**: None (blind review of result text and summary tables only).
- **Stated Author Verdict**: SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-capitulation-long_RESULTS.md:3`: `"Verdict: FAIL (not a pass). 0 of 6 tested cells pass; every VALIDATION and RECENT week-block CI includes 0; 0 BH rejections at 10%."`

---

## 2. Table Analysis and Internal Consistency

### 2.1 Recomputation of Counts and Arithmetic
All arithmetic that can be calculated from the text was recomputed:
1. **Universe Partition Sums (`NEW20` + `OLD10` vs `ALL30`)**:
   - `1h 24h DEV`: SOURCED `853` (NEW20) + `651` (OLD10) = OURS `1504` (matches reported ALL30 `n1504`).
   - `1h 24h VAL`: SOURCED `340` (NEW20) + `208` (OLD10) = OURS `548` (matches reported ALL30 `n548`).
   - `1h 24h REC`: SOURCED `420` (NEW20) + `262` (OLD10) = OURS `682` (matches reported ALL30 `n682`).
   - `1h 3d DEV`: SOURCED `841` (NEW20) + `644` (OLD10) = OURS `1485` (matches reported ALL30 `n1485`).
   - `1h 3d VAL`: SOURCED `338` (NEW20) + `203` (OLD10) = OURS `541` (matches reported ALL30 `n541`).
   - `1h 3d REC`: SOURCED `417` (NEW20) + `259` (OLD10) = OURS `676` (matches reported ALL30 `n676`).
   - `4h 24h DEV`: SOURCED `178` (NEW20) + `103` (OLD10) = OURS `281` (matches reported ALL30 `n281`).
   - `4h 24h VAL`: SOURCED `72` (NEW20) + `35` (OLD10) = OURS `107` (matches reported ALL30 `n107`).
   - `4h 24h REC`: SOURCED `95` (NEW20) + `69` (OLD10) = OURS `164` (matches reported ALL30 `n164`).
   - `4h 3d DEV`: SOURCED `177` (NEW20) + `103` (OLD10) = OURS `280` (matches reported ALL30 `n280`).
   - `4h 3d VAL`: SOURCED `72` (NEW20) + `35` (OLD10) = OURS `107` (matches reported ALL30 `n107`).
   - `4h 3d REC`: SOURCED `94` (NEW20) + `68` (OLD10) = OURS `162` (matches reported ALL30 `n162`).

2. **Weighted Mean Reconciliation**:
   - `1h 24h DEV`: (853 * -0.10 + 651 * -0.07) / 1504 = OURS `-0.0870%` -> reported SOURCED `-0.09%`.
   - `1h 24h VAL`: (340 * 0.65 + 208 * 0.74) / 548 = OURS `+0.6842%` -> reported SOURCED `+0.68%`.
   - `1h 24h REC`: (420 * 0.28 + 262 * 0.39) / 682 = OURS `+0.3223%` -> reported SOURCED `+0.32%`.
   - `1h 3d DEV`: (841 * -0.04 + 644 * -0.08) / 1485 = OURS `-0.0573%` -> reported SOURCED `-0.06%`.
   - `1h 3d VAL`: (338 * 0.65 + 203 * 0.76) / 541 = OURS `+0.6913%` -> reported SOURCED `+0.69%`.
   - `1h 3d REC`: (417 * 0.21 + 259 * 0.25) / 676 = OURS `+0.2253%` -> reported SOURCED `+0.22%`.
   - `4h 24h DEV`: (178 * 1.06 + 103 * -0.05) / 281 = OURS `+0.6531%` -> reported SOURCED `+0.65%`.
   - `4h 24h VAL`: (72 * 0.74 + 35 * -1.20) / 107 = OURS `+0.1054%` -> reported SOURCED `+0.10%`.
   - `4h 24h REC`: (95 * 1.36 + 69 * 0.43) / 164 = OURS `+0.9687%` -> reported SOURCED `+0.97%`.
   - `4h 3d DEV`: (177 * 0.50 + 103 * -0.02) / 280 = OURS `+0.3087%` -> reported SOURCED `+0.31%`.
   - `4h 3d VAL`: (72 * -0.11 + 35 * -1.50) / 107 = OURS `-0.5647%` -> reported SOURCED `-0.57%`.
   - `4h 3d REC`: (94 * 2.37 + 68 * 0.45) / 162 = OURS `+1.5641%` -> reported SOURCED `+1.57%`.

3. **Universe Coin Count**:
   - `NEW20 = DOT UNI ATOM NEAR FIL TRX ETC BCH AAVE XLM ICP APT ARB OP INJ SAND MANA AXS ALGO GRT`: exactly OURS `20` coins.
   - Combined with OLD10 (10 coins), ALL30 = 30 coins.

### 2.2 Consistency Assessment
- **Internally Consistent**: **YES**. All trade count sums and weighted subgroup averages match the aggregate lines (`d ... ALL30 ...`) within floating rounding precision.

---

## 3. Methodological Risks Exposed in the Text

The text directly discloses several structural risks:

1. **Look-Ahead / Prior Leakage Risk**:
   - Quote: SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-capitulation-long_RESULTS.md:3`: `"Wave-1 1h/OLD10 VALIDATION+RECENT were already seen; out-of-sample = NEW20 and 4h."`
   - *Risk*: The 1h timeframe on OLD10 had already been inspected during prior exploratory work (wave-1). The author correctly demotes `1h OLD10` and `1h ALL30` to descriptive (`d`), restricting formal testing (`T`) to uninspected cells (`NEW20` and `4h`).

2. **Fee and Slippage Handling Risk**:
   - Quote: SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-capitulation-long_RESULTS.md:5`: `"Per-trade fee-net mean, 95% week-block CI, placebo mean / 95th pct (all in %)."`
   - *Risk*: While the metric is reported as "fee-net mean", the text specifies no fee model parameters (maker/taker bps, funding, or execution slippage assumptions). If slippage during capitulation spikes is larger than the modelled fee-net deduction, returns would degrade further.

3. **Placebo Validity Risk**:
   - Quote: SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-capitulation-long_RESULTS.md:21`: `"1h NEW20 (new coins, same direction as wave 1) is positive on VALIDATION (+0.65%, n 338-340, above placebo p95 on 24h) and RECENT (+0.2..+0.3%) but CIs span 0 (lower -0.4..-0.8%), and DEV is about 0 (-0.1%): the effect exists only after mid-2024, so it is regime-dependent or noise."`
   - *Risk*: In multiple cells, placebo 95th percentile reaches substantial levels (e.g., `4h OLD10 3d VAL` placebo 95th pct is `+1.56%`, higher than the strategy mean of `-1.50%`; `4h NEW20 3d VAL` placebo 95th pct is `+1.24%`). This indicates wide noise distributions under the placebo baseline, making standard statistical separation difficult with small samples.

4. **Clustering, Sample Size, and Independence Risk**:
   - Quote: SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-capitulation-long_RESULTS.md:21`: `"4h NEW20 is positive in 3 of 4 split cells but n is 72-95 with CI half-width 3-5%."`
   - Quote: SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-capitulation-long_RESULTS.md:5`: `"95% week-block CI"`
   - *Risk*: The author uses week-block bootstrapping to account for temporal clustering across simultaneous capitulation events across assets. However, in 4h cells, `n` drops to `35` to `95` trades total across 20 coins, resulting in huge confidence intervals (e.g. `[-2.85, +5.14]` and `[-3.29, +3.75]`), preventing any rejection of the null hypothesis.

5. **Multiple Testing and Pre-Registration**:
   - Quote: SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-capitulation-long_RESULTS.md:3`: `"0 of 6 tested cells pass; every VALIDATION and RECENT week-block CI includes 0; 0 BH rejections at 10%. PRE_REG frozen in 99f4cb645 before outcomes."`
   - *Risk*: Multiple hypothesis testing across 6 formal candidate cells (`1h/4h` x `NEW20/OLD10` x `24h/3d`) was controlled using Benjamini-Hochberg (BH) at 10% FDR, with git pre-registration (`99f4cb645`). Under this protocol, zero cells achieved significance.

---

## 4. Verdict Evaluation

- **Does the verdict follow from the table?**: **YES**.
  - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge2-capitulation-long_RESULTS.md:3`: Every single tested cell shows `passV False` and `passVR False`.
  - For all 6 tested cells (`T`), the 95% week-block confidence intervals in both `VAL` and `REC` contain zero:
    - `T 1h NEW20 24h`: VAL `[-0.61, +1.98]`, REC `[-0.37, +0.97]`
    - `T 1h NEW20 3d`: VAL `[-0.81, +2.30]`, REC `[-0.52, +1.02]`
    - `T 4h OLD10 24h`: VAL `[-3.59, +2.09]`, REC `[-1.01, +2.26]`
    - `T 4h OLD10 3d`: VAL `[-3.60, +1.67]`, REC `[-1.18, +2.58]`
    - `T 4h NEW20 24h`: VAL `[-2.85, +5.14]`, REC `[-0.23, +3.13]`
    - `T 4h NEW20 3d`: VAL `[-3.29, +3.75]`, REC `[-0.37, +5.47]`
  - Furthermore, DEV period returns are flat or negative across 1h cells (`-0.10%`, `-0.04%`).
  - Therefore, the author's verdict of `FAIL (not a pass)` is strictly supported by the empirical data and pre-registered protocol.
