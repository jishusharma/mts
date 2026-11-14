PASS

# Blind Re-derivation: `reclaim_close_stop_2026-11`

Re-derived from `MyTradingSys/research/reclaim_close_stop_2026-11/PRE_REG.md`, `MyTradingSys/research/reclaim_close_stop_2026-11/results_DEV.csv`, and `MyTradingSys/research/reclaim_close_stop_2026-11/reclaim.py` / `run_reclaim.py` via `rederive.py` before opening `RESULT.md`.

## Method & Inputs

- **PRE_REG verdict rule** (`MyTradingSys/research/reclaim_close_stop_2026-11/PRE_REG.md:21`, SOURCED): `"n < 100 -> INCONCLUSIVE; else CI upper < 0 FAIL; CI lower > 0 PASS; else INCONCLUSIVE."`
- **Fee rule** (`MyTradingSys/research/reclaim_close_stop_2026-11/PRE_REG.md:15`, SOURCED): `"BINANCE_TAKER 0.0005 per side, round trip 0.10 % (regime A). Maker is not tested. Net = gross - 0.10 %."`
- **Re-derivation script**: `python MyTradingSys/research/layer_lab/gemini_1114c/rederive-reclaim-close-stop/rederive.py`
  - Reads `results_DEV.csv`, checks `n_all = n_low + n_high`, recomputes `all` weighted means (`gross_pct`, `net_pct`, `win_pct`, `stop_share`, `mean_hold`) from the `low` and `high` rows, verifies `net_pct = gross_pct - 0.10%`, and applies the `MyTradingSys/research/reclaim_close_stop_2026-11/PRE_REG.md:21` verdict rule.
  - Note: Raw `data.binance.vision` klines cache (`mts_reclaim_klines`) is not present on this machine, so the bootstrap CI bounds (`ci_lo`, `ci_hi`) and per-side counts/means are taken directly from `results_DEV.csv`.

## Claim Comparison Table (`RESULT.md` vs Recomputed)

| Claim | Recomputed (OURS from `results_DEV.csv` + `PRE_REG.md`) | Stated (`RESULT.md`) | `file:line` | Status |
|---|---|---|---|---|
| Headline verdict | `INCONCLUSIVE` for both `4h` (`ci_lo = -0.2534% <= 0`, `ci_hi = 0.8054% >= 0`) and `1D` (`n = 13 < 100`) | `"Answer: **INCONCLUSIVE at 4h and 1D.**"` | `MyTradingSys/research/reclaim_close_stop_2026-11/RESULT.md:5` | MATCH |
| `4h all DEV` headline | `n = 114` (`62 + 52`), `gross = 0.3710%`, `net = 0.2710%`, `95% CI = [-0.2534%, 0.8054%]`, `INCONCLUSIVE` | `114`, `0.371`, `0.271`, `-0.253 .. 0.805`, `INCONCLUSIVE` | `MyTradingSys/research/reclaim_close_stop_2026-11/RESULT.md:9` (`MyTradingSys/research/reclaim_close_stop_2026-11/results_DEV.csv:2`) | MATCH |
| `1D all DEV` headline | `n = 13` (`5 + 8`), `gross = -1.0934%` (weighted from 4dp `low`/`high`: `-1.0935%`), `net = -1.1934%`, `95% CI = [-3.8836%, 1.4962%]`, `INCONCLUSIVE` | `13`, `-1.093`, `-1.193`, `-3.884 .. 1.496`, `INCONCLUSIVE (n < 100)` | `MyTradingSys/research/reclaim_close_stop_2026-11/RESULT.md:10` (`MyTradingSys/research/reclaim_close_stop_2026-11/results_DEV.csv:5`) | MATCH |
| `4h low` descriptive | `n = 62`, `net = 0.4268%`, `95% CI = [-0.2506%, 1.2180%]` | `n 62, net +0.427 % (CI -0.251 .. 1.218)` | `MyTradingSys/research/reclaim_close_stop_2026-11/RESULT.md:12` (`MyTradingSys/research/reclaim_close_stop_2026-11/results_DEV.csv:3`) | MATCH |
| `4h high` descriptive | `n = 52`, `net = 0.0852%`, `95% CI = [-0.6588%, 0.8115%]` | `n 52, net +0.085 % (CI -0.659 .. 0.811)` | `MyTradingSys/research/reclaim_close_stop_2026-11/RESULT.md:12` (`MyTradingSys/research/reclaim_close_stop_2026-11/results_DEV.csv:4`) | MATCH |
| `1D low` & `1D high` descriptive | `1D low n = 5`, `1D high n = 8`, no CI (`MyTradingSys/research/reclaim_close_stop_2026-11/run_reclaim.py:57`: `if len(x) < 10: return np.nan, np.nan`) | `1D low n 5, high n 8 (no CI, n < 10)` | `MyTradingSys/research/reclaim_close_stop_2026-11/RESULT.md:12` (`MyTradingSys/research/reclaim_close_stop_2026-11/results_DEV.csv:6-7`) | MATCH |
| `4h` secondary stats | `stop_share = 0.5000` (`50.00%`), `mean_hold = 4.0351`, `win_pct = 40.3509%` | `50 % of trades end on the level-stop, mean hold 4.0 bars, win rate 40 %` | `MyTradingSys/research/reclaim_close_stop_2026-11/RESULT.md:12` (`MyTradingSys/research/reclaim_close_stop_2026-11/results_DEV.csv:2`) | MATCH |

## Verification

- `python MyTradingSys/research/layer_lab/gemini_1114c/rederive-reclaim-close-stop/rederive.py` -> exited 0, all weighted means, fee subtractions (`gross - 0.10% = net`), and `MyTradingSys/research/reclaim_close_stop_2026-11/PRE_REG.md:21` verdicts match `results_DEV.csv` and `RESULT.md`.
- `python -m pytest MyTradingSys/research/reclaim_close_stop_2026-11/test_reclaim.py` -> `6 passed in 3.63s`.
