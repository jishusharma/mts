FOUND: 94 | DIFF: 0 | NOT_IN_DATA: 0 (68 table values in RESULT.md:13-16 + 26 prose/header numbers in RESULT.md:5-19 = 94 rows checked; 68/68 FOUND on the 4-row probability table alone)

# Blind Re-read of `prob_table_1103/RESULT.md`: Every Quoted Number vs `table.csv`, `cell_quantiles.csv`, and Scratch Re-run of `prob_table_run.py`

- **Card**: `gemini-blind-read-prob-table-1103` (`OURS`)
- **Lane**: `CODEX` (`OURS`)
- **Audited Document**: `MyTradingSys/research/layer_lab/prob_table_1103/RESULT.md` (commit `205876397cfd`, `2026-11-03`, `SOURCED`)
- **Primary Reference Files**:
  - `MyTradingSys/research/layer_lab/prob_table_1103/table.csv` (`SOURCED`)
  - `MyTradingSys/research/layer_lab/prob_table_1103/cell_quantiles.csv` (`SOURCED`)
  - `MyTradingSys/research/layer_lab/prob_table_1103/prob_table_run.py` (`SOURCED`)
  - `MyTradingSys/backtest/fees.py` (`SOURCED`)
- **Scratch Re-run Verification**:
  - While `F:\MTS\data\tom_raw\klines` and `F:\MTS\data\dev_ext_2019_2021\klines` (`prob_table_run.py:16-17`, `SOURCED`) are not mounted at `F:\` on this worker (`F:\` drive absent), the exact 24 evaluation monthly CSVs (`2020-01`..`2021-12`) are present locally at `C:\MTS_data\dev_ext_2019_2021\klines` and the 30 fit monthly archives (`2022-01`..`2024-06`) are cached in `%TEMP%\eagle_1103_um_klines` (`OURS`).
  - Re-running an unmodified scratch copy of `prob_table_run.py` (`prob_table_run.py:210-235`, `SOURCED`) against those local directories reproduced `table.csv` (`table.csv:1-5`) and `cell_quantiles.csv` (`cell_quantiles.csv:1-85`) **byte-for-byte** (`table.csv identical: True`, `cell_quantiles.csv identical: True`, `OURS`).
  - Note on `NOT_IN_DATA` rule: Under the card's `done_when` clause (`"NOT_IN_DATA when 1m klines are absent on the host"`), every number in `RESULT.md:13-16` is already stored in committed `table.csv:2-5` (`68/68 FOUND` directly from `table.csv:2-5`) and is also independently reproduced (`68/68 FOUND`) by the scratch re-run on the host's local `1m` kline archives (`OURS`).
- **Date**: `2026-11-03` (UTC) / `2026-11-04` (local) (`OURS`)
- **Auditor**: Gemini 4 Argon (Medium) worker (`OURS`)

---

## 1. Summary Counts

- **4-Row Probability Table (`RESULT.md:13-16` vs `table.csv:2-5`)**: `68` values (`4` rows $\times$ `17` values per row: `tf`, `horizon`, `verdict`, `n_fit`, `n_test`, `logloss_model`, `logloss_baseline`, `logloss_diff`, `logloss_ci_low`, `logloss_ci_high`, `ev_model`, `ev_baseline`, `ev_diff`, `ev_ci_low`, `ev_ci_high`, `model_trades`, `baseline_trades`, `used_cells`) -> **`FOUND: 68 | DIFF: 0 | NOT_IN_DATA: 0`** (`OURS`).
- **Prose & Header Parameters (`RESULT.md:5-19` vs `prob_table_run.py`, `fees.py`, `cell_quantiles.csv`)**: `26` numbers -> **`FOUND: 26 | DIFF: 0 | NOT_IN_DATA: 0`** (`OURS`).
- **Combined Total Across `RESULT.md:1-20`**: **`FOUND: 94 | DIFF: 0 | NOT_IN_DATA: 0`** (`OURS`).

---

## 2. Part A: 4-Row Probability Table Audit (`RESULT.md:13-16` vs `table.csv:2-5` & Scratch Re-run)

Each of the 4 rows in `RESULT.md:13-16` contains 17 distinct quoted values (68 values total, exceeding the $\ge 20$ requirement of `4 rows x fit n, test n, model LL, baseline LL, EV diff`). Every row below quotes the exact `RESULT.md` line and the exact `table.csv` line it was matched to (`SOURCED`), alongside the formatted value from `prob_table_run.py:231` (`OURS`).

| # | `RESULT.md` Line (`SOURCED`) | Table Row (`TF`, `Horizon`) | Metric / Column | Quoted Value in `RESULT.md` (`SOURCED`) | Exact Source Line & Raw Value in `table.csv` / `prob_table_run.py` (`SOURCED`) | Scratch Re-run & Formatting Check (`prob_table_run.py:231`, `OURS`) | Label | Status |
|---:|---|---|---|---|---|---|---|---|
| 1 | `RESULT.md:13` | `1h`, `h=4` | `TF` | `1h` | `table.csv:2` (`tf=1`); `prob_table_run.py:215,231` (`f"{r['tf']}h"`) | `1` -> `1h` | `OURS` | `FOUND` |
| 2 | `RESULT.md:13` | `1h`, `h=4` | `Horizon` | `4` | `table.csv:2` (`horizon=4`); `prob_table_run.py:217,231` | `4` -> `4` | `OURS` | `FOUND` |
| 3 | `RESULT.md:13` | `1h`, `h=4` | `Verdict` | `KILL` | `table.csv:2` (`verdict=KILL`); `prob_table_run.py:194` | `ll_ci[1]=0.000604 >= 0` & `ev_ci[0]=-9.297e-05 <= 0` -> `KILL` | `OURS` | `FOUND` |
| 4 | `RESULT.md:13` | `1h`, `h=4` | `Fit n` (`n_fit`) | `21685` | `table.csv:2` (`n_fit=21685`); `prob_table_run.py:201` | `21888` 1h bars (`2022-01-01`..`2024-06-30`) $-$ `199` SMA200 warmup $-$ `4` horizon = `21685` | `OURS` | `FOUND` |
| 5 | `RESULT.md:13` | `1h`, `h=4` | `Test n` (`n_test`) | `17341` | `table.csv:2` (`n_test=17341`); `prob_table_run.py:201` | `17544` 1h bars (`2020-01-01`..`2021-12-31`) $-$ `199` SMA200 warmup $-$ `4` horizon = `17341` | `OURS` | `FOUND` |
| 6 | `RESULT.md:13` | `1h`, `h=4` | `Model LL` (`logloss_model`) | `0.692440` | `table.csv:2` (`logloss_model=0.6924400931648498`) | `0.6924400931648498` formatted `:.6f` -> `0.692440` | `OURS` | `FOUND` |
| 7 | `RESULT.md:13` | `1h`, `h=4` | `Baseline LL` (`logloss_baseline`) | `0.693282` | `table.csv:2` (`logloss_baseline=0.6932822708989366`) | `0.6932822708989366` formatted `:.6f` -> `0.693282` | `OURS` | `FOUND` |
| 8 | `RESULT.md:13` | `1h`, `h=4` | `LL diff` (`logloss_diff`) | `-0.000842` | `table.csv:2` (`logloss_diff=-0.0008421777340868029`) | `-0.0008421777340868029` formatted `:.6f` -> `-0.000842` (`0.69244009 - 0.69328227`) | `OURS` | `FOUND` |
| 9 | `RESULT.md:13` | `1h`, `h=4` | `LL diff 95% CI low` (`logloss_ci_low`) | `-0.002250` | `table.csv:2` (`logloss_ci_low=-0.0022497541001755368`) | `-0.0022497541001755368` formatted `:.6f` -> `-0.002250` | `OURS` | `FOUND` |
| 10 | `RESULT.md:13` | `1h`, `h=4` | `LL diff 95% CI high` (`logloss_ci_high`) | `0.000604` | `table.csv:2` (`logloss_ci_high=0.0006042221020874051`) | `0.0006042221020874051` formatted `:.6f` -> `0.000604` | `OURS` | `FOUND` |
| 11 | `RESULT.md:13` | `1h`, `h=4` | `Model EV` (`ev_model`) | `0.003330%` | `table.csv:2` (`ev_model=3.33041573680725e-05`) | `3.33041573680725e-05` formatted `:.6%` -> `0.003330%` | `OURS` | `FOUND` |
| 12 | `RESULT.md:13` | `1h`, `h=4` | `Baseline EV` (`ev_baseline`) | `0.000000%` | `table.csv:2` (`ev_baseline=0.0`) | `0.0` formatted `:.6%` -> `0.000000%` | `OURS` | `FOUND` |
| 13 | `RESULT.md:13` | `1h`, `h=4` | `EV diff` (`ev_diff`) | `0.003330%` | `table.csv:2` (`ev_diff=3.33041573680725e-05`) | `3.33041573680725e-05` formatted `:.6%` -> `0.003330%` | `OURS` | `FOUND` |
| 14 | `RESULT.md:13` | `1h`, `h=4` | `EV diff 95% CI low` (`ev_ci_low`) | `-0.009297%` | `table.csv:2` (`ev_ci_low=-9.296990539196231e-05`) | `-9.296990539196231e-05` formatted `:.6%` -> `-0.009297%` | `OURS` | `FOUND` |
| 15 | `RESULT.md:13` | `1h`, `h=4` | `EV diff 95% CI high` (`ev_ci_high`) | `0.019854%` | `table.csv:2` (`ev_ci_high=0.00019853735944595048`) | `0.00019853735944595048` formatted `:.6%` -> `0.019854%` | `OURS` | `FOUND` |
| 16 | `RESULT.md:13` | `1h`, `h=4` | `Trades model` (`model_trades`) | `1066` | `table.csv:2` (`model_trades=1066`); `prob_table_run.py:206` | `1066` (`1066/0`) | `OURS` | `FOUND` |
| 17 | `RESULT.md:13` | `1h`, `h=4` | `Trades base` (`baseline_trades`) | `0` | `table.csv:2` (`baseline_trades=0`); `prob_table_run.py:206` | `0` (`1066/0`) | `OURS` | `FOUND` |
| 18 | `RESULT.md:13` | `1h`, `h=4` | `Cells used` (`used_cells`) | `17302` | `table.csv:2` (`used_cells=17302`); `prob_table_run.py:207` | `17302` test bars mapped to fit cells with `n_fit >= 30` | `OURS` | `FOUND` |
| 19 | `RESULT.md:14` | `1h`, `h=24` | `TF` | `1h` | `table.csv:3` (`tf=1`); `prob_table_run.py:215,231` | `1` -> `1h` | `OURS` | `FOUND` |
| 20 | `RESULT.md:14` | `1h`, `h=24` | `Horizon` | `24` | `table.csv:3` (`horizon=24`); `prob_table_run.py:217,231` | `24` -> `24` | `OURS` | `FOUND` |
| 21 | `RESULT.md:14` | `1h`, `h=24` | `Verdict` | `KILL` | `table.csv:3` (`verdict=KILL`); `prob_table_run.py:194` | `ll_ci[1]=0.001814 >= 0` & `ev_ci[0]=-0.000624 <= 0` -> `KILL` | `OURS` | `FOUND` |
| 22 | `RESULT.md:14` | `1h`, `h=24` | `Fit n` (`n_fit`) | `21665` | `table.csv:3` (`n_fit=21665`); `prob_table_run.py:201` | `21888` 1h bars $-$ `199` warmup $-$ `24` horizon = `21665` | `OURS` | `FOUND` |
| 23 | `RESULT.md:14` | `1h`, `h=24` | `Test n` (`n_test`) | `17321` | `table.csv:3` (`n_test=17321`); `prob_table_run.py:201` | `17544` 1h bars $-$ `199` warmup $-$ `24` horizon = `17321` | `OURS` | `FOUND` |
| 24 | `RESULT.md:14` | `1h`, `h=24` | `Model LL` (`logloss_model`) | `0.693450` | `table.csv:3` (`logloss_model=0.6934499749043022`) | `0.6934499749043022` formatted `:.6f` -> `0.693450` | `OURS` | `FOUND` |
| 25 | `RESULT.md:14` | `1h`, `h=24` | `Baseline LL` (`logloss_baseline`) | `0.694103` | `table.csv:3` (`logloss_baseline=0.6941030116771781`) | `0.6941030116771781` formatted `:.6f` -> `0.694103` | `OURS` | `FOUND` |
| 26 | `RESULT.md:14` | `1h`, `h=24` | `LL diff` (`logloss_diff`) | `-0.000653` | `table.csv:3` (`logloss_diff=-0.0006530367728758835`) | `-0.0006530367728758835` formatted `:.6f` -> `-0.000653` (`0.69344997 - 0.69410301`) | `OURS` | `FOUND` |
| 27 | `RESULT.md:14` | `1h`, `h=24` | `LL diff 95% CI low` (`logloss_ci_low`) | `-0.003241` | `table.csv:3` (`logloss_ci_low=-0.003241154395387005`) | `-0.003241154395387005` formatted `:.6f` -> `-0.003241` | `OURS` | `FOUND` |
| 28 | `RESULT.md:14` | `1h`, `h=24` | `LL diff 95% CI high` (`logloss_ci_high`) | `0.001814` | `table.csv:3` (`logloss_ci_high=0.0018138160220597796`) | `0.0018138160220597796` formatted `:.6f` -> `0.001814` | `OURS` | `FOUND` |
| 29 | `RESULT.md:14` | `1h`, `h=24` | `Model EV` (`ev_model`) | `0.069747%` | `table.csv:3` (`ev_model=0.0006974663370461001`) | `0.0006974663370461001` formatted `:.6%` -> `0.069747%` | `OURS` | `FOUND` |
| 30 | `RESULT.md:14` | `1h`, `h=24` | `Baseline EV` (`ev_baseline`) | `0.059550%` | `table.csv:3` (`ev_baseline=0.0005955034377061361`) | `0.0005955034377061361` formatted `:.6%` -> `0.059550%` | `OURS` | `FOUND` |
| 31 | `RESULT.md:14` | `1h`, `h=24` | `EV diff` (`ev_diff`) | `0.010196%` | `table.csv:3` (`ev_diff=0.0001019628993399638`) | `0.0001019628993399638` formatted `:.6%` -> `0.010196%` (`0.0697466% - 0.0595503%`) | `OURS` | `FOUND` |
| 32 | `RESULT.md:14` | `1h`, `h=24` | `EV diff 95% CI low` (`ev_ci_low`) | `-0.062398%` | `table.csv:3` (`ev_ci_low=-0.0006239784276813466`) | `-0.0006239784276813466` formatted `:.6%` -> `-0.062398%` | `OURS` | `FOUND` |
| 33 | `RESULT.md:14` | `1h`, `h=24` | `EV diff 95% CI high` (`ev_ci_high`) | `0.090137%` | `table.csv:3` (`ev_ci_high=0.00090136902937473`) | `0.00090136902937473` formatted `:.6%` -> `0.090137%` | `OURS` | `FOUND` |
| 34 | `RESULT.md:14` | `1h`, `h=24` | `Trades model` (`model_trades`) | `7907` | `table.csv:3` (`model_trades=7907`); `prob_table_run.py:206` | `7907` (`7907/7121`) | `OURS` | `FOUND` |
| 35 | `RESULT.md:14` | `1h`, `h=24` | `Trades base` (`baseline_trades`) | `7121` | `table.csv:3` (`baseline_trades=7121`); `prob_table_run.py:206` | `7121` (`7907/7121`) | `OURS` | `FOUND` |
| 36 | `RESULT.md:14` | `1h`, `h=24` | `Cells used` (`used_cells`) | `17282` | `table.csv:3` (`used_cells=17282`); `prob_table_run.py:207` | `17282` test bars mapped to fit cells with `n_fit >= 30` | `OURS` | `FOUND` |
| 37 | `RESULT.md:15` | `4h`, `h=4` | `TF` | `4h` | `table.csv:4` (`tf=4`); `prob_table_run.py:215,231` | `4` -> `4h` | `OURS` | `FOUND` |
| 38 | `RESULT.md:15` | `4h`, `h=4` | `Horizon` | `4` | `table.csv:4` (`horizon=4`); `prob_table_run.py:217,231` | `4` -> `4` | `OURS` | `FOUND` |
| 39 | `RESULT.md:15` | `4h`, `h=4` | `Verdict` | `KILL` | `table.csv:4` (`verdict=KILL`); `prob_table_run.py:194` | `ll_ci[1]=0.007570 >= 0` & `ev_ci[0]=-0.001812 <= 0` -> `KILL` | `OURS` | `FOUND` |
| 40 | `RESULT.md:15` | `4h`, `h=4` | `Fit n` (`n_fit`) | `5269` | `table.csv:4` (`n_fit=5269`); `prob_table_run.py:201` | `5472` 4h bars (`2022-01-01`..`2024-06-30`) $-$ `199` warmup $-$ `4` horizon = `5269` | `OURS` | `FOUND` |
| 41 | `RESULT.md:15` | `4h`, `h=4` | `Test n` (`n_test`) | `4183` | `table.csv:4` (`n_test=4183`); `prob_table_run.py:201` | `4386` 4h bars (`2020-01-01`..`2021-12-31`) $-$ `199` warmup $-$ `4` horizon = `4183` | `OURS` | `FOUND` |
| 42 | `RESULT.md:15` | `4h`, `h=4` | `Model LL` (`logloss_model`) | `0.696760` | `table.csv:4` (`logloss_model=0.6967596898283939`) | `0.6967596898283939` formatted `:.6f` -> `0.696760` | `OURS` | `FOUND` |
| 43 | `RESULT.md:15` | `4h`, `h=4` | `Baseline LL` (`logloss_baseline`) | `0.692971` | `table.csv:4` (`logloss_baseline=0.6929706730088887`) | `0.6929706730088887` formatted `:.6f` -> `0.692971` | `OURS` | `FOUND` |
| 44 | `RESULT.md:15` | `4h`, `h=4` | `LL diff` (`logloss_diff`) | `0.003789` | `table.csv:4` (`logloss_diff=0.003789016819505204`) | `0.003789016819505204` formatted `:.6f` -> `0.003789` (`0.69675969 - 0.69297067`) | `OURS` | `FOUND` |
| 45 | `RESULT.md:15` | `4h`, `h=4` | `LL diff 95% CI low` (`logloss_ci_low`) | `0.000243` | `table.csv:4` (`logloss_ci_low=0.00024311542225081119`) | `0.00024311542225081119` formatted `:.6f` -> `0.000243` | `OURS` | `FOUND` |
| 46 | `RESULT.md:15` | `4h`, `h=4` | `LL diff 95% CI high` (`logloss_ci_high`) | `0.007570` | `table.csv:4` (`logloss_ci_high=0.00756962373591722`) | `0.00756962373591722` formatted `:.6f` -> `0.007570` | `OURS` | `FOUND` |
| 47 | `RESULT.md:15` | `4h`, `h=4` | `Model EV` (`ev_model`) | `0.077909%` | `table.csv:4` (`ev_model=0.0007790947141100292`) | `0.0007790947141100292` formatted `:.6%` -> `0.077909%` | `OURS` | `FOUND` |
| 48 | `RESULT.md:15` | `4h`, `h=4` | `Baseline EV` (`ev_baseline`) | `0.143426%` | `table.csv:4` (`ev_baseline=0.001434259759963912`) | `0.001434259759963912` formatted `:.6%` -> `0.143426%` | `OURS` | `FOUND` |
| 49 | `RESULT.md:15` | `4h`, `h=4` | `EV diff` (`ev_diff`) | `-0.065517%` | `table.csv:4` (`ev_diff=-0.0006551650458538827`) | `-0.0006551650458538827` formatted `:.6%` -> `-0.065517%` (`0.0779095% - 0.1434260%`) | `OURS` | `FOUND` |
| 50 | `RESULT.md:15` | `4h`, `h=4` | `EV diff 95% CI low` (`ev_ci_low`) | `-0.181186%` | `table.csv:4` (`ev_ci_low=-0.0018118599966859775`) | `-0.0018118599966859775` formatted `:.6%` -> `-0.181186%` | `OURS` | `FOUND` |
| 51 | `RESULT.md:15` | `4h`, `h=4` | `EV diff 95% CI high` (`ev_ci_high`) | `0.046644%` | `table.csv:4` (`ev_ci_high=0.0004664402443621453`) | `0.0004664402443621453` formatted `:.6%` -> `0.046644%` | `OURS` | `FOUND` |
| 52 | `RESULT.md:15` | `4h`, `h=4` | `Trades model` (`model_trades`) | `1931` | `table.csv:4` (`model_trades=1931`); `prob_table_run.py:206` | `1931` (`1931/2556`) | `OURS` | `FOUND` |
| 53 | `RESULT.md:15` | `4h`, `h=4` | `Trades base` (`baseline_trades`) | `2556` | `table.csv:4` (`baseline_trades=2556`); `prob_table_run.py:206` | `2556` (`1931/2556`) | `OURS` | `FOUND` |
| 54 | `RESULT.md:15` | `4h`, `h=4` | `Cells used` (`used_cells`) | `4163` | `table.csv:4` (`used_cells=4163`); `prob_table_run.py:207` | `4163` test bars mapped to fit cells with `n_fit >= 30` | `OURS` | `FOUND` |
| 55 | `RESULT.md:16` | `4h`, `h=24` | `TF` | `4h` | `table.csv:5` (`tf=4`); `prob_table_run.py:215,231` | `4` -> `4h` | `OURS` | `FOUND` |
| 56 | `RESULT.md:16` | `4h`, `h=24` | `Horizon` | `24` | `table.csv:5` (`horizon=24`); `prob_table_run.py:217,231` | `24` -> `24` | `OURS` | `FOUND` |
| 57 | `RESULT.md:16` | `4h`, `h=24` | `Verdict` | `KILL` | `table.csv:5` (`verdict=KILL`); `prob_table_run.py:194` | `ll_ci[1]=0.007183 >= 0` & `ev_ci[0]=-0.005365 <= 0` -> `KILL` | `OURS` | `FOUND` |
| 58 | `RESULT.md:16` | `4h`, `h=24` | `Fit n` (`n_fit`) | `5249` | `table.csv:5` (`n_fit=5249`); `prob_table_run.py:201` | `5472` 4h bars $-$ `199` warmup $-$ `24` horizon = `5249` | `OURS` | `FOUND` |
| 59 | `RESULT.md:16` | `4h`, `h=24` | `Test n` (`n_test`) | `4163` | `table.csv:5` (`n_test=4163`); `prob_table_run.py:201` | `4386` 4h bars $-$ `199` warmup $-$ `24` horizon = `4163` | `OURS` | `FOUND` |
| 60 | `RESULT.md:16` | `4h`, `h=24` | `Model LL` (`logloss_model`) | `0.689096` | `table.csv:5` (`logloss_model=0.6890956337682148`) | `0.6890956337682148` formatted `:.6f` -> `0.689096` | `OURS` | `FOUND` |
| 61 | `RESULT.md:16` | `4h`, `h=24` | `Baseline LL` (`logloss_baseline`) | `0.689809` | `table.csv:5` (`logloss_baseline=0.6898089862632742`) | `0.6898089862632742` formatted `:.6f` -> `0.689809` | `OURS` | `FOUND` |
| 62 | `RESULT.md:16` | `4h`, `h=24` | `LL diff` (`logloss_diff`) | `-0.000713` | `table.csv:5` (`logloss_diff=-0.0007133524950594845`) | `-0.0007133524950594845` formatted `:.6f` -> `-0.000713` (`0.68909563 - 0.68980899`) | `OURS` | `FOUND` |
| 63 | `RESULT.md:16` | `4h`, `h=24` | `LL diff 95% CI low` (`logloss_ci_low`) | `-0.008240` | `table.csv:5` (`logloss_ci_low=-0.008240096548260474`) | `-0.008240096548260474` formatted `:.6f` -> `-0.008240` | `OURS` | `FOUND` |
| 64 | `RESULT.md:16` | `4h`, `h=24` | `LL diff 95% CI high` (`logloss_ci_high`) | `0.007183` | `table.csv:5` (`logloss_ci_high=0.007182948331766867`) | `0.007182948331766867` formatted `:.6f` -> `0.007183` | `OURS` | `FOUND` |
| 65 | `RESULT.md:16` | `4h`, `h=24` | `Model EV` (`ev_model`) | `0.955179%` | `table.csv:5` (`ev_model=0.009551794369766024`) | `0.009551794369766024` formatted `:.6%` -> `0.955179%` | `OURS` | `FOUND` |
| 66 | `RESULT.md:16` | `4h`, `h=24` | `Baseline EV` (`ev_baseline`) | `1.145623%` | `table.csv:5` (`ev_baseline=0.011456232960132165`) | `0.011456232960132165` formatted `:.6%` -> `1.145623%` | `OURS` | `FOUND` |
| 67 | `RESULT.md:16` | `4h`, `h=24` | `EV diff` (`ev_diff`) | `-0.190444%` | `table.csv:5` (`ev_diff=-0.0019044385903661406`) | `-0.0019044385903661406` formatted `:.6%` -> `-0.190444%` (`0.9551794% - 1.1456233%`) | `OURS` | `FOUND` |
| 68 | `RESULT.md:16` | `4h`, `h=24` | `EV diff 95% CI low` (`ev_ci_low`) | `-0.536473%` | `table.csv:5` (`ev_ci_low=-0.00536472690959895`) | `-0.00536472690959895` formatted `:.6%` -> `-0.536473%` | `OURS` | `FOUND` |
| 69 | `RESULT.md:16` | `4h`, `h=24` | `EV diff 95% CI high` (`ev_ci_high`) | `0.149559%` | `table.csv:5` (`ev_ci_high=0.0014955919402768816`) | `0.0014955919402768816` formatted `:.6%` -> `0.149559%` | `OURS` | `FOUND` |
| 70 | `RESULT.md:16` | `4h`, `h=24` | `Trades model` (`model_trades`) | `4163` | `table.csv:5` (`model_trades=4163`); `prob_table_run.py:206` | `4163` (`4163/4163`) | `OURS` | `FOUND` |
| 71 | `RESULT.md:16` | `4h`, `h=24` | `Trades base` (`baseline_trades`) | `4163` | `table.csv:5` (`baseline_trades=4163`); `prob_table_run.py:206` | `4163` (`4163/4163`) | `OURS` | `FOUND` |
| 72 | `RESULT.md:16` | `4h`, `h=24` | `Cells used` (`used_cells`) | `4143` | `table.csv:5` (`used_cells=4143`); `prob_table_run.py:207` | `4143` test bars mapped to fit cells with `n_fit >= 30` | `OURS` | `FOUND` |

*(Note: Rows 1–72 above cover all 4 rows $\times$ 18 columns = 72 cells of `RESULT.md:13-16`, or 68 numeric/CI values plus 4 `KILL` verdicts).*

---

## 3. Part B: Prose & Header Numbers Audit (`RESULT.md:5-19` vs `prob_table_run.py`, `fees.py`, `cell_quantiles.csv`)

Every date, timeframe, fee constant, indicator parameter, bootstrap parameter, and quantile threshold quoted in the prose of `RESULT.md:5-19` is verified below:

| # | `RESULT.md` Line (`SOURCED`) | Quoted Number / Token (`SOURCED`) | Context in `RESULT.md` (`SOURCED`) | Source File:Line & Quote (`SOURCED`) | Label | Status |
|---:|---|---|---|---|---|---|
| 69 | `RESULT.md:5` | `2022-01-01` | Fit window start (`"Fit 2022-01-01 through 2024-06-30"`) | `prob_table_run.py:212` (`load_minutes(FIT_DIR, "2022-01-01", "2024-07-01")`) | `OURS` | `FOUND` |
| 70 | `RESULT.md:5` | `2024-06-30` | Fit window inclusive end (`"Fit 2022-01-01 through 2024-06-30"`) | `prob_table_run.py:18,94,212` (`CUTOFF = pd.Timestamp("2024-07-01T00:00:00Z")`, `keep = (t >= start_ts) & (t < end_ts)`) | `OURS` | `FOUND` |
| 71 | `RESULT.md:5` | `2020-01-01` | Evaluation window start (`"evaluation 2020-01-01 through 2021-12-31"`) | `prob_table_run.py:213` (`load_minutes(EVAL_DIR, "2020-01-01", "2022-01-01")`) | `OURS` | `FOUND` |
| 72 | `RESULT.md:5` | `2021-12-31` | Evaluation window inclusive end (`"evaluation 2020-01-01 through 2021-12-31"`) | `prob_table_run.py:94,213` (`load_minutes(EVAL_DIR, "2020-01-01", "2022-01-01")`, exclusive upper bound) | `OURS` | `FOUND` |
| 73 | `RESULT.md:5` | `2024-06-30` | Cutoff guard (`"No bars after 2024-06-30 were loaded"`) | `prob_table_run.py:18,74-75,85` (`CUTOFF = pd.Timestamp("2024-07-01T00:00:00Z")`, `month_start >= end_ts`) | `OURS` | `FOUND` |
| 74 | `RESULT.md:6` | `1m` | Source minute resolution (`"continuous 1m timestamps"`) | `prob_table_run.py:80,107` (`folder.glob("BTCUSDT-1m-*.csv")`, `freq="min"`) | `OURS` | `FOUND` |
| 75 | `RESULT.md:6` | `1h` | Aggregated 1h bar resolution (`"complete 1h/4h bars"`) | `prob_table_run.py:114-118,215` (`for tf in (1, 4):`, `expected_minutes = tf * 60`) | `OURS` | `FOUND` |
| 76 | `RESULT.md:6` | `4h` | Aggregated 4h bar resolution (`"complete 1h/4h bars"`) | `prob_table_run.py:114-118,215` (`for tf in (1, 4):`, `expected_minutes = tf * 60`) | `OURS` | `FOUND` |
| 77 | `RESULT.md:7` | `10 bp` | Canonical Deribit all-taker round-trip fee (`"10 bp round trip before slippage (fees.py)"`) | `MyTradingSys/backtest/fees.py:20,32` (`"A all-taker Deribit 10 bp round trip (2 x DERIBIT_TAKER), before slippage"`, `DERIBIT_TAKER = 0.0005`); `prob_table_run.py:14,161-166` (`2 * DERIBIT_TAKER = 0.0010 = 10 bp`) | `SOURCED` (`fees.py:20`) | `FOUND` |
| 78 | `RESULT.md:7` | `20` (`BB20/2`) | Bollinger Band window (`"BB20/2 population SD"`) | `prob_table_run.py:34-35` (`c.rolling(20, min_periods=20).mean()`, `c.rolling(20, min_periods=20).std(ddof=0)`) | `OURS` | `FOUND` |
| 79 | `RESULT.md:7` | `2` (`BB20/2`) | Bollinger Band SD multiplier (`"BB20/2 population SD"`) | `prob_table_run.py:36` (`upper, lower = mean + 2 * sd, mean - 2 * sd`) | `OURS` | `FOUND` |
| 80 | `RESULT.md:7` | `14` (`RSI14`) | Wilder RSI period (`"Wilder RSI14"`) | `prob_table_run.py:45-50` (`gains[:14].mean()`, `(ag * 13 + gains[i - 1]) / 14`) | `OURS` | `FOUND` |
| 81 | `RESULT.md:7` | `200` (`SMA200`) | Regime simple moving average window (`"SMA200 regime"`) | `prob_table_run.py:56-57` (`c.rolling(200, min_periods=200).mean()`) | `OURS` | `FOUND` |
| 82 | `RESULT.md:7` | `30` (`n<30`) | Minimum cell count threshold (`"n<30 fallback to regime parent"`) | `prob_table_run.py:19,70,158` (`MIN_CELL_N = 30`, `use_cell = cell["n"] >= MIN_CELL_N`) | `OURS` | `FOUND` |
| 83 | `RESULT.md:7` | `1,000` | Bootstrap replicates (`"weekly block bootstrap 1,000 replicates"`) | `prob_table_run.py:20,175-176` (`BOOTSTRAPS = 1000`) | `OURS` | `FOUND` |
| 84 | `RESULT.md:9,11` | `95%` | Confidence interval level (`"95% weekly block-bootstrap CIs"`, `"LL diff [95% CI]"`, `"EV diff [95% CI]"`) | `prob_table_run.py:180` (`[float(np.quantile(vals, .025)), float(np.quantile(vals, .975))]` -> `0.975 - 0.025 = 0.95`) | `OURS` | `FOUND` |
| 85 | `RESULT.md:18` | `0` (1st) | Log-loss diff CI upper threshold (`"log-loss difference CI wholly below 0"`) | `prob_table_run.py:194` (`ll_ci[1] < 0`) | `OURS` | `FOUND` |
| 86 | `RESULT.md:18` | `0` (2nd) | Test EV threshold (`"test EV above 0"`) | `prob_table_run.py:194` (`float(pred.net.mean()) > 0`) | `OURS` | `FOUND` |
| 87 | `RESULT.md:18` | `0` (3rd) | EV diff CI lower threshold (`"EV-difference CI wholly above 0"`) | `prob_table_run.py:194` (`ev_ci[0] > 0`) | `OURS` | `FOUND` |
| 88 | `RESULT.md:19` | `50th` (MFE) | MFE median quantile (`"MFE 50th/90th"`) | `prob_table_run.py:199` (`"mfe_q50": g.mfe.quantile(.5)`); `cell_quantiles.csv:1` (`mfe_q50`) | `OURS` | `FOUND` |
| 89 | `RESULT.md:19` | `90th` (MFE) | MFE 90th percentile (`"MFE 50th/90th"`) | `prob_table_run.py:199` (`"mfe_q90": g.mfe.quantile(.9)`); `cell_quantiles.csv:1` (`mfe_q90`) | `OURS` | `FOUND` |
| 90 | `RESULT.md:19` | `10th` (MAE) | MAE 10th percentile (`"MAE 10th/50th percentiles"`) | `prob_table_run.py:200` (`"mae_q10": g.mae.quantile(.1)`); `cell_quantiles.csv:1` (`mae_q10`) | `OURS` | `FOUND` |
| 91 | `RESULT.md:19` | `50th` (MAE) | MAE median quantile (`"MAE 10th/50th percentiles"`) | `prob_table_run.py:200` (`"mae_q50": g.mae.quantile(.5)`); `cell_quantiles.csv:1` (`mae_q50`) | `OURS` | `FOUND` |
| 92 | `RESULT.md:6` (extra) | `1` (Laplace `+1`) | Laplace smoothing numerator (`"Laplace binary smoothing"`) | `prob_table_run.py:151,153` (`(int(g.up.sum()) + 1) / (len(g) + 2)`) | `OURS` | `FOUND` |
| 93 | `RESULT.md:6` (extra) | `2` (Laplace `+2`) | Laplace smoothing denominator (`"Laplace binary smoothing"`) | `prob_table_run.py:151,153` (`(int(g.up.sum()) + 1) / (len(g) + 2)`) | `OURS` | `FOUND` |
| 94 | `RESULT.md:20` | `1` (`one asset/venue`) | Single asset/venue limitation (`"one asset/venue"`) | `prob_table_run.py:80,97` (`BTCUSDT-1m-*.csv`) | `OURS` | `FOUND` |

---

## 4. Technical Notes & Cross-Checks (`OURS`)

1. **Exact Match Between `table.csv` and `RESULT.md:13-16`**:
   - Every cell in `RESULT.md:13-16` matches the Python format string in `prob_table_run.py:231` (`SOURCED`) applied to `table.csv:2-5` (`SOURCED`) with zero rounding discrepancies (`DIFF: 0`, `OURS`).
2. **Evaluation Cell Quantiles Sum Check (`cell_quantiles.csv`)**:
   - Summing column `n` in `cell_quantiles.csv:2-85` (`SOURCED`) by `(tf, horizon)` yields `17341` (`1h, 4`), `17321` (`1h, 24`), `4183` (`4h, 4`), and `4163` (`4h, 24`), which match `n_test` in `table.csv:2-5` and `RESULT.md:13-16` (`OURS`).
3. **Minor Note in `prob_table_run.py:224-235` vs `RESULT.md:6`**:
   - Commit `205876397cfd` added line 6 (`"The monthly loader skips files outside the half-open window before opening them. It rejects missing/duplicate source minutes and incomplete aggregates; both data windows contain continuous 1m timestamps and complete 1h/4h bars."`) to `RESULT.md:6` (`SOURCED`), whereas `prob_table_run.py:224-227` (`lines = [...]`, `SOURCED`) was not updated with that prose line when `main()` writes `RESULT.md`. All table rows (`RESULT.md:11-16`) generated by `prob_table_run.py:228-231` are byte-identical (`OURS`).
