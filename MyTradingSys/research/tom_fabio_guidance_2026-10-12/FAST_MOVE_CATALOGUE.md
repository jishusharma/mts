# Fast-move zone catalogue: triggers and context filters, ready to backtest (Q32 -> Q33)

Sources: `SOURCED_RULES.md` (S1..S14). Code status: `GUIDANCE_AUDIT.md`. Nothing here is tuned; every number marked
`grid` is NO-SOURCE, goes into the pre-registered grid and the FDR family, and is never changed after seeing results.

## 0. Conventions (apply to every definition)
- Data: BTCUSDT perp 1m bars with `delta` (taker buy minus sell volume) and `volume`, UTC. Higher timeframes (5m, 15m,
  1h, 4h) are resampled from 1m, closed bars only. Decision at the close of bar t, entry at the OPEN of t+1.
  A feature may use bars <= t only. No lookahead across resample boundaries (use the bar that closed at or before t).
- Event = first qualifying bar, then 60 one-minute bars of cooldown per (trigger, side). Dedup is per cell.
- Outcome (fee-net, per event, per side): `ret_H = side * (close[t+1+H] / open[t+1] - 1) - 2*fee`, H in {15, 60, 240} bars;
  report mean, median, hit rate, and MFE/MAE in R where R = 1.0 x ATR(14, 15m) at t. `fee` = the repo cost model
  (`backtest` cost module / Deribit cost model of FABIO_TRADE_MODEL.md section 3), taker both ways, not retuned.
- Side is explicit: a cell is (trigger variant, filter state, direction). Longs and shorts never pooled.
- ATR(n): Wilder mean of true range. EMA/SMA standard. pctrank(x, N) = share of the last N values <= x.

## 1. Triggers (T): where a fast move may start
Each trigger yields an event with a `zone` and, per variant, a trade direction.

| id | Definition | Variants (direction) | Source | In code? |
|---|---|---|---|---|
| T1 BB-outside | BB(20, 2) on 15m close. `upper = SMA20 + 2*sd20`, `lower = SMA20 - 2*sd20` (population sd). Event: close[t] > upper (UB) or close[t] < lower (LB), and close[t-1] was inside. Also grid 5m. | UB-cont = long; UB-fade = short; LB-cont = short; LB-fade = long. Long cells: UB-cont, LB-fade. Short cells: LB-cont, UB-fade. | NO-SOURCE as trigger; S7 says volume decides (filter F8) | No (nowhere in code) |
| T2 LVN-traverse | Daily profile of the PRIOR UTC day from 1m volume at `price_bin = ATR(14,1h)/10` (grid 0.05, 0.1, 0.2 x ATR(1h)). Smooth 3 bins. HVN = local max with volume >= median of non-empty bins. LVN band = contiguous bins between two HVNs with smoothed volume <= 0.5 x median (grid 0.25, 0.5, 0.75). Event: within N=15 1m bars price closes at the far edge after being at the near edge, close[t] beyond far edge. | Continuation: trade in crossing direction (long if crossing up, short if down). | S2, S3 (S1 says bounce, so T2b is the contrary variant) | Computed: Java `MarketDataSnapshot.java:654-673` (3 LVN, daily VP), Fabio `signals.py:158-176 select_lvn`. No traverse event detector. |
| T2b LVN-reject | Same LVN bands. Event: bar t wicks into the band by >= 1 bin and closes back outside on the entry side; no close beyond far edge for the next 3 bars. | Fade: trade back toward the side price came from (long off a low-side touch, short off a high-side touch). | S1 (bounce) | No |
| T3 FVG-first-test | 15m 3-bar gap. Bull FVG at bar i: `low[i] > high[i-2]`, zone [high[i-2], low[i]]; bear: `high[i] < low[i-2]`, zone [high[i], low[i-2]]. Unfilled until a close inside the zone. Event: first bar whose range enters an unfilled zone no older than 96 bars. | HOLD: trade in the gap's original impulse direction (long into bull FVG, short into bear FVG). Contrary variant T3b = second test breaks through: event on the second entry, trade against the original impulse (S5 / TOM-205). | S3, S5 (TOM-204, 205, 209) | Java computes FVG in snapshot (not tested as trigger); verify in Q33. |
| T3sp Single print | Prior-day or current-day profile (same bins as T2): contiguous bins with volume <= 1 print-equivalent (<= 1 bin of 1m bar visits; grid 1 and 2 touches) in a move, zone = that range. Same event rule as T3. | as T3 | S4 | `NakedPocTracker` is the nearest; single print itself: No |
| T4 Sweep-void (Fabio) | Level L = max/min of the last 240 1m bars (grid 120, 480) and prior-session high/low. Event: price trades through L and closes beyond it within 3 bars, AND T2 void ahead: next HVN beyond L is >= 1.0 x ATR(14,15m) away (grid 0.5, 1, 2), AND F3 (CVD) agrees with the direction. | long above a high, short below a low (continuation); fade variant = close back inside within 3 bars (sweep-reject). | S11, S12 | Partial: `fabio_cvd_absorption.py`, Fabio v3 signals. Void-distance test: No |
| T5 Tom frozen entries | Existing Tom core rows (`tom_bt` / live setup candidates), frozen parameters, no retune. | as emitted (long/short) | Tom core, sourced separately | Yes |
| T6 Fabio v3 frozen entries | Existing Fabio v3 events, frozen. | as emitted | FABIO_TRADE_MODEL | Yes (shadow; live silent per M5) |

## 2. Context filters (F): which side, and whether to act (evaluated at bar t, closed data)
A filter state partitions the T events; every (T, F-state, direction) is a cell. States are discrete so n per cell can
be counted before running.

| id | State definition | States | Source | In code? |
|---|---|---|---|---|
| F1 HTF trend | `side_vwap = sign(close[t] - VWAP_day)` with VWAP anchored 00:00 UTC (S10); `wpoc = sign(POC_thisweek - POC_lastweek)` (weekly volume POC, S9/TOM-196 idea); `ema = sign(EMA20(4h) - EMA20(4h, 6 bars ago))` (NO-SOURCE, convention). | UP if >= 2 of 3 positive, DOWN if >= 2 negative, else MIXED | S10 and weekly POC: sourced; ema: NO-SOURCE | VWAP: Yes (Java). Weekly POC migration: No (M3). EMA slope: No |
| F2 RSI regime | `RSI(14)` Wilder on 15m close. `bear` < 40, `neutral` 40..60, `bull` > 60. | 3 states | NO-SOURCE for Tom/Fabio. Malkan (secondary): confirm quote in `research/malkan_rsi_2026-09-28/` before use | RSI(14) + 40 level events: `live_layers.py:146-166`. 40-60 regime: No |
| F3 CVD slope | `cvd_n = sum(delta[t-n+1..t]) / sum(volume[t-n+1..t])`, n = 30 (grid 60, 120) 1m bars. `cvd_z = (cvd_n - mean_{30d})/sd_{30d}`. | POS if cvd_z >= +1, NEG if <= -1, else FLAT (grid 0.5, 1.0, 1.5) | S13, S14 (direction); threshold NO-SOURCE | Yes (Java `cvd_slope`; Python `orderflow_bars.py`, Fabio S2) |
| F4 OI change | `doi = OI[t]/OI[t-60 bars] - 1`. With price change over the same window `dp` and F3 sign: quad = sign(dp) x sign(cvd) x sign(doi). | doi rising/falling/flat (pctrank 7d: >= 80, <= 20, else) ; quad label as `quad_classify` | NO-SOURCE | Snapshot only: `MarketDataSnapshot.java:342,405`; `quad_classify.py`; history on JIS-NB (check coverage) |
| F5 L/S ratio | Global account long/short ratio (and top-trader ratio, reported separately) `ls[t]`; `ls_z` = z over 30d. | HIGH if z >= +1, LOW if <= -1, else MID (both directions are tested; contrarian is NOT assumed) | NO-SOURCE | Snapshot only: `MarketDataSnapshot.java:1541-1562` |
| F6 Funding | Last published 8h funding rate `fr[t]`; z over 30d. | HIGH >= +1, LOW <= -1, else MID | NO-SOURCE | `live_layers.py:79-100`; `MarketDataSnapshot.java:256-259` |
| F7 Compression (squeeze) | `bbw = (upper - lower)/SMA20` on 15m; `sq = pctrank(bbw, 672)` (7 days). Alt: `atrr = ATR(14,15m)/ATR(100,15m)`. Fabio S1 form: `range(N)/ATR(1m,N) <= k` with N in {60,120,240}, k grid {2, 3}. | SQUEEZE if sq <= 20 (grid 10, 20, 30) ; EXPANDED if sq >= 80; else NORMAL | S9 and FABIO_TRADE_MODEL S1 (idea); BB-width form NO-SOURCE | Fabio S1 balance: in v3 (shadow). BB width/atrr: No |
| F8 Volume support | `rv = volume_tf[t] / median(volume_tf at the same time-of-day, last 20 days)` on the trigger timeframe; and `cvd` sign agrees with the breach (F3). | SUPPORTED if rv >= 1.5 (grid 1.5, 2.0) AND F3 sign = trigger direction; UNSUPPORTED if rv < 1.0; else NEUTRAL | S7 (idea); threshold NO-SOURCE | rv: No. CVD: Yes |

Joint derived state used for side choice (pre-registered, not tuned): `TREND = F1 state`, `MOMO = F3 state`. The 3x3 grid of
(F1, F3) is the default partition; F2, F4-F8 are tested one at a time on top of it (one extra filter per cell, never
stacked more than 2 deep, to keep n >= 300).

## 3. Expected reading per side (hypotheses written BEFORE the run, from the sources)
| Trigger | Long cells | Short cells | Hypothesis |
|---|---|---|---|
| T1 UB/LB | UB-cont, LB-fade | LB-cont, UB-fade | H1: cont beats fade only when F8 SUPPORTED. UB-fade short with F1 UP is the "trap" cell (Tom S7) and should be worst. |
| T2 | up-crossing | down-crossing | H2: continuation needs F3 agreeing; T2b bounce (S1) is the control. |
| T3 / T3b | long into bull FVG | short into bear FVG | H3: HOLD works with F1 UP/DOWN trend-stable (S5); fails in MIXED; T3b wins in MIXED/sideways (S5 "traded through"). |
| T4 | long above high | short below low | H4: needs void ahead + F3 agree (S11). |
| T5/T6 | as emitted | as emitted | descriptive tagging only; compare with and without each T1-T4 agreement (like `fabio_tag`). |

## 4. What Q33 may NOT do
No parameter outside the grids above, no new filter after seeing results, no stacking beyond 2 filters, no pooling of
long and short, ROADMAP STOP list applies. Cells with F4/F5/F6 report NOT_IN_DATA if the history has gaps; do not impute.
