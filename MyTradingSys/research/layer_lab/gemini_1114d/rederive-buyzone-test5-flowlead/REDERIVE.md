PASS

Independent blind re-derivation of `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14` from `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/PRE_REG.md`, `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/PRE_REG.md` (phase definitions), and the host cache data (`$MTS_FLOW_CACHE`, `$MTS_DATA_CACHE`), without reading `REPORT.md`, `summary.json`, or study code prior to recomputation. Script: `MyTradingSys/research/layer_lab/gemini_1114d/rederive-buyzone-test5-flowlead/rederive.py`.

## Claim Table

| Claim | Recomputed | Stated | Source (`file:line`) | Status |
|---|---|---|---|---|
| Primary verdict (ALL phases, VAL, ret24, both cutoffs) | KILL (OURS, via `rederive.py` + `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/PRE_REG.md:42`) | KILL (SOURCED: `"Verdict: KILL."`) | `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/REPORT.md:5`, `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/summary.json:15376` | MATCH |
| Total flow-return days (`ret24`, `2023-01-01`..`2026-11-11`) | 1411 (OURS) | 1411 (SOURCED: `"Flow days used: 1411, 2023-01-01 to 2026-11-11."`) | `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/REPORT.md:14`, `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/summary.json:4` | MATCH |
| `ALL1M` VAL `n` | 1046 (OURS) | 1046 (SOURCED: `ALL1M \| 1046`) | `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/REPORT.md:9`, `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/summary.json:178` | MATCH |
| `ALL1M` VAL spread (bp) | +32.601 bp (OURS) | 32.6 bp (SOURCED: `ALL1M \| 1046 \| 32.6`) | `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/REPORT.md:9`, `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/summary.json:193` | MATCH |
| `ALL1M` VAL 95% block-bootstrap CI (bp) | [-7.920, +75.058] bp (OURS) | [-7.92, 75.06] bp (SOURCED: `[-7.92, 75.06]`) | `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/REPORT.md:9`, `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/summary.json:206` | MATCH |
| `ALL1M` DEV `n` and spread (bp) | n=365, +8.321 bp (OURS) | n=365, 8.32 bp (SOURCED: `365 \| 8.32`) | `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/REPORT.md:9`, `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/summary.json:12` | MATCH |
| `ALL5M` VAL `n` | 1046 (OURS) | 1046 (SOURCED: `ALL5M \| 1046`) | `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/REPORT.md:10`, `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/summary.json:2548` | MATCH |
| `ALL5M` VAL spread (bp) | +4.806 bp (OURS) | 4.81 bp (SOURCED: `ALL5M \| 1046 \| 4.81`) | `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/REPORT.md:10`, `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/summary.json:2563` | MATCH |
| `ALL5M` VAL 95% block-bootstrap CI (bp) | [-28.997, +39.135] bp (OURS) | [-29.0, 39.14] bp (SOURCED: `[-29.0, 39.14]`) | `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/REPORT.md:10`, `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/summary.json:2576` | MATCH |
| `ALL5M` DEV `n` and spread (bp) | n=365, -1.414 bp (OURS) | n=365, -1.41 bp (SOURCED: `365 \| -1.41`) | `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/REPORT.md:10`, `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/summary.json:15406` | MATCH |
| `ALL1M` & `ALL5M` DEV quintile cutoffs (bp) | `ALL1M`: [-70.015, -19.056, 15.865, 61.390]; `ALL5M`: [-18.794, -2.367, 3.349, 16.248] (OURS) | `ALL1M`: [-70.01, -19.06, 15.87, 61.39]; `ALL5M`: [-18.79, -2.37, 3.35, 16.25] (SOURCED) | `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/REPORT.md:99` | MATCH |

## Notes
- Shuffle placebo (2000 draws, seed 1114): our `np.random.default_rng(1114)` within-phase shuffle produced VAL 95.00% percentile (band [-39.88, +38.86] bp) for `ALL1M` and 61.50% (band [-35.11, +33.19] bp) for `ALL5M` (OURS), consistent with the stated 95.2% ([-40.97, 37.64] bp) and 62.0% ([-33.59, 34.93] bp) (SOURCED, `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/REPORT.md:9`, `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/summary.json:214`, `MyTradingSys/research/buyzone_test5_flowlead_2026-11-14/summary.json:2584`); minor Monte Carlo variance from RNG/order does not affect the < 97.5% KILL decision.
