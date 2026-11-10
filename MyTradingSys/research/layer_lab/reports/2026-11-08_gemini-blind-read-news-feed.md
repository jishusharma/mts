MATCH: 6 | DIFF: 0 | NOT_IN_DATA: 0

# Gemini Blind Read Report: `news_feed.js` Panel Logic vs `sample_tree_news.json`

- **Card**: `gemini-blind-read-of-mytradingsys-tools-`
- **Date**: 2026-11-08 UTC (Verified 2026-11-10 UTC)
- **Reader**: Gemini (`gemini-3.8-flash-low`, blind read worker, JIS-NUC)
- **Target File**: `MyTradingSys/tools/live_aid/news_feed.js`
- **Data Source**: `MyTradingSys/research/news_feeds_2026-10-30/sample_tree_news.json` (20 items fetched 2026-11-08)
- **Reference Contract**: `MyTradingSys/tools/live_aid/test_news_feed.py`
- **Scope In / Out**:
  - In: Blind read of `news_feed.js` against `sample_tree_news.json`; independent calculation outside repo of importance >= 7 count, duplicate IDs, 12 newest IDs; check 6 panel rules (mark threshold 7, dedupe by _id, sort newest first, row limit, poll only while visible every 15 s, larger fetch limit after a gap).
  - Out: No edits to source files (`news_feed.js`, `sample_tree_news.json`, `test_news_feed.py`); no live-tree edit; no deploy; no `.secrets` or `.env` access.

---

## 1. Independent Computation from `sample_tree_news.json` (Outside Repo)

From `sample_tree_news.json` alone (20 Tree News items total):

1. **Items with `importance >= 7`**:
   - Independent Count: **1** item [OURS].
   - Sourced item: `_id: "1794073023724CUTmtcoceMo1biaif"`, `importance: 7.1`, `source: "COINDESK"`, `title: "COINDESK: U.S. Treasury moves to cut off crypto exchange MEXC over $16 billion in alleged illicit flows"` [SOURCED: `sample_tree_news.json:115-121`].
   - All other 19 items have importance <= 5.2 (ranging from 0.0 to 5.2, or null/none).

2. **Duplicate IDs**:
   - Independent Count: **0** duplicates (20 unique `_id` strings across 20 entries) [OURS].
   - Duplicate list: `[]` [OURS].

3. **IDs of the 12 Newest Items (Sorted by `time` descending)**:
   - Total items evaluated: 20 [SOURCED: `sample_tree_news.json:1-142`].
   - Sliced top 12 newest [OURS]:
     1. `117576661120815885` (`time: 1794077471401`) [SOURCED: `sample_tree_news.json:3`]
     2. `117576637813209602` (`time: 1794077115791`) [SOURCED: `sample_tree_news.json:10`]
     3. `117576618491350292` (`time: 1794076821315`) [SOURCED: `sample_tree_news.json:17`]
     4. `2119137465323708895` (`time: 1794076719087`) [SOURCED: `sample_tree_news.json:24`]
     5. `2119135865662300669` (`time: 1794076337298`) [SOURCED: `sample_tree_news.json:31`]
     6. `2119131060806074732` (`time: 1794075191766`) [SOURCED: `sample_tree_news.json:38`]
     7. `2119130949434888330` (`time: 1794075164875`) [SOURCED: `sample_tree_news.json:45`]
     8. `1794075069406NtotHjdukwfywai` (`time: 1794075069406`) [SOURCED: `sample_tree_news.json:52`]
     9. `2119129963613851751` (`time: 1794074930107`) [SOURCED: `sample_tree_news.json:59`]
     10. `2119128111803408513` (`time: 1794074488524`) [SOURCED: `sample_tree_news.json:66`]
     11. `1794073710109TOIAtsBcitps` (`time: 1794073710109`) [SOURCED: `sample_tree_news.json:73`]
     12. `117576401180733840` (`time: 1794073505151`) [SOURCED: `sample_tree_news.json:80`]

---

## 2. Panel Rules Reconciliation Table (6 Rules Checked)

| Rule # | Panel Rule Description | Independent Expected Value (from Sample / Spec) | Code Implementation Reference | Value Code Gives | Label | Status | Repro / Audit Verification Notes |
|---:|---|---|---|---|---|---|---|
| 1 | **Mark threshold 7** | `importance >= 7` marked `hi: true`; sample has exactly 1 marked item (`1794073023724CUTmtcoceMo1biaif`, 7.1) | `news_feed.js:8,10` (`var MARK = 7;`, `function mark(x) { return !!x && isFinite(parseFloat(x.importance)) && parseFloat(x.importance) >= MARK; }`) | `MARK = 7`; 1 marked item in sample; boundary tests: 6.9 -> `false`, 7.0 -> `true`, "8.5" -> `true`, `null` -> `false` | SOURCED (`news_feed.js:8,10`, `sample_tree_news.json:115`) | MATCH | Code accurately checks `parseFloat(x.importance) >= 7` and guards against non-finite values. Only MEXC headline marked. |
| 2 | **Dedupe by `_id`** | Keep only first occurrence of each `_id`; duplicate items dropped | `news_feed.js:23-24` (`var seen = {}; filter(... !seen[x._id] && (seen[x._id] = 1))`) | Evaluated on 20 items (0 dups) -> 20 items; synthetic test with 21 items (1 duplicate injected) -> drops duplicate, yields 20 unique rows | SOURCED (`news_feed.js:23-24`, `sample_tree_news.json:1-142`) | MATCH | Uses `seen` map keyed by `_id`. Drops items missing `_id` or with repeated `_id`. |
| 3 | **Sort newest first** | Descending order by `time` (`b.time - a.time`) | `news_feed.js:24-25` (`filter(... isFinite(+x.time)).sort(function (a, b) { return b.time - a.time; })`) | Rows strictly ordered monotonically descending by `time`: timestamps 1794077471401 down to 1794073505151 | SOURCED (`news_feed.js:24-25`, `sample_tree_news.json:3-80`) | MATCH | Verified all consecutive pairs satisfy `rows[i-1].time >= rows[i].time`. Non-numeric `time` filtered out. |
| 4 | **Row limit** | Output capped at `n || ROWS` (default 12 rows) | `news_feed.js:8,25` (`var ROWS = 12; ... slice(0, n || ROWS)`) | Returns exactly 12 rows for default call on 20-item sample; returns `n` when custom limit specified | SOURCED (`news_feed.js:8,25`) | MATCH | `rows(sample).length === 12`; matches the top 12 newest items computed independently. |
| 5 | **Poll only while visible every 15 s** | Returns `true` only if `!hidden` AND (`!lastAt` OR `now - lastAt >= 15000`); pauses when `hidden: true` | `news_feed.js:8,13` (`var EVERY_MS = 15000; function shouldPoll(hidden, lastAt, now) { return !hidden && (!lastAt || now - lastAt >= EVERY_MS); }`) | `shouldPoll(true, ...)` -> `false`; `shouldPoll(false, 0, t)` -> `true`; `shouldPoll(false, t - 14900, t)` -> `false`; `shouldPoll(false, t - 15000, t)` -> `true` | SOURCED (`news_feed.js:8,13`) | MATCH | Contract matches document visibility requirement; tested via `test_poll_only_while_visible_every_15s` in `test_news_feed.py`. |
| 6 | **Larger fetch limit after a gap** | Limit is 300 on first load (`!lastOkAt`) or after gap > 120,000 ms (2 min); 20 items during steady state | `news_feed.js:8,14` (`var POLL_LIMIT = 20, FIRST_LIMIT = 300, GAP_MS = 120000; function fetchLimit(lastOkAt, now) { return (!lastOkAt || now - lastOkAt > GAP_MS) ? FIRST_LIMIT : POLL_LIMIT; }`) | `fetchLimit(0, t)` -> 300; `fetchLimit(t - 15000, t)` -> 20; `fetchLimit(t - 119000, t)` -> 20; `fetchLimit(t - 121000, t)` -> 300 | SOURCED (`news_feed.js:8,14`) | MATCH | Full contract verified: resets to 300 headlines after tab was inactive or hidden > 2 minutes. |

---

## 3. Verification & Test Execution Summary

- All 15 unit tests in `MyTradingSys/tools/live_aid/test_news_feed.py` passed (`15 passed in 0.85s`) [SOURCED: `test_news_feed.py:1-124`].
- Independent calculations against `sample_tree_news.json` match code outputs with 0 diffs.
- `git diff` shows no edits to any repository files other than the newly created report.
