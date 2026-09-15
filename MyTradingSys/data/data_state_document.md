# DATA STATE DOCUMENT — MTS v4.2.0-p5
# Date: 2026-09-02
# Purpose: Single source of truth for "what data do we have, what do we need, what's missing"
# Status: ACTIVE — Updated per session
# LAST CLEANUP: 2026-09-02 — Archived 3 completed DSA tasks, renamed schema v1.0→v1.2.0, replaced stale sample JSON
# ---

## 1. CURRENT DATA INVENTORY

### 1.1 What the DSA JSON Provides (Per Snapshot)

| Category | Fields | History Depth | Confidence | Visual Validation Needed? |
|----------|--------|--------------|------------|--------------------------|
| **Price** | current_price | Point-in-time | HIGH (direct from exchange) | NO |
| **Weekly VP** | poc, vah, val, shape, prior_week_poc, two_week_ago_poc | 3 weeks POC only | MEDIUM (1m OHLCV approx) | YES |
| **Daily VP** | poc, vah, val, shape, hvns, lvns | 2 days (current + prior) | MEDIUM (1m OHLCV approx) | YES |
| **4H VP** | poc, vah, val, shape | Current only | MEDIUM (1m OHLCV approx) | YES |
| **Post-Funding VP** | poc, vah, val, shape | Current only | MEDIUM (1m OHLCV approx) | YES |
| **VWAP** | price, slope, slope_pct, bands (+1s/+2s/-1s/-2s) | Current only | MEDIUM (1m OHLCV approx) | YES |
| **CVD** | value, slope, divergence, last_3_delta, cvd_recent (1h/4h) | Current + 1h/4h slopes | MEDIUM (takerBuy proxy) | YES |
| **Trade Flow** | net_delta | Current only | HIGH (computed from delta) | NO |
| **Structure** | swing_high, swing_low, stale (1h/15m/5m) | Current only | HIGH (computed from OHLC) | NO |
| **FVG** | unfilled_count, nearest_unfilled (type/top/bottom) | Current only | LOW (screener heuristic) | YES |
| **Order Book** | bid_ask_ratio | Point-in-time | HIGH (direct from API) | NO |
| **Funding** | current_rate, extreme | Point-in-time | HIGH (direct from API) | NO |
| **OI** | direction, change_1h_pct | Point-in-time | HIGH (direct from API) | NO |
| **Session** | current_session, funding_reset_window, us_equity_open_in_minutes | Point-in-time | HIGH (computed) | NO |
| **Conditions** | 15 boolean flags (price_vs_poc, speed_picking_up, etc.) | Point-in-time | MIXED | PARTIAL |
| **Prior Day** | poc, vah, val, high, low, close | 1 day | MEDIUM (1m OHLCV approx) | YES |

### 1.2 What the JSON Does NOT Provide (Gaps)

| Missing Data | Why It Matters | Workaround | Priority |
|-------------|---------------|------------|----------|
| **Weekly VAH/VAL history** | Cannot detect if weekly balance is expanding/contracting | Screenshot + mental map | MEDIUM |
| **Weekly shape history** | Cannot detect if weekly B is breaking into trend | Screenshot only | MEDIUM |
| **Daily HVN/LVN history** | Cannot track multi-day volume node migration | None | LOW |
| **4H VP history** | Cannot see if 4H balance held over multiple periods | Screenshot only | HIGH |
| **1H/15m/5m VP** | No intraday volume profile at all | Screenshot only | HIGH |
| **OHLC history** | No candle data for pattern recognition | Screenshot only | HIGH |
| **Multi-day CVD trend** | Only 1h/4h slopes, no daily/weekly CVD context | Screenshot only | MEDIUM |
| **Historical swing levels** | Cannot see if swings are being taken out over time | Screenshot only | LOW |
| **True tick delta** | DSA uses takerBuy proxy, not real delta | Screenshot Net Delta panel | HIGH |
| **Liquidation clusters** | DSA status = "none" (API not connected) | CoinGlass heatmap (manual) | LOW |
| **Absorption detection** | No field for this | Screenshot only | HIGH |
| **Finished auction detection** | No field for this | Screenshot only | HIGH |
| **Prior week VAH/VAL** | Only POC history, not full value area | None | MEDIUM |

---

## 2. DATA SUFFICIENCY ANALYSIS

### 2.1 For Weekly VPOC Migration (Current Status: SUFFICIENT)

**What we have:** 3 weeks of POC data (two_week_ago → prior_week → current)
**What we can detect:** Rising VPOC = bullish structure, falling VPOC = bearish structure
**Example from today's JSON:**
  77,250.28 → 79,284.54 → 77,913.27 = VPOC rose then fell = mixed structure
**What we CANNOT detect:** Whether weekly VAH/VAL are also migrating (need history)

### 2.2 For Daily Context (Current Status: PARTIAL)

**What we have:** Current day + prior day full VP
**What we can detect:** Day-over-day POC shift, prior day close as level
**What we CANNOT detect:** Multi-day trend (only 2 days), HVN/LVN migration

### 2.3 For 4H/Intraday Setup (Current Status: INSUFFICIENT)

**What we have:** Current 4H VP only (single point)
**What we can detect:** Current balance area, price position within it
**What we CANNOT detect:**
  - Whether 4H balance held over previous periods
  - Whether this is a fresh balance or developing trend
  - Whether prior 4H POCs were revisited (naked POC concept)
**Impact:** The engine assumes 4H VP is "current context" but cannot validate if that context is stable.

### 2.4 For Proof Items (Current Status: MISSING — Screenshot Required)

**What DSA provides:** Boolean flags (rejection_wick_at_zone, volume_spike_at_level)
**What DSA CANNOT provide:**
  - Visual confirmation of wick quality (long wick vs short wick)
  - Absorption evidence (large delta bar, price doesn't move)
  - Finished auction (extreme delta, immediate reversal)
  - Delta flip on bounce (per-candle delta direction)
**Rule:** DSA flags = "check this." Screenshot = "here's the proof."

---

## 3. DIVISION OF LABOR: DSA vs SCREENSHOT vs AI JUDGMENT

```
DSA JSON (The Map)
  ├── Exact levels (POC, VAH, VAL, swings) ← Ground truth
  ├── Computed conditions (price_vs_va, cvd_slope) ← Context
  └── Boolean flags (rejection_wick, speed_picking_up) ← Alerts
        ↓
SCREENSHOT (The Battlefield)
  ├── Proof items (wick, absorption, auction) ← Visual validation
  ├── Real-time flow (CVD line, Net Delta bars) ← Current state
  └── Pattern confirmation (VP shape, candle structure) ← Visual check
        ↓
AI JUDGMENT (The Commander)
  ├── Applies compiled_engine.md rules ← Decision framework
  ├── Cross-references DSA + Screenshot ← Dual-source verification
  └── Generates verdict (A/B/C/D) ← Output
```

**Hard Rule:** AI never overrides DSA levels with screenshot levels. Screenshot is for PROOF, not for LEVELS.

---

## 4. WHAT NEEDS TO BE ADDED TO DSA

### 4.1 High Priority (Would Eliminate Screenshot Dependency for Setup Validation)

| Field | Why | Complexity | Status |
|-------|-----|------------|--------|
| **absorption_at_zone** | Boolean: large delta bar at level, price doesn't break | MEDIUM | NOT REQUESTED |
| **finished_auction** | Boolean: extreme delta + immediate reversal | MEDIUM | NOT REQUESTED |
| **delta_flip** | Boolean: delta direction changed on bounce | LOW | NOT REQUESTED |
| **1h_vp** | POC/VAH/VAL for 1H timeframe | MEDIUM | NOT REQUESTED |
| **15m_vp** | POC/VAH/VAL for 15m timeframe | MEDIUM | NOT REQUESTED |

### 4.2 Medium Priority (Would Improve Context)

| Field | Why | Complexity | Status |
|-------|-----|------------|--------|
| **prior_week_vah/val** | Weekly value area migration | MEDIUM | NOT REQUESTED |
| **prior_4h_vp** | Previous 4H balance area | MEDIUM | NOT REQUESTED |
| **cvd_daily_slope** | Daily CVD trend context | LOW | NOT REQUESTED |
| **volume_profile_1h** | Intraday volume structure | HIGH | NOT REQUESTED |

### 4.3 Low Priority (Nice to Have)

| Field | Why | Complexity | Status |
|-------|-----|------------|--------|
| **historical_hvns** | Multi-day high volume node tracking | HIGH | NOT REQUESTED |
| **swing_level_history** | Track swing highs/lows over time | MEDIUM | NOT REQUESTED |
| **liquidation_clusters** | API-dependent, not available | HIGH | BLOCKED |

---

## 5. SCREENSHOT MINIMUM REQUIREMENTS (What We MUST See)

Given current DSA gaps, the screenshot MUST provide:

| Setup Type | Minimum Screenshots | What to Verify |
|------------|--------------------|----------------|
| CT at daily zone | 15m (entry) + 1H (context) | Rejection wick at zone, absorption, delta flip |
| CT at 4H zone | 5m (entry) + 15m (context) | Rejection wick at zone, CVD slope, delta direction |
| TC pullback | 15m (entry) + 1H (context) | Pullback depth, CVD divergence, VWAP band test |
| BO | 5m (entry) + 15m (context) | Volume spike, acceptance beyond level, OI rise |
| Scalp | 3m/5m (entry) + 15m (context) | Quick rejection, VWAP band, speed confirmation |

**Without these screenshots, the AI cannot validate proof items. The setup remains C+ (unconfirmed).**

---

## 6. CURRENT PROJECT STATUS — WHERE WE STAND

### What's BUILT and WORKING:
✅ 47 Tom video extracts, cross-referenced
✅ 7 condition files (~370 claims, 91 gaps documented)
✅ compiled_engine.md — sole runtime decision engine
✅ Math layer compiled (mts_math.py + math_object_builder.py, 98/98 tests)
✅ Hard rule enforced: AI never recomputes math
✅ 13 live trading cards generated
✅ VVP-001 screenshot protocol created
✅ Cross-trader integration (Phase 4 complete, 85 rules extracted)
✅ DSA schema v1.2.0 (weekly POC history, prior day close, volume spike)

### What's PARTIALLY BUILT:
⚠️ Visual validation — works but requires proper screenshot discipline
⚠️ Data schema — covers current snapshot, limited historical depth
⚠️ Paper trade log — template needed (Task 5)

### What's MISSING:
❌ Absorption/finished auction detection in DSA (screenshot-only currently)
❌ Intraday VP (1H/15m/5m) — screenshot-only currently
❌ Historical VP tracking (weekly VAH/VAL, 4H history)
❌ Paper trade tracking system
❌ Performance analytics

### The Core Question You Asked:

> "Does JSON show enough historical data for weekly analysis?"

**Answer: PARTIALLY.**

- VPOC migration: YES (3 weeks of POC data)
- Weekly balance stability: NO (only current week VAH/VAL)
- Weekly trend direction: PARTIAL (POC migration helps, but VAH/VAL history would confirm)

**For a complete weekly analysis, you need:**
1. DSA: weekly POC history (✅ we have this)
2. DSA: weekly VAH/VAL history (❌ missing — add prior_week_vah/val?)
3. Screenshot: visual confirmation of weekly VP shape (✅ can get from TV)

---

## 7. RECOMMENDED ACTIONS

### Immediate (This Session):
1. ✅ Task 1-3 complete (JSON card, quick check, full validation)
2. ✅ Task 4 complete (chart layout fixes identified)
3. ⏳ Task 5: Paper trade log template (NOT DSA — separate system)
4. ⏳ Task 6: VVP-001 revisions (NOT DSA — visual protocol)

### DSA-Related (See `dsa_enhancement_spec_v1.3.0.md` for full spec):
5. **PROPOSED:** `rejection_wick_quality`, `absorption_at_zone`, `finished_auction`, `delta_flip` — all specified in enhancement spec v1.3.0
6. **PROPOSED:** `cvd_divergence_details`, `volume_spike` expansion, `speed` expansion — all specified in enhancement spec v1.3.0
7. **NOT REQUESTED:** `prior_week_vah/val`, `1h_vp` — lower priority, no spec written

**Status:** Awaiting JISHU approval for `dsa_enhancement_spec_v1.3.0.md`. If approved, schema updates to v1.3.0. If rejected, these fields stay screenshot-only.

### Medium Term (Next Phase):
8. Build paper trade tracking system (NOT DSA)
9. Add performance analytics (NOT DSA)
10. Store historical snapshots for regression testing (NOT DSA)

---

# END
