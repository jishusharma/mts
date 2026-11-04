# PRE_REG_LONG: amendment to PRE_REG.md, long-window DEV pass (frozen 2026-11-04, before any return was computed)

Card `longdev-rsi-divergence-gated`. Amends `PRE_REG.md` of this folder (run 1 = INCONCLUSIVE, 2022-01..2024-06, power gate blocked all
timeframes at 146-186 days per cell vs 478-1783 needed). Code: `study_long.py` (reuses `study.py` cell logic unchanged), tests
`test_long_wiring.py`. Counts (no returns) are in `counts_long.csv`, `regime_mix_count_long.txt`, gate lines in `BLOCKED_LONG.md`.

## Why (power)

Run 1 could not detect a plausible effect because DEV held only 130 weeks. Public spot klines 2017-08..2026-10 are now on disk
(`MyTradingSys/research/klines_history_2017/README.md`). The only change is a longer DEV window; this is a re-measurement, not a new idea.

## Reused unchanged from PRE_REG.md

Arms W12 (3..12) and W18 (3..18) confirmatory, C3_10 / C5_14 comparison columns only; close-based strict swings, RSI14, any RSI
difference; gate = research_kit.regime_tag (monthly AND weekly RSI >= 60 bull / <= 40 bear, last closed bar as-of; daily SMA200 side);
aligned / counter / range / ungated controls; entries signal and retest (N=10); exit 10 bars after entry; cost 0.14 % round trip;
BTCUSDT; 15m/1h/4h/1d; day-clustered SE and 95 % CI; drift control; survivor rule (n >= 30, >= 20 days, net > 0, Holm p < 0.05, excess t >= 2).
No new parameters. The Malkan weekly-AND-monthly <= 40 bear definition is NOT changed.

## Data and windows (honest split definition)

- Data: Binance SPOT klines (not futures, no splice with futures), read directly at 15m/1h/4h/1d; weekly and monthly RSI from the spot 1d bars.
  Spot prices differ slightly from the futures 1m used in run 1; cells are not bit-comparable with run 1, only comparable in size and sign.
- `backtest/splits.py` defines DEV = 2022-01-01..2024-07-01, VALIDATION = 2024-07-01..2025-07-01, HOLDOUT = 2025-07-01+. This amendment
  declares **2017-08-01..2021-12-31 as NEW DEV data** (it is PRE_DEV in splits.py terms and was never read by any study of this card; run 1 used
  2020-2021 only as indicator warm-up and read no returns before 2022). splits.py itself is not edited.
- Long DEV = events with bar close in [2017-08-01, 2024-07-01) (= splits.DEV_END, exclusive). Data is loaded only to that instant. Early events
  have no regime (SMA200 and monthly RSI14 need history): they are dropped from every gate row, including the ungated control, so all rows share
  one time span (first tagged week about 2018-11). Everything at or after the original VALIDATION start stays untouched: VALIDATION is read once,
  survivors only, same rule with raw p < 0.05 and same sign; HOLDOUT is never loaded (loader end = window end).
- Spot archive has exchange-maintenance gaps (9-25 per series, largest about 33 h): "10 bars" means 10 bars present, not 10 elapsed periods; not filled.

## Bear proxy arm P40 (coordinator decision d-bear-proxy-1104; OURS, never Malkan's)

The primary bearish gate (weekly AND monthly RSI <= 40) is expected to fire never (monthly RSI14 has not been <= 40 since 2017-08; closest
40.4 in 2023-01). Exactly ONE proxy arm is added: **P40: bear regime = weekly RSI14 <= 40 alone (monthly ignored) AND daily close below SMA200;
bull and range exactly as the primary.** It applies to bearish aligned cells only (W12, W18 x 4 TF x 2 entries = 16 cells). Label: OURS.
Holm family size m = 32 (primary: W12, W18 x 4 TF x 2 sides x 2 entries) + 16 (P40) = **48**, counting empty cells. Both are reported side by side.

## Power gate (scripts/dev/prereg_gate.py, m = 48, cost 0.14, sd as run 1: 0.8 / 1.9 / 4.0 / 10 % OURS, unit %; n = distinct days of aligned W12 signal events)

| TF | primary bull days | gate | P40 bear days | gate |
|---|---|---|---|---|
| 15m | 282 (need 424) | BLOCK | 236 (need 424) | BLOCK |
| 1h | 94 (need 2393) | BLOCK | 77 | BLOCK |
| 4h | 34 (need 10604) | BLOCK | 25 | BLOCK |
| 1d | 1 (need 66275) | BLOCK | 2 | BLOCK |

Still blocked on every timeframe (15m closest: MDE + cost 0.336 vs max plausible gross 0.30). Fixed now: the long DEV table is DESCRIPTIVE; the
verdict ceiling stays INCONCLUSIVE (underpowered) unless a cell survives the DEV rule AND VALIDATION. No FAIL and no PASS from a blocked cell.

## What the result will say

RESULT_LONG.md line 1 = `Regime mix:` for the long DEV window (primary and P40 bear counts); then verdict, per-cell table vs run 1, gate effect, P40 vs primary.

## Context
Regime: the Malkan gate (daily SMA200 side plus weekly/monthly RSI 60/40, SOURCED) as primary; P40 weekly-only bear proxy (OURS) side by side.
Phase: none, because this study tests the regime gate only; phase tags (OURS) are left to a later re-run.
Session: none, because session tags (OURS) are left to a later re-run.
Entry: signal-bar entry and retest entry (N=10, OURS) both reported; same as run 1.
