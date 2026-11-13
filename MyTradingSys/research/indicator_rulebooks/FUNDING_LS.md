# Rule book: Funding rate and long/short ratio (BitMEX 2016 / Binance)

Sources: FORM = `backtest/layers/FORMULAS.md` s13, s14; T055 = `research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md`; FLOW = `research/flow_layers_concepts_2026-10-28/README.md`; KROWN = `research/krown_ta101_2026-10-13/extracts/extract_P3rDSh187TE.md`; LA = `tools/live_aid/`; BM = https://www.bitmex.com/app/perpetualContractsGuide (Arthur Hayes / BitMEX 2016 invention of perpetual swap funding mechanism); BIN_F = https://www.binance.com/en/support/faq/introduction-to-binance-futures-funding-rates-360033525031 (Binance funding rate calculation mechanics, clamp, and intervals); BIN_LS = https://binance-docs.github.io/apidocs/futures/en/#top-trader-long-short-ratio-positions (Binance topLongShortPositionRatio and topLongShortAccountRatio documentation). All repo paths under `MyTradingSys/` unless stated otherwise.

**Result: Funding rate is a periodic tether anchoring perpetual contracts to spot; long/short ratios measure account and position crowding. Creators designed them as balance/settlement mechanisms, not directional signals; our tests show fading funding extremes failed out-of-sample (T055 C1 OOS net -0.0453%, Sharpe -0.0346, FAIL). Use both strictly as FLOW context and liquidation cascade vulnerability gauges, never as standalone entry triggers.**

## 1. What it measures
Measures positioning imbalance, leveraged crowding, and cost of carry in perpetual futures.
- **Funding rate:** The periodic cash payment exchanged between longs and shorts to tether perpetual contract prices to spot index prices. When positive, perp trades at a premium over spot and longs pay shorts; when negative, perp trades at a discount and shorts pay longs.
- **Long/short ratios:** The relative proportion of net-long versus net-short market participants. Binance provides Global Account Ratio (retail proxy, one account = one vote), Top Trader Account Ratio (fraction of top 20% margin-balance accounts net-long vs short), and Top Trader Position Ratio (aggregate contract volume / notional held long vs short by top traders).
Formula pointer: `backtest/layers/FORMULAS.md` section 13 (funding cash flow: `side_sign * rate`, longs pay positive, shorts pay negative) and section 14 (`layers/positioning/funding_cvd_fade.py`, funding percentile reversion). Parity: `NOT VERIFIED-TV` (exchange API feeds, not standard Pine indicators). Code modules: `tools/live_aid/live_aid.html` (funding table & top-trader ratio fetch), `backtest/layers/positioning/funding_cvd_fade.py`, and `research/fast_track_2026-09-27/run_t055.py`.

## 2. Developer's own rules (SOURCED)
| Item | What is stated | Source |
|---|---|---|
| Who & Year (Funding rate) | Arthur Hayes, Ben Delo, and Sam Reed (BitMEX), introduced May 2016 with the XBTUSD perpetual swap contract to solve liquidity fragmentation across expiring futures contracts. | BM, SOURCED |
| Mechanism & Purpose (Funding rate) | BitMEX engineered periodic cash payments between long and short contract holders to tether perpetual contracts to the spot index without contract expiry. When mark price > index price, funding is positive (longs pay shorts); when mark price < index price, funding is negative (shorts pay longs). The exchange collects zero fee from this payment. | BM, SOURCED |
| Exchange Formula (Binance funding) | Funding Rate $F = \text{Average Premium Index } P + \text{clamp}(\text{Interest Rate} - P, -0.05\%, +0.05\%)$ scaled by interval $(8/N)$ hours. Standard baseline interest rate is 0.01% per 8h (0.03% daily) for USDT-margined contracts. Premium Index is sampled every 5 seconds. Rate is clamped to avoid extreme rate distortion. | BIN_F, SOURCED |
| Fee Calculation & Settlement | Funding Fee = $\text{Position Notional Value} \times \text{Funding Rate}$, where Notional = $\text{Mark Price} \times \text{Size}$. Settled discretely at timestamps (standard 8h: 00:00, 08:00, 16:00 UTC; or accelerated 4h/1h). Only traders holding an open position at the exact settlement timestamp pay or receive funding. | BIN_F, SOURCED |
| Developer directional rule | The exchange documentation states NO directional trading rules, NO entry signals, NO stops, and NO win rate. It is explicitly a market tethering and settlement clearing mechanism. | BM, BIN_F, SOURCED |
| Binance Top Trader Ratios | Defined for top 20% users by margin balance. `topLongShortAccountRatio` = proportion of top accounts net-long vs net-short ($long / short$). `topLongShortPositionRatio` = proportion of actual contract volume / notional positions held long vs short. Published across periods from 5m to 1d. | BIN_LS, SOURCED |
| Ratio developer directional rule | The API documentation states NO trading rules. It is an informational data feed reflecting positioning fractions. | BIN_LS, SOURCED |

## 3. What the internet and crypto traders say
| Claim | Source URL | Evidence grade |
|---|---|---|
| Delta-neutral funding rate carry arbitrage (long spot + short high-funding perp) yields stable risk-adjusted returns | He, Manela, Ross, & von Wachter (2022/2026), "Fundamentals of Perpetual Futures": https://ideas.repec.org/p/nbr/nberwo/32936.html | measured (T1, empirical bounds show persistent mean-reverting deviations; high paper Sharpe, friction/liquidation limits net return; SOURCED) |
| Extreme funding rates exhibit statistical mean reversion, but fees and liquidation spikes erode simple contrarian directional edges | Ackerer, Hugonnier, & Jermann (2024), "Perpetual Futures Pricing", NBER WP 32936: https://www.nber.org/papers/w32936 | measured (T1, closed-form pricing model showing funding forces futures to spot expectation; SOURCED) |
| Retail crowding contrarian fade: when Global Account Long/Short ratio spikes heavily long while Top Trader Position ratio leans short, a long squeeze / correction is imminent | Hyblock Capital & CoinGlass sentiment commentary: https://www.coinglass.com/LongShortRatio | anecdote (T3, vendor concept; divergence between retail headcount and whale capital footprint; no costed sample or fixed thresholds; SOURCED) |
| High positive funding rate (>0.03% to 0.05% per 8h) indicates overleveraged longs vulnerable to a rapid cascade downward | Mudrex & CryptoRank market commentary: https://mudrex.com/blog/ | anecdote (T3, trader rule of thumb using 3x standard 0.01% baseline; unverified trade log; SOURCED) |
| Funding rate Granger-causes spot price moves during sentiment extremes | Aalto University quantitative research papers on crypto market microstructures: https://aaltodoc.aalto.fi/ | measured (T2, statistical lead/lag identified during extreme basis widening; sample abstract read; SOURCED) |
| Top-trader account ratio > 2.0 indicates extreme bullish consensus that should be faded | Crypto Twitter / community consensus claims | UNVERIFIED (common claim on social channels; no systematic sample or fee-net proof found) |

## 4. What our analysts say (extracts)
| Analyst | Their rule in plain words | File pointer |
|---|---|---|
| Krown | Funding rate is a "thermometer for how crowded one side of the boat has become." Hot positive funding means longs are aggressive and literally paying shorts to stay leveraged; hot funding + stacked high open interest = "loaded mountain of snow" indicating high cascade vulnerability (avalanche risk), though not the exact trigger timestamp. Sizing rule: "check the weather before you size funding and open interest are free"; never risk liquidation ("do not multiply by zero"). | `research/krown_ta101_2026-10-13/extracts/extract_P3rDSh187TE.md:20,30,40,86` [t=00:10:45, 00:11:39, 00:13:50, 00:28:36] |
| Tom | NO-SOURCE: does not use funding rate or long/short ratios as levels, setups, or triggers. 0 hits for "funding" or "long short" in canonical transcripts. Positioning data is MTS-own. | `research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:43` |
| Fabio | NO-SOURCE: does not use funding rates or long/short account ratios (relies strictly on footprint, tape, and CVD orderflow). | `research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:43` |
| CCU | NO-SOURCE: CCU extracts show no funding rate or long/short ratio usage (uses moving averages, Stoch RSI, WaveTrend). | `research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md` |
| Malkan | NO-SOURCE: requires strictly OHLC price bars for Wilder RSI(14); no aggressor order flow, OI, or funding rate is used. | `research/malkan_extract_2026-10-15/PRE_REG_MALKAN_GFS_BTC.md:32-34` |
| NK (StockTalk) | NO-SOURCE: no extract mentions funding rate or long/short ratios. | none found |
| CryptoCred | NO-SOURCE: no extract mentions funding rate or long/short ratios. | none found |
| Habib / CBP | NO-SOURCE: no extract mentions funding rate or long/short ratios. | none found |

## 5. OUR measurements
All rows OURS, copied from the named file. BTCUSDT.
| Study folder | What was tested | n | Fee-net result | Verdict |
|---|---|---|---|---|
| `research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md` (C1 funding_cvd_fade) | Funding-extreme reversion plus CVD/price divergence fade, 15m bars, 108 variants, fee 10 bp + slip 2 bp + real funding, chronological 70/30 IS/OOS (not the DEV/VALIDATION/HOLDOUT split) | IS 129 events; OOS 76 | IS net +0.4113%; OOS net -0.0453%, net Sharpe -0.0346; PBO 0.1385; criteria oos_mean_net, oos_net_sharpe, same_sign fail | 15m: DO NOT USE (file verdict FAIL, provisional, single OOS year) |
| `research/gross_effect_screen_2026-10-15/FUNDING_RERUN.md` | Gross-effect screen, primary cell d=1 h=60, flat 1 bp funding vs real signed funding, DEV < 2024-07-01, before the 0.14% trading cost | T 40; notF 1399; C 1439 | mean G with real funding: T -0.05610%, notF -0.00548%, C -0.00688% (before cost) | UNDERPOWERED (file: INCONCLUSIVE, n_T 40 < 200 pre-registered minimum; funding impact on the primary cell +0.0013 pp at most) |
| `research/layer_lab/funding_extreme_event_table/REPORT.md` | DEV-only event table: trailing 90-print 95th-percentile funding flag, faded, 24h forward excursions in ATR14 units | 2,736 prints; 726 extreme events (695 short fades, 31 long fades) | none: the report is a table build, no outcome or fee-net result | UNTESTED (file verdict BUILT; no trading rule) |
| `research/flow_layers_concepts_2026-10-28/README.md` | Top-trader long/short ratios beside price around the US open, observation of one session | observed, no sample | no returns computed; ratios moved slowly and opposite to the hours-long price swing (README point 3); lead/lag finer than the source period NOT_IN_DATA (F10) | CONTEXT ONLY (descriptive concept, no outcome) |
Long/short ratio fade (INDEX verdict "ratio fade 0 of 2", side-notes `edge2-ratio-fade-wide-1113_RESULTS.md`): that file is not in the repo, so the numbers are NOT_MEASURED here; re-copy once it is committed. Funding-rate rule fee-net on the DEV / VALIDATION / RECENT split, regime mix: NOT_MEASURED.

## 6. How to read it now on Live Aid
- **Funding and premium panel** (`tools/live_aid/live_aid.html` table `#fund`):
  - Displays venue rows (Deribit, Bybit, Binance status).
  - Columns: `Last`, `Mark - index` (premium), `Funding 8h` (Deribit continuous ticker `funding_8h`, Bybit `fundingRate` per 8h), `A year` (annualized rate = `rate * 3 * 365`), `Reads` (flag: "about zero" under 0.001% per 8h; "high" at >= 0.03% per 8h / 3x baseline), `Open int. USD`, and `Next funding` countdown.
  - Who bullet: summarizes who pays funding (`longs pay funding` or `shorts pay funding`).
- **Big candle story panel** (`tools/live_aid/live_aid.html` `#age-bc`):
  - Fetches Binance `topLongShortPositionRatio` and `topLongShortAccountRatio`.
  - Compares top traders' position ratio versus account ratio over trailing 60 minutes (flat under 0.2%) to gauge whether whale capital agrees with headcount.

## 7. Confluence role: FLOW
Funding rate and long/short ratio serve strictly as a FLOW and positioning context gauge (liquidation cascade vulnerability thermometer).
May add confidence to: a veto against opening leveraged long positions when funding is hot positive (>= 0.03% per 8h) and OI is stacked at range highs; or confidence to an exhaustion fade setup when an extreme liquidation cascade flushes out crowded positioning into a structural level.
Rule in one line: Never trade raw funding or ratio extremes as an entry; use them as a cascade risk veto and position sizing throttle. Today it is CONTEXT ONLY.

## 8. Open tests
- Study `edge2-ratio-fade-wide-1113`: Systematic backtest evaluating whether extreme divergences between retail global accounts ratio and top-trader position ratio yield a fee-net edge on BTC 1h/4h.
- Study `funding_extreme_cascade_veto`: Formalization of Krown rule KR-LQC02 as a systematic sizing and long-veto gate when 8h funding exceeds 0.03% and OI z-score > 2.0.
- Study `perpetual_basis_mean_reversion`: Multi-exchange (Binance vs Bybit vs Deribit) funding-rate spread and basis mean-reversion carry test net of taker/maker fee models.
