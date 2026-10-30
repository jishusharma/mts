# 30m WaveTrend: what the sequence tells (2026-10-30)

Descriptive counts only: no fees, no edge claim. Definitions in the header of `study.py`. WT 10/21/4 and ±53 are SOURCED (LazyBear); event rules and outcomes are OURS. Data: Binance BTCUSDT perp 1m rolled to 30m, DEV 2022-01 to 2024-06. The WT validation window (2024-07 onward) stays unread.

Trigger: operator shot 0a7af8773801 (Bitstamp 30m, 10-22 to 10-30) plus HTF shots 11b007ec579e (1D), 6f7da2f8be07 (8h), 9ab09fa48938 (4h), 69f5649353c4 (1D WT).

## Counts (baseline: random 30m bars, up after 12 h 50%, +1% first 45%, -1% first 45%)

| Event | n | Up 4 h | Up 12 h | +1% first | -1% first | Mean 12 h |
|---|---|---|---|---|---|---|
| T1 top cross (sell dot >= 53) | 465 | 48% | 51% | 53% | 42% | +0.20% |
| T1 with 4h WT up | 308 | 52% | 54% | 56% | 41% | +0.30% |
| T1 with 4h WT down | 157 | 41% | 47% | 47% | 44% | 0.00% |
| T2 bottom cross (buy dot <= -53) | 422 | 57% | 53% | 43% | 48% | -0.11% |
| T2 with 4h WT down | 304 | 56% | 53% | 42% | 49% | -0.17% |
| T3 bearish divergence at the top | 44 | 61% | 61% | 59% | 34% | +0.46% |
| T4 bullish divergence at the bottom | 52 | 52% | 48% | 39% | 52% | -0.25% |
| T5 centre cross up | 1,108 | 46% | 48% | 45% | 44% | +0.03% |
| T6 centre cross down | 1,113 | 55% | 52% | 44% | 46% | +0.06% |
| T7 rejection at 0 from below (came from <= -53) | 152 | 57% | 59% | 41% | 50% | +0.10% |
| T7 with 4h WT down | 124 | 52% | 60% | 41% | 50% | +0.10% |
| T8 rejection at 0 from above (came from >= 53) | 163 | 50% | 40% | 49% | 44% | +0.02% |
| T9b top-to-bottom in <= 16 bars | 7 | 43% | 29% | 0% | 86% | -0.18% |

One standard error is about 2.3 points at n=465, 4 points at n=150, 7 points at n=50.

After a top cross, wt1 reached the bottom zone within 24 h in 21% (4h up) to 29% (4h down) of cases. When it did, the median price move was -1.7% to -2.1%, in about 16 hours.

## Reading (the hidden stuff)

1. **On 30m the dots are not trade signals; they mark exhaustion of the current swing, not the trend.**
   - A sell dot at the top was followed by +1% before -1% in 53% of cases. With the 4h WT up, 56%.
   - A buy dot at the bottom gave a short pop (57% up after 4 h), then -1% came first 48% vs 43%.
   - The 4h decides which way the 30m swing resolves. That is the operator's 10-22 to 10-26 stretch: 30m WT cycled top to bottom and through 0 while the 4h and 1D stayed down.
2. **Centre crosses carry no information** (n≈1,100 each, within 2 points of base).
3. **The divergences ran opposite to the textbook, on small n.**
   - Bearish divergence at the top: price went up (61%, n=44).
   - Bullish divergence at the bottom: price went down first (52%, n=52).
   - Read: a divergence shows the trend is still strong enough to make new price extremes. Not settled at this n.
4. **The asymmetric one is the rejection at the zero line.**
   - From above (T8, came from the top, rejected at 0): up after 12 h only 40% (n=163, about 2.5 SE below base). The bounce failed and price continued lower.
   - From below (T7, today's shape): up after 12 h 59%, but -1% came first 50% vs 41%. The usual path was a dip first, then recovery within 12 h.
5. **Fast top-to-bottom swings (the 10-29 82k-to-77k path) are rare:** 7 cases in 2.5 years on DEV. They are too few to read.

## Live, 10-30 08:00Z (spot, closed bars)

| TF | wt1 | wt2 | State |
|---|---|---|---|
| 30m | -3.6 | -5.4 | Back near 0 from -55.7 (up-cross 02:30Z at 77,436). The 07:30 close almost crossed down. A closed 30m down-cross under 0 = T7. |
| 4h | -26.9 | -11.4 | Falling, below 0: the 4h-down context |
| 1D | -41.9 | -37.9 | Lower half, falling (the operator's 1D WT shot) |

- **If T7 prints with the 4h down:** 60% up after 12 h, but -1% (about 77.4k) first 50% vs +1% first 41%. That is base rates only, not a call.
- **The 10-29 17:00Z top cross (53.6 at 81,089) came with the 4h still up.** Only about 21% of such crosses reached the bottom zone within 24 h. That night took the minority path, with the Binance-hack news (dash-designer research, 74d7dc9f) as the likely driver.

## Next

- The asymmetric rejection at 0 (T8 vs T7) and the 4h-context split are the two leads. Both need pre-registered confirmation on the WT validation window before anything reaches the panel.
- This extends `wavetrend_2026-10-17` (which tested 5m to 1h, not 30m). The C1 divergence there was flagged invalid by the audit; T3/T4 here use real WT pivots, confirmed 2 bars later.
