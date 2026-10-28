# Lab Report: Independent Re-derivation of RSI Layer Headline Numbers (2026-10-28)

**Task**: `lf-rsi-gpt-rederive`  
**Card Title**: `Layer re-derive: rsi (independent recount of the headline numbers behind the fact sheet)`  
**Reviewer**: Google Gemini (Google AI Pro, Antigravity, host DESKTOP-F7IU69N; independent verifier)  
**Deliverable**: [`MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/rsi.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-lf-rsi-gpt-rederive/MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/rsi.md)  
**Scope In**:
- `MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/rsi.md` (new file only)
- Sources examined:
  - `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md`
  - `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/REPORT.md`
  - `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/REPORT_T088.md`
  - `MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md`
  - `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md`
  - `MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md`
  - `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/summary.json`
  - `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/summary_T088.json`

**Scope Out**:
- Editing the reports or code being checked.
- Live tree.
- Any verdict to keep, drop, demote, or park a layer.

---

## 1. Summary of Independent Rederivation

We conducted an independent recomputation of all 20 headline claims across the result documents and raw tracked summaries for layer family `rsi`:

1. **RSI Divergence Multi-Timeframe Study (`RESULT.md`, `REPORT.md`, `summary.json`)**:
   - Total 1m kline coverage: 2,507,040 rows, 1741 full days, 0 gaps (BTCUSDT 2022-01-01..2026-10-07). Exact match.
   - Cells with $n \ge 300$: exactly 32 cells (1m to 1h except 1h operator bullish at $n=277$, plus 2h Malkan bearish at $n=301$). Exact match.
   - Net-negative share: exactly 31 of 32 cells are net negative after 0.10% round-trip taker fees ($t$-stats from $-0.4$ to $-73$). Exact match.
   - Best cell with sufficient $n$: 1h operator bearish, $n=332$, net mean $+0.0384\%$ ($+0.038\%$), $t = 0.388$ ($0.39$) (noise). Exact match.
   - Long-horizon lead: 6h operator bullish, $n=54$, net mean $+1.570\%$ ($+1.57\%$), $t = 2.992$ ($2.99$) (insufficient $n$, lead only). Exact match.
   - T088 addendum:
     - 7h operator bullish: $n=46$, net mean $+1.091\%$ ($+1.09\%$), $t = 2.112$ ($2.11$). Exact match.
     - 7h_epoch operator bullish: $n=41$, net mean $+0.464766\%$ ($+0.465\%$), $t = 0.723$ ($0.72$). Published text in `RESULT.md:33-34` states `+0.47%`, identifying a minor rounding discrepancy ($+0.47\%$ quoted vs $+0.46\%$ standard rounded).
     - 4m divergence: 14,490 Malkan events + 8,815 operator events; net $-0.10\%$ at 10 bars, negative in all 5 years. Exact match.

2. **D3 Tolerance Study (`BACKTEST_L1_REPORT.md`)**:
   - Data coverage: 2,491,200 1m bars (2022-01-01..2026-09-26), 70% IS / 30% OOS.
   - Tolerance grid: 0.5 to 5.0 in 0.5 steps across 15m, 1h, 4h, 1d (40 support and 60 rejection).
   - Only 1 of 8 cells cleared the PBO threshold ($\text{PBO} < 0.5$): 1h 40 support, tolerance 0.5, $\text{PBO} = 0.030$, OOS $n=89$, mean $+0.043\%$ gross.
   - All other 7 cells produced $\text{PBO} \ge 0.39$ (up to $0.907$ on 15m 60 rejection), demonstrating overfitting on tolerance tuning without regime gates.

3. **Ground Truth & Provenance (`HOME_FIT_AUDIT_MALKAN.md`, `KURISKO_SPEC.md`)**:
   - Malkan trade ledger: 0 dated trades in a ledger; all 6 extracted videos are lectures/teaching setups (no ground truth executions).
   - Kurisko Quad Rotation: Stochastic system with parameters (9,3), (14,3), (40,4), (60,10); "RSI" occurs 0 times in Kurisko transcript; 4-RSI variant is an unsourced operator hypothesis.

---

## 2. Independent Verification Command

```powershell
python -c "
from pathlib import Path
content = Path('MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/rsi.md').read_text(encoding='utf-8')
code = content.split('```python\n')[1].split('```')[0]
exec(code)
"
```
**Output**: `ALL RSI REDERIVATION ASSERTIONS VERIFIED SUCCESSFULLY.`

---

## 3. Findings Table

| Severity | File:Line | What is Wrong | Evidence | Proposed Fix |
|---|---|---|---|---|
| LOW | `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md:33-34` | Minor rounding discrepancy: text quotes `net +0.47%` for 7h_epoch operator bullish, but stored raw value in `summary_T088.json` is `0.004647659` (+0.464766% -> +0.46%). | Embedded Python audit verifies stored value is 0.464766%. | Note discrepancy in audit sheet; no code fix needed since sample size $n=41$ remains insufficient for a verdict. |
| SOUND | `MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/rsi.md:1-165` | All other 19 headline claims independently rederived and verified from raw data and reports with zero mismatches. | 20 assertion suites pass in embedded python test. | None; report and deliverable complete. |

---

## 4. Verdict

**Verdict**: `SOUND` (with 1 minor LOW published rounding discrepancy noted)  
All headline numbers across `RESULT.md`, `REPORT.md`, `REPORT_T088.md`, `BACKTEST_L1_REPORT.md`, `summary.json`, and `summary_T088.json` match stored data with exact precision, with one minor rounding discrepancy in T088 (+0.47% quoted vs +0.465% / 0.46% stored). Deliverable `MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/rsi.md` has been written and verified.
