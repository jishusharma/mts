# ALERT FAILURE MODES

Generated: 2026-09-15
Source: ALERT_AUDIT_2026_09_13_14.md + Q7 discriminator audit
Scope: failure modes observed in 2026-09-13/14 window

## FM-1: NO PER-ZONE VISIT STATE
The engine re-fires the same zone on every cycle where zone price,
proof, or state changes. No field records that the zone was already
tested, or how many times.
Evidence: #284-#289 (6 consecutive weekly_vah fires 15:00-15:36 UTC,
same zone name). #296-#305 (10 consecutive 4h_vah fires 17:03-17:48).
Root cause (Q7): zone_visited_at absent in 0/73.
Impact (Q8): expectancy -138.74 pts/trade. #296-#305 lost 10 trades
in one hour.

## FM-2: NO TREND/REGIME GATE
Trend override (above_vah + cvd_slope rising -> suppress SHORT) is
per-cycle. Does not persist across a multi-hour directional move.
Evidence: 2026-09-14 up-leg fired override on 5 cycles
(17:07, 17:27, 17:29, 17:30, 17:47). ~30 ct_short alerts without
suppression.
Root cause (Q7): regime_filter and trend_direction absent in 0/73.
Impact (Q8): 40 ct_short alerts in 5-hour window. #271 lost -265.65 pts.
## FM-3: PROXIMITY WITHOUT ACCEPTANCE STATE
Engine fires on tag of a zone without a persistent state
distinguishing "just touched" / "accepted through" / "rejected."
Evidence: #296-#305 posted WATCH on 4h_vah repeatedly during the
up-move. Each WATCH was a proximity trigger. Zone was being
traversed, not rejected.
Root cause (Q7): acceptance_flag absent in 0/73. price_vs_va gives
position, not acceptance.
Impact (Q8): same expectancy as FM-1/FM-2. This is the structural
explanation; FM-1 and FM-2 are its two visible symptoms.

## FM-4: TARGET BEYOND HORIZON
Engine target (next volume node / POC / VWAP per compiled_engine.md
section 7) is systematically beyond the intraday horizon.
Evidence: all 73 alerts. 0/73 hit target within 60m. Representative:
#271 entry 78078.15 target 77266.80 (811.35 pts below entry);
#310 entry 78870.12 target 78380.25 (489.87 pts below entry).
Structural targets, unreachable in one 60m window on a
counter-trend fade.
Root cause (Q7): no field distinguishes structural target from
60-minute target.
Impact (Q8): 0/73 target hits. Single biggest driver of negative
expectancy.
## FM-5: RANK-1 SELECTION WITHOUT LEVEL CONTEXT
Rank-1 selects closest high-score candidate without regard for
whether the level is being approached from inside or outside value,
or whether it was just traversed.
Evidence: 2026-09-14 up-move rank-1 walked up through pf_vah ->
weekly_vah -> 4h_vah -> daily_vah -> 15m_swing_high. Each zone was
already crossed on the way up. Engine treated each crossing as a
fresh CT opportunity.
Root cause (Q7): no field encodes "just crossed" vs "approaching
from below with rejection." substate only says at_zone.
Impact (Q8): contributes to FM-1/2/3/4. Structural selection gap.

## CROSS-CUTTING OBSERVATION
FM-1, FM-2, FM-3, FM-5 are all the same shape: no persistent state
across cycles for the level or the regime. Per-snapshot by
architecture. FM-4 is orthogonal — target-horizon mismatch.

Three AIs (Claude, GPT, Grok) converged on the same framing:
the rejection is not the signal; the evolution of value/POC after
the rejection is the signal. MTS has no field for that evolution.

No failure mode above requires a new engine rule to diagnose. All
five are absent-field diagnoses, not misclassification diagnoses.