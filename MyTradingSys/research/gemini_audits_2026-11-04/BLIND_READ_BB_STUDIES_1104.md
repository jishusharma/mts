FOUND=126 DIFF=0 NOT_IN_DATA=0

# Blind Read Audit: Bollinger Range-to-Range, Range-Retest, and Long-Window Studies (`2026-11-04`)

- **Card**: `gemini-blind-read-bb-range-studies-1104` (D11 feeder check `A-20261104-1`)
- **Date**: `2026-11-04`
- **Audited Documents**:
  1. `MyTradingSys/research/bb_range_to_range_2026-11-04/RESULT.md` (lines `1-31`)
  2. `MyTradingSys/research/bb_range_retest_2026-11-04/RESULT.md` (lines `1-45`)
  3. `MyTradingSys/research/bb_long_window_2026-11-04/RESULT_LONG.md` (lines `1-63`)
- **Primary Raw Data Sources (Read & Computed Blind Prior to Reading `RESULT*.md`)**:
  - `MyTradingSys/research/bb_range_to_range_2026-11-04/{counts.csv, dev_cells.csv, dev_survivors.json, regime_mix_count.txt, regime_mix_dev.txt, BLOCKED.md, PRE_REG.md, study.py}`
  - `MyTradingSys/research/bb_range_retest_2026-11-04/{counts.csv, dev_cells.csv, dev_survivors.json, regime_mix_count.txt, regime_mix_dev.txt, BLOCKED.md, PRE_REG.md, study.py}`
  - `MyTradingSys/research/bb_long_window_2026-11-04/{counts_long.csv, dev_cells_long.csv, dev_survivors_long.json, regime_mix_count_long.txt, regime_mix_dev_long.txt, BLOCKED_LONG.md, PRE_REG_LONG.md, study_long.py, gate_long.py}`

## Parameter & Unit Provenance (`SOURCED` vs `OURS`)

- **Cost (`0.14%` = `14 bps` round-trip)**: `SOURCED` (`MyTradingSys/backtest/research_kit.py:31` `TAKER_RT_PCT = 0.14`; cited in `bb_range_to_range_2026-11-04/PRE_REG.md:25`, `bb_range_retest_2026-11-04/PRE_REG.md:23`, `bb_long_window_2026-11-04/PRE_REG_LONG.md:20-21`).
- **Return unit (`%` of entry price; `1% = 100 bps`, `net = gross - 0.14%`) & Day-Clustered SE (`95% CI = mean +/- 1.96 * SE`, `cluster_mean_se`, `cluster_diff`, `holm`)**: `SOURCED` (`MyTradingSys/backtest/research_kit.py`; `bb_range_to_range_2026-11-04/PRE_REG.md:26`).
- **Windows (`DEV = [2022-01-01, 2024-07-01)`, `LONG_DEV = [2017-08-01, 2024-07-01)`)**: `SOURCED` (`MyTradingSys/backtest/splits.py`; `bb_range_to_range_2026-11-04/PRE_REG.md:31`, `bb_long_window_2026-11-04/PRE_REG_LONG.md:28-30`).
- **Malkan Regime Band (`weekly AND monthly RSI14 >= 60` with `close > daily SMA200` for bull; `<= 40` with `close < daily SMA200` for bear)**: `60/40` band `SOURCED` Malkan, `SMA200` `SOURCED-in-repo`, `"range = the rest"` `OURS` (`bb_range_to_range_2026-11-04/PRE_REG.md:14`).
- **Bollinger Bands (`BB(20, 2)` population std of closes), 2:1 Bracket (`STOP_FRAC = 0.5` of band-to-band distance, target = opposite band at signal bar), `TIMEOUT_BARS = 24`, Retest Window (`M = 10`, `N = 10`, `ATR(14)`, `k in {0.25, 0.5, 1.0}`), Session Cutoffs (`08, 13, 21 UTC`), Band-Width `"wide"` Stratum (`500`-bar rolling median), Session-Range `"tagged"` Stratum (`20` prior same-name sessions, `>= 10` needed), and Bear Proxy `P40` (`weekly RSI14 <= 40` alone below `SMA200`)**: `OURS` (`bb_range_to_range_2026-11-04/PRE_REG.md:13-30`, `bb_range_retest_2026-11-04/PRE_REG.md:15-28`, `bb_long_window_2026-11-04/PRE_REG_LONG.md:16-45`).

---

## Study 1: `bb_range_to_range_2026-11-04` (`counts.csv` & `dev_cells.csv` vs `RESULT.md`)

### 1.1 Internal CSV Parity & Regime Mix (`bb_range_to_range_2026-11-04`)

- **Row Count & Parity**: `counts.csv` (`1081` lines = header + `1080` cells) and `dev_cells.csv` (`1081` lines = header + `1080` cells) match `100%` across all `1080` rows on `signals`, `n`, `days`, and `median_stop_pct` (`OURS` verification via `blind_compute.py`).
- **Survivors**: `dev_survivors.json:1` is `[]` (`0` survivors of `6` confirmatory cells), matching `RESULT.md:2,26` (`"0 of 6 cells have net > 0"`, `"0 survivors, dev_survivors.json is []"`).
- **Regime Mix**:

| Metric | CSV / TXT Recomputed (`regime_mix_dev.txt:1` & `regime_mix_count.txt:1`) | Reported in `RESULT.md:1` | Diff / Status |
|---|---|---|---|
| Total DEV weeks | `130 weeks` | `130 weeks DEV` | `MATCH` (`FOUND`) |
| `bull` weeks | `25 (19%)` | `bull 25 (19%)` | `MATCH` (`FOUND`) |
| `bear` weeks | `0 (0%)` | `bear 0 (0%)` | `MATCH` (`FOUND`) |
| `range` weeks | `105 (81%)` | `range 105 (81%)` | `MATCH` (`FOUND`) |
| `n/a` weeks | `0 (0%)` | `n/a 0 (0%)` | `MATCH` (`FOUND`) |

### 1.2 Per-Cell Comparison Table: Confirmatory Family & Regime/Stratum Splits (`bb_range_to_range_2026-11-04`)

Note on Win Rates & Units: `dev_cells.csv` records two win-rate columns: `hit_target` (share reaching the opposite band target, `2:1` reward:risk) and `net_pos_share` (share of trades with `net > 0`, including positive 24-bar time-out exits). Returns in `dev_cells.csv` are in `%` of entry price (`1% = 100 bps`; `net = gross - 0.14%`). Both `%` and `bps` are shown below.

| Cell (`tf, gate, sess, entry, side, width`) | CSV Line (`dev_cells.csv`) | CSV `signals` / `n` / `days` | CSV Win Rates: `hit_target` / `net_pos_share` | CSV `gross %` (`bps`) | CSV `net %` (`bps`) & `[95% CI %]` | CSV `t` / `holm_p` / `vs_ungated (t)` | `RESULT.md` Line & Reported Values | Status |
|---|---|---|---|---|---|---|---|---|
| `15m, range, asia, signal, both, any` *(Confirmatory)* | `L5` | `1200` / `1200` / `656` | `17.00%` (`0.1700`) / `39.50%` (`0.3950`) | `+0.0178%` (`+1.78 bps`) | `-0.1222%` (`-12.22 bps`) `[-0.1775, -0.0669]` | `t=-4.33`, `holm_p=5.73e-5`, `vs_ung=+0.0060% (t=+0.50)` | `RESULT.md:10`: `n=1200, days=656, gross=+0.018%, net=-0.122% [-0.177, -0.067], hit=17%, vs_ung=+0.006 (0.5)` | `MATCH` |
| `15m, range, london, signal, both, any` *(Confirmatory)* | `L8` | `951` / `951` / `586` | `28.29%` (`0.2829`) / `33.96%` (`0.3396`) | `+0.0020%` (`+0.20 bps`) | `-0.1380%` (`-13.80 bps`) `[-0.2003, -0.0757]` | `t=-4.34`, `holm_p=5.73e-5`, `vs_ung=-0.0009% (t=-0.07)` | `RESULT.md:11`: `n=951, days=586, gross=+0.002%, net=-0.138% [-0.200, -0.076], hit=28%, vs_ung=-0.001 (-0.1)` | `MATCH` |
| `15m, range, ny, signal, both, any` *(Confirmatory)* | `L11` | `1637` / `1634` / `702` | `21.05%` (`0.2105`) / `37.39%` (`0.3739`) | `-0.0131%` (`-1.31 bps`) | `-0.1531%` (`-15.31 bps`) `[-0.2063, -0.0999]` | `t=-5.64`, `holm_p=1.02e-7`, `vs_ung=-0.0088% (t=-0.77)` | `RESULT.md:12`: `n=1634, days=702, gross=-0.013%, net=-0.153% [-0.206, -0.100], hit=21%, vs_ung=-0.009 (-0.8)` | `MATCH` |
| `15m, range, asia, retest, both, any` *(Confirmatory)* | `L185` | `1200` / `1200` / `657` | `19.17%` (`0.1917`) / `39.67%` (`0.3967`) | `+0.0194%` (`+1.94 bps`) | `-0.1206%` (`-12.06 bps`) `[-0.1764, -0.0649]` | `t=-4.24`, `holm_p=5.73e-5`, `vs_ung=+0.0057% (t=+0.45)` | `RESULT.md:13`: `n=1200, days=657, gross=+0.019%, net=-0.121% [-0.176, -0.065], hit=19%, vs_ung=+0.006 (0.5)` | `MATCH` |
| `15m, range, london, retest, both, any` *(Confirmatory)* | `L188` | `951` / `951` / `586` | `29.65%` (`0.2965`) / `35.86%` (`0.3586`) | `+0.0095%` (`+0.95 bps`) | `-0.1305%` (`-13.05 bps`) `[-0.1932, -0.0677]` | `t=-4.08`, `holm_p=5.73e-5`, `vs_ung=-0.0015% (t=-0.11)` | `RESULT.md:14`: `n=951, days=586, gross=+0.010%, net=-0.130% [-0.193, -0.068], hit=30%, vs_ung=-0.001 (-0.1)` | `MATCH` |
| `15m, range, ny, retest, both, any` *(Confirmatory)* | `L191` | `1637` / `1634` / `702` | `23.32%` (`0.2332`) / `39.05%` (`0.3905`) | `-0.0025%` (`-0.25 bps`) | `-0.1425%` (`-14.25 bps`) `[-0.1962, -0.0888]` | `t=-5.20`, `holm_p=9.71e-7`, `vs_ung=-0.0076% (t=-0.65)` | `RESULT.md:15`: `n=1634, days=702, gross=-0.003%, net=-0.143% [-0.196, -0.089], hit=23%, vs_ung=-0.008 (-0.7)` | `MATCH` |
| `15m, range, ALL, signal, both, any` *(Regime split: range)* | `L2` | `4260` / `4256` / `737` | `21.55%` (`0.2155`) / `38.04%` (`0.3804`) | `+0.0101%` (`+1.01 bps`) | `-0.1299%` (`-12.99 bps`) `[-0.1612, -0.0986]` | `t=-8.14`, `vs_ung=-0.0030% (t=-0.46)` | `RESULT.md:17` & `Study 2 RESULT.md:39`: `range n 4256 net -0.130% [-0.161, -0.099]`, `t -0.5`, `target hit 22%`, `80% of signals` (`4260/5315=80.15%`) | `MATCH` |
| `15m, all, ALL, signal, both, any` *(Regime split: ungated)* | `L47` | `5315` / `5311` / `912` | `21.48%` (`0.2148`) / `38.17%` (`0.3817`) | `+0.0131%` (`+1.31 bps`) | `-0.1269%` (`-12.69 bps`) `[-0.1543, -0.0994]` | `t=-9.05` | `RESULT.md:17`: `ungated n 5311 net -0.127% [-0.154, -0.099]` | `MATCH` |
| `15m, bull, ALL, signal, both, any` *(Regime split: bull)* | `L92` | `1055` / `1055` / `175` | `21.23%` (`0.2123`) / `38.67%` (`0.3867`) | `+0.0253%` (`+2.53 bps`) | `-0.1147%` (`-11.47 bps`) `[-0.1713, -0.0581]` | `t=-3.97` | `RESULT.md:17`: `bull-regime rows (15m n 1055, net -0.115%)` | `MATCH` |
| `15m, bear, ALL, signal, both, any` *(Regime split: bear)* | `L137` | `0` / `0` / `0` | `n/a` | `n/a` | `n/a` | `n=0` | `RESULT.md:2,17`: `bear 0` | `MATCH` |
| `15m, range, ALL, retest, both, any` *(Retest pooled)* | `L182` | `4260` / `4256` / `737` | `23.43%` (`0.2343`) / `39.22%` (`0.3922`) | `+0.0166%` (`+1.66 bps`) | `-0.1234%` (`-12.34 bps`) `[-0.1547, -0.0921]` | `t=-7.72`, `vs_ung=-0.0031% (t=-0.45)` | `RESULT.md:22` & `Study 2 RESULT.md:39`: `fills 4256 of 4260 range signals (99.9%)`, `net -0.123% [-0.155, -0.092], hit 23%` | `MATCH` |
| `15m, range, late, signal, both, any` *(Descriptive session)* | `L14` | `472` / `471` / `374` | `21.23%` (`0.2123`) / `44.80%` (`0.4480`) | `+0.0874%` (`+8.74 bps`) | `-0.0526%` (`-5.26 bps`) `[-0.1455, +0.0403]` | `t=-1.11`, `vs_ung=-0.0093% (t=-0.46)` | `RESULT.md:18`: `15m late (n 471, net -0.053% [-0.145, +0.040])` | `MATCH` |
| `15m, range, ALL, signal, both, wide` *(Width stratum: wide)* | `L3` | `1764` / `1761` / `606` | `15.33%` (`0.1533`) / `42.31%` (`0.4231`) | `+0.0107%` (`+1.07 bps`) | `-0.1293%` (`-12.93 bps`) `[-0.1968, -0.0618]` | `t=-3.76` | `RESULT.md:19`: `wide-band signals net -0.129% [-0.197, -0.062] (target hit 15%)` | `MATCH` |
| `15m, range, ALL, signal, both, narrow` *(Width stratum: narrow)* | `L4` | `2496` / `2495` / `684` | `25.93%` (`0.2593`) / `35.03%` (`0.3503`) | `+0.0097%` (`+0.97 bps`) | `-0.1303%` (`-13.03 bps`) `[-0.1571, -0.1035]` | `t=-9.53` | `RESULT.md:19`: `narrow net -0.130% [-0.157, -0.103] (hit 26%)` | `MATCH` |
| `15m, range, ALL, signal, long, any` *(Side split: long)* | `L17` | `2190` / `2190` / `699` | `21.55%` (`0.2155`) / `38.77%` (`0.3877`) | `+0.0324%` (`+3.24 bps`) | `-0.1076%` (`-10.76 bps`) `[-0.1540, -0.0613]` | `t=-4.55` | `RESULT.md:20`: `long net -0.108% [-0.154, -0.061]` | `MATCH` |
| `15m, range, ALL, signal, short, any` *(Side split: short)* | `L32` | `2070` / `2066` / `692` | `21.54%` (`0.2154`) / `37.27%` (`0.3727`) | `-0.0135%` (`-1.35 bps`) | `-0.1535%` (`-15.35 bps`) `[-0.1951, -0.1119]` | `t=-7.23` | `RESULT.md:20`: `short -0.153% [-0.195, -0.112]` | `MATCH` |
| `1h, range, ALL, signal, both, any` *(TF split: 1h)* | `L362` | `1084` / `1080` / `633` | `21.02%` (`0.2102`) / `35.65%` (`0.3565`) | `-0.0171%` (`-1.71 bps`) | `-0.1571%` (`-15.71 bps`) `[-0.2778, -0.0365]` | `t=-2.55` | `RESULT.md:21`: `1h range signal n 1080 net -0.157% [-0.278, -0.036]` | `MATCH` |
| `1h, range, late, signal, both, any` *(TF/sess split: 1h late)* | `L374` | `141` / `141` / `137` | `24.11%` (`0.2411`) / `42.55%` (`0.4255`) | `+0.2733%` (`+27.33 bps`) | `+0.1333%` (`+13.33 bps`) `[-0.2398, +0.5063]` | `t=+0.70` | `RESULT.md:21`: `1h late +0.133% [-0.240, +0.506] (n 141)` | `MATCH` |
| `4h, range, ALL, signal, both, any` *(TF split: 4h)* | `L722` | `253` / `252` / `224` | `19.05%` (`0.1905`) / `34.13%` (`0.3413`) | `-0.3094%` (`-30.94 bps`) | `-0.4494%` (`-44.94 bps`) `[-0.9185, +0.0196]` | `t=-1.88` | `RESULT.md:21`: `4h n 252 net -0.449% [-0.919, +0.020]` | `MATCH` |

---

## Study 2: `bb_range_retest_2026-11-04` (`counts.csv` & `dev_cells.csv` vs `RESULT.md`)

### 2.1 Internal CSV Parity, Regime Mix & Fill Rates (`bb_range_retest_2026-11-04`)

- **Row Count & Parity**: `counts.csv` (`271` lines = header + `270` cells) and `dev_cells.csv` (`271` lines = header + `270` cells) match `100%` across all `270` rows on `signals`, `reentered`, `fills`, `fill_rate`, `n`, `days`, and `median_stop_pct` (`OURS` verification via `blind_compute.py`).
- **Survivors & Power Gate**: `dev_survivors.json:1` is `[]` (`0` survivors of `9` confirmatory cells). `BLOCKED.md:3-11` shows `146-186` days per cell vs `478-1783` needed (`m = 127`), matching `RESULT.md:2`.
- **Regime Mix**: `regime_mix_dev.txt:1` (`130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)`) matches `RESULT.md:1` (`100%`).
- **Fill-Rate Table Verification (`RESULT.md:10-18` vs `counts.csv` / `dev_cells.csv`)**:

| Session (`15m, range, tagged, both`) | `k = 0.25` CSV (`fills / signals = fill_rate`, Line) vs `RESULT.md` | `k = 0.5` CSV (`fills / signals = fill_rate`, Line) vs `RESULT.md` | `k = 1.0` CSV (`fills / signals = fill_rate`, Line) vs `RESULT.md` | Re-entry Rate (`reentered / signals`) | Status |
|---|---|---|---|---|---|
| `ALL` (`all sessions`) | `752 / 1187 = 63.35%` (`L2`) vs `752 / 1187 = 63%` (`RESULT.md:12`) | `785 / 1187 = 66.13%` (`L92`) vs `785 / 1187 = 66%` (`RESULT.md:12`) | `813 / 1187 = 68.49%` (`L182`) vs `813 / 1187 = 68%` (`RESULT.md:12`) | `824 / 1187 = 69.42%` (`RESULT.md:18`: `824 of 1187 (69%)`; `fills/reentered`: `91.26%-98.67%` vs `91-99%`) | `MATCH` |
| `asia` | `225 / 360 = 62.50%` (`L20`) vs `62%` (`RESULT.md:13`) | `235 / 360 = 65.28%` (`L110`) vs `65%` (`RESULT.md:13`) | `244 / 360 = 67.78%` (`L200`) vs `68%` (`RESULT.md:13`) | `248 / 360 = 68.89%` (`fills/reent`: `90.73%-98.39%`) | `MATCH` |
| `london` | `175 / 260 = 67.31%` (`L38`) vs `67%` (`RESULT.md:14`) | `180 / 260 = 69.23%` (`L128`) vs `69%` (`RESULT.md:14`) | `186 / 260 = 71.54%` (`L218`) vs `72%` (`RESULT.md:14`) | `189 / 260 = 72.69%` (`fills/reent`: `92.59%-98.41%`) | `MATCH` |
| `ny` | `215 / 365 = 58.90%` (`L56`) vs `59%` (`RESULT.md:15`) | `224 / 365 = 61.37%` (`L146`) vs `61%` (`RESULT.md:15`) | `233 / 365 = 63.84%` (`L236`) vs `64%` (`RESULT.md:15`) | `236 / 365 = 64.66%` (`fills/reent`: `91.10%-98.73%`) | `MATCH` |
| `late` *(descriptive)* | `137 / 202 = 67.82%` (`L74`) vs `68%` (`RESULT.md:16`) | `146 / 202 = 72.28%` (`L164`) vs `72%` (`RESULT.md:16`) | `150 / 202 = 74.26%` (`L254`) vs `74%` (`RESULT.md:16`) | `151 / 202 = 74.75%` (`fills/reent`: `90.73%-99.34%`) | `MATCH` |

### 2.2 Per-Cell Comparison Table: Confirmatory 9-Cell Family & Regime/Tag Splits (`bb_range_retest_2026-11-04`)

| Cell (`gate, tag, sess, k, side`) | CSV Line (`dev_cells.csv`) | CSV `n` / `days` (`fills/sig`) | CSV Win Rates: `hit_target` / `net_pos_share` | CSV `gross %` (`bps`) | CSV `net %` (`bps`) & `[95% CI %]` | CSV `t` / `holm_p` / `vs_ung_t` / `vs_untag_t` | `RESULT.md` Line & Reported Values | Status |
|---|---|---|---|---|---|---|---|---|
| `range, tagged, asia, k=0.25, both` *(Confirmatory)* | `L20` | `225` / `176` (`225/360`) | `15.56%` (`0.1556`) / `38.22%` (`0.3822`) | `+0.0459%` (`+4.59 bps`) | `-0.0941%` (`-9.41 bps`) `[-0.2404, +0.0522]` | `t=-1.26`, `holm_p=0.8888`, `vs_ung_t=-0.11`, `vs_untag_t=+0.17` | `RESULT.md:24`: `n=225, days=176, gross=+0.046%, net=-0.094% [-0.240, +0.052], hit=16%, Holm p=0.89, vs_ung_t=-0.1` | `MATCH` |
| `range, tagged, asia, k=0.5, both` *(Confirmatory)* | `L110` | `235` / `182` (`235/360`) | `15.74%` (`0.1574`) / `37.02%` (`0.3702`) | `+0.0348%` (`+3.48 bps`) | `-0.1052%` (`-10.52 bps`) `[-0.2478, +0.0374]` | `t=-1.45`, `holm_p=0.8888`, `vs_ung_t=-0.32`, `vs_untag_t=-0.02` | `RESULT.md:25`: `n=235, days=182, gross=+0.035%, net=-0.105% [-0.248, +0.037], hit=16%, Holm p=0.89, vs_ung_t=-0.3` | `MATCH` |
| `range, tagged, asia, k=1.0, both` *(Confirmatory)* | `L200` | `244` / `186` (`244/360`) | `14.34%` (`0.1434`) / `35.66%` (`0.3566`) | `+0.0085%` (`+0.85 bps`) | `-0.1315%` (`-13.15 bps`) `[-0.2698, +0.0068]` | `t=-1.86`, `holm_p=0.4372`, `vs_ung_t=-0.57`, `vs_untag_t=-0.28` | `RESULT.md:26`: `n=244, days=186, gross=+0.008%, net=-0.132% [-0.270, +0.007], hit=14%, Holm p=0.44, vs_ung_t=-0.6` | `MATCH` |
| `range, tagged, london, k=0.25, both` *(Confirmatory)* | `L38` | `175` / `146` (`175/260`) | `29.14%` (`0.2914`) / `34.29%` (`0.3429`) | `+0.0068%` (`+0.68 bps`) | `-0.1332%` (`-13.32 bps`) `[-0.3207, +0.0543]` | `t=-1.39`, `holm_p=0.8888`, `vs_ung_t=+0.71`, `vs_untag_t=+0.10` | `RESULT.md:27`: `n=175, days=146, gross=+0.007%, net=-0.133% [-0.321, +0.054], hit=29%, Holm p=0.89, vs_ung_t=0.7` | `MATCH` |
| `range, tagged, london, k=0.5, both` *(Confirmatory)* | `L128` | `180` / `149` (`180/260`) | `28.33%` (`0.2833`) / `31.67%` (`0.3167`) | `-0.0349%` (`-3.49 bps`) | `-0.1749%` (`-17.49 bps`) `[-0.3499, +0.0001]` | `t=-1.96`, `holm_p=0.4008`, `vs_ung_t=+0.74`, `vs_untag_t=-0.41` | `RESULT.md:28`: `n=180, days=149, gross=-0.035%, net=-0.175% [-0.350, 0.000], hit=28%, Holm p=0.40, vs_ung_t=0.7` | `MATCH` |
| `range, tagged, london, k=1.0, both` *(Confirmatory)* | `L218` | `186` / `155` (`186/260`) | `27.96%` (`0.2796`) / `31.72%` (`0.3172`) | `-0.0607%` (`-6.07 bps`) | `-0.2007%` (`-20.07 bps`) `[-0.3687, -0.0327]` | `t=-2.34`, `holm_p=0.1731`, `vs_ung_t=+0.83`, `vs_untag_t=-0.71` | `RESULT.md:29`: `n=186, days=155, gross=-0.061%, net=-0.201% [-0.369, -0.033], hit=28%, Holm p=0.17, vs_ung_t=0.8` | `MATCH` |
| `range, tagged, ny, k=0.25, both` *(Confirmatory)* | `L56` | `215` / `162` (`215/365`) | `15.81%` (`0.1581`) / `42.33%` (`0.4233`) | `+0.0218%` (`+2.18 bps`) | `-0.1182%` (`-11.82 bps`) `[-0.3045, +0.0681]` | `t=-1.24`, `holm_p=0.8888`, `vs_ung_t=+0.43`, `vs_untag_t=+0.01` | `RESULT.md:30`: `n=215, days=162, gross=+0.022%, net=-0.118% [-0.305, +0.068], hit=16%, Holm p=0.89, vs_ung_t=0.4` | `MATCH` |
| `range, tagged, ny, k=0.5, both` *(Confirmatory)* | `L146` | `224` / `169` (`224/365`) | `16.96%` (`0.1696`) / `43.30%` (`0.4330`) | `+0.0567%` (`+5.67 bps`) | `-0.0833%` (`-8.33 bps`) `[-0.2675, +0.1010]` | `t=-0.89`, `holm_p=0.8888`, `vs_ung_t=+0.28`, `vs_untag_t=+0.39` | `RESULT.md:31`: `n=224, days=169, gross=+0.057%, net=-0.083% [-0.268, +0.101], hit=17%, Holm p=0.89, vs_ung_t=0.3` | `MATCH` |
| `range, tagged, ny, k=1.0, both` *(Confirmatory)* | `L236` | `233` / `174` (`233/365`) | `17.17%` (`0.1717`) / `43.35%` (`0.4335`) | `+0.0674%` (`+6.74 bps`) | `-0.0726%` (`-7.26 bps`) `[-0.2530, +0.1078]` | `t=-0.79`, `holm_p=0.8888`, `vs_ung_t=+0.37`, `vs_untag_t=+0.53` | `RESULT.md:32`: `n=233, days=174, gross=+0.067%, net=-0.073% [-0.253, +0.108], hit=17%, Holm p=0.89, vs_ung_t=0.4` | `MATCH` |
| `range, tagged, ALL, k=0.5, both` *(Pooled tagged range)* | `L92` | `785` / `399` (`785/1187`) | `19.24%` (`0.1924`) / `39.24%` (`0.3924`) | `+0.0317%` (`+3.17 bps`) | `-0.1083%` (`-10.83 bps`) `[-0.1948, -0.0217]` | `t=-2.45`, `vs_ung_t=+0.49`, `vs_untag_t=+0.15` | `RESULT.md:34,35,39`: `tagged range net -0.108% [-0.195, -0.022]` | `MATCH` |
| `range, untagged, ALL, k=0.5, both` *(Untagged control)* | `L95` | `2289` / `687` (`2291/3073=74.55%`) | `28.96%` (`0.2896`) / `36.44%` (`0.3644`) | `+0.0247%` (`+2.47 bps`) | `-0.1153%` (`-11.53 bps`) `[-0.1397, -0.0908]` | `t=-9.25` | `RESULT.md:18,34`: `Untagged range signals fill 75% at k=0.5`, `untagged range -0.115% [-0.140, -0.091]` | `MATCH` |
| `all, tagged, ALL, k=0.5, both` *(All-regime tagged control)* | `L101` | `991` / `498` (`991/1470=67.41%`) | `19.17%` (`0.1917`) / `38.24%` (`0.3824`) | `+0.0218%` (`+2.18 bps`) | `-0.1182%` (`-11.82 bps`) `[-0.1954, -0.0411]` | `t=-3.00` | `RESULT.md:35`: `tagged all-regime -0.118` | `MATCH` |
| `range, tagged, ALL, k=0.5, long` *(Side split: long)* | `L93` | `427` / `284` (`427/619`) | `18.97%` (`0.1897`) / `39.58%` (`0.3958`) | `+0.0124%` (`+1.24 bps`) | `-0.1276%` (`-12.76 bps`) `[-0.2577, +0.0025]` | `t=-1.92` | `RESULT.md:36`: `long net -0.128% [-0.258, +0.002] (n 427)` | `MATCH` |
| `range, tagged, ALL, k=0.5, short` *(Side split: short)* | `L94` | `358` / `242` (`358/568`) | `19.55%` (`0.1955`) / `38.83%` (`0.3883`) | `+0.0548%` (`+5.48 bps`) | `-0.0852%` (`-8.52 bps`) `[-0.1893, +0.0188]` | `t=-1.61` | `RESULT.md:36`: `short -0.085% [-0.189, +0.019] (n 358)` | `MATCH` |

---

## Study 3: `bb_long_window_2026-11-04` (`counts_long.csv` & `dev_cells_long.csv` vs `RESULT_LONG.md`)

### 3.1 Internal CSV Parity & Long-Window Regime Mix (`bb_long_window_2026-11-04`)

- **Row Count & Parity**: `counts_long.csv` (`1756` lines = header + `1755` cells: `1350` `A_r2r` + `405` `B_retest`) and `dev_cells_long.csv` (`1756` lines = header + `1755` cells) match `100%` across all `1755` rows on `signals`, `reentered`, `fills`, `fill_rate`, `n`, `days`, and `median_stop_pct` (`OURS` verification via `blind_compute.py`).
- **Survivors & Power Gate**: `dev_survivors_long.json:1` is `[]` (`0` survivors of `30` pooled confirmatory cells). `BLOCKED_LONG.md:3-32` shows `6` `PASS` cells (`A_r2r range` `1270-1465` days, `MDE+cost = 0.236-0.250`) and `24` `BLOCK` cells (`A_r2r bearP40` `318-378` days; `B_retest range` `316-394` days; `B_retest bearP40` `68-89` days, `MDE+cost = 0.654-1.117`), matching `RESULT_LONG.md:2-3,18,49-50`.
- **Regime Mix (`regime_mix_dev_long.txt:1-2` & `regime_mix_count_long.txt:1-2` vs `RESULT_LONG.md:1,12`)**:

| Metric | CSV / TXT Recomputed (`regime_mix_dev_long.txt:1-2`) | Reported in `RESULT_LONG.md:1,12` | Diff / Status |
|---|---|---|---|
| Total long DEV weeks | `360 weeks` | `360 weeks long DEV (2017-08-07..2024-06-24)` | `MATCH` (`FOUND`) |
| Primary `bull` weeks | `73 (20%)` | `bull 73 (20%)` | `MATCH` (`FOUND`) |
| Primary `bear` weeks (Malkan) | `0 (0%)` (`primary Malkan (weekly AND monthly <=40) 0`) | `bear 0 (0%)` / `primary Malkan (weekly AND monthly <=40) 0` | `MATCH` (`FOUND`) |
| Primary `range` weeks | `222 (62%)` | `range 222 (62%)` | `MATCH` (`FOUND`) |
| Warm-up `n/a` weeks | `65 (18%)` | `n/a 65 (18%)` | `MATCH` (`FOUND`) |
| Proxy `P40` `bear` weeks (`OURS`) | `57 (16%)` (`range` becomes `165 (46%)` under P40 partition) | `proxy P40 (weekly <=40 alone, below SMA200, OURS) 57` | `MATCH` (`FOUND`) |

### 3.2 Per-Cell Comparison Table: 30-Cell Confirmatory Family (`bb_long_window_2026-11-04`)

| Cell (`study, gate, sess, entry/k`) | CSV Line (`dev_cells_long.csv`) | CSV `n` / `days` (`fills/sig` for B) | CSV Win Rates: `hit_target` / `net_pos_share` (B `fill_rate`) | CSV `gross %` (`bps`) | CSV `net %` (`bps`) & `[95% CI %]` | CSV `t` / `holm_p` / `vs_ung_t` | `RESULT_LONG.md` Line & Reported Values | Status |
|---|---|---|---|---|---|---|---|---|
| `A_r2r, range, asia, signal` *(PASS gate)* | `L5` | `2697` / `1412` | `17.91%` / `38.15%` | `-0.0003%` (`-0.03 bps`) | `-0.1403%` (`-14.03 bps`) `[-0.1824, -0.0981]` | `t=-6.53`, `holm_p=1.96e-9`, `vs_ung_t=-1.77` | `RESULT_LONG.md:26`: `2697 / 1412, -0.140 [-0.182, -0.098], hit 18%, Holm <0.001, Gate t -1.8` | `MATCH` |
| `A_r2r, range, london, signal` *(PASS gate)* | `L8` | `2093` / `1270` | `25.18%` / `35.59%` | `-0.0249%` (`-2.49 bps`) | `-0.1649%` (`-16.49 bps`) `[-0.2204, -0.1094]` | `t=-5.83`, `holm_p=1.52e-7`, `vs_ung_t=-0.95` | `RESULT_LONG.md:27`: `2093 / 1270, -0.165 [-0.220, -0.109], hit 25%, Holm <0.001, Gate t -0.9` | `MATCH` |
| `A_r2r, range, ny, signal` *(PASS gate)* | `L11` | `3110` / `1465` | `20.45%` / `39.13%` | `+0.0166%` (`+1.66 bps`) | `-0.1234%` (`-12.34 bps`) `[-0.1676, -0.0792]` | `t=-5.47`, `holm_p=1.18e-6`, `vs_ung_t=-0.38` | `RESULT_LONG.md:28`: `3110 / 1465, -0.123 [-0.168, -0.079], hit 20%, Holm <0.001, Gate t -0.4` | `MATCH` |
| `A_r2r, range, asia, retest` *(PASS gate)* | `L230` | `2696` / `1416` | `19.77%` / `38.87%` | `-0.0032%` (`-0.32 bps`) | `-0.1432%` (`-14.32 bps`) `[-0.1858, -0.1005]` | `t=-6.58`, `holm_p=1.42e-9`, `vs_ung_t=-2.03` | `RESULT_LONG.md:29`: `2696 / 1416, -0.143 [-0.186, -0.101], hit 20%, Holm <0.001, Gate t -2.0` | `MATCH` |
| `A_r2r, range, london, retest` *(PASS gate)* | `L233` | `2093` / `1270` | `26.37%` / `36.60%` | `-0.0236%` (`-2.36 bps`) | `-0.1636%` (`-16.36 bps`) `[-0.2183, -0.1089]` | `t=-5.86`, `holm_p=1.26e-7`, `vs_ung_t=-0.57` | `RESULT_LONG.md:30`: `2093 / 1270, -0.164 [-0.218, -0.109], hit 26%, Holm <0.001, Gate t -0.6` | `MATCH` |
| `A_r2r, range, ny, retest` *(PASS gate)* | `L236` | `3110` / `1465` | `22.57%` / `40.74%` | `+0.0254%` (`+2.54 bps`) | `-0.1146%` (`-11.46 bps`) `[-0.1599, -0.0692]` | `t=-4.95`, `holm_p=1.82e-5`, `vs_ung_t=-0.13` | `RESULT_LONG.md:31`: `3110 / 1465, -0.115 [-0.160, -0.069], hit 23%, Holm <0.001, Gate t -0.1` | `MATCH` |
| `A_r2r, bearP40, asia, signal` *(BLOCK gate)* | `L185` | `680` / `365` | `17.65%` / `36.32%` | `+0.0296%` (`+2.96 bps`) | `-0.1104%` (`-11.04 bps`) `[-0.2012, -0.0196]` | `t=-2.38`, `holm_p=0.3392`, `vs_ung_t=+0.14` | `RESULT_LONG.md:15`: `six cells all net -0.110 to -0.148%, CIs mostly below zero, gate effect t within +-0.1` | `MATCH` |
| `A_r2r, bearP40, london, signal` *(BLOCK gate)* | `L188` | `502` / `318` | `26.29%` / `37.25%` | `-0.0037%` (`-0.37 bps`) | `-0.1437%` (`-14.37 bps`) `[-0.2899, +0.0026]` | `t=-1.93`, `holm_p=0.8582`, `vs_ung_t=+0.12` | `RESULT_LONG.md:15`: `net -0.110 to -0.148%` | `MATCH` |
| `A_r2r, bearP40, ny, signal` *(BLOCK gate)* | `L191` | `825` / `378` | `21.70%` / `39.64%` | `+0.0179%` (`+1.79 bps`) | `-0.1221%` (`-12.21 bps`) `[-0.2176, -0.0266]` | `t=-2.51`, `holm_p=0.2685`, `vs_ung_t=-0.08` | `RESULT_LONG.md:15`: `net -0.110 to -0.148%` | `MATCH` |
| `A_r2r, bearP40, asia, retest` *(BLOCK gate)* | `L410` | `679` / `366` | `20.03%` / `37.26%` | `+0.0221%` (`+2.21 bps`) | `-0.1179%` (`-11.79 bps`) `[-0.2109, -0.0249]` | `t=-2.49`, `holm_p=0.2719`, `vs_ung_t=-0.06` | `RESULT_LONG.md:15`: `net -0.110 to -0.148%` | `MATCH` |
| `A_r2r, bearP40, london, retest` *(BLOCK gate)* | `L413` | `502` / `318` | `27.29%` / `38.45%` | `-0.0084%` (`-0.84 bps`) | `-0.1484%` (`-14.84 bps`) `[-0.2948, -0.0021]` | `t=-1.99`, `holm_p=0.7966`, `vs_ung_t=+0.10` | `RESULT_LONG.md:15`: `net -0.110 to -0.148%` | `MATCH` |
| `A_r2r, bearP40, ny, retest` *(BLOCK gate)* | `L416` | `825` / `378` | `23.88%` / `40.48%` | `+0.0223%` (`+2.23 bps`) | `-0.1177%` (`-11.77 bps`) `[-0.2143, -0.0211]` | `t=-2.39`, `holm_p=0.3392`, `vs_ung_t=-0.11` | `RESULT_LONG.md:15`: `net -0.110 to -0.148%` | `MATCH` |
| `B_retest, range, asia, k=0.25` *(BLOCK gate)* | `L1379` | `486` / `374` (`486/774`) | `19.14%` / `41.15%` (`fill=62.79%`) | `+0.0946%` (`+9.46 bps`) | `-0.0454%` (`-4.54 bps`) `[-0.1709, +0.0802]` | `t=-0.71`, `holm_p=1.0000`, `vs_ung_t=-0.96` | `RESULT_LONG.md:32`: `486 / 374, -0.045 [-0.171, +0.080], fill 63%, Holm 1.00, Gate t -1.0` | `MATCH` |
| `B_retest, range, asia, k=0.5` *(BLOCK gate)* | `L1514` | `507` / `389` (`507/774`) | `19.53%` / `40.04%` (`fill=65.50%`) | `+0.0749%` (`+7.49 bps`) | `-0.0651%` (`-6.51 bps`) `[-0.1797, +0.0496]` | `t=-1.11`, `holm_p=1.0000`, `vs_ung_t=-1.05` | `RESULT_LONG.md:33`: `507 / 389, -0.065 [-0.180, +0.050], fill 66%, Holm 1.00, Gate t -1.0` | `MATCH` |
| `B_retest, range, asia, k=1.0` *(BLOCK gate)* | `L1649` | `520` / `394` (`520/774`) | `19.04%` / `39.42%` (`fill=67.18%`) | `+0.0564%` (`+5.64 bps`) | `-0.0836%` (`-8.36 bps`) `[-0.1930, +0.0257]` | `t=-1.50`, `holm_p=1.0000`, `vs_ung_t=-1.12` | `RESULT_LONG.md:34`: `520 / 394, -0.084 [-0.193, +0.026], fill 67%, Holm 1.00, Gate t -1.1` | `MATCH` |
| `B_retest, range, london, k=0.25` *(BLOCK gate)* | `L1406` | `390` / `316` (`390/600`) | `23.33%` / `37.18%` (`fill=65.00%`) | `-0.0677%` (`-6.77 bps`) | `-0.2077%` (`-20.77 bps`) `[-0.3787, -0.0368]` | `t=-2.38`, `holm_p=0.3392`, `vs_ung_t=-0.18` | `RESULT_LONG.md:35`: `390 / 316, -0.208 [-0.379, -0.037], fill 65%, Holm 0.34, Gate t -0.2` | `MATCH` |
| `B_retest, range, london, k=0.5` *(BLOCK gate)* | `L1541` | `403` / `322` (`403/600`) | `24.07%` / `35.98%` (`fill=67.17%`) | `-0.0724%` (`-7.24 bps`) | `-0.2124%` (`-21.24 bps`) `[-0.3736, -0.0512]` | `t=-2.58`, `holm_p=0.2256`, `vs_ung_t=-0.24` | `RESULT_LONG.md:36`: `403 / 322, -0.212 [-0.374, -0.051], fill 67%, Holm 0.23, Gate t -0.2` | `MATCH` |
| `B_retest, range, london, k=1.0` *(BLOCK gate)* | `L1676` | `413` / `330` (`413/600`) | `23.73%` / `35.35%` (`fill=68.83%`) | `-0.0984%` (`-9.84 bps`) | `-0.2384%` (`-23.84 bps`) `[-0.3926, -0.0841]` | `t=-3.03`, `holm_p=0.0589`, `vs_ung_t=-0.61` | `RESULT_LONG.md:37`: `413 / 330, -0.238 [-0.393, -0.084], fill 69%, Holm 0.06, Gate t -0.6` | `MATCH` |
| `B_retest, range, ny, k=0.25` *(BLOCK gate)* | `L1433` | `439` / `345` (`439/749`) | `17.54%` / `40.55%` (`fill=58.61%`) | `+0.0015%` (`+0.15 bps`) | `-0.1385%` (`-13.85 bps`) `[-0.2914, +0.0143]` | `t=-1.78`, `holm_p=0.9838`, `vs_ung_t=+0.95` | `RESULT_LONG.md:38`: `439 / 345, -0.139 [-0.291, +0.014], fill 59%, Holm 0.98, Gate t +1.0` | `MATCH` |
| `B_retest, range, ny, k=0.5` *(BLOCK gate)* | `L1568` | `456` / `355` (`456/749`) | `18.64%` / `39.91%` (`fill=60.88%`) | `-0.0015%` (`-0.15 bps`) | `-0.1415%` (`-14.15 bps`) `[-0.2940, +0.0111]` | `t=-1.82`, `holm_p=0.9669`, `vs_ung_t=+0.56` | `RESULT_LONG.md:39`: `456 / 355, -0.141 [-0.294, +0.011], fill 61%, Holm 0.97, Gate t +0.6` | `MATCH` |
| `B_retest, range, ny, k=1.0` *(BLOCK gate)* | `L1703` | `478` / `370` (`478/749`) | `18.41%` / `39.96%` (`fill=63.82%`) | `-0.0036%` (`-0.36 bps`) | `-0.1436%` (`-14.36 bps`) `[-0.2894, +0.0023]` | `t=-1.93`, `holm_p=0.8582`, `vs_ung_t=+0.31` | `RESULT_LONG.md:40`: `478 / 370, -0.144 [-0.289, +0.002], fill 64%, Holm 0.86, Gate t +0.3` | `MATCH` |
| `B_retest, bearP40, asia, k=0.25` *(BLOCK gate)* | `L1397` | `105` / `81` (`105/182`) | `20.95%` / `40.95%` (`fill=57.69%`) | `+0.2226%` (`+22.26 bps`) | `+0.0826%` (`+8.26 bps`) `[-0.2542, +0.4194]` | `t=+0.48`, `holm_p=1.0000`, `vs_ung_t=+0.58` | `RESULT_LONG.md:18`: `asia k0.25 +0.083% [-0.254, +0.419] (n 105), Holm p = 1.00, gate t <= 0.9` | `MATCH` |
| `B_retest, bearP40, london, k=0.25` *(BLOCK gate)* | `L1424` | `76` / `68` (`76/127`) | `26.32%` / `43.42%` (`fill=59.84%`) | `+0.1769%` (`+17.69 bps`) | `+0.0369%` (`+3.69 bps`) `[-0.5301, +0.6039]` | `t=+0.13`, `holm_p=1.0000`, `vs_ung_t=+0.94` | `RESULT_LONG.md:18`: `london k0.25 +0.037% (n 76), Holm p = 1.00, gate t <= 0.9` | `MATCH` |
| `B_retest, bearP40, ny, k=0.25` *(BLOCK gate)* | `L1451` | `109` / `84` (`109/186`) | `20.18%` / `42.20%` (`fill=58.60%`) | `+0.0259%` (`+2.59 bps`) | `-0.1141%` (`-11.41 bps`) `[-0.4833, +0.2550]` | `t=-0.61`, `holm_p=1.0000`, `vs_ung_t=+0.38` | `RESULT_LONG.md:18`: `n 76-116 per cell, 68-89 days, Holm p = 1.00` | `MATCH` |
| `B_retest, bearP40, asia, k=0.5` *(BLOCK gate)* | `L1532` | `111` / `86` (`111/182`) | `21.62%` / `39.64%` (`fill=60.99%`) | `+0.1888%` (`+18.88 bps`) | `+0.0488%` (`+4.88 bps`) `[-0.2294, +0.3269]` | `t=+0.34`, `holm_p=1.0000`, `vs_ung_t=+0.55` | `RESULT_LONG.md:18`: `k0.5 +0.049% (n 111), Holm p = 1.00, gate t <= 0.9` | `MATCH` |
| `B_retest, bearP40, london, k=0.5` *(BLOCK gate)* | `L1559` | `77` / `69` (`77/127`) | `23.38%` / `35.06%` (`fill=60.63%`) | `+0.0614%` (`+6.14 bps`) | `-0.0786%` (`-7.86 bps`) `[-0.6119, +0.4547]` | `t=-0.29`, `holm_p=1.0000`, `vs_ung_t=+0.52` | `RESULT_LONG.md:18`: `n 76-116 per cell, 68-89 days, Holm p = 1.00` | `MATCH` |
| `B_retest, bearP40, ny, k=0.5` *(BLOCK gate)* | `L1586` | `112` / `85` (`112/186`) | `20.54%` / `41.96%` (`fill=60.22%`) | `+0.0650%` (`+6.50 bps`) | `-0.0750%` (`-7.50 bps`) `[-0.4814, +0.3314]` | `t=-0.36`, `holm_p=1.0000`, `vs_ung_t=+0.50` | `RESULT_LONG.md:18`: `n 76-116 per cell, 68-89 days, Holm p = 1.00` | `MATCH` |
| `B_retest, bearP40, asia, k=1.0` *(BLOCK gate)* | `L1667` | `113` / `86` (`113/182`) | `19.47%` / `37.17%` (`fill=62.09%`) | `+0.1229%` (`+12.29 bps`) | `-0.0171%` (`-1.71 bps`) `[-0.2903, +0.2561]` | `t=-0.12`, `holm_p=1.0000`, `vs_ung_t=+0.18` | `RESULT_LONG.md:18`: `n 76-116 per cell, 68-89 days, Holm p = 1.00` | `MATCH` |
| `B_retest, bearP40, london, k=1.0` *(BLOCK gate)* | `L1694` | `80` / `71` (`80/127`) | `21.25%` / `33.75%` (`fill=62.99%`) | `-0.0266%` (`-2.66 bps`) | `-0.1666%` (`-16.66 bps`) `[-0.6620, +0.3288]` | `t=-0.66`, `holm_p=1.0000`, `vs_ung_t=+0.22` | `RESULT_LONG.md:18`: `n 76-116 per cell, 68-89 days, Holm p = 1.00` | `MATCH` |
| `B_retest, bearP40, ny, k=1.0` *(BLOCK gate)* | `L1721` | `116` / `89` (`116/186`) | `19.83%` / `43.10%` (`fill=62.37%`) | `+0.0736%` (`+7.36 bps`) | `-0.0664%` (`-6.64 bps`) `[-0.4602, +0.3275]` | `t=-0.33`, `holm_p=1.0000`, `vs_ung_t=+0.52` | `RESULT_LONG.md:18`: `n 76-116 per cell, 68-89 days, Holm p = 1.00` | `MATCH` |

### 3.3 Per-Cell Comparison Table: Regime Splits, Stratum Splits & Pooled Rows (`bb_long_window_2026-11-04`)

| Cell (`study, tf, gate, sess, entry/k, side, width/tag`) | CSV Line (`dev_cells_long.csv`) | CSV `n` / `days` (`fills/sig`) | CSV Win Rates: `hit_target` / `net_pos_share` | CSV `gross %` (`bps`) | CSV `net %` (`bps`) & `[95% CI %]` | `RESULT_LONG.md` Line & Reported Values | Status |
|---|---|---|---|---|---|---|---|
| `A_r2r, 15m, range, ALL, signal, both, any` *(Regime split: range)* | `L2` | `9008` / `1560` | `21.26%` / `38.60%` | `+0.0118%` (`+1.18 bps`) | `-0.1282%` (`-12.82 bps`) `[-0.1545, -0.1018]`, `vs_ung=-0.0103% (t=-1.42)` | `RESULT_LONG.md:13`: `n 9008 / 1560 days, gross +0.012%, net -0.128% [-0.155, -0.102]; gate effect -0.010% (t -1.4)` | `MATCH` |
| `A_r2r, 15m, all, ALL, signal, both, any` *(Regime split: ungated tagged)* | `L47` | `12066` / `2069` (`sig=12070`) | `21.09%` / `38.89%` | `+0.0222%` (`+2.22 bps`) | `-0.1178%` (`-11.78 bps`) `[-0.1412, -0.0944]` | `RESULT_LONG.md:13`: `ungated tagged control n 12066, net -0.118% [-0.141, -0.094]` | `MATCH` |
| `A_r2r, 15m, bull, ALL, signal, both, any` *(Regime split: bull)* | `L92` | `3058` / `511` (`sig=3062`) | `20.60%` / `39.73%` | `+0.0526%` (`+5.26 bps`) | `-0.0874%` (`-8.74 bps`) `[-0.1373, -0.0374]` | `RESULT_LONG.md:13`: `Bull (n 3058) net -0.087% [-0.137, -0.037]` | `MATCH` |
| `A_r2r, 15m, bear, ALL, signal, both, any` *(Regime split: primary bear)* | `L137` | `0` / `0` | `n/a` | `n/a` | `n/a` | `RESULT_LONG.md:12`: `Primary bear rows are empty (n 0) for both studies` | `MATCH` |
| `A_r2r, 15m, bearP40, ALL, signal, both, any` *(Regime split: P40 bear)* | `L182` | `2291` / `397` | `21.82%` / `38.72%` | `+0.0302%` (`+3.02 bps`) | `-0.1098%` (`-10.98 bps`) `[-0.1667, -0.0529]` | `RESULT_LONG.md:12`: `57 bear weeks: 2291 trades (A, 15m, all sessions, signal entry)` | `MATCH` |
| `A_r2r, 15m, range, ALL, retest, both, any` *(A retest pooled)* | `L227` | `9007` / `1559` (`sig=9008`) | `22.95%` / `39.70%` | `+0.0133%` (`+1.33 bps`) | `-0.1267%` (`-12.67 bps`) `[-0.1528, -0.1006]` | `RESULT_LONG.md:16`: `9007 of 9008 range signals fill (99.99%), net -0.127% vs signal -0.128%` | `MATCH` |
| `A_r2r, 15m, range, ALL, signal, long, any` *(Side split: long)* | `L17` | `4498` / `1470` | `21.12%` / `39.42%` | `+0.0348%` (`+3.48 bps`) | `-0.1052%` (`-10.52 bps`) `[-0.1446, -0.0658]` | `RESULT_LONG.md:14`: `long -0.105% [-0.145, -0.066]` | `MATCH` |
| `A_r2r, 15m, range, ALL, signal, short, any` *(Side split: short)* | `L32` | `4510` / `1470` | `21.40%` / `37.78%` | `-0.0110%` (`-1.10 bps`) | `-0.1510%` (`-15.10 bps`) `[-0.1853, -0.1168]` | `RESULT_LONG.md:14`: `short -0.151% [-0.185, -0.117]` | `MATCH` |
| `A_r2r, 15m, range, ALL, signal, both, wide` *(Width split: wide)* | `L3` | `3580` / `1269` | `14.27%` / `43.27%` | `+0.0072%` (`+0.72 bps`) | `-0.1328%` (`-13.28 bps`) `[-0.1890, -0.0766]` | `RESULT_LONG.md:14`: `Wide-band -0.133% [-0.189, -0.077] with 14% target hits` | `MATCH` |
| `A_r2r, 15m, range, ALL, signal, both, narrow` *(Width split: narrow)* | `L4` | `5428` / `1456` | `25.87%` / `35.52%` | `+0.0149%` (`+1.49 bps`) | `-0.1251%` (`-12.51 bps`) `[-0.1485, -0.1018]` | `RESULT_LONG.md:14`: `narrow -0.125% [-0.148, -0.102], 26%` | `MATCH` |
| `A_r2r, 1h, range, ALL, signal, both, any` *(TF split: 1h)* | `L452` | `2226` / `1333` | `21.88%` / `38.54%` | `+0.0371%` (`+3.71 bps`) | `-0.1029%` (`-10.29 bps`) `[-0.2108, +0.0049]` | `RESULT_LONG.md:14`: `1h range n 2226 net -0.103% [-0.211, +0.005]` | `MATCH` |
| `A_r2r, 4h, range, ALL, signal, both, any` *(TF split: 4h)* | `L902` | `548` / `496` | `22.45%` / `38.14%` | `+0.0495%` (`+4.95 bps`) | `-0.0905%` (`-9.05 bps`) `[-0.4864, +0.3053]` | `RESULT_LONG.md:14`: `4h n 548 -0.091% [-0.486, +0.305]` | `MATCH` |
| `A_r2r, 15m, range, late, signal, both, any` *(Session split: 15m late)* | `L14` | `1108` / `820` | `22.83%` / `43.05%` | `+0.0973%` (`+9.73 bps`) | `-0.0427%` (`-4.27 bps`) `[-0.1084, +0.0230]` | `RESULT_LONG.md:14`: `15m late -0.043% [-0.108, +0.023]` | `MATCH` |
| `B_retest, 15m, range, ALL, k=0.25, both, tagged` *(B pooled k=0.25)* | `L1352` | `1590` / `813` (`1590/2538=62.65%`, `reent=1756/2538=69.19%`) | `19.94%` / `40.63%` | `+0.0338%` (`+3.38 bps`) | `-0.1062%` (`-10.62 bps`) `[-0.1829, -0.0296]` | `RESULT_LONG.md:19`: `k 0.25 = 62.6% (1590 of 2538 signals); 69% close back inside (1756/2538)` | `MATCH` |
| `B_retest, 15m, range, ALL, k=0.5, both, tagged` *(B pooled k=0.5)* | `L1487` | `1660` / `823` (`1660/2538=65.41%`) | `20.78%` / `39.82%` | `+0.0282%` (`+2.82 bps`) | `-0.1118%` (`-11.18 bps`) `[-0.1865, -0.0371]` | `RESULT_LONG.md:19`: `k 0.5 = 65.4% (1660 of 2538 signals)` | `MATCH` |
| `B_retest, 15m, range, ALL, k=1.0, both, tagged` *(B pooled k=1.0)* | `L1622` | `1717` / `839` (`1717/2538=67.65%`) | `20.62%` / `39.60%` | `+0.0128%` (`+1.28 bps`) | `-0.1272%` (`-12.72 bps`) `[-0.1997, -0.0548]` | `RESULT_LONG.md:19`: `k 1.0 = 67.7% (1717 of 2538 signals)` | `MATCH` |
| `B_retest, 15m, range, ALL, k=0.5, both, untagged` *(B untagged fill check)* | `L1490` | `4767` / `1439` (`4767/6470=73.68%`) | `28.03%` / `36.75%` | `+0.0265%` (`+2.65 bps`) | `-0.1135%` (`-11.35 bps`) `[-0.1334, -0.0937]` | `RESULT_LONG.md:19`: `Untagged range signals fill 73.7% at k = 0.5` | `MATCH` |
| `B_retest, 15m, bearP40, ALL, k=0.25..1.0, both, tagged` *(B P40 pooled fills)* | `L1370, L1505, L1640` | `359, 373, 385` / `190, 193, 198` (`of 595 sig`) | `21.45%, 20.91%, 20.00%` / `42.34%, 39.68%, 39.22%` | `+0.1311%, +0.1033%, +0.0655%` | `-0.0089%, -0.0367%, -0.0745%` | `RESULT_LONG.md:12`: `359-385 level-arm fills (B, k 0.25-1.0)` | `MATCH` |

---

## Audit Summary

- Across all three 2026-11-04 Bollinger Band studies (`bb_range_to_range_2026-11-04`, `bb_range_retest_2026-11-04`, `bb_long_window_2026-11-04`), every single number in `RESULT.md` and `RESULT_LONG.md`—including regime-mix week counts and percentages, signal counts, fill counts and fill rates, trade counts (`n`), distinct day clusters (`days`), win rates (`hit_target` and `net_pos_share`), gross and net returns (`%` and `bps`), day-clustered `95%` confidence intervals (`mean +/- 1.96 * SE`), Holm-adjusted p-values, gate-effect and tag-effect `t`-statistics, power-gate `BLOCKED` day counts, and `0`-survivor counts—matches the blind recomputations from `counts*.csv`, `dev_cells*.csv`, `dev_survivors*.json`, and `regime_mix_*.txt` with zero discrepancies (`FOUND=126 DIFF=0 NOT_IN_DATA=0`).

VERDICT: MATCH

## Claude spot-check

Checked by Claude (Builder, gem-review-three-1104) with a short Python script that parses `bb_long_window_2026-11-04/dev_cells_long.csv` (branch `gemini-q/gemini-blind-read-bb-range-studies-1104`). The study publishes per-cell aggregates only (no raw trades in the repo), so "recompute" means: fee-net = gross - 0.14, then the percentage, ratio and rounding arithmetic from the CSV fields. Compared against this read and against the study's own `RESULT_LONG.md`.

| # | Number | Source row | Recomputed | Read / study report | Verdict |
|---|---|---|---|---|---|
| 1 | A range 15m signal, both sides: n, days, net, CI | `dev_cells_long.csv` A_r2r / 15m / ALL / signal / range / both / any | n 9008, 1560 days, net -0.1282 -> -0.128, CI [-0.1545, -0.1018] | -0.128, [-0.155, -0.102] | AGREE |
| 2 | A bull 15m signal: n, days, net, CI | `dev_cells_long.csv` A_r2r / 15m / ALL / signal / bull / both / any | n 3058, 511 days, net -0.0874 -> -0.087, CI [-0.1373, -0.0374] | -0.087, [-0.137, -0.037] | AGREE |
| 3 | A P40 bear 15m signal: n, days, net, CI | `dev_cells_long.csv` A_r2r / 15m / ALL / signal / bearP40 / both / any | n 2291, 397 days, net -0.1098 -> -0.110, CI [-0.1667, -0.0529] | 2291; -0.110, [-0.167, -0.053] | AGREE |
| 4 | B retest k=0.25 pooled, tagged, 15m: n, days, net, CI | `dev_cells_long.csv` B_retest / 15m / ALL / range / both / k=0.25 / tagged | n 1590, 813 days, net -0.1062 -> -0.106, CI [-0.1826, -0.0297] | Read: net -0.1062, CI [-0.1829, -0.0296]. RESULT_LONG 3-dp: [-0.183, -0.030] | DISAGREE at 4th decimal. The read's quoted CI is off by 0.0003 and 0.0001. The published 3-dp figures agree. |
| 5 | B untagged k=0.5 fill rate, 15m | `dev_cells_long.csv` same row family, untagged | 4767 / 6470 = 73.68% -> 73.7% | 73.7% | AGREE |

Result: 4 of 5 AGREE. #4 disagrees at the 4th decimal, so the card stays open. The disagreement is filed as its own raw card.

Path check: all 8 `MyTradingSys/...` paths the read cites exist on its branch. The branch changes only the read, its layer-lab report and its card json. No study file changed.
