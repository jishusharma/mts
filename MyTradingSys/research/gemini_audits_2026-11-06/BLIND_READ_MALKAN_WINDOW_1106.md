# Blind Read Audit: `malkan_window_dev_2026-11` (`study.py`, `counts.csv`, `PRE_REG.md`)

- **Card**: `gemini-blind-read-of-malkan-window-dev-s`
- **Audited Files**: `MyTradingSys/research/malkan_window_dev_2026-11/study.py`, `counts.csv`, `dev_cells.csv`, `PRE_REG.md`, `RESULT.md`
- **Date**: 2026-11-06 UTC

## 1. Window Rule & `PRE_REG.md` Compliance Check

- **Arms Definition (`study.py:33, 50-54` vs `PRE_REG.md:10-15`)**:
  - `ARMS = {"S3_10": (3, 10), "B11_12": (11, 12), "C13_18": (13, 18), "D19_50": (19, 50)}`
  - `arm_of(bars)` checks `lo <= bars <= hi` (inclusive of both endpoints), tiling `3..50` disjointly.
  - `divergences()` (`study.py:93-98`) calls `rsi_divergence(closes, rsi, ts, 3, 50, kind, 0.0)` and tags each event with `arm_of(e["bars"])`.
- **DEV Window & Split Guard (`study.py:43-47, 57-60` vs `PRE_REG.md:24`)**:
  - `DEV_START_MS = 2022-01-01T00:00Z`, `DEV_END_MS = 2024-07-01T00:00Z` (asserted equal to `splits.DEV_START` and `splits.DEV_END`).
  - `load_1m` raises `ValueError` if `end_ms > DEV_END_MS` and never opens monthly files at or after `2024-07`.
- **Entry, Exit, Cost, and Clustering (`study.py:28-31, 101-122` vs `PRE_REG.md:27-33`)**:
  - Entry at close of event bar `i`, exit at close `i + 10` (`H = 10`); events with `i + 10 >= len(bars)` are dropped (`study.py:107-108`).
  - Cost = `rk.TAKER_RT_PCT = 0.14%` (`net = g - COST`, `study.py:30, 118`).
  - Cluster key = `si * 1000000 + day` (symbol x UTC day of entry, `study.py:142`).
  - Holm family size `m = len(ARMS) * len(TF_MS) * len(KINDS) = 4 * 2 * 2 = 16` (`study.py:173`).

## 2. Per-Claim Recomputation Table (`counts.csv` & `dev_cells.csv` vs `PRE_REG.md` / `RESULT.md`)

| Claim / Cell (`tf`, `kind`, `arm`) | `counts.csv` / `dev_cells.csv` Value (`OURS`) | Stated in `PRE_REG.md` / `RESULT.md` | Status |
|---|---|---|---|
| `1h`, `bearish`, `S3_10` | `n=550, days=405`, `gross=-0.106%`, `net=-0.246% [-0.443, -0.049]`, `holm_p=0.213` | `550 / 405 | -0.106 | -0.246 | -0.443..-0.049 | 0.213` (`RESULT.md:10`) | MATCH |
| `1h`, `bearish`, `B11_12` | `n=1, days=1`, `gross=+1.493%`, `net=+1.353%`, `CI=n/a`, `holm_p=1.0` | `1 / 1 | 1.49 | 1.35 | n/a | 1.0` (`RESULT.md:11`) | MATCH |
| `1h`, `bearish`, `C13_18` | `n=2, days=2`, `gross=+2.217%`, `net=+2.077% [0.475, 3.679]`, `holm_p=0.177` | `2 / 2 | 2.22 | 2.08 | 0.48..3.68 | 0.177` (`RESULT.md:12`) | MATCH |
| `1h`, `bearish`, `D19_50` | `n=0, days=0` | `0 / 0` (`RESULT.md:13`) | MATCH |
| `1h`, `bullish`, `S3_10` | `n=517, days=399`, `gross=-0.021%`, `net=-0.161% [-0.393, +0.072]`, `holm_p=1.0` | `517 / 399 | -0.021 | -0.161 | -0.393..0.072 | 1.0` (`RESULT.md:14`) | MATCH |
| `1h`, `bullish`, `B11_12 / C13_18 / D19_50` | `n=0, days=0` in all 3 arms | `0 / 0` (`RESULT.md:15`) | MATCH |
| `4h`, `bearish`, `S3_10` | `n=132, days=128`, `gross=+0.092%`, `net=-0.048% [-0.748, +0.653]`, `holm_p=1.0` | `132 / 128 | 0.092 | -0.048 | -0.748..0.653 | 1.0` (`RESULT.md:16`) | MATCH |
| `4h`, `bearish`, `B11_12 / C13_18 / D19_50` | `n=0, days=0` in all 3 arms | `0 / 0` (`RESULT.md:17`) | MATCH |
| `4h`, `bullish`, `S3_10` | `n=129, days=125`, `gross=+0.181%`, `net=+0.041% [-0.818, +0.900]`, `holm_p=1.0` | `129 / 125 | 0.181 | 0.041 | -0.818..0.900 | 1.0` (`RESULT.md:18`) | MATCH |
| `4h`, `bullish`, `B11_12` | `n=1, days=1`, `gross=+4.301%`, `net=+4.161%`, `CI=n/a`, `holm_p=1.0` | `1 / 1 | 4.30 | 4.16 | n/a | 1.0` (`RESULT.md:19`) | MATCH |
| `4h`, `bullish`, `C13_18 / D19_50` | `n=0, days=0` in both arms | `0 / 0` (`RESULT.md:20`) | MATCH |
| Total events in OURS arms (`B11_12`, `C13_18`, `D19_50`) | `1 + 2 + 0 + 1 = 4` events across all 12 cells | `4 events in total on DEV` (`RESULT.md:24`, `PRE_REG.md:39`) | MATCH |
| Survivors across all 16 cells | `0` (`survivor=False` for all non-empty rows in `dev_cells.csv`) | `No cell survives the DEV rule` (`RESULT.md:23`) | MATCH |

VERDICT: MATCH

