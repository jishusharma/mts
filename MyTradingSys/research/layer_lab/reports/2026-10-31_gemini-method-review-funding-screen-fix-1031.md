# Layer Lab Report: Method Review of Screens Real Funding Fix (Commit 3d8722a93)

Task: `gemini-method-review-funding-screen-fix-1031`  
Lane: `CODEX`  
Reviewer: Gemini 3.8 Flash (independent cross-vendor method review)  
Date: 2026-10-31  

## Overview
Cross-vendor method review of commit `3d8722a93` ("screens: charge real signed funding (side x sum(rate) over (entry, exit]) instead of flat 1 bp").

Full detailed report is saved at `MyTradingSys/research/gemini_burn_2026-10-31/METHOD_REVIEW_FUNDING_SCREEN_FIX.md`.

## Key Findings

1. **Boundary Alignment Anomaly via Settlement Timestamp Jitter**
   - File: `MyTradingSys/backtest/bt/bt_data.py:135-143` (SOURCED)
   - Real raw settlements have timestamp jitter (+1 to +31 ms after 00/08/16 UTC as documented in `T06_cost_fill_realism.md:59` SOURCED).
   - Because `searchsorted(ts, entry_ms, side="right")` is evaluated on strict integer ms, an entry at bar open exactly at `08:00:00.000` is erroneously included in the `(entry, exit]` window of an `08:00:00.005` settlement, charging a full funding fee for a period during which the position was not held.

2. **Silent Negative Cost Rebates on Inverted Window (`entry_ms > exit_ms`)**
   - File: `MyTradingSys/backtest/bt/bt_data.py:141-143` (SOURCED)
   - No monotonic assertion `exit_ms >= entry_ms`. A reversed window results in `cum[b] - cum[a] < 0`, synthetically generating a profit rebate for long positions.

3. **Missing Settlement Timestamp Deduplication in `load_funding`**
   - File: `MyTradingSys/backtest/bt/bt_data.py:154-168` (SOURCED)
   - `load_funding` directly appends `(t, rate)` without timestamp deduplication across CSVs. Overlapping monthly archives could cause cumulative funding double-counting.

4. **Small Sample Size ($n_T = 40$) and Verdict Stability**
   - File: `MyTradingSys/research/gross_effect_screen_2026-10-15/FUNDING_RERUN.md:10-16` (SOURCED)
   - Arm T sample size $n=40 < 200$ mechanically ensures `INCONCLUSIVE` per `PRE_REG.md:77-80` (SOURCED), so verdict invariance is an algebraic property of $n$ rather than funding insensitivity.

5. **Split Boundary Enforcement**
   - File: `MyTradingSys/research/gross_effect_screen_2026-10-15/screen.py:39-43` (SOURCED)
   - **NO ISSUE FOUND**: `CUTOFF_MS = 1_719_792_000_000` is strictly enforced by `load_funding_strict`.

## What Could Not Be Checked Live
- Live files at `F:/MTS/Dumps/backtest` are absent from this isolated worktree (fail-closed check verified).
- Direct per-line verification of the 2,736 historical funding CSV rows was derived from verified audit logs in `T06_cost_fill_realism.md:59`.

Noticed: Tests in `test_bt_data.py` (53 tests), `test_screen.py` (15 tests), and `test_common.py` (15 tests) all pass cleanly.
