# MTS - Claude Code sessions

CLAUDE.md is already in context; do not cat or Read it. Code mode only (DSA chat: `DSA_SESSION_PROMPT.md`; Codex: `AGENTS.md`).

## Boot (every turn re-reads the context)
1. `python scripts/dev/sync.py start <slug>`: in a lane tree (mts-app/relay/dsa) it switches to branch <host>/<slug>; elsewhere it prints `WORKTREE: <path>` (work only there, never the live tree).
2. Read `MyTradingSys/research/STATUS.md` (rebuild: `scripts/dev/make_status.py`), not what it summarises; `LESSONS_DIGEST.md` only for live-path or backtest work. RED `CI green:` / `CI RED`: first to see it (the author above all) `git revert`s the breaking commit, ships in 10 min; putting the failing file back to its last-green bytes is a revert, a new line is a forward-fix (never forward-fix trunk). A hand-over (NEXT_SESSION.md) is history: current state comes from disk or git this turn. Read the ACTIVE entries of `MyTradingSys/system/ANNOUNCEMENTS.md` (STOP/HOLD there outranks the queue). `[MTS ACTION REQUIRED]` outranks the current task: do it first. Where a kind of work goes (machine, channel, model, checker): `MyTradingSys/system/ROUTING.md`.
3. ONE task from NEXT_SESSION.md or `tasks.py next`; `sync.py claim "<task>"`, work, `sync.py ship --release <slug>`, `sync.py where` (own tree clean).
4. Hand-over: no schedulers or routines anywhere (SCHEDULING_POLICY.md). Overwrite NEXT_SESSION.md, `sync.py ship`; the coordinator (SUPER_SESSION.md) starts the next. Zero operator input: defaults for open questions.
5a. Role sessions ("You are Eagle_Eyes"): the `role_loader.py` hook injects `roles/<role>.md`; the first reply is its `ROLE LOADED: ...` banner. Without the injected text, say `ROLE NOT LOADED` and stop.
5. SHORT SESSIONS (unattended workers; an operator-driven session ends on his word): one session = one task; hand over when done, after 10 operator turns or the tool-turn cap (WORKERS.md rule 5): commit, steps 3-4, one line, stop.
5b. After `get_usage`, once: `mts_signal.py budget ...` then `exhaust.py plan ...` (flags, phases: MOVED_RULES.md; `EXHAUST_PHASE.md`).
6. Task shipped: mark your own session completed in the sidebar (`mark_completed`); coordinators mark their workers (SUPER_SESSION.md).

## Cost and routing
- Interactive sessions and subagents: Sonnet, Opus only when the operator names it; Haiku for mechanical work; worker type + model: WORKERS.md. Wait on a queue with one background shell; spot-check one worker claim.
- No "want me to?" offers for implied work: do it now, full depth. Free public market data, YouTube: pre-approved.
- T0 script first, then by card lane (HOW_MTS_RUNS.md): run-and-report goes to DSA (`desk.py post ... --target DSA`; low on budget: post the rest to DSA, then hand over).
- Logins share one repo and queue (CLOUD_ACCOUNTS.md): whoever has budget takes NEXT_SESSION.md; never idle for a weekly reset.
- The operator dictates by voice: expect misheard words. Read for intent: take the reading that fits the project, act on it, and name it in one line only if it changes the work.
- Never wait on a question. Ask who started you: an Agent ends its report with the question and its default; a session uses SendMessage. Only money, mainnet, going private, deleting data or a live-tree change reach the operator; work goes on at the safe default. Stuck on another machine's state: `mts_signal.py who`, then broadcast.
- Fleet-wide by default: what one machine needs, all need. Put it in the repo; send a per-machine step as `mts_signal.py broadcast --cmd ...` (each host runs it and acks); never leave it to the operator.
- Operator replies: result line; What|Status|Proof table; always a "Waiting for you" table (need, exact button or `cd <full path>;` command, if nothing) or "Nothing waiting for you."; Who|Doing|Done when table. Plain words, ~25 lines (OPERATOR_REPLY_FORMAT.md).
- Surface: Win App only; never tell the operator to "use the CLI" or hand work back. Permission block: report the call, try the allowed equivalent.

## Gates (before any commit touching the area)
- `sync.py ship`: smoke gate (live-path or unknown paths = all `--quick`; `--full`); CI + green-only deploy gate the rest. Full: `python scripts/dev/run_all_tests.py` (`--quick`: no Maven/backtest). Extractions: `scripts/dev/verify_extract_quotes.py <extract.md>`.
- New tests must fail on the pre-change code at least once.
- Formulas: expected numbers come from `MyTradingSys/backtest/layers/FORMULAS.md`, computed independently, never from existing code. OUTPUT_TOKENS must fit the whole reply.

## Hard rules
- Share work only through `sync.py ship`; cloud containers open a PR into fast-track. Never commit to master, never rebase/reset/force-push. No chained `cd x && git ...`: use `git -C <dir> <cmd>`.
- Commit body carries `Result: <what works now / the number>`. Others' uncommitted files: leave them alone.
- Testnet only (Deribit test); no mainnet orders/accounts (public market data OK: q-gap-c); never read `.secrets/`, `.env`, keys.
- Repo is PUBLIC (since 2026-10-11): never commit runtime/order/account data; backups go only to local F:/MTS_backup.git; go private at mainnet or the first fee-net OOS pass, whichever first (q-go-private-on-edge).
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
