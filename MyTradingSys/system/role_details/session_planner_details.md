# Session_Planner details (read at the step that needs them; not injected by the hook)

## Refinement steps
| Step | Who / cost | What |
|---|---|---|
| 1 Draft | refiner Agent: Haiku for ROUTINE/S cards (docs, ledgers, event tables), Sonnet for IMPORTANT and up | fill the card from the registry row and repo evidence (Duty 1 above) |
| 2 T0 gate | no model, ~0 tokens | `tasks.py check <id>` (Definition of Ready) + `tasks.py lint`; every `scope_in` path exists (`git ls-files`); no `scope_in` path is in another open claim; `done_when` names a file, row count or number; a code card names a fail-first test |
| 3 Review | reviewer Agent, **Sonnet medium, a different agent from the drafter**, one call per batch of up to 5 cards | input is only each card's JSON plus the evidence lines it cites, never the drafter's reasoning; reply at most 2 lines per card: `ACCEPT` or `FIX: <what is wrong>`; checks: scope matches the goal, steps reach done_when, no hidden operator-only step, executor/est_turns plausible, weight not too low |
| 4 Fix | the drafter, once | apply FIX lines, re-run step 2; a second FIX parks the card (`tasks.py tried`) |
| 5 Stamp | planner | first words of `note`: `REVIEWED:<utc date> <ACCEPT|T0-ONLY>`; **a card without the stamp is not in the dispatch table** |
Cost control: ROUTINE cards that pass step 2 with zero warnings take the stamp `T0-ONLY` (no reviewer call) and are spot-checked by the coordinator after
the worker ships; IMPORTANT, CRUCIAL and CRITICAL cards always take step 3. Batching keeps it to one reviewer call per planner run (~one Sonnet call
instead of one per card), and a card that already bounced a worker once is always reviewed. If reviewers BLOCK >30% of drafts over a week, the
drafter model goes up one tier for that card class (log it in the Session log); if they ACCEPT >95% for a class, that class drops to `T0-ONLY`.


## CRITICAL protocol
CRITICAL protocol: (1) the worker posts `mts_signal.py send --kind ask "REVIEW <id> PLAN <branch>"` once its plan and test list exist (before code);
(2) the reviewer session (fresh context, Sonnet medium, Opus only if the operator names it) reads the card and plan and replies APPROVE or CHANGES in <= 5 lines;
(3) the worker builds, posts `REVIEW <id> DIFF <sha>`; the reviewer reads the diff only, not the worker's reasoning, edits nothing, checks the live-path test rule
(restart/reset state, non-trade balance moves, API errors, fail-closed) and a fail-first test; (4) a second BLOCK goes to the coordinator, who decides and logs it.
The worker never reviews its own diff; the reviewer is never the planner. CRITICAL cards run builder-in-worktree only; deploy stays manual or coordinator-run (DEPLOY_RUNBOOK.md).
The planner's table names the reviewer slot (`REVIEW session` or `review Agent`) next to the card; the coordinator spawns it, counting it in the 4-session cap.


## Unblock cases
- defect already shipped (`git cherry` empty on its fix) -> unblock to `ready`, refresh (`tasks.py tag <id> --refresh`);
- block is a hold the operator wrote (OPERATOR_DECISIONS.md) -> leave it, list it;
- block names nothing, or the blocker card is `done`/`dropped` -> unblock and say so;
- duplicate of a shipped card (same refs, same scope paths) -> `dropped` with the sha in `note`;
- 429/rate-limit block -> keep, set the retry date in `note` (one retry per day, LESSONS_DIGEST s6).
Output one line per change: `UNBLOCK <id>: <why> <sha>`. Never delete a card file by hand (`tasks.py sweep --apply` retires closed ones).

