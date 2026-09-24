# SESSION HANDOFF — 2026-09-13

## CRITICAL STATE (read this first)
- APPARATUS IS NOT RUNNING. Last cycle was 2026-09-12 20:40:07.
- state_code.json ~12h stale. current_market_state.md ~12h stale.
- Two orphan java.exe from 2026-09-13 11:48:31 AM (unknown mode, likely
  historical that hung). Diagnose before restart.
- Latest snapshot in runtime_data/snapshots is BTCUSDT_historical_20260913T100000Z.json
  — historical, not live. Live snapshots stopped 2026-09-12 20:40.
- Snapshot count is 290 — 200-cap not enforced.
- Historical snapshot files (BTCUSDT_historical_*.json) sitting in live
  snapshots dir; quad_classify and outcome_labeler may be consuming them.

## FIRST ACTIONS NEXT SESSION
1. Read: MyTradingSys\SESSION_ENTRY.md (read order 1-9)
2. Read: MyTradingSys\research\apparatus_fixes.md
3. Read: MyTradingSys\runtime\session_state.json (thesis)
4. Read: COMMANDS.md (project root)
5. Diagnose orphan javas:
   Get-CimInstance Win32_Process -Filter "Name='java.exe'" |
     Select-Object ProcessId, CreationDate, CommandLine | Format-List
6. Kill orphans if no apparatus running:
   .\stop_day.ps1
7. Move historical snapshots out of live dir:
   New-Item -ItemType Directory -Path "runtime_data\snapshots\historical" -Force | Out-Null
   Get-ChildItem "runtime_data\snapshots\BTCUSDT_historical_*.json" |
     Move-Item -Destination "runtime_data\snapshots\historical\"
8. Trim live snapshots to 200 (see COMMANDS.md diagnostics)
9. Restart apparatus:
   .\mode.ps1 -M armed

## MARKET THESIS ON DISK
- Direction: SHORT, high confidence
- Target 76,835 hit on 2026-09-13 10:00 (price 76,836)
- Next magnet: 76,300 (heatmap cluster, thin liquidity below 77,000)
- Invalidation: 5m close > 77,115 VWAP with CVD rising
- Bounce watch at 76,300 if CVD flips + volume spike

## WHAT WAS DONE THIS SESSION
- Rule 37 fix: DSA reads closed bars only (dropFormingBar)
- IBC-008 trend override: below_val + CVD falling suppresses CT Long
- IBC-012: popup TopMost removed, kill-prior on spawn
- Candle-close alignment in apparatus (fires at :10 past boundary)
- Singleton lock (PID TS, stale > 600s)
- Materiality gate + 180s cooldown
- session_log append regex bug fixed (line 427, .Replace not -replace)
- quad_classify.py written (price x CVD x OI classifier)
- session_state.py + session_log.json + log_decision.py (SSOT)
- outcome_labeler.py (190 labels)
- VVP-002 written (visual_validation_protocol_vvp002.md)
- COMMANDS.md written (project root)
- SESSION_ENTRY.md read order 1-9
- Backups consolidated to backup_session/ (single dir, check-then-act rule)
- VVP-001 audit: deprecated liquidation fields removed from checks
- SUPERVISOR_SESSION_PROMPT.md deleted
- IBCWP renamed to apparatus_fixes.md

## OPEN ITEMS
- Orphan javas (diagnose first)
- Event probability layer: parked until 500+ labels (currently 190)
- IBC-008 Rule 32: 3/3 collected, validated on 2026-09-13 cycles 1-4
- alignment_pass field on closed-bar data: parked
- proof_direction_details empty in some cards: cosmetic
- Heatmap field map: worker task never completed

## RULES (IBCWP = Issue Bulk Commands When Possible)
- READ BEFORE WRITE. Backup. Select-String anchor. Abort if count != 1.
  Syntax check. Grep for new symbols.
- Atomic delete: backup + grep + delete in ONE block.
- Never invent or misrepresent names. Ask if unclear.
- Do not kill java blindly. Java is state machine child. Use .\stop_day.ps1
  or .\mode.ps1.
- Check-then-act on files, dirs, IDs. Not create-then-dedupe.
- Bulk commands when possible.
- Critical files: hash before/after + diff. See DSA_SESSION_PROMPT.md.
