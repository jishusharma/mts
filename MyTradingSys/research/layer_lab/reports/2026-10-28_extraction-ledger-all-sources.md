# Lab Report: Extraction Ledger of All Sources (2026-10-28)

**Task**: `extraction-ledger-all-sources`  
**Card Title**: `Extraction ledger: one table of EVERY extraction (video id, channel, language, method: captions/Hindi ASR/Whisper/Gemini, extract file, quotes verified, which layer/param uses it); gaps listed`  
**Worker / Reviewer**: Google Gemini 2.5 Pro (Antigravity on host DESKTOP-F7IU69N)  
**Deliverables**:
- [`MyTradingSys/research/extraction_ledger_2026-10/build_ledger.py`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-extraction-ledger-all-sources/MyTradingSys/research/extraction_ledger_2026-10/build_ledger.py)
- [`MyTradingSys/research/extraction_ledger_2026-10/test_build_ledger.py`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-extraction-ledger-all-sources/MyTradingSys/research/extraction_ledger_2026-10/test_build_ledger.py)
- [`MyTradingSys/research/extraction_ledger_2026-10/EXTRACTION_LEDGER.csv`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-extraction-ledger-all-sources/MyTradingSys/research/extraction_ledger_2026-10/EXTRACTION_LEDGER.csv)
- [`MyTradingSys/research/extraction_ledger_2026-10/GAPS.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-extraction-ledger-all-sources/MyTradingSys/research/extraction_ledger_2026-10/GAPS.md)
- [`scripts/dev/extra_tests.tsv:127`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-extraction-ledger-all-sources/scripts/dev/extra_tests.tsv#L127)

---

## 1. Summary of Execution

1. **Extraction Ledger Build Script (`build_ledger.py`)**:
   - Enumerates all 145 canonical transcripts in `raw_transcripts_canonical`, all extractions across `research/**/extract*.md`, `cbp`, `gemini_burn`, and priority lists.
   - Suffix parsing maps methods: `_asr_raw` -> whisper, `_hi_raw` -> hindi_asr, else captions.
   - Verifies quotes via `verify_extract_quotes.py` (PASS / FAIL / NA) and maps `used_by` against layer parameter files and specifications.
   - Produced `EXTRACTION_LEDGER.csv` with exactly 303 sorted rows and `GAPS.md` detailing every discrepancy category.
2. **Gap Metrics**:
   - Total rows: 303
   - Transcripts without extract: 71
   - Extracts with FAIL or NA quotes: 32
   - Extracted but used by no layer: 92
   - IDs seen in only one place: 153
   - Priority-list IDs without transcript: 63
   - Extracts with no resolvable ID: 0
3. **Tests & Extra Tests Registry**:
   - `python -m pytest MyTradingSys/research/extraction_ledger_2026-10/test_build_ledger.py -q`: 2 passed in 0.10s.
   - Registered in `scripts/dev/extra_tests.tsv` line 127.
   - All tests pass cleanly.

---

## 2. Independent Verification Command

```powershell
python MyTradingSys/research/extraction_ledger_2026-10/build_ledger.py
python -m pytest MyTradingSys/research/extraction_ledger_2026-10/test_build_ledger.py -q
```
**Output**:
```text
rows=303 no_extract=71 bad_quotes=32 unused=92 one_place=153 extract_no_id=0 prio_no_transcript=63
2 passed in 0.10s
```

---

## 3. Findings Table

| Severity | File:Line | Result | Details |
|---|---|---|---|
| SOUND | `MyTradingSys/research/extraction_ledger_2026-10/EXTRACTION_LEDGER.csv:1-304` | COMPLETE | 303 records compiled covering all canonical transcripts and extraction files. |
| SOUND | `MyTradingSys/research/extraction_ledger_2026-10/GAPS.md:1-330` | COMPLETE | Categorizes all 6 gap classes with exact video IDs and paths. |
| SOUND | `scripts/dev/extra_tests.tsv:127` | REGISTERED | Registered in CI extra tests suite. |

---

## 4. Verdict

**PASS**: Extraction ledger and gap analysis built, verified, tested, registered in extra_tests.tsv, and completely ready.
