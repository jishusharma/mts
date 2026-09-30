# SURFACE POLICY - routing, handoff, budget, naming (all surfaces read at boot)

Keep under 4 KB (it is in every DSA boot paste). Tiers: CLAUDE.md work routing. Machines: WORKSTATION_MODES.md.

## 1. Surfaces and ownership
| Surface | Reach | Owns |
|---|---|---|
| CLI desktop (SUP) | full tree, queue, NUC gate, live processes, testnet, commits | live path, restarts, HALT, promote/merge, commits |
| APP desktop | scheduled tasks (hourly-builder-check, dsa-feeder) | chat supervision, scheduled checks |
| LAP laptop CLI | read-only monitors, queue share | questions, monitoring |
| ASK poller | headless claude -p; default haiku, escalation sonnet | status questions |
| DSA chat (chat.deepseek.com) | pasted text only, no disk | long-context reading, extraction, rulebooks |
| CLD cloud (free pool) | pushed git refs only; no LAN, no gitignored files | offline research, specs, reviews, docs, backtests on committed data |
| Qwen NUC | packed files only | implementation and extraction drafts |
Builders touching execution/ or layers/alerts/ stage .new only (CLAUDE.md hard rules).

## 2. Handoff
A handoff is a file in the receiver's inbox that names the sender's session ID.
SUP: research/fast_track_2026-09-27/SUPERVISOR_INBOX.md. Qwen: queue incoming/. DSA worker: incoming_dsa/.
Poller: Dumps/operator/inbox. Cloud: MyTradingSys/system/CLOUD_INBOX.md (desktop commits and pushes).
Cloud returns commits on its branch plus its session record; SUP gates, merges, logs in SUPERVISOR_LOG.
Before starting a task, grep MyTradingSys/system/sessions/ and the inboxes for its slug; skip duplicates.

## 3. Budget (Pro accounts A and B)
Usage source: TBD (operator Q7). Account-to-surface map: TBD (operator Q1).
>=70%: Opus only for safety diffs; other work to T0, Qwen, DSA, Cloud.
>=85%: no Sonnet builders; supervisor wake cadence halved.
>=95% or cap hit: suspend scheduled tasks and builders; live processes keep running; the other account
only for safety incidents; Qwen, DSA, Cloud continue (procedure of SUPERVISOR_LOG 2026-09-30 03:50 IST).
Enforcement in code (BUDGET_HOLD file) is deferred; until then the supervisor applies these by hand.
Cloud: no routines, triggers or always-on sessions; one session per task; nothing live depends on it.

## 4. Naming
Session ID: MTS-YYYY-MM-DD-HHMMZ-<SURF>-<ROLE>[-<slug>] (UTC start; slug <=20 chars, lowercase kebab).
SURF: CLD APP CLI LAP DSA ASK. ROLE: SUP BLD ANA EXT MON COO WRK. Chat title = session ID.
Record: MyTradingSys/system/sessions/<ID>.md (template: sessions/README.md). Predecessor = newest record
with the same -<SURF>-<ROLE>, also named in the record.
Commit trailer: MTS-Session: <ID>.
Cloud branch: cloud/work; cloud/YYYY-MM-DD-<slug> only for concurrent Cloud sessions. Harness-assigned
names (claude/...) are recorded as branch_alias, never reused.
Lanes: qwen-nuc = incoming/; dsaweb-nb = incoming_dsa/; ask-nb = poller. Directories are not renamed.
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
