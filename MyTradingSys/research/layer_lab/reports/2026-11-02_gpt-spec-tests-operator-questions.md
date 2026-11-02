# GPT spec tests: operator questions

**10 tests pass; 3/3 scratch mutations detected.** `scripts/dev/operator_questions.py` is unchanged.

## What was checked

- `scripts/dev/operator_questions.py:26-29, 258-264` - hand-derived input boundaries: `MAX_TYPED_CHARS = 3000`; `is_automated` flags lengths strictly greater than 3000, so 2999 and 3000 are false and 3001 is true. Leading whitespace is stripped for automated-prefix matching, while the length check uses the original text.
- `scripts/dev/operator_questions.py:186-194` - `read_rows` returns `[]` for a nonexistent path; skips blank lines; parses each nonblank line as JSON and lets JSON and I/O errors propagate.
- `scripts/dev/test_operator_questions.py` - ten tests cover those limits, empty and missing files, valid JSONL with blank lines, malformed JSON, directory read error, and prefix/length filtering.
- Registered the test in `scripts/dev/extra_tests.tsv` so the smoke gate runs it.

## Findings

| Severity | File:line | Finding | Evidence | Proposed fix |
|---|---|---|---|---|
| LOW | `scripts/dev/operator_questions.py:26-29` | MATCH: stated typed-text cutoff is exclusive at 3000 characters; leading whitespace only affects prefix detection. | Test results: 2999 false, 3000 false, 3001 true; prefixed and whitespace-length cases pass. | None. |
| LOW | `scripts/dev/operator_questions.py:186-194` | MATCH: missing path is empty input; malformed JSON and read errors remain visible; blank lines are ignored. | Tests pass for empty/missing files, valid rows, malformed JSON, and directory path error. | None. |
| LOW | `scripts/dev/test_operator_questions.py` | Three mutations detected in isolated temporary copies. | `>= MAX_TYPED_CHARS` failed at-limit test; nonempty missing-path result failed missing-file test; parsing blank rows failed blank-line test. Each pytest run exited 1 with 1 failed and 9 passed. | None. |

## Commands and results

- `python -m pytest scripts/dev/test_operator_questions.py -q` - **10 passed** (one pytest cache path warning; test result successful).
- Scratch mutation runs in `tempfile.TemporaryDirectory` copies - **3/3 failed as expected**, with the respective assertion failures listed above. No live source mutation was made.
- `operator_questions.py` has 362 lines; reviewed branches include `is_automated`, `read_rows`, their `pending_questions` filtering call, and CLI setup/dispatch. The six requested boundary/error categories are directly exercised by the tests.

## Follow-up cards

None.
