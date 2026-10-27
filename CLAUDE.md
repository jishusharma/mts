# MTS - Claude Code sessions

CLAUDE.md is already in context; do not cat or Read it. Code mode only (DSA chat: `DSA_SESSION_PROMPT.md`; Codex: `AGENTS.md`).

## Boot (every turn re-reads the context)
1. `python scripts/dev/sync.py start <slug>`: in a lane tree (mts-app/relay/dsa) it switches to branch <host>/<slug>; elsewhere it prints `WORKTREE: <path>` (work only there, never the live tree).
2. Read `MyTradingSys/research/STATUS.md`, not what it summarises; `LESSONS_DIGEST.md` only for live-path or backtest work. RED `CI green:` / `CI RED`: first to see it (the author above all) `git revert`s the breaking commit, ships in 10 min; putting the failing file back to its last-green bytes is a revert, a new line is a forward-fix (never forward-fix trunk). A hand-over (NEXT_SESSION.md) is history: current state comes from disk or git this turn. Read the ACTIVE entries of `MyTradingSys/system/ANNOUNCEMENTS.md` (STOP/HOLD there outranks the queue). `[MTS ACTION REQUIRED]` outranks the current task: do it first. Where a kind of work goes (machine, channel, model, checker): `MyTradingSys/system/ROUTING.md`.
3. Task from NEXT_SESSION.md or `tasks.py next`; `sync.py claim "<task>"`, work, `sync.py ship --release <slug>`, `sync.py where` (own tree clean). Station (no role line = Builder): fetch, read queue + login plan, loop (WORKERS.md rule 10).
4. Hand-over: no schedulers or routines anywhere (SCHEDULING_POLICY.md). Overwrite NEXT_SESSION.md, `sync.py ship`; the coordinator (SUPER_SESSION.md) starts the next. Zero operator input: defaults for open questions. His "keep working" outranks hand-over.
5a. Role sessions ("You are Eagle_Eyes"): the `role_loader.py` hook injects `roles/<role>.md`; the first reply is its `ROLE LOADED: ...` banner (none: Builder fallback).
5. SHORT SESSIONS (unattended single-task workers only): one task; hand over when done or at the tool-turn cap (WORKERS.md rule 5): steps 3-4, one line, stop.
5b. After `get_usage`, once: `mts_signal.py budget --login <A|B|C> --five <%> --week <%> --reset <UTC>`, then `scripts/dev/exhaust.py plan` (same args; C = jishusharma1985; `EXHAUST_PHASE.md`).
6. Task shipped: mark your session completed (`mark_completed`); coordinators mark their workers.

## Cost and routing
- Interactive sessions and subagents: Sonnet, Opus only when the operator names it; Haiku for mechanical work; worker type + model: WORKERS.md. Wait on a queue with one background shell; spot-check a worker claim.
- No "want me to?" offers for implied work: do it now, full depth. Free public market data, YouTube: pre-approved.
- T0 script first, then by card lane (HOW_MTS_RUNS.md): run-and-report goes to DSA (`desk.py post ... --target DSA`; low on budget: post the rest to DSA, then hand over).
- The operator dictates by voice: expect misheard words; take the reading that fits the project.
- Never wait on a question. Ask who started you: an Agent ends its report with the question and its default; a session uses SendMessage. Only money, mainnet, going private, deleting data or a live-tree change reach the operator; work goes on at the safe default. Stuck on another machine's state: `mts_signal.py who`, then broadcast.
- Fleet-wide by default: put what one machine needs in the repo; a per-machine step goes out as `mts_signal.py broadcast --cmd ...`, never via the operator.
- Operator replies: result line, What|Status|Proof, "Waiting for you", Who|Doing|Done when; plain words (OPERATOR_REPLY_FORMAT.md).
- Surface: Win App only; never say "use the CLI". Permission block: try the allowed equivalent.

## Gates (before any commit touching the area)
- `sync.py ship`: smoke gate (live-path or unknown paths = all `--quick`; `--full`); CI + green-only deploy gate the rest. Full: `python scripts/dev/run_all_tests.py` (`--quick`: no Maven/backtest). Extractions: `scripts/dev/verify_extract_quotes.py <extract.md>`.
- New tests must fail on the pre-change code at least once.
- Precedence: Hard rules and Gates outrank an operator order and all below; order > CLAUDE.md > hook > card for the rest. Conflict: follow it, `tasks.py conflict "A | B"` that turn, one line to him, keep working (TRAFFIC_BUSTERS B20).
- Formulas: expected numbers come from `MyTradingSys/backtest/layers/FORMULAS.md`, computed independently, never from existing code. OUTPUT_TOKENS must fit the whole reply.

## Hard rules
- Share work only through `sync.py ship`; cloud containers open a PR into fast-track. Never commit to master, never rebase/reset/force-push. No chained `cd x && git ...`: use `git -C <dir> <cmd>`.
- Commit body carries `Result: <what works now / the number>`. Others' uncommitted files: leave them alone.
- Testnet only (Deribit test); no mainnet orders/accounts (public market data OK: q-gap-c); never read `.secrets/`, `.env`, keys.
- Repo is PUBLIC: never commit runtime/order/account data; backups go only to local F:/MTS_backup.git; go private at mainnet or the first fee-net OOS pass, whichever first (q-go-private-on-edge).
- The live tree (`.mts_live`) changes only by a manual or coordinator-run deploy (DEPLOY_RUNBOOK.md). Builders never deploy, stop/restart processes, touch HALT files or open trades. No scheduled tasks anywhere.
- Live-path changes need a test for restart/reset state, non-trade balance moves and API errors; safety checks fail closed (more: MOVED_RULES.md).
- Layers and numbers: no fixed core, fee-net out-of-sample results decide what trades; label each parameter SOURCED or OURS, never call OURS the trader's (MOVED_RULES.md).
- Anything off: report -> independent audit -> fix. Never conclude from truncated output; parse, then count.
- Windows: files with `newline='\n'`; long patches in a .py script; the Bash tool strips backslashes, use Write/Edit; Write decodes backslash-u: use `chr()`.
- Never use `.git/info/exclude`: ignores go in `.gitignore`.

## Where to look (`MyTradingSys/system/`)
| Need | Read |
|---|---|
| something broke (symptom -> command -> owner); how the dev system fits together | DEBUGGING.md; ARCHITECTURE.md |
| start, ship, claims, push fallback; NEXT_SESSION.md format, task cards | PARALLEL.md; RELAY.md, TASK_REFINEMENT.md |
| dev-time waste; MTS doctor (`mts_doctor.py`); "you are the <role>" (pinned sessions) | TRAFFIC_BUSTERS.md; MTS_DOCTOR.md; ROLES.md |
| machines, logins, lanes, who may touch what; surfaces, names | HOW_MTS_RUNS.md, DEVICES.md, CLOUD_ACCOUNTS.md; SURFACE_POLICY.md |
| deploy, CI/CD; scheduling (none allowed) | DEPLOY_RUNBOOK.md; SCHEDULING_POLICY.md |
| layers (index); Codex lab | LAYERS.md; CODEX_START.md, LAYER_LAB.md |
| DSA, AIBridge; operator Inbox and decisions | DSA_DELEGATION.md, AIBRIDGE_LANE.md; CONTROL_ROOM.md |
| live state off the desktop (`live_mirror.py brief`, quote `mirror@<utc>`) | LIVE_MIRROR.md |
| add-a-layer rules, screenshots, hand deploy, Codex status, machine off, pages follow builds, live_runner.log, declutter_backups | QUICK_ANSWERS.md |
