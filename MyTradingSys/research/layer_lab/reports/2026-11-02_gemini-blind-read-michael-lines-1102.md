# Layer Lab Report: Blind Re-read of michael_lines_2026-11 RESULT.md Numbers vs CELLS.csv and STATED_LINES.md

- **Task**: `gemini-blind-read-michael-lines-1102`
- **Lane**: `CODEX`
- **Audited Document**:
  - `MyTradingSys/research/michael_lines_2026-11/RESULT.md`
- **Underlying Sources**:
  - `MyTradingSys/research/trendlines_2026-10-17/counts/CELLS.csv`
  - `MyTradingSys/research/michael_lines_2026-11/STATED_LINES.md`
  - `MyTradingSys/research/trendlines_2026-10-17/count_only.py`
  - `MyTradingSys/research/trendlines_2026-10-17/TRENDLINE_CONTRACT.md`
- **Date**: 2026-11-02
- **Auditor**: Gemini 3.8 Flash (medium) worker

---

## 1. Executive Summary

- **Total Claims / Numbers Audited**: 52
- **FOUND**: 50 (96.2%)
- **NOT_IN_DATA**: 1 (1.9%) — chart geometry and line anchors acknowledged as missing from repository (`STATED_LINES.md:3,7-17`).
- **DIFF**: 1 (1.9%) — text arithmetic discrepancy on line 7 regarding statements referencing oil/gold/Nasdaq.

---

## 2. Key Findings by Section

### 1. Count Table vs Committed DEV Run (`trendlines_2026-10-17/counts/CELLS.csv`)
- In `RESULT.md:9-16`, the table contains 6 data rows across two timeframes (`1d` and `4h`) and three eligibility arms (`A`, `B`, `V`).
- (Note: the task card mentions "the 12-row count table", but the markdown table in `RESULT.md` has 6 data rows with 6 event count metrics per row = 36 numeric count values).
- All 36 values match `CELLS.csv` (config `wick_log_age500`, tercile `ALL`) exactly:
  - `1d|A|ALL`: 17 eligible lines, 6 first_touch, 8 all_touches, 14 break, 10 retested, 2 reclaimed (`CELLS.csv:5`).
  - `1d|B|ALL`: 19 eligible lines, 3 first_touch, 5 all_touches, 17 break, 15 retested, 8 reclaimed (`CELLS.csv:10`).
  - `1d|V|ALL`: 1 eligible line, 1 first_touch, 1 all_touches, 1 break, 0 retested, 0 reclaimed (`CELLS.csv:15`).
  - `4h|A|ALL`: 177 eligible lines, 105 first_touch, 133 all_touches, 166 break, 140 retested, 98 reclaimed (`CELLS.csv:66`).
  - `4h|B|ALL`: 208 eligible lines, 66 first_touch, 78 all_touches, 199 break, 167 retested, 109 reclaimed (`CELLS.csv:71`).
  - `4h|V|ALL`: 114 eligible lines, 84 first_touch, 96 all_touches, 110 break, 90 retested, 58 reclaimed (`CELLS.csv:76`).

### 2. Stated Lines Extraction vs Transcripts (`michael_lines_2026-11/STATED_LINES.md`)
- `RESULT.md:7` reports "11 statements in 8 of 10 videos":
  - 11 statements: exact match with 11 rows in `STATED_LINES.md:7-17` and summary in `STATED_LINES.md:19`.
  - 8 videos with statements: exact match with 8 unique video IDs (`7wl0C1lVfRE`, `_LDxOX42NS8`, `avnJKLxX4FY`, `E_AP5kudK5Y`, `F0HeO0os0GM`, `IjC2eoUzA6M`, `KKnktsvQMyo`, `NWwIbm6j6wg`).
  - 10 total videos sampled: exact match with `STATED_LINES.md:1` (`10 transcripts`).
- `RESULT.md:7` reports "8 of 11 reference oil/gold/Nasdaq (OURS keyword guess), not BTC":
  - `DIFF`: In `STATED_LINES.md:7-17`, 9 statements reference oil/gold/Nasdaq (5 oil, 3 gold, 1 nasdaq) and 2 statements are `NOT_IN_DATA` (lines 9 and 10). Zero statements reference BTC.
  - Alternatively, if counted by unique videos, 7 of the 8 videos reference oil/gold/Nasdaq (video `avnJKLxX4FY` has only `NOT_IN_DATA`).
  - Neither count is 8 of 11. The numerator 8 in "8 of 11" appears to have conflated the 8 videos count with the statement count.

### 3. Dates, Parameters, and Missing Data
- Date range: BTC DEV `2022-01-01..2024-06-30` matches `count_only.py:6,32,34`.
- Parameters: `age cap 500` matches `CELLS.csv:2` and `TRENDLINE_CONTRACT.md:27`.
- Zero numerical parameters sourced from Michael matches quotes in `STATED_LINES.md:7-17`.
- Chart geometry / line anchors: acknowledged as `NOT_IN_DATA` in `RESULT.md:20` and `STATED_LINES.md:3,7-17`.

---

## 3. Primary Audit File

Detailed itemized audit table available at:
`MyTradingSys/research/gemini_audits_2026-11-02/michael_lines_blind_read.md`

Noticed: `RESULT.md:7` has a minor numerical typo ("8 of 11 reference oil/gold/Nasdaq" instead of 9 of 11 statements or 7 of 8 videos), and the task prompt card describes `RESULT.md` as having a "12-row count table" whereas the actual table contains 6 data rows with 6 event metrics each.
