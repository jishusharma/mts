# EVENT_COUNTS: how many DEV events do KR-S1, KR-S8 and MAL-2/5/16/17 hold, and what effect can they detect? (2026-10-16)

Session `krown-malkan-p6` (Fable P6, CATALOGUE_AUDIT.md). **Counts and geometry only: no forward return and no trade outcome was computed or read.**
Data: Binance spot daily files from `F:/MTS/data/krown_daily` (DATA_COVERAGE.md), cut to bars opened before 2024-07-01 (DEV) before any indicator was built.
Reproduce: `python MyTradingSys/research/krown_malkan_g3_2026-10-16/event_counts.py --data F:/MTS/data/krown_daily --out MyTradingSys/research/krown_malkan_g3_2026-10-16` (full per-asset, per-year table: `event_counts.csv`).

## Answer

- **Enough events on BTC alone (MDE <= 0.30R net):** KR-S1 1d.
- **Too few on BTC alone but MARGINAL when pooled over BTC, ETH, BNB, SOL (MDE in brackets, assumes independent events, so optimistic):** KR-S8 1d (0.35R), KR-S8-high 1d (0.37R), KR-S1 1w (0.39R), MAL-5 1d (0.49R), MAL-17 1d (0.41R), MAL-16 1d (0.35R).
- **Too few even pooled (descriptive reading only, no G5 test):** KR-S8 1w, KR-S8-high 1w, MAL-2 1d, MAL-10 1d, MAL-17 1w, MAL-16 1w.
- No row can confirm a +0.10R net edge: that needs about 1655 independent events. The question G5 can answer is whether a large effect is present, not a small one.

## How to read it

- Every pre-filter is **OURS** (written down before any outcome was looked at); it is a cheap stand-in for the trader's chart reading, not the rule itself. Where a leg of his rule cannot be computed from OHLC alone it is dropped, so the count is an order of magnitude, not a guaranteed upper bound.
- `n` = events after merging events closer than 5 bars on the same side (OURS; neighbours share one move). `bars` = DEV bars in the series.
- Stop geometry is read from the event bar itself (never the future): stop % = distance from the planned entry to the stated stop reference; cost in R = round trip taker fee 0.10% / stop %. Fees are the Deribit taker rate (`fees.py:23`), both sides.
- **MDE** = smallest mean net R per trade the sample could detect with 80% power at a two-sided 95% test, from `MyTradingSys/backtest/power_mde.py` with a +2R / -1R payoff (OURS), variance taken at the break-even win rate. 'Win-rate pp' is the same MDE as extra win rate over break-even.
- `Events for +0.10R` = events needed for 80% power if the true edge is +0.10R net (OURS target). Verdict (OURS): ENOUGH if MDE <= 0.30R, MARGINAL up to 0.60R, THIN above.

## 1. BTCUSDT (the series every row is judged on)

| row | tf | pre-filter (OURS) | bars | n | by year | median stop | cost R | MDE net R | MDE win-rate pp | events for +0.10R | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| KR-S1 | 1d | zone twice-turned (pivot k=3) + hammer/engulf/doji/star, no trend leg | 2510 | 278 | 2017:3 2018:42 2019:47 2020:43 2021:37 2022:41 2023:47 2024:18 | 4.1% | 0.024 | 0.24 | 8.0 | 1655 | **ENOUGH** |
| KR-S8 | 1d | BBWP(13,252) <=30 in last 10, >=50 now, 10-bar range break | 2510 | 29 | 2018:1 2019:4 2020:2 2021:2 2022:12 2023:4 2024:4 | 18.8% | 0.005 | 0.74 | 24.6 | 1644 | **THIN** |
| KR-S8-high | 1d | same + BBWP>=70 in the 60 bars before the compression | 2510 | 26 | 2018:1 2019:3 2020:1 2021:2 2022:12 2023:3 2024:4 | 19.2% | 0.005 | 0.78 | 25.9 | 1644 | **THIN** |
| KR-S1 | 1w | zone twice-turned (pivot k=2) + hammer/engulf/doji/star, no trend leg | 358 | 30 | 2018:3 2019:6 2020:8 2021:2 2022:3 2023:7 2024:1 | 10.6% | 0.009 | 0.73 | 24.2 | 1646 | **THIN** |
| KR-S8 | 1w | BBWP(13,104) <=30 in last 10, >=50 now, 10-bar range break | 358 | 4 | 2021:1 2022:1 2023:1 2024:1 | 87.1% | 0.001 | 1.98 | 66.1 | 1641 | **THIN** |
| KR-S8-high | 1w | same + BBWP>=70 in the 60 bars before the compression | 358 | 4 | 2021:1 2022:1 2023:1 2024:1 | 87.1% | 0.001 | 1.98 | 66.1 | 1641 | **THIN** |
| MAL-2 | 1d | weekly+monthly RSI>60 gate, daily RSI support event at 60 (tol 2) | 2510 | 7 | 2019:1 2020:2 2021:4 | 4.5% | 0.022 | 1.51 | 50.2 | 1654 | **THIN** |
| MAL-5 | 1d | gate, daily RSI close in 58..62, green candle; order over high, stop under 3-bar low | 2510 | 25 | 2019:1 2020:6 2021:9 2024:9 | 6.3% | 0.016 | 0.80 | 26.5 | 1650 | **THIN** |
| MAL-10 | 1d | gate, daily RSI support event at 40 (tol 2) [host 5-star variant, extra] | 2510 | 6 | 2019:3 2021:1 2024:2 | 5.2% | 0.019 | 1.63 | 54.2 | 1652 | **THIN** |
| MAL-17 | 1d | bullish divergence 3-10 bars close to close + confirming candle | 2510 | 35 (of 37 divergences) | 2018:8 2019:3 2020:2 2021:5 2022:9 2023:6 2024:2 | 3.6% | 0.027 | 0.67 | 22.5 | 1657 | **THIN** |
| MAL-16 | 1d | bearish divergence 3-10 bars close to close + confirming candle | 2510 | 42 (of 54 divergences) | 2017:2 2018:2 2019:3 2020:9 2021:6 2022:3 2023:14 2024:3 | 3.6% | 0.028 | 0.62 | 20.5 | 1657 | **THIN** |
| MAL-17 | 1w | bullish divergence 3-10 bars close to close + confirming candle | 358 | 3 (of 4 divergences) | 2018:1 2019:1 2022:1 | 9.7% | 0.010 | 2.29 | 76.4 | 1647 | **THIN** |
| MAL-16 | 1w | bearish divergence 3-10 bars close to close + confirming candle | 358 | 8 (of 9 divergences) | 2019:2 2020:1 2021:2 2023:1 2024:2 | 15.8% | 0.006 | 1.40 | 46.8 | 1644 | **THIN** |

## 2. Pooled over BTC, ETH, BNB, SOL (daily and weekly-from-daily)

Pooling adds events but the four coins move together, so the MDE below is **optimistic** (it assumes independent events). Use it as a floor, not a promise.

| row | tf | n BTC | n ETH | n BNB | n SOL | pooled n | pooled MDE net R | verdict if independent |
|---|---|---|---|---|---|---|---|---|
| KR-S1 | 1d | 278 | 276 | 282 | 139 | 975 | 0.13 | ENOUGH |
| KR-S8 | 1d | 29 | 42 | 34 | 20 | 125 | 0.35 | MARGINAL |
| KR-S8-high | 1d | 26 | 39 | 30 | 18 | 113 | 0.37 | MARGINAL |
| KR-S1 | 1w | 30 | 29 | 33 | 12 | 104 | 0.39 | MARGINAL |
| KR-S8 | 1w | 4 | 2 | 1 | 0 | 7 | 1.50 | THIN |
| KR-S8-high | 1w | 4 | 1 | 0 | 0 | 5 | 1.77 | THIN |
| MAL-2 | 1d | 7 | 5 | 11 | 3 | 26 | 0.78 | THIN |
| MAL-5 | 1d | 25 | 11 | 23 | 7 | 66 | 0.49 | MARGINAL |
| MAL-10 | 1d | 6 | 7 | 4 | 4 | 21 | 0.87 | THIN |
| MAL-17 | 1d | 35 | 20 | 27 | 12 | 94 | 0.41 | MARGINAL |
| MAL-16 | 1d | 42 | 38 | 26 | 21 | 127 | 0.35 | MARGINAL |
| MAL-17 | 1w | 3 | 5 | 2 | 0 | 10 | 1.26 | THIN |
| MAL-16 | 1w | 8 | 2 | 6 | 2 | 18 | 0.94 | THIN |

## 3. What this means for G3 and G5

- A row whose BTC MDE is above 0.60R cannot reject 'no edge' on BTC alone unless the trader's claimed edge is large; on DEV it can only be **described** (does the pattern look like his chart), not **tested**. Pool it with the other coins, or widen the pre-filter and say so, before spending a G5 slot.
- MAL-2 and MAL-10 are small because the 'weekly and monthly RSI both above 60' gate is true in only a few bull stretches of BTC; the monthly RSI(14) also needs 14 closed months, so the gate is blank before late 2018.
- Weekly rows hold under 40 events on BTC; they are descriptive only. The weekly stops are wide (see the stop column), which makes fees negligible but the sample tiny.
- No pre-filter here uses the 'with the trend' leg (KR-S1) or the 5-star timeframe pairing that is garbled in the transcript (MAL-2, MAL-5), so those counts are likely above what the trader's full rule would flag.
- KR-S8 weekly shows a median stop of 87% because a 10-week range on BTC is that wide: that row is not tradeable as written, whatever its count.
- MAL-2 and MAL-5 are two readings of the same sentence (RSI back at the sixty line while weekly and monthly are above 60); the support event is the narrower one. The timeframe of that sixty line is NOT STATED in the transcript (see malkan_extract_2026-10-15/COMPARE.md s1.2).

