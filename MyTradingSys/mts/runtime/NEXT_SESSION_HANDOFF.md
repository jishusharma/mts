# NEXT SESSION HANDOFF
# Rewritten 2026-09-17 12:40 UTC by MTS-2026-09-17-1142Z.

STATUS: Session MTS-2026-09-17-1142Z open. Loop running, single chain.
Supervisor 32 -> start-trading-day 16708 -> mvn 7296 -> java 13144.
Anchor 2026-09-17T13:30:00Z. Pre-anchor snapshots show session block zeros.

## READ FIRST
1. MyTradingSys/mts/research/BUGS.md - defect SSOT.
2. MyTradingSys/mts/research/AUDIT_2026-09-17_TRACKER.md - full audit + W1/W2.
3. Dumps/workers/W1_verify_context/worker_reply.md
4. Dumps/workers/W2_live_tracking/worker_reply.md

## WHAT LANDED THIS SESSION
1. Build-Check extended to scan MyTradingSys/mts/conditions/*.md.
   apparatus_fixes.md updated with permitted non-ASCII note. PASS.
2. Worker folder layout at Dumps/workers/. W1 and W2 replies saved.
3. B035 CLOSED. SetupCandidatesBuilder.java L541 threshold changed
   from (0.4, 0.6) to (0.67, 1.5). Live evidence: 2.58 read as balanced.
   hash 3ED13909 -> C30EB08F.
4. B020 CLOSED. Timezone note added at session_timing_rules.md L24-26.
   Explains EST year-round vs EDT. Doc-only.
5. Defect 1 fix in MarketDataSnapshot.java L797-817. day_type now
   derived from IB width / prior day range. Provisional thresholds.
   hash 99938454 -> 7627EBA9.
6. B042 OPEN. day_type provisional thresholds need 3-snapshot evidence.

## FIRST ACTION NEXT SESSION
Confirm day_type populates after 13:30 UTC anchor.
  $s = Get-ChildItem data\snapshots -Filter 'BTCUSDT_*.json' |
       Sort-Object LastWriteTime -Descending | Select-Object -First 1
  $j = Get-Content $s.FullName -Raw | ConvertFrom-Json
  $j.session.day_type
  $j.session.day_type_confidence
Expected: trend_up / trend_down / range / balance. If still UNKNOWN
after 13:30, read MarketDataSnapshot.java L797-817 and check whether
`seen`, `ibHigh`, `ibLow`, `priorDayHigh`, `priorDayLow` are all
populated for the current cycle.

## STILL OPEN
- Defect 3: opening range rule not wired. No Tom threshold exists in
  any condition file. Decision needed: set screener-provisional
  threshold (like B042) or mark permanently manual.
- B042: day_type provisional thresholds, no 3-snapshot evidence.
- Audit post-fix queue from AUDIT_2026-09-17_TRACKER.md.

## OPERATOR NOTE - mode.ps1 vs supervisor
Do not run mode.ps1 while the supervisor is up. Supervisor spawns a
second loop inside its restart window, racing the same lock and files.
Clean sequence:
  1. Write data\supervisor_stop.flag.
  2. Poll until supervisor process is gone.
  3. Delete the flag.
  4. Run stop-day.ps1.
  5. Poll until no java datafeed.Main remains.
  6. Clear orphan data\apparatus.lock if any.
  7. Start supervisor only. It starts the loop.

## HARD RULES
- Never bare-kill java. Use stop-day.ps1 or mode.ps1.
- Never run mode.ps1 while supervisor is up.
- Worker has no shell. Operator runs all commands.
- Worker folder layout: Dumps/workers/<name>/. Reply saved by
  coordinator, not worker.

# END