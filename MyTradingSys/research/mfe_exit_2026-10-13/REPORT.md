> **RERUN 2026-10-17 (DEV only, new labels):** DEV-only rerun on relabelled fires in rerun_dev_2026-10-17/ (results.json, TRIAL_REGISTRY.csv). TRAIN now ends 2024-06-30; VALIDATE and HOLDOUT rows are not loaded. The same rule is chosen on TRAIN in all 3 setups (turn_of_candle_1m E3 bb10, sr_flip_15m E3 bb20, rsi_events_5m E4 cvd8/cvd24). Time-exit TRAIN net: -9.7 -> -9.8 bp, -13.4 -> -13.4, -8.9 -> -8.8; chosen-rule TRAIN net -9.4 -> -9.4, -9.7 -> -9.4, -9.4 -> -9.1; gross entry edge t 2.0 -> 1.2, -1.3 -> -1.2, 0.6 -> 0.6; placebo p TRAIN 0.0005 -> 0.0005, 0.10 -> 0.055, 0.25 -> 0.070. Verdict unchanged (nothing survives). The VALIDATE check was not redone: the clean VALIDATION 2024-07..12 was seen through the old rule choice, so a VALIDATE pass would need a new pre-registration.

> **CONTAMINATED (DEV read VALIDATION 2024-07..12)** - TRAIN = fire-file split column (to 2025-01-01): 17,658 / 105,190 turn_of_candle_1m, 631 / 3,911 sr_flip_15m, 550 / 3,234 rsi_events_5m TRAIN fires are 2024-07..12; rule choice on TRAIN therefore saw VALIDATION data. See MyTradingSys/backtest/bigtrade/SPLIT_ALIGNMENT_2026-10-17.md. Numbers below are kept as originally run, not recomputed.

# MFE exit study: can exits be reverse-engineered from the peak-profit bar? (2026-10-13, JIS-NUC)

**Answer: no. Nothing survives.** The three most-traded setups have no entry edge before fees, so there is no profit
for any exit to capture, and every causal exit rule is statistically indistinguishable from (or worse than) a plain time exit.
HOLDOUT was not read: no variant beat the time exit on VALIDATE, so none advanced.

## Design (declared before the first result)
- Setups = the 3 with the most tradable fires in `F:\MTS\data\bigtrade\fires` (BTCUSDT perp, 2022-01 .. 2026-10):
  `turn_of_candle_1m` (167k fires), `sr_flip_15m` (6.1k), `rsi_events_5m` (5.2k). Fires thinned greedily so entries never
  overlap a 32-bar hold (55,481 / 3,218 / 3,577 trades). Split = the fire file's own TRAIN / VALIDATE / HOLDOUT column.
- Entry = open of the 1m bar at `t_fire_ms`. Max hold = 32 signal-TF bars (32 min / 8 h / 160 min), fixed. Protective
  stop 2 ATR in every arm (so arms differ only in the exit rule). Cost = 0.10% round trip + funding actually paid at 8h marks.
- 15 exit variants = 5 rules x 3 settings (fast/default/slow), all read closed-bar data only, exit at the next 1m open:
  E1 fast RSI crosses 50 against the trade while slow RSI agrees; E2 StochRSI leaves 0.8/0.2; E3 close back inside the
  Bollinger band after a close beyond it; E4 fast CVD slope against while slow agrees; E5 volume > 2x same-slot average and
  the bar closes against the trade. Baselines: time exit at 32 bars, and the 1% / 2% / 8-bar bracket from EXIT_POLICIES_REPORT.
- Rule choice on TRAIN only (best mean net, n >= 100); advance to HOLDOUT only if VALIDATE net beats the time exit with t > 1.64.
  Placebo = the rule's exit offsets permuted across the same trades (2,000 perms, no replacement, seed 20261013).
- **OI change: NOT_IN_DATA** (no open-interest series on disk); not used.
- MFE bar is hindsight: it is used only in the descriptive table, never in a rule.

## 1. Entry quality (separate from exits). Time exit, gross of fees, bp of price
| setup | split | n | gross bp | t | mean MFE | mean MAE | random-entry control (gross / MFE / MAE) |
|---|---|---|---|---|---|---|---|
| turn_of_candle_1m | TRAIN | 35,065 | +0.3 | 2.0 | 28.4 | 27.5 | +0.4 / 27.6 / 27.7 |
| turn_of_candle_1m | VALIDATE | 5,792 | +0.9 | 2.2 | 25.9 | 24.3 | |
| sr_flip_15m | TRAIN | 2,061 | -3.4 | -1.3 | 114.4 | 120.1 | -4.4 / 113.3 / 115.7 |
| sr_flip_15m | VALIDATE | 328 | +8.5 | 1.5 | 106.4 | 99.5 | |
| rsi_events_5m | TRAIN | 2,227 | +1.1 | 0.6 | 67.9 | 64.4 | +1.6 / 67.7 / 62.3 |
| rsi_events_5m | VALIDATE | 382 | -0.8 | -0.3 | 58.0 | 58.3 | |

MFE looks large (28 to 114 bp, above the 10 bp fee on 70-90% of trades) but a random entry shows the same MFE and MAE:
the peak is a property of volatility over the hold, not of the signal. Mean gross edge is within about 1 bp of zero for
turn_of_candle and rsi_events and slightly negative for sr_flip; against a 10 bp fee none of the three is tradable at any exit.

## 2. What the peak bar looks like (TRAIN, hindsight, paired within trade, bars of the same trade as baseline)
At the MFE bar the signed readings are far from the trade's other bars: RSI +7 to +19 points (t 57 to 295), BB position
+0.7 to +0.8 (t 53 to 290), StochRSI +0.3, CVD slope +0.02 to +0.25 (t 36 to 205), volume ~2.5x same-slot average (log +0.9,
t 49 to 174). All three setups agree. This is mostly true by construction (the peak bar is the bar that made the high, so
momentum and volume are at their local extreme), and the readings are already elevated 1 to 3 bars before the peak, so a
rule keyed to them either fires early (cuts the winners) or at the peak with no way to know it was the peak. Full table:
`results.json` -> `mfe_table`.

## 3. Exit capture, fee-net (mean net bp per trade; time exit is the reference)
| setup | time exit TRAIN / VALIDATE | live-like bracket T / V | best rule on TRAIN | its TRAIN / VALIDATE net | VALIDATE t vs time exit | placebo p (T / V) |
|---|---|---|---|---|---|---|
| turn_of_candle_1m | -9.7 / -9.1 | -10.0 / -9.4 | E3 bb10 | -9.4 / -9.2 | -0.4 | 0.0005 / 0.32 |
| sr_flip_15m | -13.4 / -1.5 | -10.9 / -8.9 | E3 bb20 | -9.7 / -3.7 | -0.6 | 0.10 / 0.09 |
| rsi_events_5m | -8.9 / -10.8 | -10.0 / -9.8 | E4 cvd8/cvd24 | -9.4 / -11.2 | -0.2 | 0.25 / 0.54 |

- Share of MFE captured (mean gross / mean MFE): -0.05 to 0.09 for every arm, time exit included. Zero edge, not a bad exit.
- The one TRAIN hint (sr_flip 15m, E2/E3 about +3 bp vs time exit, t 1.1 to 1.8) does not hold on VALIDATE (t vs time exit -2.3 to +0.3, best case E3 bb40 +0.9 bp, t 0.3).
  The turn_of_candle E3 bb10 TRAIN t of 2.0 is 0.4 bp and does not repeat on VALIDATE.
- 45 rule variants plus the two baselines per setup are in `TRIAL_REGISTRY.csv`; the p values there are Bonferroni-adjusted over 15 x 3 = 45.
  None is below 0.05 on VALIDATE.
- Where the net is "better" than the time exit, the gain is fewer bars held at the same zero edge (fewer bars exposed), not more captured
  profit; every arm is still about -9 to -13 bp.

## What this does and does not say
- Says: for these three fire sets, no exit built from RSI/StochRSI/BB/CVD/volume readings (3 speeds each) recovers fees,
  because the entries carry no direction information at 8 h or shorter holds (random entries are the same).
- Does not say: exits never matter. A setup with a real entry edge (none found here; see the other threads) is where this
  harness should be rerun unchanged: `python mfe_exit_study.py <out_dir>` after adding the setup to `SETUPS`.
- Not tested: OI change (no data), holds beyond 32 bars, trailing / ATR-ratchet exits (EXIT_POLICIES_REPORT covers a few
  and none cleared the fee either), HOLDOUT (left unread on purpose).

Files: `mfe_exit_study.py` (study), `test_mfe_exit_study.py` (6 tests: features causal, rule timing, stop, funding sign),
`control_random_entries.py`, `results.json`, `TRIAL_REGISTRY.csv`, `run.log`.
