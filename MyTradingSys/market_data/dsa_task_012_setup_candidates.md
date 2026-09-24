# DSA_TASK_012 — PRE-COMPUTED SETUP CANDIDATES MODULE v1.3.2 (2026-09-06)

# Formal Spec for Java Developer (DSA Team/JISHU)

# Status: APPROVED — WITH POST-IMPLEMENTATION AUDIT FIXES + TARGET SELECTION UPDATE

# Scope: Move all deterministic math + proof detection from Python/AI to Java/DSA.

#        Emit one `setup_candidates` array per snapshot. AI validates top candidate only.

# Time Estimate: ~14 hours (Phase 1: 6h math/state, Phase 2: 8h proof detection)

# Backward Compatibility: DSA emits BOTH old flat fields + new `setup_candidates`.

#                         Legacy `math_object_builder.py` still works on old JSON. No breaking changes.

# Schema Version: v1.2.0 -> v1.3.1 (additive only)

---

## 0. AUDIT LOG (v1.3.1 Additions)

**Audit Date:** 2026-09-06
**Auditor:** MTS AI (Researcher/Critic)
**Basis:** `compiled_engine.md`, `zone_identification_rules.md`, `proof_requirements_formatted.md`

### 0.1 Issues Found in v1.3.0-alpha1 Implementation

| # | Issue | Severity | Fix Section |
| --- | --- | --- | --- |
| 1 | Substate misclassified: `above` instead of `at_zone` when price within +/-0.1% | Medium | Sec 2.8, Step 4 |
| 2 | `rejection_wick` proximity gate fabricated (0.1% added where spec had none) | High | Sec 9.1, 9.1.1 |
| 3 | `speed.picking_up` suppressed by fabricated `at_zone` gate | High | Sec 9.6, 9.6.1 |
| 4 | `delta_flip` attributed to wrong zone (nearest-zone rule missing) | High | Sec 9.4, 9.4.1 |
| 5 | `book_imbalance = 0.0` counted as proof signal (no-data = signal) | Medium | Sec 10, Step 10 |
| 6 | `zone.type` emitted as `"vwap"` instead of `"vwap_band"` | Low | Step 3, Zone Table |

### 0.2 Fix Summary for DSA Developer

1. **Substate:** Use engine Sec 2.8 literally: +/-0.1% = at_zone, >+0.1% = above, <-0.1% = below.
2. **rejection_wick:** Remove fabricated 0.1% proximity gate. Wick must touch zone level per Step 9.1.
3. **speed:** Remove fabricated `at_zone` gate. `picking_up = score > 5` globally, per Step 9.6.
4. **Multi-zone proof attribution:** When proof is within 0.1% of multiple zones, attribute to the **nearest zone** (min absolute distance), not the candidate being evaluated.
5. **book_imbalance:** Exclude 0.0 / no-data from proof_count.
6. **zone.type:** Emit `"vwap_band"` per zone extraction table.

---

## 1. TOP-LEVEL JSON ADDITION

Add ONE new top-level field to the existing DSA snapshot JSON:

```json
{
  // ... all existing v1.2.0 fields unchanged ...

  // NEW: setup_candidates array (may be empty)
  "setup_candidates": [
    {
      "rank": 1,
      "setup_type": "ct_short",
      "direction": "short",
      "zone": {
        "name": "pf_vah",
        "price": 78748.88,
        "type": "pf_vah"
      },
      "math": {
        "distance_pct": 0.51,
        "distance_cap": 0.4,
        "tier": "conditional",
        "substate": "above",
        "stop": 78774.0,
        "target": 77977.15,
        "gross_rr": 5.34,
        "net_rr": 4.01,
        "rr_sanity": true
      },
      "proof": {
        "rejection_wick": "STRONG",
        "rejection_wick_proximity_pct": 8.2E-5,
        "rejection_wick_actual_level": 79570.8,
        "absorption": {
          "detected": true,
          "strength": "moderate",
          "candle_count": 2,
          "vol_ratio": 3.5
        },
        "finished_auction": {
          "detected": false,
          "direction": "",
          "extreme_delta": 0.0,
          "reversal_delta": 0.0,
          "follow_through": false
        },
        "delta_flip": {
          "detected": true,
          "from_negative": true,
          "at_zone": true,
          "zone_level": 78748.88,
          "candles_since": 3,
          "actual_level": 78745.2,
          "proximity_pct": 4.7E-5
        },
        "volume_spike": {
          "detected": false,
          "magnitude": 0.0,
          "at_level": false,
          "level": 0.0
        },
        "speed": {
          "picking_up": false,
          "score": 3.0,
          "direction": "flat",
          "atr_ratio": 0.8,
          "consecutive_large": 1,
          "at_zone": false,
          "actual_level": 0.0,
          "proximity_pct": 0.0
        },
        "cvd_aligned": false,
        "book_imbalance": 0.63
      },
      "score": {
        "raw": 72,
        "confidence": "B",
        "proof_count": 3,
        "confluence_bonus": 10
      }
    }
  ]
}
```

If no valid setup exists, emit: `"setup_candidates": []`

---

## 2. ALGORITHM: HOW DSA BUILDS setup_candidates (Java Implementation Guide)

### STEP 1: STATE CLASSIFICATION (from existing fields)

**Input:** `daily_vp.shape`, `weekly_vp.shape`, `vwap.slope`, `cvd.slope`, `conditions.price_vs_va`, `conditions.price_vs_poc`, `weekly_vp.prior_week_poc`, `weekly_vp.two_week_ago_poc`

**Output:** `state` enum: `balance` | `trend_healthy` | `trend_unhealthy` | `transition`

**Algorithm (deterministic):**

1. Primary signal: `daily_vp.shape` — B -> balance, P/D -> trend
2. Secondary: `weekly_vp.shape` — weekly B overrides daily P/D to balance
3. VWAP slope: `sideways` -> balance, `sloped`/`steep` -> trend
4. CVD: `flat` + price oscillating -> balance; `aligned` -> trend; `divergent` -> trend_unhealthy
5. Price vs VWAP: oscillating -> balance; one side -> trend; extended -> trend_unhealthy
6. VPOC migration: rising/falling sequence -> trend_healthy; choppy -> transition
7. Higher TF wins: weekly > daily > intraday

---

### STEP 2: DIRECTIONAL FILTER (from existing fields)

**Input:** `conditions.price_vs_va`, `conditions.price_vs_poc`

**Output:** `evaluated_directions` array: [`short`, `long`, `both`]

**Algorithm:**

1. If `price_vs_va` = above_va -> evaluate UPPER zones for SHORTS only
2. If `price_vs_va` = below_va -> evaluate LOWER zones for LONGS only
3. If `price_vs_va` = in_va -> evaluate BOTH VAH and VAL
4. If `price_vs_va` = in_va AND `price_vs_poc` = above -> bias toward upper zones
5. If `price_vs_va` = in_va AND `price_vs_poc` = below -> bias toward lower zones

---

### STEP 3: ZONE EXTRACTION (from existing fields)

Extract all zone prices into internal list (same as `math_object_builder.py` `_extract_zones()`):

| Zone Source | Name Prefix | Type |
| --- | --- | --- |
| weekly_vp.poc/vah/val | weekly_poc, weekly_vah, weekly_val | weekly_poc, weekly_vah, weekly_val |
| daily_vp.poc/vah/val | daily_poc, daily_vah, daily_val | daily_poc, daily_vah, daily_val |
| post_funding_vp.poc/vah/val | pf_poc, pf_vah, pf_val | pf_poc, pf_vah, pf_val |
| intraday_4h_vp.poc/vah/val | 4h_poc, 4h_vah, 4h_val | 4h_poc, 4h_vah, 4h_val |
| vwap.price | vwap | **vwap_band** |
| vwap.bands.* | vwap_band_+1, vwap_band_+2, etc. | vwap_band |
| prior_day.poc/vah/val/close | prior_day_poc, prior_day_vah, prior_day_val, prior_day_close | prior_day_poc, prior_day_vah, prior_day_val, prior_day_close |
| structure.1h.swing_high/low | 1h_swing_high, 1h_swing_low | swing_high_1h, swing_low_1h |
| structure.15m.swing_high/low | 15m_swing_high, 15m_swing_low | swing_high_15m, swing_low_15m |
| structure.5m.swing_high/low | 5m_swing_high, 5m_swing_low | swing_high_5m, swing_low_5m |
| conditions.fvg_nearest_unfilled | fvg_nearest | fvg |
| naked_poc.naked_pocs[] | naked_poc_YYYY-MM-DD | weekly_poc |

**FIX v1.3.1:** `vwap.price` type must be `"vwap_band"`, not `"vwap"`.

---

### STEP 4: DISTANCE + CAP + TIER (per zone)

For each zone:

1. `distance_pct = abs(price - zone_price) / price * 100`
2. `cap = get_distance_cap(zone_type, speed_picking_up)` — use existing caps from `mts_math.py`:

| Zone Type | Cap |
| --- | --- |
| weekly_poc/vah/val | 0.5% |
| daily_poc/vah/val | 0.4% |
| 4h_poc/vah/val, pf_poc/vah/val | 0.4% |
| prior_day_poc/vah/val/close | 0.4% |
| swing_high_1h, swing_low_1h | 0.5% |
| swing_high_15m, swing_low_15m | 0.3% |
| swing_high_5m, swing_low_5m | 0.3% |
| vwap_band | 0.2% |
| fvg | 0.2% |

3. If `speed_picking_up = true`: caps remain unchanged (contextual adjustment only, per engine Sec 2.6)
4. Tier assignment:

| Distance | Tier |
| --- | --- |
| 0.0% – 0.1% | trigger_ready |
| 0.1% – cap | conditional |
| > cap | ignore |

5. If tier = ignore -> skip zone (do not include in candidates)

**FIX v1.3.1 — Substate Classification (engine Sec 2.8):**

- `at_zone`: price within +/-0.1% of zone_price (fuzz zone)
- `above`: price > +0.1% above zone_price (breakout)
- `below`: price < -0.1% below zone_price (breakdown)
- Example: price 79594.0, vwap 79577.3 -> distance 0.021% -> substate MUST be `"at_zone"`, NOT `"above"`.

---

### STEP 5: SETUP TYPE ASSIGNMENT (per zone + direction)

For each zone that passes tier filter, assign valid setup types based on zone type + directional filter:

| Zone | Short Setup | Long Setup |
| --- | --- | --- |
| VAH (weekly/daily/4h/pf) | CT Short | — |
| VAL (weekly/daily/4h/pf) | — | CT Long |
| POC | CT (unhealthy trend only) | CT (unhealthy trend only) |
| VWAP band | Scalp (if sideways) | Scalp (if sideways) |
| FVG | EXIT only | EXIT only |
| Swing High | CT Short (with confluence) | — |
| Swing Low | — | CT Long (with confluence) |
| Prior Day VAH | CT Short | — |
| Prior Day VAL | — | CT Long |
| Prior Day POC | CT (unhealthy) | CT (unhealthy) |
| Prior Day Close | CT Short (if above) | CT Long (if below) |

**Filter by state:**

- `balance` -> CT priority, Scalp if sideways
- `trend_healthy` -> TC/BO priority, CT at extremes only
- `trend_unhealthy` -> CT possible, requires exhaustion proof
- `transition` -> WAIT (no setups)

---

### STEP 6: STOP + TARGET SELECTION (per setup candidate)

For each valid (zone, setup_type) pair:

1. Determine swing TF for stop:

| Zone Type | Swing TF |
| --- | --- |
| weekly_* | 1h |
| daily_*, 4h_*, pf_*, prior_day_* | 15m |
| vwap_*, fvg_*, swing_*_5m | 5m |
| swing_*_15m | 15m |
| swing_*_1h | 1h |

2. Stop selection:

- Short setup: `stop = structure.{swing_tf}.swing_high` (must be > zone_price)
- Long setup: `stop = structure.{swing_tf}.swing_low` (must be < zone_price)

3. Target selection:

- Collect all POCs: weekly, daily, post_funding, intraday_4h, prior_day
- Collect all VALs/VAHs: daily, post_funding, intraday_4h, prior_day
  * Short target: nearest POC or VAL < zone_price (max of candidates)
  * Long target: nearest POC or VAH > zone_price (min of candidates)
- Add VWAP price as candidate if in trade direction
- Add prior_day high (short) / prior_day low (long) as candidates

**Rationale (engine Sec 7):** compiled_engine.md defines target as "Next high volume area / POC / VWAP". VAL/VAH are boundaries of high-volume areas and are valid targets per Tom's methodology. Prior day high/low provide structural target context.

4. If stop or target is null -> discard candidate

---

### STEP 7: R:R CALCULATION (per candidate)

If stop and target both exist:

1. `gross_rr = abs(target - zone_price) / abs(zone_price - stop)`
2. `net_rr = gross_rr * 0.75` (25% friction haircut)
3. `rr_sanity = gross_rr >= 1.5`
4. If `rr_sanity = false` -> discard candidate

---

### STEP 8: CONFLUENCE DETECTION

Group all remaining candidate zones. Two zones are in confluence if their prices are within 0.3% of EACH OTHER (not just price).

For each candidate, if it belongs to a confluence cluster of 2+ zones:

- `confluence_bonus = 10` (contextual weight, not numeric score modifier)

---

### STEP 9: PROOF DETECTION (Phase 2 — requires bar-level data)

DSA must have access to recent 1m or 5m bar data (OHLC + volume + delta) to compute these. If bar data unavailable, emit `detected: false` for all proof fields.

**CRITICAL v1.3.1 — PROOF-TO-ZONE ATTRIBUTION RULE:**

Before attributing ANY proof signal to a zone candidate, the DSA MUST:

1. Compute the proof event's actual price level.
2. Compute `proximity_pct = abs(actual_level - zone_price) / zone_price`.
3. Only attribute the proof to this zone if `proximity_pct <= 0.001` (0.1%).
4. If the proof event is within 0.1% of MULTIPLE zones, attribute it to the **nearest zone** (minimum absolute distance).
5. If `proximity_pct > 0.001` for a zone, set `at_zone = false` and do NOT count toward `proof_count` for that zone.

This rule applies to ALL proof types except `finished_auction` (global over last 20 bars) and `cvd_aligned` (global slope alignment).

---

#### 9.1 rejection_wick (enum: NONE / WEAK / MODERATE / STRONG)

For each of last 20 bars at zone level:

1. Check if wick touches zone:

- Support rejection: `wick_low <= zone AND close > zone`
- Resistance rejection: `wick_high >= zone AND close < zone`

2. If touched: `body_pct = abs(close - open) / (high - low)`; `wick_pct = 1.0 - body_pct`
3. Quality:

| wick_pct | body_pct | Quality |
| --- | --- | --- |
| > 0.8 | < 0.2 | STRONG |
| > 0.5 | < 0.5 | MODERATE |
| any | any | WEAK |

Return highest quality found across all bars. If none touched -> NONE.

**FIX v1.3.1 — No Proximity Gate (Sec 9.1.1):**
The spec for `rejection_wick` requires the wick to **touch the zone level** (`wick_low <= zone` or `wick_high >= zone`). There is NO 0.1% proximity gate for rejection_wick. A wick at the 5m swing low (79570.8) that does NOT touch VWAP (79577.3) must NOT be credited to the VWAP candidate. It belongs to the `5m_swing_low` candidate.

**Schema fields:**

```json
"rejection_wick": "STRONG",
"rejection_wick_proximity_pct": 8.2E-5,
"rejection_wick_actual_level": 79570.8
```

---

#### 9.2 absorption (object: {detected, strength, candle_count, vol_ratio})

For each of last 10 bars where price within 0.1% of zone:

1. `volume > 2.0 * avg_volume_20`
2. `(high - low) < 0.3 * atr_14`
3. Delta opposite to price direction:

- `delta > 0 AND close < open` (buying pressure but price down)
- `delta < 0 AND close > open` (selling pressure but price up)

If 1+2+3 true for any bar:

- `detected = true`
- `strength = (max_vol / avg_vol > 5.0) ? strong : moderate`
- `candle_count = count of matching bars`
- `vol_ratio = max_vol / avg_vol`

---

#### 9.3 finished_auction (object: {detected, direction, extreme_delta, reversal_delta, follow_through})

For each bar i in last 20:

1. `abs(bar[i].delta) > 3.0 * avg_delta_20` -> extreme delta
2. Next bar reverses:

- `bar[i].delta < 0 AND bar[i+1].close > bar[i].close` (sell extreme -> reversal up)
- `bar[i].delta > 0 AND bar[i+1].close < bar[i].close` (buy extreme -> reversal down)

3. No follow-through: `abs(bar[i+1].delta) < 0.5 * abs(bar[i].delta)`

If all 3:

- `detected = true`
- `direction = bar[i].delta < 0 ? sell : buy`
- `extreme_delta = bar[i].delta`
- `reversal_delta = bar[i+1].delta`
- `follow_through = false`

**Note:** `finished_auction` is computed globally over last 20 bars. It does NOT have a proximity gate because the spec does not require one. It is a global market structure signal.

**Schema default:** When `detected = false`, emit `follow_through = false` (not `true`). All other fields (`direction`, `extreme_delta`, `reversal_delta`) should be empty string / 0.0.

---

#### 9.4 delta_flip (object: {detected, from_negative, at_zone, zone_level, candles_since, actual_level, proximity_pct})

For each bar i in last 20:

1. `bar[i-1].delta < 0 AND bar[i].delta > 0` (negative -> positive) OR `bar[i-1].delta > 0 AND bar[i].delta < 0` (positive -> negative)
2. `abs(bar[i].close - zone_level) < 0.001 * zone_level` (within 0.1% of zone)

If both:

- `detected = true`
- `from_negative = bar[i-1].delta < 0`
- `at_zone = true`
- `zone_level = zone_level`
- `candles_since = i` (bars since flip, 0 = current)
- `actual_level = bar[i].close`
- `proximity_pct = abs(actual_level - zone_level) / zone_level`

**FIX v1.3.1 — Nearest-Zone Attribution (Sec 9.4.1):**
When a delta flip is within 0.1% of multiple zones (e.g., 79655.3 is 0.098% from VWAP 79577.3 but only 0.016% from PF POC 79667.82), attribute the flip to the **nearest zone** (minimum absolute distance). In this example, the flip belongs to the PF POC / 4H POC / daily VAH cluster, NOT to VWAP.

---

#### 9.5 volume_spike (object: {detected, magnitude, at_level, level, actual_level, proximity_pct})

Refactor existing `volume_spike_at_level` boolean:

1. `magnitude = current_volume / avg_volume_4h`
2. `detected = magnitude > 2.0`
3. `at_level = price within 0.1% of zone`
4. `level = zone_price`
5. `actual_level = bar.close` (or VWAP of bar)
6. `proximity_pct = abs(actual_level - zone_price) / zone_price`

---

#### 9.6 speed (object: {picking_up, score, direction, atr_ratio, consecutive_large, at_zone, actual_level, proximity_pct})

Refactor existing `speed_picking_up` boolean:

1. `atr_current = atr_14`
2. `atr_baseline = atr_14 over prior 20 bars`
3. `atr_ratio = atr_current / atr_baseline`
4. `large_candles = count of last 10 bars where (high-low) > 1.5 * avg_range`
5. `consecutive = max consecutive large candles`
6. `score = min(10, (atr_ratio * 3) + (consecutive * 2))`
7. `picking_up = score > 5`
8. `direction = price_trend_direction`

**FIX v1.3.1 — No at_zone Gate (Sec 9.6.1):**
The spec defines `picking_up` purely by score threshold (> 5). There is **NO `at_zone` requirement** for speed. Speed is a **global market condition**, not a zone-local proof. The DSA must NOT suppress `picking_up = true` because the speed event is not exactly at the zone level.

With score = 10.0, `picking_up` MUST be `true`.

Schema fields `at_zone`, `actual_level`, `proximity_pct` are OPTIONAL for speed (for diagnostic purposes only). They must NOT affect the `picking_up` boolean.

---

#### 9.7 cvd_aligned (boolean)

`cvd.slope` direction matches `trade_flow.net_delta` direction:

- CVD rising + net_delta > 0 -> true
- CVD falling + net_delta < 0 -> true
- Otherwise -> false

Use `cvd_recent.slope_1h` as tiebreaker if main CVD slope ambiguous.

---

### STEP 10: SCORING (per candidate)

`raw_score` is a composite for ranking only. NOT a verdict. AI still judges contextually.

```java
int proof_count = 0;
if (!rejection_wick.equals(NONE)) proof_count++;
if (absorption.detected) proof_count++;
if (finished_auction.detected) proof_count++;
if (delta_flip.detected && delta_flip.at_zone) proof_count++;
if (volume_spike.detected && volume_spike.at_level) proof_count++;
if (speed.picking_up) proof_count++;
if (cvd_aligned) proof_count++;
if (book_imbalance != 0.0 && (book_imbalance < 0.4 || book_imbalance > 0.6)) proof_count++;

int raw = 50; // base
raw += proof_count * 7; // +7 per proof signal
raw += confluence_bonus; // +10 if in confluence cluster
raw = Math.min(95, raw); // Cap at 95

// Confidence band
String confidence;
if (raw >= 70) confidence = "B";
else if (raw >= 55) confidence = "C+";
else if (raw >= 40) confidence = "C";
else confidence = "D";
```

**FIX v1.3.1 — book_imbalance Scoring:**
`book_imbalance = 0.0` means **no order-book data** (historical mode, confidence LOW). Counting "no data" as a directional proof signal is logically wrong. The condition must exclude 0.0:

```java
if (book_imbalance != 0.0 && (book_imbalance < 0.4 || book_imbalance > 0.6)) proof_count++;
```

---

### STEP 11: RANKING + OUTPUT

1. Sort all candidates by `raw_score` descending
2. If tie, prefer: higher TF zone > lower TF zone
3. Assign `rank` 1, 2, 3...
4. Emit top N candidates (recommend N=3 max to keep JSON compact)
5. If no candidates pass all filters -> emit `[]`

---

## 3. BACKWARD COMPATIBILITY

DSA emits BOTH during transition (minimum 2 weeks):

```json
{
  // OLD fields (v1.2.0) — still present
  "rejection_wick_at_zone": true,
  "volume_spike_at_level": true,
  "speed_picking_up": false,

  // NEW fields (v1.3.1)
  "setup_candidates": [
    {
      "proof": {
        "rejection_wick": "STRONG",
        "volume_spike": { "detected": true, "magnitude": 3.5 },
        "speed": { "picking_up": false, "score": 3 }
      }
    }
  ]
}
```

Legacy `math_object_builder.py` reads old fields. New code reads `setup_candidates`. Both work.
After transition (Week 3+), old booleans may be deprecated.

---

## 4. VALIDATION PROTOCOL (Rule 32)

After Phase 1+2 implementation, test on 3 historical snapshots:

| Test | Check | Pass Criteria |
| --- | --- | --- |
| 1 | DSA rank 1 candidate == AI manually computed rank 1 | Match on zone + setup_type |
| 2 | DSA proof signals match screenshot visual analysis | 2+ of 3 snapshots agree |
| 3 | DSA state classification matches AI state | 3/3 match |
| 4 | DSA R:R matches Python `math_object_builder` | Within 0.01 tolerance |
| 5 | Proof proximity fields populated and accurate | `proximity_pct` matches actual distance |
| 6 | No proof attributed to wrong zone | Visual cross-check confirms zone-level proof |

If any test fails -> debug DSA algorithm before integration.

**v1.3.1 Additional Test Case (BTCUSDT @ 2026-09-05 09:58:15Z):**

- Input: Provided snapshot
- Expected after fix:
- `setup_candidates[0].zone.name` = "vwap"
- `setup_candidates[0].proof.rejection_wick` = "NONE" (wick at 79570.8 is swing low, not VWAP)
- `setup_candidates[0].proof.delta_flip.at_zone` = false (flip at 79655.3 is closer to PF POC)
- `setup_candidates[0].proof.speed.picking_up` = true (score 10.0 > 5)
- `setup_candidates[0].score.raw` = ~57-64 (not 71-78)
- `setup_candidates[0].score.confidence` = "C+" (not "B")

---

## 5. ENGINE INTEGRATION (After DSA Validation)

1. `math_object_builder.py` updated to read `setup_candidates` directly (skip zone extraction + math)
2. AI judgment layer receives `setup_candidates[0]` as primary candidate
3. AI validates: cross-check proof signals, apply session context, apply hard stops
4. AI generates verdict + card
5. Screenshot becomes OPTIONAL quality check, not requirement

---

## 6. CROSS-TRADER GAP UNLOCKS

| This Field | Unlocks Entry | Engine Section |
| --- | --- | --- |
| proof.absorption | C03-E01 (Heavy Selling + No Breakdown = Absorption) | Sec 4 Proof Types |
| zone_intelligence.test_count | C06-E01 (Test Count Degradation) | Sec 2.7 Confluence |
| proof.finished_auction | Tom footprint proof | Sec 4 Proof Types |
| proof.delta_flip | Tom CVD proof | Sec 4 Proof Types |

---

## 7. WHAT'S EXCLUDED (Not in This Task)

| Item | Why Excluded |
| --- | --- |
| Liquidation data fix | DSA infrastructure issue, not a field spec |
| Trade flow timeframe tag | Metadata, not proof |
| Zone test count | Requires 48h history — may not be available |
| CVD divergence expansion | Boolean works; expansion is polish |
| Composite profiles | VP histogram API limitation |
| Fibonacci retracements | Not a Tom concept |

---

## 8. CHANGE LOG

| Version | Date | Changes |
| --- | --- | --- |
| v1.3.0-alpha1 | 2026-09-04 | Initial spec |
| v1.3.2 | 2026-09-06 | Post-implementation audit fixes: substate rule, rejection_wick proximity gate removed, speed at_zone gate removed, nearest-zone attribution rule, book_imbalance scoring fix, zone.type fix, validation test case added, target selection expanded to include VAL/VAH and prior_day high/low |

---

# END