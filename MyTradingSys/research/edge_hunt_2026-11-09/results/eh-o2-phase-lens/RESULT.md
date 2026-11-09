Verdict: T14=FAIL (DEV mean net -0.232 R +- 0.071, n=358, CI upper -0.094 < MDE 0.198); T15=INCONCLUSIVE (DEV mean net +0.016 R +- 0.247, n=51, CI -0.467..+0.500, MDE 0.691). Neither passed the DEV screen, so VALIDATION was not read. PHASE_LABEL shipped.

**In plain words:** the new phase label works and finds the bear markets the old regime tag missed: 112 of 358 DEV weeks are BEAR or BOTTOM_WINDOW, against 0 bear weeks in the research_kit tag. Neither trial earns money in the cell it was built for. T14, fading a sweep of the prior day's high or low on BTC 1h in the "balance" cell, loses 0.23 R per trade after costs. Before costs it breaks even (+0.004 R), and taker costs on 74 bps median stops eat 0.24 R. It also loses in every year with more than 3 trades. That is a FAIL with adequate power. T15, Malkan's 4h RSI-40 bounce long in ACCUMULATION/BULL with the weekly RSI at 40 or above, is flat (+0.02 R) on only 51 trades. That cannot tell a real edge from zero (INCONCLUSIVE). Its best sub-cell (BULL x weekly HIGH, +0.55 R, n=18) is exploratory and cannot promote.

Regime mix: DEV weeks 2017-08-14..2024-06-30 (research_kit regime_tag): 358 weeks: bull 72 (20%) | bear 0 (0%) | range 223 (62%) | n/a 63 (18%). T14 span 2020-01..2024-06: 234 weeks: bull 64 (27%) | bear 0 (0%) | range 170 (73%) | n/a 0 (0%).
Phase mix (PHASE_LABEL, same 358 DEV weeks, phase_calendar.csv): BEAR 100, ACCUMULATION 93, BULL 64, PEAK_WINDOW 46, TRANSITION 43, BOTTOM_WINDOW 12. Weekly zone: MID 170, HIGH 117, LOW 57, n/a 14 (RSI warm-up 2017).

## Context
- Regime: PHASE_LABEL = point-in-time BTC cycle phase x last closed weekly RSI14 zone (HIGH > 60, MID 40..60, LOW < 40). The research_kit regime tag is reported above only.
- Phase: T14 balance cell (zone MID, phase not PEAK_WINDOW / BOTTOM_WINDOW); T15 ACCUMULATION or BULL with zone MID or HIGH.
- Session: none, because neither rule names a session.
- Entry: signal bar close, taker (regime A + 2 bps slippage + funding).

## PHASE_LABEL (deliverable: phase_label.py, test_phase_label.py)
Pure functions over closed daily bars only. `cycle_phase(t, daily)` is the from-scratch reference, `PhaseLabeler(daily).label(t)` the fast incremental version (a test shows the two agree), and `phase_label(t, daily)` the one-shot (phase, zone). The cycles.csv turn dates are never inputs. The point-in-time detector reproduces them (BTC spot 1d, DEV):

| Turn (cycles.csv) | Known by the rule at | Phase switch |
|---|---|---|
| peak 2017-12-17 | 2018-12-15 (peak + 363 d) | BEAR from 2018-01-09 (halving + 549 d), BOTTOM_WINDOW 2018-12-15..2019-01-27 |
| bottom 2018-12-15 (3,156) | 2019-05-11 (first close >= 2 x low) | TRANSITION 2019-01-28..05-10, ACCUMULATION 2019-05-11..2020-05-10 |
| halving 2020-05-11 | scheduled | BULL to 2021-05-17, PEAK_WINDOW 2021-05-18..11-10 |
| peak 2021-11-10 | 2022-11-08 | BEAR 2021-11-11, BOTTOM_WINDOW 2022-11-08..12-21 |
| bottom 2022-11-21 (15,476) | 2023-07-04 (close 31,156 on 07-03) | TRANSITION 2022-12-22..2023-07-03, ACCUMULATION to 2024-04-19 |
| halving 2024-04-20 | scheduled | BULL |

## T14: 1h prior-day level fade, balance cell (DEV 2020-01..2024-06, BTCUSDT USD-M futures)
| n | hit (gross > 0) | mean gross R | mean fee_r | mean funding R | mean net R | SE (day) | 95 % CI | MDE 80 % |
|---|---|---|---|---|---|---|---|---|
| 358 | 38.0 % | +0.004 | 0.237 | -0.000 | **-0.232** | 0.071 | -0.371..-0.094 | 0.198 |

Per year (DEV): 2020 n=117 -0.407 | 2021 n=31 -0.000 | 2022 n=80 -0.137 | 2023 n=127 -0.210 | 2024 n=3 +0.694. By side: short (PDH) n=173 -0.133; long (PDL) n=185 -0.325. All phases pooled (exploratory): n=1061, -0.139 +- 0.042.

## T15: MLK-S1 4h RSI-40 long, ACCUMULATION/BULL x weekly MID/HIGH (DEV 2017-08..2024-06, BTC+ETH spot)
| n | hit | mean gross R | mean fee_r | mean funding R | mean net R | SE (ISO week) | 95 % CI | MDE 80 % |
|---|---|---|---|---|---|---|---|---|
| 51 | 37.3 % | +0.157 | 0.094 | 0.047 | **+0.016** | 0.247 | -0.467..+0.500 | 0.691 |

Per year (DEV): 2019 n=13 -0.533 | 2020 n=10 +0.539 | 2021 n=9 -0.060 | 2023 n=9 -0.452 | 2024 n=10 +0.697 (2017, 2018 and 2022 have no trades in the cell). By symbol: BTC n=23 -0.400, ETH n=28 +0.359. All phases pooled (exploratory): n=115, -0.320 +- 0.144. Out-of-cell events lose clearly (BEAR cells -0.75..-1.05 R), so the phase filter does separate losers from break-even. It just does not reach a positive edge.

## Exploratory phase table (cells.csv; net R per cell; cannot promote)
T14: every cell's mean is <= +0.03 R. The confirmatory MID cells are the worst (ACCUMULATION x MID -0.386, BULL x MID -0.408), because MID-zone days have the tightest stops (fee_r 0.28-0.30). BULL x HIGH -0.022 (n=200), PEAK_WINDOW x MID -0.026 (n=91), TRANSITION x HIGH +0.017 (n=39), BOTTOM_WINDOW x LOW +0.028 (n=25). No cell has a CI above 0.
T15: BULL x HIGH +0.553 (n=18, CI -0.17..+1.28), ACCUMULATION x MID -0.106 (n=16), ACCUMULATION x HIGH -0.537 (n=14), BEAR x MID -0.778 (n=12), BEAR x LOW -0.747 (n=10).

## Tests
- First run, before the code existed: `2 errors in 0.43s` (collection: phase_label / phase_trials missing).
- Final: `24 passed` (test_phase_label.py 10, test_phase_trials.py 14). They cover zone lines, BULL/PEAK_WINDOW by the clock, a peak known only at +363 d, the bottom window and TRANSITION, a bottom known after a 100 % rally, sticky ACCUMULATION up to the halving, no lookahead (future crash bars do not change the label), weekly RSI usable only at the week close, incremental = reference, the loader refusing an end past 2025-07-01 and dropping bars at or after the split end, microsecond timestamps, the cost constant from fees.py, fee/funding/net R arithmetic, the funding window (t_in, t_out], exits (target, stop-wins tie, time stop, short mirror, unresolved dropped), T14 events (high/low side, late reclaim, the close 12 bars back outside, one per level per day), T15 via malkan_40_60 (regime gate, green candle, swing low), the cell filters and the verdict rules.

## DECISION (OURS) list
- Knowability: a peak is known 363 d after it with no new high. The bottom is known once a daily close is >= 2 x the lowest low since the peak, and ACCUMULATION then holds until the next halving. Without that, the 2024-03 new high (before the halving) reopened BEAR; the sticky rule follows PRE_REG rule 3. Halvings are known in advance.
- TRANSITION is a sixth label: the bottom window has passed and no bottom is confirmed yet (2019-01-28..05-10, 2022-12-22..2023-07-03). It counts as balance-eligible for T14 when the zone is MID, as the brief excludes only the PEAK and BOTTOM windows.
- Clock and BTC zone from BTC spot 1d. ETH events use the BTC phase and ETH's own weekly RSI zone.
- T14 breach bar = the first bar of an excursion (close before it inside) with close[i-12] inside. Reclaim = the breach bar or one of the next 2 closes strictly inside. Stop = the excursion extreme. The prior day needs at least 20 bars. Futures 1h and fundingRate exist from 2020-01 only (2019-09..12 archive files 404), so T14 starts 2020-01 and funding is 0 before 2020-01 (T15 2017-2019).
- ETHUSDT fundingRate was copied from another worker's cache (F:/MTS/Dumps/backtest/eh_s3_conf/fund), because the fetcher reported 'skip' for ETH into a folder that already held BTC files. Same public archive files.
- T15 swing low = the lowest low from the start of the RSI band run through the signal bar. The Malkan level and tolerance are read from malkan_setup_bull's own defaults (D2 rule).
- All events are taken (no one-position filter); overlap is absorbed by the clustered SE. Exits are touch-fills, stop first, time stop at the bar close. Funding counts records in (entry close, exit bar close].
- phase_calendar.csv covers DEV weeks only. The VALIDATION Holm bound would have been min(1, 15 p); it was not needed.

## Noticed
- The 0-bear-week regime tag is a label problem, not a market fact. A clock-plus-weekly-RSI label gives 100 BEAR weeks (2018, 2021-11..2022-11) in the same DEV span. Studies that split "by regime" with research_kit.regime_tag never saw a bear market. PHASE_LABEL is ready to reuse (phase_label.PhaseLabeler).
- T14 restates the auction-census result in a phase-scoped cell: gross break-even, and taker costs on 60-90 bps stops (fee_r about 0.24) sink it. Its MID-zone cells are the worst, so "range = fade" does not hold on 1h.
- T15's out-of-phase events (BEAR, PEAK_WINDOW, TRANSITION) lose 0.3-1.0 R. A phase gate is a useful kill-switch for the Malkan long even without a proven edge inside the gate.
- The spot_2017 cache (F:/MTS/Dumps/backtest/spot_2017) holds months through 2026-10, i.e. HOLDOUT. This loader never opens a month at or after the split end, but other loaders reading that folder should be checked.
