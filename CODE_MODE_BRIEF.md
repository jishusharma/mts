> **SUPERSEDED (2026-10-08).** One-off FIX3 batch brief from 2026-09-28. Current rules: CLAUDE.md. Its "never run testnet suites / never push" lines applied to that batch only.

# Code-mode brief (written 2026-09-28 03:20 IST by the Opus coordinator session)

You are working natively on Windows in C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed (use `python`, PowerShell 7).

## Operator rules for this mode (approved 2026-09-28)
- You MAY commit, but ONLY to branch `fast-track` (create it from main if missing: `git switch -c fast-track`), one commit per batch, ONLY after the gate below passes.
- Never commit to main, never push/merge/rebase/reset, never delete history.
- Never run anything that contacts an exchange (no testnet/mainnet suites, no probe scripts). Those are the operator's.
- Never read secrets/.env/keys.
- For git: `*.new` is gitignored. When a batch passes the gate, PROMOTE on the branch: back up live file as <file>.pre_fix3, rename .new -> live, re-run the gate on the promoted tree, then commit.

## Batch 1: FT-2 fixes (FIX3)
Inputs: MyTradingSys/research/fast_track_2026-09-27/review/ADVERSARIAL_REVIEW_FT2.md (+ repro_ft2.py) and review/MUTATION_REPORT_FT2.md.
Fix (smallest change each): C1 transport errors on order-creating calls -> OrderStateUnknown (reads -> DeribitError after retries); C2 poll-loop read failure -> fail_closed; C3 flatten order = cancel entries/targets -> close position -> cancel stop LAST (keep stop if close fails), in executor.fail_closed and position_manager.flatten_halt; H1 per-cancel catch Exception, flatten always runs; H2 kill_switch writes HALT first, survives get_positions/authenticate failure; H3/H4 daily_loss_monitor writes HALT_DAILY_LOSS before/regardless of kill_all, atomic state write (tmp + os.replace), unreadable state -> fail closed; H5 failed stop-state READ never triggers re-place; H6 FT-2 suite uses temp HALT/state paths; M1/M3 HALT_DAILY_LOSS read utf-8-sig then utf-16, any parse/date error -> refuse; M5 flatten+halt also writes manual HALT; M6 preflight refuses plan_id > 24 chars or outside [A-Za-z0-9_-].
Add offline tests for every fix + the 13 mutation survivors -> MyTradingSys/execution/testnet/offline/test_fix3_offline.py.

## Gate (must all pass)
python scripts/dev/run_staged_tests.py MyTradingSys/execution MyTradingSys/execution/testnet/offline -- test_daily_loss_guard test_daily_loss_monitor test_gh_executor_offline test_gh_retry_offline test_halt_preflight_offline test_kill_switch test_risk_guard test_s1_cap_offline test_s3_unprotected_offline test_s6_orphan_offline test_soak_report test_fix3_offline   (baseline 68 OK)
python scripts/dev/run_staged_tests.py MyTradingSys/execution MyTradingSys/execution/testnet/offline --script test_g1g2_offline.py --fake fake_deribit_orders.py=deribit_orders.py   (12/12 PASS)
review/repro_ft2.py against the staged sandbox: no fixed finding reproduces.

## Batch 2 (after batch 1 is committed)
Promote + commit on fast-track: the rest of the FT-2 batch per MyTradingSys/research/fast_track_2026-09-27/FT2_RUNBOOK.md promotion table, scripts/worker/queue_tool.py.new, MyTradingSys/backtest/bt/BT_BUILD_NOTES.md.new. Then NUC task 019 (`python scripts/worker/queue_tool.py verify 019-ref-pbo`) + compare ref_pbo.iid_noise_experiment() vs bt_stats.pbo_cscv on iid noise (T=320,N=10,S=8, 50 seeds); is the (0.2,0.8) test band justified?

## Finish
Write MyTradingSys/research/fast_track_2026-09-27/FIX3_REPORT.md: each finding FIXED/NOT FIXED, test counts, repro results, commits made, PBO result, and exactly what the operator runs next on testnet (FT2_RUNBOOK.md steps).
Status/background: project docs claude/FAST_TRACK_STATUS_2026-09-28.md and claude/FT1_GATE_REVIEW_2026-09-28.md.
