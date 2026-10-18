# GEMINI START - first-message prompt for a Google (Antigravity) builder session (Google AI Pro, JIS-NUC)

Rules are not copied here: `GEMINI.md` -> `AGENTS.md` -> `CLAUDE.md` is the single source (Claude-only parts do not apply: screenshots, Control Room pages, DSA posting, relay hand-over); protocol is PARALLEL.md.
Gemini is one more work-tree session, modelled on Codex (CODEX_START.md). It meets Claude only through `origin/fast-track` (commits, claims, task cards, desk board).
**Gemini takes lane `CODEX` cards only** (audits, backtest runs, doc work, spec-derived tests), and only cards the Codex lab has not claimed: the claim is the lock. Machines and logins: `HOW_MTS_RUNS.md`.
The tool actually installed on the NUC (2026-10-17) is the **Google Antigravity extension 1.8.0 inside VS Code** (its backend `agy` v1.4.0 lives in `C:\Users\E-ngineers\.gemini\bin`); a standalone Antigravity IDE and a terminal `agy` also exist but are not needed. Since 2026-06-18 Google no longer serves the old Gemini Code Assist extension or Gemini CLI to AI Pro logins (error: 'This client is no longer supported ... migrate to the Antigravity suite'); `google.geminicodeassist` in VS Code is dead, ignore its crash log. Sign in through the Antigravity icon in the Activity Bar (Continue with Google). Open the folder with File > Open Folder; the path must be `F:\MTS\mts-gemini`, NOT the empty stray `F:\mts-gemini`.

## Simple working model (how people run Claude and Gemini on one repo, researched 2026-10-17)
- Two tools, never one folder: Claude works in its own work trees, Gemini only in `F:\MTS\mts-gemini`. They talk only through git, task cards and the desk board (no direct tool-to-tool link).
- One rules file: `CLAUDE.md` is the source; `AGENTS.md` and `GEMINI.md` only point to it.
- Role split: Gemini = audits, tests, docs, first-pass review (lane CODEX cards). Claude = live path, anything needing OPUS, final review of Gemini's claims.
- Never write the same files at once: the card's scope_in list and the claim are the lock; `sync.py ship` and CI check every result.
- Model: use a Flash model for routine cards; Gemini 4 Argon has a separate weekly-only quota, keep it for hard cards.
- No plugins or delegation tools (community Claude-to-agy bridges exist; not installed). Revisit only after one card has shipped cleanly.

## Antigravity facts and first run (2026-10-17, operator screenshot + dry run)
- Model menu (one Pro login): Gemini 4 Argon, Gemini 3.8 Flash (default for routine cards), Claude Opus 5.5, Claude Sonnet 5.5, GPT-OSS 120B. Limits shown: Gemini models weekly + five-hour; Claude and GPT models weekly + five-hour; Argon weekly only (all 100% at first look). `View Usage` in the model menu shows them.
- The Claude and GPT models in the menu are included in the Google AI Pro plan at no extra cost (operator 2026-10-18; not the Anthropic account). Use them, within quota. Opus use there is operator-approved (2026-10-18), recorded as `approved_by: operator` on any card that names it.
- Three quota pools, each with weekly and five-hour limits except Argon: (1) Gemini 3.8 Flash; (2) Claude Opus/Sonnet 5.5 and GPT-OSS together; (3) Gemini 4 Argon, weekly only. `View Usage` in the model menu shows them. Opus very likely drains pool 2 faster than Sonnet (UNVERIFIED): read pool 2 before and after the first Opus card and note the drop here.
- Routing (OURS, adjust after real numbers): Flash = routine audits, tests, docs, first-pass review. Sonnet 5.5 = spec-derived builds when Flash is not enough. Opus 5.5 = hard judgment only (independent challenge of critical work, blind setup discovery, design review), one card at a time. Argon = blind Tom/Fabio setup discovery and other heavy research. GPT-OSS = skip (GPT work stays in the Codex app).
- Pacing: before a heavy card read the pool it draws on; do not start if the five-hour limit is under 30% or the weekly under 25% (OURS); drop to Flash or wait for the reset. Heavy cards go one at a time.
- Claude (this repo's sessions) can delegate to the same login without the UI: `C:\Users\E-ngineers\.gemini\bin\agy.exe --print "<prompt>" --model <id>` (ids from `agy.exe models`: gemini-4-argon-{low,medium,high}, gemini-3.8-flash-*, claude-opus-5-5-*, claude-sonnet-5-5-*). Tested 2026-10-18 with flash-low: works, already signed in. Run it from a work tree or scratch folder, never the live tree. A task that needs Gemini to run commands (transcript fetch, search) goes through `scripts/dev/gemini_queue.py` (operator 2026-10-18): it runs `agy` with `--dangerously-skip-permissions` ONLY inside a throwaway worktree `F:/MTS/gq/<id>` on branch `gemini-q/<id>`, Gemini commits there only, a Claude session reviews before `sync.py ship`. Never use that flag from a scratch folder or any other tree, and never ask the operator which option to pick: file a card and queue it; the result returns as text and goes through a card or `sync.py ship` like any other.
- Dry run passed: Gemini ran `sync.py start`, `sync.py where`, `tasks.py next --lane CODEX` (returned `dsa-audit-08-split-trials`, size M, p1), asked before each command, edited nothing, committed nothing.
- Dry-run slip: it read GEMINI.md and GEMINI_START.md before syncing, so they were missing (the tree was behind). The paste block now syncs first.

## Zero-conflict rules (all already in PARALLEL.md; Gemini adds none)
1. Own checkout: the work tree `F:\MTS\mts-gemini`, never the live tree (`BinanceDataFeed` on JIS-NB, marked `.mts_live`) and never another session's tree (`mts-codex`, `mts-codex-lab`, `mts-dsa`, `mts-jis-nuc-*`). the IDE opens only `F:\MTS\mts-gemini`.
2. Own branch prefix `<host>/gemini-<slug>`; shares work only by `sync.py ship` (merge, never rebase, reset, stash or force-push; never commit to master).
3. The claim is the lock: `sync.py claim "<task>"` before work, `sync.py ship --release <slug>` after. Take no card another session holds.
4. Gemini does not touch `NEXT_SESSION.md`, the relay scripts or SCHEDULING_POLICY.md. It works cards one at a time.
5. Gemini never restarts processes, touches HALT files, opens trades, or reads `.secrets/` / `.env` / keys. Testnet only. The repo is PUBLIC: never commit runtime, order or account data.
6. Cards that need `OPUS` stay with Claude. CI gates Gemini code exactly like Claude code; Claude spot-checks one claim per Gemini report.
7. Data-bound cards (1m klines, DAX archive, videos live on JIS-NB disks): post a desk task (`desk.py post ... --target JIS-NB`) instead of guessing.
8. **NO ASSUMPTIONS, NO FABRICATIONS (strict `Producer != Reviewer`)**: Never self-stamp `ACCEPT` on a `C1+` / `IMPORTANT+` card that Gemini refined or built (`refined_by: gemini-*` gets `REVIEWED:<YYYY-MM-DD> T0-ONLY` only, leaving `C1+`/`IMPORTANT+` cards in `refined` for a non-Gemini reviewer). Never bulk-replace `T0-ONLY` with `ACCEPT` or bulk-append `HOLD-CLEARED` via script. Only stamp `REVIEWED: <gemini-model-id> <YYYY-MM-DD>` (`ACCEPT`/`FIX`/`REWORK`) when acting as an independent cross-vendor reviewer on a Claude/Codex card after verifying every `file:line` and `E1`–`E7` check one card at a time.
9. **ALWAYS COMMIT AND SHIP FINAL DELIVERY (Stop Guard enforced)**: Every Gemini session must write deliverables early, commit incrementally (`Result: ...` + `MTS-Session:` trailer), and run `python scripts/dev/sync.py ship --release <slug>` + verify `sync.py where` is clean before stopping. `.agents/hooks.json` wires `scripts/dev/stop_guard.py` into the Antigravity `Stop` lifecycle hook so a session cannot end with uncommitted or unshipped work in its worktree.

## How Google AI Pro works (checked 2026-10-17; there is no "project" object, unlike the Codex app)
- It is an IDE (Antigravity) plus a terminal tool (Antigravity CLI), not a project-based app like Codex. Old route (Code Assist extension in VS Code, Gemini CLI login) is dead for AI Pro. Quota for the AI Pro login: see Google's Antigravity pricing page (UNVERIFIED here).
- "Project" = the folder the IDE has open (workspace), also the CLI's working directory. Isolation therefore comes only from which folder you open: `F:\MTS\mts-gemini`, nothing else, and no multi-root workspace that adds another tree.
- It keeps no session history the repo can see and has no claim or card concept. Everything it knows comes from the files in that folder and the pasted prompt; results return only through git.

## Tool settings (set once in Antigravity)
- Approval: ask before every file write and every terminal command. Turn off any auto-apply, auto-run or "YOLO" mode.
- Excludes: `.geminiignore` and `.aiexclude` are committed at the repo root (secret and runtime patterns); whether Antigravity honours either is UNVERIFIED, so on first use set its own ignore/deny list to the same patterns (`.secrets/`, `.env*`, `*.pem`, `*.key`, `runtime_data/`, `.mts_live`) and keep the agent in ask-before-act mode. Keep these files; add to them, never remove.
- Storage: keep the tool's data folder on F: so C: stays clean (CLI: `GEMINI_CLI_HOME`; extensions: check the settings page).
- Tool-local folders (`.gemini/`, `.idx/`, `.vscode/`, `.antigravity/`, `.agent/`) are not committed (`.agents/hooks.json` IS tracked for the Antigravity Stop hook); if one shows up as an untracked file, add it to `.gitignore` (the one place ignores go, CLAUDE.md Hard rules).
- Context file: Gemini reads `GEMINI.md` at the repo root (a one-line pointer to AGENTS.md -> CLAUDE.md). Do not copy rules into it.

## Laptop (DESKTOP-F7IU69N, Lenovo) setup, done 2026-10-18
- Tool: the **standalone Antigravity app** (`%LOCALAPPDATA%\Programs\antigravity\Antigravity.exe`), not the VS Code extension used on the NUC. First-run onboarding is already completed; its data lives in `%USERPROFILE%\.gemini\antigravity`. The `agy` CLI is NOT installed here (`~\.gemini\bin\agy.exe` missing; the app ships only `language_server.exe`), so `gemini_queue.py` and headless `agy --print` do not work on the laptop until it is installed.
- Work tree: `C:\Users\e-ngineers\IdeaProjects\mts-gemini` (branch `DESKTOP-F7IU69N/gemini-start`, cut from `origin/fast-track`). No F: drive on the laptop. In Antigravity use File > Open Folder on that path only (not Add Folder to Workspace), sign in with the Google AI Pro login, set approval to ask-before-write/run, then paste the block below. Per task: `python scripts/dev/sync.py start gemini-<slug>` from that tree.
- Same rules as the NUC (GEMINI.md -> AGENTS.md -> CLAUDE.md); lane CODEX cards only; the claim is the lock against the NUC Gemini and the Codex lab.

## Setup (NUC, done 2026-10-17)
`git worktree add F:\MTS\mts-gemini -b jis-nuc/gemini-start origin/fast-track`; per task, `python scripts/dev/sync.py start gemini-<slug>` from that tree. In Antigravity use File > Open Folder on that path (not Add Folder to Workspace), open the agent panel, then paste the block below.

## Paste into Gemini
```
You are an MTS builder session (surface GEM, Gemini). Work only in this folder. Never read .secrets/, .env or keys; never run or stop live processes.
0. FIRST, before reading any file: `python scripts/dev/sync.py start gemini-<slug>`, `sync.py where` (the tree is often behind origin; files below may not exist until this runs). Push fails: say so in one line, stop.
   Then read GEMINI.md (-> AGENTS.md -> CLAUDE.md), MyTradingSys/research/STATUS.md, MyTradingSys/system/PARALLEL.md, MyTradingSys/system/GEMINI_START.md.
1. `python scripts/dev/tasks.py next --lane CODEX`: take the first ready card nobody has claimed.
   `tasks.py brief <card>` is the whole task. `sync.py claim "<card>"`, work, tests (new test red before the fix), `tasks.py done <card> --result "<number/file>"`.
2. ALWAYS COMMIT AND SHIP BEFORE STOPPING: write and commit deliverables early (`Result: ...` + `MTS-Session: MTS-<UTC date>-<HHMMZ>-GEM-BLD-<slug>`), run `python scripts/dev/sync.py ship --release <slug>`, and verify `sync.py where` shows `unshipped-commits=0 modified=0 untracked=0` before ending your turn.
Provenance rule applies: label every parameter SOURCED (trader's quote + file:line) or OURS (CLAUDE.md Hard rules).
NO ASSUMPTIONS, NO FABRICATIONS: never self-stamp ACCEPT on cards Gemini refined/built (use T0-ONLY); never bulk-stamp ACCEPT or HOLD-CLEARED.
Skip OPUS cards; do not touch NEXT_SESSION.md or the relay. One card per session, then stop with a one-line summary.
```

## Lab queries (on demand; read-only, `scripts/dev/lab_query.py`)
Use these instead of ad-hoc grep when asked about Tom/Fabio fixes, backtests or a layer. Family ids: `layer_index.json` (tom, fabio, guidance, ...). Add `--format md` for a readable answer, `--n N` for more rows.
- `python scripts/dev/lab_query.py changes tom` : recent commits on the family's spec, code, ledger and result files (also its layers' modules).
- `python scripts/dev/lab_query.py rulings fabio` : BUGS.md bug rows that name the family, newest first (status, severity, title).
- `python scripts/dev/lab_query.py backtests tom` : layer_map.json backtests of the family, newest first (verdict, n, report path) plus trial-audit status counts from `research/TRIAL_LEDGER.csv`.
- `python scripts/dev/lab_query.py layers [fabio]` : every layer with its status (layer_map.json) and the latest commit on its module. Layer map text: `LAYERS.md`.
Run `sync.py start` first so the data is current. Test: `scripts/dev/test_lab_query.py`.

## Hand-over both ways
Claude puts the task on a card (`tasks.py new`, lane CODEX, `kind`) and ships it; Gemini returns results only through `tasks.py done` and `sync.py ship`. A question for the operator = `Operator: <question>` in the commit body. Read the other side's work with `python scripts/dev/sync.py news 24`.
