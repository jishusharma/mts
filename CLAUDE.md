# MTS - Claude Code sessions

Already loaded: do not Read this again. Code mode only (DSA chat: `DSA_SESSION_PROMPT.md`; Codex: `AGENTS.md`).

## Boot (every turn re-reads the context)
1. `python scripts/dev/sync.py start <slug>`: in a lane tree (mts-app/relay/dsa) it switches to branch <host>/<slug>; elsewhere it prints `WORKTREE: <path>` (work only there, never the live tree).
2. Read `MyTradingSys/research/STATUS.md` (regenerate: `python scripts/dev/make_status.py`), not what it summarises; `LESSONS_DIGEST.md` only for live-path or backtest work. RED `CI green:` line: fix CI first (pinned `ci-<sha>` card).
3. ONE task from NEXT_SESSION.md (relay KICK: `relay_prompts/relay_session.md`) or `tasks.py next`; `sync.py claim "<task>"`, work, `sync.py ship --release <slug>`, `sync.py where` (own tree clean).
4. Hand-over (RELAY.md): after overwriting NEXT_SESSION.md run `python scripts/sched/relay.py handoff --file MyTradingSys/system/NEXT_SESSION.md --go` (or `--stop "<why>"`), `sync.py ship`, `relay.py unlock` (not after `--stop`). The block must run with zero operator input (defaults for open questions); no stop between tasks.
5. SHORT SESSIONS: one session = one task; hand over when it is done, after 10 operator turns or 40 tool turns, whichever first (commit, then steps 3-4, one line, stop). Live market threads: after 5 screenshot reads.
6. Task shipped: mark your own session completed in the sidebar (`mark_completed`); coordinators mark their workers (SUPER_SESSION.md).

## Cost and routing
- Interactive sessions and subagents: Sonnet (implementations, spec-derived tests), Opus only when the operator names it; relay/dispatcher sessions run on the routine model. Haiku for mechanical work; workers: one-use Agent under 100k tokens, else a session (SUPER_SESSION.md). Wait on a queue with one background shell; spot-check one worker claim.
- No routine questions or "want me to?" offers for implied work: do it now, full depth. Free public market data and YouTube: pre-approved.
- T0 script first, then by card lane (HOW_MTS_RUNS.md): run-and-report goes to DSA (`desk.py post ... --target DSA`; low on budget: post the rest to DSA, then hand over).
- Logins share one repo and queue (CLOUD_ACCOUNTS.md): whoever has budget takes NEXT_SESSION.md; never idle for a weekly reset.
- Surface: Claude Code Win App only; never tell the operator to "use the CLI" or hand work back. A permission block is not a reason to stop: report the exact blocked call, try the allowed equivalent.

## Gates (before any commit touching the area)
- `sync.py ship`: smoke gate (live-path or unknown paths = all `--quick`; `--full`); CI + green-only deploy gate the rest. Full: `python scripts/dev/run_all_tests.py` (`--quick`: no Maven/backtest). Extractions: `python scripts/dev/verify_extract_quotes.py <extract.md>`.
- New tests must fail on the pre-change code at least once.
- Formulas: expected numbers come from `MyTradingSys/backtest/layers/FORMULAS.md`, computed independently, never from existing code. OUTPUT_TOKENS must fit the whole reply.

## Hard rules
- Share work only through `sync.py ship`; cloud containers open a PR into fast-track. Never commit to master, never rebase/reset/force-push. No chained `cd x && git ...`: use `git -C <dir> <cmd>`.
- Commit body carries `Result: <what works now / the number>`. Others' uncommitted files: don't stash, clean, revert or report them.
- Testnet only (Deribit test); no mainnet orders/accounts (public market data OK: q-gap-c); never read `.secrets/`, `.env`, keys.
- Repo is PUBLIC (since 2026-10-11): never commit runtime/order/account data; MTS-Backup pushes only to local F:/MTS_backup.git; go private before mainnet.
- The live tree (`.mts_live`, JIS-NB) runs the testnet system and changes only by MTS-AutoDeploy (manual fallback: DEPLOY_RUNBOOK.md). Builders never deploy, stop/restart processes, touch HALT files or open trades. "Supervisor" = the MTS-Supervisor task (process revival only).
- Live-path changes need a test for restart/reset state, non-trade balance moves and API errors; safety checks fail closed. New timeframe or layer family: grep every TF/family map. Whoever sets AUTO_PAUSE logs owner + expected end in SUPERVISOR_LOG; each wake clears or escalates an overdue pause.
- Layers (operator 2026-10-13, replaces "Tom is core"): no fixed core. Tom, Fabio and every other system are layers (combine, filter or switch off); fee-net out-of-sample results decide what trades, never doctrine (PROJECT_VISION).
- Numbers (operator 2026-10-13): label each parameter SOURCED (trader's words, quote + file:line) or OURS (judgement or tuned). OURS is allowed: chosen on DEV, checked once on VALIDATION, holdout read once, variants in the trial ledger. Never call OURS the trader's.
- Anything off: report -> independent audit -> fix. Never conclude from truncated output (`cut`, `head`, log tails); parse the real format, then count.
- Windows: write files with `newline='\n'`; long patches go in a .py script, not a heredoc. The Bash tool strips backslashes: write paths/regexes with Write/Edit; Write decodes backslash-u escapes: use `chr()`; check CR with python bytes, not `grep -c`.
- Never add to `.git/info/exclude`: an ignore that matters goes in `.gitignore`.

## Where to look (`MyTradingSys/system/`)
| Need | Read |
|---|---|
| start, ship, claims, push fallback; hand-over, task cards | PARALLEL.md; RELAY.md, TASK_REFINEMENT.md |
| dev-time waste | TRAFFIC_BUSTERS.md |
| machines, logins, lanes, who may touch what; surfaces, names | HOW_MTS_RUNS.md, DEVICES.md, CLOUD_ACCOUNTS.md; SURFACE_POLICY.md |
| deploy, CI/CD | DEPLOY_RUNBOOK.md |
| layers (index); Codex lab | LAYERS.md; CODEX_START.md, LAYER_LAB.md |
| DSA, AIBridge; operator Inbox and decisions | DSA_DELEGATION.md, AIBRIDGE_LANE.md; CONTROL_ROOM.md |
| live state off the desktop (`live_mirror.py brief`, quote `mirror@<utc>`) | LIVE_MIRROR.md |
| add-a-layer rules, screenshots (`[SCREENSHOT INTAKE]` notice), hand deploy, Codex status, machine off, pages follow builds, `runtime_data/live_runner.log`, `declutter_backups.py --apply` | QUICK_ANSWERS.md |
