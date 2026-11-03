# Research Report: Spec Tests for live_aid Analyst and Verdict Board Functions

**Task**: `gpt-spec-tests-live-aid-analyst-verdict-1103`  
**Date**: 2026-11-03  
**Scope**: `MyTradingSys/tools/live_aid/test_spec_analyst_verdict.py` (new)  
**Reference**: `MyTradingSys/tools/live_aid/REQUIREMENTS.md` R13 and R14, `MyTradingSys/tools/live_aid/live_aid_indicators.js:374-434`

---

## 1. Summary of Functions Tested

The pure functions under `live_aid_indicators.js` implementing the analyst and verdict board were tested:
- `rosterRead(roster, rows, rejected, now)`:
  - Compiles roster view with newest published rows and rejected counts per analyst.
  - Derives age in whole days (`ageDays`).
  - Classifies analyst states: `FRESH` (age <= 3 days), `STALE` (age > 3 days), `NOT_FETCHED` (ingested false), `NO_ROW` (ingested true or omitted), and `OFF` (enabled false).
- `analystVote(read)`:
  - Nets sentiment across `FRESH` analysts (`BULLISH` +1, `BEARISH` -1, `NEUTRAL` 0).
  - Skips `STALE` or unlisted biases like `NO_VIEW`.
  - Returns `1`, `-1`, `0` (exact tie or neutral-only), or `null` when no fresh views exist.
- `levelWatch(levels, px)`:
  - Filters out expired and non-finite levels.
  - Computes percentage distance `dist = (level / px - 1) * 100` and `side` (`above` for dist >= 0, `below` for dist < 0).
  - Classifies proximity zones: `AT` (<= 0.3%), `NEAR` (<= 1.5%), `WATCH` (<= 6.0%), dropping levels outside the 6% band.
  - Sorts levels ascending by `Math.abs(dist)` (nearest first).
- `zones(watch, px)`:
  - Merges adjacent levels within `AV.merge` (0.25%) into continuous `[lo..hi]` clusters.
  - Evaluates position relative to zone: inside (`dist = 0, side = 'at', zone = 'AT'`), or exterior distance to the near edge.
- `lean(votes)`:
  - Filters valid votes (+1, -1, 0). Requires minimum 3 votes (`NOT ENOUGH DATA` if n < 3).
  - Computes `BULLISH LEAN` when `bull >= 2` and `bull >= 2 * bear`.
  - Computes `BEARISH LEAN` when `bear >= 2` and `bear >= 2 * bull`.
  - Defaults to `MIXED` when neither threshold is satisfied.
- `actions(ln, zs, pulse)`:
  - Generates actionable watch list from zones and news pulse.
  - Prepends `NOW` news action if pulse level is `EVENT`.
  - Maps zones to action urgency (`AT` -> `NOW`, `NEAR` -> `NEXT`, `WATCH` -> `LATER`).
  - Evaluates alignment with directional lean (`withLean = true` if lean direction matches zone side).
  - Strictly orders all `NOW` actions before `NEXT`, and `NEXT` before `LATER`.

---

## 2. Test Execution & Coverage

- Test file: `MyTradingSys/tools/live_aid/test_spec_analyst_verdict.py`
- Command: `python -m pytest MyTradingSys/tools/live_aid/test_spec_analyst_verdict.py -q`
- Result: **12 passed in 2.60s** (requirement was >=8 passing tests).
- All tests execute directly against Node.js runtime using JSON payload IPC, supporting `LIVE_AID_JS_PATH`.

Coverage of required edge cases:
- Analyst with no levels / empty rows: verified in `test_roster_read_empty_and_no_levels`
- Price exactly at level (distance 0, side 'above', zone 'AT'): verified in `test_level_watch_price_exactly_at_level`
- Tie votes in analystVote (sum 0 returning 0): verified in `test_analyst_vote_sentiment_and_tie`
- No data / empty inputs / malformed objects: verified in `test_analyst_verdict_edge_and_malformed`
- Ordering of NOW before NEXT in actions: verified in `test_actions_ordering_now_before_next_before_later`
- Lean determination based on net sentiment and vote thresholds: verified in `test_lean_thresholds_and_sample_size`
- Zones computation, merge thresholds, and distance calculations: verified in `test_zones_clustering_and_merge` and `test_zones_inside_and_distance_calculations`

---

## 3. Mutation Testing (Fail-First Verification)

Three distinct scratch mutations were applied to a temporary copy of `live_aid_indicators.js` and verified with `LIVE_AID_JS_PATH`:

1. **Mutation 1 (`freshDays: 3 -> freshDays: 1`)**:
   - Location: `var AV = { freshDays: 3, ... }` -> `freshDays: 1`
   - Outcome: **FAILED** `test_roster_read_states_and_freshness` (exit code 1; 1 failed, 11 passed).
2. **Mutation 2 (`lean bull threshold: 2 -> 3`)**:
   - Location: `bull >= 2 && bull >= 2 * bear` -> `bull >= 3 && bull >= 2 * bear`
   - Outcome: **FAILED** `test_lean_thresholds_and_sample_size` (exit code 1; 1 failed, 11 passed).
3. **Mutation 3 (`actions sort: inverted rank order`)**:
   - Location: `rank[a.when] - rank[b.when]` -> `rank[b.when] - rank[a.when]`
   - Outcome: **FAILED** `test_actions_ordering_now_before_next_before_later` (exit code 1; 1 failed, 11 passed).

All 3/3 scratch mutations failed the test suite as required.

---

## 4. Verification Checkpoints

- Target `.js` files remain completely untouched (`git status` confirms zero modifications to `.js` files).
- No modifications made to `scripts/dev/extra_tests.tsv` or task card json files (left for parent agent).
- Test suite passes cleanly with 12/12 tests green.
