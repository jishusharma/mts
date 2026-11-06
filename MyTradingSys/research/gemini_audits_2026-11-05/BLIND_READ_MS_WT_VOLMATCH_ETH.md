# Blind Read Audit: `wt_extreme_cross_volmatch_2026-11` (`RESULT.md` vs CSVs)

- **Card**: `gemini-blind-read-ms-wt-volmatch-eth`
- **Audited Study**: `MyTradingSys/research/wt_extreme_cross_volmatch_2026-11/RESULT.md`
- **Raw Inputs**: `dev_cells.csv` (162 rows), `summary.json`
- **Date**: 2026-11-06 UTC

## 1. Regime Mix & Global Cell Counts Verification

- **Regime mix (`summary.json` vs `RESULT.md:3`)**:
  - `BTCUSDT 130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)` [OURS]
  - `ETHUSDT 130 weeks: bull 11 (8%) | bear 0 (0%) | range 119 (92%) | n/a 0 (0%)` [OURS]
  - Matches `RESULT.md:3` exactly -> **MATCH**
- **162 cells fee-net check (`dev_cells.csv` vs `RESULT.md:7-8, 72`)**:
  - Cells with `net10 > 0`: 1 of 162 (`ETHUSDT 15m sell prior_trend HTF with`, `n=242, days=89, net10=+0.026%, t=0.335, net14=-0.014%`).
  - Remaining 161 of 162 cells at 0.10% RT range from `-0.203%` to `-0.025%`.
  - Cells with `net14 > 0`: 0 of 162.
  - Matches `RESULT.md:7-8, 72` with zero discrepancy -> **MATCH**

## 2. Focal Cells Verification (`dev_cells.csv` & `summary.json` vs `RESULT.md:33-38`)

| TF | Split | CSV `n` (`RESULT.md`) | CSV `days` (`RESULT.md`) | CSV `unm_excess` ($t$) (`RESULT.md`) | CSV `match_excess` ($t$) (`RESULT.md`) | `summary.json` $p$ (`RESULT.md`) | Holm (`RESULT.md`) | Diff | Status |
|---|---|---|---|---|---|---|---|---|---|
| `1m` | `HTF against` (`daytag=all`) | 15208 (15208) | 875 (875) | +0.045 (8.6) (+0.045 (8.6)) | -0.010 (-3.2) (-0.010 (-3.2)) | 0.999 (0.999) | no (no) | 0 | MATCH |
| `1m` | `prior_trend` (`htf=all`) | 8203 (8203) | 458 (458) | +0.044 (6.1) (+0.044 (6.1)) | -0.010 (-2.4) (-0.010 (-2.4)) | 0.992 (0.992) | no (no) | 0 | MATCH |
| `15m` | `HTF against` (`daytag=all`) | 964 (964) | 506 (506) | +0.251 (5.6) (+0.251 (5.6)) | +0.013 (0.3) (+0.013 (0.3)) | 0.371 (0.371) | no (no) | 0 | MATCH |
| `15m` | `prior_trend` (`htf=all`) | 512 (512) | 269 (269) | +0.223 (4.1) (+0.223 (4.1)) | -0.046 (-1.0) (-0.046 (-1.0)) | 0.840 (0.840) | no (no) | 0 | MATCH |

## 3. Per-Symbol & Pooled Table Verification (`dev_cells.csv` vs `RESULT.md:42-61`)

| Symbol | TF | Side | Split | CSV `n` / `days` | CSV `unm_excess` ($t$) | CSV `match_excess` ($t$) | CSV `net10` / `net14` | Stated in `RESULT.md` | Status |
|---|---|---|---|---|---|---|---|---|---|
| `BTCUSDT` | `1m` | `buy` | `HTF all` | 15935 / 912 | +0.013 (3.7) | -0.011 (-6.1) | -0.101 / -0.141 | Exact match (`L44`) | MATCH |
| `BTCUSDT` | `1m` | `buy` | `HTF against` | 7433 / 437 | +0.033 (5.4) | -0.012 (-3.4) | -0.112 / -0.152 | Exact match (`L45`) | MATCH |
| `BTCUSDT` | `1m` | `buy` | `prior_trend` | 3967 / 224 | +0.038 (4.8) | -0.012 (-3.0) | -0.112 / -0.152 | Exact match (`L46`) | MATCH |
| `BTCUSDT` | `15m` | `buy` | `HTF against` | 476 / 256 | +0.211 (3.7) | +0.020 (0.4) | -0.080 / -0.120 | Exact match (`L47`) | MATCH |
| `BTCUSDT` | `15m` | `buy` | `prior_trend` | 243 / 132 | +0.238 (3.3) | -0.010 (-0.2) | -0.039 / -0.079 | Exact match (`L48`) | MATCH |
| `ETHUSDT` | `1m` | `buy` | `HTF all` | 16110 / 912 | +0.016 (3.3) | -0.016 (-5.9) | -0.102 / -0.142 | Exact match (`L49`) | MATCH |
| `ETHUSDT` | `1m` | `buy` | `HTF against` | 7775 / 438 | +0.057 (6.7) | -0.008 (-1.6) | -0.105 / -0.145 | Exact match (`L50`) | MATCH |
| `ETHUSDT` | `1m` | `buy` | `prior_trend` | 4236 / 234 | +0.049 (4.2) | -0.008 (-1.2) | -0.106 / -0.146 | Exact match (`L51`) | MATCH |
| `ETHUSDT` | `15m` | `buy` | `HTF against` | 488 / 250 | +0.290 (4.1) | +0.007 (0.1) | -0.085 / -0.125 | Exact match (`L52`) | MATCH |
| `ETHUSDT` | `15m` | `buy` | `prior_trend` | 269 / 137 | +0.210 (2.6) | -0.078 (-1.1) | -0.025 / -0.065 | Exact match (`L53`) | MATCH |
| `POOL` | `1m` | `buy` | `HTF all` | 32045 / 1824 | +0.014 (4.8) | -0.014 (-8.3) | -0.102 / -0.142 | Exact match (`L54`) | MATCH |
| `POOL` | `1m` | `sell` | `HTF all` | 53138 / 1824 | -0.008 (-3.7) | -0.016 (-15.5) | -0.102 / -0.142 | Exact match (`L55`) | MATCH |
| `POOL` | `5m` | `buy` | `HTF against` | 2948 / 803 | +0.117 (6.4) | -0.023 (-1.7) | -0.104 / -0.144 | Exact match (`L56`) | MATCH |
| `POOL` | `5m` | `buy` | `prior_trend` | 1498 / 419 | +0.131 (5.2) | -0.017 (-0.9) | -0.086 / -0.126 | Exact match (`L57`) | MATCH |
| `POOL` | `5m` | `sell` | `HTF all` | 10277 / 1807 | -0.024 (-3.8) | -0.046 (-9.9) | -0.103 / -0.143 | Exact match (`L58`) | MATCH |
| `POOL` | `15m` | `buy` | `HTF all` | 1906 / 1003 | +0.063 (2.4) | -0.080 (-3.5) | -0.092 / -0.132 | Exact match (`L59`) | MATCH |
| `POOL` | `15m` | `buy` | `HTF with` | 942 / 497 | -0.130 (-6.4) | -0.175 (-9.7) | -0.101 / -0.141 | Exact match (`L60`) | MATCH |
| `POOL` | `15m` | `sell` | `HTF all` | 3336 / 1391 | -0.012 (-0.7) | -0.052 (-3.7) | -0.094 / -0.134 | Exact match (`L61`) | MATCH |

VERDICT: MATCH

