# GPT retention spec tests — 2026-10-30

**Result: 10 tests pass; all 3 scratch mutations fail; `scripts/dev/retention.py` unchanged.**

## What was checked

- Read `scripts/dev/retention.py` (thresholds at lines 16, 65–76, 88–100) and `MyTradingSys/system/RETENTION_POLICY.md` (rules at lines 10–14).
- Added `scripts/dev/test_retention.py` and registered it in `scripts/dev/extra_tests.tsv`.
- Hand-derived boundaries: directories at exactly 14 days and at 13.999 days stay; 14.001 days is a candidate. Logs at exactly 200,000 bytes stay; 200,001 bytes is a trim candidate. A trim retains the last 2,000 lines. Empty plans and `Dumps/workers/NUC-QUEUE/done` produce no deletion; default invocation is dry-run and leaves bytes unchanged.

## Results

| Check | Evidence |
|---|---|
| New tests | `python -m pytest scripts/dev/test_retention.py -q` — **10 passed** (one pytest cache warning due to existing cache path). |
| Mutation 1 | Scratch copy changed age `> days` to `>= days`; **1 failed, 9 passed**, `test_old_children_14_day_boundary[14.0-expected0]`. |
| Mutation 2 | Scratch copy changed size `> 200_000` to `>= 200_000`; **1 failed, 9 passed**, `test_log_size_limit_is_strictly_greater_than_200000[200000-False]`. |
| Mutation 3 | Scratch copy added `Dumps/workers/NUC-QUEUE/done` to the delete list; **1 failed, 9 passed**, `test_protected_nuc_queue_done_is_not_a_candidate`. |

The mutation runs used temporary copies inside a temporary workspace directory, removed on exit. No mutation touched the source file. No live path or market data was read.
