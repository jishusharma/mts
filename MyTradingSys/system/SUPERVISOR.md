# SUPERVISOR - how a super session's coordinator runs (design 2026-10-18; role file `roles/supervisor.md`)

SUPER_SESSION.md keeps the history, the boot facts and the session log. This file is the operating design: what the supervisor
does on each wake, which tool answers each question, and what it never does. Built in steps SV1-SV8 (cards at the end).

**Five-hour run, three logins at once, one-line start (2026-10-19):** `roles/supervisor.md` v3 and SUPER_LOOP.md (`supervisor.py plan` every wake: pacing, heartbeat, shard, lane owners; `supervisor.py handover`).

## Measured overhead (before), real data
Source: all 9 coordinator transcripts on JIS-NUC 2026-10-15..18 (>= 3 spawns each; Opus 6, Sonnet 3), parsed whole by
`coord_overhead.py` (a turn = one assistant API message; eq tokens = input 1, cache-write 1.25, cache-read 0.1, output 5).
| Category | Turns | Share | Active min | eq tokens |
|---|---|---|---|---|
| status re-derivation (tasks/desk/codex/STATUS/history reads/fetch) | 323 | 19.5% | 48 | 6.6 M (20%) |
| ship + claim/release run by the coordinator itself | 117 | 7.1% | 115 (27.5%) | 2.2 M |
| watch loops (sleep, list_sessions, notifications) | 113 | 6.8% | 40 | 1.9 M |
| bookkeeping (update_plan, ToolSearch, wrap_up) | 106 | 6.4% | 54 (13%) | 2.0 M |
| spawn (start_session / Agent) | 94 | 5.7% | 39 | 2.4 M |
| verify (cherry, CI) + steer + cleanup + read + pacing + brief edits | 166 | 10.0% | 19 | 3.2 M |
| **coordination total** | **919** | **55.6%** | **315 (75%)** | **18.2 M (56%)** |
| own work (edits, tests, scripts) | 430 | 26.0% | 103 | 8.5 M |
| text-only replies to the operator | 305 | 18.4% | (operator time) | 6.1 M |
1,654 turns, 32.8 M eq, 418 active minutes; **9.8 coordination turns per worker spawned**. Trunk, last 72 h: 2,257 commits,
61% overhead (merge 35%, claim 14%, release 13%; `traffic_report.py 72`). Desk: 17 pending, 9 STALE (`desk.py sweep`).
Gate: clean ship 544 s, 2 slots per machine; on 10-18 six shipping sessions queued 2-3 h and ships died at the 600 s tool timeout.
`relay_runs.jsonl` (51 rows, last 2026-10-17) holds no coordinator data: the relay is retired.

## The five changes that cut most of it
| # | Change | Targets | Expected |
|---|---|---|---|
| SV2 | `supervisor.py tick --json` (fetches first, reads trunk refs, not local state): ONE call per wake = dispatch top 8, desk sweep counts, CI state, gate slots busy, each worker's sha on trunk (cherry) and green ref, lane depths (codex/gemini), budget file age | status + verify + read + pacing: 482 turns, 9.7 M eq | 1-2 calls per wake (-80%) |
| SV3 | The supervisor never ships product code (one docs-only ship at hand-over, no gate slot). Its own edits go to a worker, whose turns re-read a ~80k Sonnet context instead of a 200k+ supervisor context; workers ship with `sync.py ship --release <slug>` in the wave order, with cancellable tickets (Failure handling) | ship 115 min (27.5% of active time); gate timeouts | coordinator ship time -> ~0 |
| SV1+SV4 | Role workers: `You are Builder.` + card id; `roles/builder.md` holds the boilerplate brief (no-questions rule, boot, verify line, report format); `supervisor.py brief <card> --role R` prints the start text; `role_loader.py verify` checks the banner in the worker's note | spawn + brief 2.5 M eq; wrong-workflow workers | one parallel start_session message per wave |
| SV5 | `supervisor.py wait` as THE background shell: exits on the first of a listed sha on trunk, CI red, a gate slot free, 50 min | 113 watch turns | 1 shell per wave, 0 sleep turns |
| SV6 | Bookkeeping diet in the role file: all deferred tools in ONE ToolSearch at boot, update_plan once per wave, wrap_up once per operator turn | 106 turns, 13% of active minutes | -70% |
Target after SV1-SV6: coordination under 3 turns per spawn (now 9.8) and under 25% of a super session's eq tokens (now 56%).
Re-measure with the same script (SV6) on the next two super sessions, worker and coordinator cost together, per session, not one pooled
number. The savings are GUESS until then: batching removes repeated context reads, not the work itself.

## The wake loop (every wake: operator turn, session note, or the watcher exiting)
1. `python scripts/dev/supervisor.py tick --json` (until SV2: `tasks.py dispatch --json`, `desk.py sweep --json`, `ci_watch.py`). Read nothing else
   unless the tick names it. `get_usage` once (MCP; write `~/.claude/mts-budget.json`, tick reads it).
2. Decide, in this order: CI RED -> stop dispatch, one `ci-<sha>` worker (pinned card). Budget THROTTLE -> no spawn. A note in -> verify it (below),
   mark the worker completed, take its next card if the brief chained one. Free slots -> fill from the dispatch list.
3. Act in ONE message: every `start_session` / Agent / `mark_completed` / SendMessage call of this wake in parallel.
4. Restart the one watcher (`supervisor.py wait --shas <reported> --timeout 50m`, background) and end the turn. No other waiting.
   The watcher records a baseline when it starts and exits only on a TRANSITION (a listed sha newly on trunk, CI state change, a slot going
   busy -> free while a worker waits on it), never on a state that already held at start, so restarts cannot loop.

## Dispatch
- Source of work: `tasks.py dispatch --json` (holds, claims, dependencies, reviewer slot resolved) plus `desk.py sweep` proposals.
  Never a `raw`/`refined` card; Session_Planner (foreground Sonnet Agent) refines when fewer than 4 ready cards fit the free slots.
- **Spawn on operator turns.** The app refuses `start_session` on turns a note or event started. So on every operator turn the supervisor starts
  the whole next wave (max 4 sessions, one writer per file set) and **chains 2-3 cards per session in the brief** (same file cluster, in order),
  so the wave runs without new spawns. On event turns only size-S cards start, as one-use Agents (WORKERS.md rule 3).
- Lanes: CODEX cards go to `codex_run.py` (the lab picks them itself; the supervisor only keeps 8+ ready), Gemini Flash cards to a Lab_Guy
  worker that runs `gemini_queue.py` and reviews the branch (the supervisor keeps its single shell), DSA/JIS-NB run-and-report to `desk.py post`.
- Chained cards are revalidated by the worker at each card start (`tasks.py check <id>`, `sync.py claim`): a hold, dependency or claim that
  appeared since the snapshot stops the chain there, and the worker reports instead of building.

## Role-based workers
- Every worker starts with `You are <Role>.` on line 1, then `Card: <id>` (and chained ids). Build cards use **Builder**; the card's role column
  (dispatch `role`, SV4) picks MTS_Doctor (audits, other-model verification), Lab_Guy (lab review; needs the NUC lab), Eagle_Eyes (live reads; live files only on JIS-NB, elsewhere `live_mirror.py brief`),
  1985Artifacts_Guy (pages; needs the jishusharma1985 login), Admin_Guy (questions, decisions, backlog intake, machine hygiene; Haiku high), Pipeliner (routing + allocation; one at a time, lease). ROLES.md table.
- The role file is the brief; the start text adds only card ids, defaults for open questions the card does not settle, and the stop line.
- **Version receipt** (not proof of compliance or of correct work: the token is computable from the public file): a worker's report
  (its note) starts with its banner. `python scripts/dev/role_loader.py verify --text "<note>"` exits 0 when
  the sha is on trunk and the version and token match the role file at that sha and on trunk now; 2 when genuine but the role changed since
  (send `reload role` before its next card); 1 = untrusted (no banner, ROW ONLY, ROLE NOT LOADED, wrong role/path/token, sha not on trunk).
  `--sid <worker CLI session id>` also requires the hook's own injection record (`%TEMP%/mts_roles/<sid>.json`, same machine): that binds the
  receipt to the hook, not to text the worker typed. The work itself is proven only by the Verification steps.

## Model routing (WORKERS.md rule 6 is canonical; `model_guard.py` enforces)
| Work | Model |
|---|---|
| supervisor | the one the operator started it on (Opus only when the operator named it) |
| build, judgement, spec tests | Sonnet session (est_turns 16-40) or Sonnet Agent (<= 15) |
| scoped: lookups, recomputes, registry upkeep, is-it-on-trunk batches, mechanical edits | Haiku Agent, at most 5 at once |
| CODEX lane | GPT via codex_run.py (luna default, astra for `crucial`) |
| GEMINI | Flash via gemini_queue.py (commits on its branch, never ships) |
| Fable | never started or messaged by the supervisor; the operator runs it by hand |
Every start passes `model` and `initiation: "user_asked"`; offer/own_initiative cards are denied (no clicks).

## Pacing
- 5 h window (Pro login): < 60% normal; 60-70% crucial only; 70-80% supervisor only; >= 80% stop spawning. Weekly SPEND/NORMAL/THROTTLE as in
  SUPER_SESSION.md. Rule 12: when a reset is near, remaining minutes / 40 = workers to launch, one card each.
- Turn caps (`turn_meter.py`): Sonnet/Haiku workers 4M/context tool turns (100k = 40) and 10 operator turns, then hand over through the card
  and NEXT_SESSION.md; an Opus supervisor has no turn cap and hands over at 500k context; a Sonnet supervisor at 40/10 like any worker.
  Hand-over = write the wave state to NEXT_SESSION.md (cards running, shas reported, next wave), ship it, start a fresh supervisor on the next
  operator turn with `You are Supervisor.`

## Verification (per claim, before `mark_completed`)
1. sha on trunk: `git merge-base --is-ancestor <sha> origin/fast-track` exits 0 (an error is a failure, never success; tick does it), `Result:` line present.
2. One other-model check: the worker's model never checks itself. Sonnet claim -> Haiku Agent reruns the named test or count; CRUCIAL weight ->
   diff-only review Agent before ship (SUPER_SESSION rule 11); CRITICAL -> review session; GPT/Gemini results -> a Claude reviewer (Lab_Guy rules).
3. CI: `origin/green/fast-track` contains the sha within 60 min of the ship (elapsed time, not waves); if not, the CI-red path applies.

## Failure handling
- **Stuck worker**: no note, no new commit on its branch and no gate slot or detached ship owned by its worktree for 45 min (tick) -> one
  SendMessage asking for state; still nothing on the next wake -> `stop_session`, confirm it stopped, check trunk for its sha (a late ship
  counts), keep its branch (partial work), then `tasks.py tried` and back to ready. Never a second message.
- **Messages** go only to session ids this supervisor started (from its own start results), never to a Fable session, never by search.
- **Red CI**: stop dispatch, one ci worker (exempt from every ship hold); the rest of the wave keeps building but does not ship until green.
- **Gate contention**: at most 2 gates per git common dir (slots; separate clones and prechecks are outside the cap, SV7). The brief gives
  each worker its place (`ship after <slug>`); the ticket is cancellable: if <slug> has no note or ship within 60 min, or failed, the worker
  ships anyway. Nobody holds a slot while waiting on a review or a predecessor. When the wave has a CRUCIAL/CRITICAL card, at most 3
  builders run so the review or CI repair always has a session slot. Ships run detached when they could pass 600 s; one ship per worker.
- **Merge conflicts** on registries (VERDICTS.csv, wiring_registry.json): union both sides (boot fact); the gate's registry checks catch duplicates.
- Blocked on the operator: never ask; take the default from CLAUDE.md, log `DECISION (OURS)` in the deliverable, continue.

## Cleanup
Hand-over state (NEXT_SESSION.md) is written by the wave's last worker or one docs-only ship by the supervisor before its budget ends.
Each verified worker: `mark_completed` (+ `archive_session` when allowed) in the same message as the next spawn. End of block: drain (every
worker shipped or handed over), `sync.py where` clean, stale claims released by their owners' rules, Session log line in SUPER_SESSION.md.

## Hard limits (unchanged)
No schedulers, no polling agents: wait on notes and one background shell. No operator clicks, no routine questions. Never message Fable.
Testnet only; public repo: no runtime, order or account data in commits. The supervisor and builders never deploy, restart processes or touch HALT files.
Stay out of ROUTING.md (Pipeliner owns it).

## Review (GPT-6 Astra via `codex exec -s read-only`, 55.8k tokens, 12 findings) and what was folded in
Accepted: (1) the banner is a version receipt, not proof: renamed, `--sid` binds it to the hook's record, work is proven only by Verification;
(3) cancellable ship tickets, CI repair exempt, 3-builder cap when a review must fit; (4) stuck worker: check slot, detached ship and trunk
before requeue, keep its branch; (5) watcher exits on transitions only, Gemini moves to a Lab_Guy worker so one shell stays one shell;
(6) exact ancestry instead of `git cherry`, a 60 min CI deadline instead of "2 waves"; (7) totals fixed (919 = 55.6%; brief edits were
missing from the table); (8) the "~13% fewer commits" claim dropped (`ship --release` still writes a release commit, sync.py:545); savings
marked GUESS, SV6 measures worker + coordinator per session; (9) host-wide gate budget added as SV7; (10) chained cards revalidated per
card; (11) messages only to own session ids, never Fable, guard hook SV8; (12) hand-over written by a worker or one docs-only ship.
Rejected: (2) "SV1 not implemented": the review read the tree before SV1 landed in this session (9 tests now, all failed on the old code).
(11, part) capability enforcement for builders (testnet only, no deploy/HALT): already CLAUDE.md hard rules plus existing hooks; out of scope.
(12, part) schema-aware registry merges: the gate's registry checks already reject duplicates; no lost row seen in the data read.
(8, part) "delegating the ship only moves the cost": a supervisor turn re-reads a 200k+ context, a worker turn ~80k, so moving it cuts cost.

## Build cards
| Card | Step | Worker | est_turns |
|---|---|---|---|
| sv1-role-loader-verify | `role_loader.py verify` + Supervisor in KNOWN_ROLES | done in this session (9 tests, fail first) | - |
| sv2-supervisor-tick | `scripts/dev/supervisor.py tick --json` | session, Sonnet | 25 |
| sv3-ship-release-ticket | supervisor ship order + `ship --release` default in briefs; FIFO ticket in gate_slot | session, Sonnet (CRUCIAL: gate) | 30 |
| sv4-builder-role-and-brief | `roles/builder.md` + `supervisor.py brief` + dispatch `role` field | session, Sonnet | 20 |
| sv5-supervisor-wait | `supervisor.py wait` watcher | agent, Sonnet | 12 |
| sv6-remeasure | commit `coord_overhead.py` (scripts/dev + test + wiring entry), rerun per session on the next 2 super sessions | agent, Sonnet | 12 |
| sv7-host-gate-budget | gate slots machine-wide (not per git dir), prechecks counted, queue/service/retry times logged | session, Sonnet (CRUCIAL: gate) | 25 |
| sv8-guard-supervisor-messages | model_guard: deny SendMessage/send_message to a Fable session or a session this one did not start | agent, Sonnet | 12 |
