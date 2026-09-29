# MTS - Claude Code sessions

Read first: `MyTradingSys/research/STATUS.md` (regenerate: `python scripts/dev/make_status.py`),
then `MyTradingSys/system/LESSONS_LEARNED.md`; supervisor decisions: `research/fast_track_2026-09-27/SUPERVISOR_LOG.md`. Don't re-read handoff docs STATUS.md already summarises.
Chat-surface (DSA) behaviour lives in `DSA_SESSION_PROMPT.md`; this file is for code mode.

## Work routing (cheapest tier that can do it; see research/fast_track_2026-09-27/WORKER_ROADMAP.md)
- T0 script > T1 Qwen on the NUC (`scripts/worker/queue_tool.py pack|verify|status`) > T2 Haiku > T3 Sonnet > T4 Opus.
- Qwen: implementations and transcript extractions only. Tests come from Haiku/Sonnet, derived from the spec.
- Wait on the queue with one background shell, never a polling agent. Spot-check one claim per worker report.

## Gates (must pass before any commit touching the area)
- All offline: `python scripts/dev/run_all_tests.py` (`--quick` skips Maven + backtest).
- Extractions: `python scripts/dev/verify_extract_quotes.py <extract.md>` (quotes verbatim + GPS position).
- New tests must fail on the pre-change code at least once.
- Formulas: expected numbers in test plans come from `MyTradingSys/backtest/layers/FORMULAS.md` (canonical
  definition + source), computed independently - never from existing code. OUTPUT_TOKENS must fit the whole reply.

## Hard rules
- Branch `fast-track`; never commit to master, never push/merge/rebase/reset.
- Staged work is `<file>.new` (gitignored). Promote: back up to `.pre_<tag>`, rename, re-gate, then commit.
- Testnet only (Deribit test); never mainnet; never read `.secrets/`, `.env` or keys.
- Windows: write files with `newline='\n'`; long patches go in a .py script, not a heredoc.
- Tom is core; every other indicator system is a separate layer (PROJECT_VISION), never a Tom filter.
- The working tree runs the live testnet system (auto_trader, position_manager, daily_loss_monitor,
  live_runner_cli): never edit a file they import in place, never stop/restart them, never touch HALT files
  or open trades. Every builder brief touching `MyTradingSys/execution/` or `layers/alerts/` repeats this.
- Live-path changes need a test for restart/reset state, non-trade balance moves and API errors; safety
  checks fail closed.
- Never conclude from truncated output (`cut`, `head`, tail of a log); parse the real format, then count.
- Backups/rejects: archive with `python scripts/dev/declutter_backups.py --apply` (moves, never deletes).
