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
run `research/loose_code/t063_event_study.py --oi <csv>` (hook present, see script).
<!-- PRE_REG_END -->

<!-- PRE_REG_AMEND_1_BEGIN -->
### PRE_REG AMEND 1 (Desktop, 2026-10-05, written before any A1 outcome was computed)

Facts found on Desktop that the original hand-off did not know:
- `runtime/oi_live/oi_5m_30d.csv` has 30 d of OI (2026-09-05 to 2026-10-05) but price+CVD 1m rows (`orderflow_live/*.csv`) only exist from 2026-09-29.
  The A1 join window is therefore the ~6.5 d overlap, not 30 d. The "first 20 d sanity / last 10 d holdout" split is **not possible and is dropped**; A1 is a single
  pass over the overlap with parameters unchanged (N=12, W=6, M=2.0, COOL=6). No holdout exists, so a "supported" outcome would be provisional.
- CSV columns are `ts_ms,sumOpenInterest` (not `t,oi`); the script loader is adapted to read both. `ts_ms` is joined as the 5m bar open `t`, as in section 1. No other logic changes.
- Decision rule unchanged (n_events >= 30, 1h reversal CI excludes 50%, event-minus-control 1h diff CI excludes 0). With ~6.5 d of data and an OI-drop clause, n < 30 is the likely
  outcome and would be reported as "inconclusive", not as evidence against the operator claim.
<!-- PRE_REG_AMEND_1_END -->

## 2. Results, arm A0 (sweep + price/CVD, no OI clause), run on Cloud 2026-10-05

Command: `python MyTradingSys/research/loose_code/t063_event_study.py` (script is in this commit; parameters exactly as section 1). Sign convention: positive
return = the flush **continues**, negative = it **reverses**. Raw output:

```
## A0 sweep + price/CVD (no OI)
bars=1320 days_touched=5 sweeps_with_window=369 events_raw=78 control_raw=92
events_with_full_4h=71 control_with_full_4h=82
P(flush|sweep)=0.211 (78/369); events/day=15.60
-- EVENT n=71
  15m: mean=0.0bp median=-0.6bp reversal=36/71=0.51 CI[0.39,0.62]
  1h: mean=1.5bp median=4.9bp reversal=30/71=0.42 CI[0.31,0.54]
  4h: mean=8.5bp median=11.6bp reversal=30/71=0.42 CI[0.31,0.54]
  depth_ATR median=1.49 p75=3.22
  snap_back_12bars=37/71 median_bars=4
  opposite_pivot_taken_within_4h=41/71
  per_day={20725: 18, 20726: 15, 20727: 17, 20728: 15, 20729: 6}
-- CONTROL n=82
  15m: mean=2.8bp median=0.4bp reversal=41/82=0.50 CI[0.39,0.61]
  1h: mean=2.3bp median=4.2bp reversal=32/82=0.39 CI[0.29,0.50]
  4h: mean=-3.5bp median=-0.2bp reversal=41/82=0.50 CI[0.39,0.61]
  depth_ATR median=1.60 p75=2.78
  snap_back_12bars=38/82 median_bars=4.0
  per_day={20725: 17, 20726: 18, 20727: 21, 20728: 18, 20729: 8}
diff(event-control) 15m: mean -2.8bp boot95[-9.3,3.7]
diff(event-control) 1h: mean -0.8bp boot95[-13.8,12.3]
diff(event-control) 4h: mean 11.9bp boot95[-12.5,35.9]
```

### Reading (within the pre-registered rule)

- **Base rate:** 78 of 369 sweeps (21%) were followed within 30 min by a flush bar meeting the price/CVD/magnitude conditions; about 15.6 events per day.
  The control (same flush, no prior sweep) occurs about as often (92 raw), so a flush is not rare and the sweep does not make it more likely to be followed by anything different.
- **Forward returns (sample n=71, 1h reversal rate 0.42, CI 0.31-0.54):** the 1h reversal-rate CI contains 50% and event-minus-control 1h mean difference is -0.8 bp
  with bootstrap CI [-13.8, +12.3]; 15m and 4h also straddle zero. Median returns are a few bp in the continue direction in both groups.
  **Decision rule outcome for A0: not supported (no separation from control).** This says nothing about the OI clause.
- **Pullback depth before snap-back (descriptive, events):** median extension 1.49 ATR14 (p75 3.22) beyond the flush bar close within 12 bars; a snap-back through the flush bar's
  open occurred in 37 of 71 events, median 4 bars. The control looks the same (1.60 ATR, 38/82). The only retrace numbers here are measured, not sourced (T064: NO-SOURCE).
- **"Continues in its direction":** the opposite pivot (the low before an up-sweep, or high before a down-sweep) was taken within 4h in 41 of 71 events (58%). No control for this was
  computed, so it is descriptive only.

### Caveats that matter

1. **Sample is 4.6 days of one regime** (09-29 to 10-03 17:05), with a trending drift: 379 pivot sweeps in 1,308 bars, about twice what independent bars would give (~7.7% per side).
2. **Overlapping windows:** events fire ~15 per day and 4h outcomes overlap; the Wilson/bootstrap CIs treat events as independent and are therefore too narrow. Treat every CI as optimistic.
3. **OI clause untested** (section 0). The operator's claim is specifically about a larger-than-adjacent OI drop; A0 cannot confirm or refute it.
4. The script has no unit tests; it was sanity-checked only by recounting sweeps (207 up + 172 down, matches 369 after dropping the last W bars). Results are exploratory.
5. 1m bars with the 5m grid: 1,320 complete 5m bars; any partially recorded 5m bar is dropped.

### Next (Desktop / LAN)
Run arm A1 on 30 d of 5m OI per section 1 hand-off (`--oi`), last 10 d as holdout; only if A1 passes does an alert candidate go to T067 (T067 spec in this repo is therefore written as conditional on A1).

## 3. RESULTS - arm A1 (sweep + OI drop + price/CVD), Desktop 2026-10-05

Command: `python MyTradingSys/research/loose_code/t063_event_study.py --oi MyTradingSys/runtime/oi_live/oi_5m_30d.csv` (PRE_REG + AMEND 1, parameters unchanged).
Window: overlap of OI and price/CVD, 2026-09-29 to 2026-10-05 (7 UTC days touched, 1,888 complete 5m bars). Not 30 d (see AMEND 1). No holdout.
Sign: positive = flush continues, negative = reverses. Control here also carries the OI clause (same flush + OI drop, no prior sweep).

```
## A1 sweep + OI drop + price/CVD
bars=1888 days_touched=7 sweeps_with_window=518 events_raw=22 control_raw=20
events_with_full_4h=21 control_with_full_4h=19
P(flush|sweep)=0.042 (22/518); events/day=3.14
-- EVENT n=21
  15m: mean=-1.8bp median=2.2bp reversal=9/21=0.43 CI[0.24,0.63]
  1h: mean=-9.0bp median=-0.8bp reversal=11/21=0.52 CI[0.32,0.72]
  4h: mean=5.8bp median=9.3bp reversal=6/21=0.29 CI[0.14,0.50]
  depth_ATR median=1.87 p75=2.29
  snap_back_12bars=10/21 median_bars=4.5
  opposite_pivot_taken_within_4h=12/21
  per_day={20725: 5, 20726: 2, 20727: 2, 20728: 3, 20729: 4, 20730: 3, 20731: 2}
-- CONTROL n=19
  15m: mean=1.6bp median=2.1bp reversal=6/19=0.32 CI[0.15,0.54]
  1h: mean=5.0bp median=0.0bp reversal=9/19=0.47 CI[0.27,0.68]
  4h: mean=-10.9bp median=-10.2bp reversal=11/19=0.58 CI[0.36,0.77]
  depth_ATR median=1.30 p75=3.79
  snap_back_12bars=7/19 median_bars=5
  per_day={20725: 5, 20726: 2, 20727: 1, 20728: 4, 20729: 2, 20730: 4, 20731: 1}
diff(event-control) 15m: mean -3.4bp boot95[-10.5,3.6]
diff(event-control) 1h: mean -14.0bp boot95[-38.2,7.2]
diff(event-control) 4h: mean 16.6bp boot95[-28.6,60.1]
```

### Reading (within the pre-registered rule)
- **Base rate:** 22 of 518 sweeps (4.2%) had a flush with an OI drop >= 2x adjacent-bar median within 30 min; ~3.1 per day. The OI clause cuts A0's 114 events to 22.
- **Sample size:** 21 events with a full 4h window (< 30). **Decision rule: inconclusive** (n < 30). The control has 19, so the diff CIs are wide.
- **Forward returns (event):** 15m mean -1.8bp (reversal 0.43), 1h mean -9.0bp (reversal 0.52, CI [0.32,0.72]), 4h mean +5.8bp (reversal 0.29, CI [0.14,0.50]).
  Event-minus-control 1h diff -14.0bp, bootstrap [-38.2, +7.2] contains 0; 15m and 4h also contain 0.
- **Pullback depth before snap-back:** median 1.87 ATR14 (p75 2.29) beyond the flush close in 12 bars (control 1.30 / 3.79); snap-back through the flush open in 10 of 21 (48%), median 4.5 bars.
- **Opposite pivot taken within 4h:** 12 of 21 (57%), descriptive, no control.
- **Operator claim:** neither supported nor refuted. A 4h continuation lean (reversal 0.29) is the only pattern, but its CI [0.14,0.50] touches 50% and the control flips sign (4h reversal 0.58), so this is noise-compatible at n=21.
- **Caveats:** overlapping 4h windows make every CI optimistic; one 7-day regime; ts_ms joined as bar open (assumed per PRE_REG); no unit tests on the script. Re-run when >= 30 d of price/CVD exists (orderflow recorder started 09-29; ~3 more weeks), then n should clear 30.
- **T067:** stays conditional; A1 did not pass.
