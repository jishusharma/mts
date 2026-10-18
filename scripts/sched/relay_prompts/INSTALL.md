# Install and verify the relay prompts on a host

> **RETIRED 2026-10-17**: see ACCOUNT_SYNC.md.

One App task per host, `mts-dispatcher`; its prompt is `mts-dispatcher.SKILL.md` here (a ~2 KB stub: ONE Bash call to `relay.py tick`). The
behaviour lives in git (`relay.py`, `relay_session.md`), so the stub rarely changes. Rules and recovery: `TWO_HOST.md`.

1. Task missing: `create_scheduled_task` taskId `mts-dispatcher`, prompt = the file body, working folder = the live tree, cron `*/10 * * * *`
   (JIS-NB) or `7,37 * * * *` (JIS-NUC). The model comes only from the App's routine settings (Haiku 5.5): set it there, prompt text cannot.
2. Prompt changed in git: ship the code first, then copy the file over `~/.claude/scheduled-tasks/mts-dispatcher/SKILL.md` (or
   `update_scheduled_task`). A prompt that calls a subcommand origin does not have yet prints `invalid choice` (2026-10-14: 3 of 5 ticks).
3. Per host only the number after `--peer-quiet-min` differs (NB 90, NUC 0). Delete `SKILL.md.bak*` copies: git is the history.
4. Verify: the next tick's `dispatcher: TICK ...` line carries no `drift=SKILL`. `tick` compares the installed file with origin's copy
   (sha1 of the text with CRLF turned into LF, the `--peer-quiet-min` number ignored and surrounding whitespace stripped) and prints both
   8-hex hashes when they differ. Check by hand: `python scripts/sched/relay.py tick --root <live tree>` prints the same line.

## GPT-lane watchdog (2026-10-12)
`mts-lane-watch.SKILL.md` is the hourly Haiku watchdog for `scripts/dev/lane_health.py` (taskId `mts-lane-watch`, cron `15 * * * *`, one host is enough; JIS-NB if the NUC is the thing being watched).
It is the second line: `codex_run.py tick` on JIS-NUC already runs `lane_health.py sweep --apply --ship --beat` every 30 min with no model. The watchdog catches what that cannot: a NUC that is off
(no heartbeat for 3 h). The frontmatter model is only a request (Q40: the App default decides); the task is two Bash calls either way. Not registered on JIS-NB (2026-10-15): register it where it is wanted.

## Control Room inbox pickup
`mts-control-room.SKILL.md` is not scheduled and the dispatcher no longer polls it. The Inbox db lives on the jishu.sharma page (CONTROL_ROOM.md, q21); only a session signed in as that
account can read it. Run it by hand from there, or give that host's dispatcher an inbox step on purpose (operator decision).

## Model-free gate (2026-10-15)
`scripts/sched/dispatch_gate.py` runs `relay.py tick` from Task Scheduler (`register_dispatch_gate.ps1`, task `MTS-DispatchGate`, every 10 min) and starts a
headless Haiku relay session only on `TICK KICK`; NOOP costs no tokens. The App routine `mts-dispatcher` drops to cron `7 * * * *` (hourly fallback: refine, housekeep).
Log `~/.claude/mts-dispatch-gate.log`. Register after ship: `powershell -File scripts\sched\register_dispatch_gate.ps1 -Repo <live tree> -Trigger`.
