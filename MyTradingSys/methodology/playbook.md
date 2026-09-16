# PLAYBOOK - Project: [TBD] Real-Time Trading System
# AI prompt. Read at session start. Updated after every session.
# Version: 3.0 (added Part J - Lessons from Audit Failures 2026-08-07)
# Purpose: Session continuity + project-specific rules + workflow evolution.

---

## PART I - RESEARCH METHODOLOGY GATE [v2.0]
### *"Research how to research before you research."*

### THE PROBLEM
We built rules on a "2026 Journal of Financial Markets" citation that was never verified. If fake, the CVD divergence layer lost its entire justification. This gate prevents unvalidated assumptions from entering the system disguised as "research-backed."

### THE 3-STEP PROTOCOL
Every external research task (web search, citation validation, indicator backtesting) MUST pass through these steps in order. No skipping. No shortcuts.

#### STEP 1: META-RESEARCH - Understand HOW to research this topic
Before searching for answers, search for the methodology.

**What to search:**
- "how to validate [topic] in [domain]"
- "methodology for testing [topic]"
- "common pitfalls in [topic] research"
- "accepted standards for [topic] evidence"

**Goal:** Know the validation framework BEFORE JISHU sees any evidence.
- What statistical test is standard?
- What sample size is considered meaningful?
- What lookback period is appropriate?
- What constitutes a "replicated" vs "anecdotal" finding?

**Output:** A 2-3 sentence methodology note that defines HOW the actual research will be conducted.

**If no established methodology exists   ' FLAG as "unvalidated domain." Require manual review before proceeding.**

#### STEP 2: SOURCE VALIDATION - Define what counts as evidence
Before seeing any results, commit to source tiers. This prevents cherry-picking.

| Tier | Source Type | Trust Level | Use in System? |
|------|-------------|-------------|----------------|
| **T1** | Peer-reviewed journals (JFE, JFQA, RFS, JFM), NBER/Fed/BIS working papers, institutional research from regulated entities (CME, major bank quant desks) with disclosed methodology | Gold standard | [OK] Justify core rules |
| **T2** | Replicated practitioner studies, exchange-published data analysis, verified prop-firm or quant firm research with full methodology disclosure | Strong | [OK] Support adaptation |
| **T3** | Individual practitioner content (Tom Vorwald transcripts, verified trader blogs), community backtests WITH full parameters disclosed, aggregated exchange data | Practitioner | [OK] Primary for analyst-specific rules; requires T1/T2 for universal claims |
| **REJECT** | Marketing materials, unverifiable citations, claims without methodology or raw data, affiliate content, "studies" with no author/institution/date | Garbage | [X] Never use |

**Special Rule for Tom Vorwald Content:**
- Tom's own words from verified transcripts = **T3 (Primary Source)** for Tom-specific rules
- Academic validation of Tom's concepts = **T1/T2**
- Our own AI interpolations of Tom's concepts = **REJECTED** as source material. May be used for crypto adaptation ONLY if explicitly flagged as "interpolation - requires validation"

#### STEP 3: EXECUTE RESEARCH - Conduct the actual search

**3a. Query design (Vocabulary Mining loop).**
For any search that touches a document corpus (extracts, transcripts, condition files), design queries using this loop - not intuition:

1. Seed: intuitive keyword list. Treat as incomplete.
2. Grep seed terms. Read every hit's surrounding sentence.
3. Harvest: collect every descriptive term that co-occurs with a seed hit in the same or adjacent sentence. This is empirical, not inferred.
4. Re-grep with seed + harvested terms.
5. Loop: if re-grep returns >10% additional hits, return to step 3. Stop when new hits fall below 10% of the previous pass.
6. Coverage report: list every term used, hits per term, files matched, files read. This is the evidence the search was comprehensive - not a claim that it was.

The vocabulary loop terminates on a numeric criterion, not on judgment. A search that stops before <10% growth is incomplete.

**3b. Filter results** through the source tiers from Step 2.

**3c. Extract findings** with mandatory tags: `Source Tier | Methodology Quality | Confidence Level`.

**GATE RULE:** No finding may be used to justify a system rule unless it has passed through Steps 1-3. A finding without documented methodology is treated as **"unverified assumption"** - not evidence.

### STRICT WEB SEARCH IMPLEMENTATION

**Before EVERY web_search call:**
1. State the research question
2. State the methodology (from Step 1)
3. State the source tier commitment (from Step 2)
4. Then execute search

**Example:**
```
RESEARCH TASK: Validate CVD divergence as reversal signal in crypto
METHODOLOGY: Search for backtests with defined lookback periods, 
  asset-specific thresholds, and out-of-sample testing. 
  Minimum 90 days data. Require disclosed parameters.
SOURCE TIER: T1/T2 only for predictive claims. T3 acceptable for 
  practitioner implementation notes.
EXECUTING SEARCH...
```

**After EVERY web_search call:**
1. Tag each result with source tier
2. Reject any result that doesn't meet the pre-committed tier
3. If zero results meet the tier   ' Report "No validated evidence found" rather than lowering standards

### VIOLATION CONSEQUENCES
- A rule built on unverified research = **BLOCKER** (see `BLOCKERS_6_Unvalidated_Assumptions.md`)
- A citation used without verification = **Immediate flag** in `02b_DECISIONS_LOG.md`
- A system change justified by T3/REJECT sources without T1/T2 backing = **Requires explicit user approval**

---

# END
