Regime mix: 130 weeks DEV (2022-01..2024-06, BTCUSDT spot 1d context as the market regime for all ten symbols, OURS): bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)

# RESULT_10SYM: CryptoCred 4h Setup 1 (sr_flip, ATR 1.0, 1.5 R bracket), ten symbols pooled, DEV

Verdict: **FAIL** (PRE_REG_10SYM.md rule: pooled fee-net mean R <= 0). DEV only; no VALIDATION or HOLDOUT bar was loaded. Descriptive, never a forecast. Source `result_10sym.json`, code `cc_s3_10sym_run.py` (7 tests in `test_10sym.py` pass).

| Pooled | Value |
|---|---|
| n fills | 1981 (gate needed 586: PASS, `gate_output_10sym.txt`) |
| fee-net mean R (Deribit all_taker, no funding) | -0.0467 |
| 95 % day-block CI (UTC-date clusters across symbols) | [-0.1097, +0.0162] |
| two-sided p / Holm p (m 221) | 0.154 / 1.000 |
| gross mean R | +0.0040 |
| measured sd of R | 1.224 (gate used 1.24, two-point value) |
| symbols with fee-net mean R > 0 | 2 of 10 (need 7 for the consistency check) |

| Symbol | tick | signals | n filled | fee-net mean R | hit 1.5 R target |
|---|---|---|---|---|---|
| BTCUSDT | 0.1 | 217 | 207 | -0.133 | 37.7 % |
| ETHUSDT | 0.01 | 210 | 202 | -0.046 | 40.6 % |
| SOLUSDT | 0.01 | 205 | 193 | -0.103 | 36.8 % |
| BNBUSDT | 0.01 | 222 | 212 | +0.083 | 45.8 % |
| XRPUSDT | 0.0001 | 205 | 198 | -0.008 | 41.4 % |
| DOGEUSDT | 0.00001 | 196 | 188 | -0.061 | 39.4 % |
| ADAUSDT | 0.0001 | 189 | 178 | -0.053 | 39.3 % |
| AVAXUSDT | 0.001 | 210 | 203 | +0.021 | 42.4 % |
| LINKUSDT | 0.001 | 209 | 200 | -0.065 | 39.0 % |
| LTCUSDT | 0.01 | 207 | 200 | -0.111 | 37.5 % |

Reading: gross R is about zero (+0.004), so the 10 bp all-taker cost takes it slightly negative; the pooled CI includes 0 but the mean is below it, so by the frozen rule this is FAIL, not UNDERPOWERED (n 1981 is above the gate's 586; MDE 0.126 R). The regime window is 81 % range, 0 % bear: the result says nothing about bear markets. SOL, XRP and LTC lack 7200 1m bars each in the archive (gap bars = no-signal, not interpolated). Tick sizes are recalled exchange filters (OURS). No funding applied (OURS).

Note: the `hit_target` field first printed 0 % because the engine's exit reason is `targets` (reporting field only); the file was regenerated, n, mean and verdict identical to the first run.

Kill scope: this FAIL covers CryptoCred 4h Setup 1 sr_flip, ATR buffer 1.0, fixed 1.5 R bracket, all_taker, ten USD-M symbols, DEV 2022-01..2024-06. It says nothing about other setups, other brackets (trailing, FTA exits), maker entry, 1d, bear regimes or HOLDOUT.