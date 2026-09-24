# SAMPLE PIPELINE OUTPUT — BTCUSDT
# Date: 2026-08-22T11:18:31Z
# Source: BinanceDataFeed JSON snapshot + Tom Vorwald rules from 47 FRESH extractions
# Purpose: Demonstrate what the MTS decision engine produces from raw data + Tom's rules.
# Note: This is a SAMPLE output for validation. Not a live trade recommendation.

---

## STEP 0: DATA QUALITY GATE

| Check | Result | Action |
|-------|--------|--------|
| VP confidence | MEDIUM | [FLAG] Visual validation required. "True VP requires tick-level L2 data. POC/VAH/VAL may deviate 0.2-0.5% from CoinGlass" |
| CVD confidence | MEDIUM | [FLAG] Visual validation required. "takerBuyBaseAssetVolume" is not true tick-level delta. |
| VWAP confidence | MEDIUM | [FLAG] Visual validation required. "Binance 1m OHLCV approximation." |
| Liquidation status | accumulator_not_connected | [FLAG] Missing data. Cannot evaluate liquidation clusters. |
| Alignment pass | true | [OK] All timeframe closes aligned. |

**Verdict:** 4 of 13 data blocks require visual validation. Proceed with tri-state logic (TRUE / FALSE / UNKNOWN).

---

## STEP 1: MARKET STATE CLASSIFICATION

### 1.1 Volume Profile Analysis

| Field | Value | Tom Rule Applied |
|-------|-------|-----------------|
| VP shape | B (balanced) | Tom: "Sideways means that supply and demand are in balance." (BVpYGKz9PBU, T1, [BEGINNING]) |
| Price vs POC | Below (76846 vs 77154) | Tom: "Where high volume occurs, we often see a reaction when a market returns there." (NkQeOVDTAec, T4, [BEGINNING]) |
| Price vs VA | Inside (VAL 76663 < Price 76846 < VAH 77344) | Tom: "I can definitely look for short trades up here and long trades down here" when in balance. (BVpYGKz9PBU, T1, [BEGINNING]) |

**State inference:** Market is in balance (B profile). Price is inside the value area, below POC.
**Gap:** Tom does not specify what "B" shape means formally. The screener's shape classification is heuristic.

### 1.2 VWAP Analysis

| Field | Value | Tom Rule Applied |
|-------|-------|-----------------|
| VWAP price | 77004.01 | Tom: "The VWAP shows us nothing other than the volume weighted average price of today." (43JaKHRvxHk, T4, [BEGINNING]) |
| Price vs VWAP | Below (76846 vs 77004) | Tom: "If the price is below it, they're initially more bearishly inclined." (43JaKHRvxHk, T1, [BEGINNING]) |
| VWAP slope | Falling (-0.22%) | Tom: "Should the VWAP suddenly start to go lower and lower... probability increases that a trend continuation downwards will occur." (43JaKHRvxHk, T4, [END]) |

**State inference:** VWAP is falling. Price is below VWAP. This suggests bearish bias.
**BUT:** Tom's Rule 1 for VWAP: "The VWAP must be based on a trend. Only then can I see if I might enter my trade based on counter trades on this VWAP." (43JaKHRvxHk, T5, [BEGINNING])
**Conflict:** VP says balanced. VWAP says falling (possible trend). These signals contradict.
**Resolution:** The higher timeframe (weekly/daily) must be checked. The JSON provides closes but not profiles. Visual validation required.

### 1.3 CVD Analysis

| Field | Value | Tom Rule Applied |
|-------|-------|-----------------|
| CVD slope | Falling | Tom: CVD alone = 50% random. Requires CVD + structural level. (state.md Decisions Log, 2026-08-04) |
| Divergence | false | No divergence = no reversal signal. CVD aligned with price direction. |
| Last 3 deltas | [negative, positive, negative] | Mixed. No clear sustained delta pattern. |

**State inference:** CVD falling with price = aligned, not divergent. No reversal signal from CVD.
**Gap:** Tom's CVD rules are from y67l86cSqb8. The screener's CVD is approximated from taker buy volume, not true tick delta.

### 1.4 Order Book Analysis

| Field | Value | Tom Rule Applied |
|-------|-------|-----------------|
| Bid/Ask ratio | 0.65 | More ask depth than bid depth within 1%. Selling pressure present. |
| Bid depth 1% | 1,484,167 | — |
| Ask depth 1% | 2,287,228 | — |

**State inference:** Selling pressure present at current price. But this is a snapshot, not proof of rejection at a structural level.
**Gap:** Tom does not quantify "large" orders or "thin" liquidity. The 1% depth metric is a screener invention.

### 1.5 Market State Verdict

| State | Evidence | Confidence |
|-------|----------|------------|
| Balance | VP shape = B. Price inside VA. | MEDIUM — VP is approximated. |
| Possible down trend | VWAP falling. Price below VWAP. CVD falling. Book shows selling pressure. | LOW — VP contradicts trend. Need higher TF confirmation. |
| Range | Price between VAL and VAH, not at boundary. | MEDIUM — but range boundaries are approximate. |

**Final state label: BALANCE WITH BEARISH VWAP DIVERGENCE**
**Rationale:** The volume profile says balance. The VWAP says falling. In Tom's framework, the higher timeframe profile wins. Without weekly/daily profile confirmation, the state is ambiguous.
**Action:** [FLAG] Requires visual validation of weekly + daily volume profiles on CoinGlass.

---

## STEP 2: ZONE MAP

### 2.1 Key Levels from JSON

| Level | Price | Distance from Price | Tom Relevance |
|-------|-------|---------------------|---------------|
| VAH | 77344.8 | +499 | Upper boundary of balance. Counter-trade short zone. |
| POC | 77154.37 | +308 | Point of control. Fair price. |
| VWAP | 77004.01 | +158 | Volume-weighted average. Dynamic reference. |
| Price | 76846.1 | 0 | Current price. |
| VAL | 76663.24 | -183 | Lower boundary of balance. Counter-trade long zone. |
| -1 sigma | 76793.71 | -52 | VWAP band. Not from Tom. |
| -2 sigma | 76583.41 | -263 | VWAP band. Not from Tom. |
| Naked POC (Aug 3) | 63155.87 | -13690 | Far liquidity magnet. Not relevant for intraday. |
| Unfilled FVG (bearish) | 76896.9–76901.0 | +51 | Small bearish gap above price. |

### 2.2 Price Position Relative to Fair Value

Tom: "The VWAP shows us nothing other than the volume weighted average price of today. That means with the VWAP, I'm able to see where I am right now relative to the average volume of today." (43JaKHRvxHk, T4, [BEGINNING])

- Price (76846) is BELOW VWAP (77004) = below average volume price = bearish bias.
- Price (76846) is BELOW POC (77154) = below most-traded price = not at fair value.
- Price (76846) is ABOVE VAL (76663) = above lower boundary of balance = not at support.

**Zone verdict:** Price is in "no man's land" — below fair value (POC/VWAP) but above support (VAL). Not at a clear reaction zone.
**Gap:** Tom does not specify how far from a level is "close enough" for a setup. The 183-point distance to VAL and 308-point distance to POC are within normal intraday ranges for BTC, but Tom gives no numeric threshold.

---

## STEP 3: SETUP CONDITION ENGINE

### 3.1 Counter-Trade Short (at VAH)

| Condition | Status | Reasoning |
|-----------|--------|-----------|
| Market in balance | TRUE | VP shape = B. Tom: "Sideways means supply and demand are in balance." (BVpYGKz9PBU, T1) |
| Price at upper boundary | FALSE | Price is 76846, VAH is 77344. Price is ~500 points below VAH. Not at rejection level. |
| Proof of rejection | UNKNOWN | No footprint data. No candlestick pattern in JSON. No divergence. |

**Verdict:** [FALSE] Price not at VAH. Counter-trade short requires price to reach the upper boundary of balance first.

### 3.2 Counter-Trade Long (at VAL)

| Condition | Status | Reasoning |
|-----------|--------|-----------|
| Market in balance | TRUE | VP shape = B. |
| Price at lower boundary | FALSE | Price is 76846, VAL is 76663. Price is 183 points above VAL. Not at support level. |
| Proof of rejection | UNKNOWN | No proof data available in JSON. |

**Verdict:** [FALSE] Price not at VAL. Counter-trade long requires price to reach the lower boundary of balance first.

### 3.3 Trend Continuation Short

| Condition | Status | Reasoning |
|-----------|--------|-----------|
| Trend established | UNKNOWN | VWAP falling + price below VWAP + CVD falling = bearish alignment. BUT VP shape = B (balance), contradicting trend. |
| Pullback to fair zone | FALSE | Price is already below VWAP and POC. Not a pullback to fair zone; it's already below fair value. |
| Proof of continuation | UNKNOWN | No footprint data. No setup formation. |

**Verdict:** [UNKNOWN] Contradictory signals. VP says balance. VWAP/CVD say possible trend down. Need higher timeframe confirmation.
**Tom rule:** "You should then definitely only look for a trend continuation setup here." (43JaKHRvxHk, T5) — but "here" means in a trending market. The VP says this is not trending.

### 3.4 Scalp (short at VWAP band, long at VWAP band)

| Condition | Status | Reasoning |
|-----------|--------|-----------|
| VWAP sideways | FALSE | VWAP slope = falling (-0.22%). Not sideways. |
| Market non-trend | FALSE | VP says balance, but VWAP says falling. Ambiguous. |

**Verdict:** [FALSE] Tom: "Only if the VWAP is currently oriented sideways... then I can use this whole model." (43JaKHRvxHk, T5) VWAP is falling. Scalp mode invalid.

### 3.5 Breakout

| Condition | Status | Reasoning |
|-----------|--------|-----------|
| Range break | FALSE | Price is inside VA (76663–77344). Not at boundary. No break. |
| Volume confirmation | UNKNOWN | No volume spike data in JSON. |

**Verdict:** [FALSE] Price not at range boundary. No breakout setup.

---

## STEP 4: PROOF & VISUAL GATE

### 4.1 What the JSON Cannot Provide (Visual Validation Required)

| Missing Data | Why It Matters | Required Screenshot |
|--------------|---------------|---------------------|
| Weekly volume profile | Tom's Step 1-2: weekly profile sets macro context. Is the weekly trend up, down, or balanced? | CoinGlass BTCUSDT 1W VP |
| Daily volume profile | Tom's Step 3-4: daily profile sets context. Is today balanced or trending? | CoinGlass BTCUSDT 1D VP |
| Footprint chart | Tom: "Is the seller up there or not?" Proof of rejection requires footprint (finished/unfinished auction, delta). | CoinGlass BTCUSDT 15m or 5m footprint |
| True multi-exchange VP | Screener VP is Binance-only 1m OHLCV. CoinGlass aggregates Binance+Bybit+OKX. | CoinGlass BTCUSDT VP (any TF) |
| Liquidation heatmap | Crypto-specific. Shows where leveraged positions would be liquidated. | CoinGlass BTCUSDT liquidation map |
| Higher timeframe CVD | Screener CVD is 1m approximated. True CVD/delta requires tick data. | CoinGlass BTCUSDT CVD (4H or 1H) |

### 4.2 What Would Change the Verdict

| If Visual Validation Shows... | Then Setup Becomes... |
|-------------------------------|----------------------|
| Weekly profile = uptrend, daily = balance | Counter-trade long at VAL becomes valid if price reaches VAL with proof |
| Weekly profile = downtrend, daily = balance | Counter-trade short at VAH becomes valid if price reaches VAH with proof |
| Daily profile = trending down, VWAP falling confirmed | Trend continuation short becomes valid on pullback to VWAP/POC |
| Footprint shows finished auction at VAH or VAL | Proof condition becomes TRUE for respective counter-trade |
| Footprint shows absorption at current price | Possible early entry, but Tom prefers patience: "Counter trades take time." (BVpYGKz9PBU, T1) |

---

## STEP 5: RISK & TRADE PLAN OUTPUT

### 5.1 Trade Plan

| Field | Value | Reason |
|-------|-------|--------|
| Setup name | NONE | No setup conditions met per Tom's rules. |
| Direction | — | — |
| Entry zone | — | — |
| Stop loss | — | — |
| Target | — | — |
| Invalidation | — | — |
| Net R:R | — | — |
| Position size | — | — |
| Confidence | 0% | No valid setup. |

### 5.2 No-Trade Justification

Tom: "Counter trades take time. And now there are two ways to trade this price area... I can wait for the market to make a pullback. It returns again to this price area of the value area. We have to remember that was our location and that's the absolute alpha." (BVpYGKz9PBU, T1, [MIDDLE])

Current price (76846) is not at "our location" (VAH 77344 or VAL 76663). It is in the middle of the value area. Tom would wait.

Tom: "I need an idea for a route plan and I need proof that this idea should be put into action right now. The proof is always the setup that I expect to see there." (NkQeOVDTAec, T4, [MIDDLE])

No proof is present in the data. No setup formation. No divergence. No rejection at a level.

### 5.3 What to Watch For

| Condition to Monitor | Trigger for Re-evaluation |
|----------------------|---------------------------|
| Price reaches VAH (77344) | Evaluate counter-trade short with proof requirement |
| Price reaches VAL (76663) | Evaluate counter-trade long with proof requirement |
| Price breaks below VAL with volume | Evaluate breakout short (if trend confirmed on higher TF) |
| Price breaks above VAH with volume | Evaluate breakout long (if trend confirmed on higher TF) |
| VWAP slope changes to flat | Evaluate scalp mode (if price oscillates around VWAP) |
| CVD divergence appears | Evaluate reversal setup at nearest structural level |

---

## STEP 6: CRYPTO ADAPTATIONS APPLIED

| Adaptation | Data Used | Tom Relevance |
|-----------|-----------|---------------|
| Funding rate | 0.0001, not extreme | Tom never mentions funding. Labeled as non-Tom. |
| Open interest | 106587 | Tom never mentions OI. Labeled as non-Tom. |
| Long/short ratio | 0.99 (balanced) | Tom never mentions L/S ratio. Labeled as non-Tom. |
| Liquidation clusters | Not available | Tom never mentions liquidations. Labeled as non-Tom. |

**Note:** These crypto-specific metrics are NOT used to justify the no-trade verdict. They are noted for context only. The verdict is based solely on Tom's rules (VP, VWAP, CVD, proof).

---

## TRACEABILITY TABLE — Rules Used in This Output

| # | Rule | Tier | Source GPS | Exact Quote (First 80 chars) |
|---|------|------|------------|------------------------------|
| 1 | Sideways = balance | T1 | BVpYGKz9PBU [BEGINNING] | "Sideways means that supply and demand are in balance..." |
| 2 | Short at top, long at bottom of balance | T1 | BVpYGKz9PBU [BEGINNING] | "I can definitely look for short trades up here and long trades down here..." |
| 3 | VWAP = volume weighted average price | T4 | 43JaKHRvxHk [BEGINNING] | "The VWAP shows us nothing other than the volume weighted average price..." |
| 4 | VWAP must be based on trend | T5 | 43JaKHRvxHk [BEGINNING] | "first rule, very important, the VWAP must be based on a trend..." |
| 5 | VWAP falling = trend continuation down probability | T4 | 43JaKHRvxHk [END] | "Should the VWAP suddenly start to go lower and lower..." |
| 6 | Price below VWAP = bearish | T1 | 43JaKHRvxHk [BEGINNING] | "If the price is below it, they're initially more bearishly inclined..." |
| 7 | Scalper only with sideways VWAP | T5 | 43JaKHRvxHk [MIDDLE] | "Only if the VWAP is currently oriented sideways..." |
| 8 | High volume = reaction zone | T4 | NkQeOVDTAec [BEGINNING] | "where high volume occurs, we often see a reaction when a market returns..." |
| 9 | IDEA + PROOF framework | T4 | NkQeOVDTAec [BEGINNING] | "we need an idea... and in the second step, we need proof..." |
| 10 | Need both idea and proof | T4 | NkQeOVDTAec [MIDDLE] | "I always need both and that's very important for me to tell you again..." |
| 11 | Counter trades take time | T1 | BVpYGKz9PBU [MIDDLE] | "Counter trades take time. And now there are two ways to trade..." |
| 12 | Wait for pullback to value area | T1 | BVpYGKz9PBU [MIDDLE] | "I can wait for the market to make a pullback. It returns again to this price area..." |
| 13 | CVD alone = 50% random | T3 | state.md Decisions Log | From 5-LLM research, 2026-08-04. |
| 14 | Stop loss + target mandatory | T5 | WSCIURybK3U [MIDDLE] | "That means you need a stop loss, and you need a predefined target..." |
| 15 | Reference values mandatory | T5 | WSCIURybK3U [MIDDLE] | "Without reference values, there's no chance of surviving in trading..." |

---

## GAPS DOCUMENTED IN THIS OUTPUT

1. **VP shape classification:** Tom mentions "B profile" in examples but gives no formal rules. The screener's "B" classification is heuristic.
2. **Distance threshold:** Tom does not specify how far from VAH/VAL/POC is "close enough" for a setup. The 183-point distance to VAL is within normal BTC intraday range, but Tom gives no number.
3. **VWAP slope threshold:** Tom says "very steep" but does not quantify. The -0.22% slope is labeled "falling" by the screener, but this threshold is arbitrary.
4. **Higher timeframe dependency:** Tom's 13-step framework starts with weekly and daily profiles. The JSON provides closes but not profiles. The state classification is incomplete without them.
5. **Proof signal specifics:** Tom says "wait until market shows no more liquidity" and "is the seller up there or not" but gives no specific footprint criteria for the JSON-only case.
6. **FVG relevance:** Tom's FVG rules are from one video only. The unfilled bearish FVG at 76896-76901 is noted but not used in the verdict due to insufficient cross-video validation.
7. **Book depth interpretation:** Tom does not quantify bid/ask imbalance. The 0.65 ratio is noted as selling pressure but not used as a standalone signal.

---

# END OF SAMPLE PIPELINE OUTPUT
# Status: SAMPLE — For JISHU review and validation before system build.
# Verdict: NO TRADE. Price not at structural level. No proof. Contradictory signals (balance vs falling VWAP).
