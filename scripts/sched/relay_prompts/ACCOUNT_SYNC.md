# Keeping the three logins and two machines in one shape (2026-10-15)

> **RETIRED 2026-10-17, see SCHEDULING_POLICY.md.** Do not install `mts-dispatcher` or any scheduled task; no routines on any device.

What is per machine and what is per login decides who must do what:

| Thing | Scope | Who sets it |
|---|---|---|
| `MTS-DispatchGate` (Task Scheduler, model-free tick, starts a headless Haiku relay only on KICK) | machine, serves every login | register once per machine (`register_dispatch_gate.ps1`) |
| Task Scheduler jobs (AutoDeploy, DailyHygiene, CodexLab) | machine | register scripts |
| `mts-dispatcher` routine (hourly fallback: refine + housekeep) | login | paste the prompt below, signed in as that login |
| `mts-lane-watch` routine | login, one host is enough | INSTALL.md |
| Pages, pins, Control Room Inbox | login (Inbox only on jishu.sharma, q21) | CONTROL_ROOM.md |

The relay lock (`~/.claude/mts-relay-lock.json`) is per machine, so a gate tick and any login's routine tick never launch twice.

## Target state per machine
- JIS-NB (logins A, C, and B if used): gate registered; every login's `mts-dispatcher` at `7 * * * *` (stagger the minute per login: A 7, C 27, B 47), `--peer-quiet-min 90`.
- JIS-NUC: gate needs the Claude CLI (`claude.exe`) on the machine. Without it the gate exits `NO_LAUNCHER` before ticking, so the App routine stays the dispatcher:
  keep ONE login's routine on `7,37 * * * *`, `--peer-quiet-min 0`; other logins on the hourly stagger. Once the CLI is installed: register the gate, drop every login to hourly.

## Prompt for any login: sync the dispatcher routine (paste into a Code-mode chat on that login and machine)
```
Sync the mts-dispatcher routine on this login and machine. Do not ask questions.
1. list_scheduled_tasks. If mts-dispatcher is missing, create it (taskId mts-dispatcher, working folder = the tree that has .mts_live on JIS-NB, or C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed on JIS-NUC). Prompt = the body of scripts/sched/relay_prompts/mts-dispatcher.SKILL.md on origin/fast-track (git show origin/fast-track:scripts/sched/relay_prompts/mts-dispatcher.SKILL.md), with --peer-quiet-min 90 on JIS-NB and 0 on JIS-NUC.
2. If it exists, overwrite ~/.claude/scheduled-tasks/mts-dispatcher/SKILL.md with that body (LF endings), then verify: python scripts/sched/relay.py tick --root <tree> prints no drift=SKILL.
3. Cron: JIS-NB hourly at minute <7 for login A, 27 for C, 47 for B>. JIS-NUC: 7,37 on the one login that is the NUC dispatcher, hourly on the others (see ACCOUNT_SYNC.md).
4. Model: the routine's App settings must say Haiku 5.5 (the prompt cannot set it); tell me if it does not.
5. Check python scripts/sched/dispatch_gate.py --dry-run --root <tree> prints GATE NOOP/KICK (dry-run) or GATE NO_LAUNCHER, and report the one line. Do not start the relay.
```

## Hand steps only you can do
- JIS-NUC: install the Claude CLI for the E-ngineers user (so `C:\Users\E-ngineers\.local\bin\claude.exe` exists and is signed in), then register the gate there (`ps-bg`, or from RDP:
  `powershell -File scripts\sched\register_dispatch_gate.ps1 -Repo C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed -PeerQuietMin 0 -Trigger`).
- Login C and B on JIS-NB: run the prompt above once in each.
