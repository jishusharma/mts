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
### 2026-09-24T07:10Z - coordinator, session MTS-2026-09-24-0639Z

Deep dive. Prior framing wrong on two counts, corrected.

Mechanism (corrected):
  Anchor MarketDataSnapshot.java L75-77 is stable within a UTC day.
  Window L79-81 grows by one 1m bar per cycle; not a sliding window.
  Drift source is bin edges at L501-514: minP/maxP anchor the grid, so
  a new extreme shifts every bin key. Evidence: BUGS.md prior values
  80346.11 -> 80373.47 (delta 27.36 pts over 4 cycles).

Target (corrected):
  buildStructure L687-726 contains no pf_vp code. Pf_vp is built at
  L144 (live) and L1066 (historical), both via buildVp.

Fix landed:
  New overload buildVp(bars, includeHvnsLvns, fixedBinSize).
  fixedBinSize > 0 -> binOrigin = floor(minP/binSize)*binSize; bin
  edges snap to a global 10-USD grid. numBins = ceil(range/10)+1.
  Both call sites pass 10.0.
  sha256 74B14A74 -> 52FF88CF. CRLF 1468, LF-only 0, BOM NO.
  Build-Check PASS 2026-09-24T07:10Z.

Not the same defect:
  B059 evidence also cited "zone cannot trigger" with pf_vah 80373
  and price 80524. Distance 150 pts. Rank-1 distance gate is a
  separate defect. Needs its own row.

Status: OPEN. Live tape confirmation pending next loop start.
