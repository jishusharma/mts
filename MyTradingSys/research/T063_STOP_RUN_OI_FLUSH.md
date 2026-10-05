# T063 - Opposite-extreme sweep + OI flush + CVD in step: event study

Session: MTS-2026-10-05-1600Z-CLD-ANA-cloud-haiku-batch (Cloud, static). Item: items/T063_stop_run_oi_flush_signature.md. Tag: [OPERATOR] hypothesis.

## 0. Data status (decides what can be run)

- OI: **not available.** `runtime/oi_live/` is not on the pushed ref; the public Binance `openInterestHist` host
  (`fapi.binance.com`) is blocked by the Cloud egress proxy (CONNECT 403, WebFetch `EGRESS_BLOCKED`); snapshot OI is the B136-flat 0.0.
  The full event (with the OI-drop clause) therefore **cannot be run on Cloud**.
- Price + CVD: `MyTradingSys/runtime/orderflow_live/*.csv`, 1m, UTC, 2026-09-29 00:00 to 2026-10-03 17:05 (4 full days + 1 partial; 10-04/05 not on the ref).
- So this run is the **ablation arm A0 (sweep + price/CVD together, no OI clause)**. The OI clause (arm A1) is pre-registered below and
  handed to Desktop. A0 results must not be read as a test of the operator's OI claim.

<!-- PRE_REG_BEGIN -->
## 1. PRE_REG (written and committed before any outcome was computed; see commit of this file before the results commit)

Everything below is fixed ex ante. No parameter is tuned after seeing results. All numeric parameters are research-only defaults
tagged [OPERATOR-HYPOTHESIS/UNSOURCED]: neither Tom nor Fabio gives them (T064 extract, Q3/Q4: no sourced stop-run or retrace number).

**Bars.** 5m bars from 1m rows (UTC-aligned): o first, h max, l min, c last, delta = sum of 1m delta. A 5m bar needs all 5 minutes; an event is dropped if
any bar in its forward window (up to 4h = 48 bars) is missing.

**Sweep (pivot taken).** Up-sweep at bar s: `high_s > max(high_{s-12..s-1})` (12 bars = 1h fractal lookback, N=12). Down-sweep mirror with lows.

**Flush bar t (no look-ahead; known at bar close).** For an up-sweep at s, t in [s+1, s+6] (30 min window, W=6) with
- `close_t < open_t` and `delta_t < 0` (price and CVD move together, opposite to the sweep), and
- `|close_t - open_t| >= 2.0 * median(|close-open| over t-12..t-1)` (magnitude vs adjacent bars, M=2.0).
Down-sweep mirror (close > open, delta > 0). Flush direction f = -1 for an up-sweep event, +1 for a down-sweep event.
One event per sweep (first qualifying t); cooldown 6 bars per side.
**OI clause (arm A1, NOT RUN):** additionally `dOI_t < 0` and `|dOI_t| >= 2.0 * median(|dOI| over t-12..t-1)` using 5m `openInterestHist` sumOpenInterest.

**Control C.** Flush bars satisfying the same two conditions with **no** sweep in the prior 6 bars on that side (same cooldown). This isolates the
sweep from "any big flush".

**Outcomes** measured from `close_t`, direction-adjusted by f so that **positive = flush continues, negative = reverses**:
- fwd return at 15m (3 bars), 1h (12), 4h (48): `f * (close_{t+h}/close_t - 1)` in bp; reversal rate = share < 0.
- Pullback depth (extension before the snap-back, ATR14 of the 5m bars before t): for f=-1, `(close_t - min(low_{t+1..t+12})) / ATR14`; mirror for f=+1.
- Snap-back = first bar in t+1..t+12 whose close crosses back through `open_t` against f; report share with a snap-back and median bars to it.
- Base rate: events per day, and P(flush event | sweep) = events / sweeps with a complete window.
- Also report whether the opposite pivot (the low before the sweep) was taken within 4h (the operator's "continues in its direction" claim), as a descriptive count.

**Statistics.** Counts; reversal rate with Wilson 95% CI; mean and median fwd return; difference event-minus-control with a 10,000-draw
bootstrap 95% CI (seed 7). Per-day event counts.

**Decision rule.** "Supported" only if n_events >= 30 AND the 1h reversal-rate CI excludes 50% AND the event-minus-control 1h mean difference CI excludes 0.
Otherwise "inconclusive" (n<30) or "not supported". No other conclusion is allowed from A0. A1 uses the same rule on 30 d of 5m data
(first 20 d for sanity only; the last 10 d as holdout; parameters unchanged).

**Hand-off for A1 (Desktop).** Backfill 30 d 5m `openInterestHist` for BTCUSDT (or use `runtime/oi_live` once D2 is pushed), join on 5m `t`,
run `research/t063_event_study.py --oi <csv>` (hook present, see script).
<!-- PRE_REG_END -->
