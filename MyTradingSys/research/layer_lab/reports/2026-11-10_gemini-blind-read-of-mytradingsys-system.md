MATCH: 6 | DIFF: 0 | NOT_IN_DATA: 0

# Gemini Blind Read Report: `check_dsa_review.py` vs Docstring Spec and `DSA_BLOCK_REVIEW.md`

- **Card**: `gemini-blind-read-of-mytradingsys-system`
- **Date**: 2026-11-10 UTC
- **Reader**: Gemini (`gemini-3.8-flash-low`, blind read worker, JIS-NUC)
- **Target Files**:
  - `MyTradingSys/system/check_dsa_review.py` (spec in module docstring lines 1-15, code lines 16-187)
  - `MyTradingSys/system/DSA_BLOCK_REVIEW.md` (live review document, 243 lines)
- **Scope In Read**:
  - `MyTradingSys/system/check_dsa_review.py` (module docstring, 6 structural checks)
  - `MyTradingSys/system/DSA_BLOCK_REVIEW.md`
- **Scope Out Respected**:
  - No edits to read files;
  - No live-tree edit;
  - No deploy;
  - No `.secrets` or `.env` read;
  - No trade, no order.

---

## 1. Specification Clauses Extracted from Docstring (`check_dsa_review.py:5-13`)

The module docstring defines exactly 6 structural checks for `DSA_BLOCK_REVIEW.md`:
1. **Check 1 (Sections present)**:
   "1. sections present: Bug table, Repeat classes, DeepSeek rules, Bridge behaviours, DSA prompt, Ranked fix list" [SOURCED: `check_dsa_review.py:5`]
2. **Check 2 (Bug table & repeat classes)**:
   "2. bug table: columns id|symptom|fix|state|class, >= 40 rows, no empty cell, state in open/closed/mitigated, every class in the table appears in the repeat-class table with the right count; count >= 2 => design fault" [SOURCED: `check_dsa_review.py:6-7`]
3. **Check 3 (DeepSeek rules)**:
   "3. DeepSeek rules: every source row has a date (YYYY-MM-DD) and an https URL; a 'could not be fetched' line" [SOURCED: `check_dsa_review.py:8`]
4. **Check 4 (Bridge behaviours)**:
   "4. behaviours: the six named behaviours each ranked likely/possible/unlikely and proved/unproved" [SOURCED: `check_dsa_review.py:9`]
5. **Check 5 (DSA prompt)**:
   "5. prompt section: at least 3 quoted current lines each with replacement text; DSA_SESSION_PROMPT.md is not changed against origin/fast-track" [SOURCED: `check_dsa_review.py:10-11`]
6. **Check 6 (Ranked fix list)**:
   "6. fix list: 1..12 items; items 1-3 are pacing guard, one machine per account, stop on warning; every item has failure prevented, a fail-first test and an owner lane" [SOURCED: `check_dsa_review.py:12-13`]

---

## 2. Check-by-Check Audit & Reconciliation Table

| Check # | Docstring Specification Clause | Code Implementation (`check_dsa_review.py`) | Target Document Verification (`DSA_BLOCK_REVIEW.md`) | Verdict | Label | Repro / Failing Input Demonstration |
|---:|---|---|---|---|---|---|
| 1 | Sections present: Bug table, Repeat classes, DeepSeek rules, Bridge behaviours, DSA prompt, Ranked fix list [SOURCED: `check_dsa_review.py:5`] | Lines 26-27 (`SECTIONS`), 57-61: iterates `SECTIONS`, asserts `h in text`, returns early on error | `DSA_BLOCK_REVIEW.md:23,111,129,151,165,206`: all 6 section headings (`## 1. Bug table` through `## 6. Ranked fix list`) present verbatim | MATCH | SOURCED | Failing input: rename `## 1. Bug table` to `## 1. Bugs`. Repro error: `"missing section '## 1. Bug table'"` (`check_dsa_review.py:59`). |
| 2 | Bug table: columns id\|symptom\|fix\|state\|class, >= 40 rows, no empty cell, state in open/closed/mitigated; every class appears in repeat-class table with right count; count >= 2 => design fault [SOURCED: `check_dsa_review.py:6-7`] | Lines 64-104: validates header cells, `len(body) >= 40`, `len(r) == 5` with non-empty cells, `state in {'open', 'closed', 'mitigated'}`, tallies counts; checks repeat-class table header, non-empty cells, count matching tally, `(want >= 2) == fault` (where `fault = r[2].lower().startswith("yes")`), bidirectional class existence | `DSA_BLOCK_REVIEW.md:32-110` has 76 rows [SOURCED], columns match, no empty cells, all states valid. `DSA_BLOCK_REVIEW.md:116-128` has 10 classes, all counts match exactly, all counts >= 2 have `yes` | MATCH | SOURCED | Failing input: change count of `block-read` from 14 to 13 in repeat-class table. Repro error: `"class 'block-read': count 13 != 14 rows in the bug table"` (`check_dsa_review.py:97`). Or set state to `done`: `"bug ...: state 'done' not open/closed/mitigated"` (`check_dsa_review.py:78`). |
| 3 | DeepSeek rules: every source row has a date (YYYY-MM-DD) and an https URL; a 'could not be fetched' line [SOURCED: `check_dsa_review.py:8`] | Lines 106-115: extracts section, requires >= 2 data rows in table, regex `\d{4}-\d{2}-\d{2}`, substring `"https://"`, non-empty cells, and `"could not be fetched" in rules.lower()` | `DSA_BLOCK_REVIEW.md:133-144` has 9 source rows [SOURCED], each with YYYY-MM-DD date and https:// URL; line 145 contains "Could not be fetched or not tried:" [SOURCED] | MATCH | SOURCED | Failing input: replace `https://` with `http://` or remove date. Repro error: `"DeepSeek rule row lacks date/URL or has empty cell: [...]"` (`check_dsa_review.py:113`). Or omit line 145: `"DeepSeek rules: no 'could not be fetched' statement"` (`check_dsa_review.py:115`). |
| 4 | Behaviours: the six named behaviours each ranked likely/possible/unlikely and proved/unproved [SOURCED: `check_dsa_review.py:9`] | Lines 28-29 (`BEHAVIOURS`), 118-135: verifies all 6 behaviours present in column 0, non-empty cells, regex `\b(likely\|possible\|unlikely)\b` and `\b(proved\|unproved)\b` | `DSA_BLOCK_REVIEW.md:156-164` has all 6 behaviours (`auto-send`, `rate`, `parallel chats`, `one account on several machines`, `fixed-format messages`, `command text`) [SOURCED], each ranked with valid rank and proof values | MATCH | SOURCED | Failing input: rename `auto-send` to `automatic-send` or omit rank/proof. Repro error: `"behaviour 'auto-send' not ranked"` (`check_dsa_review.py:126`) or `"behaviour 'auto-send' lacks likely/possible/unlikely"` (`check_dsa_review.py:132`). |
| 5 | Prompt section: at least 3 quoted current lines each with replacement text; DSA_SESSION_PROMPT.md is not changed against origin/fast-track [SOURCED: `check_dsa_review.py:10-11`] | Lines 137-142, 165-171: checks `p.count("Current:") >= 3` and `p.count("Replacement:") >= p.count("Current:")`; executes `git diff --quiet origin/fast-track -- DSA_SESSION_PROMPT.md` | `DSA_BLOCK_REVIEW.md:171-200` has 11 pairs of "Current:" and "Replacement:" [SOURCED]; `git diff --quiet origin/fast-track -- DSA_SESSION_PROMPT.md` returns 0 (clean, unchanged) [SOURCED] | MATCH | SOURCED | Failing input: replace `Current:` with `Old:`. Repro error: `"DSA prompt section: need >= 3 'Current:' lines each with a 'Replacement:'"` (`check_dsa_review.py:139`). Or modify `DSA_SESSION_PROMPT.md`: `"DSA_SESSION_PROMPT.md differs from origin/fast-track (must not be edited)"` (`check_dsa_review.py:141`). |
| 6 | Fix list: 1..12 items; items 1-3 are pacing guard, one machine per account, stop on warning; every item has failure prevented, a fail-first test and an owner lane [SOURCED: `check_dsa_review.py:12-13`] | Lines 30-31, 144-162: checks header columns, `1 <= len(items) <= 12`, non-empty cells, items 1-3 substring match for `pacing guard`, `one machine per account`, `stop on warning`, regex `test` in cell 3, lane in `LANES` in cell 4 | `DSA_BLOCK_REVIEW.md:211-225` has 12 items [SOURCED]; items 1-3 match required strings [SOURCED: lines 213-215]; every row specifies failure prevented, names a test with `test`, and specifies a valid owner lane (`SONNET`, `OPERATOR then SONNET`, `CLAUDE`, `CODEX`) | MATCH | SOURCED | Failing input: change item 1 text to `Rate limit guard`. Repro error: `"fix item 1 must be 'pacing guard'"` (`check_dsa_review.py:157`). Or omit test name: `"fix item 1: test cell does not name a test"` (`check_dsa_review.py:159`). Or invalid lane: `"fix item 1: owner lane 'UNKNOWN' unknown"` (`check_dsa_review.py:161`). |

---

## 3. Reconciliation Summary & Verdict

- **Clauses Checked**: 6 structural checks from module docstring
- **Matches**: 6
- **Diffs**: 0
- **Not in Data**: 0
- **Mechanical Validation**: `python MyTradingSys/system/check_dsa_review.py` passes with exit code 0 (`PASS`) against live `MyTradingSys/system/DSA_BLOCK_REVIEW.md`.
- **Failure Mode Verification**: All 6 checks were independently executed against mutated inputs; each check successfully trapped the bad review input and emitted the expected failure message as specified.
