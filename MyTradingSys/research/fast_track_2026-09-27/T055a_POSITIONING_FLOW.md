> **CORRECTION (operator 2026-09-29):** operator states the cited source for opening order imbalance (4-12 h) was the wrong paper and the real source is Kim & Hansen (tier T1 -> T2).
> Verified 2026-09-29 (arxiv.org/abs/2607.09426): "The Quarter-Hour Effect: Periodic Algorithmic Trading and Return Predictability in Cryptocurrency Futures", Chan Kim and Peter Reinhard Hansen, submitted 10 Jul 2026 (v2 16 Jul 2026). Abstract: "opening order imbalance predicts returns over four to twelve hours". Six Binance perpetuals, trade data. Arxiv preprint, no independent replication: tier T2, not T1. The body below already carries this fix (Step 3a table and evidence table); where any line still grades it T1, read T2. Body not edited.

# T055a - Positioning Flow (Net/New Longs & Shorts) Research [GATED v3.0]

Source item: `MyTradingSys/items/T055_positioning_flow_and_proven_setups.md`, part (a).
Superseded: the pre-gate version (ad-hoc A/B/C grades) is backed up at
`T055a_POSITIONING_FLOW.md.pre_gate3`. This version applies playbook.md Part I v3.0.
Reused prior gated research (not re-derived): `research/_archive/loose_2026-10/whale_positioning_evidence_2026-09-12.md`
(order-flow and funding tiers), `research/_archive/loose_2026-10/OI_DELTA_4STATE_BACKTEST_2026-09-21.md` (our own
backtest, outranks external sources per gate Step 3e).

## STEP 1 - METHOD NOTES

- **Definitions**: settled by checking what data/formula each vendor/exchange actually publishes
  vs. infers; no statistical test needed, just source verification (does the endpoint exist, does
  the formula match docs).
- **Setups**: settled only by an out-of-sample backtest with costs on Binance/Deribit data; a rule
  stated precisely without a number is a definition, not evidence.
- **MTF trend bias**: settled by a walk-forward test comparing HTF-delta-filtered vs. unfiltered
  entries on an existing layer, costs included; no accepted academic method exists for this
  specific construct, so absent that, the workflow claim stays "unvalidated domain."
- **Quantitative evidence**: settled by peer-reviewed or disclosed-method OOS studies with a
  stated sample, horizon, and cost treatment; abstract-only access is acceptable if the claim is
  in the abstract.
- **Related indicators**: settled by checking what companion series independent sources
  consistently pair with positioning flow, tiered same as above.

## STEP 3a - CITATION CHECK (opened 2026-09-28)

| Source | Claimed for | Result |
|---|---|---|
| EuropePMC ppr602886 | "opening order imbalance predicts returns 4-12h, six Binance perps" | **MISMATCH - REJECT.** Opened; this is Wen/Bouri/Xu/Zhao 2022 ("Intraday Return Predictability in the Cryptocurrency Markets: Momentum, Reversal, or Both", SSRN 4080253/ScienceDirect S1062940822000833) - BTC/ETH/LTC/XRP price momentum-reversal on 2013-2020 data, no order imbalance construct, no six-Binance-perp sample. The 4-12h/six-Binance-perp finding actually belongs to Kim & Hansen, "The Quarter-Hour Effect: Periodic Algorithmic Trading and Return Predictability in Cryptocurrency Futures", arXiv 2607.09426 (Jul 2026) - verified 2026-09-28, matches on title/authors/abstract. Logged to 02b_DECISIONS_LOG.md. |
| ScienceDirect S1544612326008688 | Bitcoin option-expiry OI/gamma -> spot reversal | Verified 2026-09-28. Weiss, Gaudiosi, Zhou, Webb, *Finance Research Letters*, Jun 2026. Title/topic match (gamma-exposure-conditioned reversal on expiry days). Peer-reviewed journal = T1. |
| arXiv 2212.06888 | perpetual-futures no-arbitrage/funding theory | Verified 2026-09-28. He, Manela, Ross, von Wachter, "Fundamentals of Perpetual Futures", Dec 2022 (rev. ongoing). Matches. T2 (arXiv, disclosed method, now widely cited). |
| arXiv 2402.03953 | unexpected OI changes affect perp returns | Verified 2026-09-28; matches title/authors (Chen/Ma/Nie). Confirmed DEX-specific (VAMM/oracle-pricing exchange designs) - not implementable/testable against Binance/Deribit CEX public data. Discarded on that basis, not on citation grounds. |
| arXiv 2411.08382, arXiv 2304.02472 | generic order-flow/volume-imbalance predicts short-horizon price | Both exist but are generic equity/crypto microstructure, not BTC-perp specific; superseded for this task by the directly-on-topic Quarter-Hour Effect paper. Discarded as redundant. |
| Binance REST docs (Top-Long-Short ratios) | exchange-published long/short ratio formulas | Verified 2026-09-28 against developers.binance.com; endpoint names and formulas match. T2 (exchange docs). |
| Coinalyze blog/PDF, CryptoCred guide, Velo writeup | 4-state OI+price / OI+CVD definitions | Practitioner/vendor sources, used for definitions only (permitted at T3); not re-opened line-by-line this pass since no predictive claim rides on them beyond the definition itself. |

## 1. DEFINITIONS (surviving)

Four-state OI+price heuristic (long_build/short_build/short_cover/long_unwind from sign of
`d_oi` and `d_px`) and the OI+CVD variant (same states, aggressor proxy = `cvd_delta` instead of
`d_px`) are documented practitioner conventions, not exchange-defined ground truth - OI is
symmetric by construction, no venue publishes which side opened a contract. `Tier T3 | definition
only, no method to validate | Confidence H` (as a definition; N/A as a predictive claim).
Already implemented in the repo: `MyTradingSys/runtime/backtest_oi_delta_4state.py` (price
variant, consumer only) and `MyTradingSys/backtest/bt/bt_data.py::cvd_delta()` (CVD variant).

Binance `topLongShortAccountRatio` / `topLongShortPositionRatio` / `globalLongShortAccountRatio`
are true point-in-time account/position splits (not OI-delta decompositions). `Tier T2 | exchange
docs, formula disclosed | Confidence H`. Not currently fetched anywhere in the repo.

## 2. SETUPS - context for H1, not independent hypotheses

Long-buildup continuation, short-squeeze, absorption, CVD/price divergence, positioning
exhaustion, and the 4-state regime map are consistently described across practitioner sources
(Coinalyze, CryptoCred, Hyblock Academy, XT.com, arrowalgo.com) as confluence context, never as a
standalone backtested edge - no source supplies a win rate, Sharpe, or sample size.
`Tier T3 | rules stated precisely, zero OOS evidence | Confidence L`. These do not get their own
backtest plan; they are exactly what H1 below tests as a package (the 4-state classification
itself), so listing them separately would duplicate H1's test.

## 3. MULTI-TIMEFRAME DELTA FOR TREND BIAS

**No validated evidence found** for "HTF delta sets bias, LTF delta times entry" as a specific,
numbered rule - every source (BackQuant, CoinUnited) states it as a workflow recommendation with
no backtest. `Tier T3 | zero OOS evidence | Confidence L`. Kept as operational caveats only
(cross-exchange OI divergence, weekend/thin-liquidity noise, funding/expiry resets, 5m snapshot
granularity as a data-source limit, not a signal) - these affect how H1/H2 must be implemented,
not whether they work.

## 4. QUANTITATIVE EVIDENCE (corrected)

| Finding | Tier \| Method quality \| Confidence | Source |
|---|---|---|
| Opening order imbalance predicts BTC/ETH/XRP/SOL/DOGE/ADA perp returns at 4-12h, much weaker at fine clock-time frequencies | T2 \| single preprint, OOS claimed in-paper, no independent replication yet, cost model not shown in abstract \| M | Kim & Hansen, arXiv 2607.09426, verified 2026-09-28 (replaces the mis-cited EuropePMC source) |
| Bitcoin option-expiry OI + gamma exposure -> spot reversal, concentrated on high-ATM-OI/negative-gamma days | T1 \| peer-reviewed event study, expiry-day conditional, no explicit cost model in abstract \| M | Weiss et al., *Finance Research Letters* 2026, verified 2026-09-28 |
| Order flow (daily/weekly horizon, 84 cryptocurrencies) has directional predictive power | T1 (already gated) | `research/_archive/loose_2026-10/whale_positioning_evidence_2026-09-12.md` section 3 - reused, not re-derived; different horizon than the Quarter-Hour result above, both point the same direction |
| DEX-specific: unexpected OI changes move perp returns more than expected changes | Discarded - not testable on Binance/Deribit CEX data | arXiv 2402.03953 |

**No source found gives a direct, numbered backtest of the retail OI-4-state heuristic itself**
predicting BTC returns (section 1/2). The two strongest adjacent results are the order-imbalance
finding and the option-expiry-reversal finding above, neither of which is the OI-split heuristic.

## 5. WHAT THE REPO ALREADY HAS (internal fact-check, unchanged from prior pass)

CVD (`bt_data.py::cvd_delta()`) and funding rate are already fetched; no raw OI history fetch and
no Binance long/short-ratio ingestion exist yet. `backtest_oi_delta_4state.py` expects OI
direction supplied upstream, it does not compute it. Our own related backtest already exists:
`OI_DELTA_4STATE_BACKTEST_2026-09-21.md` classified bars by sign of `trade_flow.net_delta_1h` (not
true OI) into aggressive_long/aggressive_short/rekt_long/rekt_short/neutral and measured forward
returns at 30/60/120m - effect sizes were small and day-clustered SEs were wide (e.g.
aggressive_short at 120m: +0.52% mean, se 0.31%, n=1019 over 8 days), i.e. suggestive but not
significant on 8-9 days of data. Per gate Step 3e this internal result outranks any external
source for H1 and sets the honest prior: expect a weak effect, not a strong one.

## 6. SURVIVING HYPOTHESES

**H1 - OI-delta x CVD 4-state filter.** Rule: gate existing trend-following layer entries to bars
where `state in {long_build, short_build}` aligned with trade direction (section 1 formulas);
skip `short_cover`/`long_unwind` bars. Data needed: Binance `futures/data/openInterestHist` (new
fetch, public/no-auth) or, as a cheaper first pass, reuse the already-computed
`trade_flow.net_delta_1h` proxy exactly as `OI_DELTA_4STATE_BACKTEST_2026-09-21.md` did, on more
days. Backtest plan: paired A/B (filter on/off) on an existing Fabio or Tom-core layer, 1h and 4h
bars, >=2 non-overlapping OOS walk-forward windows spanning at least 60 days each (the prior
internal run only had 8-9 days - too short to trust), cost = repo taker-fee + slippage assumption.
Kill if: filtered variant does not beat baseline net of costs on both OOS windows, or effect size
stays inside the day-clustered SE band seen in the prior internal run.

**H2 - CVD/price divergence + extreme funding fade.** Rule: enter mean-reversion trade when
`|funding_rate| > repo-defined extreme percentile` AND CVD/price diverge over a 20-50 bar lookback
on 15m. Data needed: none new - funding and CVD already fetched. Backtest plan: horizon = time to
TP/SL in points, walk-forward OOS, must show positive expectancy net of round-trip cost. Supporting
prior evidence: funding-extreme reversion already tiered T2 in `whale_positioning_evidence
_2026-09-12.md` (Memon 2026, 7y Binance) - reuse that tier, do not re-search it. Kill if: divergence
events are too rare at BTC 15m/1h to reach a usable sample size, or OOS Sharpe < 0.3.

**H3 - Opening/quarter-hour order-imbalance predictor, 4-12h horizon.** Rule: resample existing
`cvd_delta`/taker-buy-volume to the start of each 4h/12h window, treat the sign+magnitude of the
opening-window imbalance as the predictor. Data needed: none new - reuses klines fields already
fetched. Backtest plan: regress/bucket forward 4h and 12h returns on the imbalance signal, OOS,
compare direction and magnitude to Kim & Hansen (arXiv 2607.09426, T2, not yet independently
replicated). Kill if: no return predictability survives repo cost assumptions at BTC frequency (the
paper's six-perp sample includes BTC but was not run BTC-alone in the source).

All three are implementable from data the repo already fetches except H1's full-OI variant, which
needs the one new `openInterestHist` fetch flagged as a T0/T1 data task before backtesting.

## 7. FORMULA CANDIDATES FOR FORMULAS.md (not added yet)

- `oi_delta_4state(d_oi, d_px_or_cvd)` -> {long_build, short_build, short_cover, long_unwind}.
  Canonical definition: section 1 above. Source: practitioner convention (Coinalyze, Velo), T3.
- `cvd_delta` - already defined in FORMULAS.md's consumer code (`bt_data.py`); no new entry needed,
  cite existing.
- `opening_window_imbalance(window)` = signed taker-buy-vs-sell volume over the first N minutes of
  a 4h/12h window. Canonical definition/source: Kim & Hansen, arXiv 2607.09426, T2.

## 8. DISCARD LIST

- EuropePMC ppr602886 - REJECT, citation mismatch (wrong paper; see Step 3a table). Logged.
- arXiv 2402.03953 - DEX-specific, not testable on Binance/Deribit CEX public data.
- arXiv 2411.08382, arXiv 2304.02472 - generic microstructure, not BTC-perp specific, redundant
  with the Quarter-Hour Effect paper.
- Section-2 setup list as independent hypotheses - folded into H1, would duplicate its test.
- MTF-delta "HTF bias / LTF entry" as a numbered rule - no T1/T2 evidence found; kept only as
  operational caveats, not as a rule to implement on its own.
