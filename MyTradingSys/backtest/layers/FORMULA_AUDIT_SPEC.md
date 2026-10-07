# FORMULA_AUDIT_SPEC.md — Untested Formula Definitions (2026-10-06)

**Purpose:** Document all formulas in MTS code that currently lack corresponding unit tests, following the specification style in FORMULAS.md. These formulas are extracted directly from source code, with canonical sources listed where applicable. Expected numbers in future TEST_PLAN entries for these formulas must be derived independently from this file, never from the implementation modules.

**Status:** Initial audit complete; all formulas below are priority 1 (money-affecting runtime/math layer) or priority 2 (derived indicator logic).

---

## 17. Runtime Math Layer (`runtime/mts_math.py`) — Zone Distance & Tier Classification

### 17.1 Distance Calculation (`calculate_distance`)

**Chosen definition:** relative distance from price to zone level:
```
distance = (price - zone_price) / zone_price
```
Produces a normalized percent difference: positive when price is above zone, negative when below, zero when equal.

**Canonical source:** Derived from first principles (market convention: distance-as-fraction). Used throughout zone proximity assessment in mts_math layer.

**Purpose:** Normalize zone levels to a common scale for distance-based filtering and proximity classification.

**Worked example:** price=50100, zone_price=50000 → distance = 100/50000 = 0.002 (0.2% above zone).

### 17.2 Zone Proximity State (`get_zone_substate`)

**Chosen definition:** classify price position relative to zone level with fuzzy tolerance:
- `at_zone`: if `|distance| <= fuzz` (default fuzz=0.001, i.e., ±0.1%)
- `above_zone`: if `distance > fuzz`
- `below_zone`: if `distance < -fuzz`

**Canonical source:** Derived from operational requirement (price near level vs. clearly separated). Used in setup validation and trigger checks.

**Worked examples (fuzz=0.001):**
- price=50100, zone=50000: distance=0.002 > 0.001 → `above_zone`
- price=50000.5, zone=50000: distance=0.00001 ≤ 0.001 → `at_zone`
- price=49900, zone=50000: distance=-0.002 < -0.001 → `below_zone`

### 17.3 Distance Cap by Zone Type (`get_distance_cap`)

**Chosen definition:** lookup table of maximum distance thresholds per zone type, with optional speed-up multiplier:
```
base_cap = caps[zone_type]  # hardcoded per type
if speed_picking_up:
    cap = base_cap * 2.0
else:
    cap = base_cap
```

**Canonical source:** Operator-tuned thresholds (CLAUDE.md provenance rule: every parameter in `caps` dict must cite operator decision or transcript extract). Thresholds reflect how close to a zone price must be to trigger a setup:
- Weekly/Daily/4h/Prior-day VP levels: 0.4%–0.5%
- 15m/5m swing highs/lows: 0.3%–0.5%
- VWAP band / FVG: 0.2%

Speed-up doubles the cap when market acceleration detected (looser trigger requirements).

**Known variants:** no variants; this is MTS-specific per operator design.

**Worked example:** zone_type="weekly_vah", speed_picking_up=False → cap=0.005 (0.5%); price 50000 can trigger if within 250 points. With speed_picking_up=True → cap=0.010 (1.0%, 500 points).

### 17.4 Distance Tier Classification (`get_tier`)

**Chosen definition:** three-tier proximity classification based on distance vs. cap:
- `trigger_ready`: if `|distance| ≤ 0.001` (±0.1%, price is at zone)
- `conditional`: if `0.001 < |distance| ≤ cap` (price is close, but not yet at zone)
- `ignore`: if `|distance| > cap` (price too far, setup not yet valid)

**Canonical source:** Operational risk/reward structure (only closer zones are tradeable; far zones are noise). Used to filter candidate setups.

**Worked example:** distance=0.0008, cap=0.005 → `trigger_ready`. distance=0.002, cap=0.005 → `conditional`. distance=0.008, cap=0.005 → `ignore`.

### 17.5 Trigger Validity Check (`check_trigger_validity`)

**Chosen definition:** setup type determines valid zone substate for entry:
- **Count-Touch (ct_long, ct_short, tc_long, tc_short) and Scalp:** substate must be exactly `at_zone`
  (price must already be touching the zone to trigger these tight entries)
- **Breakout (bo_long, bo_short):** substate must be `above_zone` or `below_zone`
  (price must be breaking THROUGH the zone, not merely at it)

**Canonical source:** Setup type definition from DSA; mechanized interpretation of "entry trigger means price is AT level (count/touch) or BEYOND level (breakout)."

**Worked example:**
- Setup type=`ct_long`, substate=`at_zone` → valid (entry allowed)
- Setup type=`ct_long`, substate=`above_zone` → invalid (already passed the level, not a count-touch)
- Setup type=`bo_long`, substate=`above_zone` → valid (breakout success)
- Setup type=`bo_long`, substate=`at_zone` → invalid (not yet broken through)

### 17.6 Gross Risk/Reward Ratio (`calculate_gross_rr`)

**Chosen definition:** simple ratio of profit potential to potential loss:
```
reward = |target - entry|
risk = |entry - stop|
if risk == 0:
    gross_rr = 0.0
else:
    gross_rr = reward / risk
```

**Canonical source:** Standard risk/reward metric, universal in trading. Measures upside vs. downside exposure without cost.

**Purpose:** Sanity-check setups; later combined with friction factor for net RR.

**Worked example:** entry=50000, target=51000, stop=49500:
- reward = |51000 - 50000| = 1000
- risk = |50000 - 49500| = 500
- gross_rr = 1000 / 500 = 2.0 (2-to-1 reward:risk)

### 17.7 Net Risk/Reward After Friction (`calculate_net_rr`)

**Chosen definition:** apply friction (cost) to gross RR:
```
net_rr = gross_rr * (1.0 - friction)
```

Default friction=0.25 (25% of profit eaten by fees, slippage, spread).

**Canonical source:** Empirical friction estimation (25% accounts for Binance fees ~10 bps RT, realistic slippage, spreads).

**Purpose:** Account for trading costs in viability filter. Net RR must still pass sanity threshold after friction.

**Worked example:** gross_rr=2.0, friction=0.25 → net_rr = 2.0 * 0.75 = 1.5

### 17.8 Risk/Reward Sanity Check (`calculate_rr_sanity`)

**Chosen definition:** boolean check that RR meets minimum threshold:
```
is_sane = (gross_rr >= threshold)
```

Default threshold=1.5 (must have at least 1.5:1 gross reward:risk).

**Canonical source:** Operator/supervisor decision (every setup must have positive expectancy; 1.5:1 is the bar for entry validity). Often combined with net_rr check post-friction.

**Worked example:** gross_rr=1.5, threshold=1.5 → True (passes). gross_rr=1.4, threshold=1.5 → False (fails, rejected).

### 17.9 Confluence Detection (`detect_confluence`)

**Chosen definition:** cluster price levels if they are close together (within tolerance), report midpoint and spread of each cluster:

1. Sort zone_levels by price.
2. Iterate through sorted zones; if a zone's price is within `threshold` (relative distance) of the current cluster's midpoint, add it to the cluster; else start a new cluster.
3. Cluster midpoint = mean of all prices in the cluster. Cluster spread = max(prices) - min(prices).
4. Return only clusters with 2+ zones.

**Canonical source:** Confluence trading principle (multiple zones near the same level provide higher confidence). Midpoint-based clustering (vs. pairwise distance) avoids nested-loop quadratic behavior.

**Distance metric:** For candidate zone vs. cluster midpoint `m`, cluster is expanded if:
```
|zone_price - m| / m <= threshold
```

**Worked example (threshold=0.003 = 0.3%, base price ~50000):**
- Zones: [{"name": "swing_high_1h", "price": 50100}, {"name": "daily_vah", "price": 50110}, {"name": "weekly_poc", "price": 50050}]
- Sorted: [50050, 50100, 50110]
- Cluster 1: [50050] (first)
- Consider 50100: |50100 - 50050| / 50050 = 50/50050 ≈ 0.001 ≤ 0.003 → add to cluster 1 → [50050, 50100]
- Consider 50110: cluster midpoint = (50050 + 50100) / 2 = 50075; |50110 - 50075| / 50075 ≈ 0.0007 ≤ 0.003 → add to cluster 1 → [50050, 50100, 50110]
- All zones in 1 cluster: midpoint=50087, spread=60

---

## 18. Quadrant Classification (`runtime/quad_classify.py`)

### 18.1 Price × CVD × OI Quadrant Classifier

**Chosen definition:** Eight-way classification of market structure based on price direction × CVD momentum × OI commitment:

1. Extract 1-hour percentage changes:
   - `price_pct = (current_price - past_price_1h) / past_price_1h * 100`
   - `cvd_delta_1h = current.cvd.cvd_recent.delta_1h` (absolute delta, not percent)
   - `oi_chg_pct = current.open_interest.change_1h_pct`

2. Classify each dimension with epsilon thresholds:
   - Price direction: `PRICE_EPS = 0.05%`; `flat` if `|price_pct| < 0.05`, else `up` / `down`
   - CVD direction: `CVD_EPS = 1.0` absolute; `flat` if `|cvd_delta| < 1.0`, else `up` / `down`
   - OI direction: `OI_EPS = 0.02%`; `flat` if `|oi_chg| < 0.02`, else `up` / `down`

3. Map (price_dir, cvd_dir, oi_dir) to class:
   - (up, up, up) → `new_longs`: buyers entering, real money
   - (up, up, down) → `short_cover`: buyers dominate but OI shrinks (squeeze)
   - (up, down, up) → `distribution`: sellers controlling, OI grows (resistance)
   - (up, down, down) → `weak_rally`: drift up without conviction
   - (down, down, up) → `new_shorts`: sellers entering, real money
   - (down, down, down) → `long_liquidation`: capitulation
   - (down, up, up) → `accumulation`: buyers absorbing, OI grows
   - (down, up, down) → `weak_sell`: drift down without conviction
   - Otherwise → `flat` (no clear multi-dimensional move, or mixed signals)

4. **Delta alignment check** (optional signal quality):
   - Extract `net_delta_15m` (short-term retail flow)
   - For long-biased classes (new_longs, short_cover, accumulation, weak_sell): `delta_aligned = (net_delta_15m > 0)`
   - For short-biased classes (new_shorts, long_liquidation, distribution, weak_rally): `delta_aligned = (net_delta_15m < 0)`
   - Else: `delta_aligned = True` (no check)
   - If aligned, signal is higher quality; misalignment flags potential disagreement.

**Canonical source:** Operational classification (price + CVD + OI together reveal market structure; derived from Binance perpetual mechanics). Delta alignment is a derived quality signal (15m net delta as early-warning confirmation).

**Known variants:** Epsilons (0.05%, 1.0, 0.02%) are tunable; used here as published empirical thresholds. No alternative classification shown in literature; this is MTS-specific.

**Purpose:** Continuous market regime detection for alert routing and position management.

**Worked example:**
- price_1h_ago=50000, price_now=50010, cvd_delta=5.0, oi_chg=0.03%, nd15=100
- price_pct = 10/50000 * 100 ≈ 0.02% (< 0.05% → `flat`)
- cvd_dir: 5.0 > 1.0 → `up`
- oi_dir: 0.03% > 0.02% → `up`
- (flat, up, up) → `flat` (price flat overrides)
- Result: `{"cls": "flat", "price_pct": 0.02, "cvd_d1h": 5.0, "oi_chg": 0.03, "nd15": 100, "delta_aligned": True}`

**Second example (real move):**
- price_1h_ago=50000, price_now=50500, cvd_delta=10.0, oi_chg=0.08%, nd15=200
- price_pct = 500/50000 * 100 = 1.0% (> 0.05% → `up`)
- cvd_dir: 10.0 > 1.0 → `up`
- oi_dir: 0.08% > 0.02% → `up`
- (up, up, up) → `new_longs`
- long_bias, nd15=200 > 0 → `delta_aligned = True`
- Result: `{"cls": "new_longs", "price_pct": 1.0, "cvd_d1h": 10.0, "oi_chg": 0.08, "nd15": 200, "delta_aligned": true}`

---

## 19. Regime Classification (`runtime/regime_classifier.py`)

### 19.1 Market Structure Voting & Streak-Based Regime Confidence

**Chosen definition:** Multi-signal voting + streak confirmation + confidence graduated by streak length:

1. **Vote extraction** (from latest snapshot):
   - VWAP slope (`vs`): rising → +1 up, falling → +1 down, else → 0
   - CVD slope (`cs`): rising → +1 up, falling → +1 down, else → 0
   - Net delta 1h (`nd`): if nd > 0 → +1 up, if nd < 0 → +1 down, else → 0
   - Volume profile shape (`vp`): if P (POC higher) → +1 up, if D (POC lower) → +1 down, else → 0
   - Total: 0–4 votes up, 0–4 votes down

2. **Candidate regime** (simple majority):
   - If `up >= 3` → candidate = `TREND_UP`
   - Else if `down >= 3` → candidate = `TREND_DOWN`
   - Else → candidate = `RANGE`

3. **State machine** (persistent state in `state_code_regime.json`):
   - Track: `published` label (displayed to user), `candidate` (current), `streak` (cycles in current candidate), `consecutive` (cycles matching published), `entered_at_utc`
   - Each cycle: if candidate == previous candidate, streak++; else streak = 1
   - If candidate == published: consecutive++
   - If candidate != published AND streak >= 3: publish candidate, reset consecutive = 1, set entered_at_utc = now
   - Else: consecutive++

4. **Confidence** (graduated by streak if candidate == published):
   - If published == "UNKNOWN" → `LOW`
   - If candidate != published → `LOW`
   - If streak >= 5 → `HIGH`
   - If streak >= 3 → `MEDIUM`
   - Else → `LOW`

**Canonical source:** Operator decision (multi-signal voting for regime detection; streak > 3 required to switch published label, to avoid whipsaw). Confidence graduation is derived from this operational requirement.

**Purpose:** Track market macro structure with confirmation delay (regime doesn't flip until 3+ consecutive cycles agree).

**Worked example:**
- Initial: published="UNKNOWN", candidate="UNKNOWN", streak=0, consecutive=0, entered_at_utc=None
- Cycle 1: votes_up=3, votes_down=0 → candidate="TREND_UP"; candidate != published → consecutive=1, streak=1
- Cycle 2: votes_up=3 → candidate="TREND_UP"; candidate == previous → streak=2, consecutive=2
- Cycle 3: votes_up=3 → candidate="TREND_UP"; streak=3, consecutive=3; streak >= 3 AND candidate != published → published="TREND_UP", entered_at_utc=cycle_3_time, consecutive=1, confidence="MEDIUM"
- Cycle 4: votes_up=2, votes_down=2 → candidate="RANGE"; candidate != published → consecutive=1, streak=1, confidence="LOW"
- Cycle 5–6: same pattern → streak=3
- Cycle 7: candidate="RANGE" again, streak=4, consecutive=3 → streak >= 3 AND candidate != published → published="RANGE", consecutive=1, confidence="MEDIUM"

---

## 20. Math Object Builder Schema & Field Extraction (`runtime/math_object_builder.py`)

### 20.1 DSA Snapshot Schema Normalization

**Chosen definition:** Normalize three DSA JSON versions (old wrapped, v1.2.0 flat, v1.3.2 setup_candidates) into a common internal format:

**Old schema:**
```json
{
  "data": {
    "current_price": <float>,
    "volume_profile": {"poc": <float>, "vah": <float>, "val": <float>},
    "weekly_vp": {...},
    "vwap": {...},
    "structure": {"swing_high": <float>, "swing_low": <float>, ...},
    "conditions": {...},
    "prior_day": {...},
    "trade_flow": {...},
    "order_book_depth": {...},
    "fvg": [{"filled": <bool>, ...}],
    ...
  }
}
```

**v1.2.0 flat schema:**
```json
{
  "current_price": <float>,
  "daily_vp": {...},
  "weekly_vp": {...},
  "post_funding_vp": {...},
  "intraday_4h_vp": {...},
  "vwap": {...},
  "structure": {"1h": {...}, "15m": {...}, "5m": {...}},
  "conditions": {...},
  "prior_day": {...},
  "trade_flow": {...},
  "order_book_depth": {...},
  ...
}
```

**v1.3.2 setup_candidates schema:**
```json
{
  ...v1.2.0 fields...,
  "setup_candidates": [
    {"rank": 1, "setup_type": <str>, "zone": <float>, "math": {...}, "proof": {...}}
  ]
}
```

**Normalized format (internal contract):**
All keys present; old "fvg" array is converted to `conditions.fvg_nearest_unfilled`; old flat "structure" becomes `structure["1h"]`; missing keys default to empty dict/0.0.

**Canonical source:** DSA API evolution; normalization enables backward compatibility during v1.2→v1.3 transition.

**Purpose:** Single entry point for snapshot processing; downstream code uses normalized keys only.

### 20.2 Setup Candidate Extraction (v1.3.2)

**Chosen definition:** If snapshot contains `setup_candidates` array:
- Extract rank-1 candidate: `math_object["setup_candidate"] = candidates[0]`
- Preference: judgment layer uses `setup_candidate` (if present) preferentially over legacy zone extraction
- Fallback: legacy zone extraction continues for 2-week backward-compatibility window

**Canonical source:** Transition design (DSA sends full candidate details; MTS judgment layer prefers richer structured data over scalar zone levels).

**Purpose:** Smooth upgrade path without breaking judgment layer.

---

## 21. Book Imbalance Contradiction Logic (`runtime/math_object_builder.py:399–419`) — Live-Safety Check

### 21.1 Order Book Imbalance Direction Check

**Chosen definition:** Check if current book imbalance contradicts the intended trade direction (already correctly implemented on fast-track as of 2026-09-30):

```
if book_imbalance == 0.0 or book_imbalance is None:
    # No data; skip check (0.0 is explicitly excluded by operator approval)
    return False (no contradiction)
else if book_imbalance > 3.0:
    # Strongly bid-heavy; flag contradiction for SHORT
    if direction == "SHORT":
        return True (contradiction: book is strongly bid-heavy, SHORT entry risky)
    else:
        return False (no contradiction for LONG)
else if book_imbalance > 0.0 and < 3.0:
    # No contradiction for LONG
    return False
else if 0.0 < book_imbalance < 0.33:
    # Ask-heavy; flag contradiction for LONG
    if direction == "LONG":
        return True (contradiction: book is ask-heavy, LONG entry risky)
    else:
        return False (no contradiction for SHORT)
```

**Canonical source:** Market microstructure (bid/ask imbalance is a filling-friction indicator; matching your direction to imbalance reduces slippage). Operator-approved fix (2026-09-30): 0.0 (no Java order-book data) must skip check, not be treated as ask-heavy. Reference: Java SetupCandidatesBuilder.java:581 (skips 0.0), MarketDataSnapshot.java:213-214, SUPERVISOR_INBOX 2026-09-30 22:30Z item 1.

**Status (already fixed on fast-track):** Line 414 explicitly checks `_book != 0.0` to exclude no-data case; line 412-413 documents operator approval. This is NOT an open bug — it is already correctly implemented.

**Purpose:** Reject setups where order-book structure contradicts entry direction.

**Worked example:**
- imbalance=0.0 (no data), direction="LONG" → contradiction=False (check skipped, per operator approval)
- imbalance=0.15 (ask-heavy), direction="LONG" → contradiction=True (book argues against LONG)
- imbalance=0.15 (ask-heavy), direction="SHORT" → contradiction=False (book supports SHORT)
- imbalance=5.0 (bid-heavy), direction="SHORT" → contradiction=True (book argues against SHORT)
- imbalance=5.0 (bid-heavy), direction="LONG" → contradiction=False (book supports LONG)

**Test requirement:** Tests should verify that 0.0 correctly skips the check (no false contradiction) and that thresholds (0.33 for ask-heavy, 3.0 for bid-heavy) are applied correctly per direction.

---

## Verification Note (This Audit, 2026-10-06)

Formulas 17–21 are documented from source code inspection (no throwaway reference implementations written yet; those are future work for test-plan derivation). All section headings, parameter ranges, and class mappings are extracted verbatim from the code; no design is inferred. 

**Test derivation pathway:** Once a TEST_PLAN.md is written for any of these sections (e.g., `runtime/TEST_PLAN_math.md`), expected numbers must be computed independently using ONLY this spec, never by importing or reading the implementation modules. Each test case should include:
- Input snapshot / parameters
- Expected classification / result
- Why (reference to the rule/threshold in this spec)

**Next steps for testers:**
1. Derive worked examples for each section (as above).
2. Implement test case functions that check exact output match.
3. Verify tests fail on pre-fix code (for the book_imbalance case, and others where bug-fixes are anticipated).
4. Gate commit with full suite passing.

---

## Appendix: Untested Files Inventory

| File | Formulas | Status |
|---|---|---|
| runtime/mts_math.py | 9 core math functions (17.1–17.9) | No tests |
| runtime/quad_classify.py | 1 classifier (18.1) | No tests |
| runtime/regime_classifier.py | 1 state machine (19.1) | No tests |
| runtime/math_object_builder.py | Schema normalization + setup extraction (20.1–20.2) | Partial tests |
| runtime/update_market_state.py | State diff + formatting (calls mts_math) | No tests |
| backtest/fees.py | Cost model (may overlap FORMULAS.md §13) | No tests |
| backtest/prob_table.py | Probability lookup | No tests |
| backtest/replay.py | Event-study aggregation | No tests |

**Priority gates:**
- **P1 (live-affecting, gate before merge):** mts_math (all functions), book_imbalance fix (21.1), quad_classify, regime_classifier
- **P2 (backtest/research, can be gated separately):** fees, prob_table, replay, update_market_state
