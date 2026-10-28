# C3 (D4 directional proof count) — Opus review, 2026-09-27
Reviewed: src/main/java/datafeed/SetupCandidatesBuilder.java.new (diff in C2_C3_BUILD_REPORT.md), evidence from
the Sonnet build (A3 before/after byte-identical 2149/2149 candidates, 30086/30086 fields; A4 sample 417 snapshots,
1828 candidates, 1828/1828 deltas equal the directional recount, all deltas <= 0; 14 JUnit tests pass).

VERDICT: APPROVE for deploy via the four-step proof, together with C2 (MarketDataSnapshot.java.new) and the
verdict.py.new guard. Live acceptance still owed on the desktop: core_invariants I12/I14 at baseline 0 after 1 h of
live loop, and new check I16 "proof_count == directional recount" on live snapshots.

Checks done
- Direction strings: Candidate.direction is only ever "short"/"long" (determineDirections; used as such at
  lines 111-153). The `"long".equals(direction) ? ... : ...` form treats anything else as short; safe given that
  domain, noted.
- finishedAuctionDirection is "sell" when the extreme delta < 0 else "buy" (line ~718) -> long counts "sell"
  exhaustion, short counts "buy" exhaustion. Matches the D4 ruling.
- Book imbalance: long > 1.5, short < 0.67; 0.0 (missing / historical) never counts -> fail-closed. Matches.
- Speed: removed from the count only; still serialised in proof JSON (toJson untouched). Matches.
- Step 9 only: steps 1-8 replay unchanged -> no side effect on zones/math/ranking inputs.

Findings (non-blocking, file as items)
- C3-R1 MED (pre-existing, now matters): the finished-auction scan walks the last 20 bars oldest-first and `break`s
  on the FIRST qualifying event. With direction now mattering, an older unfavourable event masks a newer favourable
  one (and vice versa). Proposal: scan newest-first, or count if ANY qualifying event in the window favours the
  trade. Needs its own A4-style delta check; do not bundle into this deploy.
- C3-R2 LOW: the other five proof signals (rejection wick, absorption, delta flip, volume spike, cvd_aligned) were
  not in D4's scope. detectProofs() receives the candidate (direction available at line ~617), but whether each of
  them is direction-aware was not re-audited here. Add to the proof_direction_cases harness as a follow-up.
- C3-R3 INFO: with fewer countable signals, SETUP_FORMING (proof >= 5) becomes rarer; combined D1+D3+D4 effect on
  the full corpus must be re-measured with verdict_golden after deploy and written as the new baseline in the same
  review batch (not before).
