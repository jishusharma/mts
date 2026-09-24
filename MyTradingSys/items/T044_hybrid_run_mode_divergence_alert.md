# T044 - HYBRID RUN MODE DIVERGENCE ALERT

Register row: MyTradingSys/research/BUGS.md T044.
Convention: one item, one doc. Verbatim ask at top. Updates appended chronologically, newest last.

## VERBATIM ASK (dsa_developer_implementation_tasks.md TASK 4.2)

Source lines 356-369.

### TASK 4.2 - Hybrid Run Mode
Priority: P1 | Time: 4 hours | Files: DsaHybridRunner.java (new)

What to build:
Run REST snapshot and WebSocket feed in parallel. Compare outputs.

Validation gate: 20 consecutive trading cards from WebSocket DSA match REST DSA within +/-3 confidence points -> switch production to WebSocket.

Acceptance criteria:
- [ ] Both paths running, logging differences.
- [ ] Divergence >3 points triggers alert, not silent override.

Verbatim acceptance line (L366):
> - [ ] Divergence >3 points triggers alert, not silent override.

## STATE

2026-09-23 OPEN. Acceptance criteria unchecked in source. No implementation work performed. Priority P1 per source.

## UPDATES (chronological, newest last)

### 2026-09-23T15:30Z - coordinator, session MTS-2026-09-23-1445Z

Item doc created from dsa_developer_implementation_tasks.md TASK 4.2. Verbatim ask captured. Source-folded as part of T039 sweep. Register row added this session.