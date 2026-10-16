# PRE_REG_V3 addendum draft: realised-MDE and clustered verdict rule

Status: draft for review before any V2 study run. No study run or outcome data read is authorized by this addendum. The study remains DEV-only.

## Verdict function

For the pooled READ cell, let E be the preregistered event-minus-control net-R estimand, `SE_day` its day-clustered standard error, and `SE_week` its week-clustered standard error. Use the Holm threshold `z = 3.241` (OURS, from PRE_REG_V2 s.3; a larger pre-run recount wins).

- **FAIL** only when `E <= 0` and the realised MDE plus cost is at most 0.30 R: `2.8 * SE_day + cost_R <= 0.30`. If this condition is not met, an otherwise negative result is **INCONCLUSIVE** and the kill scope is not applied. The multiplier 2.8 and 0.30 R limit are OURS, implementing AUDIT_BEFORE_RUN.md item 2.
- **PASS** only when `E > 0`, `abs(t_day) >= 3.241`, and `abs(t_week) >= 3.241`, in addition to the other frozen PRE_REG_V2 PASS gates. The week-clustered condition is an additional required gate.
- All other outcomes are **INCONCLUSIVE**. `t_day = E / SE_day`; `t_week = E / SE_week`, using the study's corresponding clustered estimates. Missing required statistics are NOT_IN_DATA and cannot be replaced by zero.

## Effect-size labels and planning sensitivity

The 0.375 R plausible effect is **OURS, set after counts were seen** (PRE_REG_V2 s.0, s.3, s.6); it is not trader-sourced. Show the 0.30 R sensitivity beside it. Under the OURS planning inputs `sd = 1.5 R`, cost `0.066 R`, `z = 3.241`, and 80% power term `0.8416`, `n_needed = ceil(((z + 0.8416) * sd / (effect - cost))^2)`: 685 days at 0.30 R and 393 days at 0.375 R. These are planning counts, not outcome estimates.

## Scope and implementation

Apply only to the context composite V2 pooled READ cell, DEV only. The pure implementation is `context_fix2_mde_rule/mde_rule.py`; this file is an addendum draft and requires incorporation into the run's governing pre-registration before `study_v2.py` is run. No study has been run under this draft.
