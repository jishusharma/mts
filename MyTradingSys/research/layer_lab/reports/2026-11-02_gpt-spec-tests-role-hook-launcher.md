# Spec-derived launcher tests

**Result:** 9 tests pass; 3/3 scratch source mutations fail the test suite. `scripts/dev/role_hook_launcher.py` is unchanged.

## Checked

- Read `scripts/dev/role_hook_launcher.py` lines 1–153. Branches covered/considered: `toplevel` git success/failure/exception; project hook settings file scanning/errors; role-name match/no match; bare login regex and loader freshness/read failure; run early exits for non-MTS checkout and project hook; malformed prompt normalization; trunk loader fetch exception/missing output; trunk loader execution/handle error; empty output; hook stdin JSON error and stdout behavior; `_edit` existing/missing settings, preservation/removal, install/uninstall; CLI command dispatch.
- Added `scripts/dev/test_role_hook_launcher.py` (9 tests), using pytest temporary directories and mocked git. Boundary expectations are computed from the regex/spec: `Lead` matches the final known role, `Leadx` and `Lead2` do not; empty payload/non-repository returns empty; non-string prompt is normalized to empty; missing trunk source for a role returns `ROLE NOT LOADED` naming the missing loader; loader `ValueError` reports its class; existing project hook skips; install preserves unrelated hooks and adds one entry per event; uninstall removes launcher entries and empty event groups.
- Registered the test in `scripts/dev/extra_tests.tsv`.

## Evidence

| Severity | File:line / command | Finding | Evidence | Proposed fix |
|---|---|---|---|---|
| LOW | `scripts/dev/role_hook_launcher.py:56-61` | Role match boundary | `names_role("You are Lead") == "Lead"`; `Leadx` and `Lead2` return `None`. | MATCH; no source change. |
| LOW | `scripts/dev/role_hook_launcher.py:98-105` | Missing source/error response | Exact JSON context includes missing-loader text or `trunk role_loader failed: ValueError`. | MATCH; no source change. |
| LOW | `scripts/dev/role_hook_launcher.py:124-138` | Settings edits preserve other hooks and remove empty groups | Temp-dir install/uninstall assertions pass. | MATCH; no source change. |

## Validation

- `python -m pytest scripts/dev/test_role_hook_launcher.py -q` — 9 passed (pytest cache emitted a Windows existing-path warning).
- Three scratch copies in system temp, mutated independently, then ran pytest against each with a temporary rootdir: role-boundary mutation — exit 1, 3 tests failed; malformed-prompt normalization mutation — exit 1, 1 test failed; launcher-hook filtering mutation — exit 1, 1 test failed. Scratch files were confined to temporary directories.
- Source integrity: only new test, test registration and this report were edited; launcher source unchanged.

## Follow-up

- None.
