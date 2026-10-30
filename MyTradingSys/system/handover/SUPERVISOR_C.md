# SUPERVISOR C notes (super-session-1, Agent sonnet, login C, JIS-DESKTOP) - rewritten each wake

Started 2026-10-30T17:20Z. Work until 2026-10-31T05:06Z (plan). Wake 1 at 18:10Z. 5h window reset 17:50Z (now 5 pct, next reset 22:50Z), week 40 pct (cap 85).

## Running / waiting
- Haiku a4a6d3d01555c8ff0 haiku-refresh-stale-ready-cards: STALE 24 -> 5 (5 held: look delivered), local sha b328ea3f1 in worktree agent-a4a6d3d01555c8ff0, NOT pushed (its offline gate failed on role_budget/token/successor_wake in its tree; trunk supervisor.md is 7413 B so recheck). Re-ship after CI green via SendMessage to it; verify git cherry + one recount.
- Opus a62eb6666d8cbc5a0 (stream F, bug-supervisor-idles-after-wake-retired, approval d-supervisor-idle-bug): 6/6 built, local commits 2037b9246 9b0542273 7b66a91a7 in worktree agent-a62eb6666d8cbc5a0, NOT shipped (CI red). Re-ship when CI green.
- Haiku a1b340f351ac8ff74 (read-only idle-bug done_when check): finished.

## Done this wake
- Revert of false "GPT down (auth)" lane state: eba62ccc2 -> trunk 98d5ed195 (cherry empty). Cause: codex CLI on this desktop has no OpenAI login (401); `codex_run.py tick` here also overwrote lane_state/codex_usage. DO NOT run codex_run.py on this desktop.
- NUC ssh gate tick: lab tree salvaged 64 files, but claim push fails (no git login in the ssh session). So GPT audits go via desk row to an interactive NUC session: 20261030-174331 (6 audits). Gemini desk row 20261030-173120 (4 cards, :low).
- Signal q-f7aac9 to desktop-f7iu69n: run testnet-trade-readout-daily (stream C). b-230ce8 ack NOT sent (no run landed).
- DECISION (OURS): no manual claim before the codex tick (the runner claims itself and skips claimed cards). DECISION (OURS): started F Opus worker the same wake as Haiku (parent order beats RAMP new=1).

## Blocked / next
- CI RED: 5 fails; 067b81238 (splits revert), afc08114b (B163 revert) landed by others; run 41103757447 queued. Start no shipping work until green.
- Then: Haiku haiku-register-orphan-tests; stream A layer-review-tom-guidance (STALE until the Haiku refresh ships); stream D live-aid-replay-mode-fixture-feeds is RAW -> Session_Planner first; re-ship Opus F work.
- Feeder: file check cards in another lane per ship (none yet: only revert/desk rows).
- Noticed: handover() lacked a work-period check (fixed in the Opus F build); test_successor_wake read the real loop folder (fixed 7b66a91a7).
