# Spec tests for `ff_calendar_snapshot.py`

**10 tests pass; 3/3 scratch mutations detected.** Added `scripts/dev/test_ff_calendar_snapshot.py` and registered it in `scripts/dev/extra_tests.tsv`.

## Checked and run

- Read `scripts/dev/ff_calendar_snapshot.py` lines 1-44. Derived unit tests for pure rendering helper `render(events, fetched_ms)` and stubbed `main()`.
- Branches covered:
  - `render`:
    - Formats valid event list into Javascript assignment syntax: `window.LIVEAID_CAL_SNAP = {"fetched_ms":...,"events":...};\n`.
    - Compact separators without whitespace formatting.
    - Floating point epoch timestamp argument cast to integer milliseconds.
    - Empty event list input raises `ValueError("calendar feed is not a non-empty list")`.
    - Non-list types (`None`, dictionary, string) raise `ValueError`.
  - `main`:
    - Successful stubbed `fetch()` generates snapshot `.js` file, logs event count, and returns 0.
    - Network or HTTP errors during `fetch()` catch exception, log failure to stderr, preserve existing file untouched, and return 1.
    - Malformed feed payloads returning empty lists catch exception and return 1 without overwriting.
- `python -m pytest scripts/dev/test_ff_calendar_snapshot.py -v`: **10 passed in 0.42s**.
- Scratch mutations on temporary copies:
  - M1: Removed validation check in `render` (**5 failed, 5 passed**; caught by `test_render_empty_list_raises_value_error`, `test_render_none_raises_value_error`, etc.).
  - M2: Changed Javascript global variable prefix (`const LIVEAID_CAL_SNAP = `) (**3 failed, 7 passed**; caught by `test_render_single_event_and_exact_js_wrapper` and `test_main_success_with_stubbed_fetch`).
  - M3: Omitted integer casting for `fetched_ms` (**1 failed, 9 passed**; caught by `test_render_float_ms_cast_to_int`).
- Audited source unchanged: SHA-256 of `scripts/dev/ff_calendar_snapshot.py` is `13de9d9ae29213d520d6ceee7cd420f4fbb8b63f794f3c7f02bec6a2bf4505a9`.

## Findings

| Severity | File:line | Result | Evidence | Proposed fix |
|---|---|---|---|---|
| LOW | `scripts/dev/ff_calendar_snapshot.py:19-41` | MATCH | Rendering, validation, and error-handling behavior match docstring requirements. Audited source hash unchanged. | None. |
| LOW | `scripts/dev/extra_tests.tsv:191` | MATCH | Registered `scripts/dev/test_ff_calendar_snapshot.py` into extra test runner. | None. |

## Follow-up cards

None.
