# PRE-REGISTRATION H3: late-session new day low that holds (NY open + 180 min), long

Card: ask-p0-47-h3-ny-open-low-prereg (ledger P0-47). Frozen BEFORE any 2019-2021 data was loaded or run. Date: 2026-10-30.
Origin: post-hoc finding F6 in `research/fast_track_2026-09-27/BTC_SESSION_SWEEPS_2026-10-04.md` (cell `L_break_hold` of
T4_placebo_Op180 in `research/session_sweeps/session_open_study.py`; n=59, 72.9% up, ~70 cells looked at, so the cell is
a hypothesis, not a result). Nothing below is tuned after seeing the 2019-2021 data.

## Hypothesis
After the NY cash open + 180 min, if BTCUSDT perp has made a new low of the UTC day so far and is still below that old
low 30 min later, price is higher 6 h after that point more often than not, by more than fees.

## Rule (all parameters OURS; none sourced from a trader)
- Day set: UTC date D with `day_gates.ny_open_utc(D)` not None (Mon-Fri, DST-aware 13:30/14:30 UTC). O = that open.
  Main period: also drop `NYSE_EXTRA` dates as in the study (2022-01..2024-12-23, from memory). Test period 2019-09..2021-12:
  NO holiday exclusion (no verified calendar; frozen as such; US_CLOSED only covers 2024-12+).
  Drop a day if [00:00 UTC, O+390 min) misses > 5 one-minute bars (as the study).
- P0 = O + 180 min. Reference range = [00:00 UTC of D, P0). ref_lo = its lowest low, ref_hi = its highest high.
- Window W = [P0, P0+30 min). Event iff min low(W) < ref_lo AND max high(W) <= ref_hi (low swept, high not)
  AND close of the last bar of W (c30) < ref_lo ("holds below"). This is the study's `sweep_class == L_break_hold`.
- Trade: LONG at c30 (close of the last 1m bar in W). Exit at close of the last 1m bar ending at P0+390 min (cE). One trade
  per day, no stop, no target, no sizing, no overlap.
- Gross return r = cE / c30 - 1.

## Fee model (SOURCED: `MyTradingSys/backtest/fees.py` BINANCE_TAKER 0.0005 per side)
Primary: taker both legs, 10 bps round trip, net = r - 0.0010. Secondary (reported, not decisive): maker both legs, 4 bps RT.
Funding (6 h, at most one 8 h settlement) and slippage are not modelled; stated as a limitation.

## Metrics
Per period: n, hit rate (cE > c30) with Wilson 95% CI, mean gross and mean net return in bp, median net, bootstrap
95% CI of mean net (10 000 resamples, seed 1), hit rate and mean net per calendar year.

## Split
- Test (untouched, decides): 2019-09-01 .. 2021-12-31 (Binance USDT-M archive 1m klines).
- Main period (where F6 was found, in-sample, NOT decisive, reported for reproduction; must give n=59, 72.9%):
  2022-01-03 .. 2026-09-25.
- Run once. No parameter changes after seeing the result; a variant is a new pre-registration.

## Pass criteria (ALL on the test period, else FAIL)
1. n >= 30 events.
2. Hit rate >= 60% and one-sided exact binomial p < 0.05 against 50%.
3. Mean net return (taker, 10 bps RT) > 0 and the bootstrap 95% CI lower bound > 0.
4. At most 1 of the calendar years 2019, 2020, 2021 with hit rate < 50%.
FAIL means H3 long is rejected for BTC on this definition. PASS means only "survives one untouched sample"; it still
needs the main period to agree in sign and a separate live-path pre-registration before any use.

## Multiple testing
One hypothesis, one direction, one run. The mirror (swept high and back -> down) is NOT tested here.
