# WaveTrend: independent skeptical evidence review

Research date: 2026-10-17. Scope: external evidence only; no MTS trading implementation inspected. This report describes claims observed on publisher pages, not independently rerun results. All linked URLs below were opened; failed opens are explicitly identified. Searches covered LazyBear strategy/backtest evidence, named author strategies, FX parameter studies, crypto futures runs and methodological primary sources.

## Verdict and evidence standard

No validated evidence found that LazyBear WaveTrend provides a durable, net-of-cost edge in BTC perpetuals. This is a scoped search conclusion, not proof that an edge cannot exist. No located WaveTrend efficacy result qualified as T1 or T2. Fixed source tiers: T1 = peer-reviewed/institutional research with disclosed method; T2 = preprints, exchange documentation, or replicated full practitioner studies; T3 = author definitions/studies and unreplicated community backtests. Source tier and efficacy confidence are separate: even a high-tier source need not establish an edge. Publicly visible examples supply hypotheses and counterexamples, not deployment evidence. An indicator is not a complete strategy; implementations called WaveTrend differ materially.

For this review, effectiveness requires exact formula/version, exchange and instrument, sample dates and trade count, locked chronological OOS, costs including funding for perpetuals, feasible fills, complete returns/drawdowns, appropriate passive and simple-rule baselines, and accounting for all parameter/asset/timeframe trials. These are reviewer assessment criteria, not parameters attributed to LazyBear.

## Primary publisher evidence

### Crypto futures: T3 negative backtest with disclosed limitations

[Freqle's WaveTrend run](https://freqle.org/strategy/87e4dcbb8940491a), observed 2026-10-17, reports its own test of adevrent's strategy: 33-pair futures universe, configured 2022-01-01 to 2025-01-01, 7,893 trades, -90.18%, PF 0.75 despite 81.1% wins, 0.05% fee per side. Its last ledger trades are 2023-06-30 / 2023-07-01, not 2025. Its sandbox supplied 5m because code omitted a timeframe. OOS, executable lookahead and recursive analyses were not run; funding/slippage treatment was not established. This is not BTC-only evidence.

Reproducible hypothesis from displayed code: HLC3, EMA lengths 9/12, normalization 0.015, SMA signal length 3; cross up with WT2 below -80 enters long, mirrored +80 short; opposite crosses beyond +/-60 exit. Replication also requires its ROI/trailing/stop rules. These are derivative choices. The page says not rated yet and no discussion yet; neither GitHub stars nor downloads are reviews. Cached versions differed; use this observed run.

### FX: T3 encouraging descriptive result, no demonstrated untouched holdout

[Formiq / Yuichi Saiki, published 2026-08-24, updated 2026-08-30](https://formiq.jp/blog/wavetrend-settings) reports USDJPY 2024 and 2025 tests of 30 period combinations. Its 10/21 hourly crossover made +3,283.4 pips over 867 trades in 2025 and +1,076.6 pips in 2024. All 30 hourly settings won in 2025; 24 won in both years; no M15 setting won in both. Rules: cross up buys, cross down sells/exits; same-bar close fills; 0.3-pip spread, zero slippage; no stop or target.

This is a concrete candidate for replication, not evidence of a BTC edge. Its midpoint-based description requires formula verification. Neither a frozen-before-test chronological holdout, realistic variable execution costs, independent replication, nor multiple-trial correction is demonstrated. Comparing two historical years is not automatically OOS. Selecting the winning timeframe after examining both years adds another selection decision. 

### Crypto spot: T3 correctness audit with negative performance

[Quantroduction WaveTrend_LB audit](https://www.quantroduction.com/docs/audits/WaveTrend_LB) labels itself audited 2026-09-12 and reports a window through 2026-09-14: that date ordering needs clarification. Seven markets, 15m, 2023-07-15 through 2026-09-14; median return -24.9%, median buy-and-hold +49.6%, zero of seven profitable; 3,562 orders, not 3,562 round-trip trades. The page explicitly distinguishes code correctness from profitability and says results were not measured on a live exchange. This is the vendor's own audit, not independent certification. The [performance page](https://www.quantroduction.com/docs/audits/WaveTrend_LB/performance) opened via its link but a later direct retrieval failed; detailed cost and fill assumptions were not verified. Classify as negative author-reported spot evidence, not validated perpetuals evidence.

## Excluded leads: direct page retrieval failed

The following URLs were attempted but could not be reliably opened. They are REJECTED as evidentiary sources in this report; search snippets are not substituted for inspection. Titles and URLs are retained only for a future source-retrieval pass.

- [WaveTrend with Pump Candle Rejection, Reuter](https://www.tradingview.com/script/aQrcWpF8-WaveTrend-with-Pump-Candle-Rejection-Reuter/).
- [WaveTrend indicator strategy on gold, RipBacktest](https://ripbacktest.com/posts/wavetrend-indicator-strategy-gold/).

No performance claims, rules or engagement counts from these excluded leads enter the verdict or proposed replication candidates.
## Technical and statistical failure modes

[TradingView's official repainting documentation](https://www.tradingview.com/pine-script-docs/concepts/repainting/) explains the historical/realtime distinction: current-bar prices change before close; higher-timeframe requests can expose unconfirmed values; plotting signals back on earlier bars can conceal when they became knowable. Application to WT is an inference: an EMA/SMA oscillator using current high/low/close can change a crossover intrabar without requiring future data. Bar-close execution must use a causal fill after confirmation. A divergence requiring future pivot bars is available only after those bars, even if its marker is drawn at the pivot. Audit each derivative's requests, offsets, pivots and alert conditions separately; a non-repainting base oscillator does not certify an MTF/divergence wrapper.

[Bailey, Borwein, Lopez de Prado and Zhu, The Probability of Backtest Overfitting, revised February 2015](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf) establishes why searching configurations produces false discoveries and why a nominal holdout alone does not account for the number of trials. The paper proposes CSCV/PBO. Application here: log every WT length, threshold, asset, timeframe, divergence rule and exit variant tested; retain failed variants. Chronological OOS and a selection-aware uncertainty analysis answer different questions and both matter. Trade shuffling does not by itself prove regime robustness or chronological OOS performance.

## Magic-number skepticism and an honest next experiment

No reviewed evidence establishes that 10/21, normalization 0.015, or oversold/overbought levels have universal economic privilege. Changing normalization rescales the oscillator, so fixed thresholds are inseparable from that choice. Different derivative lengths and signal smoothing create different trading systems. A plausible oscillator picture or popular default cannot substitute for parameter stability and net expectancy.

Proposed experiment (reviewer's protocol, not an author trading prescription): freeze one exact author implementation; record a complete strategy with position sizing and exits; obtain point-in-time exchange perpetual OHLCV and funding; execute confirmed signals no earlier than the next executable price; model taker/maker feasibility, spread, slippage, funding and liquidation. Compare frozen WT rules against exposure-matched passive, simple momentum/mean-reversion and randomized-entry controls. Use chronological development/validation/final untouched test, then paper-forward. Report each period's trades, expectancy and uncertainty, turnover, costs, drawdown and exposure. Treat any parameter sensitivity exercise as another trial family. An isolated optimum should fail the research gate; a broad stable region is still only a candidate for OOS.

## Review-count and experience limitations

There is no defensible market-wide number of WaveTrend reviews: scripts, copies, videos, comments, favorites and broker/product reviews are different populations, often overlapping. Likes express engagement, not verified trading returns; comments are anecdotes unless accompanied by auditable records; stars usually refer to a repository, not one strategy. This search found contradictory publisher backtests (positive USDJPY H1, negative crypto implementations), but did not verify a representative sample of independent trader experiences or any positive BTC-perpetual live track record. Do not present missing counts as zero or infer user profitability from popularity.

## Bounded search log and quality summary

Four distinct query strings across two search calls: `site.tradingview.com WaveTrend LazyBear strategy backtest BTC`; `WaveTrend strategy backtest out of sample study`; `site.tradingview.com "Wave Trend w/ VWMA overlay" "2021"`; `site.davidhbailey.com probability backtest overfitting pdf`. Repeated opens were retrieval attempts, not additional independent evidence. Scope was English-language accessible pages, not an exhaustive systematic review. Searches completed on 2026-10-17. No strategy was rerun and no paywall bypass was attempted.

Quality assessment: Formiq supplies dates, counts and rules, but insufficient holdout/execution/control evidence; Freqle supplies inspectable source and run metrics, but missing OOS and unresolved execution details; Quantroduction supplies an engineering audit and aggregate spot metrics, but independent replication and full assumptions were not verified. The failed-open TradingView leads are excluded. All three inspected WaveTrend efficacy studies are T3 author/publisher reports, not replicated full studies. No T1/T2 WaveTrend efficacy study was located. The Bailey methodology paper is a T1 methodological reference, not a WaveTrend efficacy test; official TradingView documentation supplies platform behavior, not profitability evidence. This qualification applies to negative reports too: they refute universal claims only for the tested implementation/conditions, and do not prove every WT variant fails.
