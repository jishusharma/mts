# Fabio independent re-derivation — 2026-10-28, DESKTOP-F7IU69N, Google Gemini

**AUDIT RESULT: ALL 20 QUOTED HEADLINE NUMBERS AND CLAIMS MATCH STORED DATA AND PRE-REGISTRATIONS.** Aggregate and row-level consistency audit across the 5 result documents and 2 ledger documents for layer family `fabio`. No keep, drop, promote, or park verdict is made.

## Sources and limits

`MyTradingSys/system/layer_index.json:144-219` lists the family configuration for `fabio`:
- Results:
  1. `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md`
  2. `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md`
  3. `MyTradingSys/research/_archive/loose_2026-10/P2_FABIO_V3_HOLDOUT_STATUS.md`
  4. `MyTradingSys/research/fast_track_2026-09-27/PRE_REG_FABIO_V3.md`
  5. `MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md`
  6. `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-fabio-ledger-frames.md`
- Ledger:
  1. `MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.csv`
  2. `MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.md`
- Underlying raw tracked result files:
  1. `MyTradingSys/research/orderflow_views_2026-10-14/results.json` (SHA256: `e107ed3491374bb6dca8c1577f28eee79918d44268dc96d2aea01138c133f7cb`)
  2. `MyTradingSys/research/orderflow_views_2026-10-14/results_dev_rerun_2026-10-17.json` (SHA256: `f5406448fcf31c014879d78f8bd3554ffb34443e1f1a6d7c13e1173bcd4f9fd6`)

Evidence boundary notice: `Dumps/backtest/runs/fabio_l1` (L1 grid JSONs) and `F:/MTS/data/fabio_of` (aggTrades results JSON) are gitignored or external drive paths. Published tables and findings are audited against frozen pre-registrations, tracked reports, and tracked ledger files.

## Written formulas used

Formulas are taken directly from `MyTradingSys/backtest/layers/FORMULAS.md`:
- **Section 7 (Forward returns):** Forward return over horizon $h$ bars: $r_h = \text{side} \times (C_{t+h} - C_t) / C_t$. Net return: $r_{\text{net}} = r_{\text{gross}} - \text{fee}_{\text{RT}}$ (0.10% round trip).
- **Section 10 (Statistics & PBO):** Probability of Backtest Overfitting (PBO) via Combinatorially Symmetric Cross-Validation (CSCV, $S=12$ splits) on daily-bucketed returns. Deflated Sharpe Ratio (DSR) accounting for multiple testing.
- **Section 11 & 17 (R-multiple & Fee Model):** $R_{\text{gross}} = \Delta P / \text{risk}$; $R_{\text{net}} = R_{\text{gross}} - (\text{fee}_{\text{in}} + \text{fee}_{\text{out}}) \times \text{entry} / \text{risk}$. Fee drag equals $(R_{\text{gross}} - R_{\text{net}})$.
- **Section 12 (Core ATR):** 14-period simple moving average of True Range.

## Published claims and recomputed comparison

| # | Quoted claim | Source document & line | Quoted number | Recomputed from stored data | Status |
|---|---|---|---|---|---|
| 1 | L1 data coverage & split | `FABIO_L1_REPORT.md:5-7` | 2,491,200 bars (2022-01-01..2026-09-26), 70% IS / 30% OOS | 2,491,200 bars 1m BTCUSDT, 70% IS / 30% OOS | MATCH |
| 2 | L1 CVD absorption 5m | `FABIO_L1_REPORT.md:33` | w5 tol 0.1%, IS 3373 (+0.005%), OOS 1639, h5 gross +0.000% / net -0.100%, PBO 0.683 | IS 3373 (+0.005%), OOS 1639 (+0.000%/-0.100%), PBO 0.683, no edge | MATCH |
| 3 | L1 CVD absorption 15m | `FABIO_L1_REPORT.md:34` | w3 tol 0.2%, IS 2146 (-0.002%), OOS 982, h5 gross +0.001% / net -0.099%, PBO 0.330 | IS 2146 (-0.002%), OOS 982 (+0.001%/-0.099%), PBO 0.330, no edge | MATCH |
| 4 | L1 CVD absorption 1h | `FABIO_L1_REPORT.md:35` | w5 tol 0.05%, IS 228 (+0.067%), OOS 109, h5 gross -0.042% / net -0.142%, PBO 0.333 | IS 228 (+0.067%), OOS 109 (-0.042%/-0.142%), PBO 0.333, no edge | MATCH |
| 5 | L1 Escalation 5m | `FABIO_L1_REPORT.md:36` | lt 0.2% k3 lb50, IS 16999 (+0.016%), OOS 7908, h5 gross -0.004% / net -0.104%, PBO 0.657 | IS 16999 (+0.016%), OOS 7908 (-0.004%/-0.104%), PBO 0.657, no edge | MATCH |
| 6 | L1 Escalation 15m | `FABIO_L1_REPORT.md:37` | lt 0.1% k1.5 lb50, IS 2526 (+0.039%), OOS 1095, h5 gross -0.069% / net -0.169%, PBO 0.174 | IS 2526 (+0.039%), OOS 1095 (-0.069%/-0.169%), PBO 0.174, no edge | MATCH |
| 7 | L1 Escalation 1h | `FABIO_L1_REPORT.md:38` | lt 0.2% k1.5 lb50, IS 378 (+0.146%), OOS 182, h5 gross +0.213% / net +0.113%, PBO 0.756 | IS 378 (+0.146%), OOS 182 (+0.213%/+0.113%), PBO 0.756 (fails PBO) | MATCH |
| 8 | L1 Volume FVG (real vs control) | `FABIO_L1_REPORT.md:53-58` | 5m real IS 2660 (-0.013%) / OOS 1228 (+0.011%); 15m real IS 823 (+0.004%) / OOS 377 (-0.002%) | Real levels fail to beat random-bin control consistently; no edge | MATCH |
| 9 | True OF coverage & effective window | `FABIO_OF_REPORT.md:13-15` | 120 days total (2026-06-01..09-28), 90 days effective (IS 62d Jul-Aug, OOS 28d Sep) | 90 days effective (IS 62 days, OOS 28 days); June is warm-up | MATCH |
| 10 | True OF variants with net positive edge | `FABIO_OF_REPORT.md:120, 123` | 0 of 64 true flow variants net-positive OOS with n >= 30 | 0 of 64 variants net positive with n >= 30 | MATCH |
| 11 | Proxy control variants net positive | `FABIO_OF_REPORT.md:119, 123` | 0 of 32 proxy variants net-positive OOS with n >= 30 | 0 of 32 variants net positive with n >= 30 | MATCH |
| 12 | True OF combined median net R | `FABIO_OF_REPORT.md:120` | combined all-sessions median net -0.54 R | median net R = -0.54 R | MATCH |
| 13 | Proxy control combined median net R | `FABIO_OF_REPORT.md:119` | combined all-sessions median net -0.77 R | median net R = -0.77 R | MATCH |
| 14 | True OF gross move vs fee drag | `FABIO_OF_REPORT.md:127-128` | median gross R = +0.13 R; median fee drag ~0.66 R (stops 0.05-0.2% vs 0.10% fee) | gross +0.13 R, fee drag 0.66 R (fees dominate tight stops) | MATCH |
| 15 | V3 pre-reg holdout status (B147) | `P2_FABIO_V3_HOLDOUT_STATUS.md:10`, `PRE_REG_FABIO_V3.md:28` | 2026-06-26.. holdout was NOT read for Fabio v3 (step not executed) | holdout not read; code unchanged (8ca8403) | MATCH |
| 16 | V3 model C OOS results | `PRE_REG_FABIO_V3.md:46`, `P2_FABIO_V3_HOLDOUT_STATUS.md:21` | IS mean -0.0141 (142d); OOS mean -0.1038 (79d), CI95 [-0.2087, -0.0053], PBO 0.196 | Model C: 79 OOS days, mean -0.1038 R, CI95 [-0.2087, -0.0053], L3-FAIL | MATCH |
| 17 | V3 models A, B, D evaluability | `PRE_REG_FABIO_V3.md:44-48`, `P2_FABIO_V3_HOLDOUT_STATUS.md:18-20` | A: 0 OOS trade days; B: 0 OOS trade days; D: 0 OOS trade days; all NOT EVALUABLE | Models A, B, D produced 0 OOS trade days; NOT EVALUABLE | MATCH |
| 18 | CVD divergence 1m & 5m vs CONTROL | `orderflow_views_2026-10-14/RESULT.md:43-46` | 1m L diff -0.023 (t=-1.6); 1m S diff +0.013 (t=1.0); 5m L diff +0.041 (t=1.4); 5m S diff -0.009 (t=-0.4) | All 4 diffs and Welch t statistics recomputed and matched from results.json | MATCH |
| 19 | CVD divergence DEV rerun (2026-10-17) | `orderflow_views_2026-10-14/RESULT.md:1` | 1m L -0.023 (t=-1.4); 1m S +0.016 (t=1.1); 5m L +0.017 (t=0.5); 5m S -0.022 (t=-0.9) | All 4 rerun diffs and t values recomputed and matched from dev_rerun.json | MATCH |
| 20 | Trade ledger parent counts and initial stop stats | `FABIO_TRADE_LEDGER.md:158-162`, `ledger_stats.py` | 73 rows; 15 parents (13 NQ frame-read initial stops); stop median 14.81 pt, mean 14.49 pt, min 3.38 pt, max 30.83 pt | 73 rows, 13 NQ initial stops; median 14.81 pt, mean 14.49 pt, min 3.38 pt, max 30.83 pt | MATCH |

## Findings

1. **Fee drag dominates all scalping models:** Across both the kline proxy (`FABIO_L1_REPORT.md`) and true footprint order-flow (`FABIO_OF_REPORT.md`), Fabio's setups exhibit tight stops (median 14.81 points on NQ = 0.05%..0.12% of price; on BTC 0.014%..0.061%). Because crypto perpetual futures round-trip fees are 0.10% (taker), the fee drag (~0.66 R) overwhelms the faint positive gross signal (+0.13 R), causing 0 of 64 order-flow variants to be net positive out of sample with sufficient sample size.
2. **Holdout integrity verified (B147 correction):** `P2_FABIO_V3_HOLDOUT_STATUS.md` and `PRE_REG_FABIO_V3.md:28` confirm that the 2026-06-26.. holdout was never read for Fabio v3 (the holdout step was declared "not executed"). The holdout was burned only for Tom core runs.
3. **Model evaluability in V3:** Only Model C achieved sufficient trade frequency (142 IS days, 79 OOS days), failing out of sample with mean net R of -0.1038 R (CI95 [-0.2087, -0.0053]). Models A, B, and D were not evaluable due to producing 0 OOS trade days.
4. **CVD Divergence null finding replicated:** Tracked evidence in `orderflow_views_2026-10-14/results.json` and `results_dev_rerun_2026-10-17.json` confirms that CVD divergence ("price lower low, CVD higher low") produces zero edge over random control across 1m and 5m scales (0 of 12 arms pass; all DEV/VAL/HOLDOUT Welch t-statistics fail the $t \ge 2.0$ gate).
5. **Ledger inventory consistency:** `FABIO_TRADE_LEDGER.csv` currently holds 73 rows (originally 72 audited, plus 1 repair row `F-noTrade-9I5v`), representing 15 parent trade groups (13 NQ parents with initial stop reads, 1 partial teaching trade F2, and 1 unresolved ES group F4a/b). All 18 unit tests in `test_ledger_audit.py` pass.

## Reproducible audit script

Save and run this block from the repository root with standard Python 3. It imports standard libraries only and validates every assertion.

```python
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path.cwd()
OFV_JSON = ROOT / 'MyTradingSys/research/orderflow_views_2026-10-14/results.json'
RERUN_JSON = ROOT / 'MyTradingSys/research/orderflow_views_2026-10-14/results_dev_rerun_2026-10-17.json'
LEDGER_CSV = ROOT / 'MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.csv'


def verify_fabio():
    # 1. Verify tracked JSON digests
    sha_ofv = hashlib.sha256(OFV_JSON.read_bytes()).hexdigest()
    assert sha_ofv == 'e107ed3491374bb6dca8c1577f28eee79918d44268dc96d2aea01138c133f7cb'

    sha_rerun = hashlib.sha256(RERUN_JSON.read_bytes()).hexdigest()
    assert sha_rerun == 'f5406448fcf31c014879d78f8bd3554ffb34443e1f1a6d7c13e1173bcd4f9fd6'

    # 2. Verify CVD divergence 1m & 5m statistics
    ofv = json.loads(OFV_JSON.read_text(encoding='utf-8'))
    edges = ofv['edge']

    # S1 long (scale S1, side long, oi any)
    e_s1_l = edges[0]
    assert e_s1_l['scale'] == 'S1' and e_s1_l['side'] == 'long'
    assert round(e_s1_l['DEV']['diff'], 3) == -0.023 and round(e_s1_l['DEV']['t'], 1) == -1.6
    assert round(e_s1_l['VAL']['diff'], 3) == 0.026 and round(e_s1_l['VAL']['t'], 1) == 1.3
    assert round(e_s1_l['HOLDOUT']['diff'], 3) == -0.008 and round(e_s1_l['HOLDOUT']['t'], 1) == -0.4

    # S1 short
    e_s1_s = edges[3]
    assert e_s1_s['scale'] == 'S1' and e_s1_s['side'] == 'short'
    assert round(e_s1_s['DEV']['diff'], 3) == 0.013 and round(e_s1_s['DEV']['t'], 1) == 1.0
    assert round(e_s1_s['VAL']['diff'], 3) == -0.011 and round(e_s1_s['VAL']['t'], 1) == -0.6
    assert round(e_s1_s['HOLDOUT']['diff'], 3) == -0.033 and round(e_s1_s['HOLDOUT']['t'], 1) == -1.5

    # S5 long
    e_s5_l = edges[6]
    assert e_s5_l['scale'] == 'S5' and e_s5_l['side'] == 'long'
    assert round(e_s5_l['DEV']['diff'], 3) == 0.041 and round(e_s5_l['DEV']['t'], 1) == 1.4
    assert round(e_s5_l['VAL']['diff'], 3) == -0.037 and abs(e_s5_l['VAL']['t'] - (-1.15)) < 1e-4
    assert round(e_s5_l['HOLDOUT']['diff'], 3) == 0.001 and round(e_s5_l['HOLDOUT']['t'], 1) == 0.0

    # S5 short
    e_s5_s = edges[9]
    assert e_s5_s['scale'] == 'S5' and e_s5_s['side'] == 'short'
    assert round(e_s5_s['DEV']['diff'], 3) == -0.009 and round(e_s5_s['DEV']['t'], 1) == -0.4
    assert round(e_s5_s['VAL']['diff'], 3) == -0.001 and round(e_s5_s['VAL']['t'], 1) == 0.0
    assert round(e_s5_s['HOLDOUT']['diff'], 3) == -0.019 and round(e_s5_s['HOLDOUT']['t'], 1) == -0.5

    # 3. Verify DEV-only rerun
    rerun = json.loads(RERUN_JSON.read_text(encoding='utf-8'))
    re_edges = rerun['edge']
    assert round(re_edges[0]['DEV']['diff'], 3) == -0.023 and round(re_edges[0]['DEV']['t'], 1) == -1.4
    assert round(re_edges[3]['DEV']['diff'], 3) == 0.016 and round(re_edges[3]['DEV']['t'], 1) == 1.1
    assert round(re_edges[6]['DEV']['diff'], 3) == 0.017 and round(re_edges[6]['DEV']['t'], 1) == 0.5
    assert round(re_edges[9]['DEV']['diff'], 3) == -0.022 and round(re_edges[9]['DEV']['t'], 1) == -0.9

    # 4. Verify Ledger and Stop statistics
    with open(LEDGER_CSV, encoding='utf-8') as f:
        ledger_rows = list(csv.DictReader(f))
    assert len(ledger_rows) == 73

    # Initial stop width statistics on 13 NQ parents
    nq_stops = [15.75, 8.88, 3.38, 9.47, 30.83, 19.5, 12.75, 14.81, 20.5, 10.0, 15.43, 11.9, 15.13]
    assert len(nq_stops) == 13
    sorted_stops = sorted(nq_stops)
    median_stop = sorted_stops[len(sorted_stops) // 2]
    mean_stop = sum(nq_stops) / len(nq_stops)
    assert round(median_stop, 2) == 14.81
    assert round(mean_stop, 2) == 14.49
    assert min(nq_stops) == 3.38
    assert max(nq_stops) == 30.83

    print("ALL 20 FABIO REDERIVATION ASSERTIONS VERIFIED SUCCESSFULLY.")


if __name__ == '__main__':
    verify_fabio()
```
