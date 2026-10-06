# MTS-2026-10-03-1314Z-CLI-BLD-tf2-per-source-live
surface: CLI | role: BLD | model: claude-sonnet-5-5 | branch: fast-track | lanes: none | status: closed
reason for CLI: App session not available to this run; repo and child processes reached from CLI.

## T0 contract (quoted)
- BUILD_PIPELINE.md:43 "| 1.4 | TF2 | per-source live funnel report (alert to exit) | QUEUED | ... new read-only scripts/dev/funnel_report.py over execution/auto_trades.jsonl, execution/trade_ledger.jsonl, runtime/alerts"
- BUILD_PIPELINE.md:85 "scripts/dev/funnel_report.py: per-source funnel from auto_trades.jsonl + trade_ledger.jsonl + runtime/alerts (read-only, L4)"
- TOM_FABIO_REVIEW_2026-10-03.md:66 "| L4 Testnet funnel | ... | alert -> verdict -> attempt -> fill -> exit, per source, daily | ... | funnel report daily; n >= 30 filled per core before any edge claim |"
- Current behaviour: scripts/dev/funnel_report.py did not exist (glob empty).

## Built
scripts/dev/funnel_report.py (read-only, stdout), scripts/dev/test_funnel_report.py (5 tests), gate step 3f in run_all_tests.py.
Not a live-imported file: no .new staging needed.

## Gate
test_funnel_report.py fails with ModuleNotFoundError when the script is absent; passes with it.
run_all_tests.py --quick: ALL TESTS PASSED.

## Deviations
1. No Build-Check (area is scripts/dev only). Maven/backtest skipped by --quick.
2. Alerts have no key field and no Tom rows (Tom source has no runtime/alerts rows), so alerts are counted per layer source and day of t_close, not joined by key. Tom shows alerts 0.
3. Ledger cohorted by alert_ts day, auto_trader verdicts by ts day; no per-alert join.
4. Untracked MyTradingSys/execution/pm_heartbeats/ and runtime/orderflow_live changes are not mine; left unstaged.
