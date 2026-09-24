# ALERT REDESIGN PROPOSAL

Generated: 2026-09-15
Basis: ALERT_AUDIT + ALERT_FAILURE_MODES
Decision: choose one of A / B / C

## OPTIONS

A. ACCEPT — behavior is correct in RANGE; document the trend
   limitation and move on.
B. PATCH — add discriminator fields (acceptance state, per-zone
   visit state, regime gate) without changing core architecture.
C. REDESIGN — replace proximity-based firing with a
   confirmed-rejection sequence and add a regime classifier as a
   hard gate.

## RECOMMENDATION

Path B — PATCH. Three additions, phased, each with a Rule 32 test
before wiring.

### Justification

Option A fails on Q8. Expectancy -138.74 pts/trade with a 16.7%
win rate against 83.3% loss rate. The behavior cannot be "accepted"
as correct when the mechanical number is that negative. The pattern
is not range-only: the 5-hour up-leg on 09-14 produced 40 alerts
with the same failure signature as the range-period alerts.
Option C is too large. Full redesign requires rewriting fire logic,
adding a confirmed-rejection sequence engine, and integrating a
regime classifier as a hard gate. Multi-week work under Rule 32.
Also risks breaking working RANGE behavior.

Option B is scoped to three fields. Each is annotation-only in
phase 1 (Rule 32 does not bind field creation). Each can be tested
against the same 3-snapshot Rule 32 gate before wiring into any
verdict decision.

### Phase 1 (annotation only, no verdict impact)

1. zone_visit_state — persistent map of zone identity
   (name + type) to test_count, first_test_at, last_test_at,
   last_resolution.
2. regime_label — derived feature from existing fields
   (vwap.slope, cvd.slope, structure swings, trade_flow deltas).
   Not a new engine rule; a feature vector.
3. level_acceptance_state — per active zone tri-state:
   approaching / accepted / rejected. Derived from
   conditions.price_vs_va + cand.math.substate + small bar history.

### Phase 2 (verdict wiring, Rule 32 gate)

Each phase-2 wiring is a new engine rule. Each requires 3-snapshot
proof that at least 1 of 3 verdicts changes. Test set: 3 snapshots
from the 2026-09-14 up-leg (13:33, 15:00, 17:30).

Candidate phase-2 rules:
- Suppress new ct_short when zone_visit_state.test_count >= 3.
- Suppress new ct_short when regime_label = TREND_UP.
- Downgrade rank-1 when level_acceptance_state = accepted.
### What this proposal does NOT do
- Does not change target selection (FM-4). Separate proposal.
- Does not restructure the alert firing path.
- Does not touch compiled_engine.md.
- No rule wired without 3-snapshot proof.

### Open questions for the next session
1. Zone identity survives drift? weekly_vah on 2026-09-14 moved
   78,213.51 -> 78,870.12 (657 pts). Identity scheme must tolerate
   structural updates.
2. Should regime_label treat TRANSITION as a separate state, or
   collapse into RANGE?
3. Marginal new high (79,570 vs 79,860) — does it need its own
   field, or is it covered by swing sequence tracking?

## APPENDIX — AI RECONCILIATION

Three AIs (Claude, GPT, Grok) asked to design and falsify fixes
for three candidate gaps:

| Gap | GPT design | Grok verdict | This proposal |
|-----|------------|--------------|---------------|
| Swing sequence | state_swings.json, HH/HL/LH/LL classifier | REJECT (reconstructible) | DEFER. 2-snapshot buffer, no classifier. |
| Zone visit counter | state_zones.json, visit + resolution | DEFER (existing proof may cover) | Phase 1 annotation. Rule 32 gate. |
| Regime label | state_code.json TREND/RANGE enum | REJECT (already derivable) | Phase 1 derived feature. No new enum field. |

Unresolved divergence: marginal new high materiality (GPT yes,
Grok no, Claude conditional). Held open.