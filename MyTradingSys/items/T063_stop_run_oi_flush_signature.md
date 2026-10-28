# T063 - Opposite-extreme sweep + OI flush + CVD in step: reversal vs continuation (operator observation)

Opened 2026-10-05 by MTS-2026-10-05-1500Z-APP-ANA-operator-asks. Status OPEN. Verbatim ask: research/_archive/loose_2026-10/OPERATOR_ASKS_2026-10-05.md section 0, ask 1. Related: T058, G12, B136, T055a.
Tag: [OPERATOR] hypothesis. Separate layer if it survives; never a Tom filter. Parameters research-only until sourced.

## Hypothesis (operator, to be tested)
Before a directional move, price takes the local pivot on the opposite side; at that moment OI drops sharply versus
adjacent bars while price and CVD move together (stops / positions closing); then price turns. A very strong push may
differ. Unknown: how far price retraces before snapping back.

## Worked example 2026-10-05 (master section 1)
Up-poke 14:07Z above the 08Z high with OI rising (new longs) -> effort without result -> 14:30-14:34 flush: OI -1,108 BTC,
delta -3,063, price -1,280. Low 85,400.1 vs 4h swing low 85,369 (not taken at 14:55).

## Plan
1. D: 1m OI recorder + 30 d 5m backfill (task row 3). Needs B136 for the snapshot side.
2. C: event study on 1m/5m/15m/1h. Events = pivot sweep (N-bar fractal). Classify by OI change percentile x CVD sign x
   price sign (4-state, see runtime/backtest_oi_delta_4state.py). Outcomes: reversal vs continuation within K bars;
   retrace depth in ATR and vs VA/POC/next node; time to reclaim. Pre-register; holdout split.
3. C: T064 quotes on stop runs and retrace depth feed the definitions (Tom: next volume node; Fabio: next liquidity cluster).
4. Alert candidate goes to T067 only if the study passes.
