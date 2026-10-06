# MTS-2026-10-03-1845Z-CLI-BLD-b070-demote-utc-00
surface: Win App code mode
host: JIS-NB
model: claude-sonnet-5-5
role: BLD
branch: fast-track
lanes: none (no subagents)
started: 2026-10-03 18:45Z
status: closed
commits: the commit with trailer MTS-Session: MTS-2026-10-03-1845Z-CLI-BLD-b070-demote-utc-00

## Scope
B070 (pipeline 4.1). Operator ruling (a), 2026-10-04: friction = fee model from backtest/fees.py; UTC 00:00 anchor display-only.

## Done
- net_rr = (|target - entry| - 2*taker*entry) / (|entry - stop| + 2*taker*entry), taker 0.0005 (FORMULAS.md section 17).
  Python: mts_math.calculate_net_rr(entry, target, stop), math_object_builder.py. Java: ExecutionMathConstants.netRR,
  SetupCandidatesBuilder, ExtraSetupBuilder. Parity: tests/test_b070_fee_parity.py.
- MarketDataSnapshot.buildCvd(sessionBars, rollingBars): value = session CVD (display); slope, last_3_delta, cvd_recent from rolling 1m.
- Promoted with .pre_b070 backups (6 files). None is imported by auto_trader, position_manager, daily_loss_monitor or live_runner_cli.
- Gates: run_all_tests.py --quick PASS; mvn -o test in a temp copy with the new sources: 47 run, 0 failed.
  New tests fail on the old code (9 Python failures against the unpromoted runtime; Java tests do not compile against the old API).

## T5 deviations / handoff
- The floor 1.25 (net_rr_floor.json) is unchanged but now applies to a different net: tight stops cost more R (stop 0.1% away: net = 1.0 at gross 3.0). Expect fewer candidates; operator may revisit the floor.
- Supervisor: rebuild the jar and restart the Java feed; until then the live Java emits old net_rr while Python recomputes with the fee model.
- StateCodeEmitter.java (session_cvd, UTC ring reset) untouched: no verdict reader found (grep of runtime/execution/scripts), it is a live process.
- start-trading-day.ps1 reads conditions.cvd_slope (now rolling) - no edit needed.
- Research harness core_invariants.py I01 updated to the fee model. Old-formula docs (MISSING_PIECES, PROVENANCE_AUDIT) left as history.
- BUILD_PIPELINE.md carries another session's uncommitted row 1.11; only the 4.1 hunk is staged.
- Maven step skipped by --quick; ran separately in a temp copy. Existing files are CRLF in the working tree, written LF (index is LF).
