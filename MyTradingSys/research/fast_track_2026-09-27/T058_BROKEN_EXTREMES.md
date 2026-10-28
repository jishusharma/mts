# T058 - Broken Lows/Highs: Continuation vs Liquidity Sweep [GATED v3.0]

Item: `MyTradingSys/items/T058_broken_extremes_sweep_vs_continuation.md` (verbatim ask there).
Gate: `methodology/playbook.md` Part I v3.0. Verification date for every citation: 2026-09-29.
Status: RESEARCH + DESIGN ONLY. Nothing here is validated for MTS. Formulas below are CANDIDATES;
none has been written to `backtest/layers/FORMULAS.md`. Any setup found becomes its own layer, never a Tom filter.

## STEP 1 - METHOD NOTES (written before searching)

- **Q1 (continuation vs sweep, by timeframe)**: settled by an event study with a precise swing/break
  definition, a random-level control, multi-year sample, out-of-sample split, and costs (fees + funding).
  Externally, peer-reviewed intraday or order-level studies of stop/limit clustering would rank what to test.
  No accepted academic method labels "liquidity sweep" itself; that label is practitioner vocabulary.
  The per-timeframe claim is therefore an "unvalidated domain" until our own study runs.
- **Q2 (what confirms which case)**: each confirmer (reclaim time, volume, CVD, OI, funding, RSI, liquidations) must be
  tested as a conditioning variable inside the Q1 event study (conditional outcome frequencies, out-of-sample,
  block-bootstrap CIs). Generic predictive-power papers only rank candidates. Practitioner rules are T3.
- **Q3 (definitions/backtest plan)**: settled by internal consistency and testability on data we hold; no external
  authority is needed. Success = every definition is computable from `Dumps/backtest/raw*`, look-ahead-free, and
  reproducible by hand on a small case.
- **Q4 (hedge hook)**: a design proposal; nothing external can settle it. It is acceptable only after Q1/Q2 backtests pass.

## STEP 3a - CITATION CHECK (opened 2026-09-29)

| Source | Claimed for | Result |
|---|---|---|
| Osler 2005, *J. Int. Money & Finance* 24(2):219-241, https://ideas.repec.org/a/eee/jimfin/v24y2005i2p219-241.html | stop-loss cascades at clustered levels | Verified (RePEc page opened; title/author/venue/year match; abstract read). Also NY Fed SR150: https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr150.pdf (seen in search, not separately opened). |
| Osler 2003, *J. Finance* 58(5):1791-1819, doi 10.1111/1540-6261.00588, https://ideas.repec.org/a/bla/jfinan/v58y2003i5p1791-1819.html | take-profit orders cluster at round numbers, stop-loss just beyond | Verified (RePEc page opened; abstract read). |
| Osler 2000, *FRBNY Economic Policy Review* 6(2):53-68, https://econpapers.repec.org/RePEc:fip:fednep:y:2000:i:jul:p:53-68:n:v.6no.2 | published support/resistance levels predict intraday trend interruptions | Verified (EconPapers page opened). |
| Kavajecz & Odders-White 2004, *Rev. Financial Studies* 17(4):1043-1071, https://ideas.repec.org/a/oup/rfinst/v17y2004i4p1043-1071.html | S/R levels coincide with limit-order-book depth peaks | Verified (RePEc page opened; RePEc lists only the first author, the co-author and title were confirmed via search index and SSRN 315660 listing). |
| Brock, Lakonishok & LeBaron 1992, *J. Finance* 47(5):1731-1764, https://ideas.repec.org/a/bla/jfinan/v47y1992i5p1731-64.html | trading-range-break rule, DJIA 1897-1986 | Verified (RePEc page opened; abstract read). |
| Chung & Bellotti, arXiv 2101.07410 (Jan 2021), https://arxiv.org/abs/2101.07410 | S/R levels: bounce probability rises with prior bounces, decays with time | Verified (arXiv abstract opened). |
| George & Hwang 2004, *J. Finance* 59(5):2145-2176, doi 10.1111/j.1540-6261.2004.00695.x | 52-week-high nearness predicts returns | PARTIAL. Wiley returned 403 and RePEc 404; metadata and abstract confirmed only through search-index snippets (Wiley, Semantic Scholar). Abstract only, secondary. Used as context, Confidence capped at M. |
| Jia, Simkins, Yan, Zhang, Zhao, SSRN 5386180 (7 Aug 2025); journal listing S0378426625002122 | nearness-to-52w-high (Nearness52) predicts cross-section of crypto returns | PARTIAL. SSRN and ScienceDirect both 403; title/authors/date/abstract confirmed on a secondary mirror (paperswithbacktest.com) and search index. Cost treatment not stated in what I could read. Tag T2 (SSRN preprint), not T1, until the journal page is opened. |
| Gervais, Kaniel & Mingelgrin 2001, *J. Finance* 56(3):877-919 | abnormal volume predicts next-month returns | PARTIAL. Wiley/RePEc/EconPapers listings appear in search, abstract from the search index; page not opened. Context only. |
| Seuma, arXiv 2607.27070 (29 Jul 2026), https://arxiv.org/abs/2607.27070 | early-warning signals across seven BTC liquidation cascades | Verified (abstract opened). Does NOT study post-cascade price reversal. |
| Bookmap blog "Stop hunt or just noise" (8 Jul 2025), https://bookmap.com/blog/stop-hunt-or-just-noise-how-to-read-the-real-intent-behind-a-move | practitioner stop-hunt signals | Opened. No author, no quantified evidence. T3 (vendor content). |
| Repo: `research/_archive/loose_2026-10/OI_DELTA_4STATE_BACKTEST_2026-09-21.md`, `research/_archive/loose_2026-10/whale_positioning_evidence_2026-09-12.md` | our own OI/funding prior work | Read. Outranks external per gate 3e, but sample is only 8-9 days of snapshots and is not event-conditioned on breaks. |

## Q1. CONTINUATION vs SWEEP - EVIDENCE

### Q1.1 Stop and limit clustering at levels (mechanism)

| Finding | Tier \| Method quality \| Confidence |
|---|---|
| Stop-loss orders cluster just beyond round numbers; take-profit orders cluster at round numbers (Osler 2003, first order-level data set, USD-major FX dealer orders). Supports "trends reverse at S/R" AND "trends speed up after crossing". | T1 \| real order data, FX only, no crypto, no costs (not a trading test) \| M (mechanism), L (transfer to BTC perps) |
| Rates move unusually fast after reaching levels where stop orders were documented to cluster; stop-loss response is larger and longer-lasting than take-profit response (Osler 2005). Effects significant on hourly windows, not consistently on daily (from abstract summary). | T1 \| high-frequency FX, order-cluster documentation, no costs \| M |
| Published S/R levels predict intraday trend interruptions, with power varying by currency and by firm (Osler 2000). | T1-class (central-bank review series; treat as T1 only for the "levels have some power" claim) \| six FX firms, FX only \| M-L |
| S/R levels coincide with peaks of limit-order-book depth (NYSE stocks); technical levels proxy liquidity provision (Kavajecz & Odders-White 2004). | T1 \| equities book data \| M |
| S/R levels are not explained by AR(1); repeated bounces raise bounce odds; bounce odds decay over time without interaction (Chung & Bellotti 2021). | T2 \| intraday, disclosed algorithm; cost-free descriptive study \| M |

Reading: the literature supports BOTH sides of the operator's question as mechanisms. Take-profit clustering at
a level favours reversal (sweep-and-reclaim); stop clustering just beyond it favours a burst continuation
(cascade). Neither tells us the base rate of "hold" vs "reclaim" per timeframe. That base rate is exactly what
our event study must measure. Timeframe hint: Osler's significance on hourly but not daily windows is the only
external hint that cascade effects are a short-horizon phenomenon.

### Q1.2 Breaks of prior extremes as momentum signals

| Finding | Tier \| Method quality \| Confidence |
|---|---|
| Buy signals (trading-range break above prior max) beat sell signals; returns after sell signals were negative; inconsistent with random walk, AR(1), GARCH-M, EGARCH nulls (Brock et al. 1992, DJIA 1897-1986). Supports continuation after DAILY-scale breaks in equity indices. | T1 \| 90 yr, bootstrap nulls, no transaction costs in the original \| M (later data-snooping critiques exist; not researched here) |
| Nearness to the 52-week high dominates past returns as a predictor and does not reverse long-run (George & Hwang 2004). Supports continuation for breaks of a long-horizon high. | T1 (abstract only, secondary access) \| US stocks, monthly, 6-12 month hold \| M-L for transfer |
| Crypto analogue: nearness to the 52-week high predicts weekly cross-sectional crypto returns (~130 bp/week spread, value-weighted). | T2 \| preprint/journal listing unopened, cost treatment unseen; a third-party backtest of the same idea on the same site reported a poor live-like result, so ignore that as evidence but note the claim is fragile \| L |

Reading: at weekly-plus horizons the evidence leans continuation (momentum near highs). Those are
cross-sectional or index results; none tests "single asset, single swing level, close beyond it" at 15m-4h.

### Q1.3 Crypto-specific liquidation-cascade work

- Seuma (arXiv 2607.27070, 2026): seven BTC perp cascades 2022-2025, minute price + 5m leverage/flow. Finds
  early-warning signals differ by event ("no variable is event-invariant"); price shows critical slowing in 5 of 7,
  absent in the two tariff shocks. `Tier T2 | preprint, n=7, no reversal study, no costs | Confidence L`.
  Useful only as a caution that a single indicator will not identify a cascade in advance.
- **No validated evidence found** for (a) the frequency of "break then reclaim" vs "break then hold" per timeframe
  on BTC perps, (b) whether swing-low breaks are followed by reversal more often on higher timeframes, or
  (c) post-cascade price reversal statistics. Searches of arXiv/SSRN-indexed results returned only exchange-news and
  vendor commentary for these (all REJECT, see end).
- **Crypto S/R breakout rules**: two journal papers on Bitcoin technical rules surfaced in search but could not be opened
  (403 / certificate error), so they are excluded from findings and listed under discards.

### Q1.4 Practitioner concepts (T3, ideas and definitions only)

- **ICT "liquidity sweep / stop run"**: price trades through a prior swing high/low to take resting stops, then
  closes back inside and reverses. Operationally: wick beyond level + close back inside within 1-few bars.
- **Wyckoff "spring" (below range low) / "upthrust" (above range high)**: brief violation of a range boundary with
  rapid recovery, read as absorption. The Wyckoff reference page I tried (StockCharts) failed to open (TLS error), so
  this is described from general knowledge, not a verified citation.
- **Fake-breakout checklists** (vendor blogs, e.g. Bookmap): "aggressive volume with no follow-through", absorption
  (large volume, little price progress), and fast pullback below the broken level mark a trap. No numbers, no sample.
  `Tier T3 | zero quantified evidence | Confidence L`. These supply the candidate confirmers in Q2 and the outcome
  classes in Q3; they are hypotheses, not findings.

### Q1 verdict on "does the outcome depend on timeframe?"
**No validated evidence found.** The only external hints: momentum evidence exists at weekly-plus horizons (Brock,
George-Hwang), and Osler's cascade effect is significant hourly but not daily. Both are in different markets. It is a
testable hypothesis (H3 below), nothing more.

## Q2. WHAT CONFIRMS WHICH CASE - EVIDENCE PER CONFIRMER

| Confirmer | Hypothesised reading | Evidence | Tier \| Method \| Conf |
|---|---|---|---|
| Reclaim within N bars | fast reclaim = sweep; no reclaim = continuation | Definition only; vendor blogs. Chung-Bellotti show levels lose bounce odds over time, which is consistent but not a test | T3 \| none \| L |
| Volume spike on break | high volume with no follow-through = absorption; high volume with follow-through = real | Gervais et al. (abnormal volume -> next-month drift, equities, context only). Nothing on breaks | T1 (context) \| monthly horizon, not break-specific \| L |
| CVD (taker delta) divergence at the break | price makes new extreme, CVD does not = sweep | Repo layer uses it; its original "2026 JFM" citation was unverified (playbook Part I preamble). Order-flow T1 result (JFM 2026, 84 coins, daily/weekly) is directional, not break-specific (`whale_positioning_evidence_2026-09-12.md`) | T1 (adjacent) \| not break-specific \| L |
| OI delta on the break | OI falls = stops/liquidations closing (sweep, move exhausted); OI rises = new positions added in break direction (continuation) | Retail 4-state convention (T3 definition, see T055a). Our own 4-state backtest exists but on 8-9 days of snapshots, not break-conditioned | T3 \| own backtest tiny \| L |
| Funding | extreme funding on the crowded side raises sweep-against-crowd odds | Repo prior: one T2 study on extreme funding (Memon 2026, 7 y Binance); not break-conditioned | T2 \| one study \| L |
| RSI state | RSI extreme/divergence at the break = exhaustion | No source found tying RSI state to break outcomes | **No validated evidence found** |
| Liquidation data | large liquidations spike at break = cascade or capitulation | Only news/vendor commentary. Note: Binance public archive has no liquidation dataset among the ones our fetcher pulls | REJECT-level sources only; **No validated evidence found** |

Bottom line: every confirmer is currently a T3 hypothesis. That is acceptable for research design, but "a system
change backed only by T3 needs explicit operator approval" (Part I consequences), so no confirmer may be wired
into any rule before the event study below passes out-of-sample.

## Q3. EVENT DEFINITIONS AND BACKTEST PLAN (CANDIDATES - NOT FORMULAS.md)

### 3.1 Data we hold (checked 2026-09-29)

| Dataset | Path | Coverage | Use |
|---|---|---|---|
| 1m klines with taker-buy volume | `Dumps/backtest/raw_1m_2022/klines` (2022-01 to 2025-08, 44 files) + `Dumps/backtest/raw/klines` (2025-09-01 to 2026-09-26) | ~4.7 yr, contiguous by file names (gap check still required via `bt_data.check_gaps`) | price, volume, CVD (`bt_data.cvd_delta = 2*tbv - v`) for all TFs by resampling |
| 1d klines | `Dumps/backtest/raw_1d/klines` (2020-01 to 2025-08) | 5.7 yr | weekly/daily swings with a longer history (no tbv guarantee, verify) |
| Metrics (5m OI, long/short ratios) | `Dumps/backtest/raw/metrics` | 2025-09-01 to 2026-09-26 only | OI delta, positioning conditioners: ~13 months only |
| Funding | `Dumps/backtest/raw/fundingRate` | 2025-09 to 2026-08 (12 monthly files) | funding cost and level: ~12 months only |
| Mark price 1m | `Dumps/backtest/raw/markPriceKlines` | 2025-09 to 2026-09 | stop realism |
| bookDepth | `Dumps/backtest/raw/bookDepth` | 2025-09 to 2026-09 | optional proxy only |
| aggTrades | `Dumps/backtest/raw/aggTrades` | EMPTY | none; tick tiers must come from 1m bars |

Loaders: `MyTradingSys/backtest/bt/bt_data.py` (`load_klines`, `load_metrics`, `load_funding`, `funding_rate_at`,
`cvd_delta`, `check_gaps`); fetch: `backtest/fetch_binance_archive.py` (supports `--interval` and metrics/fundingRate).
`MyTradingSys/data/klines/*.json` are 100-row samples; do not use them.
Tick tiers: `backtest/layers/tick/tick_extremes.py.new`, `tick_flagger.py.new`, `tick_oi_extremes.py.new` exist only as
staged `.new` files (not promoted); the study should depend on them only after promotion, or reimplement `gap_tiers`.

### 3.2 Swing extreme (candidate SW-1: confirmed fractal, no look-ahead)

Bar `k` on timeframe TF is a swing low if `low[k] < low[k-j]` and `low[k] <= low[k+j]` for j = 1..L (strict on the
left, per the repo's `cc_structure.find_swings` style; ties resolved to the earliest). It becomes KNOWN only at bar
`k+L`'s close (confirmation bar). The level = `low[k]` (wick), with a body-level variant `min(open,close)[k]` for
sensitivity. Symmetric for highs. A level is "live" from confirmation until first broken; only the most recent live
swing on each side is tracked, plus a "major" variant (highest-rank swing within the last M bars).

| TF | Primary L (left=right) | Sensitivity L | M (major lookback, bars) |
|---|---|---|---|
| Weekly | 2 | 1, 3 | 26 |
| Daily | 3 | 2, 5 | 60 |
| 4h | 3 | 2, 5 | 90 |
| 1h | 5 | 3, 8 | 96 |
| 15m | 5 | 3, 8 | 96 |

All TFs built by UTC epoch-floor bucketing from 1m (`tick_extremes.resample`/FORMULAS section 8 convention); only closed
buckets. Parameters are starting values, not tuned; the grid above is the ENTIRE search space and is counted in
the multiple-testing budget.

### 3.3 Break (candidate BRK-1) and outcome classes (candidate OUT-1)

- **Touch**: first 1m bar whose low < level (high > level for highs). Event timestamp is that 1m bar, so intrabar
  order is resolved at 1m and TF-bar-close info is never used before it exists.
- **Close-break**: the first TF bar whose CLOSE is beyond the level by at least `buf = 0.1 * ATR14_TF` (buffer tested
  at 0 and 0.25 too). ATR per FORMULAS section 12 (plain SMA, operator decision 2026-09-28).
- **Classes** (evaluated at the close of the touch bar's TF bar, then over the next N TF bars):
  - **W1 wick-sweep**: touch occurs but the TF bar closes back inside the level (no close-break).
  - **R reclaim**: close-break occurs, then some TF close returns inside the level within N bars.
  - **H hold**: close-break occurs and no TF close is back inside within N bars.
  - **X extension** (subset of H): H plus a further extreme `>= 1.0 ATR` beyond the level within the horizon.
  - N (reclaim window, TF bars): W 2, D 3, 4h 6, 1h 6, 15m 8; sensitivity {N/2, 2N}.
- **Forward measures** from the NEXT bar open after the class is known (no look-ahead): signed return to horizons
  h = 1, 4, 12, 24 TF bars and 24h/72h calendar; MAE and MFE per FORMULAS section 7 but using intrabar high/low (the
  section 7 note prefers that); "trade" versions: fade R (enter long after a low reclaim, stop at the sweep extreme,
  target 1.5R and 2R), follow H (enter short, stop at the level plus 0.5 ATR).
- **Costs**: taker 0.05% each side (repo default `cc_bt_adapter`), 1-2 bp slippage sensitivity, funding accrual by
  actual 8h settlement timestamps from the funding file (long pays when rate > 0). Report gross and net separately.

### 3.4 Indicator snapshot (before / at / after)

Window definitions on the event TF: PRE = mean/last over bars `i-5..i-1`; AT = break bar `i`; POST = bars `i+1..i+N`.
Record deltas POST-AT and AT-PRE (not levels alone), since the ask is "compare current, before and after".

| Indicator | Source | Fields |
|---|---|---|
| RSI(14) Wilder | FORMULAS section 1 | value at PRE/AT/POST; regular-divergence flag (price lower low, RSI higher low vs previous swing) |
| CVD | `cvd_delta` summed over TF bars | AT bar delta; cumulative delta PRE vs AT; divergence flag (price new extreme, CVD not) |
| OI delta | metrics 5m `sum_open_interest` resampled | OI change PRE, AT, POST as % and as z-score vs 30-day; sign class (closing vs adding) |
| Funding | funding file | last settled rate at AT; percentile over trailing 30 days; time to next settlement |
| Volume | 1m sum per TF bar | AT volume / median of previous 20 same-TF bars; POST/AT ratio (follow-through) |
| Tick tiers | `tick_extremes.build_tier_table` (1,2,3,5,10,15 min; net_delta, cvd_change, volume, price_change_pct) | tier of the 1-15m bucket containing the touch, per indicator; count of tier-1/2 flags in +/-30 min |
| Position class | OI + price 4-state (T055a) | long_build / short_build / short_cover / long_unwind at AT and POST |
| Context | timestamps | session tag (`session_tag`), funding-window flag (`in_funding_window`), day of week |

Liquidations are NOT in our datasets; the study uses OI drop plus volume spike plus adverse price as a labelled proxy
(never called "liquidations" in outputs).

### 3.5 Controls and validation

1. **Random-level control (C1)**: for each real swing break, draw a matched pseudo-level: same TF, same distance below
   price (in ATR) as the real level had at confirmation, but from a non-swing bar (not a local fractal) chosen at a random
   time in the same volatility tercile. Run the identical break/class pipeline. Real-minus-pseudo class frequencies and
   forward returns are the effect of "being a swing", which is the actual claim.
2. **Time-shuffle control (C2)**: keep real levels but shift their event dates by random multiples of 7 days (preserves
   day-of-week and volatility regime); 1000 replications for a null of class frequencies.
3. **Unconditional baseline (C3)**: forward returns of all TF bars, and of all bars with `low < min(low, prior M bars)`
   (a plain rolling channel break, Brock-style). A swing break must beat the rolling break to earn a separate layer.
4. **Splits**: development 2022-01-01 to 2024-06-30; validation 2024-07-01 to 2025-08-31; untouched holdout 2025-09-01
   to 2026-09-26. Definitions and N are frozen after development; validation is used once to choose among <= 3 frozen
   candidates; holdout is opened once. OI/funding-conditioned tests can only use the holdout year (data limit), which
   is too small to validate conditioners, see gaps.
5. **Statistics**: events overlap in time; use week-block bootstrap CIs and report n and days per cell. Multiple testing:
   5 TF x 3 L x 3 N x 4 horizons x 2 sides is large; report DSR/PBO via `backtest/bt/bt_stats.py` and `ref_pbo.py`
   (FORMULAS section 10), verdict via `backtest/verdict.py`. Cells with n < 30 are labelled descriptive only.
6. **Power warning**: weekly swings over 4.7 yr give only tens of events per side; W and D results will be
   underpowered. Fetching 1d klines back to 2017 (Binance futures start 2019-09) or spot BTCUSDT would help (data decision).
7. **Cross-check**: reuse `cryptocred/cc_structure.find_swings` as a sanity comparison (its `left/right` defaults are 2/2);
   differences in swing counts are reported, not silently reconciled.

### 3.6 Formula candidates (report only; NOT in FORMULAS.md)

| ID | Candidate | Source basis |
|---|---|---|
| F-SW1 | Confirmed fractal swing (3.2) | repo `find_swings` prior + standard fractal (Williams-style); ours to define |
| F-BRK1 | Touch / close-break with ATR buffer (3.3) | own definition; ATR from FORMULAS section 12 |
| F-OUT1 | Class W1/R/H/X with window N (3.3) | own definition |
| F-RECLAIM_T | reclaim time = bars from close-break to first close back inside | own definition |
| F-OIcls | OI closing/adding sign class at the break | T055a 4-state convention (T3) |
| F-CVDdiv | price-extreme / CVD-non-confirm flag | repo CVD layer; derivation needs independent check |
| F-VOLr | volume ratio vs 20-bar same-TF median | own definition |
| F-C1 | matched pseudo-level draw (3.5 item 1) | own design |
Per the gate, each needs a canonical definition and hand-computed cases in FORMULAS.md before any Qwen spec.

## Q4. SATELLITE HOOK (T048) - PROPOSAL ONLY

Not implemented, not validated, and gated on Q1/Q2 outcomes. T048 says satellites spawn on a "validated condition"
and run on a separate sub-account with their own stop; this proposal only names candidate classes.

| Outcome class | Meaning for a parent position | Proposed satellite behaviour (hypothesis) |
|---|---|---|
| H/X on Daily or Weekly against the parent (e.g. parent long, daily swing low held-broken, OI adding) | continuation risk | Candidate HEDGE trigger: small counter-position sized as a fraction of parent notional, scaled up with TF (W > D > 4h); own stop = reclaim of the level; closes when reclaim happens |
| R (reclaim) after a wick break against the parent | sweep likely done | Do NOT hedge; if a hedge already exists, candidate to close it. Optional: a with-parent add is a core-layer decision, not a satellite |
| W1 sweep on 15m/1h only | noise-scale | No hedge; log only (cost of a satellite at that scale likely exceeds edge) |
| H at 1h/4h with CVD/OI confirming | short-term continuation | Only a small, short-lived scalp satellite, aligned with T053 (two-account hedge scalping) |
Sizing inputs to test (not fixed): timeframe weight, reclaim-time bucket, OI class, distance of the level from the parent's stop.
Governance dependencies unchanged from T048 (max concurrent, recursion depth, notional caps). None of this may gate
core Tom behaviour (modules never gate core). Operator decision needed before any implementation: whether the hedge
trigger may use only H-class confirmed AFTER N bars (delay, less loss avoided) or also touch-time signals (earlier, noisier).

## TOP TESTABLE HYPOTHESES (ranked)

- **H1**: For BTC perp swing breaks, the reclaim frequency of real confirmed-swing levels differs from matched pseudo-levels
  (C1) and depends on timeframe: higher TFs hold more, lower TFs reclaim more. Basis: Brock 1992 + George-Hwang (T1, weekly+
  equities, momentum) vs Osler 2003/2005 (T1, FX, clustering and hourly cascade). `Tier T1 (mechanism, other markets) -> our test decides | Confidence L`.
- **H2**: A close-break with OI rising and CVD non-diverging holds (class H) more often than one with OI falling; fast reclaim
  follows OI-falling, volume-spike, CVD-divergent breaks. Basis: practitioner (Bookmap etc.) + 4-state convention. `T3 | Confidence L`; testable only on 2025-09+ data.
- **H3**: Net of taker fees and funding, fading R-class reclaims (long after a low reclaim) outperforms a plain rolling-channel-break
  baseline (C3) out-of-sample on 1h/4h. Basis: Osler take-profit clustering mechanism. `T1 mechanism / T3 trade rule | Confidence L`.

## DATA GAPS
1. OI (metrics) and funding exist only 2025-09 to 2026-09; the 2022-2025 sample has none. Extend via `fetch_binance_archive.py`
   (metrics/fundingRate) if the archive covers those dates (unverified here).
2. No liquidation dataset; no aggTrades (tick tiers come from 1m bars only, so a tier is a 1m-bucket property).
3. Weekly/daily event counts are small; longer daily history (2019-09 onward) would help.
4. Tick-tier modules are still `.new` (unpromoted).
5. Cost model for shorts on lower TFs needs realistic slippage; mark-price stop fills are available from 2025-09 only.

## DISCARDED (not to be re-researched)
- Vendor/news pages on stop hunting, false breakouts and liquidation cascades (TradingView idea, Titan FX, PriceActionNinja, afaq.trade, arongroups,
  chartscout, coinchange, CryptoRank/Bitget/OneBullEx liquidation news): marketing/no method - REJECT.
- Gerritsen et al. 2020 (FRL, ScienceDirect S1544612319303770) and the 2024 "simple technical trading rules in bitcoin markets" paper (S1059056024003010):
  could not be opened (403 / certificate error) - REJECT until opened.
- paperswithbacktest strategy page: used only to read the anchoring paper's abstract; its backtest numbers are unaudited - REJECT as evidence.
- Wyckoff spring/upthrust and ICT sweeps as "evidence": T3 ideas, no quantified source - kept as vocabulary only.
