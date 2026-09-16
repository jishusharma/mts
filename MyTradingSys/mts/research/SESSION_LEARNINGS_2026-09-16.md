# SESSION LEARNINGS - 2026-09-16
# Written 17:35 UTC. Session name MTS-2026-09-16-1451Z.
# Read at the start of the next session.

## CODE CHANGES
- e89adb8 checkpoint-alerts: Invoke-WithTimeout rewrite (14:48 UTC).
- 3aec69a checkpoint-alerts-v2: alert fixes. Proof fires on crossing 5.
  State fires after holding two cycles.
- SR-004 removed from session_timing_rules.md (3 places). Not from Tom.
  Source was ATAS, B-level. No crypto study validates it.
- I21-I32 logged in L_ITEMS_MASTER.md.
- zone_map_2026-09-17.md created.

## CONFIRMED LEARNINGS
1. OI flat with rising price = short covering, not new buying.
2. CoinGlass CVD anchors at leftmost bar. DSA at 00:00 UTC.
   Compare slope direction only. Never values.
3. Book imbalance flips 6 times in 6 cycles: 0.25 1.52 8.14 0.46 1.65 0.44.
   Gates the verdict as hard contradiction. Every flip flips verdict.
4. Do not read OI off chart axis. Use snapshot field.
5. "First 30 minutes do not trade" was ATAS, not Tom.
6. Prior day close and gap fields computed, never read by any rule.
7. Session block (15 fields) and order_flow block (6 fields) are gauges.
   Decision: leave in production, do not delete.
8. B-profile definition contradictory. market_state_rules L50 says
   "B = balance (bell)". setup_type_rules L221 says "B = weakness" quotes
   Tom. setup_type_rules L549 says Tom never defined B criteria. L29
   classifier fix blocked until human ruling.

## MORE LEARNINGS
9. Verdict flicker has no debounce. Only 180s cooldown.
10. Log "no change" prints on cooldown suppression too. Ambiguous.
11. Interactive paste does not honor ErrorActionPreference = Stop.
    Each line runs independently. Throws do not halt execution.
12. LF-only guard: prove the line ending before adding a guard.
13. Supervisor works. Caught wrapper death at 16:55:40, restarted clean.
14. Double start at 14:48:22 + 14:48:45 was not the supervisor.
    Supervisor was not running yet. Cause unknown.
15. Loop wrapper does not always log its last cycle before dying.
    Cycle 50 had SNAPSHOT_FAIL exit=-1, then 4 more with empty exit,
    then 9-minute gap, then double start.

## STILL WRONG
- Verdict flicker no debounce.
- Book imbalance gates verdict on noise.
- Log "no change" ambiguous.
- B-profile definition unresolved.
- 30m structure missing from snapshot.
- Prior day bias flag flips aligned/contradiction within one cycle.
- SNAPSHOT_FAIL 14:37-14:39 cause unknown.
- Invoke-WithTimeout rewrite at 14:48 by unknown hand. Works. Committed.
  Not understood.

## STABLE
- Loop runs and cycles on current code.
- Supervisor watches and restarts.
- Alert fixes live. Proof-cross-5 fired correctly at #389.
- Zone map for 2026-09-17 on disk.
- All current state committed at 3aec69a.
# END
