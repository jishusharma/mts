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

## OPERATOR TRADE 2026-09-16 (not from MTS)

Counter-trade short at the 76000-76045 ceiling cluster.
Source: operator intuition. MTS did not signal it.

Entry: 15 scale-in sell fills, 75525 to 76381, avg 76075.68.
Exit: 3 close-buy fills, avg 75778.00.
Size: 0.1953 BTC.
Gross: 0.000767 BTC. Fees: 0.000105 BTC. Net: 0.000662 BTC.
About 5.4% of account equity. Hold time 26 minutes.

Why MTS missed it:
- Loop was OFF during the entry build (stopped 17:52:52, restarted 18:15:33).
- On restart engine printed ct_short @ 4h_vah 76054.47, nrr 1.77. Same zone,
  same direction. Below the 2.0 cap. Verdict WAIT_RR.
- Operator found the same zone independently and won.

What the operator did that the engine does not:
- 15 scale-ins on strength.
- No stop placed anywhere.
- Exit at 75778. Absolute low printed at 75364.

## SWEEP ENTRY FINDING - largest gap of the day

Six counter-trade setups today printed correct direction and correct zone.
All six failed the 2.0 net reward-to-risk cap. All six would have cleared
if the entry were the sweep wick extreme instead of the zone price.

Tom enters at the sweep. The engine enters at the level. That is the whole
difference today.

Evidence:
1. 13:48 scalp_short @ vwap, nrr 1.95. Missed by 0.05.
2. 17:12 ct_long @ 4h_val, nrr 2.01. Flickered one cycle.
3. 17:15 ct_long @ 4h_val, nrr 2.05. Flickered one cycle.
4. 17:23 ct_long @ 5m_swing_low 75620, nrr 1.94. Bounce ran 100 pts.
5. 17:45 ct_long @ pf_val, nrr 1.95. Bounce ran 153 pts.
6. 17:40 sweep low 75386, rally 1100+ pts. Engine printed longs under cap.

Same setup as the operator's winning short:
18:16 engine printed ct_short @ 4h_vah 76054.47, nrr 1.77. Operator shorted
the same zone and won.

Action: draft a sweep-entry rule. Zone is reference. Entry is the sweep
wick extreme. Three snapshots of proof before wiring into the verdict.
Rule 32 gate. Today is snapshot one. Two more sessions minimum.

## I33 CORRECTION - OI field

Scope narrower than first written. Field stalled 17:40-17:53 (flat / 0.0 /
HIGH confidence), then recovered on loop restart at 18:16 (rising / 0.21 /
HIGH). It is a stall that recovers on restart, not a permanent break.
Still returns wrong value with HIGH confidence. That is the dangerous part.

## LOG MESSAGE BUG - repeated

Alerts #391, #392, #394 all printed the state change as same-value:
"STATE B/below_val -> B/below_val" and "STATE B/in_va -> B/in_va".
Cause: $lastState is updated before the alert fires on the second cycle.
Fix: add $pendingStateFrom to record the prior state.
Cosmetic. No verdict impact. But makes state alerts unreadable.
