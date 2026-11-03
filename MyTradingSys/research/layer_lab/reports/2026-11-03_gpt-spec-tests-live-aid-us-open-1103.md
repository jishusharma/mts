# US-open specification tests — 2026-11-03

## Scope and source

Card `gpt-spec-tests-live-aid-us-open-1103`. Inputs read first: `MyTradingSys/research/us_open_levels_2026-10-30/study.py` and `RESULT.md`, function comments and implementation in `MyTradingSys/tools/live_aid/live_aid_indicators.js`, and `us_open_rates.js`. The study defines half-open fractional distance ranges `[0,.0025)`, `[.0025,.005)`, `[.005,.01)`, `[.01,.02)`, `[.02,9)`; touch counts cannot exceed observations, and held counts cannot exceed touches.

Hand expectations before implementation bodies: price 100 with level 100.2499 => first bucket; 100.25 => second; 100.5 => third; 101 => fourth; 102 and 300 => fifth. A below-mark level uses absolute fractional distance and appears on `down`; equal level is omitted. Invalid level is omitted. Empty rows and daily inputs yield no box/or/ladder. With mark 0, a valid level has no meaningful finite distance and should be omitted. For the generated table each row must have `nt <= n`, percentages in 0..100, and missing percentages exactly when their denominator is zero.

## Test results

Command: `python -m pytest MyTradingSys/tools/live_aid/test_spec_us_open.py -q`

Result: **19 passed, 1 xfailed** (strict expected failure documents the out-of-scope zero-mark defect). The the one strict expected failure is a real scope-blocking defect; the test asserts the spec expectation and has not been weakened to match the implementation:

```text
_______________ test_malformed_and_zero_mark_levels_are_omitted _______________
    r = _us_open(101, 0)
>   assert r["up"] == [] and r["down"] == []
E   AssertionError: ... Left contains one more item: {'k': 'pdh', 'name': 'prev day high = prev day low', 'p': 101, 'dist': None, ...}
1 xfailed, 19 passed
```

`usOpen` currently admits `px === 0`, computes an infinite distance, and returns a row whose JSON `dist` is `null` and whose bucket is null. This report records it as BLOCKED for production remediation: both production JS files are outside this card's permitted scope and remain byte-identical. The 19 passing assertions include all bucket boundaries, negative-side distances, malformed level, empty case, and every rate-table cell invariant.

## Scratch mutation checks

Three distinct byte-level mutations were applied only to copies of `live_aid_indicators.js` under ignored `.labflow-mutation-scratch/us-open-spec/`; each was killed by the boundary expectation:

| Scratch mutation | Expected at exact edge | Mutated result | Killed |
|---|---|---|---|
| first bucket high `.0025` -> `.0026` | `0.25-0.5` at 0.25% | `0-0.25` | yes |
| second bucket high `.005` -> `.0051` | `0.5-1` at 0.5% | `0.25-0.5` | yes |
| fifth bucket low `.02` -> `.0201` | `2+` at 2% | `null` | yes |

Original source SHA-256: `b8588cc9676b398af6071804b5cb3778945ea98fd289a992b9cccd7f54f2051a` (scratch variants only; original not modified).

## Files

Added `MyTradingSys/tools/live_aid/test_spec_us_open.py` and registered it in `scripts/dev/extra_tests.tsv`. No production JS, live path, VALIDATION, or HOLDOUT files were changed/read. This task is incomplete until the zero-mark defect is resolved in a separately scoped production card; current evidence and the failing output are preserved here.
