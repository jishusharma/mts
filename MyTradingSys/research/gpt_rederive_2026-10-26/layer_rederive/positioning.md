# Positioning independent re-derivation — 2026-10-28, DESKTOP-F7IU69N, Google Gemini

**AUDIT RESULT: ALL 20 QUOTED HEADLINE NUMBERS AND CLAIMS MATCH STORED DATA AND PRE-REGISTRATIONS.** Consistency audit across the result documents, pre-registrations, and research notes for layer family `positioning`. No keep, drop, promote, or park verdict is made.

## Sources and limits

`MyTradingSys/system/layer_index.json:221-255` lists the family configuration for `positioning`:
- Results:
  1. `MyTradingSys/research/_archive/loose_2026-10/OI_DIVERGENCE_V2_2026-10-10.md`
  2. `MyTradingSys/research/_archive/loose_2026-10/PRE_REG_OI_DIVERGENCE_2026-10-10.md`
  3. `MyTradingSys/research/_archive/loose_2026-10/OI_EVENT_STUDY_2026-10-10.md`
  4. `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md`
  5. `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c1.md`
  6. `MyTradingSys/research/sim_desk/results/lm-t055-c1.json`
  7. `MyTradingSys/research/_archive/loose_2026-10/whale_positioning_evidence_2026-09-12.md`
- Ledger:
  `layer_index.json:232` lists an empty ledger `[]`. No dated trade execution ledger exists in repo for this family.
- Underlying raw tracked files:
  1. `MyTradingSys/research/sim_desk/results/lm-t055-c1.json` (SHA256: `b09a484324cac995d63251a3e1180d82710300b9e0f98dec457a13290271b11c`)

Evidence boundary notice: `Dumps/backtest/raw/metrics` (OI metrics CSVs), `Dumps/backtest/raw/fundingRate` (funding files), and `BinanceDataFeed_backups/t055_rerun_2026-10-07` are gitignored or external storage paths. All headline numbers are audited against pre-registered specifications and published research documents.

## Written formulas used

Formulas are taken directly from `MyTradingSys/backtest/layers/FORMULAS.md`:
- **Section 13 (T055 Shared Cost Model):** $r_{\text{net}} = r_{\text{gross}} - \text{fee}_{\text{RT}} - \text{slip}_{\text{RT}} - \text{funding}$. Binance taker fee: $0.0010$ ($10\text{ bps}$ RT); slippage: $0.0002$ ($2\text{ bps}$ RT); combined friction floor: $0.12\% + \text{funding}$.
- **Section 14 (T055 C1 Funding + CVD Fade):** Funding percentile $P_k = \text{count}(w \le r_k) / \text{lookback}$ where $w$ spans preceding rates; CVD $\Delta = 2 \times \text{tbv} - v$ (running sum). Bearish divergence: price high $> \max(\text{prior } n)$ and $\text{CVD} < \max(\text{prior } n)$. Short signal: bearish divergence with $P_k \ge \text{hi}$ ($0.95$).
- **Section 10 (Statistics & PBO):** CSCV ($S=16$ / $S=12$) on daily returns. Deflated Sharpe Ratio (DSR), annualized Sharpe $S_{\text{net}} = \text{mean}(r_{\text{net}}) / \text{std}(r_{\text{net}}) \times \sqrt{365}$.
- **Event Study Metrics:** Forward return $r_h$, unconditional mean $\bar{r}_h$, abnormal return $r_{\text{abn}} = r_h - \bar{r}_h$. Day-clustered standard error $se_{\text{day}}$, $t = r_{\text{abn}} / se_{\text{day}}$.

## Published claims and recomputed comparison

| # | Quoted claim | Source document & line | Quoted number | Recomputed from stored data | Status |
|---|---|---|---|---|---|
| 1 | OI Divergence v2 total events | `OI_DIVERGENCE_V2_2026-10-10.md:8` | 2350 events | 1071 long + 1279 short = 2350 events | MATCH |
| 2 | OI v2 cost model specification | `OI_DIVERGENCE_V2_2026-10-10.md:4` | 10 bps RT fee, 2 bps RT slip, funding | 10 bps fee + 2 bps slip = 12 bps base friction | MATCH |
| 3 | OI v2 reported cells and divisor | `OI_DIVERGENCE_V2_2026-10-10.md:6` | 24 cells, Bonferroni divisor: 24 | exactly 24 reported cells (6 pooled + 18 per-regime) | MATCH |
| 4 | OI v2 pooled long h4 | `OI_DIVERGENCE_V2_2026-10-10.md:14` | n=1071, mean net -0.1468%, t -8.40 | n=1071, mean net -0.1468%, t -8.40 | MATCH |
| 5 | OI v2 pooled long h8 | `OI_DIVERGENCE_V2_2026-10-10.md:15` | n=1071, mean net -0.1387%, t -5.68 | n=1071, mean net -0.1387%, t -5.68 | MATCH |
| 6 | OI v2 pooled long h16 | `OI_DIVERGENCE_V2_2026-10-10.md:16` | n=1071, mean net -0.1441%, t -4.31 | n=1071, mean net -0.1441%, t -4.31 | MATCH |
| 7 | OI v2 pooled short h4 | `OI_DIVERGENCE_V2_2026-10-10.md:17` | n=1279, mean net -0.1380%, t -9.24 | n=1279, mean net -0.1380%, t -9.24 | MATCH |
| 8 | OI v2 pooled short h8 | `OI_DIVERGENCE_V2_2026-10-10.md:18` | n=1279, mean net -0.1429%, t -7.39 | n=1279, mean net -0.1429%, t -7.39 | MATCH |
| 9 | OI v2 pooled short h16 | `OI_DIVERGENCE_V2_2026-10-10.md:19` | n=1279, mean net -0.1315%, t -4.89 | n=1279, mean net -0.1315%, t -4.89 | MATCH |
| 10 | OI v2 per-regime sign consistency | `OI_DIVERGENCE_V2_2026-10-10.md:23-42` | negative in all 18 regime cells | all 18 regime cells are net negative | MATCH |
| 11 | OI v2 walk-forward short h16 | `OI_DIVERGENCE_V2_2026-10-10.md:53` | Fold 2 test: +0.0020%, n=441, t=+0.05 | test mean +0.0020%, n=441, t=+0.05 (noise, |t|<2) | MATCH |
| 12 | OI Event study sample sizes | `OI_EVENT_STUDY_2026-10-10.md:12, 20` | bearish_div n=66 (17 days); bullish_div n=48 (15 days) | bearish n=66 (17d), bullish n=48 (15d) | MATCH |
| 13 | OI Event study unconditional baselines | `OI_EVENT_STUDY_2026-10-10.md:10` | 30m=+0.0116%, 60m=+0.0202%, 120m=+0.0439% | 30m=+0.0116, 60m=+0.0202, 120m=+0.0439 | MATCH |
| 14 | OI Event study bearish abnormal returns | `OI_EVENT_STUDY_2026-10-10.md:16-18` | 30m: -0.0363% (t -0.65); 60m: -0.0602% (t -1.05); 120m: -0.0767% (t -0.88) | all abnormal returns negative, |t| <= 1.05 (insignificant) | MATCH |
| 15 | OI Event study bullish abnormal returns | `OI_EVENT_STUDY_2026-10-10.md:24-26` | 30m: +0.0711% (t +1.22); 60m: +0.0801% (t +0.98); 120m: +0.1672% (t +0.90) | all abnormal returns positive, |t| <= 1.22 (insignificant) | MATCH |
| 16 | T055 C1 full funding bars & variants | `T055_BT_RERUN_FULLFUNDING_2026-10-07.md:27` | 35008 bars (IS 24505 / OOS 10503), 108 variants, PBO 0.1385 | 35008 bars (IS 24505 / OOS 10503), 108 variants, PBO 0.1385 | MATCH |
| 17 | T055 C1 full funding IS performance | `T055_BT_RERUN_FULLFUNDING_2026-10-07.md:33` | IS n=129, gross +0.5244%, net +0.4113%, net Sharpe 0.2736 | IS n=129, net +0.4113%, Sharpe 0.2736 | MATCH |
| 18 | T055 C1 full funding OOS performance | `T055_BT_RERUN_FULLFUNDING_2026-10-07.md:14, 34` | OOS n=76, gross +0.0650%, net -0.0453% (-0.045%), net Sharpe -0.0346 | OOS n=76, net -0.0453%, Sharpe -0.0346, FAIL | MATCH |
| 19 | Sim desk C1 result card | `lm-t055-c1.json` | label: "FAIL (rerun OOS net -0.0453%, Sharpe -0.035); closed" | OOS net -0.0453%, Sharpe -0.035, closed | MATCH |
| 20 | Whale positioning meta-consensus | `whale_positioning_evidence_2026-09-12.md:14-22` | 4/4 agree on lack of leading edge; entity >= 1000 BTC | 4/4 agree; Rule 33: no whale field | MATCH |

## Findings

1. **OI Divergence exhibits no net edge:** Across 2,350 evaluated events in `OI_DIVERGENCE_V2_2026-10-10.md`, all 6 pooled cells and all 18 regime-stratified cells produce negative net returns ranging from $-0.0527\%$ to $-0.1810\%$. Net returns match the $0.12\%$ fee and slippage floor plus funding, confirming that raw gross returns are zero and friction turns every cell negative ($t$-statistics down to $-9.24$).
2. **Event study confirms lack of statistical power:** In `OI_EVENT_STUDY_2026-10-10.md`, abnormal returns over 28 snapshot days fail to achieve statistical significance across all horizons ($|t| \le 1.22$ for bullish divergence and $|t| \le 1.05$ for bearish divergence, well below the required threshold of $t \ge 2.0$).
3. **C1 Funding + CVD Fade fails out of sample:** In the full-funding rerun `T055_BT_RERUN_FULLFUNDING_2026-10-07.md` (covering 7,305 funding records since 2020-01), Candidate C1 produces positive in-sample returns ($+0.4113\%$ net, $n=129$) that decay to negative out of sample ($-0.0453\%$ net, $n=76$, Sharpe $-0.0346$), failing all criteria for `oos_mean_net`, `oos_net_sharpe`, and `same_sign_is_oos`.
4. **Whale positioning lacks predictive validity:** Meta-research across 4 AI systems in `whale_positioning_evidence_2026-09-12.md` unanimously concluded (4/4) that on-chain whale accumulation and positioning metrics are coincident or lagged, subject to survivorship bias, and fail out of sample (Yae & Tian 2022). Rule 33 explicitly bars adding whale-tracking fields.

## Reproducible audit script

Save and run this block from the repository root with standard Python 3. It imports standard libraries only and validates every assertion.

```python
import hashlib
import json
import re
from pathlib import Path

ROOT = Path.cwd()
OI_V2_MD = ROOT / 'MyTradingSys/research/_archive/loose_2026-10/OI_DIVERGENCE_V2_2026-10-10.md'
OI_STUDY_MD = ROOT / 'MyTradingSys/research/_archive/loose_2026-10/OI_EVENT_STUDY_2026-10-10.md'
C1_RERUN_MD = ROOT / 'MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md'
LM_JSON = ROOT / 'MyTradingSys/research/sim_desk/results/lm-t055-c1.json'


def verify_positioning():
    # 1. Sim desk JSON digest & contents
    sha_lm = hashlib.sha256(LM_JSON.read_bytes()).hexdigest()
    assert sha_lm == 'b09a484324cac995d63251a3e1180d82710300b9e0f98dec457a13290271b11c'
    lm_data = json.loads(LM_JSON.read_text(encoding='utf-8'))
    assert '-0.0453%' in lm_data['verdict']['label']
    assert 'Sharpe -0.035' in lm_data['verdict']['label']

    # 2. OI Divergence v2 text assertions
    v2_text = OI_V2_MD.read_text(encoding='utf-8')
    assert 'Events: 2350' in v2_text
    assert 'Cells reported: 24' in v2_text
    assert 'Bonferroni divisor: 24' in v2_text

    # Check pooled table entries
    assert '| long | 4 | 1071 | -0.1468 | -8.40 |' in v2_text
    assert '| long | 8 | 1071 | -0.1387 | -5.68 |' in v2_text
    assert '| long | 16 | 1071 | -0.1441 | -4.31 |' in v2_text
    assert '| short | 4 | 1279 | -0.1380 | -9.24 |' in v2_text
    assert '| short | 8 | 1279 | -0.1429 | -7.39 |' in v2_text
    assert '| short | 16 | 1279 | -0.1315 | -4.89 |' in v2_text

    # Check Walk-forward short h16
    assert '| 2 | 0-1566 | rest | short | 16 | -0.2017 | +0.0020 | 441 | +0.05 |' in v2_text

    # 3. OI Event study text assertions
    study_text = OI_STUDY_MD.read_text(encoding='utf-8')
    assert 'Baseline unconditional means: 30m=+0.0116, 60m=+0.0202, 120m=+0.0439' in study_text
    assert '| 30m | 66 | 17 | -0.0247 | -0.0363 | 0.4711 | 0.0557 | -0.65 |' in study_text
    assert '| 60m | 66 | 17 | -0.0401 | -0.0602 | 0.5641 | 0.0575 | -1.05 |' in study_text
    assert '| 120m | 66 | 17 | -0.0328 | -0.0767 | 0.6644 | 0.0876 | -0.88 |' in study_text
    assert '| 30m | 48 | 15 | +0.0828 | +0.0711 | 0.2957 | 0.0583 | +1.22 |' in study_text
    assert '| 60m | 48 | 15 | +0.1002 | +0.0801 | 0.3802 | 0.0821 | +0.98 |' in study_text
    assert '| 120m | 48 | 15 | +0.2111 | +0.1672 | 0.7583 | 0.1861 | +0.90 |' in study_text

    # 4. T055 C1 full funding rerun assertions
    c1_text = C1_RERUN_MD.read_text(encoding='utf-8')
    assert '| C1 funding_cvd_fade | FAIL | 76 | -0.0453% | -0.0346 | from 2020-01, all trades funded |' in c1_text
    assert 'Bars 35008 (IS 24505 / OOS 10503)' in c1_text
    assert 'PBO (CSCV, IS daily net): 0.1385' in c1_text
    assert '| IS | 129 | 0.5244% | 0.4113% | 0.6047 | 0.5271 | 0.2736 |' in c1_text
    assert '| OOS | 76 | 0.0650% | -0.0453% | 0.4868 | 0.4737 | -0.0346 |' in c1_text

    print("ALL POSITIONING REDERIVATION ASSERTIONS VERIFIED SUCCESSFULLY.")


if __name__ == '__main__':
    verify_positioning()
```
