# Report: Gemini Edge Mine Malkan Argon 1113

- **Date:** 2026-11-13 (UTC)
- **Task ID:** `gemini-edge-mine-malkan-argon-1113`
- **Output Artifact:** `MyTradingSys/research/layer_lab/gemini_edge_1113/mine-malkan-argon/RULES.md`
- **Verification Command:** `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/layer_lab/gemini_edge_1113/mine-malkan-argon/RULES.md`
- **Verification Result:** PASS (0 problems)

---

## Findings Summary

1. Mined 15 mechanically testable rules from Malkan RSI source extractions (`MyTradingSys/research/malkan_extract_2026-10-15/extracts/`).
2. Every number and parameter traces strictly to a verbatim quote and file:line reference:
   - SOURCED: Monthly, weekly, and daily RSI parameters (14-period, thresholds 60 and 40, divergence point C targets, candle confirmation stops).
   - Unstated parameters are marked `NOT_STATED` per specification without invention.
3. Top 5 Ranked rules by fewest `NOT_STATED` fields:
   - Rank 1: `MAL-R02` (Regular Bearish Divergence Short) - 0 `NOT_STATED` fields (`MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:464-476`)
   - Rank 2: `MAL-R03` (Regular Bullish Divergence Long) - 0 `NOT_STATED` fields (`MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:483-495`)
   - Rank 3: `MAL-R04` (Weekly Divergence Traded on Daily Chart) - 0 `NOT_STATED` fields (`MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:502-514`)
   - Rank 4: `MAL-R05` (Bullish Divergence on Trendline Break) - 0 `NOT_STATED` fields (`MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_cQ-y1oULkBw.md:285-297`)
   - Rank 5: `MAL-R06` (Seven Star Multi-Timeframe Divergence) - 0 `NOT_STATED` fields (`MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:521-533`)
