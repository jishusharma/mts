# T042 - SCHEMA GAP

Register row: MyTradingSys/research/BUGS.md T042.
Convention: one item, one doc. Verbatim ask at top. Updates appended chronologically, newest last.

## VERBATIM ASK (source)

No operator verbatim quote on file. Candidate recorded in:
- MyTradingSys/runtime/live_session_journal.md, post-close note 2026-09-23T01:30Z.
- MyTradingSys/runtime/NEXT_SESSION_HANDOFF.md, step 4.

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

### 2026-09-23T18:00Z - coordinator, session MTS-2026-09-23-1445Z

Worker T042-W1 round 2 accepted. Real producer anchors now known:

MarketDataSnapshot.java:
  L687 private ObjectNode buildStructure(Map<String, JsonNode> mtf, double currentPrice)
  L689 String[] tfs = {"1h","15m","5m"};
  L689 int[] lookbacks = {24,16,12};
  L691-696 empty branch writes swing_high=0.0, swing_low=0.0, stale=true
  L716 boolean stale = (swingHigh < currentPrice) || (swingLow > currentPrice);

Second caller (missed by worker 13):
  L947 Map<String, JsonNode> mtf = fetchMultiTimeframeAsOf(symbol, asOf);
  L1080 ObjectNode structure = buildStructure(mtf, currentPrice);

Two producer edit sites, not one. The live path (L197) and the historical path (L1080) both call buildStructure. Both must be verified after any tfs[] extension.

Consumer edit points confirmed:
  mts_math.py L185-193 field-map tuples (9 currently, add 12 for new TFs)
  mts_math.py L316-327 SWING loop, one-line TF list extension

Schema_version bump proposal 5.1.0 -> 5.2.0 accepted as additive-minor. schema_v5.1.0_spec.md is session-scope only; does NOT define structure or peaks. Net-new spec needed.

Open item at close: buildStructure caller's mtf map is populated by fetchMultiTimeframe / fetchMultiTimeframeAsOf. The kline fetch set must be extended to supply 30m/4h/1d/1w or the new TF branches stay empty.
