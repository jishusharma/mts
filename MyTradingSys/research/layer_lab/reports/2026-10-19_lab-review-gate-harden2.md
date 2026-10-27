# Review gate hardening 2: R2-R6

**DONE for R2-R6; R1 remains OPEN.** Review gates now block malformed class/note/weight types, normalize padded/case-varied weights, reject non-boolean live_path values, and require each textual review stamp to stay on one line. Flow completion converts review-gate exceptions into blocking errors. All tested close-path guards have independently biting tests; legitimate ready-to-done completion remains supported.

No trusted reviewer roster or stamp-writer authority was added. Free-text stamps still do not authenticate a reviewer; `lab-review-gate-stamp-writer` owns R1. No V1-V6 vendor-gate behavior, strategy/formula code, data, or outcomes were changed.

## Changes

Changed implementation pointers: `scripts/dev/tasks.py:640` (stamp grammars), `:817` (class parsing), `:856` (weight normalization), `:879` (blocking metadata validation); `scripts/dev/lab_flow.py:319` (shared close gate). Tests: `scripts/dev/test_tasks.py:578`, `:592`, `:608`, `:619`; `scripts/dev/test_lab_flow.py:474`, `:490`; `scripts/dev/test_lane_health.py:282`.

| Finding | Change / evidence |
|---|---|
| R2 malformed classes | `scripts/dev/tasks.py::card_class`: explicit malformed field values and note forms conservatively resolve to C3. Multiple class markers on one line are evaluated; a lower class cannot consume and hide a later higher class. Non-string metadata is a blocking review_gate error even with a syntactically valid receipt. |
| R3 weights and live_path | `tasks.py::needs_review` strips and uppercases string weights; non-string or unrecognized weights require review. `review_gate` explicitly blocks malformed types and unrecognized weight names even if a stamp is present. Non-boolean live_path values cannot bypass the live-path floor. |
| R4 independently biting tests | `scripts/dev/test_tasks.py::ReviewGateTest`: all seven producer identity fields tested separately in planner, legacy and structured receipts; valid reviewer with impossible date in each textual grammar; planner anchor; class field fallback/case; weight case/padding; each malformed metadata type with a review receipt. |
| R5 flow and DSA close paths | `scripts/dev/test_lab_flow.py::test_finish_review_gate_applies_to_ready_and_active` isolates the shared gate from other validators and verifies both states remain open on rejection. `lab_flow.py::finish` passes the selected repo and translates gate exceptions to ValueError. `test_finish_review_gate_exception_keeps_card_open` proves no completion on a broken gate. `test_lane_health.py::EndToEnd::test_lane_health_review_gate_errors_fail_closed` independently exercises the existing DSA exception branch; lane_health.py required no code change. Existing ready-to-done and blocked-state tests retained. |
| R6 multiline stamps | Both textual regexes use horizontal whitespace between stamp tokens, preserving a stamp beginning on its own line after a preamble while rejecting a stamp split over lines. |

## Validation and red-first evidence

Before product changes, added tests and ran:

```
python -m pytest scripts/dev/test_tasks.py scripts/dev/test_lab_flow.py scripts/dev/test_lane_health.py -q --tb=short
```

Baseline result: **34 failed, 148 passed, 463 subtests passed**. Failures reproduced malformed class/type/weight/live_path and multiline-stamp acceptance, plus the unwrapped flow gate RuntimeError. Existing guard-only tests (producer identity, valid-reviewer invalid dates, shared close gate and DSA exception branch) already passed; their adequacy is established by targeted guard-removal mutations, not a claim that working behavior was initially broken.

An additional red test found unrecognized weight `BOGUS` could still close with a valid stamp: **1 failed, 13 subtests passed** before adding explicit recognized-weight validation.

Final changed-file run: **150 passed, 495 subtests passed, 20.94 s**. `git diff --check` passed. Modified Python files have LF line endings. The first ship passed all 23 selected smoke steps but was blocked by existing Linux CI. After the named spawn-audit test repair, `sync.py ship --fix-ci` passed all 65 selected steps and shipped the changes. A separate local full-suite run also passed, including Maven; local Windows results do not substitute for Linux CI confirmation.

The named flow/DSA guard tests correctly passed baseline because those guards existed. The new flow-exception conversion test failed baseline. Tests were not weakened to force an artificial baseline failure on already-working guards.

## Mutation checks

On scratch copies only, copied `scripts/dev/*.py`, changed one guard at a time, ran the indicated focused test with `python -B -m pytest ... -q --tb=short -p no:cacheprovider`, and restored the scratch source after each run. Collection/import errors were classified INVALID, never as killed. The real worktree was not mutated.

| Guard removal/change | Matching test | Final result |
|---|---|---|
| producer, producer_model, vendor, model, worker, refined_by, author individually removed from identity lists (7 mutants) | test_each_producer_identity_independently_rejects_own_review | 7 KILLED |
| Planner and legacy date validation removed independently (2) | test_dates_anchors_case_and_single_line_independently | 2 KILLED |
| Planner line anchor removed | same | KILLED |
| Planner and legacy regex horizontal whitespace replaced with newline-spanning whitespace (2) | same | 2 KILLED |
| Class-field uppercase normalization removed | same | KILLED |
| Malformed class field fallback C3 changed to C0 | test_malformed_note_class_fails_closed | KILLED |
| Note class-marker processing removed | same | KILLED |
| Weight uppercase normalization removed | test_dates_anchors_case_and_single_line_independently | KILLED |
| Weight strip removed | test_weight_and_live_path_malformed_values_fail_closed | KILLED |
| Malformed metadata type blocking error removed | same | KILLED |
| live_path type blocking error removed | same | KILLED |
| Unrecognized weight blocking error removed | same | KILLED |
| Shared flow finish review_gate call removed | test_finish_review_gate_applies_to_ready_and_active (ready and active) | KILLED |
| Flow finish ready/active state restriction removed | test_flow_card_finish_refuses_other_states | KILLED |
| Flow gate exception conversion replaced with gate=[] | test_finish_review_gate_exception_keeps_card_open | KILLED |
| DSA gate exception branch replaced with gate=[] | test_lane_health_review_gate_errors_fail_closed | KILLED |

**Final: 24/24 mutants killed, zero invalid, zero surviving.** The first mutation run had two survivors: removing weight uppercase or strip was masked by the unknown-weight hard-review fallback. Direct soft-review assertions for `important` and ` IMPORTANT ` were added; both formerly surviving mutants then failed independently. No surviving mutant is represented as resolved without a failing matching test.

Local scratch harness command: `python F:/codex_home/tmp/mutation_harden2.py`; final 23-guard result log is under `%TEMP%/mts-review-mutations-rbzjex6w/results.json`; the additional recognized-weight guard is under `%TEMP%/mts-review-mutations-i8s_9pzo/results.json`. These local paths are diagnostic aids, not required production inputs.

## Limitations and delivery

This closes the scoped R2-R6 implementation/test gaps, not R1 identity authority, future-date policy, arbitrary receipt authentication, or unrelated vendor-gate findings. Source edits are limited to tasks.py and lab_flow.py; three existing test modules were extended. The report and task bookkeeping are the only other changes.

The executor's separate delivery receipt records the content commit SHA, verifies empty `git cherry origin/fast-track <sha>`, and verifies the report exists in upstream `git ls-tree`. No self-referential commit SHA is embedded here.
