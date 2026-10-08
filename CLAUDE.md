# MTS - Claude Code sessions

Read first: `MyTradingSys/research/STATUS.md` (regenerate: `python scripts/dev/make_status.py`),
then `MyTradingSys/system/LESSONS_LEARNED.md`; supervisor decisions: `research/fast_track_2026-09-27/SUPERVISOR_LOG.md`. Don't re-read handoff docs STATUS.md already summarises.
Chat-surface (DSA) behaviour lives in `DSA_SESSION_PROMPT.md`; this file is for code mode.
Parallel work (any machine, any account): `MyTradingSys/system/PARALLEL.md` - `sync.py start`, commit, `sync.py ship`.
Surfaces, budget and session naming: `MyTradingSys/system/SURFACE_POLICY.md`.

## What a CL prompt carries
- Prompt <= 30 lines.
- No restated hard rules (this file has them).
- No restated state (STATUS.md has it).
- Continuous execution, no stop between tasks.

## Work routing (cheapest tier that can do it; see research/fast_track_2026-09-27/WORKER_ROADMAP.md)
- T0 script > T1 Haiku > T2 Sonnet > T3 Opus. (Qwen NUC lane decommissioned 2026-10-01; AIBridge on desktop is the run-command surface.)
- Implementations go to Sonnet; tests derived from the spec, from Sonnet.
- Wait on the queue with one background shell, never a polling agent. Spot-check one claim per worker report.

## Surface (operator 2026-10-08, repeated)
- Claude Code Win App only. Never tell the operator to "use the CLI" or hand work back to them: run it here in bypassPermissions.
- A permission block is not a reason to stop: report the exact blocked call + why, try the allowed equivalent, keep going.
- Only if a task truly cannot run in the App (e.g. needs a process this App cannot reach) create a CLI task file
  `MyTradingSys/system/cli_tasks/<date>_<slug>.md` (exact commands, why forced, expected result) and say so in one line. Never stay silent.

## Gates (must pass before any commit touching the area)
- All offline: `python scripts/dev/run_all_tests.py` (`--quick` skips Maven + backtest).
- Extractions: `python scripts/dev/verify_extract_quotes.py <extract.md>` (quotes verbatim + GPS position).
- New tests must fail on the pre-change code at least once.
- Formulas: expected numbers in test plans come from `MyTradingSys/backtest/layers/FORMULAS.md` (canonical
  definition + source), computed independently - never from existing code. OUTPUT_TOKENS must fit the whole reply.

## Hard rules
- Share work only through `python scripts/dev/sync.py ship` (merges origin/fast-track, gates code, pushes fast-track).
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

## Interview Prep Notes
- When a thread or project message says "Note this for InterviewPrep", append one entry to `/mnt/project-files/interview_prep/NOTES.md` with date, source link, and status "not yet exported".
- Jis manually decides when to push entries to F:\Interview Prep project.
- This captures lightweight insights from MTS and CBP work without automation overhead.
