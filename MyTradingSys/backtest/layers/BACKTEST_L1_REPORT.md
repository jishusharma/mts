# Backtest L1 report - D3 RSI tolerance study + 075 CryptoCred adapter

Run id `l1_2ee35b1e79` (manifest: `Dumps/backtest/runs/l1_2ee35b1e79/manifest.json`, gitignored data
files: `d3_tolerance_study.json`, `cc_adapter_results.json` in the same dir).
Revision `da488de` (commit `da488deb447d88ae2188e017ce5d3988bb42385f`). Data: BTCUSDT 1m,
2022-01-01..2026-09-26 (2,491,200 bars, `Dumps/backtest/raw_1m_2022` + `Dumps/backtest/raw`).
Split: chronological 70% in-sample (IS) / 30% out-of-sample (OOS) per timeframe, no shuffling.
Tolerance grid: 0.5..5.0 RSI points (0.5 steps, symmetric — `rsi_events` takes one tolerance for
both sides of the band). Levels: 40 `support` (long) and 60 `rejection` (short), the D3 worked
example. Chosen tolerance = best IS mean forward return at h=5 among tolerances with >=5 IS events.
PBO via `bt/ref_pbo.ref_pbo_cscv` on IS daily-bucketed h=5 returns (no-signal days = 0 return),
S=16 blocks where the day count allowed it.

## D3 tolerance study (RSI level events, no Malkan regime gate — see caveats)

| TF | Level | Chosen tol | IS n (h5 mean/hit) | OOS n (h5 mean/hit) | OOS baseline (h5 mean/hit) | PBO |
|---|---|---|---|---|---|---|
| 15m | 40 support (long) | 1.0 | 1552 / +0.017% / 54.5% | 698 / -0.028% / 50.0% | 49820 / 0.00003% / 50.2% | 0.785 |
| 15m | 60 rejection (short) | 1.0 | 1617 / +0.016% / 53.4% | 767 / -0.002% / 49.3% | 49820 / 0.00003% / 50.2% | 0.907 |
| 1h | 40 support (long) | 0.5 | 193 / +0.108% / 54.9% | 89 / +0.043% / 56.2% | 12452 / -0.0001% / 50.7% | **0.030** |
| 1h | 60 rejection (short) | 1.5 | 564 / -0.035% / 52.3% | 219 / -0.010% / 46.6% | 12452 / -0.0001% / 50.7% | 0.681 |
| 4h | 40 support (long) | 1.0 | 93 / +0.544% / 53.8% | 32 / +0.140% / 62.5% | 3110 / 0.00005% / 51.3% | 0.886 |
| 4h | 60 rejection (short) | 0.5 | 39 / +0.095% / 48.7% | 19 / -0.605% / 21.1% | 3110 / 0.00005% / 51.3% | 0.643 |
| 1d | 40 support (long) | 4.0 | 55 / -0.821% / 47.3% | 23 / +0.891% / 56.5% | 514 / +0.011% / 49.4% | 0.390 |
| 1d | 60 rejection (short) | 1.5 | 23 / +1.084% / 60.9% | 8 / -1.526% / 37.5% | 514 / +0.011% / 49.4% | 0.477 |

(Percentages are mean forward return at horizon h=5 bars; `hit` = fraction of events with a positive
h=5 return. Full per-tolerance grid and horizons 1/3/5/10/20 are in `d3_tolerance_study.json`.)

**Headline: only one cell clears the PBO bar.** 1h / level-40 support, tolerance 0.5, PBO=0.030
(well under the conventional <0.5 "probably not overfit" line), and its OOS edge (+0.043% mean,
56.2% hit over 89 events) sits in the same direction as IS. Every other cell has PBO >= 0.39 — the
"best" tolerance on IS is statistically indistinguishable from the other nine tolerances in the grid
on OOS data, i.e. likely overfit to the IS split, not a real edge. 15m is the clearest case: huge
PBO (0.79-0.91) and the OOS mean return is near zero or negative despite a positive IS mean.

## 075 CryptoCred adapter (setups -> `signals_to_events` -> `forward_return_stats`, 1h bars)

| Setup | Signals | h5 mean return | h5 hit rate | Sim trades (bt_engine) | Sim win rate |
|---|---|---|---|---|---|
| setup1_sr_flip | 2517 | +0.021% | 46.3% | 500 (capped) | 51.2% |
| setup3_failed_msb_reversal | 290 | +0.036% | 47.6% | 290 | 33.4% |
| setup2_fib_pullback | 839 | +0.006% | 52.1% | 500 (capped) | 61.4% |

No PBO computed for CC setups (task asked for PBO on the D3 grid; CC setups aren't a parameter sweep
here, just fixed rule sets).

## Blocker found and fixed

`cc_setups.setup2_fib_pullback` (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:75-76,102-103`)
indexed `swings[broken_swing_i]`, treating `broken_swing_i` as a position in the local `swings` list.
But `cc_structure.classify_msb` sets `broken_swing_i = H_last["i"]` / `L_last["i"]`
(`cc_structure.py:106,128`), which is a **bars index** (`find_swings` stores each swing's own bar
position as `"i"`, and swings are sparse — far fewer than bars). On real data this raised
`IndexError: list index out of range` as soon as `broken_swing_i >= len(swings)`. `setup3` uses the
same field correctly (`bars[swing_i:c+1]`, a bars-index slice) and was unaffected; `setup1` never reads
the field. The existing `test_cc_setups.py` unit tests passed because their hand-built fixtures were
crafted so a swing's bars-index happened to equal its swings-list position (see the test file's own
comment at line 85: "list-index 3, matching broken_swing_i"), which masked the mismatch.

Fixed (commit `54ad393`, fast-track): `setup2_fib_pullback` now first locates the swings-list position
whose `s["i"] == broken_swing_i`, then walks backward from that position in both the bull and bear
branches. `cc_structure`'s field semantics (a bars index) were left unchanged. A regression test
(`test_u4b_bull_swing_list_index_ne_bar_index` in `test_cc_setups.py`) uses swings at bar indices
10-13 (list positions 0-3) to catch the list/bar-index mismatch; it raises `IndexError` on the
pre-fix code. The setup2 row above is from a real-data re-run with the fix applied
(`setup2_fib_pullback` over the same 1h-resampled BTCUSDT bars as setup1/setup3).

## Caveats

- **Sample size**: 4h and 1d event counts are small (8-93 per cell); their PBO and OOS figures are
  low-confidence. 15m has by far the largest sample and the cleanest (negative) result.
- **No look-ahead**: `forward_return_stats` only uses `closes[i+h]` for `i+h < len(closes)`;
  events with insufficient trailing data are excluded from `n`, not zero-filled. The IS/OOS split is
  chronological (IS strictly precedes OOS) so the tolerance choice never sees OOS bars.
- **Not Malkan-regime-gated**: this D3 study runs `rsi_events` directly (generic level
  support/rejection), not `malkan_setup_bull`/`bear` (which additionally gate on `malkan_regime` and
  candle color, per 073). The design's own MLK-GAP1 note says the full 5-star setup also needs
  Monthly+Weekly regime, which is out of scope here.
- **PBO methodology**: IS returns were bucketed by calendar day (mean h=5 return of that day's
  events, 0 for a no-signal day) to build the CSCV return matrix across the 10-tolerance grid; this
  is a reasonable but not unique way to turn sparse per-event returns into equal-length series for
  `ref_pbo_cscv`. Different bucketing could shift these numbers somewhat, though not the qualitative
  conclusion (only 1h/40-support survives).
- **CC adapter fees/costs**: `signals_to_trades` bt_engine sim used default taker/maker fees; win
  rates above are before comparing to a funding-cost or slippage-adjusted baseline.
