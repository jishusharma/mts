# Levels Confluence (LC) on BTC: research plan (operator idea, 2026-10-14)

Operator ask, chat 2026-10-14 (verbatim): "First, we need to identify the supports and resistances levels after the UTC date
start. And also, the point of control and value area high and value area low and all those things that Tom and Fabio cares
about ... when the support is visible (Could be also coming from RSI 40/60 like RSI taking suppoort on the RSI MA or on the 40
line, etc and sell at the first resistance (if CVD support is negative, stay if it is posittive or even flst or take out some
portion when flat, check if uh, the price is at the upper or the lower end of the Bollinger band ... take basic Tom and Fabio
ideas - form the bias - look for the levels - build the trade while price is moving around the levels and then get out step by
step as other indicators support."

Operator follow-up, chat 2026-10-14 (verbatim): "See u need to see what works - because if there are two levels of say support
(for long entries)- i would position to double down and then have a stop after I have built the full position. Also see what kind
of stops are good. if price reverses and meets the target thenthe stop was bad! So think in the same lines. And validate your
thoughts/ideas/findings!"

What it is: its own layer (`lc`, research only until LC3 passes; then it is added as a layer family and every TF/family map is updated). Under the 2026-10-13 rules (no fixed core) it may later be combined with Tom or Fabio. It borrows their level ideas (prior-day value area, POC, session
levels) plus consensus levels. Every number is tagged SOURCED (trader quote + file:line) or OURS (fixed before the run, printed in
the report), per the 2026-10-13 rules rewrite (q14).

## The idea in four parts (each one is a test arm, not a fixed choice)

| Part | What | Arms (pre-registered; nothing else gets tried) |
|---|---|---|
| L Levels | All known at 00:00 UTC, causal | prior-day high/low; prior-day POC/VAH/VAL (70 % value area, 1m volume profile); naked POCs of the last 10 days; daily open; prior-week high/low; 4h swing pivots (5-bar fractal); round numbers (1000s). Each level carries its source tag TOM / FABIO / CONSENSUS / OURS |
| B Bias | Higher-timeframe direction | B0 none (control); B1 price vs prior-day value area (above VAH up, below VAL down, inside neutral); B2 swing structure (higher highs+lows / lower highs+lows) on 1h, 4h, 6h, 12h, 1D; B3 close vs 20-period EMA on the same TFs |
| E Entry | At the level, with the bias | E0 touch only (control); E1 RSI(14) holds 40 (long) / 60 (short) (`layers/rsi/malkan_40_60.py`); E2 RSI holds its MA (`rsi_ma.py`); E3 CVD turns with the trade at the touch (5m CVD slope sign); E4 price at the outer Bollinger band (20, 2) |
| X Exit | Step out | X0 fixed 1R/2R (control); X1 all out at the first opposing level; X2 ladder: 1/2 at first opposing level, rest held while CVD agrees, 1/2 of the rest when CVD goes flat, all out on CVD against or the opposite Bollinger band; time stop at the end of the UTC day |

Fee rule, checked 2026-10-14: Binance USDT-M taker 0.05 % a side = 0.10 % round trip, maker 0.02 % a side (`backtest/fees.py:27-28`).
The "0.40 % minimum" is that 0.10 % divided by OUR cap "fees at most 0.25 R" (TOM_LAYER_V2_SPEC.md:316), so it is a fee-share
rule on the WHOLE position: stop distance measured from the AVERAGE entry. It is not a gate any more: every result is reported at
fee share <= 10 %, <= 25 %, <= 50 % of R, and the data says which share still pays.

| Part | What | Arms |
|---|---|---|
| S Scale-in (operator) | Two same-side levels L1 (nearer) and L2 (next one beyond it) | S0 full size at L1; S1 half at L1 + half at L2, ONE stop beyond L2 for the whole position, set from the start (operator: "a stop after I have built the full position"); S2 full size at L2 only (limit order, may never fill); S3 1/3 at L1 + 2/3 at L2 |
| K Stop | Where the one stop sits | K1 beyond the entry level by 0.10 %; K2 beyond L2 (structure); K3 beyond L2 by 0.5 x ATR(14, 1h); K4 a 15m CLOSE beyond L2 (not a wick); K5 beyond the day's low/high so far; K0 no stop (measurement only: gives the adverse-move path of every trade idea) |

R for every scale-in arm = the loss if every planned fill happens and the stop is hit. An idea where only L1 fills and then wins
earns its half; the test counts that, so averaging down is judged on all ideas, not only the ones that filled twice.

Stop quality (operator: "if price reverses and meets the target then the stop was bad"):
- BAD STOP = stop hit, then price reaches the trade's target before the end of the UTC day.
- GOOD STOP = stop hit, then price goes at least 1 more R against the trade before reaching the target.
- From K0, the adverse move of every trade that went on to reach its target (maximum adverse excursion of the winners): the stop
  that keeps 90 % of those winners is the "winner-safe" distance; a stop tighter than that is what makes bad stops.
- Check that keeps us honest: a wider stop always lowers the bad-stop rate, but each loss then costs more. The stop is chosen on
  net R after fees, not on the bad-stop rate; the bad-stop rate is a diagnostic printed next to it.

## Order of work (each step can stop the chain)

1. **Do the levels hold at all?** (LC1) For every first touch of every level per day: reaction (moves 1 x the stop width away
   before breaking through by the stop width) vs the same test on random price lines at matched distances. If a level family does
   no better than random lines, it is dropped before any indicator is stacked on it.
2. **Event table** (LC2). One row per first touch: level family, side, every bias arm per TF, every entry feature, forward MFE/MAE
   in R and which level is hit first. No trading rules yet. Which features separate good touches from bad, one at a time,
   with the count of tries written down (trial ledger, gap-g6).
3. **Ladder simulator** (LC3). Only the combinations step 2 kept (at most 6, chosen before the run) x scale-in S0-S3 x stops
   K1-K5 x exits X0-X2, DEV only, with the bad/good-stop table per stop arm.
   Report the minimum effect the sample can detect (gap-g1 power helper) next to every result; a FAIL below 50 % power reads
   INCONCLUSIVE, not STOP.
4. **VALIDATION once** (LC4). The frozen DEV winner, one run on the validation window. No changes after.

## Data and windows

- Binance BTCUSDT perpetual 1m klines (taker-buy volume gives a CVD proxy, `bt/bt_data.py cvd_delta`) and the footprint bars on
  JIS-NUC (`F:\MTS\data\orderflow_1m`, real buy/sell split) where they exist.
- DEV 2024-12..2025-03, VALIDATION 2025-04..2025-06 (same split as Tom on BTC; both studies log their trials in one ledger, so
  the shared window is counted). Nothing after 2025-06 is read.

## How each finding is validated (operator: "validate your thoughts/ideas/findings")

- Every result is compared with a control that has no skill: random lines (levels), random entry times on the same days (entries),
  S0 vs S1 on the SAME trade ideas (scale-in), K0 adverse moves (stops).
- 95 % confidence intervals by bootstrapping whole days (BTC days are not independent bars).
- The minimum effect the sample can detect is printed next to each result (gap-g1); a FAIL below 50 % power reads INCONCLUSIVE.
- Every arm tried goes into the trial ledger; the count is in the report, so a "best of 40" is read as one.
- Look-ahead tests: every level, bias and indicator value uses only bars closed before the decision bar (unit tests on
  synthetic days, plus one shuffle test: shuffling day order must destroy any level effect).
- Claude spot-checks one number per GPT report against the raw bars; the frozen rule is read ONCE on VALIDATION.

## Where it can go wrong (read before believing a result)

- Averaging down looks good on ideas that came back and hides the ones that did not: R is set on the full planned size, and S1 is
  compared with S0 on the same ideas.

- Many knobs: 7 level families x 4 bias arms x 5 TFs x 5 entries x 3 exits is hundreds of combinations. Step 2 picks with one
  feature at a time and a written count; step 3 runs at most 6. More is curve fitting.
- RSI 40/60, RSI-MA and Bollinger bands are consensus tools with weak stand-alone evidence on BTC (research/published_strats_2026-10-13).
  They are tested as filters on levels, not as signals.
- Fees: on BTC the stop must be at least 0.40 % wide, so the first opposing level must be far enough away to pay; touches with a
  nearer opposing level are counted, not traded.
- Kline CVD is a proxy; where footprint bars exist the two are compared on the same touches.

## Cards (lane CODEX = GPT lab on JIS-NUC; DSA-NUC runs; Claude spot-checks one number per report)

lc-levels-hold (LC1), lc-event-table (LC2), lc-ladder-dev (LC3), lc-validation (LC4). `python scripts/dev/tasks.py brief <card>`.
