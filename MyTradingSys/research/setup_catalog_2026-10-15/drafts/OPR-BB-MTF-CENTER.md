# DRAFT catalogue row OPR-BB-MTF-CENTER: BB(20,2) centre line on the 30m and 1h charts decides direction, confirmation or range (2026-10-15)

Status: DRAFT in its own file; `SETUP_CATALOG.md` is NOT edited. G0-G2 draft only: nothing here has passed G3, no backtest was run. Not a Tom/Fabio/Malkan/Krown setup: an operator reading of the Bollinger picture on higher timeframes. Every parameter is OPERATOR (his words) or OURS (G5 variant, decided on DEV, never called his). No trader quote is used in the row itself; the Krown range concept it is compared with is in `KRW-RANGE-BB-MAP.md`. Operator text: `../sources/OPERATOR_2026-10-15_bb_mtf_center.md` (relayed paraphrase). Data checks: `../evidence/bb_mtf_center_checks.py` + `_output.txt` (our Binance 1m klines aggregated to 30m/1h, the forming bar included as the chart legend does). Siblings: `MAL-BB-RSI-4060.md` (rows A-C, BB with RSI 40/60), `MAL-BB-MID-ENGULF.md` (5m midline rejection).

### OPR-BB-MTF-CENTER Higher-timeframe BB centre line: closes around it decide direction, confirmation or range
1. **Name / trader.** Operator reading (OPERATOR). It moves the sibling `MAL-BB-MID-ENGULF` midline idea from 5m to 30m/1h and says what the closes around the line mean. Nothing from Tom, Fabio, Malkan or Krown says this; Malkan's multi-timeframe principle (sibling draft Q4) has no intraday numbers.
2. **What you see.**
   - 30m (OPERATOR, B1): candles close around the centre line and the selling pressure eases, so price can try for the upper band. Our data: the 30m bars 10:00 to 13:30 all closed BELOW their own BB mid (mids falling 81196 -> 80991; the 13:30 bar closed 80164.5), then the 30m 14:00 bar closed ABOVE its mid (close 81133.2 against mid 80980.5) and the forming 14:30 bar stayed above it (14:39Z: 81449.9 against 80975.0). "Around the centre line" is NOT STATED (a distance, a count of closes).
   - 1h (OPERATOR, B2): when the centre line is hit, the closes above or below it decide direction, confirmation or a range. Our data: the 13 closed 1h bars from 01:00 to 13:00Z all closed below their own BB mid and none of their wicks reached it (highs 81893.8, 81775.1, 81514.4 ... 80743.5 against mids 82293 down to 81273); the 14:00 bar is the first wick to reach its mid in that run (high 81390.5 at 14:10Z against mid 81245-81262).
   - Live instance (OPERATOR, B3, about 14:30Z), against our klines: matched at 14:32Z with the forming bars: 30m mid 80952.7 (operator 80,952), 30m upper 81635.9 (81,636), 30m last 81002.8 (81,001), 1h mid 81239.3 (81,240), 1h upper 82162.3 (82,162), 1h high 81390.5 (81,390). The 1h "last 81,026" is 23 points off our 1m close at 14:32 (81002.8) and 6 points off the 14:31 close (81032.2): the chart reads the live tick, our legend the last closed 1m (same reason as in the sibling drafts). So the picture of B3 is reproduced; the number 81,026 is not an exact match.
   - What happened next (one instance, after the fact): by 14:35 the 1m close was 81227.2 and by 14:39 81449.9, with the 14:30 30m bar high 81471.3: the 1h bar (not yet closed, it closes at 15:00Z) moved from below its mid (81,239) to above it (81,262 at 14:40). The operator's reading at 14:30 was therefore "below the mid, undecided"; the decision candle is the 15:00 1h close. NOT known at the time of writing.
   - Link to the other 2026-10-15 rows: the 14:10Z high 81390.5 that wicked the 1h mid is the squeeze bar of `OPR-WEEKLY-LOW-ROUND-SWEEP.md` (top 81146.6 broken at 14:10) and `OPR-PREOPEN-TOPS.md`; one move, three readings.
3. **Entry, stop, target, management.** NOT STATED. The operator describes how to read the picture, not a trade. Nothing filled in. Illustration only: none.
4. **Context.** Trend context for the row: a lower-band trend (the 1h run of closes below the mid, above). The 5m rows (`MAL-BB-RSI-4060`, `MAL-BB-MID-ENGULF`) sit inside the same 13:30-14:30Z move and are not independent of this instance.
5. **BTC visibility: YES.** Bars, BB(20,2), 30m and 1h aggregation: from 1m klines (archive plus the fapi top-up for 2026-10-15). "Selling pressure eases": taker delta and CVD from klines (`taker_buy_volume`), RSI from klines. OI: only the 1m recorder (from 2026-10-05, sparse) and the fapi 5m history; OI is a covariate, not a requirement.
6. **Evidence.** 1 instance (2026-10-15 14:00-15:00Z 1h bar, still forming at the time of writing), same day and downtrend as the sibling rows (not independent). No ledger trade.
7. **Gaps.** "Hit" the centre line: a wick touch, a close, within x of the mid: NOT STATED. "Around the centre line": NOT STATED. "Selling pressure eases": by which measure (delta, CVD, RSI, candle size): NOT STATED. "Lower-band trend": NOT STATED. Horizon: the operator says the next 1-4 hours as the study window only, not as a trade holding time. Whether a 1h close above the mid but below the upper band is "confirmation" or "range": NOT STATED. Two statements pull different ways: B1 says closes around the centre can lead to the upper band, B2 says the closes decide direction, so the 30m centre-close is a condition on the 1h outcome, not a separate rule; the G5 card tests it as such.

## Parameter table (every parameter labelled)

| parameter | value or definition | label |
|---|---|---|
| BB | 20 closes, 2 population SD (the chart legend), mid = SMA20; forming bar included live, closed bars in the study | OPERATOR (BB(20,2)), OURS (population SD, as reproduced) |
| the mid on the 1h and 30m charts is the decision line | read the closes relative to the centre line | OPERATOR |
| lower-band trend (precondition) | at least N consecutive closed 1h bars close below their own BB mid (grid N = 3, 6, 12) AND the 1h mid is lower than 6 bars ago; this instance N >= 13 (the evidence table starts at 01:00Z) | OURS |
| touch of the mid | 1h bar high >= its own BB mid (wick touch); variant: high within x % of band half-width of the mid (grid x = 0, 10, 25 %); variant: close above the mid | OURS |
| first touch only | the first touch after the precondition is met (later touches in the same run are logged separately) | OURS |
| decision candle | the first CLOSED 1h bar at or after the touch bar's close (the touch bar itself, and the one after) | OURS |
| outcome U, upper | within H hours of the touch bar close (H = 1, 2, 4) price reaches the touch bar's upper band value (fixed level) before the touch bar's lower band value | OURS |
| outcome D, lower | within H hours price reaches the touch bar's lower band value (fixed level) before the upper | OURS |
| outcome R, range | neither fixed band is reached in H hours; sub-report: all closed 1h closes within +/- 0.25 half-widths of the mid | OURS |
| close-side outcome | sign of (1h close - mid) for the first 1, 2, 3 closed 1h bars after the touch | OURS |
| 30m centre-close condition | the last m closed 30m bars (m = 2, 3) closed within +/- y of the 30m mid (y = 0.25, 0.5 half-widths) | OURS |
| selling pressure eases | any one of: 30m taker delta over the last 4 bars >= 0; 30m CVD slope >= 0; 30m RSI14 higher than 4 bars ago (reported separately, not combined; choose on DEV) | OURS |
| controls | the mirror (touch of the 1h mid from below in an up-trend); touches of the 30m mid; random hours in the same trend state; the 1h touch with no precondition | OURS |
| flow covariates | OI change over the touch hour (up / flat / down), taker-delta sign of the touch bar, session (inside 0-60 min after the 13:30Z/14:30Z US open or not) | OURS |
| range regime split | BB width percentile of the touch bar (below / above the DEV median), to compare with Krown's range mode (`KRW-RANGE-BB-MAP.md` test M2) | OURS |

## Outcomes to measure (also on the G5 card)

1. P(U), P(D), P(R) with n and Wilson 95 % CI, unconditional and for the 30m centre-close condition on / off; the close-side outcome tables for the first 1, 2, 3 bars (above / below / mixed).
2. After U and after D: MFE and MAE to +1h, +2h, +4h in ATR(14, 1h) units, long and short measured separately.
3. Fee-net R (METHOD.md fees: taker 5 bp + 1 bp slippage per fill) for two plain rules only if the frequencies show something: long at the first 1h close above the mid, short at the first close below it; stops OURS.
4. Controls as in the table; the mirror case (up-trend touch from below) must be reported next to the main case.
5. The range-regime split and the Krown mapping tests M1-M4 from `KRW-RANGE-BB-MAP.md`, reported as descriptive tables only.
6. Every table prints n and a Wilson interval; a cell with n < 10 is not read.

## G5 study sketch (DEV only, fee-net, NOT run)

DEV days only (LAYERS.md:35 window); holdout sealed; one look at VALIDATION per frozen variant; every (N, touch rule, H, m, y, pressure measure) combination is a ledger row. Expected n: a 1h run of 6 or more closes below the mid followed by a wick touch of it is an everyday event on BTC (tens to low hundreds over the DEV window), but the 12-bar run and the 30m condition cut it fast, so report the tail cells without tuning on them. The card is `MyTradingSys/system/tasks/opr-bb-mtf-center-g5.json` (a 1h/30m aggregation of 1m klines: Sonnet-sized, no heavy event finder).
