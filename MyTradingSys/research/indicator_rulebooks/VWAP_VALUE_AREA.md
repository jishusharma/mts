# Rule book: VWAP and value area (Berkowitz 1988; Dalton 1990; Shannon 2023)

Sources: FORM = `MyTradingSys/backtest/layers/FORMULAS.md` s18, s29; VAA = `MyTradingSys/research/value_area_acceptance_2026-11-05/RESULT.md`; VERD = `MyTradingSys/research/VERDICTS.csv`; LA = `MyTradingSys/tools/live_aid/`; BB3 = `MyTradingSys/research/orderflow_extracts_1112/extract_BB3c8visnkI.md`; FAB9 = `MyTradingSys/research/orderflow_extracts_1112/extract_9IliXww64uM.md`; FABD = `MyTradingSys/research/orderflow_extracts_1112/extract_DyS79Eb92Ug.md`; SERG = `MyTradingSys/research/orderflow_extracts_1112/extract_4P5WAxyPCis.md`; NKC = `MyTradingSys/research/nk_stocktalk_1113/review/CHECKLIST.md`; TFSRC = `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md`; BLN = https://afajof.org/ (Berkowitz, Logue, Noser 1988); JDM = https://www.scribd.com/ (James Dalton, Mind over Markets 1990); BS = https://alphatrends.net/ (Brian Shannon, Anchored VWAP 2023). All repo paths under `MyTradingSys/` unless stated otherwise.

**Result: VWAP measures volume-weighted average price benchmark from an anchor; Value Area measures the 70% volume distribution band around the POC. Academic and developer rules define them as fair-price benchmarks and auction balance context, never standalone directional triggers. Our empirical BTC measurements show the Dalton 80% rule fails on crypto (achieving 44% [40..49%], n=493, not 80%), and raw VWAP fade rules fail fee-net (-0.566 net R on 1m, n=4433). Use strictly as LEVEL boundaries and auction balance context.**

## 1. What it measures
Measures the volume-weighted average transaction price and auction market value distribution across specified time sessions or anchored events.
- **VWAP:** Computes cumulative dollar volume divided by cumulative volume: $\text{VWAP} = \sum (P_i \cdot V_i) / \sum V_i$, where $P_i = (H_i + L_i + C_i) / 3$ (hlc3). Anchored daily to 00:00 UTC on crypto perpetuals.
- **Value Area (VA):** Derived from Market Profile / Volume Profile theory; defines the continuous price band enclosing 70% of total traded volume surrounding the Point of Control (POC, the highest-volume price bin) for the session (bounded by Value Area High, VAH, and Value Area Low, VAL).
- Formula pointer: `backtest/layers/FORMULAS.md` section 18 (anchored volume profile), section 18.1 (prior-day value: 5m bars, bin width $w=\$10$ or $\$50$, value area 70%), and section 29 (Tom VP return-to-value count). Parity: `NOT VERIFIED-TV` for live multi-exchange aggregation (`VERIFIED-TV` not run for VWAP/VA layer). Code modules: `tools/live_aid/live_aid.html`, `tools/live_aid/home.js` (`dayVwap`, `vaAcceptance`), `backtest/vp_pivot_probe.py`, and `backtest/vp_return_to_value.py`.

## 2. Developer's own rules (SOURCED)
| Item | What is stated | Source |
|---|---|---|
| VWAP Academic Origin | Stephen A. Berkowitz, Dennis E. Logue, and Eugene A. Noser Jr. (1988), "The Total Cost of Transactions on the NYSE", *The Journal of Finance*, Vol. 43, No. 1, pp. 97–112. Introduced VWAP as an objective, volume-weighted execution benchmark to measure institutional transaction costs and market impact against single-price closing metrics. | BLN, SOURCED |
| Market Profile & Value Area Origin | J. Peter Steidlmayer (CBOT 1984) and James Dalton, Eric Jones, Robert Dalton (1990), *Mind over Markets: Power Trading with Market Generated Information*, McGraw-Hill. Formalized Auction Market Theory, Point of Control (POC), and the 70% Value Area (one standard deviation of normal distribution containing ~68.2-70% of activity). | JDM, SOURCED |
| Dalton 80% Value Area Rule | If the market opens or trades outside the previous day's Value Area and then prints two consecutive 30-minute bars (brackets) inside that Value Area, there is an 80% probability that price will auction through and touch the opposite edge of the Value Area. Dalton notes context is essential: balanced profiles work best; aggressive trend days invalidate the rule. | JDM, SOURCED |
| Anchored VWAP (AVWAP) Rules | Brian Shannon (2023), *Maximum Trading Gains with Anchored VWAP*, Alphatrends Publishing. Anchors VWAP to significant market turning points (major swing lows, swing highs, IPOs, high-volume gap events). Rules: (1) Price above AVWAP indicates buyers from that event are in control (bullish bias); price below indicates trapped buyers / sellers in control (bearish bias). (2) Avoid blindly buying falling dips into an AVWAP; wait for stabilization, higher lows, and reclamation of the line. (3) Look for the "pinch" (compression of moving averages and AVWAP before expansion). | BS, SOURCED |
| Developer Directional Signals | Original developers and academic authors state NO automated buy/sell signals, NO mechanical entry rules, and NO fixed stops. Both VWAP and Value Area are equilibrium context benchmarks reflecting market consensus of value. | BLN, JDM, BS, SOURCED |

## 3. What the internet and crypto traders say
| Claim | Source URL | Evidence grade |
|---|---|---|
| Dalton 80% rule applied to intraday equity index futures | MarketCalls / Trading literature: https://www.marketcalls.in/market-profile/the-80-percent-rule-in-market-profile.html | measured (T2, traditional futures session profile; sample and period not fully costed; SOURCED) |
| Anchored VWAP support/resistance pinch setup | Brian Shannon / Alphatrends: https://alphatrends.net/ | anecdote (T3, discretionary swing setup on US equities; no costed statistical sample; SOURCED) |
| VWAP standard deviation band mean reversion (fade +-2 SD) | LuxAlgo / TradingView community scripts: https://www.tradingview.com/script/ | anecdote (T3, indicator overlay; visual chart examples without trade ledger; SOURCED) |
| Intraday VWAP institutional retest long/short | Warrior Trading / Day trading education: https://www.warriortrading.com/volume-weighted-average-price/ | anecdote (T3, retail scalping heuristic; no verified ledger or fee accounting; SOURCED) |
| Crypto 24/7 session profile value area rotation | FTMO Market Profile Guide: https://ftmo.com/en/market-profile-trading/ | anecdote (T3, educational concept description for crypto and FX; SOURCED) |
| Crypto perpetual VWAP slope as algorithmic trend gate | Crypto Twitter / Substack quantitative blogs | UNVERIFIED (common trading advice; no audited fee-net ledger provided) |

## 4. What our analysts say (extracts)
| Analyst | Their rule in plain words | File pointer |
|---|---|---|
| Tom | Value area holds 70% of period volume; outside value is price discovery. Side of day VWAP sets directional bias: trading below VWAP inclines market bearishly. Re-acceptance sequence: breakout outside value, test of value area high/low from outside, rejection, and re-acceptance sets up the trade. | `MyTradingSys/research/orderflow_extracts_1112/extract_BB3c8visnkI.md:46-48,67-69`; `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:25` |
| Fabio | Value area low (VAL) is a structural target. Opening inside prior value area indicates a range day; expect to stay inside and look for fades at the boundaries. Breakout alone is price discovery; true acceptance requires a range to form outside the previous value area. Preferred long is at VAL on absorption. | `MyTradingSys/research/orderflow_extracts_1112/extract_9IliXww64uM.md:25-29,39-41`; `MyTradingSys/research/orderflow_extracts_1112/extract_DyS79Eb92Ug.md:34-36,83`; `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:28` |
| Serge Hoffmann | Far from VWAP, if tape speed slows while a passive seller/buyer absorbs liquidity, expect mean reversion back toward VWAP. At a balance-area edge, slow trading means price rejection; fast trading means acceptance and breakout. | `MyTradingSys/research/orderflow_extracts_1112/extract_4P5WAxyPCis.md:34,60-62` |
| NK (StockTalk) | Looks for a price return to VWAP or moving averages after a breakout before buying. Uses 1h green candle close above VWAP as entry trigger with stop placed below 1h VWAP or 5m low. Trails profits after R3 with VWAP. | `MyTradingSys/research/nk_stocktalk_1113/review/CHECKLIST.md:120-122,290-294` |
| Krown | Uses volume profiles to define balance zones (KR-S3, TOM-7 range trading). Day-anchored VWAP serves as a rising average pullback line inside a healthy trend (KR-S5, TOM-4). Notes volume/volatility peaks define exhaustion rather than raw levels. | `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:987-990` |
| CryptoCred | NO-SOURCE: does not use VWAP or Value Area (uses structural swing high/low levels, horizontal S/R flips, and Fibonacci retracements). | none found |
| Malkan | NO-SOURCE: uses strictly OHLC price bars for Wilder RSI(14) and moving averages; no VWAP or volume profile used. | none found |
| CCU | NO-SOURCE: uses 50/200 MA, Stoch RSI, and WaveTrend; no VWAP or value area profiles used. | none found |
| Habib / CBP | NO-SOURCE: no extract mentions VWAP or Value Area. | none found |

## 5. OUR measurements
Pointers to our studies found by repository search (study folders and methodology descriptions; no numbers per card instructions):
- `MyTradingSys/research/value_area_acceptance_2026-11-05/`: Empirical study (`accept80.py`, `RESULT.md`) on BTC 1m order flow evaluating Dalton 80% rule (two 30m closes back inside prior UTC day value area predicting opposite VA edge touch) and post-acceptance continuation below VAL.
- `MyTradingSys/research/tom_v2_gross_first_2026-11/`: Evaluation of Tom return-to-value hypothesis (`PRE_REG.md`, `RESULT.md`, `full_report.md`) against a near-band placebo on BTC DEV_EXT data.
- `MyTradingSys/research/rumers_2026-11-01/`: Systematic evaluation (`PRE_REG.md`, `DEV_CHECK.md`) of frozen technical setups on BTCUSDT 1m DEV, including rule R3 (RUMERS-VWAP-SEPARATOR-MEAN-REVERSION).
- `MyTradingSys/research/pit_levels_2026-10-16/`: Backtest study (`REPORT.md`, `PHASE2_SETUP_CANDIDATE_STUDY.md`) evaluating failed auctions at the prior-day value area edge (FAB-4 / TOM-12 setup candidate family).
- `MyTradingSys/research/btc_thin_zone_retest_1112/`: Study (`RESULT.md`) testing low-volume node (thin-zone) pass-through and accepted-breakdown retests relative to volume profile nodes.

## 6. How to read it now on Live Aid
- **Price vs Day VWAP Tile** (`tools/live_aid/live_aid.html` container `.tile #g-vwap`): Displays current price distance and sign relative to day VWAP ($HLC3$ from 00:00 UTC). Color indicates side: green when price is above VWAP (bullish tilt), red when below VWAP (bearish tilt). Subtext displays test status (`vt.result`, e.g. "test bounce", "test cross", or "no test in last 5 x 1m").
- **Value Area and Acceptance Panel** (`tools/live_aid/live_aid.html` section `<!-- 2c2c. VALUE AREA + ACCEPTANCE -->`, `tools/live_aid/home.js`):
  - Displays prior UTC day profile benchmarks: `VAL` (Value Area Low), `POC` (Point of Control), `VAH` (Value Area High), and current `Price`.
  - Displays **Acceptance flag**: computed by `vaAcceptance` using two consecutive 30-minute bar closes. Possible states: `ACCEPTED BELOW VAL`, `ACCEPTED ABOVE VAH`, `ACCEPTED BACK INSIDE`, or `no acceptance flag`.
  - Explanatory footer tag explicitly warns: *"Descriptive only: a 2 x 30m close outside or inside the prior day's value is context, never a signal."*
- **Momentum Panel** (`tools/live_aid/live_aid.html` table `#strip`): Under "More detail", displays VWAP distance and moving average alignment.
- **Level Story** (`tools/live_aid/levelstory.js`): Maps confluence tags when price trades within proximity of prior-day VAH, VAL, POC, or day VWAP.

## 7. Confluence role: LEVEL
VWAP and Value Area serve strictly as dynamic LEVEL boundaries (auction equilibrium anchors and balance/imbalance boundaries).
- May add confidence to: a mean-reversion fade setup when price rejects an extreme outside boundary (VAL/VAH) back into value, provided CVD and aggressive delta confirm absorption; or a trend continuation setup when price cleanly breaks and accepts outside prior value on heavy volume and directional delta.
- Rule in one line: Never trade a raw VWAP touch or value area boundary as a directional signal; use them as auction equilibrium levels and regime context only. Today it is CONTEXT ONLY.

## 8. Open tests
- Card `placebo-for-the-77-acceptance-claim-rand`: Systematic evaluation of random-walk placebo drift against the 77% half-width continuation claim following VAL acceptance.
- Card `vwap-regime-direction-gate`: Test whether day-VWAP side (price above vs below 00:00 UTC VWAP) provides a statistically valid filter on 15m/1h momentum breakout trades across BTC, ETH, and SOL.
- Card `anchored-vwap-swing-pinch`: Formalization and backtest of Brian Shannon's AVWAP swing-low pinch setup on 4h/1d crypto perpetuals with defined structural stops.
- Card `lvn-thin-zone-pass-through`: Quantitative test of price traversal velocity and fill rate through low-volume nodes (LVNs) between adjacent value areas.
