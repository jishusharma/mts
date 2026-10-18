# MTS state of play, 2026-10-15 (input brief for the Fable audit; every line is a CLAIM to verify, not a finding)

Written by a Sonnet session after reading: PROJECT_VISION.md, LAYERS.md, tom_dax_what_is_proven_2026-10-13/REPORT.md, TOM_ON_BTC.md (head), layer_lab/reports/2026-10-15_{claude-side-audit, tom-btc-event-study}.md, ledger heads. Numbers below are quoted from those files (second-hand unless marked); none re-derived.

## 1. The operator's question, restated
"Is there a real edge, what is the code actually capturing of Tom and Fabio, and where does the project sit?"

## 2. What "real edge" should mean (proposal, three separate questions the repo mixes)
- Q1 Fidelity: does our code fire where Tom/Fabio fire? Test: recall at their logged entries versus a random-clock baseline.
- Q2 Their edge: is the trader's discretionary method profitable on his own market? Needs his audited records. Repo holds none (backtest_gap_review REPORT.md:179-181).
- Q3 The premise MTS actually trades: does order flow (with or without Tom's rules) give a gross effect on BTC that exceeds round-trip fees plus slippage at executable latency? Needs no fidelity to Tom at all.
- Real edge, operational: a rule fixed before the test, whose fee-net expectancy at realistic latency and size has a CI above 0 on data not used to choose it, and beats a matched random or plain-price baseline, on a venue and size we can trade.

## 3. Is Tom/Fabio captured in the code? (the operator suspects not)
- Mostly no, by the repo's own audits. Old BTC engine: 4,417 trades, gross -0.07R, but it matched 0 of Tom's 7 real entries, so it measured "our caricature" (what_is_proven REPORT).
- New DAX detector: 2 of 5 Tom sessions matched, a random clock does that ~16% of the time; its order-flow proofs are NOT_IN_DATA (DAX CFD delta forced to 0, dax_data.py:100-106).
- Ground truth is thin: Tom ledger ~37 rows, 12 trade groups, 0 certified executions, mostly FDAX; Fabio ledger ~72 rows; Fabio v3 holdout FAIL, ledger audit FIX-FIRST (LAYERS.md).
- LAYERS.md marks tom_core "STOP: do not backtest or tune the current BTC encoding". Tom v2 on BTC is a plan (T1-T8), not built.

## 4. Where the project sits
- Operator pivoted 2026-10-13 from DAX to BTC (BTC carries real order flow; DAX feed lacked it) and dropped "Tom is core".
- Structural doubt written in the repo itself: Tom's stops (20-63 DAX points) are small; BTC fees force stops >= 0.40% (taker) or 0.20% (maker-in); costs 0.39-1.27R per trade vs his claimed 0-0.35R edge (TOM_LAYER_V2_SPEC s11, what_is_proven). Transfer to BTC may be uneconomic by arithmetic.
- Negative evidence: 62 published rule strategies none survive fees+placebo; MFE exit study no exit recovers fees; CVD divergence adds nothing over price on 1m/5m; ETH replication 0 of 9; VP anchors no better than placebo.
- Untested, not refuted: a Tom-faithful encoding on data with real order flow (the BTC T3-T7 chain). It is stuck: today's Codex event study (T4) is BLOCKED, no eye-read marks exist (T3 needs two blind readers incl. the operator) and A-P10 retail sentiment is NOT_IN_DATA.
- Effort: last 7 days ~1,650 commits on origin, dominated by relay/dispatcher, token-cost trimming, CI/worktree hygiene, pages, plus a Krown chain (Q65-Q69) that names no profit test. Few commits on the edge question.
- Open operator decisions: Q2 pause Krown, A7 holdout, Deribit parity read (default No).

## 5. What I think the Fable session must settle (my hypothesis, to be attacked)
1. Is Q3 testable first? CORRECTION (operator, 2026-10-15): "buy every CVD push" is NOT the hypothesis and not how Tom/Fabio trade; they act at a location (level, VP, session extreme) with flow as confirmation. An unconditional flow screen is only a weak floor/control: its failure does not refute the conditional method. The screen must be location + flow versus the same location without flow (plain-price control), with stop, target and entry taken from the trader's own stated rules (SOURCED: quote + file:line; do NOT substitute our stop/target sizes; where he states none, label OURS and report as a variant that cannot decide the verdict; if his stops are too small to survive BTC fees, that is the finding about his method on BTC, not a reason to change the stop) and the pass bar = round-trip fee / (stop + target) in win-rate points over the random-entry baseline. Order the work: Q3 conditional screen -> only then Q1 fidelity. Attack whether the location rules can be defined without Tom's eye-read marks.
2. If Q3 fails: what is left (maker strategies, other markets/fee tiers, discretionary-assist tooling instead of automation, stop)?
3. Verify rungs the above rests on: R2 simulator (re-derive 3 numbers), R3 sample 5 rules (quote vs code), R4 power of the "none survive" results.
Fable should say where this brief is wrong.
