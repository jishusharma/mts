VERDICT: UNVERIFIABLE (raw 1m kline data at `F:/MTS/data/tom_raw` is not on this machine, so headline counts and returns cannot be recounted from raw data; code and CSVs are internally consistent with no look-ahead or fee errors found).

# Blind Review: `malkan_window_wide_2026-11` & `malkan_window_dev_2026-11`

## 1. Headline Claim Table

Raw data (`F:/MTS/data/tom_raw`, `wide.py:65`, `study.py:35`) is absent on this machine (`Test-Path "F:/MTS/data/tom_raw"` -> `False`). Headline numbers are therefore **UNVERIFIABLE** from raw data, though all reported values **MATCH** the study CSVs (`gate_lines.csv`, `counts.csv`, `dev_cells.csv`).

### `malkan_window_wide_2026-11/RESULT.md`

| Claim | Claimed Value | Recounted Value (CSV / Raw) | Status | Source |
|---|---|---|---|---|
| 1h S3_10 n / days / sd / MDE+cost / gate | 2359 / 2119 / 2.795 / 0.416 / BLOCK | CSV: 2359 / 2119 / 2.795 / 0.416 / BLOCK; Raw: n/a | UNVERIFIABLE (CSV MATCH) | `RESULT.md:11`, `gate_lines.csv:5` |
| 1h B11_12 n / days / sd / MDE+cost / gate | 443 / 432 / 2.795 / 0.751 / BLOCK | CSV: 443 / 432 / 2.795 / 0.751 / BLOCK; Raw: n/a | UNVERIFIABLE (CSV MATCH) | `RESULT.md:12`, `gate_lines.csv:2` |
| 1h C13_18 n / days / sd / MDE+cost / gate | 487 / 479 / 2.795 / 0.721 / BLOCK | CSV: 487 / 479 / 2.795 / 0.721 / BLOCK; Raw: n/a | UNVERIFIABLE (CSV MATCH) | `RESULT.md:13`, `gate_lines.csv:3` |
| 1h D19_50 n / days / sd / MDE+cost / gate | 140 / 140 / 2.795 / 1.214 / BLOCK | CSV: 140 / 140 / 2.795 / 1.214 / BLOCK; Raw: n/a | UNVERIFIABLE (CSV MATCH) | `RESULT.md:14`, `gate_lines.csv:4` |
| 4h S3_10 n / days / sd / MDE+cost / gate | 599 / 591 / 5.454 / 1.160 / BLOCK | CSV: 599 / 591 / 5.454 / 1.16 / BLOCK; Raw: n/a | UNVERIFIABLE (CSV MATCH) | `RESULT.md:15`, `gate_lines.csv:9` |
| 4h B11_12 n / days / sd / MDE+cost / gate | 116 / 116 / 5.454 / 2.443 / BLOCK | CSV: 116 / 116 / 5.454 / 2.443 / BLOCK; Raw: n/a | UNVERIFIABLE (CSV MATCH) | `RESULT.md:16`, `gate_lines.csv:6` |
| 4h C13_18 n / days / sd / MDE+cost / gate | 158 / 158 / 5.454 / 2.113 / BLOCK | CSV: 158 / 158 / 5.454 / 2.113 / BLOCK; Raw: n/a | UNVERIFIABLE (CSV MATCH) | `RESULT.md:17`, `gate_lines.csv:7` |
| 4h D19_50 n / days / sd / MDE+cost / gate | 38 / 38 / 5.454 / 4.163 / BLOCK | CSV: 38 / 38 / 5.454 / 4.163 / BLOCK; Raw: n/a | UNVERIFIABLE (CSV MATCH) | `RESULT.md:18`, `gate_lines.csv:8` |
| Holm m | 238 | CSV: 238; Raw: n/a | UNVERIFIABLE (CSV MATCH) | `RESULT.md:6`, `gate_lines.csv:2-9` |

### `malkan_window_dev_2026-11/RESULT.md`

| Claim | Claimed Value | Recounted Value (CSV / Raw) | Status | Source |
|---|---|---|---|---|
| 1h bear S3_10 n / days / gross / net / CI / Holm p | 550 / 405 / -0.106 / -0.246 / -0.443..-0.049 / 0.213 | CSV: 550 / 405 / -0.1063 / -0.2463 / -0.4432..-0.0494 / 0.2134; Raw: n/a | UNVERIFIABLE (CSV MATCH) | `RESULT.md:10`, `dev_cells.csv:5` |
| 1h bear B11_12 n / days / gross / net | 1 / 1 / 1.49 / 1.35 | CSV: 1 / 1 / 1.4934 / 1.3534; Raw: n/a | UNVERIFIABLE (CSV MATCH) | `RESULT.md:11`, `dev_cells.csv:2` |
| 1h bear C13_18 n / days / gross / net / CI / Holm p | 2 / 2 / 2.22 / 2.08 / 0.48..3.68 / 0.177 | CSV: 2 / 2 / 2.2168 / 2.0768 / 0.4750..3.6785 / 0.1767; Raw: n/a | UNVERIFIABLE (CSV MATCH) | `RESULT.md:12`, `dev_cells.csv:3` |
| 1h bull S3_10 n / days / gross / net / CI / Holm p | 517 / 399 / -0.021 / -0.161 / -0.393..0.072 / 1.0 | CSV: 517 / 399 / -0.0207 / -0.1607 / -0.3931..0.0718 / 1.0; Raw: n/a | UNVERIFIABLE (CSV MATCH) | `RESULT.md:14`, `dev_cells.csv:9` |
| 4h bear S3_10 n / days / gross / net / CI / Holm p | 132 / 128 / 0.092 / -0.048 / -0.748..0.653 / 1.0 | CSV: 132 / 128 / 0.0924 / -0.0476 / -0.7482..0.6529 / 1.0; Raw: n/a | UNVERIFIABLE (CSV MATCH) | `RESULT.md:16`, `dev_cells.csv:13` |
| 4h bull S3_10 n / days / gross / net / CI / Holm p | 129 / 125 / 0.181 / 0.041 / -0.818..0.900 / 1.0 | CSV: 129 / 125 / 0.1810 / 0.0410 / -0.8182..0.9001 / 1.0; Raw: n/a | UNVERIFIABLE (CSV MATCH) | `RESULT.md:18`, `dev_cells.csv:17` |
| 4h bull B11_12 n / days / gross / net | 1 / 1 / 4.30 / 4.16 | CSV: 1 / 1 / 4.3009 / 4.1609; Raw: n/a | UNVERIFIABLE (CSV MATCH) | `RESULT.md:19`, `dev_cells.csv:14` |

## 2. Look-Ahead Hunt

- **Pivot & confirmation (`wide.py:74-98`)**: `_pivots` checks `L=3` bars before (`i-L..i-1`) and `L=3` bars after (`i+1..i+L`). In `divergences`, the event is stamped at `conf = b + L` (`wide.py:95, 97`), which is the confirmation bar when all `L` right-hand bars are closed. Entry is at `bars[conf]["c"]` (`study.py:106-109` via `wide.py:122`), and exit is `bars[conf + 10]["c"]` (`study.py:110`). No look-ahead.
- **DEV split boundary (`wide.py:44-58`, `study.py:59-70`)**: `load_1m` raises `ValueError` if `end_ms > DEV_END_MS` (2024-07-01 UTC) and only reads monthly files `< end_ms`.
- **Resampling (`study.py:76-90`)**: Uses full UTC-aligned buckets only (`len(cur) == k`), dropping incomplete buckets.

## 3. Fee & Slippage Hunt

- **Fee model (`study.py:30-31`)**: `COST = rk.TAKER_RT_PCT` (0.14% round-trip including slippage; `2 * fees.BINANCE_TAKER * 100 == 0.10%` taker fee alone).
- **Side (`study.py:34, 110`)**: `KINDS = {"bullish": 1.0, "bearish": -1.0}`, `gross = sgn * (bars[i + h]["c"] - px) / px * 100.0`.
- **Round-trip count (`study.py:118`)**: `net = g - COST` subtracts `0.14%` once per trade. No missing fees, wrong side, or double counting.
