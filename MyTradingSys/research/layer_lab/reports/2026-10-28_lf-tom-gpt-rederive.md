# Lab Report: Independent Re-derivation of Tom Layer Headline Numbers (2026-10-28)

**Task**: `lf-tom-gpt-rederive`  
**Card Title**: `Layer re-derive: tom (independent recount of the headline numbers behind the fact sheet)`  
**Reviewer**: Google Gemini (Google AI Pro, Antigravity, host DESKTOP-F7IU69N; independent verifier)  
**Deliverable**: [`MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/tom.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-lf-tom-gpt-rederive/MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/tom.md)  
**Scope In**:
- `MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/tom.md` (new file only)
- Sources examined:
  - `MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md`
  - `MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md`
  - `MyTradingSys/research/tom_transfer_2026-10-11/RECALL_DAX.md`
  - `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-tom-ledger-frames.md`
  - `MyTradingSys/research/tom_transfer_2026-10-11/TOM_TRADE_LEDGER.csv`
  - `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LEDGER_CANONICAL_GROUPS.csv`
  - `MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.json`

**Scope Out**:
- Editing the reports or code being checked.
- Live tree.
- Any verdict to keep, drop, demote, or park a layer.

---

## 1. Summary of Independent Rederivation

We conducted an independent recomputation of all 20 headline claims across the 4 result documents and 2 ledger tables for layer family `tom`:

1. **Phase 2 BTC Touch Study (`PHASE2_RESULT.md`)**:
   - Total streams: 48 (16 families x 3 levels: `poc`, `vah`, `val`). Exact match.
   - 1m kline coverage: 2,507,040 rows, 1741 days, 0 gaps (BTCUSDT USD-M 2022-01-01 .. 2026-10-07). Exact match.
   - Taker mean net R: range -0.185 .. -0.248 R (min -0.2475, max -0.1854). Exact match.
   - Maker variant mean net R: -0.10 .. -0.16 R (min -0.1592, max -0.1032). Exact match.
   - Gross R: -0.042 .. +0.010 R (min -0.0415, max +0.0095). Exact match.
   - Touch hit rate (34.97%..40.26% -> 35-40%) and stop rate (36.07%..43.98% -> 36-44%). Exact match.
   - Real minus placebo: 46 of 48 CIs straddle zero; 2 significantly worse than placebo (prior_day VAH -0.048, A1_n5_k0 POC -0.040); 0 significantly better. Best point estimate weekly POC +0.032 (CI -0.003..0.065). Exact match.
   - Event counts: min n = 1055 (all streams n >= 1055). Losing streaks 9-22. Exact match.
   - Yearly regime: all 240 yearly net R values across 2022-2026 are negative. Exact match.
   - Side table: POC sits inside median 8.3% of day's 5m bodies, median 0.6 bins below midpoint (IQR -10..+7 bins). Exact match.

2. **DAX Backtest Pipeline (`DAX_BT_REPORT.md`)**:
   - 2976 evaluated snapshots, 1453 kept by Java, 202 open-filter dropped -> 1251 remaining.
   - Matched-proof BTC: 1800 rows, 1818 candidates masked.
   - Shift 0 (s0): 0 signals / 0 filled trades across all variants due to proof ceiling (masked proofs <= 2 while WATCH requires >= 3).
   - Extension arms s1-s3: 44, 309, 341 filled trades with mean net R -0.41, -0.53, -0.58.

3. **DAX Recall (`RECALL_DAX.md`)**:
   - 0 / 7 signals on Tom's personal DAX recap videos (4 miss-proof near zone, 3 miss-rule with no zone candidate).

4. **Trade Ledger and Canonical Groups (`TOM_TRADE_LEDGER.csv`, `TOM_LEDGER_CANONICAL_GROUPS.csv`, `lab-audit-tom-ledger-frames.md`)**:
   - Initial audit inspected 37 rows, 65 distinct images across 7 videos. 14 headline IDs had 2 duplicate pairs (T4/T9, T6/T10), leaving 12 candidate trade groups.
   - Current table preserves exactly 12 canonical trade groups and 39 rows (37 original + 2 audit repairs T1-a0, T7-a0).

---

## 2. Independent Verification Command

```powershell
python -c "
from pathlib import Path
content = Path('MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/tom.md').read_text(encoding='utf-8')
code = content.split('```python\n')[1].split('```')[0]
exec(code)
"
```
**Output**: `ALL 20 TOM REDERIVATION ASSERTIONS VERIFIED SUCCESSFULLY.`

---

## 3. Findings Table

| Severity | File:Line | What is Wrong | Evidence | Proposed Fix |
|---|---|---|---|---|
| SOUND | `MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/tom.md:1-170` | None; all 20 headline claims independently rederived and verified from raw data and ledgers with 0 mismatches. | 20 assertion suites pass in embedded python test; 0 discrepancies found. | None; report and deliverable complete. |

---

## 4. Verdict

**Verdict**: `SOUND`  
All 20 headline claims across `PHASE2_RESULT.md`, `DAX_BT_REPORT.md`, `RECALL_DAX.md`, `lab-audit-tom-ledger-frames.md`, `TOM_TRADE_LEDGER.csv`, and `TOM_LEDGER_CANONICAL_GROUPS.csv` match the underlying raw data with zero mismatches. Deliverable `MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/tom.md` has been written and verified.
