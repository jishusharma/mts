# 15m Bollinger pierce near the US open: force behind it, and does it reach the prior-day level (BTCUSDT, 2022-01..2026-09)

Ask (operator, 2026-10-30, shot d73c8ab44f72): "what kind of force makes that happen? Try to measure it ... how far it will go ...
the support and resistances are the target ... I cannot understand in which direction the coil will fire."
Script `study.py` (definitions in its header, fixed before the first run), full output `output.txt`. Descriptive, no fees, all thresholds OURS.
Pierce = first 15m close outside BB(20,2), bar opening within 2 h either side of the US cash open. Level = prior-day high (up) or low (down).
REACHED = level traded before a 15m close back across the BB mid; FAILED = mid first; 8 h window. Force proxy = taker buy/sell from klines (no OI in the archive).

| Group (pierces with the level still ahead) | n | Reached level | Failed (back to mid) | Median run |
|---|---|---|---|---|
| All | 1009 | 30% | 52% | 0.59% |
| Level within 0.5% | 156 | **74%** | 25% | 0.36% |
| Level 0.5-1.5% | 313 | 36% | 54% | 0.63% |
| Level beyond 1.5% | 540 | 13% | 59% | 0.71% |
| Volume low third (< 1.96x the 20-bar mean) | 351 | 26% | 58% | 0.53% |
| Volume top third (>= 3.56x) | 302 | 36% | 45% | 0.67% |
| Top volume + taker delta with the pierce (> +0.10) | 197 | 39% | 42% | 0.63% |
| Coil before the pierce (BandWidth lowest 20% of 30 d) | 330 | 29% | 56% | 0.51% |
| Same, distance-matched (level 0.5-1.5%): top volume + delta / rest | 58 / 255 | 40% / 35% | 52% / 54% | |
| Same, distance-matched: coil / no coil | 108 / 205 | 35% / 37% | | |

## What it says
1. **The force is measurable.** The median pierce bar trades 2.6x the volume of the 20 bars before it, with taker flow +0.13 in its direction.
2. **Distance to the level decides most of it.** Within 0.5% the prior-day level is hit 74% of the time; beyond 1.5%, 13%. The median run is about 0.6%.
3. **More force helps a little.** Top volume with aligned delta reaches 39% vs 26% for weak pierces, but part of that is that those pierces sit nearer
   their level; distance-matched the gap shrinks to 40% vs 35% (n=58).
4. **The coil itself does not tell direction or reach.** A coiled pierce reaches its level no more often (35% vs 37% matched). The coil predicts
   a bigger range (see `research/pre_us_squeeze_2026-10-29/`), not which side.
5. **About half of all pierces close back across the mid first.** The "dance" fails more often than it runs.

## Not measured yet
OI (not in the 1m archive), RSI/WaveTrend coils, 2-day/weekly levels, other venues. 10-29 is outside the archive.
