# GEMINI START - first-message prompt for a Gemini builder session (Google AI Pro, VS Code, JIS-NUC)

Rules are not copied here: `GEMINI.md` -> `AGENTS.md` -> `CLAUDE.md` is the single source (Claude-only parts do not apply: screenshots, Control Room pages, DSA posting, relay hand-over); protocol is PARALLEL.md.
Gemini is one more work-tree session, modelled on Codex (CODEX_START.md). It meets Claude only through `origin/fast-track` (commits, claims, task cards, desk board).
**Gemini takes lane `CODEX` cards only** (audits, backtest runs, doc work, spec-derived tests), and only cards the Codex lab has not claimed: the claim is the lock. Machines and logins: `HOW_MTS_RUNS.md`.
The tool is whichever Google surface the Pro login unlocks in VS Code (Gemini Code Assist agent mode, Gemini CLI, Antigravity). Rules are the same for all three.

## Zero-conflict rules (all already in PARALLEL.md; Gemini adds none)
1. Own checkout: the work tree `F:\MTS\mts-gemini`, never the live tree (`BinanceDataFeed` on JIS-NB, marked `.mts_live`) and never another session's tree (`mts-codex`, `mts-codex-lab`, `mts-dsa`, `mts-jis-nuc-*`). VS Code opens only `F:\MTS\mts-gemini`.
2. Own branch prefix `<host>/gemini-<slug>`; shares work only by `sync.py ship` (merge, never rebase, reset, stash or force-push; never commit to master).
3. The claim is the lock: `sync.py claim "<task>"` before work, `sync.py ship --release <slug>` after. Take no card another session holds.
4. Gemini does not touch `NEXT_SESSION.md`, the relay scripts or SCHEDULING_POLICY.md. It works cards one at a time.
5. Gemini never restarts processes, touches HALT files, opens trades, or reads `.secrets/` / `.env` / keys. Testnet only. The repo is PUBLIC: never commit runtime, order or account data.
6. Cards that need `OPUS` stay with Claude. CI gates Gemini code exactly like Claude code; Claude spot-checks one claim per Gemini report.
7. Data-bound cards (1m klines, DAX archive, videos live on JIS-NB disks): post a desk task (`desk.py post ... --target JIS-NB`) instead of guessing.

## How Google AI Pro works (checked 2026-10-17; there is no "project" object, unlike the Codex app)
- It is an IDE extension plus a terminal tool, not an app: Gemini Code Assist in VS Code (chat and agent mode) and Gemini CLI. Agent mode in VS Code runs on Gemini CLI; both draw from one shared request quota that the AI Pro login raises (exact numbers: developers.google.com, UNVERIFIED here).
- "Project" = the folder VS Code has open (the workspace), which is also the CLI's working directory. Isolation therefore comes only from which folder you open: `F:\MTS\mts-gemini`, nothing else, and no multi-root workspace that adds another tree.
- It keeps no session history the repo can see and has no claim or card concept. Everything it knows comes from the files in that folder and the pasted prompt; results return only through git.

## Tool settings (set once in VS Code)
- Approval: ask before every file write and every terminal command. Turn off any auto-apply, auto-run or "YOLO" mode.
- Excludes: `.geminiignore` (Gemini CLI) and `.aiexclude` (Code Assist) are committed at the repo root and list `.secrets/`, `.env*`, `*.pem`, `*.key`, `runtime_data/`, `.mts_live`. Keep them; add to them, never remove.
- Storage: keep the tool's data folder on F: so C: stays clean (CLI: `GEMINI_CLI_HOME`; extensions: check the settings page).
- Tool-local folders (`.gemini/`, `.idx/`, `.vscode/`) are not committed; if one shows up in `git status`, add it to `.gitignore` (the one place ignores go, CLAUDE.md Hard rules).
- Context file: Gemini reads `GEMINI.md` at the repo root (a one-line pointer to AGENTS.md -> CLAUDE.md). Do not copy rules into it.

## Setup (NUC, done 2026-10-17)
`git worktree add F:\MTS\mts-gemini -b jis-nuc/gemini-start origin/fast-track`; per task, `python scripts/dev/sync.py start gemini-<slug>` from that tree. In VS Code use File > Open Folder on that path (not Add Folder to Workspace), open the Gemini chat in agent mode, then paste the block below.

## Paste into Gemini
```
You are an MTS builder session (surface GEM, Gemini). Read GEMINI.md (-> AGENTS.md -> CLAUDE.md), then
MyTradingSys/research/STATUS.md, MyTradingSys/system/PARALLEL.md, MyTradingSys/system/GEMINI_START.md.
Work only in this folder. Never read .secrets/, .env or keys; never run or stop live processes.
0. `python scripts/dev/sync.py start gemini-<slug>`, `sync.py where`. Push fails: say so in one line, stop.
1. `python scripts/dev/tasks.py next --lane CODEX`: take the first ready card nobody has claimed.
   `tasks.py brief <card>` is the whole task. `sync.py claim "<card>"`, work, tests (new test red before the fix), `tasks.py done <card> --result "<number/file>"`.
2. `sync.py ship --release <slug>`, `sync.py where` clean.
Commit trailer `MTS-Session: MTS-<UTC date>-<HHMMZ>-GEM-BLD-<slug>`, body line `Result: <what works now / the number>`.
Provenance rule applies: label every parameter SOURCED (trader's quote + file:line) or OURS (CLAUDE.md Hard rules).
Skip OPUS cards; do not touch NEXT_SESSION.md or the relay. One card per session, then stop with a one-line summary.
```

## Hand-over both ways
Claude puts the task on a card (`tasks.py new`, lane CODEX, `kind`) and ships it; Gemini returns results only through `tasks.py done` and `sync.py ship`. A question for the operator = `Operator: <question>` in the commit body. Read the other side's work with `python scripts/dev/sync.py news 24`.
