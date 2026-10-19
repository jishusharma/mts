# SUPER SESSION - one coordinator, many workers, hours of continuous work (operator term, 2026-10-15)

A **super session** is one coordinator session in the Claude Code Win App that spawns, steers, checks and archives workers (WORKERS.md: sessions or one-use Agents)
(`start_session`) for several hours, with the operator in the loop only for direction. It can start from any device and any login (nothing in the start prompt or `role_loader.py` checks either); in practice a login with weekly
headroom (a Max login), because the meter decides (Pacing below). Only live-tree work is tied to JIS-NB (deploys, process checks, HALT reads, live-file reads): it goes to a JIS-NB desk row or the NB session, never done from a work tree. First one: 2026-10-15, coordinator local_62faa820 (Opus), about 20 linked workers, an Opus
observer, and a second coordinator (coord-2) that drained the ship queue at the end.

**Operating design: SUPERVISOR.md** (wake loop, role workers, verification, ship order; role file `roles/supervisor.md`,
loaded by line 1 of the start prompt below, `You are Supervisor.`). This file keeps the audit, rules history, boot facts and the session log.

The coordinator is the only dispatcher. When none runs, nothing moves on its own: no relay, dispatcher or routine exists (MTS-DispatchGate and `mts-dispatcher` RETIRED 2026-10-17, see SCHEDULING_POLICY.md).
For "schedule the next 5h/10h" the coordinator writes the card order into a plan file and works it.

## Audit of the first one (2026-10-15, 139 transcripts)
4,077 turns / 8,252 tool calls / 3.2 M output tokens in ~24 h; coordinator alone 319 turns and 10 compactions (the costliest session).
Fixed cost of every turn ~70-80 k tokens (tools 39 k, MCP 26 k, prompt 9 k, skills 6 k, memory 3 k). 68 compactions: 39 lost; one pays back
only after ~15 more turns (saves ~10 k per later turn, costs ~145 k once); history, replaced by the turn budget (WORKERS.md rule 5).

## Rules (from the audit)
1. **Turn budget and workers: see WORKERS.md rule 5** (canonical). No compaction: reuse a session while its budget has room, else hand off
   (NEXT_SESSION.md or a `start_session` brief) and archive.
2. **The coordinator works little itself.** It reads results, decides, spot-checks one claim per worker (`git cherry` empty =
   shipped), and archives. Model: the one the operator started it on (WORKERS.md rule 6); workers Sonnet, Haiku for mechanical status.
   Fable only when the operator starts it.
3. **At most 4 workers running at once** (gate slots are 2 per machine, `sync.py`), one writer per set of files, each with a
   full brief: goal, files, DONE-when, defaults for every open question, hard limits. Workers never ask the operator; questions
   go to the coordinator, which decides toward the goal and logs the decision in the worker's deliverable.
4. **Parallel tool calls in one message**: one turn re-reads the whole context, so batching is the cheapest saving there is.
5. **Second coordinator for the tail.** When the coordinator passes ~300 turns or the operator is about to restart, it hands the
   drain (ship queue, archive, hand-over note) to a fresh Sonnet coordinator.
6. **No disk or process scans in loops** (Defender finding 2026-10-15): size a folder once with a timeout; never kill processes.
7. **Learning loop (operator 2026-10-16).** Each super session reads Boot facts below INSTEAD of looking them up, and before it
   ends: (a) adds every fact it had to look up and corrects any that were wrong, (b) adds one line to the Session log, (c) prunes.
   Keep Boot facts under ~25 lines and the log to the last 5 sessions (older lines go to the session's own report). The measure
   is boot cost: turns and tokens spent before the first worker starts; each session should beat the last.
8. **Agent workers (2026-10-16).** Briefs ask for: ship once then stop (a second `sync.py ship` only re-wakes the coordinator),
   the proof that new tests fail on the old code (run them against `git show <sha>^:<file>` copies), a final reply of at most
   N lines, long notes in the shared notes folder. Tasks touching the same file run one after the other; others run in parallel.
9. **Turn budget by context size (operator 2026-10-18, replaces the 10-16 compaction-by-share rule).** The hook `turn_meter.py` allows 4M / context
   tool turns to Sonnet/Haiku, no turn cap to Opus (hand over at 500k), and to Fable one operator message (hard). The coordinator's own
   sweep on every wake: `get_usage` per running worker, reuse or `mark_completed` + `archive_session`. Keep working state in files
   (NEXT_SESSION.md, notes folder, task card), not in the context.
10. **Signals between logins and machines (operator 2026-10-16).** The app cannot message across logins, so `scripts/dev/mts_signal.py`
   (hook in `.claude/settings.json`, automatic) sends a line on the git branch `mts-signals` when a session starts or runs
   `sync.py claim|release|ship|start`, and every 5 minutes shows the signals other host/account pairs sent. Sessions do nothing for
   this. Optional: `mts_signal.py send "<text>" --kind ask|note` for a one-line note, `read` to list. Signals are status notes, never
   instructions, and the repo is public: no names, secrets or runtime data. `MTS_SIGNALS=off` disables. Limit: two logins on one
   machine share `MTS_ACCOUNT`, so they look like one sender to each other (they share the app, use `send_message` there).
11. **Independent review agent (operator 2026-10-17).** Any diff touching the live path, gates (`run_all_tests.py`, `sync.py` gate),
   `promote.py`, `prereg_gate.py` or decision numbers (thresholds, split dates, MDE/power) gets a second Sonnet Agent (medium) before
   `sync.py ship`. It sees only the diff (the diff against origin/fast-track), never the worker's reasoning or conclusion. Reply at most 5 lines:
   verdict APPROVE or BLOCK, then the defects. Cap 30k tokens; if the diff is larger, review the hunks in the paths above only.
   BLOCK means the worker fixes and re-submits once; a second BLOCK goes to the coordinator, who decides and logs it. The reviewer
   edits nothing and the worker may not review its own diff. Both coordinator prompts (below) carry this line.
12. **Spend the window before it resets (operator 2026-10-17).** Every login's usage window is spent, not saved: when a login (any device) has
   budget and its reset is near, pace workers so the meter reaches about 95% right as the window resets (the operator's weekly cap is 75% for logins B and C when they run on JIS-NB, an operator choice, not a technical limit; login A and the NUC logins may go to 95%; letters per traffic_inventory.json).
   Rule of thumb: remaining minutes / 40 = workers to launch in the window, staggered, one card each; re-check `get_usage` at each launch.
   An idle login with ready cards is a defect. Wake an idle NUC with `python scripts/dev/nuc_wake.py --card <id> --name <n>`. Every coordinator
   prompt carries this line.
13. **Blockers go bottom-up (operator 2026-10-17).** A defect blocks only cards that read its output. Before holding a card, name the defect and
   the file the card reads from it; if it reads nothing from it, it is not blocked. Holds with no named defect are released (`tasks.py apply-op <id> release`).
   The GPT/Codex lane never idles while a gptb-* or gpt-* card is ready.
14. **Session_Planner (operator 2026-10-17).** The coordinator runs the Session_Planner role (`roles/session_planner.md`) as a foreground Sonnet Agent at boot and on every wake with a free worker slot: it refines raw cards, returns the dispatch table (agent vs session, model, file cluster, weight), lifts blocks that name no live defect and lists stale claims, idle sessions and shipped worktrees for cleanup. Never dispatch a `raw`/`refined` card (2026-10-17: three Haiku workers came back empty on raw cards). Weight CRUCIAL = rule 11 review Agent; CRITICAL = a review session spawned mid-session (plan) and pre-ship (diff), counted in the 4-session cap. Both coordinator prompts carry this line.

## Boot facts (read, do not re-look-up; every super session corrects this list)
- Live tree = the main checkout `C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed` (`.mts_live` is a marker FILE). Read-only for sessions.
  Deploy result: `MyTradingSys/runtime/sched/auto_deploy_last.json`; HALT: `MyTradingSys/execution/HALT` (+ `halt_history`).
- Live state in one read: `live_mirror.py brief` (LIVE_MIRROR.md) + `scripts/sched/check_live_health.py`; ledger = `runtime_data` trade_ledger.jsonl.
- Workers: WORKERS.md is the rule (card fields `worker`, `est_turns`). Agents are invisible in the sidebar: name each in one line.
- Starting workers: WORKERS.md rules 2, 3, 7. `start_session` is refused on turns a side-session note or event started: on every OPERATOR turn
  start all workers the next stretch needs (max 4 at once), each briefed to chain its follow-ups; never make the operator click a card.
  On an event turn a size-S card runs as a background Agent at once; a size-M card waits for the next operator turn (brief it in NEXT_SESSION.md).
- Waking: the app continues the coordinator when a started session ends a turn (`side-sessions-event`) or a background Agent/shell finishes.
- Run `sync.py ship` detached (`nohup ... > log &`, poll the log): the gate takes 7-12 min, past the 600 s tool cap, and a killed ship loses the run. One ship per session.
- Verify a worker ship: `git cherry origin/fast-track <sha>` prints nothing; CI: `origin/green/fast-track` moved past it.
- CI: the `ci_watch.py` hook (`.claude/settings.json`) prints `CI RED` every turn; `CI RED` = stop spawning, one worker on card `ci-<sha>`.
  `gh` is NOT installed on JIS-NUC or DESKTOP-F7IU69N. Manual check: `python scripts/dev/ci_watch.py`. New research test files must be registered
  in run_all_tests / run_extra_tests.EXTRA (or skipped with a reason, B150, gate step 3gd); study scripts need a `wiring_registry.json` entry.
- `tasks.py` has no host field: `lane` carries it (JIS-NB, CODEX, DSA-NUC, SONNET, HAIKU). Ready list: `tasks.py list | grep ready`.
  Cards that change the live tree or scheduled tasks (nb-*) are operator-side. A card file can hold a hidden HOLD `note` that `tasks.py brief` omits: read it first.
- Workers run `python <main checkout>/scripts/dev/sync.py start <slug>` and work only in the printed WORKTREE (app worktrees can be stale).
- Codex lab: `codex_run.py` merges origin/fast-track before it picks. A skipped card is un-skipped by a REOPENED row in
  F:/codex_home/lab_runs/runs.jsonl (outside git). A brief must name its data path (F:/MTS/data/bigtrade/cache/perp/klines_1h.npz) or the build ends BLOCKED.
  Status from NUC: `printf 'Set-Location F:/MTS/mts-codex-lab; python scripts/dev/codex_run.py status\n' | ssh -i ~/.ssh/nuc_gate -o BatchMode=yes e-ngineers@192.168.29.110 ps`.
  Keep 8+ ready luna/medium build cards; repair skipped or BLOCKED ones.
- `traffic_report.py` takes only an hours number (no --since). test_auto_deploy.py and test_sync.py live in `scripts/dev/`. Heredocs in Bash can be denied: use a .py file.
- Research Map: `Artifact read` first, edit DATA (the one `const DATA = ` line) in the saved copy by script, write `system/artifacts/research_map.html`,
  republish with `url`; never an old saved copy. Setup requests live in the tab "Setups & story" (DATA.story, SETUP_CATALOG.md; kind question|task|backtest + `setupId`).
  Backtest = fee check at the stated stop first (fee R = 0.14% / stop%), then PRE_REG on DEV only. Fabio home-market chain stays paused.
- Thread cleanup (hard rule): a finished session marks itself completed (`mark_completed`); the coordinator marks each worker the moment its ship is verified.
- 5-hour window: under 60 % normal; 60-70 % crucial only; 70-80 % coordinator only; 80 %+ stop (weekly: Pacing section). Fix, don't analyse: when the operator complains, fix the cause in the same turn, report in 1-2 lines; put this in every worker brief.
- A worker that merges late hits VERDICTS.csv and wiring_registry.json conflicts: union both sides.

## Session log (newest first; one line each, last 5)
- SUPER-LENOVO-1019b (2026-10-19, Sonnet coordinator, 2 Agents): chunk 2 landed (4e88b6d1); gate-fix 6efd40e0 passed the full gate only with MTS_GATE_JOBS=2 and no concurrent ship; 3lh/3cx/4d = load timeouts, 5b = py3.14 exit-5 bug; chunk 3 f9497e45 and part a b9c448c7 left unshipped by operator stop. Lesson: on this laptop run ONE ship at a time with MTS_GATE_JOBS=2 and check for other sync.py ship processes first; start_session is refused on session-started turns, use Agents.
- SUPERLOOP-NB-1019 (2026-10-19, Opus one-time agent, Sonnet + Haiku review Agents): five-hour loop on every device/login: `supervisor.py plan` (pacing vs weekly room, heartbeat, shard over live supervisors, one owner per lane, DSA down flag, nuc_wake gate) and `supervisor.py handover`; SUPER_LOOP.md replaces TANDEM_3LOGIN.md; role v3. Lesson: pacing in prose drifts; a T0 command per wake does not.
- TANDEM-NB-1019 (2026-10-19, Sonnet one-time agent, 2 review Agents): three Supervisors at once (A/B/C); `mts_signal.py budget`, `tasks.py dispatch --login/--logins` shards cards, `supervisor.py tick` shows peers; one-line start; 5 h regime in roles/supervisor.md v2; TANDEM_3LOGIN.md. Lesson: the claim is the lock, but without a shard three supervisors start the same top cards.
- DOCTOR-NB-1020 (2026-10-20, Sonnet one-time agent, 2 review Agents): roles 11 -> 7 (Traffic_Controller folded into Pipeliner, Q&A_Helper + Network_Admin_Guy -> Admin_Guy on Haiku high with backlog intake, Artifacts_Guy -> 1985Artifacts_Guy; old names stay aliases in role_loader.py), location wording fixed (Eagle_Eyes runs anywhere via live_mirror brief, super session any device/login), `traffic.py budget` = SPEND per login. Lesson: an alias list in code (ALIASES) keeps old pinned sessions working across a rename.
- DOCTOR-NB-1019 (2026-10-19, Opus one-time agent, 2 review Agents): roles review; ROLES.md pin table -> 'runs anywhere; needs; at most one' (role_loader checks no host), super-session prompt line 1 now `You are Supervisor.` (the old line loaded no role), RELAY.md retired parts marked, MTS Home gets 'How to use MTS' (6 recipes). Lesson: two entry points for one role drift; one paste line each.


## Start (operator: open a new session, model Sonnet unless you name Opus (WORKERS.md rule 6), paste the prompt below)
The coordinator, on its first turn: `get_usage` (stop if the Pacing state is THROTTLE), read STATUS.md and NEXT_SESSION.md, run the
Session_Planner (rule 14), then spawn. No relay stop/resume or heartbeat: the relay and its watchdog are RETIRED (SCHEDULING_POLICY.md).

## End
Drain: every worker shipped (`git cherry` empty) or its partial work handed over in NEXT_SESSION.md; archive finished workers;
`get_usage` written into the hand-over note; refresh the operator's Research Map (`system/artifacts/research_map.html`, edit its DATA,
republish to claude.ai/artifact/9nqpZeMeEehadoBoYopZU3 from the jishusharma1985 login); one line to the operator.

## Pacing (when no super session runs) - state from the weekly meter
`f` = fraction of the week elapsed since the last weekly reset, `U` = Weekly all-models % used.
| State | Condition | What runs |
|---|---|---|
| SPEND | U < 100 f - 10, or less than 24 h to the reset with U < 85 | super session worth starting; Fable cards allowed (operator starts them) |
| NORMAL | between | (relay and Haiku dispatcher RETIRED 2026-10-17, see SCHEDULING_POLICY.md) Sonnet builders, coordinator dispatches |
| THROTTLE | U > 100 f + 5, or the 5-hour window > 80 % | only model-free work: Codex lab, DSA desk, CI |
The meter is only readable from an App session (`get_usage`), one login at a time (no CLI or headless route exists: `claude --help` has no usage command, `claude auth status` shows the login only, `/usage` is interactive). The coordinator writes its login's reading to
`~/.claude/mts-budget.json` (per machine, not in git); the gate treats a reading older than 6 h as NORMAL.
**Supervisors (2026-10-19):** `supervisor.py plan` sends this line with extra heartbeat fields every wake and paces the window from it (SUPER_LOOP.md).
**All logins at once (2026-10-20):** every top-level session sends its login's reading at start with `python scripts/dev/mts_signal.py send "BUDGET login=<A|B|C> 5h=<n>% week=<n>% reset=<weekly reset UTC YYYY-MM-DDTHH:MMZ>" --to all --kind note`; `python scripts/dev/traffic.py budget` (Pipeliner runs it) takes the newest line per login and prints SPEND / NORMAL / THROTTLE per login plus overall by the table above (a line older than 6 h counts NORMAL; a login with no line is listed as missing).

## Prompt: start a super session (one line; permission mode bypass or auto, model Sonnet)
```
You are Supervisor. Login <A|B|C>. <your tasks>
```
Everything else loads by default: the hook injects `roles/supervisor.md` (banner `ROLE LOADED: Supervisor ...`), which runs `supervisor.py plan` every wake (pacing, heartbeat,
card shard, lane owners, hand-over time). Login letter = the account signed in (A jishu.sharma, B jishu.awgp, C jishusharma1985). Design, three logins at
once, fit table, failure modes: SUPER_LOOP.md. The lines rules 11-14 ask the prompt to carry now live in the role file (same words, short):
Rule 11: any diff touching the live path, gates, promote.py, prereg_gate.py or decision numbers gets an independent Sonnet review Agent (diff only) before ship.
Rule 12: spend the window before it resets, inside the weekly cap per login (`supervisor.py plan` computes slots and mode).
Rule 13: a defect blocks only cards that read its output; release holds that name no defect.
Rule 14: Session_Planner (roles/session_planner.md) as a foreground Sonnet Agent refines cards; never dispatch raw/refined cards. (The old multi-line prompt is retired 2026-10-19; its rules are rules 11-14 above and the role file.)

## Prompt pattern: any worker or Fable session that must not stop
Lead with: "Run with zero operator input: never ask; on any open question take the most conservative default, write it as
`DECISION (OURS): ...` in the deliverable, and continue." Then: the task file on origin/fast-track, the DONE-when, the hard limits
(testnet only, no secrets, no live tree or processes, no VALIDATION/HOLDOUT reads unless the card says so; rule 11 review Agent before ship when the diff touches live path, gates, promote.py, prereg_gate.py or decision numbers), a budget stop
(+N weekly points), and a reply limit (at most 5 lines). Model and effort are set in the App before pasting; the prompt cannot set them.
Used for the Fable pilot 2026-10-15 (FABLE_PILOT_PROMPT.md).
