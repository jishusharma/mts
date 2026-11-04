# Blind recount, Haiku 5.5 (2026-11-04 result files)

Scope: the 4 RESULT / DEV_CHECK / DESIGN files on the trunk changed since 2026-11-04T09:50Z. Each headline number was recounted from the raw table or CSV it points to, by counting rows, not by re-running the study script.

| file | headline number | my recount | MATCH/DIFF/NOT CHECKABLE | note |
|---|---|---|---|---|
| wall_ledger_2026-11/RESULT.md | 15/15 tests pass | 15 test functions defined | NOT CHECKABLE | no recorded depth data; pass count needs a run |
| wt_extreme_cross_2026-11/RESULT.md | 1m buy -50 n = 15936 | 15936 (sum of same_range + same_trend rows) | MATCH | net -0.141 also matches weighted cell rows; aggregated cells, not events |
| level_approach_2026-10-30/RESULT.md | 10,822 approach events | 10,822 rows in events.csv | MATCH | pdh 9405, lh 1417 |
| sim_desk/api_review/RESULTS_CARDS_2026-11-03.md | 337 result files | 341 card rows; 337 raw reply lines | DIFF | card table 341 rows (187/109/45 verdicts) vs 337 claimed |

Tally: 2 MATCH, 1 DIFF, 1 NOT CHECKABLE.
