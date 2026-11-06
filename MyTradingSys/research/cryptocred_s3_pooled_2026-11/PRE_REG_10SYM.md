# PRE_REG_10SYM: CryptoCred 4h Setup 1 (sr_flip), ten USD-M symbols pooled, DEV (frozen 2026-11-06, before any return was computed)

Card `cc-s3-10sym-m3-1106`. The 2-symbol pooled study was BLOCKED (`BLOCKED.md`: n 409, need 586). The ten-symbol count (`count_10sym.json`, count-only, `find_limit_fill` only, no R) is pooled n = 1981 and `prereg_gate.py --n 1981 --sd 1.24 --cost 0.068 --m auto --new-cells 1` exits 0 (`gate_output_10sym.txt`: m 221, z_holm 3.688, MDE 0.126 R + cost 0.068 R = 0.194 R <= 0.30 R; n needed 586). The setup is the one frozen in `cryptocred_s3_2026-11` (`PRE_REG_ADDENDUM`, `cc_s3_run.py`); nothing is retuned.

## Context
Regime: none, because the source frozen design has no regime gate; the result reports the weekly regime mix of the DEV window (BTCUSDT spot 1d context used as the market regime for all ten symbols, OURS) and is descriptive only.
Phase: none, because the source design has no phase gate (4h structure setup, any phase).
Session: none, because the source design has no session gate; limits rest up to the card's valid_until bar in any session.
Entry: resting LIMIT at the sr_flip retest level (fills only when 1m price trades through the level by one tick, `run_cc_setups.find_limit_fill`), placed at the close of the confirm bar; no market entry.

## The single cell
4h Setup 1 `setup1_sr_flip`, ATR buffer k = 1.0, one cell, ten symbols pooled. Holm family m = 221 (220 prior DEV variants + this 1 new cell, from the gate).

## Parameters
| Parameter | Value | Label |
|---|---|---|
| Setup, stop = structural invalidation + k x Wilder ATR(14) of 4h bars, k = 1.0 | as `cc_s3_run.build_signals` (unchanged) | OURS (frozen in the 11-01 addendum) |
| Exit | fixed 1.5 R bracket, time-out 42 4h bars = 10080 1m bars | OURS |
| Cost | all_taker Deribit, `fees.FEES_ALL_TAKER` (2 x DERIBIT_TAKER = 10 bp round trip) used by the engine; 0.068 R in the gate is the historical median cost | fees SOURCED fees.py; 0.068 R OURS-UNREPRODUCED |
| Funding | none (no funding series is pulled for the 8 new symbols and no new pulls are allowed; all ten symbols computed without funding for consistency, so net = net_nofund) | OURS |
| Symbols | BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT, XRPUSDT, DOGEUSDT, ADAUSDT, AVAXUSDT, LINKUSDT, LTCUSDT USD-M 1m, F:/MTS/data/tom_raw | SOURCED Binance archive (`MANIFEST.md`) |
| Tick sizes | 0.1, 0.01, 0.01, 0.01, 0.0001, 0.00001, 0.0001, 0.001, 0.001, 0.01 (recalled exchange filters, not re-fetched; decides only the one-tick through-level rule) | OURS |
| Gaps | SOL, XRP, LTC miss 7200 1m bars (2022-02/2022-04, absent in the archive): never interpolated; limits are matched by time so a gap bar can neither fill nor exit a trade | SOURCED MANIFEST + OURS handling |
| Window | DEV signals and bars in [2022-01-01, 2024-07-01); `splits.assert_dev_only` on every symbol; VALIDATION and HOLDOUT never loaded | SOURCED splits.py |
| Statistic | pooled fee-net mean R; day-block bootstrap (FORMULAS 18.7, 2000 resamples, seed 20261009) grouped by UTC date ACROSS symbols (conservative: same-day trades are one cluster); two-sided p, Holm with m = 221 | SOURCED FORMULAS + OURS seed reuse |
| sd used in the gate | 1.24 R, two-point value from the 1.5 R bracket at breakeven 0.427 (not measured before the run); the measured pooled sd is reported in the result | OURS |

## Verdict rule (fixed now)
- PASS: pooled fee-net mean R > 0, 95 % day-block CI lower bound > 0, Holm p < 0.05 (m = 221), AND sign agreement: per-symbol fee-net mean R > 0 on at least 7 of the 10 symbols.
- UNDERPOWERED: pooled mean > 0 but CI includes 0 or Holm p >= 0.05, or pooled PASS with sign agreement below 7 of 10 (reported as inconsistent), or pooled n < 100.
- FAIL: pooled fee-net mean R <= 0.
- A PASS is only a candidate for the VALIDATION step (`require_dev_pass`); no VALIDATION or HOLDOUT bar is read here. Never a forecast. Per-symbol rows are descriptive.

## Outputs
`RESULT_10SYM.md` line 1 = `Regime mix:` (weeks bull/bear/range over DEV), then n per symbol, pooled fee-net mean R with CI, per-symbol table, verdict word. Code `cc_s3_10sym_run.py`; tests `test_10sym.py`.
