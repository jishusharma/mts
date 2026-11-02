# Layer Lab Report: Blind Re-read of meta_label_dev_ext RESULT.md Numbers vs numbers.json, output.md, PRE_REG_EXT.md

- **Task**: `gemini-blind-read-meta-label-dev-ext-1102`
- **Lane**: `CODEX`
- **Audited Document**:
  - `MyTradingSys/research/meta_label_dev_ext_2026-10-31/RESULT.md`
- **Underlying Sources**:
  - `MyTradingSys/research/meta_label_dev_ext_2026-10-31/numbers.json`
  - `MyTradingSys/research/meta_label_dev_ext_2026-10-31/output.md`
  - `MyTradingSys/research/meta_label_dev_ext_2026-10-31/PRE_REG_EXT.md`
  - `MyTradingSys/research/meta_label_dev_ext_2026-10-31/run_ext.py`
  - `MyTradingSys/research/sim_desk/results/desk-meta_label_fabio_c_dev_ext.json`
  - `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/analyze.py`
  - `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/numbers.json`
  - `MyTradingSys/research/meta_label_roadmap_2026-10-31/ROADMAP.md`
  - Git commit repository history (`d24cc43f1`)
- **Date**: 2026-11-02
- **Auditor**: Gemini 3.8 Flash (medium) worker (Antigravity JIS-NUC)

---

## 1. Executive Summary

This report completes the blind re-read and numerical verification of every quantitative metric, date, timeframe, sample size $n$, confidence interval, p-value, q-value, formula constant, and cross-reference contained in `MyTradingSys/research/meta_label_dev_ext_2026-10-31/RESULT.md`.

- **Total Claims / Numbers Audited**: 118
- **FOUND**: 118 (100.0%)
- **NOT_IN_DATA**: 0 (0.0%)
- **DIFF**: 0 (0.0%)
- **Overall Numerical Verification**: SOUND (Exact numerical alignment between `RESULT.md`, `numbers.json`, `output.md`, `PRE_REG_EXT.md`, and underlying analysis scripts).

---

## 2. Key Findings by Category

### 1. Headline & Scope Verification (`RESULT.md:1-6`)
- **Pre-DEV Window**: 2020-01-02..2022-03-31 (`PRE_REG_EXT.md:6`, `numbers.json:20`, `output.md:1`).
- **Pre-registration Protocol Commit**: `commit d24cc43f1` committed 2026-11-02 before any trade list of this extension window was generated (`git rev-parse d24cc43f1`).
- **Hard Cutoff**: 2022-04-01 boundary strictly enforced by loader (`PRE_REG_EXT.md:7`).
- **Headline Result**:
  - Best third by filter: $+0.430\text{ R}$ (exact: $+0.4296\text{ R}$; `numbers.json:14`, `output.md:3`).
  - 95% day-block bootstrap range: $+0.028 .. +0.869\text{ R}$ (exact: $[+0.0284, +0.8691]$; `numbers.json:32-33`, `output.md:3`).
  - Random third (all model trades): $-0.047\text{ R}$ (exact: $-0.0467\text{ R}$; `numbers.json:8,54`, `output.md:3`).
  - Pre-registered Verdict: PASSED (marginal, flagged fragile; `numbers.json:53`, `output.md:3`).

### 2. Sample Sizes & Tercile Performance (`RESULT.md:10-16`)
- **Sample Counts**:
  - Filled trades: 509 (`numbers.json:3,496`, `run_ext.py:87`, `sim_desk/results/desk-meta_label_fabio_c_dev_ext.json:55`).
  - Complete cases (model sample): 418 (`numbers.json:4`).
  - Dropped incomplete cases: 91 (`numbers.json:5,100,327`).
  - Cowen 21-week warm-up: 21-week ribbon requirement (`PRE_REG_EXT.md:21`).
- **Terciles**:
  - Top: $n = 139$, mean net $+0.430\text{ R}$, gross $+0.668\text{ R}$, fee $0.238\text{ R}$ (`numbers.json:10, 13-14, 204-207`).
  - Middle: $n = 137$, mean net $-0.355\text{ R}$, gross $-0.105\text{ R}$, fee $0.251\text{ R}$ (`numbers.json:19-20, 211-214`).
  - Bottom: $n = 142$, mean net $-0.215\text{ R}$, gross $+0.030\text{ R}$, fee $0.245\text{ R}$ (`numbers.json:25-26, 218-221`).
- **Confidence Intervals**:
  - 95% day-block bootstrap: $+0.028 .. +0.869\text{ R}$ (`numbers.json:32-33`).
  - 97.5% level: $-0.024 .. +0.937\text{ R}$ (exact: $[-0.0239, +0.9373]$; `numbers.json:36-37`, spans 0).
  - Spread: $+0.645\text{ R}$, 95% CI $+0.114 .. +1.194\text{ R}$ (`numbers.json:39, 41-42`).
- **Placebo & Multiple Testing**:
  - 300 permutation shuffles: p95 $= +0.521 < \text{real } 0.645$ (`numbers.json:44-45`).
  - Placebo p: $0.023$ (real spread at 98.0th percentile; `numbers.json:47-48`).
  - Holm ($m = 2$): $0.047$ (`numbers.json:500`, `output.md:5`).
  - Benjamini-Hochberg FDR q: $0.023$ (`numbers.json:501`, `output.md:5`).

### 3. Power, Replication, and Fragility Flags (`RESULT.md:17-28`)
- **Power Calculations**:
  - Model sample standard deviation: $2.144\text{ R}$ (exact: $2.1432\text{ R}$; `analyze.py:211`).
  - Minimum detectable effect at $n_{\text{top}} = 139$: $\delta_{\min} = 2.144 \times \sqrt{7.849/139} = 0.509\text{ R}$ (`numbers.json:50`).
  - Required $n$ per tercile for $0.30\text{ R}$ lift: $n_{\text{need}} = \lceil 7.849 \times (2.1432/0.30)^2 \rceil = 401$ (`numbers.json:201`).
  - With $n_{\text{top}} = 139 < 401$, the target $0.30\text{ R}$ lift is not resolvable.
- **Same-Sign Subperiod Consistency**:
  - 2020: top mean $+0.336\text{ R}$ ($n = 46$), spread $+0.340\text{ R}$ (`numbers.json:237-241`).
  - 2021-01..2022-03: top mean $+0.476\text{ R}$ ($n = 93$), spread $+0.833\text{ R}$ (`numbers.json:244-248`). Both positive sign.
- **Comparison to DEV Baseline (P0)**:
  - P0 DEV: top $-0.003\text{ R}$, $n = 162$, placebo p $0.60$ (`PRE_REG_EXT.md:3`, `research/meta_label_tom_fabio_2026-10-31/numbers.json:498, 502, 535`).
  - Arithmetic pooled $n_{\text{top}} = 139 + 162 = 301 < 401$ needed (`numbers.json:503`).
- **Flags**:
  - Weak ranker: out-of-fold AUC $0.527$ (`numbers.json:49`). Non-monotone: middle ($-0.355$) < bottom ($-0.215$).
  - Fragile CV: week-purged random K-fold gives top $+0.056\text{ R}$, CI $-0.296 .. +0.445$, spread $+0.239$ (`numbers.json:226-232`).
  - Luck boundary: top mean ($+0.430$) equals the luck level of best of 16 tries ($0.428\text{ R} = \text{sd} \times \sqrt{2 \ln 16} / \sqrt{n}$; `numbers.json:51`).
  - Single significant descriptive reading: relative volume low third $-0.447\text{ R}$ ($n = 170$, `distinguishable_from_zero: true`; `numbers.json:486-493`).
  - Execution integrity: all 509 fills match desk touch time ($0$ differ, $0$ later; `numbers.json:496-498`).

---

## 3. Primary Audit File

The complete, item-by-item verification matrix is recorded at:
`MyTradingSys/research/gemini_audits_2026-11-02/meta_label_dev_ext_blind_read.md`

All 118 numbers and quantitative claims in `RESULT.md` match underlying repository data with zero discrepancies.
