# Kurisko Quad Rotation: count-only PRE_REG, 15m/1h maker entry (2026-11-03)

Status: **0 of 24 cells pass the count gate**. The count is signal/fill eligibility only. No post-entry return, P&L, hit rate, MFE/MAE, or exit outcome was read or calculated.

## 1. Data and frozen signal rule

- DEV only, bar open `< 2024-07-01 00:00 UTC`; arrays are sliced by timestamp before OHLC fields enter the count logic. Sources: `F:/MTS/data/bigtrade/cache/perp/klines_15m.npz` (87,552 eligible bars; SHA256 `94cffec777c4474eb84b5001f0fa926857baa190c2a2d7578554a473f69c5b41`) and `klines_1h.npz` (21,888 bars; SHA256 `702497f3941216cad0d61c940acff4bfe1b03111d4d9049f833c54e8fe0ed44c`). Range on each: 2022-01-01 through 2024-06-30. No later bar was examined.
- Stochastic event uses the four D lines (9,3), (14,3), (40,4), (60,10); raw %K and SMA D as `FORMULAS.md` 24.1. Event rule is the frozen causal one-event-per-episode rule in section 24.4: all four <20 then fast D rises for long; all four >80 then fast D falls for short. RSI arm uses Wilder RSI(9,14,40,60), levels 20/80, under the same event rule. Short mirror and the RSI arm are not Kurisko-sourced; reported as separate OURS / hypothesis cells.
- Signal time is the close of the event bar. Signal counts include events irrespective of whether the maker order later touched. `n` for the gate is distinct UTC days containing a filled event, separately within each cell.

## 2. Parameter provenance and maker/fill model

| Parameter | Frozen value | Label / source |
|---|---|---|
| Stochastic periods | (9,3), (14,3), (40,4), (60,10) | (9,3), (14,3), (60,10) SOURCED; lookback 40 SOURCED and d=4 OURS adopted default. `params/kurisko_default.json`; `KURISKO_SPEC.md` s3/s5; `FORMULAS.md` 24.1. |
| Plotted line | D = SMA_d(raw %K) | SOURCED concept (R8, `FORMULAS.md` 24.1); formula/smoothing OURS where source is silent. |
| Thresholds | long <20; short >80 | Levels SOURCED; short mirror OURS/NO-SOURCE. `KURISKO_SPEC.md` s3, s5 gap 6. |
| Turn / episode | fast line changes direction; one signal per strict zone episode | OURS numeric turn rule, `FORMULAS.md` 24.4. |
| RSI arm | Wilder RSI 9/14/40/60, 20/80 | OPERATOR-HYPOTHESIS, not Kurisko; `KURISKO_SPEC.md` s4; `FORMULAS.md` 24.3. |
| Context phase | up if last completed 4h close > SMA50 and SMA50 > its value 10 completed 4h bars earlier; down if both inequalities reverse; mixed otherwise | OURS. 4h buckets start at 00/04/08/12/16/20 UTC and require four consecutive complete 1h bars. Signal uses only the latest completed 4h bucket. Warm-up/undefined context excluded. |
| Maker order | Limit one bp better than signal close: long at close×(1−0.0001), short at close×(1+0.0001); pending for the next same-TF candle only | OURS. Fill proxy = next candle low touches/breaches long limit or high touches/breaches short limit. A timestamp gap means no fill. OHLC touch does not model queue position or prove an actual passive fill. |
| Cost proxy | 11 bp per filled trade | OURS conservative fixed screen: Binance maker entry 2 bp + taker exit 5 bp (`backtest/fees.py:36-37`) + 4 bp slippage (OURS), irrespective of the eventual exit type. Per-event cost R = 11 bp / that filled event's pattern-stop distance; cell cost is the arithmetic mean. Stop distance is limit-to-episode extreme, mirrored by side (OURS, adapted from `kurisko_2026-10-18/count_events.py`). No fee was applied to a realized P&L. |
| Gate SD | 1.4 R | OURS screening proxy, not measured on these new cells: rounded up from the 1.39 R two-point example in `research/fable_audit_2026-10-18/GATE_AUDIT.md:41`. The gate's n uses filled event-days (clustered units), so its per-event SD assumption is conservative rho=1 per the same audit `:13`. |
| Gate family / ceiling | m=24; max gross 0.30 R | OURS: 2 TF × 2 arms × 2 sides × 3 phases; gate default in `scripts/dev/prereg_gate.py:16,47`. |

## 3. Counts and gate

`signals` = detected events; `fills` = next-bar maker touches; `n` = filled event-days. Stop median is descriptive only; gate cost uses mean event-level cost R. The gate command and complete stdout/exit code are in `gate.csv`.

| TF | Arm | Side | Phase | Signals | Fills | n days | Median stop bp | Mean cost R | Gate |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| 15m | stoch | long | up | 122 | 119 | 95 | 40.63 | 0.3563 | BLOCK |
| 15m | stoch | long | down | 190 | 179 | 113 | 58.08 | 0.3775 | BLOCK |
| 15m | stoch | long | mixed | 85 | 82 | 64 | 44.16 | 0.5196 | BLOCK |
| 15m | stoch | short | up | 233 | 221 | 145 | 40.52 | 0.5513 | BLOCK |
| 15m | stoch | short | down | 151 | 142 | 103 | 36.14 | 0.5021 | BLOCK |
| 15m | stoch | short | mixed | 143 | 137 | 92 | 39.44 | 0.4970 | BLOCK |
| 15m | RSI hypothesis | long | up | 0 | 0 | 0 | — | — | INVALID_N_ZERO (gate exit 2) |
| 15m | RSI hypothesis | long | down | 2 | 1 | 1 | 634.84 | 0.0173 | BLOCK |
| 15m | RSI hypothesis | long | mixed | 0 | 0 | 0 | — | — | INVALID_N_ZERO (gate exit 2) |
| 15m | RSI hypothesis | short | up | 0 | 0 | 0 | — | — | INVALID_N_ZERO (gate exit 2) |
| 15m | RSI hypothesis | short | down | 1 | 1 | 1 | 73.65 | 0.1494 | BLOCK |
| 15m | RSI hypothesis | short | mixed | 1 | 1 | 1 | 43.23 | 0.2545 | BLOCK |
| 1h | stoch | long | up | 15 | 13 | 10 | 59.23 | 0.1834 | BLOCK |
| 1h | stoch | long | down | 71 | 68 | 55 | 107.61 | 0.1148 | BLOCK |
| 1h | stoch | long | mixed | 38 | 37 | 32 | 75.13 | 0.1843 | BLOCK |
| 1h | stoch | short | up | 83 | 81 | 69 | 89.66 | 0.1765 | BLOCK |
| 1h | stoch | short | down | 8 | 8 | 7 | 74.73 | 0.2256 | BLOCK |
| 1h | stoch | short | mixed | 50 | 50 | 39 | 82.48 | 0.2190 | BLOCK |
| 1h | RSI hypothesis | long | up | 0 | 0 | 0 | — | — | INVALID_N_ZERO (gate exit 2) |
| 1h | RSI hypothesis | long | down | 1 | 1 | 1 | 823.68 | 0.0134 | BLOCK |
| 1h | RSI hypothesis | long | mixed | 0 | 0 | 0 | — | — | INVALID_N_ZERO (gate exit 2) |
| 1h | RSI hypothesis | short | up | 0 | 0 | 0 | — | — | INVALID_N_ZERO (gate exit 2) |
| 1h | RSI hypothesis | short | down | 0 | 0 | 0 | — | — | INVALID_N_ZERO (gate exit 2) |
| 1h | RSI hypothesis | short | mixed | 0 | 0 | 0 | — | — | INVALID_N_ZERO (gate exit 2) |

Gate summary: 16 cells returned `BLOCK` (exit 1); 8 zero-fill cells returned invalid n (exit 2; exact message in `gate.csv`). No cell passes. The six stochastic long cells are the sourced long-rule arm; their gate blocks under this maker-cost proxy and conservative SD. The short mirror and RSI hypothesis results remain separate and are not Kurisko claims.

## 4. Reproduction and safety

- Count: `python MyTradingSys/research/layer_lab/kurisko_quad_1103/count_prereg.py.txt`
- Per-cell gates: `python MyTradingSys/research/layer_lab/kurisko_quad_1103/run_gates.py.txt` (runs `scripts/dev/prereg_gate.py` 24 times, `--sd 1.4 --m 24`).
- Outputs: `counts.csv`, `gate.csv`. Only signal bars and the following candle's high/low for fill-touch classification are read by the calculation. No future return or P&L field is generated.
