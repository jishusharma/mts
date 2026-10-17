# BLOCKED: PRE_REG_V2 item-2 power gate fails (2026-10-17, card pit-prior-va-failed-auction-dev, Q85)

Verdict word: BLOCKED. No outcome was computed or read; no run_prereg.py was written; no bar with open >= 2024-07-01 was touched. PRE_REG.md, PRE_REG_V2.md and PIT_CONTRACT.md are unedited.

## What was rerun (count only)
- `count_prior_va.py` rerun on DEV 2026-10-17: output identical to the committed `COUNT.txt` (CRLF aside): feasible T n = 1,835 on 662 days (n_T within 0 % of 1,835, freeze bar met), C touch n = 1,254 on 886 days, DEV = 912 days.
- Holm m recount: `verdicts.py count --split DEV` now prints 37 (V2 had 17) + 6 UNPARSED + 16 context_factors trials + 1 composite + 2 arms = **62**. V2 item 4 says use the larger m' if m' > 42, so both are shown.

## Gate arithmetic (recomputed here; sd 1.46 R, cost 0.179 R, plausible 0.30 R, days 662)
| m | z_holm | MDE on 662 days | MDE + cost | n_needed days at (0.30 - cost) | days needed at zero cost |
|---|---|---|---|---|---|
| 42 | 3.241 | 0.232 R | 0.411 R | 2,427 | 395 |
| 62 | 3.351 | 0.238 R | 0.417 R | 2,559 | 416 |

MDE + cost > 0.30 R and days 662 < n_needed at both m, so the freeze rule says BLOCK. (V2's note that zero cost needs about 1,000 days is not reproduced by the formula as printed: it gives 395-416 days; the verdict does not depend on it, because cost is real.)

## What would unblock it
Any one of: (a) a written operator overrule of the plausible effect in OPERATOR_DECISIONS.md (grep found none for this study) followed by a PRE_REG_V3 with its own gate; (b) a plausible gross effect >= about 0.43 R (so that MDE 0.232 + cost 0.179 <= plausible at m = 42; 0.44 R at m = 62); (c) about 2,427 to 2,559 distinct feasible days, against 912 DEV days in all (not reachable without VALIDATION/HOLDOUT bars, which this card may not read).
No stop-floor, horizon or parameter search may rescue the gate (card scope_out).

## DECISION log
- DECISION (OURS, conservative default): BLOCKED, no outcome run, no VALIDATION/HOLDOUT read.
- DECISION (OURS): larger m' = 62 reported beside 42, as V2 item 4 requires; verdict identical.
- DECISION (OURS): no RESULT.md written (nothing to report); VERDICTS.csv row comes from `verdicts.py backfill` as it parses the folder.
