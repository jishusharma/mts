# B059 - RANK-1 ZONE DRIFT

Register row: MyTradingSys/mts/research/BUGS.md B059.
Convention: one item, one doc. Verbatim ask at top when available. Updates appended chronologically, newest last.

## VERBATIM ASK

No verbatim ask on record (opened 2026-09-20). Row title and evidence transcribed below from BUGS.md.

Title: Rank-1 candidate zone price drifts with post-funding window; substate stays above/below on a zone that is 130 pts off price.

Evidence (2026-09-20 apparatus_log.txt 09:00-09:41Z): pf_vah rank-1 printed 80346.11, 80365.02, 80368.85, 80369.87, 80373.47 across five cycles; substate=above on every one; price was 80411 to 80524. Zone cannot trigger.

## STATE

2026-09-22 OPEN.
Fix shape: freeze pf_vah for the duration of a candidate, or hide the candidate when substate disagrees with price position.

## UPDATES (chronological, newest last)

### 2026-09-22T18:00Z - coordinator, session MTS-2026-09-22-1737Z

Item doc created during T039 functionality-doc sweep.
