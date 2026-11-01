# Independent VP Return-to-Value Recount (`gpt-rederive-tom-vp-return-to-value`)

- **Card**: `gpt-rederive-tom-vp-return-to-value`
- **Audited file**: `MyTradingSys/research/tom_transfer_2026-10-11/vp_return/RESULT.md`
- **Definitions read**: `MyTradingSys/research/tom_transfer_2026-10-11/vp_return/PRE_REG.md:12-22,42` and `MyTradingSys/backtest/layers/FORMULAS.md:422-437,482-489` (sections 18.1, 18.6, 18.7)
- **DEV data used**: 30 monthly BTCUSDT 1m archives (`2022-01`..`2024-06`) under `F:/MTS/data/candle_close_dev_2022_2024/` (912 complete UTC days `2022-01-01`..`2024-06-30`; 911 evaluated days `2022-01-02`..`2024-06-30`; 0 post-`2024-06-30` bars read)

## Headline Numbers Comparison (`RESULT.md` vs Independent Recount)

| Metric (`RESULT.md` location) | `RESULT.md` value | Independent value | Status | Evidence (`file:line` & exact counts) |
|---|---|---|---|---|
| Evaluated DEV UTC days (`RESULT.md:4`) | `911` | `911` (`912` total complete days `2022-01-01..2024-06-30`, day 0 provides prior-day profile) | `SAME` | `RESULT.md:4`, `PRE_REG.md:13,42` |
| Part A Real prior-day value events & return share (`RESULT.md:8,15`) | `871` events, `57.2%` | `498 / 871 = 57.1757%` (`57.2%`) | `SAME` | `RESULT.md:8,15`, `PRE_REG.md:13-15`, `FORMULAS.md:422-431` |
| Part A Placebo shifted `d x ATR14` events & return share (`RESULT.md:8,16`) | `883` events, `46.8%` | `413 / 883 = 46.7724%` (`46.8%`) | `SAME` | `RESULT.md:8,16`, `PRE_REG.md:17`, `FORMULAS.md:482-484` (`d` indexed by `day_index mod 8` across the 912-day array, so `2022-01-02` starts at `day_index = 1`) |
| Part A Real minus placebo difference (`RESULT.md:8,17`) | `+10.4 pp` | `57.1757% - 46.7724% = +10.4033 pp` (`+10.4 pp`) | `SAME` | `RESULT.md:8,17`, `PRE_REG.md:22` |
| Part A Fire rate real / placebo (`RESULT.md:19`) | `95.6%` / `96.9%` | `871 / 911 = 95.6092%` (`95.6%`) / `883 / 911 = 96.9265%` (`96.9%`) | `SAME` | `RESULT.md:19`, `PRE_REG.md:34` |
| Part B `N=3` Applicable / Accepted / Return share / Placebo (`RESULT.md:53`) | `871` / `603` / `51.2%` / `42.6%` | `871` applicable, `309 / 603 = 51.2438%` (`51.2%`), placebo `309 / 726 = 42.5620%` (`42.6%`), diff `+8.6818 pp` (`+8.7 pp`), minus Part A `-5.9319 pp` (`-5.9 pp`) | `SAME` | `RESULT.md:53`, `PRE_REG.md:18` |
| Part B `N=6` Applicable / Accepted / Return share / Placebo (`RESULT.md:54`) | `869` / `490` / `47.8%` / `39.9%` | `869` applicable, `234 / 490 = 47.7551%` (`47.8%`), placebo `263 / 659 = 39.9090%` (`39.9%`), diff `+7.8461 pp` (`+7.8 pp`), minus Part A `-9.4206 pp` (`-9.4 pp`) | `SAME` | `RESULT.md:54`, `PRE_REG.md:18` |
| Part B `N=12` Applicable / Accepted / Return share / Placebo (`RESULT.md:55`) | `867` / `387` / `45.5%` / `36.6%` | `867` applicable, `176 / 387 = 45.4780%` (`45.5%`), placebo `217 / 593 = 36.5936%` (`36.6%`), diff `+8.8844 pp` (`+8.9 pp`), minus Part A `-11.6976 pp` (`-11.7 pp`) | `SAME` | `RESULT.md:55`, `PRE_REG.md:18` |

## Per-`d` Placebo Breakdown (`RESULT.md:38-45`)

| `d` (`RESULT.md` location) | `RESULT.md` events & return share | Independent events & return share | Status | Evidence |
|---|---|---|---|---|
| `d = -3.0` (`RESULT.md:38`) | `109` events, `33.9%` | `37 / 109 = 33.9450%` (`33.9%`) | `SAME` | `RESULT.md:38`, `PRE_REG.md:17` |
| `d = -2.0` (`RESULT.md:39`) | `112` events, `48.2%` | `54 / 112 = 48.2143%` (`48.2%`) | `SAME` | `RESULT.md:39`, `PRE_REG.md:17` |
| `d = -1.0` (`RESULT.md:40`) | `110` events, `59.1%` | `65 / 110 = 59.0909%` (`59.1%`) | `SAME` | `RESULT.md:40`, `PRE_REG.md:17` |
| `d = -0.5` (`RESULT.md:41`) | `108` events, `53.7%` | `58 / 108 = 53.7037%` (`53.7%`) | `SAME` | `RESULT.md:41`, `PRE_REG.md:17` |
| `d = +0.5` (`RESULT.md:42`) | `108` events, `56.5%` | `61 / 108 = 56.4815%` (`56.5%`) | `SAME` | `RESULT.md:42`, `PRE_REG.md:17` |
| `d = +1.0` (`RESULT.md:43`) | `113` events, `54.0%` | `61 / 113 = 53.9823%` (`54.0%`) | `SAME` | `RESULT.md:43`, `PRE_REG.md:17` |
| `d = +2.0` (`RESULT.md:44`) | `112` events, `44.6%` | `50 / 112 = 44.6429%` (`44.6%`) | `SAME` | `RESULT.md:44`, `PRE_REG.md:17` |
| `d = +3.0` (`RESULT.md:45`) | `111` events, `24.3%` | `27 / 111 = 24.3243%` (`24.3%`) | `SAME` | `RESULT.md:45`, `PRE_REG.md:17` |

## Verdict

All headline numbers (`57.2%`, `46.8%`, `+10.4 pp`, Part B `51.2% / 47.8% / 45.5%`, placebo `42.6% / 39.9% / 36.6%`) and all 8 per-`d` placebo rows in `MyTradingSys/research/tom_transfer_2026-10-11/vp_return/RESULT.md` reproduce **SAME** to the printed precision from an independent implementation of `PRE_REG.md` and `FORMULAS.md` section 18 on the 2022-01..2024-06 DEV 1m archives.
