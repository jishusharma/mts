# BTC moving-average setups: evidence review (2026-10-03)

Session: MTS-2026-10-03-2053Z-APP-ANA-btc-moving-averages (APP desktop, Code tab; Opus 5.5 + 3 Sonnet web workers).
Method: methodology/playbook.md Part I v3.0. Sections 1-2 were written and frozen BEFORE any search ran.

Operator (verbatim, 2026-10-03): "What trading setups are there for BTC using the moving averages. Maybe secret
moving averages that are back-tested and works under certain market condition like trending/ranging. There could
be other diverse factors and we have to research what they could be!"

Scope guard: everything here is a candidate SEPARATE LAYER (PROJECT_VISION: Tom is core; other systems are layers,
never Tom filters). No MA parameter enters MTS from this note; adoption needs our own OOS backtest (Part I 3e), and
any trader-sourced parameter needs that trader's own words (CLAUDE.md Provenance).

## 1. Method notes (Step 1, frozen before search)

| Q | Question | Evidence that would settle it |
|---|---|---|
| Q1 | Which standard MA setups (price-vs-MA filter, dual crossover incl. 50/200, variable-length MA "VMA", MA-ratio/MA-gap predictors, MA bands/envelopes) have evidence on BTC? | Out-of-sample (rolling/recursive or held-out) returns of the rule vs buy-and-hold on BTC, daily or intraday bars, net of fees (+ funding if perp), with a data-snooping control (White Reality Check, Hansen SPA, Romano-Wolf, or PBO/DSR) when many rules are tried; sample >= 5 years daily (>= 2 bull/bear cycles) and subperiod results (before/after Dec-2017 CME futures; after Jan-2024 spot ETFs). |
| Q2 | Do non-standard ("secret") MAs beat plain SMA/EMA on BTC, and under which conditions? (a) adaptive/low-lag: KAMA, FRAMA, VIDYA, Hull, ALMA, McGinley, JMA, Ehlers MAMA/FAMA, T3, zero-lag EMA; (b) volume-weighted: VWMA, anchored VWAP; (c) BTC-cycle MAs: 200-week SMA, Mayer Multiple (price/200DMA), Pi Cycle Top (111DMA vs 2x350DMA), 2-Year MA multiplier, bull-market support band (20W SMA/21W EMA); (d) on-chain cost-basis "averages": realized price, MVRV, STH realized price. | Same test as Q1, PLUS a head-to-head against SMA/EMA of matched lag on the same data (otherwise "better MA" is untested). For cycle-top/bottom signals: count independent signal events; n < 10 (BTC has had ~4 cycles) cannot be validated statistically and is labelled "anecdote, n=k". |
| Q3 | Does MA/trend-rule performance on BTC differ between trending and ranging regimes (and bull/bear, high/low vol), and does an ex-ante regime filter improve it? | Rule returns split by an EX-ANTE regime label (computed from data available at the bar; no look-ahead), difference tested (bootstrap or t-test), and the regime-filtered rule tested OOS net of costs. Detectors in scope: ADX, Kaufman efficiency ratio, Hurst exponent / variance ratio, MA slope, Markov/HMM regime switching, realized-vol regimes. |
| Q4 | Which other factors distinguish when MA/trend signals work on BTC? Candidates: volatility level and vol-targeting, volume/liquidity, investor attention, funding rate / basis / OI, time-of-day / day-of-week / session, halving cycle, market-efficiency drift over time (futures 2017, ETF 2024), macro/risk-on correlation, weekend effect. | Interaction test: trend/MA-rule returns conditional on the factor (terciles or threshold) or predictive regression with interaction terms, OOS, net of costs; or a T1 study showing the factor predicts BTC returns AND an explicit link to trend-rule profitability. A factor that only predicts returns on its own is recorded as a separate-layer candidate, not as an MA conditioner. |

No question is an "unvalidated domain": accepted methods exist (Brock-Lakonishok-LeBaron 1992 style rule tests with
Sullivan-Timmermann-White 1999 data-snooping control; PBO per Bailey et al.). Q2(c) cycle signals are the exception
in practice (n too small); that is stated per finding rather than stopping the whole question.

## 2. Source-tier plan (Step 2, fixed; never adjusted after results)

Tier table = playbook Part I Step 2 verbatim (T1 peer-reviewed / NBER / Fed / BIS / central bank / regulated research
with disclosed method; T2 SSRN/arXiv with disclosed data + method, exchange-published data/docs, replicated
practitioner studies with full method; T3 practitioner content, vendor docs, community backtests with full params;
REJECT marketing / no author-date-method / win-rate without costs / unopenable citation). Expected sources per Q:

| Q | Expected T1 | Expected T2 | Expected T3 | Pre-committed REJECT patterns |
|---|---|---|---|---|
| Q1 | Finance Research Letters, Financial Management, Annals of Operations Research, Journal of Forecasting, Economics Letters, JFQA/RFS/JF, Physica A, North Am. J. Econ. & Finance, J. Int. Fin. Markets Inst. & Money | SSRN/arXiv BTC trend papers with code/data; QuantPedia pages only as pointers to the original | TradingView strategy reports WITH full parameters + cost settings | "MA crossover wins 80%" videos/blogs; backtests without fees; affiliate exchange blogs |
| Q2 | Any peer-reviewed comparison of adaptive vs simple MAs (any asset; BTC-specific preferred) | SSRN/arXiv; Coin Metrics / exchange research with disclosed method | Kaufman (Trading Systems and Methods), Ehlers (S&C articles/books), Jurik, McGinley, LookIntoBitcoin/Swift, Mayer, Cowen, Glassnode docs (vendor) | Indicator-sales pages; "secret MA" content with no params/costs; cycle charts presented as backtests |
| Q3 | Zakamulin (Quantitative Finance, J. Asset Mgmt), BTC regime-switching papers (FRL etc.), BTC efficiency/Hurst papers (Economics Letters, Physica A) | SSRN/arXiv regime-conditioned crypto trend | Practitioner regime filters (ADX>25, ER) with full params | Regime claims judged on the same data the regime was fitted to (look-ahead) |
| Q4 | Liu & Tsyvinski (RFS), Han-Yang-Zhou (JFQA), Detzel et al. (Financial Management), day-of-week/intraday crypto papers (FRL, Economics Letters), futures-introduction efficiency papers | He-Manela-Ross-von Wachter (arXiv 2212.06888) perpetual funding; Binance/Deribit published data docs | Desk research notes with disclosed method | Macro "narrative" pieces with no test |

Ranking rule: our own OOS backtest > T1 > T2 > T3 (Part I 3e). Findings carry `Tier | Method quality | Confidence`.

## 3. Findings

Consolidated pass 2026-10-07 (one Sonnet worker, Q1 + Q2 definitions): btc_ma_2026-10-03/Q_ALL_ma_findings.md section 3.
Supervisor spot-check: Wei et al. 2024 (DOI 10.1002/ijfe.2863) PDF opened, title/DOI match.
OPEN: Q2 adaptive-MA head-to-head (KAMA/Hull/ALMA...) and Q3/Q4 regime/factor papers not reached (briefs sonnet-02/03 remain).

## 4. Backtest feasibility vs current MTS and Fabio functions (file map)

### 4a. Data on disk (checked 2026-10-03 by this session; `check_gaps` run, not inferred)
| Data | Path | Coverage | Note |
|---|---|---|---|
| Perp 1d klines | Dumps/backtest/raw_1d/klines | 2020-01 .. 2025-08 | + 1m below resampled -> 2,461 daily bars 2020-01-01..2026-09-26, 0 gaps |
| Perp 1m klines | Dumps/backtest/raw_1m_2022/klines + raw/klines | 2022-01 .. 2026-09-26 | 2,491,200 bars, 0 gaps |
| Funding 8h | Dumps/backtest/raw/fundingRate | 2025-09 .. 2026-08 ONLY | archive has BTCUSDT from 2020-01 (fetched 2020-01 file: 93 records). See B103 |
| OI / LS metrics 5m | Dumps/backtest/raw/metrics | 2025-09 .. 2026-09 | archive has files at least from 2020-09-01 (HTTP 200) |
| Spot 1d/1w | none | - | archive spot BTCUSDT starts 2017-08 (2017-07 = 404); fetcher is futures/um only |
| Pre-2017 BTC | none | - | not in Binance archive; 200W MA / Pi Cycle over more than one cycle need it |

### 4b. Event counts per setup on that data (feasibility only, NOT performance)
Script: session scratchpad `ma_event_counts.py` (uses bt_data.load_klines, tf_resample.resample, rsi_ma). Gate
reference: run_t055.py PASS needs n_oos >= 30 events in the last 30%.
| Setup | Events 2020-01..2026-09 | OOS (last 30%) | Event-gate verdict |
|---|---|---|---|
| 1d close x SMA20 / SMA50 | 288 / 132 | 80 / 48 | testable |
| 1d close x SMA100 / SMA200 | 89 / 52 | 24 / 18 | below 30 -> needs position-series test (4d) |
| 1d SMA50 x SMA200 (golden/death cross) | 12 | 4 | not testable as events |
| 1d EMA9 x EMA21 | 92 | 34 | marginal |
| 1d Pi Cycle (SMA111 x 2xSMA350) | 2 (2021-04-12, 2021-04-23) | 0 | anecdote, n=1 cycle |
| 1d Mayer Multiple > 2.4 / < 0.8 | 24 days / 354 days of 2,262 | - | clustered; 1-2 episodes |
| 1w close x SMA20W / x EMA21W | 28 / 26 | 8 / 8 | not testable as events |
| 1w SMA200W | 152 valid weeks only | - | warm-up eats 4 years of a 6.7-year series |
| 4h EMA9 x EMA21 / 4h close x SMA200 | 454 / 287 | 145 / 84 | testable |
| 1h EMA9 x EMA21 / 1h close x SMA200 | 1,864 / 1,429 | 562 / 432 | testable (fee floor decides) |

### 4c. What exists and can be reused (file map)
| Need | Existing function | Status for MA work |
|---|---|---|
| Load bars / funding / OI | MyTradingSys/backtest/bt/bt_data.py `load_klines`, `load_funding`, `load_metrics`, `check_gaps` | reuse; `load_klines` reads ms timestamps only (spot files from 2025 use microseconds -> normalise first) |
| Fetch history | MyTradingSys/backtest/fetch_binance_archive.py `--interval 1d`, datasets fundingRate/metrics | reuse for perp; spot needs a `--market spot` option |
| Resample 1m -> 4h/1d/1w | MyTradingSys/backtest/layers/timeframe/tf_resample.py `resample` + registry.json (1w = Monday 00:00 UTC) | reuse; drops taker-buy volume (fabio/run_backtest.py sums it itself) |
| SMA / EMA / WMA / RMA | MyTradingSys/backtest/layers/rsi/rsi_ma.py `rsi_ma(series, type, length)` - pure, any series | reuse by import (FORMULAS.md sections 2-5 already canonical) |
| Fixed-horizon event study | MyTradingSys/backtest/layers/runner.py `forward_return_stats` | reuse for crosses; close-only MAE |
| Bracket trade sim (stop/targets, mark, funding) | MyTradingSys/backtest/bt/bt_engine.py `simulate_trade` | reuse for MA-pullback entries with stops |
| Costs | MyTradingSys/backtest/layers/positioning/trade_costs.py `net_return`, `funding_paid` (FORMULAS 13) | reuse AFTER B103 (silent zero funding outside loaded range) |
| Stats | MyTradingSys/backtest/bt/bt_stats.py `sharpe`, `psr`, `dsr`, `bootstrap_mean_ci`, `pbo_cscv`; bt/ref_pbo.py | reuse |
| IS/OOS grid + PASS gate | MyTradingSys/backtest/layers/run_t055.py (70/30, IS-only grid, PBO < 0.5, n_oos >= 30, Sharpe >= 0.3, >= 2 OOS years) | template |
| Ex-ante range ("balance") label | MyTradingSys/backtest/layers/fabio/v3/signals.py `balance(bars,i,N,k_bal)`: R <= k_bal*sqrt(N)*ATR_N and close within 0.25R of POC | reuse as a Fabio-sourced RANGING label; needs the one-bin footprint adapter from fabio/htf_context_live.py for kline bars |
| Fabio HTF balance series | MyTradingSys/backtest/layers/fabio/htf_context_live.py (4H/1D balance JSONL, live since R4) | live collection only; backfill needs a loop over history |
| Day type | MyTradingSys/backtest/layers/fabio/v3/day_gates.py `day_type` | EX-POST, reporting only - must NOT be used as a filter (look-ahead) |
| Sessions (NY/London/Asia, DST) | fabio/v3/day_gates.py `ny_open_utc` etc.; layers/session/session_momentum.py | reuse for time-of-day factor |
| CVD / order-flow per bar | layers/fabio/orderflow_bars.py; bt_data `cvd_delta` | reuse for "volume confirms cross" factor |
| Funding percentile | layers/positioning/funding_cvd_fade.py | reuse for funding-conditioned MA |
| Live trend/range vote | MyTradingSys/runtime/regime_classifier.py (vwap_slope, cvd_slope, net_delta_1h, vp_shape) | live snapshots only; no history (B075) -> not backtestable now |
| Session VWAP + bands + slope | src/main/java/datafeed/MarketDataSnapshot.java `buildVwap` (NY-open anchor) | Java live only; anchored VWAP needs a Python port for backtests |

### 4d. Missing pieces (build list, smallest first)
1. T0: fetch fundingRate 2020-01..2026-09 and metrics 2020-09.. (one fetcher command each) + fix B103 (coverage check, fail closed).
2. T2: `layers/ma/position_backtest.py` - position-series evaluator: signal at close t sets position for t->t+1 (no
   look-ahead), fee + slippage on every position change, funding per 8h record while held, daily net return stream ->
   Sharpe/DSR/PBO. Needed because MA filters are position strategies; BLL-1992 and the BTC papers test them that way,
   and long-MA setups have too few events for the event gate (4b).
3. T2: `layers/ma/ma_filters.py` - KAMA/ER, Hull, ALMA, McGinley, VIDYA, FRAMA, T3, DEMA/TEMA, VWMA, anchored VWAP;
   each gets a FORMULAS.md section (canonical definition + source + worked example) BEFORE its spec (Part I 3e); tests
   from FORMULAS, not code.
4. T2: regime label series (efficiency ratio, ADX, rolling variance ratio, realized-vol terciles, Fabio `balance`
   on 4h/1d) computed ex-ante per bar.
5. T1/T2: spot 1d/1w fetch from 2017-08 (with microsecond normalisation) for 200D/200W/Mayer/Pi Cycle; pre-2017 data
   source is an operator decision (no Binance archive).

## 5. Answer and surface

See Q_ALL_ma_findings.md section 5. Short form: only the ~1-week log price/MA ratio (PMA1) has snooping-controlled, OOS,
net-of-cost support on BTC (Wei et al. 2024, T1, sample ends 2022-03). Crossovers incl. 50/200, VMA lengths and adaptive
"secret" MAs: no validated evidence found. No validated ex-ante trending/ranging filter. Pi Cycle, Mayer 2.4/0.8, 200W bottom:
folklore (n <= 4 cycles). Surface: close vs SMA20/50/200 shown in scripts/dev/market_guide.py as OBSERVATION (UNTESTED).
Next backtest (separate layer, position-series, daily, OOS post-2024-09): log price/MA ratio 1/2/4/10/20w, pre-registered PMA1 hypothesis.

## 6. Discarded (REJECT / untestable), one line each

See Q_ALL_ma_findings.md section 6. Untestable as events: 50x200 golden cross (12 events), Pi Cycle (2).
