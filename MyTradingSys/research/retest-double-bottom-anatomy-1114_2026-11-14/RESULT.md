Plain answer: after long BTC falls, about 2 of 3 lows were followed by a retest or a higher low (usually within 1-10 days, usually 4-8% above the low), 1 of 3 went up in a V with no retest, and only about 1 in 10 made a real lower low; but the confirmation signals (neckline, MA20, 4H higher-high, WaveTrend cross) did NOT beat just buying at random in a fall with a similar stop once the look-ahead is removed, so they tell you structure, not extra odds. Today's candidate low (67,568, 13 Nov) has no confirmation yet.

Study of 65 lows since 2011 (38 with volume since 2017-09). Descriptive and exploratory. Nothing here is advice. Pre-registered: PRE_REG.md (plus Addendum A, written after the first run exposed a look-ahead; flagged post-hoc).

## Context
- Definition (OURS, mechanical): fall state = >= 4 red weeks OR close <= 80% of 56-day high; first low L = +/-10-day fractal low in fall state, lows >= 30 days apart. 65 episodes.
- Regime mix at L (bear = close < 200d SMA and drawdown from ATH > 30%; bull = above 200d SMA and drawdown < 20%; else base): bear 36, base 28, bull 0 (falls of this size do not start inside a bull trend), n/a 1. DEV (L <= 2023-12-31) 57 episodes, VALIDATION (2024+) 8.
- Era mix: 27 episodes 2011-2017-08 are price-only (no taker volume, no CVD); 38 since 2017-09 have volume; funding from 2020-03 and open interest from 2020-08 (Bybit public API; Binance fapi not reachable here). Pre-2013 prices are thin-market.
- Data: Binance spot klines 1D and 4H (taker buy volume from klines, CVD = 2 x taker-buy - volume), repo btc_daily.csv for 2011-2017-08, cached in F:\MTS\data_cache\btc_anatomy\.

## What happens after a low (anatomy, 1D; classes known only after the fact)
| Class | All 65 | Since 2017-09 (38) | Bear regime (36) | Base (28) |
|---|---|---|---|---|
| Higher low (> +3% above L, after >= 8% bounce) | 21 (32%) | 18 | 13 | 8 |
| Retest / double bottom (within 3%) | 14 (22%) | 10 | 9 | 5 |
| Lower low (< -3%), sweep and reclaim within 5 days | 2 (3%) | 2 | 0 | 2 |
| Lower low, no reclaim | 5 (8%) | 2 | 2 | 3 |
| V bottom (+30% with no >= 8% pullback) | 23 (35%) | 6 | 12 | 10 |
Validation 2024+: 6 higher lows, 1 retest, 1 V (8 episodes). Lows within 3% of the 200-week SMA (12 cases): 4 V, 3 retest, 4 higher low, 1 sweep-and-reclaim, no clean lower low.

| Timing and depth | Higher low | Retest | Lower low |
|---|---|---|---|
| Days from L to second low (median, IQR) | 9 (3-28) | 5 (2-11) | 31 (30-41) |
| Depth vs L (median) | +6.4% (3.7 to 12.2) | +1.2% (0.1 to 2.8) | -10.5% (-4.4 to -16.3) |
| Bounce between lows (peak above L, median, IQR) | 19.6% (17-21) | 14.9% (12-17) | 17.0% (11-22) |
Caution: a "lower low" only counts if it happens before a +30% move or a completed pullback; later, bigger lows are separate episodes. The V share is much higher in 2011-2017 (17 of 27) than since 2017 (6 of 38).

## Indicators at the first low vs the second low (daily, 42 pairs with a second low)
Share of pairs where the indicator is better (higher) at the second low than at the first:
| Indicator | Retest (14) | Higher low (21) | Lower low (7) |
|---|---|---|---|
| RSI(14) | 10/14 | 19/21 | 1/7 |
| WaveTrend WT1 (10/21) | 6/14 | 17/21 | 2/7 |
| MACD histogram | 13/14 | 19/21 | 2/7 |
| Bollinger %B | 13/14 | 19/21 | 2/7 |
| 14-day taker delta (CVD), since 2017 | 9/10 | 13/18 | 1/4 |
| 14-day volume lower at second low | 8 of 14 (retest and lower-low pairs together) | n/a | n/a |
Reading: nearly every retest shows MACD histogram, %B and CVD turning up at the second low (divergence), WaveTrend less so (WT1 higher in only 6/14 because WT is often more oversold on the retest). Lower lows show almost no divergence. Selection effect: a retest/higher low sits at or above L by definition, so some divergence is built in; this table describes the shape, it does not prove divergence predicts anything. 4H (since 2017, 32 pairs): median 4H RSI at L 30 (higher low), 27 (retest) rising to 42 and 36 at the second low; lower lows 29 falling to 23.
Funding and OI (2020-06+, 24 lows): 7-day average daily funding at L median +0.013%, range -0.040% to +0.167% (no consistent negative-funding capitulation); open interest 14-day change at L median +4.5% (-22% to +29%), no consistent flush.

## Confirmation levels: ex-post (anatomy only, look-ahead flagged)
Entry at the trigger close, stop 0.95 x L, +10% / +20% targets, 180 days, 12 bp. These use L, which is only known 10 days later, so they are inflated and the stop cannot trigger early. Use for shape only.
| Trigger | n | Median entry above L | +10% before stop | +20% before stop | Net/trade (+10% rule) |
|---|---|---|---|---|---|
| B0 buy at L close (unattainable) | 65 | +2.0% | 97% | 88% | +9.2% |
| C1 close above neckline (swing high between lows) | 34 | +20.0% | 82% (CI 68-94) | 61% | +4.5% |
| C2 close above SMA20 | 62 | +16.9% | 86% (76-94) | 71% | +5.5% |
| C3 4H close above last swing high | 38 | +11.8% | 95% (87-100) | 71% | +8.4% |
| C4 daily WT1 crosses WT2 below -53 | 40 | +10.4% | 83% (70-92) | 73% | +5.0% |
Upside given up waiting = the "entry above L" column: neckline 20%, MA20 17%, 4H higher-high 12%, WT cross 10%, versus 2% for the exact low.

## Confirmation levels: causal re-test (the tradable version, causal.py)
Event set with no knowledge of L: fall state in the last 10 days; stop = 0.95 x lowest low of the previous 30 days; 10-day lockout; 12 bp.
| Trigger | n | Median entry above stop ref | +10% before stop (CI) | +20% before stop (CI) | Net per trade (+10% / +20%) | VALIDATION 2024+ (+10%, n) |
|---|---|---|---|---|---|---|
| C1c 20-day-high breakout | 44 | +25.9% | 71% (57-82) | 59% (45-73) | -0.9% / +1.9% | 60% (5) |
| C2c cross above SMA20 | 104 | +15.6% | 73% (64-81) | 62% (52-71) | +1.8% / +4.8% | 81% (16) |
| C3c 4H break of swing high | 99 | +12.5% | 74% (65-82) | 55% (44-65) | +2.5% / +2.2% | 71% (21) |
| C4c WT cross up below -53 | 47 | +7.8% | 64% (49-79) | 53% (38-66) | +2.0% / +5.0% | 100% (7) |
| Placebo: any fall-state day, entry premium 0-8% | 711 | | 59% | 47% | +2.3% / +4.6% | 67% (82) |
| Placebo, premium 8-15% | 575 | | 74% | 59% | +3.4% / +5.9% | 83% (121) |
| Placebo, premium 15-25% | 409 | | 69% | 58% | +0.2% / +2.8% | 77% (26) |
| Placebo, premium over 25% | 538 | | 75% | 62% | -0.5% / +0.7% | n/a |
Reading: every causal trigger sits inside the placebo band for its stop distance. Hit rate is driven by how far the stop is from entry (wider stop = higher hit rate, lower net), not by the signal. No confirmation adds measurable edge over being long in a fall with a defined stop; they do reduce the chance of catching a falling knife in the first days, but that is not visible in these numbers. Validation samples are 5-21 events: not enough to confirm or refute.
What the numbers do say: buying the neckline gives up about 20% of the move for no better odds than buying the 4H structure break (12%) or the WT cross (8%); the cheaper entries lose nothing measurable.

## BTC now (descriptive, data to 13 Nov 2026, last full daily bar)
| Item | State |
|---|---|
| Price | 68,954 (13 Nov close); ATH 126,200; drawdown 45.4% |
| Fall state | True: 6 red weekly closes counting the current week (weekly open 5 Oct 86,530 on this data), 21% below the 8-week high 87,396 |
| First-low candidate | 67,568 (13 Nov 04:00 4H bar; daily low). Your 67,468 weekly low differs by 100 on this data feed. Not yet a confirmed fractal (needs 10 days with no lower low) |
| 200-week SMA | 68,001: the low pierced it by 0.8% and the close was above it |
| Zones off 67,568 | -3% = 65,541 (below = lower-low class); -5% = 64,190 (stop reference used above); +3% = 69,595 (retest band is 65.5k-69.6k, price is inside it now); +8% = 72,973 (bounce size that starts a pullback test) |
| Bounce since the low | 4H high 70,214 only (+3.9%): a neckline does not exist yet. Candidate necklines as they form: 70.2k 4H swing high, 71.5k (12 Nov close 71.46k), SMA20 76.7k, 20-day high 82.0k, SMA200d 73.1k |
| Daily RSI / WT1 / %B | 25.4 / -74.1 (WT2 -68.6, no cross) / -0.13: lower 5-13% of historical first lows since 2017 (more oversold than 87-95% of them) |
| 4H at the low bar | RSI 16.7, WT1 -84.6: lower 5% of historical lows ; WT1 ticked above WT2 on the 20:00 bar (-78.7 vs -82.0), still deep below -53 |
| 14-day taker delta (CVD) | +0.021 (net taker buying) vs a historical median -0.030: higher than 92% of past lows; every one of 24 lows since 2020 had negative 14-day delta, today does not |
| Open interest 14d / funding | OI +7.9% over 14 days (history median +4.5%); 7-day funding +0.019%/day, mildly positive. Not a long or short flush picture |
| Volume | 14-day volume 0.94 x the 90-day average (not a volume climax) |
| Which historical retests it resembles | Daily RSI/WT/%B levels match the first lows of 2018-12 and 2022-06 (RSI 20-25, WT1 -59 to -71); CVD and OI do not match (those lows had negative delta). Closest structural match: lows near the 200-week SMA (12 cases, none a clean lower low, 4 V, 7 retest or higher low) |
What would be observable next, by the history above: a bounce of >= 8% (to ~72,973) followed by a pullback is the setup in which a retest (median 5 days, within +/-3%) or a higher low (median 9 days, +4 to +12%) gets classified; a daily close below 65,541 puts it in the lower-low class (historically median -10%, 30+ days later, and with no indicator divergence at the second low).

## Gaps and caveats
- Classes, L, and the first table are look-ahead anatomy by design (the task asked for understanding). Only the causal table is tradable-style.
- 8 validation episodes: no verdict. All thresholds (8%, 3%, 10 days, 30 days, 0.95 stop) are OURS, not SOURCED. WT 10/21 and 53/-53 are LazyBear defaults (SOURCED).
- 4H independent episode detection was not run; 4H is used for the C3 trigger and for indicator states at the 1D lows.
- Big-trade and cross-exchange data (not requested in this slug) are untouched; OI/funding are Bybit, not Binance.
- Pre-2017 daily history is a blend of blockchain.info and exchange data, thin-market.

Files: anatomy.py, run.py, causal.py, now.py, now2.py, PRE_REG.md in this folder; raw data in F:\MTS\data_cache\btc_anatomy\.
