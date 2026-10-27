# D7. Roadmap to v1 (stages, entry and exit, what is frozen)

Dates are EXPECT lines (planning). Each stage ends on a measured exit, not a date. One stage at a time; a stage does not
start while the previous exit is unmet. The coordinator (SUPER_SESSION.md) runs each stage; the operator signs the exits
marked (sign).

## Frozen for the whole v1 (until the operator unfreezes)
New layers or analyst sources; new vendors, logins or lanes; new pages; new rule documents (edits to existing ones only to
shorten); any mainnet step; confluence between layers; the options folder beyond its own plan.

## Stages
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
