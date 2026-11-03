# Layer Lab Report: Blind Re-read of oi_side_2026-10-30 RESULT.md Numbers vs output.txt

- **Task**: `gemini-blind-read-oi-side-1103`
- **Lane**: `CODEX`
- **Date**: 2026-11-03
- **Auditor**: Gemini 3.8 Flash (low) worker (Antigravity JIS-NUC)
- **Audited Document**:
  - `MyTradingSys/research/oi_side_2026-10-30/RESULT.md`
- **Underlying Sources**:
  - `MyTradingSys/research/oi_side_2026-10-30/output.txt`
  - `MyTradingSys/research/oi_side_2026-10-30/study.py`
- **Primary Deliverable**:
  - `MyTradingSys/research/gemini_audits_2026-11-03/oi_side_blind_read.md`

---

## 1. Executive Summary

A comprehensive blind re-read and numerical audit of `MyTradingSys/research/oi_side_2026-10-30/RESULT.md` was performed line-by-line against `output.txt` and its generator script `study.py`.

Every quantitative claim, event count, percentage, timeframe, sample size, standard error, and cycle split was catalogued and classified:
- **FOUND**: Exact numerical match or directly derived from `output.txt` / `study.py`.
- **NOT_IN_DATA**: Quoted trigger event metadata from the external operator screenshot prompt (shot `072bbb83f7b1`) or forward card references not present in the empirical output artifact.
- **DIFF**: Numerical discrepancies between summary text and cited data file.

### Summary Counts
- **Total Numbers / Claims Audited**: 114
- **FOUND**: 103 (90.35%)
- **NOT_IN_DATA**: 10 (8.77%)
- **DIFF**: 1 (0.88%)
- **Deliverable Header Verification**: `# FOUND: 103, NOT_IN_DATA: 10, DIFF: 1`

---

## 2. Key Findings & Empirical Comparisons

### Table A: OI x Price over the last 30 minutes (`RESULT.md:19-26` vs `output.txt:3-11`)
- **Total events**: n = 35,963 windows (`RESULT.md:8`, `output.txt:1`).
- All 30 table cell values across 6 rows (n, up 60 min, up 4 h, +0.5% first, -0.5% first) are **FOUND** with exact matching precision:
  - `up up`: n=6,193; up60=48.5% (`0.485`); up240=49.4% (`0.494`); up_first=47.9% (`0.479`); down_first=43.6% (`0.436`).
  - `up flat`: n=8,023; up60=51.3% (`0.513`); up240=51.0% (`0.510`); up_first=41.9% (`0.419`); down_first=39.3% (`0.393`).
  - `up down`: n=4,985; up60=52.7% (`0.527`); up240=52.8% (`0.528`); up_first=43.5% (`0.435`); down_first=48.8% (`0.488`).
  - `down up`: n=5,428; up60=48.9% (`0.489`); up240=49.0% (`0.490`); up_first=45.9% (`0.459`); down_first=43.3% (`0.433`).
  - `down flat`: n=5,038; up60=49.7% (`0.497`); up240=51.0% (`0.510`); up_first=37.5% (`0.375`); down_first=41.3% (`0.413`).
  - `down down`: n=6,296; up60=53.5% (`0.535`); up240=53.4% (`0.534`); up_first=43.3% (`0.433`); down_first=46.7% (`0.467`).
- Direction bounds (48% to 54%) and push lean gap (4.2 points, ~6 standard errors) verified (`RESULT.md:29-30`).

### Table A2: By Cycle / Year (`RESULT.md:36-42` vs `output.txt:13-22`)
- All 20 percentage cells (5 conditions x 4 years 2022-2025) are **FOUND** matching rounded values from `output.txt`:
  - `short covering (down up)`: 44% (`0.442`), 48% (`0.475`), 52% (`0.521`), 55% (`0.549`).
  - `long liquidation (down down)`: 54% (`0.541`), 58% (`0.581`), 53% (`0.529`), 48% (`0.481`).
  - `shorts pressing (up down)`: 52% (`0.524`), 55% (`0.551`), 53% (`0.529`), 50% (`0.496`).
  - `build-up (up flat)`: 52% (`0.518`), 52% (`0.516`), 50% (`0.499`), 52% (`0.519`).
  - `longs pressing (up up)`: 49% (`0.494`), 47% (`0.466`), 49% (`0.485`), 50% (`0.496`).
- Cell count bounds (n per cell 842-2,817) and standard error bounds (1.0-1.7 points) verified (`output.txt:17-22`).
- Shorter cycle definition (20-day mean) max spread across halves: 3.6 points verified (`output.txt:28-33`).

### Table B: Taker Delta Split (`RESULT.md:54-58` vs `output.txt:35-40`)
- All 12 cell values across 3 rows (`buyers`, `mixed`, `sellers`) are **FOUND** with exact precision:
  - `buyers`: n=2,035; up60=49.4% (`0.494`); up_first=40.9% (`0.409`); down_first=36.1% (`0.361`).
  - `mixed`: n=3,765; up60=51.6% (`0.516`); up_first=44.5% (`0.445`); down_first=41.2% (`0.412`).
  - `sellers`: n=2,223; up60=52.6% (`0.526`); up_first=38.3% (`0.383`); down_first=39.0% (`0.390`).
- Unresolved share within 4 hours: 1 - (0.383 + 0.390) = 22.7% (~23%) verified (`RESULT.md:61`).

### Section C/D: Top-Trader Long/Short Ratio (`RESULT.md:64-67` vs `output.txt:42-60`)
- Ratio moved > 1% in about 6% of build-ups ((133 + 379) / 8023 = 6.38%) verified.
- Top longs grew n=133, top shorts grew n=379 verified.
- Sellers with top longs growing (n=39, up60=71.8% -> 72%) verified (`output.txt:59`).
- **DIFF Detected**: `RESULT.md:67` states "Sub-cells hold 39-169 cases". However, `output.txt` Table D shows sub-cells with moved ratio hold 41, 87, 53, 167, 39, and 125 cases. The upper bound is 167 cases (`mixed x top shorts grew`, `output.txt:57`), not 169.

---

Noticed: `RESULT.md:67` carries a minor typo quoting sub-cell upper bound as 169 instead of 167 cases (as recorded in Table D `output.txt:57`). All other 103 data-derived figures match `output.txt` exactly.
