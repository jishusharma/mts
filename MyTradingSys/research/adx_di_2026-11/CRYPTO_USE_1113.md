# ADX / +DI / -DI on crypto: what the web says (2026-11-13)

Method: web search + page fetches 2026-11-13. SOURCED = a named author says it. OURS = our inference.
Fetch limits: tabtrader.com, liberatedstocktrader.com, red.127.pp.ua (Reddit mirror) could not be fetched; quantifiedstrategies is paywalled. Their content is NOT used except where a search snippet is cited and flagged.

## 0. Headline

| Finding | Label |
|---|---|
| No measured, fee-net, out-of-sample ADX/DI backtest on BTC was found. Every BTC number found is a vendor claim, an anecdote, or an image-only chart. | OURS (absence of evidence in this search; not proof of none) |
| Everyone agrees on the idea: ADX = trend strength, not direction; DI cross = direction; ADX > 20-25 = filter. | SOURCED (rows below) |
| Nobody found publishes a win rate for a given period/threshold. One source says so outright. | SOURCED, therighttrader (row 12) |
| "CCU" in our repo = Crypto Crew University (@CryptoCrewUniversity). Our extract of its 8 latest videos has ZERO ADX/DMI mentions; its 2-day tools are 50/200 MA golden cross, Stoch RSI, Wave Trend. The operator's "CCU uses ADX on 2-day" is NOT confirmed by our files or by web search. | OURS, file MyTradingSys/research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md and grep of ccu_DXntdN3jfTg_extract.md (no match for ADX/DMI/directional) |

## 1. CCU / 2-day use

| Item | What was found | Label |
|---|---|---|
| CCU ADX on 2-day | Web search found nothing from Crypto University / Crypto Crew on ADX. UNKNOWN whether the operator's source is a video not in our 8. | OURS |
| Closest public 2-day ADX/DI item | TradingView idea by Kamolwech, BITSTAMP:BTCUSD, 2-day candles: "each time green line crosses above red, BTC rose 23% to 485% over last 5 occurrences". No per-event numbers, no length given, lines not named +DI/-DI explicitly. Five events = tiny sample, picked after the fact. | SOURCED, https://th.tradingview.com/chart/BTCUSD/nfhoxjuI/ |
| Why 2-day is plausible | 2-day bars are slow: few crosses per year, so each cross is a cycle-scale event. A 14-bar ADX on 2-day = 28 calendar days. Few signals also means almost no statistical power. | OURS |

## 2. Settings: what is changed for crypto

| Setting | Stated by | Value | Source |
|---|---|---|---|
| Period | therighttrader | Keep 14 for crypto; crypto daily has weekends so 14 = 14 calendar days; 7 on daily crypto spikes on one wide candle; 21 daily is the calmer option | https://therighttrader.com/learn/indicator-strategies/best-adx-settings |
| Period | Mudrex Learn | 14, "most platforms default", do not over-tune early | https://mudrex.com/learn/adx-average-directional-index-crypto/ |
| Period | PineIndicators (BTC script) | 14, no timeframe advice | https://www.tradingview.com/script/9tlkyuHL-ADX-for-BTC-PineIndicators |
| Period 7-10 | A search-snippet guide (site not fetched, name UNKNOWN) | "7-10 for scalpers on 5m-1h; 14 balanced default; on 15m/1h crossovers give too many false signals without filters" | web search 2026-11-13 result list, https://therighttrader.com/learn/indicator-strategies/best-adx-settings and https://tradingbrokers.com/adx-scalping-strategy/ (attribution of this exact line to one of them unverified) |
| Threshold | Mudrex | Alerts 20, 25, 50. <20 range; 20-25 trend starting; 25-50 strong; >50 late; >75 rare | https://mudrex.com/learn/adx-average-directional-index-crypto/ |
| Threshold | cryptohopper (TradingView) | ADX line 25 as hard filter; ADX filtered out every signal 3 Jun-20 Jul 2020 (ranging) | https://my.tradingview.com/chart/BTCUSDT/JBbayiWx-Crypto-Trading-101-Trading-Bitcoin-With-The-DMI |
| Threshold | lilothebest (TradingView "ADX and DI For Crypto") | ~20 sideways; cross above 30 momentum building; 70-90 near peak. Says "favourite settings for crypto" but does NOT list them. Daily best, 4h second. | https://in.tradingview.com/script/EGurwa95-ADX-and-DI-For-Crypto |
| Threshold | PineIndicators BTC | Entry when ADX crosses above 14, exit when it crosses below 45 (page wording; odd, see section 5), optional 200 SMA filter | https://www.tradingview.com/script/9tlkyuHL-ADX-for-BTC-PineIndicators |
| Threshold (inverse) | Cryptonomist article | Long-only entry when ADX is BELOW 45 (BTC, MATIC, BNB) or 50 (ETH version): buys low-trend-strength lows, not strong trends | https://en.cryptonomist.ch/2023/05/28/trading-strategy-bitcoin-using-adx/ |
| Smoothing | TradingView community scripts | Built-in ta.dmi(diLength, adxSmoothing) uses RMA (Wilder-style, alpha 1/len) for DM, TR and ADX. Scripts exist that swap in SMA/EMA/WMA/ZLEMA. Official Pine manual NOT checked here. | https://in.tradingview.com/script/eqAAiLTU-ADX-DMI , https://id.tradingview.com/script/R3YRg9EF-adx-w-wilders-di-di-dx-adxr-equilibrium-point (community pages; unverified vs manual) |
| TV vs Wilder | OURS | Wilder's book seeds with a simple sum of first 14 values then rolls his smoothing; TV RMA seeds differently, so first ~100 bars differ slightly then converge. Our own cross-check is in TV_CROSSCHECK.md. | MyTradingSys/research/adx_di_2026-11/TV_CROSSCHECK.md |

Summary: for crypto nobody found a credible reason to leave 14/20-25. Only change is "go slower on daily+" (21) or "faster for scalps" (7-10), all stated without evidence. OURS.

## 3. Scalping (1m-15m)

| Claim | Who | Label / source |
|---|---|---|
| 5-15m ADX flips quickly, noisy; a 5m signal can fail if 4h is range-bound; use daily for regime, 4h for entries | Mudrex | https://mudrex.com/learn/adx-average-directional-index-crypto/ |
| 5m: 14 = 70 minutes, filter only; 10 or 7 for faster read; DI cross with ADX < 20 is the chop case | therighttrader | https://therighttrader.com/learn/indicator-strategies/best-adx-settings |
| ADX scalping strategy pages exist (period 7-10 on 5m) with no published results | tradingbrokers | https://tradingbrokers.com/adx-scalping-strategy/ (listed in search; page not fetched) |
| 1-minute BTC ADX: nothing specific found | search | UNKNOWN |
| Crypto 5m scalping scripts (Hilly etc.) use MACD/EMA/ATR, ADX is at most a filter | TradingView authors | https://de.tradingview.com/script/IW1KeAFv-Hilly-s-Advanced-Crypto-Scalping-Strategy-5-Min-Chart (listed, not fetched) |

OURS: scalping evidence = zero measured. ADX lags by design (smoothing of ~2x period), so on 1-5m it confirms a move already half done. Use at most as a "do not scalp mean-reversion when ADX high" gate. Untested.

## 4. Intraday (1h-4h) and swing (1d-2d-1w)

| Claim | Who | Label / source |
|---|---|---|
| Daily = regime, 4h = entries in same direction, 50 EMA bias + 20 EMA timing, ATR stops, 0.5-1% risk | Mudrex | https://mudrex.com/learn/adx-average-directional-index-crypto/ (rules, no results) |
| Daily best, 4h second | lilothebest | https://in.tradingview.com/script/EGurwa95-ADX-and-DI-For-Crypto |
| DMI "suits swing trading": +DI cross up with ADX > 25 long; stop 5%, trailing 2% armed at 7% | cryptohopper | https://my.tradingview.com/chart/BTCUSDT/JBbayiWx-Crypto-Trading-101-Trading-Bitcoin-With-The-DMI (no results given; promotional author bio) |
| Weekly 14 = 14 weeks, position trading | therighttrader | https://therighttrader.com/learn/indicator-strategies/best-adx-settings |
| Cycle-bottom reading: DI+/DI-/ADX levels at 2013 and 2018 bottoms drawn as horizontal lines; "wait for weekly buy signal + Pi Cycle low" | TradingView authors (BTC bottom ideas) | https://id.tradingview.com/chart/BTCUSD/h7IazB2j-BTC-very-near-bottom (listed in search; page not fetched, wording from snippet) |
| ADX at 2-year low = "major move imminent" (volatility squeeze reading, not direction) | KuCoin news flash | https://www.kucoin.com/news/flash/bitcoin-adx-at-2-year-low-bvol7d-at-2-89-signal-major-move-imminent (not fetched) |
| ADX "over 80 correct" on weekly BTC (peak-trend exhaustion reading) | TradingView author | https://in.tradingview.com/chart/BTCUSD/YGFIGKXV-Weekly-chart-with-Wave-Trends-and-ADX-over-80-correct (title only) |

OURS: the credible niche is swing/cycle (1d-1w): few signals, long trends in BTC, ADX regime filter keeps you out of ranges (cryptohopper's 2020 example). That fits "swing long", but no source proves edge.

## 5. Published backtests found (all weak)

| Source | Asset / period | Numbers | Fees | OOS | Verdict |
|---|---|---|---|---|---|
| Cryptonomist 2023 article, 15m data, long when ADX < 45, exit on 200-bar low / 5% stop / 5 days | BTC, MATIC, BNB; dates not given ("last year and a half") | Text has none; all numbers in images, unreadable | not stated | not stated; threshold 45 chosen as best across tests = in-sample optimisation | WEAK |
| TradingView invite-only "[Bybit BTCUSD.P] 7Years Backtest 2,609%" | BTC perp, 7y | 2,609% with 24 trades (from search summary); closed code, uses ADX unknown | UNKNOWN | UNKNOWN | MARKETING |
| PineIndicators "ADX for BTC" | BTC | page shows none | n/a | n/a | NO EVIDENCE |
| Liberated Stock Trader (search snippet) | SPY, 14/25 | CAGR 14.09% vs 13.82% buy and hold | UNKNOWN | UNKNOWN | Equity, not crypto, page not fetched; ~0.3 pt edge |
| QuantifiedStrategies Sep 2024 | S&P 500 | paywalled; says no commissions/slippage | none | n/a | Equity, no crypto |
| Reddit r/algotrading "Backtest results for an ADX trading strategy" Feb 2025 | UNKNOWN | not fetched | UNKNOWN | UNKNOWN | UNREAD |

Page URLs: https://en.cryptonomist.ch/2023/05/28/trading-strategy-bitcoin-using-adx/ ; https://www.tradingview.com/script/qnirD0Kg/ ; https://www.tradingview.com/script/9tlkyuHL-ADX-for-BTC-PineIndicators ; https://www.liberatedstocktrader.com/adx-indicator/ ; https://quantifiedstrategies.substack.com/p/adx-trading-strategy-statistics-facts ; https://red.127.pp.ua/r/algotrading/comments/1irhrcw/backtest_results_for_an_adx_trading_strategy

Oddity: PineIndicators text says entry on ADX crossing ABOVE 14 and stop on crossing BELOW 45. Read literally that exits almost immediately; the page is unclear. Do not rely on it. OURS.

## 6. Claim table

| claim | who | evidence quality | URL |
|---|---|---|---|
| ADX measures trend strength, not direction; Wilder 1978 | Mudrex, TabTrader, CoinMarketCap academy | textbook definition (not a performance claim) | https://coinmarketcap.com/academy/glossary/average-directional-index-adx |
| Use period 14, marks 20/25/50 for crypto, do not over-tune | Mudrex | anecdote | https://mudrex.com/learn/adx-average-directional-index-crypto/ |
| Keep 14 on crypto daily; 7 spikes; 21 calmer | therighttrader | anecdote | https://therighttrader.com/learn/indicator-strategies/best-adx-settings |
| No reliable published win rate for any ADX period/threshold | therighttrader | honest statement; supports our finding | https://therighttrader.com/learn/indicator-strategies/best-adx-settings |
| Higher timeframe sets regime; 5-15m ADX is noisy | Mudrex | anecdote | https://mudrex.com/learn/adx-average-directional-index-crypto/ |
| DI cross valid only if ADX > 25 (BTC 2020 filtered Jun-Jul ranging) | cryptohopper | anecdote, promotional | https://my.tradingview.com/chart/BTCUSDT/JBbayiWx-Crypto-Trading-101-Trading-Bitcoin-With-The-DMI |
| BTC 2-day +DI cross up preceded +23% to +485% in last 5 cases | Kamolwech | anecdote (n=5, no per-event data) | https://th.tradingview.com/chart/BTCUSD/nfhoxjuI/ |
| Buy BTC/MATIC/BNB when 15m ADX < 45 (200-bar-high based), 5% stop, 5-day cap | Cryptonomist | anecdote; threshold fitted; numbers in images | https://en.cryptonomist.ch/2023/05/28/trading-strategy-bitcoin-using-adx/ |
| BTC 7-year 2,609% with ADX-based invite-only script | TradingView vendor | marketing (24 trades, closed code) | https://www.tradingview.com/script/qnirD0Kg/ |
| SPY ADX 14/25 CAGR 14.09% vs 13.82% | Liberated Stock Trader | measured but equity, unverified fees/OOS, snippet only | https://www.liberatedstocktrader.com/adx-indicator/ |
| ADX at 2-year low on BTC signals big move coming | KuCoin news flash | marketing/news, volatility not direction | https://www.kucoin.com/news/flash/bitcoin-adx-at-2-year-low-bvol7d-at-2-89-signal-major-move-imminent |
| BTC cycle bottoms show DI/ADX in the same ranges as 2013/2018 | TradingView authors | anecdote (n=2 cycles) | https://id.tradingview.com/chart/BTCUSD/h7IazB2j-BTC-very-near-bottom |
| TV built-in DMI uses RMA (Wilder-style) smoothing | TradingView community scripts | anecdote, not checked against manual | https://in.tradingview.com/script/eqAAiLTU-ADX-DMI |

## 7. For the synthesis (OURS)

| Point | Implication |
|---|---|
| No measured crypto edge exists publicly | Our own census (CENSUS.md, census.py) is the only real evidence; weigh it above everything here |
| Only credible role found: regime filter (ADX < 20 = skip trend entries) and slow-TF direction (1d-2d DI cross) | Matches "swing long" use; test on 2d/1d BTC with n counted honestly, expect n of ~5-10 per cycle |
| Scalping use: zero evidence | Do not build scalp rules from this; at most a gate |
| CCU claim unconfirmed | Ask operator for the video; do not attribute ADX to CCU in docs |
| Crypto-specific parameter changes are unsupported | Test 14 vs 21 on 1d/2d only; mark as OURS |
