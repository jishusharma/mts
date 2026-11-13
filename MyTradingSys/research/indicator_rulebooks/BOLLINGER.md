# Rule book: Bollinger Bands (Bollinger 1980s / 2001)

Sources: FORM = `backtest/layers/FORMULAS.md` s22; SRC = `research/bollinger_2026-10-14/SOURCES.md`; R2R = `research/bb_range_to_range_2026-11-04/RESULT.md`; DANCE = `research/bb_dance_2026-10-30/RESULT.md`; VERD = `research/VERDICTS.csv`; LA = `tools/live_aid/`; JB = https://www.bollingerbands.com/bollinger-band-rules (22 rules, fetched 2026-11-13); SC = https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/bollinger-bands (StockCharts ChartSchool, fetched 2026-11-13); BOOK = John Bollinger, "Bollinger on Bollinger Bands", McGraw-Hill, 2001 (ISBN 978-0071373685, primary canon). All repo paths under `MyTradingSys/` unless stated otherwise.

**Result: Bollinger Bands measure relative high/low and volatility dispersion around an SMA. The creator states a band touch is merely a "tag" (continuation first), not a reversal signal; our tests show range band-to-band fades lose after fees across all sessions (0 of 6 cells positive, -0.12% to -0.15%), while band walk persistence depends on %B distance rather than bar count.**

## 1. What it measures
Measures price dispersion relative to an intermediate simple moving average, creating dynamic volatility-adaptive envelopes.
Formula pointer: `backtest/layers/FORMULAS.md` section 22 (`VERIFIED-TV 2026-10-17` parity with TradingView `ta.bb`). Code modules: `tools/live_aid/live_aid_indicators.js` (`bollinger`), `backtest/layers/alerts/live_bb_top_reversal.py`, and `research/bb_range_to_range_2026-11-04/study.py`. Chosen definition: `mid = SMA(close, n)`, `sd = POPULATION_STDEV(close, n)`, `upper = mid + mult * sd`, `lower = mid - mult * sd`. Standard defaults: n=20, mult=2.0 (SOURCED: FORM s22). %B is `(close - lower) / (upper - lower)`; BandWidth is `(upper - lower) / mid`.

## 2. Developer's own rules (SOURCED)
| Item | What is stated | Source |
|---|---|---|
| Who & Year | John Bollinger, developed in early 1980s; codified in "22 Rules for Using Bollinger Bands" and the book "Bollinger on Bollinger Bands" (McGraw-Hill, August 2001, ISBN 978-0071373685) | JB, BOOK, SRC:116 |
| Core definition | Bands provide a relative definition of high and low: price is high at the upper band and low at the lower band (Rule 1) | JB, BOOK |
| Tag vs Signal | A touch or tag of an outer band is NOT a signal by itself; it calls for study, not an automatic trade (Rule 6) | JB, BOOK, SRC:75 |
| Continuation vs Reversal | In strong trends price can walk or ride the upper or lower band (Rule 7). A close outside the band is first a continuation sign, not a reversal; many volatility breakout systems rely on this (Rule 8) | JB, BOOK, SRC:76 |
| Parameter scaling | Default 20 SMA / 2.0 SD is a starting point (Rule 9). Middle band should reflect intermediate trend (Rule 10). Scale multiplier with average length: at length 50 increase multiplier to ~2.1; at length 10 reduce multiplier to ~1.9 to maintain comparable containment (Rule 11) | JB, BOOK, SRC:79 |
| Moving average math | Simple moving average is standard because standard deviation math requires an SMA; if using exponential bands, both mid and SD must use the EMA (Rules 12-13) | JB, BOOK, SRC:80 |
| Price distribution | Price distributions have fatter tails than a Gaussian normal curve; approximately 88-90% of price closes sit inside default bands, not 95% (Rule 14) | JB, SC, SRC:31,81 |
| %B indicator | %b = (price - lower) / (upper - lower); scales position from 0 (lower) to 1 (upper); unconstrained (can go <0 or >1). Used for pattern recognition, divergence, and trading systems (Rules 15-16) | JB, BOOK, SRC:82 |
| BandWidth & The Squeeze | BandWidth = (upper - lower) / mid; measures volatility relative to the average. Best known for spotting "The Squeeze" (volatility contraction preceding a breakout) and trend changes (Rules 18-19) | JB, BOOK, SRC:83 |
| Chart patterns | Used to clarify classic patterns: W-bottoms (reaction low below lower band, bounce toward mid, second low holding above lower band) and M-tops (Rule 5) | JB, SC, SRC:41,78 |
| Non-collinear confluence | Never combine indicators derived from the same price series; combine bands with momentum, volume, sentiment, or open interest that measure different dimensions (Rules 3-4) | JB, BOOK, SRC:77 |
| Timeframe | Operates on any timeframe and most markets provided bars contain sufficient trading activity; bands do not give continuous advice, they identify setup conditions (Rules 20-22) | JB, BOOK, SRC:84 |

## 3. What the internet and crypto traders say
| Claim | Source URL | Evidence grade |
|---|---|---|
| Band-touch reversal (fade outer band to mid/opposite) | LuxAlgo Tag Reversion: https://www.luxalgo.com/library/concept/bollinger-band-tag-reversion/ | anecdote (T3, concept description; no trade sample or costed net) |
| Walking the bands continuation | LuxAlgo Band Walk: https://www.luxalgo.com/library/concept/band-walk/ | anecdote (T3, definition of consecutive closes on/beyond outer band) |
| Bitcoin futures profitability (20-day vs 60-day) | Day et al. (Applied Economics Letters 2023): https://ideas.repec.org/a/taf/apeclt/v30y2023i11p1437-1443.html | measured (T1, AHPR >20% at 20-day, >50% at 60-day; abstract read, sample/costs paywalled) |
| Contrarian vs trend on equity index | Lento et al. (Appl. Fin. Econ. Letters 2007): https://ideas.repec.org/a/taf/raflxx/v3y2007i4p263-267.html | measured (T1, net of costs BB does not beat buy-and-hold; contrarian beat trend) |
| Regime-dependent crypto mean-reversion | Coinquant 78 Backtests: https://www.coinquant.ai/blog/building-a-mean-reversion-strategy-in-cryptocurrency-markets-evidence-from-78-backtests | measured (T2, Binance spot 2022-2024; bull +16.3%, sideways -2.2%, bear -40.6%; fee rate omitted) |
| Squeeze breakout with Keltner Channel | CXO Advisory (LeCompte 2010): https://cxoadvisory.com/?p=4461 | measured (T2, SPY daily 1993-2010, n=126 breakouts, R2 0.01; no edge found) |
| Crypto 24/7 setting: use length 30 on daily | IAmSatoshi (TradingView 2016): https://my.tradingview.com/chart/BTCUSD/yQanb3wG-Changes-to-Default-BBands-for-bitcoin/ | anecdote (T3, chart opinion based on 30 calendar days per month; no backtest) |
| Squeeze-gated 5m BTC mean-reversion | Gate Research: https://www.gate.com/announcements/article/50944 | anecdote (T3, claims filters helped, but no dates, length, multiplier, or costs given) |
| S&P 500 breakout continuation | Quantified Strategies Substack: https://quantifiedstrategies.substack.com/p/bollinger-band-breakout-strategy | anecdote (T3, S&P 1960-2026, 58 trades, CAGR 5.7%; rule paywalled, gross of costs) |
| Popularity versus profitability decay | Fang et al. SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2484322 | UNVERIFIED (URL returned HTTP 403; search summary notes profits decayed after popularity) |

## 4. What our analysts say (extracts)
| Analyst | Their rule in plain words | File pointer |
|---|---|---|
| Krown | BBWP (Bollinger Band Width Percentile, 'The Caretaker' on TV) measures volatility compression/expansion; basis length 7, lookback 100 on BTC HTF; BBWP < 25-35 in range indicates compression, > 80-85 indicates expansion/breakout | `research/krown_ta101_2026-10-13/extracts/extract_kcMnnQr1VFg.md:20,92,100,109` [t=00:05:16, 00:09:19, 00:13:21] |
| Tom | Outside the Bollinger bands is NOT a signal by itself; fading an outside move without volume is a trap; volume surging outward means an imbalance that will not return quickly | `research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:22` (`4VXpUjhKG2U_raw.txt:7` [TOM-S7]) |
| NK (StockTalk) | Bollinger Band "blast" happens on breakouts (e.g. monthly new high or failure at 20 SMA); notes bands lack momentum in chop compared to pivots | `research/nk_stocktalk_1113/flash_deep/wrEEf8o9n9E/EXTRACT.md:14,51`; `research/nk_stocktalk_1113/review/CHECKLIST.md:14,51` |
| Malkan | Bollinger Bands serve as the volatility pillar in his 3D framework (candlesticks + RSI + Bollinger); mentions squeeze, squeeze breakout, and band walk; notes webinar setups | `research/malkan_extract_2026-10-15/extracts/extract_A-CQiV_UFB4.md:18,24`; `extract_2HcJ3NeZmEQ.md:12` |
| Fabio | NO-SOURCE: does not use Bollinger Bands as triggers or levels (0 hits in canonical transcripts) | `research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:43` |
| CryptoCred | NO-SOURCE: no extract mentions Bollinger Bands | none found |
| CCU | NO-SOURCE: no extract mentions Bollinger Bands (uses 50/200 MA, Stoch RSI, WaveTrend) | `research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md` |
| Habib / CBP | NO-SOURCE: no extract mentions Bollinger Bands | none found |

## 5. OUR measurements
All rows OURS, copied from the named file. BTCUSDT, DEV only; no HOLDOUT read.
| Study folder | What was tested | n | Fee-net result | Verdict |
|---|---|---|---|---|
| `research/bb_range_to_range_2026-11-04/RESULT.md` | BB(20,2) close beyond band, trade to opposite band, 2:1 bracket, 24-bar time-out, range regime, 15m, 0.14% round trip, DEV 2022-01..2024-06 | asia 1200 / london 951 / ny 1634 (signal entry) | 6 of 6 cells net negative: asia -0.122% [-0.177, -0.067], london -0.138% [-0.200, -0.076], ny -0.153% [-0.206, -0.100]; target hit 17% / 28% / 21% | 15m: DO NOT USE |
| same file | range gate vs ungated, 15m all sessions, signal entry | 4256 range vs 5311 ungated | -0.130% [-0.161, -0.099] vs -0.127% [-0.154, -0.099]; difference t -0.5 | gate adds nothing |
| same file | 1h and 4h range signals (descriptive, power BLOCKED) | 1h 1080; 4h 252 | 1h -0.157% [-0.278, -0.036]; 4h -0.449% [-0.919, +0.020] | 1h, 4h: UNDERPOWERED |
| `research/bb_dance_2026-10-30/RESULT.md` | 5m shorts after a close back below the mid then a lower-band touch; chance of a new low before a close above the mid; gross, no fees, descriptive | 11,051 | Close near band (%b < 0.25): 59% to 64% new low first (k 1 to 6; n 6,360 down to 1,474). Away from band (%b >= 0.25): 32% to 26%. Exit means gross +0.168% to +0.178% per short against 0.12% round trip (file's own statement) | 5m: CONTEXT ONLY (descriptive, no edge claim) |
| `research/wlow_bounce_bbrsi60_2026-10-16/RESULT.md` | Weekly-low break, bounce, hold under RSI 60 near upper BB, 1h, long, h=4 | 8 events | net long -0.433% (mean R4 -0.293%, SE 0.116) | 1h: UNDERPOWERED (n 8 < 10; VERDICTS.csv INCONCLUSIVE) |
| `research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md` (pooled row) | BB squeeze breakout, volume-confirmed minus unconfirmed, 6 pairs pooled, 4h | 6 pairs | DEV +88 bp [+15, +155] p 0.008; VALIDATION -13 bp [-109, +81] p 0.60 | 4h: DO NOT USE (not supported on VALIDATION) |
Regime mix (bb_range_to_range): 130 weeks DEV: bull 25 (19%), bear 0, range 105 (81%) (`bb_range_to_range_2026-11-04/RESULT.md`). 1d, 1w: NOT_MEASURED. Maker-fill cost (0.09%) and midline exits: NOT_MEASURED (stated untested in the same RESULT.md).

## 6. How to read it now on Live Aid
- **Timeframe strip panel** (`tools/live_aid/live_aid.html` table `#tfs-rows`, `tools/live_aid/tf_strip.js`): Shows "Bollinger" column computing Bollinger(20,2) position (0 to 100, where 0 = lower band, 50 = mid, 100 = upper band) on closes including forming bar. Tagged "near" when within outer 20% of the band (OURS).
- **Momentum panel** (`tools/live_aid/live_aid.html` table `#strip`): Shows `%B` column (scaled `x100`, unconstrained position relative to bands) and `BBw%` column (BandWidth percentage = `(upper - lower) / mid * 100`, under "More detail").
- **Level story** (`tools/live_aid/levelstory.js`): Emits context tags like `at upper Bollinger (15m)` or `outside lower Bollinger (15m)` as confluence evidence on price levels.

## 7. Confluence role: LEVEL
Bollinger Bands serve as dynamic LEVEL boundaries (volatility-adaptive support/resistance envelopes) and EXHAUSTION context.
May add confidence to: a reversal or sweep setup at a confirmed structural level when price reaches the outer band (%B >= 1 or %B <= 0), provided volume and CVD support exhaustion rather than breakout; or a veto against fading a move when volume surges outward during a band walk (Tom rule S7).
Rule in one line: Never trade a raw band touch as an entry; use band extremes only as a dynamic level gate when independent volume/orderflow confirms exhaustion. Today it is CONTEXT ONLY.

## 8. Open tests
- Card `bb-state-regime-tf-map`: Multi-timeframe extension of the 5m %B band dance persistence study onto 15m and 1h bars.
- Card `cvd-coil-and-absorption-u7-u8`: Evaluate whether taker delta (CVD) differentiates true band walk continuation from exhaustion at outer bands.
- Study `bb_retest_level`: Follow-up on retest-LEVEL arm under maker-fill cost model (0.09%) or alternative exit policies (midline take-profit instead of 2:1 bracket).
- Study `krown_bbwp_compression`: Systematic backtest of Krown's BBWP basis 7 lookback 100 compression breakout gate (<25-35 entry gate) on BTC daily/4h.
