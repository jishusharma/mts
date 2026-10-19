# Context-factor V3 independent GPT review

**FIX-FIRST.** The 437/319-day calculations and frozen hashes match. The matched-control edge cases are not fully specified, and a proxy stop-gap diagnosis is incorrectly presented as F3's final disposition.

Reviewed committed trunk documents only: `MyTradingSys/research/context_factors_pit_2026-10-16/{PRE_REG_V3.md,AUDIT_BEFORE_RUN.md,PRE_REG_V2.md}`. `context_asof.py` was hashed as bytes, never imported or executed. Producer: Gemini; reviewer: GPT in this session. No backtest, count rerun, protected data or outcome read. This review does not authorize the one-run card.

## Checks and findings

Paths below are relative to `MyTradingSys/research/context_factors_pit_2026-10-16/` unless stated otherwise.

| Check | Status | Severity | Evidence and conclusion |
|---|---|---|---|
| Count-only diagnostics | MATCH | — | V3:61-67 requires per-cell and matched-pool median/p90 stop percentage and rung shares, before outcomes. Matches audit:35-38. |
| Actual matched-pool caveat | MISMATCH | HIGH | Audit:38 explicitly says its pool is an at-level complement proxy; the true context_null pool must be measured after matching. V3:65 correctly requests that measurement, but V3:53 declares F3 definitively INCONCLUSIVE using the proxy +43/+45% gaps. If the actual matched gap is <=25%, that preassigned disposition need not follow. Keep proxy numbers diagnostic and decide from the prescribed matched-pool calculation. |
| Exact 25% boundary | MATCH | — | V3:68-70 uses >0.25 for INCONCLUSIVE/no-kill; PASS:84 and FAIL:95 use <=25%. Exactly 25% stays eligible subject to other gates. |
| Missing controls / undefined gap | NOT_IN_DATA | HIGH | V3:65,69,77 names a matched pool and kmin=10 but supplies no disposition if a cell has no matched events/pool, or its relative-gap denominator is invalid. A median of an empty pool, E with no matched observations, and 0/0 coverage cannot be evaluated. Explicit pre-outcome handling is required; this review does not choose it. |
| Stratified E / 80% coverage | MATCH, with missing disposition | MEDIUM | V3:72-74 sets ineligible strata (<10 controls) to E=null and requires positive E strata covering >=80% of matched events for PASS. Coverage below 80% therefore cannot PASS. It does not explicitly say how absent eligible strata or incomplete stratified coverage interacts with the separately stated FAIL iff at V3:91-95. Clarify before an executor makes that choice, particularly zero matched-event denominators. |
| Holm quantile | MATCH | — | V3:28: NormalDist.inv_cdf(1-0.05/(2*59)) = 3.3368103217106353, rounded 3.337. The 59 is the declared minimum family size, not a fresh count by this review. |
| Primary planning threshold | MATCH | — | V3:33: ((3.337+0.8416)*1.5/0.30)^2 = 436.51744900000017, ceil=437. |
| Own-SD planning threshold | MATCH | — | V3:35: ((3.337+0.8416)*1.281/0.30)^2 = 318.35915983488405, ceil=319. Using exact z, z_beta and 1.25*sqrt(1.05) also gives ceil=319. |
| Design-powered cells | MATCH | — | V3:39-56: primary 437-day threshold powers F1/F2/F3 both directions, six cells. F4/F5/F6/F7 both directions are unpowered, eight cells. At 319 days, F7 long alone joins those six; F7 short=299 remains unpowered. Counts copied from cited audit/V2, not independently regenerated. |
| Negative / zero effect FAIL | MATCH | — | V3:91-95 requires E<=0, 2.8*SE_day<=0.30 R and gap<=25%. The global unpowered override at V3:104 must also apply; the FAIL list is not independently sufficient. |
| Positive subthreshold E | MATCH | — | V3:101 explicitly says INCONCLUSIVE, correcting the prior V2 defect. |
| Unpowered-only INCONCLUSIVE | MATCH | — | V3:104 explicitly prohibits both PASS and FAIL for days<437. Execution must apply this before the FAIL iff list at :92-95; a negative, precise, unpowered cell would satisfy that shorter list but is still INCONCLUSIVE by :104. This is a precedence warning, not an assertion that V3 lacks the override. |
| Realized MDE / kill scope | MATCH | — | V3:79,94,97,105 preserve MDE_real=2.8*SE_day, 0.30 R FAIL precision bound, and definition-at-engine-SHA kill scope. No verdict or threshold was changed by this review. |
| Larger family at run time | MATCH inherited; execution warning | LOW | V3:11 leaves V2 section 3 unchanged; V2:47-48 says a larger runtime recount wins. V3's fixed 3.337 and 437-day examples must not override a larger runtime m. Recompute the planning threshold and power eligibility consistently if m rises; this review does not recount outcomes or choose m. |
| Frozen V2 bytes | MATCH | — | V3:14 SHA256 matches both working-tree bytes and committed git blob: cf44beacfe0f6f8bd58c6d0b6bcfbb9b0f5f84227d122e8e1fd633b7749be0e4. |
| Frozen engine bytes | MATCH | — | V3:13 SHA256 matches both working-tree bytes and committed git blob: 51a2a247c06e97148bdf6177f60123236a64c276cf1dd9ce3d734cf079828976. |

HIGH = could change eligibility or make an executor choose an outcome-dependent rule; MEDIUM = disposition/precedence needs clarification; LOW = implementation warning. These are design findings, not measured changes in returns.

## Independent arithmetic and boundary reasoning

Parameters retained from the committed design: OURS effect=0.30 R, cost=0, sd=1.5 or 1.281 R, 80% planning power; declared alpha=0.05 and minimum family m=59. The normal quantiles are recomputed with Python's standard-library `statistics.NormalDist`, independently of producer utilities.

```
from statistics import NormalDist
from math import ceil, sqrt
z = NormalDist().inv_cdf(1 - .05/(2*59))
zb = NormalDist().inv_cdf(.8)
assert abs(z - 3.3368103217106353) < 1e-12
assert ceil(((3.337+.8416)*1.5/.30)**2) == 437
assert ceil(((3.337+.8416)*1.281/.30)**2) == 319
assert ceil(((z+zb)*1.25*sqrt(1.05)/.30)**2) == 319
days = [694,700,654,657,448,452,161,177,27,27,247,162,376,299]
assert sum(d >= 437 for d in days) == 6
assert sum(d >= 319 for d in days) == 7
```

Logical boundary cases (design inspection, not backtest observations):

| Constructed input | V3 disposition / issue |
|---|---|
| Relative gap=0.25 | Comparability gate permits eligibility; other gates still apply. |
| Relative gap=0.250001 | INCONCLUSIVE, no kill scope. |
| E=0 and SE_day=0.30/2.8, powered and comparable | FAIL precision/sign boundary is inclusive. |
| E>0 but t_day<3.337 | INCONCLUSIVE. |
| 436 days, E<0, sufficiently small SE | INCONCLUSIVE by global override, despite satisfying the local FAIL list. |
| Positive eligible strata cover exactly 80% | Stratified PASS requirement is met; other gates still apply. |
| Zero matched events / no controls | Undefined medians, effect and coverage; explicit pre-run handling missing. |
| Some strata <10 controls | E=null there; insufficient positive coverage blocks PASS; final disposition must be made explicit relative to FAIL. |

Hashes were computed with `hashlib.sha256(Path(path).read_bytes())` and independently on `subprocess.check_output(['git','show','HEAD:'+path])`. No engine code was imported; the committed and checked-out hashes agreed exactly.

## Required follow-up

Before any outcome read, clarify the missing-control and insufficient-stratum dispositions, remove the unconditional proxy-based F3 verdict, and make verdict precedence explicit in a committed successor/addendum. Preserve PRE_REG_V2.md and engine bytes. Keep runtime family recount consistent with the inherited larger-m rule. A fresh cross-vendor review should verify that revision; the one-run remains subject to its existing audit gate.

This audit is complete with verdict FIX-FIRST. No source file was edited. The separate delivery receipt identifies the report's content commit and verifies upstream containment; it is intentionally not embedded here.
