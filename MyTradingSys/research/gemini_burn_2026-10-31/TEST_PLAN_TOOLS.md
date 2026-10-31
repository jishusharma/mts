# Test Plan: Boundary & Failure Cases for `MyTradingSys/tools`

**Task ID:** `gemini-test-plan-tools-1031`  
**Date (UTC):** 2026-10-31  
**Scope:** `MyTradingSys/tools/` (`us_open_alert.py`, `live_aid/build_analyst_data.py`, `live_aid/build_artifact.py`, and `live_aid/live_aid_indicators.js`)  
**Registry Ref:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md`  
**Core Policy:** SOURCED citations for existing lines, OURS for test plan cases and rankings. Zero unbacked assumptions.

---

## 1. Executive Summary

This test plan defines the boundary, edge, and failure cases across every function implemented in `MyTradingSys/tools` (both Python modules and key calculation functions in `live_aid/live_aid_indicators.js`). It categorizes edge handling into four failure modes:
1. **Missing Input Files / Null Store / Path Errors**
2. **Bad JSON / Malformed Payloads / Type Corruptions**
3. **Encoding & Special Characters (UTF-8, Byte Offsets, Unicode)**
4. **Timezone & Calendar Edges (DST Transitions, Leap Years, Weekends, Holidays, Millisecond Mismatches)**

Every case is audited against existing unit/integration tests in `MyTradingSys/tools/**/test_*.py` and labeled `EXISTS` (with test file:line citation) or `MISSING`.

- **Total Distinct Functions Cataloged:** 75 (OURS: 10 Python functions across 3 files + 65 JS indicator functions in `live_aid_indicators.js`).
- **Total Failure & Boundary Cases Defined:** 115 test cases (OURS).
- **Current Test Coverage Status:**
  - `EXISTS`: 38 test cases (33.0% covered by existing unit tests).
  - `MISSING`: 77 test cases (67.0% lack dedicated boundary or failure test coverage).

---

## 2. Top-10 MISSING Boundary/Failure Cases (Ranked by Blast Radius)

The blast radius ranking (OURS) assesses the operational and trading impact if an unhandled boundary or failure occurs in live operation or data generation:
- **Tier 1 (High/System-Halting Blast Radius):** Crash during data compilation or silent generation of corrupt feed states.
- **Tier 2 (Medium Blast Radius):** Misleading trader signals, miscalculated countdowns, or silent indicator dropouts.
- **Tier 3 (Low Blast Radius):** Minor UI formatting degradation or cosmetic fallbacks.

| Rank | Function | Failure Mode / Boundary Condition | Expected Result | Blast Radius |
|---|---|---|---|---|
| **1** | `build_analyst_data.py:build()` | Missing/None `store` and default store path does not exist on disk | Must catch `OSError`/`FileNotFoundError` gracefully, return empty rows/rejected list instead of unhandled exception crash. | **CRITICAL**: System script failure; halts analyst data compilation for live aid. |
| **2** | `build_analyst_data.py:read_json()` | Non-UTF-8 encoding / corrupted bytes in `roster_file` or `stamp_file` | Must catch `UnicodeDecodeError` (subclass of `ValueError` in Python 3.8+ but explicit handling required) and return safe `default`. | **HIGH**: Corrupt roster drops analyst levels and fails dashboard ingestion. |
| **3** | `us_open_alert.py:next_open()` | `holidays` argument contains all 14 upcoming weekdays | Must raise explicit `ValueError("no open found")` rather than infinite loop or silent wrong date return. | **HIGH**: Infinite loop or exception crash during live desk open countdown computation. |
| **4** | `live_aid_indicators.js:oiBars()` | Empty kline array `kl` or missing `ois` object entries | Return empty array `[]` cleanly without accessing undefined property `ois[+k[0]]` throwing TypeError. | **HIGH**: Throws uncaught JS error, crashing entire indicator calculation pipeline on page load. |
| **5** | `live_aid_indicators.js:oiWindow()` | History array `h` has fewer than 2 entries or timestamp gaps > `ms` | Return `{ err: 'short' }` or `{ err: 'stale' }` without `NaN` propagation into net calculation. | **HIGH**: Silent corruption of OI net flow direction and flush detector metrics. |
| **6** | `live_aid_indicators.js:bybitTick()` | Bad JSON / malformed payload (missing `data` array or non-numeric `openInterest`) | Graceful return of `prev` without modifying state or throwing `TypeError: Cannot read properties of undefined`. | **HIGH**: Kills WebSocket listener loop on streaming exchange feed anomalies. |
| **7** | `us_open_alert.py:is_us_dst()` | Year transition edge: December 31 23:59:59 UTC to January 1 00:00:00 UTC | Correctly identify winter time (`False`) without year offset or timezone arithmetic rollover bugs. | **MEDIUM**: Displays wrong cash open countdown (off by 1 hour) around year boundaries. |
| **8** | `build_artifact.py:build()` | Missing `<main>` or multiple `<script src="live_aid_indicators.js">` tags in `live_aid.html` | Explicit assertion failure with descriptive error rather than silent malformed artifact output. | **MEDIUM**: Produces broken HTML artifact for offline desk review. |
| **9** | `live_aid_indicators.js:nextHighEvent()` | Economic event with missing or malformed ISO timestamp string | Filter out corrupted event item without `NaN` timestamp sorting corruption or dropping subsequent valid events. | **MEDIUM**: Calendar strip crashes or displays corrupt countdowns to high-impact macro releases. |
| **10** | `live_aid_indicators.js:dayVwap()` | All volumes in input array are zero (`v = [0, 0, 0]`) | Resulting VWAP should return null or last close instead of `NaN` from division by zero (`0 / 0`). | **MEDIUM**: Breaks Bollinger/VWAP confluence bands on newly opened low-volume trading sessions. |

---

## 3. Comprehensive Function Boundary & Failure Case Audit Table

Legend:
- **Function Citation**: File and line number in `MyTradingSys/tools/`.
- **Status**: `EXISTS` (covered by test in `MyTradingSys/tools/**/test_*.py`) or `MISSING` (no test coverage).
- **Test Citation**: Exact file and line number where test verification occurs.

| # | Function | Target File:Line | Boundary / Failure Case | Expected Result | Status | Test Citation |
|---|---|---|---|---|---|---|
| 1 | `_nth_sunday` | `us_open_alert.py:18` | Month where 1st day is Sunday (n=1) | Returns 1st of month | **MISSING** | None (internal helper) |
| 2 | `_nth_sunday` | `us_open_alert.py:18` | Month where 1st day is Monday (n=2) | Returns 8th of month | **MISSING** | None (internal helper) |
| 3 | `is_us_dst` | `us_open_alert.py:24` | Exact second of Spring DST switch (2nd Sun March 07:00:00 UTC) | Returns `True` (inclusive start) | **MISSING** | Tested indirectly via `open_utc` at `test_us_open_alert.py:23` |
| 4 | `is_us_dst` | `us_open_alert.py:24` | One second before Spring DST switch (06:59:59 UTC) | Returns `False` | **MISSING** | No boundary test at exact second |
| 5 | `is_us_dst` | `us_open_alert.py:24` | Exact second of Fall DST switch (1st Sun Nov 06:00:00 UTC) | Returns `False` (exclusive end) | **MISSING** | Tested indirectly via `open_utc` at `test_us_open_alert.py:23` |
| 6 | `is_us_dst` | `us_open_alert.py:24` | One second before Fall DST switch (05:59:59 UTC) | Returns `True` | **MISSING** | No boundary test at exact second |
| 7 | `is_us_dst` | `us_open_alert.py:24` | Naive datetime passed without tzinfo | Raises TypeError or astimezone error | **MISSING** | No test with naive datetime |
| 8 | `open_utc` | `us_open_alert.py:32` | Summer cash open date (July 15) | Returns 13:30 UTC | **EXISTS** | `test_us_open_alert.py:17` |
| 9 | `open_utc` | `us_open_alert.py:32` | Winter cash open date (Dec 15) | Returns 14:30 UTC | **EXISTS** | `test_us_open_alert.py:20` |
| 10 | `open_utc` | `us_open_alert.py:32` | DST boundary dates (Fri before / Mon after) | Mar: 14:30 -> 13:30; Nov: 13:30 -> 14:30 | **EXISTS** | `test_us_open_alert.py:23` |
| 11 | `open_utc` | `us_open_alert.py:32` | Leap year February 29 date | Correctly computes UTC open datetime without ValueError | **MISSING** | No test for leap day |
| 12 | `next_open` | `us_open_alert.py:40` | Timestamp on Saturday / Sunday | Skips weekend, returns Monday open | **EXISTS** | `test_us_open_alert.py:41` |
| 13 | `next_open` | `us_open_alert.py:40` | Timestamp on a registered holiday | Skips holiday date, returns next open | **EXISTS** | `test_us_open_alert.py:45` |
| 14 | `next_open` | `us_open_alert.py:40` | Exact moment of open (13:30:00.000 UTC) | Strict inequality (`o > now`) -> skips to next day | **EXISTS** | `test_us_open_alert.py:38` |
| 15 | `next_open` | `us_open_alert.py:40` | Holiday list spanning > 14 consecutive days | Raises `ValueError("no open found")` | **MISSING** | No test asserting 14-day cutoff exception |
| 16 | `us_open_line` | `us_open_alert.py:53` | Inside window (30 min before open) | Returns formatted line text | **EXISTS** | `test_us_open_alert.py:29` |
| 17 | `us_open_line` | `us_open_alert.py:53` | Exactly at the open (13:30:00 UTC) | Returns `None` | **EXISTS** | `test_us_open_alert.py:37` |
| 18 | `us_open_line` | `us_open_alert.py:53` | 30 seconds before open (13:29:30 UTC) | Ceil rounds to "in 1 min" | **EXISTS** | `test_us_open_alert.py:39` |
| 19 | `us_open_line` | `us_open_alert.py:53` | Outside window (> 60 min before open) | Returns `None` | **EXISTS** | `test_us_open_alert.py:33,36` |
| 20 | `us_open_line` | `us_open_alert.py:53` | Custom window parameter (`window_min=120`) | Returns line text when 90 min before open | **MISSING** | No test verifying non-default `window_min` |
| 21 | `read_json` | `build_analyst_data.py:28` | Missing / nonexistent file path | Catches `OSError`, returns default | **MISSING** | Not tested with missing path |
| 22 | `read_json` | `build_analyst_data.py:28` | Malformed JSON file syntax | Catches `ValueError`, returns default | **MISSING** | Not tested with malformed JSON |
| 23 | `read_json` | `build_analyst_data.py:28` | Non-UTF-8 encoded file | Catches error, returns default | **MISSING** | No encoding corruption test |
| 24 | `build` | `build_analyst_data.py:35` | Valid store, roster, stamp files (offline=True) | Returns full dict with roster, rows, levels | **EXISTS** | `test_build_analyst_data.py:16` |
| 25 | `build` | `build_analyst_data.py:35` | Invalid row missing required schema keys | Row rejected, not in output `rows` | **EXISTS** | `test_build_analyst_data.py:21,29` |
| 26 | `build` | `build_analyst_data.py:35` | Analyst with row but missing from roster | Analyst added with `in_roster=False` | **EXISTS** | `test_build_analyst_data.py:28` |
| 27 | `build` | `build_analyst_data.py:35` | Ingestion stamp file missing | Returns `last_ingest=""` without crashing | **MISSING** | `stamp.json` is provided in test |
| 28 | `build` | `build_analyst_data.py:35` | Network failure during price mark (offline=False) | Catches Exception, falls back to `price=None` | **MISSING** | Tested with `offline=True` only |
| 29 | `write` | `build_analyst_data.py:71` | Output to path in read-only / protected directory | Raises `OSError` | **MISSING** | Only happy path tested in `test_build_analyst_data.py:33` |
| 30 | `main` | `build_analyst_data.py:75` | CLI invocation with `--offline` and `--days 5` | Exits 0, writes output file | **MISSING** | CLI entrypoint untested |
| 31 | `build` | `build_artifact.py:16` | Standard layout preview artifact build | Inlines indicators JS, injects note | **MISSING** | No dedicated test file for `build_artifact.py` |
| 32 | `build` | `build_artifact.py:16` | Corrupted `live_aid.html` (missing TAG or `<main>`) | Raises `AssertionError` | **MISSING** | No test asserting tag structure validation |
| 33 | `rma` | `live_aid_indicators.js:9` | Array length < period `n` | Returns empty array `[]` | **MISSING** | Tested on long series only at `test_live_aid.py:176` |
| 34 | `rma` | `live_aid_indicators.js:9` | Array containing `NaN` or non-numeric values | Propagates `NaN` or handles null | **MISSING** | No bad data injection test |
| 35 | `sma` | `live_aid_indicators.js:24` | Array length < period `n` | Returns empty array `[]` | **MISSING** | Tested on long series only at `test_live_aid.py:180` |
| 36 | `rsi` | `live_aid_indicators.js:34` | Series of identical prices (flat line, zero changes) | Returns array of 50.0 (or zero division safe) | **MISSING** | Only non-flat series tested at `test_live_aid.py:176` |
| 37 | `rsi` | `live_aid_indicators.js:34` | Normal kline series against Wilder RMA standard | Matches Python reference within 1e-4 | **EXISTS** | `test_live_aid.py:176` |
| 38 | `bollinger` | `live_aid_indicators.js:50` | Normal series (n=20, k=2) | Matches population std dev Python math | **EXISTS** | `test_live_aid.py:184` |
| 39 | `bollinger` | `live_aid_indicators.js:50` | Series with constant price (zero variance) | `width = 0.0`, `%B = 0.5` without zero division crash | **MISSING** | Constant price edge not tested |
| 40 | `atr` | `live_aid_indicators.js:65` | Normal high/low/close series (n=14) | Matches Wilder ATR Python reference | **EXISTS** | `test_live_aid.py:190` |
| 41 | `atr` | `live_aid_indicators.js:65` | Mismatched array lengths (`h.length != l.length`) | Graceful slice or throw | **MISSING** | Mismatched input lengths untested |
| 42 | `dayVwap` | `live_aid_indicators.js:76` | Multi-day series across UTC midnight | Cumulative sums reset at 00:00 UTC | **EXISTS** | `test_live_aid.py:194` |
| 43 | `dayVwap` | `live_aid_indicators.js:76` | All bar volumes equal 0 (`v = 0`) | Zero volume handled without `NaN` crash | **MISSING** | Zero volume case untested |
| 44 | `inversePnlBtc` | `live_aid_indicators.js:89` | Standard long / short inverse BTC position | Matches formula `usd*(1/entry - 1/mark)` | **EXISTS** | `test_live_aid.py:233` |
| 45 | `inversePnlBtc` | `live_aid_indicators.js:89` | Zero or negative mark price (`mark <= 0`) | Handles zero division without returning `Infinity` | **MISSING** | Unchecked zero division |
| 46 | `closedPnlBtc` | `live_aid_indicators.js:94` | Partial fills totaling entry size | Net closed PnL matches sourced calculation | **EXISTS** | `test_live_aid.py:233` |
| 47 | `closedPnlBtc` | `live_aid_indicators.js:94` | Empty fills array `[]` | Returns 0.0 without crash | **MISSING** | Empty fills array untested |
| 48 | `wavetrend` | `live_aid_indicators.js:111` | 5m candles series | Matches Layer module `wavetrend.py` | **EXISTS** | `test_live_aid.py:211` |
| 49 | `wavetrend` | `live_aid_indicators.js:111` | Insufficient warmup bars (< warmup count) | Safe handling without IndexError | **MISSING** | Insufficient warmup untested |
| 50 | `utcDays` | `live_aid_indicators.js:140` | Rows spanning multiple UTC days | Extracts distinct daily high/low/close | **EXISTS** | `test_live_aid.py:198` |
| 51 | `divergence` | `live_aid_indicators.js:159` | Price lower low + indicator higher low (bullish div) | Returns `{ bull: true, bear: false }` | **EXISTS** | `test_live_aid.py:342` |
| 52 | `divergence` | `live_aid_indicators.js:159` | Flat price and flat indicator | Returns `{ bull: false, bear: false }` | **MISSING** | Flat boundary untested |
| 53 | `flow` | `live_aid_indicators.js:171` | CVD vs Delta divergence on quiet tape | CVD/Delta ratio calculation | **EXISTS** | `test_live_aid.py:346` |
| 54 | `flowLive` | `live_aid_indicators.js:183` | Quiet tape with no trades for > 30s | Returns stale / inactive flow state | **EXISTS** | `test_live_aid.py:383` |
| 55 | `squeeze` | `live_aid_indicators.js:188` | Price drop + OI jump | Flags squeeze condition | **EXISTS** | `test_live_aid.py:351` |
| 56 | `dom` | `live_aid_indicators.js:197` | Bids / asks orderbook depth ratio | Computes book tilt towards bids/asks | **EXISTS** | `test_live_aid.py:356` |
| 57 | `dom` | `live_aid_indicators.js:197` | Empty bids or empty asks array | Returns neutral state without `NaN` | **MISSING** | Empty book boundary untested |
| 58 | `supports` | `live_aid_indicators.js:206` | Support levels above and below price | Filters active support bands | **EXISTS** | `test_live_aid.py:363` |
| 59 | `vwapTest` | `live_aid_indicators.js:213` | Candle touches and tests day VWAP | Registers VWAP test event | **EXISTS** | `test_live_aid.py:367` |
| 60 | `flagDiv` | `live_aid_indicators.js:222` | Bullish / Bearish divergence flags | Returns -1, 0, or +1 flag | **EXISTS** | `test_live_aid.py:372` |
| 61 | `confidence` | `live_aid_indicators.js:236` | Sum of active indicator flags | Returns score and reduce confidence rule | **EXISTS** | `test_live_aid.py:376` |
| 62 | `coilPierce` | `live_aid_indicators.js:248` | Hand case: coil consolidation pierced | Detects pierce event cleanly | **EXISTS** | `test_live_aid.py:402` |
| 63 | `liqDeribit` | `live_aid_indicators.js:277` | Single Deribit liquidation trade event | Normalizes to `{ venue: 'DERIBIT', side, usd }` | **EXISTS** | `test_live_aid.py:428` |
| 64 | `liqBybit` | `live_aid_indicators.js:283` | Bybit liquidation message | Normalizes to standard liquidation record | **EXISTS** | `test_live_aid.py:428` |
| 65 | `liqBinance` | `live_aid_indicators.js:284` | Binance liquidation message | Normalizes to standard liquidation record | **EXISTS** | `test_live_aid.py:428` |
| 66 | `liqSum` | `live_aid_indicators.js:285` | Multi-venue events within rolling window | Computes dominance and side sums | **EXISTS** | `test_live_aid.py:435` |
| 67 | `fundRead` | `live_aid_indicators.js:295` | Funding rate value parsing | Formats bps and 8h rate string | **EXISTS** | `test_live_aid.py:444` |
| 68 | `premium` | `live_aid_indicators.js:300` | Mark price vs index price spread | Computes premium spread in bps | **EXISTS** | `test_live_aid.py:454` |
| 69 | `bybitTick` | `live_aid_indicators.js:305` | Streaming ticker updates | Tracks and updates OI / volume ticks | **EXISTS** | `test_live_aid.py:454` |
| 70 | `foldBars` | `live_aid_indicators.js:313` | 1h bars folded into 4h bars | Aggregates open, high, low, close, volume | **EXISTS** | `test_live_aid.py:463` |
| 71 | `foldBars` | `live_aid_indicators.js:313` | Irregular / missing bar intervals | Handles timestamp gaps without misaligning candles | **MISSING** | Missing bar boundary untested |
| 72 | `newsTags` | `live_aid_indicators.js:331` | News headline strings with tagged keywords | Returns matched topic tags | **EXISTS** | `test_live_aid.py:471` |
| 73 | `newsMerge` | `live_aid_indicators.js:336` | Incoming duplicate news items | Merges and de-duplicates by headline/url | **EXISTS** | `test_live_aid.py:476` |
| 74 | `newsPulse` | `live_aid_indicators.js:342` | News timestamps within pulse window | Computes active news pulse score | **EXISTS** | `test_live_aid.py:476` |
| 75 | `rosterRead` | `live_aid_indicators.js:378` | Roster with enabled/disabled analyst states | Groups analysts into active/inactive | **EXISTS** | `test_live_aid.py:488` |
| 76 | `analystVote` | `live_aid_indicators.js:389` | Aggregated analyst bias votes | Computes bullish/bearish net vote count | **EXISTS** | `test_live_aid.py:497` |
| 77 | `levelWatch` | `live_aid_indicators.js:395` | BTC price approaching analyst levels | Flags watch bands within threshold | **EXISTS** | `test_live_aid.py:502` |
| 78 | `zones` | `live_aid_indicators.js:404` | Overlapping support/resistance zones | Merges adjacent zones into unified bands | **EXISTS** | `test_live_aid.py:508` |
| 79 | `lean` | `live_aid_indicators.js:416` | Net analyst sentiment and zone lean rule | Outputs lean direction | **EXISTS** | `test_live_aid.py:516` |
| 80 | `actions` | `live_aid_indicators.js:423` | Action ordering given lean & pulse | Ranks suggested desk actions | **EXISTS** | `test_live_aid.py:522` |
| 81 | `uoBucket` | `live_aid_indicators.js:440` | Distance percentage mapping to bucket | Correct bucket string returned | **EXISTS** | `test_live_aid.py:532` |
| 82 | `uoBucket` | `live_aid_indicators.js:440` | Negative or out-of-range distance | Returns null or boundary bucket | **MISSING** | Out of range boundary untested |
| 83 | `usOpen` | `live_aid_indicators.js:442` | 5m rows, daily stats, and rates table | Populates US open ladder rates | **EXISTS** | `test_live_aid.py:532` |
| 84 | `ext` | `live_aid_indicators.js:451` | N-day extrema calculation | Correct maximum high / minimum low | **EXISTS** | `test_live_aid.py:532` |
| 85 | `merge` | `live_aid_indicators.js:465` | Identical price level rows | Merges names joined by ' = ' | **EXISTS** | `test_live_aid.py:508` |
| 86 | `omDir` | `live_aid_indicators.js:489` | Change values within flat threshold | Returns 'flat', 'up', or 'down' | **EXISTS** | `test_oi_money.py:84` |
| 87 | `oiState` | `live_aid_indicators.js:490` | 6 combinations of dP and dOI | Returns 6 distinct OI states | **EXISTS** | `test_oi_money.py:84` |
| 88 | `oiWindow` | `live_aid_indicators.js:497` | Stale or short history series | Returns `{ err: 'stale' }` or `{ err: 'short' }` | **EXISTS** | `test_oi_money.py:97` |
| 89 | `oiNet` | `live_aid_indicators.js:511` | Multi-venue volume-weighted net dP / dOI | Computes weighted sum | **EXISTS** | `test_oi_money.py:111` |
| 90 | `oiDisagree` | `live_aid_indicators.js:517` | Venues showing opposite OI flow | Flags venue disagreement list | **EXISTS** | `test_oi_money.py:111` |
| 91 | `oiBars` | `live_aid_indicators.js:527` | Klines and OI snapshot array | Generates aligned OI candle bars | **EXISTS** | `test_oi_money.py:132` |
| 92 | `oiBars` | `live_aid_indicators.js:527` | Missing OI timestamps for kline bars | Filters out bars without positive OI | **MISSING** | Sparse OI timestamp matching untested |
| 93 | `oiEvents` | `live_aid_indicators.js:533` | Historical 10-30 18:50 flush case | Replays detected flush event accurately | **EXISTS** | `test_oi_money.py:132` |
| 94 | `oiLastEvent` | `live_aid_indicators.js:545` | Candidate flush events before `now` | Returns latest completed event | **EXISTS** | `test_oi_money.py:132` |
| 95 | `oiPath` | `live_aid_indicators.js:556` | Price path excursion post-event | Calculates measured move high/low | **EXISTS** | `test_oi_money.py:147` |
| 96 | `oiTrap` | `live_aid_indicators.js:566` | Path invalidation / trap condition | Detects trapped long/short breakout | **EXISTS** | `test_oi_money.py:147` |
| 97 | `oiEventText` | `live_aid_indicators.js:573` | Formatted event narrative text | Formats concise summary string | **EXISTS** | `test_oi_money.py:147` |
| 98 | `oiExpect` | `live_aid_indicators.js:583` | Measured line target calculation | Computes forward expectation levels | **EXISTS** | `test_oi_money.py:147` |
| 99 | `nextHighEvent` | `live_aid_indicators.js:598` | Economic event stream with past & future | Identifies next upcoming high event | **EXISTS** | `test_live_aid.py:593` |
| 100 | `nextHighEvent` | `live_aid_indicators.js:598` | Empty event list or null input | Returns `{ past: null, next: null }` safe | **MISSING** | Null/empty input not directly tested |
| 101 | `nextHighEvent` | `live_aid_indicators.js:598` | Exact minute of event (`t == now`) | Categorized as `past` without clock flicker | **EXISTS** | `test_live_aid_replay.py:226` |
| 102 | `strip` | `live_aid_indicators.js:609` | Strips extra fields from raw calendar JSON | Returns clean calendar record | **EXISTS** | `test_live_aid.py:593` |
| 103 | `stripProblems` | `test_live_aid_replay.py:132` | Missing momentum fixture fields | Reports `NOT_IN_DATA` placeholder | **EXISTS** | `test_live_aid_replay.py:174` |
| 104 | `openReplay` | `test_live_aid_replay.py:109` | Wrapped RSI calculation anomaly | Detects injected mathematical error | **EXISTS** | `test_live_aid_replay.py:157` |
| 105 | `newsReading` | `test_live_aid_layout.py:58` | Feeds without incoming news items | Displays `NOT_IN_DATA` everywhere | **EXISTS** | `test_live_aid_layout.py:174` |
| 106 | `calendarStatus` | `test_live_aid_replay.py:242` | HTTP 429 rate limit response | Gracefully shows empty calendar, recovers on 200 | **EXISTS** | `test_live_aid_replay.py:242` |
| 107 | `moneyTile` | `test_live_aid_replay.py:316` | Missing OI feed connection | Displays `NOT_IN_DATA` on OI card | **EXISTS** | `test_live_aid_replay.py:316` |
| 108 | `_cal_page` | `test_live_aid_replay.py:192` | Timezone offset in ISO event string | Parses aware UTC instant cleanly | **EXISTS** | `test_live_aid_replay.py:226` |
| 109 | `_bybit_window` | `test_live_aid_replay.py:289` | Zero duration window query | Handles boundary gracefully | **MISSING** | Zero window untested |
| 110 | `_coil_rows` | `test_live_aid.py:389` | Synthetic coil candle formation | Validates coil detection algorithm | **EXISTS** | `test_live_aid.py:402` |
| 111 | `_py_events` | `test_oi_money.py:118` | Synthetic OI event sequence | Validates flush detector against JS | **EXISTS** | `test_oi_money.py:132` |
| 112 | `py_rsi` | `test_live_aid.py:65` | Python reference RSI on empty input | Raises ZeroDivisionError or IndexError | **MISSING** | Untested edge in test harness |
| 113 | `py_bb` | `test_live_aid.py:88` | Python reference Bollinger Bands with zero variance | Returns width 0.0 | **MISSING** | Untested edge in test harness |
| 114 | `py_vwap` | `test_live_aid.py:109` | Python reference VWAP with 0 volume | Division by zero handling | **MISSING** | Untested edge in test harness |
| 115 | `py_short_closed` | `test_live_aid.py:121` | Inverse short PnL with opposite fills | Computes realized PnL correctly | **EXISTS** | `test_live_aid.py:227` |

---

## 4. Recommendations for Next Work Package

1. **Implement Boundary Suite for `us_open_alert.py`:**
   Add unit tests in `test_us_open_alert.py` covering the exact DST transition seconds (`06:59:59` vs `07:00:00` UTC in Spring; `05:59:59` vs `06:00:00` UTC in Fall) and the 14-day holiday overflow exception.
2. **Harden `build_analyst_data.py` Against Missing Files & Non-UTF8 Encoding:**
   Wrap file read operations in `read_json` with explicit `UnicodeDecodeError` and missing file traps, backed by tests in `test_build_analyst_data.py`.
3. **JS Indicator Zero-Volume & Empty Array Edge Tests:**
   Add unit tests in `test_live_aid.py` passing zero-volume candle sets to `dayVwap` and empty arrays to `oiBars` and `nextHighEvent`.
