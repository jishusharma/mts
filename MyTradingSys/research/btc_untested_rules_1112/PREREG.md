# PREREG: four untested value-area rules on BTC (acceptance, return to liquidity, thin close to POC, naked POC), written before any trade is computed

Card btc-test-of-untested-rules-acceptance-re (task btc-untested-rules-1112). Sources: `BB3c8visnkI` R4 and R5, `YkclL6xgu-s` R5, `ODdF0Bn_KSc` R6 in research/orderflow_extracts_1112/ORDERFLOW_RULES.md, section "Not yet tested on BTC".
Analyst statements are context, never signals. This file is committed before any trade of any rule is computed.
Four rules, one frozen parameter set each, no sweep. Every number is OURS unless it carries SOURCED (quote). The rule ids give an idea only; none states a number.

## Context
Regime: none as a gate, because none of the four rules states a regime; DEV spans bear 2022, base 2023, run-up 2024 and the RESULT reports per-year and long/short rows.
Phase: none, because phase labels are not part of the rules.
Session: none; all UTC hours trade. Day = UTC day, week = UTC Monday 00:00 to Sunday 23:59.
Entry: A, B and C enter at the open of the 15m bar after the signal bar has closed (C: the 00:00 UTC bar of the next day); D enters at a resting limit price (stated below).
Regime mix: DEV 2022-02-01..2024-05-31 (BTC daily close 38,680 -> 67,578, +75 %); descriptive day count, same window and same SMA50 definition as edge_views_2026-11-11/VA_REENTRY_POC_SHIFT/PREREG.md, no trade involved: 832 DEV days with a 50-day SMA, 51.4 % close above it and 48.6 % below. VALIDATION (2024-07-01 on) is not touched.

## Sources (the idea only)
- A `BB3c8visnkI` R4. SOURCED (quote): "This new fair price range where the market is now generating new liquidity is apparently being accepted by the market." Idea: N bars spent beyond the old edge make the edge hold on retest.
- B `BB3c8visnkI` R5. SOURCED (quote): "because the market always likes to return to high liquidity to see if it can find trading participants there again." Idea: after leaving the range, price revisits the high-volume node (the POC); fade back to it.
- C `YkclL6xgu-s` R5. SOURCED (quote): "there was little trading volume. And the logical consequence from this since we also have the point of control that is the volume weighted center of gravity up here the market moved back up again the following week." Idea: a close in a thin part of the profile is pulled back to the POC. The video says week; the daily session is OURS (needs enough events), the weekly version is not run.
- D `ODdF0Bn_KSc` R6. SOURCED (quote): "A naked POC isn't an edge in itself, but rather it's an indication for me that there was aggressive trading there". Idea: measure touch rate and the reaction at an untouched weekly POC. The video calls it no edge by itself, so a FAIL is the expected finding and not a contradiction.

## Difference from what exists
- the backtest return-to-value count script (vp return to value, in backtest/) (Tom's "returns to value 70 %" COUNT): 5m bars, event = first close outside the prior VA, outcome = touch of the prior POC, no entry, stop, target or cost, bootstrap statistics. Mine: 15m bars from the reduced aggtrades bars, trade simulation with stop, target, cap and 10 bp fee, direction-matched placebo. Rules A, C, D have no counterpart there (its Part B "accepted_N" measures a POC touch after N closes beyond the edge; my A measures the EDGE retest hold and trades it). B shares its event definition (first exit close) and is counted as a trial.
- VA_REENTRY_POC_SHIFT (R1 re-entry back inside, target = opposite edge; R2 POC shift): helpers `profile`, `day_profiles`, `simulate` are imported from its va_poc.py, not copied. Different triggers and targets: B targets the POC and enters at the exit close, not after a re-entry close.
- TESTED_MAP has no thin-close or naked-POC row (ORDERFLOW_RULES lists them as untested). Trial count: about 103 prior counted studies; these are trials ~104..107. A pass is not an edge claim.

## Data
D:/MTS_data/binance_aggtrades/reduced/BTCUSDT-bars15-YYYY-MM.csv.gz (read only), 15m bars with open, high, low, close, vol; bar index x 900,000 = open ms. Files 2022-01 .. 2024-05 only (2022-01 and days before 2022-02-01 are warm-up for prior profiles). VALIDATION is never read. A bar is usable only after its close. Daily and weekly profiles only from COMPLETED UTC days/weeks. The volume profile is built from 15m bars (OURS approximation, coarser than the 1m used before; no trade-level profile).

## Profile definition (shared)
va_poc.profile as in the earlier PREREG: each 15m bar's volume goes to the bin of its typical price (h+l+c)/3; bin width 0.05 % of the period's last close for days, 0.10 % for weeks (OURS, weeks have a wider range); POC = largest bin (ties lowest); value area = standard 70 % rule from the POC, larger of the next two bins above/below (tie above). VAH = top edge, VAL = bottom edge.

## Common simulation
Exit for B, C: stop or target on 15m bars from the entry bar, stop wins a tie, fills at the stop/target price, no slippage, cap in bars then exit at that bar close (va_poc.simulate). Stop distance = target distance (1:1, OURS). Skip if R/entry < 0.10 % (fee guard) or R <= 0. One position at a time per rule. Net bp = side x (exit/entry - 1) x 1e4 - 10 (fee 10 bp round trip = fees.BINANCE_TAKER x 2).

## A: acceptance then edge retest (BB3c8visnkI R4)
Levels for day D = VAH, VAL of day D-1. Event (up): 15m bar i of day D closes above VAH while bar i-1 closed <= VAH. Accepted if bars i..i+7 (N = 8, 2 h, OURS) all close above VAH. Retest = the first bar j > i+7, within 24 bars after i+7 (OURS), with low <= VAH. HOLD = bar j closes above VAH (known at its close). Trade: if HOLD, long at the open of j+1; if bar j closed <= VAH, no trade. Exit at the close of the 16th bar after entry (4 h, OURS), no stop (return study; a close-based stop would add a parameter). Down event = mirror (close below VAL, short; retest = high >= VAL; HOLD = close below VAL). One position at a time. Descriptive hold-share comparison: accepted events versus NON-accepted events (exit bar followed by a retest touch of the edge at bar j within 1..7 bars after i, so fewer than 8 closes beyond the edge, same HOLD test), no trade for those; plus the trade-level placebo below.

## B: return to liquidity (BB3c8visnkI R5)
Event: first 15m bar i of day D that closes outside the prior-day value area (above VAH or below VAL) while the previous bar closed inside or on the edge (one event per direction per day). Revisit share = share of events where a bar in i+1..i+24 (6 h) has low <= POC_{D-1} <= high (events with fewer than 24 later loaded bars are dropped). Trade: fade to the prior-day POC: entry at the open of i+1, target POC_{D-1}, stop 1:1, cap 24 bars; skip if R <= 0 or R/entry < 0.10 %.

## C: thin close pulls to POC (YkclL6xgu-s R5)
For completed day d: c_d = last 15m close; THIN if the volume of the close's bin <= 0.25 x the POC bin volume (OURS) and the close is not in the POC bin. Touch share = share of next days d+1 where a bar has low <= POC_d <= high, THIN days versus non-THIN days (descriptive). Trade on THIN days: entry at the 00:00 UTC bar open of d+1, long if c_d < POC_d else short, target POC_d, stop 1:1, cap 96 bars, same skips.

## D: naked weekly POC (ODdF0Bn_KSc R6)
POC_w of completed week w is born naked at Monday 00:00 UTC after week w. Event kept if |POC_w - close_w| / close_w >= 1 % (OURS, so a touch is not trivial). The POC stays naked until a bar's [low, high] contains it. Touch rate = share of kept events touched within 4 weeks (672 bars, OURS; events with fewer than 4 later loaded weeks dropped). Placebo touch rate = the mirror level (same distance, other side of the birth close). Trade: a resting limit at POC_w from birth fills at the first touching bar (fill at the POC price, ideal limit fill, no queue, OURS), side = long if the birth close was above the POC else short (bounce), exit at the close of the 96th bar after the touch bar, no stop, net bp as above, one position at a time (a touch while one is open is skipped). Reaction size: also report the median maximum favourable excursion over those 96 bars in bp (descriptive).

## Sample
DEV only: entries/events 2022-02-01 00:00 UTC .. 2024-05-31 23:59 UTC; the loaded bars end with the May 2024 file and serve only to finish trades. DEV halves split at the exact midpoint of the span (2023-04-02 UTC): both halves must be positive.

## Placebo (direction-matched; 500 draws, seed 1)
Per real trade a random 15m entry bar inside DEV (D: entry at the random bar open, not a limit), same side, same stop % and target % distances, same cap, same fee (A and D: same side and horizon, no stop). Report the placebo mean and the share of draws at or above the real mean.

## Pass bar (fixed now)
PASS: fee-net mean > 0 and t >= 2 (t = mean / (sd / sqrt n)) and both DEV halves mean > 0. FAIL: mean <= 0. Otherwise INCONCLUSIVE (also n < 30). PASS is not an edge claim: it only earns a separate pre-registered VALIDATION step and the trial-count correction.

## RESULT.md must hold
Per rule: n, win rate, mean net bp, t, both DEV halves, max drawdown (sum of bp), per-year and long/short rows from MyTradingSys/backtest/trade_sanity.py (year_side_lines; log_sanity against the 1m klines where F:/MTS/data/tom_raw/klines exists, else the 15m bar range check), placebo row, the descriptive shares (A hold share, B revisit share, C touch share, D touch rate and mirror), a `Regime mix:` line, plain-words verdict.
Tests: test_untested_rules.py with hand-computed events, written to fail on a version with the window off by one bar.
