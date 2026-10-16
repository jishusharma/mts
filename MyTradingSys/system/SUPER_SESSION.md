# SUPER SESSION - one coordinator, many workers, hours of continuous work (operator term, 2026-10-15)

A **super session** is one coordinator session in the Claude Code Win App that spawns, steers, checks and archives worker sessions
(`start_session`) for several hours, with the operator in the loop only for direction. Max plan only, and only when the weekly
meter has headroom (Pacing below). First one: 2026-10-15, coordinator local_62faa820 (Opus), about 20 linked workers, an Opus
observer, and a second coordinator (coord-2) that drained the ship queue at the end.

While a super session runs, the relay is paused: the coordinator IS the dispatcher. When none runs, the relay (MTS-DispatchGate +
`mts-dispatcher` routine, RELAY.md) keeps the queue moving at the pace the meter allows.

## Audit of the first one (2026-10-15, 139 transcripts in the last ~24 h, scripts: transcript usage blocks)
| What | Number |
|---|---|
| Sessions | 14 Opus, 32 Sonnet, 93 Haiku (mostly dispatcher ticks) |
| Turns / tool calls / output | 4,077 assistant turns, 8,252 tool calls, 3.2 M output tokens |
| Cache reads / cache writes | 527 M / 14 M tokens (Opus 191 M, Sonnet 294 M, Haiku 42 M) |
| Coordinator alone | 319 turns, 39 M cache reads, 10 manual compactions: the most expensive single session |
| Weekly meter | 32 % used after 1.9 of 7 days (pace +5 points ahead of even spend) |
| Fixed cost of every turn | ~70-80 k tokens before any message: system tools 39 k, MCP tools 26 k, system prompt 9 k, skills 6 k, memory 3 k |

### Did compacting help?
68 real compactions (all manual) in 30 sessions; the context fell from 169 k to 70 k on average. Re-reading after a compaction
was negligible (about 1.8 k tokens per compaction: the summaries carried what the session needed).
- Overall it paid: about 17 M input-equivalent tokens saved against about 10 M spent (summary output, re-caching the new prefix).
- But 39 of 68 lost: a compaction pays back only after **about 15 more turns** (it saves ~10 k per later turn and costs
  ~145 k once). The median session ran 23 turns after compacting; 14 compactions came less than 5 turns before the session ended.
- Compaction never goes below the ~70-80 k fixed floor, so on a 1 M window a session at 120 k gains little from it.

## Rules (from the audit)
1. **Compact only if the session will run at least 15 more turns and is above ~150 k.** Otherwise: finish the step, hand off
   (NEXT_SESSION.md or a `start_session` brief) and archive. Never compact a session that is about to ship.
2. **The coordinator works little itself.** It reads results, decides, spot-checks one claim per worker (`git cherry` empty =
   shipped), and archives. Mechanical status goes to a Haiku worker; drafting and code to Sonnet; Opus only for the coordinator
   and an observer the operator asks for. Fable only when the operator starts it.
3. **At most 4 workers running at once** (gate slots are 2 per machine, `sync.py`), one writer per set of files, each with a
   full brief: goal, files, DONE-when, defaults for every open question, hard limits. Workers never ask the operator; questions
   go to the coordinator, which decides toward the goal and logs the decision in the worker's deliverable.
4. **Parallel tool calls in one message**: one turn re-reads the whole context, so batching is the cheapest saving there is.
5. **Second coordinator for the tail.** When the coordinator passes ~300 turns or the operator is about to restart, it hands the
   drain (ship queue, archive, hand-over note) to a fresh Sonnet coordinator instead of compacting again.
6. **No disk or process scans in loops** (Defender finding 2026-10-15): size a folder once with a timeout; never kill processes.
7. **Learning loop (operator 2026-10-16).** Each super session reads Boot facts below INSTEAD of looking them up, and before it
   ends: (a) adds every fact it had to look up and corrects any that were wrong, (b) adds one line to the Session log, (c) prunes.
   Keep Boot facts under ~25 lines and the log to the last 5 sessions (older lines go to the session's own report). The measure
   is boot cost: turns and tokens spent before the first worker starts; each session should beat the last.
8. **Agent workers (2026-10-16).** Briefs ask for: ship once then stop (a second `sync.py ship` only re-wakes the coordinator),
   the proof that new tests fail on the old code (run them against `git show <sha>^:<file>` copies), a final reply of at most
   N lines, long notes in the shared notes folder. Tasks touching the same file run one after the other; others run in parallel.

## Boot facts (read, do not re-look-up; every super session corrects this list)
- Live tree = the main checkout `C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed` (`.mts_live` there is a marker FILE, not a
  folder). Read-only for sessions. Deploy result: `MyTradingSys/runtime/sched/auto_deploy_last.json`; HALT file:
  `MyTradingSys/execution/HALT` (+ `halt_history`); dirty files: `git -C <live> status --short --untracked-files=no`.
- Live state in one read: `live_mirror.py brief` (LIVE_MIRROR.md) + `scripts/sched/check_live_health.py`; ledger =
  `runtime_data` trade_ledger.jsonl in the live tree. A Sonnet read-only worker does this in ~15 tool calls.
- A coordinator started BY ANOTHER SESSION cannot `start_session` (the app refuses): workers are Agent subagents
  (`run_in_background`, `isolation: worktree`, model sonnet/haiku), visible in the Tasks pane, not the sidebar. A coordinator the
  operator opens directly can use `start_session` (sidebar sessions, cost about the same).
- Waking: other sessions send no idle notices. Use ONE background shell watcher (`git fetch` every 5 min; exit on a file landing
  on origin/fast-track or after 50 min), and on every wake `python scripts/sched/relay.py heartbeat "<id>" --note "<what>"`.
- JIS-NB has no MTS-DispatchGate Windows task; the `mts-dispatcher` routine runs in the live tree, so relay/watchdog code only
  takes effect after a deploy.
- `tasks.py` has no host field: `lane` carries it (JIS-NB, CODEX, DSA-NUC, SONNET, HAIKU). Ready list: `tasks.py list | grep ready`.
  Cards that change the live tree or scheduled tasks (nb-*) are operator-side.
- Verify a worker ship: `git cherry origin/fast-track <sha>` prints nothing. CI state: `origin/green/fast-track` moved past it.
- Usage: `get_usage` (ccd_session_mgmt) once per wake; NUC/Fable sessions share the same Max weekly meter.
- Research Map: read the artifact first (`Artifact read`), edit DATA in the saved copy with a script (json load/dump of the
  one `const DATA = ` line), write it to `system/artifacts/research_map.html`, republish with `url`. Another session may have
  edited it since (commit 338e365b did): read the current version, never the old saved copy.
  The Tom/Fabio story and per-setup requests live in the map tab "Setups & story" (DATA.story, source SETUP_CATALOG.md); a
  request there has kind question|task|backtest and a `setupId` (catalogue id); there is no second request store. Backtest =
  fee check at the stated stop first (fee R = 0.14% / stop%), then PRE_REG on DEV only. Fabio home-market chain stays paused.
- CI: `gh run list -R jishusharma/mts --branch fast-track --limit 5` on EVERY wake and after every ship wave (CI sat red 2 h
  unnoticed on 10-16 while a coordinator wrote prompts). New research test files must be registered in run_all_tests /
  run_extra_tests.EXTRA or skipped with a reason (B150, gate step 3gd); study scripts need a `wiring_registry.json` entry.
- AutoDeploy gate (`MyTradingSys/runtime/sched/auto_deploy_last.json`, lock in `runtime/sched/locks/`): about 5 min on an idle
  host, 16+ min under load, and it times out (25 min, old live copy) when workers, ASR or pytest extras saturate the 8 CPUs.
  Start NO CPU-heavy worker while a gate runs; a red sha is not re-gated (RED_KNOWN) until a newer green exists; STOP_DIRTY names
  the live file (`git --no-optional-locks -C <live> status --short --untracked-files=no`); only the session that owns live-tree
  actions may clean it. A new auto_deploy.py runs live only after a deploy.
- NUC lab status: `printf 'Set-Location F:/MTS/mts-codex-lab; python scripts/dev/codex_run.py status\n' | ssh -i ~/.ssh/nuc_gate
  -o BatchMode=yes e-ngineers@192.168.29.110 ps` (stdin goes to PowerShell; stderr carries post-quantum warnings).
- Task card JSON can hold a hidden HOLD `note` that `tasks.py brief` does not print: read the card file before running a refined card.
- Bash tool: a `cd` persists between calls and some `cd x && git ...` chains are denied; use `git -C <dir>` and absolute paths.

## Session log (newest first; one line each, last 5)
- 2026-10-16 autopilot-3 (JIS-NB, Sonnet coordinator, 00:10Z-06:30Z, Agent workers, started by local_1c4041fd): CI red 4 h -> green
  02:04Z, 4b/4f gate races fixed, live deployed to 32077514 at 06:01:49Z after two load timeouts and a STOP_DIRTY; imb filter FAIL,
  context composite INCONCLUSIVE, pit audit FIX-FIRST. Weekly 48 -> 55 %. Learned: heavy workers during a deploy gate cost two
  gates; check `gh run list` and `auto_deploy_last.json` on every wake; a worker that merges late hits VERDICTS.csv and
  wiring_registry.json conflicts (union both).
- 2026-10-15 22:00Z to 10-16 00:20Z super-3 (local_62faa820, Opus coordinator): DSA backtest audit pack (10 cards dsa-audit-01..10,
  AUDIT_BRIEF.md, cd5c6b3c), NUC hang forensics prompt (F:\MTS\NUC_HANG_FORENSICS_PROMPT.md), Research Map v7. Learned: CI stayed red
  for 2 h unnoticed while it wrote prompts, so check `gh run list` on every wake.
- 2026-10-16 super-2 (JIS-NB, Opus coordinator, Agent workers): boot ~25 tool turns, ~10 of them lookups now in Boot facts
  (live tree path, start_session refusal, deploy/HALT state, wake mechanism). 18 workers, 14 ships, weekly +9 (shared meter).
  Learned: coordinator wakes dominate cost; three double-ship wakes; one worker skipped the old-code test proof (rule 8); an
  Agent's first 'finished' notice can be interim while its ship gate runs - verify with git cherry before logging.

## Start (operator: open a new session, model Opus, paste the prompt below)
The coordinator, on its first turn: `get_usage` (stop if the Pacing state is THROTTLE), `python scripts/sched/relay.py stop
"super-session <session id>"` on this machine, read STATUS.md and NEXT_SESSION.md, then spawn.

Heartbeat (watchdog): on every wake the coordinator runs `python scripts/sched/relay.py heartbeat "<session id>" --note "<what>"`
(rewrites `~/.claude/mts-super-heartbeat.json`: coordinator, host, utc, note; not in git). MTS-DispatchGate runs `relay.py watchdog`
first: a stop starting `super-session` with a heartbeat missing, malformed or older than 60 min is resumed (logged `watchdog_resume`); any other stop never.

## End
Drain: every worker shipped (`git cherry` empty) or its partial work handed over in NEXT_SESSION.md; archive finished workers;
`get_usage` written into the hand-over note; refresh the operator's Research Map (`system/artifacts/research_map.html`, edit its DATA,
republish to claude.ai/artifact/9nqpZeMeEehadoBoYopZU3 from the jishusharma1985 login); `python scripts/sched/relay.py resume`; one line to the operator.

## Pacing (when no super session runs) - state from the weekly meter
`f` = fraction of the week elapsed since the last weekly reset, `U` = Weekly all-models % used.
| State | Condition | What runs |
|---|---|---|
| SPEND | U < 100 f - 10, or less than 24 h to the reset with U < 85 | super session worth starting; relay on Sonnet; Fable cards allowed (operator starts them) |
| NORMAL | between | relay on its normal cadence, Sonnet builders, Haiku dispatcher |
| THROTTLE | U > 100 f + 5, or the 5-hour window > 80 % | only model-free work: Codex lab, DSA desk, CI; relay KICKs wait |
Today (10-15 17:45Z): f = 0.27, U = 32 -> NORMAL. The meter is only readable from an App session (`get_usage`), so the
coordinator (and any KICK session) writes it to `~/.claude/mts-budget.json` (not in git); the gate treats a reading older than 6 h as NORMAL.
Wiring that file into `dispatch_gate.py` is a SONNET card (not built yet).

## Prompt: start a super session (paste into a new Opus session, permission mode bypass or auto)
```
You are the MTS super-session coordinator (MyTradingSys/system/SUPER_SESSION.md). Run for hours with zero operator input except direction I give.
Goal today: <one line, e.g. "rebuild layers setups-first: catalogue -> PRE_REG -> screens">.
First turn: get_usage (THROTTLE -> tell me and stop), relay.py stop "super-session", read STATUS.md and NEXT_SESSION.md, pick the tasks that serve the goal.
Spawn workers with start_session (Sonnet; Haiku for mechanical status), at most 4 running, each with a full brief: goal, files, DONE when, defaults for open questions, hard limits from CLAUDE.md. Workers never ask me; you decide toward the goal and log it.
Verify every ship with git cherry, archive finished workers, compact only per SUPER_SESSION.md rule 1, hand the tail to a second coordinator per rule 5.
End: drain, hand-over note with get_usage, relay.py resume, one line to me.
```

## Prompt pattern: any worker or Fable session that must not stop
Lead with: "Run with zero operator input: never ask; on any open question take the most conservative default, write it as
`DECISION (OURS): ...` in the deliverable, and continue." Then: the task file on origin/fast-track, the DONE-when, the hard limits
(testnet only, no secrets, no live tree or processes, no VALIDATION/HOLDOUT reads unless the card says so), a budget stop
(+N weekly points), and a reply limit (at most 5 lines). Model and effort are set in the App before pasting; the prompt cannot set them.
Used for the Fable pilot 2026-10-15 (FABLE_PILOT_PROMPT.md).
