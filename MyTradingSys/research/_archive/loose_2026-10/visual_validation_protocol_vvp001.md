# VISUAL VALIDATION PROTOCOL — VVP-001 v1.1.0
# Purpose: Standardize screenshot reading, eliminate cursor-position ambiguity,
#          and define indicator tiers for MTS visual validation.
# Date: 2026-09-01
# Status: ACTIVE
# Canonical: /mnt/agents/output/upload_mirror/mts/research/_archive/loose_2026-10/visual_validation_protocol_vvp001.md
# Questionnaire Decisions Applied: CVD=Line, VP=Fixed Range, Liquidations=T3, RSI/BB removed

---

## 1. THE CURSOR PROBLEM

**Issue:** CoinGlass/TradingView indicator legends update when the cursor hovers over ANY candle, not just the current one. A screenshot taken with the cursor on a historical candle shows THAT candle's values, not live values.

**Impact:** Misreading a historical candle as "current" leads to false proof assessment, wrong trigger evaluation, and incorrect verdicts.

---

## 2. SCREENSHOT CAPTURE RULES (JISHU)

### Rule 2.1: Cursor at Right Edge
- ALWAYS place cursor at the RIGHTMOST EDGE of the chart (current/live candle).
- The vertical crosshair should align with the last visible candle.
- If analyzing a historical candle, state the exact timestamp in the message.

### Rule 2.2: Timeframe Visible
- The selected timeframe MUST be clearly visible in the top bar (e.g., "15m" highlighted).
- Do not crop the top bar.

### Rule 2.3: Price Header Visible
- The main price OHLC header MUST be visible: `O X H X L X C X (+/-change)`.
- This confirms which candle the cursor is on.

### Rule 2.4: All Indicator Legends Visible
- Every indicator legend must show its FULL label and values.
- Do not crop indicator panels.

### Rule 2.5: No Overlays Blocking Legends
- Ensure no drawing tools, text boxes, or alerts block indicator values.

### Rule 2.6: Zone Markings Required (NEW v1.1.0)
- POC, VAH, VAL MUST be visually marked on the Volume Profile.
- If Fixed Range VP does not show labels, annotate manually or state levels in message.
- Without zone markings, proof detection at specific levels is impossible.

---

## 3. INDICATOR READING RULES (SYS_AI)

### Rule 3.1: O/H/L/C Format
CoinGlass shows FOUR values per indicator in this order: **Open, High, Low, Close**.

Example: `CVD: -8.732K -8.732K -8.735K -8.735K`
- O = -8.732K
- H = -8.732K
- L = -8.735K
- C = -8.735K

**For trend assessment:** Use the **Close (C)** value as the primary reading.

### Rule 3.2: Timeframe Annotation Mandatory
When reporting indicator values, ALWAYS prefix with timeframe:
- CORRECT: "15m CVD = -8.735K (falling)"
- WRONG: "CVD = -8.735K" (ambiguous — which TF?)

### Rule 3.3: Cross-Timeframe Values Are Not Contradictory
A 6H CVD of +52K and a 15m CVD of -8K are NOT contradictory. They describe different time scopes:
- 6H +52K = net buying over the last 6 hours
- 15m -8K = net selling in the last 15 minutes

This is a **pullback within a larger move** — a normal market structure.

### Rule 3.4: DSA vs Visual Priority Hierarchy

| Data Type | Primary Source | Secondary Source | Action on Conflict |
|-----------|---------------|------------------|-------------------|
| Exact price levels (POC, VAH, VAL, swings) | DSA JSON | Screenshot | Use DSA. Screenshot VP may drift with zoom. Fixed Range VP reduces drift. |
| Trend direction (CVD slope, delta direction) | Visual screenshot | DSA JSON | Use visual. DSA may lag or use different aggregation. |
| Proof items (absorption, wick, finished auction) | Visual screenshot ONLY | N/A | DSA cannot detect these. Visual is sole source. |
| OI direction | DSA JSON | Visual | Use DSA. Visual OI is per-candle, DSA is computed trend. |
| Book imbalance | DSA JSON | Visual | Use DSA. Visual may not show aggregated book. |

### Rule 3.5: Flag, Do Not Override Silently
When DSA and visual disagree on trend direction:
1. State BOTH readings with timeframes.
2. Explain the likely reason (different aggregation, lag, transient spike).
3. Do NOT silently override one with the other.
4. Degrade confidence if the disagreement is significant.

---

## 4. INDICATOR TIER SYSTEM (v1.1.0 — Questionnaire Decisions Applied)

### TIER 1: Tom-Validated — ESSENTIAL (Must be on every screenshot)

| Indicator | Why | Tom Source | Format |
|-----------|-----|------------|--------|
| **Volume Profile (Fixed Range)** | POC, VAH, VAL, shape — core of Tom's methodology | Multiple videos | Fixed Range (not VPVR). Week anchor for macro, Day for intraday. |
| **VWAP** | Business zones, scalp bands, trend confirmation | 43JaKHRvxHk, 4MoNjEQ2Dd8 | HLC3 source, Session anchor, bands +-1/2/3 sigma |
| **CVD (Line)** | Buyer/seller pressure, divergence detection | y67l86cSqb8 | LINE format. Net Delta panel handles per-candle direction. CVD Candles are redundant. |
| **Net Delta / Delta** | Per-candle order flow, absorption detection | oa8kxSLLkAo, y67l86cSqb8 | Per-candle bars showing buy/sell pressure |

**CRITICAL:** VWAP was missing from all screenshots prior to 2026-09-01. DSA emits VWAP data but visual validation cannot confirm it without VWAP on the chart. **VWAP is now REQUIRED.**

### TIER 2: MTS-Required — NEEDED (Should be on screenshots if panel space allows)

| Indicator | Why | MTS Source | Format |
|-----------|-----|------------|--------|
| **Open Interest (Candles)** | Market participation, directional commitment | compiled_engine.md Section 4 | Candles showing OI change per price candle |

### TIER 3: Cross-Trader Context — DORMANT (Not on default layout)

| Indicator | Why | Status |
|-----------|-----|--------|
| **Liquidations** | Liquidity sweep detection when data is live | DEMOTED from T2 to T3. DSA reports `status="none"`. Removed from chart until CoinGlass API connected. DSA field kept as dormant flag. |
| **RSI 14** | Malkans 40/60 levels for confluence | REMOVED from default layout. Zero unique info beyond CVD/Delta. |
| **Bollinger Bands** | Volatility context | REMOVED from default layout. Redundant with VWAP bands + VP structure. Not Tom-validated. |

**Note:** RSI and BB are NOT Tom-validated. They provide context only. NEVER let RSI or BB override a Tom-validated setup. They are NOT on the default chart layout.

### TIER 4: Not Needed — REMOVE (Waste of space)

| Indicator | Why Remove |
|-----------|------------|
| Moving Averages (SMA/EMA) | Not a Tom concept. VP + VWAP replace them. |
| MACD | Not a Tom concept. CVD replaces it. |
| Stochastic | Not a Tom concept. |
| Ichimoku | Not a Tom concept. |
| Any custom indicator | Unless explicitly approved by JISHU. |
| CVD Candles | Redundant with CVD Line + Net Delta panel. Pick line OR candles — line is REQUIRED. |

---

## 5. RECOMMENDED SCREENSHOT LAYOUT (v1.1.0)

### For JSON Validation (per-JSON workflow):
**Minimum 2 screenshots:**
1. **Setup timeframe** (15m or 5m) — shows the zone, price action, CVD, Delta
2. **Higher timeframe** (1H or 4H) — shows structural context, VP shape

**Optional 3rd screenshot:**
3. **Macro timeframe** (6H or 1D) — shows weekly structure, VPOC migration

### Indicator Stack (top to bottom):
1. Main chart: Price + Volume Profile (Fixed Range) + VWAP (with bands)
2. Panel 1: CVD (line, NOT candles)
3. Panel 2: Net Delta
4. Panel 3: Open Interest (Candles)
5. Panel 4: [EMPTY — reserved for future Tier 1 indicators]

**Layout Rules:**
- Max 4 panels below price (clutter rule).
- VWAP MUST be on main chart with bands visible.
- Volume Profile MUST be on main chart (Fixed Range, not VPVR).
- CVD and Net Delta MUST be on separate panels (different information).
- CVD is LINE format. Do NOT add CVD Candles — redundant.
- OI on its own panel.
- No duplicate information.

### Timeframe Priority:
| Setup Type | Primary TF | Context TF | Macro TF |
|------------|-----------|------------|----------|
| CT at daily zone | 15m | 1H | 4H |
| CT at 4H zone | 5m | 15m | 1H |
| TC pullback | 15m | 1H | 4H |
| BO | 5m/15m | 1H | 4H |
| Scalp | 3m/5m | 15m | 1H |

---

## 6. PROOF ITEM DETECTION FROM SCREENSHOTS

### 6.1 Absorption
**What to look for:** Large green/red delta bar at zone level with price NOT moving through it.
**Screenshot evidence:** Net Delta shows a large spike (positive or negative) at the zone price, but the price candle has a small body or wick.

### 6.2 Rejection Wick
**What to look for:** Price touches zone, produces long wick, reverses.
**Screenshot evidence:** Candle with long upper wick at resistance OR long lower wick at support.

### 6.3 Finished Auction
**What to look for:** Single large delta bar at extreme with zero follow-through.
**Screenshot evidence:** One candle with extreme delta, next candle shows immediate reversal.

### 6.4 Speed Picking Up
**What to look for:** Candles getting progressively larger, gaps between candles.
**Screenshot evidence:** 3m/5m chart shows 2-3 consecutive large candles in one direction.

---

## 7. VALIDATION CHECKLIST (Per Screenshot)

Before using any screenshot for verdict generation, verify:

- [ ] Cursor is at rightmost edge (current candle)
- [ ] Timeframe is visible in top bar
- [ ] Price OHLC header is visible
- [ ] All indicator legends are visible and readable
- [ ] No overlays block critical data
- [ ] VWAP is present with bands visible (TIER 1 requirement)
- [ ] Volume Profile is present (Fixed Range) with POC/VAH/VAL visible (TIER 1 requirement)
- [ ] CVD (line) is present (TIER 1 requirement)
- [ ] Net Delta is present (TIER 1 requirement)
- [ ] OI is present (TIER 2 requirement)
- [ ] NO CVD Candles (redundant with line + delta)
- [ ] NO RSI/BB on default layout (removed per questionnaire)

If ANY Tier 1 indicator is missing -> request re-screenshot before proceeding.

---

## 8. CHANGELOG

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-08-31 | Initial protocol. Created after cursor-position ambiguity discovered during BTCUSDT visual validation. |
| 1.1.0 | 2026-09-01 | Questionnaire decisions applied: CVD=Line, VP=Fixed Range, Liquidations=T3, RSI/BB removed. Section 2.6 added (zone markings). Section 5 layout updated. |

---

# END
