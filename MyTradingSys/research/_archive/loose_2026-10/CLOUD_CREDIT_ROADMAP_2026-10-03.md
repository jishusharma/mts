# CLOUD CREDIT ROADMAP 2026-10-03 (awgp account, ~$100, expires 2026-11-05; header corrected 2026-10-04)

Author: App session, operator request 2026-10-03. Status: PROPOSED, nothing launched.

## 1. Split (no duplicated work)
Rule: the account is not the boundary, the file set is. Local owns what needs disk, live processes or PowerShell;
Cloud (awgp) owns offline work on pushed refs. Each Cloud session claims its file set in CLOUD_INBOX.md before starting.

| Lane | Account | Owns | Never touches |
|---|---|---|---|
| LOCAL (desktop App/CLI) | main | B086/B087 dispatcher fix (pasted prompt), live path, execution/, layers/alerts/, promote .new, gates, commits to fast-track, SUPERVISOR_LOG | - |
| CLOUD (awgp) | awgp collaborator | offline analysis, specs, fail-first fixes outside execution/ and layers/alerts/, backtests on committed data, reviews | gitignored files, live trees, restarts, HALT |

Pre-flight (operator, 2 min): push fast-track (CLAUDE.md bars me from pushing). Cloud sees only pushed refs.
Each Cloud session works on cloud/2026-10-03-<slug>; local reviews, gates and merges. Cap 3 subagents per session,
commit and push between batches (Ultracode incident 2026-10-02).

## 2. Cloud queue, in value order (goal: first real trades)
| # | Slug | Task | Done when | Est $ |
|---|---|---|---|---|
| C1 | audit-reconcile | Matrix of every audit finding (REVALIDATION_ACTIONS, TWO_CORES_READINESS F7-F12, MAINTAINER reports, W3 kappa) -> bug id -> code line -> test -> IMPLEMENTED/PARTIAL/NOT. Answers "what was implemented from the audits". Read-only | AUDIT_RECONCILE_2026-10-03.md, every row cites file:line | 8 |
| C2 | no-trade-funnel | Gate funnel on committed runtime data: candidates -> each rejecting gate -> counts; names the top 3 blockers of trades. Parse real formats, count, no truncation | FUNNEL report plus the script that reproduces it | 10 |
| C3 | w1-review | Finish TWO_CORES handoff tasks 1: review staged W1 .new files (book_imbalance 0.0 first, B084), fail-first, overlay gate | TWO_CORES_FIX_PASS doc with failing run; checkpoint commit | 12 |
| C4 | fabio-v3 | Finish W2: models, engine, __init__, tests, README; pending_test_fabio_v3.py T01-T64 passes with import change only | checkpoint 2 commit | 15 |
| C5 | bug-batch | Fail-first fixes B072, B073, B074, B076 (plus B085 analysis), each small, outside owned dirs | one .new or commit per bug, tests named | 12 |
| C6 | backtest-dsr | Registered backtest on committed data, TRIAL_REGISTRY.csv created, DSR with stated N lower bound; T051 resume condition check | report plus registry file | 12 |
| C7 | research-pack | T054, T055, T058, T060, T061 one Sonnet worker each, playbook Part I citations, provenance rule | one report per item, verified quotes | 15 |
| C8 | second-reader | Adversarial review of the B086/B087 diff once LOCAL commits it; second reader for the highest-risk W1 diffs | review file, findings only | 6 |
Reserve $10. C1-C3 run first (they decide what C4-C7 should target); C4-C7 can run as two parallel sessions.

## 3. Local lane today
1. Run the pasted fix-dispatcher prompt (needs repo disk and `mts go`): LOCAL, Sonnet, Ultracode off.
2. Push fast-track, append the C-rows to CLOUD_INBOX.md, launch C1-C3 from the awgp App in Cloud mode.
3. Merge returned branches after gating (run_all_tests.py --quick, Build-Check.ps1). Promote any .new files.

## 4. Scheduler decision (machine is not 24/7)
Nothing live depends on Cloud. The NUC schedulers stay pull-based: on boot, tick.py picks the next QUEUED row.
Cloud work is launched by hand today because the credit expires; do not create routines.
