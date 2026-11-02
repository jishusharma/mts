# FOUND: 50, NOT_IN_DATA: 1, DIFF: 1

# Blind Re-read of Michael Trend Lines RESULT.md Numbers vs CELLS.csv and STATED_LINES.md

Audit of all empirical numbers, sample sizes, timeframes, parameters, and event counts in:
- `MyTradingSys/research/michael_lines_2026-11/RESULT.md`

Cross-checked against:
- `MyTradingSys/research/trendlines_2026-10-17/counts/CELLS.csv` (committed DEV run, config `wick_log_age500`, tercile `ALL`)
- `MyTradingSys/research/michael_lines_2026-11/STATED_LINES.md` (transcripts extract of Michael's stated trend lines)
- `MyTradingSys/research/trendlines_2026-10-17/count_only.py` (DEV splits and run logic)
- `MyTradingSys/research/trendlines_2026-10-17/TRENDLINE_CONTRACT.md` (arm definitions and parameters)

## Summary

- **Total Numbers / Claims Audited**: 52
- **FOUND (Exact match in cited source / machine-generated count table)**: 50
- **NOT_IN_DATA (Explicit null / missing chart frames acknowledged in text)**: 1
- **DIFF (Discrepancy between report text and source data)**: 1
  - Line 7 states "8 of 11 reference oil/gold/Nasdaq", but `STATED_LINES.md:7-17` records 9 statements referencing oil/gold/Nasdaq (5 oil, 3 gold, 1 nasdaq; 2 NOT_IN_DATA; 0 BTC). If counted by unique videos, 7 of 8 videos reference oil/gold/Nasdaq.

*Note on table row count*: The task goal refers to "the 12-row count table". The actual count table in `RESULT.md:9-16` contains 6 data rows (1d arms A, B, V and 4h arms A, B, V) with 6 count columns each, totaling 36 cell values. All 36 values exactly match `CELLS.csv`.

---

## Audit Table

| Line | Section / Context | Number / Claim | Cited Source | Value in Source | Status | Type | Provenance / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| L1 | Title | 2022-01-01 (BTC DEV start) | `trendlines_2026-10-17/count_only.py:6,32` | `2022-01-01` (`DEV_START_MS`) | **FOUND** | `OURS` | Repo DEV split start date |
| L1 | Title | 2024-06-30 (BTC DEV end) | `trendlines_2026-10-17/count_only.py:6,34` | `2024-06-30` (`NDAYS_DEV` to 2024-07-01) | **FOUND** | `OURS` | Repo DEV split end date |
| L3 | Verdict | 5 event kinds | `trendlines_2026-10-17/counts/CELLS.csv:1` | 5 kinds (first_touch, all_touches, break, retested, reclaimed) | **FOUND** | `OURS` | Event classification taxonomy |
| L3 | Verdict | 4h timeframe | `trendlines_2026-10-17/counts/CELLS.csv:66` | `tf = 4h` | **FOUND** | `OURS` | Evaluation timeframe |
| L3 | Verdict | 1d timeframe | `trendlines_2026-10-17/counts/CELLS.csv:5` | `tf = 1d` | **FOUND** | `OURS` | Evaluation timeframe |
| L5 | Source of counts | 2026-10-17 run date | `trendlines_2026-10-17/counts/CELLS.csv` | Directory path `trendlines_2026-10-17` | **FOUND** | `OURS` | Committed DEV run date slug |
| L5 | Source of counts | 500 age cap | `trendlines_2026-10-17/counts/CELLS.csv:2` | `config = wick_log_age500` | **FOUND** | `OURS` | Age cap parameter (`TRENDLINE_CONTRACT.md:27`) |
| L7 | Stated lines | 11 statements | `michael_lines_2026-11/STATED_LINES.md:19` | 11 statements | **FOUND** | `SOURCED` | SOURCED (`"11 statements"` `STATED_LINES.md:19`); 11 rows in table L7-17 |
| L7 | Stated lines | 8 videos with statements | `michael_lines_2026-11/STATED_LINES.md:19` | in 8 of 10 videos | **FOUND** | `SOURCED` | SOURCED (`"in 8 of 10 videos"` `STATED_LINES.md:19`); 8 unique video IDs |
| L7 | Stated lines | 10 total videos sampled | `michael_lines_2026-11/STATED_LINES.md:1,19` | 10 transcripts / 8 of 10 videos | **FOUND** | `SOURCED` | SOURCED (`"10 transcripts"` `STATED_LINES.md:1`); video sample size |
| L7 | Stated lines | 8 of 11 reference oil/gold/Nasdaq | `michael_lines_2026-11/STATED_LINES.md:7-17` | 9 statements reference oil/gold/Nasdaq (5 oil, 3 gold, 1 nasdaq; 2 NOT_IN_DATA); or 7 of 8 distinct videos | **DIFF** | `OURS` | Discrepancy: text reports 8 of 11, data shows 9 of 11 statements (or 7 of 8 videos) |
| L7 | Stated lines | 11 statements denominator | `michael_lines_2026-11/STATED_LINES.md:19` | 11 statements | **FOUND** | `SOURCED` | SOURCED (`"11 statements"` `STATED_LINES.md:19`); total statement count |
| L11 | Count table | 1d arm A eligible lines: 17 | `trendlines_2026-10-17/counts/CELLS.csv:5` | `eligible_lines = 17` | **FOUND** | `OURS` | Exact cell match `1d\|A\|ALL` |
| L11 | Count table | 1d arm A first_touch: 6 | `trendlines_2026-10-17/counts/CELLS.csv:5` | `first_touch = 6` | **FOUND** | `OURS` | Exact cell match `1d\|A\|ALL` |
| L11 | Count table | 1d arm A all_touches: 8 | `trendlines_2026-10-17/counts/CELLS.csv:5` | `all_touches = 8` | **FOUND** | `OURS` | Exact cell match `1d\|A\|ALL` |
| L11 | Count table | 1d arm A break: 14 | `trendlines_2026-10-17/counts/CELLS.csv:5` | `break = 14` | **FOUND** | `OURS` | Exact cell match `1d\|A\|ALL` |
| L11 | Count table | 1d arm A retested: 10 | `trendlines_2026-10-17/counts/CELLS.csv:5` | `retested = 10` | **FOUND** | `OURS` | Exact cell match `1d\|A\|ALL` |
| L11 | Count table | 1d arm A reclaimed: 2 | `trendlines_2026-10-17/counts/CELLS.csv:5` | `reclaimed = 2` | **FOUND** | `OURS` | Exact cell match `1d\|A\|ALL` |
| L12 | Count table | 1d arm B eligible lines: 19 | `trendlines_2026-10-17/counts/CELLS.csv:10` | `eligible_lines = 19` | **FOUND** | `OURS` | Exact cell match `1d\|B\|ALL` |
| L12 | Count table | 1d arm B first_touch: 3 | `trendlines_2026-10-17/counts/CELLS.csv:10` | `first_touch = 3` | **FOUND** | `OURS` | Exact cell match `1d\|B\|ALL` |
| L12 | Count table | 1d arm B all_touches: 5 | `trendlines_2026-10-17/counts/CELLS.csv:10` | `all_touches = 5` | **FOUND** | `OURS` | Exact cell match `1d\|B\|ALL` |
| L12 | Count table | 1d arm B break: 17 | `trendlines_2026-10-17/counts/CELLS.csv:10` | `break = 17` | **FOUND** | `OURS` | Exact cell match `1d\|B\|ALL` |
| L12 | Count table | 1d arm B retested: 15 | `trendlines_2026-10-17/counts/CELLS.csv:10` | `retested = 15` | **FOUND** | `OURS` | Exact cell match `1d\|B\|ALL` |
| L12 | Count table | 1d arm B reclaimed: 8 | `trendlines_2026-10-17/counts/CELLS.csv:10` | `reclaimed = 8` | **FOUND** | `OURS` | Exact cell match `1d\|B\|ALL` |
| L13 | Count table | 1d arm V eligible lines: 1 | `trendlines_2026-10-17/counts/CELLS.csv:15` | `eligible_lines = 1` | **FOUND** | `OURS` | Exact cell match `1d\|V\|ALL` |
| L13 | Count table | 1d arm V first_touch: 1 | `trendlines_2026-10-17/counts/CELLS.csv:15` | `first_touch = 1` | **FOUND** | `OURS` | Exact cell match `1d\|V\|ALL` |
| L13 | Count table | 1d arm V all_touches: 1 | `trendlines_2026-10-17/counts/CELLS.csv:15` | `all_touches = 1` | **FOUND** | `OURS` | Exact cell match `1d\|V\|ALL` |
| L13 | Count table | 1d arm V break: 1 | `trendlines_2026-10-17/counts/CELLS.csv:15` | `break = 1` | **FOUND** | `OURS` | Exact cell match `1d\|V\|ALL` |
| L13 | Count table | 1d arm V retested: 0 | `trendlines_2026-10-17/counts/CELLS.csv:15` | `retested = 0` | **FOUND** | `OURS` | Exact cell match `1d\|V\|ALL` |
| L13 | Count table | 1d arm V reclaimed: 0 | `trendlines_2026-10-17/counts/CELLS.csv:15` | `reclaimed = 0` | **FOUND** | `OURS` | Exact cell match `1d\|V\|ALL` |
| L14 | Count table | 4h arm A eligible lines: 177 | `trendlines_2026-10-17/counts/CELLS.csv:66` | `eligible_lines = 177` | **FOUND** | `OURS` | Exact cell match `4h\|A\|ALL` |
| L14 | Count table | 4h arm A first_touch: 105 | `trendlines_2026-10-17/counts/CELLS.csv:66` | `first_touch = 105` | **FOUND** | `OURS` | Exact cell match `4h\|A\|ALL` |
| L14 | Count table | 4h arm A all_touches: 133 | `trendlines_2026-10-17/counts/CELLS.csv:66` | `all_touches = 133` | **FOUND** | `OURS` | Exact cell match `4h\|A\|ALL` |
| L14 | Count table | 4h arm A break: 166 | `trendlines_2026-10-17/counts/CELLS.csv:66` | `break = 166` | **FOUND** | `OURS` | Exact cell match `4h\|A\|ALL` |
| L14 | Count table | 4h arm A retested: 140 | `trendlines_2026-10-17/counts/CELLS.csv:66` | `retested = 140` | **FOUND** | `OURS` | Exact cell match `4h\|A\|ALL` |
| L14 | Count table | 4h arm A reclaimed: 98 | `trendlines_2026-10-17/counts/CELLS.csv:66` | `reclaimed = 98` | **FOUND** | `OURS` | Exact cell match `4h\|A\|ALL` |
| L15 | Count table | 4h arm B eligible lines: 208 | `trendlines_2026-10-17/counts/CELLS.csv:71` | `eligible_lines = 208` | **FOUND** | `OURS` | Exact cell match `4h\|B\|ALL` |
| L15 | Count table | 4h arm B first_touch: 66 | `trendlines_2026-10-17/counts/CELLS.csv:71` | `first_touch = 66` | **FOUND** | `OURS` | Exact cell match `4h\|B\|ALL` |
| L15 | Count table | 4h arm B all_touches: 78 | `trendlines_2026-10-17/counts/CELLS.csv:71` | `all_touches = 78` | **FOUND** | `OURS` | Exact cell match `4h\|B\|ALL` |
| L15 | Count table | 4h arm B break: 199 | `trendlines_2026-10-17/counts/CELLS.csv:71` | `break = 199` | **FOUND** | `OURS` | Exact cell match `4h\|B\|ALL` |
| L15 | Count table | 4h arm B retested: 167 | `trendlines_2026-10-17/counts/CELLS.csv:71` | `retested = 167` | **FOUND** | `OURS` | Exact cell match `4h\|B\|ALL` |
| L15 | Count table | 4h arm B reclaimed: 109 | `trendlines_2026-10-17/counts/CELLS.csv:71` | `reclaimed = 109` | **FOUND** | `OURS` | Exact cell match `4h\|B\|ALL` |
| L16 | Count table | 4h arm V eligible lines: 114 | `trendlines_2026-10-17/counts/CELLS.csv:76` | `eligible_lines = 114` | **FOUND** | `OURS` | Exact cell match `4h\|V\|ALL` |
| L16 | Count table | 4h arm V first_touch: 84 | `trendlines_2026-10-17/counts/CELLS.csv:76` | `first_touch = 84` | **FOUND** | `OURS` | Exact cell match `4h\|V\|ALL` |
| L16 | Count table | 4h arm V all_touches: 96 | `trendlines_2026-10-17/counts/CELLS.csv:76` | `all_touches = 96` | **FOUND** | `OURS` | Exact cell match `4h\|V\|ALL` |
| L16 | Count table | 4h arm V break: 110 | `trendlines_2026-10-17/counts/CELLS.csv:76` | `break = 110` | **FOUND** | `OURS` | Exact cell match `4h\|V\|ALL` |
| L16 | Count table | 4h arm V retested: 90 | `trendlines_2026-10-17/counts/CELLS.csv:76` | `retested = 90` | **FOUND** | `OURS` | Exact cell match `4h\|V\|ALL` |
| L16 | Count table | 4h arm V reclaimed: 58 | `trendlines_2026-10-17/counts/CELLS.csv:76` | `reclaimed = 58` | **FOUND** | `OURS` | Exact cell match `4h\|V\|ALL` |
| L20 | Cannot compare | Line anchors/dates on chart frames: NOT_IN_DATA | `michael_lines_2026-11/STATED_LINES.md:3,7-17` | `chart geometry = NOT_IN_DATA` | **NOT_IN_DATA** | `OURS` | Chart frames not stored in repository |
| L22 | Parameters | age cap 500 | `trendlines_2026-10-17/TRENDLINE_CONTRACT.md:27` | `max_age_bars: 500` | **FOUND** | `OURS` | Fixed max lookback window |
| L22 | Parameters | SOURCED numerical parameters: 0 | `michael_lines_2026-11/STATED_LINES.md:7-17` | Michael transcript quotes | **FOUND** | `SOURCED` | SOURCED (`"trend line", "50% level", "$104"` `STATED_LINES.md:7-17`); zero numerical detector parameters |
| L24 | Go/no-go | 4h alert-only card candidate | `trendlines_2026-10-17/counts/CELLS.csv:66-76` | `tf = 4h` counts | **FOUND** | `OURS` | 4h timeframe recommended for alert card |
