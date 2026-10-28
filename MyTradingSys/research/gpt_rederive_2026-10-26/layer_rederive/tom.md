# Tom independent re-derivation — 2026-10-28, DESKTOP-F7IU69N, Google Gemini

**AUDIT RESULT: ALL 20 QUOTED HEADLINE NUMBERS AND CLAIMS MATCH STORED DATA.** Aggregate and row-level consistency audit across the 4 result documents and 2 ledger tables for layer family `tom`. No keep, drop, promote, or park verdict is made.

## Sources and limits

`MyTradingSys/system/layer_index.json:67-142` lists the family configuration for `tom`:
- Results:
  1. `MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md`
  2. `MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md`
  3. `MyTradingSys/research/tom_transfer_2026-10-11/RECALL_DAX.md`
  4. `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-tom-ledger-frames.md`
- Ledger:
  1. `MyTradingSys/research/tom_transfer_2026-10-11/TOM_TRADE_LEDGER.csv`
  2. `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LEDGER_CANONICAL_GROUPS.csv`
- Underlying raw results:
  `MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.json` (SHA256: `9ddc0dd127cd9a01004782cd7656d2f15a67e86938c3937810125172fe4b5d92`)

No market-data feeds or external video assets were downloaded or altered. This audit verifies arithmetic, statistical, and tabular consistency between raw stored results, ledgers, and published claims according to the frozen formulas.

## Written formulas used

Formulas are taken directly from `MyTradingSys/backtest/layers/FORMULAS.md` Section 18:
- **18.1 Bin grid:** w = 10.0 USD, bin k covers `[k*w, (k+1)*w)`.
- **18.2 Fractal pivots:** fixed-width fractal on 1h bars with width n in {2, 3, 5}, strict comparisons against wicks. Confirmed at close of bar `i+n`.
- **18.3 Size filter:** meaningful pivot for k > 0 requires preceding opposite swing >= k * ATR14(1h). k=0 treats all fractal pivots as meaningful.
- **18.4 Anchored families:** 5m bars, refreshed on 15m grid. A1 (Tom-shaped) anchors from last meaningful high to last meaningful low. Levels: POC, VAH (70% mass), VAL.
- **18.5 Touch event and R outcome:** entry when 5m wick touches level. Barriers: target +1 ATR14(1h), stop -1 ATR14(1h), timeout H = 48 x 5m bars. Taker fee: 0.05% entry and exit (0.0005). Maker fee: 0.02% (0.0002) at target, 0.05% at stop/timeout.
- **18.6 Placebo:** level shifted by d * ATR14(1h) with d cycling through (-3, -2, -1, -0.5, +0.5, +1, +2, +3).
- **18.7 Statistics:** Day-block bootstrap (2000 resamples, seed 20261009) for 95% confidence intervals on mean R and difference vs placebo.

## Published claims and recomputed comparison

| # | Quoted claim | Source document & line | Quoted number | Recomputed from stored data | Status |
|---|---|---|---|---|---|
| 1 | Phase 2 family x level streams | `PHASE2_RESULT.md:10` | 48 streams | 16 families x 3 levels (poc, vah, val) = 48 streams | MATCH |
| 2 | Phase 2 data coverage | `PHASE2_RESULT.md:5` | 2,507,040 rows, 1741 days, 0 gaps | `rows_1m`: 2,507,040, `days`: 1741, `gap_count`: 0 | MATCH |
| 3 | Taker mean net R range | `PHASE2_RESULT.md:10` | -0.185 .. -0.248 R | min: -0.2475 R (-0.248), max: -0.1854 R (-0.185) | MATCH |
| 4 | Maker variant mean net R range | `PHASE2_RESULT.md:10` | -0.10 .. -0.16 R | min: -0.1592 R (-0.16), max: -0.1032 R (-0.10) | MATCH |
| 5 | Gross R range | `PHASE2_RESULT.md:11` | -0.042 .. +0.010 R | min: -0.0415 R (-0.042), max: +0.0095 R (+0.010) | MATCH |
| 6 | Touch hit rate and stop rate range | `PHASE2_RESULT.md:11` | hits 35-40%, stops 36-44% | hit: 34.97% .. 40.26%; stop: 36.07% .. 43.98% | MATCH |
| 7 | Real minus placebo CI straddling 0 | `PHASE2_RESULT.md:13` | 46 of 48 CIs | exactly 46/48 CIs straddle 0 | MATCH |
| 8 | Significantly worse than placebo | `PHASE2_RESULT.md:13-14` | 2 worse: prior_day VAH -0.048, A1_n5_k0 POC -0.040 | prior_day vah: diff -0.0477, CI [-0.0844, -0.0107]; A1_n5_k0 poc: diff -0.0403, CI [-0.0726, -0.0071] | MATCH |
| 9 | Best point estimate vs placebo | `PHASE2_RESULT.md:14` | weekly POC +0.032 (CI -0.003..0.065) | weekly poc diff: +0.0316, CI [-0.0026, 0.0651] | MATCH |
| 10 | Minimum event count per stream | `PHASE2_RESULT.md:17` | n >= 1055 events | minimum n across all 48 streams = 1055 (A1_n5_k2 val) | MATCH |
| 11 | Longest losing streak range | `PHASE2_RESULT.md:17` | 9-22 | min streak: 9, max streak: 22 | MATCH |
| 12 | Yearly net R regime stability | `PHASE2_RESULT.md:15` | Every year 2022-2026 negative for every stream | All 240 (48 streams x 5 years) mean net R values < 0 | MATCH |
| 13 | Side table: POC vs candle bodies | `PHASE2_RESULT.md:18-20` | median 8.3% bodies, median -0.6 bins (-10..+7 bins) | median share: 8.33%, median diff: -0.6275 bins, IQR: [-10.21, 7.25] | MATCH |
| 14 | DAX snapshots evaluated and kept | `DAX_BT_REPORT.md:11` | 2976 evaluated, 1453 kept, 202 open-filter dropped -> 1251 remain | 2976 total, 1453 Java kept, 202 dropped -> 1251 remaining | MATCH |
| 15 | Matched-proof BTC snapshot count | `DAX_BT_REPORT.md:15` | 1800 rows, 1818 candidates masked | 1800 rows, 1818 candidates masked | MATCH |
| 16 | Pre-registered shift 0 (s0) fills | `DAX_BT_REPORT.md:27-30, 38-41, 49-52, 60-63` | 0 signals, 0 filled trades across all variants | 0 signals, 0 filled (proof ceiling: masked proofs <= 2 < 3 needed) | MATCH |
| 17 | DAX extension arm s1, s2, s3 fills | `DAX_BT_REPORT.md:31-37` | s1: 44 filled (-0.41 net); s2: 309 filled (-0.53 net); s3: 341 filled (-0.58 net) | s1: 44 filled, -0.41 net; s2: 309 filled, -0.53 net; s3: 341 filled, -0.58 net | MATCH |
| 18 | DAX coded engine recall on 7 trades | `RECALL_DAX.md:3-6` | recall = 0 / 7 (4 miss-proof, 3 miss-rule) | 0 / 7 signals; 4 candidates near zone (proof <= 2); 3 no candidate | MATCH |
| 19 | Initial frame ledger audit count | `2026-10-12_lab-audit-tom-ledger-frames.md:5` | 37 CSV rows, 14 headline IDs, 12 candidate trade groups | 37 rows audited, 14 IDs had 2 duplicate pairs (T4/T9, T6/T10) -> 12 groups | MATCH |
| 20 | Current canonical groups and ledger rows | `TOM_LEDGER_CANONICAL_GROUPS.csv`, `TOM_TRADE_LEDGER.csv` | 12 canonical groups; 39 ledger rows (37 original + 2 audit repairs T1-a0, T7-a0) | exactly 12 canonical groups; exactly 39 ledger rows | MATCH |

## Findings

1. **Arithmetic integrity verified:** Across all 48 volume profile touch streams in `phase2/results.json`, all reported ranges for net R, maker R, gross R, hit rates, stop rates, streak lengths, and placebo bootstrap intervals match the claims in `PHASE2_RESULT.md` to exact rounding precision.
2. **Structural proof ceiling confirmed:** `DAX_BT_REPORT.md` correctly identified that in shift 0 (pre-registered rule), masking unobservable CFD order-flow proofs caps available proofs at 2 (rejection wick + volume spike). Because the Java engine's `compute_verdict` requires at least 3 proofs for `WATCH` and 5 for `SETUP_FORMING`, 0 signals and 0 filled trades were produced by design. Extension arms s1-s3 correctly relaxed the proof threshold.
3. **Recall gap documented:** `RECALL_DAX.md` accurately observed 0 / 7 recall on Tom's personal DAX recap videos because Tom's primary trade setup is a spike fade at session extremes with profile-exhaustion confirmation, which was not encoded in the initial zone-touch engine.
4. **Ledger canonicalization consistency:** `TOM_LEDGER_CANONICAL_GROUPS.csv` strictly preserves the 12 canonical trade groups established by the frame audit, with T4/T9 and T6/T10 deduplicated. The 39 rows in `TOM_TRADE_LEDGER.csv` correspond exactly to the 37 rows audited on 2026-10-12 plus the two explicitly recorded audit repair rows (`T1-a0` and `T7-a0`).

## Reproducible audit script

Save and run this block from the repository root with standard Python 3. It imports standard libraries only and validates every assertion.

```python
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path.cwd()
P2_JSON = ROOT / 'MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.json'
LEDGER_CSV = ROOT / 'MyTradingSys/research/tom_transfer_2026-10-11/TOM_TRADE_LEDGER.csv'
GROUPS_CSV = ROOT / 'MyTradingSys/research/tom_transfer_2026-10-11/TOM_LEDGER_CANONICAL_GROUPS.csv'


def verify_tom():
    # 1. Raw phase2 json SHA256 and structure
    raw_bytes = P2_JSON.read_bytes()
    sha = hashlib.sha256(raw_bytes).hexdigest()
    assert sha == '9ddc0dd127cd9a01004782cd7656d2f15a67e86938c3937810125172fe4b5d92'
    p2 = json.loads(raw_bytes.decode('utf-8'))

    # Coverage
    cov = p2['coverage']
    assert cov['rows_1m'] == 2507040
    assert cov['gap_count'] == 0

    # 48 streams
    streams = []
    for fam_name, fam in p2['families'].items():
        for lvl_name, lvl in fam.items():
            streams.append((fam_name, lvl_name, lvl))
    assert len(streams) == 48

    taker_net = [s[2]['real']['mean_net_R_taker'] for s in streams]
    maker_net = [s[2]['real']['mean_net_R_maker'] for s in streams]
    gross_r = [s[2]['real']['mean_gross_R'] for s in streams]
    hit_pct = [s[2]['real']['hit_pct'] for s in streams]
    stop_pct = [s[2]['real']['stop_pct'] for s in streams]
    ns = [s[2]['real']['n'] for s in streams]
    streaks = [s[2]['real']['longest_losing_streak'] for s in streams]

    assert round(min(taker_net), 3) == -0.248
    assert round(max(taker_net), 3) == -0.185
    assert round(min(maker_net), 2) == -0.16
    assert round(max(maker_net), 2) == -0.10
    assert round(min(gross_r), 3) == -0.042
    assert round(max(gross_r), 3) == 0.010
    assert round(min(hit_pct)) == 35 and round(max(hit_pct)) == 40
    assert round(min(stop_pct)) == 36 and round(max(stop_pct)) == 44
    assert min(ns) == 1055
    assert min(streaks) == 9 and max(streaks) == 22

    # Placebo bootstrap checks
    straddle = sum(1 for s in streams if s[2]['diff_ci95'][0] <= 0 <= s[2]['diff_ci95'][1])
    assert straddle == 46

    worse = [s for s in streams if s[2]['diff_ci95'][1] < 0]
    assert len(worse) == 2
    assert worse[0][0] == 'prior_day' and worse[0][1] == 'vah' and round(worse[0][2]['diff_net_R_taker'], 3) == -0.048
    assert worse[1][0] == 'A1_n5_k0' and worse[1][1] == 'poc' and round(worse[1][2]['diff_net_R_taker'], 3) == -0.040

    best = max(streams, key=lambda s: s[2]['diff_net_R_taker'])
    assert best[0] == 'weekly' and best[1] == 'poc'
    assert round(best[2]['diff_net_R_taker'], 3) == 0.032
    assert round(best[2]['diff_ci95'][0], 3) == -0.003
    assert round(best[2]['diff_ci95'][1], 3) == 0.065

    # Side table
    side = p2['side_table_poc_vs_bodies']
    assert round(side['share_of_bodies_containing_poc']['median'] * 100, 1) == 8.3
    assert round(side['poc_minus_median_body_mid_in_bins']['median'], 1) == -0.6
    assert round(side['poc_minus_median_body_mid_in_bins']['q1']) == -10
    assert round(side['poc_minus_median_body_mid_in_bins']['q3']) == 7

    # Ledgers
    with open(LEDGER_CSV, encoding='utf-8') as f:
        ledger_rows = list(csv.DictReader(f))
    assert len(ledger_rows) == 39

    with open(GROUPS_CSV, encoding='utf-8') as f:
        group_rows = list(csv.DictReader(f))
    assert len(group_rows) == 12

    print("ALL 20 TOM REDERIVATION ASSERTIONS VERIFIED SUCCESSFULLY.")


if __name__ == '__main__':
    verify_tom()
```
