# Gemini supervisor wait watcher cross-review

**Verdict: FIX-FIRST.** The three requested `watchcheck` failure cases and an extra live-marker case returned the expected exit codes. The documented transition and fail-closed behavior maps to existing tests, but two integration details have no direct automated test in `test_supervisor.py`.

## Behavior-to-test map

I reviewed `scripts/dev/supervisor.py:443-600` against `scripts/dev/test_supervisor.py`. **12 behavior rows; 3 NO TEST rows.** Test references name the tests that exercise the behavior; component-reader tests are not treated as coverage for the `_probe_wait_state` integration itself.

| Behavior stated in comments/docstrings | Source | Test in `test_supervisor.py` | Result |
|---|---|---|---|
| Probe combines trunk/green SHA state, CI state, gate slots, and background stalls into one wait snapshot; a failed bg-watch probe becomes unknown (`None`) | `supervisor.py:443-460` | **NO TEST** for `_probe_wait_state` integration. Component readers are covered by `test_sha_on_trunk_and_green:17`, `test_ci_red_and_green:69`, `test_gate_slots_busy_count:93`; none calls `_probe_wait_state` | Gap |
| Stalled background task state can cause a new wake transition | `supervisor.py:453-460, 515-547` | **NO TEST** that patches `bg_watch.stalled()` and verifies its value reaches the watcher transition. Existing transition tests use caller-supplied probe dictionaries | Gap |
| After two plans with free slots but no new worker, stop the actionable wake loop | `supervisor.py:461` | `test_wait_actionable_fails_closed_and_stops_after_plans_that_spawn_nothing:598-615`; `test_plan_counts_a_wake_that_started_none_of_its_new_workers_as_stuck:706-717` | Covered |
| A plan older than 60 minutes is treated as another run and ignored | `supervisor.py:462, 465-467` | `test_wait_actionable_fails_closed_and_stops_after_plans_that_spawn_nothing:598-615`; `test_plan_counts_a_wake_that_started_none_of_its_new_workers_as_stuck:706-717` | Covered |
| Actionable wake requires a fresh NORMAL/SPEND plan, spare slot, more ready cards, no stuck-limit hit, green CI, known gate counts, and a free gate | `supervisor.py:470-490` | `test_wait_wakes_on_a_free_slot_with_ready_cards_not_after_50_min:590-595`; `test_wait_actionable_fails_closed_and_stops_after_plans_that_spawn_nothing:598-615` | Covered |
| Damaged plan data does not wake or crash the watcher | `supervisor.py:480-483, 505-513` | `test_a_damaged_plan_file_never_wakes_and_never_kills_the_watcher:774-784`; `test_a_damaged_last_plan_never_breaks_the_next_plan:732-737` | Covered |
| Missing or garbled per-login wake marker reads as empty, leaving the watcher alive | `supervisor.py:489-494` | `test_garbled_marker_files_never_kill_the_watcher_or_the_plan:797-802`; `test_one_actionable_wake_per_plan:754-763` exercises an initially missing marker | Covered |
| A watcher restart cannot emit the same actionable wake twice for one plan | `supervisor.py:496-503` | `test_one_actionable_wake_per_plan:754-763` | Covered |
| SHAs already landed at baseline do not wake; a newly landed SHA does; CI flips wake | `supervisor.py:515-535` and wait loop | `test_wait_sha_already_on_trunk_at_baseline_does_not_exit_until_new_sha_lands:163-194`; `test_wait_ci_flips_false_to_true_and_true_to_false:196-222` | Covered |
| A gate slot freed after baseline wakes, while a steady or rising slot count does not | `supervisor.py:537-547` | `test_wait_busy_slot_frees_transition:225-243`; `test_wait_wakes_when_a_ship_that_started_during_the_watch_frees_its_gate:245-258` | Covered |
| PID check must be non-destructive on Windows and only treat a process as live when its handle reports STILL_ACTIVE | `supervisor.py:554-574` | **NO TEST** calls the real `_pid_alive`; watchcheck unit tests inject an `alive` callback | Gap; manual CLI check below did exercise this Windows path |
| `watchcheck` returns 0 only for a live, unexpired watcher marker and returns 4 for absent, expired, or dead-pid markers | `supervisor.py:576-590` | `test_watchcheck_no_marker_exits_4:849-852`; `test_watchcheck_live_watcher_exits_0:854-858`; `test_watchcheck_dead_pid_exits_4:860-864`; `test_watchcheck_expired_marker_exits_4:866-870` | Covered |

## `watchcheck` CLI results

Ran `python scripts/dev/supervisor.py watchcheck --login B` in subprocesses with a fresh `MTS_RELAY_HOME` for each case. Marker files were written only in those scratch homes.

| Case | Expected | Exit code | Result |
|---|---:|---:|---|
| No marker | 4 | 4 | Match |
| Expired marker | 4 | 4 | Match |
| Future marker with nonexistent PID 2147483647 | 4 | 4 | Match |
| Future marker with this live audit process PID | 0 | 0 | Match |

## Findings

| Severity | File:line | Evidence | Proposed fix |
|---|---|---|---|
| MED | `scripts/dev/supervisor.py:443-460` | No automated test checks that `_probe_wait_state` combines component reads or fails closed to `stalled=None` on bg-watch import/read errors. | Add a focused test with patched source readers and `bg_watch.stalled()` to assert the snapshot fields and error fallback. |
| MED | `scripts/dev/supervisor.py:453-460, 515-547` | No automated test checks that a newly stalled background task propagates from `_probe_wait_state` to `TRANSITION STALLED-BG`. Existing watcher tests pass prebuilt probe snapshots. | Add an integration-style unit test that patches `bg_watch.stalled`, calls the real probe, then verifies a transition from the resulting snapshot. |
| MED | `scripts/dev/supervisor.py:554-574` | The four watchcheck tests inject `alive`; none covers the actual platform helper. The live/dead CLI checks passed on this Windows host, but the Windows PROCESS_QUERY_LIMITED_INFORMATION / STILL_ACTIVE behavior has no regression test. | Add a Windows-specific test around `_pid_alive` that verifies the limited query and handle close without terminating the process. |

The card requires a task for HIGH findings only; all three gaps are MED, so I filed no follow-up card. No code changes or product test suite runs were made.

