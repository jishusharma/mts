# PRE_REG nk5-session-open-15-10-5-1114 (written before any outcome)

Rule: NK "15-10-5" gap read (video cmH38Uo4sYM, concept nifty-gap-rsi). At the close he reads 15m RSI(14) near 30 (gap up) / 70 (gap down), then 10m and 5m Hilega Milega (HM) to call the next open.

## Context
Operator order: label phase first, test only the phase-matched direction as primary rows; mismatched direction = control rows only.
Phase for UTC day D uses data to the close of day D-1 only (daily bars built from 5m):
- slope = SMA20(close)[D-1] - SMA20(close)[D-6]; ADX(14) Wilder, +DI, -DI on daily bars.
- UP: ADX>=20 and +DI>-DI and slope>0. DOWN: ADX>=20 and -DI>+DI and slope<0. Else RANGE. (thresholds: ADX 20 = operator order; slope window 5d = OURS)
- Matched direction: UP -> long only; DOWN -> short only; RANGE -> long on oversold signal and short on overbought signal (fade both ways). Control: UP shorts, DOWN longs (not gated).
Regime mix: reported in RESULT.md (share of coin-days UP/DOWN/RANGE, DEV and VAL, and trades by phase).

## Universe / data
20 Binance spot USDT coins (BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX EOS XLM ETC DASH ZEC BCH ATOM NEO IOTA VET), 5m klines from 2019 where listed, via data-api.binance.vision, cache F:\MTS\data_cache\binance\<SYM>USDT_5m.npz (array 'a' = t,o,h,l,c,v). 10m, 15m, 1h, 1d resampled from 5m (UTC, left-labelled, incomplete bars dropped).
DEV: signal time < 2024-01-01. VALIDATION: >= 2024-01-01 (gates evaluated here only).

## Signal (one spec, no tuning)
Evaluated at anchor time T using only bars closed at or before T; entry at the 5m open at T.
- RSI14_15m: Wilder RSI(14) on 15m closes. Long touch: min of the last 4 closed 15m RSI14 values <= 35. Short touch: max >= 65. (35/65 = OURS; NK says 'zone of 30/70')
- HM (OURS reconstruction): RSI(9) Wilder; green = EMA(3) of RSI9; red = WMA(21) of RSI9. Buy state: red < green (SOURCED: red below green = buying). Sell state: red > green.
- Long signal: long touch AND 10m HM buy AND 5m HM buy at T. Short signal: short touch AND 10m HM sell AND 5m HM sell.
Anchors (crypto has no gap; mapping OURS):
- NY: NY cash close 16:00 America/New_York (20:00 UTC DST / 21:00 UTC) -> next Asia open.
- UTC: daily UTC close 00:00 -> next 4 hours.
Horizons (time exit at the 5m open at T+H): NY: 2h, 4h, Asia-end (08:00 UTC next day). UTC: 2h, 4h. => 5 rows.

## Stop / cost
- Stop distance S = max(0.5% of entry, 0.6 x ATR14 of last closed 1h bar) (minimum-stop rule, OURS), R = S. Stop checked on 5m highs/lows after entry, filled at stop price (no gap slippage modelled; stated limitation). No target.
- Net R = (signed return - fee)/ (S/entry). Primary fee 12 bp round trip (taker). One pre-registered maker-entry row at 6 bp: row NY-4h. Report fee as fraction of R (mean fee/S) and median S.
- One trade per coin per anchor per day per direction.

## Gates (VALIDATION, primary 12 bp matched rows; PASS needs all)
n>=100; mean net R>0; 95% bootstrap CI lower>0 per trade AND per day cluster (2000 resamples, seed 1); placebo p<0.05 (2000 draws of random same-size entry sets from same coin-days pool, stratified by phase and direction, same stop/horizon/fee); BH q<0.05 over all matched rows (5 rows at 12 bp + 1 maker row; p = day-cluster bootstrap one-sided); mean net R still >0 after removing best 5 trading days (by summed R).
Verdict: PASS only if a row passes all gates; else FAIL with the failing gates per row. Controls reported, not gated.

## Tests
test_study.py: causality test (truncating data after T must not change the signal/phase at T) passes on real code and fails with env STUDY_BUG=1 (look-ahead: indicators read from the bar closing at T+5m and phase from same-day close).
