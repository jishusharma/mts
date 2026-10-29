# CoinGlass survey, 2026-10-29 (free public pages, read-only)

Method: Claude in Chrome, new tab only, no login, no clicks beyond navigation, sidebar expand, indicator-list open. About 40 page visits. Pages rendered for an anonymous viewer on 2026-10-29 around 02:30 UTC (browser clock UTC+5:30, 08:08 local). Screenshots in `shots/` (index in INVENTORY.md). Anything not on screen is NOT_SEEN. Page text treated as data.

Free vs paid: every page below rendered data with no login. A "Prime" (paid) button sits on the heatmap page; what it unlocks is NOT_SEEN. The API is paid only (plans at the end).

## Family tables

### 1. Funding rates
| Item | Value |
|---|---|
| URL | https://www.coinglass.com/FundingRate |
| Shows | Table symbol x exchange (Binance, OKX, Bybit, KuCoin, MEXC, BingX, Gate, Bitunix, Bitget, WhiteBIT, LBank, tradeXYZ) plus predicted rate; OI-weighted and volume-weighted BTC/ETH rate; history chart (current, 1d, 7d, 30d, 1y); heatmap view; USDT vs token-margined |
| Seen values | BTC Binance 0.0022%, OKX 0.0073%, Bybit 0.0036% (8h quoted) |
| Cadence | live, normalised to 8h; chart 30min to 8h |
| Free / API | free page; API (real-time + history) paid |
| Use | Observer: crowding context only (rate near 0.01% baseline = no squeeze signal). Severity: weak and slow. |

### 2. Open interest by exchange
| Item | Value |
|---|---|
| URLs | https://www.coinglass.com/open-interest/BTC ; /pro/futures/FuturesOpenInterest (bars per coin) ; /pro/futures/OpenInterest (history) ; /pro/futures/oi-vol-filter (screener, not opened) |
| Shows | Per-exchange BTC OI (BTC and USD), share, 1h/4h/24h change, OI/24h-volume; CME shown separately; stacked chart by exchange, 1 day granularity |
| Seen values | Total 665.71K BTC / $53.21B; Binance $11.07B; CME $8.55B (-5.83% 24h); Bybit $5.74B; Hyperliquid $3.47B; all-exchange OI 1h -1.11%, 4h -1.70% |
| Cadence | live; chart daily |
| Free / API | free; API paid |
| Use | Observer: 1h/4h OI change per exchange separates de-risking from new positions during a move. Severity: confirms move quality. |

### 3. Liquidations and liquidation heat maps
| Item | Value |
|---|---|
| URLs | /liquidations (Liquidation Data) ; /pro/futures/Liquidations (history + 30d heatmap) ; /pro/futures/LiquidationMap ; /pro/futures/LiquidationHeatMap (Model 1) ; /LiquidationHeatMapNew (Model 2) ; /liquidation-heatmap-model3 ; /hyperliquid-liquidation-map ; /pro/futures/liquidation-events ; /LiquidationCountHeatMap (last five not opened except events) |
| Shows | 1h/4h/12h/24h totals long vs short; per-coin tiles; estimated liquidation levels by price (map = bars at price with 10x/25x/50x/100x tiers and cumulative curves; heatmap = price x time, purple to yellow); any pair, 24h default, Pair or Symbol (aggregated) mode |
| Seen values | 24h liquidation $349M (+130%); BTC $91.8M; 1h total about $95.8M of which longs about $93M (low-res read, approximate); largest order $6.35M Hyperliquid BTC-USD |
| Cadence | totals live; heatmap model recompute cadence NOT_SEEN |
| Free / API | free at 24h default; Prime button present (extra ranges NOT_SEEN); "Liquidation Map API" paid |
| Use | Observer: best free map of where stops cluster; 10-29 heatmap showed bright bands near 82,000 and 80,000. Severity: 1h/4h liquidation vs 24h average ranks event size. Caveat: modelled estimate, not realised. |

### 4. Long/short ratios
| Item | Value |
|---|---|
| URLs | https://www.coinglass.com/LongShortRatio ; /pro/futures/hyperliquid-long-short-ratio ; Legend indicators |
| Shows | Taker buy/sell volume 1h/4h/12h/24h; BTC sentiment pie; per exchange (Binance, OKX, Bybit) retail accounts, whale account, whale position, smart-money sentiment; BTC taker L/S chart (30m with price); L/S accounts chart (Binance, 4h); Hyperliquid long vs short trader counts |
| Seen values | Binance accounts 2.05, top-trader accounts 2.2, top-trader positions 1.86; OKX whale account 0.56 vs retail 2.03; 4h taker long $3.76B vs short $4.70B (44% / 56%); Hyperliquid 70,205 long vs 21,886 short traders |
| Cadence | live; charts 30m to 4h |
| Free / API | free; API paid |
| Use | Observer: whale vs retail divergence is a contrarian read. Severity: slow (30m+), context not trigger. |

### 5. Exchange volumes, spot vs futures
| Item | Value |
|---|---|
| URLs | /exchanges ; /pro/perpteual-spot-volume ; /pro/futures/ExVolume ; /pro/futures/FuturesVolume (not opened) ; /pro/i/global-exchange-trading-volume and siblings (listed only) |
| Shows | Ranked derivatives exchanges (24h volume, OI, fees, 24h liquidation, OI/vol, score); perp/spot volume ratio for Binance BTC/USDT (1d); historical volume by exchange |
| Seen values | Total futures volume $190.5B (+20%); Binance volume and OI in the ranking table (read at low resolution, not quoted) |
| Cadence | live table; charts daily |
| Free / API | free; API paid |
| Use | Volume spike vs normal ranks the move; daily charts give no intraday value. |

### 6. Aggregated CVD, net delta, taker buy/sell, net longs/shorts
| Item | Value |
|---|---|
| URLs | https://www.coinglass.com/tv (Supercharts) ; Legend indicators: CVD, Taker Buy/Sell Value, Active Buy/Sell Volume, Active Buy/Sell Trades, Open Interest Delta, Aggregated Open Interest |
| Shows | Supercharts default layout, Binance BTCUSDT 1m: Open Interest candles, Net Delta, Aggregated Futures CVD candles, Net Longs, Net Longs (New), Net Shorts, Net Shorts (New), all with "Coins open / No Filter" |
| Seen values | 1m axis appears UTC (inferred: last bar 02:3x matches 08:08 IST). About 01:45-02:00 UTC 10-29: net delta and aggregated CVD fall sharply (CVD to about -5.95K), net longs collapse then partly recover, net shorts rise, OI candles dip then recover. Units NOT_SEEN. |
| Cadence | 1-minute candles, live |
| Free / API | free to view; API paid |
| Use | Observer: best free intraday order-flow confirmation. Severity: delta and net-long collapse on the same 1m bar as price = high severity. |

### 7. Large orders / large trades (whales)
| Item | Value |
|---|---|
| URL | https://legend.coinglass.com/chart (Large Trades, Footprint, Whale Index 1-4) |
| Shows | Bubbles on candles, size = order amount, green buy / red sell; header "Maximum Order Amount 4.09M, Total Volume 14.06M, Number of Orders 9" for the visible range. Footprint was loaded on the chart but its cells were not inspected (NOT_SEEN). Whale Index definitions NOT_SEEN. |
| Cadence | live, intervals 1m to 1W |
| Free / API | viewable anonymously; save/export NOT_SEEN |
| Use | Only free large-trade overlay found. Largest bubbles about $4M, so context rather than a trigger; the "large" threshold is NOT_SEEN. |

### 8. Order-book depth and heat maps
| Item | Value |
|---|---|
| URLs | /pro/depth-delta (aggregated orderbook liquidity delta within 1%, 15m, spot, BTC, plus per-exchange chart) ; Legend: Liquidity Heatmap, Orderbook Liquidity, Orderbook Liquidity Delta, Orderbook Liquidity Ratio |
| Shows | Bid minus ask depth as 15m bars with BTC price. Legend liquidity heatmap not opened (NOT_SEEN). |
| Seen values | Delta strongly negative (red) at the chart tail as price fell to 79.8K |
| Free / API | free; API paid |
| Use | Observer: aggregated bid/ask imbalance at 15m; slower than a raw book but free. |

### 9. Options
| Item | Value |
|---|---|
| URLs | /pro/options/max-pain ; /pro/options/OpenInterest ; /OIExpiry ; /OIStrike ; /VolExpiry ; /VolStrike ; /OptionGreeks ; /net-premium-strike-heatmap ; /pro/futures/OptionsVSFutures (first two opened) |
| Shows | Max pain by expiry (BTC/ETH, exchange selectable) with notional bars; total BTC options OI over time |
| Seen values | Options OI $46.3B on the home strip (+543% flagged, treat as noisy); max pain numbers NOT_SEEN (chart only) |
| Free / API | free; API paid |
| Use | Weak intraday. Expiry-day max pain as a magnet only. |

### 10. Basis / premium
| Item | Value |
|---|---|
| URLs | /pro/futures/PremiumIndex (Binance BTCUSDT, 1m candles) ; /pro/i/coinbase-bitcoin-premium-index |
| Seen values | Coinbase premium -0.14% now, 30d average -0.09%, 1y percentile 9.59%, z-score -1.43, negative streak 36 days; intervals 1m to 1d |
| Free / API | free; API paid |
| Use | Coinbase premium at 1m is a US-flow gauge; persistent negative = US selling. Classic futures basis page NOT_SEEN (Legend has a Basis indicator). |

### 11. ETF flows
| Item | Value |
|---|---|
| URLs | home table ; /pro/i/spot-bitcoin-etf-flows (USD) and siblings (BTC, AUM, volumes, premium) ; /pro/cme/cftc (CME COT) |
| Seen values | 10-28 total +16.08 BTC; 10-27 +2.20K; 10-22 -7.56K; CME BTC OI report dated 2026-10-20 |
| Cadence | daily, T+1 |
| Use | Not intraday. Macro tag only. |

### 12. Bull/bear cycle indicators
| Item | Value |
|---|---|
| URLs | /bull-market-peak-signals ; /pro/i/ahr999 ; /pro/i/bitcoin-rainbow-chart ; /pro/i/pi-cycle-top-indicator ; sidebar: mvrv, mayer multiple, bubble, S2F, 200WMA, CBBI, power law, NUPL, terminal price, thermocap, golden ratio (not opened) |
| Seen values | Peak checklist hit 0/30, progress 40.41%; AHR999 0.4996; rainbow chart renders (band not read); Pi Cycle top not hit |
| Cadence | daily |
| Use | Not for a live trade. Background label only. |

### 13. Other finds
| Page | What | Note |
|---|---|---|
| /pro/futures/TimeZoneDistribution | BTCUSDT volume, liquidations, OI amplitude, price amplitude by Asia / EU / US session | session weighting for severity; daily |
| /pro/heatmap/* (10 pages) | treemaps of OI, OI change, volume, funding, RSI by coin | altcoin focused |
| /pro/futures/InsuranceFund, margin borrow rate, bitcoin dominance | listed, not opened | |
| /pricing, /CryptoApi | API: Hobbyist $29/mo (80+ endpoints, 30 req/min, updates <=1 min, personal use), Startup $79 (130+, 80/min), Standard $299 (150+, 300/min, commercial), Professional $699 (160+, 1200/min), Enterprise custom incl. CSV/bulk export | no free API |

## Event check: BTC 2026-10-28 to 10-29
Legend clock is UTC+5:30 (08:30 UTC shows as 14:00). Supercharts 1m axis appears to be UTC (inferred, confirm).

| Question | Page | What it showed |
|---|---|---|
| Sell near 81,800 at ~08:30 UTC | Legend 15m, Large Trades | Window high labelled 81,800 at about 14:00 shown (08:30 UTC); the largest bubbles of the window there are RED (sell). Per-bubble dollar size NOT_SEEN (window max 4.09M). Seen. |
| Same | Liquidation heatmap 24h | Bright band near 82,000 just above the high; price reversed below it. Seen. |
| Cluster near 79,830 at ~01:00-01:45 UTC | Legend 15m | Fall from about 81,300 to 79,730 between about 06:30 and 08:00 shown (01:00-02:30 UTC), red bubbles stepping down, one near 79,800. Seen. |
| Same | Supercharts 1m | Net delta, aggregated CVD, net longs fall hard about 01:45-02:00 UTC; net shorts rise. Seen. |
| Same | Liquidation Data | 1h liquidations mostly longs (about $93M of $96M, approximate). Seen at low resolution. |
| Same | Depth delta 15m | Negative at the tail. Seen. |
| Same | Coinbase premium | Negative (-0.14%), not resolved to the minute. |
| Per-minute liquidation prints | Liquidation History | NOT_SEEN (daily resolution) |

## Ranked top 8 for live-trade assist
1. Supercharts net delta / aggregated CVD / net longs-shorts, 1m: https://www.coinglass.com/tv
2. Legend Large Trades bubbles + Footprint: https://legend.coinglass.com/chart
3. Liquidation heatmap and liquidation map (where stops sit): /pro/futures/LiquidationHeatMap, /pro/futures/LiquidationMap
4. Liquidation totals 1h/4h/24h long vs short (event size, long flush vs squeeze): /liquidations
5. Coinbase premium index, 1m to 1d: /pro/i/coinbase-bitcoin-premium-index
6. OI by exchange with 1h/4h change: /open-interest/BTC
7. Aggregated orderbook liquidity delta, 15m: /pro/depth-delta
8. Top-trader vs retail long/short (whale divergence): /LongShortRatio
