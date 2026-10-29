# Fix verification report, 2026-10-28

Trunk tested: `e50d547a9`. CI: last 5 runs green.

**Result: 20 PASS / 3 FAIL / 1 CANNOT TEST (CT-1..CT-3 listed below; three further fail-first checks not done).**

## FAIL (3)

| # | Item | Finding | Card |
|---|---|---|---|
| a | `wiring_scan.py --check` (after eb305a9f0) | Prints `WARN NO-READER` for `api_batch.py` and `operator_material_index.py` (both added after eb305a9f0). | fix-wiring-no-reader-api-batch-omi |
| b | Analyst scorecard (37742aa6e) | Store on JIS-NB: Michael 5, Jason 2, Krown 4, Qriptal 1, Michaal 1, tradable 1 (Qriptal). SCORECARD says 0 for all. Michael vs Michaal (spelling or two analysts) must be resolved. | scorecard-recount-jis-nb-store |
| c | aae5cdc90 | Message claims "2 design notes blocked", but no card in the diff moves to blocked. | name-or-retract-2-design-notes-blocked |

## CANNOT TEST (CT-1..CT-3)

| # | Item | Why not tested | Card |
|---|---|---|---|
| CT-1 | Real successor wake fires (0e07b7418, 3a1c8003b, fa094a92b) | Tests are dry/stub; the real path registers a Windows scheduled task. | successor-wake-real-path-test |
| CT-2 | Two concurrent `gemini_queue` claimers (2e5ada03f) | Push is mocked, so the race is not exercised. | gemini-queue-two-process-race-test |
| CT-3 | Full `run_all_tests.py` | Over the 5 minute verifier budget. | run-all-tests-full-worker-run |

Also not done: fail-first check (new tests must fail on pre-change code) for commits 37742aa6e, 02b9db8db, c50c6191d. Card: failfirst-check-37742aa6e-02b9db8db-c50c6191d.

## PASS (20 rows in the verifier's run; 17 groups listed)

| Item | Commit(s) | Check |
|---|---|---|
| Plan under 60 s | 33ddfe6bb | PASS |
| bg_watch | e1ac77891 | PASS |
| gemini_queue unit tests | 2e5ada03f, a544be7e4 | PASS (unit only, see CT-2) |
| successor_wake dry run | 0e07b7418 family | PASS, 13 tests (dry only, see CT-1) |
| supervisor handover wake | n/a | PASS, 70 tests |
| Wiring audit code | eb305a9f0 | PASS (see FAIL a for later files) |
| is_tradable direction | 37742aa6e | PASS (see FAIL b) |
| run_all_tests step 3g | 02b9db8db | PASS |
| Super session log cap | c50c6191d, ce0b4b3ee | PASS |
| Planner refinements | aae5cdc90, cac015cdb | PASS (see FAIL c) |
| Sim desk backfill | e6b0853f0 | PASS |
| verify_extract_quotes | cc3147641 | PASS |
| DSA gateway_owner | 26edaadab | PASS |
| Divergence flags | b39401fca | PASS |
| Signed funding | 3d8722a93 | PASS |
| Sync tests | 8fce9ee1f | PASS |
| api_batch | 64b0df558 | PASS |

Note: the verifier counted 20 PASS; the source list names 17 groups (some groups hold several checks). The exact 20-row split was not supplied to this report.

## DECISION (OURS)

Card ids and lanes are chosen by the report writer; lanes follow the operator's model hints (Haiku mechanical, Sonnet for tests/recounts).
