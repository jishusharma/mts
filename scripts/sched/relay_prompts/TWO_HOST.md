# Relay on two hosts, any account: rules, install, recovery (2026-10-12; one-call tick 2026-10-15)

> **RETIRED 2026-10-17**: see ACCOUNT_SYNC.md.

One App scheduled task per host, `mts-dispatcher`, fired by cron. Its prompt is `mts-dispatcher.SKILL.md` in this folder: a ~2 KB stub,
the same on every host except `--peer-quiet-min`. It makes ONE Bash call, `relay.py tick`. On a KICK it IS the relay session (a
session may not start another one unattended: B164) and follows `relay_session.md`, which tick prints from origin at run time, so
behaviour changes in git (`relay.py`, `relay_session.md`), never per host. Install and verify: `INSTALL.md`.

Nothing is tied to an account. Sign a different account into either App: the same task keeps running, on that account's
budget, and `relay_runs.jsonl` records which account each handoff came from. If the task is missing (new machine, App reset,
an empty Scheduled list after a sign-in) tell any session on that host:
"recreate mts-dispatcher from scripts/sched/relay_prompts/INSTALL.md" (one `create_scheduled_task` call).

## How the two hosts share one queue
- `handoff` records host + signed-in account + session title in `MyTradingSys/system/relay_runs.jsonl` (same commit).
- A dispatcher stays IDLE while ANOTHER host wrote the current handoff under `--peer-quiet-min` minutes ago. When that host
  goes quiet (credits out, machine off, App closed) the other one picks the chain up by itself. A handoff with no relay_runs row is not a peer.
- Move the work on purpose: `python scripts/sched/relay.py stop "<why>"` on the host to rest (host-local flag), `resume` later.
- Self re-pacing does not work: an unattended run's `update_scheduled_task` on its own cron is refused (NUC run 2026-10-12).
  Each host keeps one fixed cron.
- Both chains at once is safe (claims stop double work) but spends both budgets.

| Host | `--peer-quiet-min` | cron | state |
|---|---|---|---|
| JIS-NB | 90 (never takes over a chain a peer moved under 90 min ago) | `*/10 * * * *` (operator 2026-10-14: no hourly wait) | Haiku 5.5 (App setting), no night task; the machine is off ~02:00-10:30 IST |
| JIS-NUC | 0 (never yields) | `7,37 * * * *` | last relay_runs row 2026-10-13; current state UNVERIFIED until a NUC session reports. It may still run the older generic prompt (`kick` only): that works, `relay_session.md` falls back to `relay.py begin` |

Find a relay chat later: `relay_runs.jsonl` gives host + account + session title; open that App on that account and search the title.

Session start (B172): `relay.py begin` replaces the worktree + sync start + task pick + claim steps on either host; it fails closed with `BEGIN FAILED: <reason>`.
