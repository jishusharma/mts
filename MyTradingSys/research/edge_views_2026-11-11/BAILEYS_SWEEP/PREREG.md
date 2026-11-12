# PREREG: Baileysforex sweep -> 15m BOS -> demand retest, WITH the daily trend (written before any result)

Card baileysforex-btc-liquidity-extract-1112, video D-0xTsMPwys. Analyst statements are context, never signals.
This file is committed before any trade of this rule is computed. One rule, one parameter set, no sweep.

## Context
Regime: the daily bias gate (close vs SMA50, long above / short below) is the only regime filter; no volatility or phase gate.
Phase: none, because phase labels were not part of the video rule; DEV spans bear 2022, base 2023, run-up 2024.
Session: none, because the video states no session; all hours trade.
Entry: next 15m bar open after the retest bar closes (market fill).
(Format amendment before any result was read: these four labelled lines restate the text below; no rule changed.)
Source: Baileysforex "Backtesting Bitcoin | Easy Liquidity Strategy": daily bias, 1h swing-low sweep, 15m break of
structure (BOS) plus fresh demand, retest, stop under demand, 1:3 target. The video gives the idea, not numbers: every
number below is OURS unless it carries SOURCED (quote).
Regime mix: DEV 2022-02-01..2024-05-31 (BTC daily close 38,680 -> 67,578, +75 %: bear 2022, base 2023, bull run into 2024);
descriptive count before any trade: 832 DEV days with a 50-day SMA, 51.4 % of them close above it (long side live) and
48.6 % below (short side live). So both sides get about equal days; VALIDATION (2024-07-01 on) is not touched.
Difference from the tested sweep fade (TESTED_MAP T04: first-touch sweep-reclaim fade at PDH/PDL/PWH/PWL, -0.221 R, n 1150;
edge_views note: fading a sweep and reclaim at a lost level -0.106 R, n 1,484): that fades a level; this rule trades
WITH the daily trend, only after a 1h sweep of a swing extreme AGAINST the trend, then a 15m structure break back in
the trend direction, and enters on a retest of a demand/supply base. Different trigger, stop (demand base, not sweep
extreme), target (fixed 3R) and filter. Overlap is not zero (both start from a sweep), so it counts as trial ~101.
Trial count: about 100 prior counted studies (TESTED_MAP); a pass needs more than a lucky t of 2 and is not an edge claim.

## Data
BTCUSDT 1m Binance perp, F:/MTS/data/tom_raw/klines/ (2022-01 .. 2024-05 used; 2022-01 only as warm-up). Resampled by
UTC bucket to 15m, 1h, 1d; a bar is usable only after its close. No downloads. Derived data (if any) to D:/MTS_data/baileys_sweep.

## Definitions (long; short is the exact mirror: highs<->lows, up<->down)
- Daily bias: at time t, last COMPLETED daily bar (UTC day) close vs SMA50 of the last 50 completed daily closes.
  close > SMA50 = bull (long only); close < SMA50 = bear (short only). OURS (video: "price was very clearly bullish").
- Pivot (fractal) low on bar series X: low[i] < low of the 3 bars before and the 3 after (strict). Confirmed only at the
  close of bar i+3 (use it from then on, never earlier). Pivot high is the mirror. OURS (video names swings, no n).
- 1h sweep (long): a 1h bar j (j closes at time Tj) with low[j] < latest confirmed 1h pivot low L (confirmed at or before
  j-1's close) and close[j] > L. The sweep low S = low[j]. Window opens at Tj and lasts 24 hours. Needs bull bias at Tj.
  SOURCED (quote): "price kind of took out this area to the left we grabbed these lows price then flipped back bullish on
  the 1 hour". The 24 h window is OURS.
- 15m BOS (long): inside the window, the first 15m bar k (closed after Tj) with close[k] > latest confirmed 15m pivot high H
  (confirmed at or before k-1's close). SOURCED (quote): "we had a grab of those two lows right there 15 minute then actually
  flipped bullish just there ... another breaker structure". Pivot n=3 is OURS.
- Demand zone (long): the 15m bar b with the lowest low among 15m bars from Tj to k (first one if tied). Zone low = low[b],
  zone high = max(open[b], close[b]) (the body top; wick excluded). OURS. SOURCED (quote) only for "we sort of had a sweep of
  that demand 15minute breaker structure you've then got this demand there so if we can get a retest into this area I'd be happy".
  The video draws zones by eye; this is a mechanical stand-in and is not Bailey's zone.
- Retest trigger (long): within 16 15m bars after k (4 h), the first bar r with low[r] <= zone high and close[r] > zone low.
  If any 15m close <= zone low first, or 16 bars pass, the setup dies. Entry = OPEN of the NEXT 15m bar after r (no look-ahead,
  market fill; the video's limit order is not modelled). OURS.
- Stop = zone low - 0.1 x ATR14(15m, simple mean of true range of the last 14 closed bars). The buffer is OURS (the video's
  stop was "tagged ... by a pip", no buffer stated; the extract suggested 0.1-0.2 ATR; 0.1 chosen, lower end, no sweep).
  Risk R = entry - stop; skip the setup if R <= 0 or R/entry < 0.10 % (OURS, fee guard) .
- Target = entry + 3 R. SOURCED (quote): "stops cover in the low and we're going to mechanically Target a one to three".
- Exit: stop or target hit; evaluated on 15m bars starting with the entry bar; if one bar touches both, the STOP counts
  (conservative). Time cap 672 15m bars (7 days), exit at that bar close. Stop/target fill at their price (no slippage). OURS.
- One position at a time; a new setup arms only when flat. Both sides allowed (bias picks the side).
- Fee: 10 bp round trip, net R = gross R - 0.001 x entry / R_dist. Net bp = net R x R_dist/entry x 1e4.

## Sample
DEV only: entries 2022-02-01 00:00 UTC .. 2024-05-31 23:59 UTC. DEV halves split at the midpoint of that span
(2023-03-17 UTC): both halves must be positive. VALIDATION (2024-07-01 on) is not read in this study.

## Placebo (direction-matched)
Same number of trades, same side counts, same stop distance in % and 3R / 7-day rules as the real trades: for each
real trade draw a random 15m entry bar inside DEV (uniform), same direction, same R% and 3R target; fee same. 500 draws,
seed 1; report placebo mean net R (mean of draws) and the share of draws at or above the real mean.
(Long-biased drift is therefore controlled for only through the direction match; the placebo ignores the daily bias.)

## Pass bar (fixed now)
PASS: fee-net mean R > 0 and t >= 2 (t = mean / (sd / sqrt n) over net R per trade) and both DEV halves mean net R > 0.
FAIL: mean net R <= 0. Otherwise INCONCLUSIVE (including n < 30). PASS is not an edge claim: it earns only a
VALIDATION run in a separate pre-registered step and the trial-count correction.

## RESULT.md must hold
n, win rate, mean net R, net bp, t, max drawdown (sum of R, peak to trough), per-year and long/short rows pasted from
MyTradingSys/backtest/trade_sanity.py (log_sanity + year_side_lines), placebo row, verdict in plain words.
