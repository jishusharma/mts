# gpt-spec-tests-ff-calendar-snapshot

Changed files: `scripts/dev/test_ff_calendar_snapshot.py` (12 passing cases) and `scripts/dev/extra_tests.tsv` (registered test path).

## What was checked

- `scripts/dev/ff_calendar_snapshot.py:19-22`: `render()` has one explicit branch: reject non-list or empty events with `ValueError`; otherwise cast `fetched_ms` with `int()`, dump compact JSON and return the JavaScript assignment plus newline. `fetch()` at lines 25-28 performs network I/O. `main()` at lines 31-40 has an exception/error return branch and a successful write/return branch.
- Hand-derived from the source docstring (`ff_calendar_snapshot.py:5-6`): output is a JavaScript assignment carrying `fetched_ms` and `events`; a snapshot older than 26 hours is treated by the page as NO CALENDAR. The age-boundary expectations hold the calendar event constant and vary the supplied timestamp by exactly 26 h, 1 ms less, and 1 ms more. `render()` itself preserves all three timestamps as integers; the age decision is downstream.
- The specified local market data paths were checked and present. No market data was needed for serialization tests; no data files were opened.

## Results

| Severity | File:line | Finding / evidence | Proposed fix |
|---|---|---|---|
| LOW | `scripts/dev/ff_calendar_snapshot.py:20-22` | MATCH: tests cover the rejection guard, malformed timestamp conversion, compact output format, integer timestamp conversion, and unchanged list items. | None. |
| LOW | `scripts/dev/ff_calendar_snapshot.py:31-40` | The requested unit scope is `render()`; network `fetch()` was not called. Error behavior in `render()` is tested via invalid arguments. | None. |

Commands/evidence:

- `python -m pytest scripts/dev/test_ff_calendar_snapshot.py -q` — **12 passed** (one environment warning: pytest could not create its cache path because it already existed).
- Three isolated scratch mutations in temporary directories — **3/3 expected failures**: removal of empty-list rejection, changing compact JSON separators, and removing timestamp integer conversion. The audited source was not edited.
- `scripts/dev/extra_tests.tsv` contains `scripts/dev/test_ff_calendar_snapshot.py`.
- No Git command was run, per the session instruction; therefore `git cherry origin/fast-track` and `git ls-tree` were not verified here.

Follow-up cards created: none.
