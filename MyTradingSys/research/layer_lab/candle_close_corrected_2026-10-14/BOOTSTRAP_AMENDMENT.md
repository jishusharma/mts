# Bootstrap normalization repair: fixed estimand, unchanged hypotheses

2026-10-14. Preserve the pre-fix outputs in analysis_v2_before_bootstrap_fix/. This is an estimator repair, not a new parameter search, and is logged as another analysis attempt on inspected DEV.

The original resampled probability contrast divided signal minus control outcome contributions by resampled signal count only. Calendar blocks can change the signal and donor masses differently. A counterexample establishes the error: all signal wins=1 and all control wins=1 must have lift=0 under any resample containing both populations; the unnormalized book could produce a nonzero contrast merely from unequal counts. With signal value10 on day0 and control6 on day1, a sample containing only day0 has no control average; it must be undefined, not contrast10.

Correct the resampled estimand to weighted_signal_win_sum / weighted_signal_count MINUS weighted_control_win_sum / weighted_control_mass. If either denominator is zero, that replicate is not comparable and is excluded. Both sides use the same calendar-block draws and the fixed feature-based matching graph. Point lift at the original weights is unchanged because original donor weight sums to the number of matched signals. Gross/funding/cost point estimates and their signal-average intervals, classifier, signatures, matched controls, all cutoffs, horizons and 6048 metric family remain unchanged. Full rematching uncertainty is still not modeled.

The constant-outcome and unequal-count fixtures fail before bootstrap_contrast exists and pass after correction. Extend the independent real-cell interval reconstruction to this separate normalization. No new price outcomes, selection rule or phase variant is introduced.
