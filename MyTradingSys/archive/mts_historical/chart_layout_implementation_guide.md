# CHART LAYOUT IMPLEMENTATION GUIDE
# Purpose: Step-by-step CoinGlass configuration for MTS v4.2.0-p5
# Date: 2026-09-01
# Status: ACTIVE
# Based on: VVP-001 v1.1.0, indicator_audit_table.md, questionnaire decisions

---

## REQUIRED INDICATORS — ADD THESE

### 1. VWAP (Tier 1 — CRITICAL)
**Path:** Indicators -> Search "VWAP"
**Settings:**
- Source: HLC3
- Anchor: Session
- Bands: ON — +-1, +-2, +-3 standard deviations
- Color: Distinguishable from price (e.g., yellow line, purple bands)

**Why:** Tom uses VWAP for business zones, scalp entries, and trend confirmation. Bands required for sigma entries.

---

### 2. Volume Profile — Fixed Range (Tier 1 — CRITICAL)
**Path:** Indicators -> Search "Fixed Range Volume Profile"
**Settings:**
- Mode: Fixed Range (NOT VPVR — VPVR drifts with zoom)
- Rows: 24 (default)
- Volume: Total (Binance+Bybit+OKX aggregated)
- Visibility: POC, VAH, VAL labels ON
- Color: Visible against chart background

**Why:** VPVR drifts when zooming in/out. Fixed Range locks to the visible bars. POC/VAH/VAL are primary zones for entry/stop/target.

**Per-timeframe anchors:**
- 1W/1D macro analysis: Week anchor
- 4H/1H intraday: Day anchor
- 15m/5m entry: Session anchor or Day anchor

---

### 3. CVD — Line (Tier 1 — CRITICAL)
**Path:** Indicators -> Search "CVD" or "Cumulative Volume Delta"
**Settings:**
- Format: LINE (not candles)
- Source: Aggregated (Binance+Bybit+OKX)
- Color: Green for positive, red for negative (or single color with direction)

**Why:** Questionnaire decision: CVD Line shows trend direction cleanly. Net Delta panel handles per-candle direction. CVD Candles are redundant.

---

### 4. Net Delta (Tier 1 — CRITICAL)
**Path:** Indicators -> Search "Delta" or "Net Delta"
**Settings:**
- Format: Per-candle bars (histogram)
- Source: Aggregated
- Color: Green for buy delta, red for sell delta

**Why:** Per-candle order flow for absorption, rejection, finished auction detection.

---

### 5. Open Interest — Candles (Tier 2 — HIGH)
**Path:** Indicators -> Search "Open Interest"
**Settings:**
- Format: Candles
- Source: Aggregated
- Panel: Separate panel below Delta

**Why:** Market participation context. Rising OI + rising price = new money entering.

---

## INDICATORS TO REMOVE

| Indicator | Why Remove |
|-----------|------------|
| CVD Candles | Redundant with CVD Line + Net Delta |
| RSI | Removed per questionnaire. Zero unique info beyond CVD/Delta. |
| Bollinger Bands | Removed per questionnaire. Redundant with VWAP bands. |
| VPVR (if present) | Replace with Fixed Range Volume Profile |
| Any moving averages (SMA/EMA) | Not Tom-validated |
| MACD | Not Tom-validated. CVD replaces it. |
| Stochastic | Not Tom-validated |
| Ichimoku | Not Tom-validated |
| Funding Rate panel | DSA provides this. Visual = clutter. |
| Long/Short Ratio panel | DSA provides this. Visual = clutter. |
| Any Whale/Top Trader indices | Context only. Not actionable. |
| Fear & Greed Index | Not actionable for trade timing. |

---

## PANEL ORDER (Top to Bottom)

```
[Main Chart]  Price + Fixed Range VP + VWAP (with bands)
[Panel 1]     CVD (line)
[Panel 2]     Net Delta (bars)
[Panel 3]     Open Interest (candles)
[Panel 4]     [EMPTY — reserved]
```

**Rules:**
- Max 4 panels below price
- CVD and Delta MUST be separate panels (different information)
- Panel 4 stays empty for now. Future Tier 1 indicators only.

---

## PER-TIMEFRAME SETTINGS

| Timeframe | VP Anchor | VWAP Anchor | Purpose |
|-----------|-----------|-------------|---------|
| 1W | Week | Session | Macro structure |
| 1D | Week | Session | Daily context |
| 4H | Day | Session | Context TF |
| 1H | Day | Session | Setup TF |
| 15m | Day | Session | Entry TF (CT at daily zone) |
| 5m | Day/Session | Session | Entry TF (CT at 4H zone) |
| 3m | Session | Session | Scalp confirmation |

---

## VALIDATION STEPS

After configuring, take a test screenshot of each timeframe (15m, 1H, 4H) and verify:
1. [ ] VWAP line + bands visible on main chart
2. [ ] Fixed Range VP showing POC/VAH/VAL labels
3. [ ] CVD line (not candles) in Panel 1
4. [ ] Net Delta bars in Panel 2
5. [ ] OI candles in Panel 3
6. [ ] No CVD Candles, no RSI, no BB, no MAs
7. [ ] Cursor at right edge, timeframe visible, OHLC header visible

---

# END
