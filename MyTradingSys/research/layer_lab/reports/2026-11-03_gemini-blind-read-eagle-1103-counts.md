# Layer Lab Report: Blind Read of Eagle_Eyes 11-03 Counts (`us_open_roundtrip.py` & `ethbtc_wt_top.py`)

- **Task**: `gemini-blind-read-eagle-1103-counts` (`OURS`)
- **Lane**: `CODEX` (`OURS`)
- **Producer Commit**: `3f73289b65ef57746dfad252ae559916661a9721` (`SOURCED`: commit `3f73289b6` Result line)
- **Audited Scripts**:
  - `MyTradingSys/research/eagle_eyes_picture_2026-10-28/us_open_roundtrip.py` (`SOURCED`)
  - `MyTradingSys/research/eagle_eyes_picture_2026-10-28/ethbtc_wt_top.py` (`SOURCED`)
- **Deliverables**:
  - Primary Audit Table: `MyTradingSys/research/gemini_audits_2026-11-03/eagle_1103_blind_read.md` (`OURS`)
  - Independent Counter Script: `MyTradingSys/research/gemini_audits_2026-11-03/eagle_1103_counter.py` (`OURS`)
- **Date**: `2026-11-03` (`OURS`)
- **Auditor**: Gemini 4 Argon (Medium) worker (`OURS`)

---

## 1. Executive Summary

Independent cross-vendor blind read and counter verification of the `7` empirical values reported in the `Result:` line of commit `3f73289b6` (`SOURCED`: `"Result: us_open_roundtrip.py n=125 low-first 63% vs high-first 16%; ethbtc_wt_top.py WT top+RSI>60 n=37 10d -2.19%, Krown flip n=43 5d +0.71%; cards for liq_events mirror and ETH data top-up"`):

- **Against Producer Archive (`USDT-M Futures` `1m`, `2022-01..2025-06` for `BTCUSDT` and `2022-01..2024-06` for `ETHUSDT`)**: **`FOUND=7 DIFF=0 NOT_IN_DATA=0`** (`OURS`). Every number in the commit `Result:` line reproduces to the exact integer/decimal when run with the producer's indexing on the perp archive (`python MyTradingSys/research/gemini_audits_2026-11-03/eagle_1103_counter.py`).
- **Against Docstring-Strict Specification / Full `2022-01..2025-06` Range (or Spot Fallback Archive)**: **`FOUND=2 DIFF=5 NOT_IN_DATA=0`** (`OURS`). Specifically:
  1. Topping up `ETHUSDT` from `2024-06` (`30` months, `5,472` `4h` bars) to the docstring's stated `2025-06` (`42` months, `7,662` `4h` bars, `ethbtc_wt_top.py:3,16`, `SOURCED`) reverses the Krown RSI `> 60` regime-flip `5d` (`30`-bar) median return from **`+0.71%` (`n=43`)** to **`-0.18%` (`n=64`)** on UM Futures (**`-0.16%`, `n=64`** on Spot) and softens `WT top + RSI > 60` `10d` (`60`-bar) median return from **`-2.19%` (`n=37`)** to **`-1.50%` (`n=43`)** on UM Futures (**`-1.33%`, `n=44`** on Spot) (`OURS`).
  2. Closing the `5`-minute gap (`14:25Z..14:29Z`, `m=865..869`) between `close(14:24)` (`m=864`) and the outcome loop start `m=870` (`14:30Z`) in `us_open_roundtrip.py:21,24` (`SOURCED`) shifts UM `low-first` from **`63.20%` (`63%`)** to **`64.80%` (`65%`)** (`OURS`).
  3. Adjusting `us_open_roundtrip.py` for US Daylight Saving Time (`America/New_York` `08:30..09:24 NY` pre-open spike -> `09:30..10:30 NY` cash open, instead of fixed `13:30Z..14:24Z` which is `09:30..10:24 NY` during `EDT` summer and `08:30..09:24 NY` only during `EST` winter) changes the count from `n=125` (`low-first 63.2%`, `high-first 16.0%`) to **`n=85` (`low-first 72.9%`, `high-first 10.6%`)** on UM Futures (`OURS`).

---

## 2. Numerical Verification Table (`python MyTradingSys/research/gemini_audits_2026-11-03/eagle_1103_counter.py`)

| # | Script & Metric | Commit `3f73289b6` Value (`SOURCED`) | UM Futures Producer (`OURS`) | UM Futures Docstring / Full `2025-06` (`OURS`) | Spot (`data/spot/monthly/klines`) (`OURS`) | Months Used (`OURS`) |
|---|---|---|---|---|---|---|
| 1 | `us_open_roundtrip.py`: `n` | `125` (`us_open_roundtrip.py:35`) | `125` (`2022-01..2025-06`) | `125` (`2022-01..2025-06`) | `123` (`2022-01..2025-06`); `85` (`2022-01..2024-06`) | `2022-01..2025-06` (`42`m) |
| 2 | `us_open_roundtrip.py`: `low-first` | `63%` (`us_open_roundtrip.py:36`) | `63.20%` (`63%`, `79/125`) | `64.80%` (`65%`, `81/125` on `14:25..15:29Z`) | `61.79%` (`62%` Producer); `62.60%` (`63%` Docstring) | `2022-01..2025-06` (`42`m) |
| 3 | `us_open_roundtrip.py`: `high-first` | `16%` (`us_open_roundtrip.py:36`) | `16.00%` (`16%`, `20/125`) | `16.00%` (`16%`, `20/125` on `14:25..15:29Z`) | `16.26%` (`16%`, `20/123` Producer & Docstring) | `2022-01..2025-06` (`42`m) |
| 4 | `ethbtc_wt_top.py`: `WT top+RSI>60 n` | `37` (`ethbtc_wt_top.py:40,51`) | `37` (`2022-01..2024-06`) | `43` (`2022-01..2025-06` Close WT); `39` / `47` (`HLC3` WT) | `38` (`2022-01..2024-06`); `44` (`2022-01..2025-06`) | `2022-01..2024-06` (`30`m) & `2022-01..2025-06` (`42`m) |
| 5 | `ethbtc_wt_top.py`: `WT top+RSI>60 10d` | `-2.19%` (`ethbtc_wt_top.py:49,51`) | `-2.19%` (`2022-01..2024-06`) | `-1.50%` (`2022-01..2025-06` Close WT); `-2.19%` (`HLC3` WT) | `-1.86%` (`2022-01..2024-06`); `-1.33%` (`2022-01..2025-06`) | `2022-01..2024-06` (`30`m) & `2022-01..2025-06` (`42`m) |
| 6 | `ethbtc_wt_top.py`: `Krown flip n` | `43` (`ethbtc_wt_top.py:43,51`) | `43` (`2022-01..2024-06`) | `44` (`2022-01..2024-06` warmup); `64` / `65` (`2022-01..2025-06`) | `43` (`2022-01..2024-06`); `64` (`2022-01..2025-06`) | `2022-01..2024-06` (`30`m) & `2022-01..2025-06` (`42`m) |
| 7 | `ethbtc_wt_top.py`: `Krown flip 5d` | `+0.71%` (`ethbtc_wt_top.py:48,51`) | `+0.71%` (`2022-01..2024-06`) | `+0.60%` (`2022-01..2024-06` warmup); `-0.18%` / `-0.23%` (`2022-01..2025-06`) | `+0.73%` (`2022-01..2024-06`); `-0.16%` (`2022-01..2025-06`) | `2022-01..2024-06` (`30`m) & `2022-01..2025-06` (`42`m) |

---

## 3. Code Review Findings

1. **Lookahead (`us_open_roundtrip.py:21-31`, `ethbtc_wt_top.py:13,18-45`)**: Neither script has lookahead between setup detection and forward outcomes (`OURS`).
2. **US DST Shift (`us_open_roundtrip.py:15,20-31`)**: Fixed `13:30Z..14:24Z` (`m=810..864`) mixes `94` summer `EDT` days (`13:30Z = 09:30 NY` cash open, `low-first 64.9%`) with `31` winter `EST` days (`13:30Z = 08:30 NY` pre-open, `low-first 58.1%`) (`OURS`).
3. **Bar Off-by-One / Indexing (`us_open_roundtrip.py:24,30-31`, `ethbtc_wt_top.py:33,35-36`)**:
   - `us_open_roundtrip.py:24` starts outcome evaluation at `m=870` (`14:30Z`) instead of `m=865` (`14:25Z`), leaving a `5`-minute unmeasured gap after `c = b[864][3]` (`close(14:24)`), and iterates over `61` bars (`range(870, 931)` closing at `15:31Z`) (`OURS`).
   - `ethbtc_wt_top.py:33,36` loops up to `n - 32` while clamping `r60` via `min(n - 1, i + 60)` (`31..59`-bar truncated horizon near the end of sample) and resets `under = 0` at `i = 60` (`ethbtc_wt_top.py:35`), dropping `1` Krown event at the start of the sample (`OURS`).
4. **Close-vs-High/Low (`ethbtc_wt_top.py:13,22-23,32-33`)**: `ethbtc_wt_top.py` computes WaveTrend on `4h` closes `C` instead of `HLC3` (`FORMULAS.md`) and computes `30`-bar `mx`/`mn` over `4h` closes instead of `4h` highs/lows (`OURS`).
