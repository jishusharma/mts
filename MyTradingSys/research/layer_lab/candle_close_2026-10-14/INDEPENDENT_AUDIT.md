# Candle-close run: independent audit of implementation and conclusions

FIX-FIRST. 2026-10-14. This is a second-pass audit of the previous run, not an independent human/model replication. No new performance trial, validation or holdout read. Original results remain unchanged.

## Findings

| ID | Severity | Evidence | Issue and consequence | Required correction |
|---|---|---|---|---|
| A1 | HIGH | study.py:120-124 | The phase classifier is a 30-day momentum/efficiency proxy, plus a single 4h return. Low efficiency is called `ranging` without checking stable boundaries. One 4h return does not establish a 4h trend. | Name the existing labels accurately. Design causal local structure, bounded-range and volatility features before any phase-specific application claim. |
| A2 | HIGH | study.py:194-199, by_phase.csv, by_trend.csv | Phase, trend, 4h direction and side are grouped separately. No joint phase/setup eligibility rule is tested; no phase-cell confidence bounds or multiplicity-adjusted promotion gate are calculated. | Test predeclared joint contexts with episode counts and uncertainty; preserve UNKNOWN/transition states. Never infer phase-specific failure or success from pooled results. |
| A3 | HIGH | study.py:147-157 | Each signature retains its first daily family/side event, while controls average all eligible nearby closes. Different opportunity weighting and elapsed confirmation paths weaken the comparison. Nearby locations also differ within a 0.25% band. | Define common first-encounter episodes and decision times for signals/controls; match phase, direction, volatility and level distance without future outcomes. NEXT_EXPERIMENT.md freezes this direction before further price runs. |
| A4 | HIGH | study.py:133,188-190; METHOD.md | Only a fixed 60-minute open-to-open outcome and 14/20bp cost screens were assessed. These do not answer bottom formation, path survival, trade management or historical funding/fill P&L. | Preserve the narrow negative pooled screen. Separate local reaction, swing persistence and macro questions; assemble actual execution/cost inputs before trading conclusions. |
| A5 | MED | verify_result.py:30-74; verification.json | The raw-row verifier checks 126 sampled events and all arm win/gross means. It does not independently rebuild regime labels, matched control means, bootstrap CIs or sampling completeness. | Extend verification to those calculations and an end-to-end future-perturbation check before relying on conditional probabilities. Eight synthetic tests and raw checks are useful but not a complete research audit. |
| A6 | MED | test_study.py:5-12; .github/workflows/ci.yml:54; AUDIT_REPRODUCTIONS.json | CI installs no pandas, so these research tests are skipped there. Worse, the same `except ImportError` covers importing `study`: a genuine application import failure can be silently misreported as missing pandas. A forced broken study import returned exit 0, eight skipped tests. | Catch only the optional pandas import; application import errors must fail. Ensure a supported research runner executes these tests with dependencies rather than interpreting a general green gate as execution coverage. |
| A7 | MED | by_phase.csv complete 378 rows; AUDIT_REPRODUCTIONS.json | Seven phase cells have positive mean after the 14bp screen, but six have fewer than 100 events. The remaining cell has negative probability lift. These were not given subgroup inference or OOS validation. | Retain as exploratory observations only. The pooled `0/126` conclusion must not be expanded to `no phase can work`; neither may subgroup winners be promoted from this same data. |
| A8 | MED | CYCLE_DESIGN.md; REPORT.md | The study does not label/test cycle bottoms, confirmed local pivots or the anonymous YouTube trader's complete sequence. At most five non-overlapping 180-day blocks fit this DEV window; that is not five proven independent cycles. | Keep macro odds UNDERPOWERED/NOT_TESTED. Source replication requires identifiable material; a larger minute count does not solve episode scarcity. |

All findings are MATCH to files read, except the anonymous trader identity, which is NOT_IN_DATA. Arbitrary thresholds were explicitly marked OURS and frozen; their lack of validation is a limitation, not evidence of parameter tuning. No forward-price leakage was demonstrated in the inspected regime/level availability joins.

## Concrete reproductions

1. A rising, oscillating sequence `close[i]=100+2*i+(10 if i is odd else 0)`, i=0..30, rises from 100 to 160. Its total absolute daily movement is 300, efficiency=60/300=0.20. The implementation calls this `ranging`; the calculation establishes choppiness, not a horizontal range. This is a synthetic counterexample, not a new BTC result.
2. A subprocess import hook deliberately raises `ImportError` only for `study`, while numpy/pandas are installed. Running test_study.py exits 0 with `OK (skipped=8)`. Thus an application import failure can disappear behind the optional-dependency skip.
3. Parsing complete existing output files yields 378 phase rows, 252 trend rows and 269 4h-direction rows. None includes joint phase+trend fields or confidence interval columns. Positive 14bp phase cells=7; with N>=100=1. No new outcome computation was performed.

Results are recorded in AUDIT_REPRODUCTIONS.json. The import failure can be reproduced without touching application files:

```python
import builtins, runpy
original = builtins.__import__
def hook(name, *args, **kwargs):
    if name == 'study':
        raise ImportError('audit: simulated broken study import')
    return original(name, *args, **kwargs)
builtins.__import__ = hook
runpy.run_path('test_study.py', run_name='__main__')
```

Run this from the study folder, in a separate Python process. EXPECT on the current implementation: eight tests skipped and exit 0. Correct fail-closed behavior would be a nonzero exit.

## Historical execution/delivery issues, already corrected

- Pandas timestamp resolution was assumed to be nanoseconds, producing a false missing-minute alarm. Actual archive gaps=0; Timedelta-based comparison replaced it. DATA_AMENDMENT.md records the error.
- A read-only pandas Boolean array stopped a run. An explicit copy fixed it; regression was reproduced before correction. Both failures preceded result tables.
- Initial quick gates failed because the new harness was absent from wiring/test discovery. Registration fixed those failures.
- Adding pandas to CI exposed a CI/cloud dependency-list mismatch, then GitHub refused a workflow change because the token lacked workflow scope. A later Claude changeset removed the workflow edits and introduced dependency skipping. The change is shipped, but A6 is the remaining coverage/fail-closed problem. c8a86f1 fixed the intermediate module-level skip/collection failure by skipping the class.

## What survives this audit

The saved raw-event returns and counts retain their mechanical checks. `0/126 pooled arms pass this particular DEV screen` is supported. `No phase-specific edge exists`, `we have tested cycle-bottom signatures`, or `these probabilities are ready to trade` are unsupported.

Priority: A1-A3 phase/encounter design, A5-A6 verification and gate reliability, then a preregistered local/swing study. Do not rerun all 126 arms hoping for a different winner. Report/page publication is a delivery task, not a substitute for those corrections.

## A6 follow-up (2026-10-17, candle-close-test-import-guard)

- Fixed in `test_study.py`: only `import pandas` sits inside the `except ImportError`; `import study` runs outside it, so a broken application import now fails the run (nonzero exit). Reproduction above on the old code: exit 0, `OK (skipped=8)`.
- New `ImportGuardTests` run `test_study.py` in a subprocess with one import forced to fail: broken `study` must exit nonzero (fails on the old implementation); missing `pandas` still gives explicit skips (exit 0, every test `s`).
- Execution coverage: with pandas present all eight numerical tests run and pass (plus the two guard tests). `.github/workflows/ci.yml:60` now installs `pandas`, so `run_all_tests.py` (which runs this file via `run_extra_tests.py`) executes them in CI; without pandas the study class skips explicitly. Workflows and strategy outputs untouched.
