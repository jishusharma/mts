STATUS: Session 2026-09-17 open. Prior session closed clean at ee895ba. Audit pending.

# NEXT SESSION HANDOFF
# Rewritten 2026-09-17 05:50 UTC

## READ FIRST
1. MyTradingSys/mts/research/AUDIT_2026-09-17_TRACKER.md — audit plan, step list, tracker.
2. MyTradingSys/mts/research/L_ITEMS_MASTER.md — open loops I21-I40.
3. MyTradingSys/mts/research/apparatus_fixes.md — SESSION 2026-09-17 AI MISTAKES section.

## WHAT LANDED LAST SESSION (2026-09-16 evening)
- I36 CLOSED: start-trading-day.ps1 log "STATE X -> X" fixed with $pendingStateFrom.
- I26 CLOSED: B profile = weakness at the extreme (Tom). market_state_rules.md L50 rewritten.
- L29 CLOSED: buildVp "B" renamed to TWOPEAK. classifyState rewritten on vwap_slope + cvd_slope + price_vs_va.
- mts_math.py STATE.classification aligned to Java.
- Docs updated: compiled_engine L30/L322, data_schema L78/L90, trading_card_generator L378.
- Loop restarted on new code. Live snapshot emits TWOPEAK.

## SESSION 2026-09-17 FIRST TASK
Independent audit of extracted code and tests. Plan on disk. Worker session needed.
Worker prompt, method, and scope are in AUDIT_2026-09-17_TRACKER.md.

## SECONDARY FINDINGS FROM 2026-09-17 REVALIDATION
- I40 OPEN: profile shape taxonomy does not match Tom. D has zero corpus hits.
  TWOPEAK is a rename, not a Tom term. Decision needed, not yet acted on.

## MISSION QUEUE (from prior session, still open)
1. Run the independent audit.
2. Collect Rule 32 evidence for sweep entry (I34). Days 2 and 3.
3. Fix I30 (book imbalance instability).
4. Fix I31 (verdict flicker).
5. Resolve I33 (OI field stall).
6. Investigate I29 (dual builder path in MarketDataSnapshot.java).

## HARD RULES
- Never bare-kill java. Use stop-day.ps1 or mode.ps1.
- No double-run of mode.ps1.
- Boot rules 5 and 6 apply: no fabricated values, no invented commands.
- Worker has no shell. Operator runs all commands. Worker analyzes pasted output.
- Write-NoBom requires dot-sourcing shared-functions.ps1 first.

# END

## SUPERVISOR RESTART COMMAND

Start-Process powershell.exe -ArgumentList @(
    "-NoProfile","-ExecutionPolicy","Bypass",
    "-File","C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\scripts\core\loop-supervisor.ps1",
    "-Mode","armed","-IntervalMin","1","-RestartGraceSec","90"
) -WindowStyle Hidden

Verify: Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" | Where-Object { $_.CommandLine -match "loop-supervisor" } | Select-Object ProcessId, CommandLine
Stop:   New-Item .\data\supervisor_stop.flag -ItemType File -Force
