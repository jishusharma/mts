# INDICATOR AUDIT TABLE — MTS v4.2.0-p3+1
# Date: 2026-08-31
# Status: COMPLETE — Phase 1.0.0 Indicator Audit
# Source Files: indicator_selection_task.md, VVP-001, data_schema_v1.0.md, compiled_engine.md
# Auditor: sys_AI per Protocol I-03

---

## EXECUTIVE SUMMARY

| Metric | Value |
|--------|-------|
| Total indicators audited | 80 |
| Tier 1 (Tom-validated, MUST have) | 4 |
| Tier 2 (MTS-required, SHOULD have) | 4 |
| Tier 3 (Cross-trader context, MAY have) | 2 |
| Tier 4 (Not needed, REMOVE) | 70 |
| DSA-aligned indicators | 10 |
| Visual-chart indicators recommended | 6-8 |
| DSA-only indicators | 4 |

**Key finding:** 87.5% of CoinGlass indicators (70/80) are TIER 4 — redundant, non-Tom, or clutter. The MTS engine needs only 10 indicators (4 T1 + 4 T2 + 2 T3), of which 6-8 should be on the visual chart.

---

## SECTION 1: COMPLETE INDICATOR AUDIT TABLE

### TIER 1 — TOM-VALIDATED, MUST HAVE (4 indicators)
These are non-negotiable. Every screenshot MUST show all Tier 1 indicators.

| # | Indicator | Tom Uses? | Engine Ref? | DSA Emits? | Unique Info? | Actionable? | Placement |
|---|-----------|-----------|-------------|------------|--------------|-------------|-----------|
| 1 | **Volume Profile (VPVR)** | YES — core methodology. POC, VAH, VAL, shape. | YES — zone_identification_rules.md, compiled_engine.md Sections 2-3 | YES — volume_profile (poc, vah, val, hvns, lvns, shape) | YES — primary zone identification, state classification, target selection | YES — determines entry zone, stop, target | Main chart overlay |
| 2 | **VWAP** | YES — business zones, scalp bands, trend confirmation (43JaKHRvxHk, 4MoNjEQ2Dd8) | YES — compiled_engine.md Sections 2.3, 2.5, 3 | YES — vwap (price, sigma, bands, slope, slope_pct) | YES — scalp entries, trend context, stop placement, sigma bands | YES — entry trigger at bands, trend filter | Main chart overlay |
| 3 | **CVD (Cumulative Volume Delta)** | YES — buyer/seller pressure, divergence (y67l86cSqb8) | YES — compiled_engine.md Sections 4-5, proof requirements | YES — cvd (value, slope, divergence, last_3_delta) | YES — proof of buyer/seller presence, divergence detection, trend alignment | YES — primary proof item for entry verdict | Separate panel |
| 4 | **Net Delta / Delta** | YES — per-candle order flow, absorption detection (oa8kxSLLkAo, y67l86cSqb8) | YES — compiled_engine.md Sections 4-5, trade_flow block | YES — trade_flow (net_delta, last_3_delta) | YES — absorption, rejection, finished auction detection | YES — primary proof item, trigger validation | Separate panel |

### TIER 2 — MTS-REQUIRED, SHOULD HAVE (4 indicators)
These are crypto-specific additions that the engine references. Include if panel space allows.

| # | Indicator | Tom Uses? | Engine Ref? | DSA Emits? | Unique Info? | Actionable? | Placement |
|---|-----------|-----------|-------------|------------|--------------|-------------|-----------|
| 5 | **Open Interest (Aggregated, Candles)** | NO — crypto-specific | YES — compiled_engine.md Section 4, OI trend context [CRYPTO HACK] | YES — open_interest (value) | YES — market participation, directional commitment | PARTIAL — context filter. Rising OI + rising price = new money. Degrades confidence if divergent. | Separate panel |
| 6 | **Funding Rate** | NO — crypto-specific | YES — session_timing_rules.md, funding_extreme flag | YES — funding (current_rate, extreme) | YES — sentiment filter, session timing context | PARTIAL — validates DSA funding_extreme. Extreme funding = caution flag. | DSA JSON only OR small panel |
| 7 | **Liquidations (Aggregated)** | NO — crypto-specific | NO — not in compiled_engine.md (future integration) | YES — liquidation (status, clusters) | YES — identifies forced exit levels, liquidity sweeps | PARTIAL — high value when data live. Currently "accumulator_not_connected" = no data. | Separate panel OR heatmap |
| 8 | **Book Imbalance (Bid/Ask Ratio)** | PARTIAL — Tom discusses order book (vl01TiVTuoQ, oa8kxSLLkAo) | YES — compiled_engine.md Section 4, secondary proof | YES — order_book_depth (bid_depth_1pct, ask_depth_1pct, bid_ask_ratio) | YES — directional pressure at current price | PARTIAL — secondary proof. DSA provides this; visual display not required. | DSA JSON only |

### TIER 3 — CROSS-TRADER CONTEXT, MAY HAVE (2 indicators)
Optional. Provide confluence context ONLY. NEVER override a Tom-validated setup.

| # | Indicator | Tom Uses? | Engine Ref? | DSA Emits? | Unique Info? | Actionable? | Placement |
|---|-----------|-----------|-------------|------------|--------------|-------------|-----------|
| 9 | **RSI 14** | NO — Malkans 40/60 from cross-trader research | NO — not in compiled_engine.md | NO — not in DSA schema | PARTIAL — overbought/oversold confluence | NO — context only. NEVER override Tom setup. | Bottom panel (optional) |
| 10 | **Bollinger Bands** | NO — crypto hack from cross-trader context | NO — not in compiled_engine.md | NO — not in DSA schema | PARTIAL — volatility context, BB middle as dynamic level | NO — context only. NEVER override Tom setup. | Main chart overlay (optional) |

### TIER 4 — NOT NEEDED, REMOVE (70 indicators)
All other indicators are redundant, non-Tom, or clutter.

| # | Indicator | Tom Uses? | Engine Ref? | DSA Emits? | Why Remove |
|---|-----------|-----------|-------------|------------|------------|
| 11 | Aggregated Futures Bid & Ask | NO | NO | NO | Raw order book data. Book Imbalance (ratio) covers this. |
| 12 | Aggregated Futures Bid & Ask Delta | NO | NO | NO | Net Delta panel covers order flow. Redundant. |
| 13 | Aggregated Futures Bid & Ask Ratio | NO | NO | NO | DSA provides bid_ask_ratio. Visual display redundant. |
| 14 | Aggregated Futures CVD Candles | NO | NO | NO | Pick CVD line OR CVD Candles — not both. |
| 15 | Aggregated Futures Taker Buy/Sell Volume | NO | NO | NO | CVD computed from this. Raw = noise. |
| 16 | Aggregated Futures Volume | NO | NO | NO | Volume Profile replaces raw volume for Tom methodology. |
| 17 | Aggregated Futures/Spot Volume Ratio | NO | NO | NO | Interesting context but not actionable. |
| 18 | Aggregated Liquidations (Coin-margined) | NO | NO | NO | Subset of Aggregated Liquidations. Clutter. |
| 19 | Aggregated Liquidations (Stablecoin-margined) | NO | NO | NO | Subset of Aggregated Liquidations. Clutter. |
| 20 | Aggregated Long/Short Ratio (Taker Buy/Sell Ratio) | NO | NO | YES | Sentiment context only. DSA covers this. |
| 21 | Aggregated Long/Short Ratio (Synchronize Main Chart) | NO | NO | NO | Same data, different display. Clutter. |
| 22 | Aggregated Open Interest (COIN-margined, Candles) | NO | NO | NO | Subset of Aggregated OI. Clutter. |
| 23 | Aggregated Open Interest (STABLECOIN-margined, Candles) | NO | NO | NO | Subset of Aggregated OI. Clutter. |
| 24 | Aggregated Spot Bid & Ask | NO | NO | NO | Raw order book. Book Imbalance covers this. |
| 25 | Aggregated Spot Bid & Ask Delta | NO | NO | NO | Net Delta covers order flow. |
| 26 | Aggregated Spot Bid & Ask Ratio | NO | NO | YES | DSA provides this. Visual redundant. |
| 27 | Aggregated Spot CVD Candles | NO | NO | NO | Pick CVD line OR CVD Candles — not both. |
| 28 | Aggregated Spot Taker Buy/Sell Volume | NO | NO | NO | CVD computed from this. Raw = noise. |
| 29 | Aggregated Spot Volume | NO | NO | NO | Volume Profile replaces raw volume. |
| 30 | Basis | NO | NO | NO | Futures-spot spread. Arbitrage metric, not trade setup. |
| 31 | Bid & Ask (non-aggregated) | NO | NO | NO | Single-exchange = incomplete. Aggregated covers this. |
| 32 | Bid & Ask Delta (non-aggregated) | NO | NO | NO | Net Delta covers this. |
| 33 | Bid & Ask Ratio (non-aggregated) | NO | NO | NO | Single-exchange = incomplete. Aggregated covers this. |
| 34 | Binance USDT Borrow Yearly Interest Rate | NO | NO | NO | Margin lending rate. Not actionable. |
| 35 | Borrow Yearly Interest Rate | NO | NO | NO | Same as above. |
| 36 | Bybit USDT Borrow Yearly Interest Rate | NO | NO | NO | Same as above. |
| 37 | CME BTC Futures Open Interest | NO | NO | NO | Institutional futures. Not primary source. |
| 38 | CME ETH Futures Open Interest | NO | NO | NO | ETH is P1, not current focus. |
| 39 | Coinbase BTC Premium Index | NO | NO | NO | Spot premium. Interesting but not actionable. |
| 40 | Crypto Fear & Greed Index | NO | NO | NO | Sentiment index. Contrarian context only. |
| 41 | CVD Candles (non-aggregated) | NO | NO | NO | Pick CVD line OR CVD Candles — not both. |
| 42 | CVD (non-aggregated) | NO | NO | NO | Single-exchange = incomplete. Aggregated covers this. |
| 43 | Funding Rates (Candles) | NO | NO | NO | Current rate sufficient. Historical = clutter. |
| 44 | Funding Rates (Open Interest Weighted) | NO | NO | NO | Weighted variant. Current rate sufficient. |
| 45 | Funding Rates (Open Interest Weighted, Candles) | NO | NO | NO | Doubly redundant. Current rate sufficient. |
| 46 | Grayscale Holdings | NO | NO | NO | Institutional holdings. Long-term context. |
| 47 | Grayscale Premium | NO | NO | NO | Same as above. |
| 48 | Long/Short Ratio (Accounts) | NO | NO | YES | Sentiment context. DSA covers this. |
| 49 | Long/Short Ratio (Accounts, Candles) | NO | NO | NO | Current ratio sufficient. Historical = clutter. |
| 50 | Market Cap | NO | NO | NO | Macro context. Not actionable. |
| 51 | Net Longs | NO | NO | NO | Derivative of L/S ratio. Redundant. |
| 52 | Net Longs (New) | NO | NO | NO | Same as above. |
| 53 | Net Shorts | NO | NO | NO | Derivative of L/S ratio. Redundant. |
| 54 | Net Shorts (New) | NO | NO | NO | Same as above. |
| 55 | OKX USDT Borrow Yearly Interest Rate | NO | NO | NO | Margin lending rate. Not actionable. |
| 56 | Open Interest (non-aggregated) | NO | NO | NO | Single-exchange = incomplete. Aggregated covers this. |
| 57 | Open Interest Delta | NO | NO | NO | Derivative of OI. Redundant if OI candles shown. |
| 58 | Open Interest/Market Cap | NO | NO | NO | Ratio context. Not actionable. |
| 59 | Options Open Interest | NO | NO | NO | Options market. MTS trades futures/spot only. |
| 60 | Options Open Interest (Expiry) | NO | NO | NO | Same as above. |
| 61 | Predicted Funding Rates | NO | NO | NO | Predicted next funding. Current rate is actionable. |
| 62 | Premium Index | NO | NO | NO | Futures premium. Context only. |
| 63 | Price Index | NO | NO | NO | Reference price. Current price is sufficient. |
| 64 | Symbol Liquidations | NO | NO | NO | Aggregated Liquidations covers this. |
| 65 | Taker Buy/Sell Count | NO | NO | NO | Count of orders, not volume. Less informative than delta. |
| 66 | Taker Buy/Sell Count (Delta) | NO | NO | NO | Derivative of count. Redundant. |
| 67 | Taker Buy/Sell Value | NO | NO | NO | Notional value. CVD covers this. |
| 68 | Taker Buy/Sell Value (Delta) | NO | NO | NO | Derivative of value. Redundant. |
| 69 | Taker Buy/Sell Volume (Delta) | NO | NO | NO | Net Delta covers this. |
| 70 | Top Trader Long/Short (Accounts) | NO | NO | NO | Whale sentiment. Context only. |
| 71 | Top Trader Long/Short (Accounts, Candles) | NO | NO | NO | Same as above. Historical = clutter. |
| 72 | Top Trader Long/Short (Positions) | NO | NO | NO | Whale positioning. Context only. |
| 73 | Top Trader Long/Short (Positions, Candles) | NO | NO | NO | Same as above. Historical = clutter. |
| 74 | Whale Index | NO | NO | NO | Whale activity. Context only. |
| 75 | Whale Index 2/3/4 | NO | NO | NO | Variants of Whale Index. Redundant. |
| 76 | MACD | NO | NO | NO | Not a Tom concept. CVD replaces it. |
| 77 | SMA / EMA | NO | NO | NO | Not a Tom concept. VP + VWAP replace them. |
| 78 | Stochastic | NO | NO | NO | Not a Tom concept. |
| 79 | Ichimoku | NO | NO | NO | Not a Tom concept. |
| 80 | Any other TradingView standard indicator | NO | NO | NO | Standard indicators not part of Tom methodology. |

---

## SECTION 2: RECOMMENDED CHART LAYOUT

### Visual Chart Stack (top to bottom)

| Panel | Indicator | Tier | Why Here |
|-------|-----------|------|----------|
| **Main Chart** | Price + Volume Profile + VWAP | T1 | Core Tom methodology. VWAP on price chart for band entries. VP for zone identification. |
| **Panel 1** | CVD (line) | T1 | Trend direction, divergence detection. Line preferred over candles for clean trend reading. |
| **Panel 2** | Net Delta | T1 | Per-candle order flow. Absorption, rejection, finished auction detection. |
| **Panel 3** | Open Interest (Candles) | T2 | Market participation context. Candles show OI change per price candle. |
| **Panel 4** | RSI 14 | T3 | Confluence context. Malkans 40/60 levels. Optional — remove if clutter. |

### Layout Rules
- Max 4 panels below price (clutter rule).
- VWAP MUST be on main chart.
- Volume Profile MUST be on main chart.
- CVD and Net Delta MUST be on separate panels (different information).
- OI on its own panel.
- No duplicate information: CVD line OR CVD Candles — pick line.
- Aggregated vs single-exchange: prefer Aggregated (Binance+Bybit+OKX) per MTS primary source policy.

### DSA-Only Indicators (not on visual chart)
These are consumed via JSON only:
- Funding Rate (current_rate, extreme) — validated by DSA, not needed visually
- Book Imbalance (bid_ask_ratio) — DSA provides this; visual display redundant
- Liquidations — when data is live, use heatmap; otherwise DSA-only
- Long/Short Ratio — DSA provides this; visual display redundant

### Timeframe-Specific Layout

| Setup Type | Primary TF | Context TF | Macro TF | Indicators Shown |
|------------|-----------|------------|----------|------------------|
| CT at daily zone | 15m | 1H | 4H | All 4 panels + VP + VWAP |
| CT at 4H zone | 5m | 15m | 1H | All 4 panels + VP + VWAP |
| TC pullback | 15m | 1H | 4H | All 4 panels + VP + VWAP |
| BO | 5m/15m | 1H | 4H | All 4 panels + VP + VWAP |
| Scalp | 3m/5m | 15m | 1H | CVD + Delta + VWAP bands (minimal) |

---

## SECTION 3: DSA ALIGNMENT REPORT

| Indicator | DSA Block | Fields | Visual Validation Needed? | Status |
|-----------|-----------|--------|--------------------------|--------|
| Volume Profile | volume_profile | poc, vah, val, hvns, lvns, shape | YES — approximated from 1m OHLCV | LIVE |
| VWAP | vwap | price, sigma, bands, slope, slope_pct | YES — approximated from 1m OHLCV | LIVE |
| CVD | cvd | value, slope, divergence, last_3_delta | YES — takerBuyBaseAssetVolume proxy | LIVE |
| Net Delta | trade_flow | net_delta, last_3_delta | YES — approximated | LIVE |
| Open Interest | open_interest | value | NO — direct from exchange | LIVE |
| Funding Rate | funding | current_rate, extreme | NO — direct from exchange | LIVE |
| Liquidations | liquidation | status, clusters | YES — currently "accumulator_not_connected" | NO DATA |
| Book Imbalance | order_book_depth | bid_depth_1pct, ask_depth_1pct, bid_ask_ratio | NO — direct from exchange | LIVE |
| Long/Short Ratio | long_short_ratio | ratio | NO — direct from exchange | LIVE |
| RSI 14 | — | — | N/A | NOT IN DSA |
| Bollinger Bands | — | — | N/A | NOT IN DSA |

**DSA Coverage:** 8 of 10 recommended indicators have DSA fields. 2 (RSI 14, Bollinger Bands) are visual-only.

---

## SECTION 4: GAP ANALYSIS

### Gaps — MTS Needs NOT Met by Current Indicators

| # | Gap | Severity | Impact | Proposed Resolution |
|---|-----|----------|--------|---------------------|
| 1 | **True tick-level delta** | HIGH | DSA CVD is computed from takerBuyBaseAssetVolume (1m OHLCV proxy), not true L2 delta. This creates approximation error in absorption detection. | Flag for visual validation. Cannot fix without tick data JISHU does not have. (Rule 33: Lean DSA Contract) |
| 2 | **True Volume Profile** | HIGH | DSA VP is approximated from 1m OHLCV. May deviate 0.2-0.5% from CoinGlass VPVR. | Visual validation mandatory per VVP-001. CoinGlass VPVR = primary for exact levels. |
| 3 | **Liquidation heatmap data** | MEDIUM | DSA liquidation status = "accumulator_not_connected". No clusters available. | CoinGlass provides liquidation heatmaps visually. Use screenshot/heatmaps when needed. DSA field exists for future connection. |
| 4 | **Footprint chart data** | MEDIUM | Tom uses footprint (bid/ask per price level) for absorption detection. DSA cannot provide this. | Visual validation ONLY. Screenshot reading per VVP-001 Section 6. |
| 5 | **VWAP standard deviation bands** | LOW | Tom never mentions sigma bands. DSA provides them but they are a screener invention. | Use cautiously. Bands are crypto adaptation, not Tom-validated. |
| 6 | **RSI 14 in DSA** | LOW | RSI is visual-only. No DSA field. | Acceptable — RSI is T3 (optional context). Visual chart sufficient. |
| 7 | **Bollinger Bands in DSA** | LOW | BB is visual-only. No DSA field. | Acceptable — BB is T3 (optional context). Visual chart sufficient. |

### Gaps — Tom Concepts NOT in CoinGlass/DSA

| # | Tom Concept | Status | Why Missing |
|---|-------------|--------|-------------|
| 1 | Single Print areas (target, not entry) | ENGINE PATCH LIVE | Requires VP histogram API. Blocked. |
| 2 | Double Distribution detection | ENGINE PATCH LIVE | Requires VP histogram API. Blocked. |
| 3 | VPOC Migration trend | ENGINE PATCH LIVE | DSA provides prior_week_poc, two_week_ago_poc. Visual confirmation needed. |
| 4 | Volume spike at level (exhaustion) | ENGINE PATCH LIVE | DSA provides volume_spike_at_level boolean. |
| 5 | Prior day close as zone | ENGINE PATCH LIVE | DSA provides prior_day.close. |

---

## SECTION 5: ACTION ITEMS

### Immediate Actions (This Session)

| # | Action | Priority | Owner | Rationale |
|---|--------|----------|-------|-----------|
| 1 | **Add VWAP to main chart** | P0 — CRITICAL | JISHU | VVP-001 Rule 2.1: VWAP is Tier 1 and currently MISSING from all screenshots. Without VWAP, visual validation cannot confirm band entries or scalp setups. |
| 2 | **Add Volume Profile to main chart** | P0 — CRITICAL | JISHU | Tier 1. VP must be visible for zone identification, POC/VAH/VAL reading. |
| 3 | **Add CVD panel (line, not candles)** | P0 — CRITICAL | JISHU | Tier 1. CVD line for trend direction. Pick line OR candles — not both. |
| 4 | **Add Net Delta panel** | P0 — CRITICAL | JISHU | Tier 1. Net Delta for absorption/rejection detection. |
| 5 | **Add Open Interest (Candles) panel** | P1 — HIGH | JISHU | Tier 2. OI context for market participation. |
| 6 | **Remove ALL Tier 4 indicators from chart** | P1 — HIGH | JISHU | 70 indicators = clutter. Remove all non-T1/T2/T3 indicators. |

### Short-Term Actions (Next 1-3 Sessions)

| # | Action | Priority | Owner | Rationale |
|---|--------|----------|-------|-----------|
| 7 | **Add RSI 14 panel (optional)** | P2 — MEDIUM | JISHU | Tier 3. Malkans 40/60 confluence. Only if panel 4 is free. |
| 8 | **Test liquidation heatmap integration** | P2 — MEDIUM | JISHU + DSA | Tier 2. When liquidation data is live, heatmap provides valuable liquidity sweep detection. |
| 9 | **Validate CVD line vs CVD Candles preference** | P2 — MEDIUM | JISHU | Determine which format is more readable for absorption detection. |
| 10 | **Document final chart layout in VVP-001** | P2 — MEDIUM | sys_AI | Update VVP-001 Section 5 with finalized layout. |

### No-Action Items (Explicitly Rejected)

| # | Item | Why Rejected |
|---|------|--------------|
| 1 | Add MACD, SMA, EMA, Stochastic, Ichimoku | Not Tom-validated. CVD + VP + VWAP replace them. |
| 2 | Add Funding Rate visual panel | DSA provides this. Visual panel = clutter. |
| 3 | Add L/S Ratio visual panel | DSA provides this. Visual panel = clutter. |
| 4 | Add Book Imbalance visual panel | DSA provides this. Visual panel = clutter. |
| 5 | Add raw volume bars | Volume Profile replaces raw volume for Tom methodology. |
| 6 | Add any Whale/Top Trader indices | Context only. Not actionable. DSA does not emit. |
| 7 | Add Fear & Greed Index | Sentiment context. Not actionable for trade timing. |
| 8 | Add margin lending rates | Not actionable for trade decisions. |
| 9 | Request DSA fields for RSI/BB | Rule 33: Lean DSA Contract. RSI/BB are visual-only T3 indicators. Engine does not need them. |
| 10 | Request DSA fields for liquidation clusters | Field already exists (liquidation.clusters). Blocked on accumulator connection, not schema. |

---

## SECTION 6: SUMMARY DECISION MATRIX

| If JISHU wants... | Then add... | Tier | DSA? | Visual? |
|-------------------|-------------|------|------|---------|
| Core Tom methodology | Volume Profile + VWAP + CVD + Net Delta | T1 | YES | YES |
| Crypto context | Open Interest + Funding + Liquidations | T2 | YES | PARTIAL |
| Confluence filter | RSI 14 + Bollinger Bands | T3 | NO | YES |
| Clean chart | Remove everything else | T4 | N/A | REMOVE |

**Final recommendation:** 6 visual indicators maximum (4 T1 + 1 T2 + 1 optional T3). 4 DSA-only fields (Funding, Book Imbalance, L/S Ratio, Liquidations when live). Everything else removed.

---

# END OF INDICATOR AUDIT TABLE
# Status: COMPLETE
# Next: JISHU implements chart layout per Section 5 Action Items 1-6.
