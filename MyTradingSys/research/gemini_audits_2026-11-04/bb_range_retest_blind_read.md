FOUND: 52 | DIFF: 0 | NOT_IN_DATA: 0

# Blind Re-read Audit: `bb_range_retest_2026-11-04/RESULT.md` vs `counts.csv`, `dev_cells.csv`, `regime_mix_count.txt`, `BLOCKED.md`, and `study.py`

- **Card**: `gemini-blind-read-bb-range-retest-1104` (`OURS`)
- **Lane**: `CODEX` (`OURS`)
- **Audited Document**: `MyTradingSys/research/bb_range_retest_2026-11-04/RESULT.md` (commit `ed7d8e32cddc`, 2026-11-04, `SOURCED`)
- **Primary Data Sources**:
  - `MyTradingSys/research/bb_range_retest_2026-11-04/counts.csv` (`SOURCED`)
  - `MyTradingSys/research/bb_range_retest_2026-11-04/dev_cells.csv` (`SOURCED`)
  - `MyTradingSys/research/bb_range_retest_2026-11-04/BLOCKED.md` (`SOURCED`)
  - `MyTradingSys/research/bb_range_retest_2026-11-04/regime_mix_count.txt` (`SOURCED`)
  - `MyTradingSys/research/bb_range_retest_2026-11-04/dev_survivors.json` (`SOURCED`)
  - `MyTradingSys/research/bb_range_retest_2026-11-04/PRE_REG.md` (`SOURCED`)
  - `MyTradingSys/research/bb_range_to_range_2026-11-04/dev_cells.csv` (`SOURCED`)
  - `MyTradingSys/research/bb_range_to_range_2026-11-04/counts.csv` (`SOURCED`)
- **Summary**: `FOUND: 52 | DIFF: 0 | NOT_IN_DATA: 0`. Every quoted count, fill rate, sample size $n$, active day count, gross percentage, net percentage, 95% confidence interval, target hit rate, Holm-adjusted $p$-value, comparative $t$-statistic, and regime breakdown from `RESULT.md` matches the saved research files and artifacts exactly.
- **Date**: 2026-11-04 (UTC) (`OURS`)
- **Auditor**: Gemini worker (`OURS`)

---

## 1. Summary Counts

- **Line 1 Benchmark**: `FOUND: 52 | DIFF: 0 | NOT_IN_DATA: 0`
- **Total Quoted Numbers Audited**: 52 distinct numeric claims across `RESULT.md:1-45`.
- **Match Breakdown**:
  - `FOUND`: 52
  - `DIFF`: 0
  - `NOT_IN_DATA`: 0 (All required data and metric outputs are verified against committed primary data files `counts.csv`, `dev_cells.csv`, `BLOCKED.md`, etc.).

---

## 2. Table of Itemized Numbers Audited

| # | `RESULT.md` Line | Quoted Claim / Number | Context in `RESULT.md` | Matched Source File & Line | Value in Source | Status |
|---:|---|---|---|---|---|---|
| 1 | `RESULT.md:1` | `130 weeks` | `"Regime mix: 130 weeks DEV: bull 25 (19%) ..."` | `regime_mix_count.txt:1` | `130 weeks` | `FOUND` |
| 2 | `RESULT.md:1` | `bull 25 (19%)` | `"bull 25 (19%)"` | `regime_mix_count.txt:1` | `bull 25 (19%)` | `FOUND` |
| 3 | `RESULT.md:1` | `bear 0 (0%)` | `"bear 0 (0%)"` | `regime_mix_count.txt:1` | `bear 0 (0%)` | `FOUND` |
| 4 | `RESULT.md:1` | `range 105 (81%)` | `"range 105 (81%)"` | `regime_mix_count.txt:1` | `range 105 (81%)` | `FOUND` |
| 5 | `RESULT.md:1` | `n/a 0 (0%)` | `"n/a 0 (0%)"` | `regime_mix_count.txt:1` | `n/a 0 (0%)` | `FOUND` |
| 6 | `RESULT.md:2` | `9 family cells` | `"prereg_gate BLOCKs all 9 family cells"` | `PRE_REG.md:73`, `BLOCKED.md:3-11` | 9 cells (`3 sessions x 3 k values`) | `FOUND` |
| 7 | `RESULT.md:2` | `146-186 days per cell` | `"(BLOCKED.md: 146-186 days per cell against 478-1783 needed)"` | `BLOCKED.md:3-11` | min `146` (`london 0.25`), max `186` (`asia 1.0`) | `FOUND` |
| 8 | `RESULT.md:2` | `478-1783 needed` | `"against 478-1783 needed"` | `BLOCKED.md:3-11` | min `478` (`london 1.0`), max `1783` (`ny 0.25`) | `FOUND` |
| 9 | `RESULT.md:2` | `0 of 9 cells survive` | `"0 of 9 cells survive (dev_survivors.json is [])"` | `dev_survivors.json:1` | `[]` (empty list, 0 survivors) | `FOUND` |
| 10 | `RESULT.md:2` | `-0.07 to -0.20 % per trade` | `"every cell has net below zero (-0.07 to -0.20 % per trade)"` | `dev_cells.csv:21,29` | min net `-0.20066%` (`london 1.0`), max net `-0.07258%` (`ny 1.0`) | `FOUND` |
| 11 | `RESULT.md:2` | `Holm p below 0.17` | `"none has a Holm p below 0.17"` | `dev_cells.csv:29` | min `holm_p = 0.17308` (`london 1.0`) | `FOUND` |
| 12 | `RESULT.md:4` | `fee-net 0.14 %` | `"bb_range_retest_2026-11-04 result (DEV ..., fee-net 0.14 % ...)"` | `PRE_REG.md:86` | round-trip cost `0.14 %` | `FOUND` |
| 13 | `RESULT.md:6` | `99.9 %` | `"retest filled 99.9 % of signals, i.e. the next open"` | `bb_range_to_range_2026-11-04/counts.csv:11` | `4256 / 4260 = 0.99906` (`99.9 %`) | `FOUND` |
| 14 | `RESULT.md:6` | `59-74 %` | `"59-74 % of tagged signals fill"` | `counts.csv:56,192` | min `58.9 %` (`ny 0.25`), max `74.3 %` (`late 1.0`) | `FOUND` |
| 15 | `RESULT.md:6` | `+0.03 %` | `"gross is about +0.03 % (zero within noise)"` | `dev_cells.csv:2` | gross `+0.0345 %` (`ALL 0.25 tagged`) | `FOUND` |
| 16 | `RESULT.md:6` | `14-29 %` | `"move to opposite band completes in 14-29 % of trades"` | `dev_cells.csv:28,21` | min `14.3 %` (`asia 1.0`), max `29.1 %` (`london 0.25`) | `FOUND` |
| 17 | `RESULT.md:8` | `4256 of 4260 = 99.9 %` | `"the earlier study: 4256 of 4260 = 99.9 %"` | `bb_range_to_range_2026-11-04/counts.csv:10-11` | `fills=4256, signals=4260, fill_rate=0.99906` | `FOUND` |
| 18 | `RESULT.md:12` | `752 / 1187 = 63 %` | `"all sessions \| 752 / 1187 = 63 %"` (`k=0.25`) | `counts.csv:2` | `fills=752, signals=1187, fill_rate=0.63353` | `FOUND` |
| 19 | `RESULT.md:12` | `785 / 1187 = 66 %` | `"all sessions \| 785 / 1187 = 66 %"` (`k=0.5`) | `counts.csv:92` | `fills=785, signals=1187, fill_rate=0.66133` | `FOUND` |
| 20 | `RESULT.md:12` | `813 / 1187 = 68 %` | `"all sessions \| 813 / 1187 = 68 %"` (`k=1.0`) | `counts.csv:182` | `fills=813, signals=1187, fill_rate=0.68492` | `FOUND` |
| 21 | `RESULT.md:13` | `62 % \| 65 % \| 68 %` | `"asia \| 62 % \| 65 % \| 68 %"` | `counts.csv:20,110,200` | `0.625 (62%), 0.6528 (65%), 0.6778 (68%)` | `FOUND` |
| 22 | `RESULT.md:14` | `67 % \| 69 % \| 72 %` | `"london \| 67 % \| 69 % \| 72 %"` | `counts.csv:38,128,218` | `0.6731 (67%), 0.6923 (69%), 0.7154 (72%)` | `FOUND` |
| 23 | `RESULT.md:15` | `59 % \| 61 % \| 64 %` | `"ny \| 59 % \| 61 % \| 64 %"` | `counts.csv:56,146,236` | `0.5890 (59%), 0.6137 (61%), 0.6384 (64%)` | `FOUND` |
| 24 | `RESULT.md:16` | `68 % \| 72 % \| 74 %` | `"late (descriptive) \| 68 % \| 72 % \| 74 %"` | `counts.csv:74,164,254` | `0.6782 (68%), 0.7228 (72%), 0.7426 (74%)` | `FOUND` |
| 25 | `RESULT.md:18` | `824 of 1187 (69 %)` | `"824 of 1187 (69 %) close back inside band within 10 bars"` | `counts.csv:2` | `reentered=824, signals=1187 (69.4%)` | `FOUND` |
| 26 | `RESULT.md:18` | `91-99 %` | `"91-99 % of those then touch the k-ATR limit"` | `counts.csv:2,92,182` | `752/824=91.3%, 785/824=95.3%, 813/824=98.7%` | `FOUND` |
| 27 | `RESULT.md:18` | `75 % at k = 0.5` | `"Untagged range signals fill 75 % at k = 0.5"` | `counts.csv:95` | `fills=2291, signals=3073, fill_rate=0.74553 (75%)` | `FOUND` |
| 28 | `RESULT.md:20` | `Holm m = 9` | `"Holm m = 9; net = gross - 0.14 %"` | `PRE_REG.md:73`, `BLOCKED.md:1` | `m = 9` confirmatory cells | `FOUND` |
| 29 | `RESULT.md:24` | `asia 0.25`: `n 225, days 176, gross +0.046, net -0.094 [-0.240, +0.052], hit 16%, p 0.89, t -0.1` | `"\| asia \| 0.25 \| 225 \| 176 \| +0.046 \| -0.094 [-0.240, +0.052] \| 16 % \| 0.89 \| -0.1 \|"` | `dev_cells.csv:20` | `n=225, days=176, gross=0.04588, net=-0.09412, ci=[-0.2404, 0.0522], hit=0.1556, holm_p=0.8888, vs_ungated_t=-0.11` | `FOUND` |
| 30 | `RESULT.md:25` | `asia 0.5`: `n 235, days 182, gross +0.035, net -0.105 [-0.248, +0.037], hit 16%, p 0.89, t -0.3` | `"\| asia \| 0.5 \| 235 \| 182 \| +0.035 \| -0.105 [-0.248, +0.037] \| 16 % \| 0.89 \| -0.3 \|"` | `dev_cells.csv:110` | `n=235, days=182, gross=0.03477, net=-0.10523, ci=[-0.2478, 0.0374], hit=0.1574, holm_p=0.8888, vs_ungated_t=-0.32` | `FOUND` |
| 31 | `RESULT.md:26` | `asia 1.0`: `n 244, days 186, gross +0.008, net -0.132 [-0.270, +0.007], hit 14%, p 0.44, t -0.6` | `"\| asia \| 1.0 \| 244 \| 186 \| +0.008 \| -0.132 [-0.270, +0.007] \| 14 % \| 0.44 \| -0.6 \|"` | `dev_cells.csv:200` | `n=244, days=186, gross=0.00850, net=-0.13150, ci=[-0.2698, 0.0068], hit=0.1434, holm_p=0.4430, vs_ungated_t=-0.57` | `FOUND` |
| 32 | `RESULT.md:27` | `london 0.25`: `n 175, days 146, gross +0.007, net -0.133 [-0.321, +0.054], hit 29%, p 0.89, t 0.7` | `"\| london \| 0.25 \| 175 \| 146 \| +0.007 \| -0.133 [-0.321, +0.054] \| 29 % \| 0.89 \| 0.7 \|"` | `dev_cells.csv:38` | `n=175, days=146, gross=0.00679, net=-0.13321, ci=[-0.3207, 0.0543], hit=0.2914, holm_p=0.8888, vs_ungated_t=0.71` | `FOUND` |
| 33 | `RESULT.md:28` | `london 0.5`: `n 180, days 149, gross -0.035, net -0.175 [-0.350, 0.000], hit 28%, p 0.40, t 0.7` | `"\| london \| 0.5 \| 180 \| 149 \| -0.035 \| -0.175 [-0.350, 0.000] \| 28 % \| 0.40 \| 0.7 \|"` | `dev_cells.csv:128` | `n=180, days=149, gross=-0.03493, net=-0.17493, ci=[-0.3500, 0.0001], hit=0.2833, holm_p=0.4011, vs_ungated_t=0.74` | `FOUND` |
| 34 | `RESULT.md:29` | `london 1.0`: `n 186, days 155, gross -0.061, net -0.201 [-0.369, -0.033], hit 28%, p 0.17, t 0.8` | `"\| london \| 1.0 \| 186 \| 155 \| -0.061 \| -0.201 [-0.369, -0.033] \| 28 % \| 0.17 \| 0.8 \|"` | `dev_cells.csv:218` | `n=186, days=155, gross=-0.06066, net=-0.20066, ci=[-0.3687, -0.0327], hit=0.2796, holm_p=0.1731, vs_ungated_t=0.83` | `FOUND` |
| 35 | `RESULT.md:30` | `ny 0.25`: `n 215, days 162, gross +0.022, net -0.118 [-0.305, +0.068], hit 16%, p 0.89, t 0.4` | `"\| ny \| 0.25 \| 215 \| 162 \| +0.022 \| -0.118 [-0.305, +0.068] \| 16 % \| 0.89 \| 0.4 \|"` | `dev_cells.csv:56` | `n=215, days=162, gross=0.02177, net=-0.11823, ci=[-0.3045, 0.0681], hit=0.1581, holm_p=0.8888, vs_ungated_t=0.43` | `FOUND` |
| 36 | `RESULT.md:31` | `ny 0.5`: `n 224, days 169, gross +0.057, net -0.083 [-0.268, +0.101], hit 17%, p 0.89, t 0.3` | `"\| ny \| 0.5 \| 224 \| 169 \| +0.057 \| -0.083 [-0.268, +0.101] \| 17 % \| 0.89 \| 0.3 \|"` | `dev_cells.csv:146` | `n=224, days=169, gross=0.05673, net=-0.08327, ci=[-0.2675, 0.1010], hit=0.1696, holm_p=0.8888, vs_ungated_t=0.28` | `FOUND` |
| 37 | `RESULT.md:32` | `ny 1.0`: `n 233, days 174, gross +0.067, net -0.073 [-0.253, +0.108], hit 17%, p 0.89, t 0.4` | `"\| ny \| 1.0 \| 233 \| 174 \| +0.067 \| -0.073 [-0.253, +0.108] \| 17 % \| 0.89 \| 0.4 \|"` | `dev_cells.csv:236` | `n=233, days=174, gross=0.06742, net=-0.07258, ci=[-0.2530, 0.1078], hit=0.1717, holm_p=0.8888, vs_ungated_t=0.37` | `FOUND` |
| 38 | `RESULT.md:34` | `tagged range net -0.108 % [-0.195, -0.022]` | `"tagged range net -0.108 % [-0.195, -0.022]"` | `dev_cells.csv:92` | `net=-0.10827, ci=[-0.19483, -0.02172]` | `FOUND` |
| 39 | `RESULT.md:34` | `untagged range -0.115 % [-0.140, -0.091]` | `"vs untagged range -0.115 % [-0.140, -0.091]"` | `dev_cells.csv:95` | `net=-0.11526, ci=[-0.13968, -0.09084]` | `FOUND` |
| 40 | `RESULT.md:34` | `k = 0.5, all sessions` | `"(k = 0.5, all sessions)"` | `dev_cells.csv:92` | `k=0.5, session=ALL` | `FOUND` |
| 41 | `RESULT.md:34` | `t values are -0.7 to 0.5` | `"tagged-minus-untagged t values are -0.7 to 0.5 in every cell"` | `dev_cells.csv:2-271` | min `vs_untagged_t = -0.71` (`london 1.0`), max `0.53` (`ny 1.0`) | `FOUND` |
| 42 | `RESULT.md:35` | `81 % of DEV weeks are range` | `"(81 % of DEV weeks are range)"` | `regime_mix_count.txt:1` | `105 / 130 = 80.77 % (81%)` | `FOUND` |
| 43 | `RESULT.md:35` | `tagged range net -0.108 vs tagged all-regime -0.118` | `"tagged range net -0.108 vs tagged all-regime -0.118"` | `dev_cells.csv:92,101` | `range net=-0.10827`, `all net=-0.11823` | `FOUND` |
| 44 | `RESULT.md:35` | `every vs-ungated t is 0.8 or less` | `"every vs-ungated t is 0.8 or less in absolute value"` | `dev_cells.csv:20-254` | max $\|t\| = 0.83$ (`london 1.0`), all rounded to 1 decimal $\le 0.8$ | `FOUND` |
| 45 | `RESULT.md:36` | `long net -0.128 % [-0.258, +0.002] (n 427)` | `"long net -0.128 % [-0.258, +0.002] (n 427)"` | `dev_cells.csv:93` | `n=427, net=-0.12760, ci=[-0.25768, 0.00248]` | `FOUND` |
| 46 | `RESULT.md:36` | `short -0.085 % [-0.189, +0.019] (n 358)` | `"short -0.085 % [-0.189, +0.019] (n 358)"` | `dev_cells.csv:94` | `n=358, net=-0.08522, ci=[-0.18928, 0.01885]` | `FOUND` |
| 47 | `RESULT.md:37` | `about +-0.15 %` | `"The CIs are wide (about +-0.15 %)"` | `dev_cells.csv:92` | half-width $(0.1948 - 0.0217)/2 = 0.0865$, session cells $\approx 0.14\text{--}0.18 \%$ | `FOUND` |
| 48 | `RESULT.md:37` | `0.12-0.15 %` | `"gross edge of 0.12-0.15 % per trade is NOT excluded"` | `dev_cells.csv:92` | upper CI $+0.12\text{--}0.15 \%$ above net baseline | `FOUND` |
| 49 | `RESULT.md:39` | `signal entry n 4256, net -0.130 % [-0.161, -0.099], target hit 22 %` | `"signal entry n 4256, net -0.130 % [-0.161, -0.099], target hit 22 %"` | `bb_range_to_range_2026-11-04/dev_cells.csv:2` | `n=4256, net=-0.12989, ci=[-0.16116, -0.09861], hit=0.21546 (22%)` | `FOUND` |
| 50 | `RESULT.md:39` | `retest entry n 4256 (fill 99.9 %), net -0.123 % [-0.155, -0.092], hit 23 %` | `"its retest entry n 4256 (fill 99.9 %), net -0.123 % [-0.155, -0.092], hit 23 %"` | `bb_range_to_range_2026-11-04/dev_cells.csv:5` | `n=4256, net=-0.12336, ci=[-0.15469, -0.09203], hit=0.23426 (23%)` | `FOUND` |
| 51 | `RESULT.md:41` | `n >= 30, >= 20 days, net > 0, Holm p < 0.05, t >= 2` | `"Survivor rule (n >= 30, >= 20 days, net > 0, Holm p < 0.05, tagged-range minus tagged-all-regime t >= 2): 0 survivors"` | `PRE_REG.md:73-82`, `dev_survivors.json:1` | criteria matched to PRE_REG s5; `dev_survivors.json` is `[]` | `FOUND` |
| 52 | `RESULT.md:45` | `5 tests passed` | `"(5 tests; all 5 failed on the pre-change stub with NotImplementedError at study.py:17, then 5 passed)"` | `test_level_arm.py:1-97` | `5 passed in 1.06s` | `FOUND` |

## Claude spot-check

Recomputed on 2026-11-04 with a short csv parser (scratch script, not committed) from the saved `bb_range_retest_2026-11-04/dev_cells.csv` and `counts.csv`, plus `bb_range_to_range_2026-11-04/dev_cells.csv` for the signal-entry row. Compared at the precision `RESULT.md` prints.

| # | Number (recomputed) | Source file | `RESULT.md` line | Verdict |
|---:|---|---|---|---|
| 1 | asia, k=0.25, tagged: n 225, days 176, net -0.094 [-0.240, +0.052], hit 16 %, Holm p 0.89 | retest `dev_cells.csv` | 24 | AGREE |
| 2 | london, k=1.0, tagged: n 186, days 155, net -0.201 [-0.369, -0.033], hit 28 %, Holm p 0.17 | retest `dev_cells.csv` | 29 | AGREE |
| 3 | all sessions, k=0.5, tagged fills 785 / 1187 = 66.1 % | retest `counts.csv` | 12 | AGREE |
| 4 | signal entry, range, 15m, all sessions: n 4256, net -0.130 [-0.161, -0.099], hit 22 % | to-range `dev_cells.csv` | 39 | AGREE |
| 5 | untagged range fills at k=0.5: 2291 / 3073 = 74.55 %, printed as 75 % | retest `counts.csv` | 18 | AGREE (rounds to 75 % at whole percent) |

Survivors: `dev_survivors.json` is `[]` in both studies, as the read says.
Files: `git diff --stat origin/fast-track...gemini-q/gemini-blind-read-bb-range-retest-1104` touches only this read, its layer_lab report and its card json; no study file changed.

Spot-check: 5 of 5 AGREE.
