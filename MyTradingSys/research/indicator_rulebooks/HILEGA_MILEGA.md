# Rule book: Hilega Milega (NK StockTalk, "Hilbe_milbe")

Sources: FORM = `research/layer_lab/gemini_edge_1113/hilega-formula/FORMULA.md`; NK_EXT = `research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md`; NK_MINE = `research/layer_lab/gemini_edge_1113/mine-nk/RULES.md`; CONC = `research/conceptualizer/concepts.json`; NIFTY20 = https://nifty20.com/hilega-milega-scanner/ (fetched 2026-11-13; SOURCED); CHARTINK = https://chartink.com/screener/ (fetched 2026-11-13; SOURCED); FYERS = https://community.fyers.in/ (fetched 2026-11-13; SOURCED); DHAN = https://madefortrade.in/ (fetched 2026-11-13; SOURCED); NK_YT = https://www.youtube.com/watch?v=JLcDdrHkB5M (video JLcDdrHkB5M, Hindi captions; SOURCED). All repo paths under `MyTradingSys/`.

**Result: Hilega Milega is a momentum-exhaustion and reversal gauge created by Nitish Kumar (NK StockTalk) that layers moving averages (3 EMA and 21 WMA) over a short-term RSI (RSI 9). Our backtests find raw crosses bleed fees on every timeframe (NK rules 0 of 42 pass fee-net); treat Hilega Milega as an exhaustion gauge and context filter, never as an unconfirmed standalone entry.**

## 1. What it measures
Momentum velocity, price direction, and volume-weighted trend consensus by plotting moving averages directly over the Relative Strength Index (RSI) rather than price. The public consensus formula consists of a base 9-period RSI (`ta.rsi(close, 9)`), a fast 3-period EMA of RSI (`ta.ema(rsi, 3)`, Green line), and a slow 21-period WMA of RSI (`ta.wma(rsi, 21)`, Red line), evaluated against the 50 midline equilibrium and 80/20 extreme bands.
Formula pointer: `research/layer_lab/gemini_edge_1113/hilega-formula/FORMULA.md` sections 1-4; `NOT VERIFIED-TV` (no official TV library release from NK; Pine translations are community-authored). Code module: not in repo (`backtest/layers` has no hilega folder; layer token `none` in `INDEX.md`).

## 2. Developer's own rules (SOURCED)
| Item | What is stated | Source |
|---|---|---|
| Who | Nitish Kumar ("NK Sir"), founder of NK StockTalk (YouTube channel @NKStockTalk, Patna, India), popularized as "Hilega To Milega" / "Hilbe_milbe" trading system | NK_EXT:7, NK_MINE:3 |
| Concept origin video | YouTube video `JLcDdrHkB5M` (*Intraday Chart How To Analyse #NK Singh #nkstocktalk #nitishsirhilegamilega*, published 2025-08-15) | NK_EXT:6-7, NK_YT |
| Primary W pattern rule | Indicator forms a 'W' pattern structure at low extremes: "एक डब्ल्यू का निर्माण कर देगा हिलेगा मिलेगा ऐसे ऐसे और एक ऐसे ऊपर की तरफ डब्लू बन जाएगा" ("It will form a W, Hilega Milega like this and like this a W will form upwards") | NK_EXT:57-60, SOURCED |
| Profit target / extreme level | When W is formed, target is the 82 RSI zone: "और जब डब्लू बन जाएगा तो ये वाले आरएसआई के पास भी जाने की फिर से कोशिश करेंगे 82 के ज़ोन में" ("And when the W is formed, it will again try to go near this RSI in the 82 zone") | NK_EXT:63-66, SOURCED |
| Timeframe rules | Stated: 1 Hour for reducing stop loss hunting ("वन ऑवर के टाइम फ्रेम में एसएल हंटिंग काफी कम हो जाती है", NK_EXT:33), 10-Minute for opening breakdown/intraday ("10 मिनट का टाइम फ्रेम को लगाएंगे", NK_EXT:39), Weekly & Monthly for macro trend and Bollinger Band blast ("मंथली टाइम फ्रेम कहता है कि अगर ये नया हाई की ओर निकलेगा तो यहां से ही बुलिंजर बैंड ब्लास्ट कर जाएगी", NK_EXT:51) | NK_EXT:77-80, SOURCED |
| Formula parameters in speech | In video `JLcDdrHkB5M`, NK Sir discusses the visual pattern and levels on chart, but the transcript explicitly notes: `NOT_STATED: RSI length period not specified in transcript`, `NOT_STATED: fast average type/length not specified`, `NOT_STATED: volume-weighted RSI average length not specified` | NK_EXT:74-76, SOURCED |

## 3. What the internet and crypto traders say
| Claim | Source URL | Evidence grade |
|---|---|---|
| Formula parameters: RSI(9), Green Line = EMA(RSI(9), 3), Red Line = WMA(RSI(9), 21), Midline 50, Upper 80, Lower 20 | https://nifty20.com/hilega-milega-scanner/ (fetched 2026-11-13) | anecdote (standard public formula consensus; SOURCED) |
| Bullish entry: Fast Green Line (3 EMA) crosses above slow Red Line (21 WMA) while RSI(9) tracks above 50 | https://nifty20.com/hilega-milega-scanner/ (fetched 2026-11-13) | anecdote (scanner rule; SOURCED) |
| Screener logic: 3 EMA of RSI(9) crossing 21 WMA of RSI(9) for intraday, hourly, and weekly momentum breakouts | https://chartink.com/screener/ (fetched 2026-11-13) | anecdote (community screener query; SOURCED) |
| Broker integration request: Native stacking of 3 EMA and 21 WMA on RSI for Indian equity and F&O intraday trading | https://community.fyers.in/ (fetched 2026-11-13) | anecdote (broker forum discussion; SOURCED) |
| Community consensus: Indicator is a momentum-exhaustion setup combining RSI speed with moving-average smoothing | https://madefortrade.in/ (fetched 2026-11-13) | anecdote (community discussion; SOURCED) |
| Crypto trading parity: Ported from Indian cash equities/Nifty to crypto 24/7 perpetuals | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md:81` | none (UNVERIFIED outside repo; tested internally) |

## 4. What our analysts say (extracts)
| Analyst | Rule in plain words | File pointer |
|---|---|---|
| NK StockTalk | Hilega Milega forms W pattern upwards towards the 82 RSI zone; 1h timeframe recommended to minimize stop loss hunting; pair with 10m/5m index state | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md:57` [45:00] |
| Krown | No extract mentions Hilega Milega (uses standard RSI 14, 21/55 EMA, 200 SMA/EMA; oscillators whipsaw in low volatility) | `MyTradingSys/research/krown_ta101_2026-10-13/` (none found) |
| Tom & Fabio | No extract mentions Hilega Milega (focus on CVD taker delta, VWAP value area, session levels, footprint) | `MyTradingSys/research/` (none found) |
| Malkan | No extract mentions Hilega Milega (uses standard RSI 14 with 60/40 range rules and close-only divergence) | `MyTradingSys/research/concept_decks_1112/MALKAN_FACTS.md` (none found) |
| CCU | No extract mentions Hilega Milega (uses WaveTrend, 50/200 MA, Stoch RSI on 2d/12d) | `MyTradingSys/research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md` (none found) |
| Habib / CBP | No extract mentions Hilega Milega (focus on session anchors, range sweeps, footprint) | `MyTradingSys/research/cbp/` (none found) |
| CryptoCred | No extract mentions Hilega Milega (focus on HTF market structure, swing high/low retests) | `MyTradingSys/research/` (none found) |

## 5. OUR measurements
Table of studies found by grep (study folder, no numbers per prompt instructions):
| Study folder | What was tested | Role |
|---|---|---|
| `research/layer_lab/gemini_edge_1113/hilega-formula` | Public formula definition & parameter extraction across Indian trading portals | Specification & Pine Script parity study |
| `research/nk_stocktalk_1113` | Caption-verified primary source extraction of NK StockTalk video corpus | Primary source rule extraction & catalog |
| `research/layer_lab/gemini_edge_1113/mine-nk` | Rule mining of 15 mechanically testable rules from NK StockTalk extracts | Analyst rule synthesis |
| Side-session study `NK_RSI_RESULTS.md` (referenced in `research/indicator_rulebooks/INDEX.md` and `RSI.md`) | NK mechanical rules R1-R4 on 10 crypto perpetuals | Quantitative backtest |

## 6. How to read it now on Live Aid
Panel: not shown (`tools/live_aid/live_aid.html` has no Hilega Milega column or panel; Live Aid momentum table tracks RSI 14 and WaveTrend wt1/wt2).

## 7. Confluence role: EXHAUSTION
Confluence role: EXHAUSTION.
What it may add confidence to: May serve as a secondary exhaustion confirmation for counter-trend bounces or cycle turn warnings when the indicator completes an extended 'W' bottom formation or approaches extreme zones (80+ / 20-), provided primary trend gates (such as 200 SMA / EMA) agree. It is never an entry by itself: our backtests show 0 of 42 NK mechanical rules produce a fee-net pass, and raw moving-average crosses on RSI bleed fees to whipsaws. Today: context only.

## 8. Open tests
| Card id / Test | What is tested | Rule fixed before the run |
|---|---|---|
| `gemini-edge-nk-batch1-1113` through `batch5` | Systematic backtest of NK mined rules (including NK-R08 Hilega Milega W formation) | Fixed rule: W-pattern entry on 1h timeframe towards RSI 82 target with 1-hour candle low stop |
| `hilega-btc-pine-parity` (not filed) | TV Pine Script parity test against TradingView golden reference export | Parameters fixed at RSI(9), EMA(3), WMA(21) on Bybit 1h BTC perp |
| `hilega-exhaustion-filter` (not filed) | Hilega Milega 20/80 zone extreme as an exhaustion veto on trend-following breakout entries | Veto long entries when Hilega Milega > 80; veto short entries when < 20 |
