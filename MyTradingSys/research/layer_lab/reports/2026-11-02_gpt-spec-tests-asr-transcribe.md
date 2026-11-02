# Spec tests for `asr_transcribe.py`

**10 tests pass; 3/3 scratch mutations detected.** Added `scripts/dev/test_asr_transcribe.py` and registered it in `scripts/dev/extra_tests.tsv`.

## Checked and run

- Read `scripts/dev/asr_transcribe.py` lines 1-63. Derived unit tests for pure helper functions `resume_point(out)` and `log(msg, fh=None)`.
- Branches covered:
  - `resume_point`:
    - Nonexistent output file returns initial tuple `(0.0, 0, 0)`.
    - Empty output file returns `(0.0, 0, 0)`.
    - Whitespace and blank lines skipped cleanly.
    - Single valid segment parsed for last timestamp, segment count, and word list length.
    - Multiple segments correctly accumulated across `last`, `n_seg`, and `n_words`.
    - Out-of-order segment timestamps correctly evaluated via `max()`.
    - Missing `"words"` key handled with empty fallback without raising `KeyError`.
    - Torn / interrupted trailing lines from abrupt process termination handled via `ValueError` catch and skipped without dropping earlier segments.
    - Corrupted intermediate non-JSON lines skipped while remaining valid lines are parsed.
  - `log`:
    - Formats timestamped output `[%H:%M:%S] <msg>` to standard output with flush.
    - Formats and appends message to file handle `fh` with newline and flush.
- `python -m pytest scripts/dev/test_asr_transcribe.py -v`: **10 passed in 0.21s**.
- Scratch mutations on temporary copies:
  - M1: Replaced `last = max(last, float(r["end"]))` with direct assignment `last = float(r["end"])` (**1 failed, 9 passed**; caught by `test_resume_point_out_of_order_takes_max_end`).
  - M2: Removed `try/except ValueError` for json parsing (**2 failed, 8 passed**; caught by `test_resume_point_torn_trailing_line_skipped` and `test_resume_point_corrupt_middle_line_skipped`).
  - M3: Changed word counter accumulation `w += len(...)` to `w += 1` (**3 failed, 7 passed**; caught by `test_resume_point_multiple_segments_accumulate`).
- Audited source unchanged: SHA-256 of `scripts/dev/asr_transcribe.py` is `535b9560040b235877a33d5acd4e9c5e2ea44068a334f827a23f5c5baabd5c2e`.

## Findings

| Severity | File:line | Result | Evidence | Proposed fix |
|---|---|---|---|---|
| LOW | `scripts/dev/asr_transcribe.py:28-63` | MATCH | Pure helpers match spec and resilience requirements under killed/torn output conditions. Audited source hash unchanged. | None. |
| LOW | `scripts/dev/extra_tests.tsv:187` | MATCH | Registered `scripts/dev/test_asr_transcribe.py` into extra test runner. | None. |

## Follow-up cards

None.
