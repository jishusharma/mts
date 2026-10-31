# Layer Lab Report: gemini-quote-audit-all-extracts-1031

- **Date**: 2026-10-31 (SOURCED: system clock / UTC)
- **Task ID**: `gemini-quote-audit-all-extracts-1031` (SOURCED: [gemini-quote-audit-all-extracts-1031.json](file:///F:/MTS/gq/gemini-quote-audit-all-extracts-1031/MyTradingSys/system/tasks/gemini-quote-audit-all-extracts-1031.json#L15))
- **Worker**: Gemini Flash worker (Lane: `CODEX`)
- **Gate Tool**: `python scripts/dev/verify_extract_quotes.py` (SOURCED: [verify_extract_quotes.py](file:///F:/MTS/gq/gemini-quote-audit-all-extracts-1031/scripts/dev/verify_extract_quotes.py#L1-L173))
- **Primary Deliverable**: `MyTradingSys/research/gemini_burn_2026-10-31/QUOTE_AUDIT.md` (SOURCED: card done_when)

---

## 1. Executive Summary & Counts

- **Total committed Markdown files in `MyTradingSys/research`**: 1513 (SOURCED: `git ls-files MyTradingSys/research`)
- **Files matching card filter pattern `extract|_levels|rules`**: 96 (SOURCED: `git ls-files MyTradingSys/research | grep -i -E "extract|_levels|rules"`)
- **Command-matched files quoting video captions via `Source GPS`**: 43 (OURS: evaluated by regex `Source GPS: <id> | <position>`)
- **Other research markdown files quoting video captions via `Source GPS`**: 30 (OURS: evaluated across all `MyTradingSys/research/*.md`)
- **Total files audited with video quote assertions**: 73 (OURS)

### Breakdown of the 43 Command-Matched Extracts (`extract|_levels|rules`):
- **Fully Checkable (all caption files present on host)**: 29 files (OURS)
  - **Passing (`exit 0`, 0 failing quotes)**: 23 files (OURS)
  - **Failing (`exit 1`, position errors / mis-positioned quotes)**: 6 files, 7 failing lines total (OURS)
- **Partially Checkable (captions present for some videos, missing for others)**: 2 files (OURS)
  - `MyTradingSys/research/malkan_rsi_2026-10-31/MALKAN_RULES_2026-10-31.md`: 9 missing caption lines for unfetched videos, 12 passing quotes (OURS)
  - `MyTradingSys/research/tom_correlation_trick_2026-10-26/EXTRACT.md`: 6 missing caption lines for video `e83njGZFrPw`, 9 passing quotes (OURS)
- **Uncheckable (no caption file exists on this host)**: 12 files (OURS)
  - 8 Krown TA101 extracts: `LB3DRYxnA0A`, `OggsnATGbOg`, `V0gjxlaW2Qk`, `ZNvLh3JyOco`, `_JoJbu_Ug-A`, `fMRvOt26xcA`, `hNfjyrJEytI`, `sCLLZKY_r8g` (SOURCED: missing in `raw_transcripts_canonical/`)
  - 1 Krown audit file: `MyTradingSys/research/krown_audit_2026-10-22/GEMINI_RULES_QUOTE_AUDIT.md` (SOURCED: videos `SOaAP9vBgM4`, `EQy4HouRMMk`, `-9rAJNUpMsk`, `UHY740h3e-Y` captions not in canonical)
  - 1 Pizzino method extraction: `MyTradingSys/research/pizzino_layer_2026-10-27/method_extraction.md` (SOURCED: all 19 video transcripts absent)
  - 2 YouTube feed extractions: `COWEN_LEVELS_2026-10-31.md` (7 vids absent), `REKT_LEVELS_2026-10-31.md` (8 vids absent)

---

## 2. Invented Quotes & Positioning Errors Caught

`verify_extract_quotes.py` validates both verbatim occurrence and transcript position thirds (`BEGIN`, `MIDDLE`, `END`).
Zero quotes were found to be completely fabricated in checkable files; however, 7 quotes had positioning tag mismatches:

1. `MyTradingSys/research/_archive/loose_2026-10/T064_TF_CONFIRMATION_EXTRACT.md`
   - Line 41: `POSITION T064_TF_CONFIRMATION_EXTRACT.md:41 tagged END, found MIDDLE`
   - Line 96: `POSITION T064_TF_CONFIRMATION_EXTRACT.md:96 tagged MIDDLE, found BEGIN`
2. `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_2-nG9bsMoPQ.md`
   - Line 117: `POSITION extract_2-nG9bsMoPQ.md:117 tagged BEGIN, found MIDDLE`
3. `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_6aA-P4Gvhrc.md`
   - Line 123: `POSITION extract_6aA-P4Gvhrc.md:123 tagged BEGIN, found MIDDLE`
4. `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_UqAvU1loT_k.md`
   - Line 254: `POSITION extract_UqAvU1loT_k.md:254 tagged MIDDLE, found BEGIN`
5. `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_ftK2BqggabQ.md`
   - Line 99: `POSITION extract_ftK2BqggabQ.md:99 tagged BEGIN, found MIDDLE`
6. `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_kcMnnQr1VFg.md`
   - Line 404: `POSITION extract_kcMnnQr1VFg.md:404 tagged MIDDLE, found END`

---

## 3. Findings in Other Research Documents Quoting Captions

Across the 30 other research documents quoting captions:
- 20 documents were fully checkable with captions present and passed `verify_extract_quotes.py` with exit code 0 (e.g. `EXEC_PROVENANCE_AUDIT.md`, `ANGLE_TRADE_CATALOG.md`, `PROVENANCE_AUDIT_TOM.md`, `SETUP_SUMMARY.md`, `COMPARE.md`).
- 3 documents had position tag mismatches:
  - `MyTradingSys/research/fast_track_2026-09-27/MISSING_PIECES_2026-09-30.md:175 tagged END, found MIDDLE`
  - `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:383 tagged BEGIN, found MIDDLE`
  - `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:622 tagged MIDDLE, found END`
  - `MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md:658 tagged MIDDLE, found BEGIN`
- 1 document was partially checkable (`krown_capture_2026-10-16/KROWN_VIEWS_HIGHS.md` missing transcript for `dzH7m9cQeZA`).
- 9 documents were UNCHECKABLE due to missing caption files on host (`ALT_BUY_PLAN_2026-10-31.md`, `STOP_SOURCE_HUNT_2026-10-31.md`, `method_jala.md`, `KROWN_LIVE_SETUPS_2026-10-31.md`, `method_jason.md`, `method_michael.md`, `JASON_BAR_UPDATE_2026-10-31.md`, `LOUKAS_CYCLE_2026-10-31.md`, `MICHAEL_BAR_UPDATE_2026-10-31.md`).

---

## 4. Deliverable Verification

- Audit table created: `MyTradingSys/research/gemini_burn_2026-10-31/QUOTE_AUDIT.md` (SOURCED: [QUOTE_AUDIT.md](file:///F:/MTS/gq/gemini-quote-audit-all-extracts-1031/MyTradingSys/research/gemini_burn_2026-10-31/QUOTE_AUDIT.md))
- Table includes exact path, exit code, failing quote count or UNCHECKABLE, total quote counts, and specific failure lines.

Noticed: Several recent extract files created on 2026-10-31 (`COWEN_LEVELS_2026-10-31.md`, `REKT_LEVELS_2026-10-31.md`, `JASON_BAR_UPDATE_2026-10-31.md`, `MICHAEL_BAR_UPDATE_2026-10-31.md`) quote YouTube videos whose caption files were never committed to `raw_transcripts_canonical/`, rendering their quote assertions uncheckable on fresh clones without caption fetching.
