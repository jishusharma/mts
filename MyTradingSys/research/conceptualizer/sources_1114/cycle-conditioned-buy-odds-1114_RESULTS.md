Answer: buying BTC now is an average-to-slightly-below-average spot by the full cycle-position match (analog median 90-day return -2%, 40th percentile of all days, large drawdown risk), but a better-than-average spot by the single "price within +10% of the 200-week SMA" rule (median +22%, 76% positive, small dips); the two disagree, the multi-feature match has no out-of-sample skill, and the 200-week evidence rests on 9 episodes (about 4 real cycle bottoms).

## Context
- Sample: 4,443 days with a full 90d outcome, 2014-06-17 to 2026-08-15 (the 200w SMA needs 1,400 days of history, so 2013 to mid-2014 cannot be scored). "Today" = 2026-11-13 intraday snapshot (close 68,952, provisional); 2026-11-12 (71,460, complete) gives the same analogs.
- Regime mix of all eligible days (phase known at the time): bear 1,841 (41%), base/recovery 1,523 (34%), bull 1,079 (24%). Today = bear (drawdown <= -20% and below the 200d SMA). 13 of the 15 analogs are bear days, 2 base, 0 bull.
- Returns are close-to-close (no daily open in the data). Forward windows overlap heavily: the 4,443 days are about 144 independent 30-day episodes and only about 4 true cycle bottoms.
- MVRV: free source found (CoinMetrics community CapMVRVCur, cached at F:\MTS\data_cache\coinmetrics). Used as variant V2 and in the exploratory section.
- Pre-registered before any outcome was computed: PRE_REG.md (commit cf2021f49). Rule, bins and tests were not changed afterwards; the "Exploratory" section was added after seeing results and is labelled so.

## Today's features (known at the close)
| feature | value | note |
|---|---|---|
| days since halving (2024-04-20) | 937 | |
| days since ATH (2025-10-06, 126,199) | 403 | |
| drawdown from ATH | -45.4% | 11-12: -43.4% |
| red-week streak (running week counted) | 6 | close-to-close weeks |
| close vs 200w SMA (67,605) | +1.6% | 11-12: +5.3% |
| close vs 50w SMA (75,818) | -8.7% | |
| weekly RSI(14), last completed week | 47.9 | |
| weekly WaveTrend wt1, last completed week | +20.3 | |
| MVRV (CoinMetrics, 11-12) | 1.32 | days with MVRV 1.2-1.5: median 90d +1.8% (962 days) |

## Headline: analog rule (pre-registered, 15 independent analogs, 90d)
| set | n | median 90d ret | 95% CI of median | % positive | median MAE90 | p10 MAE90 | % MAE < -20% | pctile of median among all days (ret / MAE) | placebo p (ret / MAE) |
|---|---|---|---|---|---|---|---|---|---|
| ALL days | 4,443 | +7.3% | | 57.6% | -15.1% | -45.6% | 39.6% | 50 | |
| PRIMARY (8 features) | 15 | -2.0% | -19.7% to +25.5% | 46.7% | -18.1% | -41.5% | 33.3% | 40 / 44 | 0.81 / 0.71 |
| V2 (+MVRV, run on 11-12) | 15 | -2.0% | -19.7% to +27.4% | 46.7% | -18.1% | -41.5% | 33.3% | 40 / 44 | 0.77 / 0.66 |
| V3 (drawdown, 200w dist, weekly RSI) | 15 | +12.3% | -6.6% to +31.3% | 66.7% | -9.5% | -55.8% | 33.3% | 55 / 62 | 0.33 / 0.18 |

Placebo p = share of random 15-day independent draws that did as well. Nothing is distinguishable from a random draw (p 0.18 to 0.81). The 15 primary analogs: 2014-10, 2015-01, 2015-09, 2016-02, 2018-05, 2018-11, 2019-10, 2019-11, 2020-03, 2022-05, 2023-05, 2023-09, 2025-11, 2026-02, 2026-06. Their 90d returns split into two clusters: rebounds (2015-09 +58%, 2020-03 +77%, 2023-09 +60%, 2026-06 +27%) and continuation drops (2014-10 -20%, 2015-01 -22%, 2018-11 -25%, 2022-05 -34%). Full table in run.log.

Plain reading: by eight features, "where we are in the cycle" looks like a late-bear continuation and a bottom zone in roughly equal parts. The match cannot tell which.

Walk-forward test (VALIDATION 2024-01 to 2026-08, 958 days, analogs only from days at least 90 days old): predicted top-third vs bottom-third days realised +11.3% vs +4.9% mean 90d return; difference +6.4 pp, block-bootstrap 95% CI -11.5 to +36.8 pp; correlation of predicted vs realised 90d return 0.00. The analog rule has no demonstrated skill. Today's prediction (-2.0%) sits at the 30th percentile of validation-period predictions.

## Simple bins (pre-registered; 90d unless noted; all days in the bin, overlapping)
| bin | today in it? | days | independent episodes | median 90d | % positive | median MAE90 | p10 MAE90 | median 30d | median 180d |
|---|---|---|---|---|---|---|---|---|---|
| ALL | | 4,443 | 144 | +7.3% | 57.6% | -15.1% | -45.6% | +2.5% | +24.7% |
| B1 close <= 200w SMA +10% | yes | 665 | 30 | +22.5% | 76.4% | -6.4% | -21.3% | +6.1% | +48.4% |
| B2 350-450 days after ATH | yes | 303 | 12 | +22.5% | 74.9% | -7.4% | -47.9% | +2.7% | +58.8% |
| B12 B1 and B2 | yes | 143 | 8 (3 distinct windows) | +41.0% | 100% | -4.9% | -17.5% | +7.4% | +62.0% |
| B3a drawdown -20..-35% (operator wording) | no (now -45%) | 437 | 32 | +18.9% | 61.3% | -14.2% | -38.5% | +3.7% | +11.4% |
| B3b drawdown -40..-50% (today's band) | yes | 675 | 33 | +10.6% | 55.0% | -15.5% | -45.5% | +1.7% | +22.1% |
| B1b B1 and drawdown <= -40% | yes | 665 | 30 | +22.5% | 76.4% | -6.4% | -21.3% | +6.1% | +48.4% |

B1b equals B1 because every day near the 200w SMA was already 40%+ below its ATH.

By phase (median 90d / % positive / days): B1 bear +27.4% / 74% / 495; B1 base +15.9% / 84% / 170. B3a bear -9.6% / 46% / 187 (a -20 to -35% drawdown in a bear phase was a continuation zone, not a bottom); B3a base +27.9% / 73% / 250. B3b bear +6.4% / 54% / 279. All days: bear -3.7% / 46%, base +19.8% / 70%, bull +6.8% / 59%. Full grid: bins.csv.

## Exploratory (added after seeing results, not pre-registered)
Episodes with close <= 200w SMA +10%:
| episode | days | min dist to 200w | median 90d ret | median MAE90 |
|---|---|---|---|---|
| 2015-01 | 6 | -10.9% | +7.9% | +1.0% |
| 2015-04 to 06 | 42 | +2.5% | +4.6% | -5.6% |
| 2015-08 to 10 | 62 | -8.7% | +76.3% | -0.9% |
| 2018-12 to 2019-02 | 36 | +1.6% | +52.6% | -2.7% |
| 2020-03 | 9 | -12.4% | +76.7% | -5.7% |
| 2022-06 to 2023-06 | 342 | -34.2% | +6.2% | -12.6% |
| 2023-07 to 10 | 91 | -9.0% | +49.5% | -4.2% |
| 2026-02 | 2 | +8.5% | +25.1% | -3.1% |
| 2026-06 to 08 | 75 | -6.2% | +25.9% | -3.7% |
- All 9 episodes have a positive median 90d return; median of episode medians +25.9%, bootstrap 95% CI +6.2% to +76.3%. DEV (to 2023): 588 days, median +20.1%, 73% positive. VALIDATION (2024+): 77 days, median +25.9%, 100% positive (one episode, 2026-06 to 08).
- Weak spot: the 2022 episode sat near or below the 200w SMA for 342 days and went as far as 34% under it; median dip -12.6%, return only +6%. "Near the 200w" was not "the bottom" there; the low came later and lower.
- Red-week streak >= 6 (today's state): 55 days, 7 episodes, median 90d -14.5%, 33% positive, median MAE -37.7%. Long red streaks alone were continuation, not exhaustion (streak >= 5: -3.6%, 47% positive, 11 episodes).
- Weekly RSI < 50 and near the 200w SMA: 488 days, 9 episodes, +26.3% median, 73% positive.
- MVRV: median 1.00 on 200w-SMA days (all days 1.64). Today's 1.32 is above the 0.7 to 1.0 zone of the 2015, 2018 and 2022 lows, and matches the 1.2 to 1.3 seen at the 2023-07 and 2026-06 episodes.
- Price context: lowest low since the ATH = 57,800 (2026-07-01); lowest low since then = 59,588. Price is now about 19% above the July low.

## BTC now (descriptive, no advice)
- Close 68,952 (provisional): 45.4% under the ATH, 403 days after it, 6 red weeks in a row, 937 days after the halving; phase = bear.
- 200w SMA 67,605 (price +1.6% above, it was +9% on 11-11); 50w SMA 75,818 (price 8.7% below).
- Weekly RSI 47.9 and weekly WaveTrend +20.3 (last completed week) are not oversold. Weekly WT was about -39 to -47 around the 2014-15 and 2018 lows, so weekly momentum has not reset.
- MVRV 1.32, above the 1.0 area of past cycle lows.
- Days near the 200w SMA had a median 90d forward return of +22.5% with a median 90d worst dip of -6.4% (p10 -21%); days matching the full 8-feature profile had -2.0% with a median dip of -18%. A close below the 200w SMA stays inside bin B1, which includes dips down to -34% under it.

## Limits
- About 4 cycles: episodes, not days, are the sample (9 in B1, 3 in B12). All CIs are optimistic.
- The analog rule has zero walk-forward skill; the -2% and +12% are not forecasts.
- 2014-2016 daily data is thin-market (blockchain.info then Binance); the 200w SMA is 1,400 daily closes.
- The B1 bin was fixed before computing, but the idea of the 200w SMA is the operator's prior; the 2026-06 VALIDATION episode is one data point.
- Fees: 24 bp round trip (12 bp per side) subtracted in net figures (mean 90d net in B1: +25.7% DEV, +26.4% VAL); immaterial next to 90d moves.

Files: PRE_REG.md, fetch.py, analyze.py, extra.py, run.log, extra.log, bins.csv; feature table at F:\MTS\data_cache\btc_cycle_features_1114.csv (not in repo).
