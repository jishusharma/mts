FAIL — Headline verdict matches (`KILL`), but `n` and headline numbers (`meanR12`, `95% CI`, `placebo pct`, `BASE` counts) **MISMATCH** between independent `PRE_REG.md` re-derivation and `REPORT.md` / `summary.json`.

Re-derived independently from `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/PRE_REG.md` and `MyTradingSys/backtest/layers/FORMULAS.md` using `rederive.py` on the 22 cached Binance spot daily files (`C:/Users/e-ngineers/MTS_data_cache/binance_spot_1d/*.json`, bars through `2026-11-13` UTC).

## Claim Table

| Claim | Recomputed (OURS) | Stated (SOURCED) | Source `file:line` | Status |
|---|---|---|---|---|
| Primary A (`HL_BREAK`) Verdict | `KILL` | `KILL` | `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/REPORT.md:155` | MATCH |
| A `UP+BASE` `VAL` `n` | `127` | `97` | `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/REPORT.md:46`, `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/summary.json:36` | MISMATCH |
| A `UP+BASE` `VAL` `mean R 12bp` | `+0.0690` | `0.037` (`0.036645`) | `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/REPORT.md:46`, `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/summary.json:38` | MISMATCH |
| A `UP+BASE` `VAL` `95% CI (12bp)` | `[-0.1114, +0.2541]` | `[-0.15, 0.21]` (`[-0.1479, 0.2128]`) | `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/REPORT.md:46`, `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/summary.json:40-41` | MISMATCH |
| A `UP+BASE` `VAL` `placebo pct (12bp)` | `84.15%` (`97.5th=+0.1949`) | `80.8%` (`97.5th=0.162`) | `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/REPORT.md:46,155`, `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/summary.json:43,45` | MISMATCH |
| A `UP+BASE` `DEV` `n` / `mean R 12bp` | `219` / `+0.2053` | `195` / `0.208` (`0.208312`) | `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/REPORT.md:45`, `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/summary.json:23,25` | MISMATCH |
| A `UP+BASE` `RECENT` `n` / `mean R 12bp` | `42` / `+0.0783` | `20` / `0.118` (`0.118097`) | `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/REPORT.md:47`, `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/summary.json:49,51` | MISMATCH |
| A `UP` `VAL` `n` / `mean R 12bp` | `90` / `+0.0514` | `90` / `0.051` (`0.051380`) | `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/REPORT.md:50`, `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/summary.json:90,92` | MATCH |
| A `BASE` `VAL` `n` / `mean R 12bp` | `37` / `+0.1119` | `7` / `-0.153` (`-0.152804`) | `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/REPORT.md:54`, `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/summary.json:144,146` | MISMATCH |
| A total events kept after lockout | `563` (`346+70+42+105`) | `563` | `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/REPORT.md:39`, `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/summary.json:19` | MATCH |
| Secondary B (`BULL_DIV`) Verdict | `UNDERPOWERED` (`VAL n=13 < 30`) | `UNDERPOWERED (VAL n=9 < 30)` | `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/REPORT.md:225` | MATCH (verdict) / MISMATCH (`n`) |
| B `UP+BASE` `VAL` `n` / `mean R 12bp` | `13` / `-0.0912` | `9` / `-0.100` (`-0.099667`) | `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/REPORT.md:166`, `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/summary.json:1067,1069` | MISMATCH |
| B total events kept after lockout | `57` (`25+1+7+24`) | `57` | `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/REPORT.md:159`, `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/summary.json:1050` | MATCH |
| `regime_mix` `VAL` `BASE` coin-days | `6297` | `2813` | `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/summary.json:12` | MISMATCH |

## Diagnosis of Mismatch (OURS)

- Signal extraction, swing-low detection, Wilder `RSI14`/`ATR14`, stop/exit simulation, and lockout match the stated study **exactly**:
  - Total kept events match identically (`A`: `563` vs `563`, `B`: `57` vs `57`; `dropped_stop = 0`).
  - `UP` phase rows match to 4 decimal places (`A UP DEV`: `n=163`, `meanR12=+0.2418` vs `0.2418`; `A UP VAL`: `n=90`, `meanR12=+0.0514` vs `0.0514`; `B UP DEV`: `n=4`, `meanR12=+0.0678` vs `0.0678`; `B UP VAL`: `n=6`, `meanR12=-0.0776` vs `-0.0776`).
- The divergence is isolated to **phase classification** (`BASE` vs `POSTPEAK_BEAR` / `RANGE` / `DOWN`): following `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/PRE_REG.md:32-38` literally yields `6297` `BASE` coin-days in `VAL` (`37` `BASE` events in `A VAL`), whereas `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/summary.json:12` reports `2813` `BASE` coin-days in `VAL` (`7` `BASE` events in `A VAL`).
