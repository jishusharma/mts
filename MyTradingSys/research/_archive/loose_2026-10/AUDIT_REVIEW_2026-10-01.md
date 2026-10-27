# AUDIT REVIEW - Tom/Fabio provenance work (2026-10-01, DSA-COO)

Purpose: handoff note for Claude (local CLI or cloud). Captures what the
Tom/Fabio audit block produced, the method gaps found on review, and
alternatives. Written from disk, section 8/10 read verbatim. Author: this
DSA session. No repo file edited to produce this note.

## 1. Artifacts (all under MyTradingSys/research/fast_track_2026-09-27/)

- PROVENANCE_AUDIT_TOM.md, 266 lines, 11 sections. Read-only.
- FABIO_V3_SPEC.md, ~36.5 KB, v3.0 then v3.1 (8 findings folded in).
- TOM_LINE_BY_LINE_4MoNjEQ2Dd8.md, ~33 KB.
- FABIO_LINE_BY_LINE_fZlNGWvd2Ko.md, ~31.4 KB.
- TOM_RULEBOOK_MERGE_999.md, ~9.6 KB.
- MISSING_PIECES_2026-09-30.md, ~34.4 KB.
- TOM_CORE_BT_REVIEW_2026-09-30.md, ~9.6 KB (defects-only review of the
  Tom core backtest: 2 HIGH, 9 MED, 6 LOW).
- EXTRACTION_METHOD_V2.md + EXTRACTION_METHOD_V2_FABIO.md.
- (Sibling, not in fast_track) CONSOLIDATION_REPORT_2026-10-01.md, 8 KB.
- (Sibling, not in fast_track) DSA_TASKS_2026-10-01.md, 7 KB, 8 tasks T1-T8.

Author of provenance audit and Fabio spec: cloud session
MTS-2026-09-30-1005Z-CLD-ANA-connected-system, Opus 5.5 (from commit
trailers 5f816ae, e6601af, 8f155f5, 02fc346).

## 2. Verdict tally (PROVENANCE_AUDIT_TOM.md L9-15)

| verdict | rows |
|---|---|
| TOM-SOURCED | 2 |
| TOM-CONCEPT-ONLY | 33 |
| NO-SOURCE | 36 |
| DATA-PLUMBING | 3 |
| total | 74 |

L17 verbatim: "None of the numbers that decide whether a Tom trade exists
(stop floor and fallback, target window, net R:R gate, proof bands, book
veto, distance caps, below-VAL rule) has a Tom quote. Only the 70% value
area is TOM-SOURCED (plus one example row). The '2:1 net' rule cited to
qLnQan0KGmQ is not in that video (A13)."

## 3. Section 8 impact ranks (L135-152) - measured, not judged

| rank | item | cited impact |
|---|---|---|
| 1 | Target window 2.0-3.5R | Kills 8.1R trade; 80,847 of 120,892 rows WAIT_RR |
| 2 | Net R:R >= 2.0 cited to qLnQan0KGmQ | Miscited; leaves band [2.67, 3.5]R |
| 3 | 0.1% stop floor -> 0.2% | Removes Tom-size stops (12 ticks about 0.04%) |
| 4 | 0.2% fallback stop | Median stop in every variant |
| 5 | Proof bands 3 and 5 | Only SETUP_FORMING fires; 19 signals in 4.7 years |
| 6 | Book veto 3.0/0.33 with 0.0 default | Every long at proof 5 -> WATCH when book 0.0; 19 of 19 short |
| 7 | No shorts below VAL; flow vetoes | Longs into breakdowns then vetoed |
| 8 | 0.1% tier and caps 0.2-0.5% | Drop zones |
| 9 | trend_healthy outside VA | Blocks VAH shorts; contradicts CE:172 |
| 10 | TWOPEAK 0.6 / D-P 0.8-1.2 | No trade effect; STATE popup always TWOPEAK |
| 11 | +10 bonus; score bands | Chooses top candidate |
| 12 | Weak wick counts; book 1.5/0.67; last-3 veto | Inflate or veto proof count |
| 13 | Popup thresholds, cooldowns, debounce | Decide which alerts reach operator |
| 14 | Gross >= 1.5; "Tom never lowers R:R" | Redundant; unsupported |

## 4. Section 10 not audited (L186)

MDS open interest, funding, session timing, liquidation, alignment check,
FvgCalculator; NakedPocTracker; ArchiveHistoricalSource (gitignored);
state_code/quad_classify (V10). Anything the plan claims about those is
outside the audit's coverage.

## 5. The audit method - what it does and does not check

Uses: exact-substring quote verification (51/51 verified). Per-row verdict
tagging (TOM-SOURCED / CONCEPT-ONLY / NO-SOURCE / DATA-PLUMBING). Impact
rank measured from current-state backtest counts.

Does not use:
- No pre-registration. FROZEN.md written by the report script after rows
  exist and overwritten every run (TOM_CORE_BT_REVIEW M9).
- No inter-rater check. One reader (Opus 5.5).
- No blinded re-derivation.
- No falsification attempt. The audit searched for quotes; it did not try
  to disprove "no source exists."
- No predeclared counterfactuals. Ranks use current-state counts, not
  what changes if a fix lands.
- No independent replication.

## 6. Review of the backtest statistics (TOM_CORE_BT_REVIEW)

The review audits the audit's own instruments and finds them defective:

- H1: Live rule untested, reason not diagnosed; 301 rows lost to
  verdict.py downgrades, no per-row reason count. All 19 signals short
  (p about 4e-6 if 50/50).
- H2: Random-entry null not like-for-like. Market-entry null vs
  limit-with-attrition real. Null keeps day but not conditioning.
- M7: Bootstrap treats trades as iid; they cluster in time and on shared
  levels. CIs too narrow.
- M8: Holdout contaminated by design history (Rule 32 evidence, D1/D3/D4
  rulings, sim.py replay all inside holdout window).
- M9: No real pre-registration. Registry dedupe by run_id = date; N_trials
  understated. FROZEN.md is written after the fact.
- M1-M6, L1-L6: fill mechanics, fee asymmetry, invented exit rules,
  episode dedupe key uses zprice (dynamic zones become new episodes),
  fee structure not sim.py.

## 7. Alternatives ranked (proposed by DSA-COO, 2026-10-01)

Alt A. Add rule ids at every decision point (T8) before T1-T6. Makes
every later audit mechanical. No behaviour change.

Alt B. Change book-veto 0.0 default on a backtest branch, count longs
at proof 5. Addresses the strongest signal in the evidence (19 of 19
short). Not currently on the T1-T8 list. Cheapest test in the plan.

Alt C. Like-for-like random null (TOM_CORE_BT_REVIEW H2 fix). Turns
"null at least as good" from a claim into a measurement. One test.

Alt D. Three specific fixes (T5 states, T2 window, T3 stop), not a
rebuild. Nothing in the audit argues for a rebuild.

Alt E. Run EXTRACTION_METHOD_V2 against V1 on one video already
extracted. Validates the extraction method itself. Not in the plan.

Alt F. Freeze the Fabio spec until MISSING_PIECES H1-H3 run. Spec
growth against negative evidence (best family 1h net +0.113%, PBO 0.756;
OF model net negative after fees).

## 8. Scientific-method gap (operator question 2026-10-01)

Direct answer: the project does not currently use a scientifically
validated method to cross-validate goals, actions, audits, or reviews.
It has a research gate (playbook Part I: source tiers T1/T2/T3/REJECT,
citation check, OOS, costs, PBO) and its own review document shows the
gate's statistical instruments are partly broken and the audits are not
pre-registered.

A validated method would need, at minimum:
1. Pre-registration of question, metric, decision rule, stopping condition.
2. Two independent readers, agreement measured (kappa).
3. Blinded re-derivation of a verdict list.
4. Falsification attempt (strongest search first).
5. Predeclared counterfactuals: expected effect size per fix.
6. Multiplicity adjustment across the whole search space.
7. Independent replication on a held-out subset.

## 9. Open item for the next session

Pre-register T2 (target window / R:R decision) before its backtest runs.
One file: metric, threshold, stopping rule. This is the cheapest
concrete step and it is what makes the T2 result falsifiable.

## 10. Sources

- PROVENANCE_AUDIT_TOM.md, sections 1, 8, 10 read verbatim this session.
- CONSOLIDATION_REPORT_2026-10-01.md, DSA_TASKS_2026-10-01.md,
  TOM_CORE_BT_REVIEW_2026-09-30.md, EXTRACTION_METHOD_V2*.md read full.
- Commit trailers 5f816ae, e6601af, 8f155f5, 02fc346 name the authoring
  session.