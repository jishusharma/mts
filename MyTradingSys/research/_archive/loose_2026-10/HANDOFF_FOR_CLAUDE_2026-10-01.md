# HANDOFF FOR CLAUDE - Tom/Fabio revalidation (2026-10-01)

To: Claude (local CLI, cloud, or Qwen NUC)
From: MTS-2026-10-01-1431Z-DSA-COO
Status: open. Work items W1-W8 below.
Prior notes:
- MyTradingSys/research/_archive/loose_2026-10/AUDIT_REVIEW_2026-10-01.md (review of the Tom/Fabio
  provenance block)
- MyTradingSys/research/_archive/loose_2026-10/REVALIDATION_REQUEST_2026-10-01.md (ten methods,
  D1-compliant, every citation UNVERIFIED-WEB)

## Read first

Read AUDIT_REVIEW then REVALIDATION_REQUEST in that order. The second
iteration findings in this file assume both.

## Part 1 - The ten methods (summary, details in REVALIDATION_REQUEST)

R1 DSR (Bailey & Lopez de Prado 2014). Trial-count correction.
R2 Purged K-Fold (Lopez de Prado 2018 ch.7). Time-respecting CV.
R3 CPCV (same, ch.12). Multiple backtest paths.
R4 PBO via CSCV (Bailey et al. 2013). Probability of overfit.
R5 White Reality Check / Hansen SPA (2000, 2005). Data-snooping test.
R6 Romano-Wolf stepwise (2005). Which specific rules survive.
R7 Benjamini-Hochberg FDR (1995). Multiplicity across subgroups.
R8 Stationary Bootstrap (Politis & Romano 1994). Temporal CIs.
R9 Cohen's Kappa (1960). Second-reader agreement.
R10 T2 pre-registration. Internal format.

All ten citations are UNVERIFIED-WEB until a surface with web reach opens
and matches them.

## Part 2 - Second-iteration findings (new, this pass)

The first pass listed method gaps. This pass applied each method to the
audit's own conclusions. Six findings the first pass did not name.

### F1. The 36 NO-SOURCE count is a point estimate from one reader.

The provenance audit classifies 74 rows: 2 SOURCED, 33 CONCEPT-ONLY, 36
NO-SOURCE, 3 DATA-PLUMBING (PROVENANCE_AUDIT_TOM.md L9-15). One reader
(Opus 5.5). No kappa. No confidence band. If a second reader re-derives
the same 74 rows, the NO-SOURCE count could shift 5-15 rows in either
direction. The headline number is honest as a single-reader measurement
and unreliable as a population estimate.

Work item W3 below.

### F2. The impact ranks are current-state counts, not counterfactuals.

Section 8 ranks NO-SOURCE items by "impact on Tom trades." The impact
figures are what IS happening now (80,847 WAIT_RR, 19 SETUP_FORMING, 19 of
19 short). They do not say what changes if a fix lands. Every rank-1 fix
moves a different count. The audit measures the current state, not the
fix's effect. A predeclared counterfactual per rank (playbook Part I,
D1 item 6 in the first pass) would make the ranking falsifiable: "if we
widen the R:R window to X, WAIT_RR drops from 80,847 to below Y, or the
fix failed."

### F3. The audit searched for support, not for falsification.

For each parameter, the audit searched for a Tom quote. Not found =
NO-SOURCE. It did not run a falsification-first search: broader terms,
synonyms across the whole corpus, quote fragments. A stronger read would
search "risk reward," "stop," "floor," "window," "band," "cap," "veto,"
"gate" before concluding no source exists. Some NO-SOURCE items may
become CONCEPT-ONLY with a wider search.

Work item W4 below.

### F4. Section 10 omits the fields most likely to carry hidden Tom quotes.

PROVENANCE_AUDIT_TOM.md L186 not-audited list: MDS open interest, funding,
session timing, liquidation, alignment check, FvgCalculator,
NakedPocTracker, ArchiveHistoricalSource, state_code/quad_classify. If any
of those carries a Tom quote, the audit is incomplete. The audit does not
say whether it checked, only that it did not classify. The 36 count might
under- or over-count depending on what those fields contain.

Work item W5 below.

### F5. The Fabio side has no equivalent provenance audit.

Fabio v3.1 has a 41-row provenance table (FABIO_V3_SPEC.md section 7.1).
It uses the same "concept" / "number" distinction as Tom, but it has no
NO-SOURCE count, no verdict tally, no one-reader caveat marked. The Tom
audit's headline finding - "no number that decides whether a trade exists
has a Tom quote" - has no Fabio counterpart. That comparison is the
audit's most useful output and it is missing for half the block.

Work item W6 below.

### F6. "Our backtest decides" is underdetermined when the backtest is defective.

REVALIDATION_REQUEST section "OUR BACKTEST DECIDES" says adoption of any
method requires our own backtest. But TOM_CORE_BT_REVIEW_2026-09-30.md
independently flags the backtest instruments as defective (H1, H2, M7,
M8, M9). The adoption gate is currently a broken instrument. Fixing the
instruments is a precondition for the adoption rule to mean anything.

Work item W7 below.

## Part 3 - Work items for Claude

Each item: input, task, output, gate. W1-W4 are cheapest. Do them in
order. W5-W8 need operator approval to touch live paths.

### W1. Verify citations (UNVERIFIED-WEB clearance).

Input: 9 papers and 6 packages in REVALIDATION_REQUEST, UNVERIFIED-WEB
list section.
Task: open each source, match title/authors/venue/year. For paywalled
items, mark "abstract only" if the abstract carries the claim.
Output: same file with each line changed to "VERIFIED <YYYY-MM-DD> URL/DOI"
or "REJECT reason".
Gate: no citation enters FORMULAS.md until VERIFIED.

### W2. Compute the DSR trial count.

Input: MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md.
Task: count the actual number of independent trials. The review says 16
rows (4 variants x 4 stress configs); variants were chosen post hoc. The
real N is the number of Sharpe ratios you would see under the null of
"no skill." Report both the count and the basis.
Output: N and basis in a one-line addendum to REVALIDATION_REQUEST R1.
Gate: DSR is undefined until N is settled.

### W3. Second-reader kappa on the 74 provenance rows.

Input: PROVENANCE_AUDIT_TOM.md section 1 verdict table plus each row's
rule text.
Task: independently re-derive each of the 74 verdicts, blind to the first
list. Different reader (surface or model).
Output: kappa, plus a list of rows where the two readers disagreed.
Gate: kappa < 0.6 means the headline NO-SOURCE count is reader-dependent.

### W4. Falsification-first re-search of the top 5 NO-SOURCE items.

Input: PROVENANCE_AUDIT_TOM.md section 8, ranks 1-5. The stop floor,
fallback, target window, net R:R, proof bands.
Task: search the corpus with broader terms first. "risk," "reward,"
"stop," "floor," "window," "band," "cap." Report whether any passage
supports or contradicts the audit's NO-SOURCE verdict.
Output: per rank, PASS (no source found in wide search, NO-SOURCE stands)
or CORRECTION (source found, reclassify).
Gate: a single new source on any of the top-5 changes the rank-1 or rank-2
action.

### W5. Check section 10 fields for hidden Tom quotes.

Input: PROVENANCE_AUDIT_TOM.md L186 not-audited list.
Task: for each field in that list, search the Tom corpus with the field's
name. Report quote found or none.
Output: one line per field.
Gate: if any field yields a quote, the 36 count and the sections that
depend on it are incomplete.

### W6. Build the Fabio equivalent of the provenance audit.

Input: FABIO_V3_SPEC.md section 7.1 provenance table (41 rows), the 10
Fabio video extracts, raw_transcripts_canonical.
Task: same classification as Tom. TOM-SOURCED / CONCEPT-ONLY / NO-SOURCE
/ DATA-PLUMBING per row. Count.
Output: FABIO_PROVENANCE_AUDIT_2026-10-01.md.
Gate: a NO-SOURCE count for Fabio is required before any Fabio testnet
entry per the operator's provenance rule.

### W7. Read the backtest review and propose a defect-fix order.

Input: TOM_CORE_BT_REVIEW_2026-09-30.md (H1, H2, M1-M9, L1-L6).
Task: propose the sequence to fix the backtest instruments. Which defect
first if the goal is to make "our backtest decides" meaningful.
Output: a one-page plan in SUPERVISOR_INBOX.md.
Gate: H2 (like-for-like null) and M8 (contaminated holdout) are the two
that most change the verdict. Propose those first.

### W8. Pre-register T2.

Input: DSA_TASKS_2026-10-01.md T2, ANGLE_HYPOTHESES.md L77-112 (format).
Task: write PRE_REG_T2.md before T2 backtest runs. Metric, threshold,
decision rule, stopping condition.
Output: MyTradingSys/research/fast_track_2026-09-27/PRE_REG_T2.md.
Gate: T2 cannot run until this file exists.

## Priority order

1. W1 (verify citations). Cheap. Unblocks all method application.
2. W2 (DSR trial count). One number. Unblocks R1.
3. W8 (T2 pre-registration). One file. No code.
4. W3 (kappa). One more reader.
5. W4 (falsification re-search). Wider corpus search.
6. W6 (Fabio audit). Parallel to Tom audit.
7. W7 (backtest fix order). Read-only plan.
8. W5 (section 10 check). Depends on corpus search tooling.

## Do not do

- Do not apply all ten methods at once. Pick from the priority order.
- Do not lower the source bar. If a citation cannot be opened and matched,
  REJECT it.
- Do not run T2 before W8 lands.
- Do not change live paths (execution/, layers/alerts/, loop) without the
  operator. Builders stage .new only.
- Do not merge to main from a cloud session. Cherry-pick onto main by the
  operator.

## Reply path

Write replies to MyTradingSys/system/CLOUD_INBOX.md or
Dumps/workers/incoming_dsa/. If a work item cannot be done for a reason
not listed here, log it so the next session does not re-request.

End of handoff.
