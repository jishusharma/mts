## D1 COMPLIANCE HEADER (added 2026-10-01, retroactive)

This section was NOT present when the note was first committed at e2fb528.
The audit below the line was produced before the playbook Part I gate was
applied. It is corrected here, not rewritten.

### Method note (playbook Part I STEP 1)

Question. Do standard scientific methods exist to close the seven method
gaps found in the Tom/Fabio audit review, and does each method map to a
concrete file and line in this repository where it can be applied?

Evidence that would settle it. Existence of a T1 peer-reviewed method that
directly addresses a named gap, plus a specific disk artifact the method
would change (file path, line range, or data file). A method with no
concrete artifact is listed as unapplied.

### Source-tier commitment (playbook Part I STEP 2, written before search)

Accept: T1 (peer-reviewed journal, NBER/Fed/BIS/central-bank working paper,
regulated-institution research with disclosed method). Accept T2 (preprints
with disclosed method, exchange docs, replicated practitioner studies with
full method). Reject T3 as sole support for core rules (Tom transcripts,
trader blogs, vendor docs). Reject marketing/affiliate outright.

For this note specifically: T1 only. Every method below carries a T1
citation. If no T1 exists for a gap, the note records "no T1 found".

### Tier and quality tag (playbook Part I STEP 3b)

Every item below is re-tagged:
Tier | Method quality (OOS? costs? sample) | Confidence H/M/L

### UNVERIFIED-WEB tag (playbook Part I, D1 item 5)

This session cannot open a web page. Every citation below is UNVERIFIED-WEB
until a surface that can open the source pastes back title, authors, venue,
year, and (for paywalled items) an abstract match. See the dedicated
section at the end of this file.

### No blending disk and web in one sentence

The original R-items mix disk counts (Tom core backtest rows) with method
citations. This is corrected by the tags below: every sentence carrying a
citation carries UNVERIFIED-WEB, and every sentence carrying a disk count
carries file:line.

---

# REVALIDATION REQUEST - scientific methods for the Tom/Fabio audit (2026-10-01)

To: Claude (local CLI or cloud)
From: MTS-2026-10-01-1431Z-DSA-COO
Status: open - each item needs revalidation before T1-T8 proceeds
Related: MyTradingSys/research/_archive/loose_2026-10/AUDIT_REVIEW_2026-10-01.md

## Purpose

The DSA session on 2026-10-01 read the Tom/Fabio audit block (ten files,
listed in AUDIT_REVIEW_2026-10-01.md section 1). It found seven method gaps:
no pre-registration, one reader, no blinded re-derivation, no falsification
attempt, no predeclared counterfactuals, no multiplicity adjustment across
the full search space, no independent replication. The backtest review
document (TOM_CORE_BT_REVIEW_2026-09-30.md) independently found its own
instruments defective: H1, H2, M7, M8, M9.

For each gap, this note names the standard scientific method that addresses
it, tags the source per playbook.md Part I (T1/T2/T3/REJECT), cites the
proof paths and line references on disk, and states what Claude must
revalidate. Each item is a request. None of these methods have been applied
to the audit itself yet.

## R1. Deflated Sharpe Ratio (DSR)

Gap. No trial-count correction. AUDIT_REVIEW_2026-10-01.md section 6, M9:
"No real pre-registration. Registry dedupe by run_id = date; N_trials
understated. FROZEN.md is written after the fact."

Method. DSR corrects observed Sharpe for selection bias under multiple
testing and for non-normal returns (skew, kurtosis). Under M independent
strategies the expected maximum Sharpe from pure chance grows as
O(sqrt(ln(M))). DSR subtracts that expected maximum and normalizes by the
standard error.

Source. Bailey & Lopez de Prado (2014), "The Deflated Sharpe Ratio:
Correcting for Selection Bias, Backtest Overfitting and Non-Normality",
Journal of Portfolio Management 40(5), 94-107. Tier T1 peer-reviewed.

Proof paths on disk:
- MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md - backtest
  results for 4 variants (episode, A, watch_episode, p4_episode)
- MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_REVIEW_2026-09-30.md
  - the defects review (H1-H2, M1-M9, L1-L6)
- MyTradingSys/research/_archive/loose_2026-10/AUDIT_REVIEW_2026-10-01.md section 6

What Claude must revalidate:
1. Read TOM_CORE_BT.md and count the actual N of trials. The review says
   16 rows (4 variants x 4 stress configs) but variants were chosen post hoc.
2. Compute DSR per variant with the correct N.
3. Report whether any variant has DSR p < 0.05 after correction.

Package: deflated-sharpe on PyPI (zero dependencies).
Cost: one function call per variant, given a correct trial count.

Addendum 2026-10-01 (W2, MTS-2026-10-01-1604Z-CLD-ANA-revalidate-tom-fabio): N = 3 distinct signal sets (episode and A are identical; stress configs are re-pricings), lower bound; registry rows 16 (TOM_CORE_BT.md:3) is the upper bound readable from disk; true N including undocumented design iterations is not on disk. DSR probability < 0.95 for every variant at N = 1, 3, 16, 100 (max 0.55, n=17). Detail: REVALIDATION_ACTIONS_2026-10-01.md W2.

## R2. Purged K-Fold with Embargo

Gap. Standard k-fold assumes rows are independent. Time-series labels
overlap when horizons overlap. This leaks future information into training
and inflates backtested Sharpe. Not yet applied in the Tom core backtest.

Method. Purging removes training rows whose label horizon overlaps the test
window. Embargoing removes a post-test buffer. Prevents label leakage.

Source. Lopez de Prado (2018), "Advances in Financial Machine Learning",
Wiley, chapter 7. Tier T1.

Proof paths on disk:
- MyTradingSys/research/_archive/loose_2026-10/GOLAS_CD_WEB_2026-09-21.md L38 lists "Purged K-fold
  + embargo" with T1 tag - already named but not applied
- MyTradingSys/research/_archive/loose_2026-10/BACKTEST_METHOD_2026-09-21.md L35 lists multiple
  testing pre-registration - adjacent, not the same method

What Claude must revalidate:
1. Read TOM_CORE_BT_REVIEW_2026-09-30.md M8. The holdout period
   2026-06-26..2026-09-26 is contaminated by design history: Rule 32
   evidence (Java:120), sim.py:10-13 replay, D1/D3/D4 rulings.
2. Confirm whether backtest/tom_bt.py uses any CV split or a single
   holdout. The review says single holdout (BT:20).
3. If single holdout, propose the CPCV variant (R3).

Packages: purgedcv (PyPI, scikit-learn compatible), vectorbt.pro,
skfolio.

## R3. Combinatorial Purged Cross-Validation (CPCV)

Gap. Single holdout period. AUDIT_REVIEW section 6 M8.

Method. CPCV generates multiple paths of combinations of training and test
data. With N=6 groups and k=2 test groups per split, 15 splits and 5
reconstructed backtest paths. Each path is fully purged and embargoed. A
single contaminated period cannot dominate the verdict.

Source. Lopez de Prado (2018), chapter 12. Tier T1.
Application: KCI cryptocurrency DRL study (2026) used CPCV on BTC data and
achieved lower max drawdown than walk-forward or k-fold.

Proof paths on disk:
- MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md L20 shows one
  holdout period (2026-06-26..2026-09-26)
- MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_REVIEW_2026-09-30.md
  M8 names the contamination

What Claude must revalidate:
1. Confirm the current backtest uses a single holdout.
2. Compute how many CPCV paths are feasible on the 4.7 years of 1m BTCUSDT
   data (hist 2022-01..2025-08, dev 2025-09..2026-06, holdout 2026-06..2026-09).
3. If feasible, replace the single holdout with CPCV and re-run.

## R4. Probability of Backtest Overfitting (PBO) via CSCV

Gap. The review says "DSR/PBO does not apply" (BT:530) because all variants
are reported, but variants were chosen post hoc. M9.

Method. PBO estimates the probability that a backtest is overfit. CSCV
splits the return matrix into S subsets, forms all combinations of S/2
in-sample and S/2 out-of-sample, measures how often the in-sample best
underperforms out-of-sample. Output: probability of overfit, performance
degradation, probability of loss, stochastic dominance.

Source. Bailey, Borwein, Lopez de Prado, Zhu (2013), "The Probability of
Backtest Overfitting", Journal of Computational Finance. Tier T1.

Proof paths on disk:
- MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md - 4 variant
  return series available
- MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_REVIEW_2026-09-30.md
  M9

Package: pbo on CRAN. Documentation gives exact usage: data frame of
returns, S subsets, performance function (Sharpe, Omega).

What Claude must revalidate:
1. Assemble the 4 variant return series into a single matrix.
2. Run PBO with S=16 (typical).
3. Report probability of overfit per variant.

## R5. White's Reality Check and Hansen's SPA test

Gap. Multiple setup families tested without a data-snooping correction. No
correction applies at the family level. AUDIT_REVIEW section 8 item 6.

Method. White's Reality Check (2000) bootstraps the maximum performance
across all K strategies under the null that none has skill. Hansen's SPA
(2005) improves power by recentering and by handling poor and irrelevant
alternatives differently.

Source. White (2000), "A Reality Check for Data Snooping", Econometrica
68(5). Hansen (2005), "A Test for Superior Predictive Ability", Journal of
Business and Economic Statistics 23(4). Tier T1 peer-reviewed.

Application evidence. KOSPI200 futures study applied both: best rule
generated about 32% annual net return, but under data-snooping the result
was statistically insignificant. Finding: substantial technical trading
profits may be obtained due to chance.

Proof paths on disk:
- MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md - 7 setup
  families
- MyTradingSys/research/_archive/loose_2026-10/AUDIT_REVIEW_2026-10-01.md section 8 item 6

Package: sealedge on PyPI implements SPA with a Hansen-literal path
(stationary block bootstrap over per-trial loss-differentials, Hansen Eq.7
recenter, Eq.8 cross-strategy max).

What Claude must revalidate:
1. Extract per-trial return series for the 7 setup families.
2. Run SPA with the sealedge implementation.
3. Report the p-value; if p > 0.10, no family survives data-snooping.

## R6. Romano-Wolf stepwise extensions

Gap. Same as R5 but at the identification level: which specific rules are
significant, not just whether any are.

Method. Romano-Wolf (2005) stepwise extensions to the Reality Check. More
powerful than Bonferroni for correlated tests, identifies which specific
rules survive.

Source. Romano & Wolf (2005), "Stepwise Multiple Testing as Formalized Data
Snooping", Econometrica 73(4). Tier T1.

Proof paths on disk:
- Already referenced in
  MyTradingSys/research/fast_track_2026-09-27/T055a_POSITIONING_FLOW.md  [CHECKED 2026-10-01: NOT FOUND there; grep -i romano hits only the handoff notes and 03_FILE_INDEX.md]

What Claude must revalidate:
1. Same universe as R5.
2. Apply Romano-Wolf stepwise.
3. Report which specific setups survive, not just the family-level p-value.

## R7. Benjamini-Hochberg FDR

Gap. AUDIT_REVIEW section 6 M7: "Subgroup tables (setup, tf, direction,
regime, vol, year, period: RPT:237-243) are not multiplicity-adjusted; only
Fabio tags get Bonferroni-8 (RPT:268-281), per variant, not across 4
variants x 8."

Method. BH-FDR (1995) controls the expected proportion of false discoveries
among rejected hypotheses. Less conservative than Bonferroni.

Source. Benjamini & Hochberg (1995), "Controlling the False Discovery Rate",
JRSS B 57(1). Tier T1.

Application evidence. The tickfloor study ran 517 strategies across 31
families, applied BH-FDR at q < 0.10, and found 0 of 598 tests survived
correction. Lowest adjusted q-value 0.1196.

Proof paths on disk:
- MyTradingSys/research/_archive/loose_2026-10/GOLAS_CD_WEB_2026-09-21.md L40 lists "BH FDR at
  q=0.10 accepted default" with T1 tag
- MyTradingSys/research/_archive/loose_2026-10/BACKTEST_METHOD_2026-09-21.md L35 mentions FDR at
  q=0.10 [UNVERIFIED-WEB]
- MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md L121, L241,
  L371, L501 show Bonferroni-8 per variant

What Claude must revalidate:
1. Collect p-values from all subgroup tables in TOM_CORE_BT.md.
2. Apply BH-FDR at q=0.10 across the whole table (not per variant).
3. Report which subgroup findings survive.

## R8. Stationary Bootstrap

Gap. AUDIT_REVIEW section 6 M7: "Bootstrap treats trades as iid; they
cluster in time and on shared levels. CIs too narrow."

Method. Block bootstrap with random block length. Preserves temporal
dependence by resampling contiguous blocks. The moving block bootstrap is
subject to non-stationarity bias when large drawdowns occur at boundaries;
the stationary bootstrap is more robust for longer block lengths.

Source. Politis & Romano (1994), "The Stationary Bootstrap", JASA 89(428).
Tier T1.

Application evidence. The sealedge SPA implementation uses stationary
bootstrap for the same reason.

Proof paths on disk:
- MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md L284-290
  (2000 iid draws, percentile)  [CORRECTED 2026-10-01: wrong file; the bootstrap is MyTradingSys/backtest/tom_bt.py:283-289]
- MyTradingSys/research/fast_track_2026-09-27/T058_BROKEN_EXTREMES.md L207
  mentions "week-block bootstrap CIs" for overlapping events - adjacent

What Claude must revalidate:
1. Read backtest/tom_bt.py around the bootstrap section.
2. Replace iid bootstrap with stationary block bootstrap (block length
   estimated by Politis-White 2004 automatic selection).
3. Report the wider CI and whether the verdict direction changes.

## R9. Cohen's Kappa on a second reader

Gap. AUDIT_REVIEW section 5: "No inter-rater check. One reader (Opus 5.5)."

Method. Cohen's Kappa measures agreement between two independent readers
beyond chance. kappa >= 0.6 is the conventional threshold for substantial
agreement.

Source. Cohen (1960), "A Coefficient of Agreement for Nominal Scales",
Educational and Psychological Measurement 20(1). Standard practice, T1.

Application on disk.
MyTradingSys/research/fast_track_2026-09-27/ANGLE_HYPOTHESES.md L234-235
already names kappa for the TWOPEAK state hypothesis: "F: TWOPEAK < 60% on
real data (E-002 does not transfer to real profiles), or kappa >= 0.6."
The method is known; it is not applied to the audit itself.

Proof paths on disk:
- MyTradingSys/research/fast_track_2026-09-27/PROVENANCE_AUDIT_TOM.md
  (74 verdict rows)
- MyTradingSys/research/_archive/loose_2026-10/AUDIT_REVIEW_2026-10-01.md section 5

What Claude must revalidate:
1. A second reader (different surface, e.g. cloud Claude) re-derives the
   74 verdict rows from the same rule text, blind to the first list.
2. Compute kappa.
3. Report kappa; if < 0.6, the verdicts are not reliable across readers.

## R10. Pre-registration file for T2

Gap. AUDIT_REVIEW_2026-10-01.md section 9: "Pre-register T2 (target window
/ R:R decision) before its backtest runs. One file: metric, threshold,
stopping rule."

Method. The project already has a format in
MyTradingSys/research/fast_track_2026-09-27/ANGLE_HYPOTHESES.md L77-112:
claim (C), prediction (P), falsifier (F), cheapest test (T), runner,
verdict CONFIRMED | FALSIFIED | INCONCLUSIVE. It is not applied to T2.

Source. Project internal method. No external source needed.

Proof paths on disk:
- MyTradingSys/research/fast_track_2026-09-27/ANGLE_HYPOTHESES.md L77-112
  (format)
- MyTradingSys/research/_archive/loose_2026-10/DSA_TASKS_2026-10-01.md T2 (the task)
- MyTradingSys/research/_archive/loose_2026-10/AUDIT_REVIEW_2026-10-01.md section 9

What Claude must revalidate:
1. Write the T2 pre-registration file before running the T2 backtest.
2. Name: metric (WAIT_RR rate?), threshold (e.g. reduce WAIT_RR from 67%
   to below X%), decision rule, stopping condition.
3. File at MyTradingSys/research/fast_track_2026-09-27/PRE_REG_T2.md.

## State on disk - what is partial, what is missing

Already applied in the project:
- Bonferroni-8 per variant (TOM_CORE_BT.md L121, L241, L371, L501)
- Bootstrap CI (iid) per variant (TOM_CORE_BT.md L284-290)
- Holdout period (single) (TOM_CORE_BT.md L20)
- Kappa named in ANGLE_HYPOTHESES.md L234-235
- BH-FDR at q=0.10 named in GOLAS_CD_WEB_2026-09-21.md L40

Named but not applied:
- DSR (ANGLE_ELICITATION_RESEARCH.md L80 cites Bailey & Lopez de Prado 2014)
- Purged K-fold + embargo (GOLAS_CD_WEB_2026-09-21.md L38)
- Pre-registration format (ANGLE_HYPOTHESES.md L77-112)

Not on disk at all:
- DSR computed on the Tom core backtest
- PBO on the 4 variants
- SPA/Reality Check on the 7 setup families
- Romano-Wolf
- BH-FDR across the full subgroup table (only per variant)
- Stationary bootstrap
- Kappa on the provenance verdicts
- CPCV
- Pre-registration for T2

## Ranked by cost (cheapest first)

1. R10 - T2 pre-registration file. One file, no code.
2. R1 - DSR on 4 variants. One function call per variant.
3. R8 - Stationary bootstrap. Replace iid bootstrap in tom_bt.py.
4. R7 - BH-FDR across subgroup tables. Collect p-values, adjust.
5. R9 - Kappa. One more reader, same corpus.
6. R4 - PBO via CSCV. Return matrix per variant.
7. R5 - SPA/Reality Check. Per-trial return series per setup family.
8. R2/R3 - Purged K-fold + CPCV. Requires backtest restructure.
9. R6 - Romano-Wolf. Follows R5.

## References (full citations)

- Bailey, D., & Lopez de Prado, M. (2014). The Deflated Sharpe Ratio.
  Journal of Portfolio Management 40(5), 94-107.
- Bailey, D., Borwein, J., Lopez de Prado, M., & Zhu, Q. (2013). The
  Probability of Backtest Overfitting. Journal of Computational Finance.
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the False Discovery
  Rate. JRSS B 57(1), 289-300.
- Cohen, J. (1960). A Coefficient of Agreement for Nominal Scales.
  Educational and Psychological Measurement 20(1), 37-46.
- Hansen, P. R. (2005). A Test for Superior Predictive Ability. Journal of
  Business and Economic Statistics 23(4), 365-380.
- Lopez de Prado, M. (2018). Advances in Financial Machine Learning.
  Wiley. Chapters 7 (purged CV) and 12 (CPCV).
- Politis, D. N., & Romano, J. P. (1994). The Stationary Bootstrap. JASA
  89(428), 1303-1313.
- Romano, J. P., & Wolf, M. (2005). Stepwise Multiple Testing as Formalized
  Data Snooping. Econometrica 73(4), 1237-1282.
- White, H. (2000). A Reality Check for Data Snooping. Econometrica 68(5),
  1097-1126.

All tagged T1 under playbook.md Part I STEP 2 except where noted.

## Packages verified

- purgedcv (PyPI, scikit-learn compatible)
- vectorbt.pro (native CPCV splitters)
- skfolio (CPCV)
- deflated-sharpe (PyPI, zero dependencies)
- pbo (CRAN)
- sealedge (PyPI, PSR + DSR + SPA + BH-FDR + stationary bootstrap,
  HMAC-sealed holdouts)

## Handoff

Claude: read this file, pick which items to apply. Do not apply all at
once. Ranked by cost suggests starting with R10 (one file, no code) then
R1 (one function call). Each item names exactly what to check and what
proof already exists on disk. If an item cannot be applied for a reason
not listed here, reply in
Dumps/workers/incoming_dsa/ or MyTradingSys/system/CLOUD_INBOX.md so the
next session does not re-request it.

End of note.

---

## R1-R10 RE-TAGGED (Tier | Method quality | Confidence)

R1 DSR. Tier T1 | Method quality: applies to non-normal returns with
sample skew and kurtosis; OOS-agnostic (it corrects a sample statistic).
| Confidence H. Backtest-decides: the correct N of trials from
TOM_CORE_BT.md; without N, DSR is undefined.

R2 Purged K-Fold. Tier T1 | Method quality: preserves temporal order,
removes overlap leakage, requires label horizon definition. | Confidence H.
Backtest-decides: whether tom_bt.py already has a CV split; if it does not,
CPCV is the replacement.

R3 CPCV. Tier T1 | Method quality: N=6, k=2 yields 15 splits and 5 paths
on 4.7 years of 1m BTCUSDT. | Confidence H. Backtest-decides: whether the
single holdout 2026-06-26..2026-09-26 is contaminated as M8 says; if so,
CPCV replaces it.

R4 PBO. Tier T1 | Method quality: requires a return matrix across variants;
S=16 typical. | Confidence H. Backtest-decides: the overfit probability
per variant. A PBO above about 0.5 means the in-sample winner is likely
overfit.

R5 White/Hansen SPA. Tier T1 | Method quality: stationary block bootstrap
over per-trial loss-differentials; handles correlated strategies. |
Confidence H. Backtest-decides: whether any of the 7 setup families has
positive performance under the null that none does.

R6 Romano-Wolf stepwise. Tier T1 | Method quality: more powerful than
Bonferroni under correlated tests. | Confidence H. Backtest-decides: which
specific families survive, not just whether any does.

R7 BH-FDR. Tier T1 | Method quality: controls false discovery proportion
under independence or positive dependence; q=0.10 is the project default
per GOLAS_CD_WEB_2026-09-21.md L40. | Confidence H. Backtest-decides:
which subgroup findings survive q=0.10 across the whole table.

R8 Stationary Bootstrap. Tier T1 | Method quality: preserves temporal
dependence via geometric block lengths; robust to non-stationarity at
boundaries. | Confidence H. Backtest-decides: whether the wider CI still
excludes zero; the direction of the verdict is unlikely to flip.

R9 Cohen's Kappa. Tier T1 (Cohen 1960) | Method quality: agreement beyond
chance; kappa >= 0.6 conventional threshold. | Confidence H.
Backtest-decides: the second reader's verdict list on the 74 provenance
rows; kappa < 0.6 means the audit is reader-dependent.

R10 T2 pre-registration. Tier internal (no external source required) |
Method quality: format exists at ANGLE_HYPOTHESES.md L77-112. |
Confidence H. Backtest-decides: the pre-declared metric and threshold; if
the T2 result does not move WAIT_RR below the declared value, the T2
ruling is falsified.

---

## UNVERIFIED-WEB LIST

UPDATE 2026-10-01 (MTS-2026-10-01-1604Z-CLD-ANA-revalidate-tom-fabio, ACTIONS W1): per-line status below; all 9 papers remain UNVERIFIED-WEB (egress blocked),
three packages opened on PyPI, sealedge's "DSR" claim rejected.

Every citation below was UNVERIFIED-WEB as of the first pass. None was opened,
searched, or matched against an abstract from this surface. Verification
requires a surface that can reach the source: paste title, authors, venue,
year, DOI or URL, and abstract match.

Papers:
1. Bailey & Lopez de Prado (2014), "The Deflated Sharpe Ratio". Journal of
   Portfolio Management 40(5), 94-107. UNVERIFIED-WEB - cloud egress blocked 2026-10-01, requires desktop.
2. Bailey, Borwein, Lopez de Prado, Zhu (2013), "The Probability of
   Backtest Overfitting". Journal of Computational Finance. UNVERIFIED-WEB - cloud egress blocked 2026-10-01, requires desktop. Year check needed: 2013 may be the SSRN date, not the journal date (recollection only).
3. Benjamini & Hochberg (1995), "Controlling the False Discovery Rate".
   JRSS B 57(1), 289-300. UNVERIFIED-WEB - cloud egress blocked 2026-10-01, requires desktop.
4. Cohen (1960), "A Coefficient of Agreement for Nominal Scales".
   Educational and Psychological Measurement 20(1), 37-46.
   UNVERIFIED-WEB - cloud egress blocked 2026-10-01, requires desktop.
5. Hansen (2005), "A Test for Superior Predictive Ability". Journal of
   Business and Economic Statistics 23(4), 365-380. UNVERIFIED-WEB - cloud egress blocked 2026-10-01, requires desktop.
6. Lopez de Prado (2018), "Advances in Financial Machine Learning". Wiley.
   UNVERIFIED-WEB - cloud egress blocked 2026-10-01, requires desktop. Textbook, not a peer-reviewed journal; T1 tag flagged for the operator.
7. Politis & Romano (1994), "The Stationary Bootstrap". JASA 89(428),
   1303-1313. UNVERIFIED-WEB - cloud egress blocked 2026-10-01, requires desktop.
8. Romano & Wolf (2005), "Stepwise Multiple Testing as Formalized Data
   Snooping". Econometrica 73(4), 1237-1282. UNVERIFIED-WEB - cloud egress blocked 2026-10-01, requires desktop.
9. White (2000), "A Reality Check for Data Snooping". Econometrica 68(5),
   1097-1126. UNVERIFIED-WEB - cloud egress blocked 2026-10-01, requires desktop.

Packages:
1. purgedcv (PyPI). VERIFIED 2026-10-01 https://pypi.org/pypi/purgedcv/json (existence, summary, MIT, Alpha, 23 releases in 4.5 months; algorithm not tested). Tag T3 | unknown | M.
2. vectorbt.pro (native CPCV splitters). UNVERIFIED-WEB - cloud egress blocked 2026-10-01, requires desktop. (PyPI returns 404; consistent with private distribution, recollection only.)
3. skfolio (CPCV). VERIFIED 2026-10-01 https://pypi.org/pypi/skfolio/json (README lists CombinatorialPurgedCV). Tag T3 | docs only | M.
4. deflated-sharpe (PyPI, claimed zero dependencies). VERIFIED 2026-10-01 https://pypi.org/pypi/deflated-sharpe/json (v0.1.0, Apache-2.0; scipy is optional, so zero required dependencies holds). DEFECT: docstring says annualized SR but the SE is per-period, README example inflates z to 16.49; use per-period SR only. Tag T3 | formula matches Gaussian DSR | M.
5. pbo (CRAN). UNVERIFIED-WEB - cloud egress blocked 2026-10-01, requires desktop.
6. sealedge (PyPI, claimed PSR + DSR + SPA + BH-FDR + stationary bootstrap
   + HMAC-sealed holdouts). VERIFIED 2026-10-01 https://pypi.org/pypi/sealedge/json (existence only; the claimed "DSR" is REJECTED as unsupported): v0.5.1, first release 2026-07-02, GPL-3.0); README lists PSR, SPA, BH-FDR, stationary bootstrap, HMAC; "DSR" NOT in the README, claim unsupported; Hansen-literal SPA is opt-in, default path lacks the cross-strategy max. Tag T3 | README only | M.

Adjacent references used in R5 and R7 evidence sections (KOSPI200 futures
application, tickfloor 517-strategy study, KCI cryptocurrency DRL CPCV
application). REJECT 2026-10-01 as evidence: cannot be opened, no author/venue/date given (tickfloor: 404 on PyPI). Orientation only.

## REJECT LIST (playbook Part I STEP 3c, listed once, not researched again)

- Any application claims attributed to the papers above (KOSPI200 numeric
  results, tickfloor q-value 0.1196, KCI max-drawdown finding) are
  UNVERIFIED-WEB. They illustrate the method; they are not evidence for
  this project. Use for orientation only. Do not cite as proof.

## "OUR BACKTEST DECIDES" (playbook Part I STEP 3e)

For every method in this note, adoption requires a run on this repository's
own data. None of the ten methods is adopted because a paper names it.
Adoption is per method, per application, on the artifact named in the
"Backtest-decides" line of each R-item.

## FORMULAS.md

No formula from this note is committed to backtest/layers/FORMULAS.md yet.
Canonical definition plus verified source is required first; UNVERIFIED-WEB
sources do not qualify. DSR and BH-FDR are the two most likely first
entries once verified.

End of D1 addendum.
