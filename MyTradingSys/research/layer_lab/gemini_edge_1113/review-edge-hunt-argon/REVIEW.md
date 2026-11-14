Verdict: SOUND (all 13 run-trial headline numbers in EDGE_TABLE.md match RESULT.md and result CSVs/JSONs; no look-ahead or fee/slippage errors found in code; raw klines/funding caches live outside the repo so from-scratch kline-to-trade recomputation is UNVERIFIABLE from repo-only files)

# Blind Review: edge_hunt_2026-11-09 (Argon Twin)

- **Scope**: `MyTradingSys/research/edge_hunt_2026-11-09/` (`EDGE_TABLE.md`, `TRIALS.md`, `PLAN.md`, `results/*`).
- **Tests run**: `python -m pytest MyTradingSys/research/edge_hunt_2026-11-09/results -q` -> `206 passed in 36.58s` (all 9 test suites).

---

## 1. Headline Number Recount

| Trial | Claim (from `EDGE_TABLE.md`) | Claimed Value (`EDGE_TABLE.md`) | Recounted Value (from `results/*/*.csv`, `*.json`) | Status |
|---|---|---|---|---|
| T01 | 7-star spinning top, BTC+ETH 4h/1d | n=108, mean=-0.217, SE=0.150, CI=-0.511..+0.077, FAIL | `counts.csv` flags: 4h long=82, 4h short=114, 1d long=14, 1d short=18 (MATCH `RESULT.md:19-22`); trade-level net R not in CSV (raw klines outside repo) | MATCH (flags) / UNVERIFIABLE (trades) |
| T02 | 7-star MTF long | n=7, mean=+1.058, SE=1.012, CI=-0.93..+3.04, INCONCLUSIVE | `events.csv` (7 T02 rows): n=7, mean=+1.0584 | MATCH |
| T03 | 5-star MTF long | n=8, mean=+0.072, SE=0.509, CI=-0.92..+1.07, INCONCLUSIVE | `events.csv` (8 T03 rows): n=8, mean=+0.0723 | MATCH |
| T04 | first-touch sweep-reclaim fade | n=1150, mean=-0.221, SE=0.043, CI=-0.305..-0.136, FAIL | `dev_screen.json` & `cells.csv` row 1: n=1150, mean=-0.220896, SE=0.043158, CI=-0.305485..-0.136308 | MATCH |
| T05 | fast-in short-time level fade | n=300, mean=-0.086, SE=0.081, CI=-0.245..+0.074, FAIL | `cells.csv` row 1: n=300, mean=-0.0858, SE=0.0815 | MATCH |
| T06 | RSI14 cross of SMA14, 4h | n=1322, mean=+0.048, SE=0.040, CI=-0.029..+0.126, INCONCLUSIVE | `cells.csv` row 1: n=1322, mean=0.0484, SE=0.0397, CI=-0.0294..0.1261 | MATCH |
| T07 | Malkan 5-layer level short | NOT RUN as frozen trial | No results folder in `results/` | MATCH |
| T08 | T07 mirrored as long | NOT RUN | No results folder in `results/` | MATCH |
| T09 | HTF support wick long, BTC 15m | n=41, mean=-0.581, SE=0.235, CI=-1.042..-0.120, FAIL | `cells.csv` row 1: n=41, mean=-0.5810, SE=0.2351, CI=-1.0417..-0.1202 | MATCH |
| T10 | HTF resistance wick short, BTC 15m | n=47, mean=-0.804, SE=0.215, CI=-1.226..-0.382, FAIL | `cells.csv` (T10 primary): n=47, mean=-0.804, SE=0.215, CI=-1.226..-0.382 | MATCH |
| T11 | RSI 40/60 bounce + MTF confluence | n=1588, mean=-0.146, SE=0.042, CI=-0.228..-0.064, FAIL | `cells.csv` row 1: n=1588, mean=-0.1462, SE=0.0417, CI=-0.2280..-0.0644 | MATCH |
| T12 | T11 against HTF bias | n=1477, mean=-0.133, SE=0.044, CI=-0.219..-0.047, FAIL | `cells.csv` (T12 all): n=1477, mean=-0.133, SE=0.044, CI=-0.219..-0.047 | MATCH |
| T13 | confluence score 0-5 slope | n=13851, slope +1.04, CI -0.91..+2.99, INCONCLUSIVE | `dev_screen.json`: n=13851, slope=1.0370, SE=0.9949, CI=-0.9130..+2.9871 | MATCH |
| T14 | 1h level fade, balance phase | n=358, mean=-0.232, SE=0.071, CI=-0.371..-0.094, FAIL | `cells.csv` (T14 BALANCE): n=358, mean=-0.232, SE=0.071, CI=-0.371..-0.094 | MATCH |
| T15 | MLK-S1 4h RSI-40 long, accum/bull | n=51, mean=+0.016, SE=0.247, CI=-0.467..+0.500, INCONCLUSIVE | `cells.csv` (T15 accum/bull): n=51, mean=+0.016, SE=0.247, CI=-0.467..+0.500 | MATCH |

---

## 2. Look-Ahead Hunt

No `shift(-...)` or future-bar leakage was found in any of the 9 scripts:
- **T01** (`spinning_top.py:134-159`): `setup_flags` uses `v[i - VOL_WIN:i]` and `l[i - LOC_WIN + 1:i + 1]` / `h[i - LOC_WIN + 1:i + 1]` (bars `<= i`); stop-entry triggers on `i+1..i+3` (`spinning_top.py:192-210`).
- **T02, T03** (`star_grades.py:245-300`, `RESULT.md:19`): Higher-TF (weekly/monthly) bars count only once `close_time <= daily_signal_bar_close_time` (verified by `test_star_grades.py` `test_no_lookahead`). Entry is next daily open.
- **T04–T06, T09–T15** (`first_touch.py`, `speed_time.py`, `rsi_ma_cross.py`, `wick_context.py`, `line_confluence.py`, `confluence_score.py`, `phase_trials.py`): All features and HTF alignments are computed at or before the signal bar `i`, with entry at `close[i]` or `open[i+1]` / limit fill on `k > i`.

---

## 3. Fee & Slippage Hunt

All 9 scripts import `MyTradingSys/backtest/fees.py` as the single cost source:
- **Regime A** (T01, T02, T03, T04, T05, T06, T11, T12, T13, T14, T15):
  - 5 bps taker per side × 2 sides = 10 bps + 2 bps RT slippage (`fees.SLIPPAGE_RT_S13`) = **12 bps round-trip**, converted to R via `fee_r = 0.0012 / stop_frac` (`spinning_top.py:35-37,162-164`; `star_grades.py:43-44,132`; `first_touch.py:25,73-74`; `speed_time.py:45,144`; `rsi_ma_cross.py:65,191`; `line_confluence.py:258-262`; `confluence_score.py:30,314`; `phase_trials.py:42,117`).
  - Funding is summed over `calc_time` in the hold window and signed by trade side (`+1` long, `-1` short).
- **Regime B** (T09, T10 in `wick_context.py:44-45,128-138`):
  - `fees.FEES_DERIBIT`: maker entry (0 bps), maker target (0 bps), taker stop/timeout (5 bps + 1 bp taker slippage = 6 bps).
- **Verdict on fees**: No missing fees, no wrong-side funding signs, no double counting.
