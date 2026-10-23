# EXHAUST PHASE: spend the paid quota before the weekly reset (operator 2026-10-23)

Unused quota is lost money. Rule, in force until the operator says otherwise: **from 2 hours before a login's weekly reset, that login plans to use up every model's remaining quota, and in the last hour it does.** Idling, "stopping for the reset" and handing over because the quota is nearly full are not allowed in this window.

## Who acts (no collisions)
- Only a **top-level session** acts. Subagents, Agent-tool children and workers a Supervisor started ignore the broadcast; the parent decides whether to pass work to them.
- **One actor per login.** The first top-level session on a login that reads the broadcast runs `python scripts/dev/sync.py claim "exhaust-<login>"` (login = A, B or C, CLOUD_ACCOUNTS.md). Claim held by another session: do not act; `mts_signal.py ack <id> told --note "login <X> held"` and carry on. The claim holder acks `done` when the window ends.
- A session never spends another login's quota.

## Timeline (reset time from `get_usage`, UTC)
| When | What |
|---|---|
| T-120 min | `get_usage`: weekly %, 5h %, every per-model window (Sonnet, Opus, Fable, Haiku). Send `mts_signal.py budget`. Claim `exhaust-<login>`. Choose the job. |
| T-120 to T-60 | Work the job in saved steps. All models allowed (WORKERS.md Opus/Fable limits lifted for the window); spend the model with the most headroom first. |
| T-60 to reset | Exhaust: take the next finishable card; use the highest-cost model that still has quota; background runs only while they can finish. |
| 100% or reset | Stop. Refresh NEXT_SESSION.md, ship, ack `done`. |

## Choosing the job
1. Pick a card sized below the remaining quota (`est_turns`); split anything larger.
2. Prefer cards that finish here and are not data-blocked (`tasks.py next --all`).
3. Every step: commit, `sync.py ship --again`, confirm `git cherry origin/fast-track HEAD` is empty. The quota can end between two tool calls.
4. A model with headroom but no fitting card does independent audits and second checks of shipped work.

## Never
Trade, deploy, restart, touch HALT files, read `.secrets/`, add a scheduler (SCHEDULING_POLICY.md).

## Requirements to build (card `exhaust-phase-tooling`)
1. `scripts/dev/exhaust.py plan --login <A|B|C> --week --five --reset --model name=pct`: prints phase (none/plan/exhaust/done), minutes to reset, per-model headroom, model order.
2. `exhaust.py start`: takes the `exhaust-<login>` claim; a second caller on the login is refused with the holder's name.
3. `mts_signal.py` `--audience top`: a subagent or worker session neither shows nor acks it.
4. Per-login dedupe: the ACTION banner stops once any session on that login acked; siblings see "held by X".
5. The Stop guard never blocks subagents.
6. The BUDGET line carries every per-model window.
7. Trigger without a scheduler: the boot hook runs `exhaust.py plan` after `get_usage`.

## Tests (each fails on the code before the change)
- phase boundaries: T-121 none, T-120 plan, T-59 exhaust, past reset done.
- two sessions, one login: one claim wins, the loser sees the holder.
- subagent environment: not shown, not acked, Stop not blocked.
- two logins: one actor each, no cross-login claim.
- model order: most headroom first; a model at 100% skipped.
- delivery: `acks <id>` shows hosts `none` before and `done` after an ack (temp clone, `MTS_SIGNALS_SYNC=1`).
