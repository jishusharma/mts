SAME 8 / DIFFERENT 0 / NOT_IN_DATA 3 (reclaim_close_stop RESULT.md headline rows vs results_DEV.csv; DSA direct recount 2026-11-02 on JIS-NUC)

# Reclaim close stop: headline rows re-derived from results_DEV.csv

Source: results_DEV.csv (6 aggregate rows; no per-trade file in the repo). Fee rule: net = gross - 0.10 pp round trip (PRE_REG.md:15). Checks below are arithmetic on the file's own aggregates, not a trade-level recount.

| figure | my value | file / RESULT.md | verdict |
|---|---|---|---|
| 4h all n | 114 | 114 | SAME |
| 4h all gross % | 0.3710 | 0.371 | SAME |
| 4h all mean fee-net % (gross - 0.10) | 0.2710 | 0.271 | SAME |
| 4h all week-block CI | not recomputable | -0.253 .. 0.805 | NOT_IN_DATA (no per-trade rows; run_reclaim.py needs DEV klines not on this machine) |
| 1D all n | 13 | 13 | SAME |
| 1D all gross % | -1.0934 | -1.093 | SAME |
| 1D all mean fee-net % | -1.1934 | -1.193 | SAME |
| 1D all week-block CI | not recomputable | -3.884 .. 1.496 | NOT_IN_DATA |
| 4h long (low-break reclaim) n | 62 | 62 | SAME |
| 4h long fee-net % (0.5268 - 0.10) | 0.4268 | 0.427 | SAME |
| 4h long CI | not recomputable | -0.251 .. 1.218 | NOT_IN_DATA |

Verdict rule check (PRE_REG.md:21): 4h all CI lower bound -0.253 is not above 0 and n = 114 >= 100, so INCONCLUSIVE; 1D all n = 13 < 100, so INCONCLUSIVE. Both match the file. Mirror arms (4h high n 52, 1D low 5, high 8) agree with RESULT.md n values: 52 + 62 = 114 and 5 + 8 = 13.

Counts: SAME 8, DIFFERENT 0, NOT_IN_DATA 3. No verdict on the strategy; the INCONCLUSIVE stands on the file's numbers.
