# Blind Read Audit: WaveTrend C30 Retest and Long-Window RESULT.md vs CSVs

- **Card**: `gemini-blind-read-wavetrend-c30-retest-1104`
- **Audited Documents**:
  - `MyTradingSys/research/wavetrend_c30_retest_2026-11-04/RESULT.md` (Run 1 DEV 2022-01-01..2024-06-30)
  - `MyTradingSys/research/wavetrend_c30_retest_2026-11-04/RESULT_LONG.md` (Long DEV 2018-04-01..2024-06-30)
- **Primary Data Sources**:
  - `MyTradingSys/research/wavetrend_c30_retest_2026-11-04/counts.csv` [SOURCED: counts.csv:1-1081]
  - `MyTradingSys/research/wavetrend_c30_retest_2026-11-04/dev_cells.csv` [SOURCED: dev_cells.csv:1-1081]
  - `MyTradingSys/research/wavetrend_c30_retest_2026-11-04/counts_long.csv` [SOURCED: counts_long.csv:1-1357]
  - `MyTradingSys/research/wavetrend_c30_retest_2026-11-04/dev_cells_long.csv` [SOURCED: dev_cells_long.csv:1-1357]
  - `MyTradingSys/research/wavetrend_c30_retest_2026-11-04/dev_survivors.json` [SOURCED: dev_survivors.json:1]
  - `MyTradingSys/research/wavetrend_c30_retest_2026-11-04/dev_survivors_long.json` [SOURCED: dev_survivors_long.json:1]
  - `MyTradingSys/research/wavetrend_c30_retest_2026-11-04/regime_mix_dev.txt` [SOURCED: regime_mix_dev.txt:1]
  - `MyTradingSys/research/wavetrend_c30_retest_2026-11-04/regime_mix_long_dev.txt` [SOURCED: regime_mix_long_dev.txt:1]
  - `MyTradingSys/research/wavetrend_c30_retest_2026-11-04/BLOCKED.md` [SOURCED: BLOCKED.md:1-12]
  - `MyTradingSys/research/wavetrend_c30_retest_2026-11-04/BLOCKED_LONG.md` [SOURCED: BLOCKED_LONG.md:1-12]
  - `MyTradingSys/system/OPERATOR_DECISIONS.md` (`d-bear-proxy-1104`) [SOURCED: OPERATOR_DECISIONS.md:1694-1698]
- **Date**: 2026-11-04
- **Auditor**: Gemini (independent blind read)
- **Summary**: All 82 checked numerical and categorical claims in `RESULT.md` and `RESULT_LONG.md` match the underlying CSV and txt outputs with 100% precision (`FOUND=82 DIFF=0 NOT_IN_DATA=0`). Every metric (counts, win rates `hit_net`, expectancy `net` and `gross`, regime splits) was independently recomputed from `counts.csv`, `dev_cells.csv`, `counts_long.csv`, and `dev_cells_long.csv`. Labeling strictly conforms to `d-bear-proxy-1104`: strict Malkan regime is SOURCED, whereas the weekly-only bear proxy arm is explicitly marked OURS and never called Malkan's.

VERDICT: MATCH

---

## 1. Independent Recomputation of Metrics from CSV Outputs

### 1.1 Run 1 Dataset Inventory and Verification (`dev_cells.csv` and `counts.csv`)
- Total rows in `dev_cells.csv`: 1,080 rows [SOURCED: dev_cells.csv:1-1081] [OURS recomputation: len=1080]
- Total rows in `counts.csv`: 1,080 rows [SOURCED: counts.csv:1-1081] [OURS recomputation: len=1080]
- Discrepancies between `counts.csv` and `dev_cells.csv` on (`tf`, `side`, `conf`, `gate`, `session`, `entry`) for `n`, `days`, `signals`: 0 mismatches across 1,080 rows [OURS recomputation: n_diff=0, days_diff=0, sig_diff=0]
- Regime mix (DEV 2022-01-01 to 2024-06-30): 130 weeks total [SOURCED: regime_mix_dev.txt:1]
  - Bull: 25 weeks (19.23% -> 19%) [SOURCED: regime_mix_dev.txt:1] [OURS recomputation: 25/130 = 0.1923]
  - Bear: 0 weeks (0.00% -> 0%) [SOURCED: regime_mix_dev.txt:1] [OURS recomputation: 0/130 = 0.0]
  - Range: 105 weeks (80.77% -> 81%) [SOURCED: regime_mix_dev.txt:1] [OURS recomputation: 105/130 = 0.8077]
  - N/A: 0 weeks (0.00% -> 0%) [SOURCED: regime_mix_dev.txt:1] [OURS recomputation: 0/130 = 0.0]
- Confirmatory screening families [SOURCED: PRE_REG.md:20]:
  - Family A (pooled sessions `session == 'ALL'`, gate `with`, conf in `{'rsi', 'div'}`): 24 cells [OURS recomputation: len=24]
  - Family B (session-split `session != 'ALL'`, gate `with`, conf in `{'rsi', 'div'}`): 96 cells [OURS recomputation: len=96]
  - Total screened cells: 120 cells [OURS recomputation: 24 + 96 = 120]
  - DEV survivors: 0 cells [SOURCED: dev_survivors.json:1] [OURS recomputation: (dev_cells['survivor']==True).sum() == 0]
- Sample size and confidence interval distribution:
  - Cells with `n >= 30`: 509 cells [OURS recomputation: len(dev_cells[dev_cells['n']>=30]) == 509]
  - Cells with `n >= 30` and `ci_hi < 0` (entirely below zero): 126 cells [OURS recomputation: len==126]
  - Cells with `n >= 30` and `ci_lo > 0` (entirely above zero): 0 cells [OURS recomputation: len==0]

### 1.2 Long Window Dataset Inventory and Verification (`dev_cells_long.csv` and `counts_long.csv`)
- Total rows in `dev_cells_long.csv`: 1,356 rows [SOURCED: dev_cells_long.csv:1-1357] [OURS recomputation: len=1356]
- Total rows in `counts_long.csv`: 1,356 rows [SOURCED: counts_long.csv:1-1357] [OURS recomputation: len=1356]
- Discrepancies between `counts_long.csv` and `dev_cells_long.csv` on matching keys: 0 mismatches across 1,356 rows [OURS recomputation: n_diff=0, days_diff=0, sig_diff=0]
- Regime mix (DEV 2018-04-01 to 2024-06-30): 326 weeks total [SOURCED: regime_mix_long_dev.txt:1]
  - Bull: 73 weeks (22.39% -> 22%) [SOURCED: regime_mix_long_dev.txt:1] [OURS recomputation: 73/326 = 0.2239]
  - Strict Bear: 0 weeks (0.00% -> 0%) [SOURCED: regime_mix_long_dev.txt:1] [OURS recomputation: 0/326 = 0.0]
  - Range: 222 weeks (68.10% -> 68%) [SOURCED: regime_mix_long_dev.txt:1] [OURS recomputation: 222/326 = 0.6810]
  - N/A: 31 weeks (9.51% -> 10%) [SOURCED: regime_mix_long_dev.txt:1] [OURS recomputation: 31/326 = 0.0951]
  - Proxy Bear (`reg_bearp`, weekly RSI14 <= 40 alone, below SMA200, OURS): 57 weeks of 326 weeks (17.48%) [SOURCED: regime_mix_long_dev.txt:1] [OURS recomputation: 57/326 = 0.1748]
- Long window confirmatory families (strict + proxy bear, m=48 pooled, m=192 session):
  - Pooled cells with `holm_p` assigned: 48 cells [OURS recomputation: len=48]
  - Session cells with `holm_p` assigned: 192 cells [OURS recomputation: len=192]
  - DEV survivors: 0 cells [SOURCED: dev_survivors_long.json:1] [OURS recomputation: len==0]

### 1.3 Key Cell Recomputed Win Rates (`hit_net`) and Expectancy (`net` / `gross`)
Independent recomputation of performance metrics for representative cells in `dev_cells.csv`:
1. `15m sell rsi signal ALL`:
   - Count `n`: 257 [SOURCED: dev_cells.csv:250] [OURS recomputation: 257]
   - Event days: 170 [SOURCED: dev_cells.csv:250] [OURS recomputation: 170]
   - Win rate (`hit_net`): 46.69% (120/257) [SOURCED: dev_cells.csv:250 `hit_net=0.466926`] [OURS recomputation: 0.4669]
   - Gross expectancy: +0.148% [SOURCED: dev_cells.csv:250 `gross=0.147614`] [OURS recomputation: +0.148%]
   - Net expectancy: +0.008% [SOURCED: dev_cells.csv:250 `net=0.007614`] [OURS recomputation: +0.008%]
   - 95% CI: [-0.134%, +0.149%] [SOURCED: dev_cells.csv:250 `ci_lo=-0.133642`, `ci_hi=0.149289`]
   - Excess over drift: +0.133% [SOURCED: dev_cells.csv:250 `excess=0.133496`], excess t: 1.91 [SOURCED: dev_cells.csv:250 `excess_t=1.905663`], Holm p: 1.00 [SOURCED: dev_cells.csv:250 `holm_p=1.0`]
2. `1h sell div signal ALL`:
   - Count `n`: 22 [SOURCED: dev_cells.csv:1030] [OURS recomputation: 22]
   - Event days: 20 [SOURCED: dev_cells.csv:1030] [OURS recomputation: 20]
   - Win rate (`hit_net`): 54.55% (12/22) [SOURCED: dev_cells.csv:1030 `hit_net=0.545455`] [OURS recomputation: 0.5455]
   - Gross expectancy: +0.944% [SOURCED: dev_cells.csv:1030 `gross=0.943730`] [OURS recomputation: +0.944%]
   - Net expectancy: +0.804% [SOURCED: dev_cells.csv:1030 `net=0.803730`] [OURS recomputation: +0.804%]
   - 95% CI: [-0.152%, +1.759%] [SOURCED: dev_cells.csv:1030 `ci_lo=-0.151772`, `ci_hi=1.759231`]
3. `1h sell div retest ALL`:
   - Count `n`: 19 [SOURCED: dev_cells.csv:1031] [OURS recomputation: 19]
   - Event days: 17 [SOURCED: dev_cells.csv:1031] [OURS recomputation: 17]
   - Win rate (`hit_net`): 73.68% (14/19) [SOURCED: dev_cells.csv:1031 `hit_net=0.736842`] [OURS recomputation: 0.7368]
   - Gross expectancy: +1.257% [SOURCED: dev_cells.csv:1031 `gross=1.257070`] [OURS recomputation: +1.257%]
   - Net expectancy: +1.117% [SOURCED: dev_cells.csv:1031 `net=1.117070`] [OURS recomputation: +1.117%]
   - 95% CI: [+0.007%, +2.227%] [SOURCED: dev_cells.csv:1031 `ci_lo=0.006935`, `ci_hi=2.227205`]
   - Excess t: 2.15 [SOURCED: dev_cells.csv:1031 `excess_t=2.150119`], Holm p: 0.92 [SOURCED: dev_cells.csv:1031 `holm_p=0.920038`]
4. `15m buy rsi signal ALL`:
   - Count `n`: 238 [SOURCED: dev_cells.csv:70] [OURS recomputation: 238]
   - Event days: 144 [SOURCED: dev_cells.csv:70] [OURS recomputation: 144]
   - Win rate (`hit_net`): 46.22% (110/238) [SOURCED: dev_cells.csv:70 `hit_net=0.462185`] [OURS recomputation: 0.4622]
   - Gross expectancy: -0.047% [SOURCED: dev_cells.csv:70 `gross=-0.046640`] [OURS recomputation: -0.047%]
   - Net expectancy: -0.187% [SOURCED: dev_cells.csv:70 `net=-0.186640`] [OURS recomputation: -0.187%]
   - 95% CI: [-0.303%, -0.070%] [SOURCED: dev_cells.csv:70 `ci_lo=-0.303273`, `ci_hi=-0.070007`]
   - Holm p: 0.040 [SOURCED: dev_cells.csv:70 `holm_p=0.039641`]
5. `15m sell rsi signal asia`:
   - Count `n`: 78 [SOURCED: dev_cells.csv:252] [OURS recomputation: 78]
   - Event days: 66 [SOURCED: dev_cells.csv:252] [OURS recomputation: 66]
   - Win rate (`hit_net`): 41.03% (32/78) [SOURCED: dev_cells.csv:252 `hit_net=0.410256`] [OURS recomputation: 0.4103]
   - Gross expectancy: +0.192% [SOURCED: dev_cells.csv:252 `gross=0.192062`] [OURS recomputation: +0.192%]
   - Net expectancy: +0.052% [SOURCED: dev_cells.csv:252 `net=0.052062`] [OURS recomputation: +0.052%]
   - 95% CI: [-0.157%, +0.261%] [SOURCED: dev_cells.csv:252 `ci_lo=-0.156550`, `ci_hi=0.260674`]
   - Excess over drift: +0.191% [SOURCED: dev_cells.csv:252 `excess=0.190989`], excess t: 1.87 [SOURCED: dev_cells.csv:252 `excess_t=1.868739`]

---

## 2. Check of SOURCED vs OURS Labels Against `d-bear-proxy-1104`

Operator decision `d-bear-proxy-1104` [SOURCED: OPERATOR_DECISIONS.md:1694-1698] mandates:
1. Strict Malkan weekly-and-monthly <= 40 bear gate is SOURCED (`MALKAN_RULES_2026-10-31.md`). On BTCUSDT spot (2017-08..2026-11, 479 weeks), monthly RSI14 never closed at or below 40 (min 40.4 in 2023-01), giving 0 bear weeks in both DEV windows.
2. The primary arm keeps the SOURCED gate untouched (`reg_bear`).
3. One proxy arm is added, defined as weekly RSI14 <= 40 alone and below SMA200 (`reg_bearp`). This proxy arm is strictly labelled OURS and never called Malkan's.

Audit of label compliance in `RESULT.md` and `RESULT_LONG.md`:
- `RESULT.md:15`: `reg_bear empty (0 bear weeks in DEV)` matches the strict SOURCED Malkan rule [SOURCED: OPERATOR_DECISIONS.md:1695].
- `RESULT.md:19`: Explicitly documents that a bear regime never occurs under the strict Malkan band in 2022-24, and notes 12-bar horizon and midpoint retest are OURS [SOURCED: RESULT.md:19].
- `RESULT_LONG.md:1`: Labels `strict bear 0` alongside `proxy bear (weekly RSI14 <= 40 alone, below SMA200, OURS) 57 of 326 weeks` [SOURCED: RESULT_LONG.md:1].
- `RESULT_LONG.md:10`: Re-iterates `Strict Malkan (weekly AND monthly RSI14 <= 40, below SMA200) never fires: 0 bear weeks over 2017-08..2026-10... The OURS proxy (weekly RSI14 <= 40 alone, below SMA200) gives 57 of 326 weeks, Proxy is never called Malkan's` [SOURCED: RESULT_LONG.md:10].
- `RESULT_LONG.md:36`: Section title `## Proxy arm (OURS weekly RSI14 <= 40 alone, below SMA200), strict arm beside it` explicitly maintains the required separation [SOURCED: RESULT_LONG.md:36].

**Label Compliance**: 100% compliant with `d-bear-proxy-1104`.

---

## 3. Complete Reconciliation Table: `RESULT.md` (Run 1) vs CSVs

| # | Item Description | `RESULT.md` Location & Quote | CSV / Source File & Location | CSV Derived Value | Status | Label |
|---|---|---|---|---|---|---|
| 1 | DEV total weeks | `RESULT.md:1` (`130 weeks`) | `regime_mix_dev.txt:1` | 130 weeks | MATCH | SOURCED |
| 2 | Bull regime share | `RESULT.md:1` (`bull 25 (19%)`) | `regime_mix_dev.txt:1` | 25 weeks (19.23%) | MATCH | SOURCED |
| 3 | Bear regime share | `RESULT.md:1` (`bear 0 (0%)`) | `regime_mix_dev.txt:1` | 0 weeks (0.00%) | MATCH | SOURCED |
| 4 | Range regime share | `RESULT.md:1` (`range 105 (81%)`) | `regime_mix_dev.txt:1` | 105 weeks (80.77%) | MATCH | SOURCED |
| 5 | N/A regime share | `RESULT.md:1` (`n/a 0 (0%)`) | `regime_mix_dev.txt:1` | 0 weeks (0.00%) | MATCH | SOURCED |
| 6 | DEV survivors count | `RESULT.md:2` (`0 DEV survivors`) | `dev_survivors.json:1` | `[]` (0 survivors) | MATCH | OURS |
| 7 | Pooled cells count | `RESULT.md:2` (`24 pooled`) | `dev_cells.csv` (`session=='ALL'`, `holm_p` not null) | 24 cells | MATCH | OURS |
| 8 | Session cells count | `RESULT.md:2` (`96 session cells`) | `dev_cells.csv` (`session!='ALL'`, `holm_p` not null) | 96 cells | MATCH | OURS |
| 9 | Holm family sizes | `RESULT.md:2` (`Holm m=24 / 96`) | `PRE_REG.md:20` | m=24 pooled / m=96 session | MATCH | OURS |
| 10 | Fee net roundtrip | `RESULT.md:4` (`fee-net 0.14 %`) | `PRE_REG.md:16`, `research_kit.py` | 0.14% RT (14 bps) | MATCH | SOURCED |
| 11 | Horizon length | `RESULT.md:4` (`exit 12 bars`) | `PRE_REG.md:15` | 12 bars | MATCH | OURS |
| 12 | dev_cells row count | `RESULT.md:6` (`dev_cells.csv (1080 rows)`) | `dev_cells.csv:1-1081` | 1,080 rows | MATCH | SOURCED |
| 13 | Bare dot 15m buy | `RESULT.md:9` (`15m buy -0.131 %`) | `dev_cells.csv:1` (`net=-0.131293`) | -0.131% | MATCH | SOURCED |
| 14 | Bare dot 15m sell | `RESULT.md:9` (`15m sell -0.202 %`) | `dev_cells.csv:181` (`net=-0.201847`) | -0.202% | MATCH | SOURCED |
| 15 | Bare dot 30m buy | `RESULT.md:9` (`30m buy -0.103 %`) | `dev_cells.csv:361` (`net=-0.102698`) | -0.103% | MATCH | SOURCED |
| 16 | Bare dot 30m sell | `RESULT.md:9` (`30m sell -0.254 %`) | `dev_cells.csv:541` (`net=-0.253572`) | -0.254% | MATCH | SOURCED |
| 17 | Bare dot 1h buy | `RESULT.md:9` (`1h buy -0.342 %`) | `dev_cells.csv:721` (`net=-0.342280`) | -0.342% | MATCH | SOURCED |
| 18 | Bare dot 1h sell | `RESULT.md:9` (`1h sell -0.295 %`) | `dev_cells.csv:901` (`net=-0.295393`) | -0.295% | MATCH | SOURCED |
| 19 | Cells with n >= 30 | `RESULT.md:9` (`509 cells with n >= 30`) | `dev_cells.csv` (`n >= 30`) | 509 cells | MATCH | OURS |
| 20 | Net CI below zero | `RESULT.md:9` (`126 of the 509 cells... CI entirely below zero`) | `dev_cells.csv` (`n>=30 & ci_hi<0`) | 126 cells | MATCH | OURS |
| 21 | Net CI above zero | `RESULT.md:9` (`none has a CI entirely above zero`) | `dev_cells.csv` (`n>=30 & ci_lo>0`) | 0 cells | MATCH | OURS |
| 22 | Trend gate 15m sell with | `RESULT.md:10` (`15m sell with-trend... -0.062 %`) | `dev_cells.csv:187` (`net=-0.062031`) | -0.062% | MATCH | SOURCED |
| 23 | Trend gate 15m sell against | `RESULT.md:10` (`vs against-trend -0.305 %`) | `dev_cells.csv:193` (`net=-0.305096`) | -0.305% | MATCH | SOURCED |
| 24 | Trend gate 30m sell with | `RESULT.md:10` (`30m sell -0.090`) | `dev_cells.csv:547` (`net=-0.089851`) | -0.090% | MATCH | SOURCED |
| 25 | Trend gate 30m sell against | `RESULT.md:10` (`vs -0.361`) | `dev_cells.csv:553` (`net=-0.360877`) | -0.361% | MATCH | SOURCED |
| 26 | Trend gate 1h sell with | `RESULT.md:10` (`1h sell +0.079`) | `dev_cells.csv:907` (`net=0.078864`) | +0.079% | MATCH | SOURCED |
| 27 | Trend gate 1h sell against | `RESULT.md:10` (`vs -0.562`) | `dev_cells.csv:913` (`net=-0.562309`) | -0.562% | MATCH | SOURCED |
| 28 | Trend gate 15m buy with | `RESULT.md:10` (`15m -0.141`) | `dev_cells.csv:7` (`net=-0.141257`) | -0.141% | MATCH | SOURCED |
| 29 | Trend gate 15m buy against | `RESULT.md:10` (`vs -0.122`) | `dev_cells.csv:13` (`net=-0.122394`) | -0.122% | MATCH | SOURCED |
| 30 | Trend gate 30m buy with | `RESULT.md:10` (`30m -0.035`) | `dev_cells.csv:367` (`net=-0.035444`) | -0.035% | MATCH | SOURCED |
| 31 | Trend gate 30m buy against | `RESULT.md:10` (`vs -0.161`) | `dev_cells.csv:373` (`net=-0.160533`) | -0.161% | MATCH | SOURCED |
| 32 | Trend gate 1h buy with | `RESULT.md:10` (`1h -0.461`) | `dev_cells.csv:727` (`net=-0.461413`) | -0.461% | MATCH | SOURCED |
| 33 | Trend gate 1h buy against | `RESULT.md:10` (`vs -0.252`) | `dev_cells.csv:733` (`net=-0.252084`) | -0.252% | MATCH | SOURCED |
| 34 | 15m sell RSI n / days | `RESULT.md:11` (`n 257 / 170 days`) | `dev_cells.csv:251` (`n=257, days=170`) | 257 signals / 170 days | MATCH | SOURCED |
| 35 | 15m sell RSI gross / net | `RESULT.md:11` (`gross +0.148 %, net +0.008 %`) | `dev_cells.csv:251` (`gross=0.147614, net=0.007614`) | gross +0.148%, net +0.008% | MATCH | SOURCED |
| 36 | 15m sell RSI 95% CI | `RESULT.md:11` (`[-0.134, +0.149]`) | `dev_cells.csv:251` (`ci_lo=-0.133642, ci_hi=0.149289`) | [-0.134%, +0.149%] | MATCH | SOURCED |
| 37 | 15m sell RSI excess / t | `RESULT.md:11` (`excess over drift +0.133 % (t 1.91)`) | `dev_cells.csv:251` (`excess=0.133496, excess_t=1.905663`) | excess +0.133%, t=1.91 | MATCH | SOURCED |
| 38 | 15m sell RSI Holm p | `RESULT.md:11` (`Holm p 1.0`) | `dev_cells.csv:251` (`holm_p=1.0`) | 1.00 | MATCH | SOURCED |
| 39 | 1h sell div n / days | `RESULT.md:11` (`n 22 / 20 days`) | `dev_cells.csv:1031` (`n=22, days=20`) | 22 signals / 20 days | MATCH | SOURCED |
| 40 | 1h sell div net / CI | `RESULT.md:11` (`net +0.804 % [-0.152, +1.759]`) | `dev_cells.csv:1031` (`net=0.803730, ci_lo=-0.151772, ci_hi=1.759231`) | net +0.804% [-0.152%, +1.759%] | MATCH | SOURCED |
| 41 | 1h sell div retest n / days | `RESULT.md:11` (`retest entry n 19 / 17 days`) | `dev_cells.csv:1032` (`n=19, days=17`) | 19 signals / 17 days | MATCH | SOURCED |
| 42 | 1h sell div retest net / CI | `RESULT.md:11` (`net +1.117 % [+0.007, +2.227]`) | `dev_cells.csv:1032` (`net=1.117070, ci_lo=0.006935, ci_hi=2.227205`) | net +1.117% [+0.007%, +2.227%] | MATCH | SOURCED |
| 43 | 1h sell div retest excess t | `RESULT.md:11` (`excess t 2.15`) | `dev_cells.csv:1032` (`excess_t=2.150119`) | t=2.15 | MATCH | SOURCED |
| 44 | 1h sell div retest Holm p | `RESULT.md:11` (`Holm p 0.92`) | `dev_cells.csv:1032` (`holm_p=0.920038`) | 0.92 | MATCH | SOURCED |
| 45 | 1h sell div family cell count | `RESULT.md:11` (`with 120 cells in the family`) | `dev_cells.csv` (24 pooled + 96 session) | 120 cells | MATCH | OURS |
| 46 | 15m buy RSI n / days | `RESULT.md:12` (`15m n 238 / 144 days`) | `dev_cells.csv:71` (`n=238, days=144`) | 238 signals / 144 days | MATCH | SOURCED |
| 47 | 15m buy RSI net / CI | `RESULT.md:12` (`net -0.187 % [-0.303, -0.070]`) | `dev_cells.csv:71` (`net=-0.186640, ci_lo=-0.303273, ci_hi=-0.070007`) | net -0.187% [-0.303%, -0.070%] | MATCH | SOURCED |
| 48 | 15m buy RSI Holm p | `RESULT.md:12` (`Holm p 0.040`) | `dev_cells.csv:71` (`holm_p=0.039641`) | 0.040 | MATCH | SOURCED |
| 49 | Retest signal drop range | `RESULT.md:13` (`removes 8-29 % of signals`) | `dev_cells.csv` (confirmatory 12 cells drop) | min 8.40%, max 29.17% | MATCH | OURS |
| 50 | Retest net improvement | `RESULT.md:13` (`better in 6 and worse in 6`) | `dev_cells.csv` (12 pooled confirmatory) | 6 better, 6 worse | MATCH | OURS |
| 51 | Session survivor count | `RESULT.md:14` (`96 session cells, Holm m=96: 0 survivors`) | `dev_cells.csv` (`session!='ALL'`) | 96 cells, 0 survivors | MATCH | OURS |
| 52 | 15m sell RSI asia n / days | `RESULT.md:14` (`asia n 78 / 66 days`) | `dev_cells.csv:253` (`n=78, days=66`) | 78 signals / 66 days | MATCH | SOURCED |
| 53 | 15m sell RSI asia net / CI | `RESULT.md:14` (`net +0.052 % [-0.157, +0.261]`) | `dev_cells.csv:253` (`net=0.052062, ci_lo=-0.156550, ci_hi=0.260674`) | net +0.052% [-0.157%, +0.261%] | MATCH | SOURCED |
| 54 | 15m sell RSI asia excess / t | `RESULT.md:14` (`excess +0.191 % t 1.87`) | `dev_cells.csv:253` (`excess=0.190989, excess_t=1.868739`) | excess +0.191%, t=1.87 | MATCH | SOURCED |
| 55 | 15m sell RSI london / ny | `RESULT.md:14` (`london / ny near zero`) | `dev_cells.csv:255, 257` (`net=-0.005%, 0.000%`) | -0.005%, 0.000% | MATCH | SOURCED |
| 56 | Smallest raw p sample size | `RESULT.md:14` (`cells with n 2-11 and are negative`) | `dev_cells.csv` (`p < 0.001`) | n in 2..11, net < 0 | MATCH | OURS |
| 57 | Regime bull 15m buy | `RESULT.md:15` (`reg_bull 149 buy dots on 15m (net -0.190 %)`) | `dev_cells.csv:19` (`n=149, net=-0.189914`) | 149 signals, net -0.190% | MATCH | SOURCED |
| 58 | Regime range 15m buy | `RESULT.md:15` (`reg_range 620 (-0.117 %)`) | `dev_cells.csv:25` (`n=620, net=-0.117173`) | 620 signals, net -0.117% | MATCH | SOURCED |
| 59 | Regime bear 15m buy | `RESULT.md:15` (`reg_bear empty (0 bear weeks in DEV)`) | `dev_cells.csv:31` (`n=0, net=NaN`) | 0 signals | MATCH | SOURCED |
| 60 | MDE + cost 15m / 30m / 1h | `RESULT.md:17` (`0.38 / 0.60 / 1.02 against 0.30`) | `BLOCKED.md:5-7` (`0.381 / 0.596 / 1.023 vs 0.30`) | 0.381, 0.596, 1.023 | MATCH | SOURCED |
| 61 | 1h event-days needed | `RESULT.md:17` (`about 2,100 event-days (n needed 2165)`) | `BLOCKED.md:7` (`n needed = 2165`) | 2,165 event-days | MATCH | SOURCED |

---

## 4. Complete Reconciliation Table: `RESULT_LONG.md` (Long Window & Bear Proxy) vs CSVs

| # | Item Description | `RESULT_LONG.md` Location & Quote | CSV / Source File & Location | CSV Derived Value | Status | Label |
|---|---|---|---|---|---|---|
| 62 | Long DEV total weeks | `RESULT_LONG.md:1` (`326 weeks`) | `regime_mix_long_dev.txt:1` | 326 weeks | MATCH | SOURCED |
| 63 | Long bull weeks | `RESULT_LONG.md:1` (`bull 73 (22%)`) | `regime_mix_long_dev.txt:1` | 73 weeks (22.39%) | MATCH | SOURCED |
| 64 | Long strict bear weeks | `RESULT_LONG.md:1` (`strict bear 0`) | `regime_mix_long_dev.txt:1` | 0 weeks (0.00%) | MATCH | SOURCED |
| 65 | Long range weeks | `RESULT_LONG.md:1` (`range 222 (68%)`) | `regime_mix_long_dev.txt:1` | 222 weeks (68.10%) | MATCH | SOURCED |
| 66 | Long N/A weeks | `RESULT_LONG.md:1` (`n/a 31 (10%)`) | `regime_mix_long_dev.txt:1` | 31 weeks (9.51%) | MATCH | SOURCED |
| 67 | Long proxy bear weeks | `RESULT_LONG.md:1` (`proxy bear... OURS) 57 of 326 weeks`) | `regime_mix_long_dev.txt:1` | 57 weeks (17.48%) | MATCH | OURS |
| 68 | Long pooled / session cells | `RESULT_LONG.md:2` (`48 pooled + 192 session cells... 0 survivors`) | `dev_cells_long.csv`, `dev_survivors_long.json` | 48 pooled, 192 session, 0 survivors | MATCH | OURS |
| 69 | Long power gate 15m none | `RESULT_LONG.md:13` (`580 days PASS (0.294 vs 0.30, m=48)`) | `BLOCKED_LONG.md:5` | 580 days, MDE+cost 0.294 | MATCH | SOURCED |
| 70 | Long power gate 15m rsi | `RESULT_LONG.md:13` (`15m rsi 413 days 0.322`) | `BLOCKED_LONG.md:6` | 413 days, MDE+cost 0.322 | MATCH | SOURCED |
| 71 | Long bare dot 15m buy / sell | `RESULT_LONG.md:16` (`15m buy -0.115 % [-0.192, -0.038], sell -0.186 % [-0.245, -0.127]`) | `dev_cells_long.csv:1, 226` (`net=-0.115, -0.186`) | buy -0.115%, sell -0.186% | MATCH | SOURCED |
| 72 | Long bare dot 30m buy / sell | `RESULT_LONG.md:16` (`30m buy -0.147, sell -0.229 (CI upper bound -0.000 / -0.128)`) | `dev_cells_long.csv:451, 676` (`net=-0.147, -0.229`) | buy -0.147%, sell -0.229% | MATCH | SOURCED |
| 73 | Long bare dot 1h buy / sell | `RESULT_LONG.md:16` (`1h buy -0.157 [-0.427, +0.112], sell -0.544 [-0.766, -0.323]`) | `dev_cells_long.csv:901, 1126` (`net=-0.157, -0.544`) | buy -0.157%, sell -0.544% | MATCH | SOURCED |
| 74 | Table Lead 1: 15m sell RSI | `RESULT_LONG.md:21` (`651 / 419, -0.183 [-0.294, -0.072], fresh -0.305, old +0.011`) | `dev_cells_long.csv` (long, fresh, old) | long -0.183%, fresh -0.305%, old +0.011% | MATCH | SOURCED |
| 75 | Table Lead 2: 1h sell div retest | `RESULT_LONG.md:28` (`46 / 41, -0.225 [-1.058, +0.608], fresh -0.891, old +0.722`) | `dev_cells_long.csv` (long, fresh, old) | long -0.225%, fresh -0.891%, old +0.722% | MATCH | SOURCED |
| 76 | Strict pooled negative net | `RESULT_LONG.md:30` (`24 of 24 have a negative long net`) | `dev_cells_long.csv` (24 confirmatory strict pooled) | 24 of 24 net < 0 | MATCH | OURS |
| 77 | Proxy buy 15m rsi long | `RESULT_LONG.md:37` (`15m rsi n 230 / 148 days +0.084 [-0.151, +0.318], excess t 1.88`) | `dev_cells_long.csv` (`gate=='reg_bearp'`) | n=230, days=148, net=+0.084%, t=1.88 | MATCH | OURS |
| 78 | Proxy buy 15m div long | `RESULT_LONG.md:37` (`15m div n 75 +0.281 [-0.036, +0.599], excess t 2.63`) | `dev_cells_long.csv` (`gate=='reg_bearp'`) | n=75, net=+0.281%, t=2.63 | MATCH | OURS |
| 79 | Proxy buy 30m rsi / div retest | `RESULT_LONG.md:37` (`30m rsi +0.130, 30m div retest +0.283`) | `dev_cells_long.csv` (`gate=='reg_bearp'`) | rsi +0.130%, div retest +0.283% | MATCH | OURS |
| 80 | Proxy fresh slice 15m rsi / div | `RESULT_LONG.md:37` (`15m rsi fresh n 66 +0.208, 15m div fresh n 19 +0.478`) | `dev_cells_long.csv` (`seg=='fresh'`) | rsi n=66 +0.208%, div n=19 +0.478% | MATCH | OURS |
| 81 | Proxy 1h buy fresh vs old | `RESULT_LONG.md:37` (`fresh +1.27 on n 17, old -1.13 on n 52`) | `dev_cells_long.csv` (`seg=='fresh'`, `seg=='old'`) | fresh n=17 +1.27%, old n=52 -1.13% | MATCH | OURS |
| 82 | Proxy sells 15m / 30m / 1h | `RESULT_LONG.md:37` (`15m -0.134, 30m -0.208, 1h sell div n 17 +0.738`) | `dev_cells_long.csv` (`gate=='reg_bearp'`) | 15m -0.134%, 30m -0.208%, 1h div n=17 +0.738% | MATCH | OURS |

---

## 5. Audit Conclusion

All numerical figures, statistical intervals, test counts, regime distributions, and descriptive statements in `RESULT.md` and `RESULT_LONG.md` have been independently recomputed directly from the raw outputs in `MyTradingSys/research/wavetrend_c30_retest_2026-11-04/*.csv` and confirmed to match with zero discrepancies. The SOURCED vs OURS distinction strictly adheres to repo protocol and operator decision `d-bear-proxy-1104`.

VERDICT: MATCH

<!-- Verification completed on 2026-11-04T19:50:00+05:30 -->

---

## Claude spot-check

Re-derived by a second reader (Claude, Haiku 5.5) from the CSVs on branch `gemini-q/gemini-blind-read-wavetrend-c30-retest-1104`, using a short Python script and not this read's tables. "ALL" in §1.3 means session=ALL; cells 1–3 are gate `with`, which the read leaves implicit. That is a wording point, not a disagreement.

| # | Claim (read location) | Recomputed from CSV | Result |
|---|---|---|---|
| 1 | Retest 15m sell RSI signal: n 257, 170 days (§1.3 #1) | `dev_cells.csv`: tf 15m, side sell, conf rsi, entry signal, session ALL, gate with → n=257, days=170 | AGREE |
| 2 | Same cell win rate 46.69% (120/257) (§1.3 #1) | `hit_net`=0.466926 × 257 = 120 | AGREE |
| 3 | Retest 1h sell div retest: net +1.117%, CI lo +0.007% (§1.3 #3) | `dev_cells.csv`: gate with, entry retest → net=+1.117, ci_lo=+0.007 | AGREE |
| 4 | Long bare 15m buy net −0.115%, CI [−0.192, −0.038] (§4 #71) | `dev_cells_long.csv`: seg long, 15m buy, conf none, entry signal, session ALL, gate all → net=−0.115, CI [−0.192, −0.038] | AGREE |
| 5 | Long proxy arm 15m RSI buy: n 230, 148 days, net +0.084% [−0.151, +0.318] (§4 #77) | `dev_cells_long.csv`: seg long, gate reg_bearp, 15m buy rsi signal ALL → n=230, days=148, net=+0.084, CI [−0.151, +0.318] | AGREE |

Result: 5 of 5 AGREE.

Other checks: every study file the read names exists on the branch. `d-bear-proxy-1104` exists in `MyTradingSys/system/OPERATOR_DECISIONS.md`. The branch changes no study file: its diff against `origin/fast-track` is only this read, its layer-lab report and the card json.

Spot-check verdict: AGREE (5 of 5). The read's MATCH verdict stands.
