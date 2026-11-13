# Rule book: Open interest (exchange feeds / CME / Binance)

Sources: OI_CONC = `MyTradingSys/research/oi_side_2026-10-30/OI_CONCEPTS.md`; KROWN = `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_P3rDSh187TE.md`; SPEC = `MyTradingSys/research/eagle_eyes_picture_2026-10-28/OI_COMMENTARY_SPEC.md`; LA = `MyTradingSys/tools/live_aid/live_aid.html`; CME = https://www.cmegroup.com/education/courses/introduction-to-futures/open-interest.html (CME Group official definition and counting rules); BIN_DOCS = https://binance-docs.github.io/apidocs/futures/en/#open-interest (Binance USDS-M and COIN-M Futures Open Interest API documentation); CG = https://www.coinglass.com/open-interest (CoinGlass aggregated crypto open interest and leverage analytics); MURPHY = John J. Murphy, "Technical Analysis of the Financial Markets", New York Institute of Finance, 1999 (Chapter 5: Volume and Open Interest). All repo paths under `MyTradingSys/` unless stated otherwise.

**Result: Open interest counts active, unliquidated derivative contracts (potential market energy); it measures participation and fuel, not directional bias. The six price/OI states describe whether money is entering, leaving, or coiling; our studies show post-flush OI behavior offers no directional predictive edge (4h win rate 53-56% vs 52% base), but persistent drain doubles the likelihood of outsized volatility. Use Open Interest strictly as a FLOW context gauge and liquidation cascade risk veto, never as a directional entry trigger.**

## 1. What it measures
Measures the total number of outstanding, active derivative contracts (futures or perpetual swaps) that remain unliquidated, unexercised, and unsettled at a given moment in time.
- Each open contract requires exactly one buyer (long) and one seller (short); OI counts the pair as one single contract.
- Formula pointer: `backtest/layers/FORMULAS.md` has no dedicated entry for open interest (NOT IN FORMULAS; positioning data treated as exchange feed context); parity: `NOT VERIFIED-TV` (multi-venue exchange data, not standard single-stream Pine indicators). Code modules: `MyTradingSys/tools/live_aid/live_aid.html` (multi-venue fetch and "What the money is doing" 6-state commentary), `MyTradingSys/research/oi_side_2026-10-30/fetch_metrics.py`, and `MyTradingSys/research/eagle_eyes_picture_2026-10-28/OI_COMMENTARY_SPEC.md`.

## 2. Developer's own rules (SOURCED)
| Item | What is stated | Source |
|---|---|---|
| Origin & Regulatory Concept | Open interest has been standardized since early commodity futures exchanges (codified by CME Group and CFTC). In crypto perpetuals, BitMEX introduced real-time continuous OI (May 2016), later standardized across Binance, Bybit, and OKX. | CME, BIN_DOCS, SOURCED |
| Exchange Core Definition | The total number of open contracts (long or short) held by market participants at the close of a session (CME) or in real-time (crypto perp exchanges) that have not been closed out by an offsetting trade, delivery, or exercise. | CME, SOURCED |
| Counting Mechanics | Every contract has two sides (one buyer and one seller), but only one side is counted: 1 open long + 1 open short = 1 open interest. When both parties open a new trade, OI increases by 1; when both parties close existing trades, OI decreases by 1; when an existing contract is transferred from an old trader to a new trader, OI remains unchanged. | CME, SOURCED |
| Binance Futures API Specifications | Binance serves present OI via `GET /fapi/v1/openInterest` (returns `openInterest` in contract/base units, `symbol`, `time`) and historical OI via `GET /futures/data/openInterestHist` across intervals (`5m` to `1d`). COIN-M inverse futures are served via `GET /dapi/v1/openInterest`. | BIN_DOCS, SOURCED |
| Developer Directional Rules | Exchange API and clearinghouse rulebooks state NO directional trading rules, NO signals, NO price forecasts, and NO stops. Open interest is strictly a clearinghouse ledger metric measuring market size, contract depth, and margin obligations. | CME, BIN_DOCS, SOURCED |

## 3. What the internet and crypto traders say
| Claim | Source URL | Evidence grade |
|---|---|---|
| The 4 canonical Price/OI states: Price Up + OI Up (Long Buildup, strong bull); Price Down + OI Up (Short Buildup, strong bear); Price Up + OI Down (Short Covering, weak bull); Price Down + OI Down (Long Liquidation, weak bear) | CME Group Education: https://www.cmegroup.com/education/courses/introduction-to-futures/open-interest.html | measured (T2, traditional futures clearinghouse canon; classifies capital expansion vs contraction; SOURCED) |
| The 6 price/OI states (including neutral/flat states): Flat Price + Rising OI = Storing potential energy / accumulation for breakout; Flat Price + Falling OI = Quiet position unwind / interest waning | Definedge Securities / Quantsapp derivative scans: https://www.definedgesecurities.com/ | anecdote (T3, vendor classification extending 4-state matrix with neutral price thresholds; SOURCED) |
| Aggregated crypto OI as a fuel gauge: Rapidly climbing OI during price rallies indicates aggressive leverage stacking; high OI combined with extreme funding warns of liquidation cascade vulnerability | CoinGlass Open Interest Analytics: https://www.coinglass.com/open-interest | anecdote (T3, market microstructure monitoring platform; observed leverage flushes; SOURCED) |
| Murphy's open interest trend rules: A healthy trend requires rising volume and rising OI; declining OI during a trend warns of trend exhaustion and impending reversal | John J. Murphy, "Technical Analysis of the Financial Markets" (1999), Ch. 5: https://www.amazon.com/Technical-Analysis-Financial-Markets-Comprehensive/dp/0735200661 | measured (T2, empirical classic principles across commodity and futures markets; SOURCED) |
| Cross-exchange OI divergence: Binance OI rising while Bybit OI falls indicates position migration between venues rather than net global capital inflow | CoinGlass / Hyblock Capital commentary | anecdote (T3, multi-venue order-flow commentary; SOURCED) |
| Open interest divergence with CVD: Bullish price and CVD with falling OI indicates short covering rally rather than new organic spot/perp buying | Crypto Twitter / trading literature | UNVERIFIED (common social trading rule; no costed sample or statistical verification provided) |

## 4. What our analysts say (extracts)
| Analyst | Their rule in plain words | File pointer |
|---|---|---|
| Krown | Open interest relates to how many leveraged contracts exist right now; every open contract is a future exit with a liquidation price. High open interest combined with hot funding does not predict the exact day or time of an avalanche, but indicates the mountain is loaded with snow. Rule: check the weather (funding rate and open interest) before sizing; if you get liquidated you lose everything, so do not multiply by zero. | `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_P3rDSh187TE.md:38-45,76-83` |
| Operator | Dashboard commentary requirement (2026-10-31): live_aid needs "What the money is doing" commentary detailing the six price/OI states, venue disagreements, last flush/squeeze event, and trapped side lines. | `MyTradingSys/research/eagle_eyes_picture_2026-10-28/OI_COMMENTARY_SPEC.md:1-46` |
| Tom | NO-SOURCE: does not use open interest, funding, or long/short ratios as levels, setups, or triggers. 0 hits for "open interest" or "OI" in canonical transcripts. Positioning data is MTS-own. | `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:45` |
| Fabio | NO-SOURCE: does not use open interest (focuses on NQ footprint, delta, CVD, and order-book liquidity; 0 hits in canonical transcripts). | `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:45` |
| CCU | NO-SOURCE: CCU extracts show no open interest usage (relies on 50/200 MA, Stoch RSI, WaveTrend). | `MyTradingSys/research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md:1-35` |
| Malkan | NO-SOURCE: requires strictly OHLC price bars for Wilder RSI(14); no open interest or aggressor order flow used. | `MyTradingSys/research/malkan_extract_2026-10-15/PRE_REG_MALKAN_GFS_BTC.md:32-34` |
| NK (StockTalk) | NO-SOURCE: no extract mentions open interest. | none found |
| CryptoCred | NO-SOURCE: no extract mentions open interest (focuses on price action, S/R levels, triggers). | none found |
| Habib / CBP | NO-SOURCE: no extract mentions open interest. | none found |

## 5. OUR measurements
All rows OURS, copied from the named file. BTCUSDT. No fee-net OI rule has been run in a committed file; fee-net columns say NOT_MEASURED.
| Study folder | What was tested | n | Fee-net result | Verdict |
|---|---|---|---|---|
| `research/oi_side_2026-10-30/RESULT.md` | Binance USD-M 5m OI and price over 30-minute windows (OI up or down >= 0.25%), share up 60 min later; descriptive counts, no fees, no edge claim; DEV 2022-2025 (file's own DEV label) | 35,963 windows; cells 4,985 to 8,023 | NOT_MEASURED. Up 60 min later: OI up/price up 48.5% (n 6,193); OI up/price down 52.7% (4,985); OI down/price up 48.9% (5,428); OI down/price down 53.5% (6,296); all cells 48% to 54%; +0.5%-first vs -0.5%-first between 37.5% and 47.9% vs 39.3% and 48.8% | 5m/30m: CONTEXT ONLY (OI alone gives no direction; gap of about 4 points is below fee level per the file) |
| same file, by year | Short-covering rally (OI down, price up), share up 60 min | per-year cells 842 to 2,817 | 2022 44%, 2023 48%, 2024 52%, 2025 55%; long liquidation (OI down, price down) bounce 2023 58%, 2025 48% | CONTEXT ONLY (sign flips across years; about 5 standard errors swing, regime-dependent) |
| same file, taker-delta split | Taker delta in the window, share up 60 min | buyers 2,035; mixed 3,765; sellers 2,223 | up 60 min 49.4% / 51.6% / 52.6%; next +-0.5% first about a coin flip (38% vs 39% for one split); ratio moved > 1% in about 6% of build-ups (n 133 and 379) | CONTEXT ONLY |
| `research/eagle_eyes_picture_2026-10-28/OI_COMMENTARY_SPEC.md` (line 40, C24 Bybit 5m, 120 days, window not DEV-labelled in the extract) | After an OI flush (price -0.25% and OI -0.2% on a 5m bar), OI path over the next 40 min and 4h forward | rebuilding 18, flat 9, still falling 22 | 4h up 53% / 56% / 55% vs 52% base (gross); still falling: 4h drop > 1% 14% vs 6% base | UNDERPOWERED (n 9 to 22; direction not given by OI) |
| `research/wlow_bounce_bbrsi60_2026-10-16/RESULT.md` | OI as a layer on weekly-low bounce events | 8 | NOT_EVALUATED, every split has a side with n < 10; OI is NOT_IN_DATA on DEV (Binance metrics archive starts 2025-09-01) | UNDERPOWERED |
Backlog notes `edge-oi-flush-1113`, `edge-crowding-reversal-1113`, `edge-forced-move-fade-1113` (INDEX verdict "flush 0/10, crowding 0/24, forced-move 0/128") are not committed, so those counts are NOT_MEASURED here; re-copy once committed. Regime mix and DEV / VALIDATION / RECENT split: only the per-year rows above exist; the rest NOT_MEASURED.

## 6. How to read it now on Live Aid
- **Panel:** "What the money is doing" (`tools/live_aid/live_aid.html` container `#m-wrap` / `.hd`):
  - **Six-State Sentence:** Evaluates price change ($\Delta p$) vs open interest change ($\Delta OI$) over 5m, 15m, and 60m windows (flat threshold = $|\Delta| < 0.1\%$):
    1. *Price up, OI up:* "Money entering on the long side: new longs are buying."
    2. *Price down, OI up:* "Money entering on the short side: new shorts are selling."
    3. *Price up, OI down:* "Money leaving: shorts are covering (a squeeze); the rise is not fed by new buyers."
    4. *Price down, OI down:* "Money leaving: longs are closing or being liquidated (a flush)."
    5. *Price flat, OI up:* "Positions building without a move: both sides adding, pressure stored for the next break."
    6. *Price flat, OI down:* "Positions closing quietly; interest is fading."
  - **Venue Disagreement:** Flags when exchanges diverge ($\ge 0.2\%$ up on one, $\le -0.2\%$ down on another), e.g., "Binance adding, Bybit closing: positions moving between exchanges, net money about flat."
  - **Just Happened (last 60 min):** Highlights liquidation FLUSH (Bybit 5m bar low $\ge 0.25\%$ below prior close with $OI \le -0.2\%$) or SQUEEZE (mirrored upward).
  - **Trapped Side Line:** Marks trapped participants after a flush (e.g., "shorts trapped above <bounce high>; longs trapped below <flush low>") once OI increases by $\ge 0.2\%$.
- **Panel:** "Funding and premium" (`tools/live_aid/live_aid.html` table `#fund`): Displays total `Open int. USD` per venue (Deribit, Bybit, Binance).

## 7. Confluence role: FLOW
Open interest serves strictly as a FLOW and positioning context gauge (liquidation cascade vulnerability thermometer and coiling pressure metric).
- May add confidence to: a veto against opening leveraged breakout longs when OI is heavily stacked (>95th percentile) and funding is hot positive; or confidence to an exhaustion fade setup when a violent liquidation cascade flushes out trapped leverage into a major structural HTF level.
- Rule in one line: Never trade raw open interest changes as a directional entry trigger; use them as a leverage crowding veto, cascade risk gauge, and volatility expansion warning. Today it is CONTEXT ONLY.

## 8. Open tests
| Test | Status |
|---|---|
| Study `edge-oi-flush-1113`: Systematic backtest of post-flush reclaim (entering after a 5m bar with $\Delta p \le -0.25\%$ and $\Delta OI \le -0.2\%$ once delta turns positive) | side-note filed; formal repo study pending |
| Study `edge-crowding-reversal-1113`: Backtest fading extreme OI expansion at range highs with hot funding ($>0.03\%$ per 8h) | side-note filed; formal repo study pending |
| Multi-symbol validation of C24 flush persistence rule on ETH and SOL | not filed |
| Formalization of Krown rule KR-LQC02 (leverage sizing throttle when rolling 30d OI z-score > 2.0) | not filed |
