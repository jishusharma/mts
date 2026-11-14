# BTC bear-phase reactions: where buyers stepped in after 5+ red weeks (2026-11-14)

**Finding: of 7 past episodes with 5+ red weekly closes and an 18%+ fall, 5 kept falling 36-86% below the 5th red close (lows 48-144 days later) and only 2 bounced within days; no level type (range low, 200w, fractal, volume node) beat chance within 2%.** Descriptive only; no rule, no gate, not a trade instruction.

Regime mix: 44 closed episodes (all fall >= 18% or 5+ red weeks, 2011-2026): cycle label at the low post-halving bull 14, post-bottom base 16, post-peak bear 12, pre-cycle 2; 200w SMA at detect: above 29, below 1, no history 14 (pre-2015). Strict set (both tests, n=7): bear-labelled 3, base-labelled 3, bull-labelled 1. Today's own label is ambiguous (see T4).

## Context
- Ask (operator, 2026-11-13 20:05Z): 6 red weeks in a row; understand past reactions before choosing where to look for edges. Bybit weekly open 2026-10-05 = 86,487 (operator quoted 86,486), week low 67,468.4: both confirmed from public klines.
- Data (SOURCED): Binance SPOT daily 2017-08-17 to 2026-11-13 (data-api.binance.vision), repo `btc_cycles_2026-11/btc_daily.csv` (blockchain.info index, high/low/close only, open = prior close) for 2011 to 2017-08, Bybit BTCUSDT 2020-03+ for cross-check (lows agree within 0.4% except 2021-05-19: Binance 30,000 vs Bybit 28,801). Bitstamp and api.binance.com timed out from this machine. Weeks are Monday 00:00 UTC. 2026-11-09 week is incomplete (5 of 7 days), excluded from streak counts.
- Cycle dates: SOURCED from `mts_bible/BIBLE.md` section 1 (2026-07-01 bottom is provisional there); 2011 peak/bottom OURS from the csv.
- All thresholds below are OURS (5 reds, 18%/8w fall, 2% tolerance, 5-bar fractal, 6m volume window). No parameter is the trader's.
- Episodes: union of (a) maximal runs of >= 5 red weekly closes (close < open) and (b) a weekly close >= 18% under the highest weekly close of the prior 8 weeks; clusters within 8 weeks merge unless price rallied >= 40% in between; low = lowest daily low, extended while a lower low prints within 28 days. 45 rows incl. today's open one: `episodes.csv`.
- Early blockchain.info data (2011-2013) is thin; 2014+ subset is shown where it matters. Sample sizes are small; every figure is a count, not a forecast.

## T1 strict episodes (>= 5 red weekly closes AND >= 18% fall; n=7 closed + today)
| Detect (5th red close) | Red wks | Depth* | Low vs detect close | Low (date) | 50w/200w at detect | Cycle at low | Bounce 1/2/4/8w | Days detect to low | Bear trap | Retest | 26w outcome |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2011-06-19 | 6 | -91% | -86% | 2 (2011-10-21) | n/a | post-peak bear | 33/52/52/52% | 124 | N | n/a | LH+new low |
| 2014-08-24 | 7 | -73% | -65% | 172 (2015-01-15) | below/n/a | base (406d post-peak) | 31/60/60/72% | 144 | N | no reclaim | LH |
| 2015-08-23 | 5 | -28% | -9% | 211 (2015-08-25) | below/above | base | 10/14/16/28% | 2 | Y | reclaimed, no retest | UP |
| 2016-08-07 | 6 | -29% | -10% | 531 (2016-08-03) | above/above | post-halving bull | 12/12/12/18% | -4 | N | n/a | UP |
| 2018-08-12 | 5 | -62% | -50% | 3,156 (2018-12-15) | below/above | base (363d post-peak) | 31/33/33/33% | 125 | N | no reclaim | UP |
| 2022-05-01 | 9 | -62% | -54% | 17,622 (2022-06-18) | below/above | post-peak bear | 23/24/28/41% | 48 | N | no reclaim | LH+new low |
| 2025-11-16 | 6 | -51% | -36% | 60,000 (2026-02-06) | below/above | post-peak bear | 20/20/23/27% | 82 | N | no reclaim | LH+new low |
| **2026-11-08 (today)** | 5 (+ week 6 red so far) | -22% so far | -10% so far | 67,568 so far | below/above | ambiguous | open | 5 so far | N | open | open |

*Depth = low vs highest weekly close of the 8 weeks before the trigger. Bounce = max high within n weeks after the low / low - 1. Outcome UP = weekly close back above the pre-fall high within 26 weeks; LH = no, and the low held; LH+new low = no, and a lower low printed. Bear trap = low undercut the lowest 5-bar weekly fractal low of the prior 26 weeks, then a weekly close at or above it within 2 weeks. Retest only defined when that swing low was undercut: after reclaiming it, did price come back within 2% and keep weekly closes >= 98% of it.

## T2 outcome stats (OURS definitions; bounce medians)
| Set | n | Median bounce 1/2/4/8w | IQR 4w ; 8w | Median days detect to low | Bear trap | 26w UP / LH / LH+new low |
|---|---|---|---|---|---|---|
| strict (a)+(b) | 7 | 23 / 24 / 28 / 33% | 20-42% ; 27-47% | 82 | 1/7 | 3 / 1 / 3 |
| all episodes 2011+ | 44 | 25 / 32 / 40 / 51% | 27-62% ; 40-85% | 8 | 6/43 | 30 / 2 / 12 |
| all 2014+ | 33 | 22 / 29 / 34 / 48% | 27-46% ; 39-77% | 6 | 6/33 | 22 / 2 / 9 |
| low in post-peak bear | 12 | 25 / 39 / 44 / 50% | 32-52% ; 45-64% | 46 | 1/12 | 1 / 0 / 11 |
| low in post-bottom base | 16 | 19 / 24 / 31 / 41% | 19-46% ; 28-74% | 10 | 5/16 | 13 / 2 / 1 |
| low in post-halving bull | 14 | 29 / 37 / 43 / 71% | 31-95% ; 44-124% | 0 | 0/14 | 14 / 0 / 0 |
Retests where the swing low was undercut (n=15): held 5, reclaimed with no retest 4, failed 1, no reclaim in 8w 5.

## T3 level hit rate: episode low within 2% of the level (n=44 closed episodes; base = every complete weekly low 2014-06+, same rule)
| Level type (as known at the low) | n with level | Hits | Hit % | Strict hits | Base % | Median nearest distance |
|---|---|---|---|---|---|---|
| range low 26w (days -182..-28) | 44 | 0 | 0% | 0/7 | 2% | 47.8% |
| range low 52w | 44 | 1 | 2% | 0/7 | 1% | 70.3% |
| round, 5k-style step (5k at 69k) | 44 | 11 | 25% | 2/7 | 39% | 3.3% |
| round, 10k-style step | 44 | 5 | 11% | 1/7 | 21% | 5.3% |
| 50w SMA | 40 | 3 | 8% | 0/6 | 2% | 38.4% |
| 100w SMA | 38 | 1 | 3% | 0/6 | 2% | 55.0% |
| 200w SMA | 31 | 1 | 3% | 1/6 | 2% | 36.7% |
| weekly 5-bar fractal low (104w) | 43 | 8 | 19% | 1/7 | 20% | 17.8% |
| volume node (6m daily, 2018+ only) | 19 | 0 | 0% | 0/3 | 18% | 26.0% |
At least one non-round level within 2%: 12/44. Lows below the 26w range low 15/44, below the 52w range low 8/44, below every daily low of the prior 6 months 12/44 (no volume node can exist there). At 5% tolerance: 200w SMA 13% vs 8% base, 50w 10% vs 7%, fractal 28% vs 38%, volume node 0% vs 42%, round 5k 77% vs 76%: still no level beats its base rate except a weak 200w/50w edge. Bible s.5 (200w within 1-11% of three of four cycle bottoms) is consistent: a zone, not a line.

## T4 today (2026-11-14; Binance spot close 69,091, week open 74,851, week low 67,568; Bybit low 67,468)
| Level type | Price(s) | Distance from close |
|---|---|---|
| range low 26w / 52w | 57,800 (2026-07-01) | -16.3% |
| round (5k and 10k step) | 70,000 (and 65,000, 60,000 below) | +1.3% (-5.9%, -13.2%) |
| 50w SMA | 75,110 | +8.7% (close is 8.0% under it) |
| 100w SMA | 88,749 | +28.5% |
| 200w SMA | 68,002 | -1.6% (close is 1.6% above it) |
| weekly fractal lows (104w, confirmed) | 76,606; 74,968; 74,508; 65,000; 62,510; 60,000 | +10.9%; +8.5%; +7.8%; -5.9%; -9.5%; -13.2% |
| volume nodes (182 daily bars) | 77,633; 64,199 | +12.4%; -7.1% |
| prior swing low in force (bear-trap reference) | 57,800 | -16.3%, not undercut |
State: 5 completed red weeks + week 6 red so far; depth -22% (-13% at the 5th red close) from the 86,530 8-week high close; 404 days after the 2025-10-06 peak (Bible peak-to-bottom range 363-406 d), 136 days after the provisional 2026-07-01 bottom, 938 days after the halving. Close below the 50w, above the 200w. Label is ambiguous: "base" if July holds, "post-peak bear" if not.

## T5 closest analogues (OURS score: streak gap + depth-at-detect gap + 50w/200w/cycle mismatches; 2014+)
| Score | Detect | Red wks | Depth | 50w/200w | Cycle | Low | Bounce 1/2/4/8w | Trap | 26w |
|---|---|---|---|---|---|---|---|---|---|
| 0.7 | 2015-08-23 | 5 | -28% | below/above | base | 211 (2015-08-25) | 10/14/16/28% | Y | UP |
| 1.0 | 2018-08-12 | 5 | -62% | below/above | base | 3,156 (2018-12-15) | 31/33/33/33% | N | UP |
| 1.4 | 2025-11-16 | 6 | -51% | below/above | post-peak bear | 60,000 (2026-02-06) | 20/20/23/27% | N | LH+new low |
| 1.5 | 2014-08-24 | 7 | -73% | below/n/a | base | 172 (2015-01-15) | 31/60/60/72% | N | LH |
| 1.8 | 2022-05-01 | 9 | -62% | below/above | post-peak bear | 17,622 (2022-06-18) | 23/24/28/41% | N | LH+new low |
| 2.4 | 2015-04-19 | 0 | -23% | below/above | base | 216 (2015-04-15) | 9/9/12/12% | N | UP |
Range across these six: bounce 1w 9-31%, 2w 9-60%, 4w 12-60%, 8w 12-72%; 26w outcome UP 3, LH 1, LH+new low 2. The shallow, fast pair (2015-08, 2015-04) is the only one with depth near today's; the deeper ones (2014, 2018, 2022, 2025) kept falling a further 36-65% below their 5th red close.

## Findings (at most 6)
1. Strict set (n=7): 5 of 7 printed their low 48-144 days after the 5th red close and 36-86% under that close; 2 (2015-08, 2016-08) bottomed within 4 days at -9/-10%. Today is -10% under the detect close after 5 days: it fits the second group so far, not the first (OURS reading; n=7).
2. Phase of the low separates outcomes: post-peak bear lows 11 of 12 made a lower low within 26 weeks and 1 of 12 reclaimed the pre-fall high; post-bottom base lows 13 of 16 reclaimed it; bull-phase lows 14 of 14. Today's phase is the open question (404 days post-peak, July bottom provisional).
3. Bounces after the low are large and fast in every phase: median 22-29% in 1 week and 48-51% in 8 weeks over 33-44 episodes (strict only 23% and 33%); the bounce is not a sign of a bottom, 11 of 12 bear-phase bounces later made a lower low.
4. Bear traps (swept 26w fractal low then reclaimed within 2 weeks): 6 of 43 episodes (14%), 1 of 7 strict, 1 of 12 in bear phase; most lows undercut the prior swing low (15 of 43) without reclaiming it. Retest of the reclaimed level held 5 of 15 undercut cases, failed 1, no reclaim in 8 weeks 5.
5. Levels: within 2% nothing beat its base rate (200w 3% vs 2%, fractal 19% vs 20%, volume node 0/19 vs 18%, 5k round 25% vs 39%); lows tend to print in volume vacuums or beneath prior lows (12/44 below every 6m low), not on nodes. 200w SMA is a weak zone (13% vs 8% at 5%).
6. Today the nearest candidates are the 200w SMA 68,002 (price sits 1.6% above), 70,000 round, 65,000 / 62,510 / 60,000 fractal lows, 64,199 volume node, and 57,800 swing low; the 50w (75,110) and 74.5-77k fractal cluster are overhead. Not a trade instruction.

Reproduce: `python fetch_data.py` (data/ is git-ignored) then `python run_study.py`; tests `python -m pytest test_btc_bear.py` (a deliberately off-by-one streak version fails 2 of 8).
