# PROMPT FAILURE ANALYSIS - 2026-10-03
# Session: MTS-2026-10-03-0430Z-DSA-COO
# Scope: DSA prompt-composition defects this session, cross-referenced
#        with prior session records and LESSONS_LEARNED.md.

## 1. FINDINGS

Eight defects this session, one line each.

- D1. Invented a capability limit on Claude (no disk, design-only).
- D2. Conflated the WORKER role with the CL builder surface.
- D3. Wrote 'this session changes no code' without saying which session.
- D4. Named R4 parameters K_BAL / BAL_POC_BAND / B_PROF in a prompt
      without reading the file; those tokens are absent from
      htf_context_live.py (actual tokens MIN_MS, FP_BIN, SYMBOL, BASE,
      N_4H, N_1D).
- D5. Carried T3 fail-before into a design task.
- D6. Named only three task sources; missed apparatus_fixes.md OPEN
      and NEEDS OPERATOR, both handoff files, operator directives.
- D7. Framed the T3 clause as a DSA trust check on Claude.
- D8. Proposed a mandatory split-reply clause without operator ask.

## 2. PRIOR RECORDS SHOW REPETITION

LESSONS_LEARNED.md is 311 lines, LF-only. The boot manifest reads
tail 40 lines. Two prior entries name this exact class of mistake,
both written 2026-10-02, one day before this session.

Entry 2026-10-02 'prompt delivery failures': claimed 13 Fabio v3 files
(disk had 14); invented a 500K/100K token cap; invented four 'do not
read' restrictions on an Opus session; delivered a prompt labelled
verified from prior pastes.

Entry 2026-10-02 'DSA prompt-construction mistakes': cited paths that
do not exist; wrong line numbers; wrote prompt files to disk when the
operator wanted chat; claimed files written when write never executed.

Match against this session's eight:

  D1 <- 'Invented four do-not-read restrictions' (2026-10-02)
  D4 <- 'Claimed 13 Fabio v3 files; disk had 14' (2026-10-02)
  D4 <- 'Cited paths that do not exist' (2026-10-02)
  D5 <- 'Every prompt: grep every cited line' (2026-10-02)
  D6 <- 'Composed prompts from earlier pastes' (2026-10-02)
  D7 <- 'Labelled verified, composed from prior pastes' (2026-10-02)
  D8 <- 'Wrote budget-refusal clauses' (2026-10-02)

Six of eight were logged one day earlier. Not a new pattern. A repeat.

## 3. STRUCTURAL FINDING

The rules already exist. They were not in this session's boot.

LESSONS_LEARNED.md loads as tail 40 lines. The two 2026-10-02 entries
sit near line 180 and line 250 of a 311-line file. Line 180 is outside
the tail-40 window. Rules 1-7 of the 2026-10-02 construction list
(Test-Path every cited path; grep every cited line; never write a
prompt to disk unless asked) were therefore not in context.

SESSION_MANIFEST.json current entry for LESSONS_LEARNED.md:
  'read: tail, lines: 40'

Two structural options:
  A. Bump tail 40 to tail 160. Covers all three recent entries.
     Boot paste grows ~120 lines (~8 KB). Within section-2 size rule.
  B. Add a read-on-demand rule. Section 5c already says read at boot;
     a partial read does not satisfy that.

Option A is simpler: one manifest edit.

## 4. COST

Six DSA turns this session went to correction rather than delivery.
No cloud spend. No file damage. No live-path risk.

Prior sessions cost more: 2026-10-02 cloud burn ~ (Ultracode), one
wasted Opus session, one 1-byte file, seven tracked files deleted.

## 5. ACTIONS

1. B083 filed. Build scripts/dev/prompt_check.ps1: gate that greps a
   composed prompt against disk and refuses launch on FAIL. Pending
   since 2026-10-02, still unbuilt.
2. Optional: bump LESSONS_LEARNED.md tail 40 -> 160 in the manifest.
3. Optional: read the two 2026-10-01 DSA session records for prior
   context (MTS-2026-10-01-1503Z-DSA-COO.md, MTS-2026-10-01-1431Z-DSA-COO.md).

# END
