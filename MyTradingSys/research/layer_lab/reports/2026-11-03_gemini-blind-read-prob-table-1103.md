# Layer Lab Report: Blind Re-read of `prob_table_1103/RESULT.md` vs `table.csv` and `prob_table_run.py`

- **Task**: `gemini-blind-read-prob-table-1103` (`OURS`)
- **Lane**: `CODEX` (`OURS`)
- **Audited Document**: `MyTradingSys/research/layer_lab/prob_table_1103/RESULT.md` (commit `205876397cfd`, `2026-11-03`, `SOURCED`)
- **Reference Sources**:
  - `MyTradingSys/research/layer_lab/prob_table_1103/table.csv` (`SOURCED`)
  - `MyTradingSys/research/layer_lab/prob_table_1103/cell_quantiles.csv` (`SOURCED`)
  - `MyTradingSys/research/layer_lab/prob_table_1103/prob_table_run.py` (`SOURCED`)
  - `MyTradingSys/backtest/fees.py` (`SOURCED`)
- **Primary Audit Output**: `MyTradingSys/research/gemini_audits_2026-11-04/prob_table_blind_read.md` (`OURS`)
- **Date**: `2026-11-03` (UTC) / `2026-11-04` (local) (`OURS`)
- **Auditor**: Gemini 4 Argon (Medium) worker (`OURS`)

---

## 1. Executive Summary

- **Counts (`prob_table_blind_read.md:1`)**: `FOUND: 94 | DIFF: 0 | NOT_IN_DATA: 0` (`68` table values in `RESULT.md:13-16` + `26` prose/header numbers in `RESULT.md:5-20` = `94` rows checked; `68/68 FOUND` on the 4-row probability table alone, `OURS`).
- **Direct CSV Verification**: Every single quoted number across the 4 rows of `RESULT.md:13-16` (`fit n`, `test n`, `model LL`, `baseline LL`, `LL diff`, `LL 95% CI`, `model EV`, `baseline EV`, `EV diff`, `EV 95% CI`, `trades model/base`, and `cells used`) matches `table.csv:2-5` under the exact formatting rules in `prob_table_run.py:231` (`:.6f` for log-loss metrics, `:.6%` for EV metrics, `OURS`).
- **Scratch Re-run Verification**: Re-running an unmodified scratch copy of `prob_table_run.py` against the local `1m` BTCUSDT kline archives (`C:\MTS_data\dev_ext_2019_2021\klines` for `2020-01`..`2021-12` and `%TEMP%\eagle_1103_um_klines` for `2022-01`..`2024-06`) reproduced `table.csv` and `cell_quantiles.csv` byte-for-byte (`table.csv identical: True`, `cell_quantiles.csv identical: True`, `OURS`).

---

## 2. 4-Row Probability Table Summary (`RESULT.md:13-16` vs `table.csv:2-5`)

1. **Row 1 (`1h`, `Horizon 4`, `RESULT.md:13` vs `table.csv:2`, all `OURS`)**:
   - `Verdict`: `KILL` | `Fit n`: `21685` | `Test n`: `17341`
   - `Model LL`: `0.692440` (`0.6924400931648498`) | `Baseline LL`: `0.693282` (`0.6932822708989366`) | `LL diff [95% CI]`: `-0.000842 [-0.002250, 0.000604]` (`-0.0008421777340868029 [-0.0022497541001755368, 0.0006042221020874051]`)
   - `Model EV`: `0.003330%` (`3.33041573680725e-05`) | `Baseline EV`: `0.000000%` (`0.0`) | `EV diff [95% CI]`: `0.003330% [-0.009297%, 0.019854%]` (`3.33041573680725e-05 [-9.296990539196231e-05, 0.00019853735944595048]`)
   - `Trades model/base`: `1066/0` | `Cells used`: `17302`
2. **Row 2 (`1h`, `Horizon 24`, `RESULT.md:14` vs `table.csv:3`, all `OURS`)**:
   - `Verdict`: `KILL` | `Fit n`: `21665` | `Test n`: `17321`
   - `Model LL`: `0.693450` (`0.6934499749043022`) | `Baseline LL`: `0.694103` (`0.6941030116771781`) | `LL diff [95% CI]`: `-0.000653 [-0.003241, 0.001814]` (`-0.0006530367728758835 [-0.003241154395387005, 0.0018138160220597796]`)
   - `Model EV`: `0.069747%` (`0.0006974663370461001`) | `Baseline EV`: `0.059550%` (`0.0005955034377061361`) | `EV diff [95% CI]`: `0.010196% [-0.062398%, 0.090137%]` (`0.0001019628993399638 [-0.0006239784276813466, 0.00090136902937473]`)
   - `Trades model/base`: `7907/7121` | `Cells used`: `17282`
3. **Row 3 (`4h`, `Horizon 4`, `RESULT.md:15` vs `table.csv:4`, all `OURS`)**:
   - `Verdict`: `KILL` | `Fit n`: `5269` | `Test n`: `4183`
   - `Model LL`: `0.696760` (`0.6967596898283939`) | `Baseline LL`: `0.692971` (`0.6929706730088887`) | `LL diff [95% CI]`: `0.003789 [0.000243, 0.007570]` (`0.003789016819505204 [0.00024311542225081119, 0.00756962373591722]`)
   - `Model EV`: `0.077909%` (`0.0007790947141100292`) | `Baseline EV`: `0.143426%` (`0.001434259759963912`) | `EV diff [95% CI]`: `-0.065517% [-0.181186%, 0.046644%]` (`-0.0006551650458538827 [-0.0018118599966859775, 0.0004664402443621453]`)
   - `Trades model/base`: `1931/2556` | `Cells used`: `4163`
4. **Row 4 (`4h`, `Horizon 24`, `RESULT.md:16` vs `table.csv:5`, all `OURS`)**:
   - `Verdict`: `KILL` | `Fit n`: `5249` | `Test n`: `4163`
   - `Model LL`: `0.689096` (`0.6890956337682148`) | `Baseline LL`: `0.689809` (`0.6898089862632742`) | `LL diff [95% CI]`: `-0.000713 [-0.008240, 0.007183]` (`-0.0007133524950594845 [-0.008240096548260474, 0.007182948331766867]`)
   - `Model EV`: `0.955179%` (`0.009551794369766024`) | `Baseline EV`: `1.145623%` (`0.011456232960132165`) | `EV diff [95% CI]`: `-0.190444% [-0.536473%, 0.149559%]` (`-0.0019044385903661406 [-0.00536472690959895, 0.0014955919402768816]`)
   - `Trades model/base`: `4163/4163` | `Cells used`: `4143`
