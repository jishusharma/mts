# Blind Spec Review: Malkan Divergence Window Card (`malkan-window-12-18-vs-hindi`, Class C2)

- **Target Card**: `MyTradingSys/system/tasks/malkan-window-12-18-vs-hindi.json` [SOURCED: malkan-window-12-18-vs-hindi.json:16]
- **Target Card Class**: C2 (Base Definition feeding downstream chart, alerts, and divergence backtests) [SOURCED: malkan-window-12-18-vs-hindi.json:4,38]
- **Reviewer**: Gemini 3.8 Flash (independent cross-vendor review lens per `roles/lab_guy.md` Class C2 policy)
- **Date**: 2026-11-04 (UTC)
- **Scope & Context**:
  - `MyTradingSys/system/tasks/malkan-window-12-18-vs-hindi.json` [SOURCED: malkan-window-12-18-vs-hindi.json:1-69]
  - `MyTradingSys/research/malkan_hindi_2026-11-04/HINDI_CONCEPTS.md` [SOURCED: HINDI_CONCEPTS.md:1-54]
  - `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json` [SOURCED: malkan_divergence_default.json:1-24]
  - `MyTradingSys/research/malkan_extract_2026-10-15/extracts` [SOURCED: 6 files]
  - `MyTradingSys/system/OPERATOR_DECISIONS.md:1685-1686` (`d-malkan-divergence-window-1104`) [SOURCED: OPERATOR_DECISIONS.md:1685-1686]
  - `scripts/dev/verify_extract_quotes.py` [SOURCED: verify_extract_quotes.py:1-236]
- **Focus**: Non-Claude spec review addressing the three required questions:
  1. Is the question right?
  2. Are the sources enough?
  3. Can its test be passed by a wrong answer?
- **Rule Check**: Label every number SOURCED (quote + file:line) or OURS. Defects only; do not answer the card.

---

## 1. Executive Summary & Assessment of Core Questions

The task card `malkan-window-12-18-vs-hindi` intends to audit and reconcile the 12/18 bar divergence lookback window adopted from operator decision `d-malkan-divergence-window-1104` against Malkan's Hindi and English videos.

Before the card is accepted and executed by an agent, this spec review identifies 8 concrete defects (OURS: count 8) across error classes E1 (Data), E2 (Definition), E3 (Implementation), and E4 (Wrong Question / Test Integrity).

### Question 1: Is the question right?
**NO.** The question suffers from fundamental conceptual ambiguity:
- **Conflation of Regular vs Reverse Divergence**: In Malkan's teachings and in `malkan_divergence_default.json`, regular divergence (R-BULL/R-BEAR) and reverse divergence (PRD/NRD) have distinct bar count parameters (regular is 3..10 bars, while reverse is 5..14 bars [SOURCED: malkan_divergence_default.json:4,14-15]). The card asks to reconcile "the Malkan divergence bar window", citing only line 17 (`reverse.max_bars_quote` [SOURCED: malkan-window-12-18-vs-hindi.json:57]), but downstream consumers (`div_flags_chart.py:217`, `live_confluence_feed.py:48`) apply the 12/18 window to regular divergence. The card fails to specify whether the reconciliation governs regular, reverse, or both.
- **Omission of Core Baselines**: The goal and step 1 query only 12, 15, and 18, omitting the primary numbers Malkan repeatedly cites as powerful: 3, 5, 7, and 10 bars (e.g. "between three and 10" [SOURCED: extract_Wvq1TZh8aF0.md:133], "तीन" [SOURCED: HINDI_CONCEPTS.md:43]).

### Question 2: Are the sources enough?
**NO.** Critical inputs are missing from `scope_in` and `sources`:
- **Missing English Video `GbXnw_tNMtw`**: The only cited source for the 15-bar limit in `malkan_divergence_default.json:17` is `GbXnw_tNMtw_raw.txt:379`. However, `GbXnw_tNMtw` has NO extract file in `MyTradingSys/research/malkan_extract_2026-10-15/extracts/` (OURS: count 0 files). It exists only in `raw_transcripts_canonical/GbXnw_tNMtw_raw.txt`. Because `raw_transcripts_canonical/` is omitted from `scope_in`, a worker restricted to `scope_in` cannot access the primary source of the 15-bar rule.
- **Missing Operator Decision File**: `OPERATOR_DECISIONS.md:1685-1686` (`d-malkan-divergence-window-1104`) is omitted from `scope_in` and `sources`, leaving the worker without the canonical source text that originated the 12/18 claim.
- **Missing Canonical Hindi Transcripts**: `raw_transcripts_canonical/` is not in `scope_in`, preventing direct quote verification against the 6 raw transcripts.

### Question 3: Can its test be passed by a wrong answer?
**YES.**
The assertion in `malkan-window-12-18-vs-hindi.json:65`:
`assert t.count('|')>=20 and re.search(r'SOURCED|OURS',t) and '18' in t`
can be passed trivially by an invalid, hallucinated, or wrong output (e.g. any 4-line markdown table containing "18" and the word "SOURCED"). It fails to test:
- Presence of required video IDs.
- Presence of verdicts for each threshold (10, 12, 14/15, 18).
- That 18 is classified as `NOT_IN_DATA` or `OURS` (a worker falsely claiming "18 is SOURCED" passes).
- Valid quote attribution.
Furthermore, the verification command `python scripts/dev/verify_extract_quotes.py ...` is broken for Hindi quotes because its normalizer `re.sub(r"[^a-z0-9%]+", " ", s.lower())` [SOURCED: verify_extract_quotes.py:36] strips all Devanagari text, silently skipping Hindi quotes and reporting false-positive PASS.

---

## 2. Detailed List of Defects (E1–E7)

### Defect 1: [E4 Wrong Question / Test Integrity] Verification Test Can Be Passed by a Wrong or Fabricated Answer
- **File & Line**: `MyTradingSys/system/tasks/malkan-window-12-18-vs-hindi.json:65` [SOURCED: malkan-window-12-18-vs-hindi.json:65]
- **Severity**: HIGH (Blocker)
- **Evidence**:
  The card tests completion via:
  ```python
  python -c "import pathlib,re; t=pathlib.Path('MyTradingSys/research/malkan_hindi_2026-11-04/WINDOW_RECONCILE_1104.md').read_text(); assert t.count('|')>=20 and re.search(r'SOURCED|OURS',t) and '18' in t"
  ```
  This test checks only 3 superficial properties:
  1. `t.count('|') >= 20` [SOURCED: malkan-window-12-18-vs-hindi.json:65]: A table with 20 pipe characters (as few as 4 short rows of 5 columns).
  2. `re.search(r'SOURCED|OURS', t)` [SOURCED: malkan-window-12-18-vs-hindi.json:65]: The single word "SOURCED" or "OURS" anywhere in the document.
  3. `'18' in t` [SOURCED: malkan-window-12-18-vs-hindi.json:65]: The substring "18" anywhere in the document (matches a timestamp, date like `2026-10-18`, line number, or arbitrary text).
  The test passes even if:
  - The worker fabricates Hindi or English quotes.
  - The worker erroneously concludes that 18 is `SOURCED` to Malkan (contradicting `HINDI_CONCEPTS.md:27` which states `18` is `NOT_IN_DATA`).
  - The worker proposes no valid parameters or omits regular divergence vs reverse divergence distinctions.
  - The table contains zero video IDs.
- **Fix**: Harden `tests` to verify:
  1. Presence of required video IDs (`GbXnw_tNMtw`, `cQ-y1oULkBw`, `Wvq1TZh8aF0`, `kVIvcn7T44o`, `TrZQ4Xat_sQ`, `TO3pLafk7Us`).
  2. Presence of threshold labels for 10, 12, 15, and 18.
  3. Assertion that 18 is classified as `OURS` or `NOT_IN_DATA` (never `SOURCED`).
  4. Fenced JSON code block with proposed keys (`min_bars`, `max_bars`).

---

### Defect 2: [E3 Implementation / E1 Data] Quote Verification Script Cannot Verify Hindi Text
- **File & Line**: `MyTradingSys/system/tasks/malkan-window-12-18-vs-hindi.json:6,62` [SOURCED: malkan-window-12-18-vs-hindi.json:6,62], `scripts/dev/verify_extract_quotes.py:32-40,156-157` [SOURCED: verify_extract_quotes.py:32-40,156-157]
- **Severity**: HIGH (Blocker)
- **Evidence**:
  The card lists as command and step 2:
  `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/malkan_hindi_2026-11-04/WINDOW_RECONCILE_1104.md`
  In `scripts/dev/verify_extract_quotes.py:36`:
  ```python
  for w in re.sub(r"[^a-z0-9%]+", " ", s.lower()).split():
  ```
  `norm()` strips every character outside `[a-z0-9%]`. Hindi (Unicode Devanagari range `\u0900-\u097F`) is completely discarded.
  - In `check_doc_line` (`verify_extract_quotes.py:156`):
    `if len(norm(quote).split()) < 3: continue`
    Any Devanagari quote with fewer than 3 ASCII words/numbers is dropped from validation. A completely fabricated Hindi quote is reported as `OK` with exit code 0.
  - In `check` (`verify_extract_quotes.py:205`):
    `if not q: bad += 1; continue`
    Any quote formatted as an extract block (`> "..."`) in Devanagari produces `q == ""` and fails with `MISSING` even when 100% verbatim in the transcript.
- **Fix**:
  Either:
  1. Update `scripts/dev/verify_extract_quotes.py` to preserve Unicode letters (`\w` or Devanagari blocks) so Hindi quotes can be verified; OR
  2. Remove `verify_extract_quotes.py` from `commands` and `steps` for Hindi quotes, substituting a dedicated verification command or restricting `verify_extract_quotes.py` to English quotes while using line-cite checking for Hindi quotes.

---

### Defect 3: [E1 Data / Scope Defect] Critical English Source Video (`GbXnw_tNMtw`) Missing from `scope_in`
- **File & Line**: `MyTradingSys/system/tasks/malkan-window-12-18-vs-hindi.json:45-50` [SOURCED: malkan-window-12-18-vs-hindi.json:45-50], `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:16-17` [SOURCED: malkan_divergence_default.json:16-17]
- **Severity**: HIGH (Blocker)
- **Evidence**:
  - `malkan_divergence_default.json:17` cites:
    `"max_bars_quote": "number of bars which are less than 15 (GbXnw_tNMtw_raw.txt:379)"` [SOURCED: malkan_divergence_default.json:17]
  - The card specifies:
    `"scope_in": [ ... "MyTradingSys/research/malkan_extract_2026-10-15/extracts" ... ]` [SOURCED: malkan-window-12-18-vs-hindi.json:48]
  - However, directory `MyTradingSys/research/malkan_extract_2026-10-15/extracts` contains ONLY 6 files:
    `extract_-CBvFi40sIQ.md`, `extract_2HcJ3NeZmEQ.md`, `extract_A-CQiV_UFB4.md`, `extract_cQ-y1oULkBw.md`, `extract_W1HrDl70Lhk.md`, `extract_Wvq1TZh8aF0.md`.
    It does NOT contain `GbXnw_tNMtw` (OURS: count 0 files).
  - Video `GbXnw_tNMtw` is an English live class that exists ONLY at `raw_transcripts_canonical/GbXnw_tNMtw_raw.txt`.
  - Because `raw_transcripts_canonical/` is not in `scope_in`, the worker cannot inspect or grep the source of the 15-bar quote cited in line 17 of `malkan_divergence_default.json`.
- **Fix**: Add `raw_transcripts_canonical/GbXnw_tNMtw_raw.txt` (or `raw_transcripts_canonical/`) to `scope_in`.

---

### Defect 4: [E1 Data / Scope Defect] Canonical Hindi Transcripts Missing from `scope_in`
- **File & Line**: `MyTradingSys/system/tasks/malkan-window-12-18-vs-hindi.json:45-50` [SOURCED: malkan-window-12-18-vs-hindi.json:45-50]
- **Severity**: MEDIUM
- **Evidence**:
  - `HINDI_CONCEPTS.md:5-10` cites 6 raw transcripts under `raw_transcripts_canonical/` (`-2uZSqKKrFQ`, `fgN6QBFY3Ss`, `kVIvcn7T44o`, `sPu2SnAFEIY`, `TO3pLafk7Us`, `TrZQ4Xat_sQ`) [SOURCED: HINDI_CONCEPTS.md:5-10].
  - The card requires tabulating "every bar-count quote (video id, quote, English or Hindi)" [SOURCED: malkan-window-12-18-vs-hindi.json:10].
  - If a worker only reads `HINDI_CONCEPTS.md`, they are reading a secondary summary, not the primary data. To audit whether other bar counts exist in the Hindi videos, the worker must have `raw_transcripts_canonical/` in `scope_in`.
- **Fix**: Add `raw_transcripts_canonical/` to `scope_in`.

---

### Defect 5: [E2 Definition / Scope Defect] Missing `OPERATOR_DECISIONS.md` (`d-malkan-divergence-window-1104`) from `scope_in` and `sources`
- **File & Line**: `MyTradingSys/system/tasks/malkan-window-12-18-vs-hindi.json:15,45-50,56-58` [SOURCED: malkan-window-12-18-vs-hindi.json:15,45-50,56-58]
- **Severity**: MEDIUM
- **Evidence**:
  - The card title and goal explicitly target `d-malkan-divergence-window-1104`:
    `"goal": "Reconcile the Malkan divergence bar window (ours: 12 STRONG, 13-18 OK, >18 WEAK) with the Hindi videos ..."` [SOURCED: malkan-window-12-18-vs-hindi.json:15]
  - The verbatim decision is in `MyTradingSys/system/OPERATOR_DECISIONS.md:1685-1686`:
    `Operator: "... always calculate the divergence properly, and especially the Malkan way. So his 12 bar divergence, 18 bar divergence ... after 18 bar, any divergence is weaker ... (all three SOURCED, Malkan)"` [SOURCED: OPERATOR_DECISIONS.md:1685-1686]
  - `OPERATOR_DECISIONS.md` is omitted from both `scope_in` and `sources`.
  - A worker cannot trace how the operator phrased the rule or why the operator designated 12 and 18 as SOURCED without reading `OPERATOR_DECISIONS.md:1685-1686`.
- **Fix**: Add `MyTradingSys/system/OPERATOR_DECISIONS.md` to `scope_in` and `MyTradingSys/system/OPERATOR_DECISIONS.md:1685-1686` to `sources`.

---

### Defect 6: [E2 Definition / E4 Wrong Question] Conflation of Regular Divergence vs Reverse Divergence (PRD/NRD)
- **File & Line**: `MyTradingSys/system/tasks/malkan-window-12-18-vs-hindi.json:15,56-58` [SOURCED: malkan-window-12-18-vs-hindi.json:15,56-58]
- **Severity**: HIGH (Blocker)
- **Evidence**:
  - `malkan-window-12-18-vs-hindi.json:57` cites only:
    `"sources": ["MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:17"]` [SOURCED: malkan-window-12-18-vs-hindi.json:57]
  - In `malkan_divergence_default.json`:
    - Line 17 is: `"max_bars_quote": "number of bars which are less than 15 (GbXnw_tNMtw_raw.txt:379)"` [SOURCED: malkan_divergence_default.json:17].
    - Line 17 is nested inside the `"reverse"` block (`PRD/NRD`), which has `min_bars: 5`, `max_bars: 14` [SOURCED: malkan_divergence_default.json:14-15].
    - Regular divergence is defined in lines 4-8: `min_bars: 3`, `max_bars: 10`, citing English video `extract_Wvq1TZh8aF0.md:133` ("between three and 10") [SOURCED: malkan_divergence_default.json:4-8].
  - The card fails to clarify whether the 12 STRONG / 13-18 OK / >18 WEAK window applies to:
    1. Regular divergence only (as implemented in `div_flags_chart.py:217` and `live_confluence_feed.py:48`);
    2. Reverse divergence (PRD/NRD) only; OR
    3. Both regular and reverse divergence.
  - In Malkan's videos, regular divergence is taught with 3..10 bars (English `Wvq1TZh8aF0:133`, Hindi `kVIvcn7T44o:43-45`) and under 15 bars (Hindi `TrZQ4Xat_sQ:21`), whereas reverse divergence is taught with 5..14 bars (English `GbXnw_tNMtw:379,460`).
  - Without distinguishing divergence types, proposing a single window in `malkan_divergence_default.json` risks corrupting both parameters.
- **Fix**:
  1. Add lines 4-8 (`min_bars`, `max_bars`) of `malkan_divergence_default.json` to `sources`.
  2. Clarify in `goal` and `done_when` whether the reconciliation proposes values for `min_bars`/`max_bars` (regular) or `reverse.min_bars`/`reverse.max_bars` (reverse) or separate proposed windows for each.

---

### Defect 7: [E4 Wrong Question / Step Omission] Search Step Omits Core Bar Counts (3, 5, 7, 10)
- **File & Line**: `MyTradingSys/system/tasks/malkan-window-12-18-vs-hindi.json:61` [SOURCED: malkan-window-12-18-vs-hindi.json:61]
- **Severity**: MEDIUM
- **Evidence**:
  - Step 1 instructs: `"grep the English extracts and HINDI_CONCEPTS.md for bar-count quotes (15, 12, 18, less than)"` [SOURCED: malkan-window-12-18-vs-hindi.json:61].
  - This selectively targets the disputed numbers and ignores the core consensus numbers:
    - 3 bars: minimum required for any divergence (`kVIvcn7T44o:43`, `cQ-y1oULkBw:128`, `Wvq1TZh8aF0:127`).
    - 5 and 7 bars: repeatedly cited as most powerful (`cQ-y1oULkBw:144,182`, `Wvq1TZh8aF0:172`).
    - 10 bars: upper bound for powerful divergence ("less than 10 bars is the most powerful divergence. It should be between three and 10" [SOURCED: extract_Wvq1TZh8aF0.md:133]; "ज़्यादा 10 के ऊपर गया 15, 20, 25, 50 फिर वह डाइल्यूट होते जाता है" [SOURCED: HINDI_CONCEPTS.md:45]).
  - Omitting 3, 5, 7, 10 blinds the worker to the primary baseline against which 12 and 18 must be reconciled.
- **Fix**: Update step 1 to include `(3, 5, 7, 10, 12, 14, 15, 18, "less than", "dilut")`.

---

### Defect 8: [E4 Done_When Underspecification] `done_when` Contract Is Incomplete
- **File & Line**: `MyTradingSys/system/tasks/malkan-window-12-18-vs-hindi.json:10` [SOURCED: malkan-window-12-18-vs-hindi.json:10]
- **Severity**: MEDIUM
- **Evidence**:
  - `done_when` states:
    `"MyTradingSys/research/malkan_hindi_2026-11-04/WINDOW_RECONCILE_1104.md has a table of every bar-count quote (video id, quote, English or Hindi), a verdict per threshold, and a proposed malkan_divergence_default.json window labelled SOURCED or OURS"` [SOURCED: malkan-window-12-18-vs-hindi.json:10]
  - Deficiencies:
    1. It does not enumerate the required thresholds (e.g. 10, 12, 14/15, 18) to prevent a worker from omitting 18 or 10.
    2. It does not mandate stating whether 18 is `NOT_IN_DATA` in primary sources.
    3. It does not specify whether the proposed window applies to `regular` or `reverse` parameters.
    4. Since `scope_out` excludes editing `malkan_divergence_default.json`, `done_when` should require an exact JSON snippet suitable for the follow-up implementation card.
- **Fix**: Update `done_when` to explicitly require:
  - Table of quotes covering video IDs, language, bar count, and verbatim quote.
  - Explicit threshold verdicts for 10, 12, 15, and 18 (confirming 18 is `NOT_IN_DATA` in Malkan transcripts and retained only as `OURS` per operator relay).
  - Proposed JSON patch with separate regular (`min_bars`, `max_bars`) and reverse (`min_bars`, `max_bars`) windows, labeled SOURCED or OURS.

---

## 3. Recommended Remediation Patch for `malkan-window-12-18-vs-hindi.json`

To enable the card to be safely ACCEPTed, apply the following updates:

```json
{
  "sources": [
    "MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:4-8,14-17",
    "MyTradingSys/system/OPERATOR_DECISIONS.md:1685-1686",
    "raw_transcripts_canonical/GbXnw_tNMtw_raw.txt:379,460",
    "MyTradingSys/research/malkan_hindi_2026-11-04/HINDI_CONCEPTS.md:16-27"
  ],
  "scope_in": [
    "MyTradingSys/research/malkan_hindi_2026-11-04/WINDOW_RECONCILE_1104.md",
    "MyTradingSys/research/malkan_hindi_2026-11-04/HINDI_CONCEPTS.md",
    "MyTradingSys/research/malkan_extract_2026-10-15/extracts",
    "raw_transcripts_canonical/GbXnw_tNMtw_raw.txt",
    "raw_transcripts_canonical/",
    "MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json",
    "MyTradingSys/system/OPERATOR_DECISIONS.md"
  ],
  "steps": [
    "grep the English extracts, GbXnw_tNMtw_raw.txt, and HINDI_CONCEPTS.md for bar-count quotes (3, 5, 7, 10, 12, 14, 15, 18, less than, dilute)",
    "Tabulate each quote with video id, language, context (regular vs reverse divergence), and verbatim text; verify English quotes against transcripts and Hindi quotes against canonical files",
    "State per threshold (10, 12, 15, 18) SOURCED (quote + file:line), OURS, or NOT_IN_DATA; propose separate windows for regular divergence and reverse divergence in malkan_divergence_default.json format labelled SOURCED or OURS"
  ],
  "tests": "python -c \"import pathlib,re; t=pathlib.Path('MyTradingSys/research/malkan_hindi_2026-11-04/WINDOW_RECONCILE_1104.md').read_text(encoding='utf-8'); assert t.count('|')>=25 and all(v in t for v in ['GbXnw_tNMtw','Wvq1TZh8aF0','cQ-y1oULkBw','kVIvcn7T44o','TrZQ4Xat_sQ','TO3pLafk7Us']) and all(th in t for th in ['10','12','15','18']) and ('NOT_IN_DATA' in t or 'OURS' in t) and '```json' in t\"",
  "done_when": "MyTradingSys/research/malkan_hindi_2026-11-04/WINDOW_RECONCILE_1104.md has a table of every bar-count quote (video id, quote, English or Hindi, regular vs reverse), an explicit verdict per threshold (10, 12, 15, 18 with 18 identified as NOT_IN_DATA in trader transcripts), and proposed malkan_divergence_default.json regular and reverse windows labelled SOURCED or OURS in a json block"
}
```

---

## 4. Verification Command for This Review

```powershell
python -c "import pathlib; t=pathlib.Path('MyTradingSys/research/malkan_hindi_2026-11-04/REVIEW_MALKAN_WINDOW_GEMINI_1104.md').read_text(encoding='utf-8'); assert 'VERDICT:' in t"
```

---

VERDICT: FIX-FIRST

---

## Claude spot-check (2026-11-05, Sonnet 5.5; each cite opened and each quote searched in its source)

| # | Finding | Result | What the source shows |
|---|---|---|---|
| 1 | Test passable by a wrong answer | CONFIRMED | card line 65 checks only `|` count, the word SOURCED/OURS and the substring 18. Replaced; mutation-checked (old-style wrong file, missing 18 row, SOURCED 18 with no video id, fake Hindi line, missing reverse keys all fail). |
| 2 | verify_extract_quotes.py cannot check Hindi | CONFIRMED | `norm()` keeps `[a-z0-9%]` (line 36), short-quote skip at 156, empty quote -> MISSING at 206-208 (Gemini wrote 205). Script left alone (out of scope); card test checks Hindi quotes as exact substrings of raw_transcripts_canonical. |
| 3 | GbXnw_tNMtw missing from scope_in | CONFIRMED | no extract mentions GbXnw; only raw_transcripts_canonical/GbXnw_tNMtw_raw.txt. Quotes "number of bars which are less than 15" and "should be between five to fifty" exist, at lines 382 and 461 (the params json and the review say 379 and 460: off by 3 and 1; card now cites 382,461). |
| 4 | Hindi raw transcripts missing from scope_in | CONFIRMED | all 6 exist, 8 lines each; HINDI_CONCEPTS.md is a summary. Added raw_transcripts_canonical/. |
| 5 | OPERATOR_DECISIONS.md missing | CONFIRMED | header at line 1685, text at 1686, contains the 12 / 18 / "after 18 bar" wording. Added to scope_in and sources. |
| 6 | Regular vs reverse conflated | CONFIRMED | params json line 17 is inside the `reverse` block (12-22); regular is lines 4-8 (3..10). live_confluence_feed.py:48-49 WINDOW_STRONG=12 / WINDOW_MAX=18 and div_flags_chart.py:217 carry 12/18. Gemini's claim that the regular range is "under 15 bars (Hindi TrZQ4Xat_sQ:21)" cites a HINDI_CONCEPTS line number as a transcript line: not taken. Card now needs a per-type window, without saying which is right. |
| 7 | Step omits 3, 5, 7, 10 | CONFIRMED | extract_Wvq1TZh8aF0.md:133 "between three and 10" and :127; extract_cQ-y1oULkBw.md:144 "three bars, five bars, seven bars"; HINDI_CONCEPTS.md:45 10-bar quote. Gemini's cites cQ:128,182 and Wvq1:172 not checked: not used. |
| 8 | done_when incomplete | CONFIRMED in part | thresholds and regular/reverse split added. NOT taken: Gemini's "18 identified as NOT_IN_DATA in trader transcripts" (it answers the card; HINDI_CONCEPTS.md:27 covers the 6 Hindi videos only, the English extracts were not searched for 18). |

Blocking findings (1, 2, 3, 6): all CONFIRMED and fixed on the card. Not taken from the proposed patch: the 18 = NOT_IN_DATA wording, bare substring checks for the thresholds, the unverified cites above.

VERDICT after fixes: ACCEPT
