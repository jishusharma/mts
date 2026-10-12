# Q33 matrix report (2026-10-12, JIS-NUC): nothing survives

Pre-registration: `PRE_REG_Q33.md` (frozen before the run). Runner: `matrix_q33.py`. Cells: `MATRIX_CELLS.csv`; summary: `MATRIX_SUMMARY.json`.
Data: BTCUSDT perp 1m klines 2022-01-01..2026-10-11 (2,512,800 bars, 0 gaps) from data.binance.vision, resampled to 15m.
Cost: both legs taker (`FEES_ALL_TAKER`), 0.10 % round turn, no stop/target, entry open t+1, exit close after H bars.

## Verdict
**No cell survives.** 336 cells were built, 186 had n >= 300 and were tested at the primary horizon (60 min), 89 were
underpowered (n 20-299, reported, not judged), the rest had n < 20. Survivors (n >= 300, BH-FDR q <= 0.05 on placebo p,
net mean > 0, same sign in both halves): **0**. The smallest q is 0.62.

| trigger (variant) | events | all-filter net mean at 60 min, long / short | reading |
|---|---|---|---|
| T1 BB-outside, continuation | 8,689 | -0.091 % / -0.103 % | fee only; gross about 0 |
| T1 BB-outside, fade | 8,689 | -0.097 % / -0.109 % | same |
| T2 LVN traverse, continuation | 1,491 | -0.104 % / -0.115 % | same |
| T2b LVN reject, fade | 1,275 | -0.102 % / -0.114 % | same |
| T3 FVG first test, hold | 19,282 | -0.090 % / -0.093 % | same |
| T3b FVG second test, through | 8,427 | -0.109 % / -0.100 % | same |
| T4 sweep-void, continuation | 1,870 | -0.102 % / -0.097 % | same |

Median gross edge across the 186 tested cells at 60 min: +0.0003 %. Every trigger is a coin flip before fees and a
0.1 % loss after fees. 0 of 186 cells have a positive net mean at 60 min; 3 are positive at 240 min (best +0.039 %,
`T3b_through short F1=UP`, p 0.038, q 0.62, first half -0.034 %, second half -0.071 %, so not stable).

## What this says about the idea
- Price outside the Bollinger band, entering an LVN, or testing a gap does not move fast enough, in either direction and
  with any of the tested direction/momentum/squeeze/volume/RSI states, to cover a 0.1 % taker round turn on BTC at 15m to 4h.
- The context filters change the sign of the (tiny) gross edge in a few cells but never by more than the fee, and
  the apparent winners (smallest p) are the cells whose losses were smaller than the placebo, not positive cells.
- This confirms the earlier single-indicator failures. It is not a verdict on Tom's or Fabio's own trades: their edge is
  management (breakeven, add, trail, 1:5 to 1:19 winners), which a fixed-horizon forward return cannot show.

## Limits (what this test cannot say)
1. F4 open interest, F5 long/short ratio, F6 funding were NOT_IN_DATA on this machine (only klines were fetched). Those cells are not run.
2. T4b (sweep reject) and T5/T6 (frozen Tom / Fabio v3 events) were not run, so the descriptive Tom/Fabio agreement tag is not reported.
3. Detection is on 15m closes. 1m detection of LVN traverse and sweep (the catalogue's N=15 1m window) could fire earlier
   and is not covered; a 1m re-run with stops/targets and maker entry is the only branch left that is not already excluded.
4. 1h ATR for the LVN bin width is 2 x ATR(14, 15m), a stated shortcut.
5. Taker both ways is the pessimistic cost. With a maker entry (FEES_DERIBIT) the round turn falls but the gross edge is
   about 0, so maker fees would not change the verdict for a fixed-horizon exit.
6. Placebo p-values have resolution 0.001; survivor rule was fixed in advance.

## Decision for Q34
Skip: no combination survived. Record "no combination survived (Q33, 2026-10-12)". The Tom/Fabio cross-guidance wiring
and the "Tom is never filtered" ruling are not needed.
