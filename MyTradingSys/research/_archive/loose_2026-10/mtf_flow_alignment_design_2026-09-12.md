# MTF FLOW ALIGNMENT - DESIGN
# Date: 2026-09-12
# Status: APPROVED - inert until Rule 32 evidence
# Authority: compiled_engine.md (unchanged by this doc)
# Scope: additive snapshot field only. No consumer rule.

## 1. WHY
Single-timeframe reads cannot separate a 15m blip inside a healthy trend
from a genuine reversal. The engine has no field that states whether
15m/1h/4h flow agree or contradict. This layer emits that state per
snapshot, inert, so evidence can accumulate.

## 2. TIMEFRAMES
15m, 1h, 4h. Fixed by user.
Rejected: 5m (user-rejected, noisy), 1d (too coarse), two TFs (no swing
envelope), four-plus TFs (user constraint).

## 3. PER-TF MEASUREMENT
axis      | source field                                              | scope
price 15m | current_price vs midpoint(structure.15m.swing_high/low)   | 24h
price 1h  | current_price vs midpoint(structure.1h.swing_high/low)    | session
price 4h  | current_price vs intraday_4h_vp.poc                       | session
flow 15m  | sign(trade_flow.net_delta_15m)                            | 24h
flow 1h   | sign(cvd.cvd_recent.delta_1h)                             | session
flow 4h   | sign(cvd.cvd_recent.delta_4h)                             | session

OI per TF is not available. coverage.oi_per_tf = "unavailable".

## 4. STATE VOCABULARY (per TF)
+A = price up, flow up (aligned bullish)
-A = price down, flow down (aligned bearish)
+D = price down, flow up (bullish divergence: flow refusing down)
-D = price up, flow down (bearish divergence: flow refusing up)
N  = neutral / one axis missing

Rejected A/D/F: A collides with the single-TF state machine vocabulary
(A, A>S, A>L, S, S>L, L, L>S); no direction; F needs an undefined
reference for "lagging".

## 5. PATTERNS (summary)
all_aligned_long                (+A,+A,+A)
all_aligned_short               (-A,-A,-A)
fast_aligned_slow_divergent     (+A,+A,-D) or (-A,-A,+D)
slow_aligned_fast_divergent     (+D,+A,+A) or (-D,-A,-A)
all_divergent_same              all +D or all -D
mixed_no_majority               no two same-sign A and no two same-sign D
thin_data                       any N (non-structural)

## 6. JSON BLOCK - SEALED SPEC
Key: mtf_flow_alignment

{
  "timeframes": ["15m","1h","4h"],
  "per_tf": {
    "15m": {"state":"+D","price_dir":"down","flow_dir":"up","scope":"24h"},
    "1h":  {"state":"+A","price_dir":"up","flow_dir":"up","scope":"session"},
    "4h":  {"state":"+A","price_dir":"up","flow_dir":"up","scope":"session"}
  },
  "pattern": "slow_aligned_fast_divergent",
  "pattern_scope_valid": false,
  "coverage": {"axes_present":6,"axes_max":6,"missing":[],"oi_per_tf":"unavailable"}
}

pattern_scope_valid: false when the three per_tf scope values differ,
true otherwise. Pattern is emitted regardless; consumers must check the
flag before acting on pattern.

Dropped per supervisor: direction_bias, conviction. Renamed from
mtf_divergence to mtf_flow_alignment.

## 7. SCOPE BOUNDARY
IN:  additive snapshot field, emitted every snapshot, inert.
OUT: no trade trigger, no stop/target, no score modification, no auto-
downgrade, no new API call, no new runtime file, no compiled_engine.md
edit, no consumer rule until 3-snapshot evidence.

## 8. RULE 32 PLAN
Rule 32 (01_AI_BEHAVIOR.md Section 10 rule 32): any engine rule must
change verdict on >=1 of 3 live snapshots.
Rule 32-B (adapted, from Phase 4 traceability matrix): meaningful
context shift acceptable where binary verdict does not change.
Flow:
1. Emit field on every snapshot. No consumer.
2. Accumulate until three actionable pattern families each have >=3
   samples across >=3 regimes.
3. For each candidate rule (e.g. soft-downgrade long when pattern =
   fast_aligned_slow_divergent AND pattern_scope_valid), locate 3
   snapshots where the rule changes the verdict.
4. Pass -> propose for compiled_engine.md with user approval.
5. Fail -> discard.

Sparse-snapshot caveat: minutes-to-hours-apart snapshots validate firing
and computability only, not timing.

## 9. KNOWN CONSTRAINTS
- 15m flow scope is 24h-rolling (trade_flow.net_delta_15m).
- 1h/4h flow scope is session-anchored 00:00 UTC (cvd.cvd_recent).
- Not numerically comparable; scope-tagging makes the difference
  explicit; pattern_scope_valid gates cross-scope use.
- structure has 1h/15m/5m only; 4h price reference is intraday_4h_vp.poc.
- OI per TF unavailable.

## 10. OPEN
1. Should 15m use a session-anchored flow metric if one is added later?
2. Does 4h price reference stay on intraday_4h_vp.poc, or move to
   structure.4h mid if the producer adds it?
3. Flow magnitude floor: sign-only, or per-TF noise floor?

# END
