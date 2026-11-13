# Iteration 3 merge: other_layers

Sources: argon only. Rows 20: AGREED 0, SINGLE 20, CONFLICT 0, UNVERIFIED 1 (rows needing a quote that no transcript match supported). Verified quotes below: 17.
Only one model ran this topic, so no row can be AGREED; every row is SINGLE. Pattern, ledger and fix columns are assigned by rule from the source row (code column, numbers, transfer words) and the ledger column matches video id plus two shared content words; both are first-pass labels, not a re-read.

## Items

| id | item | model verdict | pattern | in ANSWER_LEDGER? | fix type |
|---|---|---|---|---|---|
| OL-01 | Regular divergence is strongest at 3 to 10 bars; beyond 10 (15, 20, 25, 50) it is diluted. | SINGLE | 4 | N | re-code |
| OL-02 | Reverse divergence (PRD/NRD) bar count stated as 5 to 50 here, vs less than 15 earlier in the same video. | SINGLE | 1 | N | re-frame |
| OL-03 | 5-Star GFS long requires Monthly RSI > 60, Weekly RSI > 60, and Daily RSI near 40 (all 14-period); whereas in XFO49JlODxI 7-Star means a ... | SINGLE | NEW | N | test |
| OL-04 | GFS scans Nifty 500 stocks using current 14-month and 14-week RSI >= 60 plus 14-day RSI crossing 40, not a 20-bar rolling regime on 1h ... | SINGLE | 5 | N | re-frame |
| OL-05 | Entry is a buy-stop above the signal candle's high, with stop loss below that candle's low and 2:1 risk-reward. | SINGLE / UNVERIFIED | 4 | N | re-code |
| OL-06 | Malkan's framework uses RSI 40/60 and price action; WaveTrend and 4h BTCUSDT are never mentioned in any Malkan transcript. | SINGLE | NEW | N | test |
| OL-07 | Dual-timeframe Bollinger Band strategy: higher TF supports at middle band while lower TF touches lower band; requires 4x-6x ratio between timeframes. | SINGLE | 2 | N | extract |
| OL-08 | Small-body spinning top with long shadows and high exhaustion volume; says he ignores RSI, Bollinger Bands, and ADX when this appears. | SINGLE | 2 | N | extract |
| OL-09 | Grades divergences into 3/5/7-star (and Class A/B/C in cQ-y1oULkBw); exact grading parameters are withheld. | SINGLE | 2 | N | extract |
| OL-10 | Scale out 35% to 50% of the position at first target and trail the remainder. | SINGLE | 2 | N | extract |
| OL-11 | Krown defines hidden bullish divergence strictly inside uptrends (and hidden bearish inside downtrends) as trend continuation. | SINGLE | NEW | N | test |
| OL-12 | Uptrend RSI holds 40-80, downtrend holds 20-60, and ranging holds 40-60 (rather than 30-70). | SINGLE | NEW | N | test |
| OL-13 | Places stop on the opposite side of the compression zone and confirms breakouts above the 50th BBWP percentile with a momentum oscillator pointing the same ... | SINGLE | 4 | N | re-code |
| OL-14 | Daily (00:00 UTC) is the gold-standard timeframe for crypto; kcMnnQr1VFg also uses 252 trading days as alternate BBWP lookback. | SINGLE | 5 | N | re-frame |
| OL-15 | Top-4 framework (reversal candle, 2x 30-day volume, BBWP > 85, RSI divergence/MACD cross) signals major tops; zones (3-5) and range edges also core. | SINGLE | NEW | N | test |
| OL-16 | Requires Daily, Weekly, or Monthly timeframe and scales out 20% to 85% of holdings (80 to 85% or as little as 20%). | SINGLE | NEW | N | test |
| OL-17 | Trendlines must anchor to confirmed swing highs/lows and require 3 touches (Three touches makes it a trend) to be valid. | SINGLE | 4 | N | re-code |
| OL-18 | Expect 2-3 major liquidation cascades/year; monitor perp funding rates (1h/4h/8h) and shallow weekend order-book liquidity. | SINGLE | 5 | N | re-frame |
| OL-19 | Crypto spot volume can be faked via wash trading; cross-check against a composite index or CME Bitcoin futures. | SINGLE | 2 | N | extract |
| OL-20 | The 200-week SMA (~4 years of price) is Bitcoin's primary historical macro support/cycle line. | SINGLE | 4 | N | re-code |

## Evidence

#### OL-01 SINGLE
> "So I will say that less than 10 bars is the most powerful divergence. It should be between three and 10. Right? It goes above 10, 15, 20, 25, 50 and then it keeps getting diluted."
**Source GPS: Wvq1TZh8aF0 | MIDDLE**

#### OL-02 SINGLE
> "number of bar should be between five to fifty and both the point should be about sixty if it's a positive edge divergence"
**Source GPS: GbXnw_tNMtw | END**

#### OL-03 SINGLE
> "To trade on the long side you have to find such trades whose 14 month RSI is above 60 weekly RSI should be above 60 The daily RSI i.e. 14 day RSI must be near 40"
**Source GPS: -CBvFi40sIQ | BEGIN**

#### OL-04 SINGLE
> "this particular screener runs on Nifty 500 points, along with this, I have the applied filter of 14 week RSI great than or equal to 60"
**Source GPS: -CBvFi40sIQ | MIDDLE**

#### OL-05 SINGLE
UNVERIFIED: no quote from the model files was found in the transcript (no video id); no quote given.

#### OL-06 SINGLE
> "RSI is also 0 to 100 and we have divided it into three parts which is 40 and 60, meaning bearish below 40, bullish above 60"
**Source GPS: Wvq1TZh8aF0 | BEGIN**

#### OL-07 SINGLE
> "हमेशा हायर टाइम फ्रेम और लोअर टाइम फ्रेम के बीच में चार से छह गुने का फर्क होना चाहिए। फोर टू सिक्स टाइम्स।"
**Source GPS: fgN6QBFY3Ss | MIDDLE**

#### OL-08 SINGLE
> "spinning top small body long shadows long volume trend down"
**Source GPS: XFO49JlODxI | END**

#### OL-09 SINGLE
> "created this reverse divergence between a 3 star 5 star and 7 star based on certain more parameters advanced"
**Source GPS: GbXnw_tNMtw | MIDDLE**

#### OL-10 SINGLE
> "And at least you should exit 50% to 35% of the quantity. Rest if you do a little more trailing then"
**Source GPS: Wvq1TZh8aF0 | END**

#### OL-12 SINGLE
> "In an uptrend, your RSI generally will hold between 40 and 80."
**Source GPS: INOCBmqQupc | MIDDLE**

#### OL-13 SINGLE
> "stop on the opposite side of the compression zone"
**Source GPS: kcMnnQr1VFg | END**

#### OL-14 SINGLE
> "the rule by asset the daily is a gold standard for most cryptos for slower markets Like equities the weekly earns the top slot"
**Source GPS: _t_XIBrcjRk | MIDDLE**

#### OL-15 SINGLE
> "if three of the four align, then you're probably at the very least at a major top"
**Source GPS: 7IxfsuD2wCM | BEGIN**

#### OL-16 SINGLE
> "at least a daily time frame, but preferably like a weekly or monthly depending upon how much history the asset has"
**Source GPS: 7IxfsuD2wCM | BEGIN**

#### OL-17 SINGLE
> "Rule number one, a trend line may only be anchored to swing points or swing highs and swing lows, a confirmed high or a confirmed low"
**Source GPS: 14bxwxC8gBQ | BEGIN**

#### OL-18 SINGLE
> "realistically in crypto or should I say Bitcoin, especially altcoins, you see two to three of these events per year"
**Source GPS: P3rDSh187TE | BEGIN**

#### OL-20 SINGLE
> "This 200 simple on the weekly, which is basically four years of price in one line, that's Bitcoin's one of its most favorite indicators"
**Source GPS: -NXzJs5JRks | MIDDLE**
