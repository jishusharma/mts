# AUDIT_BEFORE_RUN: pit_levels PRE_REG and card `pit-prior-va-failed-auction-dev` (2026-10-16, independent)

**Verdict: FIX-FIRST (4 items).** Card set to `refined`; PRE_REG.md untouched. Fix route: new
`PRE_REG_V2.md` committed BEFORE any outcome code (no outcome read yet, so a supersede is legitimate).
Data: DEV count-only columns; no outcome, no bar >= 2024-07-01. Reproduced n_T feasible 1,835 / 662 days.

| # | Item | Verdict |
|---|---|---|
| 1 | T vs control | **FIX-FIRST** |
| 2 | Plausible effect / MDE | **FIX-FIRST** |
| 3 | Feasible-subset filter | GO |
| 4 | Holm k | **FIX-FIRST** |
| 5 | VERDICTS.csv row | **FIX-FIRST** |
| 6 | PIT builders | GO |

## 1. T vs C: FIX-FIRST
PRE_REG:74-75 PASS_T needs only mean net_R_T > 0, t >= 2.0, MDD <= buy-and-hold. No T-minus-C term. PASS_C (:75) is a separate arm
verdict, so a T pass with a losing C still reads PASS_T; R1's lesson (control t_cost -6.0, FABLE_RUNS_AUDIT.md:53) is not applied.
C is also not comparable: stop fixed at 0.40 % (:48) vs T median 0.78 %, so R units and R:R differ. Fix: PASS_T also needs a day-paired clustered (T - C) > 0 at the item-4 Holm z, C matched to T on stop_pct.

## 2. Plausible effect and MDE: FIX-FIRST
Own arithmetic, n 1,835, rr 1.94, cost 0.179 R (mean 0.184 R over the subset), power term 0.8416:
- 0.75 R (sd 1.443): i.i.d. 0.094 + 0.179 = 0.273 (:70); passes under every variant.
- **0.30 R** (sd 1.46): i.i.d., alpha 0.05: 0.095 + 0.179 = 0.274, holds barely. But the verdict uses day-clustered SE (:56, 3.3), and
  events cluster: 662 days, 2.77 events/day, 55 % of day-sides have > 1 event. With 662 effective days MDE 0.159, total 0.338: **fails**.
  With Holm m = 15: i.i.d. 0.308 fails; m = 37: 0.317 fails.
So at 0.3 R the freeze does not hold once clustering or Holm is priced in. The 0.75 R (:67-69) is Tom's swing win rate on another setup; the only location-only evidence is ~0 gross (gross_effect_screen C). Fix: plausible <= 0.3 R, MDE on days with the Holm z; if MDE + cost > plausible, BLOCK. Also T5 (:43) drops triggers that count_prior_va.py:163 keeps, so traded n_T < 1,835 trips the :72-73 1 % rule: define the n compared.

## 3. Filter: GO
stop_pct = |E - close[t]| / close[t] with E = max high of bars that closed outside, up to t (count_prior_va.py:155-170). Only bars <= t, so no
look-ahead. Notes for V2 (not blockers): the day skip (:141) uses later bars' presence, not price; E excludes the trigger bar's own high (beyond E in 3.6 % of events); R denominator uses close[t] but fills use open[t+1] (:3.1) and
the floor is not re-tested at the fill: define it.

## 4. Holm: FIX-FIRST
`verdicts.py count --split DEV` returns **14** (lower bound: 6 UNPARSED rows not counted). PRE_REG:81-82 sets Holm only
"when the ledger holds k > 1 variants of this family"; `EXPOSURE_LEDGER.csv` does not exist (:85), so k = 1, t >= 2.0. That omits the 14 and
the shipped `context_factors_2026-10-16` study, whose PRE_REG:61 already fixed m = 37 (14 + 6 + 16 + 1) and which reads the same pd_va
VAH/VAL levels (CONTEXT_FACTORS_SPEC.md:35, from 5m bars, a different profile source than this 1m build). Fix: m = 37 + this study's 2 arms = 39 (or
recount), z = 3.22, written into PRE_REG_V2 and into the pass rule.

## 5. VERDICTS.csv row: FIX-FIRST
Card steps/commands (card:45-52) never call `verdicts.py`; sync.py and run_all_tests.py do not either. Even a `backfill` would give UNPARSED: it reads a table headed
"Verdict arms"/"Primary" and a sentence "FAIL means stop:" (verdicts.py:160,199); RESULT (card:12) and PRE_REG:78 use neither. Fix: card step
"python scripts/dev/verdicts.py backfill, check T and C rows are not UNPARSED, commit"; PRE_REG_V2 carries the "FAIL means stop: ..." sentence.

## 6. PIT builders: GO
count_prior_va.py:130 builds `vp_pivot_probe.build_profile` (:101-112) from day d-1's 1m slice, used at :136-143 for day d only; UTC epoch buckets. No level other than prior-day POC/VAH/VAL. Gap: test_pit_leakage.py:366 tests `CTX.static_levels`, not this script's slicing: add a fail-first test (planted day-d level changes events).
