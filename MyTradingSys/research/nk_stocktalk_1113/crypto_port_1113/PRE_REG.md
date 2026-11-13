# PRE_REG: NK StockTalk RSI / Hilega Milega ideas ported to crypto perps (edge-nk-rsi-hilega-1113)

Written and committed BEFORE any rule outcome is computed. Code: `study.py` (written after this commit).

## Hypothesis
Nitish Kumar (NK StockTalk, Indian index trader) claims (a) a 15m RSI(14) in the 70 or 30 zone during the last 30 min of the session predicts a gap up / gap down at the next open, (b) the "Hilega Milega" RSI-average state on 10m/5m/daily gives direction. Null: after 10 bp round-trip fees none of these ports has a positive fee-net mean on crypto perps.

## Context
Source: `nk_stocktalk_1113/flash_deep/cmH38Uo4sYM/EXTRACT.md` (RSI 14, 15m, zone 70/30, window 3:00-3:30 PM, confirm on 10m/5m, trail stop = candle low; "index only, not commodities or stocks, there the story is different") and `JLcDdrHkB5M/EXTRACT.md` (Hilega Milega formula NOT_STATED; weekly/monthly trend, 10m intraday). His rule is explicitly for cash-index gaps. Crypto perps trade 24/7 so there is no close and no gap: the whole port is OURS and the mechanism (overnight gap from closed-market news) is absent. Prior: low. This is a falsification test; a FAIL is the expected result.

## Regime mix:
DEV BTC +832% (51% up days, 52% of days above SMA200); VALIDATION +70% (52% up days, 70% above SMA200, bull-leaning); RECENT -32% (49% up days, 41% above SMA200, bear-leaning). Computed on BTC daily closes only, before any rule was run (`study.py --regime`).

## Data
Bybit v5 public linear 5m klines, 10 USDT perps: BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX, from 2020-01-01 or listing. 10m/15m/1h/1d bars are resampled from 5m in UTC (bar stamped by open time, usable only after close). Cached in `runtime_data/edge-nk-rsi-hilega-1113/` (ignored). Fetch: `fetch.py`.

## Splits
DEV 2020-01-01..2024-06-30, VALIDATION 2024-07-01..2025-06-30, RECENT 2025-07-01..now. Split = entry timestamp. DEV is only descriptive; verdict is VALIDATION. No parameter is tuned on any split (every parameter is fixed here).

## Indicators
- RSI(14), Wilder smoothing (alpha 1/14), on closes. SOURCED length 14 ("14 पीरियड की आरएसआई 15 मिनट", cmH38Uo4sYM 14:45).
- Hilega Milega (OURS-EXTERNAL, unverified, the widely published version; NK never gives the formula, both extracts say NOT_STATED): RSI(9) Wilder; fast = EMA(3) of RSI; slow = WMA(21) of RSI. BUY state = fast > slow AND RSI(9) > 50; SELL state = fast < slow AND RSI(9) < 50; else NEUTRAL. Flip to buy = state not-BUY on previous bar and BUY on this bar.
  This is a Hilega-style proxy; a FAIL says nothing about his exact chart settings.

## Rules (all fixed)
Fees: round trip = 2 * `fees.BINANCE_TAKER` (10 bp) on every trade (regime A-like all-taker); no slippage added. Fee-net return = direction * (exit/entry - 1) - 2*BINANCE_TAKER. Entry always at the close of the bar that gives the signal (known then), exit at the stated bar's close/open (no look-ahead).

R1 Session-close RSI extreme. Event times E (OURS ports, crypto has no close): E1 = 00:00 UTC, E2 = 20:00 UTC (US cash close, winter), E3 = 21:00 UTC (US cash close, summer). Window = the two 15m bars closing at E-15m and E (his "last 30 min", SOURCED 3:00-3:30 PM). Signal: 15m RSI(14) >= 70 on either close = UP, <= 30 on either close = DOWN (his "70 or 30 zone"; the >=/<= edge is OURS). Trade at E, hold h in {1h, 4h, 8h} (OURS; his gap is next open, no crypto equivalent), all 7 weekdays (OURS; he is Mon-Fri).
  Variant CONT: UP -> long, DOWN -> short (his gap logic). Variant REV: mirrored (UP -> short, DOWN -> long).
  Cells: 3 E x 2 variants x 3 h = 18. Pooled over the 10 symbols.

R2 Hilega state flip with daily filter. TF in {10m, 15m}. LONG entry at the close of the TF bar where state flips to BUY while the daily state (last COMPLETED daily bar, same definition on 1d bars) is BUY. SHORT mirrored (flip to SELL, daily SELL). Exit: the TF bar where the state flips to the opposite state (SELL for long, BUY for short; OURS reading of "hold until the state flips back"), exit at that bar's close. Stop: low of the signal candle for long (high for short), checked on the TF bars after entry (bar low/high); fill at the stop price, or the bar open if it gaps through (stop distance is NK's, "low of that day's candle... trail" is a trail we do not port, OURS = fixed stop at signal-candle extreme). Cells: 2 TF x 2 sides = 4.

R3 Confirm combo. R1 signal AND the 5m and 10m Hilega states at E (last completed bars) both equal BUY (for UP) or both SELL (for DOWN). Same E, h, CONT/REV grid as R1: 18 cells. (REV is reported but his claim is CONT.)

R4 Daily trend change. LONG: daily Hilega BUY AND close > SMA(20) (SMA 20 OURS, from the brief) OR last completed weekly candle is a bullish engulfing (weekly body engulfs prior weekly body, green over red; OURS definition) -> enter at that daily close when the condition turns true (false the day before); exit at the close of the first day the daily state is SELL (SOURCED idea "exit on sell state", params OURS). SHORT mirrored (daily SELL AND close < SMA20, or bearish engulfing; exit on daily BUY). Cells: 2.

Total cells per split: 42.

## Metric, tests, pass rule
Primary metric: mean fee-net return per trade (pooled across symbols), per cell per split. 
CI: block bootstrap over trades, blocks = calendar weeks of entry (trades in the same week resampled together, handles cross-coin and overlap clustering), 4000 draws, 95% percentile CI; one-sided p = P(bootstrap mean <= 0).
Placebo (same period, same symbol, same trade durations and directions): each trade's entry moved by a uniformly random shift of 3..60 days (wrapping inside the same split), holding duration and direction fixed, stop ignored; 500 draws of the pooled fee-net mean. Beat placebo = observed mean above the 95th percentile of the placebo means.
BH: Benjamini-Hochberg at 10% over the p-values of all 42 VALIDATION cells (the only family that decides).
PASS (per cell) = VALIDATION n >= 30, fee-net mean > 0, bootstrap 95% CI lower bound > 0, beats placebo, and survives BH 10%. UNDERPOWERED = n < 30. Else FAIL. RECENT is reported as confirmation only; DEV is descriptive. A cell passes the program only if it is also fee-net mean > 0 in RECENT. A single-rule verdict = PASS if any of its cells passes, UNDERPOWERED if all cells with a positive mean have n < 30, else FAIL.
Per-symbol breakdown of VALIDATION is reported for any cell with mean > 0.

## Parameter labels
RSI 14, 15m, 70/30 zone, 3:00-3:30 window shape, 10m/5m/daily timeframes, candle-low stop: SOURCED (quotes in extracts). Hilega RSI(9)/EMA3/WMA21: OURS-EXTERNAL. Event times, horizons, SMA20, weekly engulfing definition, exit-on-flip, symbols, fees tier, weekend inclusion: OURS.
