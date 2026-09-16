STATUS: Session 2026-09-17 open. L29 and I26 landed. Loop restarted on new jar.

# NEXT SESSION HANDOFF
# Written 2026-09-16 21:00 UTC

## READ FIRST
1. MyTradingSys/mts/research/SESSION_LEARNINGS_2026-09-16.md
2. MyTradingSys/mts/research/L_ITEMS_MASTER.md (I30-I39)
3. MyTradingSys/mts/research/zone_map_2026-09-17.md

## WHAT LANDED THIS SESSION (2026-09-16 20:32Z to 21:00Z)
- I36 CLOSED: start-trading-day.ps1 log "STATE X -> X" fixed with $pendingStateFrom.
- I26 CLOSED: B profile ruling = weakness at the extreme (Tom). market_state_rules.md L50 rewritten.
- L29 CLOSED: buildVp "B" renamed to "TWOPEAK". classifyState rewritten on vwap_slope + cvd_slope + price_vs_va. Rule 32 test: 3/3 outside-VA snapshots changed to trend_healthy.
- mts_math.py STATE.classification aligned to Java. Now emits real state, keeps vp_shape under a new key.
- Docs updated: compiled_engine.md L30/L322, data_schema_v1.2.0.md L78/L90, trading_card_generator.md L378.
- Loop restarted on new jar. Supervisor ON.

## WHAT IS DIFFERENT FROM THIS MORNING
- Engine no longer forces state=balance on every snapshot. Was 2090/2090 before.
- Snapshot shape field now emits TWOPEAK / D / P. No more collision with Tom's B.
- Tom's B (top-heavy weakness) is NOT yet computed. That is future work.

## BIGGEST FINDING
The classifier was locked. All 2090 snapshots on disk emitted shape=B. The engine
was in balance state always, and generated scalp_short/long at VWAP bands against
trending markets. 671 of 2090 snapshots had shape=B while price was outside value
area. Rule 32 test: proposed classifyState flips 3/3 of those to trend_healthy.

## MISSION FOR NEXT SESSION
1. Watch next 20 cycles for candidate mix change. Expect fewer naked scalps at VWAP in trend.
2. Collect Rule 32 evidence for sweep entry (I34). Days 2 and 3.
3. Fix I30 (book imbalance instability). Smoothed 5-cycle window or drop from contradiction.
4. Fix I31 (verdict flicker). Two-cycle persistence like the state debounce.
5. Resolve I33 (OI field stall). Investigate source after 17:40 UTC.
6. Investigate I29 (dual builder path in MarketDataSnapshot.java, line ~1065).
7. Consider drafting Tom's B detector as a new field. Not yet a rule.

## LOOP STATUS AT CLOSE
- Wrapper 5308, state machine java 18060, supervisor ON.
- Last price 76,163.10, TWOPEAK/above_vah, nrr 1.61 WAIT_RR.

## HARD RULES
- Never bare-kill java. Use stop-day.ps1 or mode.ps1.
- No double-run of mode.ps1.
- Boot rules 5 and 6 apply.
- Write-NoBom requires dot-sourcing shared-functions.ps1 first.
- Interactive paste does not honor ErrorActionPreference = Stop.

# END
