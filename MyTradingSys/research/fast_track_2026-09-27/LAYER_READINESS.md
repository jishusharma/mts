# LAYER READINESS ASSESSMENT
# Date: 2026-09-28
# Status: READY for Phase 3 Integration Planning

---

## 1. PROBABILITY LAYER LABELS: GROWTH TRAJECTORY

### Current Status
- **Label count (2026-09-27):** 10,289 outcomes labeled
- **Target threshold:** 500+ labels ✓ EXCEEDED (2,057% of target)
- **Next gate:** 5,000 labels for frequency table MVP (achieved 2026-09-23, ~4 days ago)

### Growth Rate Analysis (14-day window)
- **2026-09-14:** ~759 labeled outcomes (design doc baseline)
- **2026-09-16:** 2,124 labels (day 2 data snapshot)
- **2026-09-27:** 10,289 labels (current)

**Rate calculation (14-day window):**
- 09-14 to 09-27 = 13 days elapsed
- Growth: 10,289 - 759 = 9,530 labels in 13 days
- **Average rate: ~733 labels/day**

### Projected Timeline
- 500-label gate: ACHIEVED (2026-09-15 estimated)
- 5,000-label gate: ACHIEVED (2026-09-23 estimated)
- 50,000-label gate: (50,000 - 10,289) / 733 = ~54 days from 2026-09-27 → **2026-11-20 (estimated)**

### Summary
**PROBABILITY LAYER LABELS: ON TRACK for Phase 3**
- Current count far exceeds 500 baseline
- 5K MVP gate already cleared; accumulation running at ~733/day
- 50K gate projected mid-November 2026 (manageable timeline for EV calibration)

Source: runtime_data/outcome_labels.json (last written 2026-09-27, 10,289 labels)

---

## 2. HISTORICAL DATA FOR LAYER BACKTESTS: OHLCV COVERAGE

### Available Data Inventory
**BTCUSDT 1-minute klines (Binance archive):**
- Range: 2025-09-01 through 2026-09-26
- Duration: **13 months, ~390 trading days**
- Granularity: 1m OHLCV bars (~560K+ bars)
- Storage: Dumps/backtest/raw/klines/ (monthly + daily files)
- Status: Recent (files updated 2026-09-27 13:49 UTC)

**Supplementary data also present:**
- Metrics (5m OI, long/short ratio): daily 2025-09-01 to 2026-09-26
- Book depth bands: daily 2025-09-01 to 2026-09-26
- Funding rates: 8h monthly 2025-09 to 2026-09
- Mark price klines: 1m 2025-09 to 2026-09

### Timeframe Sufficiency Analysis

#### MONTHLY RSI(14): **NOT YET SUFFICIENT**
**Requirement:** 14 monthly bars (≈14+ months of daily data)
**Available:** 13 complete months (2025-09 through 2026-09)
**Deficit:** 1 month short
**Current Status:** Can compute RSI on 13 monthly bars; 14th bar needed for standard RSI(14) validity
**Next window:** October 2026 klines will complete 14-month minimum
**Expected availability:** ~2026-10-31

#### WEEKLY RSI(14): **SUFFICIENT TODAY**
**Requirement:** 14 weekly bars (≈3.5 months of daily data)
**Available:** 13 months >> 3.5 months needed
**Current Status:** ✓ Can compute WEEKLY RSI(14) today on BTCUSDT
**Note:** First reliable weekly RSI (with full 14 bars lookback) producible now

#### DAILY RSI(14): **FULLY SUFFICIENT**
**Requirement:** 14 daily bars
**Available:** ~390 trading days (39x requirement)
**Current Status:** ✓ Fully supported

### Conclusion on Backtests
**Can compute MONTHLY and WEEKLY RSI(14) for BTCUSDT TODAY?**
- **WEEKLY RSI(14):** YES, today (2026-09-28)
- **MONTHLY RSI(14):** NO, need 1 additional month (Oct 2026 required); achievable 2026-10-31
- **Both together:** October 2026 for complete joint analysis

**What exactly needs downloading:**
- October 2026 daily klines (1 month, ~22 trading days, ~31.5K bars at 1m)
- Source: Binance public archive (data.binance.vision/data/futures/um/daily/klines/BTCUSDT/1m/)
- File: BTCUSDT-1m-2026-10.csv (or daily chunks 2026-10-01 through 2026-10-31)

---

## 3. CRYPTOCRED / FLOWHORSE TESTABILITY: RULE ANALYSIS TABLE

### Testability Summary by Cluster

| Cluster ID | Cluster Name | # Rules | Testable on OHLCV? | Mechanical? | Notes |
|-----------|-------------|---------|---------------------|-------------|-------|
| **C01** | Volume Profile Philosophy | 5 | Needs order flow | No | Requires TPO/delta/CVD; OHLCV insufficient |
| **C02** | Compression/Expansion | 3 | Partial (DVOL proxy) | Partly | Needs volatility compression proxy |
| **C03** | Absorption / Seller Exhaustion | 1 | Needs order flow | No | Requires large seller activity detection |
| **C04** | False Break Signatures | 3 | YES | Mostly | Low volume + rejection detectable from bars |
| **C05** | Break Validity & Continuation | 5 | YES | YES | Candle low, pullback depth, balance mechanics |
| **C06** | Zone Reliability & Test Degradation | 2 | YES | YES | Test count, retest ranking |
| **C07** | Retest Mechanics | 10 | YES | YES | Highest-density testable cluster |
| **C08** | MSB Definition & Significance | 6 | YES | YES | Structure breaks, timeframe scaling |
| **C09** | Swing Point Quality & Confluence | 4 | YES | YES | Swing selection, confluent levels |
| **C10** | Setup Types (Entry Patterns) | 5 | YES | Mostly | SR flip, pullback levels, failed MSB |
| **C11** | Entry Precision & Positioning | 4 | YES | YES | Precision/move size ratio, stop strictness |
| **C12** | Trade Management Framework | 8 | Discretionary | No | Requires active thesis reassessment |
| **C13** | Profit Taking & Targets | 5 | Discretionary | Partly | FTA framework can be automated; PT choices are heuristic |
| **C14** | Dynamic Risk/Reward | 2 | Discretionary | Partly | Can track R:R evolution; management signals discretionary |
| **C15** | Break-Even Stop Skepticism | 3 | Discretionary | No | Psychological rules; not mechanically testable |
| **C16** | Invalidation & Stop Placement | 3 | Partly | Partly | Falsifiable idea framework is testable if entry rules defined |
| **C17** | Risk/Position Sizing | 4 | YES | YES | Position formula, EV spectrum, leverage effects |
| **C18** | Psychological/Process | 5 | Discretionary | No | Process-oriented rules; not mechanically testable |
| **C20** | LVN as Rejection Zone | 1 | Needs order flow | No | Requires prior session HVN/LVN detection |

### Testability Breakdown

**FULLY TESTABLE WITH OHLCV + VOLUME (YES):**
- C04: False Break Signatures (3 rules)
- C05: Break Validity & Continuation (5 rules)
- C06: Zone Reliability (2 rules)
- C07: Retest Mechanics (10 rules)
- C08: MSB Definition & Significance (6 rules)
- C09: Swing Point Quality (4 rules)
- C10: Setup Types (5 rules)
- C11: Entry Precision & Positioning (4 rules)
- C17: Risk/Position Sizing (4 rules)

**Subtotal:** 43 rules mechanically testable with OHLCV harness

**PARTIALLY TESTABLE (needs order flow or discretion):**
- C02: Compression/Expansion (3 rules) — DVOL compression proxy possible but not ideal
- C12: Trade Management (8 rules) — Framework testable as heuristics, not mechanics
- C13: Profit Taking (5 rules) — FTA framework testable; PP heuristics not
- C14: Dynamic Risk/Reward (2 rules) — R:R evolution testable; management signals discretionary
- C16: Invalidation & Stops (3 rules) — Testable if entry rules clearly defined

**Subtotal:** 21 rules partially testable (framework exists; full execution requires domain)

**NOT TESTABLE (require order flow or psychology):**
- C01: Volume Profile Philosophy (5 rules) — Requires TPO/delta/CVD
- C03: Absorption (1 rule) — Requires order flow detection
- C15: Break-Even Stops (3 rules) — Psychological; no price-action baseline
- C18: Psychological/Process (5 rules) — Process-oriented; not price-mechanical
- C20: LVN Rejection (1 rule) — Requires HVN/LVN from order flow

**Subtotal:** 15 rules not testable on OHLCV alone

### Top 3 Most Testable Rule Groups

| Rank | Cluster | Rule Count | Why Testable | Harness Support |
|------|---------|-----------|-------------|-----------------|
| 1 | **C07: Retest Mechanics** | 10 rules | Retest definition, depth, timing all OHLCV-derived; no discretion | Full support (bt_engine can track candle-by-candle retests) |
| 2 | **C08: MSB Definition** | 6 rules | Market structure break is candle-body binary; timeframe scaling algorithmic | Full support (swing tracking in bt_ladder) |
| 3 | **C10: Setup Types** | 5 rules | SR flip, pullback zones, failed breaks all definable from price structure | Full support (entry rules in bt_data filters) |

### Implementation Roadmap

**Phase 3A (Ready Now):**
- C05, C06, C07, C08, C09, C11: 33 rules → direct bt_engine integration (structure + confluence)
- C10: 5 rules → setup pattern codification (SR flip, Fib levels, failed MSB detection)
- C17: 4 rules → risk calculator (position size formula, EV mapping)

**Phase 3B (Requires Volatility Proxy):**
- C02: 3 rules → use ATR/DVOL surrogate for compression detection
- C04: 3 rules → implement volume rejection detection (threshold TBD)

**Phase 3C (Discretionary / Beyond Scope):**
- C12, C13, C14, C15, C18: 23 rules → trade management, psychology, process (not harness-testable)
- C01, C03, C20: 7 rules → order flow required (Deribit or bookDepth archive needed)

---

## Summary Table: 73 Consolidated Rules by Testability

| Testability Category | Rule Count | Cluster IDs | Status |
|---------------------|-----------|-----------|--------|
| **Mechanical (OHLCV)** | 43 | C04, C05, C06, C07, C08, C09, C10, C11, C17 | Ready for bt harness |
| **Partial (Framework + Heuristic)** | 21 | C02, C12, C13, C14, C16 | Can backtest if discretion formalized |
| **Not Testable (Order Flow Required)** | 9 | C01, C03, C20 | Requires Deribit/bookDepth delta/OI |

---

## Ready for Phase 3?

**PROBABILITY LAYER:** ✓ YES (10.3K labels; 5K MVP cleared; 50K ETA mid-Nov)
**WEEKLY RSI(14):** ✓ YES (13 months klines available; sufficient for weekly)
**MONTHLY RSI(14):** ✗ NOT YET (need Oct 2026; achievable 2026-10-31)
**CRYPTOCRED/FLOWHORSE:** ✓ YES (43 rules directly testable; 21 partially; 9 order-flow-only)

**Blocking issues:** None critical. Oct 2026 klines will unblock MONTHLY RSI; 43 core testable rules ready for Phase 3A harness integration now.

---

Sources:
- runtime_data/label_count.json, outcome_labels.json:line 1-10 (labels inventory)
- Dumps/backtest/raw/klines/{BTCUSDT-1m-*.csv}:sorted (data availability)
- MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:line 1-986 (rule catalog & testability mapping)

## CORRECTION (coordinator, 2026-09-28)
- Section 2 was wrong: monthly RSI does not need to wait for October 2026 data. data.binance.vision has
  history back to 2020, so the fix is to download older daily bars. RESULT (2026-09-28, JIS-NB):
  `fetch_binance_archive.py --datasets klines --interval 1d --start 2019-09-01 --end 2025-08-31
  --out Dumps/backtest/raw_1d` -> 68 monthly files (2020-01..2025-08; 2019 months 404 on the archive).
  With the 1m set to 2026-09, that is about 6.7 years: monthly and weekly RSI(14) are both computable now.
- Section 1 confirmed: 10,289 labels in runtime_data/outcome_labels.json. The design's stage 3 gate is
  5,000, so the frequency-table MVP is unblocked. PROJECT_VISION's "parked (~154)" is stale.
