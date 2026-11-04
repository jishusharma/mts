# Layer Lab Report: `gemini-blind-read-bb-range-studies-1104`

- **Card**: `gemini-blind-read-bb-range-studies-1104` (D11 feeder check `A-20261104-1`)
- **Date**: `2026-11-04`
- **Deliverable**: `MyTradingSys/research/gemini_audits_2026-11-04/BLIND_READ_BB_STUDIES_1104.md`
- **Verdict**: `VERDICT: MATCH` (`FOUND=126 DIFF=0 NOT_IN_DATA=0`)

## 1. Scope & Blind-Read Protocol

1. **Blind CSV/TXT/JSON Extraction First**: Prior to reading `RESULT.md` or `RESULT_LONG.md`, all raw CSV, TXT, and JSON outputs across the three 2026-11-04 Bollinger Band studies were inspected and independently aggregated:
   - `MyTradingSys/research/bb_range_to_range_2026-11-04/{counts.csv, dev_cells.csv, dev_survivors.json, regime_mix_count.txt, regime_mix_dev.txt, study.py}`
   - `MyTradingSys/research/bb_range_retest_2026-11-04/{counts.csv, dev_cells.csv, dev_survivors.json, regime_mix_count.txt, regime_mix_dev.txt, study.py}`
   - `MyTradingSys/research/bb_long_window_2026-11-04/{counts_long.csv, dev_cells_long.csv, dev_survivors_long.json, regime_mix_count_long.txt, regime_mix_dev_long.txt, study_long.py, gate_long.py}`
2. **Parameter Provenance (`SOURCED` vs `OURS`)**:
   - `TAKER_RT_PCT = 0.14%` (`14 bps` round-trip cost): `SOURCED` (`MyTradingSys/backtest/research_kit.py:31`).
   - Day-clustered standard error (`cluster_mean_se`), paired day-cluster difference (`cluster_diff`), and Holm step-down adjustment (`holm`): `SOURCED` (`MyTradingSys/backtest/research_kit.py:124-182`).
   - Windows (`DEV = [2022-01-01, 2024-07-01)`, `LONG_DEV = [2017-08-01, 2024-07-01)`): `SOURCED` (`MyTradingSys/backtest/splits.py`).
   - Malkan RSI regime band (`weekly AND monthly RSI14 >= 60` or `<= 40`): `60/40` `SOURCED` Malkan, `SMA200` `SOURCED-in-repo`, `"range = the rest"` `OURS` (`MyTradingSys/backtest/research_kit.py:42-78`).
   - `BB(20, 2)` population std of closes (`study.py:21,45-53`), `2:1` bracket (`STOP_FRAC = 0.5`, `study.py:23,81`), `TIMEOUT_BARS = 24` (`study.py:22`), `RETEST_N = 10` (`study.py:24`), re-entry `M = 10` and `k in {0.25, 0.5, 1.0}` x `ATR(14)` (`bb_range_retest_2026-11-04/study.py:25-27`), `500`-bar rolling median band-width tag (`bb_range_to_range_2026-11-04/study.py:25,65`), `20`-session running-range tag (`bb_range_retest_2026-11-04/study.py:28-29,39-57`), and `P40` bear proxy (`weekly RSI14 <= 40` alone below `SMA200`, `bb_long_window_2026-11-04/study_long.py:55-82`): `OURS`.

## 2. Key Findings & Citations (`file:line`)

### Study 1: `bb_range_to_range_2026-11-04`
- **Internal Parity**: `counts.csv:2-1081` and `dev_cells.csv:2-1081` (`1080` rows) match `100%` on `signals`, `n`, `days`, and `median_stop_pct`. `dev_survivors.json:1` is `[]` (`0` survivors).
- **Regime Mix**: `regime_mix_dev.txt:1` (`130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)`) matches `RESULT.md:1`.
- **Confirmatory 6-Cell Family (`15m, gate=range, side=both, width=any`)**:
  - `asia, signal` (`dev_cells.csv:5` vs `RESULT.md:10`): `n=1200, days=656, gross=+0.0178% (+1.78 bps), net=-0.1222% (-12.22 bps), CI=[-0.1775%, -0.0669%], hit_target=17.00%, net_pos_share=39.50%, vs_ungated=+0.0060% (t=+0.50), holm_p=5.73e-5` -> `MATCH`.
  - `london, signal` (`dev_cells.csv:8` vs `RESULT.md:11`): `n=951, days=586, gross=+0.0020% (+0.20 bps), net=-0.1380% (-13.80 bps), CI=[-0.2003%, -0.0757%], hit_target=28.29%, net_pos_share=33.96%, vs_ungated=-0.0009% (t=-0.07), holm_p=5.73e-5` -> `MATCH`.
  - `ny, signal` (`dev_cells.csv:11` vs `RESULT.md:12`): `n=1634 (signals=1637), days=702, gross=-0.0131% (-1.31 bps), net=-0.1531% (-15.31 bps), CI=[-0.2063%, -0.0999%], hit_target=21.05%, net_pos_share=37.39%, vs_ungated=-0.0088% (t=-0.77), holm_p=1.02e-7` -> `MATCH`.
  - `asia, retest` (`dev_cells.csv:185` vs `RESULT.md:13`): `n=1200, days=657, gross=+0.0194% (+1.94 bps), net=-0.1206% (-12.06 bps), CI=[-0.1764%, -0.0649%], hit_target=19.17%, net_pos_share=39.67%, vs_ungated=+0.0057% (t=+0.45), holm_p=5.73e-5` -> `MATCH`.
  - `london, retest` (`dev_cells.csv:188` vs `RESULT.md:14`): `n=951, days=586, gross=+0.0095% (+0.95 bps), net=-0.1305% (-13.05 bps), CI=[-0.1932%, -0.0677%], hit_target=29.65%, net_pos_share=35.86%, vs_ungated=-0.0015% (t=-0.11), holm_p=5.73e-5` -> `MATCH`.
  - `ny, retest` (`dev_cells.csv:191` vs `RESULT.md:15`): `n=1634 (signals=1637), days=702, gross=-0.0025% (-0.25 bps), net=-0.1425% (-14.25 bps), CI=[-0.1962%, -0.0888%], hit_target=23.32%, net_pos_share=39.05%, vs_ungated=-0.0076% (t=-0.65), holm_p=9.71e-7` -> `MATCH`.
- **Regime & Stratum Splits (`RESULT.md:17-22`)**:
  - `15m, range, ALL, signal` (`dev_cells.csv:2`): `n=4256/4260, net=-0.1299% [-0.1612%, -0.0986%], vs_ung_t=-0.46`; `all` (`dev_cells.csv:47`): `n=5311/5315, net=-0.1269% [-0.1543%, -0.0994%]`; `bull` (`dev_cells.csv:92`): `n=1055, net=-0.1147%`; `bear` (`dev_cells.csv:137`): `n=0`; `15m late` (`dev_cells.csv:14`): `n=471, net=-0.0526% [-0.1455%, +0.0403%]`; `wide` (`dev_cells.csv:3`): `net=-0.1293% [-0.1968%, -0.0618%], hit=15.33%`; `narrow` (`dev_cells.csv:4`): `net=-0.1303% [-0.1571%, -0.1035%], hit=25.93%`; `long` (`dev_cells.csv:17`): `net=-0.1076% [-0.1540%, -0.0613%]`; `short` (`dev_cells.csv:32`): `net=-0.1535% [-0.1951%, -0.1119%]`; `1h range` (`dev_cells.csv:362`): `n=1080, net=-0.1571% [-0.2778%, -0.0365%]`; `1h late` (`dev_cells.csv:374`): `n=141, net=+0.1333% [-0.2398%, +0.5063%]`; `4h range` (`dev_cells.csv:722`): `n=252, net=-0.4494% [-0.9185%, +0.0196%]`; `15m range retest ALL` (`dev_cells.csv:182`): `fills=4256/4260 (99.91%), net=-0.1234% [-0.1547%, -0.0921%]` -> all `MATCH`.

### Study 2: `bb_range_retest_2026-11-04`
- **Internal Parity & Fill Rates**: `counts.csv:2-271` and `dev_cells.csv:2-271` (`270` rows) match `100%`. `dev_survivors.json:1` is `[]` (`0` survivors). Pooled `range, tagged, ALL, both` (`dev_cells.csv:2,92,182` vs `RESULT.md:12,18`): `signals=1187, reentered=824 (69.42%), fills=752 (63.35% at k=0.25), 785 (66.13% at k=0.5), 813 (68.49% at k=1.0)` -> `MATCH`.
- **Confirmatory 9-Cell Family (`15m, gate=range, tag=tagged, side=both`, `dev_cells.csv:20,38,56,110,128,146,200,218,236` vs `RESULT.md:24-32`)**:
  - `asia`: `k=0.25` (`L20`, `n=225/176d, gross=+0.0459%, net=-0.0941% [-0.2404%, +0.0522%], hit=15.56%, holm_p=0.89, vs_ung_t=-0.11`); `k=0.5` (`L110`, `n=235/182d, gross=+0.0348%, net=-0.1052% [-0.2478%, +0.0374%], hit=15.74%, holm_p=0.89, vs_ung_t=-0.32`); `k=1.0` (`L200`, `n=244/186d, gross=+0.0085%, net=-0.1315% [-0.2698%, +0.0068%], hit=14.34%, holm_p=0.44, vs_ung_t=-0.57`) -> `MATCH`.
  - `london`: `k=0.25` (`L38`, `n=175/146d, gross=+0.0068%, net=-0.1332% [-0.3207%, +0.0543%], hit=29.14%, holm_p=0.89, vs_ung_t=+0.71`); `k=0.5` (`L128`, `n=180/149d, gross=-0.0349%, net=-0.1749% [-0.3499%, +0.0001%], hit=28.33%, holm_p=0.40, vs_ung_t=+0.74`); `k=1.0` (`L218`, `n=186/155d, gross=-0.0607%, net=-0.2007% [-0.3687%, -0.0327%], hit=27.96%, holm_p=0.17, vs_ung_t=+0.83`) -> `MATCH`.
  - `ny`: `k=0.25` (`L56`, `n=215/162d, gross=+0.0218%, net=-0.1182% [-0.3045%, +0.0681%], hit=15.81%, holm_p=0.89, vs_ung_t=+0.43`); `k=0.5` (`L146`, `n=224/169d, gross=+0.0567%, net=-0.0833% [-0.2675%, +0.1010%], hit=16.96%, holm_p=0.89, vs_ung_t=+0.28`); `k=1.0` (`L236`, `n=233/174d, gross=+0.0674%, net=-0.0726% [-0.2530%, +0.1078%], hit=17.17%, holm_p=0.89, vs_ung_t=+0.37`) -> `MATCH`.
- **Secondary Splits (`RESULT.md:34-36`)**: `k=0.5, ALL, tagged range` (`L92`, `net=-0.1083% [-0.1948%, -0.0217%]`) vs `untagged range` (`L95`, `fill=74.55%, net=-0.1153% [-0.1397%, -0.0908%]`) and `tagged all-regime` (`L101`, `net=-0.1182%`); `long` (`L93`, `n=427, net=-0.1276% [-0.2577%, +0.0025%]`); `short` (`L94`, `n=358, net=-0.0852% [-0.1893%, +0.0188%]`) -> all `MATCH`.

### Study 3: `bb_long_window_2026-11-04`
- **Internal Parity & Regime Mix**: `counts_long.csv:2-1756` and `dev_cells_long.csv:2-1756` (`1755` rows) match `100%`. `dev_survivors_long.json:1` is `[]` (`0` survivors of `30`). `regime_mix_dev_long.txt:1-2` (`360 weeks: bull 73 (20%) | bear 0 (0%) | range 222 (62%) | n/a 65 (18%) | bear weeks: primary Malkan 0, proxy P40 57`) matches `RESULT_LONG.md:1,12`.
- **Confirmatory 30-Cell Pooled Family (`dev_cells_long.csv` vs `RESULT_LONG.md:15,17-18,26-40`)**:
  - `A_r2r range` (`6` cells, `L5,8,11,230,233,236`): `asia signal` (`2697/1412d, net=-0.1403% [-0.1824%, -0.0981%], hit=17.91%, holm_p=1.96e-9, vs_ung_t=-1.77`), `london signal` (`2093/1270d, net=-0.1649% [-0.2204%, -0.1094%], hit=25.18%, holm_p=1.52e-7, vs_ung_t=-0.95`), `ny signal` (`3110/1465d, net=-0.1234% [-0.1676%, -0.0792%], hit=20.45%, holm_p=1.18e-6, vs_ung_t=-0.38`), `asia retest` (`2696/1416d, net=-0.1432% [-0.1858%, -0.1005%], hit=19.77%, holm_p=1.42e-9, vs_ung_t=-2.03`), `london retest` (`2093/1270d, net=-0.1636% [-0.2183%, -0.1089%], hit=26.37%, holm_p=1.26e-7, vs_ung_t=-0.57`), `ny retest` (`3110/1465d, net=-0.1146% [-0.1599%, -0.0692%], hit=22.57%, holm_p=1.82e-5, vs_ung_t=-0.13`) -> all `MATCH`.
  - `A_r2r bearP40` (`6` cells, `L185,188,191,410,413,416`): nets `-0.1104%` to `-0.1484%`, `vs_ung_t` in `[-0.11, +0.14]` -> `MATCH`.
  - `B_retest range` (`9` cells, `L1379,1406,1433,1514,1541,1568,1649,1676,1703`): `asia k=0.25/0.5/1.0` (`486/374d net=-0.0454%`, `507/389d net=-0.0651%`, `520/394d net=-0.0836%`), `london k=0.25/0.5/1.0` (`390/316d net=-0.2077% holm_p=0.34`, `403/322d net=-0.2124% holm_p=0.23`, `413/330d net=-0.2384% holm_p=0.06`), `ny k=0.25/0.5/1.0` (`439/345d net=-0.1385% holm_p=0.98`, `456/355d net=-0.1415% holm_p=0.97`, `478/370d net=-0.1436% holm_p=0.86`) -> all `MATCH`.
  - `B_retest bearP40` (`9` cells, `L1397,1424,1451,1532,1559,1586,1667,1694,1721`): 3 positive net cells (`asia k=0.25` `L1397` `n=105/81d, net=+0.0826% [-0.2542%, +0.4194%]`; `asia k=0.5` `L1532` `n=111/86d, net=+0.0488%`; `london k=0.25` `L1424` `n=76/68d, net=+0.0369%`), all 9 cells `n=76-116`, `days=68-89`, `holm_p=1.00`, `vs_ung_t <= 0.94` -> all `MATCH`.

## 3. Verification Commands Executed

```bash
python -c "import pathlib; p=pathlib.Path('MyTradingSys/research/gemini_audits_2026-11-04/BLIND_READ_BB_STUDIES_1104.md'); assert p.exists() and len(p.read_text())>400"
python -c "import pathlib; p=pathlib.Path('MyTradingSys/research/gemini_audits_2026-11-04/BLIND_READ_BB_STUDIES_1104.md'); assert p.exists() and 'VERDICT' in p.read_text()"
```
