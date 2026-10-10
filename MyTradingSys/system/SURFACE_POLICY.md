# SURFACE POLICY - routing, handoff, budget, naming (all surfaces read at boot)

Keep under 4 KB (it is in every DSA boot paste). Tiers: CLAUDE.md work routing. Machines: WORKSTATION_MODES.md.

## 0. Mode (operator, direct, 2026-09-30)
Auto mode: reversible work -> safe default, act, log it in the session record. Irreversible or
outward-facing (delete, force-push, merge to main, live trading, HALT, orders) -> stop for operator.

## 1. Surfaces and ownership
| Surface | Reach | Owns |
|---|---|---|
| CLI desktop (SUP) | full tree, queue, live processes, testnet, commits | live path, restarts, HALT, promote/merge, commits |
| APP desktop | scheduled tasks (hourly-builder-check, dsa-feeder) | chat supervision, scheduled checks |
| LAP laptop CLI | read-only monitors, queue share | questions, monitoring |
| ASK poller | headless claude -p; default haiku, escalation sonnet | status questions |
| DSA chat (chat.deepseek.com) | pasted text only, no disk | long-context reading, extraction, rulebooks |
| CLD cloud (free pool) | pushed git refs only; no LAN, no gitignored files | offline research, specs, reviews, docs, backtests on committed data |
| COD Codex (NB) | own checkout, branch codex/work; offline work, proposes only on live path | research, tests, reviews, docs |
| AIBridge (F:\AIBridge) | allowlisted loopback agent 127.0.0.1:7181, Chrome MV3 extension | PowerShell on desktop, on request from a web AI |
Builders touching execution/ or layers/alerts/ stage .new only (CLAUDE.md hard rules).

## 2. Handoff
A handoff is a file in the receiver's inbox that names the sender's session ID.
SUP: research/fast_track_2026-09-27/SUPERVISOR_INBOX.md. AIBridge: F:\AIBridge\HANDOFF.md. DSA worker: incoming_dsa/. COD: system/CODEX_INBOX.md.
Poller: Dumps/operator/inbox. Cloud: MyTradingSys/system/CLOUD_INBOX.md (desktop commits and pushes).
Cloud returns commits on its branch plus its session record; SUP gates, merges, logs in SUPERVISOR_LOG.
A cloud session sees one repo; cross-repo work (CBP owns mts_queue/, MTS writes acks/ only) runs on the desktop.
Before starting a task, grep MyTradingSys/system/sessions/ and the inboxes for its slug; skip duplicates.

## 3. Budget (per account; read /usage or the chat-header usage indicator)

OPERATOR DIRECTIVE 2026-10-02: never refuse a task for budget. Work to
completion. If usage is at 95 percent or above (5 percent or less remaining),
commit and push immediately, then continue with a commit after each step.
At 1 percent remaining, still work.

A: chat, cowork, code, cloud (only cloud account). B: chat, cowork, code; cloud
later. Route to the one with headroom. Cloud also spends session credits
(100 USD pool, expires 2026-11-05 13:29 GMT+5:30; applied automatically to cloud sessions; not eligible for Projects or Routines; per Claude account, see CLOUD_ACCOUNTS.md).

>=70 percent weekly: Opus only for safety diffs; rest to T0, DSA, other account.
>=85 percent: prefer one session reading by range over subagent fan-out.
>=95 percent: write-then-commit each step. Do not stop. Live processes run.

Cloud: no routines or always-on sessions; one session per task; nothing live
depends on it.

## 4. Naming
Session ID: MTS-YYYY-MM-DD-HHMMZ-<SURF>-<ROLE>[-<slug>] (UTC start; slug <=20 chars, lowercase kebab).
SURF: CLD APP CLI LAP DSA ASK COD. ROLE: SUP BLD ANA EXT MON COO WRK. Chat title = session ID.
Record: MyTradingSys/system/sessions/<ID>.md (template: sessions/README.md). Predecessor = newest record
with the same -<SURF>-<ROLE>, also named in the record.
Commit trailer: MTS-Session: <ID>.
Cloud branch: cloud/work; cloud/YYYY-MM-DD-<slug> only for concurrent Cloud sessions. Harness-assigned
names (claude/...) are recorded as branch_alias, never reused.
Lanes: bridge-nb = F:\AIBridge; dsaweb-nb = incoming_dsa/; ask-nb = poller. Directories are not renamed.
Subagents: <parent ID>/<tier>-<nn> (e.g. /sonnet-02).
Renames: chat titles by hand; git refs never renamed or rewritten (new ref at same commit, old deleted
by the operator after merge); legacy names stay in old logs, mapped below.

## 5. Legacy aliases
| Legacy name | Maps to |
|---|---|
| MTS-YYYY-MM-DD-HHMMZ (start-session.ps1:46) | same prefix + -DSA-COO |
| MTS-2.1, MTS-1, MTS-MAIN-OLD | LEGACY-<name> (no timestamp in repo) |
| claude/clever-bohr-8878jr | branch_alias of MTS-2026-09-30-1005Z-CLD-ANA-connected-system |
| supervisor "session N" (SUPERVISOR_LOG) | MTS-...-CLI-SUP, heading per entry from now on |
