# lab-data-pin-hash

PASS: data inputs are pinned in flow receipts and holdout paths are refused.

## What changed and was checked

- `scripts/dev/lab_flow.py:11-12,27-58` defines the data root, rejects holdout path components, confines absolute paths to the repo or data root, and hashes optional `data_scope` entries under stable `data:<relative-path>` keys.
- `scripts/dev/lab_flow.py:60-64,74-78,130-134,154-161,233-234` includes `data_scope` in the flow contract, validates it at launch, and records/rechecks its hashes in the receipt source map.
- `scripts/dev/test_lab_flow.py:184-211` adds fail-first coverage for changed data hashes, receipt persistence, and holdout refusal. The tests use temporary fixture files; no market data bars were read.

## Findings

| Severity | Evidence | Result |
|---|---|---|
| HIGH | `scripts/dev/lab_flow.py:49-58,233-234` | PASS: modifying the fixture data changes the fingerprint and a finished receipt stores its `data:dev.csv` SHA-256. |
| HIGH | `scripts/dev/lab_flow.py:41-42`; `scripts/dev/test_lab_flow.py:202-211` | PASS: `holdout` path component raises `ValueError` before file content can be read. |
| LOW | `pytest -q --basetemp F:/MTS/mts-codex-lab/.pytest-tmp scripts/dev/test_lab_flow.py` | RESULT (2026-10-18): 22 passed; pytest emitted one cache-path warning due to workspace cache creation. |

Fail-first evidence: before implementation, the two new tests failed because `fingerprint()` accepted only two arguments and `safe_file()` did not refuse holdout paths. After implementation, all 22 tests passed.

Follow-up cards created: none.

