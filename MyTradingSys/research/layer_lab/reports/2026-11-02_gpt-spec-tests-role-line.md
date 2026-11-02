# Spec tests for `role_line.py`

**11 tests pass; 3/3 scratch mutations detected.** Added `scripts/dev/test_role_line.py` and registered it in `scripts/dev/extra_tests.tsv`.

## Checked and run

- Read `scripts/dev/role_line.py` lines 1-71. Its documented contract names the first nonempty line, after wrappers, and accepts at most two name words. Derived the two-word boundary cases using `known`, since an unrestricted parse can validly accept the first word of a longer phrase as a one-word name.
- Branches covered: event detection after leading reminders; wrapper cleanup and line ending normalization; first nonempty line/label skipping; role start recognition; one and two word parsing; known-name spelling/rejection; strict versus loose end boundaries; event handling; and propagated `str()` errors.
- `python -m pytest scripts/dev/test_role_line.py -q`: initial spec correction was needed because an unrestricted three-word phrase resolves to its valid first one-word role. After correcting that expectation:
- `python -m pytest scripts/dev/test_role_line.py -q -p no:cacheprovider --basetemp="$env:TEMP\role_line_pytest_final"`: **11 passed**.
- Scratch mutations on temporary source copies: event recognition disabled (**1 failed, 10 passed**); strict boundary made loose (**1 failed, 10 passed**); paste tag cleanup disabled (**1 failed, 10 passed**). No mutation touched the audited source.
- SHA-256 of `scripts/dev/role_line.py` before/after: `1c54e7516e380759b7112b8c93827462a2618a25f52fad6114b9b0492276a3c0`.

## Findings

| Severity | File:line | Result | Evidence | Proposed fix |
|---|---|---|---|---|
| LOW | `scripts/dev/role_line.py:1-98` | MATCH | Tests assert the documented wrapper, first-line, event, known-name, strictness, malformed and error behavior; the source hash remained unchanged. | None. |
| LOW | `scripts/dev/extra_tests.tsv: end` | MATCH | Added `scripts/dev/test_role_line.py` as a registered extra test. | None. |

## Follow-up cards

None.
