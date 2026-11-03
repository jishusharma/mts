# COUNT-ONLY: Kurisko 15m/1h maker-entry preregistration

**1,194 signals; 1,141 next-bar maker-touch fills across 24 cells. Gate: 16 BLOCK, 8 INVALID_N_ZERO; zero cells pass.** No forward return, P&L, hit rate, MFE/MAE, or exit outcome was read or calculated.

## What was run

- Read `MyTradingSys/research/kurisko_2026-10-18/BLOCKED.md`, `PRE_REG.md`, `count_events.py`; `MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md`; `MyTradingSys/backtest/layers/FORMULAS.md` 24.1–24.4; `MyTradingSys/backtest/layers/kurisko/quad_rotation.py`, `params/kurisko_default.json`; RSI layer section `MyTradingSys/system/LAYERS.md:83-101`; gate help and `scripts/dev/prereg_gate.py`.
- Eligible DEV inputs only: `klines_15m.npz` 87,552 bars and `klines_1h.npz` 21,888 bars, opens from 2022-01-01 through 2024-06-30. SHA256s and exact freeze are in `MyTradingSys/research/layer_lab/kurisko_quad_1103/PRE_REG.md:5-7`.
- Frozen phase: up/down/mixed from the latest completed 4h bar (50-bar SMA and its value 10 completed 4h bars earlier). Four-hour bars use only complete UTC 00/04/08/12/16/20 buckets of four consecutive 1h bars. The definition, warm-up and all OURS/SOURCED labels are in `PRE_REG.md:16-29`.
- Maker proxy: limit 1 bp better than signal close, active for the next same-TF bar; touch by that bar's low/high counts as a fill. Counts include both signals and touches; no fill means no stop-width cost. The OHLC touch proxy cannot model queue priority. Frozen cost proxy is 11 bp per filled event (2 bp maker + 5 bp taker + 4 bp slippage OURS); mean event cost in R is fed to the gate. Gate n is filled event-days.
- Reproduction commands: `python MyTradingSys/research/layer_lab/kurisko_quad_1103/count_prereg.py.txt`; `python MyTradingSys/research/layer_lab/kurisko_quad_1103/run_gates.py.txt`. The gate runner executed `prereg_gate.py` once per cell with m=24, sd=1.4 R (OURS screening proxy; prior two-point proxy is `GATE_AUDIT.md:39`) and the exact mean event-level cost. Full stdout, command and return code are in `gate.csv`.

## Cell results

| TF | Arm | Side | Phase | Signals | Fills | n days | Mean cost R | Gate |
|---|---|---|---|---:|---:|---:|---:|---|
| 15m | stoch | long | up | 122 | 119 | 95 | 0.3563 | BLOCK |
| 15m | stoch | long | down | 190 | 179 | 113 | 0.3775 | BLOCK |
| 15m | stoch | long | mixed | 85 | 82 | 64 | 0.5196 | BLOCK |
| 15m | stoch | short | up | 233 | 221 | 145 | 0.5513 | BLOCK |
| 15m | stoch | short | down | 151 | 142 | 103 | 0.5021 | BLOCK |
| 15m | stoch | short | mixed | 143 | 137 | 92 | 0.4970 | BLOCK |
| 15m | RSI hypothesis | long | up | 0 | 0 | 0 | — | INVALID_N_ZERO |
| 15m | RSI hypothesis | long | down | 2 | 1 | 1 | 0.0173 | BLOCK |
| 15m | RSI hypothesis | long | mixed | 0 | 0 | 0 | — | INVALID_N_ZERO |
| 15m | RSI hypothesis | short | up | 0 | 0 | 0 | — | INVALID_N_ZERO |
| 15m | RSI hypothesis | short | down | 1 | 1 | 1 | 0.1494 | BLOCK |
| 15m | RSI hypothesis | short | mixed | 1 | 1 | 1 | 0.2545 | BLOCK |
| 1h | stoch | long | up | 15 | 13 | 10 | 0.1834 | BLOCK |
| 1h | stoch | long | down | 71 | 68 | 55 | 0.1148 | BLOCK |
| 1h | stoch | long | mixed | 38 | 37 | 32 | 0.1843 | BLOCK |
| 1h | stoch | short | up | 83 | 81 | 69 | 0.1765 | BLOCK |
| 1h | stoch | short | down | 8 | 8 | 7 | 0.2256 | BLOCK |
| 1h | stoch | short | mixed | 50 | 50 | 39 | 0.2190 | BLOCK |
| 1h | RSI hypothesis | long | up | 0 | 0 | 0 | — | INVALID_N_ZERO |
| 1h | RSI hypothesis | long | down | 1 | 1 | 1 | 0.0134 | BLOCK |
| 1h | RSI hypothesis | long | mixed | 0 | 0 | 0 | — | INVALID_N_ZERO |
| 1h | RSI hypothesis | short | up | 0 | 0 | 0 | — | INVALID_N_ZERO |
| 1h | RSI hypothesis | short | down | 0 | 0 | 0 | — | INVALID_N_ZERO |
| 1h | RSI hypothesis | short | mixed | 0 | 0 | 0 | — | INVALID_N_ZERO |

`INVALID_N_ZERO` is the gate's exit 2 for n=0, not a statistical BLOCK. Every positive-n cell exits 1 (BLOCK); no gate PASS and no cell is frozen. The stochastic long arm is sourced as a signal concept; the short mirror is OURS/NO-SOURCE, and the RSI arm remains an operator hypothesis.

## Findings

| Severity | Evidence | Finding | Status |
|---|---|---|---|
| MED | `kurisko_2026-10-18/BLOCKED.md:3` says 15m/1h and maker entry were untested; current `gate.csv` records all 24 new cells | New count scope has no gate PASS; this does not extend the previous BLOCK beyond these TFs, phases and fill assumptions. | MATCH |
| MED | `gate.csv` outputs: 15m stochastic mean cost 0.356–0.551 R; 1h stochastic MDE+cost 0.761–2.299 R; RSI positive-n MDE+cost >5.4 R | Gate fails on fee burden and/or low event-day count with the frozen proxy. | MATCH |
| LOW | `gate.csv` zero-n cells each have exit 2 and `bad input: need n>0...` | These are correctly recorded as `INVALID_N_ZERO`, not mislabeled as a statistical BLOCK. | MATCH |

Artifacts: `PRE_REG.md`, `counts.csv`, `gate.csv`, and the reproducible count/gate scripts under `MyTradingSys/research/layer_lab/kurisko_quad_1103/`.
