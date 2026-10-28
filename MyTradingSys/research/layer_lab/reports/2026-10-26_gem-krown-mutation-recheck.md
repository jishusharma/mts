# Lab Report: Re-check of GPT Krown Audit Claims (2026-10-28)

**Task**: `gem-krown-mutation-recheck`  
**Card Title**: `[GEMINI] Re-run two GPT claims on Krown tests: weekly completeness and zone cap`  
**Producer**: GPT `gpt-6-luna` ([`MyTradingSys/research/gpt_burn_2026-10-24/gx-krown-audit/report.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-krown-mutation-recheck/MyTradingSys/research/gpt_burn_2026-10-24/gx-krown-audit/report.md))  
**Reviewer**: Google Gemini (Google AI Pro, Antigravity, host DESKTOP-F7IU69N; vendor separation MET)  
**Files Audited**:
- `MyTradingSys/backtest/layers/krown/krown_context.py` (lines 84–100)
- `MyTradingSys/backtest/layers/krown/krown_core.py` (lines 257–285)
- `MyTradingSys/backtest/layers/krown/test_krown_core.py` (lines 71–80)
- `MyTradingSys/research/gpt_burn_2026-10-24/gx-krown-audit/report.md`

*Constraint adherence*: `MyTradingSys/research/gpt_burn_2026-10-24/gx-krown-audit/audit.py` was NOT read, inspected, or imported.

---

## 1. Executive Summary

Both of GPT's audit claims regarding the Krown layer implementation and test suite have been independently executed, re-derived, and **CONFIRMED**:
1. **Weekly Completeness**: [`weekly_from_daily`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-krown-mutation-recheck/MyTradingSys/backtest/layers/krown/krown_context.py#L85-L100) with day offsets `[0, 0, 2, 3, 4, 5, 6]` emits **1 complete week** where **0 complete weeks** are expected. The guard checks only `len(idx) != 7`, accepting a duplicated Monday in place of a missing Tuesday.
2. **Zone Cap Test Blind Spot**: Capping [`zones_from`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-krown-mutation-recheck/MyTradingSys/backtest/layers/krown/krown_core.py#L257-L279) to at most 1 zone (`[:1]`) in memory allows **all 73 tests** in the Krown suite to pass with **0 failures and 0 errors**. [`test_at_most_five_zones`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-krown-mutation-recheck/MyTradingSys/backtest/layers/krown/test_krown_core.py#L71-L80) asserts only `len(zones) <= 5` and does not test for retention of multiple valid zones.

---

## 2. Independent Claim Re-Derivations

### Claim 1: Weekly Completeness with Duplicated Day
- **Code Reference**: [`krown_context.py:85-100`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-krown-mutation-recheck/MyTradingSys/backtest/layers/krown/krown_context.py#L85-L100)
- **Specification Intent**: "Only weeks with all 7 daily bars; lists keyed by week open."
- **Execution Test**:
  - Monday week start: `ws = 1705881600000` (2024-01-22 00:00:00 UTC).
  - Daily bar timestamps constructed with offsets: `[0, 0, 2, 3, 4, 5, 6]` (offset 0 Monday duplicated; offset 1 Tuesday omitted).
  - Executed `weekly_from_daily(t, o, h, l, c)`:
    - Expected output: `len(wt) == 0` (week is incomplete due to missing Tuesday).
    - Actual output: `len(wt) == 1` (week emitted with 7 aggregated rows).
- **Analysis**: Line 93 checks only `if len(idx) != 7: continue`. Because `idx` has 7 elements, it passes the guard despite lacking all 7 distinct ISO weekdays.

### Claim 2: Zone Cap Mutation Blind Spot
- **Code Reference**: [`krown_core.py:257-279`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-krown-mutation-recheck/MyTradingSys/backtest/layers/krown/krown_core.py#L257-L279) and [`test_krown_core.py:71-80`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-krown-mutation-recheck/MyTradingSys/backtest/layers/krown/test_krown_core.py#L71-L80).
- **Execution Test**:
  - Dynamically monkeypatched `krown_core.zones_from` in memory to return `kept[:1]`.
  - Executed entire test suite across all 5 Krown test files:
    - `test_krown_core.py`
    - `test_krown_context.py`
    - `test_krown_events.py`
    - `test_krown_context_artifacts.py`
    - `test_recall_table.py`
  - Results:
    - **Total Tests Run**: 73 (note: 72 tests when GPT audited on 2026-10-24; 1 test added since).
    - **Failures**: 0
    - **Errors**: 0
    - **wasSuccessful**: True
- **Analysis**: [`test_at_most_five_zones`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-krown-mutation-recheck/MyTradingSys/backtest/layers/krown/test_krown_core.py#L71-L80) only tests `self.assertLessEqual(len(kc.zones_at(h, l, c, v, n - 1, p)), 5)`. Returning 1 zone satisfies `<= 5`, so truncation of valid non-overlapping zones is completely unmonitored by the test suite.

---

## 3. Findings

| Severity | File:Line | What is wrong | Evidence | Proposed Fix |
|---|---|---|---|---|
| LOW | [`krown_context.py:85-100`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-krown-mutation-recheck/MyTradingSys/backtest/layers/krown/krown_context.py#L85-L100) | `weekly_from_daily` checks only row count `len(idx) == 7`, allowing malformed input with duplicate days and missing weekdays to be aggregated as a complete week. | Hand-constructed offsets `[0,0,2,3,4,5,6]` emitted 1 complete week instead of 0. | Verify that the 7 timestamps correspond to the 7 distinct daily offsets `(t[i] - ws) // DAY_MS == set(range(7))`, identical to the bucket checking pattern used in `aggregate_4h`. |
| LOW | [`test_krown_core.py:71-80`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-krown-mutation-recheck/MyTradingSys/backtest/layers/krown/test_krown_core.py#L71-L80) | `test_at_most_five_zones` tests only an upper bound (`assertLessEqual(..., 5)`). It does not test that multiple valid non-overlapping zones are preserved when discovered. | In-memory mutation capping `zones_from` to `[:1]` passes all 73 tests with 0 failures and 0 errors. | Add a deterministic multi-zone fixture asserting that exactly `k > 1` distinct non-overlapping zones are extracted and ranked. |

---

## 4. Verdict

**Verdict: SOUND.**  
Both claims reported in GPT's audit (`report.md:19-22`) are reproducible, mathematically sound, and verified on the codebase:
1. `weekly_from_daily` emits 1 complete week on duplicate/missing day input `[0,0,2,3,4,5,6]` where 0 is expected.
2. In-memory mutation capping `zones_from` to 1 zone passes all 73 tests in the Krown test suite without failure.
