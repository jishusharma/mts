# Layer Lab Report: `gemini-blind-read-us-open-oos-1104`

- **Card**: `gemini-blind-read-us-open-oos-1104`
- **Date**: 2026-11-04 UTC
- **Deliverable**: `MyTradingSys/research/gemini_audits_2026-11-04/us_open_oos_blind_read.md`
- **Headline Counts**: `FOUND=68 DIFF=0 NOT_IN_DATA=1`

## Findings

1. **Section 1 & 2 Direction, Wilson CIs, and Bucket Multiples (`FOUND=68`)**:
   - Every probability, Wilson 95% CI, placebo spread (`0.440..0.555`, median `0.501` across 24 UTC hour anchors in `MyTradingSys/research/us_open_oos_2026-10-30/results_oos_2020_2021.json:111-309`), per-year split (`2020` `0.502` on `n=253`, `2021` `0.468` on `n=252` in `results_oos_2020_2021.json:311-328`), and `T1` 15-min UTC bucket multiple (`us_dst` and `us_std` in `results_oos_2020_2021.json:4-69` and `MyTradingSys/research/session_sweeps/results_2026-10-04.json:4-69`) matches `MyTradingSys/research/us_open_oos_2026-10-30/REPORT.md:1-30` to the stated rounding precision (`0` `DIFF`).
   - Specifically verified the `00:00` UTC top-bucket claim (`REPORT.md:26`, row 48 in `us_open_oos_blind_read.md`): `00:00` UTC is #1 by `absret_x` in both `us_dst` (`1.55x`, `vol_x=1.52`, `results_oos_2020_2021.json:7-10`) and `us_std` (`1.51x`, `vol_x=1.44`, `results_oos_2020_2021.json:39-42`), and is absent from the top-6 arrays in `session_sweeps/results_2026-10-04.json:5-68`.
2. **Raw 1m Bar Count (`NOT_IN_DATA=1`)**:
   - `REPORT.md:3` quotes `1,052,640 bars` from `F:/MTS/Dumps/backtest/raw_1m_2019/klines`. That path is absent on `DESKTOP-F7IU69N` and `results_oos_2020_2021.json` stores `"days": 505, "dropped": 0` (`results_oos_2020_2021.json:2-3`) without a total 1m bar counter (though $731\text{ calendar days in 2020--2021} \times 1440 = 1,052,640$). Recorded as `NOT_IN_DATA`.
