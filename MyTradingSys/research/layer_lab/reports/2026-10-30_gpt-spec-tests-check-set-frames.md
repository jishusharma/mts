# gpt-spec-tests-check-set-frames

Changed: `scripts/dev/test_check_set_frames.py` (13 tests) and `scripts/dev/extra_tests.tsv` (registered test). The audited source `scripts/dev/check_set_frames.py` was not edited.

## What was checked

- Read `scripts/dev/check_set_frames.py` docstring and implementation (lines 1–134).
- Added pytest fixtures that redirect every module path to `tmp_path`; no real ledger, CHECK set or video files are read.
- Ran `python -m pytest scripts/dev/test_check_set_frames.py -q`: **13 passed**. Pytest emitted a cache-path warning (`WinError 183`); it did not affect test results.
- Ran three scratch-copy mutations under `scripts/dev/` temporary directories; each produced a failing assertion: case sensitivity (1 failed), outcome acceptance boundary (1 failed), `NOT_IN_DATA` contract (1 failed). Scratch directories were automatically removed.

## Branches and hand-derived expectations

| Severity | File:line | Finding / evidence | Proposed fix |
|---|---|---|---|
| LOW | `scripts/dev/check_set_frames.py:33–48` | MATCH: absent CHECK_SET.md returns one missing-file error; the phrase is case-insensitive; either “trades found” or the complete none-found phrase satisfies outcome. Tests cover accepted boundary, missing outcome, and alternate accepted outcome. | None |
| LOW | `scripts/dev/check_set_frames.py:51–101` | MATCH: missing CSV returns an error; CSV with headers and zero rows reports no CHECK rows; missing `id` header raises `KeyError`; qualifying rows require an existing frame, forbid caption references in three fields and four caption extensions, and require `NOT_IN_DATA`. | None; malformed-header exception is captured as current behavior. |
| LOW | `scripts/dev/check_set_frames.py:104–114` | MATCH: missing ledger Markdown reports one error; either `14 trade ids / 37 rows` or any `trade ids` phrase passes. | None |
| LOW | `scripts/dev/check_set_frames.py:117–134` | MATCH: unittest wrapper dispatches when argument is `unittest`; main aggregates three validators, returns 1 and prints each error on failure, or returns 0 and prints PASS. Main success/error output is tested. | None |
| LOW | `scripts/dev/check_set_frames.py:1–134` | MISMATCH (task wording): the source defines no numeric “limit” or numeric input boundary. “At limit / one below / one above” were mapped to the nearest implemented acceptance boundaries (valid outcome phrase / omitted outcome / alternate valid phrase); no numeric threshold was invented. | Clarify card wording if numeric boundary cases were intended. |

## Follow-up cards

None.
