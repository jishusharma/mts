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
