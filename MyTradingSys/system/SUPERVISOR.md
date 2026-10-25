# SUPERVISOR - how a super session's coordinator runs (design 2026-10-18; role file `roles/supervisor.md`)

SUPER_SESSION.md keeps the history, the boot facts and the session log. This file is the operating design: what the supervisor
does on each wake, which tool answers each question, and what it never does. Built in steps SV1-SV8 (cards at the end).

**Five-hour run, three logins at once, one-line start (2026-10-19):** `roles/supervisor.md` v3 and SUPER_LOOP.md (`supervisor.py plan` every wake: pacing, heartbeat, shard, lane owners; `supervisor.py handover`).

Design history (measured overhead, SV1-SV6, review): `handoff_history/supervisor_design_history_2026-10-18.md`.

## The wake loop (every wake: operator turn, session note, or the watcher exiting)
1. `python scripts/dev/supervisor.py tick --json` (until SV2: `tasks.py dispatch --json`, `desk.py sweep --json`, `ci_watch.py`). Read nothing else
   unless the tick names it. `get_usage` once (MCP; write `~/.claude/mts-budget.json`, tick reads it).
2. Decide, in this order: CI RED -> stop dispatch, one `ci-<sha>` worker (pinned card). Budget THROTTLE -> no spawn. A note in -> verify it (below),
   mark the worker completed, take its next card if the brief chained one. Free slots -> fill from the dispatch list.
3. Re-channel: a finished result may go to Codex lab / DSA desk / Gemini / Haiku checker when that lane is better; the Thinker names the lane, the coordinator runs `desk.py post` / `tasks.py apply-op`.
   Act in ONE message: every `start_session` / Agent / `mark_completed` / SendMessage call of this wake in parallel.
4. Restart the one watcher (`supervisor.py wait --login <L> --shas <reported> --timeout 50m`, background) and end the turn. No other waiting.
   The watcher records a baseline when it starts and exits only on a TRANSITION (a listed sha newly on trunk, CI state change, a slot going
   busy -> free while a worker waits on it), never on a state that already held at start, so restarts cannot loop.

## Dispatch
- Source of work: `tasks.py dispatch --json` (holds, claims, dependencies, reviewer slot resolved) plus `desk.py sweep` proposals.
  Never a `raw`/`refined` card; Session_Planner (foreground Sonnet Agent) refines when fewer than 4 ready cards fit the free slots.
- **Spawn on operator turns.** Event turns make `start_session` show an Allow card (model_guard.py denies it, 2026-10-23): sessions only on operator turns (whole next wave, max 4,
  one writer per file set, 2-3 chained cards each). Event turns run EVERY card as an Agent (size S: stop at 20 turns; size M: stop at 40, chained cards allowed; WORKERS.md rule 3).
- Lanes: CODEX cards go to `codex_run.py` (the lab picks them itself; the supervisor only keeps 8+ ready), Gemini Flash cards to a Lab_Guy
  worker that runs `gemini_queue.py` and reviews the branch (the supervisor keeps its single shell), DSA/JIS-NB run-and-report to `desk.py post`.
- Chained cards are revalidated by the worker at each card start (`tasks.py check <id>`, `sync.py claim`): a hold, dependency or claim that
  appeared since the snapshot stops the chain there, and the worker reports instead of building.

## Role-based workers
- Every worker starts with `You are <Role>.` on line 1, then `Card: <id>` (and chained ids). Build cards use **Builder**; the card's role column
  (dispatch `role`, SV4) picks MTS_Doctor (audits, other-model verification), Lab_Guy (lab review; needs the NUC lab), Eagle_Eyes (live reads; live files only on JIS-NB, elsewhere `live_mirror.py brief`),
  1985Artifacts_Guy (pages; needs the jishusharma1985 login), Admin_Guy (questions, decisions, backlog intake, machine hygiene; Sonnet medium), Pipeliner (routing + allocation; one at a time, lease). ROLES.md table.
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
| build, judgement, spec tests | Sonnet session (est_turns 31-40) or Sonnet Agent (<= 30) |
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
