# T041 - ENGINE VERDICT TIMEFRAME GAP

Register row: MyTradingSys/mts/research/BUGS.md T041.
Convention: one item, one doc. Verbatim ask at top. Updates appended chronologically, newest last.

## VERBATIM ASK (operator, 2026-09-22 continuation)

"note this gap and ask for a audit and research on this by a worker"

Context at time of ask:
  Operator observed a 7-hour up leg on the BTCUSDT 1h klines (10:00-17:00 UTC, close 85856.2 to 86527.5, +671).
  Engine verdict stayed WATCH ct_short throughout. Engine has no read on the hourly leg.
  Also: snapshot structure.1h.stale = true (levels 86309.7 / 86209.1) while MyTradingSys/data/klines/BTCUSDT_1h.json is fresh (mtime 2026-09-23T00:31Z).
  CVD delta_1h -1943, delta_4h -3913, OI direction falling (-0.21 pct 1h). Covering-rally shape, not fresh buying.

## STATE

2026-09-22 OPEN. Not yet classified as bug vs design. Audit will decide.
Candidate labels: (a) correct behavior — engine is designed for tape, not legs; (b) missing layer — no multi-timeframe context; (c) defect — engine cannot see legs it should see.
Second open question: structure.1h.stale = true with fresh 1h klines on disk. Is that a mtime check bug, an update path bug, or intended?

## UPDATES (chronological, newest last)

### 2026-09-23T01:00Z - coordinator

Item doc created. Worker dispatch at Dumps/workers/T041_verdict_timeframe_audit/DISPATCH.md.
