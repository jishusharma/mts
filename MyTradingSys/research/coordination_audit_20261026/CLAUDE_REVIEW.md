# Claude independent review of coordination_audit_20261026/REPORT.md

Reviewed on trunk head f02dc2fa4 (audited ec00608e9 plus later commits touching scripts/dev: none of them change the code paths below). Review only, no code changed.

## Reproduction run
`python MyTradingSys/research/coordination_audit_20261026/reproduce.py` on this NUC: exit 0, 12 of 12 demonstrations assert their defect (keys: fetch_does_not_refresh_dispatch, racing_claims_both_succeed, tasks_misses_side_claim, dispatch_bypasses_stop_tag, failed_ship_emits_done, green_completion_not_watched, uninvoked_tool_passes_wiring, gemini_full_id_release_mismatch, ship_wall_excludes_ci_wait, fast_gate_missing_from_supervisor, timeout_cached_as_pass, worker_brief_drops_context_contract). Direct run of `scripts/dev/test_supervisor.py`: first failure `test_pick_cards_jis_nb_lane_follows_the_live_host_file` (test_supervisor.py:446), as reported. Limit: the 73/268 suite counts and the CI run numbers were not re-run (no network use); only the failure above was re-checked.

## Verdicts
| # | Verdict | Proof (file:line, evidence key) |
|---|---|---|
| 1 | ACCEPT, narrowed | `push_claim_commit` (sync.py:1232) refetches the tip and rebuilds the commit on each rejected push but never re-validates. `claim()` (sync.py:1308) does re-check on its own loop, but only before the push. The overwrite is certain when both racers use the same slug (same file path in the tree); with different slugs and overlapping `--area` both files land (no overlap re-check). `racing_claims_both_succeed`. Smallest fix: inside the push loop, if `rel` already exists in the fetched parent with another owner, or an area overlap appears, raise instead of committing. |
| 2 | ACCEPT (A, B, C all hold) | A: `tasks.open_claims` (tasks.py:522) reads only `origin/fast-track` while claims live on `origin/claims`; `tasks_misses_side_claim`. B: `_dispatch_raw` uses `tasks.load_all(repo)` on the worktree files (supervisor.py:101), fetch does not update them; `fetch_does_not_refresh_dispatch`. C: `stop_tag` is applied in `tasks.py next` (tasks.py:782) but not in dispatch (tasks.py:1500) or codex_run; `dispatch_bypasses_stop_tag`. Counts (54 vs 3, 8, 21) are not re-measured, treat as the audit's snapshot. |
| 3 | ACCEPT | `_probe_wait_state` (supervisor.py:386) returns only on_trunk, ci_red and slot counts: `on_green` is read (supervisor.py:88) then dropped, no eligible-set or signal input. `_gate_slots_raw` (supervisor.py:195) counts the default pool only; `fast_gate_missing_from_supervisor` shows actual 1, seen 0. `green_completion_not_watched`. |
| 4A | ACCEPT, ALREADY CARDED | `auto_send_text` keys on the command text (mts_signal.py:408 verb == ship); `failed_ship_emits_done`. Existing card `ship-signal-send-done-only-on-a-complete` (refined) covers it exactly: build that, do not open a new one. |
| 4B | ACCEPT | `exec_step` returns True on timeout when TIMEOUT_DEFERS (run_all_tests.py:235); the print and `save_record` treat it as PASS and reusable. `timeout_cached_as_pass`. Note: DEFERRED for a gate-file ship is deliberate; only the recording is wrong. |
| 4C | ACCEPT | `record_ship_wall` runs in `ship()` finally (sync.py:1056), before `wait_own_ci` in main (sync.py:1715); `ship_wall_excludes_ci_wait`. The ok flag in the finally path is not the verdict. Card `bug-session-handoff-ship-speed-audit` (refined) is the home for the timer fix. |
| 5A | ACCEPT as observation, LOW | `uninvoked_tool_passes_wiring`: the wiring check is an inventory, not behavior proof. Cheapest value is the integration tests in 5B/5C; do not rework wiring_scan. |
| 5B | ACCEPT, confirmed failing now | `test_supervisor.py` is excluded from the gate by test_gate_discovery_b150 and fails on trunk. Stale host-alias expectation, not a live routing bug (not verified beyond the test). Restoring it to CI is a small card. |
| 5C | ACCEPT in part | The `\bgit log\b` ban exists (tests/docs/test_integrity.py:48). The three CI run ids were not fetched here, so the "all three failures" claim is UNVERIFIED. Replace by testing the real invariant; low priority next to 1-4. |
| 6 | ACCEPT | `worker_brief_drops_context_contract`: `supervisor.brief` (supervisor.py:589) builds goal and scope only; `tasks.brief` (tasks.py:458) has the context. Cheapest fix: have `supervisor.brief` call the tasks.brief renderer for the card body. Counts of folded cards and the context baseline are the audit's and were not re-derived; the report itself says no improvement is yet shown. |
| 7 | ACCEPT | `gemini_queue.run_job` releases the full card id (gemini_queue.py:96) while `slugify` truncates to 40 (sync.py:1181); `gemini_full_id_release_mismatch`. The return code of the release is logged only. The review-handoff mismatch with SUPER_SESSION.md was not re-read; treat as UNVERIFIED. |

No finding is REJECTED and none is ALREADY FIXED on current trunk.

## Repair order review
Agree with 1-2 first, then 3-4, then 6, with 5 riding along. Adjustments (DECISION, OURS):
1. Do the cheapest part of 2 first: make `tasks.open_claims` call `sync.open_claims` (the one canonical reader). One function, removes the 54-vs-3 gap for next, dispatch and codex; no design needed.
2. Finding 1 fix is a few lines inside `push_claim_commit` (refuse if the claim path exists with another owner or areas overlap, then let `claim()` re-run its check). Release by token is optional; compare owner fields on release first.
3. Finding 7 release mismatch is a one-line `slugify(card)` fix: ship it with step 1, do not wait for the receipt redesign.
4. Reuse cards: `ship-signal-send-done-only-on-a-complete` (4A), `bug-session-handoff-ship-speed-audit` (4C), `tandem-dispatch-host-lanes` and `dispatch-a-critical-crucial-blocker-outr` (same file set as finding 2C, one editor per file), `q17-p4-bookkeeping-out-of-git` (claim storage, touches finding 1), `gemini-laptop-open-questions` (gemini_queue.py). New cards are needed only for: claim push-loop validation (1), single claims reader (2A), snapshot reads from pinned trunk (2B), watcher probe inputs (3), DEFERRED as its own result (4B), supervisor.brief using tasks.brief (6), restore test_supervisor in CI plus alias fix (5B).

## Missing end-to-end requirements
- The A builds, B reviews, C consumes scenario needs one deterministic two-clone test as the acceptance gate; the audit lists it but no card owns it.
- A claim-token or owner check on release is only useful if stale-claim release (`STALE` hints in `sync.py start`) stays a human or coordinator decision; keep the rule that age alone never transfers ownership.
- Findings 3 and 4 depend on the claims move to origin/claims being final (q17-p4); decide that before changing the watcher probe, or it will read the wrong ref again.
