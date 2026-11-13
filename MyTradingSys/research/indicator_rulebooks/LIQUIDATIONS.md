# Rule book: Liquidations and Liquidation Heatmaps (CoinGlass model / Exchange forceOrder feeds)

Sources: CGS = `research/coinglass_usage_2026-10-28/A_liquidation.md`; LIQ = `research/liquidation_layer_2026-10-28/README.md`; KRO = `research/krown_ta101_2026-10-13/extracts/extract_P3rDSh187TE.md`; KRO_Q = `research/krown_ta101_2026-10-13/extracts/extract_qEfES84jwwo.md`; ORD_D = `research/orderflow_extracts_1112/extract_DVZVE9rXGtU.md`; ORD_R = `research/orderflow_extracts_1112/extract_RwQBdF9TSvc.md`; LA_S = `tools/live_aid/STEPS.md`; LA_X = `tools/live_aid/xliq.js`; LA_C = `tools/live_aid/xliq_collector.py`; BIN = https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Liquidation-Order-Streams (Binance USD-M docs, fetched 2026-11-13); CG_DOC = https://docs.coinglass.com/reference/liquidation-heatmap-model2 (CoinGlass API docs, fetched 2026-11-13); CG_X = https://x.com/coinglass_com/status/1833073677015126058 (CoinGlass on X, fetched 2026-10-28); HYP = https://hyperliquid.gitbook.io/hyperliquid-docs/trading/liquidations (Hyperliquid docs, fetched 2026-10-28); SIM = https://simplemarkets.io/blog/post/coinglass-liquidation (SimpleMarkets, fetched 2026-10-28); KYL = https://kyledoops.substack.com/p/harnessing-liquidation-zones-magnet (Kyledoops, fetched 2026-10-28); BIT = https://bittime.com (Bittime, fetched 2026-10-28); SEU = https://arxiv.org/abs/2607.27070 (Garcia Seuma, 2026-07-29, arXiv:2607.27070, fetched 2026-10-28). All repo paths under `MyTradingSys/` unless stated otherwise.

**Result: Liquidations and liquidation heatmaps are algorithmic forced-exit feeds and modelled open-interest estimates, not an entry signal or guaranteed price magnet. Our data shows no fee-net edge has been measured yet (ledger and live monitor only); the primary verified function is a descriptive context gauge of forced flow and exhaustion.**

## 1. What it measures
Measures forced-closing market orders executed by exchange risk engines to cover insolvent margin accounts, and projects estimated liquidation price clusters derived from open interest, price history, and leverage distributions.
Formula pointer: `backtest/layers/FORMULAS.md` section N (none found, `NOT VERIFIED-TV`; no Pine formula exists for exchange forced liquidations). Code modules: `tools/live_aid/xliq_collector.py` (parsers `parse_bybit`, `parse_binance`, `parse_okx`), `tools/live_aid/xliq.js`, `tools/live_aid/live_aid_indicators.js` (`liqSum`, `liqSide`). Realized event notional: `USD = qty * execution_price` (OURS). Heatmap cell: `[x_time_index, y_price_index, relative_intensity]` (SOURCED: CG_DOC).

## 2. Developer's own rules (SOURCED)
| Item | What is stated | Source |
|---|---|---|
| Who & Origin | CoinGlass (formerly Bybt, crypto derivatives data vendor); exchange liquidation engines codified in exchange margin rules (Binance, Bybit, OKX, Hyperliquid) | CGS:9-20, CG_DOC, BIN, HYP |
| Model 1 Definition | "only calculates high leverage, 10X, 25X, 50X, 100X", intended for short-term trading | SOURCED: CG_X, CGS:35 |
| Model 2 Definition | "calculates all leverage", intended for long-term trading; per exchange and pair | SOURCED: CG_X, CGS:35, CG_DOC |
| Model 3 Definition | Aggregated coin-level liquidation heatmap calculating multi-market parameters and deep liquidity distribution across various leverage amounts | SOURCED: CG_DOC, CGS:13,35 |
| Model Output Nature | Heatmap intensity values are relative model-derived indices, not an exact accounting ledger of open limit orders or absolute guaranteed liquidation USD | SOURCED: CG_DOC, SIM, CGS:35 |
| Exchange Feed Throttling | Binance USD-M WebSocket `forceOrder` stream pushes only the single largest liquidation order within each 1000 ms window per symbol; intermediate liquidations are dropped, making the stream a lower bound | SOURCED: BIN, CGS:55, LA_C:7 |
| Hyperliquid Liquidation Engine | Positions liquidated upon breaching maintenance margin using a mark price blend; orders >100k USDC capped at 20% order book submission with a 30-second cooldown; backstop to Liquidator Vault below 2/3 maintenance margin | SOURCED: HYP, CGS:45 |
| Stated Trading Rules | Vendor pages state no quantitative entry rules, win rates, or stops; they state descriptive monitoring of liquidation clusters and volume spikes | SOURCED: CG_DOC, CGS:35 |

## 3. What the internet and crypto traders say
| Claim | Source URL | Evidence grade |
|---|---|---|
| Heatmaps act as price magnets pulling price like gravity into dense liquidity clusters | Kyledoops Substack: https://kyledoops.substack.com/p/harnessing-liquidation-zones-magnet | anecdote (T3, vendor promotion; no costed sample or trade ledger) |
| Heatmaps show zones of elevated probability, not guaranteed price targets; alerts should sit short of clusters | SimpleMarkets: https://simplemarkets.io/blog/post/coinglass-liquidation | anecdote (T3, risk advisory; no quantitative backtest) |
| Clusters act as major support and resistance where big players accumulate or flip trends | Bittime Guide: https://bittime.com | anecdote (T3, educational blog; no statistical evidence) |
| Sharp open interest drop with volume spike signals capitulation; price drop with rising OI confirms trend | TradingView CME BTC Capitulation Script: https://in.tradingview.com/script/4Ww1ZJ40 | anecdote (T3, closed-source Pine indicator; no fee-net table) |
| Taker order-flow variance decline precedes cascades across BTC crashes, but no reliable per-event early alarm | Garcia Seuma (arXiv:2607.27070): https://arxiv.org/abs/2607.27070 | measured (T1 preprint, empirical study of 7 BTC cascade events 2022-2025; no predictive trading edge) |
| Forced liquidations exhaust order book depth causing extreme execution slippage | Sepper (arXiv:2603.09164): https://arxiv.org/abs/2603.09164 | measured (T1 preprint abstract, microstructure model of slippage-at-risk; theoretical/simulated) |
| Two-regime liquidity recovery occurs following perpetual futures liquidation cascades | J. FinTech and Digital Assets: https://journals.lincoln.ac.nz/index.php/JFDA/article/view/1395 | UNVERIFIED (T1 journal paper; search summary only, full text not fetched) |
| High leverage and auto-deleveraging turned October 2025 sell-off into a liquidity cascade | FTI Consulting: https://www.fticonsulting.com/en/canada/insights/articles/crypto-crash-october-2025-leverage-met-liquidity | UNVERIFIED (T3 consultancy report; figures unverified) |

## 4. What our analysts say (extracts)
| Analyst | Their rule in plain words | File pointer |
|---|---|---|
| Krown | A cascade is algorithmic deleveraging wiping out borrowed conviction, not organic selling; liquidation prints carry zero human opinion; high OI + hot funding indicates loaded potential energy ("the mountain is loaded with snow"); once forced selling exhausts, sharp V-shaped recoveries often occur; keep liquidation price far from liquidity pools ("do not multiply by zero") | SOURCED: `research/krown_ta101_2026-10-13/extracts/extract_P3rDSh187TE.md:18,40,52,78` [t=00:01:20, 00:08:23, 00:20:21, 00:27:55] |
| Krown (Wicks) | Candle wicks capture emotional overshoots, often forced liquidations, whereas candle closes reflect agreed market value; zones should be drawn between wick extreme and candle close | SOURCED: `research/krown_ta101_2026-10-13/extracts/extract_qEfES84jwwo.md:16` [t=00:05:06] |
| Tom | Does not trade liquidation prints directly; historical backtest snapshots lack live liquidation data; liquidation flow is treated alongside book imbalance and funding as live proof context | SOURCED: `research/fast_track_2026-09-27/TOM_CORE_BT.md:15` |
| Order-flow extract DVZ | Forced-flow proxies for BTC include liquidation stream bursts, taker-sell volume spikes with price not following (absorption), and funding extremes | SOURCED: `research/orderflow_extracts_1112/extract_DVZVE9rXGtU.md:43` |
| Order-flow extract RwQ | Rejects classic "stop-hunt" retail myth; crypto liquidation cascades represent distinct mechanical forced-market executions of leveraged positions | SOURCED: `research/orderflow_extracts_1112/extract_RwQBdF9TSvc.md:36` |
| Pizzino | Discusses institutional and sovereign paper liquidations in macro cycle context; no quantitative intraday liquidation rule | SOURCED: `research/yt_feed_2026-10-31/transcripts_jason-pizzino-new10/es_I-z8Pnek_timed.txt:18` [t=00:18:06] |
| Fabio | NO-SOURCE: does not use liquidation heatmaps or liquidation prints (0 hits in canonical transcripts) | none found |
| CryptoCred | NO-SOURCE: no extract mentions liquidation heatmaps or liquidation feeds | none found |
| CCU | NO-SOURCE: no extract mentions liquidation heatmaps (relies on MA, Stoch RSI, WaveTrend) | `research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md` |
| Habib / CBP | NO-SOURCE: no extract mentions liquidation heatmaps | none found |
| NK (StockTalk) | NO-SOURCE: no extract mentions liquidation heatmaps (relies on Hilega Milega, RSI, moving averages) | `research/nk_stocktalk_1113/` |
| Malkan | NO-SOURCE: no extract mentions liquidation heatmaps | `research/malkan_extract_2026-10-15/` |

## 5. OUR measurements
Pointers to our studies found by repository grep (no numbers in this section per task instruction):
- `MyTradingSys/research/liquidation_layer_2026-10-28/` (README.md, BANDS_LEDGER.csv): Pre-registered framework evaluating CoinGlass and Hyperliquid liquidation bands on forward data, testing touch rates (H1), reversal >=1 ATR (H2), and realized forceOrder notional (H3) against random placebos.
- `MyTradingSys/research/coinglass_usage_2026-10-28/` (A_liquidation.md): Systematic qualitative survey of CoinGlass liquidation heatmaps (Models 1-3), Hyperliquid liquidation maps, and Binance forceOrder feeds.
- `MyTradingSys/research/sim_desk/results/` (c26-q7-liquidation-bands.json, dir-liquidation_layer_2026-10-28.json): Forward ledger logging and simulation capture of liquidation bands.

## 6. How to read it now on Live Aid
- **Liquidations glance tile** (`tools/live_aid/live_aid.html`, `tools/live_aid/STEPS.md:29`): Displays 5-minute net liquidation state: `longs flushed`, `shorts flushed`, `both sides` (whipsaw), or `none`.
- **Liquidations detail panel** (`tools/live_aid/STEPS.md:29,56-68`, `tools/live_aid/live_aid_indicators.js`): Summarizes USD liquidated per side over 1, 5, and 15-minute rolling windows across Bybit (`allLiquidation.BTCUSDT`), Binance (`forceOrder`), and Deribit (trade liquidation flag). Shows a tape of the last 8 prints; flags dominant side when one side >= 2x the other, and marks individual "big prints" >= 100,000 USD.
- **Cross-exchange liquidation feed (xliq)** (`tools/live_aid/xliq.js`, `tools/live_aid/xliq_collector.py`): Live Aid row displaying cross-venue status and actionable context:
  - Big long liquidations: `"So what: big long liquidations on <venues> at <price> = forced selling, watch for absorption. Read: WAIT for the flush to be absorbed, then long only."`
  - Big short liquidations: `"So what: big short liquidations on <venues> at <price> = forced buying (squeeze), do not chase. Read: WAIT for exhaustion, then short only."`
  - Both sides: `"So what: big liquidations on both sides = whipsaw. Read: WAIT."`
- **What the money is doing panel** (`tools/live_aid/STEPS.md:37`): Tracks Bybit 5-minute flush/squeeze events combined with open interest drops and taker flow.

## 7. Confluence role: LEVEL
Liquidations and liquidation heatmap clusters serve as dynamic LEVEL context and EXHAUSTION boundaries.
May add confidence to: fading an extreme move after a major liquidation cascade or cluster touch when open interest flushes, realized liquidation prints peak, and CVD confirms absorption (taker selling absorbed by resting bids); or a veto against chasing breakouts directly into large opposing liquidation clusters or buying during active cascading liquidations.
Rule in one line: Never trade a raw liquidation cluster or liquidation spike as an entry; use liquidation prints as an exhaustion veto and wait for post-flush absorption to confirm a level. Today it is CONTEXT ONLY.

## 8. Open tests
- Card `liquidation-layer-trust-ledger`: Execution of the pre-registered H1/H2/H3 tests on `BANDS_LEDGER.csv` using forward Binance 1m klines and recorded `forceOrder` stream against distance-matched placebo levels.
- Study `forceorder_absorption_reversal`: Measure forward fee-net expectancy of fading long-liquidation spikes (>100k USD on 1m) conditioned on positive taker delta divergence (absorption) over 3/6/12 bars on BTCUSDT.
- Study `coinglass_model1_touch_drift`: Systematic forward test of price drift and touch probabilities within 24 hours of CoinGlass Model 1 bright clusters versus random control bands.
- Study `hyperliquid_whale_sweep`: Forward verification of price behavior and slippage when spot approaches listed Hyperliquid whale liquidation levels.
