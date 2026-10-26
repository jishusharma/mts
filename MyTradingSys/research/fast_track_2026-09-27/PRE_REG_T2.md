# PRE-REGISTRATION T2 - target window and R:R gate (2026-10-01)

Session: MTS-2026-10-01-1604Z-CLD-ANA-revalidate-tom-fabio. Format: ANGLE_HYPOTHESES.md:77-112 (fields 1-10 committed BEFORE the run; the
result block is appended later; a change means a new ID with `supersedes:`). Task: DSA_TASKS_2026-10-01.md T2
[disk: MyTradingSys/research/_archive/loose_2026-10/DSA_TASKS_2026-10-01.md:12-16]. T2 does not run until this file is committed.
Status: REGISTERED BY THIS FILE. Nothing has been run. The cloud cannot run T2 (no F: snapshots).

## The four required fields (summary; detail in the block below)
- Metric: mean net R per filled trade (base fees, sim.py rates), compared between the MARGINAL set and the CONTROL set (definitions below).
- Threshold: 95 percent two-sided week-block bootstrap interval on the difference, 2000 draws, seed 12345; and n filled >= 100 in each set.
- Decision rule: three outcomes (CONFIRMED / FALSIFIED / INCONCLUSIVE) fixed in field 8. The Provenance rule, not the backtest, decides the form of the replacement; the backtest decides only whether the replacement may go beyond collection-only.
- Stopping condition: one run per (option, config hash); stop on n < 100 in either set, or on any change to the code under test after registration; no parameter is re-tuned after a result.

## Why the WAIT_RR rate is not the metric
The HANDOFF suggested "reduce WAIT_RR from 67 percent to below X percent". [disk: MyTradingSys/research/_archive/loose_2026-10/REVALIDATION_REQUEST_2026-10-01.md:348] WAIT_RR was 80,847 of 120,892 rows, 66.9 percent. [disk: TOM_CORE_BT.md:14]
Removing the R:R gate sets that share to 0 by construction, so a threshold on it cannot be missed and cannot falsify anything. It is reported as a funnel
figure and is never decisive.

## E-T2-01 (id assigned by this file; the supervisor may renumber) - what do the NO-SOURCE R:R gates remove?
1  hypothesis:   H-T2-1. The NO-SOURCE target window [2.0R, 3.5R], the nearest-level pick, the gross >= 1.5 gate and the net >= 2.0 gate (A08-A11, A13; all NO-SOURCE
                 [disk: PROVENANCE_AUDIT_TOM.md:30-35]) remove trades whose mean net R is not higher than the trades they keep.
                 Tag: NO-SOURCE (the gates). Arm O1 below uses Tom-sourced forms: TOM-018 (HVN as target, per DSA_TASKS_2026-10-01.md T1) and the target quotes Q03, Q12, Q44 (audit quote ids, not TOM ids) [disk: PROVENANCE_AUDIT_TOM.md:163].
2  competitors:  H-T2-2: the gates select better trades (marginal set is worse than control). Predicts a NEGATIVE difference with the interval excluding 0.
                 H-T2-3: R:R has no relation to net R at all (difference near 0 with a tight interval); equals H-T2-1 in action but differs in cause.
3  prediction:   Arms. CONTROL O0 = the rows and trades the current rule keeps (verdict not WAIT_RR; window and gates as in code). O1 = O0 plus the candidates the gates
                 remove, with target = nearest high-volume node or POC in trade direction, VWAP for scalps, no prior-day high/low targets, no window, no R:R gate, fee charged
                 in R (fee / stop width) instead of the flat 25 percent [disk: PROVENANCE_AUDIT_TOM.md:163-164]. MARGINAL set = trades in O1 not in O0.
                 Metric: D = mean net R(MARGINAL) minus mean net R(O0), per filled trade, base fees (maker 0, taker 5 bps, sim.py rates [disk: TOM_CORE_BT.md:18]).
                 Direction and threshold: H-T2-1 predicts that D is not negative; it is judged by the 95 percent interval of D (field 8), not by a point estimate.
                 Also predicted (mechanical, reported only): WAIT_RR share 0 percent under O1; share of marginal-set trades with planned gross R:R above 3.5 is above 0.
4  falsifier:    D < 0 with the 95 percent interval entirely below 0 (H-T2-2). A marginal set that is empty or has n < 100 is INCONCLUSIVE, not falsified.
5  test:         code path@commit: the commit that carries this file (tom_bt.py, verdict.py, SetupCandidatesBuilder.java unchanged; any change after registration voids this block).
                 data: F:\\MTS\\data\\tom_snapshots (gz JSONL, 120,892 rows 2022-01-20..2026-09-27 [disk: TOM_CORE_BT.md:10]) re-evaluated with the O1 candidate rule.
                 Feasibility note (not verified on F:): rows dropped by the net R:R gate remain as WAIT_RR rows with a candidate; candidates dropped by the window (A10, "else candidate
                 dropped") are absent from the stored rows and need the Java candidate builder re-run in archive mode on the desktop.
                 Variant: proof >= 3 (WATCH + SETUP_FORMING episodes), the only variant with n >= 100 (n filled 4417 [disk: TOM_CORE_BT.md:275]). proof >= 4 reported as secondary
                 (n filled 902). The live rule (proof >= 5, n filled 17) is reported descriptively only. The stop stays as built: the 0.1 percent floor and 0.2 percent fallback are
                 NO-SOURCE and unchanged here (T3 decides them), so T2 measures the target rule under an unsourced stop; this is a stated limitation.
                 Statistics: week-block bootstrap (blocks of calendar weeks; existing practice [disk: MyTradingSys/research/fast_track_2026-09-27/T058_BROKEN_EXTREMES.md:207]),
                 2000 draws, seed 12345 (as boot_ci [disk: MyTradingSys/backtest/tom_bt.py:283]). Trial count increment: +1 (O1); stress configs are re-pricings and not trials.
                 Registry key: run_id + git hash + config hash (ANGLE_HYPOTHESES.md:84-86).
6  runner:       desktop F: snapshots; tier T1 Qwen implements the O1 candidate rule (stage .new only; backtest/ files, not execution/ or layers/alerts/); tests from Sonnet/Haiku
                 derived from this spec; supervisor reads the diff.
7  cost:         about 1 desktop hour of wall time for the re-evaluation (estimate, not measured), one Sonnet test pass, 15 operator minutes.
8  decision rule (fixed now):
                 n gate: n filled >= 100 in the MARGINAL set and in O0 (protocol minimum [disk: TOM_CORE_BT.md:20]); else INCONCLUSIVE.
                 CONFIRMED (H-T2-1; means "not rejected", not "proved"): the interval for D lies above 0 or contains 0, i.e. no evidence the gates add net R. Action: the NO-SOURCE window and gates are replaced by O1's
                 Tom-sourced forms (Provenance rule: remove or replace unsourced gates) and O1 may be considered for the engine behind a flag after supervisor review.
                 FALSIFIED (H-T2-2): interval entirely below 0. Action: the gates still have no Tom source and are still removed from the NO-SOURCE list per the Provenance rule, but
                 the marginal trades are NOT admitted to the live path; the supervisor decides whether a Tom-sourced condition that reproduces the filter exists (hit-rate conditioned
                 minimum: Q05 and the "at least a riskreward ratio of 1.5" passage [T/k0zm5NYn0IQ:19@19400]).
                 INCONCLUSIVE: same action as FALSIFIED for the live path; report counts.
                 The backtest never rescues an unsourced gate and never condemns the removal of one; it only gates going beyond collection-only.
                 No threshold in this block is a trading parameter; none may be tuned after a result.
8b stopping condition (fixed now):
                 One run per (option, config hash). Stop and report INCONCLUSIVE if either set has n < 100. Stop and void the block if any file named in field 5 changes after
                 registration (write a new E-ID with `supersedes:`). A same-day re-run after a bug fix is a new trial row, never an overwrite. No re-run to change a block length,
                 seed, variant or the proof threshold. Maximum 2 arms (O0, O1); a third arm needs a new pre-registration.
9  if confirmed / if falsified: see 8.
10 registered:   2026-10-01, session MTS-2026-10-01-1604Z-CLD-ANA-revalidate-tom-fabio; commit hash of this file: recorded by the operator on cherry-pick (a file cannot contain its own commit hash).
--- RESULT (appended) --- none yet.

## Known limits, stated before the run
- The simulator defects H1, H2, M1-M9 [disk: TOM_CORE_BT_REVIEW_2026-09-30.md:18-95] apply to both arms. H2 (null) is not used by this test; M8 (holdout) is not used because the
  comparison covers the full 4.7 years and the O1 rule comes from Tom text, not from these data. M1 and M2 (optimistic fills) affect both arms equally; that is an assumption, Confidence M.
- n for the marginal set is unknown before the run; if the stored rows cannot reproduce the window-dropped candidates, the marginal set contains only the gate-dropped rows and says so.
- A positive D says nothing about live profitability: both arms have negative mean net R in the current report (watch net -0.30 [disk: TOM_CORE_BT.md:275]).
- Unvalidated domain: which R:R window is "correct" for Tom. No backtest answers it under the Provenance rule; this block does not try.
