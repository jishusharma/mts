# GPT independent audit: T05 LC1 touched-only control

## Scope and method

I re-ran the standard DEV interval only: decision bars 2022-04-01 through 2024-06-30, with history loaded from 2022-03-21 for prior-level construction. The input loader is bounded at 2024-07-01 UTC and the script asserts both the input maximum and scored DEV dates are before that boundary. No VALIDATION/HOLDOUT bars after 2024-06-30 were read.

I used the existing causal level-family generator to define the same candidate levels, but independently coded first-touch detection, prior-close side, stop-width reaction outcome, touched-only line scoring, family/month distance pool, and day-cluster bootstrap. Formula source for the value-area profile is `MyTradingSys/backtest/layers/FORMULAS.md:415-420` section 18.1; causal level definitions are in `MyTradingSys/research/levels_confluence_2026-10-14/levels.py`; the study reaction contract is described in `MyTradingSys/research/levels_confluence_2026-10-14/levels_hold.md` and implemented at `levels_hold.py:11-49`. The independent code and parsed family output are [recheck.py](recheck.py) and [independent_results.csv](independent_results.csv).

Reproduction command from repository root:

```powershell
python MyTradingSys/research/gpt_burn_2026-10-24/gx4-t05-recheck/recheck.py
```

Parameters OURS: seed 20261024, K=20 controls per candidate level, 2,000 day-bootstrap draws. A control line contributes only when touched. HOLD requires a one-stop-width favorable move after the touch before a one-width adverse penetration; penetration wins if both occur in the same bar. KEEP requires the lower 95% day-bootstrap bound of real-minus-control to be strictly positive. Bootstrap resamples days and recomputes the difference of the pooled hold ratios. As in T05, candidate generation is shared with the published study so this tests the control/recount independently, not the level definitions themselves.

## Recount

`T05 verdict` below is the fair-control verdict in T05's table (T05_placebo_nulls.md:196-209). Number columns show real touches and hold rate, control touched lines and hold rate, real-minus-control in percentage points, and my 95% CI. “Agree” is family-level KEEP/DROP agreement with T05. T05's earlier published verdict is included to show the claim's flip.

| Family | T05 verdict | My verdict | Numbers: real n / HOLD; control n / HOLD; diff pp [95% CI pp] | Published verdict | Agree? |
|---|---|---|---|---|---|
| 4h_fractal_high | DROP | DROP | 1,984 / 46.27%; 42,126 / 49.75%; -3.48 [-5.96, -0.99] | KEEP | AGREE |
| 4h_fractal_low | DROP | DROP | 1,963 / 44.88%; 41,878 / 50.27%; -5.39 [-7.69, -3.07] | KEEP | AGREE |
| daily_open | DROP | DROP | 822 / 49.27%; 16,435 / 48.93%; +0.34 [-2.46, +3.32] | DROP | AGREE |
| naked_poc | DROP | DROP | 732 / 53.14%; 14,896 / 51.04%; +2.10 [-1.20, +5.50] | KEEP | AGREE |
| prior_day_high | DROP | DROP | 380 / 37.63%; 7,937 / 49.45%; -11.82 [-16.41, -7.02] | KEEP | AGREE |
| prior_day_low | DROP | DROP | 345 / 40.87%; 7,611 / 48.61%; -7.74 [-13.13, -2.55] | KEEP | AGREE |
| prior_day_poc | DROP | DROP | 583 / 52.66%; 11,070 / 51.27%; +1.38 [-2.42, +5.47] | KEEP | AGREE |
| prior_day_vah | DROP | DROP | 537 / 48.23%; 10,508 / 51.21%; -2.98 [-7.30, +1.33] | DROP | AGREE |
| prior_day_val | DROP | DROP | 539 / 52.32%; 10,400 / 50.70%; +1.62 [-2.51, +5.80] | DROP | AGREE |
| prior_week_high | DROP | DROP | 150 / 44.67%; 2,775 / 49.84%; -5.17 [-13.11, +2.23] | KEEP | AGREE |
| prior_week_low | DROP | DROP | 124 / 43.55%; 2,809 / 50.84%; -7.29 [-16.08, +1.36] | DROP | AGREE |
| round_1000 | DROP | DROP | 831 / 45.01%; 16,454 / 49.45%; -4.45 [-7.97, -1.05] | KEEP | AGREE |

All 12 family verdicts agree with T05. None of its eight previously published KEEPs survives the stated KEEP rule; four families were already DROP. My different fixed seed changes some control rates and CI endpoints slightly, not any family decision. The three positive real-minus-control point estimates remain uncertain because their CIs include zero.

## Control audit findings

1. **The “exclude the candidate's own distance” description is false. LOW.** T05's report says the fair distance distribution is matched “without re-using the level itself” (T05_placebo_nulls.md:193), but t05_lc1.py:97-102 builds each family/month pool from *all* candidates, including the level currently receiving controls; t05_lc1.py:114-126 samples from that pool with replacement. My independent run found 50.78% of `daily_open` distance draws had exactly the candidate's own distance (other families were 0.37%-10.71%). The random sign then permits the placebo price to equal the real price. Thus the control is not a leave-one-candidate-out null and some “random” outcomes duplicate the real level. This tends to pull the difference toward zero; it does not explain away the observed verdict agreement, but it weakens the claim of an uncontaminated fair control.

2. **Distance matching uses future levels within the month. LOW.** t05_lc1.py:97-102 constructs pools using all DEV candidates in a calendar month, and t05_lc1.py:114-126 uses that month's pooled distances for each decision day. For early-month decisions, distances from later days are therefore used to construct the placebo. This is not look-ahead in HOLD outcomes or bars, and the run does not cross the DEV cutoff; it is look-ahead in the matching covariate. It is acceptable only as a retrospective month-conditioned control, not a causal/available-at-decision control. A strictly causal variant would pool distances from prior observations only (and should leave the current candidate out).

I found no evidence of VALIDATION/HOLDOUT bar leakage or a touch-denominator mismatch in the control implementation. Each untouched placebo is excluded from the touched-only denominator, and day resampling accounts for within-day dependence at the family aggregate level. The control is drawn with replacement, so identical placebo lines can also recur; the day bootstrap clusters their results by day, though the report does not separately quantify unique-line reuse.

## Conclusion

**AGREE for all 12 families.** Independently re-derived counts support T05's claim that none of the 8 published KEEP families remains KEEP under the specified touched-only random-line comparison. Qualify the claim: the implemented fair pool can reproduce a candidate's own distance and uses full-month future distances. The latter is a retrospective matching choice, not evidence that future return bars were used.

Result: Independent DEV recount agrees with T05: all 12 families DROP; the control pool includes the candidate distance and future same-month distances.

