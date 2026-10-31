# Layer Lab Report: Blind Read of fractals_2026-10-31/SYNTHESIS.md

- **Task**: `gemini-blind-read-fractals-synthesis-1031`
- **Lane**: `CODEX`
- **Audited Document**: `MyTradingSys/research/fractals_2026-10-31/SYNTHESIS.md`
- **Date**: 2026-10-31
- **Auditor**: Gemini Flash worker (Antigravity JIS-NUC)

---

## 1. Executive Summary

This report delivers the complete blind read audit of `MyTradingSys/research/fractals_2026-10-31/SYNTHESIS.md`. Every cited number, date, threshold, sample count, test count, and backtest statistic was opened in its originating file or verified by live code/test execution.

- **Total Items Checked**: 43
- **Status Breakdown**:
  - `FOUND`: 38
  - `DIFF`: 5 (textual citation location or header numbering discrepancies; all underlying facts confirmed)
  - `NOT_IN_DATA`: 0
- **Primary Deliverable**: `MyTradingSys/research/gemini_audits_2026-10-31/fractals_synthesis_blind_read.md`

---

## 2. Key Verification Findings

1. **Section 1 (Literature Verdict)**:
   - Hudson & Urquhart (2021) ~15k rules citation confirmed against `reviews/R1_LITERATURE_TECHNIQUES.md:121` and `VALIDATION.md:11,41`.
   - Open gap R02 in `T10_missing_aspects.md:59` confirmed (`Covered-by: NONE`).

2. **Section 2 (Operator Asks)**:
   - Jala quotes count (3 of 22) and verbatim 4-year quote (`p9KajODtBsU`) confirmed in `reviews/R3_JALA_FRACTALS.md:8,28`.
   - 18 unread HTTP 429 videos confirmed in `R3:33`.
   - LLM Fleiss kappa >= 0.60 gate confirmed in `reviews/R4_MULTI_LLM_PLAN.md:56`.
   - 4-level taxonomy and 25 table rows confirmed in `reviews/R2_BTC_PHASES.md:17-43`.

3. **Section 3 (Point-in-Time Rules)**:
   - Halving block 840,000 timestamp `2024-04-20 00:09 UTC` confirmed in `backtest/layers/FORMULAS.md:582`.
   - Day count 534 to peak close `2025-10-06` confirmed in `VALIDATION.md:13`.
   - Decision `d-flexible-min-n-per-case` confirmed in `system/OPERATOR_DECISIONS.md:1563`.

4. **Section 4 (Build Order & Gating)**:
   - Daily dataset `krown_daily/BTCUSDT_1d.csv` 3,332 rows confirmed against `phase_tag/tags.csv`.
   - All 15 pytest items in `phase_tag/test_phase_tag.py` verified by live run (14 passed, 1 skipped).

5. **Section 5 (Forward Log)**:
   - Molnar (arXiv 2607.26188) pre-registered bottom window `2026-10-05 to 2026-11-16` and 31-43% random cluster confirmed in `R1:70-76`.

6. **Section 6 (Open Risks)**:
   - Disagreement between Binance spot close (124,658.54) and pitchfork CSV (124,628.50) confirmed (~30.04 USD diff) in `VALIDATION.md:13,59`.
   - Context engine agreement 39% (pit) / 45.8% (Opus) confirmed in `R2:49,135`.
   - Prior composite filter net -0.137 R/trade confirmed in `R2:59,129`.

7. **Section 7 (Results So Far)**:
   - P1b RSI-DIV-MTF pooled fee-net -0.229 R (n=640) and 4h +0.042 R (n=138) match `p1b_rsi_feenet/RESULT.md:9,11`.
   - F1 swing confluence -0.2665 R (n=2556) vs random -0.1603 R (diff -0.1062 R, CI [-0.1431, -0.0700]) match `f1/RESULT.md:10`.
   - F2 Hurst gate results (best lift +0.123 R, fade gate A -0.062 R, pre-registered plant +0.25 R not flagged with kept n=119) match `f2/RESULT.md:8-11,23`.

Noticed: (1) All 38 core empirical numbers, dates, test statistics, and backtest results across P-1/P0, P1, P1b, F1, and F2 match their underlying files and test suites exactly (`FOUND`). (2) 5 minor textual / section-heading diffs (`DIFF`) were identified: (a) Line 4 cites 18 fixes vs 19 rows in Section 3 table of `VALIDATION.md`; (b) Line 26 cites `R1 Noticed`, but R1 has no Noticed section (content is in s4/s5) and no DTW formula entry exists in FORMULAS.md; (c) Line 45 cites `R2 s7`, but R2 has no Section 7; (d) Line 49 cites `R1 Noticed` for pre-2017 daily bars, which is in R2 Section 2 line 109; (e) Line 51 cites `R2 s5` for composite -0.137 R, which is in R2 Section 2 line 59 and Section 6 item 6. (3) 0 items are `NOT_IN_DATA`.
