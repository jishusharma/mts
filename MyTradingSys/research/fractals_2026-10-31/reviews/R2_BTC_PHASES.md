# R2 BTC phases: nested taxonomy, what MTS has, what to test (review only, 2026-10-31)

Review by Lab_Guy. No build, no backtest, no VALIDATION/HOLDOUT read. Labels: SOURCED = trader or public source (link/quote), OURS = our judgement.
All "n" counts are my estimates from known BTC history on daily data 2017-08 onward (not computed by code); they are OURS and rough.
Web claims come from search summaries of secondary pages (blogs, news); verify with the primary source before any pre-registration.

## 0. Plain answer

- Phases nest: 4-year cycle > bull/bear leg > swing (weeks) > intraday (hours). Only the two top levels have a public, named taxonomy. Swing and intraday phases are mostly OURS.
- Almost all macro phases are countable only 2 to 5 times since 2017-08. That is too few for a fee-net edge test. CYCLE_DESIGN.md says "at most five disjoint blocks" (`layer_lab/candle_close_2026-10-14/CYCLE_DESIGN.md`, section "Independent units and power").
- MTS today has only small, mostly OURS phase objects (weekly SMA10 phase, 30-day return, efficiency, RSI 40/60 regime, BBWP). It has NO halving-cycle clock, no 200-week MA, no realized price, and the Cowen band exists only as a sim-desk study.

## 1. Nested taxonomy

PIT = can be computed point-in-time without hindsight. n = instances on daily data 2017-08 to 2026-10 (OURS estimate).

| Level | Phase | Definition | Source | Data needed | PIT? | n since 2017-08 |
|---|---|---|---|---|---|---|
| Macro (4y) | Halving-anchored cycle: halving > peak > bear > bottom | Halvings 2012-11-28, 2016-07-09, 2020-05-11, 2024-04-19. Peak ~12-18 months after halving (reported 525 / 546 / ~511-534 days for 2016 / 2020 / 2024). Peak-to-bottom -86.8% / -83.8% / -77.5% (2012/2016/2020 cycles). Bottom ~410 days after peak in the 2012 cycle. SOURCED: [bit.com](https://www.bit.com/insights/knowledge-hub/bitcoin-cycle), [beincrypto](https://beincrypto.com/bitcoin-four-year-halving-cycle-analysis), [lambdafin](https://www.lambdafin.com/articles/bitcoin-returns-by-halving-cycle) | Halving date (fixed) | YES for "days since halving" (calendar). NO for "peak"/"bottom" labels (hindsight) | Halvings: 2 (2020, 2024). Peaks: 3 (2017-12, 2021-11, 2025-10). Bottoms: 2 (2018-12, 2022-11) |
| Macro (4y) | Low-to-low timing band (Loukas) | ~48 months low to low; lows fall within +-10% (months ~43-51); a cycle low "comes with a timing band", not always the price low. SOURCED: Loukas ctJSV8aTDSk 00:16:57; VWsFf5rQoqE 00:20:32 (`yt_feed_2026-10-31/LOUKAS_CYCLE_2026-10-31.md` I-05, I-09) | Past cycle-low dates | Window YES (calendar from last low). Low itself NO | 2 completed windows |
| Macro (4y) | Left vs right translation | Early peak (15-18 months) then bigger bear = left translated. SOURCED: Loukas DU0nwsY-8WY 00:22:35 (I-07). "Right translation" phrase NOT_IN_DATA (I-08) | Peak timing | NO until the peak is old | 3 |
| Macro (4y) | Midterm-year pattern | Midterm years: Q1 low, summer low, Q4 low; final low comes after the midterms. SOURCED: Cowen bekghgecip8; 21mBnslOLd0 00:16:45 ("always occurred after the midterms") (`cowen_q4_2026-10-31/COWEN_Q4_CONCEPT_CHECK.md` row 6); [summary](https://theinformerpost.beehiiv.com/p/bitcoin-btc-will-see-one-more-low-before-next-bull-market-warns-benjamin-cowen-heres-his-timeline) | Election calendar | YES (calendar) | 2 (2018, 2022); concept check says 3 incl. 2014 |
| Macro (4y) | Log-regression band position | Fit to "non-bubble" data; each bear tends to bottom one band lower than the last. SOURCED (his words via [Into The Cryptoverse summaries](https://rosetta.to/u/intothecryptoverse/bitcoin-logarithmic-regression)). Fit window and exact bands paywalled: NOT_IN_DATA | Full price history | NO as published (fit uses future data). YES only if refit expanding-window (OURS) | Continuous; ~3 bear lows |
| Macro (4y) | Risk metric 0-1 | One score from price, on-chain, social data; low = DCA in, high = DCA out. SOURCED ([summary](https://rosetta.to/u/intothecryptoverse/bitcoin-risk-metric-2024-07-23)). Formula paywalled: NOT_IN_DATA | On-chain + social | Unknown | Continuous |
| Macro (4y) | Wyckoff 4-phase market cycle | Accumulation > markup > distribution > markdown. SOURCED [StockCharts](https://articles.stockcharts.com/article/articles-wyckoff-2015-11-wyckoff-walk-around-the-clock/); sub-phases are discretionary | OHLCV | NO as drawn by eye. A rule version (OURS) would be PIT | ~2.5 loops |
| Macro | Valuation zones: MVRV-Z, NUPL, realized price | MVRV-Z > ~7 near tops, < 0 near bottoms; NUPL = 1 - 1/MVRV; realized price = average cost basis. Thresholds are from secondary sites: [Glassnode](https://docs.glassnode.com/further-information/metric-guides/mvrv/mvrv-z-score), [Adler](https://axeladlerjr.com/mvrv-z-score-how-to-identify-bitcoin-market-tops-and-bottoms/). Jala uses NUPL colour change (section 5) | On-chain realized cap (NOT on disk) | YES only if realized cap is vintage-correct and the z-score uses an expanding std | 3 tops, 2 bottoms |
| Macro | 200-week MA zone | Price near/under 200w SMA = deep bear; price-only proxy for realized value ([page](https://satoshimacro-git.pages.dev/tools/crypto/cycle-indicators/bitcoin-market-value-z-score/)) | Weekly closes (200 weeks; first value ~2021-06 from spot 2017-08) | YES (completed weeks) | ~1 touch (2022) after first value |
| Macro | Pi Cycle top | 111-day SMA crosses 2x the 350-day SMA = top signal. [Summary](https://ar.tradingview.com/chart/BTCUSD/ro3pN50h-BTC-2025-Bull-Market-Continuation) | Daily close | YES | 2 clean hits (2017-12, 2021-04) |
| Intermediate | Bull / bear leg by weekly MA | Cowen bull market support band = 20-week SMA + 21-week EMA; above = bull, bounce off it = dip buy, lost = bear; the band flips into bear market resistance. SOURCED: bWdXPK3Hlok 00:06:02 (band 72-76k); KZ1Jro92t48 (`COWEN_LEVELS_2026-10-31.md`); [Rosetta](https://rosetta.to/u/intothecryptoverse/bitcoin-bull-market-support-band-2024-03-27) | Daily/weekly close | YES (completed weeks only; `cowen_bmsb.py:35`) | ~7 legs; ~25 bounce/loss events (concept check s2, estimate) |
| Intermediate | Price vs long daily MA | Close vs 200-day SMA, or 400-day (Jala "iron dome" 200/400 SMA cross; 400D support/loss). SOURCED Jala -0UiEM32DX4, 4wlnRxGsSdE (`jala_layer_2026-10-31/method_jala.md` s1) | Daily | YES | ~8 crossings of 200D |
| Intermediate | Drawdown depth from ATH | Bear = more than X% below running ATH (X OURS) | Daily | YES (running max) | 3 bear legs at X = -50% |
| Intermediate | BTC dominance phase | Rising dominance = bitcoin season; strict alt season only when dominance falls hard after a parabolic BTC rally. SOURCED [Business Standard](https://www.business-standard.com/content/specials/2025-altseason-delayed-says-top-analyst-125090700171_1.html), [Benzinga](https://www.benzinga.com/crypto/cryptocurrency/25/07/46217148/heres-why-altcoin-season-for-xrp-eth-sol-has-not-happened-yet); Jala mZSSzC6C_Qg | BTC.D series (NOT on disk) | YES if vintage-correct | ~3 |
| Intermediate | Rates / business cycle | Rate-hike lag ~1.5 months then drop; equities rolling over in Q4 of a midterm year. SOURCED Cowen bekghgecip8 W5/W9 (concept check rows 7, 10) | Macro series (NOT on disk) | YES | 2 hike cycles; not testable |
| Intermediate | "Lengthening cycles" | No source found in repo or search: NOT_IN_DATA. (Loukas instead says lows come 10-15% early or late, I-06) | - | - | - |
| Swing | Loukas weekly cycle | ~26 weeks low to low; up 10-18 weeks to a peak. SOURCED wzve_n4gBY4 00:02:48 / 00:03:13 (I-02, I-03). Daily 60-day cycle NOT_IN_DATA (I-04) | Weekly | Window YES; low NO | ~18 |
| Swing | Wyckoff-style range vs trend (daily) | Bounded range vs trending; OURS rules R and F0b frozen in `PHASE_ENCOUNTER_PRE_REG.md` s2 | Daily | YES | hundreds of 14-day windows, few independent |
| Swing | Weekly SMA10 + slope (phase A) | Weekly close vs SMA10(W), slope vs 2 weeks earlier. OURS (`context_factors_2026-10-16/context_asof.py:58`) | Weekly | YES | ~450 weeks, ~30 regime changes |
| Swing | 30-day momentum / efficiency | r30 > +10% bull, < -10% bear; ER30 >= 0.30 trending. OURS (PRE_REG s2 F0a/F0b) | Daily | YES | many, autocorrelated |
| Swing | Volatility regime | q = mean TR(6x4h) / mean TR(120x4h), past-only 90-day terciles. OURS (PRE_REG s2 V, line 21). Krown BBWP regime also exists (`krown_core.py:108,130`) | 4h | YES (past-only rank) | many |
| Swing | Cowen 50-day fake-out | Daily close below the 50-day after a breakout = fake-out, at least to the band. SOURCED bWdXPK3Hlok 00:05:47 | Daily | YES | ~10 |
| Intraday | Balance vs trend day | Tom's balance/imbalance (`trend_healthy` flag, card `lab-verify-trend-healthy-in-balance`, LAYERS.md "Tom") | 1m-5m | YES from closed bars | ~3,300 days |
| Intraday | Session phase | Asia / Europe / US, weekend. OURS (context_asof F7) | Clock | YES | ~3,300 days |
| Intraday | Timeframe alignment | `htf_align` / feature A (PRE_REG s2 A). OURS | 1h/4h/1d | YES | many |

## 2. What MTS already has vs missing

| Phase object | In MTS? | Where | Verdict |
|---|---|---|---|
| Weekly SMA10 phase A / 30-day return phase B | Yes, research only | `research/context_factors_2026-10-16/context_asof.py:58` (constants), `:159` (`_phase_a`); twin in `context_factors_pit_2026-10-16/` | OURS. Two engines agree on only 39% (pit REPORT) / 45.8% (Opus REPORT finding 3). DEV 2022-2024 only |
| momentum30 / efficiency30 / range R / vol V / alignment A | Designed, build blocked | `layer_lab/candle_close_2026-10-14/PHASE_ENCOUNTER_PRE_REG.md` s2 (line 21 = V) | Frozen design, not run |
| RSI 40/60 regime, daily gated by weekly + monthly | Yes, code | `backtest/layers/rsi/malkan_40_60.py:24`, `malkan_mtf.py:53,79` | Phase gate built; no edge alone (LAYERS.md rsi) |
| Volatility regime (BBWP) | Yes, code | `backtest/layers/krown/krown_core.py:108,130`, `krown_context.py:243` | Exists; Krown not validated |
| Cowen band (20w SMA / 21w EMA) | Sim-desk study only | `research/sim_desk/studies/cowen_bmsb.py:35` | 12 settings, 3-10 trades each: NOT ENOUGH DATA; window ends 2024-06-30 |
| Halving / cycle clock | MISSING | No code; only docs. CYCLE_DESIGN.md: macro claims "INCONCLUSIVE/UNDERPOWERED by design" | - |
| 200-week MA, Pi cycle, Mayer, realized price, MVRV/NUPL | MISSING | `research/_archive/loose_2026-10/BTC_MA_SETUPS_RESEARCH_2026-10-03.md:58,109`; `btc_ma_2026-10-03/Q_ALL_ma_findings.md:151` ("out of scope until data exists") | Needs spot 1d/1w from 2017-08 and on-chain data |
| BTC dominance, rate cycle | MISSING | Not in `backtest/` or layers | No data on disk |
| Wyckoff phase | MISSING as code | Only OURS range test R in PRE_REG | - |
| Daily data on disk | Partial | `research/pitchfork_2026-10-19/btc_1d_2020_2026.csv` ends 2026-09-26; DEV 1m archive 2022-01..2024-06; daily 2017-08.. lives on F:/MTS/data/krown_daily (`research/TRIAL_LEDGER.csv:20`), not in tree | Gap |
| Phase used as a filter | Done once | `context_factors_2026-10-16/REPORT.md` s6: whole composite -0.137 R per trade; finding 3: phase confounded with year (1,440 weekly-markdown events in 2022, 50 in 2024H1) | No evidence phase raises edge |

## 3. Layers that may gain from phase context, and the test

Most layers in LAYERS.md are closed as "no edge" (tom_core, fabio, rsi divergence, cryptocred, funding_cvd_fade, session_*). The honest design is a split of existing frozen results, not a new filter search. Freeze the layer's event list first; attach phase labels as-of event time; retune nothing.

| Layer family | Phase context | Why | Test |
|---|---|---|---|
| rsi (Malkan 40/60, divergence) | Bull/bear leg (BMSB side, weekly/monthly RSI regime) | Malkan 5-star already gates on M+W regime (`malkan_mtf.py`, SOURCED); divergence "no edge on any TF" may hide opposite signs in bull vs bear (OURS) | Split RSI-DIV-MTF events by BMSB side and 200D side; fee-net mean R per bucket |
| krown | Volatility regime + leg | Krown D2 already conditions on BBWP (`krown_context.py:243`) | Same split; BBWP high vs low |
| tom / fabio | Intraday balance vs trend, vol regime, session | Balance/imbalance is core to Tom (SOURCED in Tom docs) | Split frozen ledgers by `trend_healthy`, session, V tercile |
| cryptocred | Swing trend vs range (R, F0b) | Pullbacks need trend (OURS) | Split by efficiency30 and D (up/down/mixed) |
| pitchfork / wavetrend / pizzino | Swing phase (weekly SMA10 slope), alignment A | Nested swing states are Pizzino's point (SOURCED) | Split by A: aligned vs conflict |
| positioning (funding, OI) | Macro leg, dominance | Funding extremes read differently in bull vs bear (OURS) | Split by BMSB side |
| session_timing | Weekend/session x vol regime | OURS | Split by V |
| ma_daily / bigtrade | 200D / 200W zone | MA setups depend on side of long MA (OURS); numbers NO-SOURCE | Split by 200D side |
| live_engine | Macro clock (days since halving, midterm flag) | Labels on Eagle_Eyes and dashboards only (concept check: "context flag only, never a trigger") | Display only |

Test template for every row:
1. Pre-register label and cut-points before outcomes.
2. One number per bucket: fee-net mean R with episode-bootstrap 95% range, plus same-window placebo (matched levels/times).
3. Minimum n per bucket: 30 trades (desk floor, concept check s2) AND about 390 distinct UTC days for a decisive cell (day units with Holm; 393 per `context_factors_2026-10-16/REPORT.md` s6).
4. Per-year sign check: a bucket living in one year (2022 markdown) cannot pass.
5. Labels built as-of, with a truncation test as in `context_asof`.
6. Holm count includes this trial family.
7. Macro labels (halving, midterm, 4y) are descriptive only; n is 2-3 cycles.
8. DEV 2022-01..2024-06 only until DEV is extended to 2017/2019 (decision D3 asked for 2019-09..2021-12).
Rule: "phase helps" only if a pre-registered bucket difference beats placebo in at least 2 of 3 calendar years.

## 4. Where we are now (2026-10-31)

Price about 77,000 (Cowen, bekghgecip8 00:01:07, published 2026-10-30). Disk data ends 2026-09-26 (close 84,403), so values computed by me from `pitchfork_2026-10-19/btc_1d_2020_2026.csv` (completed weeks only) are 5 weeks stale.

| Framework | Reading | Date / source |
|---|---|---|
| Halving clock | Halving 2024-04-19; 2026-10-31 is day ~925 (~30 months). Peak daily close 124,628 on 2025-10-06, ~535 days after halving, in line with 525-546 for earlier cycles. News puts the ATH near 126k in Oct 2025 ([cryptoslate](https://cryptoslate.com/?p=491265), [fxstreet](https://www.fxstreet.com/cryptocurrencies/news/is-bitcoins-four-year-cycle-dead-202604300600)) | disk + web |
| Loukas low window | 4-year period "scheduled to end around the October or November time frame" (ctJSV8aTDSk 00:24:58); months 43-51 after Nov 2022 = Jun 2026 to Feb 2027 | LOUKAS_CYCLE I-01, I-05; window arithmetic OURS |
| Cowen cycle call | Final drop after the midterms (3 Nov 2026), then the four-year low; BMSB bounce first is one scenario; day 389 from the peak (concept check row 11) | bekghgecip8 |
| Cowen levels | 83k fake-out confirmed (21mBnslOLd0 00:05:20); BMSB 72-76k (bWdXPK3Hlok 00:06:02); 77k = just above band top | 2026-10-30 |
| BMSB (disk, week to 2026-09-20) | 20w SMA 70,223; 21w EMA 72,585; weekly close 81,144 (above band then) | disk |
| 200-week SMA | 65,478 | disk, 2026-09-20 |
| 50d / 200d / 400d SMA | 75,706 / 71,004 / 82,971 (close 84,403 on 2026-09-26). Jala: lost the 400D (lJ8rI4iiXG4, 2026-10-08); "under 79K" and testing iron dome floor (dmC1U_r8PFc, 2026-10-30) | disk + method_jala.md s7 |
| Pi cycle | 111d SMA 68,949 vs 2x350d SMA 157,001: no top signal | disk, 2026-09-26 |
| Drawdown from ATH | -32.3% at 84.4k (disk). At 77k about -38% (OURS arithmetic from 124.6k). Earlier bears -77% to -87%. Search reports a fall to 60-70k in Feb 2026 and ~76k in late May 2026 ([fxstreet](https://www.fxstreet.com/cryptocurrencies/news/is-bitcoins-four-year-cycle-dead-202604300600)); not checked against disk | web, unverified |
| Weekly SMA10 phase (OURS) | Close 81,144 vs SMA10 71,497: above | disk, 2026-09-20 |
| 30-day return | +5.2% (neutral) | disk, 2026-09-26 |
| MVRV-Z, NUPL, realized price | NOT_IN_DATA | no on-chain data |
| BTC dominance, rates | NOT_IN_DATA | no data on disk |
| Wyckoff phase | Discretionary; Cowen and Jala both call bear/markdown. OURS rule version not run | - |
| Volatility regime | NOT_IN_DATA at 2026-10-31 | 4h DEV ends 2024-06 |
| Post-ETF debate | Split: [Galaxy: cycle valid, halving rule losing impact](https://www.kucoin.com/news/flash/galaxy-research-bitcoin-s-four-year-cycle-remains-valid-halving-rule-losing-impact); [Cointelegraph](https://cointelegraph.com/news/did-bitcoin-4-year-cycle-break-is-bull-market-really-over); [Rekt: "probably just leveling up"](https://decrypt.co/336505?amp=1); most agree returns shrink each cycle | web |

Reading: by calendar and price frameworks the market sits in a late-bear leg of the 2024 cycle, with timing-band lows due Nov 2026 to early 2027. The disk values show "above the band" five weeks ago; the 10-30 videos put price back at the band.

## 5. Does Jala use the 4-year cycle?

Yes, as a fractal (replay of a past-cycle shape), not as a halving clock. Quotes from `jala_layer_2026-10-31/method_jala.md`:
- "We know every four years we get this three. Now, the three is the next low that comes in off the lowest low in the bottom pocket." (p9KajODtBsU)
- "If we close beneath the 400... a failed cup and handle. And what does that mean? Well, if that happens, then now we look at the fractal." (-0UiEM32DX4)
- "We did the fractal and I said expect some kind of like head and shoulder kind of setup" (xc4TyMS3HKc)
- NUPL colour change marks the "three" confirmation (p9KajODtBsU; xIUHpTirh_g).
Caveat: 18 of 30 videos were UNVERIFIED (HTTP 429); the word "halving" is absent from the quotes.

## 6. Ten-line summary

1. Taxonomy: 4 levels, 28 rows; only macro and the weekly-MA leg have named public sources; swing/intraday are mostly OURS.
2. Halving dates and drawdowns (-87/-84/-78%) are sourced; the 2024 cycle peaked 2025-10-06, ~535 days after halving, consistent with history.
3. Macro phase n is 2-3 per label since 2017-08; a fee-net edge test per macro phase is not possible (CYCLE_DESIGN.md).
4. MTS has only OURS phase objects (weekly SMA10, 30d return, RSI regime, BBWP); no halving clock, 200W, Pi, MVRV or dominance in code.
5. Cowen band exists as a sim-desk study; 12 settings all NOT ENOUGH DATA; window ends 2024-06.
6. Earlier phase-as-filter work gave no edge (composite -0.137 R) and phase is confounded with the year.
7. Best use now: split existing frozen layer results (rsi, krown, tom, cryptocred, pitchfork) by phase with per-year sign and 30-trade / ~390-day floors; macro labels display-only.
8. Now: ~77k, ~day 925 after halving, ~-38% from the Oct 2025 high, at the 72-76k band per Cowen, Loukas low window Nov 2026 to early 2027; on-chain, dominance, 4h vol NOT_IN_DATA.
9. Jala uses a 4-year fractal ("every four years we get this three", p9KajODtBsU), not a halving clock.
10. Biggest gap: no daily 2017-2021 data in the tree and no on-chain/dominance feed; extend DEV before any phase test.

Noticed: (a) Cowen "lengthening cycles" has no source in repo or search; (b) web 2026 price points are from secondary news and not checked against disk; (c) the two context engines disagree on phase (39% vs 45.8% agreement).
Question: draft a pre-registration that splits frozen RSI-DIV-MTF and Krown event lists by BMSB side and 200D side (DEV 2022-2024 only)? Default: yes, as a SONNET card, after daily 2017-2021 data is fetched.
