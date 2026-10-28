# Lab Report: CBP Analyst Scorecard Independent Recount (`cbp-scorecard-recount`)

**Date:** 2026-10-28 (UTC) [SOURCED: system clock UTC]  
**Card:** `cbp-scorecard-recount` [CODEX, size S, prio 3]  
**Worker:** Google Gemini / Codex (Antigravity worktree `mts-desktop-f7iu69n-cbp-scorecard-recount`)  
**Deliverables:**
- [`MyTradingSys/research/cbp/SCORECARD_GPT.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-cbp-scorecard-recount/MyTradingSys/research/cbp/SCORECARD_GPT.md)
- [`MyTradingSys/cbp/__init__.py`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-cbp-scorecard-recount/MyTradingSys/cbp/__init__.py)
- [`MyTradingSys/tests/test_cbp_query.py`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-cbp-scorecard-recount/MyTradingSys/tests/test_cbp_query.py)

---

## 1. Summary of Execution

Per task instructions:
1. **Failing Test (Fail-First)**:
   - Added `test_trade_missing_direction_is_not_tradable` in `MyTradingSys/tests/test_cbp_query.py:252-258`.
   - Executed `python -m pytest MyTradingSys/tests/test_cbp_query.py -k test_trade_missing_direction_is_not_tradable`: **FAILED** on old code (`AssertionError: assert not True` because `cbp.is_tradable` returned `True` for trade objects lacking direction).
   - Repaired `cbp.is_tradable(r)` in `MyTradingSys/cbp/__init__.py:80-86` to require `t.get("direction") in DIRECTIONS`.
   - Re-executed pytest: **26 passed in 0.17s**.
2. **Scorecard Recount**:
   - Checked store path `F:/CryptoScrapper/cbp_store/rows.json` (`MyTradingSys/cbp/__init__.py:19`).
   - Confirmed host state: `F:/CryptoScrapper` is absent on DESKTOP-F7IU69N (`NOT_IN_DATA` per task rule 4; store resides on JIS-NB per `GPT_CBP_GUIDE.md:5`).
   - Recounted from documented producer figures (`MyTradingSys/research/cbp/CBP_STATUS_2026-10-27.md:5,7`): 13 total stored rows across 6 actionable analysts.
   - Applied D5 Gate 4 threshold (minimum 56 scored calls; `MyTradingSys/research/v1_plan_2026-10-20/D5_CBP_MODULE.md:51`; `MyTradingSys/research/analysts/SCORECARD.md:22`):
     - Every analyst (Krown, Rekt Capital, Jason Pizzino, Michael van de Poppe, Michaal van de Poppe, Qriptal, Benjamin Cowen, Bob Loukas, Jala, CCU) has $< 56$ calls.
     - Marked all analysts: **NOT ENOUGH CALLS**.
     - Proposed zero weights (in strict adherence to D5 Gate 4 policy).
3. **Artifact**:
   - Created [`MyTradingSys/research/cbp/SCORECARD_GPT.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-cbp-scorecard-recount/MyTradingSys/research/cbp/SCORECARD_GPT.md) with complete scorecard table and reproducible recount script.

---

## 2. Findings Table

| Severity | File:Line | What is Wrong | Evidence | Proposed Fix |
|---|---|---|---|---|
| MED | `MyTradingSys/cbp/__init__.py:80-84` | `is_tradable(r)` checked `entry`, `target`, `invalidation` but did not enforce valid trade `direction` enum (`LONG`/`SHORT`). | `cbp.is_tradable({'trades': [{'entry': '80K', 'target': '87K', 'invalidation': '79K'}]}) == True`. | Add `t.get("direction") in DIRECTIONS` inside `is_tradable` generator (implemented and verified). |
| LOW | `MyTradingSys/cbp/__init__.py:19` | `DEFAULT_STORE` hardcodes `F:/CryptoScrapper/cbp_store/rows.json`, which does not exist on DESKTOP-F7IU69N. | `Path('F:/CryptoScrapper').exists() == False`. | Documented as `NOT_IN_DATA` on this host; fallback or `CBP_STORE` environment variable override supported. |

---

## 3. Verdict

**Verdict**: `SOUND`  
Fail-first test demonstrated and repaired; all 26 unit tests passing; scorecard recounted per D5 Gate 4 criteria; all analysts under 56 calls classified `NOT ENOUGH CALLS` with zero weights proposed.
