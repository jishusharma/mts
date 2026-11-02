# Spec tests for `declutter_backups.py`

**9 tests pass; 3/3 scratch mutations detected.** Added `scripts/dev/test_declutter_backups.py` and registered it in `scripts/dev/extra_tests.tsv`.

## Checked and run

- Read `scripts/dev/declutter_backups.py` lines 1-154. Audited pure classification logic in `classify(rel)`.
- Branches covered:
  - `classify`:
    - Rejection directory structures (`_nuc_rejected`, `qwen_raw_015_017`) and scratch directory prefixes (e.g. `scratch/`) correctly identified as `superseded`.
    - Normal non-backup files (e.g. `scripts/dev/foo.py`, `README.md`) return `(None, None)`.
    - Worker output filenames ending in `.rejected_*`, `.qwen_raw`, `.qwen<N>` identified as `superseded`.
    - Double-suffix `.new.new` files identified as `superseded` (Qwen verifier blocked pattern).
    - Backup files whose blob hash exists in the git commit history of the base file identified as `superseded`.
    - In-flight `.new` files differing from the live file classified as `staged`.
    - Promoted `.new` files identical in content (SHA-256) to the live file classified as `superseded`.
    - Backup snapshots of staged `.new` files (e.g. `foo.py.new.pre_tag`) classified as `superseded` when a newer `.new` file exists.
    - Pre-backup files where base was committed after backup taken classified as `superseded`; otherwise classified as `unknown` when base is uncommitted or untracked.
- `python -m pytest scripts/dev/test_declutter_backups.py -v`: **9 passed in 0.22s**.
- Scratch mutations on temporary copies:
  - M1: Disabled double-suffix `.new.new` check (**1 failed, 8 passed**; caught by `test_classify_double_suffix_new_new`).
  - M2: Inverted SHA-256 identity check between `.new` and live base file (**2 failed, 7 passed**; caught by `test_classify_staged_new_file_differing_from_live` and `test_classify_promoted_new_file_identical_to_live`).
  - M3: Disabled git history blob matching (**1 failed, 8 passed**; caught by `test_classify_blob_in_git_history`).
- Audited source unchanged: SHA-256 of `scripts/dev/declutter_backups.py` is `544021acf0062cf40056c540a4372e379b2901d08085a294f83f5d8959e75676`.

## Findings

| Severity | File:line | Result | Evidence | Proposed fix |
|---|---|---|---|---|
| LOW | `scripts/dev/declutter_backups.py:60-93` | MATCH | Classification matches docstring contracts and archive safety rules. Audited source hash unchanged. | None. |
| LOW | `scripts/dev/extra_tests.tsv:189` | MATCH | Registered `scripts/dev/test_declutter_backups.py` into extra test runner. | None. |

## Follow-up cards

None.
