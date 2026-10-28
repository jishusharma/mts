# DATA SCHEMA v1.2.0 — MTS Decision System
# Date: 2026-08-29
# Source: sample_btc_snapshot.json (BinanceDataFeed v1.2.0 output)
# DSA_TASK_007 STATUS: COMPLETE — All fields confirmed live
# Purpose: Document every field the Java screener produces so that decision rules are built against real data, not imagined fields.
# Scope: BTCUSDT snapshot from 2026-08-22T11:18:31Z. Schema is designed to be extensible to any symbol.

---

## TOP-LEVEL METADATA

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| timestamp_utc | string (ISO 8601) | Snapshot generation time | 2026-08-22T11:18:31.374447600Z |
| asset | string | Trading pair symbol | BTCUSDT |
| data_source | string | Exchange and data type | binance_futures_public |
| screener_version | string | Java screener version | 1.2.0 |
| generation_ms | integer | Time to generate snapshot (ms) | 1887 |
| alignment_pass | boolean | All timeframe closes align within tolerance | true |

---

## METADATA BLOCK — Data Quality Disclaimers

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| disclaimer | string | Global disclaimer | "This is a watchlist screener..." |
| vp_confidence | string enum | Volume profile reliability | MEDIUM |
| vp_source | string | How VP was computed | "Binance 1m OHLCV approximation" |
| cvd_confidence | string enum | CVD reliability | MEDIUM |
| cvd_source | string | How CVD was computed | "Binance kline takerBuyBaseAssetVolume" |
| vwap_confidence | string enum | VWAP reliability | MEDIUM |
| vwap_source | string | How VWAP was computed | "Binance 1m OHLCV" |

**Rule:** Any field with confidence != HIGH must be flagged for visual validation.
**Rule:** Any field with "approximation" in source must be flagged for CoinGlass verification.

---

## DATA BLOCK — current_price

| Field | Type | Description | Example | Visual Validation Needed? |
|-------|------|-------------|---------|--------------------------|
| current_price | float | Last traded price | 76846.1 | NO — direct from exchange |

---

## DATA BLOCK — multi_timeframe

| Field | Type | Description | Example | Visual Validation Needed? |
|-------|------|-------------|---------|--------------------------|
| close_alignment_check | array of objects | Close prices across 7 timeframes with drift check | see below | NO — computed from exchange |

**close_alignment_check object fields:**

| Sub-field | Type | Description | Example |
|-----------|------|-------------|---------|
| timeframe | string enum | 1w, 1d, 4h, 1h, 15m, 5m, 1m | 1w |
| close | float | Closing price for that timeframe | 76866.1 |
| close_time_utc | string (ISO 8601) | Candle close time | 2026-08-23T23:59:59.999Z |
| drift_from_1m | float | Price drift vs 1m close | 0.0 |
| aligned | boolean | Within tolerance | true |

**Tom relevance:** Tom uses weekly profile for macro context, daily for context, 1h/15m for setup, 5m/1m for entry. The alignment check ensures timeframe consistency.
**Gap:** Tom does not specify a "drift tolerance" for multi-timeframe alignment. This is a screener convenience, not a Tom rule.

---

## DATA BLOCK — volume_profile

| Field | Type | Description | Example | Visual Validation Needed? |
|-------|------|-------------|---------|--------------------------|
| poc | float | Point of Control (highest volume price) | 77154.37 | YES — "may deviate 0.2-0.5% from CoinGlass" |
| vah | float | Value Area High (upper boundary) | 77344.8 | YES — same approximation warning |
| val | float | Value Area Low (lower boundary) | 76663.24 | YES — same approximation warning |
| hvns | array of floats | High Volume Nodes (sub-POC peaks) | [77299.7, 77264.62, 77134.32] | YES |
| lvns | array of floats | Low Volume Nodes (gaps in profile) | [76768.49, 76999.01, 77014.05] | YES |
| shape | string enum | Profile shape: TWOPEAK=bell/two-peak, D=distribution, P=one-sided. Tom's B (weakness at extreme) is NOT computed by any rule. | TWOPEAK | YES — shape classification is heuristic |
| confidence | string enum | Data reliability | MEDIUM | — |
| source | string | Computation method | "Binance 1m OHLCV approximation" | — |
| approximation_warning | string | Human-readable warning | "True VP requires tick-level L2 data..." | — |

**Tom relevance:**
- Tom: "where high volume occurs, we often see a reaction when a market returns there" (NkQeOVDTAec, T4)
- Tom: "I can definitely look for short trades up here and long trades down here" when market is in balance (BVpYGKz9PBU, T1)
- Tom: "I need an idea for a route plan" — the idea comes from volume nodes (NkQeOVDTAec, T4)

**Gap:** Tom does not specify bar type, lookback period, or session settings for volume profile. The screener uses Binance 1m OHLCV with an unspecified lookback.
**Gap:** Tom does not define what counts as "high volume" vs "low volume" numerically. HVN/LVN classification is screener heuristic.
**Gap:** Tom mentions "B profile" (top-heavy weakness) and "P profile" in examples but does not give formal shape classification rules. Current shape field emits TWOPEAK, not Tom's B.

---

## DATA BLOCK — vwap

| Field | Type | Description | Example | Visual Validation Needed? |
|-------|------|-------------|---------|--------------------------|
| price | float | Current VWAP value | 77004.01 | YES — "Binance 1m OHLCV" approximation |
| sigma | float | Standard deviation of price from VWAP | 210.3 | YES — computed from approximated data |
| bands | object | +/- 1/2/3 sigma bands | see below | YES |
| slope | string enum | rising / falling / flat | falling | YES — slope classification is heuristic |
| slope_pct | float | Slope as percentage | -0.0022 | YES — threshold not defined by Tom |
| confidence | string enum | Data reliability | MEDIUM | — |
| source | string | Computation method | "Binance 1m OHLCV" | — |

**bands object fields:**

| Sub-field | Type | Description | Example |
|-----------|------|-------------|---------|
| +1? | float | +1 sigma band | 77214.32 |
| +2? | float | +2 sigma band | 77424.62 |
| +3? | float | +3 sigma band | 77634.92 |
| -1? | float | -1 sigma band | 76793.71 |
| -2? | float | -2 sigma band | 76583.41 |
| -3? | float | -3 sigma band | 76373.11 |

**Note (BUG #6 CLOSED):** DSA outputs band keys with Unicode artifacts (`+1?` instead of `+1sigma`). Engine reads band values generically by position, not by key name. No runtime impact. DSA key format is stable.

**Tom relevance:**
- Tom: "The VWAP shows us nothing other than the volume weighted average price of today" (43JaKHRvxHk, T4)
- Tom: "VWAP must be based on a trend. Only then can I see if I might enter my trade based on counter trades on this VWAP" (43JaKHRvxHk, T5)
- Tom: "If the VWAP suddenly starts to go lower and lower... probability increases that a trend continuation downwards will occur" (43JaKHRvxHk, T4)
- Tom: "You can define so-called price ranges from the VWAP where you expect a reaction" (43JaKHRvxHk, T4)

**Gap:** Tom never mentions standard deviation bands. The +/-1/2/3 sigma bands are a screener addition, not from Tom.
**Gap:** Tom says "very steep" VWAP but does not quantify steepness. The slope_pct field is a screener heuristic.
**Gap:** Tom says VWAP resets daily. Crypto trades 24/7 — the "daily" boundary is arbitrary in crypto. This is a crypto adaptation, not a Tom rule.
**Gap:** Tom does not specify timeframe for VWAP. The screener uses intraday VWAP from 1m data.

---

## DATA BLOCK — cvd

| Field | Type | Description | Example | Visual Validation Needed? |
|-------|------|-------------|---------|--------------------------|
| value | float | Cumulative delta value | -2018.985 | YES — "takerBuyBaseAssetVolume" is not true delta |
| slope | string enum | rising / falling | falling | YES — from approximated data |
| divergence | boolean | Price and CVD moving opposite directions | false | YES — divergence detection is heuristic |
| last_3_delta | array of strings | Direction of last 3 bars | ["negative", "positive", "negative"] | YES |
| confidence | string enum | Data reliability | MEDIUM | — |
| source | string | Computation method | "Binance kline takerBuyBaseAssetVolume" | — |

**Tom relevance:**
- Tom discusses CVD in y67l86cSqb8 (CVD Strategy video)
- Tom: CVD alone = 50% random. Now requires CVD + structural level (state.md Decisions Log, 2026-08-04)

**Gap:** Tom's CVD discussion is on the CVD Strategy video (y67l86cSqb8). The screener's CVD is computed from taker buy volume, not true tick-level delta. This is a significant approximation.
**Gap:** Tom does not define "divergence" numerically. The boolean flag is a screener heuristic.
**Crypto adaptation:** CVD is used in crypto as a proxy for order flow delta. Tom uses true footprint delta on futures. The screener's CVD is a crypto hack.

---

## DATA BLOCK — fvg

| Field | Type | Description | Example | Visual Validation Needed? |
|-------|------|-------------|---------|--------------------------|
| fvg | array of objects | Fair Value Gaps detected | see below | YES — FVG detection algorithm is screener-specific |

**fvg object fields:**

| Sub-field | Type | Description | Example |
|-----------|------|-------------|---------|
| type | string enum | bullish / bearish | bearish |
| top | float | Upper boundary of gap | 76901.0 |
| bottom | float | Lower boundary of gap | 76896.9 |
| filled | boolean | Has price returned to fill the gap? | false |
| start_time_utc | string (ISO 8601) | When the gap formed | 2026-08-22T11:13:00Z |

**Tom relevance:**
- Tom discusses FVG in Fj4FDZQxw0I (The ONLY Fair Value Gap Video)
- 5-LLM research found FVG has zero academic backing (state.md Decisions Log, 2026-08-04)
- FVG is used in crypto as a structural level marker

**Gap:** Tom's FVG rules are from one video. No cross-video validation.
**Gap:** Tom does not specify FVG detection algorithm (lookback, minimum gap size, etc.). The screener's FVG detection is a black box.
**Crypto adaptation:** FVG is more commonly used in crypto than in Tom's DAX/futures teaching.

---

## DATA BLOCK — naked_poc

| Field | Type | Description | Example | Visual Validation Needed? |
|-------|------|-------------|---------|--------------------------|
| naked_pocs | array of objects | POCs from prior sessions not yet revisited | see below | YES — requires multi-day VP which screener may not have |
| visited_pocs | array of objects | POCs that have been revisited | [] | YES |

**naked_pocs object fields:**

| Sub-field | Type | Description | Example |
|-----------|------|-------------|---------|
| date | string (YYYY-MM-DD) | Session date of the POC | 2026-08-03 |
| poc | float | POC price level | 63155.87 |

**Tom relevance:**
- Tom mentions "naked POC" concept in some videos as a liquidity magnet
- A naked POC that is far from current price can act as a target for large moves

**Gap:** Tom does not give formal rules for naked POC trading. The concept is mentioned but not systematized.
**Gap:** The screener only shows 2 naked POCs (Aug 3 and Aug 22). Tom would look at weekly/daily profiles for a fuller picture.

---

## DATA BLOCK — liquidation [DEPRECATED 2026-09-12]
# Fields retained for backward compat. Consumers MUST NOT read. Source endpoint returned 404.

| Field | Type | Description | Example | Visual Validation Needed? |
|-------|------|-------------|---------|--------------------------|
| status | string enum | Data availability | accumulator_not_connected | YES — no data available |
| clusters | array of objects | Liquidation cluster levels | [] | YES |

**Tom relevance:**
- Tom does not discuss liquidation clusters. This is a crypto-specific concept.
- CoinGlass provides liquidation heatmaps which are valuable in crypto.

**Crypto adaptation:** Liquidation data is entirely a crypto addition. Tom never mentions it.
**Gap:** When status is "accumulator_not_connected", the engine must flag this as missing data, not as "no liquidation clusters exist."

---

## DATA BLOCK — order_book_depth

| Field | Type | Description | Example | Visual Validation Needed? |
|-------|------|-------------|---------|--------------------------|
| bid_depth_1pct | integer | Total bid volume within 1% of price | 1484167 | NO — direct from exchange API |
| ask_depth_1pct | integer | Total ask volume within 1% of price | 2287228 | NO — direct from exchange API |
| bid_ask_ratio | float | bid_depth / ask_depth | 0.65 | NO — computed from direct data |
| confidence | string enum | Data reliability | HIGH | — |
| source | string | API endpoint | "Binance /fapi/v1/depth limit=100" | — |

**Tom relevance:**
- Tom discusses order book in vl01TiVTuoQ (Master Orderflow) and oa8kxSLLkAo (Footprint)
- Tom: "Is the seller up there or not" (BVpYGKz9PBU, T1)
- Book depth imbalance can indicate directional pressure

**Gap:** Tom does not quantify "large" orders or "thin" liquidity. The 1% depth metric is a screener invention.
**Gap:** Tom uses Level 2 order book in real-time. The screener provides a snapshot with limit=100, which may not capture full depth.
**Crypto adaptation:** Order book depth is more relevant in crypto due to fragmented liquidity across exchanges.

**Engine note:** The engine references ONLY `bid_ask_ratio` for order book proof. `bid_depth_1pct` and `ask_depth_1pct` are raw inputs; `bid_ask_ratio` is the derived metric. No expanded thresholds (0.1%, 0.2%, 0.5%) are in the schema or referenced by the engine. If DSA adds them in the future, they require engine integration review per Rule 31 (validate before fix).

---

## DATA BLOCK — setup_alerts

| Field | Type | Description | Example | Visual Validation Needed? |
|-------|------|-------------|---------|--------------------------|
| setup_alerts | array of objects | Screener-generated condition flags | see below | YES — all alerts require visual validation |

**setup_alerts object fields:**

| Sub-field | Type | Description | Example |
|-----------|------|-------------|---------|
| setup | string | Old setup code (S01, S04, S05) | S01 |
| symbol | string | Asset symbol | BTCUSDT |
| score | integer | Screener heuristic score | 15 |
| requires_visual_validation | boolean | Always true in current screener | true |
| reason | string | Human-readable alert reason | "Balanced VP (B). VP rejection candidate." |
| confidence | string enum | Screener confidence | MEDIUM |

**CRITICAL NOTE:** These are old setup codes (S01/S04/S05) that the user has instructed to discard. The screener should be updated to output raw condition flags instead. See java_screener_spec.md (future phase).

**Tom relevance:**
- Tom does not use setup codes or scores. He uses IDEA + PROOF framework.
- Tom: "Setups are only point 8 of 13" (Ld1dhjGdTCA, T4)
- The alerts are screener heuristics, not Tom-validated setups.

---

## DATA BLOCK — funding

| Field | Type | Description | Example | Visual Validation Needed? |
|-------|------|-------------|---------|--------------------------|
| current_rate | float | Funding rate | 0.0001 | NO — direct from exchange |
| extreme | boolean | Is rate extreme? | false | YES — "extreme" threshold is screener heuristic |
| confidence | string enum | Data reliability | HIGH | — |
| source | string | API endpoint | "Binance /fapi/v1/premiumIndex" | — |

**Tom relevance:**
- Tom NEVER mentions funding rates. This is a crypto-specific concept.
- Funding rates indicate sentiment: positive = longs pay shorts (bullish), negative = shorts pay longs (bearish).

**Crypto adaptation:** Funding is a crypto-only filter. Must be labeled as non-Tom.
**Gap:** Tom does not define what "extreme" funding means. The boolean flag is a screener heuristic.

---

## DATA BLOCK — open_interest

| Field | Type | Description | Example | Visual Validation Needed? |
|-------|------|-------------|---------|--------------------------|
| value | float | Open interest in contracts | 106587.626 | NO — direct from exchange |
| confidence | string enum | Data reliability | HIGH | — |
| source | string | API endpoint | "Binance /fapi/v1/openInterest" | — |

**Tom relevance:**
- Tom NEVER mentions open interest. This is a crypto-specific concept.
- OI indicates market participation. Rising OI + rising price = new money entering longs.

**Crypto adaptation:** OI is a crypto-only metric. Must be labeled as non-Tom.

---

## DATA BLOCK — long_short_ratio

| Field | Type | Description | Example | Visual Validation Needed? |
|-------|------|-------------|---------|--------------------------|
| ratio | float | Long accounts / Short accounts | 0.9912 | NO — direct from exchange |
| confidence | string enum | Data reliability | HIGH | — |
| source | string | API endpoint | "Binance /futures/runtime_data/globalLongShortAccountRatio" | — |

**Tom relevance:**
- Tom NEVER mentions long/short ratios. This is a crypto-specific concept.
- Ratio < 1 = more short accounts than long accounts (bearish sentiment)
- Ratio > 1 = more long accounts than short accounts (bullish sentiment)

**Crypto adaptation:** L/S ratio is a crypto-only sentiment filter. Must be labeled as non-Tom.

---

## DATA BLOCK — conditions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| cvd_trade_flow_aligned | boolean | True if CVD slope and trade_flow.net_delta agree in direction | true |
| price_vs_poc | string enum | "above", "below", "at", "in_va" | "below" |
| fvg_unfilled_count | integer | Number of unfilled Fair Value Gaps | 2 |
| funding_reset_window | boolean | True if within 30 min of 00:00/08:00/16:00 UTC | false |
| speed_picking_up | boolean | True if 15m ATR > 2x daily average or last 3 candles show acceleration | false |

**Tom relevance:** None — all are system inventions for automation.
**Added:** DSA_TASK_003 (cvd_trade_flow_aligned, speed_picking_up) + system (price_vs_poc, fvg_unfilled_count, funding_reset_window).

---

## DATA BLOCK — trade_flow

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| net_delta | float | Net aggressive buy/sell delta | -1.954 |
| last_3_delta | array of floats | Delta for last 3 candles | [-0.8, -0.5, -0.654] |

**Tom relevance:** Tom uses delta/flow as proof of aggressive buyers/sellers. `last_3_delta` resolves CVD/flow contradictions.
**Added:** DSA_TASK_003.

---

## DATA BLOCK — structure

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| stale | boolean | True if swing levels may be stale | false |
| swing_low | float | Structural swing low (1h/15m/5m) | 77230.0 |
| swing_high | float | Structural swing high (1h/15m/5m) | 78200.0 |

**Tom relevance:** Tom uses "last low" for stop context. Swing levels are structural — valid when confluencing with VP levels.
**Resolution (BUG #3 CLOSED):** `swing_low` is a structural level (matched to zone precision: daily zone -> 1h swing, 4H zone -> 15m swing, scalp -> 5m swing), NOT the candle low. Engine handles this correctly via Swing TF Matching (compiled_engine.md Section 2.4).
**Added:** System (always present).

---

## DATA BLOCK — weekly_vp (UPDATED)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| poc | float | Current week Point of Control | 78850.0 |
| vah | float | Current week Value Area High | 80100.0 |
| val | float | Current week Value Area Low | 77600.0 |
| prior_week_poc | float | Previous week Point of Control | 79500.0 |
| two_week_ago_poc | float | Two weeks ago Point of Control | 80200.0 |

**Tom relevance:** "Rising VPOCs with increasing liquidity indicate a stable, bullish structure." (KEe_CWHyuSg T1)
**Added:** DSA_TASK_007 (prior_week_poc, two_week_ago_poc).

---

## DATA BLOCK — prior_day (UPDATED)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| high | float | Prior day high | 79300.0 |
| low | float | Prior day low | 78100.0 |
| poc | float | Prior day Point of Control | 78700.0 |
| vah | float | Prior day Value Area High | 79000.0 |
| val | float | Prior day Value Area Low | 78400.0 |
| close | float | Prior day closing price | 78250.0 |

**Tom relevance:** "if you combine that with a price range that you've predefined, for example, yesterday's closing price, then that's information that there was a rejection down here" (rrHj24GSR6M T4)
**Added:** DSA_TASK_007 (close). Prior day VAH/VAL/POC already present.

---

## DATA BLOCK — cvd (UPDATED)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| slope | string enum | "rising", "falling", "flat" | "falling" |
| cvd_recent | object | Recent CVD breakdown | see below |

**cvd_recent object fields:**

| Sub-field | Type | Description | Example |
|-----------|------|-------------|---------|
| slope_1h | string enum | 1h CVD slope | "falling" |
| slope_4h | string enum | 4h CVD slope | "falling" |
| delta_1h | float | 1h CVD delta | -45.2 |
| delta_4h | float | 4h CVD delta | -120.5 |

**Tom relevance:** Resolves CVD/trade_flow contradictions. Recent flow reflects current market control; cumulative reflects session context.
**Added:** DSA_TASK_003.

---

## DATA BLOCK — volume_spike_at_level (LIVE — DSA_TASK_007)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| volume_spike_at_level | boolean | True if current volume at price > 2x 4h average at that price level | false |

**Tom relevance:** "absolute exhaustion is seen with a volume spike, or a lot of volume is suddenly generated at one price level" (KEe_CWHyuSg T4)
**Status:** LIVE. Confirmed in snapshot `BTCUSDT_2026-08-29_1787980996935.json`.

---

## VISUAL VALIDATION SUMMARY

| Data Block | Fields Requiring CoinGlass Validation | Reason |
|------------|--------------------------------------|--------|
| volume_profile | poc, vah, val, hvns, lvns, shape | "True VP requires tick-level L2 data. May deviate 0.2-0.5%" |
| vwap | price, sigma, bands, slope, slope_pct | "Binance 1m OHLCV approximation" |
| cvd | value, slope, divergence, last_3_delta | "takerBuyBaseAssetVolume" is not true delta |
| fvg | all fvg objects | Detection algorithm is screener-specific, not Tom-validated |
| naked_poc | all naked_poc objects | Requires multi-day VP; screener may have incomplete history |
| liquidation | all fields | "accumulator_not_connected" = no data |
| setup_alerts | all alerts | Old S01/S04/S05 codes; not Tom-validated |

**Fields that are DIRECT from exchange (HIGH confidence, no visual validation needed):**
- current_price
- multi_timeframe.close_alignment_check
- order_book_depth (bid_depth_1pct, ask_depth_1pct, bid_ask_ratio)
- funding.current_rate
- open_interest.value
- long_short_ratio.ratio

---

## GAPS — WHAT TOM DOES NOT ADDRESS IN EXTRACTED VIDEOS

1. **Exact volume profile settings:** Bar type, lookback period, session settings not specified.
2. **Minimum volume threshold:** No quantified rule for "high volume" vs "low volume."
3. **VWAP standard deviation bands:** Tom never mentions sigma bands.
4. **VWAP slope quantification:** "Very steep" is not defined numerically.
5. **CVD divergence threshold:** No numeric definition of divergence.
6. **FVG detection algorithm:** No rules for minimum gap size or lookback.
7. **Naked POC formal rules:** Mentioned but not systematized.
8. **Funding/OI/L/S ratio:** Tom never mentions these. All are crypto adaptations.
9. **Liquidation clusters:** Tom never mentions this. Crypto-only.
10. **Multi-timeframe drift tolerance:** Tom does not specify what "aligned" means numerically.

---

## DATA BLOCK — setup_candidates (NEW v1.3.0 — DSA_TASK_012)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| setup_candidates | array of objects | Pre-computed setup candidates ranked by score | see below |

**setup_candidates object fields:**

| Sub-field | Type | Description | Example |
|-----------|------|-------------|---------|
| rank | integer | 1 = best candidate | 1 |
| setup_type | string enum | ct_short, ct_long, tc_short, tc_long, bo_short, bo_long, scalp | ct_short |
| direction | string enum | short, long | short |
| zone | object | {name, price, type} | {"name": "pf_vah", "price": 78748.88, "type": "pf_vah"} |
| math | object | {distance_pct, distance_cap, tier, substate, stop, target, gross_rr, net_rr, rr_sanity} | see below |
| proof | object | {rejection_wick, absorption, finished_auction, delta_flip, volume_spike, speed, cvd_aligned, book_imbalance} | see below |
| score | object | {raw, confidence, proof_count, confluence_bonus} | {"raw": 72, "confidence": "B", "proof_count": 3, "confluence_bonus": 10} |

**math object fields:**

| Sub-field | Type | Description | Example |
|-----------|------|-------------|---------|
| distance_pct | float | Distance from price to zone (%) | 0.51 |
| distance_cap | float | Max distance for this zone type (%) | 0.4 |
| tier | string enum | trigger_ready, conditional, ignore | trigger_ready |
| substate | string enum | at_zone, above_zone, below_zone | above_zone |
| stop | float | Stop level | 78774.0 |
| target | float | Target level | 77977.15 |
| gross_rr | float | Gross risk:reward | 5.34 |
| net_rr | float | Net R:R after 25% friction | 4.01 |
| rr_sanity | boolean | gross_rr >= 1.5 | true |

**proof object fields:**

| Sub-field | Type | Description | Example |
|-----------|------|-------------|---------|
| rejection_wick | string enum | NONE, WEAK, MODERATE, STRONG | STRONG |
| absorption | object | {detected, strength, candle_count, vol_ratio} | {"detected": true, "strength": "moderate", "candle_count": 3, "vol_ratio": 3.2} |
| finished_auction | object | {detected, direction, extreme_delta, reversal_delta, follow_through} | {"detected": false} |
| delta_flip | object | {detected, from_negative, at_zone, zone_level, candles_since} | {"detected": true, "from_negative": true, "at_zone": true, "zone_level": 76490.64, "candles_since": 2} |
| volume_spike | object | {detected, magnitude, at_level, level} | {"detected": false} |
| speed | object | {picking_up, score, direction, atr_ratio, consecutive_large} | {"picking_up": false, "score": 3, "direction": "flat", "atr_ratio": 1.1, "consecutive_large": 0} |
| cvd_aligned | boolean | CVD slope aligns with trade_flow.net_delta | false |
| book_imbalance | float | bid_ask_ratio | 0.63 |

**Tom relevance:** All proof types are derived from Tom's 14 proof categories (proof_requirements_formatted.md Section 2). Rejection wick, absorption, finished auction, and delta flip were previously [REQUIRES FOOTPRINT] — now computable from bar-level data.
**Added:** DSA_TASK_012 (all fields).
**Backward compatibility:** DSA emits BOTH old booleans (rejection_wick_at_zone, volume_spike_at_level, speed_picking_up) AND new setup_candidates during transition.

---

# END OF DATA SCHEMA v1.2.0
# Status: ACTIVE — Built from actual BTC JSON snapshot.
# v1.3.0 draft: setup_candidates section added (DSA_TASK_012).


---

## trade_flow (updated 2026-09-11)

| Field | Type | Description |
|-------|------|-------------|
| net_delta_1m | float | Net (buy - sell) taker volume, last 1 minute |
| net_delta_5m | float | Net taker volume, last 5 minutes |
| net_delta_15m | float | Net taker volume, last 15 minutes |
| net_delta_1h | float | Net taker volume, last 1 hour |
| confidence | string | HIGH / LOW |

**Formula:** net_delta per 1m bar = `2 * takerBuyBaseAssetVolume - volume`. Windows sum the last N bars.

**Deprecated 2026-09-11:** `net_delta` (singular) removed. Was based on aggTrades(1000) — fixed-count, not fixed-time. Replaced by multi-window from klines1m.

**Naming note (2026-09-11):** `net_delta_*` measures **Volume Delta summed over N bars** — the same as CoinGlass's "Volume Delta," not their "Net Delta."

CoinGlass distinguishes three things:
- **Volume Delta** = taker buy − taker sell per bar (flow).
- **CVD** = cumulative Volume Delta (flow, accumulated).
- **Net Long / Net Short** = Long Openings − Long Closings / Short Openings − Short Closings (positioning). Confirmed T2 at coinglass.com/learn/net-long-short-en.
- **Net Delta** = not directly defined on any CoinGlass public page. Best available proxy: `Net Longs − Net Shorts` (T3, Leviathan TradingView script). CoinGlass API endpoint `/api/futures/net-position/history` returns `net_position_change_cum`, consistent with the positioning family.

Our field name `net_delta_*` kept for internal continuity — it refers to the flow family, not the positioning family. Not a naming contract with any external system.

---

## CVD anchor vs CoinGlass (confirmed 2026-09-11)

Our `cvd.value` anchors at **00:00 UTC** (session scope).

CoinGlass Cum CVD anchors at the **leftmost visible bar of the chart**.
The same moment on CoinGlass can show three different values depending on
the visible timeframe:

| Timeframe | Visible range | Value at same moment |
|-----------|---------------|---------------------|
| 4H | ~10 days | +40,755 |
| 4H (zoomed) | ~2 days | +36,753 |
| 3m | ~13 hours | −199 |
| **Our JSON** | **00:00 UTC** | **+1,857** |

**All four are correct.** They accumulate from different starting points.

**Rule:** Never compare our `cvd.value` numerically to a CoinGlass CVD
chart unless both anchors are set to the same start time. Directional
sign at the same moment may still differ by the offset — do not use the
sign as a cross-validation either.

**No bug in our code.** Confirmed by arithmetic: chart_3m_value −
our_value = net flow between the two anchors, which matches the visible
chart drop.

---

## order_flow (DSA_TASK_013, added 2026-09-10)

| Field | Type | Description |
|-------|------|-------------|
| trades_per_sec | float | Aggregate trades per second in the current window (last 1000 aggTrades) |
| volume_per_sec | float | Aggregate volume per second in the current window |
| baseline_trades_per_sec | float | Aggregate trades per second in the baseline window (20-15 min ago) |
| baseline_volume_per_sec | float | Aggregate volume per second in the baseline window |
| trades_ratio | float | current trades_per_sec / baseline trades_per_sec |
| volume_ratio | float | current volume_per_sec / baseline volume_per_sec |
| speed_state | string | accelerating / maintaining / decelerating / unknown |
| confidence | string | HIGH / LOW |
| note | string | Provenance and caveats |

### order_flow - DSA_TASK_014 historical baseline fields (added 2026-09-10)

| Field | Type | Description |
|-------|------|-------------|
| historical_baseline_trades_per_sec | float | Median trades/sec across last 30 days of samples (max 100) |
| historical_baseline_volume_per_sec | float | Median volume/sec across last 30 days of samples |
| historical_baseline_samples | int | Sample count used for the median |
| historical_baseline_confidence | string | HIGH (>=20 samples) / MEDIUM (>=5) / LOW (<5) |
| speed_vs_historical | float | current trades_per_sec / historical baseline median |

**Persistence:** `runtime_data/speed_baselines/{symbol}_speed_baseline.json` — rolling 30d window, max 100 samples, one entry appended per snapshot.
**Purpose:** Tom requires per-instrument baselines ("what are their averages?"). This provides the running median for each symbol.
**Engine status:** Not yet consumed by compiled_engine.md.

**Purpose:** Measure Tom's "speed" primitive — order-book / trade interaction rate — not candle range.
**Engine status:** Not yet consumed by compiled_engine.md. Requires Rule 32 validation before any rule reads `speed_state`.
**Caveat:** Current and baseline windows differ in shape (fixed-count vs fixed-time). Compare rates is valid; refine if production begins.
