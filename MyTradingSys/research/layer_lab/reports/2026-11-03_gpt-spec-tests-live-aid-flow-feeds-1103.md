# Research Report: Spec Tests for live_aid Flow and Feeds Functions

**Task**: `gpt-spec-tests-live-aid-flow-feeds-1103`  
**Date**: 2026-11-03  
**Scope**: `MyTradingSys/tools/live_aid/test_spec_flow_feeds.py`  
**Reference**: `MyTradingSys/tools/live_aid/REQUIREMENTS.md` R08, R17, `STEPS.md` lines 29-31, 55-78, `live_aid_indicators.js:274-323`

---

## 1. Summary of Functions Tested

The pure functions under `live_aid_indicators.js` handling exchange liquidations, funding, premium, ticker updates, and multi-timeframe bar folding were given offline unit/spec tests:

- `liqDeribit(x, t)`:
  - Deribit trade liquidation handling where amount is already USD.
  - Flags: `T` (taker), `M` (maker), `MT` (both).
  - Direction mapping: Taker sell -> long liquidated, Taker buy -> short liquidated. Maker has the opposite side.
  - Non-liquidation or malformed objects return empty arrays.
- `liqBybit(x)`:
  - Parses Bybit liquidation payloads (`allLiquidation` stream).
  - Side mapping: `S === 'Buy'` -> long liquidated, `S === 'Sell'` -> short liquidated (per venue docs / `STEPS.md` line 60).
  - USD computation: `(+x.v) * (+x.p)`.
- `liqBinance(m)`:
  - Parses Binance `forceOrder` payloads.
  - Side mapping: `o.S === 'SELL'` -> long liquidated, `o.S === 'BUY'` -> short liquidated.
  - USD computation: `(+o.q) * (+o.ap)`.
- `liqSum(ev, now, ms)`:
  - Computes rolling liquidated USD volume per side in window `e.t <= now && now - e.t <= ms`.
  - Edge verification: includes exact lower bound `now - ms` and `now`; excludes `now - ms - 1` and future timestamps.
  - Tracks total events `n` and large orders `big` (`usd >= LQ.bigUsd` = 100,000 USD).
  - Determines dominance: `longs` (long >= 2x short), `shorts` (short >= 2x long), `mixed`, or `none` (0 total).
- `fundRead(r)`:
  - Converts 8h funding rate into `pct8h` (`r * 100`) and uncompounded `annual` (`r * 1095 * 100`).
  - Classifies side: `zero` (`|r| < 0.00001`), `longs` (`r > 0`), `shorts` (`r < 0`).
  - Flags high funding: `high = true` when `|r| >= 0.0003` (0.03% threshold).
  - Handles null, empty, non-finite, and string numeric inputs gracefully.
- `premium(mark, idx)`:
  - Computes basis points and points between mark and index: `pts = mark - idx`, `bps = (pts / idx) * 10000`.
  - Returns null for non-finite values or zero index.
- `bybitTick(prev, msg)`:
  - Ingestion logic for Bybit ticker messages: snapshot replaces state completely; delta overlays changed fields onto `prev`.
  - Handles missing `msg.data` and initial null `prev` cleanly.
- `foldBars(rows, ms, dayAlign)`:
  - Folds 1m OHLCV bars into higher timeframes (2m, 7m, 10m).
  - Computes correct bucket aggregations: open of first bar, max high, min low, close of last bar, sum of volume.
  - `dayAlign`: When true, anchors bucket calculations to UTC midnight (`Math.floor(t / 86400000) * 86400000`), critical for 7m folding (per R17 and TradingView convention) where 1440 minutes in a day is not evenly divisible by 7.

---

## 2. Test Execution & Coverage

- Test file: `MyTradingSys/tools/live_aid/test_spec_flow_feeds.py`
- Command: `python -m pytest MyTradingSys/tools/live_aid/test_spec_flow_feeds.py -q`
- Result: **12 passed in 2.37s** (exceeds requirement of >=8 passing tests).
- All tests execute against Node.js via subprocess runner supporting `LIVE_AID_JS_PATH`.

The test suite covers:
1. `test_liq_binance_side_and_usd`: Binance side mapping (SELL=long, BUY=short) and USD math (`q * ap`).
2. `test_liq_bybit_side_and_usd`: Bybit side mapping (Buy=long, Sell=short) and USD math (`v * p`).
3. `test_liq_deribit_side_mapping_and_types`: Deribit Taker/Maker/MT mappings, USD pass-through, and non-liquidation filtering.
4. `test_liq_sum_window_edges`: Window edge inclusion (`e.t == now`, `e.t == now - ms`) and exclusion (`e.t == now - ms - 1`, future).
5. `test_liq_sum_dominance_and_big_threshold`: Empty inputs, `LQ.bigUsd` threshold (100k USD), dominance classifications (`longs`, `shorts`, `mixed`, `none`).
6. `test_fund_read_pct_annual_and_side`: 8h and annual math, side tags, and high funding flag.
7. `test_fund_read_falsy_and_malformed`: Falsy, malformed string, and numeric string parsing.
8. `test_premium_pts_and_bps`: Points and basis points math for premium, discount, and parity.
9. `test_premium_zero_and_invalid`: Division-by-zero protection (`idx == 0`) and non-finite inputs.
10. `test_bybit_tick_snapshot_vs_delta`: Full state replacement on snapshot vs delta key merge.
11. `test_fold_bars_ohlcv_aggregation`: Open, high, low, close, volume aggregation across multiple bars into 2m buckets.
12. `test_fold_bars_day_align_utc_midnight`: UTC midnight alignment verification for 7m bars (`dayAlign=true` vs `dayAlign=false`).

---

## 3. Mutation Testing (Fail-First Verification)

Three distinct scratch mutations were applied to a temporary copy of `live_aid_indicators.js` and verified using `LIVE_AID_JS_PATH`:

1. **Mutation 1 (`mut1_binance_side_inverted`)**:
   - Change: Inverted Binance side logic (`o.S === 'SELL' ? 'short' : 'long'`).
   - Outcome: **FAILED** `test_liq_binance_side_and_usd` (`AssertionError: assert 'short' == 'long'`).
2. **Mutation 2 (`mut2_foldbars_ignore_dayalign`)**:
   - Change: Forced `a = 0` regardless of `dayAlign` flag.
   - Outcome: **FAILED** `test_fold_bars_day_align_utc_midnight` (`AssertionError: assert 1700006280000 == 1700006400000`).
3. **Mutation 3 (`mut3_fundread_pct_scale`)**:
   - Change: Changed percentage multiplier from 100 to 10 (`pct8h: r * 10`).
   - Outcome: **FAILED** `test_fund_read_pct_annual_and_side` and `test_fund_read_falsy_and_malformed` (`AssertionError: assert 0.001 == 0.01`).

All 3/3 scratch mutations failed the test suite as required.

---

## 4. Verification Checkpoints

- Target `.js` files remain unmodified (`git status` confirms `live_aid_indicators.js` is clean).
- No changes made to `scripts/dev/extra_tests.tsv` or task card json files (left to parent agent per scope instructions).
- Pytest suite executes and passes 12/12 tests cleanly.
