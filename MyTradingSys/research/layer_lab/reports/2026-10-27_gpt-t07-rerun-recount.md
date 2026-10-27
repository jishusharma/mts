# GPT T07 rerun recount - 2026-10-27

Verdict: **FIX-FIRST** - `rerun_diff.csv` supports **9 of 10 result groups exact**, not 8. `published_strats` is not represented in this comparison and was not rerun.

## Checked

- Read `MyTradingSys/research/dsa_backtest_audit_2026-10-16/T07_stale_verdicts.md` and `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T07/out/rerun_diff.csv`.
- Applied the relevant PRE_REG_TEMPLATE boundary: this is a recount of already-produced comparisons, not a backtest or market-data read; no new run was performed and no candle bars were read.
- Command: Python `csv.DictReader` parse of `rerun_diff.csv`, counting data rows and `status` by `result`.
- CSV has 3,098 data rows (header plus 3,098 rows, lines 1-3099), 10 result groups, 2,132 `MATCH` cells and 966 `DIFF` cells.
- Nine groups are entirely `MATCH`: `gross_effect_screen` (70), `opr_preopen_tops` (634), `mal_bb_mid_engulf` (397), `opr_bb_mtf_center` (265), `opr_weekly_low_round_sweep` (244), `wlow_bounce_bbrsi60` (109), `krown_malkan_g3` (178), `qriptal_scorecard` (9), and `orderflow_views` (144).
- `mfe_exit` has 1,048 rows: 82 `MATCH`, 966 `DIFF` (CSV lines 2052-3099).
- `published_strats` has no rows in this CSV; its non-rerun status remains separate from the count of exact rerun groups.

## Findings

| Severity | File:line | What is wrong | Evidence | Proposed fix |
|---|---|---|---|---|
| MED | `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T07/out/rerun_diff.csv:2-2051, 2052-3099` | An 8-of-10 exact-result count is not supported by the comparison rows. | The nine named groups above are all `MATCH` (CSV line spans: 2-71, 72-705, 706-1102, 1103-1367, 1368-1611, 1612-1720, 1721-1898, 1899-1907, 1908-2051); the remaining `mfe_exit` group is mixed (82/1,048), rather than wholly exact. | State 9 of 10 result groups exact; retain the separate note that `published_strats` was not rerun. |

No HIGH finding; no follow-up cards created.
