# REVALIDATION ACTIONS 2026-10-01 (W1-W8)

Session: MTS-2026-10-01-1604Z-CLD-ANA-revalidate-tom-fabio (surface CLD, role ANA, branch_alias claude/focused-faraday-xnxqms)
Reader: one reader per item (this session). No second reader, no subagent (budget row >=85% assumed, SURFACE_POLICY.md:33).
Machine for every RESULT line: cloud container, linux 6.18.44, date 2026-10-01, repo at origin/main 46e8c9c.

Tag convention (STEP 6): each sentence ends with its own tag. `[disk: path:line]` = file in the repo; `[T/<id>:<line>@<char>]` = raw
transcript, char offset inside that line; `[web: URL]` = an opened web page; `[run: ...]` = a command this session ran and saw.
Rule claims carry TOM-NNN, CT-NNN, SCREENER, or NO-SOURCE. Where a new transcript passage supports a rule that has no
TOM-NNN yet, the tag is NO-SOURCE (candidate source named); no TOM id is invented, the supervisor assigns it.
Label rule (LESSONS_LEARNED.md:14): EXPECT = prediction, RESULT = what was seen. Where an EXPECT was written after a probe,
the line says so.

## 0. Meta-research (STEP 2, written once, before any source work)

Research questions of this session and what would settle each:

Q1 Are the cited papers and packages real and do they say what the request says? Settled by opening the source and matching title,
authors, venue, year (papers) or name, version, summary, license (packages); a package's algorithm is a separate question settled
only by reading its source against the paper. No statistical test applies; the unit of evidence is one opened page per citation.

Q2 What is the number of independent trials N for a deflated Sharpe ratio on the Tom core backtest? DSR needs N as the count of
configurations a fair observer would have to try to find the reported result, including unrecorded ones; it cannot be a table
row count. Settled by (a) counting distinct signal sets and (b) showing whether the verdict moves across the plausible N range.
The true N including design history is "unvalidated domain" for the part not on disk; that sub-item stops at a stated lower bound.

Q3 Are the 74 provenance verdicts reproducible by a second reader? Evidence: a second reader who has NOT seen the first list
re-derives each verdict from the rule text and the corpus; Cohen's kappa on 74 nominal labels with 4 categories, threshold 0.6.
Blindness is the validity condition; a reader who saw the first list gives an upward-biased kappa that must not be reported as kappa.

Q4 Does a wider search than the audit used find a Tom source for the top-5 NO-SOURCE items? Evidence: exhaustive term search over
the whole raw corpus (102 files), broad terms first, each hit read in context; a hit counts only if it states the value or the role.
No horizon, OOS or cost question applies (this is a text question). Absence of a hit after the broad search is a PASS, not a proof.

Q5 Do the unaudited fields (section 10) have a Tom quote? Same evidence as Q4, one search per field name plus synonyms.

Q6 What is the provenance profile of the Fabio v3.1 parameters? Evidence: per row, exact-substring check of each quoted passage in
the named transcript, then classification with the Tom definitions. No accepted method exists for comparing two traders'
provenance counts as a measure of strategy quality, so any "Fabio is better sourced than Tom" statement is "unvalidated domain" and is not made.

Q7 In which order should the backtest instruments be fixed so that "our backtest decides" is a valid gate? Evidence: a defect list
with a causal path from each defect to the verdict (H2 null, M8 holdout, M9 trial count, M7 CI width). Accepted methods exist
(like-for-like null, purged/embargoed holdout, trial registry, block bootstrap); the ordering itself is a judgement and is labelled so.

Q8 What must a pre-registration for the T2 R:R window decision contain? Evidence: metric, threshold, decision rule, stopping condition
fixed and committed before the T2 run, costs included (Deribit maker/taker per sim.py, funding and slippage as in stress rows).
Whether any particular R:R window is "right" is NOT answerable by backtest under the provenance rule (CLAUDE.md Provenance): the
backtest can only measure counts and net R of a Tom-sourced option. That sub-item is "unvalidated domain" and stops there.

Q9 Does EXTRACTION_METHOD_V2 recover more than V1 (order of events, "as long as" conditions, rejects)? Evidence: per claim yes/no
against the transcript on a small sample (2 videos). No accepted method exists for generalising extraction quality from n=2
videos; the comparison is descriptive and the generalisation is "unvalidated domain".

Q10 Do new V2 extracts contain claims the corpus contradicts? Evidence: for each claimed rule, a search of all 102 transcripts for
a contradicting passage; counts only. No statistical test; counts are descriptive.

Q11 Are the new extracts reproducible by a second reader (kappa >= 0.6)? Same validity condition as Q3. The extractor cannot be its own
second reader; see 5.4 in EXTRACTION_ROUND2_2026-10-01.md.

## 1. Source tiers (STEP 3, fixed before any search; not changed afterwards)

| tier | definition | may justify |
|---|---|---|
| T1 | peer-reviewed journal; NBER/Fed/BIS working paper; regulated institution with disclosed method | core rules |
| T2 | preprint with disclosed method; exchange docs; replicated practitioner study with full method | adaptation |
| T3 | practitioner content, blogs, vendor docs, software packages | ideas and definitions only |
| REJECT | marketing, no author, no date, no method, or cannot be opened | nothing |

Applied here: a paper that cannot be opened is UNVERIFIED-WEB, and carries "T1-if-verified" only as a pointer, never as a tier.
A software package is T3 (its page is vendor documentation) however well its README cites a T1 paper.

## W1. Citation verification

EXPECT (written after one probe of doi.org returned 403, so not blind): the 9 papers cannot be opened from this container; the PyPI
packages can. Egress probes this session [run: curl through the agent proxy]: pypi.org 200 for purgedcv, skfolio, deflated-sharpe,
sealedge; 404 for vectorbt.pro and tickfloor; doi.org: CONNECT refused, 403 (organization policy); github.com: 403; HTTP 000 (connection failed through the same proxy; the refusal text was filtered out of the output, so the reason is not shown) for api.crossref.org,
search.crossref.org, cran.r-project.org, en.wikipedia.org, arxiv.org, papers.ssrn.com, www.jstor.org, onlinelibrary.wiley.com,
scholar.google.com. Denials were not retried.

RESULT (2026-10-01, cloud container). Tag = Tier | Method quality | Confidence. Confidence is L for every unopened source.

| # | citation (as in REVALIDATION_REQUEST UNVERIFIED-WEB list) | status | tag |
|---|---|---|---|
| P1 | Bailey & Lopez de Prado (2014), The Deflated Sharpe Ratio, JPM 40(5) 94-107 | UNVERIFIED-WEB - cloud egress blocked 2026-10-01, requires desktop | T1-if-verified / corrects trial count and non-normality, sample-statistic, needs N / L |
| P2 | Bailey, Borwein, Lopez de Prado, Zhu (2013), The Probability of Backtest Overfitting, J. Comput. Finance | UNVERIFIED-WEB - cloud egress blocked 2026-10-01, requires desktop. Check the year: the request writes 2013 with no volume; recollection (not an opening) says 2013 is the SSRN date and the journal date is later | T1-if-verified / needs a return matrix over variants / L |
| P3 | Benjamini & Hochberg (1995), Controlling the FDR, JRSS B 57(1) 289-300 | UNVERIFIED-WEB - cloud egress blocked 2026-10-01, requires desktop | T1-if-verified / independence or positive dependence assumed / L |
| P4 | Cohen (1960), A Coefficient of Agreement for Nominal Scales, EPM 20(1) 37-46 | UNVERIFIED-WEB - cloud egress blocked 2026-10-01, requires desktop | T1-if-verified / nominal labels, two raters / L |
| P5 | Hansen (2005), A Test for Superior Predictive Ability, JBES 23(4) 365-380 | UNVERIFIED-WEB - cloud egress blocked 2026-10-01, requires desktop | T1-if-verified / bootstrap over loss differentials / L |
| P6 | Lopez de Prado (2018), Advances in Financial Machine Learning, Wiley (ch.7 purged CV, ch.12 CPCV) | UNVERIFIED-WEB - cloud egress blocked 2026-10-01, requires desktop. Textbook, not peer-reviewed in the T1 sense of the tier table; stays T1-if-verified only because the tier table lists journals and the request tagged it T1; flagged for the operator | T1?-if-verified (book) / purge+embargo+CPCV described / L |
| P7 | Politis & Romano (1994), The Stationary Bootstrap, JASA 89(428) 1303-1313 | UNVERIFIED-WEB - cloud egress blocked 2026-10-01, requires desktop | T1-if-verified / geometric block lengths, stationary series / L |
| P8 | Romano & Wolf (2005), Stepwise Multiple Testing as Formalized Data Snooping, Econometrica 73(4) 1237-1282 | UNVERIFIED-WEB - cloud egress blocked 2026-10-01, requires desktop | T1-if-verified / stepwise FWER control / L |
| P9 | White (2000), A Reality Check for Data Snooping, Econometrica 68(5) 1097-1126 | UNVERIFIED-WEB - cloud egress blocked 2026-10-01, requires desktop | T1-if-verified / bootstrap max over K strategies / L |

Recall note (NOT verification, never counts): the volume/page/year strings for P1, P3-P5, P7-P9 match what I remember; P2 does not
match cleanly (year). No VERIFIED mark is given for any paper.

| # | package | status | tag |
|---|---|---|---|
| K1 | purgedcv (PyPI) | VERIFIED 2026-10-01 https://pypi.org/pypi/purgedcv/json (existence and summary only). Name purgedcv, author Evgenii Lazarev, MIT, Python >=3.10, "Development Status :: 3 - Alpha", 23 releases since 2026-05-16, page version 0.1.10, at least one release on 2026-10-01 (today). Summary lists purging, embargoes, combinatorial purged CV, deflated Sharpe ratios; README mentions scikit-learn use. Correctness of its CPCV was not tested. Pin a version before any use. | T3 / unknown (alpha, one author, no OOS evidence offered) / M |
| K2 | vectorbt.pro (native CPCV splitters) | UNVERIFIED-WEB - cloud egress blocked 2026-10-01, requires desktop. pypi.org/pypi/vectorbt.pro/json returned 404 (consistent with private distribution, recollection only). | T3 / unknown / L |
| K3 | skfolio (CPCV) | VERIFIED 2026-10-01 https://pypi.org/pypi/skfolio/json. Name skfolio, author Hugo Delatte, BSD-3-Clause, 90 releases since 2023-12-14, page version 1.4.10; README lists Combinatorial Purged Cross-Validation and a CombinatorialPurgedCV class. | T3 / library docs, no backtest claims tested / M |
| K4 | deflated-sharpe (PyPI, "zero dependencies") | VERIFIED 2026-10-01 https://pypi.org/pypi/deflated-sharpe/json (existence, version 0.1.0 released 2026-03-21, Apache-2.0, vendor Mnemox AI). "Zero dependencies" is true for required dependencies: scipy is an optional extra only. I installed it and read the source [run: pip install deflated-sharpe; inspect.getsource]. Defect found: the docstring says observed_sr is annualized but the standard error uses 1/(num_obs-1) per-period scaling, so the README example (SR 2.0, 252 obs, 1000 trials) returns z=16.49 [run], an inflated figure from mixed units. Usable only with a per-period SR. | T3 / formula matches the DSR form for Gaussian returns (checked against my own computation, W2) but unit-inconsistent API / M |
| K5 | pbo (CRAN) | UNVERIFIED-WEB - cloud egress blocked 2026-10-01, requires desktop (cran.r-project.org refused) | T3 / unknown / L |
| K6 | sealedge (PyPI; "PSR + DSR + SPA + BH-FDR + stationary bootstrap + HMAC-sealed holdouts") | VERIFIED 2026-10-01 https://pypi.org/pypi/sealedge/json (existence only); the claimed "DSR" is REJECT (unsupported). Package exists, v0.5.1 released 2026-07-12, first release 2026-07-02 (about 10 days of history), author Hansen Winarto, GPL-3.0-or-later, 8 required dependencies. The README lists PSR+ESS, Bonferroni and BH-FDR, SPA, stationary block bootstrap, HMAC holdouts; the string "DSR"/"Deflated" does not occur in the README text served by PyPI [run: regex over info.description], so "DSR" in the request is not supported. The Hansen-literal SPA (cross-strategy max, Eq.7/Eq.8) is opt-in (`recenter_policy="hansen_literal"`); the default is a legacy circular-permutation null that the README itself says lacks the cross-strategy max, which the request did not mention. | T3 / README only, no source audit / M |

Adjacent items in the request (KOSPI200 futures study, tickfloor 517-strategy study, KCI cryptocurrency DRL CPCV study): REJECT as
evidence (cannot be opened; no author/venue/date in the request; tickfloor 404 on PyPI). The request already says orientation only.

Disk-reference check of the request itself (bonus, cheap): [run: sed and grep on the cited lines]
- GOLAS_CD_WEB_2026-09-21.md L38 (purged K-fold, T1) and L40 (BH FDR q=0.10): match. [disk: MyTradingSys/research/_archive/loose_2026-10/GOLAS_CD_WEB_2026-09-21.md:38]
- BACKTEST_METHOD_2026-09-21.md L35 (pre-register <=5, FDR q=0.10, UNVERIFIED-WEB): matches. [disk: MyTradingSys/research/_archive/loose_2026-10/BACKTEST_METHOD_2026-09-21.md:35]
- ANGLE_HYPOTHESES.md L234-235 (kappa): matches. [disk: MyTradingSys/research/fast_track_2026-09-27/ANGLE_HYPOTHESES.md:235]
- ANGLE_ELICITATION_RESEARCH.md L80 (DSR cited): matches. [disk: MyTradingSys/research/fast_track_2026-09-27/ANGLE_ELICITATION_RESEARCH.md:80]
- TOM_CORE_BT.md L20 (single holdout), L121/L241/L371/L501 (Bonferroni-8 headings), L530 (DSR/PBO note): match. [disk: TOM_CORE_BT.md:20,121,241,371,501,530]
- R8 cites "TOM_CORE_BT.md L284-290 (2000 iid draws)": WRONG FILE. Those lines in TOM_CORE_BT.md are a results table; the bootstrap is
  `backtest/tom_bt.py:283-289` (`boot_ci`, n_boot=2000, `rng.choices` iid resample). [disk: MyTradingSys/backtest/tom_bt.py:283]
- R6 says Romano-Wolf is "already referenced in T055a_POSITIONING_FLOW.md": NOT FOUND. A grep for "romano" over all .md and .py files hits
  only HANDOFF_FOR_CLAUDE_2026-10-01.md, REVALIDATION_REQUEST_2026-10-01.md and 03_FILE_INDEX.md. [run: grep -rIl -i romano]

Gate: no citation enters FORMULAS.md. Nothing was added to FORMULAS.md by this session.

## W2. DSR trial count

EXPECT: N is between 3 and 16 depending on basis, and DSR significance does not depend on N because the two variants with n >= 100
have negative mean net R [disk: TOM_CORE_BT.md:275,405].

RESULT (2026-10-01, cloud container). Counted by script over the report text [run: python, section split at "## 2.n" headings].
1. Registry rows stated: 16 [disk: TOM_CORE_BT.md:3]; the review says they are 4 variants x 4 stress configs, "not independent trials" [disk: TOM_CORE_BT_REVIEW_2026-09-30.md:93]. The file `bt_runs/TRIAL_REGISTRY.csv` is not in git (no match in `git ls-files`), so 16 cannot be re-counted here. [run: git ls-files | grep -i TRIAL_REGISTRY -> empty]
2. Variants `episode` and `A` are the same result: the bodies of sections 2.1 and 2.2 are identical after the three header lines (script printed True); the only difference is the one-line description. [disk: TOM_CORE_BT.md:23-141 vs 143-261] Count: 1 trial, not 2.
3. Stress config `target_first` equals `base` in all four variants (script printed True four times). [disk: TOM_CORE_BT.md:93,213,340,470] The review calls it "vacuous". [disk: TOM_CORE_BT_REVIEW_2026-09-30.md:68] `all_taker_0.05` and `slip_5bps` use the same entries and exits with a different cost model (same n signals, same n filled in each table). They are re-pricings of one signal set.
4. Distinct signal sets: 3, nested on one parameter (proof count >= 5, >= 4, >= 3). [disk: TOM_CORE_BT.md:25,265,395] The proof>=4 and proof>=3 variants were added after the live rule gave n=17, i.e. post hoc. [disk: TOM_CORE_BT_REVIEW_2026-09-30.md:87]
5. The registry dedupes by run_id = date, so a same-day re-run adds no row; 16 is therefore a floor on rows, not a count of trials. [disk: TOM_CORE_BT_REVIEW_2026-09-30.md:90]
6. Design history before this run (distance caps, the 2.0-3.5R window, the floor, proof thresholds) was chosen "after seeing data". [disk: TOM_CORE_BT_REVIEW_2026-09-30.md:86] None of it is counted anywhere on disk. N including it is "unvalidated domain" from disk alone.

N and basis, one line for the addendum to R1:
**N = 3 (distinct signal sets on one nested threshold, episode and A merged, stress configs are re-pricings), lower bound; registry row count 16 is the upper bound that can be read from disk; the true N including undocumented design iterations is not on disk.**

DSR sensitivity (computed this session, approximate). Per-trade Sharpe = mean R / sd, sd back-derived from the reported 95% CI half-width
(bootstrap iid, which the review says is too narrow, M7); Gaussian standard error; skew and kurtosis are not on disk so they are
set to the Gaussian values. Probability that the true SR exceeds the N-trial expected maximum (higher = better; 0.95 needed):

| variant | kind | n filled | mean R | SR/trade | N=1 | N=3 | N=16 | N=100 | source |
|---|---|---|---|---|---|---|---|---|---|
| episode (=A) | gross | 17 | +0.04 | +0.032 | 0.550 | 0.234 | 0.047 | 0.008 | [disk: TOM_CORE_BT.md:34] |
| episode (=A) | net | 17 | -0.19 | -0.148 | 0.278 | 0.075 | 0.008 | 0.001 | [disk: TOM_CORE_BT.md:34] |
| watch_episode | gross | 4417 | -0.07 | -0.052 | 0.000 | 0.000 | 0.000 | 0.000 | [disk: TOM_CORE_BT.md:275] |
| watch_episode | net | 4417 | -0.30 | -0.197 | 0.000 | 0.000 | 0.000 | 0.000 | [disk: TOM_CORE_BT.md:275] |
| p4_episode | gross | 902 | -0.01 | -0.007 | 0.414 | 0.142 | 0.022 | 0.003 | [disk: TOM_CORE_BT.md:405] |
| p4_episode | net | 902 | -0.24 | -0.165 | 0.000 | 0.000 | 0.000 | 0.000 | [disk: TOM_CORE_BT.md:405] |

Cross-check with the deflated-sharpe package on the same inputs [run: deflated_sharpe_ratio(sr, N, n)]: p-values 0.449 (episode gross, N=1) to
1.000, i.e. 1-0.550 = 0.450 for N=1 matches my table; at N=16 the package gives p=0.930 where I get 0.953 (it uses the Gumbel asymptotic
for the expected maximum, I used the Bailey-Lopez de Prado expression); same conclusion. Package units caveat in K4.

Finding: no variant reaches 0.95 at any N from 1 to 100. The highest value is 0.55 (episode gross, N=1, n=17), and n=17 is below the
protocol floor of 100 trades. [disk: TOM_CORE_BT.md:20] "DSR p < 0.05 after correction" is not achieved for any variant, and the answer does not depend on N.
The two variants with n >= 100 have negative mean net R with CIs that exclude 0 on the negative side. [disk: TOM_CORE_BT.md:275,405]
Caveat: the gross and net rows rest on the review's defects H1 (live rule untested), H2 (null not like-for-like), M1-M5 (optimistic fills).
[disk: TOM_CORE_BT_REVIEW_2026-09-30.md:20-69] A DSR on a defective instrument bounds nothing; it only shows N is not what decides.

## W3. Kappa, second reader on the 74 provenance verdicts

EXPECT: kappa can be measured by a blind re-derivation, and lands somewhere between 0.4 and 0.8.

RESULT (2026-10-01, cloud container): **NOT DONE as specified. Kappa was not computed and no kappa number is reported.**
Why: the blind condition failed in this session. The verdict, the Tom-source cell and the impact cell sit in the same table row as the rule text
in sections 2-6 [disk: PROVENANCE_AUDIT_TOM.md:21-116], and this session read those tables in one pass before deriving anything. A second reading
after that is not blind, and an agreement figure from it would be biased upward and would read as a kappa (the pattern of LESSONS_LEARNED.md:14).
Disagreeing rows: none can be listed. Threshold 0.6: not tested. The question "is the headline 36 NO-SOURCE reader-dependent" stays open.

What was done instead (three items, none of them a kappa):
1. Mechanical recount of the first reader's headline. Parsed the rows A01-K02 by script: 74 rows; TOM-SOURCED 2, TOM-CONCEPT-ONLY 33, NO-SOURCE 36,
   DATA-PLUMBING 3 [run: python Counter over the table rows]. This equals section 1. [disk: PROVENANCE_AUDIT_TOM.md:9-15] Every CONCEPT-ONLY row appears in section 9 (0 missing) [run].
2. Definition-consistency check (non-blind, reader-biased, Confidence L). The audit's own definition puts a role "veto, gate, cap" that Tom never gives into NO-SOURCE. [disk: PROVENANCE_AUDIT_TOM.md:5]
   Two rows are vetoes and are labelled CONCEPT-ONLY: B03 (finished-auction direction veto) and V04 (broken-value veto, whose own Tom-source cell says "no veto").
   [disk: PROVENANCE_AUDIT_TOM.md:93,106] If both are reclassified the tally becomes NO-SOURCE 38, CONCEPT-ONLY 31. Arguable but not reclassified: A20/A26 (POC-side gating, "No POC-side gating" in the Tom cell),
   A23 (CVD-flat term), A25 (state blocks). [disk: PROVENANCE_AUDIT_TOM.md:42,45,47,48]
3. Blind packet for a clean reader: the 74 rows with the Tom-source, verdict and impact columns removed, definitions, reader conditions, and an `id,verdict` CSV protocol
   [disk: MyTradingSys/research/fast_track_2026-09-27/W3_BLIND_PACKET_2026-10-01.md]. Kappa calculator with a self-test [disk: scripts/dev/kappa_check.py]; `--selftest` printed PASS and a two-row
   case returned kappa 0.000 with exit code 1 [run]. The reader must be a session that has not opened PROVENANCE_AUDIT_TOM.md or the 2026-10-01 handoff notes.

Next step (operator): run a clean Sonnet or Haiku surface on the packet; the 74 first-reader labels go in as `first.csv` from section 2-6.

## W4. Falsification-first re-search of the top five NO-SOURCE items

Search method (all 102 files in raw_transcripts_canonical, sentence-level regex, each hit read in context; a hit counts only if it states the value or the role):
broad terms first as ordered. Counts [run: python sentence search over the whole corpus]:
- risk/reward/ratio phrases with a number or "minimum/at least": 35 sentences in 17 files.
- "minimum / at least / no less than / never take" near risk, reward, ratio or target: 5 sentences in 5 files (one relevant, see rank 2).
- "window, band, bands, ceiling, veto, gate, floor, cap, capped, maximum, at most, no more than": 54 sentences in 22 files, none about a trade rule (Bollinger bands, trading floors, drawdown maxima, "rubber band").
- stop with percent/ticks/points/tight/wide/close/distance/minimum: 29 sentences in 17 files.
- proof/confirmation/confluence/checklist/criteria with a count word: 19 + 6 sentences in 10 + 5 files.
Starred ids below are in the Tom set (57 ids from extracts/fresh, extracts/processed/tom and TOM_VERBATIM_INDEX); unstarred are speaker-unconfirmed and are not used as Tom evidence.

EXPECT (rank 1-5): PASS on all five, because the audit searched 59 transcripts and quoted 51 passages.

**Rank 1 - target window 2.0-3.5R, nearest-level pick (A08, A09, A10). RESULT: CORRECTION (partial, A08 only); A09 and A10 stand.**
- A08 (minimum 2.0x stop): new passage, Tom says an average R:R "of a good 2 2.5 as a rule" for trend-following pullback trades: "Is exactly an average risk-reward ratio of a good 2 2.5 as a rule." [T/UOBgXV20yCM:7@3750]
  The same video states a trade planned "exactly three". [T/UOBgXV20yCM:7@3986] This is an average outcome, not a per-trade minimum, and the sentence is ASR-garbled ("Is exactly"). This passage is already in the V1 extract [disk: extracts/fresh/extract_UOBgXV20yCM_fresh.md:85-92] but PROVENANCE_AUDIT_TOM.md does not cite it. Reclassify A08 NO-SOURCE -> TOM-CONCEPT-ONLY at best (idea: average 2-2.5; the 2.0 gate role is ours). Tag: NO-SOURCE for the gate role; candidate source named, no TOM-NNN assigned. Confidence L.
- A09 (maximum 3.5x stop): no cap anywhere. Tom states larger ratios: "about 6 to1" [T/k0zm5NYn0IQ:19@7179], "riskreward ratio of seven" [T/3o1VVsfBmmU:19@5751], 12 ticks risk and 97 ticks profit, which is 8.08 by arithmetic [T/yRvMW6lgN1o:19@8864]. NO-SOURCE stands; the cap is contradicted by his own examples. Confidence H.
- A10 (nearest level inside the window, else drop): Tom names "the next high volume price" as target [T/qLnQan0KGmQ:19@7547], no window. NO-SOURCE stands. Confidence H.

**Rank 2 - net R:R >= 2.0 after the flat 25 percent, cited to qLnQan0KGmQ (A13, A12). RESULT: PASS (NO-SOURCE stands); two additional findings.**
- The cited video has no 2:1, minimum, net, fee or percent: the only "at least" is about volatility ("At least if you're looking for trades that last a few days longer") and the only "twice" is "proof twice" [run: regex over the full text of qLnQan0KGmQ]. The miscitation is confirmed. [disk: PROVENANCE_AUDIT_TOM.md:35]
- Contradicting evidence (not in the V1 extract of that video: grep for 1.5 in extract_k0zm5NYn0IQ_fresh.md returned no match [run]): Tom's minimum depends on hit rate and is lower than 2.0 net for counter-trading: "with such counter trading strategies, then you need at least a riskreward ratio of 1.5." [T/k0zm5NYn0IQ:19@19400] (hit rate 40 to 45 percent in the preceding words).
- Side finding on A11 (gross >= 1.5, audit rank 14): the 1.5 value appears in that passage, conditioned on a 40-45 percent hit rate and counter-trading, with no gross/net split. Reclassify A11 NO-SOURCE -> TOM-CONCEPT-ONLY (conditional value). K02 ("Tom never lowers R:R minimum") stays NO-SOURCE: the passage shows the minimum moving with hit rate. Confidence M.
  Effect on the rank-2 action: the replacement for the fixed net 2.0 gate is the hit-rate-conditioned minimum (Q05 plus this passage), not a constant.

**Rank 3 - 0.1 percent stop floor reset to 0.2 percent (A03). RESULT: PASS (no source).** Tom's stop widths are in ticks or points: 12 ticks [T/yRvMW6lgN1o:19@8864], "stop loss is suddenly only 20 points wide" [T/BVpYGKz9PBU:19@13012], "stop-loss of 20 points in the DAX" [T/k0zm5NYn0IQ:19@845]; and qualitative: "really tight" [T/4MoNjEQ2Dd8:19@16272], "can be set much tighter depending on the setup" [T/BVpYGKz9PBU:19@11625]. No percentage, no minimum stop.
The only opposing passage ("you should actually avoid setting such a tight stop", cBkwYjn-6mM) is in a guest interview, speaker not in the Tom set, about discretionary exits; excluded. A percent equivalent of 20 DAX points was not computed: no index level is stated. Confidence H.

**Rank 4 - 0.2 percent fallback stop when no swing lies beyond the zone (A04, M11). RESULT: PASS (no source).** Same searches: Tom places stops at structure ("below the last liquidity" [disk: PROVENANCE_AUDIT_TOM.md:208 Q07]), never a fixed percent fallback, and no passage says what he does when no swing exists. Confidence H.

**Rank 5 - proof bands 3 and 5 of 7 (V02). RESULT: PASS (no source).** "Proof" is one qualitative event: "And you always need two things, the idea and the proof." [T/qLnQan0KGmQ:19@7726]; "you can also wait until the proof arrives" [T/qLnQan0KGmQ:19@4652]; "The proof is always the setup that I expect to see there." [T/NkQeOVDTAec:19@8280]. No count, no weighting, no band anywhere in the criteria/confirmation search. Confidence H.

Gate result: one new source on rank 1 (A08, average, low confidence) and one on rank 2's neighbour (A11). Neither changes "the target window and net gate have no per-trade source"; both change the replacement: use the hit-rate-conditioned minimum (Q05 and the 1.5 passage) and Tom's own R:R spread (about 2.4 to 8) instead of a 2.0-3.5 window.

## W5. Section 10 fields check

EXPECT: no quote for open interest, funding or the data-adapter items; concept-level quotes for session timing, liquidation, FVG, naked POC.
RESULT (2026-10-01, cloud container; one search per field name plus synonyms over all 102 files; starred = Tom set):
1. open interest: none. Zero sentences match "open interest" or "OI" in 102 files. [run]
2. funding: none. Zero sentences match "funding". [run]
3. session timing: concept only, no numbers. "So now I've carefully prepared these four markets for the US session" [T/-dMWA_bbm3o:7@5854] and the opening read: "Does the market opening, the trading opening at cash time perhaps give me further clues that help me plan the market correctly?" [T/Ld1dhjGdTCA:19@2957]. No UTC time, no 390-minute window, no day gate.
4. liquidation: concept only. "This means that large liquidations have simply taken place and as a result the market participants are exhausted." [T/sQ_biBKhPVU:19@7457] Context is exhaustion at extremes; no liquidation data field, no threshold.
5. alignment check: concept only (higher-timeframe alignment). "This ensures you are always aligned with the bigger picture." [T/WQ_OAdz-PJ8:9@10470] No quote about an alignment check between flow and price beyond Q37/Q21 already in the audit.
6. FvgCalculator: quote found, already in the audit as Q27 (A28). "When can you use such fair value gaps as counter trading ideas?" [T/3JqMyzE8jIQ:13@2331] Nothing new.
7. NakedPocTracker: quote found, already Q42 (A29). "I can analyze naked PC's for myself." [T/YopZ5ZDmMFw:13@6165] New and speaker-unconfirmed: "A naked POC isn't an edge in itself" [T/ODdF0Bn_KSc:7@6525], which says a naked POC is not a setup by itself; relevant to A29 (naked POC zones) if the speaker is Tom.
8. ArchiveHistoricalSource: none, and none expected: it is a data adapter (gitignored), no trading meaning. No Tom quote about historical data feeds.
9. state_code / quad_classify: none for the field. quad_classify is a price x CVD x OI quadrant classifier. [disk: MyTradingSys/runtime/quad_classify.py:1] Tom's "four-quadrant model" is a capital-flow / strategy-selection model, a different object with the same word: "The third building block we like to use at Trade to Traders is the approach using the four-quadrant model" [T/pgdmKLJ0hhA:7@1187]. Name collision, no support. state_code letters: no quote.
Gate: no field yields a quote carrying a number. Five of nine yield concept-level quotes (items 3-7); two of those (6, 7) were already in the audit. The 36 count does not change because these fields are not among the 74 rows; what changes is coverage: 9 fields unaudited, 5 with concept-level Tom text, none with a threshold.

## W6. Fabio provenance audit

EXPECT: most of the 41 rows are CONCEPT-ONLY or NO-SOURCE, as for Tom, and the quotes are verbatim.
RESULT (2026-10-01, cloud container): file written [disk: MyTradingSys/research/_archive/loose_2026-10/FABIO_PROVENANCE_AUDIT_2026-10-01.md]. Counted by script over the 41 table rows [disk: FABIO_V3_SPEC.md:192-232].
Quotes: 39 quoted passages across 34 rows, 39 found verbatim (normalised substring) in the named transcripts, 0 missing; 7 rows have no quote. [run]
By the spec's labels: SOURCED 14, CONCEPT-ONLY 19, NO-SOURCE 7, DATA-PLUMBING 1 (total 41). Strict, Tom-equivalent reading (rows keyed on proxy-detected events move to CONCEPT-ONLY): SOURCED 7, CONCEPT-ONLY 26, NO-SOURCE 7, DATA-PLUMBING 1.
NO-SOURCE rows: P25, P29, P30, P31, P34, P35, P39; P29 and P30 are SAFETY-labelled and exempt by direct operator approval [disk: SUPERVISOR_INBOX.md:15], leaving 5 binding.
25 of 41 rows carry an NS-grid or NS-fixed number; the spec registers 139 NY grid cells (151 with stage 3) over NS-grid values [disk: FABIO_V3_SPEC.md:245-246], which tunes unsourced numbers against the Provenance rule. Operator decision.
Single reader; no kappa. No Fabio-versus-Tom quality comparison is made (unvalidated domain, row granularity differs).

## W7. Backtest fix order

EXPECT: H2 and M8 first, with the rest ordered by how far they move the verdict direction.
RESULT (2026-10-01): one-page plan appended to [disk: MyTradingSys/research/fast_track_2026-09-27/SUPERVISOR_INBOX.md] (last entry). Summary: step 1 H2 (like-for-like null, with L6 tests), step 2 M8 (forward holdout; purged CV does not fix a design-contamination problem when nothing is fitted), M9 key fix rides with step 1, then H1 diagnostic, M1/M2/M3/M5 fill and fee mechanics, M6/M7 dedupe and block bootstrap, M4 exit sensitivity, L-items. Arithmetic that matters: the live rule has 19 signals in 4.7 years (about 4 per year), so a 100-trade forward holdout would need about 25 years; only the non-tradable variants can be forward-tested.

## W8. Pre-register T2

EXPECT: a four-field pre-registration can be written without running anything and without depending on H2 or M8.
RESULT (2026-10-01): written [disk: MyTradingSys/research/fast_track_2026-09-27/PRE_REG_T2.md]. Metric: mean net R per filled trade for the marginal set vs the control set. Threshold: 95 percent week-block bootstrap CI, n >= 100 per set. Decision rule and stopping condition are in the file. The pre-registration does not use a WAIT_RR-rate target: the WAIT_RR share falls to zero by construction when the gates are removed, so it cannot falsify anything (reported, never decisive). T2 has not been run and cannot be run from the cloud (no F: data).

## Step 5 (extraction round 2)
Results are in [disk: MyTradingSys/research/_archive/loose_2026-10/EXTRACTION_ROUND2_2026-10-01.md] and extracts/v2/tom/*_v2.md (five files, all `verify_extract_quotes.py` PASS). 5.4 (kappa) was not done, for the same reason as W3.

## Not done, deviations, limits (stated once)
- W3 and 5.4: not done as specified (blind condition failed; extractor cannot be its own second reader). No kappa number exists. Blind packet and calculator delivered.
- W1: 0 of 9 papers verified; egress to every paper host was refused. Packages: purgedcv, skfolio, deflated-sharpe, sealedge opened on PyPI; vectorbt.pro and pbo unverified.
- Budget: usage indicator unreadable, 85 percent row applied (no Sonnet builders beyond this session, one reading pass, no fan-out). No subagent spawned; no Opus used. Model line in the session record is the configured model, not independently checked.
- T2 was not run (W8 only registers it). Nothing was added to FORMULAS.md. No code file was changed, except the new `scripts/dev/kappa_check.py` (calculator, self-test passes).
- Branch: the harness assigned claude/focused-faraday-xnxqms; cloud/work was not created. Recorded as branch_alias.
- One reader per item, Confidence tags above. Counts name how they were counted in each item.

## REJECT list (listed once; source plus reason; do not research again)
- KOSPI200 futures study, tickfloor 517-strategy study, KCI cryptocurrency DRL CPCV study (REVALIDATION_REQUEST R5/R7): no author, venue or date given; cannot be opened (tickfloor: 404 on PyPI).
- sealedge claim "DSR" (REVALIDATION_REQUEST packages list): the PyPI README does not contain it.
- cBkwYjn-6mM "you should actually avoid setting such a tight stop" as Tom evidence: guest interview, speaker not in the Tom set.
- 1xBWnyr1qe4 back-testing and scalping statements as Tom evidence: interview with machine-translated English, speaker unconfirmed.
- ODdF0Bn_KSc "A naked POC isn't an edge in itself" as Tom evidence: speaker unconfirmed (kept only as a pointer in W5 item 7).
- vectorbt.pro and pbo (CRAN) as verified packages: cannot be opened from this surface (UNVERIFIED-WEB, not rejected on merit).
