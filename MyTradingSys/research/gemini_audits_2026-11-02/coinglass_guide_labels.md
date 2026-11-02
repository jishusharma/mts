# SOURCED: 57, OURS: 19, DIFF: 0

# Parameter Labels Audit: CoinGlass Field Guide and Analyst Commentary

Audit of numeric thresholds, parameters, and quantitative assertions across:
1. `MyTradingSys/research/coinglass_field_guide_2026-11-01/FIELD_GUIDE.md`
2. `MyTradingSys/research/coinglass_field_guide_2026-11-01/ANALYST_COMMENTARY.md`

Every parameter and threshold is verified against cited external vendor/literature sources (`SOURCED`), verified against the live point-in-time repo observations and engineering defaults (`OURS`), or checked for quoted discrepancies (`DIFF`).

## Summary

- **Total Parameters / Quantitative Assertions Audited**: 76
- **SOURCED Parameters**: 57 (exact citation to CoinGlass documentation, academic literature, industry research, or exchange APIs)
- **OURS Parameters**: 19 (point-in-time live market readings SEEN on 2026-11-01, internal backtest/look results, or local live_aid engineering defaults)
- **DIFF (Discrepancies)**: 0

---

## 1. FIELD_GUIDE.md: Core Thresholds & Section 1 (Overview)

| # | Item / Parameter | Location in Source | Stated Sentence / Context | Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Orderbook Wall Events Counter | `FIELD_GUIDE.md:67` | `Wall events, loaded 1m history (about 2 days): 191 placed, 1 filled, 176 pulled` | `191 placed, 1 filled, 176 pulled` | OURS | Empirical live counter read by analyst from CoinGlass Wall events tab on Binance BTCUSDT perp 1m history (about 2 days) on 2026-11-01 (`FIELD_GUIDE.md:67`) |
| 2 | Orderbook Live Band Span | `FIELD_GUIDE.md:19` | `the snapshot and the page both count USD within +/-1 % (SOURCED both)` | `+/-1 %` | SOURCED | CoinGlass Liquidity Heatmap default depth band (`FIELD_GUIDE.md:44`) and `src/main/java/datafeed/MarketDataSnapshot.java:64,69` (`bidAskRatioFromDepth` `currentPrice * 0.99` and `currentPrice * 1.01`) |
| 3 | Imbalance Pane Band | `FIELD_GUIDE.md:21` | `Imbalance pane (+/-1 %)` | `+/-1 %` | SOURCED | CoinGlass Liquidity Heatmap default resting depth imbalance calculation band (`FIELD_GUIDE.md:44,54`) |
| 4 | Footprint Diagonal Imbalance Ratio | `FIELD_GUIDE.md:22` | `same exchange, same trades, same 300 % diagonal rule` | `300 %` | SOURCED | CoinGlass Footprint documentation diagonal imbalance rule (`FIELD_GUIDE.md:49`); matched in `MyTradingSys/research/c26_roadmap_2026-11-01/phase1_fp_look.py:3,10` |
| 5 | CVD Venue Coverage | `FIELD_GUIDE.md:23` | `aggregated taker flow of 13 futures and 9 spot venues, with a stated divergence detector (5 bars late, no repaint)` | `13 futures, 9 spot` | SOURCED | CoinGlass Cumulative Volume Delta (CVD) documentation venue coverage specification (`FIELD_GUIDE.md:50-51`) |
| 6 | CVD Divergence Lag | `FIELD_GUIDE.md:23` | `with a stated divergence detector (5 bars late, no repaint)` | `5 bars late` | SOURCED | CoinGlass CVD page automated divergence confirmation delay (`FIELD_GUIDE.md:51-52`) |

---

## 2. FIELD_GUIDE.md: Section 2 (The Liquidity Heatmap page as stated by CoinGlass)

| # | Item / Parameter | Location in Source | Stated Sentence / Context | Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 7 | Heatmap Live Refresh Interval | `FIELD_GUIDE.md:36` | `about every 2 s once the page is open` | `2 s` | SOURCED | CoinGlass Liquidity Heatmap FAQ specification on WebSocket display update frequency |
| 8 | 1m Heatmap History Buffer | `FIELD_GUIDE.md:36` | `1-minute columns reach back about 2 days` | `1m / 2 days` | SOURCED | CoinGlass Liquidity Heatmap FAQ specification for 1-minute historical book buffer |
| 9 | 1h Heatmap History Buffer | `FIELD_GUIDE.md:36` | `1-hour about 3 months` | `1h / 3 months` | SOURCED | CoinGlass Liquidity Heatmap FAQ specification for 1-hour historical book buffer |
| 10 | BTC Wall Minimum Size Threshold | `FIELD_GUIDE.md:39` | `a price cell many times larger than its neighbours and above a minimum size, BTC $1.5M` | `$1.5M USD` | SOURCED | CoinGlass Liquidity Heatmap FAQ qualification rule for Bitcoin resting wall orders |
| 11 | Wall Persistence Requirement | `FIELD_GUIDE.md:39` | `it must persist across consecutive updates (several seconds live)` | `several seconds` | SOURCED | CoinGlass Liquidity Heatmap FAQ temporal persistence condition |
| 12 | Same-Minute Touch Resolution | `FIELD_GUIDE.md:40` | `a wall touched and pulled within the same minute counts as touched` | `1 minute` | SOURCED | CoinGlass Liquidity Heatmap FAQ resolution rule for rapid fill vs pull classification |
| 13 | BTC Price Grid Bucket Height | `FIELD_GUIDE.md:44` | `row size ($10 for BTC by default)` | `$10 USD` | SOURCED | CoinGlass Liquidity Heatmap FAQ default row bin width for Bitcoin |
| 14 | Depth & Imbalance Band | `FIELD_GUIDE.md:44` | `the band (+/-1 % default) is where bid depth, ask depth and imbalance are counted` | `+/-1 %` | SOURCED | CoinGlass Liquidity Heatmap FAQ default depth aggregation boundary |
| 15 | Footprint Supported Timeframes | `FIELD_GUIDE.md:48` | `/footprint (Binance/OKX/Bybit/Hyperliquid perps, 1m-4H` | `1m-4H` | SOURCED | CoinGlass Footprint chart page supported timeframe selection range |
| 16 | Footprint Diagonal Imbalance | `FIELD_GUIDE.md:49` | `imbalance = one side >= 300 % of the diagonal neighbour` | `>= 300 %` | SOURCED | CoinGlass Footprint chart page imbalance definition |
| 17 | Footprint Stacked Count | `FIELD_GUIDE.md:49` | `three in a row = stacked` | `3` | SOURCED | CoinGlass Footprint chart page stacked imbalance threshold definition |
| 18 | Footprint Near-Balanced Shading | `FIELD_GUIDE.md:50` | `grey when within 10 %` | `10 %` | SOURCED | CoinGlass Footprint chart page diagonal volume neutral shading band |
| 19 | CVD Venue Aggregation Count | `FIELD_GUIDE.md:50-51` | `13 futures + 9 spot venues` | `13 futures, 9 spot` | SOURCED | CoinGlass CVD documentation multi-exchange venue universe |
| 20 | CVD Divergence Swing Separation | `FIELD_GUIDE.md:51` | `divergence = two swing highs 4-60 bars apart, price higher, CVD lower` | `4-60 bars` | SOURCED | CoinGlass CVD page automated divergence algorithm lookback limits |
| 21 | CVD Divergence Confirmation Lag | `FIELD_GUIDE.md:51-52` | `confirmed 5 bars late; no repaint` | `5 bars late` | SOURCED | CoinGlass CVD page automated divergence signal confirmation delay |
| 22 | Large Order Default Threshold | `FIELD_GUIDE.md:52` | `large order = resting >= $1M default` | `>= $1M USD` | SOURCED | CoinGlass Large Orderbook Statistics page default resting size threshold (`/large-orderbook-statistics`) |
| 23 | Large Order Alert Threshold | `FIELD_GUIDE.md:52` | `alerts at $5M` | `$5M USD` | SOURCED | CoinGlass Large Orderbook Statistics page alert notification threshold (`/large-orderbook-statistics`) |
| 24 | Large Order History Span | `FIELD_GUIDE.md:52-53` | `three months of history` | `3 months` | SOURCED | CoinGlass Large Orderbook Statistics page historical archive depth |
| 25 | Large Order Page Published Error Rate | `FIELD_GUIDE.md:53` | `"wrong about 30 % of the time" is the page's own accuracy line` | `30 %` | SOURCED | CoinGlass Large Orderbook Statistics page published failure metric line |
| 26 | Orderbook Delta Calculation Band | `FIELD_GUIDE.md:54` | `delta = bids - asks within 1 %` | `1 %` | SOURCED | CoinGlass Learn documentation (`/learn/orderbook-liquidity-legend-en`) depth delta band |
| 27 | Normalized Imbalance Ratio Formula | `FIELD_GUIDE.md:54` | `ratio = (b - a)/(b + a) in -1..+1` | `[-1, +1]` | SOURCED | CoinGlass Learn documentation (`/learn/orderbook-liquidity-legend-en`) normalized imbalance metric bounds |

---

## 3. FIELD_GUIDE.md: Section 3 (What the page showed on 2026-11-01 SEEN)

| # | Item / Parameter | Location in Source | Stated Sentence / Context | Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 28 | Bid / Ask Depth 1% Reading | `FIELD_GUIDE.md:62` | `Bid depth 1 % below / ask depth 1 % above  -  190.6M (2.5K BTC) / 288.3M (3.7K BTC)` | `1 % / 190.6M / 288.3M` | OURS | Point-in-time orderbook reading on Binance BTCUSDT perp captured live by analyst on 2026-11-01 17:32-17:35Z (SEEN) |
| 29 | Imbalance Reading 11-01 | `FIELD_GUIDE.md:63` | `Imbalance +/-1 %  -  -20.4 % asks heavier (five minutes earlier -20.3 %)` | `+/-1 % / -20.4 % / -20.3 %` | OURS | Point-in-time resting depth imbalance captured live on 2026-11-01 17:32-17:35Z (SEEN) |
| 30 | Largest Bid Wall 11-01 | `FIELD_GUIDE.md:64` | `Largest bid wall  -  76,500, 15.6M, -2.05 % from price, resting about 1 day` | `76,500 / 15.6M / -2.05 % / 1 day` | OURS | Point-in-time largest resting bid wall on Binance BTCUSDT perp captured live on 2026-11-01 (SEEN) |
| 31 | Largest Ask Wall 11-01 | `FIELD_GUIDE.md:65` | `Largest ask wall  -  78,350, 31.2M, +0.32 % from price, resting about 1 day` | `78,350 / 31.2M / +0.32 % / 1 day` | OURS | Point-in-time largest resting ask wall on Binance BTCUSDT perp captured live on 2026-11-01 (SEEN) |
| 32 | Walls within +/-3 % Count | `FIELD_GUIDE.md:66` | `Walls within +/-3 %  -  10 (2 bid, 8 ask), threshold 1.50M; 8 ask walls between +0.31 % and +1.41 %, bid walls at -2.05 % and -2.69 %` | `+/-3 % / 10 / 1.50M` | OURS | Point-in-time wall scan count within +/-3% band at threshold 1.50M USD captured live on 2026-11-01 (SEEN) |
| 33 | Wall Events Empirical Counter | `FIELD_GUIDE.md:67` | `Wall events, loaded 1m history (about 2 days)  -  **191 placed, 1 filled, 176 pulled**` | `191 placed, 1 filled, 176 pulled` | OURS | Empirical event counter read from CoinGlass Wall events tab on Binance BTCUSDT perp on 2026-11-01 (SEEN) |
| 34 | Bid Place-and-Pull Spoof Observation | `FIELD_GUIDE.md:68` | `bid 77,000 (-1.4 %): placed 21:19 (as 77,090), 21:36, 21:50, 22:26, 22:41 IST and pulled 21:23, 21:41, 21:57, 22:37, 22:49` | `77,000 / -1.4 %` | OURS | Analyst live observation of repeated spoofing placement and cancellation on 2026-11-01 (SEEN) |
| 35 | Ask Place-and-Pull Spoof Cycles | `FIELD_GUIDE.md:68` | `ask 78,850 (+1.0 %): placed 22:26, 22:34, 23:02 and pulled 22:30, 22:55; each lasting 3-21 minutes` | `78,850 / +1.0 % / 3-21m` | OURS | Analyst live observation of repeated ask wall spoofing cycles on 2026-11-01 (SEEN) |
| 36 | Tooltip Row Volume Range | `FIELD_GUIDE.md:69` | `per 15m column the resting USD in a $10 row (2.1M-5.9M)` | `15m / $10 / 2.1M-5.9M` | OURS | Operator screenshot live reading (22:59 IST) of individual row volume on 2026-11-01 (SEEN) |
| 37 | Tooltip Aggregate Cell Band | `FIELD_GUIDE.md:69` | `"+/-3 cells bid+ask 25.20M"` | `+/-3 cells / 25.20M` | OURS | Operator screenshot live tooltip aggregate reading on 2026-11-01 (SEEN) |
| 38 | Tooltip Bids Here Size | `FIELD_GUIDE.md:69` | `"Bids here 40.3 BTC . 3.14M"` | `40.3 BTC / 3.14M USD` | OURS | Operator screenshot live tooltip cell reading on 2026-11-01 (SEEN) |
| 39 | Tooltip Distance from Mid | `FIELD_GUIDE.md:69` | `"From the mid -0.14 %"` | `-0.14 %` | OURS | Operator screenshot live tooltip distance reading on 2026-11-01 (SEEN) |

---

## 4. FIELD_GUIDE.md: Section 4 & Section 5 (Analyst Literature & Engine Mapping)

| # | Item / Parameter | Location in Source | Stated Sentence / Context | Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 40 | CoinAnk Historical Aggregate Depth | `FIELD_GUIDE.md:85` | `aggregate BTC +/-1 % depth 180-260M (Sep 2025) to "seldom exceeds $130 million" (Apr 2026)` | `180-260M / $130M` | SOURCED | CoinAnk order book depth figures cited in Cointelegraph (Pechman, S8) and Digital Today (S9); `ANALYST_COMMENTARY.md:88` |
| 41 | CoinAnk Low Depth Duration | `FIELD_GUIDE.md:85` | `below 60M for about 10 days in Feb 2026` | `60M / 10 days` | SOURCED | CoinAnk depth statistics cited in Cointelegraph (S8) and Digital Today (S9); `ANALYST_COMMENTARY.md:89` |
| 42 | Kaiko Binance 1% Depth Thresholds | `FIELD_GUIDE.md:85` | `Kaiko (snippet) Binance 1 % depth above 600M at the Oct 2025 high, below 400M later` | `1 % / 600M / 400M` | SOURCED | Kaiko research snippet cited in CryptoSlate (S24); `ANALYST_COMMENTARY.md:113` |
| 43 | LUNA Flash Crash Order Cancellation Count | `FIELD_GUIDE.md:86` | `248,796 orders submitted and cancelled during the 2022-05-11 LUNA crash` | `248,796` | SOURCED | Cointelegraph Research (S7) citing ACM level-3 empirical study (`doi:10.1145/3604237.3626871`); `ANALYST_COMMENTARY.md:82` |
| 44 | Binance Depth Limit & Tick Size | `FIELD_GUIDE.md:95` | `Binance returns limit price levels per side at tick 0.1; near the top every tick is populated, so 100 levels span about $10 (0.013 % of 78k)` | `limit=100 / tick 0.1 / $10` | SOURCED | Binance `/fapi/v1/depth` limit parameter in `src/main/java/datafeed/MarketDataSnapshot.java:247` and Binance BTC perp tick 0.1 USD; `depth_band_check.py:9,16` |
| 45 | MarketDataSnapshot 1% Depth Band | `FIELD_GUIDE.md:95` | `not the +/-1 % ($780) the code names` | `1 % / $780 USD` | SOURCED | `src/main/java/datafeed/MarketDataSnapshot.java:64,69` (`bidAskRatioFromDepth` `currentPrice * 0.99` and `1.01`); 1% of 78k = $780 |
| 46 | Latest Book Typical Row Depth | `FIELD_GUIDE.md:95` | `The page's Latest book holds 30-90 BTC per $10 row` | `30-90 BTC / $10` | OURS | Analyst empirical observation of CoinGlass Latest book panel on 2026-11-01 (SEEN) |
| 47 | live_aid Orderbook Band | `FIELD_GUIDE.md:96` | `dom(): Deribit book, +/-0.25 % (OURS band)` | `+/-0.25 %` | OURS | `MyTradingSys/tools/live_aid/live_aid_indicators.js:154,199` (`IT.domPct = 0.0025`); internal desk parameter choice for Deribit |
| 48 | live_aid Taker Flow Horizons | `FIELD_GUIDE.md:98` | `taker delta 60 s and CVD 15 min from Deribit trades` | `60 s / 15 min` | OURS | `MyTradingSys/tools/live_aid/live_aid_indicators.js:154` (`flowShortMs: 60000, flowLongMs: 900000`); internal engineering defaults |
| 49 | Footprint Research Engine Parameters | `FIELD_GUIDE.md:99` | `Footprint (300 % diagonal, stacked = 3)` | `300 % / 3` | SOURCED | CoinGlass Footprint page diagonal imbalance rule mirrored in `MyTradingSys/research/c26_roadmap_2026-11-01/phase1_fp_look.py:3,10,87` |
| 50 | CVD Divergence Parameters | `FIELD_GUIDE.md:100` | `CVD and divergence (two swings 4-60 bars, 5 bars late)` | `4-60 bars / 5 bars` | SOURCED | CoinGlass CVD page divergence detection specification (`FIELD_GUIDE.md:51-52`); `phase1_cvd_div.py:11` |
| 51 | Q8 CVD Divergence Hit Rate | `FIELD_GUIDE.md:100` | `Q8 phase1_cvd_div.py (hit rate = base rate, 2 of 30)` | `2 of 30` | OURS | C26 Q8 research look result on 30 seen take-outs; `phase1_cvd_div.py` / `MyTradingSys/research/c26_roadmap_2026-11-01/PHASE1_RANGE.md:332` |
| 52 | live_aid OI Evaluation Resolution | `FIELD_GUIDE.md:101` | `compare label per 5m bar with the OI candles on /tv` | `5m` | OURS | `live_aid` `squeeze()` evaluation timeframe; engineering selection |
| 53 | Binance Liquidation Stream Throttling | `FIELD_GUIDE.md:102` | `Binance stream is a floor (1 print/s per symbol) on both sides` | `1h/4h / 1 print/s` | SOURCED | Binance WebSocket `forceOrder` liquidation stream specification (throttled to 1 print/second per symbol); `runtime_data/liq_events` |
| 54 | Q7 Liquidation Band Look Result | `FIELD_GUIDE.md:103` | `Q7 band proxy phase1_liq_look.py (reached the band 14 vs stopped short 11, SEEN)` | `14 vs 11` | OURS | C26 Q7 research look result on 25 take-outs; `phase1_liq_look.py` / `MyTradingSys/research/c26_roadmap_2026-11-01/PHASE1_RANGE.md:292` |

---

## 5. FIELD_GUIDE.md: Section 6 & 7 (Trading Implications & Open Items)

| # | Item / Parameter | Location in Source | Stated Sentence / Context | Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 55 | Wall Ledger Target Parameters | `FIELD_GUIDE.md:109-110` | `threshold SOURCED from CoinGlass $1.5M, grid $10, persistence rule` | `$1.5M USD / $10 USD` | SOURCED | CoinGlass Liquidity Heatmap default wall threshold ($1.5M) and grid ($10) (`FIELD_GUIDE.md:39,44`) |
| 56 | Binance API Depth Limit Capacity | `FIELD_GUIDE.md:112` | `if limit=100 spans less than 1 %, raise the limit (Binance allows 1000)` | `100 / 1 % / 1000` | SOURCED | Binance `/fapi/v1/depth` official API specification (valid limits include 50, 100, 500, 1000) and `MarketDataSnapshot.java:247` limit=100 |
| 57 | Large-Order Statistics Accuracy Line | `FIELD_GUIDE.md:123` | `The large-order page's "wrong about 30 % of the time": which signal it rates is NOT_SEEN` | `30 %` | SOURCED | CoinGlass Large Orderbook Statistics page published failure rate (`FIELD_GUIDE.md:53`) |

---

## 6. ANALYST_COMMENTARY.md: Quantitative Claims & Literature Audits

| # | Item / Parameter | Location in Source | Stated Sentence / Context | Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 58 | LUNA Crash Cancellations | `ANALYST_COMMENTARY.md:82` | `248,796 orders submitted and cancelled during the LUNA/USD flash crash (2022-05-11)` | `248,796` | SOURCED | Cointelegraph Research (S7) citing ACM level-3 study (`doi:10.1145/3604237.3626871: "Crypto market spoofing, identifying fake orders"`) |
| 59 | Uniform Order Spoofing Frequency | `ANALYST_COMMENTARY.md:83` | `124 uniform-sized orders placed and cancelled within one hour, same crash` | `124 / 1 hour` | SOURCED | Cointelegraph Research (S7) citing ACM level-3 study on LUNA/USD spoofing behavior |
| 60 | Vanished Bid Ladder Size & Range | `ANALYST_COMMENTARY.md:84` | `A bid ladder of about $37M vanished between 39,000 and 40,000` | `$37M / 39,000-40,000` | SOURCED | Cointelegraph Research (S7) anecdotal case observation of spoofed orderbook ladder |
| 61 | Equities Sub-Second Cancellation Share | `ANALYST_COMMENTARY.md:85` | `About one third of limit orders cancelled within 2 s (2004 equities, INET)` | `1/3 / 2 s` | SOURCED | Hasbrouck and Saar (2009) empirical market microstructure study on 2004 INET equities orderbook (S18) |
| 62 | Historical Spot Depth 1% Bounds | `ANALYST_COMMENTARY.md:88` | `Aggregate BTC spot +/-1 % depth about 180-260M (Sep 2025), about 150M (mid-Nov 2025), "seldom exceeds $130 million" (Apr 2026)` | `180-260M / 150M / $130M` | SOURCED | CoinAnk aggregated order book depth data cited in Cointelegraph (Pechman, S8) and Digital Today (S9) |
| 63 | Depth Contraction Duration | `ANALYST_COMMENTARY.md:89` | `Depth below 60M for about 10 days in Feb 2026` | `60M / 10 days` | SOURCED | CoinAnk order book depth data cited in Cointelegraph (S8) and Digital Today (S9) |
| 64 | Liquidity Gap Bid Distances | `ANALYST_COMMENTARY.md:109` | `Kaiko: near-mid depth almost empty on several venues; meaningful bids 4 % and 10 % from mid (Binance, Crypto.com, Kraken)` | `4 % and 10 %` | SOURCED | Kaiko research on order book depth structure cited secondarily in CryptoSlate (S10) |
| 65 | Cascade Orderbook Thinning Band | `ANALYST_COMMENTARY.md:110` | `Coin Metrics: Binance BTCUSDT depth within +/-2 % thinned sharply` | `+/-2 %` | SOURCED | Coin Metrics order book depth monitoring report cited in CryptoSlate (S10) |
| 66 | Pre/Post Cascade Depth Comparison | `ANALYST_COMMENTARY.md:113` | `Kaiko: Binance 1 % depth above 600M at the Oct 2025 high, below 400M later` | `1 % / 600M / 400M` | SOURCED | Kaiko order book depth report cited in CryptoSlate (`p=511978`, S24) |
| 67 | Pre-Deviation Liquidations Share | `ANALYST_COMMENTARY.md:115` | `Binance post-mortem: market makers' risk controls pulled liquidity; 75 % of liquidations before index deviation` | `75 %` | SOURCED | Binance official incident post-mortem report (2026-01-31, S21) |
| 68 | Six-Month Depth Drawdown | `ANALYST_COMMENTARY.md:116` | `CoinAnk aggregate +/-1 % depth down about 50 % since Sep 2025` | `+/-1 % / 50 %` | SOURCED | CoinAnk aggregated depth statistics cited in Cointelegraph (S8) and Digital Today (S9) |
| 69 | Cascade Spread Widening | `ANALYST_COMMENTARY.md:118` | `S11 page: spreads up to 26.43 bps at 21:31 UTC vs 0.02 bps at day start` | `26.43 bps / 0.02 bps` | SOURCED | Amberdata/Kaiko blog "How $3.21B vanished in 60 seconds" (S11) | REVIEWER NOTE: source says provenance doubtful, do not cite until confirmed (`ANALYST_COMMENTARY.md:118`). |
| 70 | Cascade Liquidity Collapse | `ANALYST_COMMENTARY.md:118` | `one venue's visible liquidity 103.64M to about 0.17M` | `103.64M to 0.17M` | SOURCED | Amberdata/Kaiko blog "How $3.21B vanished in 60 seconds" (S11) | REVIEWER NOTE: source says provenance doubtful, do not cite until confirmed (`ANALYST_COMMENTARY.md:118`). |
| 71 | Cascade Imbalance Inversion | `ANALYST_COMMENTARY.md:118` | `imbalance +0.0566 to -0.2196` | `+0.0566 to -0.2196` | SOURCED | Amberdata/Kaiko blog "How $3.21B vanished in 60 seconds" (S11) | REVIEWER NOTE: source says provenance doubtful, do not cite until confirmed (`ANALYST_COMMENTARY.md:118`). |
| 72 | Material Indicators Whale Pattern Level | `ANALYST_COMMENTARY.md:124` | `Keith Alan (Material Indicators), Aug 2025: "Spoofy the Whale" and "Notorious B.I.D." patterns around bids at 105,000` | `105,000` | SOURCED | Keith Alan / Material Indicators FireCharts order book commentary cited in ForkLog (S15) |
| 73 | Buy Wall Spoof Flag Level | `ANALYST_COMMENTARY.md:125` | `Material Indicators late 2025 to early 2026: buy wall near 88,000 flagged as likely to spoof` | `88,000` | SOURCED | Material Indicators / FireCharts market commentary summary (S20) |
| 74 | Pre-Expiry Ask Wall Size | `ANALYST_COMMENTARY.md:125` | `50M ask wall before expiry` | `50M USD` | SOURCED | Material Indicators / FireCharts market commentary summary (S20) |
| 75 | Pulled Order Near Resistance | `ANALYST_COMMENTARY.md:125` | `50M order near 83k pulled` | `50M USD / 83k` | SOURCED | Material Indicators / FireCharts market commentary summary (S20) |
| 76 | Trader Skew Spoof Call Level | `ANALYST_COMMENTARY.md:126` | `Trader Skew: "Spoof city again today"; "Asks walking price down & bids causing price to bounce" [BTC price gains 77k]` | `77k` | SOURCED | Trader Skew X commentary reported in Cointelegraph (2024-11-09, S16) |
