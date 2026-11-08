Verdict: T04=FAIL (DEV mean net R -0.221 +- 0.043 R, n=1150, 95% CI -0.305..-0.136; upper bound below MDE 0.121). VALIDATION not read (DEV screen not passed). No testnet-forward card.

## Answer in plain words
A first-touch sweep-and-reclaim of the prior-day or prior-week high or low, faded from the reclaim close, does not pay after fees on DEV (2020-01 .. 2024-06). Over 1150 first-touch events the mean net is -0.22 R per trade. Before costs the trade is roughly break-even (gross +0.05 R, 36 % hit rate at 2R). Fees take 0.27 R per trade because the sweep extreme is a tight stop. The DEV screen fails, and the frozen rule makes that a FAIL. The 5-week census finding (sweeps add about 13 points, blind wicks no edge) stands: a first-touch filter does not turn it into a fee-net edge.

## Context
- Regime: research_kit.regime_tag (daily SMA side x weekly/monthly RSI band), reported as a regime mix only. Not used as a filter. OURS.
- Phase: none, because the rule is level-based; phase is not a trial split here.
- Session: none, because the levels are UTC day / ISO week; the 4h-block split is exploratory.
- Entry: close of the reclaim bar r (first close back inside the level within s..s+3).

Regime mix: 234 weeks: bull 37 (16%) | bear 0 (0%) | range 132 (56%) | n/a 65 (28%). No bear weeks in DEV, so the bear side of the regime is untested here. The n/a weeks are the RSI warm-up at the start of 2020.

## Data and counts
- BTCUSDT USD-M 15m klines and fundingRate from data.binance.vision, 2020-01 .. 2024-06-30 for DEV. The 2019-09..2019-12 15m monthly files are absent (404), so DEV starts 2020-01-01. Cache: F:/MTS/Dumps/backtest/eh_h3_first_touch (outside the repo, not committed).
- Count pass (events only, no returns, count_pass.csv): first-touch 1150 events over DEV (1000 daily-level, 150 weekly-level); repeat arm 647.
- Censored events in DEV: 0 (no first-touch event within 24 h of the DEV end).
- DEV has 2024-06-30 as the last day; VALIDATION (2024-07-01..2025-06-30) was NOT read.

## DEV results (T04, first touch, both sides, four level types pooled)
| cut | n | hit | gross R | fee R | funding R | mean net R | SE (day-clustered) | CI 95 % | MDE 80 % |
|---|---|---|---|---|---|---|---|---|---|
| T04 all | 1150 | 0.363 | +0.051 | 0.273 | -0.001 | -0.221 | 0.043 | -0.305 .. -0.136 | 0.121 |
| level = daily (PDH/PDL) | 1000 | 0.371 | +0.079 | 0.283 | -0.000 | -0.203 | 0.045 | -0.292 .. -0.115 | 0.126 |
| level = weekly (PWH/PWL) | 150 | 0.307 | -0.136 | 0.206 | -0.002 | -0.339 | 0.109 | -0.552 .. -0.127 | 0.304 |
| side = high (short fade) | 604 | 0.381 | +0.130 | 0.315 | -0.008 | -0.177 | 0.062 | -0.299 .. -0.055 | 0.174 |
| side = low (long fade) | 546 | 0.342 | -0.036 | 0.226 | +0.007 | -0.269 | 0.059 | -0.386 .. -0.153 | 0.166 |

Per year (DEV):
| year | n | hit | mean gross | mean fee | mean net | SE | CI |
|---|---|---|---|---|---|---|---|
| 2020 | 234 | 0.355 | -0.002 | 0.270 | -0.270 | 0.094 | -0.454 .. -0.086 |
| 2021 | 249 | 0.361 | +0.064 | 0.202 | -0.138 | 0.092 | -0.319 .. +0.043 |
| 2022 | 256 | 0.383 | +0.099 | 0.241 | -0.141 | 0.091 | -0.319 .. +0.037 |
| 2023 | 280 | 0.382 | +0.123 | 0.352 | -0.231 | 0.092 | -0.410 .. -0.051 |
| 2024 (H1) | 131 | 0.298 | -0.124 | 0.307 | -0.426 | 0.118 | -0.658 .. -0.195 |

Every year's mean net is negative; no year's CI lies above zero.

## Exploratory (cannot promote)
- By 4h block (UTC, of the sweep bar): block 0 (00-04) -0.099 (n=425), block 1 -0.352 (n=149), block 2 -0.373 (n=137), block 3 -0.295 (n=206), block 4 -0.276 (n=152), block 5 -0.067 (n=81). Block 0 is the least negative cell; it is still negative with CI upper bound above zero, so it is not a candidate.
- Knife flag (fall/rise >= 2 % in 12 bars before the sweep, counter-move < 25 %): knife n=146, mean net -0.212; not knife n=1004, mean net -0.222. The flag does not separate the cells. The knife cell is small.
- Repeat-touch arm (second beyond-episode of the level, first repeat only): n=647, mean net -0.695 (SE 0.083), hit 0.300, fee 0.600. Negative and worse than the first touch. Only a contrast.

## Method check
- Tests: 12 tests in test_first_touch.py, all hand-built bars: daily and weekly levels with no lookahead, approach close equal to the level (not inside), the 3-bar reclaim, stop sweep extreme, stop-wins-tie, 2R target, 96-bar time stop, fee arithmetic (12 bps over stop fraction), funding sign for a short, knife definition, and the split refusal (DEV, VAL, HOLDOUT).
- Failing-first run (before the module existed): `1 error in 0.83s` (collection error).
- Final test run: 12 passed.

## DECISION (OURS) list
1. Data start 2020-01-01: archive 15m files for 2019-09..12 are absent (404). The DEV span is 4.5 years, not 4.8.
2. Fee regime A (5 bps per side taker, FEES) plus 2 bps round-trip slippage = 12 bps round trip (FORMULAS s13 slippage). Both market entries and stop exits use taker.
3. Funding from the archive over (entry close, exit close]; side sign +1 long, -1 short; a short receives positive rates.
4. Time stop = close of bar r+96. Stop checked before target on the same bar.
5. Holm first step 0.05/15 used as the VALIDATION gate (not run, since DEV failed).
6. Level windows: a day level is active on day D; a week level from Monday 00:00 to the next Monday. Partial prior periods are skipped (none in the count).
7. Knife flag (exploratory): 12-bar window, 2 % minimum move, 25 % counter-move limit. OURS, not tuned.
8. Regime mix: research_kit.regime_tag fed with closes and Wilder RSI14 computed from the same bars (weekly and monthly closes). OURS.
9. DEV censoring: 0 events dropped (none within 24 h of the DEV end).
10. The DEV screen decision was made on the frozen rule; no parameter was tuned after seeing the result.

## Noticed
- The data cache sits on F:/MTS/Dumps (outside the repo). The worktree is C:/Users/E-ngineers/IdeaProjects/mts-jis-nb-eh-h3-first-touch-sweep.
- The "Verdict: " first line and the Regime mix line are as the done check requires.
- The DEV FAIL means the VALIDATION read is not spent. A future re-test on a new span would be a new trial, not this one.
