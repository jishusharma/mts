# Review request for Claude: ship pipeline changes 1-8 (commit 7a23bdd16)

Producer: gemini (Antigravity, JIS-NUC). Reviewer needed: Claude (independent, non-Gemini). Gemini does NOT stamp ACCEPT.
REVIEWED:2026-11-13 T0-ONLY

Source review: `MyTradingSys/system/SHIP_ARCH_REVIEW_2026-11-12.md`. Applied by `7a23bdd16`.

## Revalidation done (T0, mechanical)
- `pytest scripts/dev/test_gate_select.py test_gate_impact.py test_gate_reason_wait.py test_run_all_tests.py test_route_audit.py test_tasks.py`: 347 passed, 2424 subtests, 98 s.
- `sync.py ship --full` from this tree: "nothing to ship". Host health: `java` not on PATH, so Maven/Java steps cannot run on this host.
- Not run: full suite, Maven, CI. Not verified: the claims below marked UNVERIFIED.

## Findings / gaps (for Claude to confirm or reject, each with file:line)
1. 3gd removed from ship gate. Comment claims `run_extra_tests.discovered()` plus MyTradingSys/tests shards still catch an unregistered test file in CI. UNVERIFIED: confirm a new unregistered test file turns CI red (or is auto-run), otherwise B150 regresses.
2. `tasks.py lint --warn` returns 0 for ALL errors, not only Definition-of-Ready / review stamp: also "file name differs from id" and other structural errors. Review change 3 scoped only paperwork. Confirm the demotion is not wider than the operator's yes.
3. Live-path ships no longer run the full suite locally; fast live gate = fast gate + steps 1,2,3. Confirm steps 1-3 are must-pass in `apply_fast(live=True)` (supervisor-visible reason string `fast live: ...`), and that the `except` fallback in `apply_selection` still keeps mode `live` (not weaker).
4. Removed branch `new_plan is None -> full` (live code imports the change). Live-importing changes now run fast-live only. Matches review row 2 but is a reversal of a must-not-cut item from ARCH_REVIEW_2026-11-10: confirm operator's 11-12 yes covers it (OPERATOR_DECISIONS.md was edited in the same commit).
5. Change 7 (no per-ship LAYERS.md regenerate): git log still shows `ship: regenerated LAYERS.md` (2aa91f3f5) on the current history. Check whether that predates 7a23bdd16 or the change is incomplete.
6. Change 6 (test runs stop writing to wait.log): not seen in the diff of sync.py/run_all_tests.py. Verify.
7. `NEVER_STAGE_ROOT_SUFFIXES` drops any root `*.log`/`*.out`: confirm no tracked root file with those suffixes (e.g. an intended log) is now unstageable.
8. Host: java missing from PATH on this NUC; live-path Java edits cannot be locally validated here.

## Ask
Claude: review findings 1-8 one at a time against live repo state; reply with FIX / REWORK / ACCEPT stamp. Nothing here changes code.
