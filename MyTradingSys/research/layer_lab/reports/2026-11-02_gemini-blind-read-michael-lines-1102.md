FOUND 8 / NOT_IN_DATA 1 / DIFF 2 (michael_lines_2026-11 RESULT.md numbers vs trendlines_2026-10-17/counts/CELLS.csv and STATED_LINES.md; DSA direct blind re-read 2026-11-02 on JIS-NUC)

# Michael lines RESULT.md: blind re-read of numbers

Sources read: RESULT.md (the table and the text numbers), STATED_LINES.md (11 rows, 8 unique videos), CELLS.csv (187 rows; config wick_log_age500, tercile ALL, per tf and eligibility arm). Recount script written from the table headers only; not committed. No holdout read; the committed DEV run is the only input.

| number in RESULT.md | CELLS.csv recount (wick_log_age500, ALL) | verdict |
|---|---|---|
| 1d A row: eligible 17, first_touch 6, all_touches 8, break 14, retested 10, reclaimed 2 | 17, 6, 8, 14, 10, 2 | FOUND |
| 1d B row: 19, 3, 5, 17, 15, 8 | 19, 3, 5, 17, 15, 8 | FOUND |
| 1d V row: 1, 1, 1, 1, 0, 0 | 1, 1, 1, 1, 0, 0 | FOUND |
| 4h A row: 177, 105, 133, 166, 140, 98 | 177, 105, 133, 166, 140, 98 | FOUND |
| 4h B row: 208, 66, 78, 199, 167, 109 | 208, 66, 78, 199, 167, 109 | FOUND |
| 4h V row: 114, 84, 96, 110, 90, 58 | 114, 84, 96, 110, 90, 58 | FOUND |
| "11 statements" | 11 rows in STATED_LINES.md | FOUND |
| "8 of 10 videos" (8 videos) | 8 unique video ids in STATED_LINES.md | FOUND (8); the "of 10" transcripts is only the header text, the transcript count is NOT_IN_DATA |
| "8 of 11 reference oil/gold/Nasdaq, not BTC" | 9 of 11 rows have a named asset (nasdaq 1, oil 5, gold 3); 2 rows are NOT_IN_DATA | DIFF (9, not 8) |
| "12-row count table" | the table has 6 rows (2 tf x 3 arms) | DIFF (6 rows, 36 cells) |

Note on the asset count: recounted from STATED_LINES.md, 1 nasdaq + 5 oil + 3 gold = 9 named rows. The two NOT_IN_DATA rows are the avnJKLxX4FY 00:02:19 line and the _LDxOX42NS8 00:07:29 line.

Counts: FOUND 8 (six table rows, 11 statements, 8 videos), NOT_IN_DATA 1 (transcript count), DIFF 2 (non-BTC count, row count). The descriptive verdict (GO for alert-only on first_touch/break/retested) is not a number and was not judged.
