# Supervisor hand-over, login C (written by Builder rolling-sessions-decisions, 2026-10-28)

Read as history. Current state comes from git and disk this turn. The operator speaks only the short start `Supervisor C` (role_loader.py BARE_LOGIN loads this file from origin/fast-track).

## First discussion with the operator (decision d-measure-rolling-cost, D5)
Open the session by explaining, in plain words, how context loading is wired today: what loads at boot, hooks, role files, memory, compaction. Source: card `context-loading-wiring-report` (research/context_loading_wiring_2026-10/REPORT.md) once done; until then answer from CLAUDE.md and scripts/dev/role_loader.py.

## Goals, in order
1. Verify the 21 gap cards from commit b3375534 landed on `origin/fast-track` (`tasks.py list`, grep `gap-`); dispatch the top ones (`tasks.py dispatch`).
2. Verify the gateway ships landed on `origin/fast-track` and `origin/green/fast-track` and meet done-when: `handover-log-cap`, `gemini-lane-fix`, `wake-sleeping-sessions` (independent re-run; no recorded real run = not done).
3. Drive the 3 new cards: `rolling-session-cost-comparison`, `context-loading-wiring-report`, `codex-gpt-exhaust-full`.
4. Keep CI green: revert a breaking commit, never fix forward.
5. Keep the Codex (GPT) lane fed to 100% of its session limit (d-gpt-exhaust-full); Gemini lane always `<card>:low`.

## Operator decisions 2026-10-28 (do not ask again; OPERATOR_DECISIONS.md d-rolling-sessions, d-gpt-exhaust-full, d-measure-rolling-cost)
- Rolling sessions continue on every login. Login A keeps running as is; never restart it.
- Logins A and C stay active continuously; work proceeds on all logins without gaps.
- Login C goes down now and then: keep this file current at every hand-over so a fresh session takes over with one spoken word.

## Rules the operator set
- Never hand him a long prompt to paste. Save it in a file on trunk, give a one-line start.
- A feature counts as done only when a real end-to-end run is recorded.
- Gateway sessions: public tracked files only (GATEWAY_NUC.md).
- Malkan RSI divergence flags are confirmed only in the simulator, never on screenshots.

Successor: `Supervisor C`
