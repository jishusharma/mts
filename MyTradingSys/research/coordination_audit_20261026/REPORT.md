# MTS task-flow audit — 26 October 2026

Audited revision: `ec00608e96a2249bb9fadf310ddd4199ecd3f6ef`. Scope: intake, dispatch, claims, worker context, runners, local ship, CI, completion and next-stage pickup. No production code changed. Findings below are demonstrated defects or specifically bounded design gaps; fleet-wide lost hours have not been measured.

**Verdict:** repair the existing pipeline before adding messaging infrastructure. The earlier recommendation to improve the watcher alone was incomplete. Dispatch reads stale state, misses most claims, and the claim writer can grant the same task twice. Faster dispatch would amplify these defects.

## Evidence and boundaries

- Local snapshot: 685 cards: 411 done, 84 dropped, 101 ready, 81 refined, 8 blocked.
- 54 open claims, of which 36 were over 24 hours old. The task selector sees only 3 legacy claims. Age does not authorize deleting a claim.
- NUC dispatch returned 88 cards. Eight would be excluded when given the complete claim set; 21 carry STALE tags that `tasks.py next` filters but dispatch does not. These groups overlap; do not add them.
- Existing tests: 73 passed, one failed across Supervisor/context/ship-time tests; a further 268 passed with 868 subtests across tasks/signals/Codex/role-loader/discovery tests.
- Wiring, config and role-loader checks all PASS. The audited SHA's CI is green: https://github.com/jishusharma/mts/actions/runs/40242122273 .
- Twelve controlled demonstrations are in `reproductions.json`; rerun `python MyTradingSys/research/coordination_audit_20261026/reproduce.py`. They assert the observed defects, not desired behavior. Temporary Git remotes are local; no production mutation or model calls.
- Public GitHub API: latest 30 completed CI runs, 27 success / 3 failure; creation-to-update median 171 s, p90 191 s, max 265 s. Workflow start delay was zero; individual job queue time is not inferred from that.
- Local available worktree logs since 24 October: 29 `ship_wall` rows, median 5.88 s, p90 48.19 s, max 238.38 s. This sample excludes removed/remote trees and post-push CI waiting. It is not a fleet performance estimate.

## 1. P1 — claim acquisition is not exclusive under a push race

**Proof:** `sync.py claim` checks conflicts, then calls `push_claim_commit`. That helper retries rejected pushes against the new tip without repeating the ownership check. In the local two-clone reproduction, worker B claimed after A's check. A's first push was rejected; its inner retry overwrote B's claim. Both printed `claimed same-task` successfully. Evidence key: `racing_claims_both_succeed`.

**Code:** `scripts/dev/sync.py:1215` and `:1291`.

**Impact:** duplicate paid work, conflicting changes, and incorrect release ownership. The earlier assessment that the claim was a reliable final lock was wrong.

**Repair:** one retry loop must own read-current-claims, conflict validation, commit construction and push. Every rejected push restarts validation against the newly fetched tip. Keep fast-forward pushes; never overwrite an existing reservation. Return an explicit reservation ID/token and require it for release. A stale timestamp alone must not transfer ownership.

**Acceptance:** two independent clones racing for the same card or overlapping scope yield exactly one winner; the loser selects another eligible card. A stale worker cannot release its replacement's reservation.

## 2. P1 — dispatch does not use one authoritative, current snapshot

**Proof A:** `tasks.open_claims` reads only `origin/fast-track`; `sync.open_claims` reads `origin/claims` plus legacy claims. `codex_run.cmd_next` also reads only trunk claims. Live snapshot: 54 versus 3, eight incorrectly offered cards; three ready CODEX cards have unseen claims.

**Proof B:** `supervisor.plan` fetches origin, but `_dispatch_raw` uses `tasks.load_all(repo)`, which reads the worktree's JSON. Fetch updates refs, not those files. Reproduction: remote predecessor is `done`, local predecessor remains `ready`, successor still excluded as `dependency` after a successful fetch.

**Proof C:** `tasks.cmd_next` calls `stop_tag`; `tasks.dispatch` and `codex_run.cmd_next` do not share that eligibility path. Twenty-one dispatch rows were STALE by the existing rule. Some may need legitimate revalidation rather than cancellation; the defect is inconsistent treatment.

**Code:** `tasks.py:510,518,774,1384,1447`; `supervisor.py:97,1075`; `codex_run.py:792`.

**Impact:** paid workers start only to be refused, old cards are reconsidered, completed dependencies remain blocked, and fresh work is invisible to long-running coordinators. Codex can repeatedly select the first unseen-claimed card and return idle instead of trying the next.

**Repair:** load cards/holds/lane state from a pinned fetched trunk revision without merging into the coordinator's working files. Read all claims through one canonical reader. Use one eligibility function for next/dispatch/Codex/Gemini, including host, claim, dependencies and justified stale checks. On claim refusal, refresh and try the next candidate with a bounded retry. Scope changes should request revalidation; do not blindly block on every unrelated edit to a broad folder.

**Acceptance:** another clone completes A; the first coordinator sees B become eligible on its next reconciliation without changing its own worktree. Every selector agrees on eligibility for the same snapshot. Existing claims are excluded everywhere.

## 3. P1 — watcher wake conditions omit important completion paths

**Proof:** `_probe_wait_state` keeps `on_trunk` but discards `on_green`; it observes neither task eligibility nor incoming signals. A tracked SHA progressing from landed to verified produced identical probes and a virtual 3,000-second timeout. Also `_gate_slots_raw` observes the default gate pool, while fast ships use `gate-slots-fast`: reproduction held one real fast slot, Supervisor reported zero busy.

**Code:** `supervisor.py:185,195,386,451,549`; `run_all_tests.py:1241`.

**Impact:** remote completions, CI verification and ordinary fast-gate completion can fail to wake an otherwise active coordinator. The previous plan's `ready_more` cannot detect newly eligible work. `watchcheck` verifies that a watcher process exists, not that it watches the necessary state.

**Repair:** keep the bounded session watcher. Reconcile the current eligible set, pending verification revisions, relevant requests and all gate pools. Wake only for an actionable change. Check current actionable state on startup as well as transitions, so changes during watcher restart are not lost. Persist the last acknowledged snapshot/revisions.

**Acceptance:** predecessor completion, green verification, incoming eligible request, fast-slot release and watcher restart each cause one useful wake. Repeated/no-op signals do not cause loops. Missed notifications are recovered from durable state. A target of one existing polling interval (currently five minutes) is a proposal, not a measured guarantee.

## 4. P1 — success evidence conflates attempted, pushed and verified work

**Proof A:** `mts_signal.auto_send_text` maps any Bash `sync.py ship` call to `kind=done` without examining its outcome. Reproduction supplied exit 1 / nothing pushed; output was `done` with an older commit's Result line. This was already documented in `research/thinker/2026-10-22_ship_context_review.md` and remains present.

**Proof B:** `run_all_tests.exec_step` returns True when a fast test times out. `format_step` prints PASS and omits the DEFERRED message; `save_record` stores it as a reusable passing test. Reproduction confirms all three. Deliberately deferring work to CI is a valid policy; recording it as passed is a defect.

**Proof C:** `record_ship_wall` runs in `ship()` before `main()` calls `wait_own_ci`, which may add 600 seconds. It also writes `ok=True` even from the failure finally path. Host preflight is outside this timer. The two-minute guard therefore does not measure the user's entire command wait.

**Code:** `mts_signal.py:389`; `run_all_tests.py:223,280,1104`; `sync.py:924,1038,1695`.

**Impact:** misleading progress, incomplete local checks cached as success, and optimization against the wrong duration. A `done` card alone is also not evidence that its required CI/review has completed; generic dependency checks examine card state.

**Repair:** report separate facts: work produced, pushed revision, verification pending/passed/failed. Emit completion from successful execution/runner receipts, not command-text matching. Give DEFERRED its own result and never cache it as a pass. Record command start-to-exit plus context/preflight, gate queue/run, push/retry and CI wait. Keep asynchronous CI verification in the coordinator where appropriate; downstream consumers still require the checks relevant to their card. Do not add CI waits to documentation-only work that has no required CI run.

**Acceptance:** failed push produces no completion; pushed-but-red is not verified; timed-out checks remain deferred and rerun locally when required. Measured phase totals explain elapsed command time. One duplicate receipt does not start a second successor.

## 5. P1 — the checks prove file presence more often than behavior

**Proof A:** `wiring_scan.classify` treats every non-test `scripts/dev` file as a root. A new function with no caller is DEV-TOOL and passes `--check`; NO-READER is only a warning, and a documentation mention suppresses it. This is a useful inventory check, not proof that a workflow executes it.

**Proof B:** `MyTradingSys/tests/test_gate_discovery_b150.py:17` explicitly excludes `scripts/dev/test_supervisor.py` to avoid a full gate. Direct execution found `test_pick_cards_jis_nb_lane_follows_the_live_host_file` failing after host aliases changed. This is a stale test expectation, not demonstrated broken live routing; it proves the coordinator suite is not covered by green CI.

**Proof C:** all three failures among the recent 30 CI runs include a doc check rejecting the phrase `git log` in a plan; two also lack a DEBUGGING row for usage_reminder. The broad forbidden-word check remains in `tests/docs/test_integrity.py:45`. Relevant runs: 40238013913, 40238133234, 40238311854. Such failures trigger global CI interruption while the integration defects above pass.

**Repair:** register the Supervisor suite in full CI; fix the alias expectation. Add a small cross-component test suite for the producer/consumer boundaries in findings 1–4 and 6–7. Keep dependency inventory, but replace obsolete blanket word bans with tests of actual current invariants. Test registration should verify that the generated CI plan executes the test, not only that its name appears in source text.

**Acceptance:** changing claim storage, removing an adapter call, omitting a dependency receipt, or disconnecting a wake source makes the relevant integration test fail. A legitimate Git command in a current developer procedure does not stop the project.

## 6. P2 — context improvements do not consistently reach their consumer

**Working:** role files and tokens validate; the fold is installed on Claude's Bash PreToolUse ship path. Sixteen cards contain folded context, so it has operated. The three recent context-fold revert/re-land fixes did correct a real Codex prompt incompatibility.

**Gap:** `tasks.brief` renders context, but `supervisor.brief` independently constructs a prompt with goal/scope and omits context.reads, tests and done_when. A fixture with unique required markers loses all three. A generic successor's task brief does not include its dependency ID/result; only flow cards get explicit predecessor receipts. All 53 currently open cards with dependencies are non-flow cards. A worker may recover by opening the card manually, but that is the discovery work the context change was supposed to reduce.

The fold writes to the producing card at ship time; it does not seed every successor or automatically run in non-Claude runners. Only one CODEX card currently contains context. These counts are not adoption/failure rates: the feature is new and older cards were not expected to have the field.

**Measurement:** there is one committed context-gap baseline: 38 sessions, median 26 calls before first edit, p90 61; median context at edit 128,264; unnamed reads median 7; rewrites/session 1.53. There is no second row proving improvement. Read-before-edit is a proxy and can include necessary review, not pure waste. Historical reports distinguish a large app/tool prefix from small repository role files; do not claim that further role trimming solves the dominant cost.

**Code:** `tasks.py:434,457`; `supervisor.py:589`; `preship.py:219`; `context_gap.py:288`; `codex_pack.py:38`.

**Repair:** one compact task-context renderer used by every worker adapter, containing objective, acceptance test, constraints, required source paths, upstream result/verification references and snapshot revision. Keep role-specific wrappers small. Reuse the existing card/brief/pack mechanisms; do not introduce a new knowledge database. Move reusable context collection to an explicit adapter lifecycle call where necessary. Measure equivalent task classes before/after rather than aggregate all roles.

**Acceptance:** the exact prompt delivered by each adapter contains the same required markers, including predecessor result and acceptance criteria. New sessions can start without rediscovering these facts. Track context calls to first useful action and total task cost; do not force an early edit merely to improve the metric.

## 7. P2 — Gemini has a broken release path and an incomplete review handoff

**Proof:** `gemini_queue.run_job` claims a full card ID, then releases that full ID; `sync.claim` truncates the reservation slug to 40 characters. A real local Git reproduction leaves the claim behind on a longer ID. The queue logs release failure but its main command returns zero. The runner releases after generation without publishing a structured review-ready result or verifying a review consumer picked it up.

Its actual contract says a Claude session reviews and ships the branch. SUPER_SESSION's Boot facts say Codex and Gemini ship directly. The implementation and coordinator instructions disagree.

**Code:** `gemini_queue.py:67,82,96,102`; `sync.py:1163`; `SUPER_SESSION.md` Boot facts. This audit does not claim a measured count of production Gemini failures from this cause.

**Repair:** capture the actual reservation token returned by claim and release that token; propagate failure status. Record branch/revision, produced files, result and review owner in the existing card/receipt. Keep it reserved or explicitly transfer ownership to the reviewer until the review handoff is durable. Align the coordinator document with this actual contract.

**Acceptance:** a long-ID Gemini card finishes, its review is queued exactly once, Claude sees the correct revision, and no reservation is orphaned. Failure at generation/release/review remains visible and recoverable.

## End-to-end repair order and ROI

1. **Ownership and shared state:** findings 1–2. Highest priority because every lane depends on them. One canonical claims reader and snapshot/eligibility path; transactional claim retries. Validate with two local clones before live use.
2. **Truthful completion and useful wakes:** findings 3–4 plus Gemini receipt/release. Keep existing signals as notifications and cards/Git as durable facts. Preserve the existing no-standing-scheduler policy. No active coordinator still means no autonomous work; that is an operating choice, not a transport bug.
3. **Context delivery:** finding 6. Consolidate prompt rendering; prove the exact child prompt contains the contract. Avoid spending on further document trimming without matched measurements.
4. **Verification quality:** finding 5 must accompany each repair, with the Supervisor suite restored immediately. Remove the obsolete gate friction demonstrated above; retain checks protecting actual correctness.

The validation scenario is A builds -> B reviews -> C consumes, across two clones and two adapters, with a duplicate signal, claim race, missed signal, stale checkout, CI pending/red/green, worker crash and long card ID. Required result: exactly one owner; no consumer before its required proof; no lost successor; every blocked stage has a specific reason; restart reconstructs state from durable records. Run a small real-station pilot after the deterministic suite passes.

Measure task-ready to claim, claim to first useful action, work duration, local gate wait/run, pushed to verified, and verified to successor claim. Report median/p90 by task class and station, plus duplicate starts and operator interventions. Those are the ROI measures. Message count and a 60-second test cutoff are not throughput measures.

## Review request

Independent Claude review is requested at priority 1 by the operator. Re-run the demonstrations on the pinned revision, compare against current trunk, and return ACCEPT / REJECT / ALREADY FIXED for each numbered finding with exact proof. Distinguish observations from impact estimates. Review the proposed repair order and identify any missing end-to-end requirement. Do not implement or deploy as part of this review. Reuse existing repair cards where suitable; avoid duplicate infrastructure projects.
