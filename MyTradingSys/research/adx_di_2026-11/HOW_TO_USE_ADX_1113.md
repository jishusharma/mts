# How to use ADX / +DI / -DI on BTC (card adx-di-synthesis-1113)

Sources: INV = INVENTORY_1113.md, MAS = MASTERS_1113.md, CRY = CRYPTO_USE_1113.md, MEA = MEASURE_1113.md (branch JIS-NB/adx-measure-1113, not yet on trunk), CEN = CENSUS.md. All in this folder. Numbers are copied from MEA or CEN. Measurement is OURS, one asset, no tuning (n=14; levels 20/25/40), fee 4 bps on 5m-4h only. No orders, no edge claim.

**Result: ADX/DI is a "is there a trend" gauge, not an entry signal. Our data shows no fee-net edge for a DI cross on any frame. The only measurable help is "ADX rising through 25" on 1d, and it works for longs AND shorts.**

## 1. What ADX/DI tells you (SOURCED, MAS)
| Line | Meaning |
|---|---|
| ADX | Trend strength, never direction. Low and flat = stand aside; rising = a trend is building |
| +DI vs -DI | Who is winning. A raw cross whips back and forth in ranges |
| Best use | A gate on another entry, not an entry by itself (all masters agree) |
| High ADX turning down | Warning the move is stretched. Masters disagree on what to do (section 6) |

## 2. By timeframe
| TF | Masters (MAS) | Crypto traders (CRY) | OUR measurement (MEA) | Verdict |
|---|---|---|---|---|
| 5m | Nobody uses it (all rules are in bars, daily examples) | Period 7-10 suggested, no evidence | DI cross n=10270: long -0.049% vs base -0.038%, t -3.3 (worse) | DO NOT USE |
| 15m | Same | Cryptonomist ADX<45 long: fitted, image-only (weak) | Cross: no edge (n=3476, ex +0.001%). ADX through 25 long: n=1837, +0.059% vs -0.022% at 12 bars, t 3.2, one cell of ~48 | DO NOT USE (the one hit is probably chance) |
| 1h | Same | Period 14, marks 20/25 | Cross long n=936: -0.041% vs +0.030% at 12 bars. Through 25 long n=517: +0.182% vs +0.030%, t 1.7 | DO NOT USE as entry; FILTER ONLY |
| 4h | Same | Same | Cross long n=256: -0.071% vs +0.239% at 12 bars. Through 25 long n=122: +0.634% vs +0.239%, t 1.1 | UNDERPOWERED (t under 2) |
| 1d | Raschke and Elder rules are daily (stocks and futures) | Common default | Through 25 long n=34: +2.9/+4.1/+5.6% at 3/6/12 bars vs +0.6/+1.1/+2.3 base, win 65-74%. Short n=33 also beats base (t up to 3.0). Cross n=55: no edge | FILTER ONLY (about 34 events in 9.8 years) |
| 2d | None | Only a Kamolwech TradingView anecdote: n=5 +DI crosses, picked after the fact | Cross + ADX>20 long n=33: -2.4% vs +1.1% at 3 bars, t -1.8. Through 25: n=17 and n=20, long + and short -, they disagree | UNDERPOWERED, cross not supported |
| 5d | None | None found | Every cell n under 30 (best n=13) | UNDERPOWERED (UNKNOWN) |
| 1w | None | None found | Every cell n under 30 (n=2 to 12) | UNDERPOWERED (UNKNOWN) |

## 3. Scalping (1m-15m)
| Question | Answer |
|---|---|
| Does any source support it? | No. Masters: none on intraday (MAS). Crypto: zero measured evidence, nothing on 1m BTC (CRY) |
| What do we measure? | DI cross loses to holding on 5m and 15m after fee (MEA table a). Fading low ADX earns about zero before fee, net about -0.04% = the fee (MEA table b) |
| Closest masters idea | LeBeau: flat/falling ADX, counter-trend 1.5 ATR trade. Never tested by anyone we found, and our fade rules above do not support it (MAS, MEA) |
| How to apply | Do not trade the cross. If you like ADX, read it on 1h-4h as a context line ("trend day or not") and scalp with your own method. A higher-timeframe ADX gate for scalps is UNTESTED |

## 4. Swing long
| Item | Reading |
|---|---|
| Raschke Holy Grail (SOURCED, MAS) | Daily ADX(14) above 30 and rising, then a pullback to the 20 average, buy the resume. Fits a swing long. We have not tested it |
| Elder (SOURCED, MAS) | ADX turning up 4 steps off a low with +DI above -DI. Fits a swing long. Not tested |
| Our closest test | 1d "ADX rises through 25 with +DI above -DI": n=34, beats base at 3/6/12 days (MEA). Thin, and shorts do as well, so read it as "a trend is starting" |
| CCU 2-day rule | In our repo CCU = Crypto Crew University. Its extracts show no ADX use; its 2d tools are 50/200 MA, Stoch RSI, Wave Trend (CRY). INV: his call is a multi-week bearish regime read, no settings, no threshold, no entry/stop |
| Do our numbers support it? | No. 2d cross n=33 is below base (MEA). Whipsaw within 3 bars is 32% DEV, 47% VALIDATION, 50% RECENT (CEN, INV) |
| What does hold up | CCU's three red crosses were real: depth 28.5/34.1/25.0% vs his 36/37/26% (INV, CEN). They are 3 of 44 red 2d crosses (DEV 28, VAL 7, RECENT 9), so "rare" is his word, not confirmed |
| After a red 2d cross | Low is within 1-3 bars in 37% of 35 cases (INV, CEN). A cross is not a timing tool |
| How to apply | As a regime read: higher-frame ADX tells you if a long has trend behind it. Not an entry trigger. Use your own entry |

## 5. Current readings (MEA, last closed bar, 2026-11-13 run)
| TF | ADX | +DI | -DI | State |
|---|---|---|---|---|
| 5m | 25.5 | 24.7 | 21.2 | +DI>-DI |
| 15m | 23.1 | 21.0 | 19.3 | +DI>-DI |
| 1h | 54.1 | 12.9 | 31.6 | -DI>+DI |
| 4h | 53.0 | 6.1 | 41.9 | -DI>+DI |
| 1d | 23.5 | 11.1 | 28.0 | -DI>+DI |
| 2d | 21.8 | 13.5 | 21.8 | -DI>+DI |
| 5d | 24.7 | 18.3 | 22.5 | -DI>+DI |
| 1w | 23.5 | 18.7 | 19.0 | -DI>+DI |

Plain reading (OURS): a strong, mature down move on 1h-4h; no strong trend on 1d-1w (ADX 22-25, -DI slightly ahead). For a swing long there is no higher-frame trend support yet and no 1d "through 25" signal now. Bybit data, not Binance.

## 6. Where sources and our measurement disagree
| Claim | Source | Our data |
|---|---|---|
| ADX 20-40 has the lowest whipsaw; falling from over 40 = exhaustion | USAGE_adx.md (INV) | CEN: bucket effect flips between splits (VALIDATION 20-40 falling whipsaws 75% n=8 vs 14% under 20 n=7; over 40 has n=1). MEA: after a peak over 40, ADX is still above 25 twelve bars later in 92-100% |
| Peak then turn down warns of the end (Elder, LeBeau over 35) | MAS | 4h after a peak: move bigger than average (3.6% vs 2.9%), trend direction wins 57% at 12 bars, n=219 (MEA). Read it as "stretched", not "over" |
| Low ADX means range, fade it (LeBeau; common view) | MAS, CRY | Fading low ADX is about zero or worse; following the DI leader is positive on 1d+ in both ADX states (MEA table b) |
| ADX above 30 = strong trend, trade it (Raschke) | MAS | Not tested as a level filter. Only the 25-cross was tested |
| DI system has an edge as a filter | Vendor claims (CRY) | Oxford Strategies 34y, 42 futures: DI + ADXR graded C, filter adds nothing (MAS). Live Aid: ADX agreeing gave 50% vs 46% (15m) and 49% vs 45% (1h) hit-rate, adds nothing (INV) |
| ~28-bar lag; period 14 vs 8/13 | USAGE_adx.md; Schaap | Lag has no source (INV). Period not tested; we used 14 only |

## 7. Open questions and next test
| Open question | Status |
|---|---|
| Does CCU actually use ADX on 2d? | UNCONFIRMED. No extract mentions it; video AnAx1PanZm4 has no extract file on trunk (INV, CRY). Ask the operator for the video/timestamp |
| Is 1d ADX-through-25 real? | n=34 over 9.8 years; one asset. Needs other symbols (ETH, SOL) and a split into DEV/VALIDATION/RECENT |
| Do masters' rules work (Holy Grail, Elder)? | Never tested on BTC with fees |
| Is a higher-frame ADX a useful gate for a scalp or swing entry? | Never tested |
| Other periods (7, 21)? | Not tested; no tuning rule yet |
| MEASURE caveats | ~150 cells so some t>2 are chance; overlapping windows inflate t; Bybit not Binance (MEA) |

**Next test (card filed):** 1d "ADX rises through 25" and the Holy Grail pullback rule as a gate, on BTC plus 2-3 more symbols, DEV/VALIDATION/RECENT split, fee-net, rule fixed before the run.
