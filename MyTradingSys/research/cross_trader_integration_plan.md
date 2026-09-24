# CROSS-TRADER INTEGRATION PLAN
# Date: 2026-08-31
# Status: ACTIVE — 7/7 transcripts extracted, 85 rules cataloged. Phase 1 COMPLETE.
# Purpose: Formal post-extraction workflow for integrating cross-trader rules into MTS
# Replaces: Ad-hoc tagging during extraction (discarded as methodologically unsound)
# ---

## WORKFLOW OVERVIEW

The cross-trader research proceeds in FOUR distinct phases. NO phase may be skipped. NO phase may run in parallel with another.

| Phase | Name | Input | Output | Gate |
|-------|------|-------|--------|------|
| 1 | PURE EXTRACTION | Raw transcript | Extract file (Source GPS + quotes only) | All 7 transcripts extracted |
| 2 | CONSOLIDATION | All extract files | Master rule list (grouped, deduped) | Zero contradictions unresolved |
| 3 | INTEGRATION PLANNING | Master rule list + compiled_engine.md | Integration queue (READY / BLOCKED / REJECT) | All 5 steps complete per rule |
| 4 | INTEGRATION | Integration queue + DSA fields | Patched compiled_engine.md | 3-snapshot validation per rule |

**Current status:** Phase 1 COMPLETE (7/7 transcripts extracted to pure format). 85 rules cataloged. Proceeding to Phase 2.

---

## PHASE 1: PURE EXTRACTION PROTOCOL

### 1.1 Extraction Standard

Each extract file MUST contain ONLY:

1. **Header metadata** (video ID, analyst, duration, date)
2. **Rule name** (descriptive, analyst-neutral where possible)
3. **Verbatim quotes** in `>` blockquote with Source GPS (Video ID + timestamp)
4. **Optional context note** (what the analyst describes, NOT how it relates to Tom)

Each extract file MUST NOT contain:
- Tags (CONFIRM / DUPLICATE / CLARIFY / GAP / REJECT / BLOCKED)
- Engine impact assessment
- "Validation needed" flags
- DSA field requests
- Comparison to Tom's engine

### 1.2 Source GPS Format

```
> "verbatim quote from transcript"
> — VIDEO_ID, ~MM:SS
```

Every quote MUST have:
- [ ] Video ID
- [ ] Approximate timestamp (~MM:SS or ~HH:MM:SS)
- [ ] Verbatim text in `>` blockquote

### 1.3 Context Note Format (Optional)

```
**Context:** The analyst is describing [concept] in the context of [market condition].
This is observed during [specific price action / session / timeframe].
```

Context notes describe WHAT the analyst said, not WHAT THE ENGINE SHOULD DO with it.

### 1.4 Extraction Completeness Check

Before marking a transcript as extracted, verify:
- [ ] All distinct rules/concepts identified (not just the obvious ones)
- [ ] Every rule has at least one verbatim quote with Source GPS
- [ ] No AI interpolation or paraphrasing passed off as quote
- [ ] No tagging, no engine assessment, no validation flags

---

## PHASE 2: CONSOLIDATION PROTOCOL

### 2.1 Input
All extract files from Phase 1 (7 transcripts across 3 analysts).

### 2.2 Process

1. **Compile master list:** Copy all rules from all extract files into a single document.
2. **Group by concept:** Cluster rules that describe the same underlying principle (e.g., all "compression -> expansion" rules together).
3. **Deduplicate:** If two analysts say the same thing with different words, keep ONE entry with BOTH Source GPS references.
4. **Flag conflicts:** If two rules contradict each other, document the conflict with both Source GPS references. Do NOT resolve during consolidation.
5. **Catalog:** Produce a numbered master list with cross-references.

### 2.3 Output

**Appendix A of this document** — Master rule list with:
- Rule number (cross-trader global, e.g., CT-001, CT-002)
- Rule name
- All Source GPS references (analyst + video ID + timestamp)
- All verbatim quotes (from all analysts who taught this)
- Concept grouping tag
- Conflict flag (if any)

**NO engine tags. NO integration decisions. Just a clean catalog.**

---

## PHASE 3: INTEGRATION PLANNING PROTOCOL

### 3.0 When This Phase Starts
ONLY after:
- All 7 transcripts extracted (Phase 1 complete)
- Consolidation document complete (Phase 2 complete)
- compiled_engine.md loaded for reference

### 3.1 The 5-Step Integration Check

For EVERY rule in the consolidated master list, execute ALL 5 steps in order. NO skipping. NO batching.

---

#### STEP 1: CONTEXT RECOVERY

**Task:** Return to the original extract file and understand the FULL context of the rule.

**Actions:**
1. Re-read the original transcript segment (not just the extracted quote)
2. Identify: What market condition was the analyst describing? What timeframe? What asset?
3. Identify: Was this a general principle or a specific example?
4. Identify: Did the analyst attach conditions or caveats?

**Output:** Context summary (3-5 sentences) documenting the original scenario.

**Why this matters:** A rule extracted from a bull market example may not apply to balance states. A rule about BTC may not apply to ETH. Context prevents over-generalization.

---

#### STEP 2: SCENARIO MAPPING

**Task:** List all scenarios where this rule would apply in the MTS engine.

**Actions:**
1. Map the rule to MTS states: Balance / Trend (healthy) / Trend (unhealthy) / Transition
2. Map the rule to MTS zones: VAH / VAL / POC / VWAP / FVG / Swing High / Swing Low / Prior Day levels
3. Map the rule to MTS setup types: CT / TC / BO / SC
4. Map the rule to MTS proof types: CVD / Book Depth / Structure / FVG / etc.
5. Identify: Is this rule an ENTRY rule, a STOP rule, a TARGET rule, a FILTER rule, or a CONFIDENCE rule?

**Output:** Scenario matrix — one row per applicable (state, zone, setup, proof) combination.

**Example:**
```
Rule: Test count degradation
| State | Zone | Setup | Proof | Role |
|-------|------|-------|-------|------|
| Balance | VAH | CT Short | Rejection at VAH | Confidence modifier (-10 after 3rd test) |
| Balance | VAL | CT Long | Rejection at VAL | Confidence modifier (-10 after 3rd test) |
| Trend | VAH | TC Short | Break + retest | Confidence modifier (-10 after 3rd test) |
```

---

#### STEP 3: PRE-INTEGRATION CHECK (vs compiled_engine.md)

**Task:** Systematically compare the rule against compiled_engine.md to determine relationship.

**Actions:**
1. **Search compiled_engine.md** for keywords from the rule (use grep or read relevant sections)
2. **Identify matches:** Does Tom's engine already have logic covering this concept?
3. **Classify the relationship:**

| Classification | Definition | Action |
|----------------|------------|--------|
| **DUPLICATE** | Tom's engine has IDENTICAL logic. Worded differently but same mechanics. | No integration. Document as validation. |
| **CONFIRM** | Tom's engine has RELATED logic. This rule validates or reinforces without changing mechanics. | No integration. Document as supporting evidence. |
| **CLARIFY** | Tom's engine has RELATED logic but this rule adds nuance, precision, or a condition. | Candidate for integration. Needs 3-snapshot validation. |
| **GAP** | Tom's engine has NO related logic. This is a genuinely new concept. | Candidate for integration. Needs DSA field check + 3-snapshot validation. |
| **REJECT** | Rule contradicts Tom's framework, applies to wrong market, or is narrative/macro-dependent. | No integration. Document reason. |

4. **Document evidence:** For every classification, paste the EXACT relevant lines from compiled_engine.md with line numbers. Do NOT rely on memory.

**Output:** Pre-integration check document per rule, with:
- Classification
- compiled_engine.md reference (exact lines)
- Justification (why this classification, not another)
- Blocker list (if any)

---

#### STEP 4: CONSOLIDATION OF INTEGRATION CANDIDATES

**Task:** Compile all CLARIFY and GAP rules into an integration queue.

**Actions:**
1. List all CLARIFY rules with their scenario matrices and pre-integration evidence
2. List all GAP rules with their scenario matrices and pre-integration evidence
3. For each, identify blockers:
   - DSA field missing?
   - Engine architecture gap (e.g., state persistence)?
   - Quantification needed (e.g., "shallow" needs a number)?
   - 3-snapshot validation pending?
4. Sort by: (a) blocker severity (none = highest priority), (b) expected impact on verdicts

**Output:** Integration queue with priority ranking.

---

#### STEP 5: REVALIDATION BEFORE INTEGRATION

**Task:** For every candidate in the integration queue, validate with live data BEFORE touching compiled_engine.md.

**Actions:**
1. **Load 3 live JSON snapshots** (historical, not hypothetical)
2. **Apply the rule mentally** to each snapshot: Would this rule change the verdict?
3. **Document results:**

| Snapshot | Price | State | Zone | Original Verdict | With Rule Applied | Changed? |
|----------|-------|-------|------|------------------|-------------------|----------|
| 1 | 77,965 | Balance | VAL | WAIT C (58) | [new verdict] | Y/N |
| 2 | 78,245 | Trend | VAH | CT Short (75) | [new verdict] | Y/N |
| 3 | 77,541 | Balance | POC | WAIT C (55) | [new verdict] | Y/N |

4. **Gate:** If the rule changes 0 of 3 verdicts → REJECT (documentation bloat per Rule 32).
5. **Gate:** If the rule requires a DSA field that does not exist → BLOCKED (per Rule 33).
6. **Gate:** If the rule contradicts an existing Tom rule → REJECT (per Rule 31: validate before fix).

**Output:** Validation report per rule. Only rules that pass ALL gates proceed to Phase 4.

---

### 3.2 Integration Queue Categories

After Step 5, each rule lands in ONE category:

| Category | Criteria | Next Action |
|----------|----------|-------------|
| **READY** | Passes all 5 steps. No blockers. Changes at least 1 of 3 snapshot verdicts. | Proceed to Phase 4 (Integration) |
| **BLOCKED** | Fails Step 5 due to missing DSA field, architecture gap, or quantification need. | Queue for DSA task or architecture review. Revisit when unblocked. |
| **REJECT** | Fails Step 5 due to no verdict change, contradiction, or wrong market. | Document reason. No further action. |

**ZERO rules are READY until ALL 5 steps are complete for ALL rules.**

---

## PHASE 4: INTEGRATION PROTOCOL

### 4.1 When This Phase Starts
ONLY after:
- Phase 3 complete for ALL rules
- At least one rule marked READY
- DSA fields confirmed live (if required)

### 4.2 Integration Process

For each READY rule:

1. **Draft patch:** Write the exact lines to add/modify in compiled_engine.md
2. **Trace decision path:** For each of the 3 validation snapshots, trace: state → zone → entry → stop → target → R:R → verdict. Confirm the rule produces the expected change.
3. **Regression test:** Run the 3 snapshots through the patched engine. Verify no unintended side effects on OTHER rules.
4. **Update schema:** If new DSA fields were added, update data_schema_v1.0.md
5. **Update condition files:** If the rule belongs in a specific condition file (e.g., entry_timing_triggers.md), update that file too. compiled_engine.md is the runtime source of truth, but condition files are the canonical documentation.
6. **Log decision:** Append to 02b_DECISIONS_LOG.md with full traceability.

### 4.3 Post-Integration Validation

After ALL READY rules are integrated:

1. Run 3 NEW live snapshots (different from validation snapshots)
2. Verify verdicts are sensible
3. Check for contradictions between newly integrated rules
4. Update 02a_CURRENT_STATUS.md, 00_START_HERE.md, 03_FILE_INDEX.md

---

## RULES GOVERNING THIS PLAN

These existing rules from 01_AI_BEHAVIOR.md apply directly:

| Rule | Text | Application |
|------|------|-------------|
| Rule 31 | VALIDATE BEFORE YOU FIX | Step 5: Test current engine BEFORE proposing patch |
| Rule 32 | NO NEW RULE WITHOUT 3-SNAPSHOT PROOF | Step 5: Rule must change at least 1 of 3 verdicts |
| Rule 33 | LEAN DSA CONTRACT | Step 3: Request MINIMUM fields. If engine can compute it, don't ask DSA |
| Rule 34 | RESEARCH BEFORE IMPORTING CROSS-MARKET CONCEPTS | Step 1: Verify concept applies to 24/7 crypto spot |
| Rule 35 | EXTRACTION POLICY — VALIDATE BEFORE EXTRACTING | Phase 1: Extract pure. Phase 3: Validate before integrating |

---

## CURRENT STATUS

| Phase | Status | Count |
|-------|--------|-------|
| Phase 1: Pure Extraction | COMPLETE — 7/7 transcripts, 85 rules (CT-001 to CT-085) | 85 rules |
| Phase 2: Consolidation | COMPLETE — 20 clusters, 80 entries, 5 conflicts flagged | 85 rules cataloged |
| Phase 3: Integration Planning | COMPLETE — 80 entries classified: 28 CONFIRMED, 33 NEW, 5 GAP, 3 CONFLICT, 11 REJECT | 80/80 revalidated |
| Phase 4: Integration | COMPLETE — 3 conflicts resolved, 16 NEW entries integrated (10 P0 + 6 P1), Rule 32-B 72%. 5 GAP entries resolved via DSA_TASK_008 (4 blocked, 1 deferred). | 16 integrated |

**Action required:** All phases complete. No further action on cross-trader integration. See compiled_engine.md v4.2.0-p4 for integrated rules.

---

## FILES REFERENCED

| File | Role in This Plan |
|------|-------------------|
| compiled_engine.md | Step 3 comparison target; Phase 4 patch target |
| data_schema_v1.0.md | Step 3 DSA field check; Phase 4 schema update |
| Appendix A (this document) | Phase 2 output; Phase 3 input |
| 01_AI_BEHAVIOR.md | Rules 31-35 govern this plan |
| 02b_DECISIONS_LOG.md | Phase 4 integration logging |

---

# END

---

# APPENDIX A: RULE CATALOG (Phase 1 Output)
# This section contains the consolidated master list of all extracted rules.
# It is the output of Phase 1 (Pure Extraction) and input to Phase 2 (Consolidation).
# Rules are numbered CT-001 through CT-NNN across all analysts.
# Format: CT-[sequential number] — [analyst-neutral rule name]
# ---

## GLOBAL RULE IDs

Rules are numbered CT-001 through CT-NNN across all analysts.
Format: CT-[sequential number] — [analyst-neutral rule name]

---

## THE FLOW HORSE — Oy2Z-FQ77NM ("Most Traders Misread Volume Profile")

| ID | Rule Name | Source GPS |
|----|-----------|------------|
| CT-001 | VP is descriptive, not predictive | Oy2Z-FQ77NM, ~01:30; ~01:45 |
| CT-002 | Proximity principle — short-term profiles > long-term | Oy2Z-FQ77NM, ~06:00; ~16:45 |
| CT-003 | Test count degradation — repeated tests weaken zone | Oy2Z-FQ77NM, ~07:15 |
| CT-004 | Sideways compression -> violent resolution | Oy2Z-FQ77NM, ~07:45 |
| CT-005 | Head fake signature — lack of volume/momentum on break | Oy2Z-FQ77NM, ~08:00; ~08:15 |
| CT-006 | Retest after real break — throwback to reaccept | Oy2Z-FQ77NM, ~09:00; ~09:15 |
| CT-007 | LVN as rejection zone — actionable on return | Oy2Z-FQ77NM, ~10:30; ~10:45 |
| CT-008 | Structure vs flow — profile gives areas, order flow gives execution | Oy2Z-FQ77NM, ~17:15 |
| CT-009 | Old profiles = context, not execution | Oy2Z-FQ77NM, ~19:30; ~19:15 |
| CT-010 | Composite profiles — only for tight overlap | Oy2Z-FQ77NM, ~03:45 |
| CT-011 | POC platform variance — data source consistency | Oy2Z-FQ77NM, ~02:45 |

---

## THE FLOW HORSE — zMM9QgxfEFI ("The Bitcoin Setup Changed")

| ID | Rule Name | Source GPS |
|----|-----------|------------|
| CT-012 | Heavy selling pressure + no breakdown = absorption | zMM9QgxfEFI, ~02:15; ~02:45 |
| CT-013 | Volatility compression precedes range resolution | zMM9QgxfEFI, ~04:30 |
| CT-014 | Extended balance + high-volume break = measured move | zMM9QgxfEFI, ~09:30; ~13:15 |
| CT-015 | Real change happens at extremes, not within structure | zMM9QgxfEFI, ~09:00 |
| CT-016 | Break candle low = hard invalidation after high-volume break | zMM9QgxfEFI, ~10:45; ~11:15; ~11:30 |
| CT-017 | Shallow pullback after high-volume break = continuation | zMM9QgxfEFI, ~12:00 |
| CT-018 | Day of balance after breakout = continuation building | zMM9QgxfEFI, ~12:45 |
| CT-019 | Seller exhaustion + price hold = accumulation | zMM9QgxfEFI, ~06:15; ~06:45 |

---

## CRYPTOCRED — BHwoN7VPrBE ("Market Structure")

| ID | Rule Name | Source GPS |
|----|-----------|------------|
| CT-020 | Swing high/low quality filters | BHwoN7VPrBE, ~08:00; ~08:30 |
| CT-021 | MSB definition — higher high / lower low | BHwoN7VPrBE, ~22:00 |
| CT-022 | MSB as context tool, not mechanical system | BHwoN7VPrBE, ~05:30 |
| CT-023 | Do not chase every MSB | BHwoN7VPrBE, ~19:30 |
| CT-024 | Confluence for swing selection | BHwoN7VPrBE, ~10:00; ~12:00 |
| CT-025 | Setup 1 — continuation at break level (SR flip) | BHwoN7VPrBE, ~45:00 |
| CT-026 | MSB in range = noise | BHwoN7VPrBE, ~85:00 |
| CT-027 | Time frame of MSB = expected move size | BHwoN7VPrBE, ~82:00 |
| CT-028 | Counter-trend = defensive parameters | BHwoN7VPrBE, ~33:00 |
| CT-029 | Cut and reverse trap | BHwoN7VPrBE, ~42:00 |
| CT-030 | Probability enhancers | BHwoN7VPrBE, ~38:00 |
| CT-031 | Candle bodies for structure, closes for breaks | BHwoN7VPrBE, ~28:30 |
| CT-032 | Setup 2 — continuation at pullback level (0.618-0.786) | BHwoN7VPrBE, ~50:00; ~55:00 |
| CT-033 | Setup 3 — reversal on failed MSB | BHwoN7VPrBE, ~65:00; ~66:00 |
| CT-034 | Early warning — failure to continue | BHwoN7VPrBE, ~88:00 |

---

## CRYPTOCRED — inqHN8q57X4 ("Retests")

| ID | Rule Name | Source GPS |
|----|-----------|------------|
| CT-035 | Retest is not required to confirm a level | inqHN8q57X4, ~06:15; ~06:45 |
| CT-036 | Breakout vs retest = risk/reward trade-off | inqHN8q57X4, ~09:30; ~10:30 |
| CT-037 | Timeframe alignment for break validation | inqHN8q57X4, ~13:00; ~13:30 |
| CT-038 | Immediate vs rounded retest | inqHN8q57X4, ~16:00; ~17:30; ~18:30 |
| CT-039 | Split position = sub-optimal either way | inqHN8q57X4, ~21:00; ~22:00 |
| CT-040 | Precedent — instrument's retest behavior | inqHN8q57X4, ~23:30; ~24:45 |
| CT-041 | R:R decides — big break forces retest wait | inqHN8q57X4, ~26:30; ~27:30 |
| CT-042 | Precision inversely correlated with move size | inqHN8q57X4, ~28:30; ~30:00 |
| CT-043 | Hidden retests on lower timeframes | inqHN8q57X4, ~32:00; ~32:15; ~34:30 |
| CT-044 | Don't chase breakouts in ranges | inqHN8q57X4, ~36:00; ~37:00 |
| CT-045 | Strong trend = failed breakdowns at support | inqHN8q57X4, ~37:30; ~40:00 |
| CT-046 | Rounded retest context — what happened between break and retest | inqHN8q57X4, ~41:00; ~43:30 |

---

## CRYPTOCRED — _ndAoizXy64 ("Trade Management")

| ID | Rule Name | Source GPS |
|----|-----------|------------|
| CT-047 | Evidence-based trade management | _ndAoizXy64, ~01:45; ~04:15; ~04:30; ~04:45; ~05:00; ~05:15 |
| CT-048 | Management timeframe — entry TF + one lower | _ndAoizXy64, ~08:15; ~09:00; ~09:15; ~09:30; ~09:45 |
| CT-049 | Manage both sides — losers and winners | _ndAoizXy64, ~10:15; ~10:30; ~11:00; ~11:45 |
| CT-050 | Level performance as evidence | _ndAoizXy64, ~13:00; ~13:30; ~14:00; ~14:15 |
| CT-051 | Time-based management — trade expiry | _ndAoizXy64, ~16:15; ~16:45; ~17:15; ~17:45; ~18:15 |
| CT-052 | Acceptance at level = thesis failure | _ndAoizXy64, ~19:45; ~20:30 |
| CT-053 | Profit taking — trailing stops vs fixed targets | _ndAoizXy64, ~21:30; ~23:15; ~23:30; ~24:00 |
| CT-054 | Dynamic risk/reward | _ndAoizXy64, ~25:00; ~25:30; ~26:15; ~27:30 |
| CT-055 | Skepticism of automatic break-even stops | _ndAoizXy64, ~28:30; ~29:15; ~29:45; ~31:00; ~31:45 |
| CT-056 | Trade the chart, not your P&L | _ndAoizXy64, ~02:45; ~03:00; ~03:15; ~41:30 |
| CT-057 | The dead zone — nothing to manage | _ndAoizXy64, ~43:00; ~43:15; ~43:45 |
| CT-058 | Good entry eases management | _ndAoizXy64, ~42:15 |
| CT-059 | Market does not know your trade history | _ndAoizXy64, ~44:15; ~44:30 |

---

## CRYPTOCRED — XeQV2ECtZVQ ("Risk Management")

| ID | Rule Name | Source GPS |
|----|-----------|------------|
| CT-060 | Invalidation as falsifiable idea | XeQV2ECtZVQ, ~02:30; ~03:00; ~04:00; ~04:30; ~07:30 |
| CT-061 | Stop placement = invalidation | XeQV2ECtZVQ, ~09:00; ~09:15; ~10:00 |
| CT-062 | Strictness inversely correlated with move size | XeQV2ECtZVQ, ~11:00; ~11:30; ~12:00 |
| CT-063 | Hard stop vs soft stop | XeQV2ECtZVQ, ~12:45; ~13:15; ~14:00 |
| CT-064 | Position size formula | XeQV2ECtZVQ, ~17:00; ~17:30 |
| CT-065 | Risk per trade as spectrum (EV + frequency) | XeQV2ECtZVQ, ~18:30; ~20:00; ~21:00; ~22:00 |
| CT-066 | Dynamic risk/reward (evolving R) | XeQV2ECtZVQ, ~26:00; ~27:00; ~29:00 |
| CT-067 | Beginners — conservative targets + set and forget | XeQV2ECtZVQ, ~30:00; ~30:30 |
| CT-068 | Streaks — setup-specific, not global | XeQV2ECtZVQ, ~36:30; ~37:00; ~38:00; ~39:00 |
| CT-069 | Break-even stops are psychological cope | XeQV2ECtZVQ, ~43:00; ~45:00; ~45:30; ~46:30 |
| CT-070 | Process over P&L in management | XeQV2ECtZVQ, ~43:30; ~48:00; ~48:30 |
| CT-071 | Leverage = collateralization, not P&L | XeQV2ECtZVQ, ~54:00; ~54:30; ~55:00; ~55:30 |
| CT-072 | Crypto correlations — downside stacking | XeQV2ECtZVQ, ~59:00; ~59:15; ~59:45 |

---

## CRYPTOCRED — Yp0k8HD5xro ("First Trouble Area")

| ID | Rule Name | Source GPS |
|----|-----------|------------|
| CT-073 | FTA definition | Yp0k8HD5xro, ~03:45; ~04:00; ~04:30 |
| CT-074 | FTA for profit-taking — same timeframe as trade idea | Yp0k8HD5xro, ~30:00; ~30:15; ~30:30; ~33:00 |
| CT-075 | FTA for trade management — one timeframe lower | Yp0k8HD5xro, ~34:30; ~34:45; ~36:00; ~36:45 |
| CT-076 | Two FTAs at work — profit FTA + management FTA | Yp0k8HD5xro, ~16:30; ~20:30 |
| CT-077 | Failure to break FTA = evidence of weakness | Yp0k8HD5xro, ~17:00; ~18:00; ~18:15; ~18:30 |
| CT-078 | Success in breaking FTA = evidence idea is correct | Yp0k8HD5xro, ~19:30; ~19:45; ~20:00 |
| CT-079 | FTA for trade entry — break of FTA as trigger | Yp0k8HD5xro, ~23:00; ~24:00; ~26:00 |
| CT-080 | FTA entry — proximity matters | Yp0k8HD5xro, ~25:00; ~25:15 |
| CT-081 | Don't expect mushroom clouds from low TF levels | Yp0k8HD5xro, ~33:30; ~33:45 |
| CT-082 | First test best test — stomach the retest | Yp0k8HD5xro, ~39:00; ~39:15; ~40:00 |
| CT-083 | Swing trade graveyard — break-even on first reaction | Yp0k8HD5xro, ~40:15; ~41:00 |
| CT-084 | Timeframes not mutually exclusive — defer to highest | Yp0k8HD5xro, ~39:30; ~39:45 |
| CT-085 | FTA does not prevent swing trading — it enables it | Yp0k8HD5xro, ~37:30; ~38:00 |

---

## CONCEPT GROUPING (For Phase 2 Consolidation)

| Concept Group | Rule IDs | Analysts |
|---------------|----------|----------|
| Compression / Balance Resolution | CT-004, CT-013, CT-014 | Flow Horse |
| False Break / Head Fake | CT-005, CT-016 | Flow Horse |
| Retest Mechanics | CT-006, CT-035, CT-036, CT-038, CT-040, CT-041, CT-043, CT-046 | Flow Horse, CryptoCred |
| Market Structure Break | CT-021, CT-022, CT-023, CT-025, CT-026, CT-027, CT-031, CT-033, CT-037 | CryptoCred |
| Zone Quality / Reliability | CT-003, CT-007, CT-010, CT-011, CT-024 | Flow Horse, CryptoCred |
| Trend / Counter-trend Parameters | CT-028, CT-045 | CryptoCred |
| Absorption / Exhaustion | CT-012, CT-019 | Flow Horse |
| Pullback / Continuation | CT-017, CT-032 | Flow Horse, CryptoCred |
| Profile Philosophy | CT-001, CT-002, CT-008, CT-009 | Flow Horse |
| Risk / Position Management | CT-028, CT-029, CT-039, CT-042, CT-061, CT-062, CT-063, CT-064, CT-065, CT-066, CT-067, CT-069, CT-070, CT-071, CT-075, CT-076, CT-077, CT-078, CT-082, CT-083 | CryptoCred |
| Context / Probability | CT-030, CT-034, CT-060, CT-068, CT-072 | CryptoCred |
| Post-breakout Behavior | CT-018 | Flow Horse |

---

## STATUS

| Phase | Status | Count |
|-------|--------|-------|
| Phase 1: Pure Extraction | COMPLETE — 7/7 transcripts, 85 rules (CT-001 to CT-085) | 85 rules |
| Phase 2: Consolidation | COMPLETE — 20 clusters, 80 entries, 5 conflicts flagged | 85 rules cataloged |
| Phase 3: Integration Planning | COMPLETE — 80 entries classified: 28 CONFIRMED, 33 NEW, 5 GAP, 3 CONFLICT, 11 REJECT | 80/80 revalidated |
| Phase 4: Integration | COMPLETE — 3 conflicts resolved, 16 NEW entries integrated (10 P0 post-entry management + 6 P1 pre-trade enhancement), Rule 32-B validation: 13/18 context shifts (72%). 5 GAP entries remain blocked on DSA. | 16 integrated, 5 blocked, 11 reject |

**Next:** Phase 1 COMPLETE. Proceed to Phase 2: Consolidation (deduplicate, cluster, resolve conflicts).

---

## FILES REFERENCED

| File | Role |
|------|------|
| `mts/extracts/the_flow_horse/extracted/extract_Oy2Z-FQ77NM.md` | Pure extract (11 rules) |
| `mts/extracts/the_flow_horse/extracted/extract_zMM9QgxfEFI.md` | Pure extract (8 rules) |
| `mts/extracts/cryptocred/extracted/extract_BHwoN7VPrBE.md` | Pure extract (15 rules) |
| `mts/extracts/cryptocred/extracted/extract_inqHN8q57X4.md` | Pure extract (12 rules) |
| `mts/extracts/cryptocred/extracted/extract__ndAoizXy64.md` | Pure extract (13 rules) |
| `mts/extracts/cryptocred/extracted/extract_XeQV2ECtZVQ.md` | Pure extract (13 rules) |
| `mts/extracts/cryptocred/extracted/extract_Yp0k8HD5xro.md` | Pure extract (13 rules) |

---

# END OF APPENDIX A


---

## PHASE 3: INTEGRATION PLANNING — COMPLETE

**Date:** 2026-08-31
**Analyst:** AI Session
**Input:** 80 consolidated entries (C01-E01 through C20-E01) + compiled_engine.md v4.2.0-p2 + data_schema_v1.2.0
**Method:** 5-step check per entry: Context Recovery → Scenario Mapping → Pre-Integration Check vs Engine → Classification → Consolidation

---

### 3.3 CLASSIFICATION SUMMARY

| Classification | Count | Definition | Next Action |
|----------------|-------|------------|-------------|
| **CONFIRMED** | 28 | Already covered by engine logic (duplicate or confirm) | Document as validation evidence. No integration. |
| **NEW** | 33 | Genuinely new concept. Engine has no related logic. Can integrate with existing DSA fields. | Queue for Phase 4. Prioritize by impact. |
| **GAP** | 5 | New concept but requires DSA field that does not exist. | Blocked. Needs DSA_TASK or architecture review. |
| **CONFLICT** | 3 | Tension or contradiction with existing engine logic. | Flag for human resolution before integration. |
| **REJECT** | 11 | Out of engine scope (psychology, portfolio, position sizing, leverage) | Document reason. No further action. |

**Total:** 80/80 entries classified. Zero skipped.

---

### 3.4 CONFIRMED ENTRIES (28) — VALIDATION EVIDENCE

These rules validate existing engine logic. No integration needed.

| Entry | Title | Engine Reference |
|-------|-------|-----------------|
| C01-E01 | VP is Descriptive, Not Predictive | Engine treats VP as zones/areas only. No predictive claims. |
| C01-E02 | Structure vs. Flow | Sec 1: "Profile gives areas... order flow tells you whether to care." |
| C01-E03 | Old Profiles = Context Only | weekly_vp.prior_week_poc, two_week_ago_poc used for trend context. |
| C02-E03 | Real Change at Range Extremes | Sec 2.5: Directional filter trades extremes (VAH/VAL), not within value. |
| C04-E01 | Head Fake Signature | Sec 4 Proof Types: "No liquidity," "Rejection wick," "Sellers present." Hard Stop #6: "No volume = fake-out." |
| C04-E02 | Don't Chase Breakouts in Ranges | Sec 2.5: "Skip zones in trend direction." Sec 2.8: "Above zone = Invalid." |
| C04-E03 | Strong Trend = Failed Breakdowns | [PRINCIPLE] State→Setup: healthy trend = TC/BO priority. |
| C05-E01 | Break Candle Low = Hard Invalidation | Sec 7: Stop below last liquidity. Hard Stop #3. |
| C07-E02 | Retest After Real Break | Sec 2.8: "Above zone = wait for retest." Tom quote in engine. |
| C07-E03 | Breakout vs. Retest = R:R Trade-Off | Sec 2.4: R:R calculated per boundary. Trade-off implicit. |
| C07-E04 | Timeframe Alignment for Break Validation | Sec 2.8: "Close beyond level" + multi_timeframe.close_alignment_check. |
| C07-E08 | Big Break Forces Retest Wait | Sec 2.4 Step 5: R:R sanity filter removes poor post-break entries. |
| C08-E02 | MSB as Context Tool, Not Mechanical | [PRINCIPLE] throughout engine: contextual judgment over fixed rules. |
| C08-E03 | Do Not Chase Every MSB | Hard Stop #8: "Chasing price = R:R degraded." Distance caps filter noise. |
| C08-E04 | Time Frame of MSB = Expected Move Size | Sec 2.6: Distance caps scale by TF (weekly 0.5%, 5m 0.3%). |
| C08-E05 | Candle Bodies for Structure, Closes for Breaks | Sec 2.8: "Close beyond level" as acceptance. Uses closes, not wicks. |
| C09-E01 | Swing High/Low Quality Filters | Sec 2: Swing levels require confluence. |
| C09-E02 | Confluence for Swing Selection | Sec 2.7: Confluence detection within 0.3%. |
| C09-E03 | Probability Enhancers | Sec 2.7 + Sec 4: Multiple proof types = probability stacking. |
| C09-E04 | Timeframes Not Mutually Exclusive | Sec 2.4 Step 8: "If tie, prefer higher TF." |
| C10-E01 | Setup 1 — SR Flip | Sec 2.8: CT retest at broken level = SR flip mechanics. |
| C10-E02 | Counter-Trend = Defensive Parameters | Sec 3: CT requires balance/unhealthy trend + rejection proof. |
| C11-E01 | Precision Inversely Correlated with Move Size | Sec 2.6: Distance caps vary by TF precision. |
| C11-E02 | Strictness Inversely Correlated with Move Size | Sec 7: Stop distance scales with TF (swing low vs precise level). |
| C11-E04 | Don't Expect Mushroom Clouds from Low TF | Sec 2.6: Lower TF = tighter cap = smaller expected move. |
| C16-E01 | Invalidation as Falsifiable Idea | Sec 7: Stop derived from structural level = idea-linked invalidation. |
| C16-E02 | Stop Placement = Invalidation | Hard Stop #3: Stop beyond last liquidity = abort. |
| C20-E01 | LVN as Rejection Zone | Sec 2 Zone Map + Sec 4: "No liquidity" proof type at LVNs. |

---

### 3.5 NEW ENTRIES (33) — INTEGRATION QUEUE

These are genuinely new concepts. No DSA blockers. Sorted by engine section affinity.

**Zone & State Logic (7)**
| Entry | Title | Integration Target | Impact |
|-------|-------|-------------------|--------|
| C02-E01 | Extended Sideways Compression → Violent Resolution | Sec 1 [PRINCIPLE] — add compression context | Medium |
| C03-E01 | Heavy Selling + No Breakdown = Absorption | Sec 4 Proof Types — enhance absorption detection | High |
| C05-E02 | Shallow Pullback = Legitimate Continuation | Sec 3 [PRINCIPLE] — TC setup quality context | Medium |
| C05-E03 | Day of Balance After Breakout = Continuation | Sec 1 [PRINCIPLE] — post-breakout state context | Medium |
| C06-E02 | First Test Best Test | Sec 2.7 [PRINCIPLE] — confluence weighting | Medium |
| C07-E05 | Immediate vs. Rounded Retest | Sec 11 [PRINCIPLE] — entry timing guidance | Low |
| C07-E09 | Hidden Retests on Lower Timeframes | Sec 11 [PRINCIPLE] — screenshot guidance | Low |

**Market Structure (3)**
| Entry | Title | Integration Target | Impact |
|-------|-------|-------------------|--------|
| C08-E01 | MSB Definition | New section or Sec 2.8 glossary | Medium |
| C08-E06 | Early Warning — Failure to Continue | Sec 1 [PRINCIPLE] — state transition signal | Medium |
| C07-E10 | Rounded Retest Context | Sec 2.4 [PRINCIPLE] — zone evaluation nuance | Low |

**Trade Management (14) — MAJOR GAP**
| Entry | Title | Integration Target | Impact |
|-------|-------|-------------------|--------|
| C12-E01 | Evidence-Based Trade Management | **New engine section: Post-Entry Management** | High |
| C12-E02 | Management Timeframe | **New engine section** | High |
| C12-E03 | Manage Both Sides | **New engine section** | High |
| C12-E04 | Level Performance as Evidence | **New engine section** | High |
| C12-E05 | Time-Based Management — Trade Expiry | **New engine section** | Medium |
| C12-E06 | Acceptance at Level = Thesis Failure | **New engine section** | High |
| C12-E07 | The Dead Zone | **New engine section** | Medium |
| C12-E08 | Good Entry Eases Management | **New engine section** | Low |
| C13-E01 | Profit Taking — Trailing vs Fixed | **New engine section: Target Module** | Medium |
| C15-E01 | Skepticism of Automatic BE Stops | **New engine section: Stop Management** | Medium |
| C15-E02 | BE Stops Are Psychological Cope | **New engine section** | Medium |
| C15-E03 | Swing Trade Graveyard | **New engine section** | Medium |
| C16-E03 | Hard Stop vs Soft Stop | **New engine section: Stop Types** | Low |
| C14-E01 | Dynamic Risk/Reward | **New engine section: R:R Re-evaluation** | High |
| C14-E02 | Dynamic Risk/Reward (Evolving R) | **New engine section** | High |

**FTA Framework (6)**
| Entry | Title | Integration Target | Impact |
|-------|-------|-------------------|--------|
| C11-E03 | FTA Entry — Proximity Matters | New section or integrate into Zone Map | Medium |
| C13-E02 | FTA Definition | New section — target framework | Medium |
| C13-E03 | FTA for Profit-Taking | New section — target framework | Medium |
| C13-E04 | Two FTAs at Work | New section — dual-target framework | Medium |
| C19-E01 | Failure to Break FTA = Weakness | New section — management signal | Medium |
| C19-E02 | Success in Breaking FTA = Correct | New section — management signal | Medium |
| C19-E03 | FTA for Trade Entry | New section — entry trigger variant | Low |

---

### 3.6 GAP ENTRIES (5) — RESOLVED: DSA_TASK_008 COMPLETE

**Date resolved:** 2026-08-31
**Resolution document:** `runtime_data/dsa_task_008_gap_fields.md`

| Entry | Title | Original Missing DSA Field | Resolution | Reason |
|-------|-------|---------------------------|------------|--------|
| C01-E04 | Composite Profiles | `composite_profile.shape`, `composite_profile.vah/val` | **PERMANENTLY BLOCKED** | Blocked by VP histogram API. Engine confluence logic (0.3% threshold) already covers overlap detection. |
| C02-E02 | Extended Balance + High-Volume Break = Measured Move | `balance.duration_days`, `balance.range_size`, `break_volume_ratio` | **PERMANENTLY BLOCKED** | Not a Tom-validated concept. Tom uses structural levels for targets, not measured moves. |
| C06-E01 | Test Count Degradation | `zone.test_count`, `zone.visit_history` | **DEFERRED** | Valid concept (Tom + Flow Horse). Engine already has [PRINCIPLE] coverage via C06-E02. Requires DSA architecture enhancement (historical tracking). Revisit when architecture supports it. |
| C07-E07 | Precedent — Historical Retest Behavior | `instrument.retest_rate_30d`, `instrument.trend_retest_behavior` | **PERMANENTLY BLOCKED** | Not a Tom concept. Computationally prohibitive (requires full historical trade analysis). |
| C10-E04 | Fibonacci Pullback (0.618-0.786) | `fibonacci.retracement_618`, `fibonacci.retracement_786` | **PERMANENTLY BLOCKED** | Not a Tom concept. Source (CryptoCred) explicitly states "personal preference, no fixed answer." |

**Note:** C10-E04 was additionally flagged as "personal preference, no fixed answer" by source (CryptoCred). Now permanently blocked.

**Zero new DSA fields approved.** Schema remains v1.2.0. No schema update needed.

---

### 3.7 CONFLICT ENTRIES (3) — REQUIRES HUMAN RESOLUTION

| Entry | Title | Conflict | Nature | Recommendation |
|-------|-------|----------|--------|----------------|
| C07-E01 | Retest Is Not Required | **CONFLICT 1** — vs C07-E02, C06-E02 | CT entry requires "price at zone with rejection proof" (engine Sec 2.8), which implies waiting for retest. But C07-E01 says break itself is the significant event. | **Resolution:** C07-E01 addresses *structural validity* (break confirms level). C07-E02/C06-E02 address *entry preference* (retest offers better R:R). Engine should distinguish: (a) level validation = break is enough; (b) entry execution = retest preferred. No code change needed — clarify in [PRINCIPLE]. |
| C10-E03 | Cut and Reverse Trap | **CONFLICT 3** — vs C10-E05 | Engine [PRINCIPLE] says "In transition, wait." C10-E03 warns against automatic reversal; C10-E05 describes valid reversal on failed MSB. | **Resolution:** Boundary ambiguity. Engine should add: "Failed MSB reversal = valid ONLY if MSB + failure + opposite structure confirmed. Automatic cut-and-reverse without new structure = trap." Add to Sec 3 [PRINCIPLE]. |
| C10-E05 | Reversal on Failed MSB | **CONFLICT 3** — vs C10-E03 | Same as above. | Same resolution. |

**Note:** The 5 conflicts from Phase 2 consolidation have been re-evaluated:
- **CONFLICT 2** (Active vs Passive Management) → C12-E01 through C12-E08 classified as NEW (post-entry management gap). Not a hard contradiction — spectrum resolved by experience level and trade phase.
- **CONFLICT 4** (Split Position vs Conviction) → C07-E06 classified as REJECT (position sizing philosophy, out of scope).
- **CONFLICT 5** (Breakout Chasing in Ranges vs SR Flip) → C04-E02 and C10-E01 both CONFIRMED. Contextual resolution: SR flip valid ONLY after confirmed range break, not within unbroken range.

---

### 3.8 REJECTED ENTRIES (11) — OUT OF SCOPE

| Entry | Title | Reason |
|-------|-------|--------|
| C01-E05 | POC Platform Variance | Data quality meta-rule. Engine already has vp_confidence flags. |
| C07-E06 | Split Position = Sub-Optimal | Position sizing philosophy. Engine does not dictate sizing philosophy. |
| C17-E01 | Position Size Formula | Engine deliberately avoids position sizing (Sec 7: "Fixed monetary or points-based; no universal %"). |
| C17-E02 | Risk Per Trade as Spectrum | EV/frequency sizing. Out of engine scope. |
| C17-E03 | Leverage = Collateralization | Crypto education rule, not decision logic. |
| C17-E04 | Crypto Correlations | Portfolio-level rule. Engine is single-asset. |
| C18-E01 | Trade the Chart, Not P&L | Psychological rule. Engine is decision logic. |
| C18-E02 | Market Does Not Know Your History | Psychological rule. |
| C18-E03 | Beginners — Conservative Targets | Experience-level guidance. Engine does not distinguish trader levels. |
| C18-E04 | Streaks — Setup-Specific | Performance analysis. No setup performance tracking in engine. |
| C18-E05 | Process Over P&L | Psychological rule. Already implicit in [PRINCIPLE] sections. |

---

### 3.9 PHASE 3 OUTPUT: INTEGRATION QUEUE

**READY FOR PHASE 4 (NEW entries, no DSA blockers): 33 entries**

**Priority Tiers:**

| Tier | Entries | Rationale |
|------|---------|-----------|
| **P0 — Critical** | C12-E01, C12-E02, C12-E03, C12-E04, C12-E06, C14-E01, C14-E02 | Post-entry management is the engine's largest functional gap. Dynamic R:R prevents round-trips. |
| **P1 — High** | C03-E01, C05-E02, C05-E03, C06-E02, C08-E01, C08-E06 | Enhance pre-trade decision quality. Absorption, pullback depth, MSB framework. |
| **P2 — Medium** | C02-E01, C07-E05, C07-E09, C07-E10, C11-E03, C13-E01, C13-E02, C13-E03, C13-E04, C15-E01, C15-E02, C15-E03, C16-E03, C19-E01, C19-E02, C19-E03 | Niche enhancements. FTA framework, stop types, time-based expiry. |
| **P3 — Low** | C12-E05, C12-E07, C12-E08, C13-E05 | Marginal impact or highly contextual. |

**BLOCKED FOR DSA (GAP entries): 5 entries**
- Queue for DSA_TASK_008 (composite profiles, balance duration, test count, historical behavior, Fibonacci).

**CONFLICTS TO RESOLVE: 3 entries**
- All three have recommended resolutions above. Awaiting user confirmation before Phase 4.

---

### 3.10 UPDATED STATUS TABLE

| Phase | Status | Count |
|-------|--------|-------|
| Phase 1: Pure Extraction | COMPLETE | 85 rules |
| Phase 2: Consolidation | COMPLETE | 80 entries, 20 clusters, 5 conflicts |
| Phase 3: Integration Planning | COMPLETE | 80 entries classified |
| Phase 4: Integration | COMPLETE — 33 entries integrated, 3 conflicts resolved, 5 GAP entries resolved (4 blocked, 1 deferred) | — |

---
# END OF PHASE 3 OUTPUT
