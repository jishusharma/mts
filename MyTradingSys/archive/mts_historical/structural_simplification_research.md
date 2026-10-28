# FILE: mts/research/structural_simplification_research.md
# READ ORDER: Before any simplification work begins
# PURPOSE: Research and plan for system/ folder structural simplification
# Date: 2026-09-03
# Status: ACTIVE — RESEARCH PHASE
# Canonical: /mnt/agents/output/upload_mirror/mts/research/structural_simplification_research.md
# ---

# STRUCTURAL SIMPLIFICATION RESEARCH
# Phase: Research → Design → Prototype → Validate → Migrate

---

## 1. PROBLEM STATEMENT

### Current State (Audited 2026-09-03)
| Metric | Value |
|--------|-------|
| Total files | ~145 |
| system/ files | 17 |
| system/ lines | ~2,836 |
| Redundant "next session" prompts | 5 variants |
| Version strings hardcoded | 20+ locations |
| Stale test count references found | 9 (now fixed) |
| Parallel session drift incidents | 3+ |

### Symptoms
1. **Version sprawl**: v4.2.0-p5 appears in 20+ files; updating one requires updating all
2. **Redundant prompts**: 5 different `04_NEXT_SESSION_PROMPT*` files, only 1 ever current
3. **Log bloat**: `02a_CURRENT_STATUS.md` contains 4 session end logs (should be status, not history)
4. **Cross-reference chains**: "READ ORDER: 3 of 8", "NEXT FILE: 02b" — fragile linked-list headers
5. **Parallel drift**: Multiple sessions write to different files with cached stale data

### Root Cause
The system grew organically. Each new need (bug hunt, drift fix, DSA task) spawned a new file. No architecture review ever asked: "Does this belong in an existing file?"

---

## 2. RESEARCH: WHAT HAS BEEN TRIED

### Attempt 1: File-per-concern (Current)
| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| 00_START_HERE.md | Entry point | ~120 | Active |
| 01_AI_BEHAVIOR.md | Behavior rules | ~1,200 | Active |
| 02a_CURRENT_STATUS.md | Status + logs | ~360 | Bloated |
| 02b_DECISIONS_LOG.md | Decision history | ~354 | Active |
| 02c_SESSION_END_SIGNOFF.md | Signoff template | ~180 | Template |
| 02d_AUDIT_LOG.md | Audit trail | ~200 | Stale |
| 03_FILE_INDEX.md | File inventory | ~207 | Auto-needed |
| 04_NEXT_SESSION_PROMPT.md | Main prompt | ~150 | Active |
| 04_NEXT_SESSION_PROMPT_BUGS.md | Bug hunt prompt | ~80 | Stale |
| 04_NEXT_SESSION_PROMPT_DSA008.md | DSA task prompt | ~60 | Stale |
| 04_NEXT_SESSION_PROMPT_DRIFT_FIX.md | Drift fix prompt | ~200 | Stale |
| 05_NORMS.md | Team norms | ~100 | Active |
| 06_SESSION_END_CHECKLIST.md | End checklist | ~200 | Template |
| session_end_logs.md | Historical logs | ~354 | Historical |
| COMPILED_DECISIONS.md | Decision reference | ~155 | Active |
| COMPILED_DECISIONS_TEST_PLAN.md | Decision tests | ~305 | Active |
| 00_PROJECT_INSTRUCTIONS.md | Project rules | ~120 | Superseded |

**Result**: 17 files, high cognitive load, parallel drift.

### Attempt 2: 3-File Monolith (Proposed by earlier session, REJECTED)
**Idea**: Collapse everything into START.md, ENGINE.md, DECISIONS.md.

**Why rejected**:
- START.md would be 300-400KB (unmanageable for AI reasoning)
- Loss of safe editing boundaries (edit risk rules → risk corrupting state classification)
- Session signoffs are append-only audit records — merging destroys chronological chain
- Research files contain *flagged* items not ready for integration

**Verdict**: Correctly identifies disease, prescribes wrong medicine.

### Attempt 3: 3-Tier Simplification (Proposed by parallel session)
**Idea**:
- Tier 1: Flatten `system/` → 4 files (START, ENGINE, DECISIONS, CHECKLIST)
- Tier 2: Archive `mts/conditions/` and completed `mts/research/`
- Tier 3: Rename `runtime_data/schema` only

**Why promising**:
- Preserves modularity where it matters (runtime, math, tests)
- Targets the actual problem (`system/` bloat)
- Achievable in ~85 files (from ~145)

**Open questions**:
- What happens to `02a_CURRENT_STATUS.md` session end logs?
- How does `03_FILE_INDEX.md` get auto-generated?
- What is the migration path for existing cross-references?

---

## 3. RESEARCH: PRIOR ART & PATTERNS

### Pattern A: README-Driven Development
**Source**: GitHub, open-source projects
**Idea**: One README.md per directory. No other top-level docs.
**Applied to MTS**:
- `system/README.md` = entry point + behavior + status
- `mts/runtime/README.md` = engine + math + state
- `mts/tests/README.md` = test plan + how to run
- `runtime_data/README.md` = schema + sample + tasks
**Pros**: Single file per directory, natural discovery
**Cons**: READMEs get huge; no separation of behavior vs status

### Pattern B: Diataxis Framework
**Source**: diataxis.fr (documentation system)
**Idea**: Four types of docs: Tutorials, How-To Guides, Reference, Explanation
**Applied to MTS**:
- Tutorial: `00_START_HERE.md` (one-page quickstart)
- How-To: `04_PER_JSON_GUIDE.md` (workflow steps)
- Reference: `compiled_engine.md` + `COMPILED_DECISIONS.md` (lookup tables)
- Explanation: `01_AI_BEHAVIOR.md` (why the system works this way)
**Pros**: Clear mental model, proven at scale
**Cons**: Doesn't solve the "too many files" problem directly

### Pattern C: Living Document
**Source**: RFC processes (IETF, Rust, Python)
**Idea**: One canonical doc per major component. Everything else is append-only history.
**Applied to MTS**:
- `SYSTEM_SPEC.md` = behavior + norms + checklist (living)
- `SYSTEM_HISTORY.md` = decisions + session logs + audits (append-only)
- `SYSTEM_STATUS.md` = current state only (overwritten per session)
**Pros**: Clear separation of "what is" vs "what was"
**Cons**: Requires discipline to not pollute the living doc

### Pattern D: Template + Instance
**Source**: CI/CD pipelines, form systems
**Idea**: One template file. Each session generates an instance.
**Applied to MTS**:
- `templates/session_start.md` = template with `{{variables}}`
- `instances/session_2026-09-03.md` = filled template for this session
- `templates/session_end.md` = signoff template
- `instances/signoff_2026-09-03.md` = filled signoff
**Pros**: No stale template variants. Each session gets fresh data.
**Cons**: Adds template engine complexity. Overkill for current scale.

---

## 4. DESIGN PRINCIPLES (Derived from Research)

### P1: Single Source of Truth
Every fact exists in exactly one file. All other files reference it.
| Fact | Canonical Location | Current Violations |
|------|-------------------|-------------------|
| Test count | `UNIT_TEST_PLAN.md` | Hardcoded in 10+ files (now fixed) |
| Version | `compiled_engine.md` header | Hardcoded in 20+ files |
| Last price | `current_market_state.md` | Hardcoded in 00_START_HERE, 02a |
| Card list | `02a_CURRENT_STATUS.md` table | Duplicated in 00_START_HERE |
| Decision log | `02b_DECISIONS_LOG.md` | Summarized in session_end_logs |

### P2: Append-Only History
Historical records are never edited. They are appended or archived.
| Record Type | Current | Proposed |
|-------------|---------|----------|
| Session end logs | In 02a (edited) | Separate `session_end_logs.md` (append-only) |
| Decision history | 02b (append-only) | Keep as-is |
| Audit trail | 02d (stale) | Archive or merge into history |

### P3: Overwrite-Only Status
Current state is overwritten, not appended.
| Status Type | Current | Proposed |
|-------------|---------|----------|
| Current price | In 00_START_HERE + 02a | `current_market_state.md` only |
| System version | In 00 + 01 + 02a + 03 | `compiled_engine.md` header only |
| Last card | In 00 + 02a | `02a_CURRENT_STATUS.md` only |

### P4: No Redundant Prompts
One "next session" prompt. Variants are parameterized, not separate files.
| Current | Proposed |
|---------|----------|
| 04_NEXT_SESSION_PROMPT.md | `04_NEXT_SESSION_PROMPT.md` (one file) |
| 04_NEXT_SESSION_PROMPT_BUGS.md | Section in main prompt: "IF bug hunt mode..." |
| 04_NEXT_SESSION_PROMPT_DSA008.md | Section in main prompt: "IF DSA task mode..." |
| 04_NEXT_SESSION_PROMPT_DRIFT_FIX.md | Section in main prompt: "IF drift fix mode..." |

### P5: Auto-Generated Index
`03_FILE_INDEX.md` is generated, not hand-maintained.
| Current | Proposed |
|---------|----------|
| Hand-edited 207-line file | Script: `ls -R` + `wc -l` + metadata extraction |
| Updated when someone remembers | Updated at session end automatically |

---

## 5. PROPOSED ARCHITECTURE (Research-Backed)

### Option A: 4-File system/ (Recommended)

| File | Merges From | Type | Lines (est) |
|------|------------|------|-------------|
| `START.md` | 00_START_HERE.md + 01_AI_BEHAVIOR.md (behavior rules only) | Living | ~400 |
| `ENGINE.md` | compiled_engine.md + 04_PER_JSON_GUIDE.md | Living | ~500 |
| `DECISIONS.md` | 02b_DECISIONS_LOG.md + COMPILED_DECISIONS.md | Append-only | ~600 |
| `CHECKLIST.md` | 06_SESSION_END_CHECKLIST.md + 05_NORMS.md | Living | ~250 |

**Delete**: All `04_NEXT_SESSION_PROMPT*` variants (merge into START.md sections), 02a (replaced by auto-generated status), 02c (template → CHECKLIST.md), 02d (archive), 00_PROJECT_INSTRUCTIONS.md (superseded), 03_FILE_INDEX.md (auto-generate).

**Archive**: `mts/conditions/` (7 files, ~178KB), completed `mts/research/`.

**Keep**: `mts/runtime/`, `mts/tests/`, `extracts/`, `mts/cards/`, `runtime_data/` (as-is).

**Result**: ~145 files → ~85 files. system/ 17 files → 4 files.

### Option B: 5-File system/ (Conservative)

Same as Option A, but keep `02a_CURRENT_STATUS.md` as a separate `STATUS.md` file.

| File | Purpose |
|------|---------|
| `START.md` | Entry point + behavior |
| `STATUS.md` | Current state (overwritten per session) |
| `ENGINE.md` | Runtime rules + per-JSON guide |
| `DECISIONS.md` | Decision history + reference |
| `CHECKLIST.md` | Session end checklist + norms |

**Why conservative**: STATUS.md is the file most sessions touch. Separating it from START.md reduces merge conflicts.

### Option C: Directory-Based (Diataxis)

| Directory | Files | Purpose |
|-----------|-------|---------|
| `system/tutorial/` | `START.md` | One-page quickstart |
| `system/howto/` | `JSON_GUIDE.md`, `SCREENSHOT_GUIDE.md` | Workflow steps |
| `system/reference/` | `ENGINE.md`, `DECISIONS.md` | Lookup tables |
| `system/explanation/` | `BEHAVIOR.md` | Why the system works this way |
| `system/templates/` | `SESSION_START.md`, `SESSION_END.md` | Reusable templates |

**Why not recommended**: Adds directory depth. The current flat `system/` is actually fine — the problem is file count, not structure.

---

## 6. MIGRATION PLAN

### Phase 1: Preparation (This Session)
1. ✅ Fix all stale cross-references (test counts, versions)
2. ✅ Archive completed research files
3. ✅ Document current state (this file)

### Phase 2: Design (Next Session)
1. Choose Option A, B, or C
2. Draft each new file (content only, no deletion yet)
3. Map every cross-reference from old → new
4. Identify content that needs rewriting vs copy-paste

### Phase 3: Prototype (Session After)
1. Create new files alongside old files (suffix: `_NEW.md`)
2. Update `00_START_HERE.md` to point to new files
3. Test: Can a new session start with only new files?

### Phase 4: Validation (Session After)
1. Run full test suite (98/98 tests)
2. Generate a trading card using only new files
3. Verify no information loss
4. Check all cross-references resolve

### Phase 5: Migration (Session After)
1. Rename old files to `*_OLD.md`
2. Rename new files to canonical names
3. Update `03_FILE_INDEX.md` (or auto-generate)
4. Archive old files to `mts/archive/`

### Phase 6: Cleanup (Session After)
1. Delete archived old files
2. Verify system works with only new files
3. Update `00_START_HERE.md` to remove "OLD file" references

---

## 7. RISKS & MITIGATIONS

| Risk | Severity | Mitigation |
|------|----------|------------|
| Information loss during merge | Critical | Phase 4 validation: generate card from new files only |
| Cross-reference breakage | High | Phase 2: explicit mapping table old→new |
| Parallel session writes to old files during migration | High | Lock rule: "No edits to system/ during migration" |
| New files too large for AI reasoning | Medium | Cap each file at 50KB. Split if needed. |
| User confusion during transition | Medium | Clear banner in old files: "SUPERSEDED — see START.md" |
| Template files still drift | Low | Templates use `{{variables}}`, not hardcoded values |

---

## 8. DECISIONS NEEDED FROM USER

| # | Decision | Options | Default |
|---|----------|---------|---------|
| 1 | Which option? | A (4-file), B (5-file), C (directory-based) | A |
| 2 | Auto-generate index? | Yes (script), No (hand-maintained) | Yes |
| 3 | Archive or delete old files? | Archive (safe), Delete (clean) | Archive |
| 4 | Session end logs location? | In DECISIONS.md, Separate file, Auto-archive | Separate file |
| 5 | When to start? | Next session, After next trade, After next extraction | Next session |

---

## 9. RESEARCH GAPS

| Gap | Why It Matters | How to Close |
|-----|---------------|--------------|
| How do other AI-assisted projects handle file sprawl? | Validation of approach | Search: "AI project documentation structure best practices" |
| What is the optimal file size for AI reasoning? | New files must not exceed this | Test: generate cards with 50KB, 100KB, 200KB files |
| Can we auto-generate 03_FILE_INDEX.md? | Eliminates hand-maintenance | Prototype: Python script that walks upload_mirror/ |
| What happens to `session_end_logs.md`? | Historical but referenced | Decision: merge into DECISIONS.md or keep separate |
| How to prevent future drift? | Root cause of current mess | Rule: "No hardcoded counts/versions. Reference canonical file." |

---

## 10. BOTTOM LINE

The simplification task **correctly diagnoses the disease** (overcomplexity in `system/`) but the **3-file monolith** is the wrong cure. The **4-file Option A** (or conservative 5-file Option B) achieves the same cognitive reduction without destroying modularity.

**Next step**: User chooses Option A/B/C and decides when to start. Then Phase 2 (Design) begins.

---
# END
