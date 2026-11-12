# PREREG: BTC last untested order-flow rules (btc-last-orderflow-rules-1112), written 2026-11-12 before any result

Goal: a fee-net edge before 2026-11-17. Operator decision 2026-11-12 (OPERATOR_DECISIONS.md, 10:05Z): each rule is read inside the phase and side its author traded; BTC is read on its own terms, only the order-flow idea is taken.
Nothing below was run. The only statistics computed before this file: the regime mix, the sd of 60-minute closes, and the gate (price statistics over all DEV bars, not event results).
SOURCED = a quote from `research/orderflow_extracts_1112/ORDERFLOW_RULES.md`; OURS = chosen here, cannot be called the author's.
Not touched: BB3c8visnkI R4/R5, YkclL6xgu-s R5, ODdF0Bn_KSc R6 (worker btc-untested-rules-1112). Folder check: `git ls-tree origin/fast-track MyTradingSys/research/` has no btc_last_orderflow_rules_1112.

## Context
Regime: the phase of each rule is its own gate (below); no cycle-phase gate is added. `Regime mix:` DEV days (2022-02-01..2024-05-31, 851 days; label = 90-day close return > +20 % bull, < -20 % bear, else range; the first 59 days lack the lookback): bull 301, bear 136, range 355, n/a 59. Each RESULT row also reports the regime mix of its own events.
Phase: each rule is gated to its author's phase (table below: falling market for R8, open inside prior-day value for R5, a fresh value-area breakout for R11); no cycle-phase gate beyond that.
Entry: next 1m open after the signal bar closes (R11: after the second follow-up 15m bar closes); exit 60 minutes later; taker fee both sides.
Phase and side per rule (the operator's "his phase" reading):

| Rule | Author's phase | Author's side | Carried to BTC as |
|---|---|---|---|
| y67l86cSqb8 R8 | a market that is falling ("the market will continue to fall") | trend-following short until selling delta is big | arm R8a: trend-down + no sell extreme -> short. Arm R8b (OURS reading of the extract's "a trend ends with a delta/volume extreme"): trend-down + sell extreme -> long |
| 9IliXww64uM R5 | day starts inside the previous value area, range expected | fades from the value-area edges (both edges) | arm R5: open inside prior-day value area, first edge touch -> fade |
| 9IliXww64uM R11 | a breakout of the range with volume that does not dry up | with the breakout, both directions | arm R11p: volume persists -> with the break. Arm R11d (comparison group, "each group"): dry-up -> with the break |

Session: the UTC day is BTC's own day (OURS; the index-futures cash-open clock is not carried). Entry hours are tagged in RESULT.

## Not repeated
| Earlier work | Difference |
|---|---|
| btc_orderflow_map_1112 A2 (absorption), A3 (funding), B2 (large prints at a level) | different events; none uses a rolling delta percentile, the prior-day value area, or breakout volume persistence |
| fabio_cvd_2026-10-30, orderflow_views_2026-10-14 | CVD divergence rules; not repeated |
| edge_views_2026-11-11 TESTED_MAP | the verdicts.py check below returned no prior row |

Data note: delta = 2 x taker_buy_volume - volume from the 1m klines is the same quantity as summing aggTrades by aggressor side per minute, so the aggTrades at `D:/MTS_data/binance_aggtrades` are not needed and not read (OURS, stated so nobody expects them).

## Data and splits
1m klines `F:/MTS/data/tom_raw/klines/BTCUSDT-1m-YYYY-MM.csv`, 2022-01 .. 2024-05 only (loader refuses later months; 2022-01 is trailing warm-up). DEV = 2022-02-01 .. 2024-05-31. VALIDATION (2024-07-01 on) is never read. Halves for the pass bar: first = entry before 2023-04-02, second = entry from 2023-04-02 (midpoint of DEV, OURS).
Entry = open of the 1m bar after the signal bar closes. Exit = close of the 1m bar 60 minutes later (entry bar + 59; SOURCED convention of btc_orderflow_map_1112/events.py). One horizon only: 60 minutes (OURS, chosen so the gate passes at n 180). Fee 10 bp round trip (0.05 % per side taker, `backtest/fees.py`, SOURCED operator brief). Net % = side x gross - 0.10. No stop, no target, no sizing.

## Rules and parameters (all frozen now)
Common (OURS): a signal whose window has any missing 1m bar is dropped.

R8 (`y67l86cSqb8`; quote "If it doesn't get big, the probability is simply very high that the market will continue to fall." SOURCED; "You can't just use the same values everywhere. Instead, you need to know the specific metrics." SOURCED, so the extreme is BTC's own percentile):
- Decision time = every UTC hour close H (1h bar = 60 1m bars).
- delta60 = sum over the last 60 1m bars of (2 x taker_buy - volume). Definition SOURCED ("Delta means the total accumulated buying actions minus the corresponding selling actions.").
- Trend-down (OURS): 1h close < mean of the last 48 1h closes AND 1h close < the close 24 hours earlier.
- Sell extreme (OURS): -delta60 >= the 95th percentile of -delta60 over the previous 720 hourly decisions (30 days, strictly before H). 95 is OURS; no number is in the video.
- R8a: trend-down AND delta60 < 0 AND not sell extreme -> short. R8b: trend-down AND sell extreme -> long.
- Descriptive extra (the quote's "versus before"): mean gross forward return of a short in trend-down hours, split extreme vs not extreme.

R5 (`9IliXww64uM`; quote "This is already a good sign that we're probably going to stay inside of this range for the rest of the day" SOURCED; extract: look for fades from its edges):
- Prior-day value area (OURS, market-profile convention, no quote): previous UTC day's 1m bars, volume put at typical price (high+low+close)/3, bins of 0.05 % of the previous day close, POC = max bin, VA = expand from the POC one bin at a time toward the neighbour with more volume until >= 70 % of the day's volume. VAL/VAH = lower edge of the lowest and upper edge of the highest bin in the VA.
- Event day: the 00:00Z 1m open lies inside [VAL, VAH].
- Trade: the first 1m bar of the day (00:01Z to 20:00Z inclusive) whose high >= VAH (short) or low <= VAL (long), whichever is first; if one bar touches both, skip the day. One trade per day. Entry next 1m open.
- Descriptive: share of event days whose whole range stays inside [VAL, VAH], versus the same share for days that open outside (the quote's "stay inside").

R11 (`9IliXww64uM`; quote "What happens to the volume when we break out? Do we have a dry up in volume immediately? No. We have a lot of volume in this" SOURCED):
- Same prior-day value area as R5; 15m bars, UTC-aligned, built from the 1m bars.
- Breakout bar = the first 15m bar of the UTC day whose close is above VAH (up) or below VAL (down) while the previous 15m close was inside [VAL, VAH]; one per day.
- Persistence ratio q = (volume of the next two 15m bars together / 2) / volume of the breakout bar. R11p = q >= 0.5 (OURS: "dry up" = under half); R11d = q < 0.5.
- Trade WITH the break direction; entry = open of the 1m bar after the second follow-up bar closes.

## Outcomes, placebo and pass bar
Per arm: n, mean net %, sd, t = mean / (sd / sqrt(n)), share positive, mean in each half, mean by year and by long/short via `backtest/trade_sanity.py year_side_lines`, `Regime mix:` of the events. Floor: DEV n >= 180, else INSUFFICIENT_N and no verdict (OURS, from the gate).
Placebo (direction matched): 500 draws, seed 1; per draw, as many entry minutes as events, sampled uniformly from DEV candidate minutes (R8: hourly closes; R5, R11: every 5th minute) with the same UTC-hour histogram, signed with the same long/short count (shuffled), passed through the same 60-minute de-clustering, mean net. Reported: placebo mean, 1st and 99th percentile, and the percentile rank of the arm mean (share of placebo means <= arm mean).
PASS (operator bar): mean net > 0 AND t >= 2 AND both halves mean net > 0. Anything else FAIL; n < 180 INSUFFICIENT_N. A PASS is DEV-only, never called an edge, and goes to VALIDATION only by a later card; the placebo percentile is reported beside it (a PASS under 95 is flagged "within placebo noise"). Family m = 5 arms (R8a, R8b, R5, R11p, R11d).

## Gate (measured, outputs pasted)
sd of 60-minute closes DEV: 0.574 % (20,424 returns, whole-bar price statistic).

    prereg_gate.py --n 180 --sd 0.574 --cost 0.10 --m auto --new-cells 5 --sd-source "PREREG.md sd of 60m closes DEV"
    n 180 sd 0.574 m 253 z_holm 3.722 MDE 0.195 R + cost 0.1 = 0.295 vs max plausible gross 0.3; n needed 171
    PASS: may freeze

(At a 240-minute horizon, sd 1.118, n 300 the same gate printed BLOCK; that is why the horizon is 60 minutes.)
verdicts.py check "btc order flow delta extreme value area breakout volume": no prior row matches; safe to pre-register.

## Checks to run with the code
test_rules.py: each rule gets a synthetic case that fires, and a deliberately wrong rule (flipped side, flipped extreme, value area from the same day) that must fail; lookahead_lint.py must pass for the folder; verdicts.py backfill is never run and VERDICTS.csv is never hand-edited.
