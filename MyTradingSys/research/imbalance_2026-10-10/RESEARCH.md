# RESEARCH — Order Book Imbalance: Free Data, Implementations, Evidence
# Session: MTS-2026-10-10-DSA-COO
# Method note: OBI signal, free data sources for Binance/other exchanges, net-of-cost evidence.
# Source tiers: T1 peer-reviewed, T2 arXiv/SSRN with method, T3 practitioner.

## T1 — Peer-Reviewed
Fee Structure and Order Flow Informativeness (Springer 2026, Open Access)
- Binance zero-fee to fee transition: OFI explanatory power 5% -> 21% after fees.
- TFI stronger predictor than OFI. Fees screen uninformative orders.

Bitcoin wild moves: order flow toxicity and price jumps (RIBAF 2025)
- VPIN predicts future Bitcoin price jumps. Persistent, time-zone and day-of-week effects.
- No net-of-cost strategy result.

Net buying pressures in derivatives and spot (JIFMIM 2025)
- Cross-market order imbalance improves return/volatility prediction.
- Driven by sentiment and liquidity. No net-of-cost result.

## T2 — arXiv / Working Papers
The Market Maker's Dilemma (arXiv:2502.18625v2, 2025)
- Live Binance BTC perpetual experiment.
- Maker fill likelihood negatively correlated with post-fill returns.
- Commonly-cited imbalance strategies "highly unprofitable".
- Viable maker strategies require contrarian (counter-trading) approach.
- Taker orders: main hurdle is taker fee.

## T3 — Practitioner
Illia Runner (Binance Square): tested OBI on free sample. Signal strongest at 1 second, fades by 5 min. Effect size fraction of retail round-trip cost. "Math doesn't work because it's real and too small."
marlin-strategy (LobeHub): OBI as entry-timing signal, confirmed by 15m momentum + smart-money. Wide stop, 24h hold. Not a scalper.
VisualHFT (Apache 2.0): VPIN, LOB Imbalance, Market Resilience, OTT Ratio. Binance, Bitfinex, Bitstamp, Coinbase, Gemini, Kraken, KuCoin.
Killa (@KillaXBT): imbalances not obligated to fill. Useful counterpoint.

## Free Data Sources (No API Key)
Binance REST: GET /api/v3/depth?symbol=BTCUSDT&limit=100 (free, no key)
Binance WebSocket: wss://stream.binance.com:9443/ws/btcusdt@depth@100ms
Binance Public Data: data.binance.vision -> *bookDepth*.zip
binance-book (PyPI): book.imbalance("BTCUSDT", levels=5) -> -0.55 (ask-heavy). Free, MIT.
crypto-lob-stream (PyPI): L2 order book Parquet, 8 venues. Monthly BTC/ETH/SOL on Hugging Face. MIT.
tickvault (Rust): full-depth snapshots + deltas, 6 venues, Parquet, gap stats. Free.
depthy-mcp: get_depth (bid/ask imbalance), free tier.
crypto-orderbook-mcp (kukapay): calculate_orderbook for 6 exchanges. Free, MIT.
nautilus_trader: OrderBookImbalance backtest tutorial (Binance T_DEPTH). Free.
VisualHFT: VPIN, LOB Imbalance. Apache 2.0.
VPIN Open Source: full VPIN pipeline from Binance aggTrades. MIT.
delta-cluster-framework: delta clusters, buy/sell volume, imbalance per price level. Free.
followsm-sdk: VPIN, 1% toxicity, L1 imbalance, depth bands. Free tier.
bobByDew (PyPI): real-time order book imbalance visualization. Free.
Aperiodic: L1/L2 imbalance (5/10/20/25 levels), bid/ask ratio. API tiered.
Amberdata: Order Book Pressure = (bid depth - ask depth) / (bid depth + ask depth). API tiered.
Glassnode: Spot/Perp Orderbook Depth Imbalance. 10m/1h/24h. Tiered.

## Key Formulas
OBI = (Bid Volume - Ask Volume) / (Bid Volume + Ask Volume)  [range -1 to +1]
OFI = (bid_volume - ask_volume) / (bid_volume + ask_volume)
VPIN = abs(buy_volume - sell_volume) / total_bucket_volume
Nautilus: min(bid_size, ask_size) / max(bid_size, ask_size) < 0.20 -> FOK against thinner side.

## MTS Current State
snapshot.conditions.book_imbalance: 0.96 (current)
snapshot.order_book_depth.bid_ask_ratio: 0.96
math_object_builder.py ~L395-413: _book < 0.33 -> ask-heavy vs LONG; _book > 3.0 for SHORT.
B146/B147 (stop-width vs fee), B151 (trade-through fill) directly relevant.

## Synthesis
Signal real. Signal small (seconds to minutes). Effect fraction of retail costs.
Not standalone. arXiv: commonly-cited strategies highly unprofitable.
Free data abundant. Fee wall is binding constraint.
No validated net-of-cost OBI strategy found in literature or practitioner record.
Only potentially viable as entry-timing filter on wider thesis. Not backtested with fees.

## Next Steps (MTS protocol)
1. Pre-registered backtest of MTS book_imbalance as entry-timing filter on momentum.
2. Measure net R after fees using verdict.py + PBO, OOS splits, funding included.
3. If survives, test marlin-strategy design (imbalance as entry timing, confirmed by momentum, wide stop, long hold).

# END
## T3 - Practitioner
Illia Runner (Binance Square): tested OBI on free sample. Signal strongest at 1 second, fades by 5 min. Effect size is a fraction of retail round-trip cost. Math does not work because it is real and too small.
marlin-strategy (LobeHub): OBI as entry-timing signal, confirmed by 15m momentum + smart-money. Wide stop, 24h hold. Not a scalper.
VisualHFT (Apache 2.0): VPIN, LOB Imbalance, Market Resilience, OTT Ratio. Binance, Bitfinex, Bitstamp, Coinbase, Gemini, Kraken, KuCoin.
Killa (@KillaXBT): imbalances not obligated to fill. Useful counterpoint.

## Free Data Sources (No API Key)
Binance REST: GET /api/v3/depth?symbol=BTCUSDT&limit=100 (free, no key)
Binance WebSocket: wss://stream.binance.com:9443/ws/btcusdt@depth@100ms
Binance Public Data: data.binance.vision -> bookDepth.zip
binance-book (PyPI): book.imbalance(BTCUSDT, levels=5). Free, MIT.
crypto-lob-stream (PyPI): L2 order book Parquet, 8 venues. MIT.
tickvault (Rust): full-depth snapshots + deltas, 6 venues, Parquet. Free.
depthy-mcp: get_depth (bid/ask imbalance), free tier.
crypto-orderbook-mcp (kukapay): calculate_orderbook for 6 exchanges. Free, MIT.
nautilus_trader: OrderBookImbalance backtest tutorial (Binance). Free.
VisualHFT: VPIN, LOB Imbalance. Apache 2.0.
VPIN Open Source: full VPIN pipeline from Binance aggTrades. MIT.
delta-cluster-framework: delta clusters, buy/sell volume, imbalance per price level. Free.
followsm-sdk: VPIN, 1% toxicity, L1 imbalance, depth bands. Free tier.
bobByDew (PyPI): real-time order book imbalance visualization. Free.
Aperiodic: L1/L2 imbalance (5/10/20/25 levels), bid/ask ratio. API tiered.
Amberdata: Order Book Pressure = (bid depth - ask depth) / (bid depth + ask depth). API tiered.
Glassnode: Spot/Perp Orderbook Depth Imbalance. 10m/1h/24h. Tiered.

## Key Formulas
OBI = (Bid Volume - Ask Volume) / (Bid Volume + Ask Volume). Range -1 to +1.
OFI = (bid_volume - ask_volume) / (bid_volume + ask_volume).
VPIN = abs(buy_volume - sell_volume) / total_bucket_volume.
Nautilus: min(bid_size, ask_size) / max(bid_size, ask_size) < 0.20 -> FOK against thinner side.

## MTS Current State
snapshot.conditions.book_imbalance: 0.96 (current)
snapshot.order_book_depth.bid_ask_ratio: 0.96
math_object_builder.py ~L395-413: _book < 0.33 -> ask-heavy vs LONG; _book > 3.0 for SHORT.
B146/B147 (stop-width vs fee), B151 (trade-through fill) directly relevant.

## Synthesis
Signal real. Signal small (seconds to minutes). Effect fraction of retail costs.
Not standalone. arXiv: commonly-cited strategies highly unprofitable.
Free data abundant. Fee wall is binding constraint.
No validated net-of-cost OBI strategy found in literature or practitioner record.
Only potentially viable as entry-timing filter on wider thesis. Not backtested with fees.

## Next Steps (MTS protocol)
1. Pre-registered backtest of MTS book_imbalance as entry-timing filter on momentum.
2. Measure net R after fees using verdict.py + PBO, OOS splits, funding included.
3. If survives, test marlin-strategy design.

## Related MTS work
T093_TOC_IMBALANCE_KLINES_2026-10-10.md: kline-proxy turn-of-candle imbalance, 4/8/12h, 2022-2026, NO REPLICATION (gross +0.5 bp vs 10 bp fee, net CI95 below zero).
P4_QUARTER_HOUR_IMBALANCE_CORRECTED_2026-10-08.md: same family, 2024-12..2026-09, NO REPLICATION.
This file adds the L2 order book imbalance branch (distinct from kline time-of-day). Not yet backtested in MTS.

# END
