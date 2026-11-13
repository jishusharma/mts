# Rule book: WaveTrend Oscillator (LazyBear, "WT_CROSS_LB")

Sources: FORM = `backtest/layers/FORMULAS.md` s20; SNAP = `wavetrend_2026-10-17/source_snapshot/WT_Crosses_lonestar108_jFQn4jYZ.pine.txt`; ATLAS = `wavetrend_2026-10-17/RESULT.md`; DISP = `wavetrend_2026-10-17/DISPOSITION_2026-10-19.md`; C30 = `wavetrend_c30_retest_2026-11-04/RESULT.md`; EXTS = `wavetrend_2026-10-17/EXTERNAL_SETUPS.md`; USE = `tv_favorites_2026-11/USAGE_wavetrend.md`; CCU = `yt_feed_2026-10-31/CCU_RULES_2026-10-31.md`; TV1 = https://www.tradingview.com/script/2KE8wTuF-Indicator-WaveTrend-Oscillator-WT/ and TV2 = https://www.tradingview.com/script/jFQn4jYZ-WaveTrend-with-Crosses-LazyBear/ (both fetched 2026-11-13 by Builder indicator-rulebooks-1113; the fetch tool returns a model summary, so quoted fragments are SOURCED in meaning, exact wording UNVERIFIED). All paths under `MyTradingSys/research/` unless they start with `backtest/`.

**Result: WaveTrend is a "how stretched is this swing" gauge with a cross dot. The author calls the dot a signal only when it sits beyond the band; our tests find bare dots lose after fees on every timeframe, and the trend gate helps only the sell side. Use the zone as a phase column, not the dot as an entry.**

## 1. What it measures
Distance of the typical price from its EMA, scaled by the average deviation (a CCI-style channel index), smoothed twice: wt1 = fast wave, wt2 = 4-bar SMA of wt1 (the "signal"). FORM s20.1: `ap=(h+l+c)/3; esa=EMA(ap,10); d=EMA(|ap-esa|,10); ci=(ap-esa)/(0.015*d); wt1=EMA(ci,21); wt2=SMA(wt1,4)`. Code `backtest/layers/wavetrend/wavetrend.py`. Parity: spreadsheet golden series only, `NOT VERIFIED-TV` (FORM s20.4: "no TradingView export, so NOT Pine-runtime parity"). Zone tags and the cross convention (tie bar skipped) are OURS (FORM s20.2).

## 2. Developer's own rules (SOURCED)
| Item | What is stated | Source |
|---|---|---|
| Who | LazyBear, "a port of a famous TS/MT indicator" (TV1); Pine header `@author LazyBear`, title "WaveTrend with Crosses [LazyBear]", shorttitle WT_CROSS_LB (SNAP:2, 6); the Crosses page on TradingView is published by lonestar108 | TV1, SNAP, TV2 |
| Inputs | Channel length 10, average length 21; levels OB 60 / 53, OS -60 / -53 (SNAP:7-12) | SNAP |
| Plot | zero line gray; 60 and 53 red; -60 and -53 green; wt1 green, wt2 red (SNAP:23-30) | SNAP |
| Sell | Above the upper band and "crosses down the signal (dotted line)": "usually a sell signal" | TV1 |
| Buy | Below the lower band and crossing up through the signal: "a good buy signal" | TV1 |
| Other use | The marked crossovers are "not the only useful signals" | TV1 |
| Page does NOT state | calculation, exact band numbers (in the code only), signal-line setting, timeframe, stops, exits, any win rate | TV1 |
| Crosses page | Description only: wavetrend oscillator "enhanced with wavetrend cross visualization" plus bar-colour highlights. It states no levels and no rule | TV2 |

Note: USE section 2 quotes lonestar108 as saying the dots matter "especially when occurring in the overbought or oversold areas". The fetched page text does not contain that sentence. Treat that USE quote as UNVERIFIED.

## 3. What the internet and crypto traders say
| Claim | Source | Grade |
|---|---|---|
| Fade crosses beyond the bands; persistent trends can keep it extreme while price runs against the fade; do not trade a cross alone | EXTS family A (LazyBear and thomcam pages) | anecdote (definition level, T3) |
| Cross with volume filter, VWMA trend, Supertrend or squeeze agreement improves signals | EXTS families F, G, H (Maydo, jadamcraig, 03.freeman, ForexResearchLabs) | anecdote; the squeeze / Heikin Ashi claim is rejected for unrealistic fills (EXTS G) |
| Crosses on low timeframes whipsaw; WT divergence preferred over RSI divergence | EXTS and `wavetrend_2026-10-17/METHOD_AND_MTS.md` (Reddit r/Daytrading June 2024, r/TradingView threads) | anecdote |
| Market Cipher B uses WaveTrend as its wave engine; anchor wave then smaller trigger wave | USE source 3 | UNVERIFIED (paraphrase, no URL in USE) |
| No T1/T2 (peer-reviewed or costed) validation of a WaveTrend edge was found | EXTS "Method note" | none |

## 4. What our analysts say
| Analyst | Rule | Pointer |
|---|---|---|
| CCU | On the 12-day chart, WT dipping into the green zone = extreme selling exhaustion; passing above the red zone = time to think about profits (cycle top) | CCU rows 24-26 (OGAIlXwmV1Q 00:01:24, 00:01:51, 00:04:36) |
| Operator | "Buying in a downtrend is invalid": trend gate on dots; WT_CROSS_LB is on his TradingView chart | tested as C30; `wavetrend_2026-10-17/LIVE_NOTE_2026-10-27.md` |
| Krown, Tom, Fabio, Malkan | no WaveTrend rule found in the extracts this pass (not exhaustively grepped; the Gemini lane can) | none |

## 5. OUR measurements (BTC)
| Study | What | n | Result | Verdict |
|---|---|---|---|---|
| ATLAS | 9 frozen cells, 5m-1h, DEV 2022-01..2024-06, gross | W01 3,893; W09 947 | 0 of 9 pass the gross screen; W01 conjunction mean -1.43 bps (SE 1.08) vs random clock -0.11 | W01-W03, W09 FAIL; W04-W08 INCONCLUSIVE (DISP) |
| DISP | audit of the C1 divergence detector | - | W07/W08 do not measure the written confirmed-WT-pivot divergence (detector confirms price pivots only) | W07/W08 invalid for divergence |
| C30 | bare dots, band 53, fee-net 0.14%, 15m/30m/1h, 12-bar exit | 509 cells with n>=30 | 126 have CI entirely below 0; none entirely above. 15m buy -0.131%, sell -0.202%; 1h buy -0.342%, sell -0.295% | DO NOT USE (bare dot) |
| C30 | trend gate (SMA200) | - | sell dots: 15m with-trend -0.062% vs against -0.305%; 1h +0.079% vs -0.562%. Buy dots with-trend not better (15m -0.141 vs -0.122) | CONTEXT ONLY (sell side) |
| C30 | 15m sell + RSI>=60 with-trend | 257 / 170 days | net +0.008% [-0.134, +0.149], Holm p 1.0 | UNDERPOWERED |
| C30 | 1h sell + divergence with-trend | 22 / 20 days | net +0.804% [-0.152, +1.759]; retest entry n 19 net +1.117% [+0.007, +2.227], Holm p 0.92, 120 cells in the family | a lead, UNDERPOWERED (needs about 2,165 event-days) |
| C30 | buy with RSI<=40 + trend gate | 238 / 144 days | 15m net -0.187% [-0.303, -0.070], Holm p 0.040 (negative) | DO NOT USE |
| C30 | 96 session cells, Holm m=96 | - | 0 survivors | - |

Regime mix (C30): 130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%). DEV only; VALIDATION unread, HOLDOUT never loaded. Per timeframe: 5m DO NOT USE; 15m DO NOT USE; 30m DO NOT USE; 1h CONTEXT ONLY at best (zone), sell-divergence lead UNDERPOWERED; 4h, 1d, 12d UNTESTED (ATLAS had no 4h/1d cell; CCU uses 12d).

## 6. How to read it now on Live Aid
Panel "Momentum": columns wt1, wt2, WT zone, WT cross per timeframe (`MyTradingSys/tools/live_aid/live_aid.html`, Momentum table). Read the zone: beyond +-53 = stretched. A cross alone is not a call.

## 7. Confluence role: EXHAUSTION
May add confidence to a sell setup that already has the trend gate (price below the 200 SMA) and a level; may add a "do not buy yet" veto when 1h/4h sits below -53 in a downtrend (buying the oversold dot is negative, C30). Not an entry: no fee-net out-of-sample pass exists.

## 8. Open tests
| Test | Status |
|---|---|
| Corrected C1 divergence detector (confirmed WT pivots), count-only, then a new PRE_REG | DISP says needed; card `wavetrend-c1-v2` is listed in LAYERS.md |
| 1h sell dot + divergence + trend gate on more symbols / longer history (about 2,165 event-days) | not filed as a study |
| 4h / 1d / 12d zone as a phase column (CCU's use) | UNTESTED |
| Pine-runtime parity check on TradingView for WT_CROSS_LB | not done (no VERIFIED-TV) |
| Squeeze + WT agreement (EXTS families G, H) on the same events | not filed |
