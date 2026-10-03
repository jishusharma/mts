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
| AIBridge (F:\AIBridge) | allowlisted loopback agent 127.0.0.1:7181, Chrome MV3 extension | PowerShell on desktop, on request from a web AI |
Builders edit live. Gate before commit. Stage .new only when the running system imports the file mid-session.

## 1b. Surface choice (operator directive 2026-10-03)
App first. CLI is fallback, not default. Choose by what the task needs, not by what the policy lists first.

Order:
1. Claude Win App (Code / Cowork / Chat / Cloud modes) - use whenever it can do the job.
2. CLI - only when the task needs something the App cannot reach: local Maven, local testnet,
   the live loop, PowerShell-only files, scripts that import from the repo tree, a disk write
   to a gitignored path, or anything the App explicitly refuses.

If the App can read the file, write the file, run the tests, and commit - it is the right surface.
State the fallback reason in the session record when CLI is chosen.

## 2. Handoff
A handoff is a file in the receiver's inbox that names the sender's session ID.
SUP: research/fast_track_2026-09-27/SUPERVISOR_INBOX.md. AIBridge: F:\AIBridge\HANDOFF.md. DSA worker: incoming_dsa/.
Poller: Dumps/operator/inbox. Cloud: MyTradingSys/system/CLOUD_INBOX.md (desktop commits and pushes).
Cloud returns commits on its branch plus its session record; SUP gates, merges, logs in SUPERVISOR_LOG.
A cloud session sees one repo; cross-repo work (CBP owns mts_queue/, MTS writes acks/ only) runs on the desktop.
Before starting a task, grep MyTradingSys/system/sessions/ and the inboxes for its slug; skip duplicates.

## 3. Budget (Session Manager governs; operator supplies values when needed)

OPERATOR DIRECTIVE 2026-10-02: never refuse a task for budget. Work to
completion. Commit after each step when Session Manager signals low headroom.

DSA never states a numeric usage percent, budget cap, token cap, or dollar pool
in any prompt, unless the operator supplied that exact number in the same session.
No default. No placeholder.

Session Manager routes by account and headroom. Routing tiers live in the
Session Manager, not here. This file does not restate them.

Cloud: no routines or always-on sessions; one session per task; nothing live
depends on it.

## 3b. Manager routing + spawn caps (added 2026-10-02)

Budget unit: % of session or weekly pool for Pro/CL sessions. $ for CC cloud credits. Operator hints, Session Manager routes.
Sessions inherit these rules at boot.

Spawn:
- Default one child per task. Hard cap 3 per mts go call.
- Split only when 2 or more independent files/modules, each fits one brief.
- Never split when pieces share state, task is a safety diff, or tier >= 85%.

Routing (cheapest workable):
- question/status -> Haiku, low.
- extraction, docs/spec, backtest report -> Sonnet, medium.
- build -> Sonnet (Sonnet reviews Sonnet), medium.
- safety diff (execution/, HALT, orders) -> Opus, high.

Mode selection (surface / model / Ultracode / cap / batch):
- DSA one artifact: n/a / off / 0 / n/a.
- CC one deliverable: Sonnet / off / 0 / n/a.
- CC 2-3 independent modules, or build wave: Sonnet / ON / 3 / 1.
- CL local fix: Sonnet / off / 0 / n/a.
- Safety diff: Opus / high / off / 0 / n/a.
- Question/status: Haiku / low / off / 0 / n/a.

Ultracode rules:
- OFF is default. ON only when 2 or more truly independent workstreams, each can checkpoint.
- Every prompt states: total subagent cap, batch size, "commit and push between batches".
- Never more than 3 subagents in a cloud session.
- Waves sequential unless prompt names a parallel batch.
- Live-path edit: Ultracode off, one writer, four-step proof.
- Safety diff: Opus, high, Ultracode off.

Incident: 2026-10-02 CC session MTS-2026-10-01-1916Z-CLD-BLD-two-cores-int.
Prompt said "one subagent per wave"; Ultracode spawned 4 parallel; 0.97 credit
spent in 9 minutes; Waves 1-2 lost uncommitted.


## 4. Naming
Session ID: MTS-YYYY-MM-DD-HHMMZ-<SURF>-<ROLE>[-<slug>] (UTC start; slug <=20 chars, lowercase kebab).
SURF: CLD APP CLI LAP DSA ASK. ROLE: SUP BLD ANA EXT MON COO WRK. Chat title = session ID.
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
