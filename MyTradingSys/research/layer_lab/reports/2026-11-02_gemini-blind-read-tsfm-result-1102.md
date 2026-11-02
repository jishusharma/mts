# Layer Lab Report: Blind Re-read of tsfm_2026-11 RESULT.md Numbers vs results.json and PRE_REG.md

- **Task**: `gemini-blind-read-tsfm-result-1102`
- **Lane**: `CODEX`
- **Audited Document**: `MyTradingSys/research/tsfm_2026-11/RESULT.md`
- **Underlying Sources**:
  - `MyTradingSys/research/tsfm_2026-11/results.json`
  - `MyTradingSys/research/tsfm_2026-11/PRE_REG.md`
  - `MyTradingSys/research/tsfm_2026-11/run_tsfm.py`
  - `MyTradingSys/research/tsfm_2026-11/tsfm_lib.py`
  - `MyTradingSys/research/fractals_2026-10-31/f3/RESULT.md`
  - `MyTradingSys/research/fractals_2026-10-31/f4/RESULT.md`
- **Date**: 2026-11-02
- **Auditor**: Gemini 3.8 Flash (medium) worker (Antigravity JIS-NUC)

---

## 1. Executive Summary

Complete blind re-read and numerical verification of every quantitative metric, timeframe, sample size, return percentage, standard error, confidence interval bound, benchmark, loss value, coverage fraction, p-value, threshold, and study reference in `MyTradingSys/research/tsfm_2026-11/RESULT.md`.

- **Total Numbers / Claims Audited**: 91
- **FOUND**: 89 (97.8%)
- **NOT_IN_DATA**: 0 (0.0%)
- **DIFF**: 2 (2.2%)

---

## 2. Findings by Section

### 1. Header, Setup & Environment (`RESULT.md:1-5`)
- **Window**: DEV `2022-01-01..2024-06-30` (`PRE_REG.md:7`). Refuses any bar >= `2024-07-01` (`splits.assert_dev_only`).
- **Timeframes**: `4h` and `8h` (`results.json:3,27`).
- **Execution & Architecture**: `1` run (`PRE_REG.md:28`), context `256` bars (`run_tsfm.py:14`), horizon `1` bar (`run_tsfm.py:24`), threshold `14 bp` (`tsfm_lib.py:13`).
- **Software Stack**: PyTorch `2.15.0+cpu`, `chronos-forecasting 2.3.2` pinned (`PRE_REG.md:11`).

### 2. Table 1: Verdict Arms (`RESULT.md:8-13`)
- **Chronos long 4h**: n = `1921` (`results.json:5`), mean net % = `-0.1084` (`results.json:10`), cost = `0.14` % (`PRE_REG.md:21`), verdict = `FAIL` (`results.json:23`).
  - Discrepancy: `se = 0.0207`. By formula L13 (`half-width / 1.96` on json `ci_pct`), `se = 0.02054` (rounds to `0.0205`), discrepancy of `+0.00016`. Raw `se` not in json.
- **Chronos long 8h**: n = `1073` (`results.json:29`), mean net % = `-0.0913` (`results.json:34`), cost = `0.14` % (`PRE_REG.md:21`), verdict = `INCONCLUSIVE` (`results.json:47`).
  - Discrepancy: `se = 0.0496`. By formula L13 (`half-width / 1.96` on json `ci_pct`), `se = 0.05021` (rounds to `0.0502`), discrepancy of `-0.00061`. Raw `se` not in json.

### 3. Table 2: Detailed Performance & Controls (`RESULT.md:15-18`)
- **4h Arm**: `5216` bars (`results.json:4`), `1921` trades (`results.json:5`), hit `0.420` (`results.json:9`), net R `-0.097` CI `[-0.133, -0.061]` (`results.json:15-18`), net % `-0.108` CI `[-0.148, -0.068]` (`results.json:10-13`), always-long `-0.132` % (`results.json:22`), random-bars `-0.132` % (`results.json:20`), p-value `0.128` (`results.json:21`), verdict `FAIL`.
- **8h Arm**: `2480` bars (`results.json:28`), `1073` trades (`results.json:29`), hit `0.432` (`results.json:33`), net R `-0.058` CI `[-0.122, +0.003]` (`results.json:39-42`), net % `-0.091` CI `[-0.192, +0.005]` (`results.json:34-37`), always-long `-0.126` % (`results.json:46`), random-bars `-0.125` % (`results.json:44`), p-value `0.171` (`results.json:45`), verdict `INCONCLUSIVE`.

### 4. Table 3: Quantile Calibration (`RESULT.md:20-24`)
- Quantiles: `1-bar` horizon, `9 levels` [0.1..0.9] (`PRE_REG.md:12,16`, `run_tsfm.py:15`), target `80 %` interval coverage (`0.80`).
- **4h**: Chronos pinball `0.003254` (`results.json:6`), Gaussian baseline `0.002984` (`results.json:7`), 80% coverage `0.868` (`results.json:8`).
- **8h**: Chronos pinball `0.004596` (`results.json:30`), Gaussian baseline `0.004233` (`results.json:31`), 80% coverage `0.873` (`results.json:32`).

### 5. Findings & Comparisons (`RESULT.md:26-29`)
- Pinball: Chronos is `9 %` worse than Gaussian (4h: +9.05%, 8h: +8.57%), 80% interval covers `87 %` (4h: 86.8%, 8h: 87.3%).
- Benchmark: Long flag beats always-long by `0.02-0.03 pp` (4h: +0.0240 pp, 8h: +0.0350 pp), no better than random bars (p `0.13` / `0.17`).
- Multiple testing: Holm threshold `0.05/108 = 0.00046` (`PRE_REG.md:25`).
- Power: Both runs above `519-trade` power line (`PRE_REG.md:27`). 4h CI entirely below `0` (`results.json:13`).
- Prior analog comparison: F3 (`1h`) and F4 (`8h`, `28-36` trades, `f4/RESULT.md:6,8`). TSFM tests `30-60x` more trades (`1073` and `1921` trades).

---

## 3. Primary Audit File

The complete itemized verification table is recorded at:
`MyTradingSys/research/gemini_audits_2026-11-02/tsfm_result_blind_read.md`

Noticed: All 89 empirical numbers in `RESULT.md` match `results.json` and `PRE_REG.md` exactly, with the sole exception of the two tabulated `se` values in Table 1 (4h `0.0207` vs formula `0.0205`; 8h `0.0496` vs formula `0.0502`), where the stated values diverge slightly from the Line 13 formula applied to the committed JSON CI bounds.
