# NEXT SESSION PROMPT (handoff 2026-10-09, from MTS-2026-10-09-APP-SUP-control-room)

Paste the block below into a new Claude Code session (Win App, Opus, bypassPermissions). Overwrite this file at each handoff.

```
MTS supervisor session. Read CLAUDE.md, STATUS.md, then MyTradingSys/system/CONTROL_ROOM.md. Work in a worktree, never the live tree.
0. Control Room first (https://claude.ai/artifact/EoHi2qTMEsbR4VsKWuo2su): run the pickup in CONTROL_ROOM.md now
   (Inbox items + answered decisions D01-D07), then rebuild + republish. Every operator question goes there as a decision.
1. Live tree is 1 commit ahead of origin (188fa67, B154+B155, another session's) and holds uncommitted bigtrade work
   (research/bigtrade_2026-10-09/, backtest/bigtrade/). Not yours to edit: get them shipped by their owner or via a
   desk task; until then the page reads findings only with --data-root <live tree>. Deploy origin to the live tree only
   when `git merge --ff-only` is possible (CLAUDE.md deploy rule).
2. Stage 1 (trustworthy measurements) is the road's current step. In order, each as staged .new + fail-first test:
   B148 (daily-loss monitor re-auths as MAIN), B146 + T081 plan (min stop width), F-BT-09 (buildVp weight
   normalisation; acceptance: POC within 50 of 85,580 on 2026-10-06 and 83,400 on 2026-10-07), F-BT-14 (naked-POC writer).
   Java waits for the restart window the operator picks in decision D03.
3. Then T081 backtest D and T080 maker model (Stage 2) via Sonnet workers; report fee_R per cell.
4. Apply D01 (turn_of_candle), D02 (1m ground truth), D04 (uptime), D06 (go-live bar -> T086) per the operator's answers.
5. Screenshots: 13 open (shot.py status); close them if D07 = yes.
End: update control_room.json (verdict, evidence, changelog), ship, overwrite this file with the next prompt.
```

## State at handoff
- Shipped: Control Room generator + Inbox + decisions loop (938ccc4), road tasks T080-T086 filed and mapped on the page.
- Scheduled: task `mts-control-room` 09:00 and 21:00 local (runs only while the Claude app is open; operator to click "Run now" once).
- Waiting on the operator: decisions D01-D07 on the page.
