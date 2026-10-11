# Tom core backtest phase 2: pivot-anchored volume profile touch study (2026-10-09)

Code: `backtest/vp_pivot_probe.py` (FORMULAS section 18), tests `backtest/test_vp_pivot_probe.py` (26, from the 18.1-18.7 worked
examples; all failed on a stub first). Full table: `phase2/results.md`, raw: `phase2/results.json`. Run time 40 s.
Data: BTCUSDT USD-M 1m klines 2022-01-01 .. 2026-10-07, 2,507,040 rows = 1741 full days, 0 gaps.

## Verdict
No anchor has an edge. Pivot anchoring (A1, Tom's "last major high to last major low") does not beat the calendar anchors
the engine uses, and no family beats its own placebo (a level shifted by 0.5-3 ATR).
- Every one of 48 family x level streams has mean net R below zero (taker: -0.185 .. -0.248 R; maker variant -0.10 .. -0.16 R).
- Gross R is about zero everywhere (-0.042 .. +0.010): hits 35-40%, stops 36-44%, so price touching a
  POC / VAH / VAL is a coin flip at +-1 ATR(1h) barriers. Fees are the whole loss (about 0.19 R per round trip).
- Real minus placebo: 46 of 48 CIs straddle zero; two are significantly WORSE than placebo (prior_day VAH -0.048,
  A1_n5_k0 POC -0.040); none is significantly better. Best point estimate: weekly POC +0.032 (CI -0.003..0.065).
- Every year 2022-2026 is negative for every stream (no regime where it works). Bull/bear/sideways split not run: the phase
  labels have no source.
- All streams have n >= 1055 events, above Tom's 300-event bar. Longest losing streaks 9-22.
- Side table R-5Ljf-7 (prior-day POC vs candle bodies): POC sits inside a median 8.3% of that day's 5m bodies and a median
  0.6 bins (6 USD) below the median body midpoint (IQR -10..+7 bins). So the POC is near the body centre on a typical day but
  with wide spread; this is a measurement, not a trade.

## What it means for the next phases
- Phase 3 (Tom's targets / stops on the "winning anchor") has no winning anchor. A touch alone carries no edge, so any edge
  must come from Tom's confirmations (footprint, finished auction, CVD), which need aggTrades (not on disk).
- NO-SOURCE choices in this run (flagged, not tuned): bin width 10 USD, pivot width n {2,3,5} on 1h, size filter k {0,2},
  R = ATR14(1h), barriers +-1R, timeout H = 48 x 5m, placebo offsets. A different barrier/horizon was not tried on purpose.
- Nothing here changes the live system.
