Verdict: T01=FAIL (DEV pooled n=108, mean net R -0.217, SE 0.150, 95 % CI -0.511..+0.077, MDE80 0.42; DEV mean <= 0 and CI upper below MDE; VALIDATION not read because the DEV screen failed)

# eh-h1-spinning-top-7star: Malkan 7-star spinning top, coded literally (T01)

## Plain-words answer
Coded as the source describes it (small body, long shadows both sides, volume at least 2x the prior 20-bar median, at a 20-bar extreme, buy stop above the high or sell stop below the low, stop at the other extreme, 3R target, 20-bar time stop), the rule is not a profitable trade on BTC and ETH spot 4h and 1d over 2017-08 to 2024-06. Mean net R is -0.22 per trade (n = 108). Only 29 % of trades are winners, and 10 of 108 reach the 3R target. The gross mean is already negative (-0.18 R) before fees (+0.04 R) and funding (-0.004 R). The 10R tail that Malkan's "1 is 2 10 20 30" claims never appears in DEV (0 of 108 trades reach 10R MFE). The rule fires rarely: 196 flagged 4h setups and 32 flagged 1d setups over 6.9 years for both symbols together, and about half of the 4h setups never trigger within 3 bars (96 of 196 flags). The next step is not testnet forward and not a longer backtest. T01 is dead as coded. Only a different, sourced reading of his 7-star would justify a new trial.

## Context
- Regime: none as a gate, because the rule is a one-bar pattern at a 20-bar extreme. The regime is reported only (Regime mix line below).
- Phase: none, because the trader's rule names no phase. The per-year table is the phase read.
- Session: none, because the rule is on 4h and 1d bars.
- Entry: signal bar i closes the setup. Buy stop 1 tick above its high (sell stop 1 tick below its low), live for bars i+1..i+3, filled at the trigger or at the open if the bar gaps through it.

Regime mix: 355 weeks: bull 64 (18%) | bear 14 (4%) | range 252 (71%) | n/a 25 (7%) (research_kit.regime_tag on BTCUSDT daily and weekly and monthly RSI14, as-of each DEV week start; OURS descriptive only)

## Counts (DEV, flags before the entry trigger and the position rule; no returns)
| TF | side | flags (BTC+ETH) |
|---|---|---|
| 4h | long | 82 |
| 4h | short | 114 |
| 1d | long | 14 |
| 1d | short | 18 |

Per symbol and year: counts.csv. Triggered trades (after the 3-bar stop-entry and one-position rule): BTC 4h 44, BTC 1d 7, ETH 4h 49, ETH 1d 8. Unfilled (no trigger within 3 bars): BTC 4h 47, BTC 1d 6, ETH 4h 49, ETH 1d 11. Skipped while a trade was open: 6.

## DEV result (2017-08-17 .. 2024-06-30; trial T01 pooled, both sides, both TFs, both symbols)
| n | clusters (ISO weeks) | hit rate | mean gross R | mean fee R | mean funding R | mean net R | SE | 95 % CI | MDE80 | one-sided p (mean > 0) |
|---|---|---|---|---|---|---|---|---|---|---|
| 108 | 83 | 0.287 | -0.179 | 0.041 | -0.004 | -0.217 | 0.150 | -0.511 .. +0.077 | 0.420 | 0.93 |

Outcomes: stop 71, time stop 27, target 10. Share of trades with MFE >= 10R: 0.0 (descriptive, his 1:10+ claim).

Screen: n >= 30 yes; mean net R > 0 no; CI lower > 0 no. DEV screen FAILED, so VALIDATION was not read (no 2024-07..2025-06 bar was loaded). Holdout not loaded.

### Exploratory cells (no promotion)
| cell | n | hit | mean gross R | mean fee R | mean net R | SE | 95 % CI |
|---|---|---|---|---|---|---|---|
| BTC 4h | 44 | 0.27 | -0.231 | 0.054 | -0.275 | 0.200 | -0.667 .. +0.116 |
| BTC 1d | 7 | 0.14 | -0.642 | 0.013 | -0.656 | 0.184 | -1.016 .. -0.295 |
| ETH 4h | 49 | 0.31 | -0.060 | 0.038 | -0.098 | 0.254 | -0.596 .. +0.401 |
| ETH 1d | 8 | 0.38 | -0.226 | 0.014 | -0.240 | 0.491 | -1.202 .. +0.721 |
| long (both TF, both symbols) | 41 | 0.39 | -0.075 | 0.030 | -0.111 | 0.221 | -0.543 .. +0.321 |
| short (both TF, both symbols) | 67 | 0.22 | -0.243 | 0.048 | -0.282 | 0.207 | -0.686 .. +0.123 |

### Per year (DEV, by fill year, pooled cells, mean net R)
| year | n | mean net R |
|---|---|---|
| 2017 | 8 | +1.132 |
| 2018 | 20 | -0.596 |
| 2019 | 13 | -0.342 |
| 2020 | 16 | -0.784 |
| 2021 | 8 | +0.421 |
| 2022 | 19 | +0.110 |
| 2023 | 11 | +0.020 |
| 2024 (to 06-30) | 13 | -0.711 |

Positive years are 2017, 2021, 2022 and 2023 (n 8 to 19 each); negative years are 2018 to 2020 and 2024. The sign is not stable.

## Method
- Code: spinning_top.py (rules, loader with DEV and VALIDATION refusal, simulation, cluster statistics). Tests: test_spinning_top.py, 20 tests, all passing. The first run, before spinning_top.py existed, failed at collection: last line `1 error in 1.35s`.
- Data: Binance spot klines 4h and 1d, BTCUSDT and ETHUSDT, 2017-08 .. 2024-06 used. Funding: USD-M fundingRate archive from 2019-09 (applied where it exists, 0 before 2019-09; spot has no real funding, so this is the brief's convention and is labelled).
- Fees: regime A, 5 bps per side on every leg = 10 bps round trip, plus 2 bps round-trip slippage (12 bps). fee_r = 12 bps / stop distance.
- Statistics: SE clustered by ISO week of fill time (small-G corrected). MDE80 = 2.8 SE. The p-value is normal-approximate.

## DECISION (OURS) list
1. Tick = 0.01 price unit for both symbols (Binance spot tick). Not sourced; fixed once.
2. One open trade per symbol and TF. Setups while a trade is open are skipped and counted (6 in DEV).
3. Same-bar double flag (a bar that meets both the long and short location tests): the long is kept and the short is suppressed. PRE_REG said "each side is a separate trade under the one-position rule", which cannot hold literally, so this is the conservative resolution: 1 case, BTC 4h. Stated here as a deviation from the PRE_REG wording.
4. Stop-entry fill = trigger, or the bar open if the bar gaps through it. Gap-through stop exits fill at min(open, stop); gap-through target fills at max(open, target).
5. Time stop = close of the 20th bar counting the fill bar. Windows: trades open at a window end are closed at its last close (0 in DEV).
6. Holm threshold for a single VALIDATION read = 0.05 / 15 (the most conservative step). Not reached here because VALIDATION was not read.
7. Regime mix uses research_kit.regime_tag with weekly and monthly RSI14 (Wilder, OURS) computed inside spinning_top.py from BTCUSDT daily closes.
8. DEV starts at the data start (2017-08), per the brief. splits.py DEV_START is 2022-01-01, which is not used here.

## Noticed
- The funding fetch returned 404 for 4 of 70 monthly files (ok 66). I did not check which months those are, so funding for those months may be missing; the funding R is small (-0.004), so this is immaterial to the verdict.
- Spot fees follow the brief (taker 0.0005 per side, regime A). Binance spot taker is higher in reality, so the real cost is worse than this run. Any future spot trial should check the spot fee schedule before it runs.
- The 4h trades use the 20-bar location window on a 4h chart (about 3.3 days), and the 1d trades use about 1 month. A different window is untested by design (frozen).
