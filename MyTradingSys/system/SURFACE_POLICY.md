# SURFACE POLICY - surfaces, budget, naming (read at DSA boot: keep under 4 KB)

Tiers and lanes: CLAUDE.md "Cost and routing"; machine x login x lane x model x may-touch table: HOW_MTS_RUNS.md. Machines: DEVICES.md, WORKSTATION_MODES.md.

## 0. Mode (operator, direct, 2026-09-30)
Auto mode: reversible work -> safe default, act, log it in the commit `Result:` line. Irreversible or
outward-facing (delete, force-push, merge to main, live trading, HALT, orders) -> stop for operator.

## 1. Surfaces and ownership
| SURF | Reach | Owns |
|---|---|---|
| APP | Claude Code Win App (Code / Cowork / Chat / Cloud modes): full tree, local Maven, testnet, PowerShell, gitignored paths | build, research, refine; App first, always (operator 2026-10-04, repeated 2026-10-08) |
| CLI | Claude Code CLI: only when the App cannot reach the task (a card or desk row with the reason, QUICK_ANSWERS.md) | same, as a fallback |
| CLD | cloud (claude.ai/code): pushed git refs only; no LAN, no gitignored files; ships by PR into fast-track (auto-merge on green) | offline research, specs, reviews, docs, backtests on committed data |
| DSA | DeepSeek chat through AIBridge (F:\AIBridge, loopback 127.0.0.1:7181, AIBRIDGE_LANE.md); paste mode when the bridge is down | long-context reading, extraction, run-and-report jobs (DSA_DELEGATION.md) |
| COD | Codex (CODEX_START.md, LAYER_LAB.md) | lane CODEX cards only |
| GEM | Gemini (Antigravity IDE) on JIS-NUC (GEMINI_START.md) | lane CODEX cards the lab has not claimed |
Choose by what the task needs; state the reason when a surface other than the App is chosen. Builders work in a work tree, never the live tree; sharing and
deploy: PARALLEL.md, DEPLOY_RUNBOOK.md. The ASK poller (`scripts/operator/inbox_poller.ps1`) is not registered on JIS-NB.

## 2. Handoff
PARALLEL.md (2026-10-07): ship commits to origin/fast-track; an operator question goes in the commit body as `Operator: <question>`.
Between sessions: NEXT_SESSION.md (RELAY.md). DSA (no disk) pastes into incoming_dsa/; AIBridge uses F:\AIBridge\HANDOFF.md.

## 3. Budget
OPERATOR DIRECTIVE 2026-10-02: never refuse a task for budget. Work to completion; commit after each step when headroom is low.
Handing off at the CLAUDE.md SHORT SESSIONS limit is not a refusal: finish the step, ship, overwrite NEXT_SESSION.md; the next session continues.
DSA never states a numeric usage percent, budget cap, token cap, or dollar pool in any prompt, unless the operator supplied that exact number in the same session. No default. No placeholder.
Subagents: one child per task by default; at most 3 per call and 3 in a cloud session; Ultracode is OFF unless 2 or more truly independent workstreams
each checkpoint. Every launch prompt names Ultracode on/off, the total subagent cap, the batch size and "commit and push between batches" (LESSONS_LEARNED 2026-10-02).
Cloud: no routines or always-on sessions; one session per task; nothing live depends on it.

## 4. Naming
Session ID: MTS-YYYY-MM-DD-HHMMZ-<SURF>-<ROLE>[-<slug>] (UTC start; slug <=20 chars, lowercase kebab).
SURF: APP CLI CLD DSA COD GEM. ROLE: SUP BLD ANA EXT MON COO WRK (SUP = operator-driven supervising session; it deploys nothing; deploys are by hand, DEPLOY_RUNBOOK.md). Chat title = session ID.
Record: the commit trailer `MTS-Session: <ID>` (commit history is the registry; sessions/ is history, no new files).
Cloud branch: the harness-assigned `claude/...` branch, started from origin/fast-track and shipped by PR (PARALLEL.md). Harness names are recorded as branch_alias, never reused.
Subagents: <parent ID>/<tier>-<nn> (e.g. /sonnet-02).
Renames: chat titles by hand; git refs never renamed or rewritten (new ref at same commit, old deleted by the operator after merge).
