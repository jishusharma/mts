# Planted-error trial: machine layer

Verdict: MACHINE-ONLY; 6 clean cards available (not 10), generating 8 shadows round-robin per `codex-unstick-2026-10-23.md` decision. Stack rows remain for the coordinator.

| Error class | Caught | Missed | Cheap Haiku/Flash (tokens / effort) | Expensive Argon/GPT-high (tokens / effort) |
|---|---:|---:|---|---|
| deleted trial rows | 1 | 0 |  |  |
| edited gate constant | 0 | 1 |  |  |
| expected value copied from code | 0 | 1 |  |  |
| holdout leak | 0 | 1 |  |  |
| mislabelled SOURCED number | 0 | 1 |  |  |
| one-bar shift | 0 | 1 |  |  |
| wrong data copy | 0 | 1 |  |  |
| zero slippage | 0 | 1 |  |  |

| Shadow | Card | Class | Result | Rejecting checks |
|---:|---|---|---|---|
| 1 | context-factors-v3-crossvendor-review | wrong data copy | MISSED | none |
| 2 | gptb-bb-top-reversal-event-table | one-bar shift | MISSED | none |
| 3 | gptb-funding-extreme-event-table | holdout leak | MISSED | none |
| 4 | krown-catalogue-gpt-audit | expected value copied from code | MISSED | none |
| 5 | gptb-session-levels-event-table | deleted trial rows | CAUGHT | tasks.trial_ledger_runs_count |
| 6 | lab-audit-tom-ledger-frames | zero slippage | MISSED | none |
| 7 | context-factors-v3-crossvendor-review | edited gate constant | MISSED | none |
| 8 | gptb-bb-top-reversal-event-table | mislabelled SOURCED number | MISSED | none |

Missed-shadow packets are in each numbered planted folder (`MyTradingSys/research/lab_guy/planted/<n>/`). Prose-only semantic errors are outside machine-check visibility; model desk rows should report their tokens and effort.
