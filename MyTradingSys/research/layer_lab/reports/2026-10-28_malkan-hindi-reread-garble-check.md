# Layer Lab Report: malkan-hindi-reread-garble-check

**Card**: `malkan-hindi-reread-garble-check`  
**Kind**: audit  
**Date**: 2026-10-28  
**Operator Goal**: Re-read Malkan Hindi ASR transcripts against English for garbled rules (levels, bar counts, star grades, trend condition); cross-vendor check of glossary UNVERIFIED rows.  

---

## 1. Summary of Deliverables

1. **`MyTradingSys/research/malkan_extract_2026-10-15/HINDI_REREAD_GEMINI.md`**:
   - Independent cross-vendor read of raw Hindi transcripts `W1HrDl70Lhk_hi_raw.txt` (**W**) and `A-CQiV_UFB4_hi_raw.txt` (**A**) against English extracts.
   - Section 1: Disagreements with the GPT read listed first (clarification on MAL-1 stop loss reconstruction, 60 level vs 100 ASR artifact, and 5/7-star condition withholding).
   - Section 2: Detailed status table for all MAL rows (`MAL-1`, `MAL-3`, `MAL-4`, `MAL-6`, `MAL-7`, `MAL-8`, `MAL-9`) across 18 topic fields.
   - Section 3: Definitive verdicts (Confirm, Correct, Keep Unverified) for all 12 `UNVERIFIED` rows of `MALKAN_DIVERGENCE_GLOSSARY.md`.
   - Section 4: Devanagari normalization verification confirming 372 lines in W and 346 lines in A.

2. **Automated Verification**:
   - Ran `python -I MyTradingSys/research/malkan_extract_2026-10-15/tools/check_hindi.py MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_A-CQiV_UFB4.md`.
   - Result: 96 quotes in W1HrDl70Lhk and 63 quotes in A-CQiV_UFB4 checked, 0 problems (exit code 0).

---

## 2. Key Audit Verdicts

- **MAL-1 (Level 100 vs 60)**: Spoken `100` at `W:125` is confirmed as phonetic ASR error for `60`, which is explicitly spoken repeatedly at `W:185, 333-336, 345`.
- **MAL-1 / MAL-6 Stop-Loss**: While line `W:133-134` is garbled noise (`ब्लॉक प्रिंटेड नॉट रिटारडेड चिल्ड्रन`), the stop loss rule is repeatedly stated in adjacent lines (`W:192-193`, `W:221`, `W:262-263`) as below the low of the signal candle.
- **5-Star / 7-Star Grades**: Video A confirms star grades and hit rates are sourced, but Malkan explicitly withholds conditions (`A:307-309`). Conditions remain NOT STATED.
- **Glossary UNVERIFIED Rows**: 6 rows confirmed (valid aliases, definitions, priority rule), 3 corrected (grades sourced but conditions withheld; levels not stated for regular div), and 3 kept unverified (discretionary / multi-video requirement).
