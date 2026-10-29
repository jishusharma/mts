# Critical test plan (business rules only)

Operator ask 2026-10-30: find the critical bugs hiding in the Java engine and anywhere business rules live; two kinds of bug, a rule misunderstood and a rule implemented wrong; reviewed by different models; record every test plan and how much was tested; never duplicate past work.

Scope is narrow on purpose: only places where a wrong rule costs money (orders, risk) or truth (what fires, what we believe an edge is). Everything else stays with CI and the existing gates.

## How every check runs

1. **Before starting:** search `TEST_LEDGER.md` and `research/audit_inventory` (the past audits table). If the same question was already answered on the same code, cite it and skip it.
2. **Two questions per rule:**
   - U (understood?): does the spec match the source (the trader's words, the exchange docs)? Check by a fresh read of the source, never of our spec.
   - I (implemented?): does the code match the spec? Check by a hand-computed example (`backtest/layers/FORMULAS.md` style) and a test that fails on a mutated copy of the code.
3. **Different eyes:** the reviewer gets the code and the source, never our conclusion. Each item gets at least one reviewer from another model family (Gemini on NUC, GPT/Codex when the lane is up, DSA), plus the author model. A disagreement is a finding.
4. **Result goes in the ledger the same turn:** PASS, FINDING (with severity), or UNTESTABLE (why). A FINDING files a card.

## Critical areas, ranked

| # | Area | Why it is critical | Files | Question to answer |
|---|---|---|---|---|
| T1 | Order and risk path | Money on testnet now, mainnet next | `execution/risk_guard.py`, `daily_loss_guard.py`, `kill_switch.py`, `trade_plan_validator.py`, `position_manager.py`, `reconciler.py`, `orphan_watchdog.py`, `auto_trader.py` | Every order has a stop; size never exceeds the cap; every safety check fails closed on an API error, a restart, a stale file or a non-trade balance move |
| T2 | What fires (Java signal path + launcher flags) | The operator cannot see what fires; 10-30 found Tom's fade coded but switched off and Pitchfork switched on | `SetupCandidatesBuilder.java`, `StateCodeEmitter.java`, `SpikeFade*.java`, `PitchforkSignalLayer.java`, `NetRrFloor.java`, `ExecutionMathConstants.java`, `scripts/core/start-trading-day.ps1` | For a given snapshot, which candidate wins, why, and can it reach an order? Is every on/off switch in live what was decided? |
| T3 | Rules vs the trader's words | A rule we misunderstood is a bug even if the code is perfect | Tom (A-C/A-P/A-T), Krown (KR-L10 and others), Malkan, Habib, Fabio specs | Fresh read of the source per rule; 10-30 found our KR-L10 does not see the operator's "last lower high" line |
| T4 | Fees and money maths | A wrong fee or R:R makes a losing rule look fine | `NetRrFloor.java`, `ExecutionMathConstants.java`, `costs.csv` | Hand-computed net R:R on 3 cases matches the code on both Java and Python sides |
| T5 | Data truth | Every layer reads these | OI, CVD, net delta, taker delta, klines (archive and live) | Units and anchors match the exchange docs; live and archive give the same value for the same minute |
| T6 | Alerts reach the screen | A firing nobody sees is a silent failure | alert path, popups, dashboard | Every candidate and order produces exactly one visible alert on desktop and laptop |
| T7 | New probability panel | Numbers the operator will trade on | anticipation card | Base rates recomputed by a second model from raw data before display |

## First wave (narrow, about 5 items)

1. T2: flag census. List every on/off switch the live launcher sets, against the decision that set it (spikeFade OFF, pitchfork ON found 10-30).
2. T1: fail-closed census. For each guard in T1, one test each for an API error, a restart and a stale file. Reuse the existing tests, add only the missing ones.
3. T4: net R:R hand cases, Java vs Python parity.
4. T3: KR-L10 vs the operator's lower-high definition and Krown's own words (card `krown-views-via-gemini-what-krown-says-a`).
5. T2: replay of 10-29 through the engine (offline): what would have fired, with all switches as in live and with spikeFade on.

The wave is filled in after the past-audit inventory, so items already covered are dropped, not redone.
