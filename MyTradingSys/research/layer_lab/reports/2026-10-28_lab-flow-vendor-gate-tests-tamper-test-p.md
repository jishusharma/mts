# Lab flow vendor-gate mutation coverage

**PASS — test changes; card closure still awaits the required review stamp.**

## Scope and commands

- Edited `scripts/dev/test_lab_flow.py`; read `scripts/dev/lab_flow.py` and the 2026-10-19 independent findings in `MyTradingSys/research/lab_guy/findings/2026-10-19_review_harden_pair.md`.
- `python -m pytest --basetemp F:\MTS\labflow-gate-qa-20261028-1540 scripts/dev/test_lab_flow.py -q` — 52 passed.
- Ran each targeted regression against an isolated copy of `scripts/dev` with the named gate check mutated. The copy and pytest temporary roots were under `F:\MTS\labflow-mutation-luna-20261028`.

## Findings

| Severity | File | Result |
|---|---|---|
| MED | `scripts/dev/test_lab_flow.py` | The card-vendor tamper case now requires the exact normalized-allowlist error. The tamper test fails when that gate branch is removed; the previous broad `drifted` alternative had allowed that mutant to survive. |
| MED | `scripts/dev/test_lab_flow.py` | V5 vendor-type, empty-model and lowercase-model checks now exercise `F.launch`; each rejects its corresponding type/empty/normalization mutant. The hardened-flag check exercises `F.gate` and fails when the boolean guard is removed. |
| MED | `scripts/dev/test_lab_flow.py` | A three-stage recipe with stage 3 matching the stage-1 producer is refused, while the existing case where stage 3 matches stage 2 but differs from the producer remains accepted. The refusal test fails when the producer-vendor guard is removed. |
| MED | `scripts/dev/test_lab_flow.py` | An empty vendor in a completed receipt is not accepted. This test fails when an empty receipt vendor is defaulted to the expected vendor. |

## Mutation evidence

| Mutated behavior | Test | Result |
|---|---|---|
| Remove normalized card-vendor diagnostic | `test_v5_mutant_gate_normalized_allowlist_card_vendor_check` | KILLED |
| Accept empty receipt vendor as expected vendor | `test_accepted_rejects_empty_receipt_vendor` | KILLED |
| Remove stage-3 producer-vendor restriction | `test_three_stage_recipe_stage3_matching_stage1_producer_is_refused` | KILLED |
| Remove non-string vendor guard | `test_v5_mutant_non_string_vendor_rejected_through_launch` | KILLED (all 3 parameter cases) |
| Remove empty-model guard | `test_v5_mutant_empty_model_rejected_through_launch` | KILLED (all 3 parameter cases) |
| Remove lowercase model normalization | `test_v5_mutant_model_lowercase_required_through_launch` | KILLED |
| Remove hardened-flag type guard | `test_gate_rejects_non_boolean_vendor_hardening_flag` | KILLED |

No production gate change was needed: the current gate already rejects these cases. The card remains `refined` pending the Lab_Guy review stamp; this report does not claim the card is closed.
