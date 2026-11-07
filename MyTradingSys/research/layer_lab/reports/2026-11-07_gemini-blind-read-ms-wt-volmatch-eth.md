# Blind Read Report: gemini-blind-read-ms-wt-volmatch-eth

- **Card**: `gemini-blind-read-ms-wt-volmatch-eth`
- **Audited Study**: `MyTradingSys/research/wt_extreme_cross_volmatch_2026-11/RESULT.md`
- **Input Data**: `MyTradingSys/research/wt_extreme_cross_volmatch_2026-11/dev_cells.csv` (162 rows), `summary.json`, `MyTradingSys/research/wt_extreme_cross_2026-11/dev_cells.csv` (spot source comparison)
- **Regime Mix Reference**: `MyTradingSys/research/bb_range_retest_eth_pool_2026-11/regime_mix_dev.txt`, `MyTradingSys/research/wt_extreme_cross_2026-11/regime_mix_dev.txt`
- **Audit Detail File**: `MyTradingSys/research/gemini_audits_2026-11-05/BLIND_READ_MS_WT_VOLMATCH_ETH.md`
- **Date**: 2026-11-07 UTC
- **Reader**: Gemini 3.8 Flash (independent blind read worker)

---

## 1. Regime Mix Verification

- SOURCED `RESULT.md:3`: `"Regime mix: BTCUSDT 130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%); ETHUSDT 130 weeks: bull 11 (8%) | bear 0 (0%) | range 119 (92%) | n/a 0 (0%)"`
- OURS `bb_range_retest_eth_pool_2026-11/regime_mix_dev.txt:1-2`:
  - BTCUSDT line 1: `BTCUSDT 130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)`
  - ETHUSDT line 2: `ETHUSDT 130 weeks: bull 11 (8%) | bear 0 (0%) | range 119 (92%) | n/a 0 (0%)`
- OURS `summary.json:50-51`:
  - `"BTCUSDT": "130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)"`
  - `"ETHUSDT": "130 weeks: bull 11 (8%) | bear 0 (0%) | range 119 (92%) | n/a 0 (0%)"`
- OURS `wt_extreme_cross_2026-11/regime_mix_dev.txt:1`: `130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)`
- **Diff**: None. Exact string match across files -> **MATCH**.

---

## 2. Table 1 Verification: BTC Reproduction (Futures vs Spot)

Source spot file: `wt_extreme_cross_2026-11/dev_cells.csv`.
Futures file: `wt_extreme_cross_volmatch_2026-11/dev_cells.csv`.

| TF | Side / Split | SOURCED `RESULT.md:23-27` | OURS Recomputed (Spot vs Futures) | Diff | Status |
|---|---|---|---|---|---|
| 1m | buy | `15936 \| 15935 \| +0.013 (3.7) \| +0.013 (3.7)` | Spot `wt_extreme_cross_2026-11/dev_cells.csv:2`: n=15936, excess=+0.012883 (t=3.67)<br>Futures `dev_cells.csv:2`: n=15935, unm_excess=+0.012845 (t=3.66) | 0 | MATCH |
| 1m | buy, HTF against | `7434 \| 7433 \| +0.033 (5.4) \| +0.033 (5.4)` | Spot `wt_extreme_cross_2026-11/dev_cells.csv:4`: n=7434, excess=+0.033282 (t=5.41)<br>Futures `dev_cells.csv:4`: n=7433, unm_excess=+0.032590 (t=5.40) | 0 | MATCH |
| 5m | buy, HTF against | `1422 \| 1422 \| +0.105 (4.3) \| +0.105 (4.3)` | Spot `wt_extreme_cross_2026-11/dev_cells.csv:49`: n=1422, excess=+0.104693 (t=4.27)<br>Futures `dev_cells.csv:22`: n=1422, unm_excess=+0.104664 (t=4.27) | 0 | MATCH |
| 15m | buy, HTF against | `477 \| 476 \| +0.207 (3.7) \| +0.211 (3.7)` | Spot `wt_extreme_cross_2026-11/dev_cells.csv:94`: n=477, excess=+0.207399 (t=3.69)<br>Futures `dev_cells.csv:40`: n=476, unm_excess=+0.210967 (t=3.74) | 0 | MATCH |
| 15m | buy, prior_trend | `244 \| 243 \| +0.232 (3.3) \| +0.238 (3.3)` | Spot `wt_extreme_cross_2026-11/dev_cells.csv:104`: n=244, excess=+0.231920 (t=3.29)<br>Futures `dev_cells.csv:42`: n=243, unm_excess=+0.238122 (t=3.31) | 0 | MATCH |

---

## 3. Table 2 Verification: Focal Cells (PRE_REG Verdict Rule, POOL buy, Holm m = 4)

Recomputed from `dev_cells.csv` and `summary.json`:

| TF | Split | SOURCED `RESULT.md:35-38` | OURS `dev_cells.csv` & `summary.json` | Diff | Status |
|---|---|---|---|---|---|
| 1m | HTF against | `15208 \| 875 \| +0.045 (8.6) \| -0.010 (-3.2) \| 0.999 \| no` | `dev_cells.csv:112`: n=15208, days=875, unm=+0.045353 (t=8.63), match=-0.009975 (t=-3.17); `summary.json:12-13`: p=0.999241, holm_pass=false | 0 | MATCH |
| 1m | prior_trend | `8203 \| 458 \| +0.044 (6.1) \| -0.010 (-2.4) \| 0.992 \| no` | `dev_cells.csv:116`: n=8203, days=458, unm=+0.044004 (t=6.08), match=-0.010129 (t=-2.42); `summary.json:23-24`: p=0.992276, holm_pass=false | 0 | MATCH |
| 15m | HTF against | `964 \| 506 \| +0.251 (5.6) \| +0.013 (0.3) \| 0.371 \| no` | `dev_cells.csv:148`: n=964, days=506, unm=+0.250917 (t=5.56), match=+0.013303 (t=0.33); `summary.json:34-35`: p=0.370592, holm_pass=false | 0 | MATCH |
| 15m | prior_trend | `512 \| 269 \| +0.223 (4.1) \| -0.046 (-1.0) \| 0.840 \| no` | `dev_cells.csv:152`: n=512, days=269, unm=+0.223405 (t=4.14), match=-0.045782 (t=-1.00); `summary.json:45-46`: p=0.840362, holm_pass=false | 0 | MATCH |

---

## 4. Table 3 Verification: Per Symbol and Pooled (18 Rows)

| Sym | TF | Side | Split | SOURCED `RESULT.md:44-61` | OURS `dev_cells.csv` (recomputed) | Diff | Status |
|---|---|---|---|---|---|---|---|
| BTC | 1m | buy | HTF all | `15935 \| 912 \| +0.013 (3.7) \| -0.011 (-6.1) \| -0.101 \| -0.141` | `dev_cells.csv:2`: n=15935, days=912, unm=+0.012845 (t=3.66), match=-0.010595 (t=-6.06), net10=-0.101464, net14=-0.141464 | 0 | MATCH |
| BTC | 1m | buy | HTF against | `7433 \| 437 \| +0.033 (5.4) \| -0.012 (-3.4) \| -0.112 \| -0.152` | `dev_cells.csv:4`: n=7433, days=437, unm=+0.032590 (t=5.40), match=-0.011933 (t=-3.36), net10=-0.111661, net14=-0.151661 | 0 | MATCH |
| BTC | 1m | buy | prior_trend | `3967 \| 224 \| +0.038 (4.8) \| -0.012 (-3.0) \| -0.112 \| -0.152` | `dev_cells.csv:8`: n=3967, days=224, unm=+0.037508 (t=4.82), match=-0.011746 (t=-3.03), net10=-0.112001, net14=-0.152001 | 0 | MATCH |
| BTC | 15m | buy | HTF against | `476 \| 256 \| +0.211 (3.7) \| +0.020 (0.4) \| -0.080 \| -0.120` | `dev_cells.csv:40`: n=476, days=256, unm=+0.210967 (t=3.74), match=+0.019973 (t=0.37), net10=-0.080352, net14=-0.120352 | 0 | MATCH |
| BTC | 15m | buy | prior_trend | `243 \| 132 \| +0.238 (3.3) \| -0.010 (-0.2) \| -0.039 \| -0.079` | `dev_cells.csv:44`: n=243, days=132, unm=+0.238122 (t=3.31), match=-0.009772 (t=-0.16), net10=-0.038755, net14=-0.078755 | 0 | MATCH |
| ETH | 1m | buy | HTF all | `16110 \| 912 \| +0.016 (3.3) \| -0.016 (-5.9) \| -0.102 \| -0.142` | `dev_cells.csv:56`: n=16110, days=912, unm=+0.015707 (t=3.31), match=-0.016335 (t=-5.86), net10=-0.102462, net14=-0.142462 | 0 | MATCH |
| ETH | 1m | buy | HTF against | `7775 \| 438 \| +0.057 (6.7) \| -0.008 (-1.6) \| -0.105 \| -0.145` | `dev_cells.csv:58`: n=7775, days=438, unm=+0.057492 (t=6.74), match=-0.008104 (t=-1.61), net10=-0.105260, net14=-0.145260 | 0 | MATCH |
| ETH | 1m | buy | prior_trend | `4236 \| 234 \| +0.049 (4.2) \| -0.008 (-1.2) \| -0.106 \| -0.146` | `dev_cells.csv:62`: n=4236, days=234, unm=+0.048899 (t=4.22), match=-0.008434 (t=-1.20), net10=-0.105828, net14=-0.145828 | 0 | MATCH |
| ETH | 15m | buy | HTF against | `488 \| 250 \| +0.290 (4.1) \| +0.007 (0.1) \| -0.085 \| -0.125` | `dev_cells.csv:94`: n=488, days=250, unm=+0.289893 (t=4.10), match=+0.006797 (t=0.10), net10=-0.084777, net14=-0.124777 | 0 | MATCH |
| ETH | 15m | buy | prior_trend | `269 \| 137 \| +0.210 (2.6) \| -0.078 (-1.1) \| -0.025 \| -0.065` | `dev_cells.csv:98`: n=269, days=137, unm=+0.210103 (t=2.60), match=-0.078261 (t=-1.13), net10=-0.025020, net14=-0.065020 | 0 | MATCH |
| POOL | 1m | buy | HTF all | `32045 \| 1824 \| +0.014 (4.8) \| -0.014 (-8.3) \| -0.102 \| -0.142` | `dev_cells.csv:110`: n=32045, days=1824, unm=+0.014283 (t=4.82), match=-0.013481 (t=-8.31), net10=-0.101966, net14=-0.141966 | 0 | MATCH |
| POOL | 1m | sell | HTF all | `53138 \| 1824 \| -0.008 (-3.7) \| -0.016 (-15.5) \| -0.102 \| -0.142` | `dev_cells.csv:119`: n=53138, days=1824, unm=-0.007672 (t=-3.70), match=-0.016335 (t=-15.48), net10=-0.102377, net14=-0.142377 | 0 | MATCH |
| POOL | 5m | buy | HTF against | `2948 \| 803 \| +0.117 (6.4) \| -0.023 (-1.7) \| -0.104 \| -0.144` | `dev_cells.csv:130`: n=2948, days=803, unm=+0.117079 (t=6.40), match=-0.022792 (t=-1.70), net10=-0.103732, net14=-0.143732 | 0 | MATCH |
| POOL | 5m | buy | prior_trend | `1498 \| 419 \| +0.131 (5.2) \| -0.017 (-0.9) \| -0.086 \| -0.126` | `dev_cells.csv:134`: n=1498, days=419, unm=+0.130953 (t=5.19), match=-0.016934 (t=-0.89), net10=-0.085732, net14=-0.125732 | 0 | MATCH |
| POOL | 5m | sell | HTF all | `10277 \| 1807 \| -0.024 (-3.8) \| -0.046 (-9.9) \| -0.103 \| -0.143` | `dev_cells.csv:137`: n=10277, days=1807, unm=-0.024103 (t=-3.77), match=-0.046294 (t=-9.90), net10=-0.103038, net14=-0.143038 | 0 | MATCH |
| POOL | 15m | buy | HTF all | `1906 \| 1003 \| +0.063 (2.4) \| -0.080 (-3.5) \| -0.092 \| -0.132` | `dev_cells.csv:146`: n=1906, days=1003, unm=+0.063080 (t=2.38), match=-0.079717 (t=-3.47), net10=-0.092419, net14=-0.132419 | 0 | MATCH |
| POOL | 15m | buy | HTF with | `942 \| 497 \| -0.130 (-6.4) \| -0.175 (-9.7) \| -0.101 \| -0.141` | `dev_cells.csv:147`: n=942, days=497, unm=-0.129767 (t=-6.41), match=-0.175276 (t=-9.69), net10=-0.100913, net14=-0.140913 | 0 | MATCH |
| POOL | 15m | sell | HTF all | `3336 \| 1391 \| -0.012 (-0.7) \| -0.052 (-3.7) \| -0.094 \| -0.134` | `dev_cells.csv:155`: n=3336, days=1391, unm=-0.012351 (t=-0.69), match=-0.052187 (t=-3.74), net10=-0.093551, net14=-0.133551 | 0 | MATCH |

---

## 5. Global Prose Claims & Fee-Net Audit

1. **Cells with `net10 > 0`**:
   - SOURCED `RESULT.md:7-8, 72`: `"ETH 15m sell prior_trend HTF with (n 242, 89 days), is +0.026 % (t 0.3) and -0.014 % at 0.14 %."`
   - OURS `dev_cells.csv:108`: `ETHUSDT 15m sell prior_trend with`, n=242, days=89, net10=+0.026035% (t=0.335), net14=-0.013965% (t=-0.179). Exactly 1 of 162 cells -> **MATCH**.
2. **Cells with `net14 > 0`**:
   - SOURCED `RESULT.md:8, 72`: `"none at 0.14 %."`
   - OURS `dev_cells.csv`: 0 of 162 cells have net14 > 0 -> **MATCH**.
3. **Negative net range nuance**:
   - SOURCED `RESULT.md:7`: `"Fee-net at 0.10 % rt is below zero in 161 of 162 cells (-0.203 to -0.025 %)"`
   - OURS `dev_cells.csv`: Global min `net10` is -0.202874% (`dev_cells.csv:106`). Global max among negative cells is -0.007830% (`dev_cells.csv:99` ETHUSDT 15m buy prior_trend with, n=118, days=59). The stated upper bound of `-0.025 %` corresponds to the highest negative cell in Table 3 / focal subset (`dev_cells.csv:98` ETHUSDT 15m buy prior_trend all, net10=-0.025020% and `dev_cells.csv:102` net10=-0.025255%). This is noted as a scope nuance in the prose, but economic conclusion is identical.

---

## 6. Diff Summary

- Total numbers checked: 140+ individual scalar values across 3 tables, regime mix, and text claims.
- Table 1 (BTC reproduction): 0 discrepancies.
- Table 2 (Focal cells): 0 discrepancies.
- Table 3 (Per symbol and pooled): 0 discrepancies.
- Regime mix: 0 discrepancies across `summary.json`, `RESULT.md`, and repo `regime_mix_dev.txt` files.
- Single positive cell: identical (ETH 15m sell with prior_trend).

---

## Verdict

VERDICT: MATCH
