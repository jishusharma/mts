# Blind Read Audit: `wt_extreme_cross_volmatch_2026-11` (`RESULT.md` vs CSVs)

- **Card**: `gemini-blind-read-ms-wt-volmatch-eth`
- **Audited Study**: `MyTradingSys/research/wt_extreme_cross_volmatch_2026-11/RESULT.md`
- **Raw Inputs**: `dev_cells.csv` (162 rows), `summary.json`, `wt_extreme_cross_2026-11/dev_cells.csv` (spot)
- **Date**: 2026-11-07 UTC
- **Reader**: Gemini 3.8 Flash (independent blind read worker)

## 1. Regime Mix & Global Cell Counts Verification

- **Regime mix (`summary.json` vs `RESULT.md:3`)**:
  - SOURCED `RESULT.md:3`: `"Regime mix: BTCUSDT 130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%); ETHUSDT 130 weeks: bull 11 (8%) | bear 0 (0%) | range 119 (92%) | n/a 0 (0%)"`
  - OURS `summary.json:50-51` & `bb_range_retest_eth_pool_2026-11/regime_mix_dev.txt:1-2`:
    - `BTCUSDT 130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)` [OURS]
    - `ETHUSDT 130 weeks: bull 11 (8%) | bear 0 (0%) | range 119 (92%) | n/a 0 (0%)` [OURS]
  - Diff: 0 -> **MATCH**
- **162 cells fee-net check (`dev_cells.csv` vs `RESULT.md:7-8, 72`)**:
  - SOURCED `RESULT.md:7-8, 72`: `"ETH 15m sell prior_trend HTF with (n 242, 89 days), is +0.026 % (t 0.3) and -0.014 % at 0.14 %."`
  - OURS `dev_cells.csv:108`: Cells with `net10 > 0`: 1 of 162 (`ETHUSDT 15m sell prior_trend with`, `n=242, days=89, net10=+0.026035%, t=0.335, net14=-0.013965%`).
  - Remaining 161 of 162 cells at 0.10% RT range from `-0.203%` to `-0.008%` (with stated focal upper limit `-0.025%` matching table line 53).
  - Cells with `net14 > 0`: 0 of 162.
  - Matches `RESULT.md:7-8, 72` -> **MATCH**

## 2. Table 1 Verification: BTC Reproduction (Futures vs Spot, `RESULT.md:21-27`)

| TF | Side / Split | SOURCED `RESULT.md:23-27` | OURS Recomputed (Spot `wt_extreme_cross_2026-11/dev_cells.csv` vs Futures `dev_cells.csv`) | Diff | Status |
|---|---|---|---|---|---|
| 1m | buy | `15936 \| 15935 \| +0.013 (3.7) \| +0.013 (3.7)` | Spot L2: n=15936, excess=+0.012883 (t=3.67); Futures L2: n=15935, unm=+0.012845 (t=3.66) | 0 | MATCH |
| 1m | buy, HTF against | `7434 \| 7433 \| +0.033 (5.4) \| +0.033 (5.4)` | Spot L4: n=7434, excess=+0.033282 (t=5.41); Futures L4: n=7433, unm=+0.032590 (t=5.40) | 0 | MATCH |
| 5m | buy, HTF against | `1422 \| 1422 \| +0.105 (4.3) \| +0.105 (4.3)` | Spot L49: n=1422, excess=+0.104693 (t=4.27); Futures L22: n=1422, unm=+0.104664 (t=4.27) | 0 | MATCH |
| 15m | buy, HTF against | `477 \| 476 \| +0.207 (3.7) \| +0.211 (3.7)` | Spot L94: n=477, excess=+0.207399 (t=3.69); Futures L40: n=476, unm=+0.210967 (t=3.74) | 0 | MATCH |
| 15m | buy, prior_trend | `244 \| 243 \| +0.232 (3.3) \| +0.238 (3.3)` | Spot L104: n=244, excess=+0.231920 (t=3.29); Futures L44: n=243, unm=+0.238122 (t=3.31) | 0 | MATCH |

## 3. Table 2 Verification: Focal Cells (`dev_cells.csv` & `summary.json` vs `RESULT.md:33-38`)

| TF | Split | SOURCED `RESULT.md:35-38` | OURS `dev_cells.csv` & `summary.json` | Diff | Status |
|---|---|---|---|---|---|
| `1m` | `HTF against` (`daytag=all`) | `15208 \| 875 \| +0.045 (8.6) \| -0.010 (-3.2) \| 0.999 \| no` | `dev_cells.csv:112`: n=15208, days=875, unm=+0.045 (8.6), match=-0.010 (-3.2); `summary.json:12-13`: p=0.999, holm_pass=false | 0 | MATCH |
| `1m` | `prior_trend` (`htf=all`) | `8203 \| 458 \| +0.044 (6.1) \| -0.010 (-2.4) \| 0.992 \| no` | `dev_cells.csv:116`: n=8203, days=458, unm=+0.044 (6.1), match=-0.010 (-2.4); `summary.json:23-24`: p=0.992, holm_pass=false | 0 | MATCH |
| `15m` | `HTF against` (`daytag=all`) | `964 \| 506 \| +0.251 (5.6) \| +0.013 (0.3) \| 0.371 \| no` | `dev_cells.csv:148`: n=964, days=506, unm=+0.251 (5.6), match=+0.013 (0.3); `summary.json:34-35`: p=0.371, holm_pass=false | 0 | MATCH |
| `15m` | `prior_trend` (`htf=all`) | `512 \| 269 \| +0.223 (4.1) \| -0.046 (-1.0) \| 0.840 \| no` | `dev_cells.csv:152`: n=512, days=269, unm=+0.223 (4.1), match=-0.046 (-1.0); `summary.json:45-46`: p=0.840, holm_pass=false | 0 | MATCH |

## 4. Table 3 Verification: Per-Symbol & Pooled Table (`dev_cells.csv` vs `RESULT.md:42-61`)

| Symbol | TF | Side | Split | SOURCED `RESULT.md:44-61` | OURS `dev_cells.csv` (recomputed) | Diff | Status |
|---|---|---|---|---|---|---|---|
| `BTC` | `1m` | `buy` | `HTF all` | `15935 \| 912 \| +0.013 (3.7) \| -0.011 (-6.1) \| -0.101 \| -0.141` | `dev_cells.csv:2`: n=15935, days=912, unm=+0.013 (3.7), match=-0.011 (-6.1), net=-0.101 / -0.141 | 0 | MATCH |
| `BTC` | `1m` | `buy` | `HTF against` | `7433 \| 437 \| +0.033 (5.4) \| -0.012 (-3.4) \| -0.112 \| -0.152` | `dev_cells.csv:4`: n=7433, days=437, unm=+0.033 (5.4), match=-0.012 (-3.4), net=-0.112 / -0.152 | 0 | MATCH |
| `BTC` | `1m` | `buy` | `prior_trend` | `3967 \| 224 \| +0.038 (4.8) \| -0.012 (-3.0) \| -0.112 \| -0.152` | `dev_cells.csv:8`: n=3967, days=224, unm=+0.038 (4.8), match=-0.012 (-3.0), net=-0.112 / -0.152 | 0 | MATCH |
| `BTC` | `15m` | `buy` | `HTF against` | `476 \| 256 \| +0.211 (3.7) \| +0.020 (0.4) \| -0.080 \| -0.120` | `dev_cells.csv:40`: n=476, days=256, unm=+0.211 (3.7), match=+0.020 (0.4), net=-0.080 / -0.120 | 0 | MATCH |
| `BTC` | `15m` | `buy` | `prior_trend` | `243 \| 132 \| +0.238 (3.3) \| -0.010 (-0.2) \| -0.039 \| -0.079` | `dev_cells.csv:44`: n=243, days=132, unm=+0.238 (3.3), match=-0.010 (-0.2), net=-0.039 / -0.079 | 0 | MATCH |
| `ETH` | `1m` | `buy` | `HTF all` | `16110 \| 912 \| +0.016 (3.3) \| -0.016 (-5.9) \| -0.102 \| -0.142` | `dev_cells.csv:56`: n=16110, days=912, unm=+0.016 (3.3), match=-0.016 (-5.9), net=-0.102 / -0.142 | 0 | MATCH |
| `ETH` | `1m` | `buy` | `HTF against` | `7775 \| 438 \| +0.057 (6.7) \| -0.008 (-1.6) \| -0.105 \| -0.145` | `dev_cells.csv:58`: n=7775, days=438, unm=+0.057 (6.7), match=-0.008 (-1.6), net=-0.105 / -0.145 | 0 | MATCH |
| `ETH` | `1m` | `buy` | `prior_trend` | `4236 \| 234 \| +0.049 (4.2) \| -0.008 (-1.2) \| -0.106 \| -0.146` | `dev_cells.csv:62`: n=4236, days=234, unm=+0.049 (4.2), match=-0.008 (-1.2), net=-0.106 / -0.146 | 0 | MATCH |
| `ETH` | `15m` | `buy` | `HTF against` | `488 \| 250 \| +0.290 (4.1) \| +0.007 (0.1) \| -0.085 \| -0.125` | `dev_cells.csv:94`: n=488, days=250, unm=+0.290 (4.1), match=+0.007 (0.1), net=-0.085 / -0.125 | 0 | MATCH |
| `ETH` | `15m` | `buy` | `prior_trend` | `269 \| 137 \| +0.210 (2.6) \| -0.078 (-1.1) \| -0.025 \| -0.065` | `dev_cells.csv:98`: n=269, days=137, unm=+0.210 (2.6), match=-0.078 (-1.1), net=-0.025 / -0.065 | 0 | MATCH |
| `POOL` | `1m` | `buy` | `HTF all` | `32045 \| 1824 \| +0.014 (4.8) \| -0.014 (-8.3) \| -0.102 \| -0.142` | `dev_cells.csv:110`: n=32045, days=1824, unm=+0.014 (4.8), match=-0.014 (-8.3), net=-0.102 / -0.142 | 0 | MATCH |
| `POOL` | `1m` | `sell` | `HTF all` | `53138 \| 1824 \| -0.008 (-3.7) \| -0.016 (-15.5) \| -0.102 \| -0.142` | `dev_cells.csv:119`: n=53138, days=1824, unm=-0.008 (-3.7), match=-0.016 (-15.5), net=-0.102 / -0.142 | 0 | MATCH |
| `POOL` | `5m` | `buy` | `HTF against` | `2948 \| 803 \| +0.117 (6.4) \| -0.023 (-1.7) \| -0.104 \| -0.144` | `dev_cells.csv:130`: n=2948, days=803, unm=+0.117 (6.4), match=-0.023 (-1.7), net=-0.104 / -0.144 | 0 | MATCH |
| `POOL` | `5m` | `buy` | `prior_trend` | `1498 \| 419 \| +0.131 (5.2) \| -0.017 (-0.9) \| -0.086 \| -0.126` | `dev_cells.csv:134`: n=1498, days=419, unm=+0.131 (5.2), match=-0.017 (-0.9), net=-0.086 / -0.126 | 0 | MATCH |
| `POOL` | `5m` | `sell` | `HTF all` | `10277 \| 1807 \| -0.024 (-3.8) \| -0.046 (-9.9) \| -0.103 \| -0.143` | `dev_cells.csv:137`: n=10277, days=1807, unm=-0.024 (-3.8), match=-0.046 (-9.9), net=-0.103 / -0.143 | 0 | MATCH |
| `POOL` | `15m` | `buy` | `HTF all` | `1906 \| 1003 \| +0.063 (2.4) \| -0.080 (-3.5) \| -0.092 \| -0.132` | `dev_cells.csv:146`: n=1906, days=1003, unm=+0.063 (2.4), match=-0.080 (-3.5), net=-0.092 / -0.132 | 0 | MATCH |
| `POOL` | `15m` | `buy` | `HTF with` | `942 \| 497 \| -0.130 (-6.4) \| -0.175 (-9.7) \| -0.101 \| -0.141` | `dev_cells.csv:147`: n=942, days=497, unm=-0.130 (-6.4), match=-0.175 (-9.7), net=-0.101 / -0.141 | 0 | MATCH |
| `POOL` | `15m` | `sell` | `HTF all` | `3336 \| 1391 \| -0.012 (-0.7) \| -0.052 (-3.7) \| -0.094 \| -0.134` | `dev_cells.csv:155`: n=3336, days=1391, unm=-0.012 (-0.7), match=-0.052 (-3.7), net=-0.094 / -0.134 | 0 | MATCH |

VERDICT: MATCH
