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

## Addendum 2026-10-10 - Grok X.com sweep (external, unverified)
Source: Grok, operator-pasted. X links not opened by MTS. Tier T3.
Key finding - @VelvetSoul control test:
Backtested OBI on 1600+ Polymarket 5-min BTC markets.
Raw high-imbalance cells: 94-96 pct win rate.
Controlling for price (near-coin-flip cases): 33-56 pct = noise.
Naive OBI mostly restates the price move already made.
Any MTS test of book_imbalance must control for price or it shows a false positive.
@polyquantai: claims 72.4 pct win, 695 trades, Binance book imbalance to trade Polymarket.
Polymarket not perps; fees not mentioned; unverified.
@52kskew: qualitative OBI + OI + funding confluence. No multi-trade P&L.
Other handles: educational order-flow content, no strategy P&L for pure OBI/OFI with fees.
Fee problem: NOTHING FOUND. No public post describing a working maker or queue-position OBI edge on BTCUSDT perps that beats the 0.05 pct round-trip taker wall.
Bottom line: public X evidence of profitable, fee-surviving, pure OBI/OFI on BTCUSDT perps is essentially absent.
Confirms the filed verdict. No new rule to test.
Gemini YouTube/Google sweep still pending.

## Addendum 2 - 2026-10-10 - Grok fuller X sweep (external, unverified, Tier T3)
Source: Grok, operator-pasted. X links not opened by MTS. Same caveat as addendum 1.
FLAG FIRST - net-of-fee profitable pure OBI/OFI on Binance BTCUSDT perps with P&L curve or trade log: NOTHING FOUND.
1. Exact Binance BTCUSDT perp setup (L2 depth levels, ratio threshold, stop/target, holding period): NOTHING FOUND.
Closest: @polyquantai (OBI to trade Polymarket, 72.4 pct win, 695 trades, not perps); @52kskew (discretionary OBI+OI+funding confluence); @buildixtrade (live OBI readings with CVD and Hyperliquid cohort flow).
2. Maker play (counter-trade imbalance, fade the book, queue position, post-only OBI): NOTHING FOUND.
Only tangential: @dexcexhub general queue-for-rebate bot advice, not tied to imbalance, no results.
3. Fee solution (maker rebate OBI, VIP-tier rebate systems, lower-fee venues with net numbers): NOTHING FOUND.
4. Dissent: no posts of the form I backtested OBI on BTCUSDT, fees killed it, here is the negative curve. The absence is itself a finding.
5. Top accounts by evidence quality: @polyquantai, @VelvetSoul (control test), @52kskew, @buildixtrade, @The_JDK99 / @Yuriy_Biko (tied).
6. Binance depth WebSocket angle (@depth@100ms) with code or performance numbers: NOTHING FOUND.
Closest: @skeptikons mentions Binance depth OBI as one input in a 5-min prediction-market stack, no code or numbers.
Two independent Grok sweeps plus the MTS search reach the same place: no net-of-fee OBI strategy on Binance BTCUSDT perps is publicly documented.
Verdict unchanged. No new rule to test. Design rule from addendum 1 stands: control for price.
Gemini YouTube/Google sweep still pending.
