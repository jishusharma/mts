# Rule book: Footprint / large trades (Trevor Harnett / MarketDelta 2003, Fabio Valentini)

Sources: FORM = `backtest/layers/FORMULAS.md` s28; OF_BARS = `backtest/layers/fabio/orderflow_bars.py`; SPEC = `research/fast_track_2026-09-27/FABIO_V3_SPEC.md`; CVD_CON = `research/fabio_cvd_2026-10-30/CVD_CONCEPTS.md`; LTA = `research/large_trade_absorption_2026-10-30/RESULT.md`; FP_CHK = `research/footprint_12h_1112/CHECK.md`; BT_EXIT = `research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md`; LA_STEPS = `tools/live_aid/STEPS.md`; LA_COLL = `tools/live_aid/flow_collector.py`; LA_HTML = `tools/live_aid/live_aid.html`; HABIB = `research/habib_concept_book_2026-11/HABIB_CONCEPT_BOOK.md`; HARN = Trevor Harnett / MarketDelta educational manuals and patent/trademark filing (2003); EMOJI = https://emojitrading.com/order-flow-trading/order-flow-history/ (fetched 2026-11-13); EXO = https://exocharts.com/ (fetched 2026-11-13); TV_FP = https://www.tradingview.com/support/solutions/43000694800-volume-footprint/ (fetched 2026-11-13). All paths under `MyTradingSys/` unless stated otherwise.

**Result: Footprint charts decompose intra-bar volume into executed aggressive buys (at ask) and sells (at bid) by discrete price ticks. The inventor and order-flow analysts frame absorption and imbalances as auction exhaustion or continuation only when contextualized at structural levels; our tests confirm raw large-trade absorption alone lacks a reversal edge (-0.5% first 54.7% vs +0.5% first 35.8% after absorbed sells, n=95), while bare bigtrade exit policies fail fee-net across timeframes.**

## 1. What it measures
Measures microstructural order flow within each price bar: executed market buy orders (lifting the ask) versus executed market sell orders (hitting the bid) segmented across discrete price bins. Derives bar delta (`buy_vol - sell_vol`), diagonal price imbalances (e.g. 3:1 ratio of ask volume to bid volume diagonally below), Point of Control (POC, price bucket with highest executed volume), and absorption (heavy aggressive volume failing to push price past passive limit liquidity).
Formula pointer: `backtest/layers/FORMULAS.md` section 28.1 (`NOT VERIFIED-TV`, internal custom aggregations from exchange `aggTrades`). Code modules: `backtest/layers/fabio/orderflow_bars.py` (`parse_fp`, 10 USD binning, OURS), `tools/live_aid/flow_collector.py` (`Footprint` class, `FP_BUCKET = 10`), and `scripts/dev/footprint_12h.py`.

## 2. Developer's own rules (SOURCED)
| Item | What is stated | Source |
|---|---|---|
| Who & Year | Trevor Harnett, electronic trader and founder of MarketDelta LLC; invented and introduced the Footprint® chart in 2003 (trademarked by MarketDelta) | HARN, EMOJI |
| Core Structure | Displays bid volume on the left side (market sell orders hitting the bid) and ask volume on the right side (market buy orders lifting the ask) at each price level within the bar | HARN, EMOJI |
| Diagonal Imbalance | Evaluates aggressive buyer vs seller dominance diagonally (comparing ask volume at a price against bid volume one tick below). Standard imbalance multiplier is typically 300% (3:1) or 400% (4:1) | HARN, EMOJI |
| Stacked Imbalances | Three or more consecutive diagonal imbalances stacked vertically indicate aggressive initiative buying or selling, serving as immediate microstructural support or resistance | HARN |
| Absorption & Exhaustion | Occurs when aggressive market orders surge at bar extremes (high or low) but fail to create price progress, indicating aggressive orders were completely absorbed by resting passive limit orders (icebergs). The rule is to trade *against* the absorbed aggression on a rotation away | HARN |
| Unfinished Auction / Business | When a candle extreme shows non-zero bids and asks (neither side prints zero at the absolute extreme tick), auction theory states the auction at that extreme is unfinished and price frequently revisits that level | HARN |
| Context / Location Rule | Order-flow patterns must never be traded in isolation; absorption and stacked imbalances require location context (daily highs/lows, Value Area High/Low, or Point of Control) | HARN |
| Timeframe & Stated Edge | Operates across intraday tick, volume, and time bars; no fixed win-rate or statistical edge claim is published in the base manual (discretionary auction market framework) | HARN |

## 3. What the internet and crypto traders say
| Claim | Source URL | Evidence grade |
|---|---|---|
| Diagonal imbalance at 3:1 ratio indicates directional initiative | Exocharts Knowledge Base: https://exocharts.com/ | anecdote (T3, platform convention; no fee-costed sample) |
| Stacked imbalances (3+ rows) act as dynamic support/resistance retest zones | TradingView Volume Footprint Guide: https://www.tradingview.com/support/solutions/43000694800-volume-footprint/ | anecdote (T3, documentation guide; no backtest sample) |
| Order Flow Imbalance (OFI) from limit order queues predicts short-term price impact | Cont, Kukanov, Stoikov (Journal of Financial Econometrics, 2014): https://doi.org/10.1093/jjfinec/nbt003 | measured (T1, econometric study of US equities LOB events, statistically significant R^2 for short-term price change) |
| Delta divergence at structural highs/lows signals impending reversal | ClearEdge Trading Order Flow Guide: https://clearedge.trading/order-flow/ | anecdote (T3, visual discretionary examples; no costed sample) |
| Footprint absorption faders achieve high win-rate scalps on crypto perps | TradeZella Order Flow Concepts: https://tradezella.com/ | anecdote (T3, vendor educational material; costs omitted) |
| Intra-bar Volume-at-Price conditional distributions forecast order book supply | Phee & Balch (arXiv:2610.22727, 2024): https://arxiv.org/abs/2410.22727 | measured (T1, diffusion transformer model on Level-3 order flow, machine learning benchmark; no net trading PnL) |
| Unfinished auction high/low is revisited within session >80% of the time | Day Trading Forex / Futures Forum discussions: https://www.elitetrader.com/ | UNVERIFIED (URL discussion summary; unverified retail claim without formal dataset) |

## 4. What our analysts say (extracts)
| Analyst | Rule in plain words | File pointer |
|---|---|---|
| Fabio (Fabervaale) | Footprint defines executed aggressive orders per price level (bid left, ask right); absorption occurs when huge aggressive effort at extreme prices produces no result, getting absorbed by passive limit forces; use big trades + delta footprint profile + VAH/VAL confluence as entry zones | `extracts/_staged_2026-09-27/extracts/fabio_valentini/extracts/extract_Pz8f0wWW12M.md:46-55,208-212`; `extracts/v2/fabio/06R-ebyOhDI_v2.md:21-27` [FAB-030, FAB-034] |
| Tom | Footprint charts are used on smaller timeframes for precise entry timing and identifying risk invalidation levels; fading outside moves without volume is a trap; setups must be backed by real liquidity | `MyTradingSys/research/TOM_VERBATIM_INDEX.md:89` (`yRvMW6lgN1o` [TOM-076]); `extracts/v2/tom/3o1VVsfBmmU_v2.md:36-39,123` |
| Habib / CBP | Footprint diagonal imbalance compares ask volume at a price to bid volume one tick below (3:1 / 300% standard); 3+ stacked imbalances form an active support/resistance zone until broken | `MyTradingSys/research/habib_concept_book_2026-11/HABIB_CONCEPT_BOOK.md:140-141` |
| Krown | Uses the term "footprint" philosophically as the structural trace left by large institutional players on trendlines and volume profiles; does not use intra-candle footprint ladder charts in TA101 | `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_14bxwxC8gBQ.md:22-26` |
| Malkan | Mentions big trades and institutional positioning in price action, but does not use footprint order-flow ladder charts (relies on candlesticks, RSI, Bollinger Bands, and Moving Averages) | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_2HcJ3NeZmEQ.md:12` |
| CCU | No extract mentions footprint charts or intra-candle order flow (uses HTF MAs, Stoch RSI, WaveTrend) | `MyTradingSys/research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md` |
| NK (StockTalk) | No extract mentions footprint charts or order-flow ladders (relies on Hilega-Milega, RSI, and pivots) | `MyTradingSys/research/nk_stocktalk_1113/` (no mentions found) |
| CryptoCred | No extract mentions footprint ladder charts (relies on HTF support/resistance, market structure, and trigger patterns) | `backtest/layers/cryptocred/TEST_PLAN.md` (no footprint mentions) |

## 5. OUR measurements
All rows OURS, copied from the named file. BTCUSDT. No price levels quoted.
| Study folder | What was tested | n | Fee-net result | Verdict |
|---|---|---|---|---|
| `research/large_trade_absorption_2026-10-30/RESULT.md` | Large-trade bars (top/bottom 2% of 5m large-trade net, >= +244.5 / <= -259.2 BTC) and what the next 60 min and 4 h did; DEV 2024-12..2025-12; descriptive, no fees, no edge claim | buy-aggression 1,155; buy-absorbed 99; sell-aggression 1,168; sell-absorbed 95 | Up in 60 min: 47.4% / 50.5% / 53.5% / 44.2%. Up in 4 h: 48.1% / 51.5% / 55.5% / 43.2%. After absorbed big sells, -0.5% came first 54.7% vs +0.5% first 35.8% | 5m: CONTEXT ONLY (aggression fades a little; absorption alone did not reverse price; level x absorption not yet run) |
| `research/bigtrade_2026-10-09/EXIT_POLICIES_RERUN_DEV_2026-10-17.md` | Fabio cvd_absorption layer fires (a footprint-adjacent trigger, not footprint itself), six exit policies, 10 bp taker round trip + 2 bp slippage (assumed), TRAIN 2022-01..2024-06, VALIDATE not read | 15m 2,497; 1h 603 | 15m: all six policies -12.2 to -16.6 bp. 1h: five policies -4.6 to -19.8 bp; time_96_wide_stop_2atr +26.7 bp (+0.35 R) with no VALIDATE read. Summary line: 0 cells positive in both splits | 15m: DO NOT USE. 1h: UNDERPOWERED as a lead only (single DEV cell of 114 trials, VALIDATE unread) |
| same family, original run `EXIT_POLICIES_REPORT.md` (flagged CONTAMINATED, TRAIN ran to 2025-01) | same, with VALIDATE 2025-01..06 | 1h 687 TRAIN / 120 VALIDATE | cvd_absorption 1h time_96: +26.9 bp TRAIN, -63.5 bp VALIDATE | the 1h positive does not hold out of sample |
| `research/orderflow_views_2026-10-14/RESULT.md` | CVD divergence with the OI split, 1m and 5m (not a footprint cell read) | see CVD.md section 5 | DEV rerun DIV minus CONTROL within +-0.022; 0 of 4 pass | 1m, 5m: DO NOT USE |
| `research/footprint_12h_1112/CHECK.md` | MTS 12h footprint (delta, POC) vs the Legend CoinGlass 12h footprint | 0 bars compared | Status in the file: pending, chart profile not connected | 12h: UNTESTED (parity NOT_MEASURED) |
Fee-net footprint-cell outcome study (stacked imbalance, POC rejection, per-level delta): NOT_MEASURED, none in the repo. Regime mix and DEV / VALIDATION / RECENT split: NOT_MEASURED for the large-trade study (DEV 2024-12..2025-12 only, 2026 untouched).

## 6. How to read it now on Live Aid
Panel "Timeframe strip" / "Forced moves" / "Money":
- Tags `#uo-fp` and `#uo-fp-tf` in `tools/live_aid/live_aid.html`:
  - Tag `#uo-fp-tf`: Displays 15m / 1h footprint bar metrics derived from public `aggTrades` (delta BTC, price vs POC in 10 USD buckets, largest print, large buy/sell trade counts). Label shows "Bybit perp, collector" when fresh (< 2x cadence + 2 min) or "footprint feed stale since HH:MMZ".
  - Tag `#uo-fp`: Displays Binance USD-M BTCUSDT 12h footprint (00:00-12:00 / 12:00-24:00 UTC) with 10 USD bucket, 3:1 imbalance over 3 rows, and 70% value area (`tools/live_aid/live_aid.html:245`).
- Re-read cadence handled via `tools/live_aid/footprint_cadence.js` (hourly outside US open; 15m from -2h; 1m from -2 to +15 min). All displays are context only.

## 7. Confluence role: FLOW
May add confidence to entry execution and risk placement at qualified structural levels (Value Area High/Low, swing extremes, or defended levels). Serves as a timing confirmation or veto (e.g. do not fade a move showing stacked initiative imbalances; look for absorption at key levels to tighten stop placement). It is never an entry by itself: no fee-net out-of-sample pass exists. Today: context only.

## 8. Open tests
- `edge-large-trade-level-absorption`: Test absorption of large trades (p99) conditioned on proximity to structural levels (VAH/VAL, daily high/low), testing directional reversal edge vs raw baseline.
- `footprint-12h-legend-parity`: Complete Legend CoinGlass 12h footprint parity cross-check once MTS Charts profile connects (`research/footprint_12h_1112/CHECK.md`).
- `footprint-stacked-imbalance-retest`: Test fee-net expectancy of 3:1 stacked diagonal imbalances on 15m/1h BTCUSDT perp as support/resistance retest entries.
