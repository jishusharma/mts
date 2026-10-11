# B066 - RANK-1 DISTANCE GATE

Register row: MyTradingSys/research/BUGS.md B066.
Opened: 2026-09-24. Split from B059 by MTS-2026-09-24-0639Z after Claude review.

## THE DEFECT

Rank-1 candidate shown at tier=trigger_ready while price is 150 pts away.
Substate says above but price cannot reach the zone without a large move.

## EVIDENCE

2026-09-20 apparatus_log 09:00-09:41Z (preserved here from B059 row):
  pf_vah rank-1 printed 80346.11, 80365.02, 80368.85, 80369.87, 80373.47
  across five cycles; substate=above on every one; price was 80411 to
  80524. At the extreme cycle: pf_vah 80373.47, price 80524, distance
  150.53 pts. Zone could not trigger.

## RELATION TO B059

B059 was filed as one row combining drift and this distance issue.
Deep-dive 2026-09-24 separated them: B059 is bin-edge drift inside
buildVp; this row is the candidate-selection gate. Different code
paths, different fixes.

## FIX SHAPE (not decided)

Option A: hide rank-1 when tier=trigger_ready and distance_pct > N.
Option B: downgrade tier when substate and price side disagree.
Option C: leave as-is; operator reads distance_pct and judges.

Threshold value in A or B is new rule surface. Needs Tom citation or
documented exception.

## STATE

2026-09-24 OPEN. Not started.


## STATE

2026-10-11 CLOSED as option C (handled by the 0.1% tier rule, no new threshold). Receipt: src/test/java/datafeed/SetupCandidatesBuilderTierTest.java. A gate (A/B) needs a Tom-cited threshold.
