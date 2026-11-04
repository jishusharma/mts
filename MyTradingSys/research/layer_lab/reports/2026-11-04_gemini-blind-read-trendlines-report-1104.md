# Layer Lab Report: `gemini-blind-read-trendlines-report-1104`

- **Card**: `gemini-blind-read-trendlines-report-1104`
- **Date**: 2026-11-04 UTC
- **Deliverable**: `MyTradingSys/research/gemini_audits_2026-11-04/trendlines_report_blind_read.md`
- **Headline Counts**: `FOUND=51 DIFF=0 NOT_IN_DATA=12`

## Findings

1. **`REPORT.md` Scoping Document vs Realized `counts/*.csv`**:
   - `MyTradingSys/research/trendlines_2026-10-17/REPORT.md` (`2026-10-17`) is the scoping and contract proposal (`"2026-10-17 | Research and build proposal; no backtest performed, no live rule adopted"`, `REPORT.md:3`). Every Krown source locator (`TRL-04`..`TRL-24`), timestamp (`00:04:18`..`00:26:26`), and stated rule number (`2` points, `3` touches, `2x` volume, `4-5` degrees, `0` trades in `KR-S10`/`KR-S11`) in `REPORT.md:31-46` matches `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_14bxwxC8gBQ.md` and `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:45-46` (`FOUND`).
   - 12 conceptual/methodological numbers in `REPORT.md:48-110` (such as the historical `197` Git refs scan at commit `55c66f967dd5`, the `8` deliverable steps, `45-degree` example, and `5-touch` survival example) are non-data prose items and are recorded as `NOT_IN_DATA`.
2. **Count-Only Verification (`counts/CELLS.csv`, `counts/effective_n_by_day.csv`, `counts/quality.txt`, `PRE_REG_TRENDLINES.md`)**:
   - All 37 count/rate/MDE rows audited across `PRE_REG_TRENDLINES.md:7-116` and `counts/CELLS.csv:2-188` match `counts/CELLS.csv`, `counts/effective_n_by_day.csv`, and `counts/quality.txt` with `0` `DIFF`:
     - Holm family: `base_m=65` + `12` carried = `m=77` (`counts/quality.txt:16`, `counts/CELLS.csv:2-188`).
     - All 12 carried `1h` primary cells (`wick_log_age500`, `1h|A|ALL`, `1h|B|ALL`, `1h|V|ALL` $\times$ `first_touch`, `break`, `retested`, `reclaimed`) match both `counts/CELLS.csv:130,135,140` and the per-day event sums and row counts in `counts/effective_n_by_day.csv`.
