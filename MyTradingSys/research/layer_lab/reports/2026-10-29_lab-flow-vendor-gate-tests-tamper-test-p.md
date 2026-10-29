52 passed: vendor gate tests pass; tamper and empty receipt mutants are killed.

## What was checked

- Read `scripts/dev/lab_flow.py` (receipt check at 150-161; normalized card-vendor and producer-vendor guards at 212-217) and `scripts/dev/test_lab_flow.py` (stage-3 and vendor mutation tests at 171-247).
- `python -m pytest scripts/dev/test_lab_flow.py -q` — 52 passed (one pytest cache warning).
- Isolated scratch mutation of `lab_flow.py:212`: removed the normalized allowlist diagnostic. `test_v5_mutant_gate_normalized_allowlist_card_vendor_check` failed because the exact required message was absent (1 failed).
- Isolated scratch mutation of `lab_flow.py:158`: changed empty receipt vendor fallback to expected vendor. `test_accepted_rejects_empty_receipt_vendor` failed because `accepted()` returned True (1 failed).

## Findings

| Severity | File:line | Finding | Evidence | Fix |
|---|---|---|---|---|
| MED | `scripts/dev/test_lab_flow.py:214-227` | Tamper test requires the exact normalized allowlist diagnostic. | Mutant removing the diagnostic: test failed; broad `drifted` alternative is absent. | None. |
| MED | `scripts/dev/test_lab_flow.py:183-211,230` | V5 tests exercise `F.launch` or `F.gate`, so they observe the actual gate path. | Mutation record below; 52-test suite passes. | None. |
| MED | `scripts/dev/test_lab_flow.py:171-180` | Stage 3 matching its stage-1 producer is refused; stage 3 matching stage 2 remains covered as accepted. | Producer-vendor restriction is at `lab_flow.py:217`; regression test asserts launch refusal. | None. |
| MED | `scripts/dev/test_lab_flow.py:238-247` | Empty receipt vendor is rejected by `accepted()`. | Mutant defaulting empty to expected vendor makes the assertion fail. | None. |

## Mutation coverage

| Mutated behavior | Test that kills it | Evidence |
|---|---|---|
| `lab_flow.py:158`: accept an empty receipt vendor by defaulting it to the expected vendor | `test_accepted_rejects_empty_receipt_vendor` | Re-run in isolated scratch: 1 failed, `accepted()` returned True. |
| `lab_flow.py:212`: remove normalized card-vendor diagnostic | `test_v5_mutant_gate_normalized_allowlist_card_vendor_check` | Re-run in isolated scratch: 1 failed; exact message absent. |
| `lab_flow.py:217`: remove stage-3 producer-vendor restriction | `test_three_stage_recipe_stage3_matching_stage1_producer_is_refused` | Test asserts `F.launch` raises the producer-vendor error; also recorded KILLED in prior 2026-10-28 7/7 mutant rerun. |
| Hardened recipe non-string vendor validation | `test_v5_mutant_non_string_vendor_rejected_through_launch` | KILLED in prior 2026-10-28 7/7 mutant rerun; 3 parameter cases. |
| Hardened recipe empty-model validation | `test_v5_mutant_empty_model_rejected_through_launch` | KILLED in prior 2026-10-28 7/7 mutant rerun; 3 parameter cases. |
| Lowercase model normalization | `test_v5_mutant_model_lowercase_required_through_launch` | KILLED in prior 2026-10-28 7/7 mutant rerun. |
| Non-boolean hardened flag guard | `test_gate_rejects_non_boolean_vendor_hardening_flag` | KILLED in prior 2026-10-28 7/7 mutant rerun. |

## Follow-up cards

- None.
