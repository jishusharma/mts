# Claude handoff: Binance BTC backtesting foundations

User request, 2026-10-18: research how to research first; advanced reliable general/Binance BTC backtesting research; verified studies and failure modes; Sol 6.1 double-check; deliver findings and roadmap to Claude; commit changes. No further user input expected.

Read REPORT.md, then REVIEW.md. Source URLs, versions, access limits, study inputs/outcomes and implementation acceptance criteria are in REPORT.md. This is research/documentation only; no strategy verdict, trading parameter or runtime code is changed.

## Findings to act on

1. Preserve existing PBO/DSR and pre-registration work. The missing assurance is end-to-end use with a complete search history, causal data, justified costs and suitable uncertainty; adding another statistic alone does not solve it.
2. Binance spot archive timestamp units change at 2025-01-01; archives can be revised. Extend existing data-pin coverage with product/schema/unit and raw-checksum assertions. Source B1.
3. Perpetual accounting needs funding events, position size and event mark value, plus margin/liquidation paths. The entry-notional simplification is explicit at `MyTradingSys/backtest/layers/positioning/trade_costs.py:5`; quantify its error before making claims. The long/short worked example in FORMULAS section 13 is correct; do not file a sign bug.
4. `MyTradingSys/backtest/bt/bt_stats.py:15` uses IID resampling; check dependent/overlapping-trade callers. PBO at line 69 and DSR at line 65 already exist. Audit inputs and assumptions rather than duplicate them.
5. Reconcile `MyTradingSys/backtest/PRE_REG_TEMPLATE.md:16` (effect-size/MDE) with line 64 (N<100 shorthand). Remove the unsupported fixed-bracket lower-bound assertion at line 54: changed exits can improve or worsen returns.
6. `MyTradingSys/backtest/verdict.py:66` is a snapshot setup-status function, not an overall statistical promotion gate. Locate the actual promotion paths before asserting enforcement.
7. Do not transfer published historical BTC results, aggregate wash-trading percentages or a fixed cost schedule to today's Binance product. S6 is abstract-verified and BTC-negative OOS in its sample; S9 is a versioned preprint with material limitations, not validated alpha.
8. Sol found, and the parent independently reproduced, a power-helper mismatch: `backtest/power_mde.py` documents positive-edge detection (lower 95% CI >0), but sums both rejection tails. With p=0.5, RR=1, cost=0, N=100 it returns 0.05 instead of 0.025 for that criterion; with p=0.4 it returns 0.5324208639 instead of approximately 0.0000315103. These are normal-approximation synthetic checks, not market results. Open a separately scoped correction: the existing display-only G1 card explicitly excludes this helper.
9. Effective candidate count does not correct serial dependence in returns. Existing PSR/DSR lacks a long-run covariance adjustment; treat it as assumption-dependent until calibrated. Also audit the cost helper's fixed fee_rt against actual entry/exit notionals. S9 accrues carried-forward funding over bars, unlike settlement events; its fallback is not a verified conservative bound for both long and short positions.

## Roadmap and existing work

REPORT section 6 supplies the detailed DONE-when proofs. Order: P0 data/causality/accounting -> P1 fills/inference/policy wording -> P2 one frozen BTC pilot -> P3 forward reconciliation.

At inspected base cb007264, parsed task cards say:

| Card | Recorded state | Required reconciliation |
|---|---|---|
| lab-data-pin-hash | done | Check the receipt/code coverage; extend for timestamp/schema and exchange corrections, not a duplicate hashing build. |
| lab-holdout-access-control | done | Check stated DATA_ROOT-only coverage and review debt; a done card is not proof every harness is protected. |
| gap-g1-prereg-power | ready | Existing scope is display-only and preserves frozen verdicts. Any policy/template change needs a distinct scoped follow-up, not silent widening. |
| gap-g6-trial-ledger | ready | Existing scope builds a combined ledger. Human/LLM discarded experiments and complete holdout access may need a later extension. |
| dsa-audit-08-split-trials | ready | Reuse its split/contamination audit; do not independently consume holdouts. |

These are card-state observations, not rerun test results. Refresh trunk and claims before assigning work. The roadmap proposes follow-ups; it does not change existing frozen pass bars or reopen parked strategies.

## Required independent Claude follow-through

Spot-check B1 and B3 and the cited repository functions; reconcile Sol's review with this report. Refine the smallest nonduplicative CODEX tasks for the remaining controls, using REPORT section 6 as acceptance evidence. Confirm that any shared mathematical base has the required trust review before consumers use it. No mainnet execution, live-tree edits or new holdout reads are part of this handoff.

Delivery is through origin/fast-track and the Claude-GPT relay board. A posted note proves delivery to the shared queue, not that Claude has read or accepted it.
