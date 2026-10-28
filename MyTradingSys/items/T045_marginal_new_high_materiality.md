# T045 - MARGINAL NEW HIGH MATERIALITY

Register row: MyTradingSys/research/BUGS.md T045.
Convention: one item, one doc. Verbatim ask at top. Updates appended chronologically, newest last.

## VERBATIM ASK (ALERT_REDESIGN_PROPOSAL.md L87-88)

Source context: paragraph immediately following the three-gap table (Swing sequence / Zone visit counter / Regime label).

Verbatim:
> Unresolved divergence: marginal new high materiality (GPT yes,
> Grok no, Claude conditional). Held open.

## STATE

CLOSED 2026-09-24. Ruling: materiality is a consumer-layer concern, not a producer-layer one. Fundamental readings emit raw; future consumer declares its own threshold.

## UPDATES (chronological, newest last)

### 2026-09-23T15:30Z - coordinator, session MTS-2026-09-23-1445Z

Item doc created from ALERT_REDESIGN_PROPOSAL.md L87. Verbatim ask captured. Source-folded as part of T039 sweep. Register row added this session. Resolution requires coordinator decision; item remains OPEN.

### 2026-09-24T11:22Z - coordinator, session MTS-2026-09-24-1100Z

Closed by operator ruling. Question was whether a marginal new high (small overshoot of prior high) counts as a new-high event for the alert.

Verbatim ruling:

> even a cent rise is a new high as per mechanicals - how we use this info matters - so the specific cases must be discussed

Interpretation applied: the producer emits fundamental readings (swing_high, swing_low, stale) as raw facts. No materiality threshold is added at the producer layer. Any consumer that needs materiality declares its own threshold and carries its own rule-surface and citation burden.

Doctrine source: PROJECT_VISION.md - isolate first, combine only after each read is independently validated.

No code change. No schema change. Documentation-only close.
