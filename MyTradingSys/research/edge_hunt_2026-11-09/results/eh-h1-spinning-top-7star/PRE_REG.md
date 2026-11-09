# PRE_REG: eh-h1-spinning-top-7star (trial T01)

Frozen before any return is computed. Card: edge-hunt-plan-opus-1109 (planner). Worker: Haiku 5.5, wave 1.
Trial list: MyTradingSys/research/edge_hunt_2026-11-09/TRIALS.md (T01). Shared rules: PLAN.md s5.
Labels: SOURCED = quoted source; OURS = our choice, fixed here, never tuned on outcome.

## Hypothesis
Malkan calls the spinning top a 7-star setup: "seven star means high probability ... ten seven star signals nine of them will work", RR "1 is 2 10 20 30" (SOURCED: XFO49JlODxI_raw.txt:8, quoted in malkan_level_shorts_2026-11-09/SEVEN_STAR_CAPTIONS.md s2.1).
Narrow mechanical question: coded literally, does the rule fire often enough, and is the fee-net mean R > 0 at a 3R target with a 20-bar time stop, both sides pooled (T01)?

## Rules (frozen)
| Item | Rule | Label |
|---|---|---|
| Body | abs(close - open) <= 0.25 x (high - low) | OURS ("small body", XFO49JlODxI:8) |
| Shadows | upper shadow >= 0.25 x range AND lower shadow >= 0.25 x range | words SOURCED ("long shadows on both the sides"; "both the shadows equal or not slightly up and down it's okay"); 0.25 OURS |
| Volume | volume >= 2.0 x median volume of the prior 20 bars (bars i-20..i-1, excluding the setup bar) | words SOURCED ("long volume", "significantly higher volume"); 2.0 and 20 OURS |
| Location | long: low_i = min(low over bars i-19..i) (the setup bar is the lowest low of its 20-bar window incl. itself); short: high_i = max(high over bars i-19..i) | words SOURCED ("at major top or bottom"); 20 bars OURS |
| Range | range > 0 required | OURS |
| Colour | ignored ("the color of the body is not important") | SOURCED |
| Sides | a bar that meets both location tests (range expansion both ways) produces both a long and a short candidate; each side is a separate trade under the one-position rule | OURS |
| Entry | buy stop 1 tick above the setup high (short: 1 tick below the setup low), live for bars i+1..i+3, else no trade ("buy above the high") | SOURCED trigger; 3 bars OURS; tick = 0.01 price unit (Binance spot BTCUSDT and ETHUSDT tick) OURS |
| Entry fill | fill at the trigger price, or at the bar open if the bar opens through the trigger (gap) | OURS (standard stop-order fill) |
| Stop | setup low for longs, setup high for shorts ("stop loss below the low") | SOURCED |
| Target | 3R from the fill (R = fill - stop for longs) | OURS (his 1:10+ is reported as descriptive MFE share) |
| Time stop | 20 bars counting the fill bar; exit at that bar's close (taker) | OURS |
| Same-bar tie | stop wins over target; if the fill bar also breaches the stop, the trade is a stop-out | SOURCED convention (PLAN s5) |
| Position rule | one open trade per symbol and timeframe at a time; setups while a trade is open are skipped (counted) | OURS |
| Fees | regime A: taker 0.0005 per side on every leg (fees.py DERIBIT_TAKER = BINANCE_TAKER) = 10 bps round trip, plus 2 bps round-trip slippage = 12 bps; fee_r = 12 bps / stop distance in bps | SOURCED fees.py; slippage SOURCED FORMULAS s13 via PLAN s5 |
| Funding | sum of fundingRate records with calc_time in (fill, exit]; funding_R = side_sign x sum(rate) / stop fraction, side_sign = +1 long (pays when rate > 0), -1 short. Spot-history trial: the perp fundingRate archive is applied where it exists (from 2019-09), 0 before, as PLAN s5 says | PLAN s5 (sign convention OURS, stated) |
| Net R | net R = gross R - fee_r - funding_R | PLAN s5 |
| Gross R | (exit - fill) / (fill - stop) for longs, mirrored for shorts; stop exit at min(open, stop) for longs when the bar gaps through; target exit at max(open, target) when the bar gaps through | OURS |
| Trial | T01 = both sides, both TFs (4h, 1d), both symbols (BTCUSDT, ETHUSDT), pooled | TRIALS.md |
| Exploratory (no promotion) | per TF, per side, per symbol; MFE distribution in R; share of trades with MFE >= 10R; hit rate vs his 90 % claim | - |

## Data and splits
- Source: Binance spot klines 4h and 1d, BTCUSDT and ETHUSDT, from 2017-08 (fetch_binance_archive.py --spot-history). Funding: USD-M fundingRate archive from 2019-09. Cache outside the repo: F:/MTS/Dumps/backtest/eh_h1_spot and eh_h1_fut.
- DEV = open time < 2024-07-01 00:00 UTC (data start 2017-08). Loader refuses any bar at or after 2024-07-01 for DEV.
- VALIDATION = 2024-07-01 .. 2025-06-30, read once, only for a trial that passes the DEV screen. The loader refuses any end past 2025-07-01 (splits.VALIDATION_END).
- HOLDOUT = 2025-07-01 onward: never loaded.
- A trade open at a window end is closed at the last bar close of that window (taker), and counted in `open_at_end`. No trade reads bars past its window.
- Indicators and the 20-bar windows use only bars at or before the setup bar. No higher timeframe is used, so no resampling is needed; a test checks no lookahead.
- Spot is not perp: spot has no funding; the archive is applied as the brief says, labelled.

## Statistics and verdict
- SE clustered by ISO week of the fill time (4h and 1d trades). CI = mean +- 1.96 SE. MDE at 80 % power = 2.8 x SE.
- DEV screen: n >= 30 AND mean net R > 0 AND CI lower bound > 0.
- VALIDATION: one-sided p for mean net R > 0 (normal approximation on the clustered SE); Holm at m = 15 applied as the threshold alpha/15 = 0.00333 (DECISION OURS: the most conservative Holm step, since this trial's rank among the wave is not known when it is read).
- PASS = DEV screen passed AND VALIDATION p <= 0.00333 AND VALIDATION mean > 0.
- FAIL = DEV mean net R <= 0 AND DEV CI upper bound < MDE.
- INCONCLUSIVE otherwise.
- A PASS files one raw testnet-forward card; the next step is testnet forward, never a longer backtest.

## Context
- Regime: none as a gate, because the rule is a 1-bar reversal pattern at a 20-bar extreme; the regime is only reported (Regime mix line). Descriptive regime tag from research_kit.regime_tag on weekly and monthly RSI14 and the daily SMA(14); OURS.
- Phase: none, because the trader's rule names no phase; reported descriptively per year.
- Session: none, because the rule is on 4h and 1d bars.
- Entry: signal bar i closes the setup; buy stop above its high (sell stop below its low) live for 3 bars; no retest.
