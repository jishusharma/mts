# PREREG: analyst-call paper slot ("where / when / size")

Frozen 2026-11-11 before any trade, count or return of this setup was computed. Forward paper only: no backtest is run, no order,
no account, no scheduler. Operator decision: OPERATOR_DECISIONS.md 2026-11-11 18:50Z (calls with a level become the "where",
paper only; reverses the 11-04 "context only" for this slot alone).

## Context

- Why: every piece tested alone failed (EDGE_PLAN.md f; edge_views_2026-11-11/TESTED_MAP.md, about 100 studies). The operator
  trades a level named in advance plus a trigger at that level. That combination was never tested.
- Phase: range since 2026-10-24 (OURS reading); method d-phase-first-method-1106 (forward until it fails).
- Regime mix: not computed (forward only, no history window). Each trade row records the D SMA20 +-2 % regime at entry (OURS).
- Trial count: this is 1 setup with 2 triggers, frozen. Any change to a number below is a new trial with a new params_id.
- Known weak support, stated so nobody leans on it: "forced move reverts" failed on VALIDATION pooled over ten coins
  (edge_views_2026-11-11/POOLED/RESULT.md, per the Supervisor); touching a level alone was a coin flip (0 of 48 streams).

## The setup (all numbers OURS unless marked)

Data: BTCUSDT 15m closed bars, public Binance klines. Bar delta = 2 x taker-buy volume - volume.

1. WHERE. A call row in `calls.jsonl`: analyst, side (long/short), zone [lo, hi] in USD, t_logged, expires. A single price L
   becomes the zone [L x 0.9975, L x 1.0025] (25 bp each side). A call counts only for bars that open after t_logged (the call is
   written down before the outcome). Default life 7 days from t_logged when the analyst gives none.
2. TOUCH. The first closed bar after t_logged whose low <= hi (long) or high >= lo (short).
3. WHEN. One of two triggers, on a bar inside the 16 bars (4 h) that start at the touch bar:
   - T1 divergence: regular RSI(14) divergence on closes, 3 to 10 bars between the two swings, in the call direction
     (SOURCED: Malkan, rsi/params/malkan_divergence_default.json; code backtest/layers/alerts/live_rsi_divergence.py).
   - T2 flow turn: a bar with delta > 0 and close > open (long; mirrored for short), where at least one of the 3 bars before it
     had delta < 0 (long; > 0 for short).
   The first trigger bar wins; if both fire on the same bar the row says T1+T2. No trigger inside the window: no trade (row
   `no_trigger`). One trade per call.
4. ENTRY. Open of the bar after the trigger bar. One open trade at a time for the slot; a signal while one is open is logged
   `skipped_busy` and never traded.
5. SIZE (EDGE_PLAN a). Stop = lowest low from the touch bar to the trigger bar, or zone lo if lower (long; mirrored for short).
   A stop nearer than 40 bp from entry is moved out to exactly 40 bp. Target = 2 x stop distance (so at least 80 bp, above the
   62 bp / 500 USD floor). Time stop: close of bar 96 after entry (24 h). Stop and target in the same bar: stop first.
6. COSTS. Only backtest/fees.py: FEES_ALL_TAKER entry + exit kind, plus SLIPPAGE_RT_S13. R = net return / stop distance.

## The two placebos (journalled by the same logger, never traded)

- Placebo A, level without trigger: for every call, enter at the open of the bar after the TOUCH bar. Stop = touch-bar low or
  zone lo if lower, moved out to 40 bp; same target, time stop and costs.
- Placebo B, trigger without level: T1 or T2 exactly as above, in the trigger's own direction, on a closed bar whose close is
  more than 1 % away from every live call zone, with T2 needing no touch. Stop = lowest low (highest high) of the 10 bars up to
  the trigger bar, moved out to 40 bp; same target, time stop and costs. One open placebo-B trade at a time.

## Decision rule

- Readout every week shows, for setup, placebo A and placebo B: trades, mean net R, and this rule.
- STOP: 30 closed setup trades with mean net R <= 0 (EDGE_PLAN c), or E- per the forward readout.
- EDGE-CANDIDATE: at least 30 closed setup trades, mean net R > 0, above the mean net R of placebo A and of placebo B.
- Below 30 trades the only allowed word is RUNNING. Expected pace: a few trades per month, so 30 trades take months.
- Lopez de Prado rules (EDGE_PLAN e): no sweep, one trade at a time, nothing tuned on the trades this slot produces.
