# PRE-REGISTRATION ADDENDUM B (frozen after V1/V2 DEV and V3 VALIDATION of the two addendum-A candidates; before any V4 outcome)

Parents: PRE_REG_VOLUME_2026-10-09.md (ec18096), ADDENDUM A (6e6227b). V3 result (this session): both addendum-A candidates failed VALIDATION
(R40D_N: n=50, net -2 bp; TH1: replicated with the opposite sign). HOLDOUT has never been loaded.

## B0. Why one more test
The single question the operator asked that V1-V3 could not settle with power is "does volume CONFIRMATION improve breakouts / consolidations / RSI 40-60 crosses?". On DEV the volume-confirmed
minus unconfirmed difference (contrasts C1-C6) was positive in 6 of 6 daily pairs (+100 .. +946 bp at h=10) and 5 of 6 at 4h (-43 .. +139 bp at h=18), each individually unsupported after BH (smallest q 0.19).
That pattern was SELECTED by looking at DEV, so DEV cannot test it. It is tested once, as ONE pooled hypothesis, on VALIDATION. This is a data-driven hypothesis; the literature prior (Karpoff 1987; Gervais-Kaniel-Mingelgrin
volume-shock premium; Llorente et al. 2002 speculative-volume continuation) is supportive but not BTC-specific, so it is weak support only.

## B1. The pooled volume-confirmation premium (VCP), definition fixed
Pairs (confirmed event, unconfirmed event, direction): (BBSQ_UP_V, BBSQ_UP_N, +1), (BBSQ_DN_V, BBSQ_DN_N, -1), (DON_UP_V, DON_UP_N, +1), (DON_DN_V, DON_DN_N, -1), (R60U_V, R60U_N, +1), (R40D_V, R40D_N, -1).
Event definitions are exactly those of the parent section 4 (RVadj >= 1.5 = confirmed, < 1.5 = unconfirmed). Each event instance contributes the oriented gross forward return dir * ln(o[i+1+h]/o[i+1]).
VCP = mean(oriented return over all confirmed instances, pooled over the six pairs) minus mean(oriented return over all unconfirmed instances, pooled). A bar can appear in several pairs (each appearance is an instance).
Costs are identical on both sides and cancel. H1 (one-sided): VCP > 0.
- Primary: timeframe 4h, h = 18 bars (3 days). Secondary: timeframe 1d, h = 10 days. Same event windows and block bootstrap as the parent (block 60 bars / 25 days, 1000 resamples, seed 12345, circular).
- Inference: p = share of centred bootstrap replicates >= observed VCP (one-sided). Family of two, Bonferroni alpha = 0.025 each.
- DEV values are reported as the DESCRIPTIVE prior only (the hypothesis was selected on DEV, so no DEV p-value is evidence). The TEST is VALIDATION (2024-07-01 .. 2025-06-30), run once.
- Support rule: VALIDATION p < 0.025 AND VCP > 0 AND the confirmed-group pooled oriented mean is not worse than the unconfirmed group by sign (i.e. VCP > 0 is the claim). Only then is HOLDOUT (2025-07-01 .. 2026-09-30) opened, once, with the same rule.
  If VALIDATION is not supported, HOLDOUT stays sealed and the hypothesis is recorded as NOT SUPPORTED.
- Also reported (descriptive): number of pairs with positive difference on each window; confirmed-group pooled oriented gross mean net of 14 bp round trip (is the confirmed class itself profitable?); split by session group A/B/C (4h) as EXPLORATORY.

## B2. Descriptive appendix (not evidence)
For events marked INSUFFICIENT-N in V1 (including the operator's exhaustion-volume cases BCLX, SCLX, ABS_LOW, ABS_HIGH, NODEM_HIGH, NOSUP_LOW, DRY_UP, DRY_DN), print n, oriented mean forward return and block-bootstrap CI on DEV at the V1 horizons when n >= 20,
labelled "descriptive, no inference, no pass/fail". These numbers cannot create a candidate.

## B3. Trial accounting
V4 adds 2 primary trials (4h, 1d). Registry run_id V4-2026-10-09.
