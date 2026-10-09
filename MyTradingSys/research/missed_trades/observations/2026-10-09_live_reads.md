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
