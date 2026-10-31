# F1 PRE-REG: 1h Williams pivots with 4h/daily pivot confluence vs no confluence vs random levels

Frozen 2026-10-31 BEFORE any outcome was computed (no run of run_f1.py exists at this commit). Spec: SYNTHESIS.md s4 row F1,
VALIDATION.md 3c/4a/4d/5b, R1 rank 3. Every parameter is OURS unless marked SOURCED. Nothing is tuned after the run.

## Design (frozen)
| item | value | label |
|---|---|---|
| Data | BTCUSDT 1m monthly files F:/MTS/data/tom_raw/klines, 2022-01-01..2025-06-30; files after 2025-06 never opened; bars after 2025-06-30 dropped | SOURCED (SYNTHESIS F1 row) |
| Bars | 1h, 4h, 1d UTC epoch buckets, complete buckets only (same builder as tf_break_event_study) | OURS |
| Pivot | Williams 5-bar fractal, n = 2 each side on 1h, 4h and 1d; code reused from tf_break_event_study `confirmed_pivots` (left strict, right non-strict; FORMULAS 18.2 family). Pivot at bar k is known at the CLOSE of bar k+2 (on 1h: usable 2 bars later) | SOURCED (Williams) / OURS (n = 2 on all TFs) |
| Level | pivot high price (resistance) or pivot low price (support); live from the close of its confirming bar until touched or 96 1h bars | OURS |
| Confluence | at the confirming close A of a 1h pivot, a SAME-KIND pivot on 4h (or 1d) among the last 5 pivots of that kind already confirmed (confirming close <= A), with price within 0.5 x ATR14(1h at A) of the 1h level | OURS |
| Groups | CONF_4H (4h match, no daily match), CONF_1D (daily match, with or without 4h), CONF_ANY = CONF_4H + CONF_1D, NONE (no match). Headline = CONF_ANY vs its control | OURS |
| Event | first 1m bar at/after A whose range touches the level (high >= level for a resistance, low <= level for a support). One event per level | OURS |
| Trade | fade the level: short at resistance, long at support. Entry = level (or the 1m open if it gapped through). Stop = 1.0 x ATR14(1h at A) beyond the level (R = 1 ATR); target = 1.0 x ATR back = +1R; time exit at the close of the last 1m bar before 24 h after entry. Stop checked before target inside a 1m bar (stop-first). The entry bar is included in the check | OURS |
| Fees | all-taker Binance, both legs, `fees.BINANCE_TAKER` (0.05 % per side); cost in R = 2 x taker x entry / risk. No slippage added. No cost constant defined in this study | SOURCED (fees.py) |
| Random-level control | for each real pivot in a group: same anchor A, same side, level = close(A) +/- d x ATR with d drawn with replacement from the group's own pivot distances abs(level - close(A)) / ATR; 2 draws per pivot (seed 31). Same live window, entry, stop, target, time exit | OURS |
| CI | week-block bootstrap (event touch week), 2,000 resamples, 95 % percentile, seed 31 | OURS |
| Phase split | cowen_side and sma200_side from phase_tag/tags.csv by event UTC date (tag row t is built from bars closed <= t-1); reported per group, NO verdict | OURS |
| Harness | harness.power_n(sd of net % per trade, 0.10 % effect) for the n needed; planted +0.3 % on a random 20 % of CONF_ANY events through shift_null_test must flag that cell; no injection must not flag a cell; shift null: 1,000 circular shifts, labels {NONE, CONF_4H, CONF_1D} in event-time order | SOURCED (harness.py) |

## Verdict rule (frozen)
- PASS needs ALL: CONF_ANY n >= 200 touched events; CONF_ANY mean net R > 0; CONF_ANY minus random-control block-bootstrap difference CI lower bound > 0; the shift null (family-wise over the three labels) flags a confluence cell with a positive gap.
- FAIL: n >= 200 and the difference CI upper bound < 0, or the mean net R CI upper bound < 0.
- Otherwise INCONCLUSIVE. n < 200: NOT_DECIDABLE.
- An honest negative is a valid result. No rule, gate or layer is added by this study.

## Trials (rows in research/layer_lab/TRIALS.md, written before the run)
F1-1 CONF_ANY vs random; F1-2 CONF_4H vs random; F1-3 CONF_1D vs random; F1-4 NONE vs random; F1-5 shift-null over labels; F1-6 phase split (descriptive, no verdict). One tolerance, one stop/target, one horizon: no variant was tried.
