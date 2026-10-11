# Live chart reads 2026-10-09 (BTCUSDT)
# Thread: "Live market analysis" (Claude project MTS). Append-only. Reads only, no orders.
# Every number here is "chart read" (pixel estimate, +-50 unless quoted from the chart header). No system numbers.
# Capture store: runtime_data/observations on JIS-NB (capture.py). Screenshots: runtime_data/screenshots/img/<id>.png

## R1 - 15m, bar 13:45-14:00Z (chart clock is UTC, not IST: 04:11 left on the bar, posted 13:56:59Z)
- Shot 359bdb0c7cf9. Source: CoinGlass TV, Binance BTCUSDT 15m, 7-9 Oct.
- Obs ids: chart_read 975e99434e7c, trade_call long 78c2edf14f01, trade_call short c3cfe1c22eeb.
- VVP-001 sec 7 gaps: no VAH/VAL lines (POC only), no VWAP bands, CVD as candles not line. So no value-area claims.

Header (chart read 15m): O 82533.5 H 82730.0 L 82456.7 C 82626.4; VWAP 82568.8.
Levels (chart read 15m, est.): Oct-9 POC ~82500, Oct-8 POC ~82640, Oct-7 POC ~83360, Oct-9 high ~83470 (~12:00Z), Oct-8 low ~80370.
Flow (chart read 15m): OI 91.999K, lowest on the chart, fell on the 12:00Z spike. CVD -13.053K, rising from ~-16.5K (Oct-8 18:00Z). Net Delta -7.139K, flat-up.

Read: price sits on the Oct-8 POC, just above VWAP and the Oct-9 POC. The 12:00Z push to ~83470 came with OI
falling (short covering, not new longs) and was sold back under the Oct-7 POC. Middle of the 7-9 Oct range: no edge.
Lean neutral; trade only the edges.
- Long (conditional): test of ~82500 then a 15m close back above VWAP with positive net delta. Entry 82520, stop 82380, target 83350.
- Short (conditional): rejection of 83350-83470 (upper wick, CVD lower high, OI not rising). Entry 83400, stop 83560, target 82640.
Falsification: two 15m closes below 82450 with OI rising = new shorts, balance read broken down (next ~81640 Oct-9 low).
Two 15m closes above 83470 with OI rising = broken up.
Invalidation of the read: acceptance outside 82450-83470.

## R2 - 1m, bearish RSI divergence at the ~14:33Z high (chart clock UTC, last bar ~15:10Z, posted 15:12Z)
- Shot 502363361fff. Source: CoinGlass TV, Binance BTCUSDT 1m, 11:45-15:10Z. Operator's red arrows on price and RSI.
- Obs id: chart_read b1d0a9a11a76 (short leg is retroactive scoring of the divergence, not a live call).
- Links: T089 (multi-TF RSI divergence capture), T091 (long-range pairs), T087 (session levels).

Header (chart read 1m): O 82880.0 H 82888.6 L 82855.9 C 82873.0; VWAP 82624.4; BB20 82950.6 / 83115.5 / 82785.6; RSI 43.39, SMA 43.59.
Divergence (chart read, est.): price high ~83200 (~14:21-14:25Z) then ~83250 (~14:33Z); RSI ~75 then ~69. Pair is ~9-13 bars apart,
on the edge of Malkan's sourced 3-10 bar window: T089 catches it only if the detected pivots are <=10 bars apart, else it is a T091 pair.
Kline check (fapi 1m closes): A 14:21 close 83180.8 RSI 74.54, B 14:34 close 83266.0 RSI 70.03 = 14 bars, three swing highs between.
rsi_divergence does not flag it (3-10 or 3-60): not adjacent swings. T091 pair. Extract: research/screenshots/2026-10-09_BTCUSDT_502363361fff.md.
After: lower highs, price ~82830-82870 at 15:10Z (about -400 from the high), under BB mid, near BB low. RSI under 50.

Check against MTS data (live tree, read only):
- MATCH  VWAP: snapshot 15:13Z vwap 82622.5 vs chart 82624.4.
- MATCH  Red line ~82500 = daily VP POC 82488.12 (snapshot 15:13Z). Same level R1 called the Oct-9 POC.
- MATCH  OI: oi_1m.csv 92161.9 (14:21Z) -> 92296.5 (14:31Z), flat to 92263.6 (14:56Z), then 92018.8 (14:59Z) -> 91897.1 (15:01Z), -366 coins.
- MATCH  CVD shape: snapshot session CVD peaked 4213 (14:33Z), lower high 4114 (14:58Z), 3856 at 15:12Z. Level differs (CoinGlass 5.8K vs MTS 3.8K, different anchor): shape only.
- NOT_IN_DATA  RSI: the live runner has no RSI/divergence detector; alerts at 14:30/14:45/15:00Z were turn_of_candle only. Snapshot setup_candidates empty around the high.
- Note: snapshot open_interest.change_1h_pct stayed 0.09 "flat" 14:12-15:00Z and flipped "falling" only at 15:03Z, after oi_1m.csv showed the drop at 14:59Z (hourly field, lags).

Read: bearish divergence into the high with OI building, then the OI flush at 14:57-15:01Z (longs exiting) as price lost the BB mid.
Confluence: divergence + CVD lower high + OI drop. No MTS signal confirmed it (no live layer watches RSI).
Invalidation: 1m acceptance back above ~83270 with RSI above ~75. Next levels below: VWAP ~82624, daily POC ~82488.

## R3 - 3m, same 14:30 top seen across timeframes + MTS layer state (chart clock UTC, last bar ~16:27Z, posted 16:30Z)
- Shot b5f554a9f68a. Source: CoinGlass TV, Binance BTCUSDT 3m, 09:00-16:27Z. Operator's red arrows: 3m divergence at ~14:30.
- Obs id: chart_read 6657cd911836. Operator ask: divergence checks on every timeframe, and a way to see how it rolls over between them.
- Not a tested signal: T089 found no fee-net edge for RSI divergence on any timeframe.

Header (chart read 3m): O 82683.4 H 82700.0 L 82676.3 C 82691.6; VWAP 82676.4; BB20 82862.0 / 83046.7 / 82677.3; RSI 38.97, SMA 45.30.
OI 91.78K drifting down since the 15:00 flush; CVD 3.707K flat; net delta 1.079K flat.

One top, five timeframes (fapi klines, rsi_core 14, rsi_divergence Malkan 3-10, closes):
- 1m : 14:21 -> 14:34, 14 bars, 3 swing highs between: NOT flagged (non-adjacent, outside 3-10). R2.
- 3m : 14:21 -> 14:33, 5 bars, close 83160.1 -> 83173.8, RSI 66.5 -> 64.9: FLAGGED (adjacent, inside 3-10).
- 5m : no pair at this top; earlier 3-10 bearish pairs 11:45->12:00, 12:45->13:05, 13:05->13:15.
- 15m: 13:00 -> 14:15, 6 bars, close 83013.8 -> 83128.7, RSI 62.1 -> 61.1: FLAGGED.
- 1h : none (RSI 55.0 at the 15:00 close).
Roll-over: the 1m pair is too long and too noisy for the sourced window; it compresses into a clean 3-10 pair on 3m and 15m.
Non-adjacent scan (all earlier swings within 60 bars) gives 98 bearish pairs on 1m since 12:00: long-range on low TFs is mostly noise.
Live coverage: the runner's divergence detector is 1h only (rsi|malkan_bear|1h, rsi|malkan_bull|1h); 3m is not a live frame.

MTS state at 16:30Z (live tree, read only):
- Tom: last alert #273 at 14:26Z, NO_TRADE "no candidates", state TWOPEAK/above_vah -> in_va. No Tom alert since. Today: 12 Tom signals, all
  rejected (WAIT_PROOF / WAIT_TRIGGER), last tom#266 07:04Z. MISMATCH: the alert's SSOT_THESIS text still cites price ~77600 and target 76300
  (stale, price is ~83100 in the same alert).
- Fabio: quiet since 14:20Z (v3_grid 1m long signals, unmapped, not traded). Last 15m cvd_absorption bearish ~07:15Z. All fabio counters 0 at 16:30Z.
- Flow (snapshot 16:30Z): price 82690.7 = 4h VP POC 82686.77 / VAL 82676.66, VWAP 82632.5 rising, daily POC 82488.1, CVD flat, net delta 1h +93,
  OI flat (+0.07 % 1h), book bid/ask 1.17, nearest unfilled FVG bearish 82725-82773. State code A>L (3 of 5 bullish). Regime RANGE since 14:57Z.
  Session: day_type balance (provisional), range position 31 %.
- 16:30Z testnet entries from other layers: cryptocred sr_flip short 15m @82683.5, rsi_events failure short 5m @82696.0, turn_of_candle long 1m @82687.0.

Read: price sits on a cluster (VWAP, BB low, 4h POC/VAL ~82677-82690). The divergence move from the 14:33 top has done ~580 points. Flow is flat:
no new shorts (OI drifting down), CVD flat. MTS calls it a range, Tom has no candidate, Fabio is silent.
Falsify: a 3m close back above the BB mid 82862 with OI rising = range holds. Acceptance under 82630 (VWAP) = next daily POC ~82488.
