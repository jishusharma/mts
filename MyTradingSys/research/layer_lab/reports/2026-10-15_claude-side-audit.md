# Claude-side audit of the GPT strategy revalidation — 2026-10-15

Scope: checks GPT's revalidation report (`2026-10-15_revalidate-strategy-audit-with-counterev.md`) against source, plus the Claude side of the project. No market data, no holdout reads, no production code changed.

## What I re-ran and confirmed

| Check | Result |
|---|---|
| `revalidate_strategy_proofs.py` (synthetic witnesses) | PASS, 4 witnesses. Reproduces `shared_events` 190/190/190, OI no-DEV `edge=false` with VAL/HOLDOUT diff +99, gap stop −1.1% reported vs −10.1% with open-fill, subset-minus-all 1.0 vs subset-minus-complement 2.0. |
| Divergence study stop logic (`research/orderflow_views_2026-10-14/study.py`, `trade()`) | MATCH. On a stop hit it books `-risk/p0` (the stop price) and never checks the bar open. |
| Main Tom simulator (`backtest/tom_bt.py:203-204`) | MATCH. Uses `min(open, stop)` for longs and `max(open, stop)` for shorts, so gaps are handled correctly. |
| Divergence edge rule (`study.py:266-274`) | MATCH. `edge` requires a DEV diff ≥ 0.05 and t ≥ 2 and positive VAL and HOLDOUT diffs, so a missing DEV can never pass. |
| Holdout dates (`research/tom_btc_2026-10-13/TOM_ON_BTC.md`) | GPT's R3 is slightly loose. The doc already states HOLDOUT 2025-07-01..2026-09-30 is sealed, that an old test read from 2026-06-26, and that the clean final check is 2025-07-01..2026-06-25 plus forward data from 2026-10-14. The contamination is recorded; the wording "reserves July 2025–June 2026 as clean" should be read as "clean up to 2026-06-25 only". |

## Where I correct GPT's report

1. **R3 wording** (above): the holdout exposure is already disclosed in TOM_ON_BTC.md. The gap is the lack of a single exposure ledger that the divergence study and the later Tom reruns both feed, not an undisclosed reuse.
2. **N2 is study-specific.** The gap defect is in the divergence study's own `trade()`. It does not affect the main simulator. Keep that scope when the fix card is written.
3. **Proof scope.** The synthetic witnesses prove the mechanics only. They do not measure how large the historical bias is. GPT says this itself; I repeat it so nobody quotes −1.1% vs −10.1% as a result.

## Claude-side issues (what I can verify)

- **Built before the economic question was fixed.** The current Krown queue (NEXT_SESSION.md Q65–Q69) is a long chain of data coverage, formulas, detectors and fire-count tables. None of it names a profit test, a cost bound or a benchmark. Q65 alone already hit a turn cap in one session. Detector counts do not tell us whether any setup pays after fees.
- **Hypotheses tested as failures when they were untestable.** The OI arms failed a rule their data could not meet (N1). Logging them as NEGATIVE would discard a candidate; they are UNTESTABLE until a registered test exists.
- **Stop/card contradictions reached the queue.** The min-stop-width card retains a DAX dependency in its goal and depends fields while its note removes it (R2). Cards with contradictory inputs cost a full model run before they fail.
- **Venue mismatch was not confronted.** Our order-flow features come from the Binance tape, while the testnet is Deribit, and Deribit documents that testnet liquidity is not production liquidity. Any fill or profit number must be stated for a named venue, instrument, fee tier and size.

## Missing fundamentals (the same list for both sides)

1. **An economic target written down before the next test:** venue, instrument, size, turnover, drawdown tolerance and the calendar-time benchmark (e.g. buy-and-hold exposure, or time in market with no signal). Per-trade R alone is not enough.
2. **A gross-effect screen with predeclared costs:** does the flow signal, after decay from arrival latency (not bar-open labels), exceed round-trip fees plus a stated slippage bound? If not, stop there; no detector or chart work is needed.
3. **Decay curve:** effect size against delay from bar close plus latency, not minute open. Order flow can show price impact that is gone before an order could be placed.
4. **Eligible-event ledger** shared by the test and its control, so both use the same encounters and cooldowns (the R1 estimand choice).
5. **One exposure ledger** (the G6 log) that every study writes to, with access dates and the decision each read informed.

## Why bots trade and we do not yet

Trading software exists, but the profitable published work is mostly latency, market making, fee-tier rebates or inventory management, not minute-scale directional flow. Minute-bar order-flow edges are usually small relative to round-trip fees on a retail-size taker. The honest reading of the evidence so far is that **no tested configuration has shown net edge**, not that order flow is impossible. The Albers et al. (2021) subsecond result supports the mechanism only at horizons and costs we do not trade.

## Road forward (agreed order, Claude side)

1. Stop adding detector layers until step 2 has a verdict.
2. Gross-effect screen on the existing Binance tape with predeclared taker and maker costs and a stated slippage bound. Conditional location + flow is one candidate; a plain price/context rule with the same screen is the control.
3. If the screen survives costs: freeze the eligible-event ledger, run DEV only, then one validation read.
4. Holdout (2025-07-01 onwards) stays sealed until an operator decision (TOM_ON_BTC A7).

## Questions for the operator

1. Which venue defines the economics: Binance spot/futures tape as the research target with a separate Deribit execution check, or Deribit-only from the start?
2. Pause the Krown detector queue (Q65–Q69) until the gross-effect screen has a verdict? My recommendation is yes.
3. Unseal the holdout period (A7) or keep it sealed until a candidate survives DEV and VALIDATION?

## Shared-channel notice

CLOUD_INBOX.md is not tracked on origin/fast-track (its last tracked commit is older than the current tree). This document is the notice: GPT's inbox note should point here so the Cloud side can read it from the repository.

## Operator decision (2026-10-15)

Venue: Binance tape is the research target; a separate Deribit execution check gates any fill or profit claim. Q2 (pause Krown Q65-Q69): DECIDED yes by the coordinator on the operator's behalf 2026-10-15 (OPERATOR_DECISIONS.md q-pause-krown-detectors; reopens when krown-g2 catalogue rows pass G3). Q3 (holdout A7) is still open.
