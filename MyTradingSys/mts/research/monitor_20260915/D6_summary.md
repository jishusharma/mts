# MTS Monitoring Summary - 2026-09-15 23:06

Window: last 60 cycles (R5 apparatus_log), last 100 events (R4 session_log), last 60 snapshots (R6), current state_code.json.

## Alerts (from apparatus_log ALERT lines)
| trigger_type | count |
|---|---|
| verdict|proof | 2 |
| verdict | 1 |

## Setups emitted by setup_type
| setup_type | count |
|---|---|
| ct_long | 45 |
| ct_short | 15 |

## Verdict distribution
| verdict | count |
|---|---|
| WAIT_RR | 60 |

## pd_flag distribution
| pd_flag | count |
|---|---|
| contradiction | 31 |
| aligned | 29 |

## State transition types (last 15m chain)
| transition | count |
|---|---|
| A, S | 6 |
| A, L | 1 |

## Baseline rates
- cycles observed: 60
- alerts observed: 3
- real transitions in 15m: 7 => ~28/hr
- cadence gaps >120s: 0
- cycles without verdict: 0
- current state: L; bearish=0 bullish=5 available=5

## Analysis

**1. What the system did.** Over the last 60 cycles (~1h), MTS emitted 60 setups (45 ct_long, 15 ct_short), verdict held at WAIT_RR on every cycle (net_rr 1.52-1.87 < 2.0). Position B/in_va throughout - price inside value area. 3 alert(s) fired on apparatus_log. This is a coiled, gated posture: setups present, entry filter refusing on reward.

**2. What the system missed.** Cadence healthy (51-53s, zero gaps >120s, zero verdict-less cycles). Soft flags: (a) pd_flag near 50/50 split (contradiction 31 / aligned 29) - churn, consistent with dictionary's aggTrade-vs-kline CVD caveat; (b) state_code chain shows 7 real transitions in 15m (~28/hr), mixing A>S and A>L - the A/S/L layer is noisier than the price/verdict layer.

**3. Visible patterns.** Verdict floor is RR, not trigger - every cycle reports 'price at zone, RR too low'. Setup not missing; filter working. 4h_value rising (76277.66 at 17:10 vs 76373.38 at 16:11) while price pinned ~76200, so net_rr improving as zone lifts toward price. If price holds and 4h_val rises another ~50 pts, RR crosses 2.0 without directional move. Real alerts in window are verdict-transition type (WAIT_RR -> WATCH) - watch for next one as trigger precursor.
