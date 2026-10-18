# lab-vendor-gate-harden

**PASS: vendor gate hardening is opt-in, validated, and covered by tests.**

## Changed files and evidence

- `scripts/dev/lab_flow.py:16,125-145,195-214,253-285` - Added a vendor allowlist (`codex`, `gemini`, `claude`), case/whitespace normalization, model-prefix consistency checks, and fail-closed validation for unknown or empty vendor labels. The `vendor_gate_hardened` option is strictly boolean, defaults off, and is included in the flow contract. C0-only override and boolean checks remain enforced. Critical-audit cards now retain `crucial=True` even though the recipe no longer includes an Astra stage.
- `scripts/dev/test_lab_flow.py:93-162` - Added tests for empty/unknown vendor, mismatched model prefix, normalized same-vendor labels, case normalization, C1 override rejection, non-boolean override rejection, opt-in default, and critical-audit crucial flag. The `complete` test helper sets a card active before finishing, matching `lab_flow.finish`'s existing active-card requirement.

## Red then green

- Red first, on pre-implementation code: `PYTHONPATH=. python -m pytest scripts/dev/test_lab_flow.py -k 'hardened_vendor_gate or same_vendor_override_is_c0_only_and_boolean' -q --basetemp .pytest-lab-tmp -p no:cacheprovider` - **2 failed, 1 passed**. Empty/mismatched vendors were accepted and mixed-case labels were not normalized. The C1/non-bool rejection behavior already existed; the new tests preserve it.
- Green: `PYTHONPATH=. python -m pytest scripts/dev/test_lab_flow.py -q --basetemp .pytest-lab-tmp -p no:cacheprovider` - **32 passed**.
- Lint: `python scripts/dev/lookahead_lint.py --new` - **0 new FAIL hits; 217 total hits (190 FAIL allowlisted, 27 WARN including 5 new warnings in unrelated files); 0 stale allowlist rows.** No new lint entries referenced either changed Python file.

## Findings

| Severity | Evidence | Result |
|---|---|---|
| MED | `scripts/dev/lab_flow.py:125-145,195-214` | MATCH - enabled hardening rejects unknown/empty labels and label/model prefix mismatches; normalized case and whitespace are used for vendor comparisons. |
| MED | `scripts/dev/test_lab_flow.py:125-149` | MATCH - C1 override and non-boolean override are rejected; explicit C0 boolean override is accepted. |
| LOW | `scripts/dev/lab_flow.py:285` | MATCH - all `critical-audit` stages carry `crucial=True`. |

No data was read. No holdout or live-path files were accessed. No follow-up cards were created.
