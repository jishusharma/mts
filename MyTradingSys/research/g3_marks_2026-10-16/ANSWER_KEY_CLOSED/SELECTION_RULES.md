# Window selection rules (CLOSED with KEY.csv: readers must not open)

Moved out of README.md on 2026-10-17 (blindness cards g3-remove-visible-chart-cues-that-disclo, g3-assess-and-remove-visible-chart-side-): a reader who knows half the windows satisfy a published rule can infer the selection from the chart.

## Selection (seed 20261016, per row `<seed>-<code>`)
Per unit 20 windows: 10 random (any eligible right edge, the false-positive floor) and 10 candidate-enriched (pre-filter true at the edge). Windows of one unit are at least `space` bars apart. Window ids carry the row code and a shuffled number; nothing in an id, a chart or a sheet says which half a window is. Exceptions, reported as they are: MAL-2/5 has 13 (10 random + 3 enriched: only 7 weekly candidates exist in DEV and a 4-week spacing leaves 3); MAL-16/17 enriched = 5 bearish + 5 bullish.
| unit | rows | TF | windows | pre-filter for the enriched half (OURS, selection only, never an entry rule; counts of bars before spacing) |
|---|---|---|---|---|
| TOM4 | TOM-4 | 15m | 20 | bar low (high) trades through session VWAP and closes back on the trend side while three rolling 4h volume POCs rose (fell) twice by one bin (511 bars) |
| TOM6 | TOM-6 | 30m | 20 | 12 closes in a balance (1.5 %), the next bar closes outside on at least average balance volume, no close in the 0.5 % band beyond the edge in the last 240 bars (69) |
| TOM12 | TOM-12 | 30m | 20 | 4 closes outside the prior-session VA, then a close back inside (103) |
| TOM15 | TOM-15 | 30m | 20 | after a 12-close balance: three-in-a-line, outside bar or inside bar (after a 1.5x median-range impulse) whose high/low is within 0.15 % of the balance edge (1,018) |
| FAB1 | FAB-1 | 5m | 20 | 36-close balance (1.0 %) with net delta at least 10 % of volume, then a close outside it in that direction with a big trade in the bar or the bar before (261) |
| FAB4 | FAB-4 | 5m | 20 | session opened inside the prior VA, 2 to 24 closes outside it, then the first close back inside (212) |
| FAB5 | FAB-5 | 5m | 20 | third touch in 60 bars (3 bars apart, within 0.05 %) of one low (high) with delta against it of at least 15 % of volume and no close beyond the level (403) |
| KRS1 | KR-S1 | 1d | 20 | hammer / shooting star / strict engulfing / doji on at least average 30-day volume at a price with 2 or more swing points within 1.5 % (34) |
| KRS8 | KR-S8 | 1d | 20 | BBWP at or below 30 within the last 10 bars, now above 50, and a close beyond the 20-day close range (41) |
| MAL25 | MAL-2/5 | 1w | 13 | monthly RSI above 60, weekly RSI above 60 after a dip to 55..66 in the last 3 weeks and turning up (7) |
| MAL1617 | MAL-16/17 | 1d | 20 | a new 20-day closing high (low) with RSI(14) at least 2 points below (above) the RSI at the earlier high (low) 5..60 bars back, and a red (green) candle (70: 45 bear, 25 bull) |
The filters are cheap, causal (tested: the result at bar i is identical when every later row is deleted or poisoned) and were fixed after looking at candidate counts only, never at a price outcome. KR-S1 (volume 1.5x to 1.0x), MAL-2/5 (dip band 62 to 66) and FAB-5 (delta share and level held added) were loosened or tightened once on counts; that is the only tuning. Chart lab's 80 charts and candidate detector were not reused: they target TOM-1a and need Pillow, which JIS-NB does not have.

