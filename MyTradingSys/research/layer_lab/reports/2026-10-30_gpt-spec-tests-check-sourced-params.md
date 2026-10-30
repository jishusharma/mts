# gpt-spec-tests-check-sourced-params

9 tests pass; 3/3 scratch mutations failed their targeted test. `scripts/dev/check_sourced_params.py` is byte-for-byte unchanged (SHA-256 `C155FCF927FF3489B8138B7EFB55F69CBAC9E004CECF478CA461D29B3D2C3274`).

## Checked

- `scripts/dev/check_sourced_params.py:1-126`: docstring contract and all decision branches in `load_ledger`, `load_rules`, `_cite_problems`, `check_file`, `scan`, `evaluate`, and `main`.
- `scripts/dev/test_check_sourced_params.py`: nine isolated tests; JSON fixtures and malformed-input cases use pytest temporary directories.
- `scripts/dev/extra_tests.tsv`: registered the new standalone test for the smoke gate.
- Commands: `python -m pytest scripts/dev/test_check_sourced_params.py -q -p no:cacheprovider` -> `9 passed`; mutation harness -> expiry boundary, CLI status, and parameter count each `1 failed, 8 deselected`; rerun after restoring source -> `9 passed`.

## Spec-derived expectations and branch inventory

| Branch / boundary | Hand-derived expected result | Test |
|---|---|---|
| Krown `params` dict; invalid/missing label -> `no-label`, then continue | `("length", "no-label")` | CLI finding test |
| Valid label, blank/missing source -> `no-source`, then continue | One `no-source` problem | Covered by CLI fixture construction branches; label failure is directly asserted |
| SOURCED with neither quote nor locator -> `sourced-no-quote`; citation checks run only for SOURCED | A locator (`KR-A12`) means no problem | valid sourced parameter test |
| Flat source blank -> `*::no-source`; case/space-insensitive `operator` bypasses locator | `" Operator "` -> no problems | operator source test |
| Flat non-operator lacking locator and quote key -> `sourced-no-quote` | one file-level issue | No dedicated assertion |
| Optional ledger/rules absent vs present; unknown extract/rule citations | Absent ledgers suppress membership failures; present ledgers allow only listed IDs | No dedicated assertion |
| Scan missing layer dirs / no files | `(0, [])` | empty root test |
| Count dict parameters vs flat file as one | one parameter -> `n == 1` | valid sourced test; parameter-count mutation |
| Allowlist expiry exactly at limit; one day before; one day after | allowed at expiry and before; expired on next day | three expiry tests |
| Stale allowlist entry vs no findings | stale entry fails even if no finding; reset fixture isolates cases | CLI finding test exercises cleanup of allowlist state |
| `--list` prints tuples; summary and `FAIL` lines; exit depends on failures | exact three output lines, return 1 | CLI finding test |
| Malformed JSON and missing `--root` operand error paths | `JSONDecodeError`; `IndexError` and no printed output | malformed/error-path tests |

All test-created files are under pytest temporary directories. No market data was needed or read.

## Findings

| Severity | File:line | Finding | Evidence / proposed fix |
|---|---|---|---|
| LOW | `scripts/dev/check_sourced_params.py:41-95` | Some contract branches (unknown citations, blank source, and flat locator/quote behavior) are inventoried but not independently asserted in this initial nine-test suite. | Current test output is 9 passing and all three required mutations fail. Add focused cases if expanding beyond the card's eight-test minimum. |

Follow-up cards: none.
