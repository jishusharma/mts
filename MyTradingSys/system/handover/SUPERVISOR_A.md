# Supervisor hand-over, login A (written by Supervisor C, 2026-10-28)

Read as history. Current state comes from git and disk this turn. The operator pastes only the one-line start (operator 2026-10-28: long prompts cannot be pasted on the laptop).

## Goals, in order
1. Read `MyTradingSys/research/fix_verification_2026-10-28/REPORT.md` (a Haiku checker writes it). File a card for every FAIL and CANNOT TEST in it; dispatch the top ones.
2. Verify the three gateway Builder ships landed on `origin/fast-track` and `origin/green/fast-track` and meet their done-when: `wake-sleeping-sessions` (needs a recorded real run, else not done), `handover-log-cap`, `gemini-lane-fix`.
3. Keep CI green: revert a breaking commit, never fix forward.
4. Refine or drop the 8 RAW-AGED cards; run Session_Planner on the 11 raw cards.
5. Keep the Gemini lane fed, always `<card>:low`.

## Rules the operator set (do not ask him again)
- Malkan RSI divergence flags are confirmed only in the simulator, never on screenshots.
- Never hand him a long prompt to paste. Save it in a file on trunk and give a one-line start that points at it.
- A feature counts as done only when a real end-to-end run is recorded.
- Gateway sessions: public tracked files only (GATEWAY_NUC.md).
- SUPER_SESSION.md Session log keeps the last 5 lines: drop the oldest before adding one.

Successor: `You are Supervisor. Login A. Continue from MyTradingSys/system/handover/SUPERVISOR_A.md`
