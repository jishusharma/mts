# COMPILED-OUTPUT AUDIT
# Date: 2026-09-15
# Role: WORKER (read-only). Coordinator commits.
# Intent (R51a): ranked list of must-be-compiled vs currently ad-hoc values.
# Challenge (R51b): inventory, not schema proposal.
# Revision: 2 (post-reverification). See REVERIFICATION LOG at end.

## SUMMARY

counts: COMPILED_TODAY 3 / DERIVED_TODAY 0 / ABSENT 12 / CONTRARY 4 (total 19)

Anchor failure driving this audit: AI quoted a "session low" ~50 pts off. A
structural swing_low existed (snapshot structure.5m.swing_low = 76151.3), but
no field named session_low existed anywhere in the read set. A reader grabbed
the nearest structural level and labeled it a session low. session_low is
ABSENT -- not computed in any script, not persisted, not referenced by any
Java, Python, or JSON file in the tree.

Second-order observation from reverification: FOUR distinct session anchors
exist across the read set (2026-09-12T19:03:33Z, 2026-09-13T00:00:00Z,
2026-09-14T00:00:00Z, 2026-09-15T00:00:00Z). The word "session" means at
least four different things depending on the file. Any compiled session_*
field must declare its anchor or it will compound the existing ambiguity.

---

## TABLE A - values by classification

| value_name | classification | where_computed_today | where_should_live | priority | one-line rationale |
|---|---|---|---|---|---|
| prior_day_close | COMPILED_TODAY | snapshot prior_day.close; current_market_state.md PRIOR_DAY.close | (already persisted) | L | Present and stable; no action beyond dictionary row. |
| prior_day_high | COMPILED_TODAY | snapshot prior_day.high; current_market_state.md PRIOR_DAY.high | (already persisted) | L | Present and stable. |
| prior_day_low | COMPILED_TODAY | snapshot prior_day.low; current_market_state.md PRIOR_DAY.low | (already persisted) | L | Present and stable. |
| session_high | ABSENT | Not computed anywhere. Grep of 16 candidate strings across snapshots, runtime, Java, Python, and full MyTradingSys tree returns zero hits. | New snapshot block `session` (MarketDataSnapshot.java near line 1292 write); mirror in current_market_state.md new `## SESSION` section (mts_math.py header block near lines 395-399) | H | Same failure family as session_low. Must be declared before any range_position_pct exists. |
| session_low | ABSENT | Not computed anywhere. Same grep evidence. | Same as session_high | H | Root cause of R51 failure. No script, no field. AI improvised from chart. |
| session_open_price | ABSENT | Not computed anywhere. Same grep evidence. | Same as session_high | H | Anchor for gap, range_position, session_VWAP context. |
| range_position_pct | ABSENT | Not computed anywhere. Same grep evidence. | Computed from session_high/low at snapshot build time | H | Needs session_high/low first; prevents ad-hoc "where in range" reads. |
| gap_from_prior_close | ABSENT | Not computed anywhere. Same grep evidence. | Same as session_high | M | Session-open context; currently no field. |
| gap_direction | ABSENT | Not computed anywhere. Same grep evidence. | Same as session_high | M | Pairs with gap_from_prior_close. |
| initial_balance_high | ABSENT | Not computed anywhere. Same grep evidence. PROJECT_VISION.md lists "initial balance" as planned (INTEGRATIONS TRACKED: Session-aware frame). | New `session` block, computed from first N minutes after session_start_utc | M | Named in vision; not built. |
| initial_balance_low | ABSENT | Not computed anywhere. Same grep evidence. Same vision note. | Same as initial_balance_high | M | Named in vision; not built. |
| initial_balance_window_minutes | ABSENT | Not computed anywhere. Same grep evidence. | Persisted as a config constant, echoed in snapshot metadata | M | Window length currently undefined (PROJECT_VISION OPEN QUESTIONS). |
| day_type | CONTRARY | `conditions.vp_shape = "B"` is a VP shape letter, not Tom's trend/balance day_type taxonomy. Literal string `day_type` appears nowhere in the tree. | New `session.day_type` field, distinct from vp_shape | L | A field exists but measures a different construct. Do not overload. |
| day_type_confidence | ABSENT | Not computed anywhere. Same grep evidence. | New `session` block | L | Depends on day_type existing first. |
| session_vwap_anchor_utc | CONTRARY | `cvd.session_start_utc` anchors CVD only (00:00 UTC today). VWAP anchor is implied by dictionary wording, not emitted. Four distinct session_start_utc values exist across the tree. | New `session.vwap_anchor_utc`; keep existing cvd.session_start_utc as is | H | Four-anchor ambiguity is a live bug class (dictionary CROSS-CATEGORY WARNINGS). |
| open_location | CONTRARY | `conditions.price_vs_va` = above_vah/in_va/below_val exists, but measures CURRENT price vs CURRENT VA. Session-open location is a different construct. Literal string `open_location` appears nowhere. | New `session.open_location` computed at session_start_utc | L | Partial substitute exists; may suffice if re-scoped, but semantics differ. |
| session_bias | CONTRARY | `session_state.thesis.direction / .confidence / .text` exists (AI-authored, updated 2026-09-14T09:28:31Z). No committed_at_utc. Literal string `session_bias` appears nowhere in the tree. | session_state.json schema v5.0.0 -> v5.1.0: add `session_bias.committed_at_utc`; also emit compiled `session.bias` to snapshot | M | Thesis text drifts stale (says "~77600" while apparatus_log shows 76214-77168 this session). A committed_at_utc would expose staleness. |
| sweep_flag | ABSENT | Not computed anywhere. Same grep evidence. | New `session.sweep_flag`, computed vs prior_day.high/low since session_start_utc | L | New construct; no current computation site. |
| liquidity_sweep_direction | ABSENT | Not computed anywhere. Same grep evidence. | Same as sweep_flag | L | Pairs with sweep_flag. |

---

## TABLE B - dictionary rows to add (MTS_DICTIONARY.md)

| field | proposed authority file | proposed section |
|---|---|---|
| session_open_price | data_schema_v1.2.0.md | new section "DATA BLOCK - session" |
| session_high | data_schema_v1.2.0.md | new section "DATA BLOCK - session" |
| session_low | data_schema_v1.2.0.md | new section "DATA BLOCK - session" |
| session_vwap_anchor_utc | data_schema_v1.2.0.md | new section "DATA BLOCK - session"; cross-ref existing section "CVD anchor vs CoinGlass" |
| initial_balance_high | data_schema_v1.2.0.md | new section "DATA BLOCK - session" |
| initial_balance_low | data_schema_v1.2.0.md | new section "DATA BLOCK - session" |
| initial_balance_window_minutes | data_schema_v1.2.0.md | new section "DATA BLOCK - session" |
| gap_from_prior_close | data_schema_v1.2.0.md | new section "DATA BLOCK - session" |
| gap_direction | data_schema_v1.2.0.md | new section "DATA BLOCK - session" |
| open_location | data_schema_v1.2.0.md | new section "DATA BLOCK - session" |
| day_type | data_schema_v1.2.0.md | new section "DATA BLOCK - session" |
| day_type_confidence | data_schema_v1.2.0.md | new section "DATA BLOCK - session" |
| session_bias | session_state.json v5.0.0 -> v5.1.0 (schema migration doc) | new section "session_bias" |
| sweep_flag | data_schema_v1.2.0.md | new section "DATA BLOCK - session" |
| liquidity_sweep_direction | data_schema_v1.2.0.md | new section "DATA BLOCK - session" |
| range_position_pct | data_schema_v1.2.0.md | new section "DATA BLOCK - session" |
| structure.swing_low (dict row absent) | data_schema_v1.2.0.md | existing section "DATA BLOCK - structure"; add dict row |
| structure.swing_high (dict row absent) | data_schema_v1.2.0.md | existing section "DATA BLOCK - structure"; add dict row |
| Net Delta (CoinGlass) | heatmap_field_map.md | section 2b already documents; add dict row pointing to it |
| compiled_engine.md (file itself) | mts/runtime/compiled_engine.md | add pointer row (not currently in dictionary) |
| heatmap_field_map.md (file itself) | mts/research/_archive/loose_2026-10/heatmap_field_map.md | add pointer row |

Note: current_market_state.md is a write-target of mts_math.py, not a schema
authority. The dictionary row should point at data_schema_v1.2.0.md, not the
runtime file.

Note: compiled_engine.md is at MyTradingSys/runtime/ (NOT research/ as one
might assume from its role). Verified path.

---

## TABLE C - snapshot schema gaps

Newest snapshot inspected: BTCUSDT_2026-09-15_1789494737368.json
(timestamp_utc 2026-09-15T17:52:16.271796900Z).

| block | declared_fields | emitted_fields | missing_in_newest | action |
|---|---|---|---|---|
| top-level metadata | timestamp_utc, asset, data_source, screener_version, generation_ms, alignment_pass | timestamp_utc, asset, current_price, alignment_pass | data_source, screener_version, generation_ms | Confirm intentional omission; add if reconciliation across DSA versions is needed. |
| METADATA (disclaimer block) | disclaimer, vp_confidence, vp_source, cvd_confidence, cvd_source, vwap_confidence, vwap_source | (none) | all | Emitted per-block (each block carries .confidence); source strings absent. Decide whether per-block is sufficient. |
| order_book_depth | bid_depth_1pct, ask_depth_1pct, bid_ask_ratio, confidence, source | bid_ask_ratio, confidence | bid_depth_1pct, ask_depth_1pct, source | Schema declares raw depth. Engine consumes only bid_ask_ratio (schema's own engine note). Either demote raws to optional or restore. |
| open_interest | value, confidence, source | direction, change_1h_pct, confidence | value, source | Schema declares `value`; emitter replaced it with direction/change. Reconcile schema. |
| funding | current_rate, extreme, confidence, source | current_rate, extreme, confidence | source | Minor. |
| long_short_ratio | ratio, confidence, source | (block absent) | all | Replaced by oi_breakdown (retail/whale). Update schema to deprecate the old block. |
| oi_breakdown | (not declared in v1.2.0) | retail, whale, confidence, note | n/a | Add to schema (currently undeclared emitter field). |
| naked_pocs / visited_pocs | declared | (block absent) | all | NakedPocTracker.java:68 writes a separate file; snapshot does not carry. Align schema and emitter. |
| setup_alerts | declared | (block absent) | all | Superseded by setup_candidates (v1.3.0 section). Update schema to deprecate. |
| cvd | value, slope, divergence, last_3_delta, confidence, source | value, slope, last_3_delta, cvd_recent, confidence, scope, session_start_utc | divergence, source | CLOSED 2026-10-04 (B063): deprecated in schema. |
| trade_flow | net_delta (singular), last_3_delta | net_delta_1m, net_delta_5m, net_delta_15m, net_delta_1h, confidence | n/a | Deprecated 2026-09-11 in schema body; header table still lists old names. Update header. |
| liquidation | status, clusters | liquidation_clusters (nearest_above, nearest_below, warning) | n/a | Deprecated 2026-09-12; emits 0.0. heatmap_field_map.md confirms treat as not-live. Remove from schema or mark deprecated in header. |
| conditions | price_vs_poc, fvg_unfilled_count, funding_reset_window, speed_picking_up | price_vs_poc, price_vs_va, vp_shape, vwap_slope, cvd_slope, cvd_trade_flow_aligned, fvg_unfilled_count, fvg_nearest_unfilled, book_imbalance, funding_extreme, oi_trend, speed_picking_up, volume_spike_at_level, rejection_wick_at_zone | n/a | funding_reset_window moved to session_timing. Schema header table outdated. |
| session_timing | (not declared in v1.2.0) | current_session, funding_reset_window, us_equity_open_window, us_equity_open_in_minutes | n/a | Add to schema. |
| spot_perp_basis | (not declared in v1.2.0) | spot_price, mark_price, basis_pct, direction, confidence | n/a | Add to schema (covered by dictionary pointer, not by schema doc). |
| session (new) | (does not exist) | (does not exist) | session_open_price, session_high, session_low, session_vwap_anchor_utc, range_position_pct, gap_from_prior_close, gap_direction, open_location, day_type, day_type_confidence, sweep_flag, liquidity_sweep_direction, initial_balance_high, initial_balance_low, initial_balance_window_minutes | Entire session block is a schema gap. Coordinator action. |

---

## TABLE D - evidence from today's session

| # | failure / anomaly | specific evidence in read set | field that prevents it |
|---|---|---|---|
| 1 | AI quoted a session low ~50 pts off from a chart image. | R51 brief states this. Snapshot structure.5m.swing_low = 76151.3 (BTCUSDT_2026-09-15_1789494737368.json). Apparatus log tail 200 (cycles 410-448, 17:13-17:52Z) shows a within-window low of 76214.80 (cycle 412, 17:16:18Z) and a within-window high of 77168.50 (cycle 432, 17:36:18Z). These values are not labeled session_low / session_high anywhere; they are per-cycle prints, not session extents. | session_low and session_high (compiled). Full-session extents require a session anchor and a running accumulator. |
| 2 | Thesis text is stale. | session_state.json thesis.text says "Price ~77600 never printed 76300", updated_utc 2026-09-14T09:28:31Z. Apparatus log tail from 17:13 to 17:52 shows prices between 76214.80 and 77168.50. The thesis was 32h stale. | session_bias.committed_at_utc (CONTRARY today: no timestamp on thesis). |
| 3 | pd_flag near 50/50 churn. | D6_summary.md: pd_flag contradiction 31 / aligned 29 over 60 cycles. Cause per dictionary: aggTrade vs kline CVD divergence. | session_vwap_anchor_utc + session_open_price to give an independent session-anchored reference. |
| 4 | 4h VAL drift described ad-hoc. | D6_summary.md: "4h_value rising (76277.66 at 17:10 vs 76373.38 at 16:11) while price pinned ~76200, so net_rr improving as zone lifts toward price." This is a range-position observation done in prose. | range_position_pct (requires session_high/low). |
| 5 | daily_vp.vah churns across minutes. | Corrected sequence from snapshots: 76966.74 (17:48Z) -> 76971.75 (17:49Z) -> 76976.76 (17:52Z). A reader has no session-anchored VA to hold onto. | session_high/session_low and a compiled session-level VA snapshot at session_start_utc (latter out of scope; noted). |
| 6 | Four distinct "session" anchors in the tree. | Reverification block 6 enumerated: 2026-09-12T19:03:33.452123Z (session_state, this run); 2026-09-13T00:00:00Z; 2026-09-14T00:00:00Z; 2026-09-15T00:00:00Z (snapshots across days). Any field named "session_*" must declare which anchor it uses. | session_vwap_anchor_utc (CONTRARY today: cvd.session_start_utc exists for CVD only). |
| 7 | Session-aware frame not built. | PROJECT_VISION.md INTEGRATIONS TRACKED row: "Session-aware frame | new (this project) | design | session bias, day type, initial balance". All three named reads are ABSENT. | session_bias, day_type, initial_balance_high/low. |
| 8 | Engine vs runtime contradiction on swing TF matching. | compiled_engine.md CHANGELOG v4.2.0-p2 STRIP SESSION lists F4 "SWING TF MATCHING (Weekly->1h, 4H->15m, VWAP->5m)" as DELETED. math_object_builder.py lines 188-197 still implement match_swing_tf with the same mapping. Out of scope for this audit (rule vs field). Flagged. | Not a field gap. Note for coordinator: rules-vs-runtime drift. |

---

## REVERIFICATION LOG

This revision corrects revision 1. Each change is itemized.

| # | Rev 1 claim | Reverification command | Result | Corrected to |
|---|---|---|---|---|
| 1 | session_high and session_low are DERIVED_TODAY from apparatus_log tail. | Exhaustive grep of 16 candidate strings across snapshots, runtime .json/.md, Java, Python, and full MyTradingSys tree. | Zero hits. No script computes them. Eyeballing a log is not per-cycle computation. | ABSENT. |
| 2 | 3 COMPILED_TODAY / 2 DERIVED_TODAY / 10 ABSENT / 4 CONTRARY. | Recomputed after #1. | Corrected counts. | 3 COMPILED_TODAY / 0 DERIVED_TODAY / 12 ABSENT / 4 CONTRARY. |
| 3 | session_state.json schema "v6" proposed for session_bias. | `ConvertFrom-Json .version` and grep of `session_state.py VERSION =`. | Both report 5.0.0. "v6" was invented. | v5.0.0 -> v5.1.0. |
| 4 | Two session anchors (session_state 2026-09-12, cvd 2026-09-15). | Distinct-value enumeration of `"session_start_utc"` across runtime .json and snapshots. | Four anchors: 09-12T19:03:33Z, 09-13T00:00:00Z, 09-14T00:00:00Z, 09-15T00:00:00Z. | Four anchors. Upgraded session_vwap_anchor_utc priority from M to H. |
| 5 | "compiled_engine.md Section 2.4" cited as location of "Swing TF Matching" (lifted second-hand from schema note in E). | Direct read of compiled_engine.md. | Section 2.4 is titled "MULTI-TF ZONE EVALUATION RULE [SYSTEM]". Swing TF matching lives in math_object_builder.py lines 188-197, and the engine changelog F4 marks that concept DELETED. | Corrected. Second-hand citation removed. Engine vs runtime contradiction flagged in Table D row 8. |
| 6 | heatmap_field_map.md cited via F, never read. | Direct read of heatmap_field_map.md. | Exists at MyTradingSys/research/_archive/loose_2026-10/heatmap_field_map.md. Confirms liquidation_clusters deprecation, confirms CVD/VolumeDelta/NetDelta distinctions, confirms no DSA field for CoinGlass Net Delta. | Now cited directly. Added Net Delta row to Table B. |
| 7 | daily_vp.vah sequence "76971.75 -> 76966.74 -> 76976.76 (17:48, 17:49, 17:52Z)". | Re-read three snapshots. | Actual sequence: 76966.74 (17:48Z) -> 76971.75 (17:49Z) -> 76976.76 (17:52Z). Set of values correct; ordering typed wrong. | Table D row 5 corrected. |
| 8 | session_high = 77168.50, session_low = 76214.80 presented as session extents. | Attempted full-log scan; regex failed because log line format is `YYYY-MM-DD HH:MM:SS | ISO_TS | price | ...` (three pipe fields, ISO timestamp is field 2, not field 1). | Values are within-window (cycles 410-448, 17:13-17:52Z), not session extents. Session anchor 2026-09-12T19:03:33Z spans ~70 hours, not read. Table D row 1 corrected. |
| 9 | current_market_state.md might have a `## SESSION` section. | `Select-String '^## '` on current_market_state.md. | 13 sections: META, WEEKLY, DAILY, POST_FUNDING, INTRADAY_4H, PRIOR_DAY, SWING, STATE, VWAP, CVD, TRADE_FLOW, FUNDING, SPOT_PERP. No SESSION. | Confirms ABSENT for all session fields in runtime state. |
| 10 | Grep of candidate strings not performed in rev 1. | Full grep run (block 4a-4e). | Zero hits for all 16 candidates across all five scopes. | Confirms every ABSENT and CONTRARY classification. |

Net effect on classifications: 2 changes (session_high, session_low: DERIVED_TODAY -> ABSENT). Counts adjusted. No classifications reversed.

---

## HANDOFF (5 lines)

1. Counts corrected to 3 COMPILED_TODAY / 0 DERIVED_TODAY / 12 ABSENT / 4 CONTRARY. Rev 1 had session_high and session_low misclassified as DERIVED; they are ABSENT (no script computes them; grep confirms zero tree-wide hits).
2. Highest-priority gap: session_low and session_high, both ABSENT. Direct cause of the R51 quote error. No computation site exists today.
3. Second-priority: session_open_price and range_position_pct, both ABSENT, both blocked on session_high/low. session_vwap_anchor_utc upgraded to H because four distinct anchors exist in the tree.
4. Entire session block is undeclared in data_schema_v1.2.0.md and unkeyed in MTS_DICTIONARY.md. Coordinator's schema task must create the block and add 16 dictionary rows plus two pointer rows for compiled_engine.md and heatmap_field_map.md.
5. Out of scope for this audit: compute-site target is MarketDataSnapshot.java near line 1292 (snapshot write) and mts_math.py near lines 395-399 (current_market_state.md header write). Also flagged: compiled_engine.md marks "SWING TF MATCHING" as DELETED (F4) while math_object_builder.py still implements it (lines 188-197). Rule vs runtime drift, not a field gap.