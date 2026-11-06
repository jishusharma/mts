# Blind Read Audit: `cvd_u7_u8.py` and `fabio_cvd_2026-10-30/RESULT.md`

- **Card**: `gemini-blind-read-of-cvd-u7-u8-py-fabio-`
- **Audited Files**: `MyTradingSys/research/fabio_cvd_2026-10-30/cvd_u7_u8.py`, `MyTradingSys/research/fabio_cvd_2026-10-30/RESULT.md`
- **Date**: 2026-11-06 UTC

## 1. Per-Claim Recomputation Table (`cvd_u7_u8.py` raw run vs `RESULT.md`)

| Claim / Row in `RESULT.md` | Recomputed Value / Code Reference (`OURS`) | Stated in `RESULT.md` | Status |
|---|---|---|---|
| DEV 15m bar count (`RESULT.md:4`) | `87,552` 15m bars (`2022-01-01..2024-06-30`, `cvd_u7_u8.py:38` guards `t < 1719792000`) | `87,552 15m bars` (`2022-01-01..2024-06-30`) | MATCH |
| U7 Price baseline: `box close > open` (`RESULT.md:31`) | `n=329`, `up share 63% of 275` (`cvd_u7_u8.py:124-126`) | `up share 63% of 275` | MATCH |
| U7 Price baseline: `box close <= open` (`RESULT.md:31`) | `n=301`, `up share 27% of 252` (`cvd_u7_u8.py:124-126`) | `27% of 252` | MATCH |
| U7 `squeeze (C17)` CVD `+` (`RESULT.md:20`) | `n=47`, first up `26`, first down `12`, both/none `9`, up share `68%` | `47 | 26 | 12 | 9 | 68%` | MATCH |
| U7 `squeeze (C17)` CVD `-` (`RESULT.md:21`) | `n=54`, first up `23`, first down `24`, both/none `7`, up share `49%` | `54 | 23 | 24 | 7 | 49%` | MATCH |
| U7 `all days` CVD `+` (`RESULT.md:22`) | `n=298`, first up `142`, first down `99`, both/none `57`, up share `59%` | `298 | 142 | 99 | 57 | 59%` | MATCH |
| U7 `all days` CVD `-` (`RESULT.md:23`) | `n=332`, first up `99`, first down `187`, both/none `46`, up share `35%` | `332 | 99 | 187 | 46 | 35%` | MATCH |
| U7 `all, strong third` CVD `+` (`RESULT.md:24`) | `n=95`, first up `58`, first down `16`, both/none `21`, up share `78%` | `95 | 58 | 16 | 21 | 78%` | MATCH |
| U7 `all, strong third` CVD `-` (`RESULT.md:25`) | `n=115`, first up `23`, first down `70`, both/none `22`, up share `25%` | `115 | 23 | 70 | 22 | 25%` | MATCH |
| U7 `all, box price up` CVD `+` / `-` (`RESULT.md:26-27`) | `+`: `257 | 135 | 75 | 47 | 64%`; `-`: `72 | 38 | 27 | 7 | 58%` | Exact match | MATCH |
| U7 `all, box price down` CVD `+` / `-` (`RESULT.md:28-29`) | `+`: `41 | 7 | 24 | 10 | 23%`; `-`: `260 | 61 | 160 | 39 | 28%` | Exact match | MATCH |
| U8 `divergence (CVD lower low)` (`RESULT.md:41`) | `n=1469`, reversal 4h `28.5%`, low broken 4h `65.4%`, mean 4h return `-0.006%` | `1469 | 28.5% | 65.4% | -0.006%` | MATCH |
| U8 `control raw` (`RESULT.md:42`) | `n=1439`, reversal 4h `31.4%`, low broken 4h `59.3%`, mean 4h return `+0.009%` | `1439 | 31.4% | 59.3% | +0.009%` | MATCH |
| U8 `control distance-matched` (`RESULT.md:43`) | `n=1439`, reversal 4h `31.5%`, low broken 4h `59.2%`, mean 4h return `+0.010%` | `1439 | 31.5% | 59.2% | +0.010%` | MATCH |
| U8 `2022 divergence / control matched` (`RESULT.md:44`) | `431 / 505`, rev `27.6% / 31.8%`, broke `67.3% / 57.5%`, ret `-0.030% / -0.072%` | `431 / 505 | 27.6% / 31.8% | 67.3% / 57.5% | -0.030% / -0.072%` | MATCH |
| U8 `2023 divergence / control matched` (`RESULT.md:45`) | `711 / 700`, rev `28.1% / 30.8%`, broke `65.7% / 60.4%`, ret `+0.001% / +0.052%` | `711 / 700 | 28.1% / 30.8% | 65.7% / 60.4% | +0.001% / +0.052%` | MATCH |
| U8 `2024 divergence / control matched` (`RESULT.md:46`) | `327 / 234`, rev `30.3% / 32.4%`, broke `62.1% / 58.8%`, ret `+0.009% / +0.057%` | `327 / 234 | 30.3% / 32.4% | 62.1% / 58.8% | +0.009% / +0.057%` | MATCH |

## 2. Code Logic Note (`cvd_u7_u8.py:101, 112`)

- In `u7(b)` at `cvd_u7_u8.py:101`: `box = [b.get(a15 - 900 * k) for k in range(1, 33)]`, so `box[0]` is `a15 - 900` (the last 15m bar before US open `A`) and `box[-1]` is `a15 - 32*900` (the first 15m bar of the 8h box). At line 112, `px = box[0][3] - box[-1][0]` computes `close(last bar of box) - open(first bar of box)`, which is the true 8h box price change, and `find_equal_lows` (`cvd_u7_u8.py:72-75`) starts the 4h forward window at `r = e['i'] + K` (after the K=2 confirming bars), preventing look-ahead. All numbers in `RESULT.md` match the script output 100%.

VERDICT: MATCH

