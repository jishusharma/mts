# PRE_REG: candle-close-colour probability per timeframe (the "flip engine"), frozen 2026-11-06 before any outcome was counted

Card `candle-flip-probability-study-1106`; design `DESIGN.md`; operator ask 2026-11-06 (voice), Lead verdict `d-flip-engine-study-1106`: a CONTEXT layer
(a number per timeframe), never a TAKE/SKIP signal, worth building only if it beats the random-walk null out of sample. Only the 1m bars were
downloaded (`fetch_1m.py`, public data-api.binance.vision BTCUSDT spot, 1,498,575 closed bars, 2024-01-01T00:00Z .. 2026-11-06T16:13Z, 0 gaps checked)
and the regime mix of the windows was computed (`ctx_regime.py`, no outcome read) before this file was written. No outcome (`y`) has been computed.

## The question
Inside an open bar of timeframe T, with the price at some minute, how likely is the bar to CLOSE with the colour it has now? The null is a driftless
random walk. A raw "flip rate" looks predictive without any edge (early in a bar everything flips back), so the study reports realised minus null and Brier.

## Timeframes and anchors (20, all OURS unless noted)
1w, 5d, 3d, 2d, 1d, 12h, 8h, 7h, 6h, 4h, 3h, 2h, 1h, 30m, 15m, 10m, 5m, 3m, 2m, 1m. Every bar is a block of S consecutive 1m bars. Bars tile forward
from 2024-01-01T00:00Z (a Monday) in blocks of S minutes, no reset at month or year ends (OURS). 1w = 10080 min = Monday 00:00Z, the exchange
convention (SOURCED: Binance weekly klines open Monday 00:00Z; 2024-01-01 is a Monday so the tile equals it). 1d and 12h/8h/6h/4h/3h/2h/1h/30m/15m/10m/5m divide the day;
5d, 3d, 2d, 7h, 3m, 2m do not all, so their bars cross midnight (7h) or span days (2d/3d/5d): this is the anchor choice the review is asked to check.
Only complete bars enter. **1m has no row**: the study evaluates inside a bar at 1m resolution, and a 1m bar has no inside; 1m is reported NOT_IN_DATA (the
function `P_close_colour` still takes a live tick price on 1m).

## Colour definitions (two, both reported)
- open-colour: colour of price vs the bar's open; the bar "keeps" it if close vs open has the same sign. `y_open` = 1 if kept, 0 if flipped or close = open.
- prior-close colour: price vs the previous bar's close; kept if close vs that close has the same sign. `y_pc` likewise. (On 24/7 spot the open is the prior close
  to the tick, so the two will be near-identical; reporting both is the check.) Rows with price exactly equal to the reference are dropped.

## Evaluation points
For each complete bar b of timeframe S minutes, the price is the CLOSE of the j-th 1m bar (j = 0..S-2), elapsed time (j+1)/S, `t_left = 1 - (j+1)/S` in (0,1].
Per bar at most P = min(S-1, 6) points at elapsed fractions k/(P+1), k = 1..P (j = round(S*k/(P+1)) - 1, duplicates removed). Subsample: per timeframe at most
100,000 rows (19 timeframes x 100k = 1.9M <= 2M): when bars x P exceeds it, whole bars are kept by a seeded draw (numpy default_rng(1106 + S)); never row by row.
Bars with fewer than 20 complete prior bars of the same timeframe are dropped (ATR and Bollinger need them).

## The null (SOURCED maths, OURS scale)
`sigma_bar = ATR14 / 1.5958` where ATR14 = mean true range of the 14 complete bars before bar b (TR = max(H-L, |H-prevC|, |L-prevC|), H and L from the 1m highs and lows),
1.5958 = 2*sqrt(2/pi) = expected range of a Brownian motion in units of its sd over the bar (SOURCED, standard result; the ATR scaling to the bar sd is OURS).
`d = (price - ref) / sigma_bar`, ref = bar open (open-colour) or previous bar close (prior-close colour). The remaining move to the close is N(0, t_left * sigma_bar^2):
**P(close on the other side of ref) = Phi(-|d| / sqrt(t_left)); null P(keeps colour) = Phi(|d| / sqrt(t_left)) = p0.** At d = 0, p0 = 0.5 for every t_left.
(The Lead's brief calls this a Brownian bridge; the formula is the plain Brownian remaining-increment, identical in the brief and here.)

## The 12 cells, the whole confirmatory family, per timeframe group
HTF (2) x session (3) x BB (2):
- HTF aligned / split: the FORMING 1d and 1w candle colours at the evaluation minute (price vs the 1d open, price vs the 1w open) agree = aligned, differ or either flat = split. For
  1d..1w rows one of the two is the row's own timeframe (OURS, kept; no row-colour direction is used, so this tests whether HTF agreement changes persistence, not "with the trend").
- Session of the evaluation minute close: Asia 00-08Z, EU 08-13Z, US 13-21Z (cutoffs OURS, as research_kit session_tag); 21-24Z is not in the family (dropped from tables).
- BB position: Bollinger(20, 2 sd, population) on the row's OWN timeframe closes, the window = the 19 complete prior bars' closes + the current price (as the live strip); `at band`
  = price at or beyond a band (raw 0..100 position <= 0 or >= 100), `inside` otherwise (OURS).
Timeframe groups (OURS): G1 1m-15m (2m,3m,5m,10m,15m), G2 30m-4h, G3 6h-1d (6h,7h,8h,12h,1d), G4 2d-1w. The cells are pooled over the timeframes of a group.

## Windows
- Fit: bars whose CLOSE is <= 2025-01-01T00:00Z. Score: bars whose OPEN is >= 2025-01-01T00:00Z, to the last complete bar. Bars straddling the cut are dropped (purge).
- The score window runs through the repo's sealed HOLDOUT (2025-07-01 ..). The Lead ordered this window; the data are public klines read directly, the study measures
  calibration of a context probability, not a trade return; the read is logged once in `research/holdout_reads.csv` via `splits.read_holdout` before the score pass, and the
  holdout is BURNED for this flip-probability family.

## Conditioned model and scoring
- Conditioned model: `p_cond = clip(p0 + delta_fit(group, cell), 0.001, 0.999)` where `delta_fit` = mean of `y - p0` over the fit rows of that group and cell (2024 only). No score row feeds it.
- Brier = mean (p - y)^2 on the score rows, for the null, and for the conditioned model, per timeframe and per (group, cell). 
- Primary test per (group, cell): H0 mean(y - p0) = 0 on the score rows (delta). z = mean / se, se = cluster-robust (cluster = timeframe + bar, G/(G-1) correction), two-sided normal p.
  A cell with fewer than 30 distinct score bars is NOT_POWERED: p = 1, never counts. Both colour definitions are run; the verdict is stated on open-colour, prior-close is the check.
- Holm: **m = 12 inside the study** = the 12 cells of one group table (each group table is its own family of 12). Because there are 4 group tables, the study-wide Holm p over all 48
  (group, cell) tests (m = 48) is printed next to it and the verdict line gives both. The repo-wide gate (prereg_gate.py, m = 238) is not used for this study.
- A cell COUNTS only if: n bars >= 30, Brier(conditioned) < Brier(null) on the score rows of that cell, AND Holm p (m = 12) < 0.05. "Survives study-wide" additionally needs Holm p (m = 48) < 0.05.
- Verdict wording is frozen: the study is a calibration test of a context layer; no PASS/TAKE/SKIP is claimed; if no cell counts, the answer is "the null is the engine" and the gauge
  ships as the pure-maths P(keeps colour) with no context shift.

## What the result will say
1. `RESULT.md` first lines: the `Regime mix:` lines (below), then the verdict line.
2. Per group: table cell, n (rows), bars, realised, null, delta, Brier null, Brier conditioned, Holm p (m=12), Holm p (m=48).
3. Per timeframe: rows, bars, Brier of the null and of the group-conditioned model, both colour definitions.
4. The null's own calibration across t_left buckets (realised minus null overall): if the ATR scaling is off, every cell shows it, and that is reported as a finding.

Regime mix (fit): 53 weeks: bull 35 (66%) | bear 0 (0%) | range 18 (34%) | n/a 0 (0%)
Regime mix (score): 96 weeks: bull 23 (24%) | bear 0 (0%) | range 73 (76%) | n/a 0 (0%)
The score window is range-heavy (76 % of weeks), the fit window bull-heavy (66 %): a cell effect that differs between them is a regime effect, and the study cannot separate the two.

## Context
Regime: not gated; every row is tagged by the research_kit.regime_tag weekly mix above and reported (fit bull-heavy, score range-heavy). Whether persistence differs by regime is NOT tested here (OURS: the weekly regime has 149 weeks, 12 cells already use the power).
Phase: none; the bar's own elapsed fraction t_left is the phase (the null is a function of it), and HTF 1d/1w colour agreement is the only higher-timeframe state.
Session: Asia 00-08Z / EU 08-13Z / US 13-21Z of the evaluation minute (late 21-24Z excluded from the family).
Entry: none; this is a probability of the open candle's close colour, not an entry. No trade, no TAKE/SKIP, no return.

## Parameter labels
| Parameter | Value | Label |
|---|---|---|
| Bar tiling | 2024-01-01T00:00Z forward, S-minute blocks; 1w Monday | OURS (1w Monday SOURCED) |
| sigma_bar | ATR14 / 1.5958 | 1.5958 SOURCED (Brownian range), ATR14 and the scaling OURS |
| Null | Phi(abs(d) / sqrt(t_left)) | SOURCED maths |
| BB | 20 closes (19 prior + price), 2 sd population, at band = beyond 0..100 | OURS (20, 2 as the live strip) |
| Sessions | 00-08 / 08-13 / 13-21Z | OURS |
| HTF | forming 1d and 1w colours agree | OURS |
| Points per bar / row cap | 6 / 100k per timeframe | OURS |
| Windows | fit <= 2025-01-01 < score | Lead order |
| Holm | m = 12 per group table, m = 48 study-wide shown | OURS (Lead order m = 12) |
| Min bars per cell | 30 | OURS |

## Amendments after the Haiku review (2026-11-06, after the first count; the frozen text above is unchanged and stays the record of the plan)
The first run (commit 9f7dc27ae, bar clusters) counted 16 cells. `REVIEW.md` found problems in the analysis, so the analysis was changed and rerun. Each amendment is stated with what it replaces; the first-run numbers are NOT a result.
- A1 clustering (review #1, blocker): SE and p cluster by the UTC week of the bar open (Monday start), not by timeframe + bar, because bars of different timeframes share the same 1m path and the 1d/1w colours are shared by every bar of a day or week. The bar-cluster p is kept in `cells.csv` as `p_bar`. A cell also needs >= 30 distinct score weeks.
- A2 HTF cell for own-timeframe rows (review #5): the frozen text "no row-colour direction is used" is wrong for 1d and 1w rows (one of the two colours is the row's own). 1d and 1w rows get htf = `na`, are not in the 12 cells, and stay in the per-timeframe Brier table (shift 0).
- A3 fit gate (review #7): a cell shift is fitted only with >= 30 distinct fit bars, else 0 (fail closed); fit bars are printed.
- A4 headline multiplicity (review #12): the headline counts cells surviving Holm m = 48 (all four group tables); m = 12 per group stays as printed. Only the open-colour test counts; the prior-close colour is a near-duplicate on 24/7 spot (review #9) and is not evidence.
- A5 recalibrated baseline (review #2, #3), EXPLORATORY and OURS, written after seeing the first result: the null recalibrated on |d| (8 quantile bins from the fit rows) x time left (fifths), fitted on 2024 per group, bins with < 30 fit rows fall back to the null. Cells are tested against this baseline too (same Holm, same week clusters, same Brier rule); the verdict states both.
- A6 Bollinger centring constant (review #10): the first close, not the series mean. It cancels exactly; no number changes.
- A7 regime split (review #11): score-window delta by the weekly regime tag of the bar-open week (`regime_weeks.csv`, `regime_split.csv`), descriptive only.
- A8 holdout (review #6): RESULT says that no clean holdout remains for this family; any rule that ships from these cells needs fresh data.
Not adopted: a materiality floor (review #8) is not invented after the fact; RESULT states the gains as statistical, not economic.
