# PRE-REGISTRATION V2: failed auction at the prior-day value-area edge, BTCUSDT 5m, DEV (2026-10-16, supersedes PRE_REG.md before any outcome)

Answers `AUDIT_BEFORE_RUN.md` items 1, 2, 4, 5 by number. Written by a Sonnet worker (claim `q76-q77-pre-reg-v2`), docs only: no outcome code, no outcome read, no bar with open >= 2024-07-01.
The supersede is legitimate because no outcome of this study exists (AUDIT_BEFORE_RUN.md header). Everything in `PRE_REG.md` stays as written (levels, T1-T6, entry/stop/target, costs, section 3 fills, section 6 split, section 7 traps) EXCEPT where this file states a change. Labels: SOURCED = quote + file:line; OURS = judgement.
Counts used (count-only, no outcome column): `COUNT.txt` (n_T feasible 1,835 on 662 days; C touch 1,254 on 886 days) and `python scripts/dev/verdicts.py count --split DEV` run 2026-10-16 = 17 variants from 11 studies, 6 rows UNPARSED.

## Item 1. T minus C paired term in PASS_T (AUDIT item 1)
Problem: PRE_REG:74-75 lets PASS_T hold with a losing C (R1 lesson, control t_cost -6.0, FABLE_RUNS_AUDIT.md:53, quoted in AUDIT_BEFORE_RUN.md item 1), and C's stop is fixed 0.40 % (PRE_REG:48) vs T's median 0.78 %, so R units are not comparable.
Fix (all OURS):
- **C re-defined, matched on stop_pct.** C keeps its trigger (first 5m bar of the UTC day whose high >= VAH, or low <= VAL for the long mirror; entry = that bar's close; target = other edge; T5/T6) but its stop = entry x (1 +- s) with s = the `stop_pct` of the first feasible T event of the same UTC day and side. A day-side with a feasible T event and no C touch, or a C touch with no feasible T event, is unpaired: counted, dropped from the paired term, never traded. C is now only a paired comparator; the old unmatched C (stop 0.40 %) is not computed.
- **Paired term D = mean over paired UTC days of [ mean net_R_T of that day's T trades minus net_R of that day's matched C trade ]**, taker cost on both legs, each in R of its own stop (equal stop_pct makes the R units equal). SE = day-block bootstrap, 2000 resamples, seed 20261016 (FORMULAS 18.7, as PRE_REG 3.3), clustered by UTC day.
- **PASS_T** iff all of: n_T >= 200 (n compared = traded T events after T4 and T5, not the 1,835 of the count; AUDIT item 2 note) AND mean net_R_T (taker) > 0 AND D > 0 with t_D = D / SE_D >= z_holm (item 4) AND paired days >= the item-2 gate AND MDD_T <= MDD_BH. The old `t >= 2.0` is replaced by z_holm (a higher bar; no bar is lowered).
- **PASS_C is dropped** (C is a comparator, not an arm that can be adopted). Verdict words: `T: PASS | FAIL | INCONCLUSIVE | BLOCKED`; the C row of VERDICTS.csv is written as `C (paired comparator)`, same verdict word as T, kill scope none.
- INCONCLUSIVE iff n_T < 200 or paired days < the item-2 gate; never relabelled FAIL.
- DECISION (OURS): T's stop floor, filter, fills, costs unchanged; the paired comparison can only make the verdict stricter than PRE_REG.

## Item 2. Plausible effect and MDE under day clustering with Holm k (AUDIT item 2)
- **Plausible gross effect (OURS): 0.30 R per trade.** The 0.75 R of PRE_REG:67-69 is Tom's swing win rate on another setup; the only location-only evidence is ~0 gross (`gross_effect_screen_2026-10-15` arm C, AUDIT item 2). Not changed after seeing any number.
- **Unit = UTC day** (events cluster: 662 days, 2.77 events per day, 55 % of day-sides have > 1 event, AUDIT item 2). Per-trade sd = 1.46 R (AUDIT item 2, two-point payoff at rr 1.94), cost 0.179 R (taker, median stop, PRE_REG s.4).
- **MDE (80 % power) = (z_holm + 0.8416) x sd / sqrt(days)**, z_holm from item 4. Freeze/BLOCK rule: the study may run only if MDE + cost <= plausible AND days available >= n_needed = ((z_holm + 0.8416) x sd / (plausible - cost))^2. Otherwise `BLOCKED.md`, nothing computed.
- **Arithmetic on today's counts, m = 42, z_holm = 3.241:**

| quantity | value |
|---|---|
| days available (feasible T, `COUNT.txt`) | 662 |
| MDE on 662 days | (3.241 + 0.8416) x 1.46 / sqrt(662) = **0.232 R** |
| MDE + cost | 0.232 + 0.179 = **0.411 R** > plausible 0.30 R |
| n_needed days at 0.30 R | (4.083 x 1.46 / 0.121)^2 = **2,427 days** vs 662 (DEV holds 912 days in all) |

- **The gate FAILS on today's counts.** At a plausible 0.30 R no DEV design of this cell can be powered at the Holm z: even at zero cost n_needed is about 395 days (ERRATUM 2026-10-18: the original text said "about 1,000"; correct value (4.083 x 1.46 / 0.30)^2 = 394.8, see ERRATUM section at the end; the gate still fails because 2,427 days are needed at cost 0.179 R). Per the AUDIT rule ("if MDE + cost > plausible, BLOCK") the executing session reruns this arithmetic from `COUNT.txt`, writes `BLOCKED.md` with the numbers and stops, unless the operator has first overruled the plausible effect in writing in `OPERATOR_DECISIONS.md` (then a PRE_REG_V3 with its own gate supersedes this file). `DECISION (OURS)`: conservative = BLOCK; no stop-floor, horizon or parameter search may rescue the gate (a second parameter set is scope_out in the card).
- The freeze bar `n_T within 1 % of 1,835` (PRE_REG:72-73) is kept, applied to the feasible count of `count_prior_va.py`; the traded n_T is reported separately.

## Item 4. Holm k (AUDIT item 4)
PRE_REG:81-82 gave k = 1 (no ledger). Recount, counts only, 2026-10-16:
- `verdicts.py count --split DEV` = **17** (lower bound) + **6** rows reported as split UNPARSED (counted to be safe) + **16** distinct factor x definition rows in `context_factors_2026-10-16/trials.csv` + **1** the `context_factors_2026-10-16/PRE_REG_V2.md` composite (same day, same pd_va levels, AUDIT item 4) + **2** arms of this study (T and the paired C comparator) = **42**. The AUDIT had 39 from a count of 14; the tool now says 17, so this is recounted, not copied.
- **m = 42, z_holm = Phi^-1(1 - 0.05 / (2 x 42)) = 3.241** (two-sided), written into the PASS_T rule of item 1. If a recount before the run gives m' > 42 the executing session uses m' (stricter), never a smaller m. The `EXPOSURE_LEDGER.csv` row records m.

## Item 5. VERDICTS.csv row (AUDIT item 5)
- `verdicts.py check "value area failed auction"` on 2026-10-16: no prior row matches; safe to pre-register (no BLOCK).
- Card step added (card `pit-prior-va-failed-auction-dev`): after RESULT.md run `python scripts/dev/verdicts.py backfill`, check that the T row and the C row are not UNPARSED in verdict, n and mean, fix the RESULT.md wording until they parse, commit the CSV. A BLOCKED outcome also gets a row.
- So that the parser reads it (`verdicts.py:160,199`), RESULT.md must contain a table headed `Verdict arms` with columns `arm | n | mean | se | verdict`, and this exact sentence, which this file also carries as the kill scope: **FAIL means stop: no detector, chart, layer or management work on the failed-auction-at-prior-day-value-edge family on BTC 5m with the probe-extreme stop (FAB-4, TOM-12 as encoded here); it says nothing about other stops, timeframes, Krown, Malkan or Tom's other rows.**

## Carried notes (not blockers; defined here)
- Filter (AUDIT item 3): stop basis |close[t] - E| as in count_prior_va.py:155-170; fills at open[t+1]; the 0.40 % floor is NOT re-tested at the fill (stated, not varied).
- PIT (AUDIT item 6): the card adds a fail-first test (a planted day-d level changes the events) for count_prior_va.py's slicing, before any outcome script.
- Everything not named above stays frozen as in PRE_REG.md; one run only; VALIDATION read once later by a separate card after a PASS; HOLDOUT sealed.

## DECISION log
- DECISION (OURS): plausible effect 0.30 R; units = days; two-sided z; m = 42 recounted; gate fails, so the default is BLOCK.
- DECISION (OURS): C kept only as a stop-matched paired comparator; PASS_C dropped.

## ERRATUM 2026-10-18 (power sentence; no outcome read, no decision number changed)
- Wrong: "even at zero cost n_needed is about 1,000 days". Correct: zero-cost n_needed = ((z_holm + 0.8416) x sd / plausible)^2 = (4.083 x 1.46 / 0.30)^2 = 394.8, about 395 days. Hand arithmetic: 4.083 x 1.46 = 5.9612; 5.9612 / 0.30 = 19.871; 19.871^2 = 394.8. Inputs from lines 18-20 above (sd 1.46, plausible 0.30, z_holm 3.241 + 0.8416 = 4.083). Zero-cost n_needed 395 is below the 912 DEV days, so the "> 912" wording is also wrong; the gate fails because of the 0.179 R cost: n_needed at cost = (4.083 x 1.46 / 0.121)^2 = 2,427 days (unchanged) vs 662 feasible days (unchanged).
- Unchanged: 2,427 days, 662 days, MDE 0.232 R, MDE + cost 0.411 R, BLOCK default. Sources: this file lines 18-28; MyTradingSys/research/pit_levels_2026-10-16/bug_b187_evidence.txt; MyTradingSys/research/layer_lab/reports/2026-10-18_q76-dev-ext-power-check.md (1,207 of 2,427 days with DEV_EXT).
