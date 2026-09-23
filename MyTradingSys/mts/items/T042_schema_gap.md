# T042 - SCHEMA GAP

Register row: MyTradingSys/mts/research/BUGS.md T042.
Convention: one item, one doc. Verbatim ask at top. Updates appended chronologically, newest last.

## VERBATIM ASK (source)

No operator verbatim quote on file. Candidate recorded in:
- MyTradingSys/mts/runtime/live_session_journal.md, post-close note 2026-09-23T01:30Z.
- MyTradingSys/mts/runtime/NEXT_SESSION_HANDOFF.md, step 4.

Recorded text (coordinator note, session MTS-2026-09-23-0430Z close):
Schema gap observed: no 30m/4h/daily/weekly structure in snapshot. No OI/CVD peak reference. 1h structure stale while 1h klines fresh.

## STATE

2026-09-23 OPEN. Register row added this session. Producer-side gap: the snapshot writer emits structure.{1h,15m,5m} only. No 30m/4h/daily/weekly structure block exists in the snapshot. No OI peak or CVD peak reference exists in the snapshot.

Relationship: T041 is the consumer defect (verdict path does not read HTF structure). T042 is the producer defect (snapshot schema does not carry the structure). Separate fix surfaces.

## EVIDENCE SEEN THIS SESSION

current_market_state.md (boot paste) shows structure.1h.stale=true, structure.15m.stale=true, structure.5m.stale=true.
Snapshot JSON (boot paste) has a structure block with keys 1h, 15m, 5m only. No 30m, 4h, 1d, or 1w keys.
The claim that 1h klines are fresh on disk is from the journal post-close note, not verified this session.

## UPDATES (chronological, newest last)

### 2026-09-23T08:31Z - coordinator, session MTS-2026-09-23-0831Z

Registered. Chose separate row rather than folding into T041: producer vs consumer are separate fix surfaces.
