COUNTS: MATCH=10 DIFF=1 NOT_IN_DATA=3

# Re-derivation: wt_extreme_cross_2026-11/RESULT.md

Task: `gpt-rederive-wt-extreme-cross-1108`
Re-derived independently from `dev_cells.csv`, `regime_mix_dev.txt`, and `MyTradingSys/backtest/layers/FORMULAS.md`.
Study code (`study.py`) was not read or executed.
Note: No source files edited; no git commit or ship performed.

## Headline Summary Table

| # | RESULT.md claim | Recomputed | Status | Detail / Source |
|---|---|---|---|---|
| 1 | 135 rows in `dev_cells.csv` | 135 rows | MATCH | Shape: `(135, 19)`, unique tf (3) x side (2) x lvl (2) x daytag (5) x htf (3) minus combinations = 135 |
| 2 | 1m buy -50 (card): n 15936, days 912, MFE 0.161 / 0.104, pts 32, base 0.148, excess +0.013 (3.7), net -0.141 (-58.6), hit 0.20 | n=15936, days=912, mfe=0.161/0.104, pts=32, base=0.148, excess=+0.013 (3.7), net=-0.141 (-58.6), hit=0.20 | MATCH | Matches row in `dev_cells.csv` at printed precision |
| 3 | 1m buy -60 (bible60): n 7310, days 910, MFE 0.187 / 0.122, pts 38, base 0.148, excess +0.039 (8.2), net -0.140 (-35.6), hit 0.22 | n=7310, days=910, mfe=0.187/0.122, pts=38, base=0.148, excess=+0.039 (8.2), net=-0.140 (-35.6), hit=0.22 | MATCH | Matches row in `dev_cells.csv` at printed precision |
| 4 | 1m sell +40 (card): n 26580, days 912, MFE 0.145 / 0.094, pts 29, base 0.149, excess -0.005 (-1.7), net -0.141 (-79.7), hit 0.18 | n=26580, days=912, mfe=0.145/0.094, pts=29, base=0.149, excess=-0.005 (-1.7), net=-0.141 (-79.7), hit=0.18 | MATCH | Matches row in `dev_cells.csv` at printed precision |
| 5 | 5m buy -50 (card): n 2938, days 832, MFE 0.387 / 0.248, pts 79, base 0.348, excess +0.038 (2.8), net -0.134 (-12.6), hit 0.36 | n=2938, days=832, mfe=0.387/0.248, pts=79, base=0.348, excess=+0.038 (2.8), net=-0.134 (-12.6), hit=0.36 | MATCH | Matches row in `dev_cells.csv` at printed precision |
| 6 | 5m buy -60 (bible60): n 1400, days 654, MFE 0.436 / 0.291, pts 93, base 0.348, excess +0.087 (4.3), net -0.128 (-7.2), hit 0.40 | n=1400, days=654, mfe=0.436/0.291, pts=93, base=0.348, excess=+0.087 (4.3), net=-0.128 (-7.2), hit=0.40 | MATCH | Matches row in `dev_cells.csv` at printed precision |
| 7 | 5m sell +40 (card): n 5130, days 904, MFE 0.340 / 0.219, pts 69, base 0.352, excess -0.012 (-1.6), net -0.140 (-18.2), hit 0.33 | n=5130, days=904, mfe=0.340/0.219, pts=69, base=0.352, excess=-0.012 (-1.6), net=-0.140 (-18.2), hit=0.33 | MATCH | Matches row in `dev_cells.csv` at printed precision |
| 8 | 15m buy -50 (card): n 922, days 499, MFE 0.688 / 0.459, pts 136, base 0.626, excess +0.062 (1.9), net -0.128 (-3.8), hit 0.46 | n=922, days=499, mfe=0.688/0.459, pts=136, base=0.626, excess=+0.062 (1.9), net=-0.128 (-3.8), hit=0.46 | MATCH | Matches row in `dev_cells.csv` at printed precision |
| 9 | 15m buy -60 (bible60): n 462, days 307, MFE 0.797 / 0.520, pts 164, base 0.626, excess +0.171 (3.3), net -0.089 (-1.7), hit 0.49 | n=462, days=307, mfe=0.797/0.520, pts=164, base=0.626, excess=+0.171 (3.3), net=-0.089 (-1.7), hit=0.49 | MATCH | Matches row in `dev_cells.csv` at printed precision |
| 10 | 15m sell +40 (card): n 1636, days 693, MFE 0.630 / 0.433, pts 143, base 0.632, excess -0.001 (-0.1), net -0.152 (-6.3), hit 0.42 | n=1636, days=693, mfe=0.630/0.433, pts=143, base=0.632, excess=-0.001 (-0.1), net=-0.152 (-6.3), hit=0.42 | MATCH | Matches row in `dev_cells.csv` at printed precision |
| 11 | "The only positive net cell in the 135: 15m buy -60, same_range day (ex-post tag), n 309, net +0.043 % (t 0.7)" | The cited cell numbers match (`n=309`, `net_mean=+0.043`, `net_t=+0.697`), BUT there are 4 cells with `net_mean > 0` in `dev_cells.csv`: (1) 15m buy card same_range/against: n 314, net +0.060 (t 1.05); (2) 15m buy bible60 same_range/all: n 309, net +0.043 (t 0.70); (3) 15m buy bible60 same_range/against: n 160, net +0.139 (t 1.37); (4) 15m buy bible60 prior_trend/with: n 62, net +0.069 (t 0.81). | DIFF | "Only" claim is contradicted by the data. The finding is unaffected: none has t >= 1.4. |
| 12 | Window: DEV 2022-01-01 .. 2024-07-01 (exclusive) | Not present in aggregated CSV | NOT_IN_DATA | Start/end date bounds not recorded in `dev_cells.csv` |
| 13 | Text figures: 1m ret mean -0.001 %, maker net about -0.09 % | `ret_mean` in CSV is -0.0014 %; maker net (-0.09 %) is an analytical projection | NOT_IN_DATA | Recomputed formula from `FORMULAS.md` (ret - 0.09 % = -0.091 %), but maker execution is not a column in the CSV |
| 14 | Anecdotal 11-02 bounce: 100-250 pts | Not present in data | NOT_IN_DATA | Operator chart observation outside DEV dataset |

## Supplementary Verifications

### 1. Regime Mix (`regime_mix_dev.txt`)
- Text in `regime_mix_dev.txt`: `130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)`
- Matches RESULT.md Section 1 exactly.

### 2. Day Type and HTF Split Table (buy -50 / sell +40)
All 11 split rows match `dev_cells.csv` at the printed precision:
- 1m buy same_range / same_trend: n 12066 / 3870, excess +0.008 (2.0) / +0.029 (3.7), net -0.137 / -0.156 (MATCH)
- 1m buy prior_range / prior_trend: n 11969 / 3967, excess +0.005 (1.2) / +0.038 (4.8), net -0.138 / -0.152 (MATCH)
- 1m buy HTF with / against: n 8502 / 7434, excess -0.004 (-1.2) / +0.033 (5.4), net -0.133 / -0.152 (MATCH)
- 1m sell same_range / same_trend: n 19862 / 6718, excess -0.009 (-3.1) / +0.010 (1.9), net -0.137 / -0.153 (MATCH)
- 1m sell HTF with / against: n 12626 / 13954, excess +0.010 (2.2) / -0.018 (-6.0), net -0.138 / -0.143 (MATCH)
- 5m buy prior_range / prior_trend: n 2214 / 724, excess +0.008 (0.6) / +0.129 (4.0), net -0.133 / -0.138 (MATCH)
- 5m buy HTF with / against: n 1516 / 1422, excess -0.024 (-2.3) / +0.105 (4.3), net -0.134 / -0.133 (MATCH)
- 15m buy same_range / same_trend: n 634 / 288, excess +0.088 (2.0) / +0.004 (0.1), net -0.033 (-0.9) / -0.336 (-5.2) (MATCH)
- 15m buy prior_range / prior_trend: n 678 / 244, excess +0.001 (0.0) / +0.232 (3.3), net -0.145 / -0.079 (-1.0) (MATCH)
- 15m buy HTF with / against: n 445 / 477, excess -0.093 (-3.3) / +0.207 (3.7), net -0.136 / -0.120 (MATCH)
- 15m sell same_range / same_trend: n 1168 / 468, excess +0.026 (1.1) / -0.069 (-2.0), net -0.053 (-2.1) / -0.400 (-8.3) (MATCH)

### 3. Metric Arithmetic (`FORMULAS.md`)
- `mfe_excess = mfe_mean - base_mfe` holds exactly across all rows.
- `net_mean = ret_mean - 0.14 %` (TAKER_RT_PCT) holds exactly across all rows.

### Limitations
Only aggregated cell summaries (`dev_cells.csv`) and regime mix text (`regime_mix_dev.txt`) were present in the study folder. Individual trades and raw 1m BTCUSDT price bars are not checked; `n` is verified as aggregated in the delivered artifacts.
