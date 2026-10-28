# FILE: mts/tests/compiled_code_opportunities.md
# READ ORDER: Before UNIT_TEST_PLAN.md
# PURPOSE: Map every compiled_engine.md function to: compiled vs AI-reasoning
# Date: 2026-08-30
# Status: ACTIVE v4.2.0-p5
# Canonical path: /mnt/agents/output/upload_mirror/mts/tests/compiled_code_opportunities.md
# ---

# COMPILED CODE OPPORTUNITIES — MTS v4.2.0-p5
# Goal: Identify every decision point in compiled_engine.md that can be
#       replaced with deterministic compiled code instead of AI reasoning.
# Principle: AI reasoning is reserved for visual validation, pattern recognition,
#            and contradiction resolution. Everything else = compiled.

---

## EXECUTIVE SUMMARY

| Category | Functions | Compile? | Why |
|----------|-----------|----------|-----|
| Pure math | 23 | YES | Deterministic, no ambiguity |
| Table lookup | 12 | YES | Decision tables = perfect for code |
| State machine | 8 | YES | Finite states, deterministic transitions |
| Data validation | 6 | YES | Schema checks, field presence |
| Scoring / ranking | 5 | YES | Weighted sums, sort, select |
| Visual flags | 4 | NO | Require screenshot analysis (AI) |
| Contradiction resolution | 2 | PARTIAL | Rules are compiled, but edge cases need AI |
| Verdict formatting | 1 | YES | Template fill from computed values |

**Total: 61 functions. 55 = COMPILE. 4 = AI-ONLY. 2 = HYBRID.**

**Impact:** Compiling 55 functions removes ~90% of AI reasoning from the
JSON-to-card pipeline. Remaining AI work: visual gap flags + contradiction
edge cases + prose generation.

---

## SECTION-BY-SECTION BREAKDOWN

### SEC 1: STATE CLASSIFICATION (8 functions)

| # | Function | Inputs | Outputs | Compile? | Notes |
|---|----------|--------|---------|----------|-------|
| 1.1 | `classify_state` | vp_shape, vwap_slope, cvd, price_vs_vwap, htf_shape | Balance / Trend-healthy / Trend-unhealthy / Transition | YES | Table lookup. All inputs from JSON. |
| 1.2 | `check_breakdown_override` | price, weekly_vah, weekly_val | boolean (override to Trend-healthy) | YES | Pure math: >0.3% outside VA boundary. |
| 1.3 | `check_double_distribution` | weekly_vp histogram (visual) | bias, target, setup_type | NO | Visual flag. Requires screenshot. DSA cannot emit distribution_count. |
| 1.4 | `check_single_print` | weekly_vp histogram (visual) | target_levels, entry_block | NO | Visual flag. Requires screenshot. DSA cannot emit single_print_areas. |
| 1.5 | `apply_exhaustion_gate` | volume_spike_at_level, setup_type | confidence_delta (+10/-10/+5) | YES | Table lookup. Pure math. |
| 1.6 | `get_valid_setups` | state | [primary, secondary, avoid] | YES | Table lookup. State -> Setup Matrix. |
| 1.7 | `evaluate_vpoc_migration` | current_poc, prior_poc, two_week_poc, liquidity | bias_direction, confidence_mod | YES | Pure comparison + liquidity check. |
| 1.8 | `resolve_htf_conflict` | weekly_state, daily_state, intraday_state | weekly wins | YES | Hard rule: Weekly > Daily > Intraday. |

**SEC 1 Compile Ratio: 6/8 = 75%** (2 visual flags = AI-only)

---

### SEC 2: ZONE MAP (10 functions)

| # | Function | Inputs | Outputs | Compile? | Notes |
|---|----------|--------|---------|----------|-------|
| 2.1 | `get_zone_trigger` | zone_name, direction | [setup_types] | YES | Table lookup. Zone -> Trigger Matrix. |
| 2.2 | `get_zone_distance_cap` | zone_type | percentage | YES | Table lookup. Per-zone-type caps. |
| 2.3 | `check_zone_proximity` | price, zone_level, cap | tier (trigger/conditional/ignore) | YES | Pure math: abs distance vs thresholds. |
| 2.4 | `evaluate_prior_day_close` | price, prior_day_close | bias, setup, distance_cap | YES | Pure comparison + 0.4% cap. |
| 2.5 | `check_swing_confluence` | swing_level, vp_level | confluence_boolean, midpoint | YES | Pure math: within 0.3% of each other. |
| 2.6 | `evaluate_fvg` | fvg_list, price | exit_zones (NOT entry) | YES | Filter: FVG = target only. |
| 2.7 | `check_single_print_block` | zone_level, single_print_areas | block_entry_boolean | YES | If single print area known, block entry. |
| 2.8 | `get_tom_rule_for_zone` | zone_name | quote, source_gps | NO | Prose lookup. Used for card output only. |
| 2.9 | `validate_zone_for_setup` | zone, setup_type, substate | valid/invalid + reason | YES | Table lookup. Sub-State -> Setup validity. |
| 2.10 | `check_zone_is_exit_only` | zone_type | boolean | YES | FVG and Single Print = exit only. |

**SEC 2 Compile Ratio: 9/10 = 90%** (1 prose lookup = AI for card generation)

---

### SEC 2.4: MULTI-TF ZONE EVALUATION (12 functions)

| # | Function | Inputs | Outputs | Compile? | Notes |
|---|----------|--------|---------|----------|-------|
| 2.4.1 | `apply_directional_filter` | price_vs_va, price_vs_poc, zones | filtered_zones | YES | Table lookup. Directional Filter Matrix. |
| 2.4.2 | `calculate_distance` | price, boundary | abs_dist, pct_dist | YES | Pure math. |
| 2.4.3 | `filter_by_distance` | zones, caps | zones_within_cap | YES | Pure math: pct_dist <= cap. |
| 2.4.4 | `calculate_rr` | entry, stop, target | gross_rr, net_rr | YES | Pure math. |
| 2.4.5 | `match_swing_tf` | zone_precision | swing_tf (1h/15m/5m) | YES | Table lookup. Weekly/Daily->1h, 4H->15m, Scalp->5m. |
| 2.4.6 | `validate_swing_low` | swing_low, entry_price | valid/invalid + fallback | YES | Pure comparison: swing_low < entry. |
| 2.4.7 | `check_swing_cluster` | swing_levels | cluster_boolean, lowest | YES | Pure math: within 0.1% = cluster. |
| 2.4.8 | `check_clustered_zone_target` | next_poc, stop_dist, entry | skip_boolean, next_target | YES | Pure math: reward < 2x risk -> skip. |
| 2.4.9 | `check_acceleration_target_override` | speed_picking_up, price_vs_va | override_boolean, new_target | YES | Boolean + conditional target selection. |
| 2.4.10 | `calculate_confluence_score` | zones, threshold=0.3% | bonus (+0/+10/+20) | YES | Pure math: group within threshold. |
| 2.4.11 | `calculate_composite_score` | net_rr, confluence_bonus, tf_weight | composite_score | YES | Pure math: net_rr * bonus * weight. |
| 2.4.12 | `select_best_zone` | zones_with_scores | primary_zone, conditional_flag | YES | Sort descending. Tie = higher TF wins. |

**SEC 2.4 Compile Ratio: 12/12 = 100%**

---

### SEC 2.5: DIRECTIONAL FILTER (4 functions)

| # | Function | Inputs | Outputs | Compile? | Notes |
|---|----------|--------|---------|----------|-------|
| 2.5.1 | `apply_directional_filter_core` | price_vs_va, zones | [short_zones, long_zones, skip] | YES | Table lookup. Directional Filter Matrix. |
| 2.5.2 | `apply_secondary_bias` | price_vs_poc | slight_bias | YES | Table lookup. price_vs_poc -> bias. |
| 2.5.3 | `check_trend_strength_override` | price, weekly_va_boundary | boolean + expanded_filter | YES | Pure math: >0.5% outside = override. |
| 2.5.4 | `check_ct_retest_requirement` | price, broken_boundary, direction | valid/invalid | YES | Pure math: retest from outside with rejection. |

**SEC 2.5 Compile Ratio: 4/4 = 100%**

---

### SEC 2.6: DISTANCE CAP (4 functions)

| # | Function | Inputs | Outputs | Compile? | Notes |
|---|----------|--------|---------|----------|-------|
| 2.6.1 | `get_distance_cap` | zone_type, speed_picking_up | cap_percentage | YES | Table lookup. Base cap * 2 if speed. |
| 2.6.2 | `get_tier` | distance, cap | trigger-ready / conditional / ignore | YES | Pure math: 0-0.1% / 0.1%-cap / >cap. |
| 2.6.3 | `check_volatility_expansion` | speed_picking_up, atr_15m, atr_daily | boolean | YES | Pure math: 15m ATR > 2x daily = true. |
| 2.6.4 | `check_acceleration_mode` | speed_picking_up, price_vs_va | boolean + behavior_changes | YES | Boolean + 4 behavior change flags. |

**SEC 2.6 Compile Ratio: 4/4 = 100%**

---

### SEC 2.7: CONFLUENCE SCORING (2 functions)

| # | Function | Inputs | Outputs | Compile? | Notes |
|---|----------|--------|---------|----------|-------|
| 2.7.1 | `detect_confluence` | zones, threshold=0.3% | clusters | YES | Pure math: group within threshold. |
| 2.7.2 | `calculate_confluence_bonus` | cluster_size | +0 / +10 / +20 | YES | Table lookup. 2 zones = +10, 3+ = +20. |

**SEC 2.7 Compile Ratio: 2/2 = 100%**

---

### SEC 2.8: ZONE SUB-STATES (2 functions)

| # | Function | Inputs | Outputs | Compile? | Notes |
|---|----------|--------|---------|----------|-------|
| 2.8.1 | `get_zone_substate` | price, zone_level | at_zone / above_zone / below_zone | YES | Pure math: +/- 0.1% threshold. |
| 2.8.2 | `check_trigger_validity` | substate, setup_type | valid/invalid | YES | Table lookup. Sub-State -> Setup validity. |

**SEC 2.8 Compile Ratio: 2/2 = 100%**

---

### SEC 3: SETUP VALIDITY (1 function)

| # | Function | Inputs | Outputs | Compile? | Notes |
|---|----------|--------|---------|----------|-------|
| 3.1 | `validate_setup` | setup, state, zone, proof, substate | valid/invalid + reason | YES | Table lookup. Setup Validity table. |

**SEC 3 Compile Ratio: 1/1 = 100%**

---

### SEC 4: PROOF TYPES (4 functions)

| # | Function | Inputs | Outputs | Compile? | Notes |
|---|----------|--------|---------|----------|-------|
| 4.1 | `check_proof_present` | proof_types, json_data | [present], [missing] | YES | Field presence + value checks. |
| 4.2 | `resolve_cvd_trade_flow_contradiction` | cvd_slope, trade_flow, aligned_flag | direction + confidence | PARTIAL | Rules are compiled (aligned=true/false/null). But "flag for visual validation" when null = AI decision. |
| 4.3 | `evaluate_oi_trend` | oi_direction, price_direction | confirmation/caution | YES | Table lookup. 4-state matrix. |
| 4.4 | `weight_proof` | proof_type, setup_type | weight (primary/secondary) | YES | Table lookup. Proof Types table. |

**SEC 4 Compile Ratio: 3/4 = 75%** (1 hybrid: contradiction null case = AI)

---

### SEC 5: TRIGGER HIERARCHY (1 function)

| # | Function | Inputs | Outputs | Compile? | Notes |
|---|----------|--------|---------|----------|-------|
| 5.1 | `evaluate_trigger_hierarchy` | setup, tier1, tier2, tier3 | trigger_type + entry_method | YES | Table lookup. Trigger Hierarchy table. |

**SEC 5 Compile Ratio: 1/1 = 100%**

---

### SEC 6: HARD STOPS (1 function)

| # | Function | Inputs | Outputs | Compile? | Notes |
|---|----------|--------|---------|----------|-------|
| 6.1 | `check_hard_stops` | setup, proof, price_at_zone, stop, rr, htf, volume, tf, chasing | abort/continue + reason | YES | 9 boolean checks. Any true = abort. |

**SEC 6 Compile Ratio: 1/1 = 100%**

---

### SEC 7: RISK MATH (3 functions)

| # | Function | Inputs | Outputs | Compile? | Notes |
|---|----------|--------|---------|----------|-------|
| 7.1 | `calculate_rr_sanity` | stop, target, entry | pass/fail | YES | Pure math: (target-zone)/(zone-stop) < 1.5 = fail. |
| 7.2 | `calculate_gross_rr` | target, entry, stop | ratio | YES | Pure math. |
| 7.3 | `calculate_net_rr` | gross_rr | ratio * 0.75 | YES | Pure math. |

**SEC 7 Compile Ratio: 3/3 = 100%**

---

### SEC 8: VERDICT BANDS (2 functions)

| # | Function | Inputs | Outputs | Compile? | Notes |
|---|----------|--------|---------|----------|-------|
| 8.1 | `calculate_verdict_band` | score | A/B/C+/C/D | YES | Range checks: 90-100=A, 70-89=B, 55-69=C+, 40-54=C, 0-39=D. |
| 8.2 | `calculate_score` | mandatory, primary, secondary, rr, confluence | 0-100 | YES | Weighted sum. Deterministic. |

**SEC 8 Compile Ratio: 2/2 = 100%**

---

### SEC 10: DECISION DIAMOND (1 function)

| # | Function | Inputs | Outputs | Compile? | Notes |
|---|----------|--------|---------|----------|-------|
| 10.1 | `run_decision_diamond` | data_ok, state_known, zones, mode, proof, trigger, rr | verdict + abort_reason | YES | State machine. 7 gates, each YES/NO. |

**SEC 10 Compile Ratio: 1/1 = 100%**

---

### SEC 11: SCREENSHOT TIMEFRAME GUIDANCE (1 function)

| # | Function | Inputs | Outputs | Compile? | Notes |
|---|----------|--------|---------|----------|-------|
| 11.1 | `get_recommended_footprint_tf` | setup_level | tf (1h/15m/5m/1m) | YES | Table lookup. Level -> TF mapping. |

**SEC 11 Compile Ratio: 1/1 = 100%**

---

## SUMMARY TABLE

| Section | Functions | Compile | AI-Only | Hybrid | Compile % |
|---------|-----------|---------|---------|--------|-----------|
| 1. State Classification | 8 | 6 | 2 | 0 | 75% |
| 2. Zone Map | 10 | 9 | 0 | 1 | 90% |
| 2.4 Multi-TF Evaluation | 12 | 12 | 0 | 0 | 100% |
| 2.5 Directional Filter | 4 | 4 | 0 | 0 | 100% |
| 2.6 Distance Cap | 4 | 4 | 0 | 0 | 100% |
| 2.7 Confluence Scoring | 2 | 2 | 0 | 0 | 100% |
| 2.8 Zone Sub-States | 2 | 2 | 0 | 0 | 100% |
| 3. Setup Validity | 1 | 1 | 0 | 0 | 100% |
| 4. Proof Types | 4 | 3 | 0 | 1 | 75% |
| 5. Trigger Hierarchy | 1 | 1 | 0 | 0 | 100% |
| 6. Hard Stops | 1 | 1 | 0 | 0 | 100% |
| 7. Risk Math | 3 | 3 | 0 | 0 | 100% |
| 8. Verdict Bands | 2 | 2 | 0 | 0 | 100% |
| 10. Decision Diamond | 1 | 1 | 0 | 0 | 100% |
| 11. Screenshot TF | 1 | 1 | 0 | 0 | 100% |
| **TOTAL** | **55** | **51** | **2** | **2** | **93%** |

---

## WHAT REMAINS FOR AI REASONING (7%)

### 1. Visual Flags (2 functions — AI-ONLY)

| Function | Why AI? |
|----------|---------|
| `check_double_distribution` | Requires histogram screenshot analysis. DSA cannot emit distribution_count without histogram API. |
| `check_single_print` | Requires histogram screenshot analysis. DSA cannot emit single_print_areas without histogram API. |

**Mitigation:** These are VISUAL FLAGS in compiled_engine.md. The compiled code
should emit: "[VISUAL FLAG] Check weekly VP histogram for double distribution."
The AI then analyzes the screenshot and returns true/false. The decision RULE
(when true, what to do) is compiled. Only the detection is AI.

### 2. Contradiction Edge Cases (1 function — HYBRID)

| Function | Compiled Part | AI Part |
|----------|--------------|---------|
| `resolve_cvd_trade_flow_contradiction` | aligned=true/false paths are compiled | aligned=null -> "flag for visual validation" = AI decides whether to proceed or wait |

**Mitigation:** The compiled code handles the 2 deterministic paths (aligned,
not aligned). The null path emits a visual flag. AI decides based on context.

### 3. Card Prose Generation (AI-ONLY, not a function)

The trading card output requires natural language generation. This is inherently
AI. However, the compiled code can produce a STRUCTURED DATA OBJECT containing
all verdict components. The AI then formats this into prose.

**Proposed architecture:**
```
JSON -> [COMPILED ENGINE] -> structured_verdict_object -> [AI FORMATTER] -> trading_card.md
```

The compiled engine produces:
```json
{
  "verdict_band": "C+",
  "score": 58,
  "setup": "CT Long",
  "zone": {"name": "Post-funding VAL", "price": 78008.84, "distance_pct": 0.02},
  "confluence": [{"zones": ["Post-funding VAL", "Weekly VAL"], "bonus": 10}],
  "rr": {"gross": 3.33, "net": 2.50, "stop": 77625.6, "target": 79284.54},
  "proof_present": ["B profile", "trade_flow_positive"],
  "proof_missing": ["absorption", "rejection_wick"],
  "trigger_needed": ["retest with rejection at zone on 15m"],
  "invalidation": 77625.6,
  "visual_flags": ["Check weekly histogram for double distribution"],
  "hard_stops": [],
  "state": "Balance",
  "confidence_modifiers": []
}
```

The AI formatter takes this object and produces the human-readable card.

---

## IMPLEMENTATION PRIORITY

### Phase 1: Core Pipeline (Week 1)
| Priority | Function Group | Impact | Complexity |
|----------|---------------|--------|------------|
| P0 | Decision Diamond (10.1) + State Classification (1.1, 1.2) | Highest — gates everything | Low |
| P0 | Hard Stops (6.1) | Highest — prevents bad trades | Low |
| P0 | Setup Validity (3.1) | High — filters invalid setups | Low |
| P1 | Directional Filter (2.5.x) | High — eliminates 50% of zones | Low |
| P1 | Distance Cap + Tier (2.6.x) | High — precision filtering | Low |

### Phase 2: Scoring & Selection (Week 2)
| Priority | Function Group | Impact | Complexity |
|----------|---------------|--------|------------|
| P1 | Zone Evaluation (2.4.x) | High — finds best zone | Medium |
| P1 | R:R Math (7.x) | High — math gate | Low |
| P1 | Confluence Scoring (2.7.x) | Medium — confidence boost | Low |
| P2 | Verdict Bands (8.x) | Medium — final classification | Low |

### Phase 3: Polish (Week 3)
| Priority | Function Group | Impact | Complexity |
|----------|---------------|--------|------------|
| P2 | Proof Types (4.x) | Medium — proof validation | Medium |
| P2 | Trigger Hierarchy (5.1) | Medium — entry timing | Low |
| P2 | Zone Map (2.x) | Low — zone lookup | Low |
| P3 | Screenshot TF (11.1) | Low — convenience | Low |

---

## COMPILED ENGINE INTEGRITY CHECKLIST

Before any function is marked "COMPILED", it must pass:

1. [ ] All inputs are present in DSA JSON schema v1.2.0
2. [ ] All outputs are consumed by downstream functions or card formatter
3. [ ] All thresholds match compiled_engine.md exactly (0.1%, 0.3%, 0.4%, 0.5%, 1.5, 2.0, etc.)
4. [ ] All table lookups match compiled_engine.md exactly (no invented rows)
5. [ ] Unit tests cover: happy path, boundary, error/null input
6. [ ] Integration test: full pipeline from JSON to structured_verdict_object

---
# END
