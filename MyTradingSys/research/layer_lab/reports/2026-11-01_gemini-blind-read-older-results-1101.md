# Layer Lab Report: Blind Re-read of Older RESULT.md and REPORT.md Files

- **Task**: `gemini-blind-read-older-results-1101`
- **Lane**: `CODEX`
- **Date**: 2026-11-01
- **Auditor**: Gemini worker (Antigravity JIS-NUC)
- **Studies Audited**:
  1. `MyTradingSys/research/setup_alpha_beta_v2_2026-10/RESULT.md` (cited `result_numbers.json`, `PRE_REG.md`, `setup_v2.py`, `test_beta_events.py`)
  2. `MyTradingSys/research/us_open_levels_2026-10-30/RESULT.md` (cited `results.json`, `study.py`)
  3. `MyTradingSys/research/us_open_oos_2026-10-30/REPORT.md` (cited `results_oos_2020_2021.json`, `session_sweeps/results_2026-10-04.json`)
  4. `MyTradingSys/research/wt30_sequence_2026-10-30/RESULT.md` (cited `output.txt`, `study.py`)
  5. `MyTradingSys/research/tom_transfer_2026-10-11/vp_return/RESULT.md` (cited `results.json`, `extract_BB3c8visnkI.md:38`, `NakedPocTracker.java:26`)
- **Primary Deliverable**: `MyTradingSys/research/gemini_audits_2026-11-01/older_results_blind_read.md`

---

## 1. Executive Summary

A systematic blind re-read and numerical audit was performed across five older study result files (`RESULT.md` and `REPORT.md`) against their cited raw machine artifacts (`result_numbers.json`, `results.json`, `results_oos_2020_2021.json`, `output.txt`, and canonical code / transcript sources).

Every reported number, event count, win rate, mean return, standard error, t-statistic, confidence interval, and descriptive baseline metric was audited line-by-line and classified as:
- **FOUND**: Exact match between the text claim and the cited source artifact.
- **NOT_IN_DATA**: The cited metric represents an unmodelled factor, external data boundary (e.g. pre-2020 Binance perp history), or unexecuted variant explicitly noted in study limits.
- **DIFF**: Numerical discrepancies between the summary text and cited data source.

### Summary Counts
- **Total Claims / Numbers Audited**: 504
- **FOUND**: 495 (98.21%)
- **NOT_IN_DATA**: 9 (1.79%)
- **DIFF**: 0 (0.00%)
- **Deliverable Header**: `# FOUND: 495, NOT_IN_DATA: 9, DIFF: 0`

---

## 2. Study-by-Study Breakdown

| Study | Primary Cited Sources | Total Audited | FOUND | NOT_IN_DATA | DIFF | Key Line References |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`setup_alpha_beta_v2_2026-10`** | `result_numbers.json`, `PRE_REG.md`, `setup_v2.py`, `fees.py:13`, `test_beta_events.py` | 100 | 97 | 3 | 0 | `result_numbers.json:alpha`, `beta`, `rows`, `last_bar_utc` |
| **`us_open_levels_2026-10-30`** | `results.json`, `study.py` | 165 | 164 | 1 | 0 | `results.json:meta`, `rates` (40 level x bucket cells) |
| **`us_open_oos_2026-10-30`** | `results_oos_2020_2021.json`, `session_sweeps/results_2026-10-04.json` | 24 | 23 | 1 | 0 | `results_oos_2020_2021.json:T1`, `T2`, `T3`, `T4`, `T5` |
| **`wt30_sequence_2026-10-30`** | `output.txt`, `study.py` | 89 | 88 | 1 | 0 | `output.txt:BASE`, `T1`–`T9b`, `med_bars`, `med_price_move_pct` |
| **`tom_transfer_2026-10-11/vp_return`** | `results.json`, `extract_BB3c8visnkI.md:38`, `NakedPocTracker.java:26` | 126 | 123 | 3 | 0 | `results.json:A`, `by_year`, `by_side`, `by_d`, `B`, `naked_ci` |
| **Total** | | **504** | **495** | **9** | **0** | |

---

## 3. Detailed Verification Notes

1. **`setup_alpha_beta_v2_2026-10/RESULT.md`**:
   - `result_numbers.json` verifies all Alpha vs Buy-and-hold table cells: DEV Alpha days 912, n=4, win 50%, mean R 6.18, CAGR 45.4%, Sharpe 1.22, max DD 21.5%, time in market 52%; DEV BH days 912, n=1, win 100%, CAGR 6.1%, Sharpe 0.38, max DD 68.0%, time in market 100%; VAL Alpha days 365, n=11, win 27%, mean R 0.15, CAGR 5.3%, Sharpe 0.32, max DD 32.1%, time in market 70%; VAL BH days 365, n=1, win 100%, CAGR 62.7%, Sharpe 1.23, max DD 29.0%, time in market 100%.
   - All 8 Beta cells (S1_DEV, S1_VAL, S0_DEV, S0_VAL, A1_DEV, A1_VAL, A0_DEV, A0_VAL) match events, trades, win rate, mean R net, SE, t, and median fee burden in `result_numbers.json:beta`.
   - Fee constant of 0.05% per side matches `MyTradingSys/backtest/fees.py:13` (`BINANCE_TAKER = 0.0005`).
   - SOURCED: v1 Beta per-bar n of 708,240 confirmed in `MyTradingSys/research/setup_alpha_beta_2026-10-10/BETA_RESULTS.md:9`.
   - NOT_IN_DATA: Raw aggTrades tick stream (kline taker volume proxy was used), 5m structure-shift entries, and equal highs/lows level definitions.

2. **`us_open_levels_2026-10-30/RESULT.md`**:
   - `results.json` directly corroborates all 40 table cells across 8 price level definitions (`dayH`, `dayL`, `pdh`, `pdl`, `d3h`, `d3l`, `d7h`, `d7l`) and 5 distance buckets (`0-0.25%`, `0.25-0.5%`, `0.5-1%`, `1-2%`, `2%+`).
   - Every single cell's days count (`n`), reach rate % (`touch`), touch count (`nt`), and held 60 min rate % (`held`) matches `results.json:rates` without discrepancy.
   - Metadata matches: BTCUSDT 1m 2022-01-01..2026-09-26, 1230 weekdays, 120 min window, 60 min hold.
   - NOT_IN_DATA: US holidays were not removed (stated limit in `study.py:8` and `results.json:meta.note`).

3. **`us_open_oos_2026-10-30/REPORT.md`**:
   - `results_oos_2020_2021.json` and original `session_sweeps/results_2026-10-04.json` match all reported metrics.
   - Direction test: k=10 orig 0.498 [0.470,0.527] vs OOS 0.485 [0.442,0.529]; k=15 orig 0.494 [0.466,0.523] vs OOS 0.485 [0.442,0.529]; k=30 orig 0.501 [0.472,0.529] vs OOS 0.475 [0.432,0.519].
   - Placebo spread: 24 fixed-UTC-hour anchors (0.440..0.555, median 0.501) matches `results_oos_2020_2021.json:T2.placebo_p_range` (`[0.4396, 0.501, 0.5545]`).
   - Volume / |return| peak tables for US DST and US std match `T1` rankings in both original and OOS datasets.
   - Tests T3, T4, and T5 metrics in lines 29-30 match `T3_london_sweep_asia`, `T4_open_sweep_pre`, and `T5_tom_opening_range` in the json.
   - NOT_IN_DATA: Perp 1m klines for 2019-09..12 do not exist (Binance USDT-M perps public starting 2019-12-31).

4. **`wt30_sequence_2026-10-30/RESULT.md`**:
   - All 13 event rows in the Counts table (T1, T1 4h up, T1 4h down, T2, T2 4h down, T3, T4, T5, T6, T7, T7 4h down, T8, T9b) match `output.txt` lines 7 to 15 and 22 to 39 for sample size `n`, Up 4 h, Up 12 h, +1% first, -1% first, and Mean 12 h return.
   - Baseline distribution of random 30m bars (n=20,000) matches `output.txt:6` (up 12h: 50.0%, +1% first: 45.4%, -1% first: 45.2%, mean 12h: +0.031%).
   - T1 top cross reaching bottom zone (wt1 <= -53): 21% (4h up, med 33.5 bars / ~16.75h, med move -1.74%) vs 29% (4h down, med 32.0 bars / 16.0h, med move -2.10%) matches `output.txt:44-45`.
   - SOURCED: WaveTrend 10/21/4 and levels ±53 cited from LazyBear (`study.py:6`).
   - NOT_IN_DATA: The WT validation window (2024-07 onward) was kept sealed and unread.

5. **`tom_transfer_2026-10-11/vp_return/RESULT.md`**:
   - `results.json` verifies all primary Part A results: real return share 57.2% (n=871, CI [53.9, 60.7]) vs placebo 46.8% (n=883, CI [43.6, 50.0]), diff +10.4 pp (CI [6.4, 14.4]).
   - Near placebo comparison (|d| <= 1): placebo 55.8% (n=439) vs real 55.0% (n=438), diff -0.8 pp (CI [-5.2, 3.7]).
   - Per-year breakdown (2022: real 58.6% vs placebo 44.8%, diff +13.8 pp; 2023: real 54.5% vs placebo 47.9%, diff +6.7 pp; 2024: real 59.4% vs placebo 48.5%, diff +10.9 pp) matches `results.json:by_year`.
   - Part B acceptance table (N=3, 6, 12) matches `results.json:B`.
   - Naked POC table matches `results.json:naked_ci`.
   - SOURCED: Tom's 70% claim matches `extract_BB3c8visnkI.md:38` ("the other 70% he will try and strive to run back here").
   - SOURCED: Revisit threshold 0.3% matches `src/main/java/datafeed/NakedPocTracker.java:26` (`REVISIT_THRESHOLD_PCT = 0.003`).
   - NOT_IN_DATA: Cash-session profile (continuous 24/7 crypto data used), hand-drawn chart levels, and LVN profile calculation.

---

Noticed: Across all five studies and 504 audited numbers/claims, every single claim backed by a saved machine artifact or repo source code file matches the underlying data exactly with zero discrepancies (0 DIFF).
