# NEXT SESSION PROMPT (handoff 2026-10-09 evening, from the Stage 1 supervisor session jisnb/stage1-2026-10-09)

Paste the block below into a new Claude Code session (Win App, bypassPermissions). Overwrite this file at each handoff.

```
MTS supervisor session. Read CLAUDE.md, STATUS.md, then MyTradingSys/system/CONTROL_ROOM.md. Work in a worktree, never the live tree.
0. Control Room first (https://claude.ai/artifact/EoHi2qTMEsbR4VsKWuo2su): run the pickup (Inbox + answered decisions D08-D10;
   D08 turn_of_candle next step, D09 fee gate on/off, D10 heartbeat age), apply them, rebuild + republish.
1. Live tree is behind origin and holds other sessions' uncommitted work (bigtrade FINDINGS/backtest/bigtrade). Not yours.
   Their 9 open screenshots need the shot ids written into that study's extract before `shot.py read` accepts them.
2. Stage 1 left: B148 part 5 (heartbeat-age liveness, limit from D10, fail-first test incl. pid reuse), F-BT-12 VWAP anchor,
   F-BT-10/11 OI (5m series instead of hourly; recorder holes), F-BT-20/21. Java F-BT-09/F-BT-14 are DEPLOYED (verify tomorrow's
   naked_pocs file gets 2026-10-09 and prior_day.poc stays near the trade-level POC).
3. Stage 2: read T081 and T080 reports (research/fast_track_2026-09-27/T081_..., T080_...), then T082 re-run (capture matrix + Tom
   core backtest on the fixed volume profile / naked POC) and T085 (97 % time-exits).
4. Apply D08/D09/D10 answers. T083/T084 lead checks only after T082.
End: update control_room.json (verdict, evidence, changelog), ship, overwrite this file.
```

## State at handoff
- Deployed 2026-10-09 12:46 IST: F-BT-09 (buildVp conserves volume) and F-BT-14 (naked-POC writer), engine restarted per D03; B148 parts 1-4 already ran.
- Written: GO_LIVE_BAR.md (T086), TURN_OF_CANDLE_ORIGIN_2026-10-09.md (D01), backfill_naked_pocs.py (applied once).
- Waiting on the operator: D08, D09, D10 on the page. Windows: restarts after updates / power loss are the remaining uptime risk (sleep is already off).
