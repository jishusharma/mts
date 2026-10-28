# Trust re-check: lab-data-pin-hash

DISPUTED: the data pin calculation and current checks MATCH, but this Codex/OpenAI review is not an independent vendor review of a Codex/GPT-produced artifact; do not apply VERIFIED-C2 from this review.

Reviewer: OpenAI, GPT-6.1-Sol (Codex). Re-derived from the written 2026-10-17 report and fixture bytes in the test; producer code was inspected only after the independent calculation, for comparison.

## What was checked

- Read `MyTradingSys/research/layer_lab/reports/2026-10-17_lab-data-pin-hash.md` line by line. Its lines 7-9 define the intended scope, stable `data:<relative-path>` key, receipt persistence, and fixture coverage. It does not print a concrete digest; the test's literal fixture supplies the bytes.
- Independently computed SHA-256 with Python `hashlib` from the fixture bytes `t,c\n1719705600000,1\n`, then compared with the implementation fingerprint in a temporary repo/data root.
- Applied the report's path rule independently: resolve the candidate path and allow it only under the repository or data root. Compared the outside path with `safe_file`. A symlink probe could not be created: Windows returned `OSError(22), A required privilege is not held by the client`.
- Read `scripts/dev/test_lab_flow.py`; ran the requested suite and a one-line mutant in a disposable copy of `scripts/dev/lab_flow.py`. The tracked test and implementation files were not changed.
- No market data bars were read.

## Findings

| Severity | Evidence | Result |
|---|---|---|
| HIGH | `scripts/dev/lab_flow.py:101-109`; `scripts/dev/test_lab_flow.py:392-408`; report `2026-10-17_lab-data-pin-hash.md:15` | MATCH. Fixture bytes hash to `35ab71f6cfbb1c7fe614ae7a4456015f99f794dde646785444ee5478464f6fbf`. The independent `hashlib` result equals the fingerprint entry `data:dev.csv` produced in a temporary fixture run. Changing the value byte from `1` to `2` gives `b0640028e6afc68ae36faacd94a25daf017e50c26d2097bfa3a9ef1a1164232a`, which differs. |
| HIGH | `scripts/dev/lab_flow.py:31-47`; report `2026-10-17_lab-data-pin-hash.md:7,16` | MATCH for absolute outside path. The written rule resolves the path before checking containment; independent resolution refused the outside candidate, and `safe_file` raised `ValueError` for it. A live symlink test is unverified because the sandbox denied symlink creation; the documented resolve-then-containment calculation would refuse a link resolving outside the allowed roots. |
| HIGH | `scripts/dev/test_lab_flow.py:392-408`; disposable mutant run | MATCH: fail-first bites. In a scratch copy, replaced the first `return hashes` in `lab_flow.py` with `return {}`. `pytest test_lab_flow.py -q -p no:cacheprovider`: **2 failed, 43 passed**. Failures included source-change invalidation and `test_data_scope_hash_changes_when_data_file_changes`. |
| LOW | `python -m pytest scripts/dev/test_lab_flow.py -q` | RESULT (2026-10-26): **45 passed**, one pytest cache-path warning (WinError 183). |
| HIGH | Producer identity: `MyTradingSys/research/layer_lab/reports/2026-10-17_lab-data-pin-hash.md:3,7-9`; reviewer identity above | DISPUTED: the review calculations match, but reviewer and producer are both OpenAI/GPT. The independent-vendor condition for a C2 trust re-check is not satisfied here. |

## Tag proposal

**DISPUTED.** Do not stamp VERIFIED-C2 based on this review. Obtain a different-vendor reviewer to complete the reviewer-independence requirement; the calculations and the scratch mutation result above can be reused as evidence, not as that reviewer's attestation.

Follow-up cards created: none.
