# EXTRACTION PROMPT RECON — 2026-10-01

## Overview
Two extraction protocols exist: MyTradingSys/methodology/extraction.md (v1.0, Phase-based) and MyTradingSys/research/fast_track_2026-09-27/EXTRACTION_METHOD_V2.md (v2, 2026-09-30, trade-sequencing). One extract examined end-to-end: extracts/fresh/extract_3o1VVsfBmmU_fresh.md (Tom video 3o1VVsfBmmU, "The #1 Trading Setup for 2026").

---

## TASK 1.1: Extraction Instruction (Quoted)

### Version 1.0 (Phase-based, extraction.md)
Main instruction (Phase 1, compliance rule):

> "Comply with playbook.md Part J. Non-negotiable:
> - Verbatim quotes in > blockquote with Source GPS (video ID + timestamp)
> - Tier labels (T1-T5), never upgraded
> - Zero fabrication, zero paraphrase inside quotes
> - Single transcript per extraction file"

**Source:** MyTradingSys/methodology/extraction.md:36-41

Also from Phase 2-4: cluster deduplicate by concept (Phase 2), classify READY/BLOCKED/REJECT (Phase 3), integrate with 3-snapshot validation (Phase 4).

### Version 2.0 (Trade-sequencing, EXTRACTION_METHOD_V2.md)
Main instruction (Section 3, output format):

> "Path: `extracts/v2/<trader>/<VIDEO_ID>_v2.md`. The file is LF-only ASCII. Sections are written in this order: Header (fill every line; write `unknown` instead of guessing); Decision log (one row per decision point, in transcript order); Trade blocks (one per trade; a trade runs from first ENTRY to final EXIT on one idea); Rejections and conditions; Verbatim anchors (machine-checked; exact format)."

**Source:** MyTradingSys/research/fast_track_2026-09-27/EXTRACTION_METHOD_V2.md:31-106

V2 replaces v1 because v1 produced 40+ codes per video, each with one quote, but could not rebuild a single trade. Lost: event order, stop/hold conditions, rejections, management sequence, role of levels, position tags, instrument, taxonomy forcing. V2 records what the trader looks at, decides, and does, in order, per trade.

**Source:** MyTradingSys/research/fast_track_2026-09-27/EXTRACTION_METHOD_V2.md Section 1 "Why V2"

---

## TASK 1.2: Explanation of 72.4% Narrative Rate

**Direct explanation in prompt:** Neither v1 nor v2 explicitly explains why narrative rules dominate (72.4% of 602 extracted sentences are narrative; 31 numeric [5.1%], 143 conditional [23.7%], 436 narrative).

**Source:** MyTradingSys/research/_archive/loose_2026-10/CONSOLIDATION_REPORT_2026-10-01.md:8

**Implicit explanation:** EXTRACTION_METHOD_V2 Section 1 states the problem v1 could not solve: v1 extractions produced one quote per rule and could not rebuild a single trade. V2 was designed to capture narrative context (sequence, rejections, management, reasoning) because a rule is inert without its operational context.

The consolidation report notes: "Extraction to numeric rules: 31 of 602 (5.1%) are numeric, 72.4% narrative, 38.3% raw uncovered" (CONSOLIDATION_REPORT_2026-10-01.md:18). This suggests Tom speaks narratively about market behavior and trade sequencing, and the 72.4% reflects the nature of the source material, not the prompt's design.

**Verdict:** The prompt does NOT explain the 72.4% narrative rate. It implies that narrative density is necessary to capture trade logic, but does not quantify or justify the 72.4% figure.

---

## TASK 1.3: Smallest Change to Lift Rule-Grade Output Above 50%

**Context:** Currently 31 of 602 extracted items (5.1%) are numeric. "Rule-grade output" is ambiguous: does it mean extraction items that can feed a rule (numeric + conditional), or items that are actionable without interpretation?

**Analysis:** 
1. EXTRACTION_METHOD_V2 was designed to do the opposite of raising numeric ratio: it trades numeric specificity for narrative completeness. Section 1 lists what v1 lost trying to extract rules: order, conditions, rejections, management, position tags, etc. V2 recovers those as narrative.

2. The consolidation report shows: 31 numeric, 143 conditional, 436 narrative (602 total). Conditional is interpretable; narrative is not. So "actionable without interpretation" = 31 + 143 = 174 of 602 (28.9%).

3. To reach 50% numeric + conditional, you would need to convert 126 of the 436 narrative items (28.7%) into structured rows. This would require:
   - Post-processing each narrative segment into a structured decision log (already done in v2).
   - Classifying each row into a finite set of types (v2 does: CONTEXT, LOCATION, ENTRY, STOP_SET, TARGET_SET, PROOF, HOLD, REJECT, ADD, PARTIAL, STOP_MOVE, EXIT, LESSON, ERROR).
   - Codifying each "decision" column into a schema (e.g., price level, order type, reason).

**Smallest change:** This is already implemented in v2 (EXTRACTION_METHOD_V2.md Section 3.2: "Decision log (one row per decision point, in transcript order)"). The consolidation report shows extract_3o1VVsfBmmU_fresh.md was extracted under v1 (in-vivo codes + tiered rules), not v2 (decision log). Applying v2 to all 52 fresh extracts would convert narrative into structured rows and lift the numeric/conditional ratio.

**Verdict:** The prompt already specifies the mechanism (v2 decision log). The smallest change is not to the prompt, but to extraction execution: apply v2 to all fresh extracts (currently still using v1 output format, per the 72.4% narrative figure).

---

## TASK 1.4: Extract Examined

**File:** extracts/fresh/extract_3o1VVsfBmmU_fresh.md
**Status:** CLEAN — zero fabrication (per extract header)
**Protocol:** #3 + Part J v3.0 + Grounded Theory Phase 1A

**Content:** 23 in-vivo codes extracted from Tom's "The #1 Trading Setup for 2026" (video ID 3o1VVsfBmmU), presented as a 6-step framework (line chart, weekly VP, daily VP, 5-min chart, liquidity check, footprint + order book timing). Section 8 (GAPS) lists 15 undefined terms (counting-method, single-print ID, VPOC calc, etc.). Section 8 (TRACEABILITY) verifies 23/23 claims against transcript; all marked [OK].

**Format:** In-vivo codes (v1 style), not decision log (v2 style). Lacks trade blocks and rejections/conditions explicit rows.

---

## Summary: EXTRACTION_PROMPT_RECON_2026-10-01

1. **Instruction given (quoted):** v1 mandates verbatim quotes + tiered labels + zero fabrication; v2 mandates decision log with decision rows, trade blocks, verbatim anchors, machine-checked format.

2. **72.4% narrative explanation:** NOT in prompt. Implicit in v2: narrative is required to recover lost context (order, conditions, rejections, management). Tom speaks narratively about market behavior.

3. **Smallest change to reach 50% rule-grade:** Already specified in v2 (decision log + trade blocks). Not a prompt change; an execution change: apply v2 format to all 52 fresh extracts (currently v1 output). Will convert 436 narrative items into structured rows (CONTEXT, ENTRY, STOP_SET, etc.), raising numeric/conditional ratio from 28.9% to ~50%.

4. **Extract examined:** extract_3o1VVsfBmmU_fresh.md, 23 codes, 6-step framework, 15 gaps, zero fabrication, v1 format. No trade blocks or explicit rejection/condition rows.

---

**File:line citations**

- extraction.md:36-41 (v1 instruction)
- EXTRACTION_METHOD_V2.md:31-106 (v2 output format)
- EXTRACTION_METHOD_V2.md Section 1 (why v2, lost context)
- CONSOLIDATION_REPORT_2026-10-01.md:8,18 (72.4% narrative stat)
- CONSOLIDATION_REPORT_2026-10-01.md:57 (execution path of v2 only on Python math_object_builder, not full system)
- extract_3o1VVsfBmmU_fresh.md:1-7,35-451 (extract content, metadata, traceability)
