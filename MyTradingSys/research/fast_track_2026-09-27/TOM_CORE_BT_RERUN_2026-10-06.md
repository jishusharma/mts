# TOM CORE BT RERUN (current Java), run tom_core_20261007

Session: MTS-2026-10-07-1002Z-APP-BLD-research-closeout. Source: AUDIT_RERUNS_2026-10-06.md step 2.
Full generated report: TOM_CORE_BT_RERUN_2026-10-06_full.md (306 lines, same file the pipeline writes as TOM_CORE_BT.md).

## What was run
- Research worktree mts-research at 5334975 (origin/claude/project-thread-7gvyfy merged: 3fdf8cb HistoricalSource/ArchiveHistoricalSource/MarketDataSnapshot(Path)). SetupCandidatesBuilder as of that tree, i.e. after PR #12 (stop floor removed).
- Klines staged at F:\MTS\data\tom_raw\klines (89 files, raw_1m_2022 + raw merged, duplicates keep first).
- TomSnapshotGen (compiled in a %TEMP% copy, 3 shards, below-normal priority) into F:\MTS\data\tom_snapshots_2026-10-06: 57 months, 164257 evaluated, 0 errors, 15 min step, 2022-01-20..2026-09-26. A smoke directory F:\MTS\data\tom_snapshots_smoke (2026-09-01 only) is a leftover and can be archived.
- tom_bt_run.py rows / fabio / report with TOM_SNAP_DIR, TOM_RAW_DIR and a fresh TOM_WORK_DIR=F:\MTS\data\tom_bt_2026-10-07. Registry row appended: tom_core_20261007 (36 rows to date). Logs: BinanceDataFeed_backups/tom_bt_2026-10-07/.

## Result vs the previous run (TOM_CORE_BT.md before this run, backed up as TOM_CORE_BT.pre_rerun.md)
| | previous | this run |
|---|---|---|
| live rule SETUP_FORMING filled trades | 17 (19 signals) | 0 |
| WATCH+SETUP_FORMING episodes (proof >= 3, sensitivity), filled | 4417 | 2880 |
| mean gross R | -0.07 [-0.11, -0.03] | -0.15 [-0.29, 0.04] |
| mean net R | -0.30 [-0.34, -0.25] | -2.91 [-4.35, -1.89] |
| holdout 2026-06-26.. net R | -0.32 (n=254) | -2.80 [-4.77, -0.75] (n=181) |
| fee cost per trade | ~0.23 R | ~2.76 R |

Reading: no edge shown, same conclusion as before (gross at or below zero, fees negative). The change in net R is mechanical: PR #12 removed the 0.1% minimum stop floor (B116), stops are now very tight, so R is tiny and fees cost ~2.76 R per trade. The primary rule has 0 signals because the historical snapshots carry no book imbalance, funding, OI or basis, so proof tops out at 6 and SETUP_FORMING needs 5; that ceiling was the same last run, the 17 earlier trades are not reproduced on the current Java (not investigated). Nothing here selects or tunes a parameter.

## Tooling fixes made to get the run through
- tom_bt_report.py hashed staged `ArchiveHistoricalSource.java.new`, which 3fdf8cb promoted: crash (FileNotFoundError). Added adapter_line() preferring the promoted files; test backtest/test_tom_bt.py::TestReportAdapterLine.
- The report's narrative still says "staged .new" in section 1 (template text); not changed.

## Open
- Why the live rule dropped from 19 signals to 0 on the current Java: needs a diff of the verdict rows (F:\MTS\data\tom_bt vs F:\MTS\data\tom_bt_2026-10-07) by month. Not run.
- bt_runs/tom_core_20261007/ and the registry row live in the research worktree only (not pushed, not on fast-track).
