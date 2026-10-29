# Bollinger dance: when is it over, and does an early take-profit lose the big leg? (2026-10-30)

These are descriptive counts only: no fees and no edge claim. Definitions are in the header of `study.py` (all OURS). The data is the Binance USD-M BTCUSDT 1m archive, built into 5m bars, DEV 2022-2025 only. The trigger was the operator's shot 32fd5d2253ee: a short from the 20:00Z close below the BB mid on 10-29, and his question about the slanting arrow.

Sample: 11,051 shorts that started on a 5m close back below the mid and then touched the lower band.

## 1. The dance: distance from the band matters, the candle count does not

Columns: the chance of a new low (below the low so far) before any 5m close above the mid. The rows are k, the closed bars since the last lower-band touch.

| k | Close near the band (%b < 0.25) | n | Close away from the band (%b >= 0.25) | n |
|---|---|---|---|---|
| 1 | 59% | 6,360 | 32% | 3,353 |
| 2 | 59% | 4,528 | 31% | 3,934 |
| 3 | 60% | 3,302 | 29% | 3,982 |
| 4 | 60% | 2,490 | 29% | 3,721 |
| 5 | 63% | 1,929 | 27% | 3,315 |
| 6 | 64% | 1,474 | 26% | 2,874 |

Reading:
- **A close that stays close to the lower band means the dance is still on,** however many bars have passed since the last touch: about 60% get a new low first.
- **A close a quarter of the way up the band means the dance is fading:** about 30% get a new low first, and the share falls with each quiet bar.
- %b = (close - lower) / (upper - lower). 0 is on the lower band, 0.5 is the mid.

## 2. Exits compared (gross % per short, each rule over all 11,051)

| Exit | Mean | Median | Share > 0 |
|---|---|---|---|
| First close back inside after a touch | +0.178% | +0.094% | 76% |
| Three bars without a touch | +0.178% | +0.067% | 64% |
| First close with %b >= 0.25 (left the band) | +0.172% | +0.062% | 69% |
| Close above the mid (hold) | +0.168% | +0.005% | 51% |

Reading:
- **On average, holding to the mid did not pay more than leaving early.** The means are the same within noise.
- **Holding turns the trade into a coin flip with a fat tail:** half the trades give back everything, and a few catch the big leg.
- **An early exit wins more often for the same mean.**
- All four are under +0.2% gross, against 0.12% round-trip cost. No exit here is an edge yet.

## 3. The 10-29 case, bar by bar (spot, `live_output.txt`)

- **Entry:** the 20:00 close at 80,412, below the mid at 80,798.
- **Touches:** every bar touched the lower band from 20:00 to 21:00, except 20:25. The 20:50 green closed at %b 0.02, right on the band. That is the operator's "green very close to the lower band": the dance was on, and the 20:55 and 21:00 bars touched again.
- **Last touch:** 21:00.
- **The dance fades:**
  - 21:05 closed near the band (%b 0.21), so about 59% for a new low.
  - 21:10 closed at %b 0.25, which is away from the band: about 31%.
  - From 21:15 the closes were at %b 0.30-0.46.
- **No new low:** 22:00-22:10 came back near the band (%b 0.11-0.21), but the 22:05 low of 78,627 stayed above the 78,297 low.
- **Exits for this short:**

| Exit | When | Price | Gain |
|---|---|---|---|
| %b >= 0.25 | 21:10 | 79,225 | +1.48% |
| Three bars without a touch | 21:15 | 79,567 | +1.05% |
| Close above the mid | 22:20 | 79,166 (mid 79,137) | +1.55% |

## Open

- **The bars here are 5m only.** Repeat on 15m and 1h inside `bb-state-regime-tf-map`, with %b as the state variable.
- **CVD and force were not used.** Next, split the near/away table by the bar's taker delta: does a close near the band with selling delta beat one with buying delta? This is U8-adjacent; add it to `cvd-coil-and-absorption-u7-u8`.
