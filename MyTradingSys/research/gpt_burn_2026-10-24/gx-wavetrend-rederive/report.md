# WaveTrend independent re-derivation audit

Command (repo root): `python -B MyTradingSys/research/gpt_burn_2026-10-24/gx-wavetrend-rederive/audit.py`.

Scope: FORMULAS.md:513-523; independent standard-library `wt.py` written before reading the implementation, tests or golden generator. No repository imports in wt.py. audit.py executes the implementation and test source in memory only for comparison and mutations. No existing files modified; no git, sync or push commands run.

Parameters: SOURCED HLC3, EMA(10), EMA(21), 0.015 and SMA(4) (FORMULAS.md:513); OURS first-valid seed, relative flat tolerance 1e-9, warmup 200, cross and zone conventions (:515), comparison tolerance 1e-9 (:523).

All CSV rows parsed and counted: 400 fixture + 400 golden, timestamps identical, unique and contiguous hourly, indices 0–399. Start 2022-01-01 00:00 UTC; end 2022-01-17 15:00 UTC. Indices are zero-based. CSV line = index + 2. No conclusions use truncated output.

Independent recurrence uses state += alpha*(value-state); implementation uses alpha*value+(1-alpha)*state. At bar 0: ap=46530.09666666667, esa=ap, d=0, ci/wt1/wt2=NaN. At bar 1: ap=46760.56, esa=46571.99909090909, d=34.28380165289193, ci=wt1=366.6666666666667. wt2 first exists at bar 4. Thus first-valid seeding, HLC3 and the specified smoothing agree.

## Independent vs golden, raw entire series

| Column | Finite pairs | Max abs diff | Exact differing count / first bar | >1e-9 count / first bar | NaN mismatch count / first bar |
|---|---:|---:|---|---|---|
| wt1 | 399 | 1.0664358285339404e-11 | 398 / 1 | 0 / None | 0 / None |
| wt2 | 396 | 1.0503153902163831e-11 | 396 / 4 | 0 / None | 0 / None |
| event | 400 | 0 | 0 / None | 0 / None | 0 / None |

## Independent vs wavetrend.py warmup=0, entire series

| Column | Finite pairs | Max abs diff | Exact differing count / first bar | >1e-9 count / first bar | NaN mismatch count / first bar |
|---|---:|---:|---|---|---|
| wt1 | 399 | 1.0482281709300878e-11 | 392 / 8 | 0 / None | 0 / None |
| wt2 | 396 | 1.0158984764530032e-11 | 392 / 8 | 0 / None | 0 / None |
| event | 400 | 0 | 0 / None | 0 / None | 0 / None |

## Independent vs golden, usable bars 200–399

| Column | Finite pairs | Max abs diff | Exact differing count / first bar | >1e-9 count / first bar | NaN mismatch count / first bar |
|---|---:|---:|---|---|---|
| wt1 | 200 | 6.8576255785046669e-12 | 200 / 200 | 0 / None | 0 / None |
| wt2 | 200 | 7.0432548682219931e-12 | 200 / 200 | 0 / None | 0 / None |
| event | 200 | 0 | 0 / None | 0 / None | 0 / None |

## Independent vs wavetrend.py default, usable bars 200–399

| Column | Finite pairs | Max abs diff | Exact differing count / first bar | >1e-9 count / first bar | NaN mismatch count / first bar |
|---|---:|---:|---|---|---|
| wt1 | 200 | 6.9713124162262829e-12 | 200 / 200 | 0 / None | 0 / None |
| wt2 | 200 | 6.673772645626741e-12 | 200 / 200 | 0 / None | 0 / None |
| event | 200 | 1 | 1 / 200 | 1 / 200 | 0 / None |

open_time max abs diff = 0 (0 mismatches); available_at max abs diff = 0 (0 mismatches); zone mismatches = 0. Golden has no zone/available_at columns. Raw NaNs: wt1=1, wt2=4; default output masks bars 0–199 (200 NaNs per numeric output), first usable bar=200.

Cause of exact numeric differences: floating-point evaluation order and golden CSV rounding to 12 decimal places (make_golden.py:24), not seed, smoothing or ap source. Default-vs-raw differences before index 200 are the required warmup mask (wavetrend.py:104-107), not formula errors. Golden stores unmasked crosses; comparisons use matching scope. This is spreadsheet-style parity, not TradingView/Pine-runtime parity.

## Mutation checks

| In-memory change | Tests run | Failing tests | Errors |
|---|---:|---|---|
| baseline | 13 | none | none |
| ap source HLC3 -> close (line 92) | 13 | audit_tests.TestGolden.test_events_match_golden_after_warmup, audit_tests.TestGolden.test_values_match_golden_after_warmup | none |
| EMA21 alpha -> EMA22 (line 76) | 13 | audit_tests.TestGolden.test_events_match_golden_after_warmup, audit_tests.TestGolden.test_values_match_golden_after_warmup | none |
| wt1 first seed -> zero (line 101) | 13 | audit_tests.TestGolden.test_values_match_golden_after_warmup, audit_tests.TestHandFixtures.test_two_bar_hand_value | none |
| SMA4 -> SMA3 (line 105) | 13 | audit_tests.TestGolden.test_events_match_golden_after_warmup, audit_tests.TestGolden.test_values_match_golden_after_warmup | none |
| post-gap/NaN permanently suppress output (lines 85-90,104) | 13 | none | none |

All mutations use exact string replacements in memory; the original files remain unchanged. The HLC3, smoothing, seed and SMA errors are killed by the existing suite. Golden value assertions at test_wavetrend.py:37-38 catch source/smoothing/SMA errors; the hand fixture at :67 also catches the zero-seed error.

## Finding

**LOW — reset tests do not verify recovery.** `MyTradingSys/backtest/layers/wavetrend/test_wavetrend.py:81-93` tests NaN/gap reset only through bar 259 (29 bars after reset), far short of the 200-bar re-warmup. Adding a reset_seen flag set only in the gap/NaN reset branches at wavetrend.py:85-90 and requiring not reset_seen in the output mask at :104 passes every existing test, but permanently suppresses later usable values. This is a test coverage weakness, not a demonstrated defect in the current implementation.

Reproduction: run the command above. For 800 bars made by repeating the fixture with a timestamp offset and a NaN at index 230, the unmodified implementation first recovers at index 431; the mutant has wt1=NaN at that index and 0 usable rows after reset. A test should extend beyond recovery and check recovery timing and independently derived restarted values for both NaN and gap resets.

Boundary event: the unmasked independent/golden cross at index 200 is -1; default wavetrend.py emits 0 there because its prior output is NaN and cross state resets (wavetrend.py:51-54,106-108). This is a warmup/cross-state convention, not a seed, smoothing or ap error. Existing golden event tests intentionally compare from index 201 (test_wavetrend.py:43-44). All 199 event rows at indices 201-399 match exactly. Raw events match on all 400 rows.

No CRITICAL/HIGH findings; no numeric or metadata disagreement above tolerance on the requested 400-bar fixture. The independent wt.py audit scope is this finite contiguous fixture; its gap/invalid-input behavior is not claimed as a full replacement module.

Result: Numeric parity within 1e-9; raw events match, default event differs only at warmup boundary 200; four formula mutations caught; LOW reset-recovery test gap reproduced.
