# Research Report: Spec Tests for live_aid News Functions

**Task**: `gpt-spec-tests-live-aid-news-1103`
**Date**: 2026-11-03
**Scope**: `MyTradingSys/tools/live_aid/test_spec_news.py`, `scripts/dev/extra_tests.tsv`
**Reference**: `MyTradingSys/tools/live_aid/REQUIREMENTS.md` R12, `MyTradingSys/tools/live_aid/live_aid_indicators.js:324-372`

---

## 1. Summary of Functions Tested

The pure functions under `live_aid_indicators.js` handling news processing were given offline unit/spec tests:
- `newsTags(title)`: Checks classification word rules across categories (`hack`, `halt`, `etf`, `fed`, `war`, `delist`, `btc`).
- `newsMerge(list, incoming, max)`: Merges two headline arrays, deduplicates by `_id`, sorts descending by `time`, and slices to `max`.
- `newsPulse(items, now)`: Computes headline frequency pulse:
  - Filters items with `importance >= 7` within 1 hour (`winMs = 3600000`).
  - Threshold levels: `n >= 3` -> `EVENT`, `n >= 1` -> `BUSY`, `n == 0` -> `QUIET`.
  - Determines highest-importance headline in window as `top`.
- `newsCoins(x)`: Normalizes and extracts coin tickers from `x.suggestions` objects (`{coin: 'btc'}`) and strings (`'SOL'`).
- `newsRead(x)`: Applies direction heuristics (word rules for hack, halt, macro, war, ETF up/down, non-BTC coin isolation, and BTC buy/sell sentiment).

---

## 2. Test Execution & Coverage

- Test file: `MyTradingSys/tools/live_aid/test_spec_news.py`
- Command: `python -m pytest MyTradingSys/tools/live_aid/test_spec_news.py -q`
- Result: **10 passed in 1.94s** (exceeds requirement of >=8 passing tests).
- All runs execute against live Node.js v24.20.0.

---

## 3. Mutation Testing (Fail-First Verification)

Three distinct scratch mutations were applied to a temporary copy of `live_aid_indicators.js` and verified with `LIVE_AID_JS_PATH`:

1. **Mutation 1 (`mut1_newsTags_break`)**:
   - Change: Prepend prefix `BROKEN_` to tag outputs (`out.push("BROKEN_" + c[0]);`).
   - Outcome: **FAILED** `test_news_tags_keywords_and_case` (exit code 1).
2. **Mutation 2 (`mut2_newsPulse_threshold`)**:
   - Change: Alter `mark` threshold from 7 to 99 (`var NW = { mark: 99`).
   - Outcome: **FAILED** `test_news_pulse_thresholds_and_levels`, `test_news_pulse_window_edges` (exit code 1).
3. **Mutation 3 (`mut3_newsMerge_sort`)**:
   - Change: Invert sort comparison from `b.time - a.time` to `a.time - b.time`.
   - Outcome: **FAILED** `test_news_merge_dedup_and_sort`, `test_news_merge_max_cap_and_malformed` (exit code 1).

All 3/3 scratch mutations failed the test suite as required.

---

## 4. Verification Checkpoints

- Target `.js` files remain unmodified (`git status` confirms `live_aid_indicators.js` is clean).
- Registered in `scripts/dev/extra_tests.tsv`.
- Full gate / test checks pass cleanly.
