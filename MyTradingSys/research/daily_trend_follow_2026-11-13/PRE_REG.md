# PRE-REG: daily trend-following, long AND short, 60 coins (edge7-daily-trend-follow-1113)

Written and committed before any outcome is computed (only raw data was fetched). 17 earlier studies today were buy-the-dip / mean-reversion and failed after fees; this tests the opposite family: follow the daily trend, hold days to weeks.

## Hypothesis
Crypto daily trends persist (time-series momentum / breakout). A diversified book of per-coin long/short trend positions earns a fee-and-funding-net positive return that beats a buy-and-hold basket and a random-direction placebo.

## Context
Regime mix: BTC daily close vs 200d SMA (bull > +5 %, bear < -5 %, else range), 2021-01-01..2026-11: bull 49 % / bear 38 % / range 13 %; 2024-01-01..now: bull 56 % / bear 29 % / range 15 % (computed in edge6 capitulation_breadth RESULT.md).
Phase: trend continuation, both directions, any regime (rules 8-10 gate by regime). Session: none (daily bars). Entry: signal on the close of closed daily bar t, fill at the OPEN of day t+1 (market, taker). The still-forming bar is dropped. Everything at bar t uses only bars <= t.
Regime: rules 1-7 none (long and short in any regime, regime mix reported); rules 8-10 gated: longs only while BTC close > its 200d SMA, shorts only while below.
Session: none, because daily bars.
Entry: signal on the close of a closed daily bar t (Donchian breakout, 30/90d momentum, ADX/DI, MA stack); fill at the OPEN of day t+1.
(Context lines restated at ship 2026-11-14 from this file and the study code, after the run; no rule was changed.)

## Universe (fixed now)
The 60 coins of edge6 PRE_REG.md, in universe.py (rule there: listing <= 2021-12-31, still trading Nov 2026, top 60 by 90-day volume, crypto-only). Source: data-api.binance.vision public spot daily klines, USDT quote, 2020-01-01 onward; a coin enters the book only from the first bar where all its indicators are defined. SURVIVORSHIP: only coins still trading in Nov 2026 are included (delisted losers excluded) and the rank uses current volume; long-side results are upper bounds, short-side results are lower bounds (coins that died are the best shorts and are missing). Early years hold only ~15 coins.

## Costs
- Fees: 2 x fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13 per round trip (imported, SOURCED fees.py): charged as (BINANCE_TAKER + SLIPPAGE_RT_S13/2) per unit of |change in position weight| at each fill.
- Funding (perps needed for shorts): Bybit v5 linear funding/history (symbol SYMUSDT, else 1000SYM / 10000SYM). Day-d funding f_d = sum of the settlements with timestamp in UTC day d. A held position of weight w (signed) pays w * f_d on day d (long pays positive funding, short receives it; negative funding reverses that). Where a coin-day has no Bybit funding record (before its perp listing or a gap): flat 0.01 % per 8 h = 0.03 % per day charged against LONGS, nothing credited to SHORTS. Coverage (share of held coin-days with a real record) is reported in RESULT.md.
- Return basis: open-to-open daily returns, position weight on day d = the weight set at the close of d-1. The last closed day uses its close as the end price.

## Sizing (OURS, every rule)
Each coin's signed weight w (fraction of equity) = 0.01 / stopdist, where the stop distance is the risk to the rule's own exit level at entry: Donchian = (entry close - exit-channel level) / entry close; MA trend = |entry close - MA20| / entry close; ADX = 2 x ATR(14) / entry close; time-series momentum = 2 x (sample std of the last 20 daily returns) (inverse 20-day volatility, re-sized at each weekly rebalance). stopdist is floored at 1 % and w capped at 0.5. Donchian/MA/ADX weights are fixed at entry for the whole holding. Gross exposure is not capped; average gross exposure is reported. Portfolio daily return = sum over coins of w x coin return - costs (fraction of equity, additive equity curve).

## The 10 rules (EXACTLY 10; nothing else is tested, no tuning)
Positions per coin: long / short / flat, state machines evaluated at each closed daily bar.
1. DON20/10: long when close > highest high of the previous 20 days; exit long when close < lowest low of the previous 10 days. Short mirrored (close < previous-20 lowest low; exit when close > previous-10 highest high). Exit and same-day opposite entry are both allowed.
2. DON55/20: same with 55 / 20.
3. TSM30: at each Monday close, long if close/close[-30] - 1 > 0 else short; held to the next Monday close.
4. TSM90: same with 90.
5. ADX14: long entry when +DI > -DI and ADX(14) > 25 and ADX rising (ADX[t] > ADX[t-1]); short entry mirrored (-DI > +DI). Exit when ADX < 20 or the DI order flips. ADX/DI per FORMULAS.md section 30 (backtest/layers/adx/adx.py).
6. ADX14-3d: rule 5 on 3-day bars (daily bars grouped in blocks of 3 anchored at 2020-01-01, complete blocks only); position changes only at a 3-day block close, filled at the next day's open.
7. MA: long entry when close > MA50 and MA20 > MA50 and close > MA20; short entry when close < MA50 and MA20 < MA50 and close < MA20 (SMA of closes). Exit long when close < MA20; exit short when close > MA20.
8. GATED-DON20/10: rule 1 where a long position exists only while BTC close > BTC 200d SMA and a short only while BTC close < BTC 200d SMA (checked every day; a regime flip closes the position; the state resumes when the regime allows).
9. GATED-TSM30: rule 3 with the same BTC gate.
10. GATED-ADX14: rule 5 with the same BTC gate.
For each rule three books are reported: long-only (positive weights of the combined book), short-only (negative weights), combined. The pass rule applies to the COMBINED book.

## Splits
DEV: first defined day (about 2020-07) to 2023-12-31. VALIDATION: 2024-01-01 to the last closed day (the forming bar is excluded). Unit = daily portfolio return.

## Pass rule (per rule, combined book; ALL must hold)
1. VALIDATION fee-and-funding-net mean daily portfolio return > 0 with a 95 % moving-block bootstrap (10-day blocks, 10000 resamples) CI lower bound > 0.
2. Annualised Sharpe (mean/std x sqrt(365)) >= 1.0 on VALIDATION and > 0 on DEV.
3. Beats BOTH benchmarks on VALIDATION: (a) buy-and-hold equal-weight basket of the same coins (equal weight over coins with a price each day, daily mean of coin open-to-open returns, no cost): strategy Sharpe AND strategy mean daily return both higher; (b) random-direction placebo: same runs (maximal intervals of one sign per coin), same weights and holding periods, each run's direction flipped with probability 1/2, 1000 draws, costs and funding recomputed; p = (1 + #draws with VAL mean >= real) / 1001 <= 0.05. (For the long-only and short-only rows, where a direction flip changes the book, the placebo moves each run to a random start date on the same coin keeping side, weight path and duration; same p.)
4. Benjamini-Hochberg 10 % over the 10 rules on the one-sided bootstrap p (share of resampled VAL means <= 0), combined books; the rule must be rejected.
Verdict PASS / FAIL.

## Descriptive only (not gates)
Max drawdown (additive equity curve, VAL and full), per-year return (sum of daily returns), share of VAL profit from the best 5 coins and the annualised return without them, share from the best 10 days, average holding days, trades per year, average gross exposure, funding coverage, return over the last 90 days.

## Parameter labels
Donchian 20/10 and 55/20: SOURCED (Turtle rules). ADX period 14, thresholds 25 / 20: SOURCED (Wilder). ADX "rising" = ADX[t] > ADX[t-1]; 3-day bars; TSM lookbacks 30/90 and weekly (Monday) rebalance; MA 20/50 rule and its entry/exit wording; BTC 200d gate; sizing (1 % risk, 2 x ATR / 2 x sigma stop, 1 % floor, 0.5 cap); flat 0.01 %/8 h funding fallback; 60-coin universe; splits: all OURS (none is the trader's). Fees/slippage: SOURCED (fees.py). Block length 10, 1000 placebo draws, BH 10 %: OURS (operator's brief).

## Limits stated now
Survivorship (above). Spot prices stand in for perp prices (basis ignored). Equal 1 % risk with no gross cap means total exposure varies; the basket benchmark is 1x gross, so Sharpe is the fair comparison. No intraday stop fills: the rules act on closes. Not a claim about live profitability.
