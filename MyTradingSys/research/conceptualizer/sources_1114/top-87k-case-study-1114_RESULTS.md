**Plain answer: at the Sept-Oct top (87.4k) the textbook weekly/daily "divergence outside the Bollinger Band" short did NOT fire - weekly RSI and WaveTrend were still making higher highs. The first honest trend-death evidence was the Oct 13-17 DI cross and ADX drop (about 83k-81k), then the daily lower-high break on Oct 25 (80.2k); the weekly closes below the 50W/20W (74.9k, 69.0k) came too late to trade. In 2019-2025 data these short signals, used alone, lost money on average when the 200-day average was still rising, so they only pay once the 200D has already turned down. No sequence tested beats about 60% false alarms; the single 2026 hit is one episode and not evidence of an edge.**

# top-87k-case-study-1114 (2026-11-14)

Descriptive study (understand, not validate). Data: Binance spot BTCUSDT 15m -> 1H/4H/1D/1W (2019-01..2026-11-13 20:15 UTC; the 11-13 daily and 11-09 weekly bars are partial); spot 1D taker-buy volume 2017-08+ (spot delta = 2*taker_buy - volume); Bybit perp funding (2020-03+) and 1D open interest (2020-08+). Binance fapi is unreachable from this machine, so funding/OI are Bybit. 2011-2017 csvs not used (nothing pre-2017-08 in the signal set). Rules and definitions: PRE_REG.md (committed before outcomes; Amendment 1 adds the "ANY-pivot" divergence after the strict one failed to fire at the top, so it is exploratory). Code: analysis.py. Bootstrap used 600 resamples (PRE_REG said 10,000) and placebo 600 draws, to fit the time box.

## Context
- Phase label (causal, daily 200D rule): 2019-2026 days = BULL 51%, BASE 22%, BEAR 27%.
- 2026 so far: BEAR 230 days (Jan-Aug), BULL 63 days (Sep 1-Nov 11), BASE 24 days (since Nov 12). So by this rule the 87k top happened in a BULL-labelled phase (price above a rising 200D at 70-73k), not in a post-peak bear; by the longer view (ATH 126,200 on 2025-10-06, Jan-2026 high 96.9k, lower high 87.4k) it is a bear-market rally top. Both readings are shown because the signals behave very differently by phase.
- Short-signal events 2019-2025 (all types, daily/weekly) by phase: BULL 406, BASE 103, BEAR 81, no-200D-yet 46. Most history is bull, so aggregate shorts statistics are dominated by 2020-21 and 2023-24 rallies. Always read the phase table.
- Outcome tests: "8/4" = short wins if price falls 8% before rising 4% (45 days); first-touch on daily bars. "mean 30d" = 30-day return after 24 bp round-trip fees. "placebo pctile" = rank of the signal mean vs random same-phase dates (50 = no better than random). Events de-duplicated to 5 days apart.

## 1. The fall in time order (short side; every signal that fired, 1D/1W)
Entry = close of the signal bar. "short to now" = entry to the last close 68,962. "best gain / worst pain" = best and worst excursion from entry to now (a trader must survive the worst pain to collect the gain).
| date | TF | signal | price | short to now % | best gain % | worst pain % | 8/4 test |
|---|---|---|---|---|---|---|---|
| 09-03 | 1D | FAILED_BO | 81270 | 15.1 | 16.9 | 7.5 | L |
| 09-14 | 1D | DIV_RSI_ANY_BB | 78189 | 11.8 | 13.6 | 11.8 | L |
| 09-14 | 1D | DIV_WT_ANY_BB | 78189 | 11.8 | 13.6 | 11.8 | L |
| 09-19 | 1D | FUND_EXT | 81250 | 15.1 | 16.8 | 7.6 | L |
| 09-22 | 1D | OI_EXT | 86209 | 20.0 | 21.6 | 1.2 | W |
| 09-24 | 1D | DIV_WT_ANY_BB | 84410 | 18.3 | 20.0 | 3.3 | W |
| 10-13 | 1D | DI_DEATH | 83169 | 17.1 | 18.8 | 2.1 | W |
| 10-13 | 1D | SEQ_C_ANY | 83169 | 17.1 | 18.8 | 2.1 | W |
| 10-15 | 1D | OI_EXT | 82246 | 16.2 | 17.8 | 3.2 | W |
| 10-17 | 1D | ADX_FALL<25 (after >40) | 81491 | 15.4 | 17.1 | 4.2 | n/a |
| 10-20 | 1D | DI_DEATH | 83028 | 16.9 | 18.6 | 2.3 | W |
| 10-21 | 1D | FUND_EXT | 84093 | 18.0 | 19.7 | 0.3 | W |
| 10-25 | 1D | LH_BREAK | 80154 | 14.0 | 15.7 | 2.3 | W |
| 10-29 | 1D | LH_BREAK | 77992 | 11.6 | 13.4 | 4.1 | L |
| 11-02 | 1W | W_BELOW_50W | 74851 | 7.9 | 9.7 | 1.0 | W |
| 11-03 | 1D | LH_BREAK | 77454 | 11.0 | 12.8 | 4.8 | L |
| 11-04 | 1D | OI_EXT | 80504 | 14.3 | 16.1 | 0.5 | W |
| 11-09 | 1W | W_BELOW_20W | 68962 | 0.0 |  |  | NA |
| 11-09 | 1D | LH_BREAK | 75368 | 8.5 | 10.3 | 0.1 | W |
| 11-11 | 1D | FUND_EXT | 74015 | 6.8 | 8.7 | 0.3 | W |

Faster time frames (same any-pivot divergence, BB poke, RSI>60 at the first high): 4H bearish divergence fired 10 times between Sep 4 and mid-Oct (first Sep 4 16:00, then Sep 6, 7, 10, 24, 28, Oct 1, 3, 5...), 1H fired 21 times from Sep 1. Not scored individually (too many, too small).
What the weekly chart looked like: weekly highs 87.4k (Sep 21), 87.2k, 87.0k, 84.4k, 84.9k, 82.0k, 81.2k, 75.6k - a seven-week staircase of lower highs from the first week. Weekly RSI at the top 61.6 (up from 58.7 and 59.0 in the two prior pivot weeks), weekly WT 21 -> 30 (peak week of Oct 12), i.e. no weekly divergence. The 1D/1W divergences only appear against the August spike (RSI 82 at 80k): daily RSI at 87.4k was 73.9, lower than 82.2 in August.
Daily ADX peaked at 47.6 (Sep 9), crossed below 25 on Oct 17; -DI passed +DI on Oct 13 and again Oct 20.

## 2. False alarms: same signal type, earlier in 2026 (Jan 1 - Aug 31) and in history
W/L/N under the 8/4 test. Early-2026 signals fired mostly in the BEAR phase (Jan-Jun). "Sep-Nov fires" are the ones in the table above.
| signal | TF | Jan-Aug26 fires | W | L | N | Sep-Nov fires | first fall fire | 2019-25 n | 2019-25 win | 2019-25 mean30% |
|---|---|---|---|---|---|---|---|---|---|---|
| CVD_DIV | 1D | 3 | 0 | 3 | 0 | 0 | None | 59.0 | 0.27 | -12.3 |
| DIV_RSI_ANY_BB | 1D | 2 | 0 | 2 | 0 | 1 | 2026-09-14 | 81.0 | 0.27 | -9.3 |
| DIV_RSI_BB | 1D | 2 | 0 | 2 | 0 | 0 | None | 30.0 | 0.17 | -22.8 |
| DIV_RSI_noBB | 1D | 2 | 0 | 2 | 0 | 0 | None | 35.0 | 0.17 | -19.8 |
| DIV_WT_ANY_BB | 1D | 0 | 0 | 0 | 0 | 2 | 2026-09-14 | 74.0 | 0.27 | -10.1 |
| DI_DEATH | 1D | 5 | 3 | 2 | 0 | 2 | 2026-10-13 | 59.0 | 0.39 | -4.9 |
| FAILED_BO | 1D | 5 | 2 | 3 | 0 | 1 | 2026-09-03 | 70.0 | 0.21 | -11.7 |
| FUND_EXT | 1D | 2 | 1 | 1 | 0 | 3 | 2026-09-19 | 37.0 | 0.22 | -8.8 |
| LH_BREAK | 1D | 2 | 0 | 2 | 0 | 4 | 2026-10-25 | 32.0 | 0.28 | -3.0 |
| OI_EXT | 1D | 0 | 0 | 0 | 0 | 3 | 2026-09-22 | 42.0 | 0.38 | -0.8 |
| SEQ_C_ANY | 1D | 0 | 0 | 0 | 0 | 1 | 2026-10-13 |  |  |  |
| W_BELOW_20W | 1W | 1 | 1 | 0 | 0 | 1 | 2026-11-09 | 19.0 | 0.47 | 0.9 |
| W_BELOW_50W | 1W | 0 | 0 | 0 | 0 | 1 | 2026-11-02 | 12.0 | 0.42 | -3.1 |

Read: early-2026 false alarm counts are 2 (daily divergence, both L), 3 (CVD_DIV, all L), 3 of 5 (failed breakout, L), 2 of 5 (DI cross, L), 2 of 2 (lower-high break, L). Signals that were mostly right in the fall (DI death, lower-high break, 4H) were right because the fall was big, not because they were more selective.

## 3. Do these signals work as shorts across history? (DEV 2019-2023, VALIDATION 2024-2025, 2026 excluded)
| signal | tf | period | n | win (+8 before -4) | mean 30d % | CI95 mean30% | placebo pctile |
|---|---|---|---|---|---|---|---|
| CVD_DIV | 1D | DEV | 44 | 0.27 | -15.1 | -24.1 .. -7.1 | 0.0 |
| CVD_DIV | 1D | VAL | 15 | 0.27 | -3.9 | -11.5 .. 3.5 | 62.0 |
| DIV_RSI_ANY_BB | 1D | DEV | 59 | 0.27 | -12.1 | -20.5 .. -4.5 | 0.0 |
| DIV_RSI_ANY_BB | 1D | VAL | 22 | 0.27 | -2.0 | -6.3 .. 2.7 | 75.0 |
| DIV_RSI_ANY_BB | 1W | DEV | 6 | 0.17 | 3.1 | -16.9 .. 21.2 | 88.0 |
| DIV_RSI_ANY_BB | 1W | VAL | 10 | 0.3 | -8.3 | -19.6 .. 2.3 | 34.0 |
| DIV_RSI_BB | 1D | DEV | 23 | 0.17 | -27.6 | -45.1 .. -12.2 | 0.0 |
| DIV_RSI_BB | 1D | VAL | 7 | 0.14 | -6.8 | -18.3 .. 1.9 | 38.0 |
| DIV_RSI_BB | 1W | DEV | 3 | 0.0 | 7.3 | -14.0 .. 34.9 | 87.0 |
| DIV_RSI_BB | 1W | VAL | 3 | 0.33 | -6.0 | -25.8 .. 23.5 | 38.0 |
| DIV_RSI_noBB | 1D | DEV | 27 | 0.15 | -24.3 | -39.9 .. -10.0 | 0.0 |
| DIV_RSI_noBB | 1D | VAL | 8 | 0.25 | -4.7 | -15.4 .. 3.4 | 50.0 |
| DIV_RSI_noBB | 1W | DEV | 4 | 0.0 | 11.8 | -6.4 .. 30.0 | 96.0 |
| DIV_RSI_noBB | 1W | VAL | 3 | 0.33 | -6.0 | -35.9 .. 23.5 | 41.0 |
| DIV_WT_BB | 1D | DEV | 18 | 0.17 | -25.5 | -39.5 .. -12.5 | 0.0 |
| DIV_WT_BB | 1D | VAL | 6 | 0.33 | -1.8 | -15.9 .. 8.5 | 64.0 |
| DIV_WT_BB | 1W | DEV | 3 | 0.0 | 7.3 | -14.0 .. 34.9 | 90.0 |
| DIV_WT_BB | 1W | VAL | 2 | 1.0 | 18.6 | 13.8 .. 23.5 | 99.0 |
| DI_DEATH | 1D | DEV | 45 | 0.38 | -6.9 | -18.4 .. 3.6 | 26.0 |
| DI_DEATH | 1D | VAL | 14 | 0.43 | 1.2 | -4.7 .. 7.1 | 90.0 |
| FAILED_BO | 1D | DEV | 54 | 0.19 | -12.8 | -20.3 .. -5.5 | 2.0 |
| FAILED_BO | 1D | VAL | 16 | 0.31 | -7.9 | -16.0 .. -0.2 | 29.0 |
| LH_BREAK | 1D | DEV | 26 | 0.27 | -3.3 | -12.1 .. 4.4 | 70.0 |
| LH_BREAK | 1D | VAL | 6 | 0.33 | -1.4 | -12.4 .. 7.8 | 76.0 |
| OI_EXT | 1D | DEV | 33 | 0.36 | 0.6 | -6.4 .. 7.0 | 96.0 |
| OI_EXT | 1D | VAL | 9 | 0.44 | -5.5 | -16.2 .. 4.4 | 46.0 |
| W_BELOW_20W | 1W | DEV | 13 | 0.46 | -0.7 | -10.5 .. 9.7 | 79.0 |
| W_BELOW_20W | 1W | VAL | 6 | 0.5 | 4.4 | -2.6 .. 11.3 | 91.0 |

Phase split (all of 2019-2025; n / win / mean 30d %):
| c | n_BULL | win_BULL | mean30_BULL | n_BASE | win_BASE | mean30_BASE | n_BEAR | win_BEAR | mean30_BEAR |
|---|---|---|---|---|---|---|---|---|---|
| CVD_DIV 1D | 37 | 0.27 | -8.4 | 9 | 0.11 | -19.1 | 8 | 0.38 | 0.7 |
| DIV_RSI_ANY_BB 1D | 62 | 0.27 | -6.7 | 6 | 0.33 | -20.0 | 6 | 0.5 | -0.3 |
| DIV_RSI_ANY_BB 1W | 12 | 0.33 | 2.7 | 3 | 0.0 | -19.0 | 1 | 0.0 | -40.1 |
| DIV_RSI_BB 1D | 19 | 0.21 | -14.3 | 5 | 0.2 | -19.0 | 3 | 0.0 | -12.5 |
| DIV_RSI_BB 1W | 6 | 0.17 | 0.7 |  |  |  |  |  |  |
| DIV_WT_ANY_BB 1D | 57 | 0.3 | -6.9 | 6 | 0.17 | -26.7 | 2 | 1.0 | 11.1 |
| DIV_WT_ANY_BB 1W | 12 | 0.33 | 7.1 | 3 | 0.0 | -19.0 | 1 | 0.0 | -40.1 |
| DIV_WT_BB 1D | 16 | 0.31 | -15.8 | 5 | 0.0 | -27.1 |  |  |  |
| DIV_WT_BB 1W | 5 | 0.4 | 11.9 |  |  |  |  |  |  |
| DI_DEATH 1D | 30 | 0.37 | -6.5 | 9 | 0.56 | 2.5 | 14 | 0.5 | 1.0 |
| FAILED_BO 1D | 44 | 0.2 | -8.1 | 15 | 0.13 | -14.8 | 6 | 0.33 | 6.7 |
| FUND_EXT 1D | 33 | 0.24 | -8.5 | 2 | 0.0 | -1.4 | 2 | 0.0 | -21.2 |
| LH_BREAK 1D | 9 | 0.22 | -1.4 | 11 | 0.45 | -0.7 | 11 | 0.18 | -4.1 |
| OI_EXT 1D | 16 | 0.62 | 6.0 | 10 | 0.2 | -15.4 | 16 | 0.25 | 1.7 |
| W_BELOW_20W 1W | 10 | 0.4 | 1.4 | 4 | 0.5 | 1.2 | 3 | 0.67 | 4.0 |

Reading it in plain words:
- The Bollinger filter is not a rescue: strict divergence outside BB lost on average in DEV (mean 30d -22.8% over 30 daily events for the RSI version, placebo percentile 0, i.e. worse than random same-phase dates). 83% of them hit the +4% stop first (win rate 17% on +8/-4). Strong uptrends print divergences repeatedly; the first one is rarely the top.
- In the BULL-labelled phase every daily short trigger here had mean 30d below zero except OI_EXT (62% win, n=16); the weekly ones are slightly positive on 5-12 events. In BEAR phase the DI-death, weekly MA breaks and failed-breakout show small positive means, but n is 3-14 each (not significant).
- Weekly WaveTrend divergence outside BB (DIV_WT_BB 1W, n=5, mean +11.9%, 100th placebo percentile) is the one short that stood out, and it is five events. Treat as a lead to look at, not a finding.
- Funding extreme and OI extreme: funding extreme was negative in DEV (-12.0%, n=26); OI extreme was about neutral. Both fired repeatedly during the fall (3 times each) and were right in the fall only.

## 4. Which trend-change sequence caught it with the fewest false alarms
Sequences (pre-registered): A = divergence then a daily close below the low between the two highs; B = A plus (weekly close under 20W or -DI>+DI); C = divergence then a DI death within 30 days. "_ANY" = the looser divergence.
Short side:
| sequence | period | n | win | mean 30d % | CI95 | placebo pctile |
|---|---|---|---|---|---|---|
| SEQ_A | DEV | 7 | 0.0 | -3.3 | -24.8 .. 16.0 | 64 |
| SEQ_A | VAL | 5 | 0.2 | -3.6 | -18.2 .. 8.0 | 59 |
| SEQ_A_ANY | DEV | 13 | 0.38 | -2.5 | -18.3 .. 11.7 | 68 |
| SEQ_A_ANY | VAL | 5 | 0.4 | -2.8 | -17.9 .. 7.8 | 52 |
| SEQ_B | DEV | 7 | 0.0 | -3.3 | -27.7 .. 16.5 | 60 |
| SEQ_B | VAL | 5 | 0.2 | -3.6 | -18.3 .. 8.0 | 54 |
| SEQ_B_ANY | DEV | 11 | 0.36 | -4.4 | -23.3 .. 12.5 | 51 |
| SEQ_B_ANY | VAL | 5 | 0.4 | -2.8 | -16.9 .. 7.9 | 52 |
| SEQ_C | DEV | 8 | 0.25 | -35.3 | -88.4 .. 13.8 | 0 |
| SEQ_C | VAL | 3 | 0.67 | 7.1 | -2.7 .. 17.1 | 92 |
| SEQ_C_ANY | DEV | 19 | 0.21 | -14.7 | -37.4 .. 6.2 | 3 |
| SEQ_C_ANY | VAL | 9 | 0.44 | 2.9 | -4.2 .. 9.4 | 92 |

Fires in 2026: {'SEQ_C_ANY': 1} (SEQ_A and SEQ_B, strict and ANY, fired zero times in 2026; the reason was not investigated - the lower-high break alone first fired on Oct 25 at 80.2k; only SEQ_C_ANY fired - once, Oct 13 at 83,169, +17.1% to now, worst pain 2.1%).
Plain reading: the sequence that caught this fall with the fewest false alarms in 2026 is "divergence (loose) then DI death" - one fire, one hit. Across 2019-2025 the same sequence has 28 events, 29% win (8/4), mean 30d -9.1%, placebo 17th percentile in ALL, DEV poor (-14.7%) and VAL slightly positive (+2.9%, 9 events). So this is a nice story for one episode and nothing more. The strict versions (A/B) lost 92% of the time under 8/4 (12 events). Nothing here supports "short every divergence and ride" as a rule; what supports shorting in the fall is the phase/structure sequence: 200D already flat-to-down, daily lower highs, DI death.
Riding to the reset (median forward short return from the signal, by phase, 90 / 180 days): the median 180-day short return after a divergence signal is negative in every phase (BULL -9% to -20%, BASE -23% to -27%, BEAR -12% to -29%), and the share of positive 180-day outcomes is only 11%-40%. Riding works only when the cycle top is real, which these signals alone do not tell in advance.

## 5. Mirror: bear-phase bottoms (what marked the turn)
Entry = close of the signal bar; "x% above low" is entry vs the exact daily low. Low dates are daily lows of the spot series.
| bottom | low | first marks and when | what confirmed the turn |
|---|---|---|---|
| 2018-12 | 12-15 3,156 | daily bull div (RSI and WT, outside lower BB) 12-11 (-3d, +7%): early, stopped by the next leg; 12-18 (+4d, +16%): win; CVD_DIV_UP 12-15 (low day, +2%): win | SEQ_A_UP 12-19 (+5d, +16%) win; higher-low break 2019-02-18 (+66d, +24%); weekly 20W reclaim 2019-03-18 (+100d, +26%) |
| 2020-03 | 03-13 3,782 (V-shape) | no daily/weekly divergence at all; FAILED_BD 03-09 (7,930, -3d) was a false alarm (price fell another 52%); 4H divergence 03-17 (+4d) | HL_BREAK 04-06 (+25d, +94% above low); weekly 20W/50W reclaim 04-27 (+52d). V-bottoms are not marked by divergence sequences |
| 2022-11 | 11-21 15,476 | funding negative extreme 11-15 (-5d, +9%), 4H divergence 11-15; FAILED_BD on the low day 11-21 (+2%): win | HL_BREAK 12-03 (+13d, +9%) win; weekly bull div 12-05 (+21d, +10%) win; weekly 20W reclaim 2023-01-09 (+56d, +35%) |
| 2026-02 | 02-06 60,000 | FUND_NEG 02-08 (+3d, +17%): L; daily bull div 02-27 (+22d, +10%): W | SEQ_A_ANY_UP 03-04 (+27d, +21%) lost - the Feb low was retested (62.5k 02-23, 65.0k 03-23) and undercut in June |
| 2026-06/07 | 07-01 57,800 (3.7% under the Feb low) | weekly bull div (all variants) 06-15 (-9d, +9.5%): L; daily bull div 06-28 (-2d, +3.1%): W; FUND_NEG 06-19 | SEQ_A_UP 07-05 (+5d, +10%) win; HL_BREAK 08-19 (+50d, +20%) win; weekly 20W reclaim 08-17 (+54d) |
Pattern: the cleanest two-step marks were 2018-12 and 2026-06/07 (a bullish divergence on a lower low, then a daily close above the high between the two lows). 2022-11 was marked by a negative-funding extreme and a failed breakdown on the low day. 2020-03 had nothing before a +94% rally. In 2018-12, 2022-11 and 2026-06/07 the first mark came 2-9 days before the low (3-10% above it) and the confirming close came 5-13 days after (+9% to +16% above the low); 2020-03 and 2026-02 did not follow that pattern.
Long-side base rates, same tests (DEV/VAL):
| signal | tf | period | n | win (+8 before -4) | mean 30d % | CI95 mean30% | placebo pctile |
|---|---|---|---|---|---|---|---|
| CVD_DIV_UP | 1D | DEV | 13 | 0.54 | 0.2 | -9.7 .. 10.0 | 20.0 |
| CVD_DIV_UP | 1D | VAL | 1 | 0.0 | 24.7 | 24.7 .. 24.7 | 87.0 |
| DIV_RSI_BB_UP | 1D | DEV | 15 | 0.4 | 5.8 | -4.2 .. 14.3 | 60.0 |
| DIV_RSI_BB_UP | 1D | VAL | 1 | 0.0 | -12.0 | -12.0 .. -12.0 | 15.0 |
| DIV_WT_BB_UP | 1D | DEV | 9 | 0.44 | 8.6 | 2.0 .. 16.5 | 70.0 |
| DIV_WT_BB_UP | 1D | VAL | 1 | 1.0 | 31.4 | 31.4 .. 31.4 | 88.0 |
| FAILED_BD | 1D | DEV | 25 | 0.2 | -1.0 | -7.1 .. 5.3 | 6.0 |
| FAILED_BD | 1D | VAL | 9 | 0.56 | 1.1 | -5.8 .. 7.9 | 18.0 |
| FUND_NEG | 1D | DEV | 22 | 0.36 | 10.4 | -0.0 .. 23.6 | 90.0 |
| FUND_NEG | 1D | VAL | 18 | 0.17 | 2.1 | -2.0 .. 5.9 | 21.0 |
| HL_BREAK | 1D | DEV | 44 | 0.5 | 9.3 | 0.5 .. 18.8 | 93.0 |
| HL_BREAK | 1D | VAL | 11 | 0.27 | 5.8 | -1.9 .. 13.6 | 62.0 |
| W_ABOVE_20W | 1W | DEV | 14 | 0.57 | -0.4 | -10.2 .. 9.8 | 23.0 |
| W_ABOVE_20W | 1W | VAL | 5 | 0.2 | -3.2 | -16.0 .. 8.7 | 11.0 |

Long sequences:
| sequence | period | n | win | mean 30d % | CI95 | placebo pctile |
|---|---|---|---|---|---|---|
| SEQ_A_ANY_UP | DEV | 13 | 0.38 | 1.6 | -7.2 .. 11.1 | 29 |
| SEQ_A_ANY_UP | VAL | 2 | 0.5 | 1.8 | -9.6 .. 13.2 | 49 |
| SEQ_A_UP | DEV | 9 | 0.44 | 1.0 | -10.7 .. 14.5 | 30 |
| SEQ_A_UP | VAL | 1 | 1.0 | 19.3 | 19.3 .. 19.3 | 80 |
| SEQ_B_ANY_UP | DEV | 12 | 0.42 | 1.6 | -7.9 .. 11.3 | 32 |
| SEQ_B_ANY_UP | VAL | 2 | 0.5 | 1.8 | -9.6 .. 13.2 | 47 |
| SEQ_B_UP | DEV | 6 | 0.5 | 4.7 | -10.4 .. 21.3 | 54 |
| SEQ_B_UP | VAL | 1 | 1.0 | 19.3 | 19.3 .. 19.3 | 85 |
| SEQ_C_ANY_UP | DEV | 11 | 0.45 | 15.7 | 3.1 .. 27.9 | 96 |
| SEQ_C_ANY_UP | VAL | 4 | 0.0 | -6.9 | -18.3 .. 2.9 | 10 |
| SEQ_C_UP | DEV | 6 | 0.33 | 15.5 | -4.5 .. 37.2 | 87 |
| SEQ_C_UP | VAL | 1 | 0.0 | -24.0 | -24.0 .. -24.0 | 2 |

Longs in BEAR phase (n / win +12 before -6 / mean 30d %):
| c | n_BULL | win_BULL | mean30_BULL | n_BASE | win_BASE | mean30_BASE | n_BEAR | win_BEAR | mean30_BEAR |
|---|---|---|---|---|---|---|---|---|---|
| CVD_DIV_UP 1D | 2 | 0.5 | 5.4 | 4 | 0.25 | -0.1 | 7 | 0.71 | 3.6 |
| DIV_RSI_BB_UP 1D | 1 | 0.0 | -12.0 | 4 | 0.5 | 10.4 | 9 | 0.44 | 0.1 |
| DIV_WT_ANY_BB_UP 1D | 5 | 0.0 | -7.9 | 14 | 0.5 | 4.8 | 17 | 0.41 | 2.9 |
| DIV_WT_ANY_BB_UP 1W |  |  |  |  |  |  | 2 | 1.0 | 18.6 |
| DIV_WT_BB_UP 1D | 1 | 0.0 | 13.7 | 4 | 0.5 | 11.9 | 4 | 0.75 | 9.9 |
| DI_BIRTH 1D | 20 | 0.2 | 6.7 | 11 | 0.55 | 10.8 | 12 | 0.17 | -3.6 |
| FAILED_BD 1D | 6 | 0.33 | -3.4 | 15 | 0.33 | 0.3 | 12 | 0.25 | -1.9 |
| FUND_NEG 1D | 17 | 0.24 | 9.0 | 11 | 0.36 | 12.3 | 12 | 0.25 | -1.9 |
| HL_BREAK 1D | 29 | 0.34 | 4.4 | 8 | 0.62 | 15.8 | 15 | 0.53 | 4.0 |
| W_ABOVE_20W 1W | 5 | 0.4 | -1.1 | 4 | 0.5 | 11.3 | 7 | 0.57 | 2.2 |

Reading: HL_BREAK (higher low, then close above the high between the two lows) is the only long trigger with a positive CI in DEV (n=44, +9.3%, CI +0.5..+18.8, placebo 93) and it still drops to a CI that includes zero in VALIDATION (n=11, +5.8%). In BEAR phase specifically HL_BREAK has 15 events at 53% win and +4.0% mean. Negative funding extreme was a better flag in DEV (+10.4%, n=22) than in VAL (+2.1%). Among long sequences only SEQ_C_ANY_UP has a DEV CI above zero (+3.1..+27.9, n=11) and its VALIDATION is -6.9% (n=4); the rest straddle zero. The +12/-6 test breaks even at a 33% win rate, so the 40-57% win rates are not by themselves an edge after the placebo check.

## BTC now (descriptive levels and states, no advice; data to 2026-11-13 20:15 UTC)
| item | state |
|---|---|
| price / 200W SMA | 68,962 vs 200W SMA 68,001 (1.4% above); 20W 74,096, 50W 75,107; daily 200D 73,095 (price below it, phase BASE since 11-12) |
| lows already made | 60,000 (02-06), 62,510 (02-23), 65,000 (03-23), 59,131 (06-01), 57,800 (07-01); weekly low this week 67,568 |
| 1D | RSI 25.4, WT -74.1, close under the lower BB (70,519), ADX 25.7 rising, -DI 35.1 vs +DI 9.8 |
| 4H | RSI 24.5, WT -78.7, ADX 54.2, -DI 34.6 vs +DI 8.7, price just above the lower BB (67,702) |
| 1W | RSI 41.7, WT 9.3, lower BB 57,820 (far below). Weekly momentum is not as oversold as at the Feb low (RSI 29.0, WT -54) or the Jun/Jul low (RSI 38.2, WT -43) |
| divergence | none bullish at this low: RSI is lower now (25.4) with price 19% above the 07-01 low (RSI 37.2); the last daily swing lows are 79.8k (10-15), 79.2k (10-24), 76.3k (10-30) and today's, each lower |
| funding (Bybit, daily sum of 3 prints) | last 10 days +0.00011 to +0.00029, around its 365d 90th percentile 0.00022; 365d 10th percentile -0.00007. At the 2022-11, 2026-02 and 2026-06 lows funding had gone negative; it has not now |
| open interest (Bybit linear) | 72,297 BTC = 99.7th percentile of 365 days, +29% from 56,150 on 09-21 and +6.5% on 11-13 alone while price fell 3.5%: positions were added into the fall, not removed |
| spot delta (Binance, taker buy - sell) | 30d +8.5k BTC, 14d +4.5k, 7d +1.4k, today -0.7k: spot takers net buying during the decline, so far |
| levels above, nearest first | 70.5k (1D lower BB), 74.1k (20W), 75.1k (50W) / 76.4k (11-06 high), 81.2k (11-04 lower high), 84.9k, 87.4k (09-21 high) |
| levels below | 68.0k (200W SMA, now), 65.0k and 62.5k (March/Feb weekly lows), 60.0k (Feb low), 57.8k (Jul low; lower BB 1W) |
Bottom sequence by past patterns (what would still be missing, not a call): a falling-price low with funding turned negative and open interest dropped; a bullish divergence on a lower low; then a daily close above the last lower-high between the two lows (HL_BREAK-style). None of these is present today. Negative funding preceded the lows of 2022-11, 2026-02 and 2026-06; the divergence plus reclaim pair marked 2018-12 and 2026-06/07.

## What this study cannot say
- No big-trade / order-flow data was used (task scoped to price, funding, OI, spot delta). Spot delta is a daily taker-flow proxy, not a footprint.
- Funding/OI start 2020 (Bybit); pre-2020 funding/OI/CVD-in-futures not tested; 4H/1H only from 2019 and only counted for the case.
- Sequence results are small (n 7-28) and the 2026 episode is in-sample by construction.
