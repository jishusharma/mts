# D1-D7 DECISION BRIEF - for fast operator ruling

Source: CORE_READINESS_PLAN.md (Opus 5.5, 2026-09-26), section "OPERATOR
DECISIONS PENDING". This file exists so ruling on all seven takes one
sitting instead of re-deriving context each time. Each entry: what's
being decided, the evidence, the options, the plan's own recommendation,
and what a YES actually changes in code. Nothing here has been decided
by Claude - D7 is the one exception, already implemented (see note).

---

## D1 - R:R suspension (finding F1)

**What**: compiled_engine.md sec 6 says the 2:1 net R:R hard stop applies
always, no exceptions. Live code (B058's floor/ceiling mode) suspends it
within 0.15% of a floor/ceiling zone. Of 260 SETUP_FORMING signals in the
9,175-snapshot sample, 158 exist ONLY because of this suspension.

**Options**:
(a) Revert - hard stop always applies, no floor/ceiling exception.
(b) Keep as a documented [SYSTEM] exception in compiled_engine sec 6,
    with the floor/ceiling evidence written in as justification.

**Plan recommends**: (a) revert.

**What YES to (a) changes in code**: C1 task - remove the suspend_rr path
in Compute-Verdict (start-trading-day.ps1, critical file, four-step
proof) and verdict.py. Keep the `mode` field for display only. Combined
with D4, this drops 158 of 260 SETUP_FORMING to WAIT_RR.

---

## D2 - Zone-math authority (finding F8)

**What**: Python's get_distance_cap (mts_math.py) disagrees with Java's
version and with compiled_engine sec 2.6 on three values: vwap bands
(0.3 vs 0.2), 1h swings (0.3 vs 0.5), prior_day_close (0.3 vs 0.4). Java
matches the doc; Python's stale values are enshrined in its own tests.
Currently off the live verdict path (no verdict effect measured), so
this is a correctness/consistency issue, not an active bug.

**Options**: pick one implementation as authoritative.

**Plan recommends**: Java is the single implementation; Python's zone
functions get aligned to sec 2.6 and marked legacy/advisory.

**What YES changes**: C4 task - mts_math.get_distance_cap aligned to
compiled_engine sec 2.6 (critical file), tests updated, docstring marked
legacy. Accept criterion: for every rank-1 candidate,
get_distance_cap(zone.type) == math.distance_cap (today 7,958 diffs
across all candidates) -> 0.

---

## D3 - Extra/FVG candidates (finding F6)

**What**: compiled_engine sec 2 defines FVG as an EXIT area, never an
entry. ExtraSetupBuilder's output (116 "extra" candidates observed) has
inverted geometry in some cases (e.g. a long with its target below
entry, one printed net_rr 36.88) and can land in setup_candidates[0] -
the slot any executor would read as "the" signal. 343 snapshots have
extra/FVG candidates reaching that slot.

**Options**: leave as-is, or separate extra candidates from the
authoritative slot.

**Plan recommends**: move ExtraSetupBuilder's output to a new field,
module_candidates; setup_candidates holds ranks 1-3 only, sourced from
the real (Tom-cited) candidate builder.

**What YES changes**: C2 task - MarketDataSnapshot.java (Java, both live
and historical paths) writes ExtraSetupBuilder output to
module_candidates instead of setup_candidates. Since this changes what
verdict_golden.py replays against archived snapshots (it can't see a
live-only routing change), accept criterion is core_invariants I12/I14
at baseline 0 measured --since the deploy timestamp, PASS after 1 hour
of live loop, plus a verdict.py guard: top candidate = first with
rank <= 3.

---

## D4 - Directional proof count (finding F3)

**What**: countSignals() currently counts book imbalance and finished
auction regardless of direction, and includes "speed" in the count.
Since the golden boundary, 161 of 613 rank-1 candidates carry a book
signal AGAINST their own direction, and speed appears in 113 of 156
proof>=5 cases - meaning proof counts are partly counting evidence that
doesn't actually support the trade.

**Options**: (a) count book imbalance/finished auction only when they
favour the trade; move speed out of the count entirely (keep it in the
proof JSON as a module reading, just not counted).

**Plan recommends**: (a), combined with D1(a). Together: of 260
SETUP_FORMING, 158 -> WAIT_RR, 79 -> WATCH, only 23 remain SETUP_FORMING.

**What YES changes**: C3 task (Sonnet builds, Opus reviews before
deploy) - countSignals() counts book imbalance only when long:>1.5 or
short:<0.67 in the trade's favor; finished auction only when the
exhausted side is opposite the trade direction; speed removed from the
count. Accept: A3 replay unchanged (steps 1-8), A4 replay shows
proof_count deltas matching the new recount rule exactly, live snapshots
after deploy satisfy new core_invariants check I16 ("proof_count equals
directional recount").

---

## D5 - Unhealthy trend / transition states (finding F5, ties to B063)

**What**: classifyState can never actually return trend_unhealthy or
transition - only balance/trend_healthy are reachable. This connects to
B063 (divergence has no dictionary definition, no condition-file rule,
no verdict consumer) - the engine has no Tom-cited definition of what
"unhealthy" or "transition" even means yet.

**Options**: cannot write code for this without a Tom-cited divergence
definition first. Until then: document the actual current behavior
(engine only emits balance/trend_healthy) honestly in compiled_engine
sec 1, rather than implying trend_unhealthy/transition are live.

**Plan recommends**: the documentation-only interim step now; real fix
waits on a Tom-cited divergence definition (separate research task,
not a code task).

**What YES changes**: C5 task (Opus, critical file, four-step proof,
operator approval, TEXT ONLY, no code) - compiled_engine.md sec 1 gets
language clarifying only balance/trend_healthy are currently reachable.

---

## D6 - Proof thresholds and SETUP_CONFIRMED (finding F9, filed as B076)

**What**: Compute-Verdict never emits SETUP_CONFIRMED - it's structurally
unreachable. compiled_engine.md sec 8 defines it, and alert-gating logic
lists it. The proof thresholds 3 and 5 that Compute-Verdict actually uses
appear nowhere in compiled_engine.md - they're undocumented [SYSTEM]
values, not Tom-cited.

**Options**: (a) document 3/5 as [SYSTEM] in sec 8 and either define a
real Tom-cited trigger for SETUP_CONFIRMED, or (b) remove
SETUP_CONFIRMED from the alert lists entirely since it can never fire.

**Plan recommends**: document 3/5 as [SYSTEM] now (critical file, four-
step proof); separately, either define a Tom-cited SETUP_CONFIRMED
trigger or drop it from alert lists. Hard rule either way: an executor
must never key on SETUP_CONFIRMED until this is resolved (relevant now
that T050's executor.py exists).

**What YES changes**: C5 task (Opus, same sec-8 text task as D5), plus
a decision on whether SETUP_CONFIRMED gets a real trigger or gets
removed from alert lists.

---

## D7 - B071 floor (finding F2) - ALREADY IMPLEMENTED, needs ratification

**What**: when the proof-direction check (L2) fails, what should the
verdict floor at?

**Plan recommends**: cap at WAIT_PROOF with reason "proof_dir error"
(spec'd in fail_closed_spec.py). Accept as written.

**STATUS: this is already live.** The B071 fix applied 2026-09-27 (see
BUGS.md, items/B071_fail_open_proof_direction.md) implements exactly
this - not a pre-emptive decision by Claude, but because D7's
recommendation was already the fix everyone (Opus's review, the harness
verification) had converged on. Flagging this explicitly rather than
treating it as quietly settled: the item doc's ORIGINAL required-fix
spec asked for halt+alert on error, not a silent WAIT_PROOF cap with a
log line. D7 as shipped is the softer behavior. If halt+alert is
actually wanted, that is a real follow-up change, not a formality.

---

## SUMMARY TABLE

| # | Decision | Plan's rec | Code impact | Status |
|---|---|---|---|---|
| D1 | Revert R:R suspension? | Yes, revert | C1 (critical file) | Pending |
| D2 | Java or Python zone math authoritative? | Java | C4 (critical file) | Pending |
| D3 | Separate extra/FVG candidates? | Yes | C2 (Java, both paths) | Pending |
| D4 | Directional-only proof count? | Yes | C3 (Sonnet+Opus review) | Pending |
| D5 | Document unhealthy/transition gap? | Yes, doc-only | C5 (Opus, text only) | Pending |
| D6 | Document 3/5 thresholds + SETUP_CONFIRMED fate? | Yes, doc + decide | C5 (Opus, text only) | Pending |
| D7 | Cap at WAIT_PROOF on L2 failure? | Yes | Already shipped | **Needs ratification, not a new decision** |

---

## OPERATOR RULINGS (2026-09-27, via Sonnet session)

- **D1: REVERT.** Matches plan recommendation. -> C1 (Sonnet: verdict.py +
  start-trading-day.ps1, critical file, four-step proof).
- **D2: NO CHANGE.** Deviates from plan's recommendation (Java
  authoritative) - operator chose to leave the Python/Java zone-math
  discrepancy as-is since it's off the live verdict path. No C4 task.
- **D3: SEPARATE.** Matches plan recommendation. -> C2 (Sonnet: Java,
  MarketDataSnapshot.java, both live and historical paths - needs Maven
  to compile/verify, blocked in this session same as A3/A4).
- **D4: DIRECTIONAL-ONLY.** Matches plan recommendation. -> C3 (Sonnet
  builds, Opus reviews before deploy - Java, same Maven blocker as C2).
- **D5: DOCUMENT NOW.** Matches plan recommendation. -> part of C5
  (Opus, compiled_engine.md sec 1, text only, four-step proof).
- **D6a: DOCUMENT thresholds as [SYSTEM].** Matches plan recommendation.
  -> part of C5 (Opus, compiled_engine.md sec 8, text only).
- **D6b: DEFINE A REAL TOM-CITED TRIGGER for SETUP_CONFIRMED.** Deviates
  from plan's simpler recommendation (remove from alert lists) - operator
  wants a real trigger found/confirmed instead of removal. This is a new
  research task, not a text edit - needs a T-numbered item filed
  separately (T052 candidate).
- **D7: SHIPPED BEHAVIOR IS FINE.** No halt+alert added. B071's
  WAIT_PROOF-cap-with-log-line fix stands as the final, ratified
  behavior - not provisional.

## IMPLEMENTATION STATUS

- C1: not yet built.
- C2, C3: not yet built - both are Java changes that need Maven to
  compile/verify, which is not available in this bridge session. Can be
  drafted as source edits here but must be compiled and harness-verified
  on the operator's Windows machine before being trusted.
- C4: cancelled per D2 ruling.
- C5: not Sonnet's to write per the plan's own role assignment (Opus,
  critical file, operator approval) - can be drafted as proposed text
  for Opus/operator review, not applied directly.
- D6b follow-up task: not yet filed.

## C1 BUILT (2026-09-27)

verdict.py: suspend_rr path removed, mode field kept for display only.
Verified against verdict_golden.py: SETUP_FORMING/aligned->WAIT_RR/aligned
158 (plan predicted 158, exact match), WATCH->WAIT_RR 807 (exact),
WAIT_PROOF->WAIT_RR 1195 (exact), WAIT_TRIGGER->WAIT_RR 891 (plan
predicted 893, off by 2 - corpus drift since the plan was measured, not
a logic error). New baseline NOT yet written (--write-baseline)
deliberately - that's a real state change belonging in the same review
batch as the .ps1 file, not done unilaterally.

scripts/core/start-trading-day.ps1 (critical file, four-step proof):
hash before fb3f6f70..., edited via explicit replace mirroring verdict.py
exactly, hash after 8c07ef1b.... Cannot execute-verify - no PowerShell in
this session. Diff shown to operator inline in chat.

Both changes are UNCOMMITTED, same as everything else this session.
