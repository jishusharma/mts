# PRE-REG: market-wide capitulation breadth event (edge6-capitulation-breadth-1113)

Written and committed before any outcome is computed. Only the universe (listing date + 90-day volume rank) and the BTC daily regime mix were computed first.

## Hypothesis
Six single-coin studies of "4h RSI extreme, next candle up = long" failed, and in each the profit sat in a few market-wide capitulation days (best 5 days = 240-590 % of total R). So the per-coin signal may be noise and the market-wide event (many coins oversold together) the real signal. Test the event directly: breadth B(t) = share of the universe with 4h RSI(14) <= 25.

## Context
Regime mix: BTC daily close vs 200d SMA (bull > +5 %, bear < -5 %, else range), 2021-01-01..2026-11: bull 49 % / bear 38 % / range 13 %; 2024-01-01..now: bull 56 % / bear 29 % / range 15 %.
Phase: capitulation / forced-selling washout, long the rebound; any regime (regime split descriptive only). Session: any (24h). Entry: close of the confirm 4h bar (market, taker). Closed bars only; the still-forming bar is dropped; B at bar t uses only bars <= t; a coin counts in B only from the bar its RSI(14) is defined (its listing + 15 bars); B is NaN while fewer than 10 coins are defined.
Regime: none as a gate, because the study pools all regimes; BTC daily close vs 200d SMA mix is reported and the regime split is descriptive only.
Session: none, because 4h bars, any hour (24h market).
Entry: breadth B = share of 60 coins with 4h RSI14 <= 25; event when B >= 30 %/50 % after 30 quiet bars; entry at the close of the first confirm bar (B falls back and BTC closes up) within 3 bars.
(Context lines restated at ship 2026-11-14 from this file and the study code, after the run; no rule was changed.)

## Universe (fixed now)
Source: data-api.binance.vision public spot 4h klines (USDT quote). Candidate list = 93 well-known crypto tickers written in fetch.py (explicit crypto-only: no stock/ETF/commodity tokens, no stablecoins, no wrapped/staked tokens). Rule (OURS): first 4h bar on or before 2021-12-31 (history from 2021 or earlier), still trading (last bar within 7 days of the newest), rank by quote volume of the last 90 days, top 60. Computed by universe.py:
BTC ETH SOL ZEC XRP NEAR BNB DOGE UNI TRX LINK ADA AVAX LTC AAVE XLM HBAR BCH DASH FIL DOT ICP ONE CAKE SAND CRV SHIB AR RUNE ALGO ETC RLC ATOM GALA BAT AXS VET ENS ONT CHZ COMP GRT XTZ SKL ZIL IOTA ENJ RVN CVC DYDX EGLD SUSHI CELR MANA KAVA HOT THETA FLOW NEO CTK.
Survivorship limit: only coins STILL TRADING in Nov 2026 are in the set (EOS, FTM, WAVES, OMG, XEM, REEF, ALPHA, SXP, OCEAN and others that ended are excluded), and the rank uses current volume. That flatters buy-the-dip results (coins that kept falling to delisting are missing) and biases B downward in crashes; every result is an upper bound.

## Rule
- B(t): as above, threshold 25 (RSI). EVENT = first 4h bar with B >= T after at least 30 consecutive bars (5 days) with defined B < T. T in {30 %, 50 %}.
- ENTRY = first bar j in event+1..event+3 where B[j] < B[j-1] (B falls back) AND BTC close[j] > BTC close[j-1]. No such bar = no trade (event still listed). Entry price = close of bar j.
- Baskets: (i) BTC only; (ii) top-10 coins by trailing 30-day (180 bars, through bar j) quote volume among coins with a price at j, equal weight.
- Exits: H12 hold 12 bars (2 d); H42 hold 42 bars (7 d); STOP2R: stop = lowest BTC low over bars event..j (the event window), target = entry + 2R on BTC (R = BTC entry - stop), cap 42 bars; triggers read on BTC bars after j (stop first on a bar; gap fills at min(stop, open)); BTC exits at the stop/target price, top-10 coins exit at the close of the trigger bar; time cap = close of bar j+42.
- Cost per coin: 2 x fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13 (imported, SOURCED fees.py) = 12 bp round trip, subtracted from each coin's return. No funding (spot).
- Event return = equal-weight mean of coin net returns (a coin delisted before exit exits at its last close).

## Cells (EXACTLY 12)
T {30 %, 50 %} x basket {BTC, top-10} x exit {H12, H42, STOP2R}. Nothing else is tested; no tuning.

## Splits
DEV: event bar to 2023-12-31. VALIDATION: event bar from 2024-01-01. The unit is the event.

## Pass rule (per cell; ALL must hold)
1. VALIDATION n events with a trade >= 12 (fewer = UNDERPOWERED, not pass). 2. VALIDATION fee-net mean return per event > 0 with a 95 % bootstrap CI (10000 resamples of events) lower bound > 0. 3. DEV mean has the same sign (> 0; DEV n reported; if DEV has 0 trades the cell cannot pass). 4. Placebo (a): for each VALIDATION event a random 4h entry bar in the same calendar year, same event-window length, same basket/exit rule, 1000 draws of the whole set; p = (1 + #draws with mean >= real)/1001 <= 0.05. 5. Placebo (b): same events entered at the EVENT bar close (event-window = event bar only for STOP2R) with the same basket/exit; diff = mean(confirm entry) - mean(event-bar entry) over events that have a confirm; must be > 0. 6. Benjamini-Hochberg 10 % over the 12 cells on the one-sided bootstrap p (share of resampled means <= 0) of VALIDATION; the cell must be rejected. Verdict PASS / FAIL / UNDERPOWERED.

## Descriptive only (not gates)
Event table: every event date with B, BTC drawdown from its 30-day high (close vs max high of the prior 180 bars), 2-day and 7-day (12 / 42 bars) gross basket returns from the entry (BTC, top-10) or from the event bar close when no confirm; worst event; max adverse move (lowest low vs entry within 42 bars, BTC and top-10 mean); whether 2026-11-13 qualified.

## Parameter labels
RSI period 14 and Wilder smoothing: SOURCED (standard). RSI threshold 25, B thresholds 30 %/50 %, 5-day quiet period, 3-bar confirm window, "B falls back" = B[j] < B[j-1], BTC-up confirm, 60 coins, top-10 by 30-day volume, hold 12/42, stop/2R, 42-bar cap: OURS (operator's brief; none is the trader's). Fees/slippage: SOURCED (fees.py).

## Limits stated now
Few events (power low by construction); survivorship (above); spot klines, long only; 4h bar cannot resolve intrabar order (stop-first is pessimistic); the 12 cells share the same events so are strongly correlated (BH is conservative-ish but not independent); the period is bull-heavy; USDT-pair prices include tether basis.
