# CI fixture race repair

Source: [failed multiplicity-commit CI run](https://github.com/jishusharma/mts/actions/runs/40382326578), GitHub check annotations for Windows shard 9/12 and Ubuntu shard 2/3. Windows failed TestExtraTestsRunConcurrently because a 0.1-second sleep observed peak concurrency 1. Ubuntu failed SyncTest.setUp copying a disappearing .git/objects/maintenance.lock from the shared template. Neither failure involved changed research output.

Changes: scripts/dev/test_run_all_tests.py uses a two-party Barrier instead of elapsed sleep to prove overlapping workers; scripts/dev/test_sync.py disables automatic GC and maintenance only in its temporary origin/clones before fixture commits/pulls. User Git config and application code are unchanged. No locks are ignored or errors suppressed.

Fail-first: new test_fixture_repositories_disable_background_git_maintenance ran against the old fixture and failed for all three repos (missing local gc.auto). After the fixture fix, both entire affected modules passed: 183 tests and 3 subtests, 158.12 seconds. A scratch serial-worker mutation of run_files is rejected by the concurrency test with BrokenBarrierError; the probe shortened its barrier timeout to 0.05 seconds, leaving real code unchanged.

Validation command: pytest on scripts/dev/test_sync.py and scripts/dev/test_run_all_tests.py with a fresh temporary directory on F:/MTS for TMP/TEMP and pytest basetemp. No live tree, account data, external repo or production services were used. Claim: ci-fixture-concurrency-maintenance. CI result after push must be checked separately; a local pass alone is not CI-green evidence.
