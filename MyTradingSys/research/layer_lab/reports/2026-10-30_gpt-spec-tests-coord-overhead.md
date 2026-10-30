# gpt-spec-tests-coord-overhead

Changed files: `scripts/dev/test_coord_overhead.py` (9 passing tests) and `scripts/dev/extra_tests.tsv` (registered test). `scripts/dev/coord_overhead.py` was not changed.

## What was checked

- Read `coord_overhead.py` lines 38–101: equivalent-token arithmetic, tool-category precedence and fallback branches; lines 104–156: JSONL parsing, malformed-line skip, assistant-record selection, usage/content fallback, aggregation and zero-spawn ratio; lines 159–185: table defaults, all eight categories, shares and summary; lines 188–235: help/empty-argument usage, JSON flag, missing-file error, combined result and process exit.
- Hand-derived formula case: `10 + 4×1.25 + 20×0.1 + 2×5 = 27`. Neighboring input-only values 9, 10 and 11 produce 9.0, 10.0 and 11.0.
- Empty JSONL produces zero turns/counts/tokens, and zero coordination per spawn. A malformed line is skipped while a valid assistant line with 3 input tokens remains one text-only turn and 3.0 equivalent tokens. One spawn plus one text-only turn yields 2 total turns, 1 coordination turn, 1 spawn and ratio 1.0. Missing path returns exit 1 and the exact file-not-found message.

## Verification

`python -m pytest scripts/dev/test_coord_overhead.py -q` — **9 passed**. Pytest emitted a cache-directory `WinError 183` warning; the suite passed.

Three temporary scratch mutations were each restored immediately after their run and each made the suite fail (pytest exit 1): token output weight `5.0`→`4.0`; Agent spawn classifier name `Agent`→`AgentX`; missing-file exit status `1`→`0`. The original source was restored after each mutation.

## Findings

| Severity | File:line | Finding | Evidence | Fix |
|---|---|---|---|---|
| LOW | `scripts/dev/coord_overhead.py:44` | Formula is covered by independently calculated weighted and adjacent-value expectations. | 27 exact; mutation detected. | None. |
| LOW | `scripts/dev/coord_overhead.py:111-119, 202-205` | Malformed JSON skip and missing-file CLI failure are asserted. | Valid record survives malformed line; missing path returns 1. | None. |
| LOW | `scripts/dev/coord_overhead.py:144-146, 161-184` | Empty totals and zero-spawn formatting have explicit expectations. | Empty JSON summary and table assertions pass. | None. |

Follow-up cards: none.
