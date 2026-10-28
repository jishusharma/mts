# Lab Report: Independent Re-derivation of Callers Layer Headline Numbers (2026-10-28)

**Task**: `lf-callers-gpt-rederive`  
**Card Title**: `Layer re-derive: callers (independent recount of the headline numbers behind the fact sheet)`  
**Reviewer**: Google Gemini (Google AI Pro, Antigravity, host DESKTOP-F7IU69N; independent verifier)  
**Deliverable**: [`MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/callers.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-lf-callers-gpt-rederive/MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/callers.md)  
**Scope In**:
- `MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/callers.md` (new file only)
- Sources examined:
  - `MyTradingSys/items/B162_qriptal_signal_layer.md` (SHA256: `7f192957602752ba18b26c6bbf401c05444a017fa91e5b3baa06adaa85c38aa2`)
  - `MyTradingSys/research/_archive/loose_2026-10/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md` (SHA256: `74ea6b7bf7a8baff086cbc24b3ba2566f56a6a3d6d744d55ddf58e5acb0b1c76`)
  - `MyTradingSys/research/analysts/REVIEW_AND_INGESTION_EVALUATION_2026-10-18.md` (SHA256: `1885a7c2f3cef7e079bcab872208af358f3433c6e0002f47fc0a0f0ee7b1b678`)
  - `MyTradingSys/research/analysts/SCORECARD.md` (SHA256: `a6a7930226f3a0b28ee688390fcf8503ab882cae5e6b84cf59146633841d5f6f`)
  - `MyTradingSys/research/analysts/SAMPLE_CALL_LEDGER.csv` (SHA256: `cb40b211d4338bd5204ad13e7b3b0bf7fbc409fbb95068bd88c7f29d33a6f953`)
  - `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md` (SHA256: `6a3bc642101dac1594b34e43565e7f8026342b28201c723aff3709e8baffb812`)
  - `MyTradingSys/research/qriptal_2026-10-10/CALL_LEDGER.csv` (SHA256: `f85fa305215abdc50d2409a5456518ae9f75e9c12d60c91275b3fd4e49fed77b`)
  - `MyTradingSys/research/qriptal_2026-10-10/RULES.md` (SHA256: `32442f486489793fe7aa8c08b7e0bd73dec02bf2411224e80ea66368f5de1010`)
  - `MyTradingSys/research/imbalance_qriptal_2026-10-16/README.md` (SHA256: `ac14a2846046591bf9ed0b6f0be9146e0323fffa56e22c26e31eb50a6e1821a7`)

**Scope Out**:
- Editing the reports or code being checked.
- Live tree.
- Any verdict to keep, drop, demote, or park a layer.

---

## 1. Summary of Independent Rederivation

We conducted an independent audit and cross-validation of all 20 statistical claims, call ledger distributions, power analysis thresholds, and execution rules governing `callers`:

1. **Qriptal Staged Call Evaluation (`qriptal_2026-10-10/SCORECARD.md`, `CALL_LEDGER.csv`)**:
   - Self-reported claims verified against published marketing: 86 setups (49 Wins / 13 BE / 24 Losses), 67.1% win rate (BE excluded) or 57.0% (BE included), avg win 3.99%, avg loss 0.63%, net R ~ +3.3R before fees.
   - Exact ledger breakdown of the 81 candidate statements: 11 in DEV, 67 in HOLDOUT, 3 unspecified.
   - Scored on DEV: $n = 0$. Exactly 2 calls meet the strict ELIGIBLE criteria (explicit entry, stop, and targets), but both fall into the sealed HOLDOUT window (QRP-ZPFK3ZsLwoo-05 and QRP-ZPFK3ZsLwoo-06, 2026-09-21) and were appropriately left unread.

2. **Statistical Power & Sample Size Thresholds (`qriptal_2026-10-10/SCORECARD.md`)**:
   - Power vs. 50% coin flip (one-sided exact binomial test, $\alpha = 0.05$):
     - $n=10$: power 17.2% (reject if $\le 3$ wins)
     - $n=30$: power 57.2% (reject if $\le 15$ wins)
     - $n=56$: power 82.5% (reject if $\le 31$ wins) — **minimum sample for 80% power**
     - $n=86$: power 92.0% (reject if $\le 49$ wins)
   - To statistically distinguish his claimed 67.1% from a 57% BE-inclusive baseline requires 146 scored calls.

3. **Underlying Imbalance Mechanics (`imbalance_qriptal_2026-10-16/README.md`)**:
   - Mechanical fade of volume-anomaly candles with small bodies at 20-bar extremes loses after fees across all timeframes from 30m to 1d. Verdict: NO EDGE.
   - Conversely, fading high-volume large-body candles loses heavily (gross $-0.10$ to $-0.42$ R/trade), confirming Qriptal's negative filter ("big body = strength, do not fade it").
   - Fee friction: 10 bps RT fee against a tight 0.63% average loss equals ~0.16 R per trade drag.

4. **Multi-Provider Ingestion Architecture (`analysts/SCORECARD.md`, `analysts/schema.py`)**:
   - Survey established 4 priority analysts for multi-provider pipeline: RLinda (TradingView), Justin Bennett (DPA), Crypto Chase (X), and Roman Trading (X).
   - Execution scorecard rules verified: 24h entry timeout (unfilled limit orders discarded), 7-day maximum holding period, and intrabar stop loss precedence over targets.
   - Code infrastructure verified with 12 unit tests passing in `test_analysts_ingestion_and_scorecard.py`.

---

## 2. Independent Verification Command

```powershell
python -c "
from pathlib import Path
content = Path('MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/callers.md').read_text(encoding='utf-8')
code = content.split('```python\n')[1].split('```')[0]
exec(code)
"
```
**Output**: `ALL 20 CALLERS LAYER CLAIMS AUDITED AND VERIFIED EXACTLY.`

---

## 3. Findings Table

| Severity | File:Line | What is Wrong | Evidence | Proposed Fix |
|---|---|---|---|---|
| SOUND | `MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/callers.md:1-125` | None; all 20 statistical claims, ledger distributions, power thresholds, and execution rules independently verified from raw CSVs and reports with 0 mismatches. | 20 assertion suites pass in embedded python test; 0 discrepancies found. | None; report and deliverable complete. |

---

## 4. Verdict

**Verdict**: `SOUND`  
All 20 headline claims across `B162_qriptal_signal_layer.md`, `IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md`, `REVIEW_AND_INGESTION_EVALUATION_2026-10-18.md`, `analysts/SCORECARD.md`, `analysts/SAMPLE_CALL_LEDGER.csv`, `qriptal_2026-10-10/SCORECARD.md`, `qriptal_2026-10-10/CALL_LEDGER.csv`, and `imbalance_qriptal_2026-10-16/README.md` match the underlying raw data, call ledgers, and scorecards with zero mismatches. Deliverable `MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/callers.md` has been written and verified.

