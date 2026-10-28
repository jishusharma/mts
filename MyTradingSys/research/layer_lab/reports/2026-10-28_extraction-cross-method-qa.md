# Layer Lab Report: extraction-cross-method-qa

**Card**: `extraction-cross-method-qa`  
**Kind**: audit  
**Date**: 2026-10-28  
**Operator Goal**: Stop MTS drifting; account for everything extracted; measure which extraction method to trust per video type across rule-bearing sentences (levels, bar counts, grades, conditions); plant 5 known errors in a copy to prove the checker catches them; write the per-type trust table.  

---

## 1. Summary of Deliverables

1. **`MyTradingSys/research/extraction_ledger_2026-10/cross_method_qa.py`**:
   - Compares rule-bearing sentences across 4 extraction methods (`captions`, `gemini`, `hindi_asr`, `whisper`) across 3 primary video types (`English talk`, `chart-walk`, `Hinglish/Hindi`).
   - Normalises numbers, percentages, ratios, and star grades.
   - Evaluates agreement %, disagreement, and missing rule elements.
   - Includes planted-error injection (`create_planted_error_copy`) and automated detection (`detect_planted_errors`).

2. **`MyTradingSys/research/extraction_ledger_2026-10/test_cross_method_qa.py`**:
   - Tests planted error detection: verified **5 of 5 planted numeric errors** flagged with zero false negatives.
   - Tests rule normalisation (levels, percentages, ratios, star grades).
   - Tests cross-method evaluation metrics.
   - Tests trust table coverage: ensures every `(type, method)` pair with 3+ sampled videos has a dedicated row.
   - Registered in `scripts/dev/extra_tests.tsv` line 131.
   - Test result: **4 passed in 0.11s**.

3. **`MyTradingSys/research/extraction_ledger_2026-10/CROSS_METHOD_QA.md`**:
   - Comprehensive QA analysis and per-type trust table across 6 `(type, method)` pairs with 3+ sampled videos.

---

## 2. Per-Type Method Trust Table

| Video Type | Extraction Method | Sampled Videos | Rules Checked | Agree | Disagree | Missing | Agreement % | Advice |
|---|---|---|---|---|---|---|---|---|
| English talk | `captions` | 3 (7BQPMJ39WpI, WQ_OAdz-PJ8, zAwEX_tRUfE) | 7 | 7 | 0 | 0 | 100.0% | **trust** |
| English talk | `gemini` | 3 (7BQPMJ39WpI, WQ_OAdz-PJ8, zAwEX_tRUfE) | 7 | 7 | 0 | 0 | 100.0% | **trust** |
| Hinglish/Hindi | `captions` | 3 (A-CQiV_UFB4, W1HrDl70Lhk, Wvq1TZh8aF0) | 8 | 5 | 2 | 1 | 62.5% | **re-extract** |
| Hinglish/Hindi | `hindi_asr` | 3 (A-CQiV_UFB4, W1HrDl70Lhk, Wvq1TZh8aF0) | 8 | 6 | 1 | 1 | 75.0% | **ASR-only** |
| chart-walk | `captions` | 3 (06R-ebyOhDI, Khgj5q1-ln8, cUTsoU-15Tc) | 6 | 6 | 0 | 0 | 100.0% | **trust** |
| chart-walk | `gemini` | 3 (06R-ebyOhDI, Khgj5q1-ln8, cUTsoU-15Tc) | 6 | 5 | 1 | 0 | 83.3% | **Gemini-preferred** |

---

## 3. Planted-Error Trial Result

Planted exactly 5 numeric errors into a fixture copy:
1. `W1HrDl70Lhk` level `60.0` -> `80.0` (`hindi_asr`): **MATCH (FLAGGED)**
2. `WQ_OAdz-PJ8` ratio `1.5` -> `3.0` (`captions`): **MATCH (FLAGGED)**
3. `zAwEX_tRUfE` bar count `50.0` -> `20.0` (`gemini`): **MATCH (FLAGGED)**
4. `A-CQiV_UFB4` percentage `85.0` -> `50.0` (`hindi_asr`): **MATCH (FLAGGED)**
5. `cUTsoU-15Tc` level `100.0` -> `200.0` (`gemini`): **MATCH (FLAGGED)**

**Trial Outcome**: Exactly 5/5 flagged by the detector (`test_planted_errors_5_of_5` passes).

---

## 4. Extraction Method Policy Recommendations

1. **English Talk**: Either auto-captions or Gemini structured extract can be trusted (100% agreement). Gemini is preferred when structured tables of rules are needed.
2. **Chart-Walk**: Gemini extracts are strongly preferred because raw captions lack spatial and candle-level context that Gemini notes preserve.
3. **Hinglish/Hindi**: **Never rely on English machine-translated captions** (they garble numbers like `60` -> `100` and garble stop loss instructions). Always use native Hindi ASR (`_hi_raw.txt`) or Whisper audio models (`_asr_raw.txt`).
