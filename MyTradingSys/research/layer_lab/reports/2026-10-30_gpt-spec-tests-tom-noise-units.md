# GPT spec tests: Tom noise units

BUILD RESULT: 12 tests pass; 3/3 scratch mutations fail a test. Source `scripts/dev/tom_noise_units.py` was not edited.

## Checked and derived

- Read `scripts/dev/tom_noise_units.py`: `true_ranges` uses the maximum of high-low and both gaps to prior close (lines 26-33); `aggregate` keeps buckets with exactly `tf` rows, combines extrema, and takes the latest close (36-50); `tr_fracs` rejects nonadjacent buckets and failed predicates (53-64).
- `n5` has direct `(high, low, close)` and timestamped input paths, rejects `asof` for direct bars and timezone-naive datetimes, handles date/datetime/numeric cutoffs, filters completed bars at the upper cutoff, and returns zero when no ranges exist (lines 79-145). `min_stop_width` chooses the larger of noise and fee width (68-76).
- Hand calculations in `scripts/dev/test_tom_noise_units.py`: direct TR fractions `0.1` and `0.2` have median `0.15`; the same three complete 5-minute buckets give `0.15`; at entry `100`, `n5=0.01` gives noise width `0.88`, while fee `0.001` gives width `0.4`, so the result is `0.88`. With `n5=0.001` and round-trip fees `0.005`, fee width is `0.005 / 0.25 * 100 = 2.0`, exceeding noise width `0.088`.
- The CLI emits rows only when the data produces medians: empty directories raise `StatisticsError` at `main()` line 192 (`median(v)`). The test records that current error path; it does not invent a zero-row CLI result.

## Test evidence

Command: `python -m pytest scripts/dev/test_tom_noise_units.py -q -p no:cacheprovider --basetemp .pytest-tmp-tom-noise` → **12 passed**. The first default-temp attempt hit a permission error scanning the existing user pytest temp directory (9 passed, 3 setup errors); this invocation used an isolated worktree-local temp directory.

Scratch mutation evidence (each mutant was written under a temporary directory and tested by setting `TOM_NOISE_UNITS_SOURCE`; audited source remained untouched):

| Mutation | Result |
|---|---|
| Replace true-range max with high-low only | Test suite failed as expected |
| Admit incomplete aggregate buckets | Test suite failed as expected |
| Change completed-bar cutoff from `<=` to `<` | Test suite failed as expected |

## Branch and boundary coverage

- Aggregation: complete vs incomplete bucket, extrema/last close; true-range gap terms and no-prior-bar empty result.
- `n5`: timestamped and direct modes, empty result, full 5-minute buckets, incomplete bucket, median, inclusive completion cutoff, naive datetime and unsupported direct-list cutoff errors.
- Other functions: noise/fee max, file month/window/header/nonnumeric/dropped-day filters, malformed split JSON, and dev/holdout overlap assertion.

## Scope and gate note

`scripts/dev/test_tom_noise_units.py` and `scripts/dev/extra_tests.tsv` are in the card scope. The new test is registered in `extra_tests.tsv`; `python MyTradingSys/tests/test_gate_discovery_b150.py` passed (2 tests). No live or market data was read.

## Follow-up cards

- None created.
