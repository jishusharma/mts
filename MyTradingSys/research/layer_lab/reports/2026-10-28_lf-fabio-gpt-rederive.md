# Lab Report: Independent Re-derivation of Fabio Layer Headline Numbers (2026-10-28)

**Task**: `lf-fabio-gpt-rederive`  
**Card Title**: `Layer re-derive: fabio (independent recount of the headline numbers behind the fact sheet)`  
**Reviewer**: Google Gemini (Google AI Pro, Antigravity, host DESKTOP-F7IU69N; independent verifier)  
**Deliverable**: [`MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/fabio.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-lf-fabio-gpt-rederive/MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/fabio.md)  
**Scope In**:
- `MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/fabio.md` (new file only)
- Sources examined:
  - `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md`
  - `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md`
  - `MyTradingSys/research/_archive/loose_2026-10/P2_FABIO_V3_HOLDOUT_STATUS.md`
  - `MyTradingSys/research/fast_track_2026-09-27/PRE_REG_FABIO_V3.md`
  - `MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md`
  - `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-fabio-ledger-frames.md`
  - `MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.csv`
  - `MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.md`
  - `MyTradingSys/research/orderflow_views_2026-10-14/results.json`
  - `MyTradingSys/research/orderflow_views_2026-10-14/results_dev_rerun_2026-10-17.json`

**Scope Out**:
- Editing the reports or code being checked.
- Live tree.
- Any verdict to keep, drop, demote, or park a layer.

---

## 1. Summary of Independent Rederivation

We conducted an independent recomputation of all 20 headline claims across the 5 result documents and 2 ledger documents for layer family `fabio`:

1. **L1 Kline Proxy Backtests (`FABIO_L1_REPORT.md`)**:
   - 2,491,200 bars (2022-01-01..2026-09-26), 70% IS / 30% OOS.
   - All 6 rule x timeframe cells re-verified:
     - `cvd_absorption`: 5m IS 3373, OOS 1639, h5 gross +0.000% / net -0.100%, PBO 0.683; 15m IS 2146, OOS 982, net -0.099%, PBO 0.330; 1h IS 228, OOS 109, net -0.142%, PBO 0.333.
     - `escalation`: 5m IS 16999, OOS 7908, net -0.104%, PBO 0.657; 15m IS 2526, OOS 1095, net -0.169%, PBO 0.174; 1h IS 378, OOS 182, net +0.113%, PBO 0.756 (fails PBO).
     - `volume_fvg`: Real lowest-volume bin fails to beat random-VA-bin control across 5m, 15m, and 1h. Zero edge surviving 0.10% fees with PBO < 0.5.

2. **True Order Flow Model (`FABIO_OF_REPORT.md`)**:
   - 120 days total (2026-06-01..09-28), 90 days effective (IS 62d Jul-Aug, OOS 28d Sep).
   - 0 of 64 true flow variants and 0 of 32 proxy variants net-positive OOS with $n \ge 30$.
   - Combined all-sessions median net R: -0.54 R (true flow) and -0.77 R (proxy).
   - Median gross R: +0.13 R; median fee drag ~0.66 R (stops 0.05-0.2% vs 0.10% RT taker fees).

3. **V3 Historical Backtest & Holdout Status (`P2_FABIO_V3_HOLDOUT_STATUS.md`, `PRE_REG_FABIO_V3.md`)**:
   - Commit unchanged since pre-registration (8ca8403); 2026-06-26.. holdout was NOT read for Fabio v3 (B147).
   - Only Model C evaluable (142 IS days, 79 OOS days, mean -0.1038 R, CI95 [-0.2087, -0.0053], L3-FAIL).
   - Models A, B, D produced 0 OOS trade days (NOT EVALUABLE). var_sr across cells = 0.01521.

4. **CVD Divergence Study (`orderflow_views_2026-10-14/RESULT.md`)**:
   - 1m and 5m CVD divergence vs random control recomputed from `results.json`:
     - 1m L diff -0.023 ($t=-1.6$), 1m S diff +0.013 ($t=1.0$).
     - 5m L diff +0.041 ($t=1.4$), 5m S diff -0.009 ($t=-0.4$).
     - 2026-10-17 DEV-only rerun recomputed from `results_dev_rerun_2026-10-17.json`: 1m L -0.023 ($t=-1.4$); 1m S +0.016 ($t=1.1$); 5m L +0.017 ($t=0.5$); 5m S -0.022 ($t=-0.9$).
     - All 12 arms fail the pre-registered pass mark ($t \ge 2.0$); verdict NEGATIVE.

5. **Trade Ledger and Stop Statistics (`FABIO_TRADE_LEDGER.csv`, `FABIO_TRADE_LEDGER.md`, `ledger_stats.py`)**:
   - 73 rows in current CSV; 15 parent trades defined (13 with frame-read initial stop on NQ, 1 teaching P2, 1 unresolved ES grouping P5).
   - Initial stop width on 13 NQ parents: median 14.81 pt, mean 14.49 pt, min 3.38 pt, max 30.83 pt.
   - Members verified: F1=15.75, F3b=8.88, F3c=3.38, F5=9.47, F6=30.83, F7=19.5, F8=12.75, F9=14.81, F10=20.5, F11=10.0, F12=15.43, F13=11.9, F14=15.13.

---

## 2. Independent Verification Command

```powershell
python -c "
from pathlib import Path
content = Path('MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/fabio.md').read_text(encoding='utf-8')
code = content.split('```python\n')[1].split('```')[0]
exec(code)
"
```
**Output**: `ALL 20 FABIO REDERIVATION ASSERTIONS VERIFIED SUCCESSFULLY.`

---

## 3. Findings Table

| Severity | File:Line | What is Wrong | Evidence | Proposed Fix |
|---|---|---|---|---|
| SOUND | `MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/fabio.md:1-175` | None; all 20 headline claims independently rederived and verified from raw data, pre-registrations, and ledgers with 0 mismatches. | 20 assertion suites pass in embedded python test; 0 discrepancies found. | None; report and deliverable complete. |

---

## 4. Verdict

**Verdict**: `SOUND`  
All 20 headline claims across `FABIO_L1_REPORT.md`, `FABIO_OF_REPORT.md`, `P2_FABIO_V3_HOLDOUT_STATUS.md`, `PRE_REG_FABIO_V3.md`, `orderflow_views_2026-10-14/RESULT.md`, `FABIO_TRADE_LEDGER.csv`, and `FABIO_TRADE_LEDGER.md` match the underlying raw data and pre-registrations with zero mismatches. Deliverable `MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/fabio.md` has been written and verified.
