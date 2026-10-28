# FABIO RULEBOOK (consolidated, source = extracts in scope)
## 1. Rule table
| id | rule (one line, your words) | source rule ids (e.g. FAB-0jM5Y31YJak-R7) | topic (entry/stop/target/management/risk/session/zones/proof) | class | data needed | Tom overlap |
|---|---|---|---|---|---|---|
| FR-01 | Execute only the blueprint; discipline baseline is 66 days | FAB-0KyIEdvVKMQ-R1; FAB-0KyIEdvVKMQ-R10 | management | PSYCH | NONE | NONE |
| FR-02 | Equal risk per execution | FAB-0KyIEdvVKMQ-R2 | risk | RISK | NONE | NONE |
| FR-03 | No size-up after a loss | FAB-0KyIEdvVKMQ-R3; FAB-jasv3L-d8ZE-R1 | risk | RISK | NONE | NONE |
| FR-04 | Daily drawdown circuit breaker / max daily risk | FAB-0KyIEdvVKMQ-R4; FAB-fZlNGWvd2Ko-R1; FAB-LQvv5xgy_ik-R8; FAB-LQvv5xgy_ik-R9 | risk | RISK | NONE | NONE |
| FR-05 | Scale only on profit / risk only the day's profit | FAB-0KyIEdvVKMQ-R5; FAB-0jM5Y31YJak-R9; FAB-fZlNGWvd2Ko-R4 | risk | RISK | NONE | NONE |
| FR-06 | Beginner execution cap: 10 per day | FAB-0KyIEdvVKMQ-R6 | management | RISK | NONE | NONE |
| FR-07 | Journal by session and trigger | FAB-0KyIEdvVKMQ-R7 | management | PSYCH | NONE | NONE |
| FR-08 | Plan must contain four components | FAB-0KyIEdvVKMQ-R8 | management | PSYCH | NONE | NONE |
| FR-09 | Session range pre-estimate via ATR/open behavior | FAB-0KyIEdvVKMQ-R9 | session | CONTEXT | KLINES | NONE |
| FR-10 | CVD pressure before price breakout | FAB-0jM5Y31YJak-R1 | proof | CONTEXT | AGGTRADES | COMPLEMENT |
| FR-11 | First entry on volume plus price confirmation | FAB-0jM5Y31YJak-R2 | entry | SIGNAL | AGGTRADES | COMPLEMENT |
| FR-12 | Stop to break-even after first push / fast break-even | FAB-0jM5Y31YJak-R3; FAB-fZlNGWvd2Ko-R3; FAB-jasv3L-d8ZE-R3 | stop | SIGNAL | KLINES | NONE |
| FR-13 | Minimum 1:3 reward-to-risk on initial trades | FAB-0jM5Y31YJak-R4 | risk | RISK | NONE | NONE |
| FR-14 | Reinvest realized profit into next position | FAB-0jM5Y31YJak-R5 | management | RISK | NONE | NONE |
| FR-15 | Exit when big trades stop pushing / get stopped out | FAB-0jM5Y31YJak-R6; FAB-fZlNGWvd2Ko-R5 | exit | SIGNAL | AGGTRADES | COMPLEMENT |
| FR-16 | Absorption: delta in, price flat; CVD divergence; heavy absorption | FAB-0jM5Y31YJak-R7; FAB-FawPrRUGNpk-R18 (3of3); FAB-002 (o-w5Gxss6T0); FAB-007 (o-w5Gxss6T0) | proof | SIGNAL | AGGTRADES | COMPLEMENT |
| FR-17 | Absorption + reload = sustained move / entry | FAB-FawPrRUGNpk-R10 (3of3); FAB-FawPrRUGNpk-R24 (3of3) | entry | SIGNAL | L2 | COMPLEMENT |
| FR-18 | Escalating aggression into absorbed level -> breakout | FAB-003 (o-w5Gxss6T0) | proof | SIGNAL | AGGTRADES | COMPLEMENT |
| FR-19 | CVD absorption confirms failed auction and day direction | FAB-008 (o-w5Gxss6T0) | entry | SIGNAL | AGGTRADES | COMPLEMENT |
| FR-20 | Trend-following entry: absorption of counter-trend aggression inside momentum | FAB-009 (o-w5Gxss6T0) | entry | SIGNAL | AGGTRADES | COMPLEMENT |
| FR-21 | Take profit at the extreme when big trades sell into it | FAB-0jM5Y31YJak-R8 | target | SIGNAL | AGGTRADES | COMPLEMENT |
| FR-22 | Aggressive seller control entry | FAB-8CWKfoSJu3c-R1 | entry | SIGNAL | AGGTRADES | COMPLEMENT |
| FR-23 | Profit taking based on floating profit | FAB-8CWKfoSJu3c-R2 | management | RISK | NONE | NONE |
| FR-24 | Trail stop loss on profit | FAB-8CWKfoSJu3c-R3; FAB-fZlNGWvd2Ko-R6 | stop | SIGNAL | KLINES | NONE |
| FR-25 | Risk-to-reward targeting, e.g. 1:19 | FAB-8CWKfoSJu3c-R4 | target | RISK | NONE | NONE |
| FR-26 | Position sizing based on market control | FAB-8CWKfoSJu3c-R5 | risk | RISK | L2 | COMPLEMENT |
| FR-27 | Psychological level break control | FAB-8CWKfoSJu3c-R6 | zones | CONTEXT | KLINES | NONE |
| FR-28 | Absorption level reversal exit | FAB-8CWKfoSJu3c-R7 | exit | SIGNAL | AGGTRADES | COMPLEMENT |
| FR-29 | Squeeze level reaction exit | FAB-8CWKfoSJu3c-R8 | exit | SIGNAL | L2 | COMPLEMENT |
| FR-30 | Aggressive buy reversal exit | FAB-8CWKfoSJu3c-R9 | exit | SIGNAL | AGGTRADES | COMPLEMENT |
| FR-31 | Guessed retail liquidity is unreliable | FAB-FawPrRUGNpk-R1 (1of3) | zones | CONTEXT | L2 | SAME |
| FR-32 | Heat-map intensity = level importance | FAB-FawPrRUGNpk-R2 (1of3) | zones | CONTEXT | L2 | SAME |
| FR-33 | Path of least resistance: sum passive orders over 5 levels | FAB-FawPrRUGNpk-R3 (1of3) | proof | SIGNAL | L2 | SAME |
| FR-34 | Rising liquidity lifts the path of least resistance | FAB-FawPrRUGNpk-R4 (1of3) | proof | CONTEXT | L2 | SAME |
| FR-35 | Bid reload in compression | FAB-FawPrRUGNpk-R5 (1of3) | entry | SIGNAL | L2 | SAME |
| FR-36 | Spoofing caution on bid reload | FAB-FawPrRUGNpk-R6 (1of3) | risk | RISK | L2 | NONE |
| FR-37 | Iceberg = hidden reloading | FAB-FawPrRUGNpk-R7 (1of3); FAB-FawPrRUGNpk-R6 (2of3); FAB-FawPrRUGNpk-R7 (2of3) | zones | CONTEXT | L2 | COMPLEMENT |
| FR-38 | Book sweep location: all-time high/low, range extremes, NY high | FAB-FawPrRUGNpk-R8 (1of3) | session | CONTEXT | L2 | SAME |
| FR-39 | Book sweep asymmetric risk | FAB-FawPrRUGNpk-R9 (1of3) | risk | RISK | L2 | NONE |
| FR-40 | Book flip management | FAB-FawPrRUGNpk-R10 (1of3) | management | SIGNAL | L2 | COMPLEMENT |
| FR-41 | Buyers reload absorption sequence | FAB-FawPrRUGNpk-R11 (1of3) | proof | SIGNAL | L2 | COMPLEMENT |
| FR-42 | Scalper aggression confirmation | FAB-FawPrRUGNpk-R12 (1of3) | proof | SIGNAL | AGGTRADES | COMPLEMENT |
| FR-43 | Reload breakout entry and stop | FAB-FawPrRUGNpk-R13 (1of3) | entry | SIGNAL | L2 | COMPLEMENT |
| FR-44 | Reload targets / next liquidity cluster | FAB-FawPrRUGNpk-R14 (1of3); FAB-FawPrRUGNpk-R17 (1of3); FAB-FawPrRUGNpk-R22 (3of3) | target | SIGNAL | L2 | SAME |
| FR-45 | Directional bias prerequisite | FAB-FawPrRUGNpk-R15 (1of3) | other | CONTEXT | AGGTRADES | COMPLEMENT |
| FR-46 | Sellers reload confirmation | FAB-FawPrRUGNpk-R16 (1of3) | proof | SIGNAL | L2 | COMPLEMENT |
| FR-47 | Stop below next liquidity area | FAB-FawPrRUGNpk-R18 (1of3) | stop | SIGNAL | L2 | SAME |
| FR-48 | Sustained move with aggressive market orders | FAB-FawPrRUGNpk-R1 (2of3) | proof | CONTEXT | AGGTRADES | COMPLEMENT |
| FR-49 | Break and retest with reload | FAB-FawPrRUGNpk-R2 (2of3) | proof | SIGNAL | L2 | COMPLEMENT |
| FR-50 | Liquidity cluster wall pattern | FAB-FawPrRUGNpk-R3 (2of3) | proof | CONTEXT | L2 | SAME |
| FR-51 | Stucky Grill pattern | FAB-FawPrRUGNpk-R4 (2of3) | proof | CONTEXT | L2 | SAME |
| FR-52 | Break and protect pattern | FAB-FawPrRUGNpk-R5 (2of3) | proof | SIGNAL | L2 | COMPLEMENT |
| FR-53 | Institutional order distribution | FAB-FawPrRUGNpk-R7 (2of3) | proof | CONTEXT | AGGTRADES | COMPLEMENT |
| FR-54 | Aggressive order squeeze | FAB-FawPrRUGNpk-R9 (2of3) | proof | SIGNAL | AGGTRADES | COMPLEMENT |
| FR-55 | Market micro mechanics confirmation | FAB-FawPrRUGNpk-R10 (2of3) | proof | CONTEXT | AGGTRADES | COMPLEMENT |
| FR-56 | Raised resting bids confirm breakout | FAB-FawPrRUGNpk-R1 (3of3) | proof | SIGNAL | L2 | SAME |
| FR-57 | Fresh liquidity after break fuels move / reload pattern for market control | FAB-FawPrRUGNpk-R2 (3of3); FAB-FawPrRUGNpk-R8 (2of3) | proof | SIGNAL | L2 | COMPLEMENT |
| FR-58 | Aggression stopped at ceiling = partial exit | FAB-FawPrRUGNpk-R3 (3of3) | target | SIGNAL | AGGTRADES | COMPLEMENT |
| FR-59 | No protecting liquidity = retracement expected / break without resting liquidity | FAB-FawPrRUGNpk-R4 (3of3); FAB-FawPrRUGNpk-R6 (3of3) | proof | CONTEXT | L2 | SAME |
| FR-60 | Break plus reloaded liquidity = sustained move | FAB-FawPrRUGNpk-R5 (3of3) | proof | SIGNAL | L2 | COMPLEMENT |
| FR-61 | Levels are areas, not single prices | FAB-FawPrRUGNpk-R7 (3of3) | zones | CONTEXT | L2 | SAME |
| FR-62 | Price above VWAP +1 SD = buyers in control | FAB-FawPrRUGNpk-R8 (3of3) | proof | CONTEXT | KLINES | SAME |
| FR-63 | First touch of wall shows absorption | FAB-FawPrRUGNpk-R9 (3of3) | zones | SIGNAL | L2 | COMPLEMENT |
| FR-64 | Unremoved liquidity keeps bias | FAB-FawPrRUGNpk-R11 (3of3) | proof | CONTEXT | L2 | SAME |
| FR-65 | Expect retracements inside the day's bias | FAB-FawPrRUGNpk-R12 (3of3) | session | CONTEXT | KLINES | NONE |
| FR-66 | No counter-trend long while CVD is falling | FAB-FawPrRUGNpk-R13 (3of3) | entry | SIGNAL | AGGTRADES | COMPLEMENT |
| FR-67 | Wait for buyer protection before long | FAB-FawPrRUGNpk-R14 (3of3) | entry | SIGNAL | L2 | COMPLEMENT |
| FR-68 | Acceptance above level with fresh liquidity = rebound zone | FAB-FawPrRUGNpk-R15 (3of3) | zones | SIGNAL | L2 | COMPLEMENT |
| FR-69 | Break of protected level flips the day's bias | FAB-FawPrRUGNpk-R16 (3of3) | management | SIGNAL | L2 | COMPLEMENT |
| FR-70 | Flat CVD while price rises = no buyer aggression | FAB-FawPrRUGNpk-R17 (3of3) | proof | CONTEXT | AGGTRADES | COMPLEMENT |
| FR-71 | Short target below session low | FAB-FawPrRUGNpk-R19 (3of3) | target | SIGNAL | KLINES | NONE |
| FR-72 | Absorption + reload at Nasdaq effort area | FAB-FawPrRUGNpk-R21 (3of3) | entry | SIGNAL | AGGTRADES | COMPLEMENT |
| FR-73 | Resting liquidity lowered = sellers accept lower | FAB-FawPrRUGNpk-R23 (3of3) | proof | SIGNAL | L2 | SAME |
| FR-74 | Low-variance risk geometry for prop firms | FAB-LQvv5xgy_ik-R1; FAB-LQvv5xgy_ik-R2 | risk | RISK | NONE | NONE |
| FR-75 | Withdraw prop profits to personal account | FAB-LQvv5xgy_ik-R3 | risk | RISK | NONE | NONE |
| FR-76 | Multiple brokerages | FAB-LQvv5xgy_ik-R4 | risk | RISK | NONE | NONE |
| FR-77 | Conservative per-trade risk: 0.5%-1.25% | FAB-LQvv5xgy_ik-R5 | risk | RISK | NONE | NONE |
| FR-78 | Competition three-phase structure | FAB-LQvv5xgy_ik-R6 | session | CONTEXT | NONE | NONE |
| FR-79 | Late-stage aggression | FAB-LQvv5xgy_ik-R7 | session | RISK | NONE | NONE |
| FR-80 | Post-earnings announcement drift | FAB-StaphlRH8NQ-R1 | other | CONTEXT | NONE | NONE |
| FR-81 | Opening range breakout has positive skew | FAB-StaphlRH8NQ-R2 | session | SIGNAL | KLINES | NONE |
| FR-82 | Direction from statistics, timing from order flow | FAB-StaphlRH8NQ-R3 | entry | CONTEXT | AGGTRADES | COMPLEMENT |
| FR-83 | Copy congress committee members | FAB-StaphlRH8NQ-R4 | other | PSYCH | NONE | NONE |
| FR-84 | Option premium harvesting / IV > RV | FAB-StaphlRH8NQ-R5; FAB-StaphlRH8NQ-R6 | other | SIGNAL | NONE | NONE |
| FR-85 | MVRV Z-score smart DCA on Bitcoin | FAB-StaphlRH8NQ-R7 | other | SIGNAL | NONE | NONE |
| FR-86 | Failed auction plus buyer aggression | FAB-fZlNGWvd2Ko-R2 | entry | SIGNAL | AGGTRADES | COMPLEMENT |
| FR-87 | Cover behind new low | FAB-fZlNGWvd2Ko-R7 | target | SIGNAL | KLINES | NONE |
| FR-88 | Break of horizontal level raises continuation probability | FAB-jasv3L-d8ZE-R2 | entry | SIGNAL | KLINES | SAME |
| FR-89 | Positive gamma compresses volatility | FAB-jasv3L-d8ZE-R4 | session | CONTEXT | NONE | NONE |
| FR-90 | Do not cut profit early on choppy days | FAB-jasv3L-d8ZE-R5 | management | PSYCH | NONE | NONE |
| FR-91 | Do not trend-follow on compression days | FAB-jasv3L-d8ZE-R6 | session | CONTEXT | NONE | NONE |
| FR-92 | Endure drawdown to catch the new range | FAB-jasv3L-d8ZE-R7 | management | PSYCH | NONE | NONE |
| FR-93 | Orderflow shows the aggressor; candles do not | FAB-001 (o-w5Gxss6T0) | proof | CONTEXT | AGGTRADES | COMPLEMENT |
| FR-94 | Candle-gap FVG is the wrong definition | FAB-004 (o-w5Gxss6T0) | proof | CONTEXT | KLINES | SAME |
| FR-95 | Real FVG = lowest-volume price inside the value area | FAB-005 (o-w5Gxss6T0) | proof | CONTEXT | AGGTRADES | SAME |
| FR-96 | Price rejects at the volume-defined FVG | FAB-006 (o-w5Gxss6T0) | proof | SIGNAL | AGGTRADES | SAME |
| FR-97 | Heat map predicts volatility regime | FAB-FawPrRUGNpk-R20 (3of3) | session | CONTEXT | L2 | SAME |

## 2. Counts
Counts by class:
| class | count |
|---|---:|
| SIGNAL | 45 |
| CONTEXT | 29 |
| RISK | 17 |
| PSYCH | 6 |
| total | 97 |

Counts by data needed:
| data needed | count |
|---|---:|
| NONE | 26 |
| KLINES | 11 |
| AGGTRADES | 26 |
| L2 | 34 |
| total | 97 |

Counts by Tom overlap:
| Tom overlap | count |
|---|---:|
| SAME | 21 |
| COMPLEMENT | 40 |
| CONFLICT | 0 |
| NONE | 36 |
| total | 97 |

## 3. Testable core
Order of application: location -> context -> trigger -> management. Thresholds are verbatim where the source states one; otherwise UNDEFINED.

### Location
- FR-31, FR-32, FR-33, FR-34, FR-37, FR-50, FR-51, FR-59, FR-61, FR-64, FR-73, FR-94, FR-95, FR-97: liquidity/heat-map levels, icebergs, clusters, walls, Stucky Grill, areas not single prices, VWAP+1 SD, volume-defined FVG. Thresholds: FR-33 uses "five price levels above and below"; FR-62 uses "first standard deviation of session VWAP"; FR-95 uses "70% of the volume" value area and example "24,318 to 24,317". All other location thresholds UNDEFINED.
- FR-09, FR-27, FR-38, FR-65, FR-80, FR-81, FR-89, FR-91: session/regime context. Thresholds: FR-27 example "25,550"; FR-80 "up to 60 days"; FR-81 "first 30 minutes" and "13.5%" skew; FR-09 "ATR or open session behavior" UNDEFINED; FR-38 "New York session high" UNDEFINED; FR-89 "long gamma" UNDEFINED; FR-91 "compression day" UNDEFINED.

### Context
- FR-10, FR-45, FR-48, FR-55, FR-62, FR-70, FR-82, FR-93, FR-94, FR-95, FR-97: order-flow bias and higher-time-frame confirmation. Thresholds: FR-10 "large directional pressure" UNDEFINED; FR-45 "directional bias and probability framework" UNDEFINED; FR-55 "higher time frame" UNDEFINED; FR-70 "CVD is stable" UNDEFINED; FR-93 "big traders" UNDEFINED.
- FR-16, FR-18, FR-19, FR-20, FR-28, FR-30, FR-41, FR-42, FR-46, FR-49, FR-52, FR-54, FR-56, FR-57, FR-60, FR-63, FR-66, FR-67, FR-68, FR-69, FR-72, FR-86, FR-96: absorption/reload/aggression triggers. Thresholds: FR-16 "almost zero" price result; FR-18 "all-time high on volume 4,600 with 812 of delta" (example); FR-19 "failed auction" UNDEFINED; FR-20 "huge amount of aggression" UNDEFINED; FR-33 5 levels; FR-35 "110 contracts" (example); FR-41 "three times" absorption; FR-42 "big trades" UNDEFINED; FR-46 "aggressive and reload fresh liquidity" UNDEFINED; FR-52 "fresh liquidity" UNDEFINED; FR-54 "squeezing the top" UNDEFINED; FR-56 "raised resting bids" UNDEFINED; FR-57 "fresh liquidity" UNDEFINED; FR-60 "reloading liquidity" UNDEFINED; FR-63 "first touch" UNDEFINED; FR-66 "CVD is falling" UNDEFINED; FR-67 "buyers show some kind of protection" UNDEFINED; FR-68 "accept above this level" UNDEFINED; FR-69 example levels "27,870 / 27,850"; FR-72 "Nasdaq effort printed" UNDEFINED; FR-86 "failed auction" UNDEFINED; FR-96 "price will reject" UNDEFINED.

### Trigger
- FR-11, FR-17, FR-22, FR-33, FR-35, FR-40, FR-43, FR-44, FR-47, FR-49, FR-52, FR-54, FR-56, FR-57, FR-60, FR-63, FR-66, FR-67, FR-68, FR-69, FR-71, FR-72, FR-81, FR-84, FR-85, FR-86, FR-87, FR-88, FR-96: entries, exits, stops, targets. Thresholds: FR-11 "volume and confirmation from price" UNDEFINED; FR-13 1:3; FR-17 "absorption + reload" UNDEFINED; FR-22 "sellers completely absorb buyer aggression" UNDEFINED; FR-25 1:19 example and "27,600" target; FR-29 example "25,584" and "25,570"; FR-33 5 levels; FR-35 "110 contracts" example; FR-43 "breakout protected below the reload level" UNDEFINED; FR-44 "next liquidity cluster" UNDEFINED; FR-47 "below the next liquidity area" UNDEFINED; FR-54 "squeeze" UNDEFINED; FR-57 "fresh liquidity" UNDEFINED; FR-60 "reloading liquidity" UNDEFINED; FR-63 "first touch" UNDEFINED; FR-66 "CVD is falling" UNDEFINED; FR-67 "buyers show protection" UNDEFINED; FR-68 "fresh liquidity" UNDEFINED; FR-69 "break this horizontal level" UNDEFINED; FR-71 "way lower than the low" UNDEFINED; FR-72 "Nasdaq effort" UNDEFINED; FR-81 "first 30 minutes" and "13.5%"; FR-84 IV > RV UNDEFINED; FR-85 MVRV Z-score bands UNDEFINED; FR-86 "failed auction + aggression" UNDEFINED; FR-87 "new low" UNDEFINED; FR-88 "break this low" UNDEFINED; FR-96 "price will reject" UNDEFINED.

### Management
- FR-12, FR-15, FR-21, FR-24, FR-28, FR-29, FR-30, FR-40, FR-44, FR-47, FR-58, FR-69, FR-71, FR-87: stops, break-even, trailing, exits, targets. Thresholds: FR-12 "break even" after first push; FR-15 "big trades are not pushing anymore" UNDEFINED; FR-21 "all-time low for the day" and "big traders sell" UNDEFINED; FR-24 "trail aggressively" UNDEFINED; FR-28 "sellers taking back control" UNDEFINED; FR-29 "yellow level" and "25,584" UNDEFINED as a mechanical threshold; FR-30 "aggressive buyers take back control" UNDEFINED; FR-40 "door closes above" UNDEFINED; FR-44 "next liquidity cluster" UNDEFINED; FR-47 "next liquidity area" UNDEFINED; FR-58 "ceiling" UNDEFINED; FR-69 "flip of the auction" UNDEFINED; FR-71 "way lower than the low" UNDEFINED; FR-87 "below this low" UNDEFINED.
- FR-04, FR-05, FR-06, FR-13, FR-14, FR-23, FR-25, FR-26, FR-36, FR-39, FR-74, FR-75, FR-76, FR-77, FR-79: risk and sizing. Thresholds: FR-04 "1%" daily drawdown example; FR-06 "10 execution per day" for beginners; FR-13 1:3; FR-25 1:19 example; FR-74 "60-70%" win rate, 1:1 to 0.75:1, max 1.5:1; FR-77 "1.25%, 0.5% per trade"; FR-23 "$10,000" floating profit example; FR-79 "maximum aggression" UNDEFINED.

## 4. Gaps
- "Big trades" is proprietary/undefined in FAB-0jM5Y31YJak, FAB-FawPrRUGNpk, FAB-fZlNGWvd2Ko, FAB-o-w5Gxss6T0. Needs AGGTRADES with a size threshold.
- "Aggression" has no numeric threshold. Needs AGGTRADES delta/volume threshold.
- "Absorption" has no numeric threshold. Needs AGGTRADES CVD-vs-price divergence or delta-vs-price-result threshold.
- "Reload" / "fresh liquidity" / "resting liquidity" have no numeric thresholds. Needs L2 order-book depth/reload detection.
- "Heat map" / "darker level" / "major liquidity" have no thresholds. Needs L2 resting-order intensity.
- "Path of least resistance" uses 5 levels only as an example; no ratio threshold. Needs L2.
- "Iceberg" requires an iceberg indicator; no detection threshold. Needs L2/AGGTRADES.
- "Spoofing" is cautionary, no detection threshold. Needs L2.
- "VWAP +1 SD" is stated but anchor/reset and session definition are UNDEFINED. Needs KLINES.
- "Fair value gap" procedure uses swing A to B, 70% value area, lowest-volume price; swing selection, bin size, and timeframe are UNDEFINED. Needs AGGTRADES.
- "Failed auction" has no mechanical definition. Needs AGGTRADES/L2.
- "Long gamma" / "positive gamma" has no threshold or measurement. Needs options/L2.
- "Compression day" / "choppy day" have no numeric threshold. Needs KLINES.
- "Big trades get stopped out" has no stop/indicator definition. Needs AGGTRADES.
- "Psychological level" is illustrated by 25,550 only; no general rule. Needs KLINES.
- "MVRV Z-score" bands for capitulation/euphoria are not given. Needs blockchain data, not in scope.
- "Post-earnings announcement drift," "copy congress," "option premium harvesting," and "MVRV DCA" are non-MTS equity/options/Bitcoin hypotheses; no parameters in source.
