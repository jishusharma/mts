# BTC bottom signatures: durable lows vs failed bounces

2026-11-12, about 17:00Z. This is context, not a signal. It contains no orders and no sizes.

## Data
- Binance spot BTCUSDT klines with taker-buy volume (data-api.binance.vision):
  - 1d: 3,375 bars from 2017-08.
  - 4h: 20,232 bars.
  - 1h: from 2018.
- Bybit v5 linear BTCUSDT:
  - open interest, 1d and 4h, from 2020-08-05;
  - funding from 2020-03-26.
- Spot data covers one venue only (Binance). OI and funding come from Bybit only.

## Pre-registered definitions (all OURS, fixed before outcomes were tabulated)
| Item | Daily | 4h |
|---|---|---|
| Swing low | low = min of ±N bars, N=10 | N=30 bars (5 d) |
| Drawdown filter | low ≤ 0.85 × max high of prior 90 bars (≥15%) | ≥10% below max high of prior 180 bars (30 d) |
| DURABLE | no lower low within X=60 days | no lower low within X=120 bars (20 d) |
| FAILED | lower low within X | same |
| Retest | first bar after +3 within 3% of the low (window 30 bars daily, 60 bars 4h) | same |

Measures:
- **Delta:** taker buy minus taker sell, in BTC.
- **z (net-taker):** delta/volume minus its 30-bar mean. Binance spot has a standing buy bias of about +2 to +3%, so the raw delta is biased and z removes that.
- **Net buy:** delta minus the 30-bar bias times volume, in units of the 30-bar median volume.
- **OI into low:** OI change from bar −3 to bar +1.
- **Bounce type:** OI change over bars +1 to +4, together with z over bars +1 to +3:
  - GENUINE: OI up and spot delta up.
  - SHORTCOVER: OI down.
  - OI up with spot delta down: a perp-led bounce.

## Results (durable % when the signature is present vs absent, n)
Base rates:
- Daily: 52% durable (n=89).
- 4h: 56% durable (n=177).
- OI-based rows use only lows after 2020-08 (daily n=57, 4h n=113).

| Signature | Daily yes / no | 4h yes / no | Read |
|---|---|---|---|
| Capitulation volume ≥2x 30d median | 50% (30) / 53% (59) | 58% (109) / 54% (68) | **no edge** |
| Volume ≥3x | 44% (16) / 53% (73) | 58% (64) / 56% (113) | no edge |
| Close in top 40% of the low bar (wick) | 52% (52) / 51% (37) | 58% (103) / 54% (74) | no edge |
| Low bar absorbed (z on the low bar >0) | **64% (39) / 42% (50)** | 64% (73) / 51% (104) | weak to moderate, same sign on both timeframes |
| Next 3 bars z>0 | 54% (70) / 42% (19) | 59% (145) / 47% (32) | weak |
| Next 3 bars net buy ≥ +0.25x median volume | 0% (2) / 53% | **67% (51) / 52% (126)** | 4h moderate; daily n too small |
| 10-bar z>0 (buying persists) | **62% (63) / 27% (26)** | 61% (136) / 41% (41) | **strongest, both timeframes** (daily z≈3.3) |
| OI flush into low ≤ −5% | 42% (19) / 63% (38) | **79% (24) / 48% (89)** | 4h strong (z≈3.1); daily shows the opposite sign, so **inconclusive** across timeframes |
| OI rose into low | 71% (24) / 45% (33) | 42% (62) / 71% (51) | contradicts between timeframes |
| Funding ≤0 into low | 50% (4) / 57% (53) | 50% (22) / 56% (91) | no edge; daily n=4 |
| Bounce GENUINE | 67% (12) / 53% (45) | 61% (18) / 54% (95) | weak, n small: **inconclusive** |
| Bounce SHORTCOVER | 52% (25) / 59% (32) | 56% (72) / 54% (41) | **no edge**: a short cover is not by itself bearish |
| OI flush ≤ −5%, then GENUINE | 58% (12) / 56% | 75% (12) / 52% | inconclusive (n=12) |
| Retest on lower volume (<0.7x the low bar) | 35% (23) / 34% (35) | 46% (80) / 52% (52) | **no edge**: the textbook signal does not show up |
| No retest within the window | 26/31 = 84% | 36/45 = 80% | the low simply never got retested; this is close to the outcome itself (lookahead) |

Median net buy over the 12 h after a 4h low (3 bars, bias removed, Binance spot), lows since 2024:

| Outcome | n | Median net buy | 75th percentile |
|---|---|---|---|
| DURABLE | 24 | +824 BTC | +1,460 BTC |
| FAILED | 20 | +360 BTC | +905 BTC |

Caveats:
- Every row is conditional on the bar already being a confirmed pivot. In live trading you do not know that yet.
- About 25 tests were run per timeframe, so 1 or 2 rows will look "significant" by chance.
- 4h lows overlap one another.
- The daily OI history is short, and Bybit units before 2021 look noisy (one value of +200%).

## Answer: what amount of buying marks a real change
- Capitulation volume, a long wick, a low-volume retest and the bounce type alone do **not** separate the two groups.
- What does separate them is **sustained spot net-taker buying above its own baseline**:
  - on the low bar (absorption);
  - over the next 12 h on 4h bars;
  - over the next 10 days.
- On 4h bars, a **flush in perp OI into the low** (≥5% down) also separates them.

## Three thresholds to watch live (4h basis, current 30-bar median 4h spot volume 1,922 BTC, bias +3.2%)
1. **OI flush.** Bybit OI falls at least 5% (about −3,600 BTC at an OI of about 73k) between 12 h before the low and the bar after it.
   - With the flush: 79% durable (n=24).
   - When OI rises into the low: 42% durable (n=62).
2. **Absorption on the low bar.** The low 4h bar's spot delta/volume is above +3.2%, meaning raw delta is about +3% of the bar's volume or more.
   - Absorbed: 64% durable (n=73).
   - Not absorbed: 51% (n=104).
3. **Net buying over the next 12 h.** Raw Binance spot delta of at least **+670 BTC** in total over 12 h, which is +480 de-biased (0.25 × median 4h volume).
   - That is about **+14 BTC per 15m bar on average over 48 bars**.
   - Durable lows since 2024 had a median of +824 de-biased.
   - Then, for the daily layer: z stays above 0 for 10 days.
   - Hold on 12 h net buying: 67% durable (n=51). Without it: 52%.
   - The short-cover high of 72,224 is a level only. This study did not test it.

## How today's low scores (low 71,255 at 2026-11-12 ~15:00Z, 4h bar 12:00)
| Check | Today | Bucket |
|---|---|---|
| OI into low | **+8.6%** (67,870 → 73,683 BTC, Bybit 4h) | the weak bucket, 42% (n=62) |
| Low-bar absorption | delta −315 on 6,411 BTC; z = **−0.081** | not absorbed, 51% |
| Daily low bar | volume 0.82x, z −0.026 | not absorbed, 42% (n=50) |
| Capitulation volume (4h) | 3.3x | no edge |
| 16:00Z bounce | OI −348 with spot +5 = short cover | no edge on its own |
| 12 h net buy | 16:00 bar +51 raw (+21 de-biased); the earlier 9 h total was −254 | pending: needs about +670 raw by around 04:00Z on 11-13 |

Score: 0 of 3 met, 1 pending. So far today's low looks like the failed-bounce profile: OI was added into the drop, the selling was not absorbed, and the bounce was short-cover only. It is not yet a durable-bottom signature. None of this is a forecast.

Scripts and data are in the session scratchpad (fetch.py, an.py, tab.py, now.py). Nothing was committed.
