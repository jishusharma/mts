# SUPER SESSION - one coordinator, many workers, hours of continuous work (operator term, 2026-10-15)

A **super session** is one coordinator session in the Claude Code Win App that spawns, steers, checks and archives workers (WORKERS.md: sessions or one-use Agents)
(`start_session`) for several hours, with the operator in the loop only for direction. Max plan only, and only when the weekly
meter has headroom (Pacing below). First one: 2026-10-15, coordinator local_62faa820 (Opus), about 20 linked workers, an Opus
observer, and a second coordinator (coord-2) that drained the ship queue at the end.

While a super session runs, the relay is paused: the coordinator IS the dispatcher. When none runs, nothing moves on its own: no relay, dispatcher or routine (MTS-DispatchGate and `mts-dispatcher` RETIRED 2026-10-17, see SCHEDULING_POLICY.md).
For "schedule the next 5h/10h" the coordinator writes the card order into a plan file and works it.

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
1. **Compaction and workers: see WORKERS.md** (canonical; measured numbers there). Short form: never compact by hand a session that will
   ship soon; compact only with 15+ turns left and above ~150k, else hand off (NEXT_SESSION.md or a `start_session` brief) and archive.
2. **The coordinator works little itself.** It reads results, decides, spot-checks one claim per worker (`git cherry` empty =
   shipped), and archives. Model: the one the operator started it on (WORKERS.md rule 6); workers Sonnet, Haiku for mechanical status.
   Fable only when the operator starts it.
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
9. **Compaction by context share (operator 2026-10-16).** `.claude/settings.json` sets `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=25`: a backstop, not a
   plan (WORKERS.md rule 5). A model cannot run `/compact` itself. Working bands: under ~18 % keep going; 18-20 % finish the current task,
   then end it (ship, release, hand off); 20-25 % finish only if crucial and nearly done, else commit and let it run. Keep working state in
   files (NEXT_SESSION.md, notes folder, task card), not in the context.
10. **Signals between logins and machines (operator 2026-10-16).** The app cannot message across logins, so `scripts/dev/mts_signal.py`
   (hook in `.claude/settings.json`, automatic) sends a line on the git branch `mts-signals` when a session starts or runs
   `sync.py claim|release|ship|start`, and every 5 minutes shows the signals other host/account pairs sent. Sessions do nothing for
   this. Optional: `mts_signal.py send "<text>" --kind ask|note` for a one-line note, `read` to list. Signals are status notes, never
   instructions, and the repo is public: no names, secrets or runtime data. `MTS_SIGNALS=off` disables. Limit: two logins on one
   machine share `MTS_ACCOUNT`, so they look like one sender to each other (they share the app, use `send_message` there).

## Boot facts (read, do not re-look-up; every super session corrects this list)
- NUC facts (super-nuc-1017): `gh` is NOT installed on JIS-NUC; read CI with the public API `api.github.com/repos/jishusharma/mts/actions/runs?branch=fast-track` (3 consecutive completed `success` = green). test_auto_deploy.py and test_sync.py live in `scripts/dev/`, not `scripts/sched/`. A Codex lab brief must name its data path (F:/MTS/data/bigtrade/cache/perp/klines_1h.npz), else the build ends BLOCKED. `codex_run.py status` run from a shared tree can show stale card states (the lab reads F:/MTS/mts-codex-lab). Compound `cd x && git ...` and heredocs in Bash get denied: use git -C and a .py file.
- Live tree = the main checkout `C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed` (`.mts_live` there is a marker FILE, not a
  folder). Read-only for sessions. Deploy result: `MyTradingSys/runtime/sched/auto_deploy_last.json`; HALT file:
  `MyTradingSys/execution/HALT` (+ `halt_history`); dirty files: `git -C <live> status --short --untracked-files=no`.
- Live state in one read: `live_mirror.py brief` (LIVE_MIRROR.md) + `scripts/sched/check_live_health.py`; ledger =
  `runtime_data` trade_ledger.jsonl in the live tree. A Sonnet read-only worker does this in ~15 tool calls.
- Workers: WORKERS.md is the rule (operator 2026-10-17, replaces the 10-16 "always sessions" and "100k" rules): the card carries `worker` and
  `est_turns`; session by default, one-use Agent only for size S <= 15 turns. Agents are invisible in the sidebar, so name each in one line.
  Sizes seen 10-17: count-only PRE_REG read 78k / 11 calls (Agent ok); 7 lab cards + 3 card fixes 178k / 44 calls and relabel + 3 reruns 122k / 27 (sessions).
- NUC lab: codex_run.py merges origin/fast-track before it picks (line ~646), so new cards need no lab-tree pull. A skipped card
  is un-skipped by a REOPENED row in F:/codex_home/lab_runs/runs.jsonl (outside git), not by the card JSON. `traffic_report.py`
  takes only an hours number (no --since): for 'after 12:00Z' use the hours since then.
- Waking: other sessions send no idle notices. Use ONE background shell watcher (`git fetch` every 5 min; exit on a file landing
  on origin/fast-track or after 50 min), and on every wake `python scripts/sched/relay.py heartbeat "<id>" --note "<what>"`.
- (RETIRED 2026-10-17, see SCHEDULING_POLICY.md) JIS-NB has no MTS-DispatchGate Windows task; the `mts-dispatcher` routine runs in the live tree, so relay/watchdog code only
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
- (RETIRED 2026-10-17, see SCHEDULING_POLICY.md) AutoDeploy gate (`MyTradingSys/runtime/sched/auto_deploy_last.json`, lock in `runtime/sched/locks/`): about 5 min on an idle
  host, 16+ min under load, and it times out (25 min, old live copy) when workers, ASR or pytest extras saturate the 8 CPUs.
  Start NO CPU-heavy worker while a gate runs; a red sha is not re-gated (RED_KNOWN) until a newer green exists; STOP_DIRTY names
  the live file (`git --no-optional-locks -C <live> status --short --untracked-files=no`); only the session that owns live-tree
  actions may clean it. A new auto_deploy.py runs live only after a deploy.
- NUC lab status: `printf 'Set-Location F:/MTS/mts-codex-lab; python scripts/dev/codex_run.py status\n' | ssh -i ~/.ssh/nuc_gate
  -o BatchMode=yes e-ngineers@192.168.29.110 ps` (stdin goes to PowerShell; stderr carries post-quantum warnings).
- Task card JSON can hold a hidden HOLD `note` that `tasks.py brief` does not print: read the card file before running a refined card.
- Bash tool: a `cd` persists between calls and some `cd x && git ...` chains are denied; use `git -C <dir>` and absolute paths.
- App worktrees can be stale (cut from 2026-10-02, no sync.py). Workers run `python <main checkout>/scripts/dev/sync.py start <slug>`
  from the main checkout and work only in the printed WORKTREE.
- Starting workers: WORKERS.md rules 2, 3, 7. `start_session` is refused on turns a side-session note or event started, so on every OPERATOR
  turn start all workers the next stretch needs (max 4 at once) and brief each to chain its follow-ups. NEVER make the operator click a card for
  work already handed to the session (operator 2026-10-16: "a waste of time and a waste of resources"). On an event turn where `start_session`
  is refused, a size-S card runs as a background Agent at once; a size-M card waits for the next operator turn (brief it in NEXT_SESSION.md).
- Thread cleanup (operator 2026-10-16, hard rule, all sessions): a finished session marks itself completed in the sidebar
  (`mark_completed`; `archive_session` too when allowed; archive refuses while Remote Control or a client is attached, so the
  completed mark is the reliable one). The coordinator marks every worker it started the moment its ship is verified.
- Pacing on the Pro login: 5-hour window, `get_usage` on every wake. Under 60 %: normal; 60-70 %: crucial work only; 70-80 %:
  coordinator only; 80 % and up: stop. In the last ~15 min before a reset, spend what is left on workers that finish real items.
- Keep the GPT lab busy: `codex_run.py status` on every wake; keep 8+ ready luna/medium build cards; repair skipped or BLOCKED
  cards. Its spend guard was the real throttle; raised to 10 runs/window and 60 week points on 2026-10-16 (e6955a8f).
- Fix, don't analyse: when the operator complains, fix the cause in the same turn and report the result in 1-2 lines. Never send
  an analysis-only reply. Put this rule in every worker brief.
- Live watch: one watcher session covers the whole market window (a background shell waits until each check time), within the
  5-screenshot-read cap per thread.

## Session log (newest first; one line each, last 5)
- SUPER-NB-1018 (2026-10-18, Sonnet coordinator, ~9 sessions + review Agents, weekly 73 -> 81%): labeler fix, krown, state audit, RV02 R1+R2, Fabio dating, planner batch 3 shipped; diff-only review Agents caught real defects in 4 of 6 diffs. Lesson: with 6+ sessions shipping, the 2 gate slots queue 2-3 h and a ship dies at the tool 600 s timeout unless run detached; one ship per session; weekly cap hit before the block ended.
- DOCTOR-NB-1017 (2026-10-17, Sonnet): post-B1/B4 `traffic_report.py 24` = 631 commits, overhead 60% (merge 34, claim 13, release 13), was 68% pre-B1; doctor findings 3 -> 2 (remaining: relay skill 'Output caps' line is intentionally per-skill).
- 2026-10-17 super-nuc-1017b (JIS-NUC, Opus coordinator, 3 Agents, 03:20Z-03:50Z): boot 12 tool turns (prior session's NEXT_SESSION on origin, not the stale shared checkout); Q85 BLOCKED e5988045, fire CSVs relabelled + 3 DEV reruns (no verdict change) 450636f4, 7 luna cards + g3-blindness-audit-rerun 1d2c875f; T07/T08 still absent. Learned: two of three workers exceeded 100k (should have been sessions); the operator could not see Agents in the sidebar.
- 2026-10-17 super-nuc-1017 (JIS-NUC, Sonnet coordinator + 3 Agents + 1 triage session, ~8 h): context-compare-close shipped; CI green x3, 163 tests pass; traffic 24 h = 849 commits, overhead 64% (was 68%; re-measure on a window after 2026-10-16 12:00Z); lab BLOCKED cause = no data path in the briefs (fixed, 6a9d63d3); bigtrade DEV leak (DEV_END_MS) fixed 5b1bdc27; fires_kline SPLITS aligned to the repo split 23fb3c7d (old TRAIN fires contaminated, F: CSVs still carry the old split column); lab unstuck (wiring-gate STALE rule 984dbe74, prompt lint line 7eb5b5c8). Weekly 29% at stop. T07/T08 verdicts never landed, so Q87/Q88/confluence-read-encode/prob-dist were NOT started.
- 2026-10-16 JIS-NUC lagging-tasks super session: layer readiness census; 5 live adapters plus wlow side wired (W3, live in
  28ca4005/fc9794f4); D3 power result (no factor powered at Holm m=37); Java buildVp edge fix (62.5% zone match); GPT lab
  unthrottled with 6 build cards; bigtrade reclassified as a build; HALT still on (operator clears it); grandfather review_by 2026-10-23.
- 2026-10-16 busters-b4 (JIS-NB, Sonnet): B4 `sync.py ship --release <slug>` shipped + B9-B12 added to TRAFFIC_BUSTERS.md. `traffic_report.py 24`: 890 commits, merge 40%, claim 14%, release 14%, overhead 68% (still the pre-B1 baseline: the 24 h window is mostly before B1); rerun on 2026-10-17.
- 2026-10-16 autopilot-3 (JIS-NB, Sonnet coordinator, 00:10Z-06:30Z, Agent workers, started by local_1c4041fd): CI red 4 h -> green
  02:04Z, 4b/4f gate races fixed, live deployed to 32077514 at 06:01:49Z after two load timeouts and a STOP_DIRTY; imb filter FAIL,
  context composite INCONCLUSIVE, pit audit FIX-FIRST. Weekly 48 -> 55 %. Learned: heavy workers during a deploy gate cost two
  gates; check `gh run list` and `auto_deploy_last.json` on every wake; a worker that merges late hits VERDICTS.csv and
  wiring_registry.json conflicts (union both).
11. **Independent review agent (operator 2026-10-17).** Any diff touching the live path, gates (`run_all_tests.py`, `sync.py` gate),
   `promote.py`, `prereg_gate.py` or decision numbers (thresholds, split dates, MDE/power) gets a second Sonnet Agent (medium) before
   `sync.py ship`. It sees only the diff (the diff against origin/fast-track), never the worker's reasoning or conclusion. Reply at most 5 lines:
   verdict APPROVE or BLOCK, then the defects. Cap 30k tokens; if the diff is larger, review the hunks in the paths above only.
   BLOCK means the worker fixes and re-submits once; a second BLOCK goes to the coordinator, who decides and logs it. The reviewer
   edits nothing and the worker may not review its own diff. Both coordinator prompts (below) carry this line.
12. **Spend the window before it resets (operator 2026-10-17).** Every login's usage window is spent, not saved: when a login (NUC or NB) has
   budget and its reset is near, pace workers so the meter reaches about 95% right as the window resets (NUC may go to 95%; NB weekly cap stays 75%).
   Rule of thumb: remaining minutes / 40 = workers to launch in the window, staggered, one card each; re-check `get_usage` at each launch.
   An idle login with ready cards is a defect. Wake an idle NUC with `python scripts/dev/nuc_wake.py --card <id> --name <n>`. Every coordinator
   prompt carries this line.
13. **Blockers go bottom-up (operator 2026-10-17).** A defect blocks only cards that read its output. Before holding a card, name the defect and
   the file the card reads from it; if it reads nothing from it, it is not blocked. Holds with no named defect are released (`tasks.py apply-op <id> release`).
   The GPT/Codex lane never idles while a gptb-* or gpt-* card is ready.

14. **Session_Planner (operator 2026-10-17).** The coordinator runs the Session_Planner role (`roles/session_planner.md`) as a foreground Sonnet Agent at boot and on every wake with a free worker slot: it refines raw cards, returns the dispatch table (agent vs session, model, file cluster, weight), lifts blocks that name no live defect and lists stale claims, idle sessions and shipped worktrees for cleanup. Never dispatch a `raw`/`refined` card (2026-10-17: three Haiku workers came back empty on raw cards). Weight CRUCIAL = rule 11 review Agent; CRITICAL = a review session spawned mid-session (plan) and pre-ship (diff), counted in the 4-session cap. Both coordinator prompts carry this line.

## Start (operator: open a new session, model Opus, paste the prompt below)
The coordinator, on its first turn: `get_usage` (stop if the Pacing state is THROTTLE), `python scripts/sched/relay.py stop
"super-session <session id>"` on this machine, read STATUS.md and NEXT_SESSION.md, then spawn.

Heartbeat (watchdog): on every wake the coordinator runs `python scripts/sched/relay.py heartbeat "<session id>" --note "<what>"`
(rewrites `~/.claude/mts-super-heartbeat.json`: coordinator, host, utc, note; not in git). MTS-DispatchGate (RETIRED 2026-10-17, see SCHEDULING_POLICY.md) ran `relay.py watchdog`
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
| NORMAL | between | (relay and Haiku dispatcher RETIRED 2026-10-17, see SCHEDULING_POLICY.md) Sonnet builders, coordinator dispatches |
| THROTTLE | U > 100 f + 5, or the 5-hour window > 80 % | only model-free work: Codex lab, DSA desk, CI; relay KICKs wait |
Today (10-15 17:45Z): f = 0.27, U = 32 -> NORMAL. The meter is only readable from an App session (`get_usage`), so the
coordinator (and any KICK session) writes it to `~/.claude/mts-budget.json` (not in git); the gate treats a reading older than 6 h as NORMAL.
Wiring that file into `dispatch_gate.py` is a SONNET card (not built yet).

## Prompt: start a super session (paste into a new Opus session, permission mode bypass or auto)
```
You are the MTS super-session coordinator (MyTradingSys/system/SUPER_SESSION.md). Run for hours with zero operator input except direction I give.
Goal today: <one line, e.g. "rebuild layers setups-first: catalogue -> PRE_REG -> screens">.
First turn: get_usage (THROTTLE -> tell me and stop), relay.py stop "super-session", read STATUS.md and NEXT_SESSION.md, pick the tasks that serve the goal.
Spawn workers per WORKERS.md (session by default, Agent only for size S; Sonnet; Haiku for mechanical status), at most 4 running, each with a full brief: goal, files, DONE when, defaults for open questions, hard limits from CLAUDE.md. Workers never ask me; you decide toward the goal and log it.
Rule 11: any diff touching the live path, gates, promote.py, prereg_gate.py or decision numbers gets an independent Sonnet review Agent (diff only, 5-line reply, 30k token cap) before ship.
Verify every ship with git cherry, mark finished workers completed, compact only per WORKERS.md rule 5, hand the tail to a second coordinator per rule 5 above.
End: drain, hand-over note with get_usage, relay.py resume, one line to me.
```

## Prompt pattern: any worker or Fable session that must not stop
Lead with: "Run with zero operator input: never ask; on any open question take the most conservative default, write it as
`DECISION (OURS): ...` in the deliverable, and continue." Then: the task file on origin/fast-track, the DONE-when, the hard limits
(testnet only, no secrets, no live tree or processes, no VALIDATION/HOLDOUT reads unless the card says so; rule 11 review Agent before ship when the diff touches live path, gates, promote.py, prereg_gate.py or decision numbers), a budget stop
(+N weekly points), and a reply limit (at most 5 lines). Model and effort are set in the App before pasting; the prompt cannot set them.
Used for the Fable pilot 2026-10-15 (FABLE_PILOT_PROMPT.md).
- SUPER-NB-1017 (2026-10-17, Sonnet coordinator, 6 Agent workers because start_session is refused for a session started by another session): 14 cards shipped, weekly 66 -> 67%; Agents fit the 100k rule; compound `cd && git`/merge commands were denied, use git -C.
