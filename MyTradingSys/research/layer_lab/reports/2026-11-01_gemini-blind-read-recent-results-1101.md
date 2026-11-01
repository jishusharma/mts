# Layer Lab Report: Blind Re-read of Recent RESULT.md Files

- **Task**: `gemini-blind-read-recent-results-1101`
- **Lane**: `CODEX`
- **Date**: 2026-11-01
- **Auditor**: Gemini worker (Antigravity JIS-NUC)
- **Studies Audited**:
  1. `MyTradingSys/research/tom_v2_gross_first_2026-11/RESULT.md`
  2. `MyTradingSys/research/reclaim_close_stop_2026-11/RESULT.md`
  3. `MyTradingSys/research/meta_label_breaks_2026-10-31/RESULT.md`
  4. `MyTradingSys/research/cowen_q4_2026-10-31/event_study/RESULT.md`
  5. `MyTradingSys/research/tf_break_event_study_2026-10-30/RESULT.md`
- **Primary Deliverable**: `research/gemini_audits_2026-11-01/recent_results_blind_read.md`

---

## 1. Executive Summary

A systematic blind re-read and numerical audit was performed across five recent study `RESULT.md` files against their cited raw data files (`results.json`, `results_DEV.csv`, `output.md`, `explore_div_output.md`, and `EVENTS.csv`).

Every numeric claim, sample count, mean, standard error, confidence interval, and descriptive feature metric was catalogued line-by-line, verified against the cited data source, and classified as:
- **FOUND**: Exact numerical match in the cited raw data artifact.
- **NOT_IN_DATA**: The cited file is absent from the repository / disk (e.g. `confirm_div.json`, external `F:/MTS/runs/` paths), or the cited metric was an external baseline / runtime bootstrap range not retained in the tabular data file.
- **DIFF**: Numerical discrepancies between the summary text and cited data file.

### Summary Counts
- **Total Claims / Numbers Audited**: 221
- **FOUND**: 201 (90.95%)
- **NOT_IN_DATA**: 20 (9.05%)
- **DIFF**: 0 (0.00%)
- **Deliverable Header Verification**: `# FOUND: 201, NOT_IN_DATA: 20, DIFF: 0`

---

## 2. Study-by-Study Breakdown

| Study | Primary Cited Sources | Total Numbers Audited | FOUND | NOT_IN_DATA | DIFF | Key Sources / Line References |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`tom_v2_gross_first_2026-11`** | `results.json`, `PRE_REG.md`, `extract_BB3c8visnkI.md:38` | 27 | 24 | 3 | 0 | `results.json:meta`, `primary_near`, `far_descriptive`, `A` |
| **`reclaim_close_stop_2026-11`** | `results_DEV.csv`, `fees.py`, `tf_break/output.md:12` | 22 | 22 | 0 | 0 | `results_DEV.csv:1-7`, `fees.py:BINANCE_TAKER` |
| **`meta_label_breaks_2026-10-31`** | `output.md`, `explore_div_output.md`, `confirm_div.json` | 100 | 92 | 8 | 0 | `output.md:6-18,38-51`, `explore_div_output.md:26-103` |
| **`cowen_q4_2026-10-31/event_study`** | `EVENTS.csv`, `PRE-REG.md`, `COWEN_LEVELS_2026-10-31.md:21` | 44 | 35 | 9 | 0 | `EVENTS.csv` (82 events across 4 ideas and 7 years) |
| **`tf_break_event_study_2026-10-30`** | `output.md`, `fees.py` | 28 | 28 | 0 | 0 | `output.md:11-19,28-97,116-127` |
| **Total** | | **221** | **201** | **20** | **0** | |

---

## 3. Detailed Verification Notes

1. **`tom_v2_gross_first_2026-11/RESULT.md`**:
   - `results.json` accurately corroborates the primary near-band placebo comparison: real share 63.4% (n=352, CI [58.2, 68.2]) vs placebo 58.9% (n=353, CI [53.8, 64.0]), difference 4.4 pp (CI [-0.3, 8.9]).
   - Far band numbers (`far_descriptive` in `results.json`) match exactly: real 58.5% (n=349) vs placebo 37.3% (n=359), difference 21.1 pp (CI [13.7, 28.6]).
   - SOURCED: Tom's 70% claim is cited from `extract_BB3c8visnkI.md:38` ("the other 70% he will try and strive to run back here").
   - NOT_IN_DATA: The historical DEV reference figures (57.2/46.8/51.2/47.8) and task card prior expectation (~870 events) are external references explicitly stated as not re-derived in this run.

2. **`reclaim_close_stop_2026-11/RESULT.md`**:
   - Every single metric in the summary and descriptive text matches `results_DEV.csv` lines 2 to 7 without any discrepancies.
   - 4h all DEV: n=114, gross=0.371%, net=0.271%, CI=[-0.253, 0.805], win_pct=40.35%, stop_share=50.0%, mean_hold=4.04 bars.
   - 1D all DEV: n=13, gross=-1.093%, net=-1.193%, CI=[-3.884, 1.496].
   - External reference to T058 fade-R at 4h DEV (-0.417%, n=111) matches `tf_break_event_study_2026-10-30/output.md:12`.

3. **`meta_label_breaks_2026-10-31/RESULT.md`**:
   - All meta-label test arm numbers (trades, gross, net, week-block CIs, placebo p, Holm p, and subgroup splits) match `output.md` lines 6 to 18.
   - Early exit trade proportions and underwater shares (winners underwater 27-28%, losers underwater 62-67%) match `output.md` exactly.
   - Descriptive feature splits and Malkan divergence exploratory numbers match `output.md` and `explore_div_output.md` lines 26 to 103.
   - NOT_IN_DATA: The fresh-data validation run raw file (`F:/MTS/runs/meta_label_breaks/confirm_div.json`, lines 72-80) and raw `dev.json` are stored outside this repository and not present on this machine's disk.

4. **`cowen_q4_2026-10-31/event_study/RESULT.md`**:
   - Direct verification against `EVENTS.csv` (82 total rows) confirms all event counts, reasons, and gross/net R metrics:
     - BOUNCE: n=21, 5 hit (23.8%), 15 stop (71.4%), 1 timeout (4.8%), 6 wins (28.6%), gross R -0.18, net R -0.20.
     - LOSE: n=22, 12 hit (54.5%), 9 stop (40.9%), 1 timeout (4.5%), 13 wins (59.1%), gross R +0.72, net R +0.69.
     - FAKEOUT: n=20, 9 hit (45.0%), 11 stop (55.0%), 0 timeout (0.0%), 9 wins (45.0%), gross R +0.35, net R +0.33.
     - CATCHDOWN: n=19, 4 hit (21.1%), 15 stop (78.9%), 0 timeout (0.0%), 4 wins (21.1%), gross R -0.37, net R -0.40.
   - All 24 yearly breakdown cells across 2018–2024 match `EVENTS.csv` means exactly.
   - NOT_IN_DATA: The 8-cycle shifted placebo events and bootstrap 95% ranges were generated at execution time and not saved into `EVENTS.csv`.

5. **`tf_break_event_study_2026-10-30/RESULT.md`**:
   - All 18 verdict arms (n, net mean %, SE %, CI) match `output.md` lines 11 to 19.
   - All 6 findings (event frequencies, pseudo-level comparisons, indicator states before/at/after, break distance splits, and gross continuations) match tables T0 to T5 in `output.md`.

---

Noticed: Across all five studies, every reported number that has a saved artifact on disk matches the underlying data without variance (zero DIFFs found); discrepancies only arise when raw runtime JSONs reside on non-repo machine storage paths (`F:/MTS/runs/`).
