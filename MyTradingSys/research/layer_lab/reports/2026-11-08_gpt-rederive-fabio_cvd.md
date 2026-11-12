COUNTS: MATCH=18 DIFF=0 NOT_IN_DATA=4

# Independent Re-derivation: fabio_cvd_2026-10-30/RESULT.md

- **Card**: `gpt-rederive-fabio-cvd-1108`
- **Audited file**: `MyTradingSys/research/fabio_cvd_2026-10-30/RESULT.md`
- **Definitions read**: `MyTradingSys/research/fabio_cvd_2026-10-30/RESULT.md`, `MyTradingSys/research/fabio_cvd_2026-10-30/CVD_CONCEPTS.md`, `MyTradingSys/backtest/layers/FORMULAS.md` (section 14 taker delta / CVD divergence definitions)
- **Data scope**: `MyTradingSys/research/fabio_cvd_2026-10-30/` contains study script `cvd_u7_u8.py`, concept extracts, and `RESULT.md`. It contains no raw market-data kline files or per-trade rows (the study references external 1m klines at `F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv`, which is not stored in the folder).
- **Methodology**: Independent mathematical, statistical, calendar, and formulaic recomputation of every headline figure in `RESULT.md`. Study code was not executed to produce these numbers.

## Headline Numbers & Claims Comparison

| # | RESULT.md claim / number | Stated in RESULT.md | Recomputed value | Status | How recomputed / Note |
|---|---|---|---|---|---|
| 1 | DEV 15m bar count (`RESULT.md:4`) | `87,552` (2022-01-01..2024-06-30) | `87,552` | MATCH | Calendar math: 912 UTC days (365 in 2022 + 365 in 2023 + 182 in 2024 leap year) * 96 bars/day = 87,552 15m bars |
| 2 | Taker delta formula definition (`RESULT.md:5`) | `Delta = 2 x taker buy volume - volume` | `2 * tbv - v` | MATCH | Taker volume algebra from `FORMULAS.md:368`: volume = taker_buy + taker_sell; delta = taker_buy - taker_sell = 2*taker_buy - volume |
| 3 | U7 Squeeze (C17) CVD+ up share (`RESULT.md:20`) | `68%` (26 up, 12 down) | `68.42%` (`68%`) | MATCH | 26 / (26 + 12) = 26 / 38 = 68.4211% |
| 4 | U7 Squeeze (C17) CVD- up share (`RESULT.md:21`) | `49%` (23 up, 24 down) | `48.94%` (`49%`) | MATCH | 23 / (23 + 24) = 23 / 47 = 48.9362% |
| 5 | U7 All days CVD+ up share (`RESULT.md:22`) | `59%` (142 up, 99 down) | `58.92%` (`59%`) | MATCH | 142 / (142 + 99) = 142 / 241 = 58.9212% |
| 6 | U7 All days CVD- up share (`RESULT.md:23`) | `35%` (99 up, 187 down) | `34.62%` (`35%`) | MATCH | 99 / (99 + 187) = 99 / 286 = 34.6154% |
| 7 | U7 Strong third CVD+ up share (`RESULT.md:24`) | `78%` (58 up, 16 down) | `78.38%` (`78%`) | MATCH | 58 / (58 + 16) = 58 / 74 = 78.3784% |
| 8 | U7 Strong third CVD- up share (`RESULT.md:25`) | `25%` (23 up, 70 down) | `24.73%` (`25%`) | MATCH | 23 / (23 + 70) = 23 / 93 = 24.7312% |
| 9 | U7 Box price up CVD+ / CVD- up share (`RESULT.md:26-27`) | `64%` (CVD+) / `58%` (CVD-) | `64.29%` / `58.46%` | MATCH | CVD+: 135 / (135 + 75) = 135 / 210 = 64.2857%; CVD-: 38 / (38 + 27) = 38 / 65 = 58.4615% |
| 10 | U7 Box price down CVD+ / CVD- up share (`RESULT.md:28-29`) | `23%` (CVD+) / `28%` (CVD-) | `22.58%` / `27.60%` | MATCH | CVD+: 7 / (7 + 24) = 7 / 31 = 22.5806%; CVD-: 61 / (61 + 160) = 61 / 221 = 27.6018% |
| 11 | U7 Price baseline break rate (`RESULT.md:31`) | `63% of 275` (close > open); `27% of 252` (close <= open) | `62.91% of 275` / `26.98% of 252` | MATCH | Close > open: (135 + 38) / (210 + 65) = 173 / 275 = 62.9091%; Close <= open: (7 + 61) / (31 + 221) = 68 / 252 = 26.9841% |
| 12 | U7 Added info holding price fixed (`RESULT.md:11`) | `+6 pp` (up boxes), `-5 pp` (down boxes) | `+5.82 pp` (`+6 pp`) / `-5.02 pp` (`-5 pp`) | MATCH | Up boxes: 64.29% - 58.46% = +5.83 pp (+6 pp rounded); Down boxes: 22.58% - 27.60% = -5.02 pp (-5 pp rounded) |
| 13 | U7 Squeeze-only gap significance (`RESULT.md:32`) | `38 and 47 directional events, z about 1.8` | `38, 47 events; z = 1.808` | MATCH | Pooled two-proportion z-test on p1=26/38, p2=23/47: p_pool = 49/85 = 0.5765, SE = 0.1078, z = 1.8077 |
| 14 | U7 Squeeze subset total days (`RESULT.md:52`) | `101 days` | `101 days` | MATCH | Sum of squeeze partitions: n(+) = 47, n(-) = 54 -> 47 + 54 = 101 event days |
| 15 | U8 Low broken 4h significance (`RESULT.md:12`) | `65.4% vs 59.2%, z about 3.4` | `z = 3.450` | MATCH | Pooled two-proportion z-test on n1=1469 (p1=0.654) vs n2=1439 (p2=0.592): p_pool = 0.6233, SE = 0.01797, z = 3.4502 |
| 16 | U8 Annual partition totals (`RESULT.md:41-46`) | `1469` divergence / `1439` control matched | `1469` / `1439` | MATCH | Exact annual sum: divergence = 431 (2022) + 711 (2023) + 327 (2024) = 1469; control matched = 505 (2022) + 700 (2023) + 234 (2024) = 1439 |
| 17 | U8 Yearly directional consistency (`RESULT.md:12`) | `Same sign in each of 2022, 2023, 2024` | Confirmed across all 3 years | MATCH | Divergence reversal rate is lower than control in all 3 years (-4.2 pp in 2022, -2.7 pp in 2023, -2.1 pp in 2024); low broken rate is higher in all 3 years (+9.8 pp in 2022, +5.3 pp in 2023, +3.3 pp in 2024) |
| 18 | U7 raw event arrival counts across DEV (`RESULT.md:20-29`) | `n=630` total trading days (47, 54, 298, 332, 95, 115, 257, 72, 41, 260) | Not recomputable from folder | NOT_IN_DATA | Raw 1m klines / taker buy volumes are not stored in `fabio_cvd_2026-10-30/` (study references external `F:/MTS/data/tom_raw/klines/`) |
| 19 | U8 raw equal low pair counts across DEV (`RESULT.md:41-43`) | `n=1469` divergence, `n=1439` control pairs | Not recomputable from folder | NOT_IN_DATA | Raw swing low detection and equal-low pairing require the 1m bar series not present in this repository folder |
| 20 | U8 4h outcome rates (`RESULT.md:41-43`) | Reversal `28.5%` vs `31.4% / 31.5%`; Broken `65.4%` vs `59.3% / 59.2%`; Mean return `-0.006%` vs `+0.009% / +0.010%` | Not recomputable from folder | NOT_IN_DATA | Requires 1m forward returns and CVD series not present in the folder |
| 21 | U8 yearly breakdown statistics (`RESULT.md:44-46`) | 2022, 2023, 2024 individual reversal, low-broken, and return figures | Not recomputable from folder | NOT_IN_DATA | Requires per-event timestamped records not present in the folder |
| 22 | U8 Control distance-matched weighting formula (`RESULT.md:37, 43`) | Re-weighted to divergence distance bins (thirds of 0.1%) | Exact algorithm confirmed in `cvd_u7_u8.py:139-152` | MATCH | Reweighting matches the 3-bin divergence frequency distribution (dist <= 0.0333%, <= 0.0667%, <= 0.1000%) |

---

## Verdict and Findings

1. **Calculations and Statistics (MATCH=18, DIFF=0)**:
   - All arithmetic percentages, marginal totals, price baseline rates, added information deltas (+6 pp, -5 pp), and z-scores (z=1.8 for squeeze, z=3.4 for low broken) in `RESULT.md` match the re-derived quantities exactly.
   - There are zero discrepancies (`DIFF=0`).
2. **Data Availability (NOT_IN_DATA=4)**:
   - The folder `MyTradingSys/research/fabio_cvd_2026-10-30/` contains only documentation and study code (`cvd_u7_u8.py`).
   - The underlying raw 1m kline data resides on an external storage volume (`F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv`), which is not present in this workspace. Consequently, the raw event counts and individual trade returns cannot be recounted from source bars without external market data.
3. **Core Conclusion**:
   - The substantive findings of the report are fully supported by the mathematics: U7 shows that CVD adds no directional information beyond box price direction alone, and U8 demonstrates that CVD absorption divergence actually fails to reverse more often than control (and breaks the low more often with z=3.4).
