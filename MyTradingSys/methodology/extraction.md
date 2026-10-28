# EXTRACTION LIFECYCLE - MTS
# Version 1.0 | 2026-09-13
# Purpose: How to add a new transcript (Tom, CryptoCred, The Flow Horse, CrypNuevo)
#          to the corpus without fabricating, without forcing categories, and
#          without contaminating the engine.
#
# Trigger:     New transcript arrives (raw text uploaded, new analyst video identified).
# Loaded with: playbook.md Part J (verbatim extraction rules).
# Skip when:   JSON sessions, chart sessions, code edits, research questions.
# Canonical:   MyTradingSys/methodology/extraction.md

---

## 1. SCOPE

Governs the LIFECYCLE of a new extraction:

  1. Extraction           (Phase 1)
  2. Consolidation        (Phase 2)
  3. Integration Planning (Phase 3)
  4. Integration          (Phase 4)

Verbatim extraction rules live in playbook.md Part J. This file assumes those
are followed. It describes what happens AFTER a clean extraction.

Reference implementation: cross-trader corpus (CryptoCred + The Flow Horse).
  Phase 1: 7 transcripts extracted -> 85 rules (CT-001 to CT-085)
  Phase 2: 80 entries, 20 clusters (cross_trader_consolidated.md)
  Phase 3: 5-step classification (cross_trader_integration_plan.md Section 3)
  Phase 4: 3-snapshot validation + engine integration

---

## 2. PHASE 1 - EXTRACTION

Comply with playbook.md Part J. Non-negotiable:

  - Verbatim quotes in > blockquote with Source GPS (video ID + timestamp)
  - Tier labels (T1-T5), never upgraded
  - Zero fabrication, zero paraphrase inside quotes
  - Single transcript per extraction file

Output: extract_<VIDEOID>.md

SAFEGUARD 1 - IN VIVO RULE
  If a code does not appear verbatim in at least one transcript,
  it is NOT a valid code.

SAFEGUARD 5 - CLEAN SLATE RULE
  Phase 1 = ONE transcript only.
  Do NOT load prior extractions.
  Do NOT compare codes to prior videos during extraction.
  Comparison is Phase 2.
  Loading prior extractions during Phase 1 causes confirmation bias
  and violates open coding principles.

---

## 3. PHASE 2 - CONSOLIDATION

Goal: turn N extractions into one master rule list, grouped by concept,
deduplicated, conflicts flagged (not resolved).

Steps:
  1. Compile all rules from all extracts into one document.
  2. Group by concept - cluster rules that describe the same principle.
  3. Deduplicate - one entry per principle, with all Source GPS refs.
  4. Flag conflicts - document, do NOT resolve.
  5. Catalog - numbered master list with cross-references.

Output: <corpus>_consolidated.md

SAFEGUARD 2 - CLUSTER EVIDENCE RULE
  A cluster (setup type / concept group) is only valid if:
    - At least 3 different videos contain rules that naturally group together
    - The grouping is supported by the analyst's own language
      (not the extractor's interpretation)
    - A boundary exists - codes in Cluster A do not appear with codes
      in Cluster B in the same trade example

  If these are not met, the cluster is not a pattern. It is noise.

---

## 4. PHASE 3 - INTEGRATION PLANNING

Goal: for every consolidated rule, classify READY / BLOCKED / REJECT.

5-step check per rule (see cross_trader_integration_plan.md Section 3.1):

  Step 1 - Context Recovery:       Re-read the original transcript segment.
                                   What market condition? What timeframe?
                                   General principle or specific example?
  Step 2 - Scenario Mapping:       Map to state / zone / setup / proof.
  Step 3 - Pre-Integration Check:  Search compiled_engine.md for the concept.
                                   Classify: DUPLICATE / CONFIRM / CLARIFY /
                                   GAP / REJECT.
  Step 4 - Consolidation:          Compile candidates. List blockers.
  Step 5 - Revalidation:           Test on 3 live snapshots. If rule changes
                                   0 of 3 verdicts -> REJECT. If contradicts
                                   existing rule -> REJECT.

Output: integration queue with categories READY / BLOCKED / REJECT.

SAFEGUARD 3 - SATURATION GATE
  No setup file may be built until:
    - At least 20 videos extracted (minimum for pattern detection)
    - Last 5 consecutive extractions produced <5% new codes
    - Cluster map (Phase 2 output) reviewed

  Saturation = new data produces no new codes.
  Stopping before saturation means the theory is incomplete, not done.

---

## 5. PHASE 4 - INTEGRATION

For every READY rule:
  1. Draft patch (exact lines to add/modify in compiled_engine.md)
  2. Trace decision path for 3 validation snapshots
  3. Regression test - run 3 snapshots through patched engine
  4. Update schema if new DSA fields required
  5. Update condition files (canonical documentation)
  6. Log decision in OPERATOR_DECISIONS.md

Post-integration: run 3 NEW live snapshots. Verify no contradictions between
newly integrated rules and existing ones.

Governing rules: 01_AI_BEHAVIOR.md Rules 31-36.
  Rule 31 - Validate before fix
  Rule 32 - No new rule without 3-snapshot proof
  Rule 33 - Lean DSA contract
  Rule 34 - Research before importing cross-market concepts
  Rule 35 - Validate before extracting

---

## 6. SAFEGUARD 4 - REFLEXIVITY

After each extraction batch, document:
  - What codes emerged that were unexpected?
  - What pre-conceptions were challenged?
  - What assumptions need revision?

Output: append to reflexivity_log.md

---

# END
