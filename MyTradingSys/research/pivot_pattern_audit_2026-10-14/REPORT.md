# Pivot-pattern scope audit — 2026-10-14

## Finding and status

The requested question is how candles develop around local, swing and macro tops/bottoms, conditional on the strength and origin of levels and the market phase. The delivered experiments answer narrower questions about close signatures at previous-period highs/lows. They are useful development diagnostics, but do not establish a reversal detector or calibrated bottom/top probabilities.

The Codex chat **Research BTC candle signatures** (01a1390f-99af-7de3-9a86-7a419d542e66) was active with its corrected-rerun turn in progress when inspected. This is evidence of an unfinished chat, not proof that it is stuck. File changes during this audit, a new frozen estimator receipt, preserved prior analyses and regenerated results demonstrate substantive progress. No interruption or duplicate full-data rerun was performed.

Latest inspected result: 1,313,280 minute bars, 79,174 ledger rows, 112,606 matched-pair rows, 2,016 registered cells, 6,048 screening metrics and zero candidate cells. Of 2,016 cells, 1,074 have zero matched events and 1,810 have fewer than 100. These are cell counts, not independent trades. The earlier 1,764-cell result predates the registered level-bounce amendment. Revised verification.json was absent at the root at inspection, while old verification receipts were preserved under analysis_v1 and analysis_v2_before_bootstrap_fix. Consequently the latest result is provisional pending the owning session's independent verification and delivery.

An independent invocation of the current research_gate.py executed **13 tests, zero skips, PASS**. Current engine/rules hashes matched FROZEN.json. This verifies the focused mechanical gate; it is not an independent full-data outcome or interval reconstruction. Snapshot details are in RECEIPT.json.

## What was already available and should be reused

- Original 2026-10-14 METHOD/report, raw-event checks and INDEPENDENT_AUDIT document the 126-cell diagnostic and sampling/test-import weaknesses.
- Corrected PRE_REG, engine/rules, funding coverage, encounter ledger and amendments address comparable encounters, structural phase hypotheses, chronology, costs, placebo stability, orientation and bootstrap normalization.
- CYCLE_DESIGN.md already defines delayed five-bar pivots, reclaim → higher low → structure confirmation, local/swing/persistence labels, missed alerts, confirmation delay and episode-based evaluation. It is a design, not an executed study. Its readiness fields must be refreshed for inputs subsequently assembled.
- The 2026-10-04 candle pilot already tested classical shapes on 1h/1d data. Repeating a broad hammer/engulfing scan would duplicate it; that scan does not settle pivot-conditioned sequences.
- BACKTEST_FAILURES_RESEARCH.md and the non-core layer audit document prior scope, source, timeframe, management and holdout mistakes. Existing candle-close-cycle-labels and lc-levels-hold cards cover related follow-ups; attach this audit to their refinement rather than creating competing runs.

## Recurring mistakes, and what is newly exposed

| Failure pattern | Previous evidence | Current evidence / remaining action |
|---|---|---|
| Proxy substituted for intended setup | Wrong timeframe/horizon and generic exits in trader-transfer audits | Fixed third-bar close at prior-period levels does not cover developing pivot sequences. Register exact scope before coding. |
| Operational label treated as market fact | Choppy labelled ranging; generic regimes used for sourced setups | Improved 20-bar structural rules remain OURS hypotheses. A 4h/1h phase is not a daily/weekly macro regime. |
| Green tests treated as comprehensive proof | Import failure hidden by skipped tests; source fidelity unresolved despite passing tests | Thirteen executed tests are a positive repair; final raw-data/controls/inference verification must match revised code and output hashes. |
| Comparison changes the question | All nearby closes versus first signals | Matching decision-close distance is useful for incremental shape information after displacement, but can condition away part of the breakout's total effect. State the estimand; use separate comparisons for level skill and whole sequence. |
| Timing and sampling definitions drift | Live timing differs from research; availability fields absent | engine.py groups first hits by **bar-close day** (line 166), while PRE_REG says encounter-open UTC day. A 23:59–00:00 1m candle demonstrates the discrepancy. Impact on outcomes has not been measured; owner should adjudicate, test midnight fixtures and log any repair. |
| More cells substituted for more information | Rare daily events and macro underpower | 1,810/2,016 cells below 100 matched observations. Many cells are inconclusive; a zero-survivor screen does not reject all phase-specific reversal hypotheses. |
| Reused data treated as fresh validation | Contaminated holdouts and repeated DEV searches | Corrected DEV, added bounce arm and estimator repairs remain one inspected lineage. Preserve versions, count trials and audit clean validation eligibility. |

Further scope gaps: only the first encounter per day is kept; repeat tests and late confirmations are not followed as sequences. Rejection/retest check a wick crossing the line, not a full wick-length distribution. Strong break uses body and close-location thresholds, but there is no explicit approach speed/deceleration measurement. OHLC cannot establish intrabar path, absorption, aggressor flow or why traders bought. Multiple side rows, shared episodes and reused donors are not independent information; seven-day blocks are an assumption whose adequacy is horizon-dependent.

## How support/resistance must exist during replay

Completed parent highs/lows are causal candidate levels: engine.py aggregates completed 4h/day/week periods and aligns them to trigger **open** timestamps. Each encountered value is frozen. That establishes availability, not predictive strength. A previous low may fail, flip roles or cease to matter.

For a swing pivot at bar j whose definition needs two later bars, available_at is the close of j+2. It cannot be used at j. This exact delay is already specified in CYCLE_DESIGN. Future-confirmed extrema may label outcomes, but cannot create earlier input levels or move an alert back onto the eventual low. Support is a pre-existing candidate; a bottom is a later outcome.

Reuse existing level implementations after parity checks. Maintain a level ledger containing origin, source timeframe, price/zone, formed_at, available_at, as-of touch history, age, role, invalidation and algorithm/source version. Overlapping levels should retain provenance and be deduplicated for episode counting. Test level families separately before claiming a strength score. Historical reactions, separated tests, age, higher-timeframe origin and confluence are candidate features, not proven monotonic strength rules; repeated tests can also precede failure. Weights and thresholds require sourced definitions or explicit research-hypothesis status and prospective validation.

Every past level, phase and alert must remain unchanged when data after that decision is removed or perturbed. Include parent-boundary, midnight, missing-bar, tie-pivot and later-extreme fixtures. The present truncation test and timestamp-seeded placebo fix are useful foundations.

## Focused web research — verified 2026-10-14

Method: METHOD.md was saved before searching. Practitioner probabilities and promotional performance assertions are excluded. No external source below validates a BTC trading rule.

| Primary source | Tier / quality / confidence | Permitted conclusion |
|---|---|---|
| Carol Osler, *Support for Resistance: Technical Analysis and Intraday Exchange Rates*, NY Fed Economic Policy Review 6(2), July 2000, pp.53–68. [Official article](https://www.newyorkfed.org/research/epr/00v06n2/0007osle.html), abstract inspected | T1; externally provided levels from six FX firms; abstract only, execution costs/OOS not assessed here; H for reported finding, L for BTC transfer | Published levels predicted intraday interruptions with variation by firm/currency. Supports testing levels defined before encounters, not assuming every historical high/low is effective. |
| Carol L. Osler, *Currency Orders and Exchange-Rate Dynamics: Explaining the Success of Technical Analysis*, NY Fed Staff Report 125, April 2001; published Journal of Finance 58(5), 2003, pp.1791–1819. [Official report](https://www.newyorkfed.org/research/staff_reports/sr125.html) | T1; bank order study, abstract only; no BTC/costed-OOS claim; H for mechanism report, L for transfer | Take-profit/stop-loss clustering offers a mechanism for reversal at levels and acceleration through them. OHLC wick geometry cannot verify that mechanism. |
| DeMARK Analytics, *Sequential*, undated official documentation. [Definition](https://demark.com/sequential-indicator/) | T3 definition only; no disclosed costed BTC OOS experiment; H for count definition, predictive confidence unestablished | Setup counts nine consecutive close comparisons against four bars earlier; Countdown has thirteen qualifying, nonconsecutive comparisons against two bars earlier. Deferral, recycling and cancellation matter. Numbers are conditional counts, not arbitrary candle positions. |
| Al Brooks, official *Price Action Trading Glossary*, undated. [Glossary](https://www.brookstradingcourse.com/price-action-trading-terms-glossary/) | T3 definition only; no validated BTC probabilities; H for glossary meaning | H1/H2 and L1/L2 count attempts within pullbacks/range context, not simply the first and second elapsed candle. |
| Al Brooks, *Coaching Session #3: Major Trend Reversals*, dated August 14 in a 2025-hosted slide deck. [Original slides](https://www.brookstradingcourse.com/wp-content/uploads/2025/08/250830-Coaching-Session-3-MTRs.pdf) | T3; chart teaching examples, no audited sample/costed OOS; M for operational completeness | Describes break of prior trend, test near its extreme and another reversal with a signal. Useful sequence hypothesis; advertised probabilities are not adopted. |

The remembered candles 3/5/7 do not uniquely identify a trader or system. DeMARK and Brooks are possibilities, not identification. NR7 in the prior pilot is a narrowest-range lookback definition, also distinct from an ordinal entry candle. Do not implement a guessed numbered strategy. No validated BTC pivot-conditioned, costed out-of-sample edge was established by this focused search.

Unusable lead recorded once: *Trend definition or holding strategy: What determines the profitability of candlestick charting?*, publisher URL S0378426615002678 returned an access error. Not relied on.

## Concrete next work

1. Owning rerun session finishes revised independent checks, resolves/logs the midnight discrepancy, freezes an output receipt and delivers it. Keep prior failed analyses. Do not launch another same-scope run in parallel.
2. Refine existing cycle-labels/levels cards using this audit and CYCLE_DESIGN. Freeze separate level-timeframe, trigger-timeframe, phase-timeframe and outcome-horizon fields. Start with local/swing scope; retain macro as underpowered case/forward collection.
3. Build an as-of level and **all-encounter sequence ledger**. Record approach, sweep/wick, reclaim, failed attempts, retest/higher-low, structure break and follow-through at their actual availability times. Measure wick/body fractions, ATR-normalized displacement per unit time, overlap and confirmation lag as continuous observations before inventing thresholds.
4. Compare level-only, level+shape and level+sequence on common episodes. Include nonpivots and failures so both precision and missed pivots/recall are visible. Separate outcome labels from predictor features. Freeze the reduced hypothesis family, controls, clustered inference, censoring and cost conventions before outcomes.
5. Audit data lineage and validate once on genuinely unseen chronological data; purge/embargo overlapping label windows. Probability forecasts require training-fold-only fitting and calibration/Brier/log-loss checks. More historical minutes do not create more independent macro cycles.

This audit closes the diagnosis/research task; it does not claim the sequence implementation or new profitability test is complete. No strategy, live process or holdout was changed.
