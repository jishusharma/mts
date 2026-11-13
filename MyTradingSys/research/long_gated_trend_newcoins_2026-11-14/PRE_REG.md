# PRE-REG: long-only BTC-gated trend, gross capped at 1.0x, 60 NEW coins (edge8-long-gated-trend-newcoins-1114)

Written and committed before any return is computed (only the coin list and listing metadata were fetched). Parent: edge7 daily_trend_follow_2026-11-13 (0 of 10 combined long/short books passed on 60 coins; the leads were long-only rules 9 and 10, VAL Sharpe 0.85 each, CI crossing 0, uncapped gross 1.3x-10.8x so drawdowns were unsurvivable). This is a confirmation on coins the parent never saw, with a survivable gross cap. Exactly 2 rules; nothing else is tuned.

## Hypothesis
Following the daily trend LONG ONLY, while BTC is above its 200-day average, earns a fee-and-funding-net positive return on coins other than the 60 where it was found, with the book never more than 1.0x of equity.

## Context
Regime mix (BTC daily close vs 200d SMA: bull > +5 %, bear < -5 %, else range; parent definition): 2024-01-01..2026-11: bull 56 % / bear 29 % / range 15 % (edge6 capitulation_breadth RESULT.md); RESULT.md recomputes it from the BTC data used here.
Market condition the rule needs: a persistent, broad uptrend (BTC bull) in which coins that start trending keep going for days to weeks, so that entering after a strength signal and exiting on trend decay pays more than the round-trip cost. In chop or bear the BTC gate keeps the book flat; in a bull market that reverses sharply the rules give back gains before exit (they act on daily closes, no intraday stop). Without a bull regime and without sustained trends the rule has no reason to work. Session: none (daily bars). Entry: signal on the close of closed daily bar t, fill at the OPEN of day t+1; the forming bar is dropped. Everything at bar t uses bars <= t only.

## Rules (EXACTLY 2; definitions identical to parent rules 9 and 10; code = parent trend_lib.py copied unchanged)
- R9 GATED-TSM30: at each Monday close, long if close/close[-30] - 1 > 0 else flat (the parent's short half is discarded); held to the next Monday close; position exists only while BTC close > BTC 200d SMA (checked every day; resumes when the regime allows). Weight = 0.01 / max(2 x std of last 20 daily returns, 1 %), capped 0.5 per coin, re-sized each Monday.
- R10 GATED-ADX14: long entry when +DI > -DI and ADX(14) > 25 and ADX[t] > ADX[t-1]; exit when ADX < 20 or -DI > +DI; same BTC gate. Weight = 0.01 / max(2 x ATR(14)/entry close, 1 %), capped 0.5, fixed at entry. ADX per FORMULAS.md section 30 (backtest/layers/adx/adx.py).
- BTC gate: BTC spot daily closes from data-api.binance.vision (public spot data, same source as the parent), strict close above its 200d SMA.
- NEW and only change: GROSS CAP. On every day the effective weights across coins are summed; if the sum exceeds 1.0 all are scaled by 1/sum (pro rata). Never levered above 1.0x. The cap acts on the day's weights before costs, so the scale change itself costs turnover (charged). Placebo books are capped identically.
- Order: the parent's gated weights, positive (long) part only, then the cap.

## Universe (fixed now, before any return is computed)
Rule: Bybit v5 linear USDT perpetuals, status Trading, symbolType empty or "innovation" (crypto only: no stock, ETF, commodity or forex contracts), excluding stablecoins and tokenised commodities (XAUT, PAXG, USDC, USDE, ...), excluding every base coin in the parent's 60 (1000-prefixed variants normalised), ranked by CURRENT 24 h turnover (turnover24h, /v5/market/tickers on 2026-11-13); the first 60. Script select_universe.py, snapshot universe_snapshot.json, list in universe.py:

AKE HYPE BARD 1000PEPE ENA INIT SUI ARIA JCT INJ LIT WLD XMR PUMPFUN SOPH ONDO TAO ARB BTW TRUMP ZRO GRAM H PONS BMT FARTCOIN MAGMA TIA USELESS PIEVERSE QNT AERO APT STRK CAP VVV OP KGEN DNA DGAI WLFI SHELL XPL JUP Q IMX ERA ETHFI GRASS MNT ASTER IDOL PLAYSOUT UAI ICNT VIRTUAL WIF BIRB MON RENDER

Price data: Bybit v5 linear daily klines of the same symbols (perp prices, public), from each contract's launch. A coin enters the book on the first bar where its indicators are defined (R9 about 30 bars; R10 about 40 bars; the BTC gate needs 200 BTC days). Many of these contracts launched in 2025-2026, so most of the book exists only in the later part of VALIDATION and some coins never enter; coins in the book per day is reported.
SURVIVORSHIP / SELECTION BIAS, plainly: the list is today's most-traded coins, chosen by current turnover, which favours coins that rallied or became popular recently; delisted and faded coins are absent. Long-side results are upper bounds. Turnover rank today is partly caused by recent price moves, so this is NOT a clean out-of-sample draw of "all coins a trader would have held in 2024".
Also reported, labelled NOT-CONFIRMATION (already seen by the parent): the same 2 capped rules on the parent's 60 coins (parent cache, Binance spot prices).

## Splits
DEV: first day the book exists (BTC 200d SMA defined) to 2023-12-31. VALIDATION: 2024-01-01 to the last closed day (2026-11-12; the forming bar is dropped). Same as parent. Unit = daily portfolio return (fraction of equity, additive curve).

## Costs (same as parent)
Fees: (fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13 / 2) per unit of |change in weight| at each fill (backtest/fees.py, SOURCED). Funding: real Bybit v5 linear funding/history for the symbol, summed over the UTC day; a long weight w pays w x f_d. Where no record exists: flat 0.01 % per 8 h = 0.03 % per day against longs. Return basis: open-to-open, weight on day d = weight set at the close of d-1; the last closed day ends at its close.

## Pass rule (per rule; ALL must hold; VALIDATION unless stated)
1. 95 % bootstrap CI of the mean daily return, day-cluster (10-day moving blocks, 10000 resamples), lower bound > 0.
2. Annualised Sharpe (mean/std x sqrt(365)) >= 1.0.
3. Beats the equal-weight buy-and-hold basket of the same coins (daily mean of open-to-open returns of coins with a price that day, no cost): strategy Sharpe AND mean daily return both higher.
4. Beats a random-entry placebo with the same exposure profile: each trade (maximal run of a coin held) moved to a random start date on the same coin (inside that coin's data), keeping the weight path and duration, with the gross cap, costs and funding recomputed; 1000 draws; p = (1 + #draws with VAL mean >= real) / 1001 < 0.05.
5. Bonferroni over the 2 tests: gates 1 and 4 must clear at 0.05 / 2 = 0.025 (one-sided bootstrap p = share of resampled means <= 0 must be <= 0.025; placebo p <= 0.025).
6. Robustness: VALIDATION mean daily return stays > 0 without the best 10 days, and annualised return stays > 0 without the best 5 coins (by VALIDATION profit).
Verdict PASS / FAIL per rule. A PASS on a list selected this way would still not be a live-profit claim.

## Descriptive (not gates)
Max drawdown (VAL and full), per-year return, trades (VAL), average gross exposure, share of VAL days with any position, DEV Sharpe, coins in book per day, funding coverage, last-90-day sum.

## Parameter labels
Rules, parameters and the BTC gate: copied from the parent, OURS (none is the trader's). ADX 14, thresholds 25/20: SOURCED (Wilder). Sizing 1 % risk, 2 x ATR / 2 x sigma stop, 1 % floor, 0.5 per-coin cap: OURS. Gross cap 1.0x: OURS (survivability, chosen before any result). Fees: SOURCED (fees.py). Block 10, 1000 draws, seed 20261114: OURS.

## Limits stated now
Survivorship / popularity selection (above). Short histories: most coins have well under 2 years of data, so VALIDATION is a thin, mostly 2025-2026 window and a few coins' sudden moves can dominate. Perp prices for the new coins, spot prices for the parent-60 row and the BTC gate. No intraday stops. Two rules, one run, no tuning; no result is read before this file is committed.
