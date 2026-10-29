# CoinGlass inventory (screenshots in `shots/`, taken 2026-10-29 about 02:30 UTC, anonymous, free)

All pages open without login. "Paid" = API only unless stated. Prefix https://www.coinglass.com unless a full URL is given.

| Page | URL | What it shows | Shot | Free/paid |
|---|---|---|---|---|
| Home | / | Market strip, top movers, OI/liq/funding tiles, coin table, ETF flow table | (text only) | free |
| Funding rates | /FundingRate | Symbol x 12 exchanges + predicted, weighted BTC/ETH, history | (text only) | free |
| OI by exchange | /open-interest/BTC | Per-exchange BTC OI, 1h/4h/24h change | exchange_oi_bars.jpg (coin bars page) | free |
| OI per coin bars | /pro/futures/FuturesOpenInterest | Exchange OI bars for each coin | exchange_oi_bars.jpg | free |
| Liquidation data | /liquidations | Liq heatmap tiles, 1h/4h/12h/24h long/short totals | liquidation_data.jpg | free |
| Liquidation history | /pro/futures/Liquidations | Perpetual liquidation history + 30d coin heatmap | liq_history.jpg | free |
| Liquidation heatmap M1 | /pro/futures/LiquidationHeatMap | Binance BTC/USDT 24h price x liquidation levels | liq_heatmap_binance_24h.jpg | free (Prime button for more) |
| Liquidation map | /pro/futures/LiquidationMap | Liquidation bars at price, leverage tiers, cumulative | liquidation_map.jpg | free |
| Top liquidation events | /pro/futures/liquidation-events | Largest historical events table | top_liq_events.jpg | free |
| Long/short ratio | /LongShortRatio | Taker volume, sentiment pie, per-exchange retail/whale/smart money | long_short_ratio.jpg | free |
| L/S taker chart | /LongShortRatio (scrolled) | BTC taker L/S 30m with price | ls_taker_chart.jpg | free |
| Hyperliquid L/S traders | /pro/futures/hyperliquid-long-short-ratio | Long vs short trader counts + ratio | hyperliquid_ls.jpg | free |
| Orderbook liquidity delta | /pro/depth-delta | Aggregated and per-exchange bid-ask depth delta, 15m | depth_delta_agg.jpg | free |
| Perp/spot volume | /pro/perpteual-spot-volume | Futures/spot volume ratio, Binance BTC/USDT, 1d | perp_spot_ratio.jpg | free |
| Historical volume | /pro/futures/ExVolume | Futures volume history by exchange | hist_volume.jpg | free |
| Exchange ranking | /exchanges | Derivatives exchanges: volume, OI, fees, liq, score | exchanges_rank.jpg | free |
| Coinbase premium | /pro/i/coinbase-bitcoin-premium-index | Premium %, 30d avg, percentile, z-score, 1m-1d chart | coinbase_premium.jpg | free |
| Binance premium index | /pro/futures/PremiumIndex | Binance BTCUSDT premium, 1m candles | binance_premium_1m.jpg | free |
| Max pain | /pro/options/max-pain | BTC/ETH max pain by expiry | max_pain.jpg | free |
| Options OI | /pro/options/OpenInterest | Total BTC options OI history | options_oi.jpg | free |
| ETF flows | /pro/i/spot-bitcoin-etf-flows | Spot BTC ETF flows USD by fund | etf_flows.jpg | free |
| CME report | /pro/cme/cftc | CME BTC OI + COT table | cme_cftc.jpg | free |
| Trading sessions | /pro/futures/TimeZoneDistribution | Volume/liq/OI by Asia, EU, US session | trading_sessions.jpg | free |
| OI change heatmap | /pro/heatmap/oi-change | Coin treemap by OI change | heatmap_oi_change.jpg | free |
| Bull peak checklist | /bull-market-peak-signals | 30 indicators, hit/not hit, progress | bull_peak_indicators.jpg | free |
| AHR999 | /pro/i/ahr999 | Index chart and table | ahr999.jpg | free |
| Rainbow chart | /pro/i/bitcoin-rainbow-chart | Log-regression bands | rainbow.jpg | free |
| Supercharts | /tv | TradingView-based, Binance BTCUSDT 1m with OI, Net Delta, Agg CVD, Net Longs/Shorts | supercharts_tv.jpg | free to view |
| Legend chart | https://legend.coinglass.com/chart | 15m candles with Large Trades bubbles + Footprint | legend_chart_15m.jpg, legend_zoom_drop.jpg | free to view; save/login NOT_SEEN |
| Legend indicator list | (dialog on Legend chart) | Liquidation Heatmap, VWAP, Net Longs/Shorts, Hyperliquid Liq Map, Liquidity Heatmap, Footprint, Large Trades, Mkt Cap, OI/Mkt Cap, Fear&Greed, Index Price, Coinbase Premium, Volume, VPVR, CVD, Taker Buy/Sell Value, Active Buy/Sell Volume and Trades, Orderbook Liquidity/Delta/Ratio, Whale Index 1-4, Aggregated L/S, L/S Accounts, Top Trader L/S Positions and Accounts, Liquidation (+aggregated variants), Open Interest, OI Delta, Aggregated OI (coin and stablecoin), Predicted Funding, Aggregated Funding, Basis, then classic TA (BIAS, AO, BOLL, BRAR, BBI, CCI, CR, DMA, DMI, EMV, EMA, MTM, MA, MACD, OBV, PSY, ROC, RSI, SMA, KDJ, SAR, TRIX, VR, WR). A short gap in the list between Aggregated OI and Predicted Funding was not read (NOT_SEEN). | legend_indicators_1..4.jpg | free to view |
| API pricing | /pricing | Plans $29-$699/mo, enterprise for bulk export | api_pricing.jpg | paid |
| API home | /CryptoApi | Marketing, docs link | api_home.jpg | paid |

Sidebar pages listed but not opened (hrefs seen): /pro/options/OIExpiry, OIStrike, VolExpiry, VolStrike, OptionGreeks, net-premium-strike-heatmap; /pro/futures/OptionsVSFutures; /pro/futures/FuturesVolume; /pro/futures/InsuranceFund; /pro/i/MarginFeeChart; /pro/i/bitcoin-dominance; /pro/i/FearGreedIndex; /pro/i/nupl; /pro/i/mvrv-ratio; /pro/i/mayer-multiple; /pro/i/pi-cycle-top-indicator; /pro/i/bitcoin-power-law; /pro/gray/Grayscale; /pro/etf/Premium; /pro/futures/LiquidationHeatMapNew; /liquidation-heatmap-model3; /hyperliquid-liquidation-map; /pro/heatmap/{market-cap,fundingrate,rsi,price-change,oi,oi-change-usd,vol,vol-change,vol-change-usd}; /watchlist; /stocks.
Category counts from the sidebar: Derivatives 33, Market Cycle 45, Technical Indicators 16, On-Chain 88, Institutions 25, Heatmap 10, CoinGlass Index 2, Dashboard 3. On-Chain was not opened.
