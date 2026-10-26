# STATE MACHINE DESIGN - 2026-09-11
# Status: DESIGN ONLY - no code until approved
# Purpose: Continuous market context via a compact state code

## 1. WHY

Snapshots are isolated. Between snapshots, transitions are invisible.
The engine proposes setups based on the current snapshot, but by the time
the user sees them, the flow may have flipped.

This design emits a state code every 60 seconds from the live stream, giving
continuous context between snapshot evaluations.

It does NOT replace snapshots. Snapshots produce setups. State codes
provide context. Two layers, two jobs.

## 2. STATE CODES

| Code  | Meaning |
|-------|---------|
| A     | Neutral. Neither direction has conviction. |
| A>S   | Short building. 3-4 bearish signals, not yet confirmed. |
| A>L   | Long building. 3-4 bullish signals, not yet confirmed. |
| S     | Short active. 5+ bearish signals aligned. |
| S>L   | Long flip forming. Bearish weakening, bullish emerging. |
| L     | Long active. 5+ bullish signals aligned. |
| L>S   | Short flip forming. Bullish weakening, bearish emerging. |

Read alongside `bearish_count` / `bullish_count` (0-7 canonical, 0-5 in v1) for granularity.
v1 ships with 5 signals (see §10 Q9): thresholds recalibrate to
A>S=2, A>L=2, S=3, L=3. The 2-gap between emerging and confirmed is
preserved across both scales.

## 3. SIGNAL SET (7 signals canonical; 5 in v1)

| # | Signal | Bearish if | Bullish if | Neutral if |
|---|--------|-----------|-----------|-----------|
| 1 | net_delta_1m | < 0 | > 0 | = 0 |
| 2 | last_3_delta | 3x neg | 3x pos | mixed |
| 3 | volume_ratio | >2.0 & down bars | >2.0 & up bars | <2.0 |
| 4 | book_imbalance | < 0.5 | > 1.5 | 0.5-1.5 |
| 5 | cvd.slope | falling | rising | flat |
| 6 | OI + price | rising+fall | falling+rise | else |
| 7 | price vs vwap | below | above | within 0.05% |

All signals are derivable from the current JSON snapshot. No new data feeds.

v1 excludes signals 4 (book_imbalance) and 6 (OI + price) — both require
a REST poll the v1 emitter does not perform. v2 adds them back (see §6).
Thresholds for the 5-signal set are in §2 and §4.

## 4. TRANSITIONS (with hysteresis)

Each tick: count bearish and bullish signals.

- A -> A>S    : bearish >= 3 and bullish <= 1
- A -> A>L    : bullish >= 3 and bearish <= 1
- A>S -> S    : bearish >= 5
- A>S -> A    : bearish < 3 for 2 consecutive ticks
- S -> S>L    : bullish >= 3
- S -> A      : both counts < 3 for 2 consecutive ticks
- L -> L>S    : bearish >= 3
- L -> A      : both counts < 3 for 2 consecutive ticks
- S>L -> L    : bullish >= 5
- S>L -> S    : bearish >= 5
- L>S -> S    : bearish >= 5
- L>S -> L    : bullish >= 5

v1 (5-signal): thresholds scale to A>S=2, A>L=2, S=3, L=3.
The 2-gap between emerging and confirmed is preserved.

Partial availability: thresholds are fixed at the v1 5-signal values
regardless of how many signals are available. Unavailable signals
count as neither bearish nor bullish. Snapshots with fewer than 3
available signals are skipped entirely - no state evaluation, no
transition, no log line. Fixed thresholds preserve semantic
stability; the skip rule prevents low-information snapshots from
driving transitions. This is why the historical prototype exercised
3-signal density for 90% of snapshots without corrupting the
transition table.

Hysteresis: 2 consecutive ticks with the new condition before transition
fires. Prevents flip-flop on single-tick noise.

## 5. OUTPUT SCHEMA

Written to `mts/runtime/state_code.json` every 60 seconds:

{
  "timestamp_utc": "2026-09-11T08:30:00Z",
  "state": "S",
  "bearish_count": 3,
  "bullish_count": 0,
  "seconds_in_state": 180,
  "last_transition_utc": "2026-09-11T08:27:00Z",
  "transition_chain_15m": ["A", "A>S", "S"],
  "weekend": false,
  "signals": {
    "net_delta_1m": -8.3,
    "last_3_delta": ["neg","neg","neg"],
    "volume_ratio": 2.4,
    "cvd_slope": "falling",
    "price_vs_vwap": "below"
  }
}

Atomic write: tmp file + os.replace. No partial reads.

Consumer caveat: emitter's cvd_slope (aggTrade-based) may diverge numerically
from snapshot's cvd.slope (kline-based). Names differ (signals.cvd_slope vs
cvd.slope) - do not equate them.

Ring buffer: 30 entries held in memory. `transition_chain_15m`
displays the last 15. Consumers may request longer windows.

## 6. ARCHITECTURE (recommended)

Java continuous mode:
- New Main mode: `statemachine BTCUSDT`
- Subscribe to @aggTrade (real-time trades, aggressor m flag)
- Compute state every 60s
- Write state_code.json (atomic)
- Reconnect + backoff logic reused from BinanceLiquidationAccumulator

v1 ships 5 signals (net_delta_1m, last_3_delta, volume_ratio,
cvd_slope, price_vs_vwap). No REST poll in v1. OI + book_imbalance
are deferred to v2 to keep the emitter WebSocket-only.

Restart persistence: on construction, StateCodeEmitter reads state_code.json
if present and restores currentState + transition_chain. Missing file -> start at A.

Session boundary: session CVD and VWAP accumulators reset at 00:00 UTC rollover.
Funding resets (08:00, 16:00) are contextual events, not session boundaries.

Alternative: Python cron every 60s.
- Calls existing snapshot (heavy)
- Or reads last snapshot (may be stale by up to cadence)
- Simpler but slower or staler

Recommendation: Java. Java owns the wire. Reuse accumulator pattern.

## 7. CONSUMERS

- math_object_builder.py: reads state_code.json alongside snapshot.
  If state contradicts setup direction (e.g., state=S but candidate is
  long), downgrade verdict.
- AI session: reads state_code.json at start. Example: "State: S4,
  180s, flow bearish."
- divergence_monitor.py: optional cross-check.

## 8. VALIDATION PLAN (Rule 32)

Design approval does not require Rule 32. Each RULE (transition threshold,
signal definition) enters live code only after 3-snapshot evidence showing
the rule changes a verdict.

Rule 32 flow:
1. Run statemachine in observation mode for N days.
2. Capture all state transitions.
3. For each rule, test: would removing it change behavior on 3 snapshots?
4. Rules that pass 3-snapshot test -> commit to live.
5. Rules that do not -> discard.

## 9. WHAT IT DELIBERATELY DOES NOT DO

- Does NOT emit trade recommendations.
- Does NOT replace setup_candidates.
- Does NOT hard-reject candidates. Soft downgrades only (see §7).
- Does NOT add new indicators (uses existing JSON fields only).
- Does NOT need a Python Binance client (Java owns the wire).

## 10. RESOLVED QUESTIONS (2026-09-11)

1. Hysteresis: 2 consecutive ticks.
2. Emit frequency: 60s.
3. Transition thresholds: 7-signal canonical = A>S=3, S=5.
   5-signal v1 = A>S=2, S=3. 2-gap preserved.
4. State contradiction with candidate: soft downgrade (see §7).
   §9 adjusted to match. No hard reject.
5. Persistence: 30-entry ring buffer; display 15.
6. Weekend behavior: normal operation. `weekend` flag in output.
   No forced A, no pause.

## 11. NEXT STEPS

1. Design approved 2026-09-11 (see §10 RESOLVED).
2. Build Java statemachine mode (1-2 days work).
3. Run 24h in observation-only mode (no consumers).
4. Review transitions vs price action.
5. Rule 32 validate each threshold.
6. Wire into Python consumer.
7. Deprecate any redundant manual reads.

# END
