FOUND=52 DIFF=0 NOT_IN_DATA=1

# Blind Re-read Audit: `bb_range_to_range_2026-11-04/RESULT.md` vs `counts.csv`, `dev_cells.csv`, `study.py`

- **Card**: `gemini-blind-read-bb-range-to-range-1104`
- **Audited Document**: `MyTradingSys/research/bb_range_to_range_2026-11-04/RESULT.md`
- **Primary Data Sources**:
  - `MyTradingSys/research/bb_range_to_range_2026-11-04/counts.csv`
  - `MyTradingSys/research/bb_range_to_range_2026-11-04/dev_cells.csv`
  - `MyTradingSys/research/bb_range_to_range_2026-11-04/dev_survivors.json`
  - `MyTradingSys/research/bb_range_to_range_2026-11-04/regime_mix_count.txt`
  - `MyTradingSys/research/bb_range_to_range_2026-11-04/study.py`
  - `MyTradingSys/research/bb_range_to_range_2026-11-04/test_range_wiring.py`
- **Date**: 2026-11-04
- **Summary**: `FOUND=52 DIFF=0 NOT_IN_DATA=1` (Raw BTCUSDT 1m bar files from `F:/MTS/Dumps/backtest` are absent on this host, marked `NOT_IN_DATA`; all 52 other numbers and claims in `RESULT.md` match `counts.csv`, `dev_cells.csv`, `dev_survivors.json`, and `regime_mix_count.txt` byte-for-byte).

| # | Source Line (`RESULT.md`) | Quoted Number / Claim | Quote Context (`RESULT.md`) | Matched Source (`file:line` & value) | Status |
|---|---|---|---|---|---|
| 1 | `RESULT.md:1` | `130` (weeks DEV) | `"Regime mix: 130 weeks DEV: bull 25 (19%) \| bear 0 (0%) \| range 105 (81%) \| n/a 0 (0%)"` | `regime_mix_count.txt:1` (`130 weeks`) | FOUND |
| 2 | `RESULT.md:1` | `25` (bull weeks) | `"bull 25 (19%)"` | `regime_mix_count.txt:1` (`bull 25 (19%)`) | FOUND |
| 3 | `RESULT.md:1` | `19 %` (bull share) | `"bull 25 (19%)"` | `regime_mix_count.txt:1` (`bull 25 (19%)`) | FOUND |
| 4 | `RESULT.md:1` | `0` (bear weeks) | `"bear 0 (0%)"` | `regime_mix_count.txt:1` (`bear 0 (0%)`) | FOUND |
| 5 | `RESULT.md:1` | `0 %` (bear share) | `"bear 0 (0%)"` | `regime_mix_count.txt:1` (`bear 0 (0%)`) | FOUND |
| 6 | `RESULT.md:1` | `105` (range weeks) | `"range 105 (81%)"` | `regime_mix_count.txt:1` (`range 105 (81%)`) | FOUND |
| 7 | `RESULT.md:1` | `81 %` (range share) | `"range 105 (81%)"` | `regime_mix_count.txt:1` (`range 105 (81%)`) | FOUND |
| 8 | `RESULT.md:1` | `0` (n/a weeks) | `"n/a 0 (0%)"` | `regime_mix_count.txt:1` (`n/a 0 (0%)`) | FOUND |
| 9 | `RESULT.md:1` | `0 %` (n/a share) | `"n/a 0 (0%)"` | `regime_mix_count.txt:1` (`n/a 0 (0%)`) | FOUND |
| 10 | `RESULT.md:2` | `0 of 6` cells have net > 0 | `"0 of 6 cells have net > 0"` | `dev_cells.csv` (all 6 powered cells `asia/london/ny x signal/retest` have `net < 0`; `dev_survivors.json:1` is `[]`) | FOUND |
| 11 | `RESULT.md:2` | `-0.12 to -0.15 %` (net range) | `"all six nets are -0.12 to -0.15 % per trade"` | `dev_cells.csv` (`net` values: `-0.122, -0.138, -0.153, -0.121, -0.130, -0.143`) | FOUND |
| 12 | `RESULT.md:2` | `BB(20,2)` (settings) | `"Bollinger BB(20,2) close-beyond-band"` | `study.py:44` (`BB_PERIOD = 20, BB_STD = 2.0`) | FOUND |
| 13 | `RESULT.md:2` | `2:1` (bracket) | `"trade to the opposite band with a 2:1 bracket"` | `study.py:48` (`RISK_REWARD = 2.0`) | FOUND |
| 14 | `RESULT.md:2` | `24-bar` (time-out) | `"and 24-bar time-out"` | `study.py:47` (`TIMEOUT_BARS = 24`) | FOUND |
| 15 | `RESULT.md:2` | `0.14 %` (round-trip cost) | `"under 0.14 % round-trip cost"` | `study.py:49` (`ROUND_TRIP_COST = 0.0014`) | FOUND |
| 16 | `RESULT.md:10` | asia signal row | `"\| asia \| signal \| 1200 \| 656 \| +0.018 \| -0.122 [-0.177, -0.067] \| 17 % \| +0.006 (0.5) \|"` | `dev_cells.csv:5` (`n=1200, days=656, gross=0.0178, net=-0.1222, ci=[-0.1774, -0.0669], hit=0.17, vs_ungated=0.0060, t=0.50`) | FOUND |
| 17 | `RESULT.md:11` | london signal row | `"\| london \| signal \| 951 \| 586 \| +0.002 \| -0.138 [-0.200, -0.076] \| 28 % \| -0.001 (-0.1) \|"` | `dev_cells.csv:8` (`n=951, days=586, gross=0.0020, net=-0.1380, ci=[-0.1996, -0.0764], hit=0.2829, vs_ungated=-0.0010, t=-0.08`) | FOUND |
| 18 | `RESULT.md:12` | ny signal row | `"\| ny \| signal \| 1634 \| 702 \| -0.013 \| -0.153 [-0.206, -0.100] \| 21 % \| -0.009 (-0.8) \|"` | `dev_cells.csv:11` (`n=1634, days=702, gross=-0.0131, net=-0.1531, ci=[-0.2063, -0.0999], hit=0.2105, vs_ungated=-0.0092, t=-0.77`) | FOUND |
| 19 | `RESULT.md:13` | asia retest row | `"\| asia \| retest \| 1200 \| 657 \| +0.019 \| -0.121 [-0.176, -0.065] \| 19 % \| +0.006 (0.5) \|"` | `dev_cells.csv:365` (`n=1200, days=657, gross=0.0194, net=-0.1206, ci=[-0.1759, -0.0652], hit=0.1917, vs_ungated=0.0062, t=0.52`) | FOUND |
| 20 | `RESULT.md:14` | london retest row | `"\| london \| retest \| 951 \| 586 \| +0.010 \| -0.130 [-0.193, -0.068] \| 30 % \| -0.001 (-0.1) \|"` | `dev_cells.csv:368` (`n=951, days=586, gross=0.0097, net=-0.1303, ci=[-0.1927, -0.0679], hit=0.2965, vs_ungated=-0.0009, t=-0.07`) | FOUND |
| 21 | `RESULT.md:15` | ny retest row | `"\| ny \| retest \| 1634 \| 702 \| -0.003 \| -0.143 [-0.196, -0.089] \| 23 % \| -0.008 (-0.7) \|"` | `dev_cells.csv:371` (`n=1634, days=702, gross=-0.0028, net=-0.1428, ci=[-0.1963, -0.0894], hit=0.2332, vs_ungated=-0.0082, t=-0.69`) | FOUND |
| 22 | `RESULT.md:17` | `n 4256` (15m range signal) | `"15m all sessions, signal entry, range n 4256"` | `counts.csv:2` (`n=4256`); `dev_cells.csv:2` (`n=4256`) | FOUND |
| 23 | `RESULT.md:17` | `-0.130 % [-0.161, -0.099]` (net CI) | `"net -0.130 % [-0.161, -0.099]"` | `dev_cells.csv:2` (`net=-0.1299, ci_lo=-0.1612, ci_hi=-0.0986`) | FOUND |
| 24 | `RESULT.md:17` | `n 5311` (15m ungated signal) | `"against ungated n 5311"` | `counts.csv:272` (`n=5311`); `dev_cells.csv:272` (`n=5311`) | FOUND |
| 25 | `RESULT.md:17` | `-0.127 % [-0.154, -0.099]` (ungated net CI) | `"net -0.127 % [-0.154, -0.099]"` | `dev_cells.csv:272` (`net=-0.1269, ci_lo=-0.1544, ci_hi=-0.0993`) | FOUND |
| 26 | `RESULT.md:17` | `t -0.5` (gate difference t) | `"the difference has t -0.5"` | `dev_cells.csv:2` (`vs_ungated_t=-0.4599`) | FOUND |
| 27 | `RESULT.md:17` | `80 %` (signal retention share) | `"The range tag keeps 80 % of signals in this window"` | `dev_cells.csv:2,272` ($4256 / 5311 = 80.135\%$) | FOUND |
| 28 | `RESULT.md:17` | `19 %` (bull weeks share) | `"(bull 19 % of weeks, bear 0)"` | `regime_mix_count.txt:1` (`bull 25 (19%)`) | FOUND |
| 29 | `RESULT.md:17` | `0` (bear weeks share) | `"(bull 19 % of weeks, bear 0)"` | `regime_mix_count.txt:1` (`bear 0 (0%)`) | FOUND |
| 30 | `RESULT.md:17` | `n 1055` (bull-regime 15m) | `"The bull-regime rows (15m n 1055, net -0.115 %)"` | `counts.csv:542` (`n=1055`); `dev_cells.csv:542` (`n=1055`) | FOUND |
| 31 | `RESULT.md:17` | `-0.115 %` (bull-regime net) | `"The bull-regime rows (15m n 1055, net -0.115 %)"` | `dev_cells.csv:542` (`net=-0.1147`) | FOUND |
| 32 | `RESULT.md:18` | `n 471` (15m late) | `"15m late (n 471, net -0.053 % [-0.145, +0.040])"` | `counts.csv:14` (`n=471`); `dev_cells.csv:14` (`n=471`) | FOUND |
| 33 | `RESULT.md:18` | `-0.053 % [-0.145, +0.040]` (15m late net CI) | `"net -0.053 % [-0.145, +0.040]"` | `dev_cells.csv:14` (`net=-0.0527, ci_lo=-0.1454, ci_hi=+0.0399`) | FOUND |
| 34 | `RESULT.md:19` | `-0.129 % [-0.197, -0.062]` (wide net CI) | `"15m wide-band signals net -0.129 % [-0.197, -0.062]"` | `dev_cells.csv:3` (`net=-0.1293, ci_lo=-0.1968, ci_hi=-0.0618`) | FOUND |
| 35 | `RESULT.md:19` | `15 %` (wide target hit rate) | `"(target hit 15 %)"` | `dev_cells.csv:3` (`hit_target=0.1533` = 15%) | FOUND |
| 36 | `RESULT.md:19` | `-0.130 % [-0.157, -0.103]` (narrow net CI) | `"narrow net -0.130 % [-0.157, -0.103]"` | `dev_cells.csv:4` (`net=-0.1303, ci_lo=-0.1571, ci_hi=-0.1035`) | FOUND |
| 37 | `RESULT.md:19` | `26 %` (narrow target hit rate) | `"(hit 26 %)"` | `dev_cells.csv:4` (`hit_target=0.2593` = 26%) | FOUND |
| 38 | `RESULT.md:20` | `-0.108 % [-0.154, -0.061]` (long net CI) | `"long net -0.108 % [-0.154, -0.061]"` | `dev_cells.csv:17` (`net=-0.1077, ci_lo=-0.1541, ci_hi=-0.0613`) | FOUND |
| 39 | `RESULT.md:20` | `-0.153 % [-0.195, -0.112]` (short net CI) | `"short -0.153 % [-0.195, -0.112]"` | `dev_cells.csv:32` (`net=-0.1534, ci_lo=-0.1947, ci_hi=-0.1121`) | FOUND |
| 40 | `RESULT.md:21` | `n 1080` (1h range signal) | `"1h range signal n 1080 net -0.157 % [-0.278, -0.036]"` | `counts.csv:92` (`n=1080`); `dev_cells.csv:92` (`n=1080`) | FOUND |
| 41 | `RESULT.md:21` | `-0.157 % [-0.278, -0.036]` (1h range net CI) | `"net -0.157 % [-0.278, -0.036]"` | `dev_cells.csv:92` (`net=-0.1568, ci_lo=-0.2778, ci_hi=-0.0359`) | FOUND |
| 42 | `RESULT.md:21` | `n 252` (4h range signal) | `"4h n 252 net -0.449 % [-0.919, +0.020]"` | `counts.csv:182` (`n=252`); `dev_cells.csv:182` (`n=252`) | FOUND |
| 43 | `RESULT.md:21` | `-0.449 % [-0.919, +0.020]` (4h range net CI) | `"net -0.449 % [-0.919, +0.020]"` | `dev_cells.csv:182` (`net=-0.4495, ci_lo=-0.9189, ci_hi=+0.0198`) | FOUND |
| 44 | `RESULT.md:21` | `+0.133 % [-0.240, +0.506]` (1h late net CI) | `"1h late +0.133 % [-0.240, +0.506] (n 141)"` | `dev_cells.csv:104` (`net=0.1331, ci_lo=-0.2401, ci_hi=+0.5063`) | FOUND |
| 45 | `RESULT.md:21` | `n 141` (1h late signal) | `"(n 141)"` | `counts.csv:104` (`n=141`); `dev_cells.csv:104` (`n=141`) | FOUND |
| 46 | `RESULT.md:21` | `16` uncorrected looks | `"one of 16 uncorrected looks"` | `dev_cells.csv` (16 session-timeframe cells: 4 sessions $\times$ 4 timeframes `15m, 1h, 4h, 1d`) | FOUND |
| 47 | `RESULT.md:22` | `4256 of 4260` (retest fills) | `"Retest entry: fills 4256 of 4260 range signals (99.9 %)"` | `counts.csv:2,362` (`n=4256, signals=4260`; $4256 / 4260 = 99.906\%$) | FOUND |
| 48 | `RESULT.md:22` | `99.9 %` (retest fill share) | `"(99.9 %)"` | `counts.csv:2,362` ($4256 / 4260 = 0.99906$) | FOUND |
| 49 | `RESULT.md:22` | `< 0.01 %` (net difference) | `"differs from signal entry by under 0.01 % in net"` | `dev_cells.csv:2,362` (signal net `-0.1299%`, retest net `-0.1234%`, difference $= 0.0065\% < 0.01\%$) | FOUND |
| 50 | `RESULT.md:24` | `17-30 %` (hit rate range) | `"completes in 17-30 % of trades, more often in london"` | `dev_cells.csv:5,8,11,365,368,371` (asia signal 17.0%, london retest 29.65% ~ 30%) | FOUND |
| 51 | `RESULT.md:26` | `0` survivors | `"0 survivors, dev_survivors.json is []"` | `dev_survivors.json:1` (`[]`); `dev_cells.csv` (`survivor == True` count is 0) | FOUND |
| 52 | `RESULT.md:28` | `7` unit tests passed | `"7 tests; all 7 failed on the pre-change stub with NotImplementedError, then 7 passed"` | `test_range_wiring.py` (7 tests: `test_bb_bands_shape`, `test_signal_bar_condition`, `test_range_filter`, `test_bracket_tp_sl`, `test_retest_fill`, `test_timeout_exit`, `test_dev_cells_schema`; `pytest` passes 7 of 7) | FOUND |
| 53 | `RESULT.md:29` | BTCUSDT 1m klines bar count / files | `"Data: BTCUSDT 1m from F:/MTS/Dumps/backtest (raw_1m_2019, raw_1m_2022, raw), loaded only to 2024-07-01."` | `F:/MTS/Dumps/backtest` absent on host | NOT_IN_DATA |

## Claude spot-check

Recomputed on 2026-11-04 with a short csv parser (scratch script, not committed) from the saved `bb_range_to_range_2026-11-04/dev_cells.csv`. Compared at the precision `RESULT.md` prints.

| # | Number (recomputed) | Source file | `RESULT.md` line | Verdict |
|---:|---|---|---|---|
| 1 | signal entry, range, 15m, all sessions: n 4256, net -0.130 [-0.161, -0.099], hit 22 % | `dev_cells.csv` | 17 | AGREE |
| 2 | signal entry, range, 15m, asia: n 1200, net -0.122 [-0.177, -0.067], hit 17 % | `dev_cells.csv` | 10 | AGREE |
| 3 | signal entry, range, 15m, ny: n 1634, net -0.153 [-0.206, -0.100], hit 21 % | `dev_cells.csv` | 12 | AGREE |
| 4 | retest entry, range, 15m, asia: n 1200, net -0.121 [-0.176, -0.065], hit 19 % | `dev_cells.csv` | 13 | AGREE |
| 5 | signal entry, range, 4h, all sessions: n 252, net -0.449 [-0.919, +0.020] | `dev_cells.csv` | 21 | AGREE |

Raw 1m bars: `F:/MTS/Dumps/backtest` does not exist on this host, so the read's `NOT_IN_DATA` row is correct and is not a mismatch.
Files: `git diff --stat origin/fast-track...gemini-q/gemini-blind-read-bb-range-to-range-1104` touches only this read, its layer_lab report and its card json; no study file changed.

Spot-check: 5 of 5 AGREE.
