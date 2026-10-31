# D7. Roadmap to v1 (stages, entry and exit, what is frozen)

Dates are EXPECT lines (planning). Each stage ends on a measured exit, not a date. One stage at a time; a stage does not
start while the previous exit is unmet. The coordinator (SUPER_SESSION.md) runs each stage; the operator signs the exits
marked (sign).

## Frozen for the whole v1 (until the operator unfreezes)
New layers or analyst sources; new vendors, logins or lanes; new pages; new rule documents (edits to existing ones only to
shorten); any mainnet step; confluence between layers; the options folder beyond its own plan.

## Stages
Now: S0 (operator 2026-10-30, d-simplify-align-s0; MTS Home reads this line, move it when an exit is signed)

| Stage | Entry | Work | Exit (measured) | EXPECT |
|---|---|---|---|---|
| S0 Freeze and clean | operator answers q-v1-freeze | ship the unjam branch (review per rule 11); apply D1: release 3 stale claims, retire worktrees after one ship each, close/park cards, BUGS stage-tag pass, GAP-5 reconcile; decide the 22 Windows tasks (q-v1-keepers) and the CBP routine (q-v1-cbp-routine); 2026-10-23 config review (q-v1-config-1023) | ready cards <= 15, claims <= 4 and 0 stale, worktrees <= 8, bookkeeping share of trunk commits < 30 % on STATUS.md, traffic.py jam exits 0 on JIS-NB, no scheduled task outside the keeper list | now to 2026-10-27 |
| S1 Spec signed | S0 exit | operator reads D2 and D3, answers q-v1-bar and q-v1-layers; Signal v1 schema written as the one schema (cbp_contract_v1 promoted); seam test (D6) | D2 marked signed in OPERATOR_DECISIONS.md; GO_LIVE_BAR.md revision block in; schema + seam test green on CI (sign) | 2026-10-27 to 10-29 |
| S2 Platform hardening | S1 exit | bar items M1-M4: state-code backfill (GAP-2), L6/B149 settlement, gap-g7 stop parity, uptime heartbeat on JIS-NB; restart/reset/balance/API-error tests per live file; fail-closed everywhere | all four cards done with tests that failed on old code; 14 days of heartbeat >= 95 % on JIS-NB; one HALT drill and one restart drill with EXPECT written before, RESULT after (sign) | 2026-10-29 to 11-14 |
| S3 Two-layer funnel | S1 exit (runs in parallel with S2; different files) | LC3 ladder DEV, LC4 validation; CryptoCred 4h/1d DEV card then one VALIDATION read; DSA audits T06 and T09 on a Claude or Codex lane so numbers can be trusted; WIP = 2 enforced | one config passes VALIDATION fee-net with lower CI > 0 and enters promoted_setups.json; or both FAIL and the next two in line enter (Tom v2, RSI deep-buy) and S3 repeats | first pass or fail by 2026-11-14 |
| S4 CBP module | S1 exit (parallel; CBP repo + queue files only) | D5: producer-side schema and quote gates, golden-set harness, coordinator-run pipeline, consumer end to end | one real analyst row producer -> queue -> consumer -> CANDIDATE_UNTESTED with ack; harness green on CI; no routine outside the dispatcher | by 2026-11-14 |
| S5 Testnet to the bar | S2 exit and at least one promoted config | the promoted config(s) trade on testnet; daily bar read from trade_ledger.jsonl; the operator's decision page gets one line per week | the revised bar (D3) holds over its rolling window (sign) | 30-60 days from the first promoted config |
| S6 Mainnet decision | S5 exit | the operator decides mainnet at tiny fixed size with an experiment stop (M7); repo goes private first (CLAUDE.md); keys handled by the operator only | signed decision; builders still never touch keys or enable mainnet | operator's call |
| v2 | S6 running | options via D6 seams (OPTIONS_PLAN P0-P5), then other markets | separate spec | after v1 |

## S3 run list (the one list of backtests still to run; operator 2026-10-31, d-s3-run-list)
Rechecks already done, so these are not on the list: re-running 10 published verdicts on today's code (T07: 8 identical, mfe_exit fixed
ad4e461d6, published_strats has no data here; no verdict flipped); the LC1 keep list against a fair control (0 of 12 keep); Q33 confluence
(0 of 186); Tom VP (10 of 12 desk runs FAILED); tf_break 15m (FAIL); Setup Alpha/Beta (FAIL / all cells negative); Krown S8 E2
(INCONCLUSIVE; a forward read needs about 72 months, so Fable run 7 is on hold). A failed test comes back only with a new reason written on
its card.

| # | Test | Card (state 2026-10-31) | Data | Why it is on the list |
|---|---|---|---|---|
| 1 | Meta-label 1h break lead, frozen model scored on 2020-2021 | meta-label-1h-dev-ext-check (raw) | `F:/MTS/Dumps/backtest/raw_1m_2019` (BTCUSDT 1m 2020-01..2021-12) | nearest miss on DEV (best third +0.063 %, Holm p 0.060); fresh years cost no sealed read |
| 2 | Meta-label Fabio Model C stand-in on 2020-2021 | meta-label-fabio-c-dev-ext-power (ready) | same | NOT ENOUGH DATA on DEV (2.7x underpowered) |
| 3 | LC4 Levels Confluence: frozen rule, one VALIDATION read | lc-validation (refined, HOLD A-20261018-5 until its base carries a trust tag) | VALIDATION 2025-04..06 | the only frozen rule waiting for its read; check it against the LC1 0-of-12 restatement first |
| 4 | CryptoCred 4h/1D on DEV, then one VALIDATION read | cryptocred-4h-1d-dev-s3 (raw, filed with this list) | DEV + funding (`Dumps/backtest/raw/fundingRate`) | named in S3 since 10-20 but had no card |
| 5 | RSI deep-buy: pre-reg, engine, DEV grid | rsi-deep-prereg, rsi-deep-engine(-ladders, -exits), rsi-deep-run-dev (refined) | DEV | S3 next in line |
| 6 | Tom v2: a variant that passes GROSS first (near-band placebo on 2020-2021, SETUP_REVIEW.md section 6 test 2) | tom-v2-gross-first-dev-ext (raw, filed with this list) | 2020-2021 | S3 next in line; Tom VP net -0.20..-0.26 R, so no filter can rescue it |
| 7 | Reclaim at the video's timing (enter at the reclaim close, stop on a close back below) | follow-reclaim-daily-close-stop (raw) | DEV | the one untested piece of the Brando price-action note |

Order: 1 and 2 first (cheap, no sealed read), then 3, then 4-6 under WIP = 2; 7 only if a slot is free.
Every run: rules frozen in PRE_REG.md before any result; fee-net (taker both legs, funding where a hold crosses a stamp); Holm over the
family with m written first; label-shuffle placebo; contiguous-block CV; same sign 2022 vs 2023-24H1; one VALIDATION read per setup,
HOLDOUT never; new ideas test on 2020-2021 before DEV/VALIDATION; one TRIALS.md row per setting; results exported to
`sim_desk/results/<id>.json`. A pass enters `execution/promoted_setups.json` (empty today), and S5 testnet can then start.

## Order and why
S0 first because every later stage ships through the gate the jam blocked, and a frozen list is the only list that can
shrink. S1 is short and is the operator's: without a signed spec, S2-S4 build to a moving target. S2, S3 and S4 run in
parallel because they touch disjoint files (live path; backtest layers; CBP repo and queue) and use different lanes. S5 cannot
start before S2 because trades taken on a wrong CVD are not evidence. S6 is a decision, not work.

## Capacity rule (Brooks)
Three parallel stages, three worker sessions at most, one coordinator. Adding a fourth lane goes to a stage that has a
measured bottleneck, never to start something new. The fixed cost per turn (70-80k tokens, SUPER_SESSION.md) means
fewer, longer sessions beat many short ones once S0 has cut the boot context.

## Weekly read (what the operator sees)
One line per stage on the decision page: stage, exit metric, today's number, blocked-on. Nothing else grows.
