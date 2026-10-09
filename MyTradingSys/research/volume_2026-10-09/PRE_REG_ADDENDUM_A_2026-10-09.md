# PRE-REGISTRATION ADDENDUM A (frozen after V1 DEV, before any V2 or VALIDATION outcome)

Parent: PRE_REG_VOLUME_2026-10-09.md (commit ec18096). V1 DEV results: commit 81c0b10. Nothing in the parent is changed. This addendum adds (A1) how VALIDATION is run and (A2) a second, better-powered
family. Reason for A2: V1 showed the daily event study is underpowered (120 of 216 daily trials INSUFFICIENT-N; MDE 190-550 bp at n=50-200), so mid/long-term questions need STATE variables that exist on every bar.
Deviations already logged: (i) funding is charged on settlements in (entry, exit] (FORMULAS.md section 13) where the parent text said [entry, exit); (ii) warm-up W=150 bars; (iii) V1 DEV was executed 3 times
(two crashed on code bugs before any outcome was computed; third complete; a fourth only added group means to the contrast table, outcomes identical, seeds fixed).

## A1. VALIDATION (2024-07-01 .. 2025-06-30), run once, frozen
- Frozen event candidate (the only V1 triage PASS): R40D_N, 4h, h=6 bars, REVERSAL orientation (long after RSI(14) crosses down through 40 on a bar with RVadj < 1.5), DEV net +70 bp [+24, +121], RC p_adj 0.081.
  Parent decision rule applies unchanged: VALIDATION pass = n >= 100 AND net > 0 with CI lower bound > 0 AND p < 0.10 AND excess > 0. The expected n on one year is about 40, so the registered rule will most likely
  return INSUFFICIENT-N. That outcome is reported as such (the statistics are still printed), the candidate stays "unvalidated hypothesis", and HOLDOUT stays sealed. The rule is not relaxed after the fact.
- Time hypothesis TH1 (SP3 continuation, session C minus session A, 4h, h=18) was SUPPORTED on DEV (diff -178 bp, CI [-344, -20], q_TH 0.081). It is replicated once on VALIDATION: replicated only if the 95 percent
  CI excludes 0 with the same sign (diff < 0). A DEV-supported contrast that does not replicate is dropped.
- Validation features are computed on DEV+VALIDATION concatenated (so warm-up windows are filled) and events/baselines are restricted to bars with open time >= 2024-07-01; forward returns never reach past 2025-06-30.
- No other V1 trial is evaluated on VALIDATION (no fishing). V2 candidates (below) are evaluated on VALIDATION only if they pass the V2 DEV triage.

## A2. V2 state family (1d bars, DEV only, then VALIDATION for passes)
State at the close of daily bar i (all windows include bar i, nothing after):
- D20 = sum(dv over i-19..i) / sum(v over i-19..i) (20-day taker delta share), dv = 2*tbv - v.
- VT = ln( mean(v over i-19..i) / mean(v over i-99..i) ) (20-day volume trend vs 100-day).
- MOM = ln(c_i / c_{i-20}) (plain price momentum, the CONTROL that every volume state must beat).
- DUS = sum(dv over 20 days restricted to 1h bars 16:00-23:59 UTC) / sum(v over the same bars); DAS = same restricted to 00:00-07:59 UTC. (time analysis: who is buying, US hours or Asian hours)
- Ex-ante rank PR_i = share of the previous 250 values x_{i-250..i-1} that are <= x_i. HI: PR >= 2/3; LO: PR <= 1/3. First valid bar index >= 350 (VT needs 100, rank needs 250).
- RSI(14) daily regime (Malkan 40/60): BULLR = RSI >= 60; RANGE = 40 < RSI < 60; BEARR = RSI <= 40.
Events (16): D20_HI, D20_LO, VT_HI, VT_LO, MOM_HI, MOM_LO, DUS_HI, DUS_LO, DAS_HI, DAS_LO; and BULLR_D20HI, BULLR_D20LO, RANGE_D20HI, RANGE_D20LO, BEARR_D20HI, BEARR_D20LO.
Label direction for *_HI = +1, *_LO = -1; BOTH orientations (follow and fade) are tested as separate trials. Horizons h = 5, 10, 20 days. Trials = 16 x 3 x 2 = 96.
Entry open(i+1), exit open(i+1+h), cost 14 bp + funding (entry, exit]. Inference as parent section 5: RC max-T over the 96 trials, block 40 days, 1000 resamples, seed 12345; min n = 100 (events overlap heavily, so effective n is lower;
the MDE table prints n and the 20-day overlap warning). Triage as parent section 8 (p_adj < 0.10 within the 96-trial family).
Registered contrasts (own BH family of 3, h = 10, follow-oriented): K1 = (MOM_HI & D20_HI) minus (MOM_HI & not D20_HI) [does buy-volume confirm momentum]; K2 = (MOM_LO & D20_LO) minus (MOM_LO & not D20_LO), short-oriented;
K3 = DUS_HI minus DAS_HI [US-hours buying vs Asia-hours buying, time analysis]. Supported only if the CI excludes 0 and q < 0.10.
Placebo: 20 runs with volume and taker-buy shifted by a multiple of 42 days (1d) and the same number of days x 24 hours in the 1h data; same pass-rate rule (> 0.20 = miscalibrated).
Trial registry: 96 + 3 + placebo rows appended under run_id V2-2026-10-09.
