# gpt-spec-tests-deploy-untrack-backup

Changed files: `scripts/dev/test_deploy_untrack_backup.py` (15 tests), `scripts/dev/extra_tests.tsv` (registered), this report. `python -m pytest scripts/dev/test_deploy_untrack_backup.py -q -p no:cacheprovider --basetemp=F:/MTS/mts-codex-lab/.tmp_deploy_tests` — **15 passed**. Scratch mutations: **3/3 caught**.

## What was checked

- Read `scripts/dev/deploy_untrack_backup.py` lines 1–200. The source helper was not edited.
- Tests use pytest temporary directories. The three mutation variants lived in a temporary directory inside the repo and were removed after each run.
- The size boundary is the implementation's 1 MiB SHA read block (`deploy_untrack_backup.py:40–43`): expected digest for `2^20 - 1`, `2^20`, and `2^20 + 1` deterministic bytes is independently calculated with `hashlib.sha256`.
- Hand-derived behavior: a zero-match backup has `{}` manifest and verifies as `[]`; selected paths are unique and lexically sorted; an ordinary backup records the copied bytes' SHA and byte count; missing live files restore and verify; a different existing live file remains untouched and produces one `KEPT-NEWER` result; missing/changed backup entries produce the corresponding exact problem; malformed JSON raises `JSONDecodeError`; duplicate destination raises `RuntimeError`; malformed CLI arguments and missing manifest return 1 with usage/`PROBLEM` output.

## Branch inventory (`deploy_untrack_backup.py`)

| Location | Branch/condition | Expected result |
|---|---|---|
| `:49–53` | each glob result is a file or not | Add only files; sorted unique relative POSIX paths |
| `:68–71` | stamp omitted / supplied; destination exists | Generate UTC stamp or use supplied value; existing destination raises without overwrite |
| `:74–82` | zero or more collected paths | Copy each; manifest maps path to copied SHA and size; write sorted JSON and return stamp + manifest |
| `:87–89` | manifest missing / present | Missing raises `RuntimeError`; present is JSON-decoded (malformed JSON propagates decoder error) |
| `:96–102` | backup file missing / hash mismatch / match | Append exact missing or SHA problem; otherwise no problem |
| `:110–120` | live bytes extend backup / are rewritten or shorter | Extension replaces backup and updates manifest; rewrite preserves prior backup in first free `.pre-reset-N` and returns `False` |
| `:126–141` | backup verification fails; git file untracked/error; tracked clean; tracked dirty; checkout fails | Fail closed; skip nontracked; skip clean; refresh then checkout and return reset path; checkout error raises |
| `:150–166` | corrupt backup; live exists same/different; live missing and copy verifies/fails | Report corrupt and continue; keep same silently or different as `KEPT-NEWER`; restore and list verified copy or report mismatch |
| `:171–197` | invalid args; backup; reset; restore; `RuntimeError`; verification problems / kept files | Usage + 1; command-specific output and status; caught runtime errors print `PROBLEM` and return 1; restore problems/kept return 1 |

The explicit test cases exercise the hash chunk boundary, collect filtering/order, empty backup, manifest/hash/size values, verified restore, newer-live preservation, missing and changed backup diagnostics, malformed manifest, duplicate backup, corrupt backup, argument validation, and CLI error output. Git reset branches and the exceptional failed-copy verification branch are listed above but were not invoked; reset would require a Git working tree and the task restricts these tests to temporary directories.

## Mutation check

Three temporary source edits were run against the same pytest file via `DEPLOY_UNTRACK_BACKUP_MODULE`; each produced a failing suite:

1. Uppercase `sha256` output — caught by digest comparisons.
2. Reverse `collect` sorting — caught by the expected path order.
3. Permit overwriting a different existing live file — caught by the `KEPT-NEWER` and preserved-bytes assertions.

No findings against the audited source; no follow-up cards created.
