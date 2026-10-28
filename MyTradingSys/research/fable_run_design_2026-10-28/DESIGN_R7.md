# Fable run design R7, 2026-10-28 (Lead, Opus, login C): FORWARD TEST DESIGN

**Goal (one sentence):** make every testnet day from now on count as fresh out-of-sample data for the R6 frozen rule (Krown S8 4h), by designing a forward test the live path runs exactly as pre-registered, frozen before the E2 DEV outcome is known.

**Honest limit (Lab_Guy recount):** at 0.33 signal days per calendar day a forward read reaches 439 days in about 44 months at best, so the forward test is a live-cost and parity check plus slow confirmation, never the near-term verdict; E2 on DEV and the one VALIDATION read stay the decision. R7 must state this in its Result.

**Why this is the next Fable run:** R1's STOP list says new backtests on trader sources stop "until new data exists"; R6 shows the edge question now hangs on one family with a 3-23 % power margin (`opus_run_design_2026-10-28/R6_LIVE_READ.md`). New data only comes from time. Today testnet produces none that counts: live exits are a fixed 1 %/2 %/8-bar bracket no backtest used (`R3_LIVE_REDTEAM.md` F-T09-2, T09), and 27 grandfathered sources trade unvalidated (`fable-run5-grandfather-decision`). Fixing that is a design judgement over many files (pre-reg, live executor, bracket config, stats of a slow-filling forward sample), which is Fable work; the build after it is Sonnet.

## Candidates
| Candidate | Value | Cost | Verdict |
|---|---|---|---|
| **R7 forward test design (this)** | Turns idle testnet time into the only new OOS data; independent of the E2 result | ~35 turns, ~3 pts | **RUN after R6 ships** |
| fable-run5 grandfather decision | KEEP/SHADOW/DROP for 27 sources; R7 decides what one source must look like, run5 then sorts the rest | ~30 turns | after R7 |
| R5 live-validation protocol | detector checks; not profit | ~25 turns | later |
| R6 review | needs an independent model: Opus O2, not Fable | - | Opus |

## Inputs
1. `research/fable_run6_powered_prereg/PRE_REG.md` (frozen rule, cells, cost, fills), `COUNTS.csv`; `opus_run_design_2026-10-28/R6_LIVE_READ.md`.
2. `research/fable_runs_2026-10-28/R3_LIVE_REDTEAM.md` (F-GAP-1, F-T09-2/3, F-BLK), `research/layer_lab/reports/*t09*` (live parity).
3. Live path, read only: `execution/auto_trader.py`, `execution/auto_trader_config.json` (bracket, `trade_blocklist`), `execution/executor.py`, `execution/position_manager.py`, `execution/mainnet_plan_check.py`.
4. `research/sim_desk/studies/krown.py`, `_bars.py` (event code the live path must reuse unchanged); `backtest/fees.py:27-28`; FORMULAS.md fees; `backtest/power_mde.py`.
5. `system/MOVED_RULES.md` (live-path test rule), `DEPLOY_RUNBOOK.md` (builders never deploy).

## Output
`research/fable_run7_forward_test/FORWARD_PREREG.md` (max 3 pages):
1. Parity spec: the live event = `krown.py` S8 on closed 4h bars, same stop/target/time stop/fees as PRE_REG item 6-8; a replay test that feeds cached 4h klines through the live decision code and must reproduce R6's event list exactly (0 mismatches), written as a failing test spec.
2. Forward sample rule: start date = first deploy after the build card ships; unit = UTC day; expected trade days per month from COUNTS.csv: signal-day rate 539 / 1,643 = 0.33 per calendar day before the busy rule (0.49/day is the event rate, `PRE_REG.md` item 3; never use it for days), so 439 days is about 44 months at best; months to reach 439 days and to reach the MDE at t >= 2.0 (formula SOURCED, numbers OURS); interim looks: none, or a stated alpha-spending rule.
3. Pass/fail rule fixed now, read on testnet fills only (testnet fill quality vs taker+slip model stated as a check, not a verdict input).
4. Isolation: S8 forward trades tagged and never mixed with other testnet layers; what the other 27 sources may keep doing (calibration only, never evidence).
5. Cards (twins first): build (SONNET, live path: test for restart, non-trade balance moves, API errors), replay parity test (SONNET), F-GAP-1 as a hard dependency of the build (already carded), monthly forward readout (SONNET, run-and-report). `tasks.py check`; revert any other card it rewrites.
6. USAGE.md R7 rows.

## Stop conditions
Weekly Fable +4 pts, 5 h window 85 %, 45 turns, context 60 %. Any read of a bar >= 2024-07-01 or any outcome column: STOP. No live-tree edit, no deploy, no process touch, testnet only.

## Estimate (OURS)
~35 turns, 45-60 min, ~3 Fable pts (R6 cost on record in USAGE.md when it ships).

## Waste if
It changes the R6 rule (frozen); it reads E2 or VALIDATION outcomes; it designs a forward test the live path cannot run without a new layer framework; it promotes anything to mainnet.

## Done when
`git cherry origin/fast-track` empty; on trunk `research/fable_run7_forward_test/FORWARD_PREREG.md` with the 5 parts; >= 3 new cards naming it; commit body `Result:` = months to a powered forward read + parity rule.

Parity is pinned to the PRE_REG.md commit R7 read (named in FORWARD_PREREG.md); if O2 REJECTs and the rule changes, R7 is re-run.
DECISION (OURS): R7 runs after R6 ships but does not wait for O2 or E2; if O2 changes R6's m, R7's power months change, not its design, and R7 states both.
