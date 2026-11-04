# US-open specification tests — 2026-11-03

## Scope and source

Card `gpt-spec-tests-live-aid-us-open-1103`. Inputs read first: `MyTradingSys/research/us_open_levels_2026-10-30/study.py` and `RESULT.md`, function comments and implementation in `MyTradingSys/tools/live_aid/live_aid_indicators.js`, and `us_open_rates.js`. The study defines half-open fractional distance ranges `[0,.0025)`, `[.0025,.005)`, `[.005,.01)`, `[.01,.02)`, `[.02,9)`. In the generated table `n` is the number of eligible observations, `touch` is a rounded percentage of `n`, `nt` is the count of touched observations, and `held` is a rounded percentage of `nt`.

Hand expectations before implementation bodies: price 100 with level 100.2499 => first bucket; 100.25 => second; 100.5 => third; 101 => fourth; 102 and 300 => fifth. A below-mark level uses absolute fractional distance and appears on `down`; equal level is omitted. Invalid level is omitted. Empty rows and daily inputs yield no box/or/ladder. With mark 0, a valid level has no meaningful finite distance and should be omitted. For the generated table each row must have `nt <= n`, percentages in 0..100, and missing percentages exactly when their denominator is zero. The live aid suppresses `touch` while `n < 30` and `held` while `nt < 30`.

## Test results

Command: `python -m pytest MyTradingSys/tools/live_aid/test_spec_us_open.py -q`

Result after follow-up review: **21 passed, 1 xfailed** (strict expected failure documents the out-of-scope zero-mark defect). The one strict expected failure is a real scope-blocking defect; the test asserts the spec expectation and has not been weakened to match the implementation:

```text
_______________ test_zero_mark_level_is_omitted _______________
    r = _us_open(101, 0)
>   assert r["up"] == [] and r["down"] == []
E   AssertionError: ... Left contains one more item: {'k': 'pdh', 'name': 'prev day high = prev day low', 'p': 101, 'dist': None, ...}
1 xfailed, 21 passed
```

`usOpen` currently admits `px === 0`, computes an infinite distance, and returns a row whose JSON `dist` is `null` and whose bucket is null. This report records it as BLOCKED for production remediation: both production JS files are outside this card's permitted scope and remain byte-identical. The 21 passing tests include all bucket boundaries, negative-side distances, a separately passing malformed-level case, the empty case, rate-table count/percentage invariants and pinned per-kind sample totals, plus both sides of the live aid’s 30-observation display threshold. The strict xfail isolates only the known zero-mark defect.

## Independent review follow-up

Claude returned PASS-WITH-NOTES and identified two useful omissions: the `n >= 30` / `nt >= 30` display gates were not exercised, and a changed table sample count could survive the original loose invariants. Added checks for both display thresholds, the relation between `nt`, `n`, and rounded `touch`, and the fixed per-kind sample totals from this committed study result. A single-cell `n` mutation is now included in mutation evidence.

## Scratch mutation checks

Six distinct byte-level mutations were applied only to scratch copies under ignored `.labflow-mutation-scratch/`; each was killed by a focused assertion:

| Scratch mutation | Check | Mutated result | Killed |
| first bucket high `.0025` -> `.0026` | edge belongs to second bucket | first bucket | yes |
| second bucket high `.005` -> `.0051` | edge belongs to third bucket | second bucket | yes |
| fifth bucket low `.02` -> `.0201` | 2% belongs to `2+` | null bucket | yes |
| touch threshold `n >= 30` -> `n > 30` | `n=30` displays touch | touch hidden | yes |
| held threshold `nt >= 30` -> `nt > 30` | `nt=30` displays held | held hidden | yes |
| first `dayH/0-0.25` sample count `105` -> `106` | percentage/count consistency and sample total | inconsistent row | yes |

Original source SHA-256: `b8588cc9676b398af6071804b5cb3778945ea98fd289a992b9cccd7f54f2051a` (scratch variants only; original not modified).

## Files

The test module remains registered in `scripts/dev/extra_tests.tsv`; this review follow-up extends its checks and report. No production JS, live path, VALIDATION, or HOLDOUT files were changed/read. The zero-mark defect remains outside this test-only scope; its failing output is preserved here for a separately scoped production fix.
