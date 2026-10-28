# VVP-002 — EXTENDED VISUAL VALIDATION PROTOCOL
# Extends: VVP-001 v1.1.0 (2026-09-01)
# Date: 2026-09-13
# Rule: Extend, do not replace. VVP-001 sections remain authoritative.
# Every step below references VVP-001 section OR a JSON field path from data_schema_v1.2.0.

## A. VVP-001 REFERENCE (NOT COPIED)

VVP-002 builds on VVP-001 without redefining any VVP-001 rule. Authoritative sections:

| VVP-001 Section | Title | Consumed by VVP-002 |
|-----------------|-------|---------------------|
| 2.1-2.6 | Screenshot Capture Rules | B.2, C.1, F.1 |
| 3.1 | O/H/L/C Format | B.4, C.3 |
| 3.2 | Timeframe Annotation | B.4, D, F |
| 3.3 | Cross-Timeframe Values | E.4 |
| 3.4 | DSA vs Visual Priority Hierarchy | B.6, C.6, D, G |
| 3.5 | Flag, Do Not Override Silently | E.2, G |
| 4 Tier 1 | VP (Fixed Range), VWAP, CVD, Net Delta | D |
| 4 Tier 2 | Open Interest (Candles) | D |
| 4 Tier 3 | Liquidations (DORMANT) | B |
| 4 Tier 4 | RSI/BB/CVD-candles removed | B.1 |
| 5 | Recommended Layout | B.2, D |
| 6.1-6.4 | Proof Detection | C.4-C.5 |
| 7 | Validation Checklist | F |

Any VVP-002 step that conflicts with VVP-001 is invalid. VVP-001 wins.

## B. HEATMAP PROTOCOL

Status: EXTENDS VVP-001 4 Tier 3 (Liquidations). VVP-001 4 marks Liquidations Tier 3 / DORMANT because DSA emits liquidation_clusters.nearest_above.price = 0.0, liquidation_clusters.nearest_below.price = 0.0, liquidation_clusters.warning = false unconditionally (see 02a_CURRENT_STATUS: "D2 CLOSED 2026-09-12 — engine confirmed zero liquidation reads. Schema marks liquidation.* DEPRECATED"). Heatmap is therefore CONTEXT ONLY per VVP-001 3.4.

B.1 Capture rules
- Step 1: Same as VVP-001 2.1 (cursor at right edge).
- Step 2: Same as VVP-001 2.2 (timeframe visible).
- Step 3: Heatmap panel must show its own timeframe label. Record it (VVP-001 3.2).
- Step 4: Heatmap must NOT replace any VVP-001 4 Tier 1 indicator. If heatmap displaces VP/VWAP/CVD/Net Delta, the screenshot fails VVP-001 7. RSI/BB/CVD-candles remain disallowed (VVP-001 4 Tier 4).

B.2 What to read (three observations only)
- Cluster price: nearest visible cluster above and below current_price.
- Density: qualitative (thick / medium / thin) — no numeric threshold at this stage. DSA does not emit density; this is a visual read only.
- Thin zones: zones of low/missing heatmap color.

B.3 Cross-check fields (schema v1.2.0 — exact paths)
- open_interest.direction — does OI direction match heatmap cluster formation on the same timeframe? (Rising OI + cluster = positioning build. Falling OI + cluster = unwind.)
- open_interest.change_1h_pct — magnitude check.
- spot_perp_basis.basis_pct and spot_perp_basis.direction — premium/discount context.
- funding.current_rate, funding.extreme — crowded-side check.
- liquidation_clusters.* — MUST be checked and MUST be reported as NOT LIVE (all three fields emit 0.0/false as of 2026-09-12). If any of these fields is non-zero, FLAG (unexpected — do not act on it, report to user).

B.4 Reading discipline
- Apply VVP-001 3.1 (O/H/L/C) only to indicator legends, not to heatmap colors.
- Apply VVP-001 3.2: every heatmap value reported MUST carry its timeframe.

B.5 Verdict rule
- Heatmap output is context only. Never a trigger. Never overrides any VVP-001 4 Tier 1 read. Never overrides any VVP-001 3.4 priority hierarchy decision. If heatmap and Tier 1 disagree, Tier 1 wins; note the disagreement per VVP-001 3.5.

B.6 If heatmap not present in screenshot
- Do not infer heatmap state from any other field. Report absence. No verdict impact.

## C. FOOTPRINT PROTOCOL

Status: EXTENDS VVP-001 6 (Proof Detection) using manual_patterns.md 1 (Working notes, NOT validated). All footprint reads are Tier 2 (primary) proof sources.

C.1 Pre-read (VVP-001 2.6)
- Confirm zone markings visible on chart. Without zone markings, footprint read is invalid.

C.2 Panel identification
- Footprint panel = per-price bid/ask transactions. Not to be confused with the CVD line (VVP-001 4 Tier 1) or Net Delta (VVP-001 4 Tier 1). All three may coexist.

C.3 Per-bar read (VVP-001 3.1)
- Read each bar's bid side and ask side separately. Record bar extreme (largest one-sided print).

C.4 Absorption (manual_patterns 1)
- Step 1: identify candidate bar — one-sided volume >= 1,500 BTC (threshold from manual_patterns 1, unvalidated).
- Step 2: check next bars — opposite-side bars >= 150 (manual_patterns 1).
- Step 3: verify price did NOT break through the level.
- Step 4: cross-check conditions.volume_spike_at_level (schema v1.2.0) — TRUE corroborates.
- Step 5: tag per VVP-001 6.1.

C.5 Exhaustion (manual_patterns 1)
- Step 1: candidate bar >= 500 BTC (manual_patterns 1, unvalidated).
- Step 2: next 2-3 bars shrink.
- Step 3: opposite direction re-enters.
- Step 4: cross-check conditions.speed_picking_up (schema v1.2.0) and conditions.rejection_wick_at_zone.
- Step 5: tag per VVP-001 6.3.

C.6 Snapshot cross-check (mandatory, not optional)
- For every footprint read, confirm against: cvd.slope, cvd.cvd_recent.slope_1h, cvd.last_3_delta, trade_flow.net_delta_1m, trade_flow.net_delta_5m, order_book_depth.bid_ask_ratio.
- If snapshot confirms -> tag per VVP-001 6 item.
- If snapshot contradicts -> tag per Section G below.
- If snapshot silent (field null) -> tag per Section G below.

C.7 Two patterns on the same zone strengthen the read (manual_patterns 1 close). One pattern = single-signal, weaker.

## D. FIELD-TO-VISUAL TABLE (per screenshot type)

Screenshot types taken from VVP-001 5 timeframe priority table.

D.1 CT at daily zone — 15m primary / 1H context / 4H macro
| JSON field (exact path) | Must be confirmed or contradicted visually |
|-------------------------|--------------------------------------------|
| current_price | 15m last close (VVP-001 2.3) |
| daily_vp.poc, daily_vp.vah, daily_vp.val | Zone lines visible on 1H (VVP-001 2.6) |
| vwap.price, vwap.slope | VWAP line + slope on 15m (VVP-001 4 Tier 1) |
| cvd.slope | CVD panel 15m (VVP-001 4 Tier 1) |
| trade_flow.net_delta_15m | Net Delta 15m panel |
| structure.15m.swing_high, structure.15m.swing_low | Swing markings on 15m |
| open_interest.direction | OI panel 15m (VVP-001 4 Tier 2) |
| conditions.price_vs_va | Visual position vs VAH/VAL lines |

D.2 CT at 4H zone — 5m primary / 15m context / 1H macro
| JSON field | Visual check |
|------------|--------------|
| current_price | 5m last close |
| intraday_4h_vp.poc/vah/val | 4H zone lines on 15m |
| vwap.price | 5m VWAP |
| cvd.slope, cvd.last_3_delta | 5m CVD + last-3 direction |
| trade_flow.net_delta_5m | 5m Net Delta panel |
| structure.5m.swing_high/low | 5m swings |
| open_interest.direction | OI on 5m |

D.3 TC pullback — 15m primary / 1H context / 4H macro
| JSON field | Visual check |
|------------|--------------|
| current_price | 15m last close |
| structure.15m.swing_high/low, structure.1h.swing_high/low | Both TF swings visible |
| vwap.price | Trend-side of VWAP |
| cvd.slope, cvd.cvd_recent.slope_1h | Pullback CVD shape |
| trade_flow.net_delta_15m | Net Delta |
| conditions.speed_picking_up | Candle body expansion (VVP-001 6.4) |

D.4 BO — 5m/15m primary / 1H context / 4H macro
| JSON field | Visual check |
|------------|--------------|
| current_price | Breakout candle close vs level |
| daily_vp.vah or daily_vp.val | Break level visible |
| conditions.volume_spike_at_level | Volume expansion at level |
| conditions.speed_picking_up | Candle expansion (VVP-001 6.4) |
| open_interest.direction, open_interest.change_1h_pct | OI confirming break |
| order_book_depth.bid_ask_ratio | Book skew toward breakout side |
| cvd.slope | CVD slope aligned with break |

D.5 Scalp — 3m/5m primary / 15m context / 1H macro
| JSON field | Visual check |
|------------|--------------|
| current_price | 3m/5m last close |
| vwap.price, vwap.bands (+1s/+2s/-1s/-2s) | Band touch/rejection (VVP-001 4 Tier 1) |
| cvd.slope | Short-window CVD turn |
| trade_flow.net_delta_1m | 1m Net Delta |
| order_book_depth.bid_ask_ratio | Book skew at band |

## E. QUAD RECONCILIATION

E.1 Source
- quad_classify.py output (runtime). Classes: new_longs, short_cover, distribution, weak_rally, new_shorts, long_liquidation, accumulation, weak_sell, flat. Carries a delta_conflict suffix when delta_aligned == False.
- Chart visual = price direction + CVD direction + OI direction as read per VVP-001 3.1 and 3.2 on the SAME timeframe label.

E.2 Conflict resolution rule (explicit)
- Step 1: Confirm both sides refer to the SAME timeframe. If quad's 1h window and the chart's visible window differ, this is not a conflict — it is a scope mismatch. Report the scope mismatch. Do NOT flag as conflict.
- Step 2: If timeframes match and quad says X while chart shows Y:
  - Apply VVP-001 3.4: DSA is primary for OI direction and book imbalance; visual is primary for CVD slope and delta direction.
  - If the conflicting axis is OI -> DSA wins. Report visual as supplementary.
  - If the conflicting axis is CVD/delta -> visual wins. Report quad as supplementary.
  - If both axes conflict -> downgrade confidence (VVP-001 3.5). Tag per Section G.
- Step 3: Never silently overwrite quad output or the chart read. State both, state the resolution per VVP-001 3.5.

E.3 delta_conflict suffix
- quad_classify.py already flags this. If the suffix is present AND the chart confirms CVD/delta counter-flow, treat as confirmation of quad's flag. If chart contradicts, apply E.2 Step 2.

E.4 Cross-timeframe values are not contradictions
- Per VVP-001 3.3, a 1h CVD reading and a 5m CVD reading describe different windows. A "conflict" between them is not a conflict.

## F. ORDER OF OPERATIONS (per screenshot)

Strict order. No step skipped. Derived from VVP-001 7 checklist.

F.1 Pre-read gate (VVP-001 2.1-2.6)
- 1. Cursor at right edge.
- 2. Timeframe label visible.
- 3. Price OHLC header visible.
- 4. Indicator legends readable.
- 5. No overlays blocking.
- 6. Zone markings visible (VVP-001 2.6).

F.2 Tier-1 read (VVP-001 4 Tier 1)
- 7. Volume Profile (Fixed Range) — POC, VAH, VAL.
- 8. VWAP + bands.
- 9. CVD line.
- 10. Net Delta.

F.3 Tier-2 read
- 11. Open Interest panel.
- 12. If footprint panel present -> run Section C.

F.4 Tier-3 read (context only)
- 13. If heatmap present -> run Section B.
- 14. Otherwise report absence. No verdict impact.

F.5 Reconciliation
- 15. Run Section E (quad vs chart).
- 16. Run Section D field table for the applicable screenshot type.

F.6 Output
- 17. Tag each field per Section G.
- 18. Emit verdict per compiled_engine.md.

## G. FAILURE FLAGS

Three tags. Exact strings. No others.

G.1 [VISUAL-CANNOT-CONFIRM:<field_path>]
- When: field value exists in JSON but the visual does not show the information needed to confirm or contradict (e.g., open_interest.direction present but no OI panel on screenshot).
- Verdict impact: field confidence drops to "unknown" for this analysis. Does NOT change verdict on its own. Does NOT trigger visual validation gap.
- Reference: VVP-001 3.4 table (last column "Action on Conflict").

G.2 [VISUAL-CONTRADICTS:<field_path>]
- When: visual clearly shows the opposite of what the JSON field states, on the same timeframe and same scope.
- Verdict impact: flag only. Field is excluded from proof scoring for this analysis. No auto band downgrade (Rule 32: a visual flag cannot modify a verdict without 3-snapshot evidence). Judgment layer decides whether the contradiction affects the verdict. If a hard-stop check depended on the field, emit the hard stop.
- Reference: VVP-001 3.5 (flag, do not override silently).

G.3 [SCOPE-MISMATCH:<field_path>]
- When: JSON field and visual refer to different timeframes or different windows (VVP-001 3.3). Not a contradiction.
- Verdict impact: none. Informational only. Both values retained.

G.4 Absence rule
- If a required source file for a section was not available, that section is marked MISSING at the top of the section body. In this run, no section is MISSING — all four required sources (VVP-001, manual_patterns, data_schema_v1.2.0) were available. heatmap_field_map.md was not provided; Section B is written entirely from VVP-001 4 Tier 3 and schema v1.2.0. If heatmap_field_map.md exists, it does not change Section B's rules (context-only), only its field list — flag for follow-up.

# END OF VVP-002
