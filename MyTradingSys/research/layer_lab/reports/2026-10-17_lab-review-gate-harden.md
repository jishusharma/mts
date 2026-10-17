# BLOCKED — lab-review-gate-harden

The in-scope review gate is hardened and its changed test file passes. The card remains BLOCKED because finding 5 names `scripts/dev/lane_health.py` as a close path that must honor the gate, while the card's explicit scope permits edits only to `scripts/dev/tasks.py`, `scripts/dev/test_tasks.py`, and `scripts/dev/lab_flow.py`. Closing that path requires an out-of-scope edit; per the task instruction, this report records the exact reason and the card is not marked done.

## Changed files

- `scripts/dev/tasks.py:557` — planner and legacy stamps must begin a note line; dates are parsed as real calendar dates; placeholder reviewer identities and identities matching producer/model/vendor/worker fields are refused. Existing planner ACCEPT/T0-ONLY grammar is retained.
- `scripts/dev/tasks.py:585` — class severity takes the highest value across the card field and note. Malformed class forms fail closed at C3; live-path remains C3.
- `scripts/dev/tasks.py:673` — `done` requires active state and applies the hard review gate. `scripts/dev/tasks.py:722` — `sweep --apply` applies the same gate before closing a hard card.
- `scripts/dev/lab_flow.py:280` — flow finish checks the shared review gate; PASS requires active state.
- `scripts/dev/test_tasks.py:555` — forged stamps (placeholder, producer, self, invalid date, quoted mid-note), class downgrade/malformed class, whitespace receipt, active-state close, and sweep close regressions.

## Red then green

- Red first, before implementation: `python -m unittest scripts.dev.test_tasks.ReviewGateTest.test_forged_stamp_forms_are_rejected scripts.dev.test_tasks.ReviewGateTest.test_class_field_cannot_downgrade_note_class scripts.dev.test_tasks.ReviewGateTest.test_whitespace_receipt_is_rejected` — **FAILED**, 6 failures: all forged forms and class-field downgrade were accepted; whitespace receipt already rejected.
- After implementation: `$env:PYTHONPATH='F:/MTS/mts-codex-lab'; python -m unittest scripts.dev.test_tasks` — **OK**, 66 tests.
- `python scripts/dev/lookahead_lint.py --new` — **217 hits: 190 FAIL (190 allowlisted, 0 new), 27 WARN (22 allowlisted, 5 new), 0 stale allowlist rows**. No new FAIL hit on changed files.

## Tip checks

- Finding 2: `tasks.py:557` accepts the planner `REVIEWED:<date> ACCEPT` grammar; existing `test_t0_only_stamp_is_not_a_review_for_crucial` and promotion tests cover ACCEPT vs T0-ONLY.
- Finding 3: `tasks.py:585` sets `live_path: true` to C3; existing `test_planner_class_format_and_live_path_floor` covers the floor.
- Finding 5 remaining: `scripts/dev/lane_health.py:317` directly writes `state="done"` without the shared gate. That path is outside this card's declared scope, so the all-close-path objective is incomplete.

No follow-up card was created because this unattended task has no authority to expand its scope. The runner must not treat this card as complete until `lane_health.py` is added to scope and gated.