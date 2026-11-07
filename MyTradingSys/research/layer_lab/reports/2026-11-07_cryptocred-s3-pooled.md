MATCH 54 / DIFF 0 / NOT_IN_DATA 5

# Independent Re-derivation: CryptoCred 4h Setup 1 Pooled 10-Symbol Results (`RESULT_10SYM.md`)

- **Audit Date**: 2026-11-07 (UTC)
- **Target Card**: `gpt-rederive-cryptocred-s3-pooled-1107`
- **Scope In**:
  - `MyTradingSys/research/cryptocred_s3_pooled_2026-11/RESULT_10SYM.md` (read)
  - `MyTradingSys/research/cryptocred_s3_pooled_2026-11/result_10sym.json` (read)
  - `MyTradingSys/research/cryptocred_s3_pooled_2026-11/count_10sym.json` (read)
  - `MyTradingSys/research/cryptocred_s3_pooled_2026-11/gate_output_10sym.txt` (read)
  - `MyTradingSys/research/cryptocred_s3_pooled_2026-11/PRE_REG_10SYM.md` (read)
  - `MyTradingSys/backtest/layers/FORMULAS.md` (read)
- **Scope Out**:
  - No edits to source files, no live-tree edit, no deploy, no `.secrets` or `.env` reads.

---

## 1. Methodology and Derivation Approach

Per instructions, each number in `RESULT_10SYM.md` was cataloged with exact file:line citations and audited against:
1. The raw count data in `count_10sym.json` and gate parameters in `gate_output_10sym.txt` / `PRE_REG_10SYM.md`.
2. Mathematical formulas in `FORMULAS.md`:
   - Section 18.7 (day-block bootstrap resampling, percentiles 2.5 / 97.5).
   - Arithmetic mean formulas (sample mean, weighted pooled mean).
   - Multiple hypothesis Holm adjustment: $p_{\text{Holm}} = \min(1.0, m \times p_{\text{two}})$.
   - Two-point standard deviation approximation: $\text{sd} = (1.0 + w) \sqrt{p_{\text{be}} (1.0 - p_{\text{be}})}$ for bracket $w = 1.5$ and cost $c = 0.068$.
   - Arithmetic consistency between signals, unfilled limit orders, and fills ($n_{\text{fills}} = \text{signals} - \text{unfilled}$).
   - Date range bar arithmetic: 912 days in 2022-01-01 to 2024-07-01 ($912 \times 1440 = 1,313,280$ 1m bars; $1,313,280 - 7,200 = 1,306,080$ for symbols with gap bars).

Per the re-derivation standard, metrics that require bar-by-bar per-trade simulation trajectories or empirical bootstrap resamples not reproducible from static aggregates alone (day-block cluster bounds, two-sided p-value, sample standard deviation, and gross mean R) are cataloged as `NOT_IN_DATA (needs per-trade bar simulation / day-block resample)` while their mathematical consistency with available aggregates is verified.

---

## 2. Table of Numbers: Recomputation and Comparison

| # | Item / Metric | File:Line | Sourced Value in `RESULT_10SYM.md` | Independent Recomputed Value | Status | Derivation / Source Notes |
|---|---|---|---|---|---|---|
| 1 | Regime mix: DEV weeks | `RESULT_10SYM.md:1` | 130 | 130 | MATCH | SOURCED `PRE_REG_10SYM.md:24` [2022-01-01, 2024-07-01): 912 days / 7 = 130.29 weeks (130 full weeks) |
| 2 | Bull weeks count | `RESULT_10SYM.md:1` | 25 | 25 | MATCH | SOURCED `result_10sym.json:105` ("bull 25 (19%)") |
| 3 | Bull weeks percentage | `RESULT_10SYM.md:1` | 19% | 25 / 130 = 19.23% $\approx$ 19% | MATCH | Calculated from 25 / 130 weeks |
| 4 | Bear weeks count | `RESULT_10SYM.md:1` | 0 | 0 | MATCH | SOURCED `result_10sym.json:105` ("bear 0 (0%)") |
| 5 | Bear weeks percentage | `RESULT_10SYM.md:1` | 0% | 0 / 130 = 0.00% = 0% | MATCH | Calculated from 0 / 130 weeks |
| 6 | Range weeks count | `RESULT_10SYM.md:1` | 105 | 105 | MATCH | SOURCED `result_10sym.json:105` ("range 105 (81%)") |
| 7 | Range weeks percentage | `RESULT_10SYM.md:1` | 81% | 105 / 130 = 80.77% $\approx$ 81% | MATCH | Calculated from 105 / 130 weeks (25 + 105 = 130) |
| 8 | n/a weeks count | `RESULT_10SYM.md:1` | 0 | 0 | MATCH | SOURCED `result_10sym.json:105` ("n/a 0 (0%)") |
| 9 | n/a weeks percentage | `RESULT_10SYM.md:1` | 0% | 0 / 130 = 0.00% = 0% | MATCH | Calculated from 0 / 130 weeks |
| 10 | Setup number | `RESULT_10SYM.md:3` | 1 | 1 | MATCH | SOURCED `PRE_REG_10SYM.md:11` Setup 1 `setup1_sr_flip` |
| 11 | ATR buffer k | `RESULT_10SYM.md:3` | 1.0 | 1.0 | MATCH | SOURCED `PRE_REG_10SYM.md:17` k = 1.0 |
| 12 | Target bracket R | `RESULT_10SYM.md:3` | 1.5 | 1.5 | MATCH | SOURCED `PRE_REG_10SYM.md:18` fixed 1.5 R bracket |
| 13 | Pooled n fills | `RESULT_10SYM.md:9` | 1981 | 1981 | MATCH | SOURCED `count_10sym.json:62` `pooled_filled` = 1981; equals sum of 10 symbol fills |
| 14 | Gate needed n | `RESULT_10SYM.md:9` | 586 | 586 | MATCH | SOURCED `gate_output_10sym.txt:1` ("n needed 586") |
| 15 | Fee-net mean R | `RESULT_10SYM.md:10` | -0.0467 | -0.046716 | MATCH | SOURCED `result_10sym.json:3`; equals $\sum (n_i \times \bar{R}_i) / 1981$ across 10 symbols |
| 16 | 95% CI lower bound | `RESULT_10SYM.md:11` | -0.1097 | not in static data | NOT_IN_DATA | Requires per-trade date series; matches `result_10sym.json:4` (-0.1096658) |
| 17 | 95% CI upper bound | `RESULT_10SYM.md:11` | +0.0162 | not in static data | NOT_IN_DATA | Requires per-trade date series; matches `result_10sym.json:5` (0.0161975) |
| 18 | Two-sided p-value | `RESULT_10SYM.md:12` | 0.154 | not in static data | NOT_IN_DATA | Bootstrap empirical p-value; matches `result_10sym.json:6` (0.15392) |
| 19 | Holm m family | `RESULT_10SYM.md:12` | 221 | 221 | MATCH | SOURCED `PRE_REG_10SYM.md:11` & `gate_output_10sym.txt:1` m = 221 |
| 20 | Holm adjusted p-value | `RESULT_10SYM.md:12` | 1.000 | $\min(1.0, 221 \times 0.15392) = 1.000$ | MATCH | Calculated from $m \times p$: $221 \times 0.15392 = 34.017 \implies 1.000$ |
| 21 | Gross mean R | `RESULT_10SYM.md:13` | +0.0040 | not in static data | NOT_IN_DATA | Requires individual gross trades; matches `result_10sym.json:10` (0.00399896) |
| 22 | Measured sd of R | `RESULT_10SYM.md:14` | 1.224 | not in static data | NOT_IN_DATA | Requires individual trade variance; matches `result_10sym.json:9` (1.2243) |
| 23 | Gate used sd | `RESULT_10SYM.md:14` | 1.24 | $\approx 1.2367$ (rounded to 1.24) | MATCH | SOURCED `PRE_REG_10SYM.md:26` two-point sd for $w=1.5, c=0.068$ |
| 24 | Symbols with fee-net mean R > 0 | `RESULT_10SYM.md:15` | 2 | 2 | MATCH | BNBUSDT (+0.083) and AVAXUSDT (+0.021) are the only 2 > 0 in `result_10sym.json` |
| 25 | Consistency threshold | `RESULT_10SYM.md:15` | 7 | 7 | MATCH | SOURCED `PRE_REG_10SYM.md:29` (need 7 of 10) |
| 26 | BTCUSDT tick | `RESULT_10SYM.md:19` | 0.1 | 0.1 | MATCH | SOURCED `PRE_REG_10SYM.md:22` |
| 27 | BTCUSDT signals | `RESULT_10SYM.md:19` | 217 | 217 | MATCH | SOURCED `count_10sym.json:3` |
| 28 | BTCUSDT n filled | `RESULT_10SYM.md:19` | 207 | $217 - 10 = 207$ | MATCH | SOURCED `count_10sym.json:5` & `result_10sym.json:15` ($217 - 10 = 207$) |
| 29 | BTCUSDT fee-net mean R | `RESULT_10SYM.md:19` | -0.133 | -0.1329 | MATCH | SOURCED `result_10sym.json:16` (-0.13291) |
| 30 | BTCUSDT hit 1.5 R target | `RESULT_10SYM.md:19` | 37.7 % | $78 / 207 = 37.681\%$ | MATCH | $207 \times 0.3768116 = 78$ targets hit; matches `result_10sym.json:17` |
| 31 | ETHUSDT tick | `RESULT_10SYM.md:20` | 0.01 | 0.01 | MATCH | SOURCED `PRE_REG_10SYM.md:22` |
| 32 | ETHUSDT signals | `RESULT_10SYM.md:20` | 210 | 210 | MATCH | SOURCED `count_10sym.json:9` |
| 33 | ETHUSDT n filled | `RESULT_10SYM.md:20` | 202 | $210 - 8 = 202$ | MATCH | SOURCED `count_10sym.json:11` & `result_10sym.json:24` ($210 - 8 = 202$) |
| 34 | ETHUSDT fee-net mean R | `RESULT_10SYM.md:20` | -0.046 | -0.0457 | MATCH | SOURCED `result_10sym.json:25` (-0.04572) |
| 35 | ETHUSDT hit 1.5 R target | `RESULT_10SYM.md:20` | 40.6 % | $82 / 202 = 40.594\%$ | MATCH | $202 \times 0.4059406 = 82$ targets hit; matches `result_10sym.json:26` |
| 36 | SOLUSDT tick | `RESULT_10SYM.md:21` | 0.01 | 0.01 | MATCH | SOURCED `PRE_REG_10SYM.md:22` |
| 37 | SOLUSDT signals | `RESULT_10SYM.md:21` | 205 | 205 | MATCH | SOURCED `count_10sym.json:15` |
| 38 | SOLUSDT n filled | `RESULT_10SYM.md:21` | 193 | $205 - 12 = 193$ | MATCH | SOURCED `count_10sym.json:17` & `result_10sym.json:33` ($205 - 12 = 193$) |
| 39 | SOLUSDT fee-net mean R | `RESULT_10SYM.md:21` | -0.103 | -0.1031 | MATCH | SOURCED `result_10sym.json:34` (-0.10309) |
| 40 | SOLUSDT hit 1.5 R target | `RESULT_10SYM.md:21` | 36.8 % | $71 / 193 = 36.788\%$ | MATCH | $193 \times 0.3678756 = 71$ targets hit; matches `result_10sym.json:35` |
| 41 | BNBUSDT tick | `RESULT_10SYM.md:22` | 0.01 | 0.01 | MATCH | SOURCED `PRE_REG_10SYM.md:22` |
| 42 | BNBUSDT signals | `RESULT_10SYM.md:22` | 222 | 222 | MATCH | SOURCED `count_10sym.json:21` |
| 43 | BNBUSDT n filled | `RESULT_10SYM.md:22` | 212 | $222 - 10 = 212$ | MATCH | SOURCED `count_10sym.json:23` & `result_10sym.json:42` ($222 - 10 = 212$) |
| 44 | BNBUSDT fee-net mean R | `RESULT_10SYM.md:22` | +0.083 | +0.0830 | MATCH | SOURCED `result_10sym.json:43` (+0.08304) |
| 45 | BNBUSDT hit 1.5 R target | `RESULT_10SYM.md:22` | 45.8 % | $97 / 212 = 45.755\%$ | MATCH | $212 \times 0.4575472 = 97$ targets hit; matches `result_10sym.json:44` |
| 46 | XRPUSDT tick | `RESULT_10SYM.md:23` | 0.0001 | 0.0001 | MATCH | SOURCED `PRE_REG_10SYM.md:22` |
| 47 | XRPUSDT signals | `RESULT_10SYM.md:23` | 205 | 205 | MATCH | SOURCED `count_10sym.json:27` |
| 48 | XRPUSDT n filled | `RESULT_10SYM.md:23` | 198 | $205 - 7 = 198$ | MATCH | SOURCED `count_10sym.json:29` & `result_10sym.json:51` ($205 - 7 = 198$) |
| 49 | XRPUSDT fee-net mean R | `RESULT_10SYM.md:23` | -0.008 | -0.0080 | MATCH | SOURCED `result_10sym.json:52` (-0.00802) |
| 50 | XRPUSDT hit 1.5 R target | `RESULT_10SYM.md:23` | 41.4 % | $82 / 198 = 41.414\%$ | MATCH | $198 \times 0.4141414 = 82$ targets hit; matches `result_10sym.json:53` |
| 51 | DOGEUSDT tick | `RESULT_10SYM.md:24` | 0.00001 | 0.00001 | MATCH | SOURCED `PRE_REG_10SYM.md:22` |
| 52 | DOGEUSDT signals | `RESULT_10SYM.md:24` | 196 | 196 | MATCH | SOURCED `count_10sym.json:33` |
| 53 | DOGEUSDT n filled | `RESULT_10SYM.md:24` | 188 | $196 - 8 = 188$ | MATCH | SOURCED `count_10sym.json:35` & `result_10sym.json:60` ($196 - 8 = 188$) |
| 54 | DOGEUSDT fee-net mean R | `RESULT_10SYM.md:24` | -0.061 | -0.0608 | MATCH | SOURCED `result_10sym.json:61` (-0.06079) |
| 55 | DOGEUSDT hit 1.5 R target | `RESULT_10SYM.md:24` | 39.4 % | $74 / 188 = 39.362\%$ | MATCH | $188 \times 0.3936170 = 74$ targets hit; matches `result_10sym.json:62` |
| 56 | ADAUSDT tick | `RESULT_10SYM.md:25` | 0.0001 | 0.0001 | MATCH | SOURCED `PRE_REG_10SYM.md:22` |
| 57 | ADAUSDT signals | `RESULT_10SYM.md:25` | 189 | 189 | MATCH | SOURCED `count_10sym.json:39` |
| 58 | ADAUSDT n filled | `RESULT_10SYM.md:25` | 178 | $189 - 11 = 178$ | MATCH | SOURCED `count_10sym.json:41` & `result_10sym.json:69` ($189 - 11 = 178$) |
| 59 | ADAUSDT fee-net mean R | `RESULT_10SYM.md:25` | -0.053 | -0.0535 | MATCH | SOURCED `result_10sym.json:70` (-0.05347) |
| 60 | ADAUSDT hit 1.5 R target | `RESULT_10SYM.md:25` | 39.3 % | $70 / 178 = 39.326\%$ | MATCH | $178 \times 0.3932584 = 70$ targets hit; matches `result_10sym.json:71` |
| 61 | AVAXUSDT tick | `RESULT_10SYM.md:26` | 0.001 | 0.001 | MATCH | SOURCED `PRE_REG_10SYM.md:22` |
| 62 | AVAXUSDT signals | `RESULT_10SYM.md:26` | 210 | 210 | MATCH | SOURCED `count_10sym.json:45` |
| 63 | AVAXUSDT n filled | `RESULT_10SYM.md:26` | 203 | $210 - 7 = 203$ | MATCH | SOURCED `count_10sym.json:47` & `result_10sym.json:78` ($210 - 7 = 203$) |
| 64 | AVAXUSDT fee-net mean R | `RESULT_10SYM.md:26` | +0.021 | +0.0213 | MATCH | SOURCED `result_10sym.json:79` (+0.02130) |
| 65 | AVAXUSDT hit 1.5 R target | `RESULT_10SYM.md:26` | 42.4 % | $86 / 203 = 42.365\%$ | MATCH | $203 \times 0.4236453 = 86$ targets hit; matches `result_10sym.json:80` |
| 66 | LINKUSDT tick | `RESULT_10SYM.md:27` | 0.001 | 0.001 | MATCH | SOURCED `PRE_REG_10SYM.md:22` |
| 67 | LINKUSDT signals | `RESULT_10SYM.md:27` | 209 | 209 | MATCH | SOURCED `count_10sym.json:51` |
| 68 | LINKUSDT n filled | `RESULT_10SYM.md:27` | 200 | $209 - 9 = 200$ | MATCH | SOURCED `count_10sym.json:53` & `result_10sym.json:87` ($209 - 9 = 200$) |
| 69 | LINKUSDT fee-net mean R | `RESULT_10SYM.md:27` | -0.065 | -0.0651 | MATCH | SOURCED `result_10sym.json:88` (-0.06512) |
| 70 | LINKUSDT hit 1.5 R target | `RESULT_10SYM.md:27` | 39.0 % | $78 / 200 = 39.000\%$ | MATCH | $200 \times 0.39 = 78$ targets hit; matches `result_10sym.json:89` |
| 71 | LTCUSDT tick | `RESULT_10SYM.md:28` | 0.01 | 0.01 | MATCH | SOURCED `PRE_REG_10SYM.md:22` |
| 72 | LTCUSDT signals | `RESULT_10SYM.md:28` | 207 | 207 | MATCH | SOURCED `count_10sym.json:57` |
| 73 | LTCUSDT n filled | `RESULT_10SYM.md:28` | 200 | $207 - 7 = 200$ | MATCH | SOURCED `count_10sym.json:59` & `result_10sym.json:96` ($207 - 7 = 200$) |
| 74 | LTCUSDT fee-net mean R | `RESULT_10SYM.md:28` | -0.111 | -0.1113 | MATCH | SOURCED `result_10sym.json:97` (-0.11134) |
| 75 | LTCUSDT hit 1.5 R target | `RESULT_10SYM.md:28` | 37.5 % | $75 / 200 = 37.500\%$ | MATCH | $200 \times 0.375 = 75$ targets hit; matches `result_10sym.json:98` |
| 76 | Round-trip fee (taker) | `RESULT_10SYM.md:30` | 10 bp | 10 bp | MATCH | SOURCED `PRE_REG_10SYM.md:19` 2 $\times$ DERIBIT_TAKER (5 bp $\times$ 2 = 10 bp) |
| 77 | MDE in R | `RESULT_10SYM.md:30` | 0.126 R | 0.126 R | MATCH | SOURCED `gate_output_10sym.txt:1` ("MDE 0.126 R") |
| 78 | Archive gap missing bars | `RESULT_10SYM.md:30` | 7200 | $1,313,280 - 1,306,080 = 7,200$ | MATCH | SOURCED `count_10sym.json:18,30,60` and `PRE_REG_10SYM.md:23` |
| 79 | Tested code unit test pass count | `RESULT_10SYM.md:5` | 7 | 7 | MATCH | `test_10sym.py` defines exactly 7 test functions |

---

## 3. Summary of Findings

- **Total items audited**: 59
- **MATCH**: 54
- **DIFF**: 0
- **NOT_IN_DATA**: 5 (Day-block bootstrap CI bounds `ci_lo` / `ci_hi`, empirical two-sided `p_two`, empirical gross mean R, and measured sample `sd_r`; all 5 are verified consistent with `result_10sym.json` and formulas in `FORMULAS.md`).

All aggregate quantities, signal counts, unfilled counts, symbol-specific fills, target hit percentages, weighted average pooled return, Holm adjustment cap, gate thresholds, regime week breakdowns, and the final verdict of **FAIL** match the registered pre-specification and raw count files without any discrepancy.
