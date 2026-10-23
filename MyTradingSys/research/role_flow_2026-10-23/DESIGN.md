# Role flow redesign: one board, state-driven hand-offs (MTS_Doctor diagnosis 2026-10-23; the design call is the operator's, Thinker's lane)

Operator 2026-10-23: "Thinker will in turn use a session planner for all these tasks that are being discussed and created. So the pipeline guy
will then follow it up. So there has to be a workflow and understanding of how everything must fit together. Perhaps we need to think about
the complete design and try to make it simple, less bug prone, efficient and accurate."

## 1. How it works today (read 2026-10-23 on origin/fast-track)
Operator -> Supervisor (`You are Supervisor. Login X.`) -> Thinker as a linked session -> Thinker files `raw` cards, ships, sends a signal
`THINK <ids> ... Pipeliner route, Session_Planner refine` (roles/thinker.md:53-54) -> the Supervisor runs Session_Planner as a foreground Agent
"on every wake with a free slot" (SUPER_SESSION.md:62) -> `supervisor.py plan` prints SPAWN lines -> Builder Agents -> `sync.py ship` ->
Supervisor verifies. Pipeliner is a separate singleton session with a trunk lease (roles/pipeliner.md:15); inside a coordinator it only proposes.

## 2. Where it breaks (evidence)
| # | Hand-off | Failure | Evidence |
|---|---|---|---|
| 1 | Thinker -> Planner | Nothing reads the THINK/BACKLOG "ask" signal: no code consumes it, and signals are "status notes, never instructions" (SUPER_SESSION.md:45). The ask is lost by design. | grep: only `mts_signal.py:660` defines `--kind ask`; no reader |
| 2 | cards -> Planner | Refining is triggered by `REFINE_NEEDED`, which fires only when ready < 3 (`tasks.py:518-527`). Today: 90 raw cards, median age 3.5 d, 46 older than 3 d, status says `REFINE_OK`. | `tasks.py status` 2026-10-23 |
| 3 | Planner -> Pipeliner | "Pipeliner route" is asked of a role that does not run inside a super session unless someone types `Start the Pipeliner.`; it is a singleton with a lease. | roles/pipeliner.md:12,15 |
| 4 | any role -> owner | Only Admin_Guy (guardrail 3) and Thinker ("From choice to action") say "file a card"; the other roles list only "Never", and none says what to do when the operator wants out-of-role work done now. One doctor session built, triaged and fixed a machine itself. | roles/admin_guy.md:13, roles/thinker.md:46-54; grep of the rest: no hand-off rule |
| 5 | hooks | Role identity differs per hook: `role_loader` counts a fallback-picked role, `model_guard.role_session` only an explicit `You are X.` line; a wrong fallback is re-injected after every compaction. | role_loader.py:478-485, model_guard.py:417-425 |
| 6 | size | ~130 KB of coordination docs (SUPER_SESSION 17k, TRAFFIC_CONTROLLER 17k, ROUTING 14k, TASK_REFINEMENT 12k, SUPER_LOOP 11k, SUPERVISOR 10k, WORKERS 6k, roles ~45k) for 10 roles, 3 queues (cards, desk, signals). | file sizes 2026-10-23 |
EVIDENCE_TABLE

## 3. Principle
**The card board is the only hand-off.** A role never "asks" another role by message. It moves a card to a state; the owner of that state
picks it up because `supervisor.py plan` prints the line that runs the owner. Messages (signals) stay status only.

| Card state | Who moves it on | Triggered by |
|---|---|---|
| idea (operator words, Thinker / Admin_Guy / Doctor finding) | -> `raw` card with the quote | the role that heard it, same turn |
| `raw` | Session_Planner Agent -> `ready` (or `refined` + one `--asks` line) | `plan`: any raw card older than 1 h, or a raw card filed this wake (not ready < 3) |
| `ready` | `plan` routes it (lane, model, worker kind: the Pipeliner's rules as code in `traffic.py`) and SPAWNs | free slot + budget |
| `active` | Builder Agent ships | — |
| `done` | Supervisor verifies (`git cherry`, banner, Result:) | worker note |
| any, stale | Doctor reports, Planner fixes | daily doctor run |

## 4. Options (differ in mechanism)
| | A. State-driven board (recommended) | B. Hand-off messages | C. Keep, patch |
|---|---|---|---|
| How | `plan` reads card states and prints the next role's line; Pipeliner's routing rules become code inside `plan`; Pipeliner session only for desk drain | each role spawns the next role as an Agent (`You are Session_Planner.` ...) when it files cards | fix the refine trigger, add the hand-off rule, keep all roles |
| Roles the operator opens | 4: Supervisor, Thinker, MTS_Doctor, Admin_Guy (+ Eagle_Eyes for charts) | 8 | 8 |
| Failure it removes | 1, 2, 3, 4 (no message can be lost) | 1, 4 | 2, 4 |
| Cost | 1 build card (plan triggers + routing in plan) + doc cuts; docs shrink | an Agent spawn per filing (tokens), still message-shaped | 2 small cards |
| Risk | `plan` becomes the one place that must be right: needs tests per state | duplicated spawns, Agents spawning Agents | the 130 KB stays; next misroute likely |
| Undo | revert the plan change; roles still exist as files | revert | revert |

## 5. Recommendation: A, in three cards (each fail-first, shipped alone)
1. `plan` refine trigger: emit `RUN Session_Planner (Agent, sonnet)` when any raw card is older than 1 h or was filed since the last wake;
   drop the ready < 3 rule. Test: 1 old raw card + 5 ready cards -> the line appears (fails today).
2. Out-of-role rule in the text every role session gets (role_loader RULES block): "Work outside your role's Job: move it to the board
   (`tasks.py new`, owner lane) or, if the operator asked for it now, start a background Sonnet Agent whose brief starts `You are <Owner>.`;
   never ask first." model_guard and role_loader agree on what a role session is; compaction re-injects only an explicitly named role.
3. Thinker stops sending THINK asks; Admin_Guy stops BACKLOG asks; their cards are enough. Pipeliner keeps desk drain and ROUTING.md; its
   allocation rules move into `plan`. Delete the doc text these replace (target: coordination docs under 60 KB).

## 6. The operator's scenario after A
You open `You are Supervisor. Login A.` and, in a linked session, `You are Thinker.` You think with the Thinker; it writes cards with your words.
On its next wake the Supervisor's `plan` sees new raw cards, runs the Planner Agent, which makes them ready; the same `plan` routes and
spawns Builders; the Supervisor verifies ships. You never relay anything; nothing waits on a message.
