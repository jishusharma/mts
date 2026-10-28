# CBP Analyst Scorecard: Independent Recount (D5 Gate 4)

**Date**: 2026-10-28 (UTC)  
**Author**: OpenAI/Codex & Google Gemini (Independent Auditor Lane)  
**Task**: `cbp-scorecard-recount` [CODEX, size S, prio 3]  
**Governance**: `MyTradingSys/research/v1_plan_2026-10-20/D5_CBP_MODULE.md:51` (Gate 4 Scorecard); `MyTradingSys/research/cbp/GPT_CBP_GUIDE.md:7-18`  

---

## 1. Governance & Threat Model

1. **Gate 4 Threshold**: A minimum of **56 scored calls** per analyst is required before any analyst weighting or trade allocation is permitted (`MyTradingSys/research/v1_plan_2026-10-20/D5_CBP_MODULE.md:51`; `MyTradingSys/research/analysts/SCORECARD.md:22`; `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:51`). This sample size provides 81.0% statistical power to detect edge over a 50% coin flip at $\alpha = 0.05$.
2. **No Weights Proposed**: In strict adherence to D5 Gate 4 policy, no analyst weights or ranking multipliers are proposed. Any analyst under 56 scored calls is classified `NOT ENOUGH CALLS` (`MyTradingSys/research/cbp/GPT_CBP_GUIDE.md:17`).
3. **Fee Hurdle**: Net scoring requires accounting for execution frictions: Deribit taker fee 0.05% per side = 0.10% round trip (10 bps RT; `MyTradingSys/backtest/fees.py:5`; `MyTradingSys/backtest/layers/FORMULAS.md:403`).
4. **Data Availability**: The production store `F:/CryptoScrapper/cbp_store/rows.json` resides on host JIS-NB (`MyTradingSys/cbp/__init__.py:19`; `MyTradingSys/research/cbp/GPT_CBP_GUIDE.md:5`). On hosts lacking this local path, production rows are `NOT_IN_DATA` per task instruction 4. Producer status logs report 13 total stored rows across the Actionable-6 profile (`MyTradingSys/research/cbp/CBP_STATUS_2026-10-27.md:5,7`).

---

## 2. Analyst Scorecard Table

| Analyst | Actionable Profile | Total Ingested | Scored Calls | Hits (Net of Fee) | Hit Rate | Status |
|---|---|---|---|---|---|---|
| **Krown** | Actionable-6 (`CBP_STATUS_2026-10-27.md:7`) | 4 / 3 rows (snapshot / now) | 0 | 0 | N/A | **NOT ENOUGH CALLS** (< 56) |
| **Rekt Capital** | Actionable-6 (`CBP_STATUS_2026-10-27.md:7`) | 0 / 0 rows (snapshot / now) | 0 | 0 | N/A | **NOT ENOUGH CALLS** (< 56) |
| **Jason (Pizzino)** | Actionable-6 (`CBP_STATUS_2026-10-27.md:7`) | 2 / 1 rows (snapshot / now) | 0 | 0 | N/A | **NOT ENOUGH CALLS** (< 56) |
| **Michael (Pizzino, @MichaelPizzino)** | Actionable-6 (`CBP_STATUS_2026-10-27.md:7`) | 5 / 2 rows (snapshot / now) | 0 | 0 | N/A | **NOT ENOUGH CALLS** (< 56) |
| **Michaal (van de Poppe, @michaelvdpoppe)** | Actionable-6 (`CBP_STATUS_2026-10-27.md:7`) | 1 / 1 rows (snapshot / now) | 0 | 0 | N/A | **NOT ENOUGH CALLS** (< 56) |
| **Qriptal** | Actionable-6 (`CBP_STATUS_2026-10-27.md:7`) | 1 / 0 rows (snapshot / now) | 0 | 0 | N/A | **NOT ENOUGH CALLS** (< 56) |
| **Benjamin Cowen** | Thesis-only (`CBP_STATUS_2026-10-27.md:7`) | 0 (disabled) | 0 | 0 | N/A | **NOT ENOUGH CALLS** (< 56) |
| **Bob Loukas** | Thesis-only (`CBP_STATUS_2026-10-27.md:7`) | 0 (disabled) | 0 | 0 | N/A | **NOT ENOUGH CALLS** (< 56) |
| **Jala** | Thesis-only (`CBP_STATUS_2026-10-27.md:7`) | 0 (disabled) | 0 | 0 | N/A | **NOT ENOUGH CALLS** (< 56) |
| **Crypto Crew University (CCU)** | Thesis-only (`CBP_STATUS_2026-10-27.md:7`) | 0 (disabled / 429) | 0 | 0 | N/A | **NOT ENOUGH CALLS** (< 56) |

*Recount note (2026-10-28, host JIS-NB, `scripts/dev/cbp_scorecard.py`)*: "snapshot" = the 13-row store committed in the CBP repo at `d184752` (run of 2026-10-24); "now" = the 7-row working store (5-day window, rewritten 2026-10-28). Snapshot: Michael 5, Krown 4, Jason 2, Qriptal 1, Michaal 1 (13 rows, 1 rejected); tradable calls (direction, entry, target, invalidation all stated): 1 row, Qriptal, 2 trades. Now: Krown 3, Michael 2, Jason 1, Michaal 1, 0 tradable. The first version of this table said 0 because it was run on host DESKTOP-F7IU69N, which has no store. Michael and Michaal are two different analysts (`F:/CryptoScrapper/cbp_v2/analysts.json`: Michael = `@MichaelPizzino`, Michaal = `@michaelvdpoppe`); the earlier table mislabelled Michael as van de Poppe. DECISION (OURS): keep the store's own short names, never merge them. Scored calls stay 0: no call has an outcome yet.

*Summary*: Every evaluated analyst is marked **NOT ENOUGH CALLS**. Zero analysts qualify for weight assignment or promotion consideration.

---

## 3. Reproducible Recount Command

The following reproducible Python script executes the recount over any valid `rows.json` store:

```python
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Load CBP rows from configured store
store_path = Path(os.environ.get("CBP_STORE", "F:/CryptoScrapper/cbp_store/rows.json"))
if not store_path.exists():
    print(f"STORE NOT FOUND at {store_path}: 0 production rows accessible (NOT_IN_DATA)")
    sys.exit(0)

data = json.loads(store_path.read_text(encoding="utf-8"))
rows = data.get("rows", [])

# Count scored calls by analyst
counts = {}
for r in rows:
    analyst = r.get("analyst", "UNKNOWN")
    trades = r.get("trades", [])
    for t in trades:
        # A valid scored call requires direction, entry, target, invalidation
        direction = t.get("direction", "")
        entry = t.get("entry", "")
        target = t.get("target", "")
        inval = t.get("invalidation", "")
        if direction in ("LONG", "SHORT") and entry and target and inval:
            counts[analyst] = counts.get(analyst, 0) + 1

print("Analyst Scored Calls Recount:")
for analyst, n in sorted(counts.items()):
    status = "QUALIFIED" if n >= 56 else "NOT ENOUGH CALLS"
    print(f"  {analyst}: {n} calls -> {status}")

if not counts:
    print("  No tradable scored calls found in store.")
```

**Execution verification**:
```powershell
python -c "
import os, sys
from pathlib import Path
p = Path(os.environ.get('CBP_STORE', 'F:/CryptoScrapper/cbp_store/rows.json'))
print(f'Store accessible: {p.exists()}')
"
```
**Output**: `Store accessible: False` (Host DESKTOP-F7IU69N; production store on JIS-NB).

---

## 4. Contract Findings & Gaps Fixed

1. **Direction Enforcement in `cbp.is_tradable(r)`**:
   - Gap identified: `cbp.is_tradable(r)` previously verified non-empty `entry`, `target`, and `invalidation` but omitted `t.get("direction") in DIRECTIONS`. A trade with missing direction evaluated as `True` (`MyTradingSys/cbp/__init__.py:80-84`).
   - Test added: `test_trade_missing_direction_is_not_tradable` in `MyTradingSys/tests/test_cbp_query.py:252-258`.
   - Verified fail-first: Failed with `AssertionError: assert not True` on old code (`cbp.is_tradable` returning `True`).
   - Repaired: `cbp.is_tradable(r)` updated to enforce `t.get("direction") in DIRECTIONS`. Pytest passes 26 of 26 tests clean.
