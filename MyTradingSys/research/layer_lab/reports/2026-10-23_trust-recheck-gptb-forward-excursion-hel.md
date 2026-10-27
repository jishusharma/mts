# Trust re-check: gptb-forward-excursion-helper (2026-10-28)

**Verdict: VERIFIED-C2.** Cross-vendor independent reviewer requirement is satisfied: Producer is CODEX / GPT, Reviewer is Gemini (Google, Google AI Pro, Antigravity, DESKTOP-F7IU69N). The pure forward excursion helper definitions and tests have been independently re-derived and verified against repo code. The fail-first mutation test turned `test_same_bar_touching_both_levels_counts_stop_first` RED. No holdout, outcome, or market data was read or rerun; audited source files remain unchanged.

## 1. Producer and Reviewer Identity

- **Producer**: CODEX / OpenAI GPT (`gpt-6-luna`, commit `6035523a7674`, archived task `MyTradingSys/system/tasks/archive/gptb-forward-excursion-helper.json`).
- **Reviewer**: Google Gemini (Google AI Pro, Antigravity, host DESKTOP-F7IU69N).
- **Vendor Separation**: **MET**. Producer is OpenAI / GPT; Reviewer is Google / Gemini (`Producer != Reviewer` strictly satisfied).

## 2. Independent Calculations and Re-Derivations

Derived directly from `REPORT.md` and task card goal (`forward_excursion(bars, i_entry, side, r_price, horizon) -> mfe_r, mae_r, first_hit`), where `stop_1R` = stop level touched first, `target_1R` = +1R level touched first, and a bar touching both levels counts stop first (fail-closed, OURS):

| Case | Independent Hand Calculation | Function Output | Status / Source |
|---|---|---|---|
| **Case 1: Long target touched first**<br>Entry close 100, R=2, Horizon=1.<br>Bar 1: High 102.5, Low 99.5.<br>Target=102, Stop=98. | Target reached: `102.5 >= 102`.<br>Stop untouched: `99.5 > 98`.<br>`MFE = (102.5 - 100) / 2 = 1.25R`<br>`MAE = (100 - 99.5) / 2 = 0.25R`<br>`first_hit = target_1R` | `{'mfe_r': 1.25, 'mae_r': 0.25, 'first_hit': 'target_1R', 'truncated': False}` | **MATCH**<br>[`event_table.py:30-45`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-trust-recheck-gptb-forward-excursion-hel/MyTradingSys/research/layer_lab/forward_excursion/event_table.py#L30-L45) |
| **Case 2: Short stop touched first**<br>Entry close 100, R=2, Horizon=1.<br>Bar 1: High 102.5, Low 99.5.<br>Target=98, Stop=102. | Stop reached: `102.5 >= 102`.<br>Target untouched: `99.5 > 98`.<br>`MFE = (100 - 99.5) / 2 = 0.25R`<br>`MAE = (102.5 - 100) / 2 = 1.25R`<br>`first_hit = stop_1R` | `{'mfe_r': 0.25, 'mae_r': 1.25, 'first_hit': 'stop_1R', 'truncated': False}` | **MATCH**<br>[`event_table.py:30-45`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-trust-recheck-gptb-forward-excursion-hel/MyTradingSys/research/layer_lab/forward_excursion/event_table.py#L30-L45) |
| **Case 3: Long bar touching both levels**<br>Entry close 100, R=2, Horizon=1.<br>Bar 1: High 103.0, Low 97.0.<br>Target=102, Stop=98. | Both reached: `103 >= 102` and `97 <= 98`.<br>Rule: Same bar touching both counts stop first.<br>`MFE = (103 - 100) / 2 = 1.5R`<br>`MAE = (100 - 97) / 2 = 1.5R`<br>`first_hit = stop_1R` | `{'mfe_r': 1.5, 'mae_r': 1.5, 'first_hit': 'stop_1R', 'truncated': False}` | **MATCH**<br>[`event_table.py:40-45`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-trust-recheck-gptb-forward-excursion-hel/MyTradingSys/research/layer_lab/forward_excursion/event_table.py#L40-L45) |

All 3 independent derivations match the implementation and fixture behavior exactly.

## 3. Test Suite and Mutation Check

- **Baseline Test Command**:
  `python -m pytest MyTradingSys/research/layer_lab/forward_excursion/test_event_table.py -q`
  Result: **5 passed in 0.08s**.

- **Fail-First Mutation Probe**:
  Mutated lines 40-44 in `MyTradingSys/research/layer_lab/forward_excursion/event_table.py` to prioritize `hit_target` over `hit_stop`:
  ```python
  if first_hit is None:
      if hit_target:
          first_hit = "target_1R"
      elif hit_stop:
          first_hit = "stop_1R"
  ```
  Executed test command:
  Result: **1 failed, 4 passed in 0.28s**.
  - `FAILED test_same_bar_touching_both_levels_counts_stop_first`:
    `AssertionError: assert 'target_1R' == 'stop_1R'`
    `- stop_1R`
    `+ target_1R`
  - Mutation killed; `event_table.py` was immediately reverted to the original source.
  - Subsequent baseline run: **5 passed in 0.08s**.

## 4. Tag Proposal

**Tag Proposal: VERIFIED-C2.**
- Vendor separation requirement is fully satisfied (Producer: OpenAI GPT; Reviewer: Google Gemini).
- Independent hand calculations and helper output match in all 3 test cases.
- Fail-first mutation verifies that the test suite detects any compromise of the fail-closed stop-first priority.
- No market, outcome, or holdout data was read or rerun.
