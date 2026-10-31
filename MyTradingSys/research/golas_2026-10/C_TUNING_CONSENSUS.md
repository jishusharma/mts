# GOLAS-C: internet consensus on indicator tuning for BTC (ledger P0-04)

Date 2026-10-31. Builder, card ask-p0-04-golas-tuning-consensus. Start point: the archived GOLAS-C note (2026-09-21) had NO URLs, so none of its values could be re-verified at a URL; they are carried below as UNVERIFIED. All rows here come from pages fetched on 2026-10-31 (fetch tool paraphrases and trims, so quotes are as returned, short). n_sources = distinct domains whose fetched page states the value. Tier: SOURCED = a value a named page states; OURS = a value MTS chose (none here). No value below is validated on BTC data or is an MTS parameter. Pages are education or platform docs (T2/T3); no T1 paper states any of these values.

## Result table (one row per indicator and timeframe)

| Indicator | Timeframe | Value | n_sources | URL and short quote | Tier |
|---|---|---|---|---|---|
| RSI length | all / daily / default | 14 | 3 | https://forklog.com/en/what-the-rsi-is-for-and-whether-it-suits-cryptocurrencies/ "Many use the default 14-day period." ; https://www.tradingview.com/support/solutions/43000502338-relative-strength-index-rsi/ "14 bars is the default." ; https://cryptint-site.pages.dev/declassified/technical-analysis/rsi-crypto "The standard RSI period is 14." | SOURCED |
| RSI length | 4h (medium term) | 14 | 2 | forklog (above) "traders operating on a medium-term horizon apply a 14-day period"; cryptint (above) "The 4-hour chart is the most reliable RSI frame for most crypto traders." (frame claim, not a period) | SOURCED |
| RSI length | intraday / 5m-1h | 7-11 (7 or 9 typical) | 2 | forklog (above) "for intraday trading, a 7-11 day time frame"; cryptint (above) RSI 7 "Used by scalpers on low timeframes", RSI 9 "Common alternative for active traders"; also "Shorter timeframes (5m, 15m, 1h) produce too many false signals during consolidation" | SOURCED |
| RSI length | daily-weekly / swing | 21-30 | 2 | forklog (above) "for long-term trading, a 21-30 day period"; cryptint (above) 20-25 "better for swing traders on higher timeframes" | SOURCED |
| RSI levels | any | 70 / 30 | 1 | tradingview support (above) "any number above 70 should be considered overbought and any number below 30 should be considered oversold." | SOURCED |
| RSI levels | intraday | 80 / 20 | 2 | forklog (above) "traders often widen the bands to above 80 and below 20."; tradingview support (above) "someone might consider any number above 80 as overbought and anything below 20 as oversold." | SOURCED |
| Bollinger Bands | daily (BTC example) | 20 / 2 (SMA, 2 sd) | 2 | https://forklog.com/en/bollinger-bands-using-the-indicator-in-crypto-trading/ "For a daily bitcoin chart, for example, that means a 20-period SMA with a deviation of 2." ; https://www.luxalgo.com/library/indicator/bollinger-bands/ Length default 20, Multiplier default 2.0 | SOURCED |
| Bollinger Bands | 5m to monthly (any) | 20 / 2 | 1 | forklog (above) "The indicator suits any timeframe, including five-minute, hourly, daily, weekly and monthly." | SOURCED |
| Bollinger Bands | length direction | do not go above 20 | 1 | forklog (above) "Setting the period above 20 creates undesirable 'stability' for analysis." | SOURCED |
| Bollinger Bands | intraday / scalping | NOT_IN_DATA (search snippet said BingX suggests 10 / 1.5; page fetch failed) | 0 verified | https://bingx.com/ro/learn/article/how-to-use-bollinger-bands-to-spot-breakouts-and-trends-in-crypto-market : UNVERIFIED | UNVERIFIED |
| MACD | daily and 4h | 12 / 26 / 9 | 1 verified | https://coinpaprika.com/education/macd-indicator-in-crypto-how-it-works-and-key-signals/ standard settings "remain the best general-purpose choice for daily and 4-hour crypto charts." ; https://www.binance.com/en/academy/articles/macd-indicator-explained (search snippet says 12,26,9 default; fetch failed): UNVERIFIED | SOURCED |
| MACD | 1h and 15m | 6 / 13 / 5 | 1 | coinpaprika (above) "Faster settings such as 6/13/5 suit 1-hour and 15-minute charts." | SOURCED |
| MACD | 1h and 4h | 8 / 17 / 9 | 1 | coinpaprika (above) table row; its "tested profitable after costs" note is from equity studies, not crypto | SOURCED |
| MACD | daily and weekly | 24 / 52 / 18 | 1 | coinpaprika (above) "Slower settings such as 24/52/18 suit daily and weekly position trading." | SOURCED |
| VWAP anchor | any (platform) | Session, Week, Month, Quarter, Year (user picks; page gives no default) | 1 | https://www.tradingview.com/support/solutions/43000502018-volume-weighted-average-price-vwap/ "Possible values: Session, Week, Month, Quarter, Year, Decade, Century," | SOURCED (options only; default NOT_IN_DATA) |
| VWAP anchor | BTC 24/7 | daily reset 00:00 UTC; weekly Monday 00:00 UTC; monthly 1st | 1 (weak) | https://cryptint-site.pages.dev/declassified/technical-analysis/vwap "resets at 00:00 UTC each day" / "resets on Monday 00:00 UTC" / "Many traders reset their VWAP analysis on Monday morning UTC." Single low-quality site | SOURCED (T3, no second source) |
| VWAP anchor | event anchored | swing/event date | 1 | same cryptint page: anchored VWAP starts "from a specific event date instead of a fixed session boundary." Event list (ETF approval, FTX) came from a search snippet of dextools.io; page returned 404: UNVERIFIED | SOURCED / UNVERIFIED |

## Carried from the archived 2026-09-21 note, not re-verified (no URL existed)

| Claim | Status |
|---|---|
| MACD divergence read on histogram | UNVERIFIED (MACD 12/26/9 itself is re-sourced above) |
| RSI divergence window 5-30 bars | UNVERIFIED, no page found |
| ATR-normalised thresholds preferred over absolute | UNVERIFIED |
| Weekend divergence noisier on BTC | UNVERIFIED (a search snippet gave a 30-50% weekend-volume figure; not retrieved) |
| CVD / OI divergence rules | UNVERIFIED; see B_INDICATOR_RELATIONS.md, which found no T1/T2 page |

## Flags

- Pages whose fetch failed (marked UNVERIFIED, not used as evidence): binance.com MACD academy, bingx.com RSI and Bollinger, kucoin.com Bollinger and MACD, bitmex.com Bollinger, coinmarketcap Bollinger, stockcharts (SSL error), tabtrader (DNS), dextools anchored VWAP (404). Search-snippet claims that Wilder set 14 in 1978 and that 14 is the platform default are likewise unfetched.
- The TradingView Bollinger and MACD support pages fetched did not state 20/2 or 12/26/9 (they describe inputs only), so they are not cited for those values.
- Every value is a practitioner or platform default. None has a fee-net out-of-sample result on BTC; before any use in MTS each must be labelled OURS and tested.
- cryptint-site.pages.dev is a low-quality aggregator: rows resting on it alone are weak (RSI 7/9, VWAP UTC resets).
