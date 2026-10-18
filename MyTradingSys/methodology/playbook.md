# PLAYBOOK - Project: [TBD] Real-Time Trading System
# AI prompt. Read at session start. Updated after every session.
# Version: 3.0 (added Part J - Lessons from Audit Failures 2026-08-07)
# Purpose: Session continuity + project-specific rules + workflow evolution.

---

## PART I - RESEARCH METHODOLOGY GATE [v3.0, 2026-09-28]
### *"Research how to research before you research."*
Trigger (added 2026-10-09): any reply that would cite an external source, name a web study, or state what exists on the internet is a research task under this Part, regardless of how the question is phrased. Run STEP 1 before searching.

Why: a never-verified "2026 Journal of Financial Markets" citation once justified the CVD divergence layer.
No external claim enters MTS unverified. Applies to every external research task (web research, citation
checks, indicator evidence). Transcript extraction follows methodology/extraction.md instead.
v3.0 changes: per-search ritual replaced by one method note per question; explicit citation check; REJECT
findings are removed from reports; our own backtest outranks external sources; dead BLOCKERS_6 link removed.

### STEP 1: METHOD NOTE (once per research question, before searching)
2-3 sentences: what evidence would settle the question - statistical test, horizon, sample period/size,
out-of-sample requirement, costs (fees + funding + slippage). If no accepted method exists, label the
question "unvalidated domain" and stop for operator review.

### STEP 2: SOURCE TIERS (fixed table; never adjusted after seeing results)
| Tier | Source type | Use |
|---|---|---|
| **T1** | Peer-reviewed journal article; NBER/Fed/BIS/central-bank working paper; regulated-institution research with disclosed method | May justify core rules |
| **T2** | Working papers/preprints (SSRN, arXiv) with disclosed data + method; exchange-published data/docs; replicated practitioner studies with full method | Supports adaptation; universal claims need T1 or our own OOS backtest |
| **T3** | Practitioner content (Tom transcripts, trader blogs, vendor docs); community backtests with full parameters | Ideas and definitions only; predictive claims need T1/T2 or our own backtest |
| **REJECT** | Marketing/affiliate; no author, date or method; win-rate or profit claims without costs; any citation that cannot be opened and matched | Never used |

Tom content: Tom's verified words = T3 primary source for Tom rules. AI interpolation of Tom = REJECT unless
flagged "interpolation - requires validation". No fixed core (operator 2026-10-13): layers may combine or filter each other; results decide.

### STEP 3: EXECUTE
a. **Citation check.** Open every cited source and match title, authors, venue, year; record URL/DOI and
   "verified YYYY-MM-DD". Abstract-only access is allowed if the claim is in the abstract (mark "abstract only").
   Cannot open or does not match = REJECT.
b. **Tag every finding** `Tier | Method quality (OOS? costs? sample/period) | Confidence H/M/L`.
c. **Discard.** REJECT findings and anything we cannot implement or test are removed from the body; list them
   once at the end (source + reason, one line each) so they are not researched again.
d. **No lowering the bar.** If a question has no T1/T2 evidence, write "No validated evidence found".
e. **Our backtest decides.** External evidence only ranks what to test first; adoption needs our own
   backtest (verdict.py + PBO, out-of-sample, fees + funding). Formulas go to backtest/layers/FORMULAS.md
   with canonical definition + source before any spec.

### CORPUS SEARCHES (extracts, transcripts, condition files) - Vocabulary Mining loop
Seed keywords -> grep -> harvest co-occurring terms from each hit's sentence -> re-grep -> repeat until a pass
adds <10% new hits. Report every term, hits per term, files matched and files read.

### CONSEQUENCES
- A rule built on unverified research = BLOCKER; log it in system/OPERATOR_DECISIONS.md.
- A system change backed only by T3 needs explicit operator approval.

---

# END
