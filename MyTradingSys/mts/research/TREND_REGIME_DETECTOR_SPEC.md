# TREND REGIME DETECTOR SPEC

Generated: 2026-09-15
Basis: ALERT_REDESIGN_PROPOSAL.md, Path B

## PURPOSE
Per-cycle regime classifier as a derived feature, not a new engine
rule. Exists so future verdict-wiring proposals can test against
it under Rule 32.

## INPUTS (existing snapshot fields only)
- conditions.vwap_slope (rising | falling | sideways)
- conditions.cvd_slope (rising | falling | sideways)
- cvd.slope, cvd.slope_pct
- trade_flow.net_delta_15m, net_delta_1h
- structure.1h.swing_high, swing_low
- structure.15m.swing_high, swing_low
- conditions.price_vs_va (in_va | above_vah | below_val)
- conditions.vp_shape (B | P | D)
- open_interest.direction (rising | falling)
No new fields.
## LOGIC (per cycle)

Define:
  trend_up_votes = 0
  trend_down_votes = 0
  if vwap_slope == "rising":  up += 1
  if vwap_slope == "falling": down += 1
  if cvd_slope == "rising":   up += 1
  if cvd_slope == "falling":  down += 1
  if net_delta_1h > 0:        up += 1
  if net_delta_1h < 0:        down += 1
  if vp_shape == "P":         up += 1
  if vp_shape == "D":         down += 1

Classify:
  if up >= 3:     candidate = TREND_UP
  elif down >= 3: candidate = TREND_DOWN
  else:           candidate = RANGE

Anti-whipsaw: require candidate label to hold 3 consecutive cycles
before publishing. A single conflicting cycle downgrades confidence,
not the label.

## OUTPUT
Per cycle, append to state_code.json as a new sub-object (do not
repurpose existing keys):

  "regime": {
    "label": "TREND_UP" | "TREND_DOWN" | "RANGE",
    "confidence": "LOW" | "MEDIUM" | "HIGH",
    "consecutive_cycles": integer,
    "entered_at_utc": ISO
  }

Initial label = UNKNOWN until first publish.
## PLACEMENT
Phase 1: standalone Python helper mts/runtime/regime_classifier.py.
Called by start_trading_day.ps1 immediately after snapshot
normalization, before verdict generation. Writes JSON sub-object
only. No verdict consumption.
Phase 2 (Rule 32 gated): verdict consumption at
start_trading_day.ps1 L411/L428 region, adjacent to existing trend
override logic. Only if 3-snapshot test shows a verdict change.

## FAILURE MODES OF THE DETECTOR ITSELF
1. Lagging label. structure.15m.swing_high updates while
   regime.label unchanged for >5 cycles.
2. Whipsaw. Consecutive flips TREND_UP -> RANGE -> TREND_UP within
   10 cycles.
3. Vote split. vwap.slope and cvd.slope disagree; net_delta_1h is
   noise. up_votes and down_votes both = 2 for extended periods.
4. Session contamination. New session starts but regime label
   carries over. Detection: session_timing.current_session changes
   while regime.entered_at_utc pre-dates the change.
Mitigation: expose regime.votes_up, regime.votes_down, and
regime.cycles_in_candidate_state as debug fields so failures are
visible on disk.

## WHAT THIS DETECTOR DOES NOT DO
- Does not gate any alert in phase 1.
- Does not modify compiled_engine.md.
- Does not replace the existing trend override. Both can run; the
  override remains per-cycle; the regime label is per-regime.

## RULE 32 POSTURE
Field creation (phase 1): not gated by Rule 32 (feature layer).
Verdict consumption (phase 2): Rule 32 requires 3-snapshot proof.
Test set: 2026-09-14 13:33, 15:00, 17:30 snapshots. Verdict change
required in at least one.