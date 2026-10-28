# lab-planted-error-trial: Planted-Error Trial Machine Layer

**Date:** 2026-10-23  
**Runner:** Gemini Flash (Antigravity, JIS-NUC)  
**Card:** `lab-planted-error-trial`  
**Decision source:** `MyTradingSys/system/card_specs/codex-unstick-2026-10-23.md` (MIN_CLEAN = 6; 8 shadows round-robin across the 6 clean cards)

---

## 1. Summary of Execution

- **Clean originals inventory:** Scanned `MyTradingSys/system/tasks/archive/*.json` for finished CODEX cards. Exactly 6 cards passed every clean original check (report existence, `tasks.problems`, `lab_flow.gate`, `lab_flow.fingerprint`, and trial rows == runner records count):
  1. `context-factors-v3-crossvendor-review`
  2. `gptb-bb-top-reversal-event-table`
  3. `gptb-funding-extreme-event-table`
  4. `gptb-session-levels-event-table`
  5. `krown-catalogue-gpt-audit`
  6. `lab-audit-tom-ledger-frames`
- **Fail-first test written:** `scripts/dev/test_planted_error_trial.py` was created first and run against the pre-change script. It confirmed failure (`RuntimeError: only 1 clean originals pass all checks; need 10`).
- **Harness implemented:** `scripts/dev/planted_error_trial.py` updated to support `MIN_CLEAN = 6` with 8 shadows across the 8 error classes, round-robin across the 6 clean cards, asserting that clean originals pass all checks and exactly 1 edit hunk is changed per shadow.
- **Trial output artifacts:**
  - `MyTradingSys/research/lab_guy/FLOW_PLANTED_2026-10-18.md`: Catch table per error class with empty columns for Haiku/Flash and Argon/GPT-high model stacks.
  - `MyTradingSys/research/lab_guy/planted/manifest.json`: Full manifest with shadow records, clean originals, machine checks, and skipped candidate reasons.
  - `MyTradingSys/research/lab_guy/planted/01/` through `08/`: Isolated packets containing `card.original.json`, `card.shadow.json`, `report.md`, `trials_excerpt.md`, and `runs_excerpt.jsonl`.

---

## 2. Machine Layer Catch Table

| Error class | Caught | Missed | Rejecting checks |
| :--- | :---: | :---: | :--- |
| **deleted trial rows** | 1 | 0 | `tasks.trial_ledger_runs_count` |
| **edited gate constant** | 0 | 1 | none (semantic prose edit) |
| **expected value copied from code** | 0 | 1 | none (semantic prose edit) |
| **holdout leak** | 0 | 1 | none (semantic prose edit) |
| **mislabelled SOURCED number** | 0 | 1 | none (semantic prose edit) |
| **one-bar shift** | 0 | 1 | none (semantic prose edit) |
| **wrong data copy** | 0 | 1 | none (semantic prose edit) |
| **zero slippage** | 0 | 1 | none (semantic prose edit) |

Total shadows: 8. Machine layer caught: 1 (`deleted trial rows`). Missed: 7 (prose-only semantic errors outside machine-check AST/regex visibility, reserved for model evaluation stacks).

---

## 3. Verification Commands & Outputs

1. `python -m unittest scripts/dev/test_planted_error_trial.py`
   - Outcome: `Ran 1 test in 6.314s. OK`
2. `python scripts/dev/planted_error_trial.py`
   - Manifest written to `MyTradingSys/research/lab_guy/planted/manifest.json`
3. Pre-change test failure:
   - Command: `python -m unittest scripts/dev/test_planted_error_trial.py`
   - Output: `RuntimeError: only 1 clean originals pass all checks; need 10`
