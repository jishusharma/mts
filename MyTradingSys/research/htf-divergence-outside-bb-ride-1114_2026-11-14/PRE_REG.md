# PRE_REG htf-divergence-outside-bb-ride-1114 (written before any outcome was computed)

Belief tested (operator): divergence outside Bollinger Band on higher timeframes, with confirmation, ridden for the full cycle. Understanding first; pass/fail second.

Data: Binance spot klines (data-api.binance.vision) 4h/1d/1w from listing (BTC/ETH 2017-08, BNB 2017-11, XRP 2018-05, SOL 2020-08); 3d = daily resampled in groups of epoch-day//3 (Binance alignment). Last unclosed bar dropped. Cache F:\MTS\data_cache\binance_spot_htf.
Indicators: BB(20,2) on close, RSI(14) Wilder, WaveTrend (LazyBear n1=10,n2=21, wt1), MACD(12,26,9), SMA20.
Pivots: high[p] > highs of the 2 bars left and the 2 bars right (confirmed at bar p+2 close; signal time = that close; entry = open of the next bar). Previous pivot q = immediately preceding same-type pivot, 5 <= p-q <= LB (LB: 4h 60, 1d 60, 3d 40, 1w 30 bars).
Bearish signal: high[p] > high[q], osc[p] < osc[q], and high[p] > upper BB[p] (variant C: close[p] > upper BB[p], counts only). osc = RSI or WT (separate sets). Bullish = mirror (lows, lower BB).
Confirmations (entry bar = next open after confirm bar): none (c=p+2); backin = first bar in p+2..p+12 closing back inside the band; swing = first bar in p+2..p+32 closing below the lowest low between q and p; macd = first MACD-below-signal cross in p+2..p+12. No confirmation inside window = no trade.
Risk: stop = high[p] (short) / low[p] (long); R = |entry - stop|; skip if R/entry < 0.5% or entry beyond stop. Fee 12 bp round trip (SOURCED fees.py 10 bp + 2 bp slippage), fee_R = 12bp*entry/R. Net R reported.
Exits: opp (opposite same-osc signal, confirm none, exit next open, NO stop = full cycle), opp_stop (same with pivot stop), 2R, 3R (stop first on same-bar tie), trail (close crosses SMA20 against position, exit next open, pivot stop active). Open at data end = marked to last close, flagged.
Stats: n, win rate (net R>0), mean net R, median hold (days), bootstrap 95% CI of mean R (2000 resamples). DEV to 2023-12-31, VALIDATION 2024+. Placebo: same n random entry bars, same direction, stop = extreme of last 6 bars, same exits, 200 draws; report placebo mean R of means.
Phase (known at signal time, daily SMA200 d of that symbol): bull = close>SMA200 and SMA200 rising over 30d; bear = close<SMA200 and falling; base = everything else; n/a before 200d warmup.
Equity curve: BTC, one position at a time, long+short flip on opp signals (confirm none), compounding, 12 bp per trade, per TF and osc; plus long-only and short-only; vs buy and hold.
No parameter tuning after seeing outcomes. All thresholds above are OURS (not the trader's).
