# Gemini Spec Review Report: Malkan Divergence Window Card (`malkan-window-12-18-vs-hindi`)

- **Card ID**: `gemini-spec-review-malkan-window-1104` [SOURCED: gemini-spec-review-malkan-window-1104.json:13]
- **Audited Target Card**: `MyTradingSys/system/tasks/malkan-window-12-18-vs-hindi.json` [SOURCED: malkan-window-12-18-vs-hindi.json:16]
- **Card Class**: C2 (Base Definition feeding downstream chart, alerts, and divergence backtests) [SOURCED: malkan-window-12-18-vs-hindi.json:4,38]
- **Date**: 2026-11-04 (UTC)
- **Reviewer**: Gemini 3.8 Flash (independent cross-vendor review lens per `roles/lab_guy.md` Class C2 policy)
- **Deliverable Review Document**: `MyTradingSys/research/malkan_hindi_2026-11-04/REVIEW_MALKAN_WINDOW_GEMINI_1104.md`
- **Total Defects Identified**: 8 defects [OURS: count 8]
- **Final Verdict**: VERDICT: FIX-FIRST

---

## 1. Summary of Findings & Defect Ledger

1. **Defect 1 [E4 Wrong Question / Test Integrity] (HIGH / Blocker)**: Verification test easily passed by invalid or wrong answer.
   - Evidence: `malkan-window-12-18-vs-hindi.json:65` asserts only `t.count('|')>=20 and re.search(r'SOURCED|OURS',t) and '18' in t`. It passes on any 4-line table with '18' and 'SOURCED', ignoring video IDs, threshold verdicts, or factual correctness.
   - Command: `python -c "import pathlib,re; t=pathlib.Path('MyTradingSys/research/malkan_hindi_2026-11-04/WINDOW_RECONCILE_1104.md').read_text(); assert t.count('|')>=20 and re.search(r'SOURCED|OURS',t) and '18' in t"` [SOURCED: malkan-window-12-18-vs-hindi.json:65].
   - Fix: Harden test to assert video IDs, threshold labels (10, 12, 15, 18), and that 18 is classified as `NOT_IN_DATA` or `OURS`.

2. **Defect 2 [E3 Implementation / E1 Data] (HIGH / Blocker)**: Quote verification script fails on Hindi text.
   - Evidence: `malkan-window-12-18-vs-hindi.json:6,62` specifies `python scripts/dev/verify_extract_quotes.py ...`. `scripts/dev/verify_extract_quotes.py:36` runs `norm()` with regex `[^a-z0-9%]+`, stripping all Devanagari characters. At line 156, Hindi quotes with `< 3` ASCII tokens are skipped and pass with false-positive OK. At line 205, Devanagari quotes formatted with `> "..."` evaluate to empty strings and fail with `MISSING`.
   - Command: `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/malkan_hindi_2026-11-04/HINDI_CONCEPTS.md` [OURS: returns 0 problems because Hindi quotes are skipped].
   - Fix: Update `verify_extract_quotes.py` to support Unicode/Devanagari, or substitute a dedicated line-check for Hindi quotes.

3. **Defect 3 [E1 Data / Scope Defect] (HIGH / Blocker)**: Missing English source video `GbXnw_tNMtw` from `scope_in`.
   - Evidence: `malkan_divergence_default.json:17` cites `GbXnw_tNMtw_raw.txt:379` for the 15-bar limit. `MyTradingSys/research/malkan_extract_2026-10-15/extracts` contains 6 files [SOURCED: extract_-CBvFi40sIQ.md, extract_2HcJ3NeZmEQ.md, extract_A-CQiV_UFB4.md, extract_cQ-y1oULkBw.md, extract_W1HrDl70Lhk.md, extract_Wvq1TZh8aF0.md] and does not contain `GbXnw_tNMtw` [OURS: count 0]. The file exists only at `raw_transcripts_canonical/GbXnw_tNMtw_raw.txt`, which is omitted from `scope_in` [SOURCED: malkan-window-12-18-vs-hindi.json:45-50].
   - Fix: Add `raw_transcripts_canonical/GbXnw_tNMtw_raw.txt` to `scope_in`.

4. **Defect 4 [E1 Data / Scope Defect] (MEDIUM)**: Canonical Hindi transcripts omitted from `scope_in`.
   - Evidence: `HINDI_CONCEPTS.md:5-10` cites 6 raw transcripts under `raw_transcripts_canonical/`. Auditing and verifying primary bar-count quotes across the Hindi videos requires access to `raw_transcripts_canonical/`, which is omitted from `scope_in` [SOURCED: malkan-window-12-18-vs-hindi.json:45-50].
   - Fix: Add `raw_transcripts_canonical/` to `scope_in`.

5. **Defect 5 [E2 Definition / Scope Defect] (MEDIUM)**: Missing `OPERATOR_DECISIONS.md` from `scope_in` and `sources`.
   - Evidence: The card title and goal refer to operator decision `d-malkan-divergence-window-1104` [SOURCED: malkan-window-12-18-vs-hindi.json:15,66], which is defined in `MyTradingSys/system/OPERATOR_DECISIONS.md:1685-1686`. `OPERATOR_DECISIONS.md` is omitted from both `scope_in` and `sources` [SOURCED: malkan-window-12-18-vs-hindi.json:45-50,56-58].
   - Fix: Add `OPERATOR_DECISIONS.md` to `scope_in` and line range `:1685-1686` to `sources`.

6. **Defect 6 [E2 Definition / E4 Wrong Question] (HIGH / Blocker)**: Conflation of Regular Divergence vs Reverse Divergence.
   - Evidence: `malkan-window-12-18-vs-hindi.json:57` cites only `malkan_divergence_default.json:17`, which defines `reverse.max_bars_quote` (PRD/NRD). In `malkan_divergence_default.json:4-8`, regular divergence is defined separately with `min_bars: 3`, `max_bars: 10`. The card does not clarify whether the 12/18 reconciliation applies to regular, reverse, or both, while downstream modules (`div_flags_chart.py:217`) apply it to regular divergence.
   - Fix: Add `malkan_divergence_default.json:4-8` to `sources` and explicitly scope whether regular, reverse, or both are being reconciled.

7. **Defect 7 [E4 Wrong Question / Step Omission] (MEDIUM)**: Step 1 search criteria omits primary numbers (3, 5, 7, 10).
   - Evidence: Step 1 specifies searching only for `(15, 12, 18, less than)` [SOURCED: malkan-window-12-18-vs-hindi.json:61]. Malkan's foundational rules cite 3 candles minimum [SOURCED: extract_Wvq1TZh8aF0.md:127, HINDI_CONCEPTS.md:43], 5 and 7 as most powerful [SOURCED: extract_cQ-y1oULkBw.md:144], and 10 as the upper bound ("between three and 10" [SOURCED: extract_Wvq1TZh8aF0.md:133]).
   - Fix: Expand Step 1 search terms to include `(3, 5, 7, 10, 12, 14, 15, 18, "less than", "dilut")`.

8. **Defect 8 [E4 Done_When Underspecification] (MEDIUM)**: `done_when` contract does not specify required thresholds or parameter target.
   - Evidence: `done_when` requires a "verdict per threshold" and a "proposed malkan_divergence_default.json window" [SOURCED: malkan-window-12-18-vs-hindi.json:10], but fails to enumerate the required thresholds (10, 12, 15, 18) or clarify whether regular or reverse parameters are proposed.
   - Fix: Explicitly specify required threshold verdicts (10, 12, 15, 18 with 18 identified as `NOT_IN_DATA`), and require a proposed JSON snippet with separate regular and reverse keys.

---

## 2. Test Verification

The deliverable review document was verified using the card's required test command:
```powershell
python -c "import pathlib; t=pathlib.Path('MyTradingSys/research/malkan_hindi_2026-11-04/REVIEW_MALKAN_WINDOW_GEMINI_1104.md').read_text(encoding='utf-8'); assert 'VERDICT:' in t"
```
Result: Command exited with code 0 (Pass) [OURS: exit code 0].

---

VERDICT: FIX-FIRST
