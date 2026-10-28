# Build report: lab-crossvendor-same-vendor-gate

PASS — same-vendor reviewer pairs are rejected by vendor; tests pass.

## Changed

- `scripts/dev/lab_flow.py:168` compares reviewer and producer vendor fields. A same-vendor pair requires both `risk_class: C0` and `same_vendor_override: true`; these values are part of the flow contract at `scripts/dev/lab_flow.py:111`.
- `scripts/dev/lab_flow.py:17` and `scripts/dev/lab_flow.py:21` route the built-in critical-audit and run-review recipes to Gemini reviewers so they satisfy the gate.
- `scripts/dev/test_lab_flow.py:67` covers Codex Sol reviewing Codex Astra rejection, cross-vendor acceptance, and the explicit C0 override. The test was run before the code change and failed with `DID NOT RAISE`, confirming the old gate accepted the same-vendor pair.

## Verification

- `python -m pytest scripts/dev/test_lab_flow.py -q --basetemp F:/MTS/mts-codex-lab/.pytest-tmp-lab-flow` — **28 passed**.
- The runner's default temporary directory was inaccessible, so pytest used the workspace temporary directory shown in the command.

## Findings

| Severity | Evidence | Finding | Resolution |
|---|---|---|---|
| HIGH | `scripts/dev/lab_flow.py:178` | Same-vendor reviews with different model IDs bypassed the old model-only check. | Compare recorded vendor fields and require an explicit C0-only override. |
| MED | `scripts/dev/lab_flow.py:17`, `scripts/dev/lab_flow.py:21` | Built-in critical-audit and run-review recipes would violate the new gate because both stages used Codex. | Route their reviewer stage to Gemini. |

Follow-up cards: none.
