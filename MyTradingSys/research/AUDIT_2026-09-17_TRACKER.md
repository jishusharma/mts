# AUDIT TRACKER - 2026-09-17
# Independent code review. Coordinator tracks, worker investigates.
# Worker = fresh chat instance. Coordinator = this session.

## PROTOCOL
- Operator runs each block, pastes output to worker chat. Worker analyzes only.
- Coordinator verifies the output, updates this file, issues next block.
- Each finding needs two receipts. Unconfirmed findings are dropped.
- No writes to runtime state by worker. Coordinator writes this tracker only.

## SCOPE
Java:  MarketDataSnapshot.java, SetupCandidatesBuilder.java, StateCodeEmitter.java,
       ExtraSetupBuilder.java, SetupScreener.java
Py:    mts_math.py, math_object_builder.py, quad_classify.py, regime_classifier.py,
       update_market_state.py
Tests: test_mts_math.py, test_math_object_builder.py, test_session_state.py,
       state_signal_prototype.py
Conds: entry_timing_triggers.md, setup_type_rules.md, zone_identification_rules.md,
       risk_protocol.md, market_state_rules.md

## KNOWN CLAIMS TO VERIFY OR REFUTE
1. buildVp emits TWOPEAK for two-peak profiles. classifyState no longer reads shape.
2. B profile = weakness at the extreme (Tom).
3. Rule 32 test passed 3/3 for classifyState rewrite.
4. STATE.classification in mts_math.py matches Java classifyState.
5. SetupScreener is dead code, never called.

## PROGRESS
Step 1: method inventory. IN PROGRESS. MarketDataSnapshot.java DONE (4 ranges, 1388 lines, 23 methods per worker final). SetupCandidatesBuilder.java DONE (3 ranges, 827 lines, 19 methods + 3 inner classes). Next: math_object_builder.py.
Step 2: dual-builder path audit (MarketDataSnapshot). PENDING.
Step 3: classifyState downstream consumers. PENDING.
Step 4: Python field readers vs snapshot. PENDING.
Step 5: test coverage gaps. PENDING.
Step 6: dead output / dead input sweep. PENDING.
Step 7: condition file cross-check. PENDING.

## FINDINGS

### MarketDataSnapshot.java - 1388 lines, 23 methods, inventoried 2026-09-17 (worker first said 21, corrected to 23)

Flags raised by worker across Ranges A-D. Pending coordinator second receipt.

| # | Line(s) | Flag | Class |
|---|---------|------|-------|
| 1 | 437, 439 | duplicate root.set("setup_candidates", ...) | cosmetic |
| 2 | 371, 438 | duplicate root.set("liquidation_clusters", ...) | cosmetic |
| 3 | 1168, 1170 | duplicate root.set("setup_candidates", ...) in historical path | same as #1 |
| 4 | 283 | two statements on one line | style |
| 5 | 484, 550-553, 561 | buildVp: empty-bars default shape is "D" (484); comment at 550-552 states TWOPEAK is a rename; TWOPEAK emitted when secondPeakVol > 0.6*maxVol (553); "D" if left/right ratio 0.8-1.2 else "P" (561) | 1 (claim 1) |
| 6 | 165-166 | fetchSnapshot removes +3s/-3s bands that buildVwap never emits | dead code |
| 7 | 693 | RETRACTED by worker: Double.MIN_VALUE works for positive prices | withdrawn |
| 8 | 892 | computeSpeedPickingUp: divisor hardcoded 45, biases avg low near series start | minor bug |
| 9 | 814-819 | buildSessionTiming: US holidays hardcoded 2026 only | will break 2027 |
| 10 | 797-798 | buildSession: day_type="UNKNOWN" placeholder, not derived | dead field |
| 11 | 671-672 | buildCvd: cvd_recent slope uses +-0.001 absolute; main slope uses +-0.02 on percentage | formula mismatch |
| 12 | 1068 | fetchHistoricalSnapshot: cvd_trade_flow_aligned hardcoded false; live path computes it | I29 evidence |
| 13 | 1096, 1144 | historical path calls live-fetch helpers buildSpotPerpBasis, buildOiBreakdown | I29 class |
| 14 | 470, 473-474, 1191 | fetchMultiTimeframe(AsOf): IOException on one timeframe silently drops it (470); catch (Exception ignored) {} (473); pool.shutdownNow() (474); same at 1191-1196 | 1 |
| 15 | 842 | buildSessionTiming comment claims "L25 fix (2026-09-16)" but L25 is OPEN in master | tracker conflict |


### SetupCandidatesBuilder.java - 827 lines, 19 methods + 3 inner classes, inventoried 2026-09-17

| # | Line(s) | Flag | Tier |
|---|---------|------|------|
| 1 | 152 | Double.MIN_VALUE as unset target sentinel; RETRACTED same reason as MarketDataSnapshot | withdrawn |
| 2 | 170-173 | target == 0 used as unset, silently drops candidates | 1 |
| 3 | 187-194 | redundant double rrSanity filter | 1 |
| 4 | 216 | confidence thresholds as chained ternary, hard-coded | 1 |
| 5 | 242 | indentation anomaly, substate at col 0 | 1 |
| 6 | 262-266 | classifyState rewritten 2026-09-17, no longer reads daily_vp.shape | 1 (claim 1 evidence) |
| 7 | 266 | comment asserts Rule 32 test 3/3; receipts pending | 3 |
| 8 | 385 | addZoneIfPresent overload 2: isSwing param unused | 1 |
| 9 | 416-425 | getDistanceCap "vwap" branch unreachable (type rewritten to vwap_band) | 3 |
| 10 | 430 | determineSetupType "transition" branch dead (classifyState never returns it) | 3 |
| 11 | 447 | determineSetupType "sideways" branch dead | 3 |
| 12 | 480-491 | computeConfluence: Zone has no equals/hashCode, distinct() identity-based | 1 |
| 13 | 564, 569 | ProofResult.toJson: detected=false can emit actual_level/proximity_pct | 1 |
| 14 | 574, 578 | same pattern for volume spike | 1 |
| 15 | 541 | countSignals book imbalance threshold 0.4-0.6 mismatched with snapshot field bid_ask_ratio=2.5 (ratio around 1.0). Balanced book at 1.0 counted as extreme. Relevant to I30. | 1 |
| 16 | 757-772 | speedScore saturates: averageTrueRange returns 0 for start<1; ratio -> Infinity; speedScore capped at 10; speedPickingUp unconditionally true for 20-34 bar histories | 1 |
| 17 | 584 | "volatile" speed regime unreachable, speedScore capped at 10 | 1 |
| 18 | 652-660 | rejection wick tie-break: most recent bar of strongest tier wins (worker correction) | 1 |

### Claims status after SetupCandidatesBuilder.java

1. Internally consistent with paste. Range B lines 262-266 direct reading: classifyState no longer reads shape. buildVp comment at MarketDataSnapshot 550-552 corroborates. Coordinator verdict, not worker verdict.
2. NO EVIDENCE in either file.
3. ASSERTED in a code comment, not independently verified. Need the three snapshot IDs.
4. NO EVIDENCE yet.
5. NO EVIDENCE yet. SetupScreener.java not yet read.

### Coordinator calibration note (2026-09-17)

Worker self-corrected twice on method counts and tie-break semantics. Findings tagged:
- Tier 1 = direct reading of pasted text
- Tier 2 = arithmetic over Tier 1
- Tier 3 = inferential, scoped to "within pastes"
- Tier 4 = interpretive flags
- Tier 5 = cannot verify (paste fidelity)

Tracker wording for all "confirmed" claims is "internally consistent with paste."
### StateCodeEmitter.java - 479 lines, 23 method-like entities, inventoried 2026-09-17

Worker first pass + self-revalidation. Corrections folded in.

| # | Line(s) | Flag | Tier |
|---|---------|------|------|
| 1 | 73, 168-180, 337-353 | cvdSeries ring not cleared at UTC-day rollover. sessionCvd resets, ring keeps pre-reset values. computeCvdSlope returns false BEARISH up to 20 emit ticks after every 00:00 UTC. Material. | 1 |
| 2 | 51, 50 | CVD_MIN_SAMPLES=10, CVD_SAMPLES=40 per worker reading of constants at lines 50-51; ring math checks (10 min min, 40 min ring). I26 close supported by this file, not independently verified by coordinator. | 1 |
| 3 | 214 | nowT = lastTickMs if > 0. Stale when stream quiet. Window signals shortfall. | 1 |
| 4 | 235 | available >= MIN_SIGNALS gates whole hysteresis block. Below 3, no debounce update. | 1 |
| 5 | 249-250, 270-271 | transitionChain append + RING_SIZE trim duplicated verbatim | 1 |
| 6 | 276-278 | unconditional println every 60s | 1 |
| 7 | 315-323 | computeVolumeRatio buckets align to lastTickMs sub-minute offset, not :00 | 1 |
| 8 | 324 | idx bounds check dead (enclosing else-if guarantees range) | 1 |
| 9 | 337-353 | computeCvdSlope: relative change with absolute floor at 1.0; discontinuity at |older|=1.0; only fires for very-low-CVD | 1 |
| 10 | 306 | computeLast3Delta requires all 3 buckets; null after >=3min tick gap | 1 |
| 11 | 412-413, 470-473 | last_transition_utc derived from stateSinceMs; after restart reports last write time not state-entry time | 1 |
| 12 | 441-452 | I39 EVIDENCE: appendTransitionLog writes to session_end_logs.md. No lock. Platform newline. | 1 |
| 13 | 66-67 | BUFFER_LOCK static, ticks per-instance. Contention only, not a bug. | 4 |

### Claims status after StateCodeEmitter.java

1. Internally consistent with paste.
2. NO EVIDENCE.
3. ASSERTED in code comment, receipts pending.
4. NO EVIDENCE yet.
5. NO EVIDENCE yet.

### I39 second receipt landed

StateCodeEmitter.java line 442-452 confirms the writer. The file session_end_logs.md receives state-machine transition lines, not session end archives. Finding stands.

### Retraction log

- MarketDataSnapshot row 7 (Double.MIN_VALUE): withdrawn.
- MarketDataSnapshot method count: 21 -> 23.
- SetupCandidatesBuilder row 1 (Double.MIN_VALUE): withdrawn.
### ExtraSetupBuilder.java - 145 lines, 7 methods, inventoried 2026-09-17

Worker double-pass, both agree. Corrections folded in.

| # | Line(s) | Flag | Tier |
|---|---------|------|------|
| 1 | 141 | previousLow returns Double.MAX_VALUE on size<3. Early return bypasses ternary. Momentum-long stop becomes MAX_VALUE, gross_rr approx 0, candidate still emitted (no RR gate at 103-135). | 1 |
| 2 | 12 | NPE if current_price missing | 1 |
| 3 | 13-14 | ClassCastException if conditions/structure not ObjectNode | 1 |
| 4 | 14 | structure local declared, never referenced | 1 |
| 5 | 24 | proximity gate 0.0015 vs 0.001 used elsewhere | 1 |
| 6 | 27-29 vs 43-44 | stop/target recompute same expressions as fvgStop/fvgTarget | 1 |
| 7 | 62-64 vs 78-79 | same pattern for the second FVG branch | 1 |
| 8 | 32, 107 | rank = 10 + extra.size() after addObject() means first emitted rank is 11 | 1 |
| 9 | 53, 88 vs 127 | proof key is "speed" for FVG, "speed_picking_up" for momentum. Schema mismatch. | 1 |
| 10 | 103-135 | momentum branch has no RR sanity gate | 1 |
| 11 | 131-133 | hard-coded raw=70, confidence="B", proof_count=2 | 1 |
| 12 | 140 | previousHigh returns 0 on size<3, momentum-short stop becomes 0 | 1 |
| 13 | 142 | speedFromKlines returns trailing run, not max run | 4 |

### Claims status after ExtraSetupBuilder.java

1. Internally consistent with paste.
2. NO EVIDENCE.
3. ASSERTED, receipts pending.
4. NO EVIDENCE yet.
5. NO EVIDENCE yet.

### Retraction log - addendum

- ExtraSetupBuilder worker first pass: claimed momentum-stop division by zero -> Infinity. Worker corrected to: short -> stop=0 (finite), long -> stop=MAX_VALUE (gross_rr near 0, not Infinity).
### SetupScreener.java - 215 lines, 4 method-like entities + 1 inner class, inventoried 2026-09-17

| # | Line(s) | Flag | Tier |
|---|---------|------|------|
| 1 | 15, 19 | Only occurrences of SetupScreener in src/*.java are the class declaration and its ctor. Zero hits in .py/.ps1 under MyTradingSys/ and scripts/. | 1 (claim 5, scoped) |
| 2 | 46, 47, 52 | Unused params: sigma, vwapSlopePct, cvd | 1 |
| 3 | 68, 69 | distToVahPct, distToValPct computed and never used | 1 |
| 4 | 86 | "B".equals(vpShape) branch dead with current producers (buildVp emits TWOPEAK/D/P) | 1 |
| 5 | 91, 92 | needVis<60 and cap 95 only false/bind in rare POC approx VAH/VAL edge case | 1 |
| 6 | 66-69, 99 | divide by vwap unguarded: vwap==0 -> S02 gains +40 spuriously | 1 (conditional on caller) |
| 7 | 121, 122 | S02 requiresVisualValidation hardcoded true, confidence hardcoded MEDIUM | 1 |
| 8 | 133 | %d on top.priceLevel: throws if priceLevel is double. Cluster type not in scope. | 3 |
| 9 | 145, 146, 166, 167, 195, 196 | confidence values all MEDIUM/HIGH; LOW never emitted | 1 |
| 10 | 153-161 | S04 header says OI/L-S Flip, code has no flip detection; oiValue threshold 100000 marked arbitrary | 1 |
| 11 | 178-183 | S05 header says Order Book Thickening, code tests static ratio | 1 |
| 12 | 188-189 | S05 ratio thresholds 1.5/0.67, symmetric | 4 |
| 13 | 202-214 | toJsonArray NPE if alerts null | 1 |

### Claim 5 status after SetupScreener.java

SUPPORTED WITHIN SEARCHED SCOPE, not proven.

Grep scope: all .java under src/, all .py and .ps1 under MyTradingSys/ and scripts/.
Hits outside the class file: zero.
Gaps: .md, .json, .xml, .gradle, pom.xml, .properties, .yaml, .sh, .bat, directories outside those three roots. Dynamic class construction would evade grep. Class has no main, no static entry, so cannot self-invoke.

### Claims status after SetupScreener.java

1. Internally consistent with paste.
2. NO EVIDENCE.
3. ASSERTED, receipts pending.
4. NO EVIDENCE yet.
5. SUPPORTED WITHIN SEARCHED SCOPE.

### Corrections log - SetupScreener

- Worker first pass claimed S01 branches mutually exclusive. Worker corrected: only 78 vs 82 strictly exclusive; 74 vs 78/82 edge-case both-fire.
- Worker first pass claimed S01 needVis always true. Worker corrected: false only in that edge case.
### mts_math.py Range A (1-275) - 13 functions, inventoried 2026-09-17

| # | Line(s) | Flag | Tier |
|---|---------|------|------|
| 1 | 204 | STATE.classification mapped to conditions.vp_shape in field_map. Java classifyState returns balance/trend_unhealthy/trend_healthy. vp_shape carries TWOPEAK/D/P. Value spaces disjoint. Strong evidence against claim 4. | 1 |
| 2 | 25-40 vs Java 416-425 | get_distance_cap: Python exact-match dict lookup, Java startsWith prefix. Java swing names 1h_swing_high vs Python swing_high_1h. All Java swing types fall to default 0.003. | 1 |
| 3 | 25-40 | vwap_band_+1/-1/+2/-2 keys absent; Java emits those types. Same fall-through. Intended 0.002 never applies. | 1 |
| 4 | 78-104 vs Java 478-491 | detect_confluence denominator differs: Python uses cluster midpoint, Java uses first zone price. Same 0.3% threshold, different reference. | 1 |
| 5 | 250 | diff_state: unguarded float() on zone price. Only unguarded conversion in function. Raises ValueError on non-numeric state. | 1 |
| 6 | 255 | No zero guard on new_zone_price. buildVp emits 0.0 on empty bars. calculate_distance raises ValueError on zero. | 1 |
| 7 | 55 | check_trigger_validity has bare "scalp". Java emits scalp_short/scalp_long. Dead branch. | 1 |
| 8 | 264 | unchanged_count reset only on structural_change; substate_change and state_transition do not reset | 4 |
| 9 | 225 | if old_price_str: filters falsy 0 and empty string before float, not just None | 4 |

### Claim 4 status after mts_math.py Range A

EVIDENCE AGAINST, pending Range B. Line 204 shows the diff reads conditions.vp_shape, not a Java classifyState output. If update_state (Range B) writes classifyState output to STATE.classification, the diff will fire on every emit because the two sides carry different value spaces. Confirm in Range B.

### Claims status summary

1. Internally consistent with paste.
2. NO EVIDENCE.
3. ASSERTED, receipts pending.
4. EVIDENCE AGAINST, pending Range B confirmation.
5. SUPPORTED WITHIN SEARCHED SCOPE.

1. NOT REFUTED. Comment at 550-552 states TWOPEAK is a rename and classifyState no longer reads shape. Confirm at SetupCandidatesBuilder.
2. NO EVIDENCE in this file.
3. NO EVIDENCE in this file.
4. NO EVIDENCE in this file.
5. NO EVIDENCE in this file.

# END


### Claim 4 verdict - 2026-09-17

VERIFIED. Java SetupCandidatesBuilder.classifyState lines 267-278 and Python mts_math.update_state lines 336-346 have identical logic:
- same inputs: conditions.vwap_slope, conditions.cvd_slope, conditions.price_vs_va
- same branch order: balance gate -> divergent -> above_vah/below_val -> aligned -> default balance
- same return set: balance / trend_unhealthy / trend_healthy

### Diff / update_state disagreement - severity

state_transition has exactly one reader, update_market_state.py line 70, a print. No engine rule consumes it. Line 204 of mts_math.diff_state still maps STATE.classification to conditions.vp_shape. Value spaces disjoint. Records a change every cycle. Display noise today, material only if state_transition is ever wired into a rule.

### Double-diff observation

update_market_state.py calls diff_state at line 65, then update_state at line 79 which calls diff_state at line 387. Diff runs twice per cycle. Wasteful, not incorrect. Tier 4.

### Prior patch failure note

Two tracker patches were attempted with anchors from long wrapped lines. Both failed. File unchanged. This append is the fallback. Anchors must be short and unwrapped.

### update_market_state.py - 91 lines, 4 functions, inventoried 2026-09-17

| # | Line(s) | Flag | Tier |
|---|---------|------|------|
| 1 | 27 | glob BTCUSDT_*.json matches historical snapshots (MarketDataSnapshot.java 1222). Backfill can shadow live. | 1 |
| 2 | 27 | mtime sort vs embedded timestamp in filename. Copies/checkouts change mtime. | 1 |
| 3 | 27 | Hard-coded BTCUSDT, no symbol param | 1 |
| 4 | 40, 44 | No fsync before os.replace | 1 |
| 5 | 40, 42 | fd leak if os.fdopen raises | 1 |
| 6 | 40, 44 | mkstemp 0600 transferred to target. Silent narrowing from 0644. | 1 |
| 7 | 44 | Windows: os.replace fails if target open by another process. No retry. | 1 |
| 8 | 17 | ROOT = parents[3]. Layout-locked. | 1 |
| 9 | 19 vs Java 1220/1378 | Python derives SNAPSHOT_DIR from ROOT, Java uses CWD-relative. Agree only if CWD matches. | 1 |
| 10 | 51-87 | No try/except across any step. Any failure yields traceback. | 4 |
| 11 | 39 | mkdir no-op: parent is RUNTIME, already exists | 4 |
| 12 | 73 | display truncates to [:8], no ellipsis marker | 4 |

### Retraction - update_market_state worker first pass

Temp-file-collision concern withdrawn. Glob requires .json suffix. mkstemp temp uses .state_/.tmp. No collision possible.

### Claims status final after python runtime layer (in progress)

1. Internally consistent with paste.
2. NO EVIDENCE.
3. ASSERTED, receipts pending.
4. VERIFIED. Java 267-278 and Python 336-346 identical.
5. SUPPORTED WITHIN SEARCHED SCOPE.

### math_object_builder.py - 413 lines, 6 functions, inventoried 2026-09-17

Worker revalidation. Two prior observations reframed as matching documented intent, not defects: any_zone_rr_below_threshold identity check, and zero-drop truthy skips.

| # | Line(s) | Flag | Tier |
|---|---------|------|------|
| 1 | 357, 388 | setup_candidates and cvd.last_3_delta read from snapshot, not normalized. Old-schema wrappers lose them. | 1 |
| 2 | 393, 400 | isinstance(_book, (int, float)) admits booleans. False < 0.4 fires spurious "ask-heavy vs LONG" contradiction. | 1 |
| 3 | 383, 404 | proof_direction_status defaults to "aligned" when direction missing or unrecognized | 1 |
| 4 | 176, 322 | Naked POC name collision overwrites silently when two entries share a date | 1 |
| 5 | 303, 304 | trigger_valid_ct and trigger_valid_tc always equal | 1 |
| 6 | 354, 372 | Empty zone_math -> all() returns True -> chasing_price=True. No-data shown as chasing. | 1 |
| 7 | 197 | _swing_tf_for_zone returns "5m" for swing zones themselves. Docstring implies match-by-precision. | 4 |
| 8 | 318 | calculate_gross_rr called with entry=zone price, not current price | 1 |
| 9 | 407-411 | proof.speed override fires only for dict shape (SetupCandidatesBuilder). ExtraSetupBuilder writes bool. Silent skip. | 1 |
| 10 | 137 | Base VWAP typed vwap_band; shares cap 0.002 with bands | 4 |
| 11 | 141 | Band cleanup replace("?","") no-op against Java +1s/+2s/-1s/-2s keys | 4 |
| 12 | 342 | detect_confluence threshold=0.003 redundant with default | 4 |

### Correction - coordinator error in worker prompt

Coordinator told worker: "line 160 emits swing_high_1h which won't match mts_math keys." WRONG. mts_math.get_distance_cap has swing_high_1h keys. Python producer matches Python consumer. The mismatch is Java vs Python only, already logged in mts_math Range A row 2. Worker caught it.

### quad_classify.py - 117 lines, 5 functions, inventoried 2026-09-17

| # | Line(s) | Flag | Tier |
|---|---------|------|------|
| 1 | 21 | R hardcoded absolute Windows path C:\Users\E-ngineers\... | 1 |
| 2 | 55 | (p_cur - p_past)/p_past*100 outside try block. p_past==0 -> uncaught ZeroDivisionError. | 1 |
| 3 | 33-34 | load_all bare except Exception: pass silently skips unparseable files | 1 |
| 4 | 16, 18 | os import unused, timezone import unused | 1 |
| 5 | 3 vs 114 | docstring format (pipe-separated) does not match actual print (parenthesized) | 1 |
| 6 | 114 | %.0f on cvd_d1h drops sub-unit precision; +0 for |cvd|<0.5 | 1 |
| 7 | 56-58, 74 | "flat" has two origins (price flat, table flat) with same label, no differentiator | 4 |
| 8 | 107 | cur_ts unpacked but unused | 1 |
| 9 | 104 | len(snaps)<2 guard makes past is None check at 39 defensive | 4 |

### I23 evidence - partial

quad_classify.py produces 9 labels: new_longs, short_cover, distribution, weak_rally, new_shorts, long_liquidation, accumulation, weak_sell, flat. No code path reads setup_candidates or any setup direction. Comparison between quad direction and setup direction does NOT happen in this file. Where it might happen: alert card path (not yet read). I23 remains OPEN.

### Open question for later - delta_aligned bias sets

Worker answer grouped new_shorts/long_liquidation/distribution/weak_rally under nd15<0. Verify against lines 77-78 on next regime_classifier pass or via a targeted read if needed.

### regime_classifier.py - 102 lines, 5 functions, inventoried 2026-09-17

| # | Line(s) | Flag | Tier |
|---|---------|------|------|
| 1 | 20 | c = snap.get("conditions", {}) or {} assumes dict. Line 58 guards state dict but not snapshot. Non-dict JSON raises AttributeError. | 1 |
| 2 | 62 | consecutive_cycles persisted, never consumed by any branch | 1 |
| 3 | 23 | "B" fallback for vp_shape matches neither P nor D, contributes no vote. Silent vote loss. | 1 |
| 4 | 32 | vp_shape "D" mapped to down vote; Java line 561 defines D as balanced (0.8<ratio<1.2). Directional mapping anomalous. | 1 |
| 5 | 61-62 | unguarded int(prev.get(...)) raises ValueError on non-numeric | 1 |
| 6 | 91-95 | no fsync before os.replace, no try/except | 1 |
| 7 | 7 | ROOT hardcoded absolute Windows path | 1 |
| 8 | 15 | glob BTCUSDT_*.json matches historical snapshots, mtime sort | 1 |
| 9 | 49 vs 55 | snapshot read utf-8, state read utf-8-sig. Asymmetric. | 4 |
| 10 | 97-98 | print omits consecutive_cycles and entered_at_utc | 4 |

### Debounce confirmed - regime_classifier vs verdict layer

regime_classifier has genuine 3-cycle streak debounce (line 71). Promotes only when cand != published AND streak>=3. Rapid flips never promote. confidence_of returns LOW whenever cand != published because main line 78 zeroes streak.

This is the debounce pattern I31 says the verdict layer lacks. regime_classifier has it. Verdict layer does not. Same class of problem, opposite states.

### L31 status

Confirmed. state_code_regime.json is written by regime_classifier.py only. StateCodeEmitter.java writes state_code.json (different filename) at line 430. Java does not read state_code_regime.json. L31 remains OPEN, its premise verified.

### Quad bias sets closed - 2026-09-17

Confirmed from quad_classify.py lines 74-88:
- long_bias (nd15>0): new_longs, short_cover, accumulation, weak_sell
- short_bias (nd15<0): new_shorts, long_liquidation, distribution, weak_rally
- flat: neither set, delta_aligned=True

### Python layer audit COMPLETE

mts_math.py, update_market_state.py, math_object_builder.py, quad_classify.py, regime_classifier.py - all inventoried. Moving to test coverage sweep.

### Test coverage sweep - 2026-09-17

Coverage analysis from test-name lists only. Test bodies not read. Name-level judgement, not verified assertions.

| source file | test coverage |
|-------------|---------------|
| MarketDataSnapshot.java | NONE |
| SetupCandidatesBuilder.java | NONE |
| StateCodeEmitter.java | NONE |
| ExtraSetupBuilder.java | NONE |
| SetupScreener.java | NONE |
| mts_math.py | covered by test_mts_math.py (81 defs) |
| math_object_builder.py | covered by test_math_object_builder.py (39 defs) |
| update_market_state.py | NONE |
| quad_classify.py | NONE |
| regime_classifier.py | NONE |

### Notes

- state_signal_prototype.py is a source file, not a test file. Mirrors StateCodeEmitter method names (s_net_delta, s_last3, s_vol_ratio, s_cvd_slope, s_price_vs_vwap, next_target). Whether it exercises the Java logic is undecidable from name list.
- test_session_state.py tests a session_state module, NOT update_market_state.py. Different files.
- Most material audit findings have NO TEST or AMBIGUOUS coverage. Few would be caught by any existing test.

### Material findings with NO TEST

- CVD ring not reset at UTC rollover (StateCodeEmitter.java)
- Book-imbalance threshold 0.4-0.6 in countSignals (SetupCandidatesBuilder.java)
- setup_candidates / cvd.last_3_delta read from snapshot not normalized (math_object_builder.py)
- isinstance(_book, (int,float)) accepts booleans (math_object_builder.py)
- proof_direction_status defaults to aligned (math_object_builder.py)
- get_distance_cap Java vs Python key mismatch (mts_math.py vs Java)
- diff_state unguarded float (mts_math.py)
- check_trigger_validity "scalp" vs Java scalp_short/long

### Worker context note

Worker stated it had not seen mts_math.py lines 276-528. Those were pasted earlier in the chat. Context appears to have dropped in a long worker session. For any further mts_math.py analysis, re-paste Range B (276-528).

## AUDIT SUMMARY - 2026-09-17

### What the audit covered

11 files: 5 Java (MarketDataSnapshot, SetupCandidatesBuilder, StateCodeEmitter, ExtraSetupBuilder, SetupScreener), 5 Python (mts_math, update_market_state, math_object_builder, quad_classify, regime_classifier), plus 6 condition files via targeted grep and the corpus via targeted grep.

### Findings logged

Over 100 findings across the tracker. Tiered: Tier 1 direct reading, Tier 2 arithmetic, Tier 3 inferential scoped, Tier 4 interpretive.

### Material defects (worth acting on)

1. CVD ring not cleared at UTC rollover. StateCodeEmitter.java. computeCvdSlope returns false BEARISH for up to 20 minutes after every 00:00 UTC. Counts toward bearish tally. No test.
2. Book imbalance threshold 0.4-0.6 in countSignals (SetupCandidatesBuilder.java L541) treats a balanced ratio of 1.0 as extreme. Directly relevant to I30.
3. math_object_builder.py reads setup_candidates and cvd.last_3_delta from snapshot, not normalized. Old-schema wrappers lose them silently.
4. isinstance(_book, (int,float)) accepts booleans in math_object_builder.py. False < 0.4 fires a spurious "ask-heavy vs LONG" contradiction.
5. diff_state L204 compares STATE.classification to conditions.vp_shape. update_state L346 writes a state label. Value spaces disjoint. Only current consumer is a print. Cosmetic today.
6. Momentum branch in ExtraSetupBuilder has no RR gate. previousLow returns Double.MAX_VALUE on short history, drives gross_rr to near-zero, candidate still emitted.

### Claims final verdict

1. buildVp emits TWOPEAK; classifyState no longer reads shape: INTERNALLY CONSISTENT WITH PASTE.
2. B profile = weakness at the extreme (Tom): SUPPORTED. Corpus grep, direct quotes TOM-001 to TOM-005. Exact phrase "weakness at the extreme" is screener paraphrase, not Tom. Cosmetics issue.
3. Rule 32 test passed 3/3: ASSERTED, receipts pending. Snapshot IDs not located.
4. STATE.classification in mts_math matches Java classifyState: VERIFIED. Java L267-278 and Python L336-346 identical logic.
5. SetupScreener is dead code: SUPPORTED WITHIN SEARCHED SCOPE.

### Citation infrastructure built

- TOM_VERBATIM_INDEX.md: 10 verbatim quotes, 4 screener-proxy entries.
- verify_rule_citations.ps1: checks rule tags resolve to index.
- Corpus negative results: "weakness at the extreme" zero hits, "TWOPEAK" zero hits.
- Condition-file negative results: distance caps, book-imbalance 0.4/0.6, scalp_short/long split appear in no condition file. Screener inventions.

### Test coverage

5 Java files + 3 Python files have ZERO test coverage. Only mts_math and math_object_builder are tested. Most material findings have NO TEST or AMBIGUOUS coverage.

### Open loops touched

I23 partial (quad vs setup comparison not in quad_classify.py; may be in alert card path).
I26 supported by StateCodeEmitter code.
I29 evidence (historical path sets cvd_trade_flow_aligned false, calls live fetchers).
I30 explanatory (book-imbalance 0.4-0.6 threshold).
I31 pattern contrast (regime_classifier has debounce, verdict layer does not).
I39 second receipt landed.
L25 conflict flagged (comment claims fix but master says OPEN).
L31 premise verified.

### Open loops untouched

I21, I22, I24, I25, I27, I28, I32, I33, I34, I35-I38, I40. Plus L28, L30.

### Post-audit work

1. Fix material defects 1-6 above. Each needs its own test.
2. Populate condition-file rule tags. Mechanical pass, one file per session.
3. I40 decision (rename to Tom's terms or accept screener letters).
4. Claim 3 receipts (locate Rule 32 snapshot IDs).
5. Resume secondary queue: I30, I31, I33, I29, I34 evidence.

### Session artifacts

- USER.md: no-cannot-reply rule added.
- start-session.ps1: audit tracker inlined when present.
- AUDIT_2026-09-17_TRACKER.md: this file.
- TOM_VERBATIM_INDEX.md: new.
- verify_rule_citations.ps1: new.
- 03_FILE_INDEX.md: 2 rows added.

## SESSION MTS-2026-09-17-1142Z APPEND - 2026-09-17 12:30 UTC

Two workers dispatched. Replies saved under Dumps/workers/.

### W1_verify_context
Verified the 2026-09-16 context note. 5 of 7 findings accepted.
- Rejected: Assumption 1 (13:30 UTC is correct today; condition file shows 14:30 because it documents EST year-round; BUGS.md B020).
- Rejected: Defect 2 (vp_shape). Live snapshot emits TWOPEAK. L29 closed 2026-09-17.
- Accepted: Defect 1 (day_type UNKNOWN, still open). Defect 3 (opening range not wired, still open). Assumption 2 (unvalidated). Assumption 3 (refuted, no consumer). Assumption 4 (unvalidated).
Files: Dumps/workers/W1_verify_context/WORKER_READY_1.md, WORKER_READY_2.md, worker_reply.md.

### W2_live_tracking
Live engine + multi-week context brief. Accepted.
- POC migration three weeks: 79892.45 -> 77155.43 -> 75719.66. Down drift.
- Price at 76920.7, inside intraday_4h VA near VAH.
- Digest 48 snapshots: 32 trigger_ready, 16 conditional, 0 below, 0 none.
- Alerts #401 12:14:20Z, #402 12:21:21Z.
- Anchor 2026-09-17T13:30:00Z, session block zeros pre-anchor, expected to populate after.
- Book imbalance live 2.58, digest min 0.48. B035 evidence.
Files: Dumps/workers/W2_live_tracking/WORKER_READY_1.md, WORKER_READY_2.md, WORKER_READY_3.md, worker_reply.md.

### Apparatus change this session
Build-Check.ps1 extended to scan MyTradingSys/conditions/*.md.
apparatus_fixes.md PERMANENT SAFEGUARDS updated with permitted non-ASCII note.
Build-Check verified PASS at 17:29:49 UTC.

### Pending
- Verify session block populated after 13:30 UTC anchor.
- B035 (book imbalance threshold 0.4-0.6 inverted) still open.
- B020 (session_timing_rules.md EST year-round) still open.
- Defects 1 and 3 still open.

# END SESSION APPEND
