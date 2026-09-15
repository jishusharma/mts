# MTS Monitoring Summary - 2026-09-15 22:40

Sources: R5 last 500 apparatus lines | R4 last 100 session events | R6 last 60 snapshots.

## Alerts (R4) by trigger_type
| trigger_type | count |
|---|---|

## Setups (R6) by setup_type
| setup_type | count |
|---|---|

## Verdict distribution
| verdict | count |
|---|---|

## Baseline rates
- cycles observed: 0
- alerts observed: 0
- transitions observed: 0
- cadence gaps >120s: 0

## Analysis
1. What the system did - see D1/D2 counts above; dominant verdict and setup_type indicate current regime posture.
2. What the system missed - cross-check D5_cycles_without_verdict and D5_alert_parity for silent cycles.
3. Visible patterns - D5_pd_flips_per_hour and D4_transition_rate_per_hour show stability vs churn by hour.
