# DATA DIRECTORY AUDIT — 2026-09-03
# Purpose: Clean up runtime_data/DSA files — identify what exists, why, and what to do
# Last updated: 2026-09-03
# ---

## CURRENT FILES (8 files)

| # | File | Size | Status | Purpose | Action |
|---|------|------|--------|---------|--------|
| 1 | data_schema_v1.2.0.md | ~23KB | ACTIVE | DSA JSON schema — contract between Java dev and AI | KEEP — update when enhancement spec approved |
| 2 | data_state_document.md | ~11KB | ACTIVE | Inventory of what DSA provides vs gaps | KEEP — update per session, deduplicate with enhancement spec |
| 3 | dsa_enhancement_spec_v1.3.0.md | ~9KB | PROPOSED | Proof detection module spec for Java dev | KEEP — pending JISHU approval |
| 4 | DSA_TASK_INDEX.md | ~2.5KB | ACTIVE | Master inventory of all DSA task numbers | KEEP — update when new tasks created |
| 5 | dsa_task_010_transcript_download.md | ~5KB | STALE/ARCHIVED | Cross-trader transcript download | ARCHIVED — Phase 1 complete, all transcripts extracted |
| 6 | sample_btc_snapshot.json | ~5KB | ACTIVE v1.2.0 | Example JSON output from DSA | KEEP — current format |
| 7 | test_snapshot_v4.2.0-p2_validation.json | ~6KB | ACTIVE | Regression test data for v4.2.0-p2 | KEEP |
| 8 | DIRECTORY_AUDIT.md | ~7KB | ACTIVE | This file | KEEP |

## GHOST FILES (referenced but NEVER EXISTED)

These files were claimed in prior versions of 03_FILE_INDEX.md as "archived" but were never created as standalone documents. Their content lives in 02b_DECISIONS_LOG.md entries only.

| Claimed File | Reality | Where Content Lives |
|-------------|---------|-------------------|
| dsa_task_007_htf_alignment.md | NEVER EXISTED | 02b_DECISIONS_LOG.md 2026-08-28 |
| dsa_task_008_gap_fields.md | NEVER EXISTED | 02b_DECISIONS_LOG.md 2026-08-31 |
| dsa_task_009_liquidation_investigation.md | NEVER EXISTED | Referenced only in DSA_TASK_010 header |

## DEDUPLICATION NOTE

`data_state_document.md` Section 7 (Recommended Actions) and `dsa_enhancement_spec_v1.3.0.md` request the SAME fields. The enhancement spec is the AUTHORITATIVE source. The data_state_document should reference it, not duplicate it.

## NEXT ACTIONS

1. **JISHU decides:** Approve/reject `dsa_enhancement_spec_v1.3.0.md` (12.5 hours dev work)
2. **If approved:** Update `data_schema_v1.2.0.md` to v1.3.0 with new fields
3. **If rejected:** Mark spec as REJECTED, update data_state_document to reflect

---
# END
