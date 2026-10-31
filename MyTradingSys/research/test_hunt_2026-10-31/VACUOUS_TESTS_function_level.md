# Vacuous-test audit (card sonnet-new-tests-must-fail-on-old-code-audit)

Method: newest 30 non-merge, non-revert commits (base 239f17a1f) that ADD a `*test_*.py` file. For each: detached worktree at the commit, every non-test file the commit touched restored to its parent state (added non-test files deleted), then only the new test file run (`pytest <file> -q -x`). Fails/errors = Y (test guards the change). Passes = N (vacuous on old code).
Repro: any row, e.g. `git worktree add --detach W <sha>; git -C W checkout <sha>^ -- <non-test files>; pytest W/<test>`.

| # | sha | test | fails on old? | note |
|---|---|---|---|---|
| 1 | 908cbb858 | MyTradingSys/tests/test_gemini_queue_lock.py | Y | 1 failed |
| 2 | e31013dfb | research/tf_break_event_study_2026-10-30/test_study.py | Y | import error (module absent) |
| 3 | 92aa0ab3d | tools/live_aid/test_live_aid_replay.py | **N** | 1 passed, 4 skipped on old live_aid.html; the one passing test does not exercise the change; 4 skipped (needs deps) |
| 4 | 2877e1fed | research/gap_g7_stop_slippage_2026-10-18/test_slippage.py | Y | slippage.py absent |
| 5 | a43b9fbff | research/setup_alpha_beta_v2_2026-10/test_beta_events.py | Y | error |
| 6 | 46cb4255e | backtest/test_splits.py | Y | error |
| 7 | 36f311c44 | scripts/dev/test_artifact_pages.py | **N** | 12 skipped (no headless Chromium here): cannot fail; unverifiable on this machine |
| 8 | 589685fbb | scripts/dev/test_cbp_run.py | Y | 1 failed |
| 9 | c409e3f6b | scripts/dev/test_where_is.py | Y | 1 failed |
| 10 | 1448911c7 | tools/live_aid/test_build_analyst_data.py | Y | error |
| 11 | 14f601e2c | scripts/dev/test_analyst_levels.py | Y | error |
| 12 | 2d7d4d49c | backtest/test_no_own_costs.py | Y | 1 failed |
| 13 | 792ae66b6 | scripts/dev/test_fix_verifier.py | Y | error |
| 14 | d3570f13b | tests/docs/test_operator_decisions_parse.py | Y | 1 failed |
| 15 | f20eeed04 | tools/test_us_open_alert.py | Y | error |
| 16 | 50b9036ff | scripts/dev/test_check_sourced_params.py | **N** | 9 passed; commit touches no code (retro spec test of existing check) |
| 17 | 5e37f0323 | scripts/dev/test_where_is.py | Y | 1 failed |
| 18 | 451545147 | tests/test_operator_questions_gaps.py | Y | 1 failed |
| 19 | 5e52c5540 | scripts/dev/test_deploy_untrack_backup.py | **N** | 15 passed; retro spec test, no code change |
| 20 | 108c58d8a | research/bb_state_map_2026-10/test_bb_state_map.py | Y | error |
| 21 | d585606e2 | scripts/dev/test_check_set_frames.py | **N** | 13 passed; retro spec test, no code change |
| 22 | 222976f9d | scripts/dev/test_coord_overhead.py | **N** | 9 passed; retro spec test, no code change |
| 23 | 1deae1acd | scripts/dev/test_tom_noise_units.py | **N** | 12 passed; retro spec test, no code change |
| 24 | 414a5e7d3 | scripts/dev/test_retention.py | **N** | 10 passed; retro spec test, no code change |
| 25 | 499d6fda4 | scripts/dev/test_station_disk_report.py | Y | error |
| 26 | 4209a07ba | research/sim_desk/test_page_top.py | Y | 1 failed |
| 27 | 771d07995 | scripts/dev/test_aibridge_version.py | **N** | 13 passed; retro spec test (its message claims 3/3 mutations caught, so not empty) |
| 28 | c6355a908 | scripts/dev/test_station_disk_report.py | Y | error |
| 29 | a97b86446 | item4_summarise.py, replay_prep_spot_days.py (research/critical_test_wave_1) | n/a | scripts matched by path, not tests (error: no module) |
| 30 | c511a40dc | item1_prefix_check.py, item2_settlement_identity.py | n/a | not pytest tests ("no tests ran"); matched by path only |

Summary: 30 commits, 19 Y, 9 N (7 retro spec tests of unchanged code, 1 fully skipped, 1 pass/skip on live_aid replay), 2 not tests. Retro spec tests cannot fail on "old code" by construction; for them the gate needs a mutation check instead (as 771d07995 did). Rows 3 and 7 are the real vacuity risks. Findings are listed here only; no cards filed (operator instruction).
