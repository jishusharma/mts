# Blind Read Audit: `level_approach_eth_2026-11` (`RESULT.md` vs CSVs)

- **Card**: `gemini-blind-read-ms-level-eth`
- **Audited Study**: `MyTradingSys/research/level_approach_eth_2026-11/RESULT.md`
- **Raw CSV Inputs**: `sequences.csv` (124 rows; 64 `near_miss`/`wick_back` rows), `classes.csv` (48 rows; 24 `near_miss`/`wick_back` rows)
- **Date**: 2026-11-06 UTC

## 1. Headline Counts & Regime Mix Verification

- **64 `near_miss` / `wick_back` sequence rows in `sequences.csv`**:
  - `AGREES`: 4 rows [OURS]
  - `DISAGREES`: 20 rows [OURS]
  - `UNDERPOWERED`: 40 rows [OURS]
  - Total: $4 + 20 + 40 = 64$ rows -> **MATCH** (`RESULT.md:5`)
- **Regime mix (`RESULT.md:7`)**:
  - `POOL 260 weeks: bull 36 (14%) | bear 0 (0%) | range 224 (86%) | n/a 0 (0%) (BTCUSDT 130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%); ETHUSDT 130 weeks: bull 11 (8%) | bear 0 (0%) | range 119 (92%) | n/a 0 (0%))` -> **MATCH**

## 2. Agreeing Rows Verification (`sequences.csv` vs `RESULT.md:16-21`)

| `cls` | `tf` | `rsi` | `cvd` | `bbmid` | CSV `BTC n / p / A / B` (`RESULT.md`) | CSV `ETH n / p / A / B` (`RESULT.md`) | CSV `POOL n / p / CI / base / agreement` (`RESULT.md`) | Diff | Status |
|---|---|---|---|---|---|---|---|---|---|
| `near_miss` | `1m` | `0` | `0` | `0` | `466 / 0.210 / 0.222 / 0.176` (`466 / 0.210 / 0.222 / 0.176`) | `423 / 0.281 / 0.287 / 0.275` (`423 / 0.281 / 0.287 / 0.275`) | `889 / 0.244 / 0.217-0.273 / 0.278 / AGREES` (`889 / 0.244 / 0.217-0.273 / 0.278 / AGREES`) | 0 | MATCH |
| `near_miss` | `1m` | `0` | `0` | `1` | `641 / 0.287 / 0.286 / 0.289` (`641 / 0.287 / 0.286 / 0.289`) | `753 / 0.321 / 0.343 / 0.299` (`753 / 0.321 / 0.343 / 0.299`) | `1394 / 0.306 / 0.282-0.330 / 0.278 / AGREES` (`1394 / 0.306 / 0.282-0.330 / 0.278 / AGREES`) | 0 | MATCH |
| `near_miss` | `5m` | `0` | `0` | `1` | `187 / 0.369 / 0.409 / 0.312` (`187 / 0.369 / 0.409 / 0.312`) | `214 / 0.407 / 0.382 / 0.429` (`214 / 0.407 / 0.382 / 0.429`) | `401 / 0.389 / 0.343-0.438 / 0.325 / AGREES` (`401 / 0.389 / 0.343-0.438 / 0.325 / AGREES`) | 0 | MATCH |
| `wick_back` | `5m` | `1` | `1` | `0` | `175 / 0.309 / 0.302 / 0.333` (`175 / 0.309 / 0.302 / 0.333`) | `188 / 0.282 / 0.281 / 0.286` (`188 / 0.282 / 0.281 / 0.286`) | `363 / 0.295 / 0.250-0.344 / 0.369 / AGREES` (`363 / 0.295 / 0.250-0.344 / 0.369 / AGREES`) | 0 | MATCH |

## 3. Powered Disagreeing Rows & Class Base Rates (`sequences.csv` & `classes.csv` vs `RESULT.md:24-73`)

All 20 `DISAGREES` rows in `RESULT.md:26-45` and all 24 `classes.csv` base rate rows in `RESULT.md:50-73` were cross-checked cell-for-cell against `sequences.csv` and `classes.csv`:
- `POOL near_miss 1m`: `n=8513, p=0.278 [0.269-0.288], nA=4751 (0.284), nB=3762 (0.270)` -> **MATCH** (`RESULT.md:58`)
- `POOL near_miss 5m`: `n=3082, p=0.325 [0.309-0.342], nA=1676 (0.349), nB=1406 (0.297)` -> **MATCH** (`RESULT.md:61`)
- `POOL near_miss 15m`: `n=1376, p=0.323 [0.299-0.349], nA=723 (0.354), nB=653 (0.289)` -> **MATCH** (`RESULT.md:52`)
- `POOL near_miss 1h`: `n=416, p=0.332 [0.288-0.378], nA=210 (0.390), nB=206 (0.272)` -> **MATCH** (`RESULT.md:55`)
- `POOL wick_back 1m/5m/15m/1h`: `1071 (0.376) / 1204 (0.369) / 1048 (0.364) / 798 (0.361)` -> **MATCH** (`RESULT.md:64,67,70,73`)
- Zero discrepancies across all 48 table rows in `RESULT.md`.

VERDICT: MATCH

