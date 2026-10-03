# MTS-2026-10-03-1059Z-CLI-BLD-tf1-gate-fabio-v3
surface: CLI | host: JIS-NB | account: none | model: claude-sonnet-5-5 | role: BLD | branch: fast-track | branch_alias: none
predecessor: none | lanes: none (no subagents, no workers)
started: 2026-10-03 | ended: 2026-10-03 | status: closed | commits: e1d5eac
handoff: row 1.3 LANDED; unblocks 1.9 (TF7) and 1.10 (TF8).

## Scope
Gate Fabio v3 tests, test_orderflow_live.py, test_htf_context_live.py in scripts/dev/run_all_tests.py (review E7).
No live-imported file edited; no process stopped; no HALT or trade touched.

## T0
- run_all_tests.py step 5b (unittest, rglob layers) already imported these modules but ran 26 of 119 tests;
  the rest are pytest function-style and were never collected. Step 4 (pytest) did not list them.
- BUILD_PIPELINE.md:42 row 1.3 QUEUED; TOM_FABIO_REVIEW_2026-10-03.md:51 E7.

## Change
- run_all_tests.py: PYTEST_LAYER_PATHS (3 paths) appended to step 4 pytest; new step 3g runs
  scripts/dev/test_run_all_tests.py.
- scripts/dev/test_run_all_tests.py: 2 tests (paths cover v3 + both live-writer tests; paths exist).

## Proof
- Fail-before: test against HEAD run_all_tests.py: FAILED (failures=1).
- pytest on the 3 paths: 119 passed. run_all_tests.py --quick: ALL TESTS PASSED (step 3g, 4, 5b PASS).

## Deviations
- Surface CLI (task named App): this run was launched as CLI session; no App-specific blocker recorded.
- Register row = pipeline row 1.3 (no BUGS row exists for TF1).
- Existing step 5b unittest overlap (26 tests) left in place; harmless double run.
