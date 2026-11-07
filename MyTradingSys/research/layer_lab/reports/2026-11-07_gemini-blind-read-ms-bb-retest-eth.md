# Blind Read Audit: `gemini-blind-read-ms-bb-retest-eth`

- **Card**: `gemini-blind-read-ms-bb-retest-eth`
- **Date**: 2026-11-07 UTC
- **Reader**: Gemini (independent blind read worker, JIS-NUC)
- **Target Study**: `MyTradingSys/research/bb_range_retest_eth_pool_2026-11/RESULT.md`
- **Raw Data / CSV Inputs Read Before RESULT.md**:
  - `MyTradingSys/research/bb_range_retest_eth_pool_2026-11/counts.csv` (810 rows)
  - `MyTradingSys/research/bb_range_retest_eth_pool_2026-11/dev_cells.csv` (810 rows)
  - `MyTradingSys/research/bb_range_retest_eth_pool_2026-11/dev_survivors.json`
  - `MyTradingSys/research/bb_range_retest_eth_pool_2026-11/regime_mix_dev.txt`
  - `MyTradingSys/research/bb_range_retest_eth_pool_2026-11/regime_mix_count.txt`
  - `MyTradingSys/research/bb_range_retest_eth_pool_2026-11/BLOCKED.md`
- **Audit Detail Reference**: `MyTradingSys/research/gemini_audits_2026-11-05/BLIND_READ_MS_BB_RETEST_ETH.md`
- **Verification Command**:
  `python -c "import pathlib; p=pathlib.Path('MyTradingSys/research/layer_lab/reports/2026-11-07_gemini-blind-read-ms-bb-retest-eth.md'); assert p.exists() and 'VERDICT' in p.read_text()"`

---

## 1. Regime Mix & Survivors Verification

### Regime Mix Check (`regime_mix_dev.txt` & `regime_mix_count.txt` vs `RESULT.md:1`)
- OURS `regime_mix_dev.txt:1`: `BTCUSDT 130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)`
- OURS `regime_mix_dev.txt:2`: `ETHUSDT 130 weeks: bull 11 (8%) | bear 0 (0%) | range 119 (92%) | n/a 0 (0%)`
- OURS `regime_mix_dev.txt:3`: `POOL 260 weeks: bull 36 (14%) | bear 0 (0%) | range 224 (86%) | n/a 0 (0%)`
- SOURCED `RESULT.md:1`: `"Regime mix: POOL 260 weeks DEV: bull 36 (14%) | bear 0 (0%) | range 224 (86%) | n/a 0 (0%) (BTCUSDT bull 19% / range 81%; ETHUSDT bull 8% / range 92%)"`
- Diff: 0
- Status: MATCH

### Survivors Check (`dev_survivors.json:1` vs `RESULT.md:2`)
- OURS `dev_survivors.json:1`: `[]` (0 surviving cells)
- SOURCED `RESULT.md:2`: `"0 of 9 cells survive (dev_survivors.json is []); every pooled cell has net below zero at 0.14 % (-0.044 to -0.156 % per trade), lowest Holm p 0.19."`
- Diff: 0
- Status: MATCH

---

## 2. Table 1 Verification: BTC Reproduction Row (`RESULT.md:14-16` vs `dev_cells.csv`)

| Cell (range, tagged, sides both) | SOURCED `RESULT.md:14-16` (`this run futures n / net %`) | OURS `dev_cells.csv` (`n / net %`) | Diff | Status |
|---|---|---|---|---|
| `asia 0.25 / 0.5 / 1.0` | `222 / 232 / 241; -0.087 / -0.093 / -0.121` (`RESULT.md:14`) | Row 19: n=222, net=-0.0869%<br>Row 109: n=232, net=-0.0934%<br>Row 199: n=241, net=-0.1209% | 0 | MATCH |
| `london 0.25 / 0.5 / 1.0` | `174 / 179 / 185; -0.126 / -0.168 / -0.195` (`RESULT.md:15`) | Row 37: n=174, net=-0.1260%<br>Row 127: n=179, net=-0.1684%<br>Row 217: n=185, net=-0.1945% | 0 | MATCH |
| `ny 0.25 / 0.5 / 1.0` | `209 / 217 / 226; -0.127 / -0.105 / -0.091` (`RESULT.md:16`) | Row 55: n=209, net=-0.1269%<br>Row 145: n=217, net=-0.1047%<br>Row 235: n=226, net=-0.0912% | 0 | MATCH |

---

## 3. Table 2 Verification: Confirmatory Family POOL (`RESULT.md:24-32` vs `dev_cells.csv`)

Conditions: `symbol == 'POOL'`, `gate == 'range'`, `tag == 'tagged'`, `side == 'both'` (15m, cluster = symbol-day, Holm m = 9).

| Session | $k$ | Row | Metric | SOURCED `RESULT.md:24-32` | OURS `dev_cells.csv` | Diff | Status |
|---|---|---|---|---|---|---|---|
| `asia` | 0.25 | 559 | n, days, fill, gross, net@0.14, net@0.10, hit, Holm p, vs_ungated t | `472 \| 363 \| 63 % \| +0.070 \| -0.070 [-0.200, +0.060] \| -0.030 [-0.160, +0.100] \| 18 % \| 1.00 \| -0.8` | n=472, days=363, fill=63.27%, gross=+0.0702%, net=-0.0698% [-0.1997, +0.0601], net_bin=-0.0298% [-0.1597, +0.1001], hit=18.01%, holm_p=1.00, vs_ungated_t=-0.806 | 0 | MATCH |
| `asia` | 0.5 | 649 | n, days, fill, gross, net@0.14, net@0.10, hit, Holm p, vs_ungated t | `495 \| 376 \| 66 % \| +0.058 \| -0.082 [-0.206, +0.043] \| -0.042 [-0.166, +0.083] \| 19 % \| 0.99 \| -1.2` | n=495, days=376, fill=66.35%, gross=+0.0585%, net=-0.0815% [-0.2056, +0.0426], net_bin=-0.0415% [-0.1656, +0.0826], hit=18.59%, holm_p=0.9901, vs_ungated_t=-1.155 | 0 | MATCH |
| `asia` | 1.0 | 739 | n, days, fill, gross, net@0.14, net@0.10, hit, Holm p, vs_ungated t | `512 \| 385 \| 69 % \| +0.050 \| -0.090 [-0.211, +0.030] \| -0.050 [-0.171, +0.070] \| 18 % \| 0.86 \| -1.1` | n=512, days=385, fill=68.63%, gross=+0.0499%, net=-0.0901% [-0.2105, +0.0302], net_bin=-0.0501% [-0.1705, +0.0702], hit=18.36%, holm_p=0.8593, vs_ungated_t=-1.137 | 0 | MATCH |
| `london` | 0.25 | 577 | n, days, fill, gross, net@0.14, net@0.10, hit, Holm p, vs_ungated t | `351 \| 300 \| 64 % \| +0.026 \| -0.114 [-0.260, +0.031] \| -0.074 [-0.220, +0.071] \| 29 % \| 0.86 \| 0.6` | n=351, days=300, fill=63.70%, gross=+0.0257%, net=-0.1143% [-0.2595, +0.0309], net_bin=-0.0743% [-0.2195, +0.0709], hit=29.06%, holm_p=0.8593, vs_ungated_t=0.649 | 0 | MATCH |
| `london` | 0.5 | 667 | n, days, fill, gross, net@0.14, net@0.10, hit, Holm p, vs_ungated t | `364 \| 310 \| 66 % \| -0.005 \| -0.145 [-0.281, -0.009] \| -0.105 [-0.241, +0.031] \| 29 % \| 0.29 \| 1.2` | n=364, days=310, fill=66.06%, gross=-0.0050%, net=-0.1450% [-0.2812, -0.0088], net_bin=-0.1050% [-0.2412, +0.0312], hit=28.57%, holm_p=0.2949, vs_ungated_t=1.152 | 0 | MATCH |
| `london` | 1.0 | 757 | n, days, fill, gross, net@0.14, net@0.10, hit, Holm p, vs_ungated t | `374 \| 317 \| 68 % \| -0.016 \| -0.156 [-0.288, -0.024] \| -0.116 [-0.248, +0.016] \| 29 % \| 0.19 \| 1.3` | n=374, days=317, fill=67.88%, gross=-0.0158%, net=-0.1558% [-0.2878, -0.0237], net_bin=-0.1158% [-0.2478, +0.0163], hit=28.61%, holm_p=0.1869, vs_ungated_t=1.267 | 0 | MATCH |
| `ny` | 0.25 | 595 | n, days, fill, gross, net@0.14, net@0.10, hit, Holm p, vs_ungated t | `439 \| 339 \| 59 % \| +0.072 \| -0.068 [-0.213, +0.078] \| -0.028 [-0.173, +0.118] \| 18 % \| 1.00 \| 1.0` | n=439, days=339, fill=58.93%, gross=+0.0724%, net=-0.0676% [-0.2135, +0.0782], net_bin=-0.0276% [-0.1735, +0.1182], hit=17.77%, holm_p=1.00, vs_ungated_t=1.000 | 0 | MATCH |
| `ny` | 0.5 | 685 | n, days, fill, gross, net@0.14, net@0.10, hit, Holm p, vs_ungated t | `458 \| 352 \| 61 % \| +0.096 \| -0.044 [-0.185, +0.097] \| -0.004 [-0.145, +0.137] \| 19 % \| 1.00 \| 0.7` | n=458, days=352, fill=61.48%, gross=+0.0961%, net=-0.0439% [-0.1846, +0.0968], net_bin=-0.0039% [-0.1446, +0.1368], hit=18.78%, holm_p=1.00, vs_ungated_t=0.749 | 0 | MATCH |
| `ny` | 1.0 | 775 | n, days, fill, gross, net@0.14, net@0.10, hit, Holm p, vs_ungated t | `472 \| 361 \| 63 % \| +0.084 \| -0.056 [-0.196, +0.084] \| -0.016 [-0.156, +0.124] \| 19 % \| 1.00 \| 0.2` | n=472, days=361, fill=63.36%, gross=+0.0839%, net=-0.0561% [-0.1957, +0.0835], net_bin=-0.0161% [-0.1557, +0.1235], hit=19.28%, holm_p=1.00, vs_ungated_t=0.215 | 0 | MATCH |

---

## 4. Table 3 Verification: Per Symbol Descriptive Table (`RESULT.md:38-40` vs `dev_cells.csv`)

| Symbol | SOURCED `RESULT.md:38-40` | OURS `dev_cells.csv` Recomputation | Diff | Status |
|---|---|---|---|---|
| `BTCUSDT` | net % range: `-0.087 to -0.195`<br>days per cell: `145-184`<br>lowest Holm p: `0.21`<br>ALL k=0.5: `771, -0.109 [-0.197, -0.022]` (`L38`) | 9-cell net range: `[-0.1945%, -0.0869%]`<br>days range: `[145, 184]`<br>min holm_p: `0.2131`<br>Row 91 (ALL k=0.5): n=771, net=-0.1094% [-0.1968, -0.0220] | 0 | MATCH |
| `ETHUSDT` | net % range: `-0.122 to +0.011`<br>days per cell: `155-201`<br>lowest Holm p: `1.00`<br>ALL k=0.5: `865, -0.115 [-0.214, -0.015]` (`L39`) | 9-cell net range: `[-0.1224%, +0.0109%]`<br>days range: `[155, 201]`<br>min holm_p: `1.0000`<br>Row 361 (ALL k=0.5): n=865, net=-0.1148% [-0.2143, -0.0153] | 0 | MATCH |
| `POOL` | net % range: `-0.044 to -0.156`<br>days per cell: `300-385`<br>lowest Holm p: `0.19`<br>ALL k=0.5: `1636, -0.112 [-0.179, -0.045]` (`L40`) | 9-cell net range: `[-0.1558%, -0.0439%]`<br>days range: `[300, 385]`<br>min holm_p: `0.1869`<br>Row 631 (ALL k=0.5): n=1636, net=-0.1122% [-0.1791, -0.0454] (net_bin=-0.0722% [-0.1391, -0.0054]) | 0 | MATCH |

---

## 5. Narrative Prose Claims Verification

1. **ETH ny positive cell claim** (`RESULT.md:7-8`):
   - SOURCED `RESULT.md:7-8`: `"ETH ny is the only cell with net >= 0 (k 0.5: +0.011 % [-0.197, +0.219], n 241), one of 27 per-symbol cells and far from significant (Holm p 1.0)."`
   - OURS `dev_cells.csv:415`: symbol=`ETHUSDT`, session=`ny`, k=`0.5`: n=241, net=+0.010881% [ci_lo=-0.196839%, ci_hi=+0.218601%], holm_p=1.0. All other 26 per-symbol cells have net < 0.
   - Status: MATCH.

2. **Pooled all sessions k=0.5 net claim** (`RESULT.md:42`):
   - SOURCED `RESULT.md:42`: `"Pooled all sessions (k 0.5): net -0.112 % [-0.179, -0.045] at 0.14 and -0.072 % [-0.139, -0.005] at 0.10: below zero at both costs."`
   - OURS `dev_cells.csv:631`: n=1636, net=-0.112247% [-0.179069%, -0.045425%], net_bin=-0.072247% [-0.139069%, -0.005425%].
   - Status: MATCH.

3. **Gate & Tag effect size claims** (`RESULT.md:43`):
   - SOURCED `RESULT.md:43`: `"The range gate does nothing measurable (pooled vs all-regime t -1.2 to 1.3); the session-range tag does nothing (vs untagged t -0.1 to 1.1)."`
   - OURS `dev_cells.csv`: Across the 9 POOL confirmatory cells, `vs_ungated_t` ranges from -1.155 to +1.267 (rounds to -1.2 to 1.3); `vs_untagged_t` ranges from -0.135 to +1.099 (rounds to -0.1 to 1.1).
   - Status: MATCH.

4. **Power Gate / Sample size required** (`RESULT.md:2` & `BLOCKED.md:3-11`):
   - SOURCED `RESULT.md:2`: `"prereg_gate still BLOCKs all 9 pooled family cells (BLOCKED.md: 600-1944 needed)."`
   - OURS `BLOCKED.md:3-11`: n needed ranges across the 9 cells from 600 (london 1.0) to 1944 (ny 0.25).
   - Status: MATCH.

---

## 6. Audit Verdict

Every single number across all 3 tables (Table 1 BTC reproduction, Table 2 POOL confirmatory, Table 3 Per-symbol descriptive) and all prose narrative claims in `MyTradingSys/research/bb_range_retest_eth_pool_2026-11/RESULT.md` matches the raw CSV outputs (`dev_cells.csv`, `counts.csv`, `regime_mix_dev.txt`, `regime_mix_count.txt`, `dev_survivors.json`, `BLOCKED.md`) exactly. Zero numerical or semantic discrepancies exist.

VERDICT: MATCH
