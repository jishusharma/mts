# MTS - Claude Code sessions

Read first: `MyTradingSys/research/STATUS.md` (regenerate: `python scripts/dev/make_status.py`),
then `MyTradingSys/system/LESSONS_DIGEST.md` (rules only; full stories in LESSONS_LEARNED.md, read an entry when its rule touches your task); supervisor decisions: `research/fast_track_2026-09-27/SUPERVISOR_LOG.md`. Don't re-read handoff docs STATUS.md already summarises.
Chat-surface (DSA) behaviour lives in `DSA_SESSION_PROMPT.md`; this file is for code mode.
Parallel work (any machine, any account): `MyTradingSys/system/PARALLEL.md` - `sync.py start`, commit, `sync.py ship`.
Same-page check on either Claude account, and before ending a session: `python scripts/dev/sync.py where` (lists worktrees holding work not on origin/fast-track); commit + ship anything flagged.
Every session works in its own worktree: `sync.py start` makes one when the tree is shared/dirty and prints `WORKTREE: <path>` (work only there); `sync.py health` lists collisions (PARALLEL.md).
Start ritual for any account or device (full text in PARALLEL.md): `sync.py start` (prints open claims), pick ONE task from NEXT_SESSION.md,
`sync.py claim "<task>"`, work, `sync.py ship`, `sync.py release <slug>`, `sync.py where` clean.
Automatic hand-over to a fresh session (no operator input): `MyTradingSys/system/RELAY.md`; at the end of a task run `relay.py handoff` then `relay.py gate`, fire the task it names. Writing tasks into NEXT_SESSION.md: RELAY.md "Task list standard" (curated, one session each, `DONE when:`); `relay.py handoff` refuses a list that fails `relay.py lint`.
Layers (Tom, Fabio, RSI, CryptoCred, positioning, session, ...): ONE index per layer with spec, code, ledger, latest results, roadmap and open cards, for Claude and Codex sessions: `MyTradingSys/system/LAYERS.md` (pointers in `system/layer_index.json`; regenerate `python scripts/dev/make_layers_md.py`). A new layer, ledger or result report gets a pointer there in the same commit.
Task cards (refinement stage: raw idea -> ready task, Definition of Ready, Backlog on the Control Room): `MyTradingSys/system/TASK_REFINEMENT.md`; `python scripts/dev/tasks.py next` before picking work, `tasks.py new` for follow-ups you find.
Surfaces, budget and session naming: `MyTradingSys/system/SURFACE_POLICY.md`.
Live state off the desktop (NUC, laptop): `sync.py start` pulls the read-only mirror; `python scripts/dev/live_mirror.py brief` before any live read; say `mirror@<utc>` when you quote it (LIVE_MIRROR.md).

## What a CL prompt carries
- Prompt <= 30 lines.
- ONE-MESSAGE HANDOFF (operator 2026-10-10): NEXT_SESSION.md's block must run with zero operator input: defaults for every open question, tasks in order, Control Room checked by the session.
- No restated hard rules (this file has them).
- No restated state (STATUS.md has it).
- Continuous execution, no stop between tasks.
- SHORT SESSIONS (operator 2026-10-09): one session = one task. Hand off as soon as the task is done, or after 5 turns with
  the operator, or 15 tool turns (a session already starts at ~65k tokens, measured B172 2026-10-12; turns x that prefix is
  the cost), whichever comes first: finish the step, commit and `sync.py ship`, overwrite
  `system/NEXT_SESSION.md` (queue, what waits for the weekly reset, open questions, last commit), confirm `sync.py where`
  is clean, say so in one line, and stop. Live market analysis threads hand off after 5 screenshot reads.

## Standing rules for every account (operator 2026-10-09)
- Model default is Sonnet for sessions and subagents; Opus only when the operator names it. Subagents only when clearly needed, on Sonnet/Haiku. Cost is the priority.
- Two Claude accounts share one repo and one queue: whichever has budget takes NEXT_SESSION.md; never idle for a weekly reset.
- Claim before you work, release when shipped; a claim older than 24 h is stale, ask then release it.

## Work routing (cheapest tier that can do it; see research/fast_track_2026-09-27/WORKER_ROADMAP.md)
- T0 script > T1 Haiku > T2 Sonnet > T3 Opus. (Qwen NUC lane decommissioned 2026-10-01; AIBridge on desktop is the run-command surface.)
- Implementations go to Sonnet; tests derived from the spec, from Sonnet.
- Wait on the queue with one background shell, never a polling agent. Spot-check one claim per worker report.

## Surface (operator 2026-10-08, repeated)
- Claude Code Win App only. Never tell the operator to "use the CLI" or hand work back to them: run it here in bypassPermissions.
- A permission block is not a reason to stop: report the exact blocked call + why, try the allowed equivalent, keep going.
- Only if a task truly cannot run in the App (e.g. needs a process this App cannot reach) create a CLI task file
  `MyTradingSys/system/cli_tasks/<date>_<slug>.md` (exact commands, why forced, expected result) and say so in one line. Never stay silent.

## Quick answers (the operator is not a developer: do these, do not ask, do not re-investigate)
- Operator page = MTS Control Room (pinned artifact). Their questions/tasks arrive in its Inbox, verbatim; procedure `MyTradingSys/system/CONTROL_ROOM.md`. Ask the operator via a page decision, not chat.
- Push: never from the live tree (the folder holding `.mts_live`). `git worktree add ../mts-push -b <host>/<slug> HEAD` (reuse it if present),
  `git merge origin/fast-track` there (docs conflicts: take origin's text; STATUS.md: take origin's, regenerate),
  `python scripts/dev/run_all_tests.py --quick`, then `git push origin <branch>:fast-track`. `sync.py ship` does the same.
- CI/CD without the operator: `.github/workflows/ci.yml` gates every push (ubuntu AND windows) and moves `green/fast-track`;
  `MTS-AutoDeploy` (15 min) deploys only that SHA, stops on red; `MTS-DailyHygiene` writes the report STATUS.md embeds. Details,
  restart map, registration: `MyTradingSys/system/DEPLOY_RUNBOOK.md`. STATUS.md's `CI green:` line says RED when the tip has not
  gone green for an hour: then nothing deploys, and fixing CI is the first job of any session.
- Deploy to the live tree by hand only if that job is down (operator pre-authorised "just do it" 2026-10-09): if other sessions have uncommitted edits there, do NOT
  merge/stash. `git -C <live> checkout origin/fast-track -- <only the changed live-path files>`, run their tests, kill only that
  process; `loop-supervisor` restarts it in ~1 min. Java needs `mvn compile` + restart: leave until a window, say so.
- Git denies chained `cd x && git checkout/merge ...` in Bash: use `git -C <dir> <cmd>` as its own call.
- Machine off = stack down. `MTS-Supervisor` starts at logon (+90 s) and revives every aux process. Missed events are not replayed
  after an outage on purpose (no stale-signal trades); do not build catch-up.
- "How is Codex doing?" = `python scripts/dev/codex_run.py status` (also in STATUS.md, "Layer Lab (Codex)"). Codex works lane `CODEX` cards
  unattended on JIS-NUC (`MTS-CodexLab`, no Claude tokens); how it works, its limits and how to feed it: `MyTradingSys/system/LAYER_LAB.md`.
  A NEEDS A LOOK line is a NUC session's first job. Scoped research or backtest-code work goes to lane CODEX before a Claude session takes it.
- Runner output: `runtime_data/live_runner.log`. alert_rate_check candles: `scripts/dev/refresh_klines.py` runs daily before it.
- Local gate needs `pip install numpy` (Step 3p). Two `htf_context_live` loops = duplicate rows: keep one (shim parent + child = one loop).

## Gates (must pass before any commit touching the area)
- All offline: `python scripts/dev/run_all_tests.py` (`--quick` skips Maven + backtest).
- Extractions: `python scripts/dev/verify_extract_quotes.py <extract.md>` (quotes verbatim + GPS position).
- New tests must fail on the pre-change code at least once.
- Formulas: expected numbers in test plans come from `MyTradingSys/backtest/layers/FORMULAS.md` (canonical
  definition + source), computed independently - never from existing code. OUTPUT_TOKENS must fit the whole reply.

## Hard rules
- Share work only through `python scripts/dev/sync.py ship` (merges origin/fast-track, gates code, pushes fast-track).
  Cloud containers (claude.ai/code, harness branch `claude/...`): start from origin/fast-track, push the harness branch, open a PR
  into fast-track; CI auto-merges it when green (PARALLEL.md). `python scripts/dev/cloud_setup.py` installs the gate deps and prints the state.
  Never commit to master, never rebase/reset/force-push. Never work in the live tree (it holds `.mts_live`).
- Commit body carries `Result: <what works now / the number>` - the operator reads `sync.py news`, not diffs.
- Other sessions' uncommitted files are not yours: don't stash, clean, revert or report them.
- Testnet only (Deribit test); never mainnet; never read `.secrets/`, `.env` or keys.
- Windows: write files with `newline='\n'`; long patches go in a .py script, not a heredoc.
- Tom is core; every other indicator system is a separate layer (PROJECT_VISION), never a Tom filter.
- Provenance (operator 2026-09-30): every engine/layer parameter, gate and label comes from that trader's own words
  (transcript quote + file:line) or it does not exist. Unsourced = NO-SOURCE: flag, then remove or replace; never tune it.
- Whoever sets AUTO_PAUSE logs owner + expected end; each wake clears or escalates an overdue pause.
- Adding a timeframe or layer family: grep every TF/family map (alert_rate_check, account routing, audits).
- The live tree on JIS-NB runs the testnet system (auto_trader, position_manager, daily_loss_monitor,
  live_runner_cli). Code reaches it only by the supervisor's deploy (stop, `git merge --ff-only origin/fast-track`,
  gate, restart). Builders never stop/restart processes, touch HALT files or open trades.
- Live-path changes need a test for restart/reset state, non-trade balance moves and API errors; safety
  checks fail closed.
- Never conclude from truncated output (`cut`, `head`, tail of a log); parse the real format, then count.
- Backups/rejects: archive with `python scripts/dev/declutter_backups.py --apply` (moves, never deletes).
- Never add to `.git/info/exclude`; an ignore that matters goes in `.gitignore` and ships.

## Screenshots (the operator's charts and random images are evidence, not decoration)
- A hook saves every pasted image and prints `[SCREENSHOT INTAKE] ... SAVED` with ids; no notice = nothing new landed. On the notice: `python scripts/dev/shot.py classify <id> --kind ... --why "<operator's meaning>"`, read, `shot.py read`, `shot.py done`. Never leave a shot `new` at session end (`shot.py status`, also in STATUS.md).
- Charts of one moment are one set, read together; every claim is MATCH / MISMATCH / NOT_IN_DATA against files you read; file the last two. Process and per-surface rules: `MyTradingSys/methodology/screenshot_intake.md`. Project map (which group an item belongs to): `MyTradingSys/system/PROJECT_MAP.md`.

## DSA delegation and inbox (operator 2026-10-09)
- Session start: after `sync.py start`, read the Control Room Inbox/decisions (ArtifactData, CONTROL_ROOM.md) only if your task aligns; fetch full text of aligned items only.
- Run-and-report work (backtest reruns, stratifying, inventories, source hunts, gate runs) goes to DSA: `desk.py post "<t>" --need "<commands>" --done-when "<obs>" --target DSA`. Routing and operator guide: `MyTradingSys/system/DSA_DELEGATION.md`. Low on budget: post the rest to DSA, then hand off.

## Interview Prep Notes
- When a thread or project message says "Note this for InterviewPrep", append one entry to `/mnt/project-files/interview_prep/NOTES.md` with date, source link, and status "not yet exported".
- Jis manually decides when to push entries to F:\Interview Prep project.
- This captures lightweight insights from MTS and CBP work without automation overhead.
