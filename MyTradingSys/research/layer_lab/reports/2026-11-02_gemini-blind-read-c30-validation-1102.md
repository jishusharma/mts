# Layer Lab Report: Blind Re-read of eagle_eyes_picture C30_VALIDATION.md Numbers vs c30_validation.py

- **Task**: `gemini-blind-read-c30-validation-1102`
- **Lane**: `CODEX`
- **Audited Document**:
  - `MyTradingSys/research/eagle_eyes_picture_2026-10-28/C30_VALIDATION.md`
- **Underlying Sources**:
  - `MyTradingSys/research/eagle_eyes_picture_2026-10-28/c30_validation.py`
  - `MyTradingSys/research/eagle_eyes_picture_2026-10-28/c30_validation_verdict.json`
  - `MyTradingSys/research/eagle_eyes_picture_2026-10-28/PRE_REG_C30.md`
  - Git commit history (`bb124f5cd`)
- **Date**: 2026-11-02
- **Auditor**: Gemini 3.8 Flash (medium) worker (Antigravity JIS-NUC)

---

## 1. Executive Summary

This report completes the blind re-read and numerical verification of every quantitative metric, date, timeframe, bar count, percentage, confidence interval, p-value, and cross-reference contained in `MyTradingSys/research/eagle_eyes_picture_2026-10-28/C30_VALIDATION.md`.

- **Total Numbers / Claims Audited**: 71
- **FOUND**: 71 (100.0%)
- **NOT_IN_DATA**: 0 (0.0%)
- **DIFF**: 0 (0.0%)
- **Overall Numerical Verification**: SOUND (Exact numerical alignment between `C30_VALIDATION.md`, `c30_validation.py`, `c30_validation_verdict.json`, `PRE_REG_C30.md`, and git commit history).

---

## 2. Key Findings by Category

### 1. Preflight Coverage & Integrity Checks (`C30_VALIDATION.md:4`)
- **P1 coverage**:
  - 30m chart: 21,888 of 21,888 bars over 456 days (91 days warm-up from 2024-04-01 + 365 days VALIDATION up to 2025-06-30 23:55 UTC; 456 days * 48 bars/day = 21,888 bars). `c30_validation.py:68-69`.
  - 15m chart: 43,776 of 43,776 bars (456 days * 96 bars/day = 43,776 bars). `c30_validation.py:68-69`.
- **P2b prefix**: 0 of 15 sample cuts differ (`cuts = 15; bad == 0`). `c30_validation.py:71, 77`.
- **P6 fee identity**: max gap 0 (`worst < 1e-6`). `c30_validation.py:83`.
- **P7 overlap**: 0 overlaps (`ov == 0`). `c30_validation.py:84-85`.

### 2. Hypothesis H1 (30m, any trend) Metrics (`C30_VALIDATION.md:9`)
- **Trade count n**: 35 (`c30_validation_verdict.json:7`).
- **Win rate**: 74% (exact: 74.2857%, 26 wins of 35 trades; `c30_validation_verdict.json:12`).
- **Mean (fee-net)**: -0.066% (exact: -0.065915%; `c30_validation_verdict.json:8`).
- **Sample SD**: 1.97 (exact: 1.972866; `c30_validation_verdict.json:9`).
- **95% CI**: -0.720 .. +0.588 (exact: [-0.719526, +0.587696]; `c30_validation_verdict.json:10-11`).
- **Worst trade**: -6.63% (exact: -6.634848%; `c30_validation_verdict.json:13`).
- **Half-years**:
  - H1: n = 19, mean = -0.013% (exact: -0.012918%; `c30_validation_verdict.json:17-18`).
  - H2: n = 16, mean = -0.129% (exact: -0.128849%; `c30_validation_verdict.json:21-22`).
- **P-values**: one-sided p = 0.578 (exact: 0.577754; `c30_validation_verdict.json:15`), Holm p = 0.578 (`c30_validation_verdict.json:207`).
- **Verdict**: FAIL (mean <= 0; `c30_validation.py:115`, `PRE_REG_C30.md:40`).

### 3. Hypothesis H2 (15m, 2h trend up) Metrics (`C30_VALIDATION.md:10`)
- **Trade count n**: 22 (`c30_validation_verdict.json:211`).
- **Win rate**: 73% (exact: 72.7273%, 16 wins of 22 trades; `c30_validation_verdict.json:216`).
- **Mean (fee-net)**: +0.220% (exact: +0.220298%; `c30_validation_verdict.json:212`).
- **Sample SD**: 0.81 (exact: 0.814034; `c30_validation_verdict.json:213`).
- **95% CI**: -0.120 .. +0.560 (exact: [-0.119865, +0.560461]; `c30_validation_verdict.json:214-215`).
- **Worst trade**: -1.45% (exact: -1.454117%; `c30_validation_verdict.json:217`).
- **Half-years**:
  - H1: n = 11, mean = +0.298% (exact: +0.297819%; `c30_validation_verdict.json:221-222`).
  - H2: n = 11, mean = +0.143% (exact: +0.142777%; `c30_validation_verdict.json:225-226`).
- **P-values**: one-sided p = 0.109 (exact: 0.109191; `c30_validation_verdict.json:219`), Holm p = 0.218 (exact: 0.218381; `c30_validation_verdict.json:346`).
- **Verdict**: INCONCLUSIVE (mean > 0, but Holm p > 0.05 and CI spans 0; `c30_validation.py:115`, `PRE_REG_C30.md:40`).

### 4. P8 Random Entries Test (`C30_VALIDATION.md:12`)
- 30 draws (`c30_validation.py:89`).
- H2 beats random entries: 30/30 draws, random median net return = -0.037% (`c30_validation_verdict.json:342-344`).
- H1 beats random entries: 10/30 draws, random median net return = +0.001% (`c30_validation_verdict.json:203-205`).

### 5. Prior DEV Comparisons & Weaknesses (`C30_VALIDATION.md:13-14`)
- H2 DEV mean: +0.261% (`PRE_REG_C30.md:16`).
- Pre-reg weaknesses section: Section 4 ("## 4. Known weaknesses (disclosed now)", `PRE_REG_C30.md:51`).

---

## 3. Primary Audit File

The full itemized verification matrix is recorded at:
`MyTradingSys/research/gemini_audits_2026-11-02/c30_validation_blind_read.md`

Noticed: All numbers in `C30_VALIDATION.md` trace with 100% precision to `c30_validation.py`, `c30_validation_verdict.json`, `PRE_REG_C30.md`, and commit `bb124f5cd`.
