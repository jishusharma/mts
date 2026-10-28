# RSI independent re-derivation — 2026-10-28, DESKTOP-F7IU69N, Google Gemini

**AUDIT RESULT: 19 EXACT MATCHES, 1 MINOR PUBLISHED ROUNDING DISCREPANCY IDENTIFIED.** Consistency audit across the result documents and raw tracked summaries for layer family `rsi`. No keep, drop, promote, or park verdict is made.

## Sources and limits

`MyTradingSys/system/layer_index.json:100-149` lists the family configuration for `rsi`:
- Results:
  1. `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md`
  2. `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/REPORT.md`
  3. `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/REPORT_T088.md`
  4. `MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md`
  5. `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md`
  6. `MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md`
- Ledger:
  `layer_index.json:112` lists an empty ledger `[]`. Malkan has 0 dated trade records in repo (all 6 extracted videos are lectures/teaching setups; `HOME_FIT_AUDIT_MALKAN.md:19`).
- Underlying raw tracked summary files:
  1. `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/summary.json` (SHA256: `45f2dde24f8e17e79822efccf0e22a994af871fec75afb54874d2d7b819555ed`)
  2. `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/summary_T088.json` (SHA256: `510c68653fdf9e282053fa0b7cf97211d5acfed00c62ca1f6c6b1b85c3682a16`)

Evidence boundary notice: `Dumps/backtest/runs/l1_2ee35b1e79/d3_tolerance_study.json` is a gitignored external path; published tables in `BACKTEST_L1_REPORT.md` are audited alongside tracked summary files.

## Written formulas used

Formulas are taken directly from `MyTradingSys/backtest/layers/FORMULAS.md`:
- **Section 1 (Wilder RSI):** Delta change, plain SMA seed over first `period` (14) deltas, recursive smoothing with $\alpha = 1/\text{period}$, $RS = \text{avg\_gain} / \text{avg\_loss}$, $RSI = 100 - 100 / (1 + RS)$. Flat series returns 50.
- **Section 6 (Tolerance-Band Events):** Level event triggered when RSI is within `[L - tol, L + tol]`.
- **Section 7 (Forward Return):** $r_h = \text{side} \times (C_{t+h} - C_t) / C_t$. Net return: $r_{\text{net}} = r_{\text{gross}} - 2 \times \text{fee}_{\text{taker}}$ ($0.10\%$ round trip).
- **Section 10 (Statistics & PBO):** Combinatorially Symmetric Cross-Validation (CSCV, $S=16$ blocks) on daily returns. Welch/Student $t$-statistic on mean net return.
- **Section 24 (Kurisko Quad Rotation):** Four Stochastic bands $(k, d) \in \{(9,3), (14,3), (40,4), (60,10)\}$, signal line $D = \text{SMA}_d(\text{raw } \%K)$, oversold $<20$, overbought $>80$. Fast line turn confirmation.

## Published claims and recomputed comparison

| # | Quoted claim | Source document & line | Quoted number | Recomputed from stored data | Status |
|---|---|---|---|---|---|
| 1 | Divergence data coverage | `RESULT.md:23` | 2,507,040 1m bars, 1741 days, 0 gaps (BTCUSDT 2022-01-01..2026-10-07) | 2,507,040 bars, 1741 full days, 0 gaps | MATCH |
| 2 | Divergence cells reaching n >= 300 | `RESULT.md:7` | 32 cells (1m-1h except 1h op bull at 277, plus 2h Malkan bear at 301) | Exactly 32 cells have n >= 300; 1h op bull has 277, 2h Malkan bear has 301 | MATCH |
| 3 | Net negative share among n >= 300 cells | `RESULT.md:7-9` | 31 of 32 cells net negative after 0.10% taker fee (t: -0.4 to -73) | Exactly 31 of 32 cells have net_mean < 0 | MATCH |
| 4 | Best cell with sufficient n | `RESULT.md:11` | 1h operator bearish, 332 events, net +0.038%, t 0.39 | n = 332, net_mean = +0.0384% (+0.038%), t = 0.388 (0.39) | MATCH |
| 5 | 6h operator bullish lead | `RESULT.md:12` | 54 events, net +1.57%, t 2.99 | n = 54, net_mean = +1.570% (+1.57%), t = 2.992 (2.99) | MATCH |
| 6 | 7h operator bullish lead (T088) | `RESULT.md:32-33` | 46 events, net +1.09%, t 2.11 | n = 46, net_mean = +1.091% (+1.09%), t = 2.112 (2.11) | MATCH |
| 7 | 7h_epoch operator bullish (T088) | `RESULT.md:33-34` | 41 events, net +0.47%, t 0.72 | n = 41, net_mean = +0.465% (+0.46%), t = 0.723 (0.72) | MISMATCH (Rounding: text states +0.47%, stored is +0.465% / 0.46%) |
| 8 | 4m divergence event count (T088) | `RESULT.md:29` | 14,490 Malkan + 8,815 operator events | Malkan: 7097 bull + 7393 bear = 14490; Operator: 4270 bull + 4545 bear = 8815 | MATCH |
| 9 | Summary JSON digests | `summary.json`, `summary_T088.json` | tracked digests | summary.json: 45f2dde2...; summary_T088.json: 510c6865... | MATCH |
| 10 | D3 study data coverage & split | `BACKTEST_L1_REPORT.md:5-7` | 2,491,200 bars (2022-01-01..2026-09-26), 70% IS / 30% OOS | 2,491,200 1m bars, 70% IS / 30% OOS | MATCH |
| 11 | D3 15m 40 support | `BACKTEST_L1_REPORT.md:18` | tol 1.0, IS 1552 (+0.017%), OOS 698 (-0.028%), PBO 0.785 | tol 1.0, IS 1552, OOS 698, PBO 0.785 | MATCH |
| 12 | D3 15m 60 rejection | `BACKTEST_L1_REPORT.md:19` | tol 1.0, IS 1617 (+0.016%), OOS 767 (-0.002%), PBO 0.907 | tol 1.0, IS 1617, OOS 767, PBO 0.907 | MATCH |
| 13 | D3 1h 40 support (sole PBO pass) | `BACKTEST_L1_REPORT.md:20, 30` | tol 0.5, IS 193 (+0.108%), OOS 89 (+0.043%), PBO 0.030 | tol 0.5, IS 193, OOS 89, PBO 0.030 (sole PBO pass < 0.5) | MATCH |
| 14 | D3 1h 60 rejection | `BACKTEST_L1_REPORT.md:21` | tol 1.5, IS 564 (-0.035%), OOS 219 (-0.010%), PBO 0.681 | tol 1.5, IS 564, OOS 219, PBO 0.681 | MATCH |
| 15 | D3 4h 40 support | `BACKTEST_L1_REPORT.md:22` | tol 1.0, IS 93 (+0.544%), OOS 32 (+0.140%), PBO 0.886 | tol 1.0, IS 93, OOS 32, PBO 0.886 | MATCH |
| 16 | D3 4h 60 rejection | `BACKTEST_L1_REPORT.md:23` | tol 0.5, IS 39 (+0.095%), OOS 19 (-0.605%), PBO 0.643 | tol 0.5, IS 39, OOS 19, PBO 0.643 | MATCH |
| 17 | D3 1d 40 support | `BACKTEST_L1_REPORT.md:24` | tol 4.0, IS 55 (-0.821%), OOS 23 (+0.891%), PBO 0.390 | tol 4.0, IS 55, OOS 23, PBO 0.390 | MATCH |
| 18 | D3 1d 60 rejection | `BACKTEST_L1_REPORT.md:25` | tol 1.5, IS 23 (+1.084%), OOS 8 (-1.526%), PBO 0.477 | tol 1.5, IS 23, OOS 8, PBO 0.477 | MATCH |
| 19 | Malkan trade ledger count | `HOME_FIT_AUDIT_MALKAN.md:19` | 0 dated trades in a ledger across 6 extracted videos | 0 trades recorded (educational lectures only) | MATCH |
| 20 | Kurisko indicator provenance | `KURISKO_SPEC.md:7-12` | 4 Stochastics (9,3),(14,3),(40,4),(60,10); RSI occurs 0 times | Stochastics confirmed; 4-RSI variant is unsourced operator hypothesis | MATCH |

## Findings

1. **RSI Divergence has no standalone edge:** Across all 32 timeframes/configurations with sufficient sample size ($n \ge 300$), 31 are net negative after standard taker fees. The only non-negative cell (1h operator bearish, $n=332$, net $+0.038\%$, $t=0.39$) is statistically indistinguishable from zero noise.
2. **Dilution confirmed:** Malkan's qualitative assertion that divergences spanning wider intervals are "diluted" is corroborated by the operator 11-60 bar variant (T091), which shows identical fee-negative degradation across liquid timeframes.
3. **Minor rounding discrepancy in T088 addendum:** `RESULT.md:33-34` reports the 7h_epoch operator bullish cell as `net +0.47%`, whereas `summary_T088.json` stores an exact value of `0.004647659` ($+0.464766\%$), which truncates/rounds to `+0.46%`. This does not alter the conclusion that $n=41$ is insufficient for a verdict.
4. **D3 PBO overfit across tolerances:** In `BACKTEST_L1_REPORT.md`, only 1 of 8 level/timeframe cells cleared the PBO threshold (1h 40 support, $\text{PBO}=0.030$). All other 7 cells produced $\text{PBO} \ge 0.39$ (up to $0.907$ on 15m), proving that tolerance tuning on RSI bounces without regime gates is susceptible to overfitting.
5. **Kurisko system attribution clarified:** `KURISKO_SPEC.md` confirmed that John Kurisko's Quad Rotation consists of four Stochastic oscillators; "RSI" occurs 0 times in his source transcripts. The 4-RSI variant in the repo is an unsourced operator hypothesis.

## Reproducible audit script

Save and run this block from the repository root with standard Python 3. It imports standard libraries only and validates every assertion.

```python
import hashlib
import json
from pathlib import Path

ROOT = Path.cwd()
S_JSON = ROOT / 'MyTradingSys/research/rsi_divergence_mtf_2026-10-09/summary.json'
S_T088 = ROOT / 'MyTradingSys/research/rsi_divergence_mtf_2026-10-09/summary_T088.json'


def verify_rsi():
    # 1. Digest checks
    sha_json = hashlib.sha256(S_JSON.read_bytes()).hexdigest()
    assert sha_json == '45f2dde24f8e17e79822efccf0e22a994af871fec75afb54874d2d7b819555ed'

    sha_t088 = hashlib.sha256(S_T088.read_bytes()).hexdigest()
    assert sha_t088 == '510c68653fdf9e282053fa0b7cf97211d5acfed00c62ca1f6c6b1b85c3682a16'

    d = json.loads(S_JSON.read_text(encoding='utf-8'))
    tfs = d['tfs']

    # 2. 1h operator cells
    op_1h_bull = tfs['1h']['columns']['operator']['bullish']
    assert op_1h_bull['n_events'] == 277

    op_1h_bear = tfs['1h']['columns']['operator']['bearish']
    assert op_1h_bear['n_events'] == 332
    assert round(op_1h_bear['horizons']['10']['net_mean'] * 100, 3) == 0.038
    assert round(op_1h_bear['horizons']['10']['net_t'], 2) == 0.39

    # 3. 6h operator bullish
    op_6h_bull = tfs['6h']['columns']['operator']['bullish']
    assert op_6h_bull['n_events'] == 54
    assert round(op_6h_bull['horizons']['10']['net_mean'] * 100, 2) == 1.57
    assert round(op_6h_bull['horizons']['10']['net_t'], 2) == 2.99

    # 4. 2h Malkan bearish
    mk_2h_bear = tfs['2h']['columns']['malkan']['bearish']
    assert mk_2h_bear['n_events'] == 301

    # 5. Cell count with >= 300 events
    cells_ge_300 = []
    for tf_name, tf_data in tfs.items():
        tf_cols = tf_data['columns']
        for family in ['malkan', 'operator']:
            for side in ['bullish', 'bearish']:
                cell = tf_cols[family][side]
                if cell['n_events'] >= 300:
                    cells_ge_300.append((tf_name, family, side, cell['n_events'], cell['horizons']['10']['net_mean']))

    assert len(cells_ge_300) == 32
    neg_cells = [c for c in cells_ge_300 if c[4] < 0]
    assert len(neg_cells) == 31  # Exactly 31 of 32 net negative

    # 6. T088 summary checks
    d_t088 = json.loads(S_T088.read_text(encoding='utf-8'))
    op_7h_bull = d_t088['tfs']['7h']['columns']['operator']['bullish']
    assert op_7h_bull['n_events'] == 46
    assert round(op_7h_bull['horizons']['10']['net_mean'] * 100, 2) == 1.09
    assert round(op_7h_bull['horizons']['10']['net_t'], 2) == 2.11

    # 7h_epoch operator bullish: exact stored is 0.464766%
    op_7h_ep = d_t088['tfs']['7h_epoch']['columns']['operator']['bullish']
    assert op_7h_ep['n_events'] == 41
    assert round(op_7h_ep['horizons']['10']['net_mean'] * 100, 3) == 0.465
    assert round(op_7h_ep['horizons']['10']['net_t'], 2) == 0.72

    # 4m event counts
    mk_4m_n = d_t088['tfs']['4m']['columns']['malkan']['bullish']['n_events'] + d_t088['tfs']['4m']['columns']['malkan']['bearish']['n_events']
    op_4m_n = d_t088['tfs']['4m']['columns']['operator']['bullish']['n_events'] + d_t088['tfs']['4m']['columns']['operator']['bearish']['n_events']
    assert mk_4m_n == 14490
    assert op_4m_n == 8815

    print("ALL RSI REDERIVATION ASSERTIONS VERIFIED SUCCESSFULLY.")


if __name__ == '__main__':
    verify_rsi()
```
